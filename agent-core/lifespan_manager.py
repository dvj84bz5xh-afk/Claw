"""
Lifespan 资源生命周期管理器
借鉴 modelcontextprotocol/python-sdk 的 Lifespan API (@asynccontextmanager)，
为 Claw 实现生产级资源生命周期管理。

核心概念:
1. LifespanManager - 资源管理器 (注册/初始化/清理)
2. @lifespan 装饰器 - 将生成器转为上下文管理器 (支持同步/异步)
3. LifespanContext - 上下文对象 (持有资源和元数据)
4. 资源类型 - DB连接/文件锁/API会话/子进程

异常安全: 即使初始化失败，也保证已分配资源的清理。
"""

import asyncio
import contextlib
import functools
import inspect
import json
import logging
import os
import sqlite3
import threading
import time
from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Generator, AsyncGenerator, ContextManager, AsyncContextManager

logger = logging.getLogger(__name__)


# ─── 数据结构 ───────────────────────────────────────────────────────────────

@dataclass
class ResourceInfo:
    """资源元信息"""
    resource_id: str
    resource_type: str           # "db" | "file" | "api" | "process" | "custom"
    created_at: str = ""
    closed_at: str = ""
    status: str = "init"        # init -> open -> closed | error
    error: str = ""
    metadata: dict = field(default_factory=dict)

    def mark_open(self):
        self.status = "open"
        self.created_at = datetime.now().isoformat()

    def mark_closed(self, error: str = ""):
        self.status = "error" if error else "closed"
        self.closed_at = datetime.now().isoformat()
        self.error = error


@dataclass
class LifespanContext:
    """
    生命周期上下文对象。
    持有资源引用，供托管代码使用。
    """
    resources: dict = field(default_factory=dict)       # resource_id -> resource object
    info: dict = field(default_factory=dict)           # resource_id -> ResourceInfo
    data: dict = field(default_factory=dict)            # 任意共享数据
    _owner: str = ""                                   # 拥有者标识

    def add_resource(self, rid: str, obj: Any, info: ResourceInfo):
        self.resources[rid] = obj
        self.info[rid] = info

    def get(self, rid: str) -> Any:
        return self.resources.get(rid)

    def remove_resource(self, rid: str):
        if rid in self.resources:
            del self.resources[rid]
        if rid in self.info:
            del self.info[rid]

    def summary(self) -> dict:
        return {
            "owner": self._owner,
            "resource_count": len(self.resources),
            "resources": {k: v.status for k, v in self.info.items()},
            "data_keys": list(self.data.keys()),
        }


# ─── @lifespan 装饰器 ──────────────────────────────────────────────────────

def lifespan(fn: Callable) -> Callable:
    """
    将生成器函数转为生命周期上下文管理器。

    用法:
        @lifespan
        def db_lifespan(path: str):
            conn = sqlite3.connect(path)
            try:
                yield {"conn": conn}
            finally:
                conn.close()

        # 使用
        with db_lifespan("/tmp/test.db") as ctx:
            conn = ctx.resources["conn"]
            ...

    支持同步/异步生成器。
    """
    if inspect.isasyncgenfunction(fn):
        return _async_lifespan_wrapper(fn)
    elif inspect.isgeneratorfunction(fn):
        return _sync_lifespan_wrapper(fn)
    else:
        raise ValueError("@lifespan 必须装饰生成器函数 (yield)")


def _sync_lifespan_wrapper(fn: Callable) -> Callable:
    """同步生成器包装器"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs) -> "_LifespanContextManager":
        return _LifespanContextManager(fn, args, kwargs)
    return wrapper


def _async_lifespan_wrapper(fn: Callable) -> Callable:
    """异步生成器包装器"""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs) -> "_AsyncLifespanContextManager":
        return _AsyncLifespanContextManager(fn, args, kwargs)
    return wrapper


class _LifespanContextManager:
    """同步生命周期上下文管理器"""
    def __init__(self, fn, args, kwargs):
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._gen = None
        self._resource = None
        self._cleaned = False

    def __enter__(self):
        """启动生成器，返回 yield 的值（字典或对象）"""
        self._gen = self._fn(*self._args, **self._kwargs)
        self._resource = next(self._gen)  # 保存 yield 的值
        return self._resource  # 返回给 with 语句的 as 变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理生成器（触发 finally 块）"""
        if self._cleaned:
            return
        self._cleaned = True
        try:
            if exc_type is not None:
                # 有异常，通过 throw 传入
                self._gen.throw(exc_val)
            else:
                # 正常清理，通过 next 触发 finally
                next(self._gen, None)
        except (StopIteration, StopAsyncIteration):
            pass  # 正常结束
        except Exception as e:
            logger.warning(f"Lifespan 清理异常: {e}")


class _AsyncLifespanContextManager:
    """异步生命周期上下文管理器"""
    def __init__(self, fn, args, kwargs):
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._gen = None
        self._resource = None
        self._cleaned = False

    async def __aenter__(self):
        """启动生成器，返回 yield 的值"""
        self._gen = self._fn(*self._args, **self._kwargs)
        self._resource = await self._gen.__anext__()
        return self._resource  # 返回给 with 语句的 as 变量

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理生成器（触发 finally 块）"""
        if self._cleaned:
            return
        self._cleaned = True
        try:
            if exc_type is not None:
                await self._gen.athrow(exc_val)
            else:
                await self._gen.__anext__()
        except (StopIteration, StopAsyncIteration):
            pass
        except Exception as e:
            logger.warning(f"Async Lifespan 清理异常: {e}")


# ─── 预置资源工厂 ───────────────────────────────────────────────────────────

@lifespan
def sqlite_lifespan(db_path: str, **connect_args):
    """
    SQLite 数据库连接生命周期。
    用法: with sqlite_lifespan("/path/db.sqlite") as ctx: ...
    """
    conn = sqlite3.connect(db_path, **connect_args)
    try:
        yield {"conn": conn}
    finally:
        conn.close()


@lifespan
def jsonl_lifespan(filepath: str, mode: str = "a"):
    """
    JSONL 文件写入生命周期（跨平台文件锁）。
    用法: with jsonl_lifespan("/path/log.jsonl") as ctx: ...
    """
    import platform
    fd = open(filepath, mode, encoding="utf-8")
    lock_acquired = False
    try:
        # 跨平台文件锁
        if platform.system() != "Windows":
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            lock_acquired = True
        else:
            # Windows: 使用 msvcrt 或跳过锁（演示环境）
            try:
                import msvcrt
                # 简化：Windows 下不强制加锁（避免复杂度）
            except ImportError:
                pass
        
        yield {"fd": fd, "write": lambda obj: fd.write(json.dumps(obj, ensure_ascii=False) + "\n")}
    finally:
        if lock_acquired:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


@lifespan
def api_session_lifespan(base_url: str, headers: dict = None, timeout: int = 30):
    """
    API 会话生命周期（HTTP连接池）。
    用法: with api_session_lifespan("https://api.example.com") as ctx: ...
    """
    import urllib.request
    import urllib.parse

    class Session:
        def __init__(self, base, hdrs, to):
            self.base = base
            self.headers = hdrs or {}
            self.timeout = to

        def get(self, path, params=None):
            url = self.base.rstrip("/") + "/" + path.lstrip("/")
            if params:
                url += "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())

        def post(self, path, data=None):
            url = self.base.rstrip("/") + "/" + path.lstrip("/")
            payload = json.dumps(data or {}).encode()
            req = urllib.request.Request(url, data=payload, headers={**self.headers, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())

    session = Session(base_url, headers, timeout)
    try:
        yield {"session": session}
    finally:
        pass  # urllib 自动关闭


@lifespan
def subprocess_lifespan(cmd: list[str], cwd: str = None, env: dict = None, timeout: int = 300):
    """
    子进程生命周期。
    用法: with subprocess_lifespan(["python", "script.py"]) as ctx: ...
    """
    import subprocess
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        yield {"proc": proc, "pid": proc.pid}
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


# ─── LifespanManager ────────────────────────────────────────────────────────

class LifespanManager:
    """
    资源管理器。
    集中注册、初始化、清理资源，保证异常安全。
    """
    def __init__(self, owner: str = "default"):
        self.owner = owner
        self._factories: dict[str, Callable] = {}
        self._ctx: LifespanContext | None = None
        self._lock = threading.RLock()
        self._initialized = False
        self._cms: list = []  # 持有所有上下文管理器的引用

    def register(self, resource_id: str, factory: Callable):
        """
        注册资源工厂函数。
        factory 必须是由 @lifespan 装饰的生成器函数。
        """
        with self._lock:
            self._factories[resource_id] = factory

    def register_sqlite(self, resource_id: str, db_path: str, **connect_args):
        """快捷注册: SQLite"""
        self.register(resource_id, lambda: sqlite_lifespan(db_path, **connect_args))

    def register_jsonl(self, resource_id: str, filepath: str, mode: str = "a"):
        """快捷注册: JSONL 文件"""
        self.register(resource_id, lambda: jsonl_lifespan(filepath, mode))

    def register_api_session(self, resource_id: str, base_url: str, headers: dict = None):
        """快捷注册: API 会话"""
        self.register(resource_id, lambda: api_session_lifespan(base_url, headers))

    def register_subprocess(self, resource_id: str, cmd: list[str], **kwargs):
        """快捷注册: 子进程"""
        self.register(resource_id, lambda: subprocess_lifespan(cmd, **kwargs))

    def __enter__(self) -> "LifespanManager":
        self.start()
        return self

    def __exit__(self, *args):
        self.shutdown()

    async def __aenter__(self) -> LifespanContext:
        return await self.astart()

    async def __aexit__(self, *args):
        await self.ashutdown()

    def start(self) -> LifespanContext:
        """同步启动所有注册的资源"""
        with self._lock:
            if self._initialized:
                return self._ctx

            self._ctx = LifespanContext(_owner=self.owner)
            errors = []

            for rid, factory in self._factories.items():
                try:
                    # factory() 返回 _LifespanContextManager 或 _AsyncLifespanContextManager
                    cm = factory()
                    self._cms.append(cm)
                    # __enter__() 返回 yield 的值（字典或对象）
                    resource = cm.__enter__()
                    # 保存为资源，资源ID 是 rid
                    info = ResourceInfo(resource_id=rid, resource_type=type(resource).__name__)
                    info.mark_open()
                    self._ctx.add_resource(rid, resource, info)
                except Exception as e:
                    errors.append((rid, str(e)))
                    logger.error(f"资源 {rid} 初始化失败: {e}")

            self._initialized = True

            if errors:
                logger.warning(f"部分资源初始化失败: {errors}")

            return self._ctx

    def shutdown(self):
        """同步关闭所有资源"""
        with self._lock:
            if not self._initialized:
                return
            # 遍历所有上下文管理器，调用 __exit__
            for cm in self._cms:
                try:
                    cm.__exit__(None, None, None)
                except Exception as e:
                    logger.warning(f"资源清理异常: {e}")
            self._cms = []  # 清空引用
            self._ctx = None
            self._initialized = False

    async def astart(self) -> LifespanContext:
        """异步启动（暂委托给同步实现）"""
        return self.start()

    async def ashutdown(self):
        """异步关闭"""
        self.shutdown()

    def get_ctx(self) -> LifespanContext | None:
        return self._ctx

    def get_resource(self, rid: str) -> Any:
        if self._ctx:
            return self._ctx.get(rid)
        return None

    def status(self) -> dict:
        """返回管理器状态摘要"""
        return {
            "owner": self.owner,
            "initialized": self._initialized,
            "registered_count": len(self._factories),
            "active_resources": len(self._ctx.resources) if self._ctx else 0,
            "resources": self._ctx.summary() if self._ctx else {},
        }


# ─── 集成示例 ───────────────────────────────────────────────────────────────

def demonstrate_lifespan():
    """
    演示 LifespanManager 用法。
    """
    print("=== LifespanManager 演示 ===\n")

    # 示例1: 管理 SQLite 连接
    print("[示例1] SQLite 生命周期")
    mgr = LifespanManager("demo_db")
    mgr.register_sqlite("main_db", ":memory:")
    with mgr:
        ctx = mgr.get_ctx()
        conn = mgr.get_resource("main_db")["conn"]  # yield 的是 {"conn": conn}
        conn.execute("CREATE TABLE test (id INT, val TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'hello')")
        conn.commit()
        row = conn.execute("SELECT * FROM test").fetchone()
        print(f"  查询结果: {row}")
        print(f"  管理器状态: {mgr.status()}")
    print("  ✅ SQLite 连接已自动关闭\n")

    # 示例2: 管理 JSONL 文件
    print("[示例2] JSONL 文件生命周期")
    import tempfile, os
    test_file = os.path.join(tempfile.gettempdir(), "lifespan_demo.jsonl")
    mgr2 = LifespanManager("demo_jsonl")
    mgr2.register_jsonl("log", test_file, mode="w")
    with mgr2:
        write_fn = mgr2.get_resource("log")["write"]  # yield 的是 {"fd": fd, "write": fn}
        write_fn({"event": "start", "ts": time.time()})
        write_fn({"event": "end", "ts": time.time()})
        print(f"  已写入: {test_file}")
    print("  ✅ 文件已自动关闭\n")

    # 示例3: 异常安全
    print("[示例3] 异常安全演示")
    class FakeError(Exception):
        pass

    @lifespan
    def failing_resource():
        resource = {"data": "important"}
        try:
            yield {"res": resource}
        finally:
            print("   清理函数被调用 (即使有异常)")

    try:
        mgr3 = LifespanManager("demo_exc")
        mgr3.register("bad", failing_resource)
        with mgr3:
            raise FakeError("模拟异常")
    except FakeError:
        print("  ✅ 异常被捕获，资源仍被正确清理\n")

    # 示例4: 与进化引擎集成
    print("[示例4] 与进化引擎集成 (模拟)")
    print("  进化引擎现在可以使用 LifespanManager 管理:")
    print("    - SQLite 连接 (evolution_log.jsonl)")
    print("    - 文件锁 (防止并发写入)")
    print("    - GitHub API 会话 (token 管理)")
    print("  ✅ 资源生命周期可预测\n")

    print("=== 演示完成 ===")


# ─── CLI 入口 ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demonstrate_lifespan()
