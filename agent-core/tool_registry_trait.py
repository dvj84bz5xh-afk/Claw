"""
Phase 3.1: Trait-based Tool Registry System

基于 Rust Trait 模式的 Python 实现
支持动态工具发现、注册、执行和沙箱
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Type, Protocol, runtime_checkable
from enum import Enum, auto
from datetime import datetime
import json
import inspect
import importlib
import pkgutil
from pathlib import Path
import threading
import uuid


class ToolCategory(Enum):
    """工具分类"""
    FILE_IO = auto()      # 文件读写
    SHELL = auto()        # 命令执行
    SEARCH = auto()       # 搜索查询
    NETWORK = auto()      # 网络操作
    SYSTEM = auto()       # 系统操作
    CUSTOM = auto()       # 自定义工具


class ToolPermission(Enum):
    """工具权限级别"""
    READ_ONLY = 1
    WORKSPACE_WRITE = 2
    DANGER_FULL_ACCESS = 3


@dataclass
class ToolSpec:
    """工具规格定义"""
    name: str
    description: str
    category: ToolCategory
    permission: ToolPermission
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.name,
            "permission": self.permission.name,
            "parameters": self.parameters,
            "returns": self.returns,
            "examples": self.examples,
            "tags": self.tags,
            "version": self.version,
            "author": self.author
        }


@dataclass
class ToolCall:
    """工具调用请求"""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    caller_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    call_id: str = ""
    
    @classmethod
    def success_result(cls, data: Any, execution_time_ms: float = 0.0, call_id: str = "") -> 'ToolResult':
        return cls(success=True, data=data, execution_time_ms=execution_time_ms, call_id=call_id)
    
    @classmethod
    def error_result(cls, error_message: str, call_id: str = "") -> 'ToolResult':
        return cls(success=False, data=None, error_message=error_message, call_id=call_id)


@runtime_checkable
class ToolTrait(Protocol):
    """
    工具 Trait (Protocol)
    
    参考 Rust 的 Trait 模式，定义工具必须实现的方法
    """
    
    @property
    def spec(self) -> ToolSpec:
        """返回工具规格"""
        ...
    
    def execute(self, call: ToolCall) -> ToolResult:
        """执行工具"""
        ...
    
    def validate_args(self, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """验证参数"""
        ...


class BaseTool(ABC):
    """
    基础工具类
    
    所有工具都应该继承此类并实现抽象方法
    """
    
    def __init__(self):
        self._call_history: List[ToolCall] = []
        self._lock = threading.RLock()
    
    @property
    @abstractmethod
    def spec(self) -> ToolSpec:
        """子类必须定义工具规格"""
        pass
    
    @abstractmethod
    def _execute_impl(self, call: ToolCall) -> Any:
        """子类实现具体的执行逻辑"""
        pass
    
    def execute(self, call: ToolCall) -> ToolResult:
        """
        执行工具（包装方法）
        
        添加执行时间统计和错误处理
        """
        import time
        
        start_time = time.perf_counter()
        
        with self._lock:
            self._call_history.append(call)
        
        try:
            # 验证参数
            valid, error = self.validate_args(call.arguments)
            if not valid:
                return ToolResult.error_result(f"参数验证失败: {error}", call.call_id)
            
            # 执行工具
            result_data = self._execute_impl(call)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return ToolResult.success_result(result_data, execution_time, call.call_id)
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            return ToolResult.error_result(str(e), call.call_id)
    
    def validate_args(self, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证参数
        
        默认实现检查必需参数，子类可覆盖
        """
        required_params = self.spec.parameters.get("required", [])
        for param in required_params:
            if param not in args:
                return False, f"缺少必需参数: {param}"
        return True, None
    
    def get_call_history(self) -> List[ToolCall]:
        """获取调用历史"""
        with self._lock:
            return self._call_history.copy()


# ==================== 具体工具实现示例 ====================

class FileReadTool(BaseTool):
    """文件读取工具"""
    
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="file_read",
            description="读取文件内容",
            category=ToolCategory.FILE_IO,
            permission=ToolPermission.READ_ONLY,
            parameters={
                "required": ["file_path"],
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "offset": {"type": "integer", "description": "起始偏移", "default": 0},
                    "limit": {"type": "integer", "description": "读取行数", "default": 100}
                }
            },
            returns={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "total_lines": {"type": "integer"}
                }
            },
            examples=[
                '{"file_path": "/path/to/file.txt"}',
                '{"file_path": "/path/to/file.txt", "offset": 10, "limit": 50}'
            ],
            tags=["file", "read", "io"],
            version="1.0.0",
            author="Agent Core"
        )
    
    def _execute_impl(self, call: ToolCall) -> Any:
        file_path = call.arguments.get("file_path")
        offset = call.arguments.get("offset", 0)
        limit = call.arguments.get("limit", 100)
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = offset
        end = offset + limit
        selected_lines = lines[start:end]
        
        return {
            "content": ''.join(selected_lines),
            "total_lines": len(lines),
            "returned_lines": len(selected_lines)
        }


class BashTool(BaseTool):
    """Bash命令执行工具"""
    
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="bash",
            description="执行Bash命令",
            category=ToolCategory.SHELL,
            permission=ToolPermission.DANGER_FULL_ACCESS,
            parameters={
                "required": ["command"],
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"},
                    "timeout": {"type": "integer", "description": "超时时间(秒)", "default": 60},
                    "cwd": {"type": "string", "description": "工作目录"}
                }
            },
            returns={
                "type": "object",
                "properties": {
                    "stdout": {"type": "string"},
                    "stderr": {"type": "string"},
                    "exit_code": {"type": "integer"}
                }
            },
            examples=[
                '{"command": "ls -la"}',
                '{"command": "python script.py", "timeout": 30}'
            ],
            tags=["shell", "bash", "command"],
            version="1.0.0",
            author="Agent Core"
        )
    
    def _execute_impl(self, call: ToolCall) -> Any:
        import subprocess
        import shlex
        
        command = call.arguments.get("command")
        timeout = call.arguments.get("timeout", 60)
        cwd = call.arguments.get("cwd")
        
        # 安全检查
        dangerous_patterns = ['rm -rf /', '> /dev/null', 'mkfs']
        for pattern in dangerous_patterns:
            if pattern in command:
                raise ValueError(f"检测到危险命令模式: {pattern}")
        
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }


# ==================== 工具注册表 ====================

class ToolRegistry:
    """
    Trait-based 工具注册表
    
    核心功能:
    - 工具动态注册
    - 按类别/权限查询
    - 工具路由和分发
    - 调用历史追踪
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._lock = threading.RLock()
        self._execution_stats: Dict[str, Dict[str, Any]] = {}
    
    def register(self, tool: BaseTool) -> bool:
        """注册工具"""
        with self._lock:
            tool_name = tool.spec.name
            if tool_name in self._tools:
                print(f"[警告] 工具 '{tool_name}' 已存在，将被覆盖")
            
            self._tools[tool_name] = tool
            self._execution_stats[tool_name] = {
                "call_count": 0,
                "error_count": 0,
                "avg_execution_time": 0.0,
                "last_called": None
            }
            print(f"[注册] 工具 '{tool_name}' ({tool.spec.category.name})")
            return True
    
    def unregister(self, tool_name: str) -> bool:
        """注销工具"""
        with self._lock:
            if tool_name in self._tools:
                del self._tools[tool_name]
                del self._execution_stats[tool_name]
                print(f"[注销] 工具 '{tool_name}'")
                return True
            return False
    
    def get(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(tool_name)
    
    def list_tools(self, category: Optional[ToolCategory] = None, 
                   permission: Optional[ToolPermission] = None) -> List[ToolSpec]:
        """列出符合条件的工具"""
        specs = []
        for tool in self._tools.values():
            spec = tool.spec
            if category and spec.category != category:
                continue
            if permission and spec.permission != permission:
                continue
            specs.append(spec)
        return specs
    
    def execute(self, tool_name: str, arguments: Dict[str, Any], 
                caller_context: Optional[Dict] = None) -> ToolResult:
        """执行工具"""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult.error_result(f"工具不存在: {tool_name}")
        
        call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            caller_context=caller_context or {}
        )
        
        result = tool.execute(call)
        
        # 更新统计
        with self._lock:
            stats = self._execution_stats[tool_name]
            stats["call_count"] += 1
            if not result.success:
                stats["error_count"] += 1
            stats["last_called"] = datetime.now().isoformat()
            
            # 更新平均执行时间
            if result.execution_time_ms > 0:
                old_avg = stats["avg_execution_time"]
                count = stats["call_count"]
                stats["avg_execution_time"] = (old_avg * (count - 1) + result.execution_time_ms) / count
        
        return result
    
    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """获取执行统计"""
        with self._lock:
            if tool_name:
                return self._execution_stats.get(tool_name, {})
            return self._execution_stats.copy()
    
    def discover_tools(self, package_path: str) -> List[str]:
        """
        从包路径自动发现工具
        
        扫描指定包中的所有模块，查找 BaseTool 子类
        """
        discovered = []
        try:
            package = importlib.import_module(package_path)
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_name = f"{package_path}.{module_name}"
                try:
                    module = importlib.import_module(full_name)
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTool) and 
                            obj != BaseTool and
                            not inspect.isabstract(obj)):
                            discovered.append(f"{full_name}.{name}")
                except Exception as e:
                    print(f"[发现] 加载模块 {full_name} 失败: {e}")
        except Exception as e:
            print(f"[发现] 扫描包 {package_path} 失败: {e}")
        
        return discovered
    
    def load_tool_from_string(self, tool_path: str) -> Optional[BaseTool]:
        """
        从字符串路径加载工具
        
        格式: "package.module.ClassName"
        """
        try:
            module_path, class_name = tool_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            
            if issubclass(tool_class, BaseTool):
                tool_instance = tool_class()
                self.register(tool_instance)
                return tool_instance
        except Exception as e:
            print(f"[加载] 工具 {tool_path} 失败: {e}")
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """导出注册表信息"""
        return {
            "tool_count": len(self._tools),
            "tools": [tool.spec.to_dict() for tool in self._tools.values()],
            "stats": self._execution_stats
        }


# ==================== 工具沙箱 ====================

class ToolSandbox:
    """
    工具执行沙箱
    
    提供隔离的执行环境
    """
    
    def __init__(self, allowed_paths: Optional[List[str]] = None,
                 blocked_commands: Optional[List[str]] = None):
        self.allowed_paths = set(allowed_paths or [])
        self.blocked_commands = set(blocked_commands or [
            'rm -rf /', 'mkfs', 'dd if=', 'format',
            '> /etc/', 'passwd', 'userdel'
        ])
    
    def validate_command(self, command: str) -> tuple[bool, Optional[str]]:
        """验证命令是否安全"""
        for blocked in self.blocked_commands:
            if blocked in command:
                return False, f"包含禁止的命令模式: {blocked}"
        return True, None
    
    def validate_path(self, path: str) -> tuple[bool, Optional[str]]:
        """验证路径是否在允许范围内"""
        if not self.allowed_paths:
            return True, None
        
        path_obj = Path(path).resolve()
        for allowed in self.allowed_paths:
            allowed_obj = Path(allowed).resolve()
            try:
                path_obj.relative_to(allowed_obj)
                return True, None
            except ValueError:
                continue
        
        return False, f"路径 {path} 不在允许的范围内"


# ==================== 快速创建工具的装饰器 ====================

def create_tool(name: str, description: str, 
                category: ToolCategory = ToolCategory.CUSTOM,
                permission: ToolPermission = ToolPermission.READ_ONLY,
                tags: Optional[List[str]] = None):
    """
    快速创建工具的工厂函数
    
    使用示例:
    ```python
    @create_tool("my_tool", "我的工具", ToolCategory.CUSTOM)
    def my_tool_impl(args):
        return {"result": args.get("input", "")}
    ```
    """
    def decorator(func: Callable) -> BaseTool:
        class DynamicTool(BaseTool):
            @property
            def spec(self) -> ToolSpec:
                # 从函数签名推断参数
                sig = inspect.signature(func)
                params = {
                    "required": [],
                    "properties": {}
                }
                for param_name, param in sig.parameters.items():
                    if param.default == inspect.Parameter.empty:
                        params["required"].append(param_name)
                    params["properties"][param_name] = {
                        "type": "any",
                        "default": param.default if param.default != inspect.Parameter.empty else None
                    }
                
                return ToolSpec(
                    name=name,
                    description=description,
                    category=category,
                    permission=permission,
                    parameters=params,
                    tags=tags or [],
                    version="1.0.0"
                )
            
            def _execute_impl(self, call: ToolCall) -> Any:
                return func(call.arguments)
        
        return DynamicTool()
    
    return decorator


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3.1: Trait-based Tool Registry System Test")
    print("=" * 60)
    
    # 创建注册表
    registry = ToolRegistry()
    
    # 注册内置工具
    registry.register(FileReadTool())
    registry.register(BashTool())
    
    print(f"\n已注册工具: {len(registry._tools)} 个")
    
    # 列出所有工具
    print("\n工具列表:")
    for spec in registry.list_tools():
        print(f"  - {spec.name} ({spec.category.name}) [{spec.permission.name}]")
    
    # 执行工具测试
    print("\n测试1: 执行文件读取工具")
    result = registry.execute("file_read", {
        "file_path": "tool_registry_trait.py",
        "limit": 10
    })
    print(f"  结果: {'成功' if result.success else '失败'}")
    if result.success:
        print(f"  返回行数: {result.data.get('returned_lines')}")
    else:
        print(f"  错误: {result.error_message}")
    
    # 执行Bash工具测试
    print("\n测试2: 执行Bash工具")
    result = registry.execute("bash", {
        "command": "echo 'Hello from Trait-based Tool System'",
        "timeout": 10
    })
    print(f"  结果: {'成功' if result.success else '失败'}")
    if result.success:
        print(f"  输出: {result.data.get('stdout', '').strip()}")
    
    # 查看统计
    print("\n执行统计:")
    stats = registry.get_stats()
    for tool_name, tool_stats in stats.items():
        print(f"  {tool_name}: {tool_stats['call_count']} 次调用")
    
    # 导出注册表信息
    print("\n注册表导出:")
    registry_info = registry.to_dict()
    print(f"  总工具数: {registry_info['tool_count']}")
    
    print("\n" + "=" * 60)
    print("Trait-based Tool Registry System Test Completed!")
    print("=" * 60)
