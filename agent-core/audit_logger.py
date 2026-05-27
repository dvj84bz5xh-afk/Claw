#!/usr/bin/env python3
"""
Audit Logger - 审计日志系统
记录所有关键操作，支持合规性审计和安全分析

灵感来源: Claw Code 的审计和可观测性设计
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum, auto
from datetime import datetime
import time
import json
import hashlib
import threading
from pathlib import Path
import uuid


class AuditLevel(Enum):
    """审计级别"""
    DEBUG = "debug"       # 调试信息
    INFO = "info"         # 一般信息
    ACTION = "action"     # 用户操作
    SYSTEM = "system"     # 系统事件
    SECURITY = "security" # 安全相关
    ERROR = "error"       # 错误


class AuditCategory(Enum):
    """审计类别"""
    FILE_ACCESS = "file_access"
    COMMAND_EXEC = "command_exec"
    TOOL_CALL = "tool_call"
    SESSION = "session"
    CONFIG = "config"
    NETWORK = "network"
    AUTH = "auth"
    DATA_CHANGE = "data_change"


@dataclass
class AuditRecord:
    """审计记录"""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    level: Any = None  # AuditLevel
    category: Any = None  # AuditCategory
    action: str = ""
    actor: str = "system"
    target: str = ""
    status: str = "success"
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if self.level is None:
            self.level = AuditLevel.INFO
        if self.category is None:
            self.category = AuditCategory.SYSTEM
    
    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level.value,
            "category": self.category.value,
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "status": self.status,
            "details": self.details,
            "metadata": self.metadata,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id
        }
    
    def compute_hash(self) -> str:
        """计算记录哈希（防篡改）"""
        data = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class AuditQuery:
    """审计查询条件"""
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    levels: Optional[List[AuditLevel]] = None
    categories: Optional[List[AuditCategory]] = None
    actors: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    status: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = 100
    offset: int = 0


class AuditLogger:
    """审计日志管理器"""
    
    def __init__(self, storage_dir: Optional[str] = None, 
                 max_memory_records: int = 10000):
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / ".claw" / "audit"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_buffer: List[AuditRecord] = []
        self.max_memory_records = max_memory_records
        self._lock = threading.RLock()
        
        # 配置
        self.enabled_levels: Set[AuditLevel] = set(AuditLevel)
        self.enabled_categories: Set[AuditCategory] = set(AuditCategory)
        self.hooks: List[Callable] = []
        self.auto_flush_interval: int = 60  # 秒
        self._flush_timer: Optional[threading.Timer] = None
        
        # 启动自动刷新
        self._start_auto_flush()
    
    def log(self, level: AuditLevel, category: AuditCategory, action: str,
            actor: str = "system", target: str = "", status: str = "success",
            details: Optional[Dict] = None, session_id: Optional[str] = None,
            correlation_id: Optional[str] = None) -> AuditRecord:
        """记录审计日志"""
        # 检查是否启用
        if level not in self.enabled_levels:
            return None
        if category not in self.enabled_categories:
            return None
        
        record = AuditRecord(
            level=level,
            category=category,
            action=action,
            actor=actor,
            target=target,
            status=status,
            details=details or {},
            session_id=session_id,
            correlation_id=correlation_id
        )
        
        # 添加完整性哈希
        record.metadata["integrity_hash"] = record.compute_hash()
        
        with self._lock:
            self.memory_buffer.append(record)
            
            # 内存缓冲区满了则刷新到磁盘
            if len(self.memory_buffer) >= self.max_memory_records:
                self._flush_to_disk()
        
        # 执行hooks
        for hook in self.hooks:
            try:
                hook(record)
            except Exception:
                pass
        
        return record
    
    # 便捷方法
    def debug(self, category: AuditCategory, action: str, **kwargs):
        """记录DEBUG级别日志"""
        return self.log(AuditLevel.DEBUG, category, action, **kwargs)
    
    def info(self, category: AuditCategory, action: str, **kwargs):
        """记录INFO级别日志"""
        return self.log(AuditLevel.INFO, category, action, **kwargs)
    
    def action(self, category: AuditCategory, action: str, **kwargs):
        """记录ACTION级别日志"""
        return self.log(AuditLevel.ACTION, category, action, **kwargs)
    
    def security(self, category: AuditCategory, action: str, **kwargs):
        """记录SECURITY级别日志"""
        return self.log(AuditLevel.SECURITY, category, action, **kwargs)
    
    def error(self, category: AuditCategory, action: str, **kwargs):
        """记录ERROR级别日志"""
        return self.log(AuditLevel.ERROR, category, action, **kwargs)
    
    def log_tool_call(self, tool_name: str, arguments: Dict, 
                      result: Any, duration_ms: float,
                      actor: str = "system", session_id: Optional[str] = None):
        """记录工具调用"""
        return self.log(
            level=AuditLevel.ACTION,
            category=AuditCategory.TOOL_CALL,
            action=f"tool.{tool_name}",
            actor=actor,
            target=tool_name,
            status="success" if result else "error",
            details={
                "arguments": arguments,
                "result_summary": str(result)[:200] if result else None,
                "duration_ms": duration_ms
            },
            session_id=session_id
        )
    
    def log_file_access(self, file_path: str, operation: str,
                        actor: str = "system", session_id: Optional[str] = None):
        """记录文件访问"""
        return self.log(
            level=AuditLevel.ACTION,
            category=AuditCategory.FILE_ACCESS,
            action=f"file.{operation}",
            actor=actor,
            target=file_path,
            session_id=session_id
        )
    
    def log_command(self, command: str, exit_code: int,
                    actor: str = "system", session_id: Optional[str] = None):
        """记录命令执行"""
        return self.log(
            level=AuditLevel.ACTION,
            category=AuditCategory.COMMAND_EXEC,
            action="command.exec",
            actor=actor,
            target=command[:100],
            status="success" if exit_code == 0 else "error",
            details={"exit_code": exit_code},
            session_id=session_id
        )
    
    def query(self, query: AuditQuery) -> List[AuditRecord]:
        """查询审计记录"""
        with self._lock:
            results = self.memory_buffer.copy()
        
        # 应用过滤条件
        filtered = []
        for record in results:
            if query.start_time and record.timestamp < query.start_time:
                continue
            if query.end_time and record.timestamp > query.end_time:
                continue
            if query.levels and record.level not in query.levels:
                continue
            if query.categories and record.category not in query.categories:
                continue
            if query.actors and record.actor not in query.actors:
                continue
            if query.actions and record.action not in query.actions:
                continue
            if query.status and record.status != query.status:
                continue
            if query.session_id and record.session_id != query.session_id:
                continue
            filtered.append(record)
        
        # 排序和分页
        filtered.sort(key=lambda r: r.timestamp, reverse=True)
        return filtered[query.offset:query.offset + query.limit]
    
    def _flush_to_disk(self):
        """刷新到磁盘"""
        with self._lock:
            if not self.memory_buffer:
                return
            
            # 按日期分文件
            now = datetime.now()
            filename = f"audit_{now.strftime('%Y%m%d')}.jsonl"
            filepath = self.storage_dir / filename
            
            with open(filepath, "a", encoding="utf-8") as f:
                for record in self.memory_buffer:
                    f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
            
            self.memory_buffer.clear()
    
    def _start_auto_flush(self):
        """启动自动刷新"""
        def flush_and_reschedule():
            self._flush_to_disk()
            self._start_auto_flush()
        
        self._flush_timer = threading.Timer(self.auto_flush_interval, flush_and_reschedule)
        self._flush_timer.daemon = True
        self._flush_timer.start()
    
    def flush(self):
        """手动刷新"""
        self._flush_to_disk()
    
    def close(self):
        """关闭并刷新"""
        if self._flush_timer:
            self._flush_timer.cancel()
        self._flush_to_disk()
    
    def add_hook(self, hook: Callable):
        """添加hook"""
        self.hooks.append(hook)
    
    def set_level(self, level: AuditLevel, enabled: bool = True):
        """设置级别启用状态"""
        if enabled:
            self.enabled_levels.add(level)
        else:
            self.enabled_levels.discard(level)
    
    def set_category(self, category: AuditCategory, enabled: bool = True):
        """设置类别启用状态"""
        if enabled:
            self.enabled_categories.add(category)
        else:
            self.enabled_categories.discard(category)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            total = len(self.memory_buffer)
        
        by_level = {}
        by_category = {}
        by_actor = {}
        
        for record in self.memory_buffer:
            by_level[record.level.value] = by_level.get(record.level.value, 0) + 1
            by_category[record.category.value] = by_category.get(record.category.value, 0) + 1
            by_actor[record.actor] = by_actor.get(record.actor, 0) + 1
        
        return {
            "total_in_memory": total,
            "by_level": by_level,
            "by_category": by_category,
            "by_actor": by_actor,
            "storage_dir": str(self.storage_dir)
        }
    
    def generate_report(self, hours: int = 24) -> str:
        """生成审计报告"""
        now = time.time()
        start = now - hours * 3600
        
        query = AuditQuery(start_time=start, end_time=now, limit=1000)
        records = self.query(query)
        
        stats = {
            "total": len(records),
            "by_level": {},
            "by_category": {},
            "errors": 0,
            "security": 0
        }
        
        for record in records:
            stats["by_level"][record.level.value] = stats["by_level"].get(record.level.value, 0) + 1
            stats["by_category"][record.category.value] = stats["by_category"].get(record.category.value, 0) + 1
            if record.status == "error":
                stats["errors"] += 1
            if record.level == AuditLevel.SECURITY:
                stats["security"] += 1
        
        lines = [
            "=" * 60,
            f"Audit Report (Last {hours}h)",
            "=" * 60,
            f"Total Records: {stats['total']}",
            f"Errors: {stats['errors']}",
            f"Security Events: {stats['security']}",
            "-" * 60,
            "By Level:"
        ]
        
        for level, count in stats["by_level"].items():
            lines.append(f"  {level}: {count}")
        
        lines.extend(["-" * 60, "By Category:"])
        
        for cat, count in stats["by_category"].items():
            lines.append(f"  {cat}: {count}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 上下文管理器
class AuditContext:
    """审计上下文管理器"""
    
    def __init__(self, logger: AuditLogger, action: str, 
                 actor: str = "system", session_id: Optional[str] = None):
        self.logger = logger
        self.action = action
        self.actor = actor
        self.session_id = session_id
        self.start_time: Optional[float] = None
        self.record: Optional[AuditRecord] = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.record = self.logger.action(
            AuditCategory.SYSTEM,
            self.action,
            actor=self.actor,
            session_id=self.session_id,
            details={"status": "started"}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(
                AuditCategory.SYSTEM,
                self.action,
                actor=self.actor,
                session_id=self.session_id,
                details={
                    "duration_ms": duration,
                    "error": str(exc_val)
                }
            )
        else:
            self.logger.info(
                AuditCategory.SYSTEM,
                self.action,
                actor=self.actor,
                session_id=self.session_id,
                details={"duration_ms": duration, "status": "completed"}
            )


# 测试代码
if __name__ == "__main__":
    print("Audit Logger Test")
    print("=" * 60)
    
    logger = AuditLogger()
    
    # 记录一些日志
    logger.info(AuditCategory.SYSTEM, "system.start", actor="admin")
    logger.action(AuditCategory.FILE_ACCESS, "file.read", target="config.json")
    logger.log_tool_call("file_read", {"path": "test.txt"}, "content", 150)
    logger.log_command("ls -la", 0)
    logger.security(AuditCategory.AUTH, "auth.login", actor="user123", status="success")
    
    # 查询
    query = AuditQuery(limit=10)
    records = logger.query(query)
    print(f"\nQueried {len(records)} records from memory")
    
    # 统计
    stats = logger.get_statistics()
    print(f"\nStatistics: {stats}")
    
    # 生成报告
    print("\n" + logger.generate_report(hours=1))
    
    # 刷新到磁盘
    logger.flush()
    print("\nFlushed to disk")
    
    logger.close()
    print("\n" + "=" * 60)
    print("Audit Logger module ready!")
