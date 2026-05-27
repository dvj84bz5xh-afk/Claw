#!/usr/bin/env python3
"""
Mock Services - 测试模拟服务
提供工具调用的模拟实现，用于测试和开发

灵感来源: Claw Code 的 Mock 测试框架
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum, auto
from pathlib import Path
import json
import hashlib
import time
from datetime import datetime


class MockBehavior(Enum):
    """Mock行为类型"""
    NORMAL = auto()      # 正常返回
    ERROR = auto()       # 返回错误
    DELAY = auto()       # 延迟返回
    RANDOM = auto()      # 随机返回
    SEQUENCE = auto()    # 序列返回


@dataclass
class MockCall:
    """Mock调用记录"""
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    call_id: str = field(default_factory=lambda: hashlib.md5(
        str(time.time()).encode()).hexdigest()[:8])
    
    def to_dict(self) -> Dict:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }


@dataclass
class MockResponse:
    """Mock响应"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    delay_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "delay_ms": self.delay_ms,
            "metadata": self.metadata
        }


class MockTool(ABC):
    """Mock工具基类"""
    
    def __init__(self, name: str, behavior: MockBehavior = MockBehavior.NORMAL):
        self.name = name
        self.behavior = behavior
        self.call_history: List[MockCall] = []
        self.response_sequence: List[MockResponse] = []
        self.sequence_index: int = 0
        self.error_rate: float = 0.0  # 错误率 (0-1)
        self.delay_range: tuple = (0, 0)  # 延迟范围 (min, max) ms
        
    @abstractmethod
    def _execute_mock(self, arguments: Dict[str, Any]) -> MockResponse:
        """执行Mock逻辑"""
        pass
    
    def execute(self, arguments: Dict[str, Any]) -> MockResponse:
        """执行Mock调用"""
        # 记录调用
        call = MockCall(tool_name=self.name, arguments=arguments)
        self.call_history.append(call)
        
        # 根据行为类型处理
        if self.behavior == MockBehavior.ERROR:
            return MockResponse(
                success=False,
                error=f"Mock error for {self.name}"
            )
        
        elif self.behavior == MockBehavior.DELAY:
            delay = self.delay_range[0] + (
                hash(str(arguments)) % (self.delay_range[1] - self.delay_range[0] + 1)
            )
            return MockResponse(
                success=True,
                data=self._execute_mock(arguments).data,
                delay_ms=delay
            )
        
        elif self.behavior == MockBehavior.SEQUENCE and self.response_sequence:
            response = self.response_sequence[self.sequence_index % len(self.response_sequence)]
            self.sequence_index += 1
            return response
        
        elif self.behavior == MockBehavior.RANDOM:
            import random
            if random.random() < self.error_rate:
                return MockResponse(
                    success=False,
                    error=f"Random mock error for {self.name}"
                )
        
        # 正常执行
        return self._execute_mock(arguments)
    
    def set_sequence(self, responses: List[MockResponse]):
        """设置响应序列"""
        self.response_sequence = responses
        self.behavior = MockBehavior.SEQUENCE
        
    def set_error_rate(self, rate: float):
        """设置错误率"""
        self.error_rate = max(0.0, min(1.0, rate))
        self.behavior = MockBehavior.RANDOM
        
    def set_delay(self, min_ms: int, max_ms: int):
        """设置延迟范围"""
        self.delay_range = (min_ms, max_ms)
        self.behavior = MockBehavior.DELAY
        
    def get_call_history(self) -> List[MockCall]:
        """获取调用历史"""
        return self.call_history.copy()
        
    def clear_history(self):
        """清除调用历史"""
        self.call_history.clear()


class MockFileRead(MockTool):
    """模拟文件读取工具"""
    
    def __init__(self):
        super().__init__("file_read")
        self.virtual_files: Dict[str, str] = {}
        
    def add_virtual_file(self, path: str, content: str):
        """添加虚拟文件"""
        self.virtual_files[path] = content
        
    def _execute_mock(self, arguments: Dict[str, Any]) -> MockResponse:
        file_path = arguments.get("file_path", "")
        
        if file_path in self.virtual_files:
            return MockResponse(
                success=True,
                data={"content": self.virtual_files[file_path], "path": file_path}
            )
        
        # 检查实际文件
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8")
                return MockResponse(
                    success=True,
                    data={"content": content, "path": file_path}
                )
        except Exception as e:
            return MockResponse(success=False, error=str(e))
        
        return MockResponse(
            success=False,
            error=f"File not found: {file_path}"
        )


class MockFileWrite(MockTool):
    """模拟文件写入工具"""
    
    def __init__(self):
        super().__init__("file_write")
        self.written_files: Dict[str, str] = {}
        self.simulate_only: bool = True
        
    def set_simulate_only(self, simulate: bool):
        """设置是否仅模拟"""
        self.simulate_only = simulate
        
    def _execute_mock(self, arguments: Dict[str, Any]) -> MockResponse:
        file_path = arguments.get("file_path", "")
        content = arguments.get("content", "")
        
        self.written_files[file_path] = content
        
        if not self.simulate_only:
            try:
                Path(file_path).write_text(content, encoding="utf-8")
            except Exception as e:
                return MockResponse(success=False, error=str(e))
        
        return MockResponse(
            success=True,
            data={"path": file_path, "bytes_written": len(content.encode())}
        )
    
    def get_written_content(self, path: str) -> Optional[str]:
        """获取已写入的内容"""
        return self.written_files.get(path)


class MockBash(MockTool):
    """模拟Bash命令工具"""
    
    def __init__(self):
        super().__init__("bash")
        self.command_handlers: Dict[str, Callable] = {}
        self.virtual_commands: Dict[str, tuple] = {}  # cmd -> (stdout, stderr, returncode)
        
    def register_handler(self, command_pattern: str, handler: Callable):
        """注册命令处理器"""
        self.command_handlers[command_pattern] = handler
        
    def add_virtual_command(self, command: str, stdout: str = "", stderr: str = "", returncode: int = 0):
        """添加虚拟命令"""
        self.virtual_commands[command] = (stdout, stderr, returncode)
        
    def _execute_mock(self, arguments: Dict[str, Any]) -> MockResponse:
        command = arguments.get("command", "")
        
        # 检查虚拟命令
        if command in self.virtual_commands:
            stdout, stderr, returncode = self.virtual_commands[command]
            return MockResponse(
                success=returncode == 0,
                data={
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": returncode
                }
            )
        
        # 检查处理器
        for pattern, handler in self.command_handlers.items():
            if pattern in command:
                try:
                    result = handler(command)
                    return MockResponse(success=True, data=result)
                except Exception as e:
                    return MockResponse(success=False, error=str(e))
        
        # 默认返回
        return MockResponse(
            success=True,
            data={
                "stdout": f"Mock output for: {command}",
                "stderr": "",
                "returncode": 0
            }
        )


class MockWebSearch(MockTool):
    """模拟网络搜索工具"""
    
    def __init__(self):
        super().__init__("web_search")
        self.mock_results: Dict[str, List[Dict]] = {}
        
    def add_mock_results(self, query: str, results: List[Dict]):
        """添加模拟搜索结果"""
        self.mock_results[query] = results
        
    def _execute_mock(self, arguments: Dict[str, Any]) -> MockResponse:
        query = arguments.get("query", "")
        
        if query in self.mock_results:
            return MockResponse(
                success=True,
                data={"results": self.mock_results[query], "query": query}
            )
        
        # 默认返回
        return MockResponse(
            success=True,
            data={
                "results": [
                    {
                        "title": f"Mock result for: {query}",
                        "url": "https://example.com/mock",
                        "snippet": "This is a mock search result for testing purposes."
                    }
                ],
                "query": query
            }
        )


class MockServiceRegistry:
    """Mock服务注册表"""
    
    def __init__(self):
        self.tools: Dict[str, MockTool] = {}
        self.global_delay: int = 0
        self.global_error_rate: float = 0.0
        self.recording_enabled: bool = True
        self.call_log: List[Dict] = []
        
    def register(self, tool: MockTool):
        """注册Mock工具"""
        self.tools[tool.name] = tool
        
    def get_tool(self, name: str) -> Optional[MockTool]:
        """获取Mock工具"""
        return self.tools.get(name)
        
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> MockResponse:
        """执行Mock调用"""
        if tool_name not in self.tools:
            return MockResponse(
                success=False,
                error=f"Mock tool not found: {tool_name}"
            )
        
        # 应用全局延迟
        if self.global_delay > 0:
            time.sleep(self.global_delay / 1000)
        
        # 执行
        response = self.tools[tool_name].execute(arguments)
        
        # 记录
        if self.recording_enabled:
            self.call_log.append({
                "tool": tool_name,
                "arguments": arguments,
                "response": response.to_dict(),
                "timestamp": time.time()
            })
        
        return response
    
    def set_global_delay(self, delay_ms: int):
        """设置全局延迟"""
        self.global_delay = delay_ms
        
    def set_global_error_rate(self, rate: float):
        """设置全局错误率"""
        self.global_error_rate = rate
        
    def enable_recording(self, enabled: bool = True):
        """启用/禁用记录"""
        self.recording_enabled = enabled
        
    def get_call_log(self) -> List[Dict]:
        """获取调用日志"""
        return self.call_log.copy()
        
    def clear_log(self):
        """清除日志"""
        self.call_log.clear()
        
    def create_snapshot(self) -> Dict:
        """创建快照"""
        return {
            "tools": list(self.tools.keys()),
            "call_count": len(self.call_log),
            "global_delay": self.global_delay,
            "global_error_rate": self.global_error_rate,
            "timestamp": time.time()
        }
    
    def reset_all(self):
        """重置所有状态"""
        for tool in self.tools.values():
            tool.clear_history()
        self.call_log.clear()
        self.global_delay = 0
        self.global_error_rate = 0.0


# 预设场景
class MockScenarios:
    """Mock预设场景"""
    
    @staticmethod
    def create_file_reading_scenario() -> MockServiceRegistry:
        """创建文件读取场景"""
        registry = MockServiceRegistry()
        
        file_read = MockFileRead()
        file_read.add_virtual_file("/test/file1.txt", "Content of file 1")
        file_read.add_virtual_file("/test/file2.txt", "Content of file 2")
        
        registry.register(file_read)
        return registry
    
    @staticmethod
    def create_error_scenario(error_rate: float = 0.5) -> MockServiceRegistry:
        """创建错误场景"""
        registry = MockServiceRegistry()
        
        file_read = MockFileRead()
        file_read.set_error_rate(error_rate)
        
        registry.register(file_read)
        registry.set_global_error_rate(error_rate)
        return registry
    
    @staticmethod
    def create_slow_scenario(delay_ms: int = 1000) -> MockServiceRegistry:
        """创建慢速场景"""
        registry = MockServiceRegistry()
        
        bash = MockBash()
        bash.set_delay(delay_ms, delay_ms * 2)
        
        registry.register(bash)
        registry.set_global_delay(delay_ms)
        return registry
    
    @staticmethod
    def create_full_suite() -> MockServiceRegistry:
        """创建完整测试套件"""
        registry = MockServiceRegistry()
        
        # 文件操作
        file_read = MockFileRead()
        file_read.add_virtual_file("config.json", '{"key": "value"}')
        file_read.add_virtual_file("data.txt", "Line 1\nLine 2\nLine 3")
        
        file_write = MockFileWrite()
        
        # Bash
        bash = MockBash()
        bash.add_virtual_command("ls -la", "file1.txt\nfile2.txt", "", 0)
        bash.add_virtual_command("pwd", "/home/user", "", 0)
        bash.add_virtual_command("cat config.json", '{"key": "value"}', "", 0)
        
        # 搜索
        search = MockWebSearch()
        search.add_mock_results("python", [
            {"title": "Python Documentation", "url": "https://python.org", "snippet": "Official Python docs"}
        ])
        
        registry.register(file_read)
        registry.register(file_write)
        registry.register(bash)
        registry.register(search)
        
        return registry


# 测试harness
class TestHarness:
    """测试harness - 运行和管理测试"""
    
    def __init__(self):
        self.registry = MockServiceRegistry()
        self.tests: List[Dict] = []
        self.results: List[Dict] = []
        
    def setup(self, scenario: str = "full"):
        """设置测试环境"""
        if scenario == "file_reading":
            self.registry = MockScenarios.create_file_reading_scenario()
        elif scenario == "error":
            self.registry = MockScenarios.create_error_scenario()
        elif scenario == "slow":
            self.registry = MockScenarios.create_slow_scenario()
        else:
            self.registry = MockScenarios.create_full_suite()
    
    def add_test(self, name: str, tool: str, arguments: Dict, 
                 expected_success: bool = True, validator: Optional[Callable] = None):
        """添加测试用例"""
        self.tests.append({
            "name": name,
            "tool": tool,
            "arguments": arguments,
            "expected_success": expected_success,
            "validator": validator
        })
    
    def run_all(self) -> Dict:
        """运行所有测试"""
        self.results = []
        passed = 0
        failed = 0
        
        for test in self.tests:
            result = self._run_single(test)
            self.results.append(result)
            
            if result["passed"]:
                passed += 1
            else:
                failed += 1
        
        return {
            "total": len(self.tests),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(self.tests) if self.tests else 0,
            "results": self.results
        }
    
    def _run_single(self, test: Dict) -> Dict:
        """运行单个测试"""
        start = time.time()
        
        try:
            response = self.registry.execute(
                test["tool"],
                test["arguments"]
            )
            
            # 验证
            passed = response.success == test["expected_success"]
            
            if test.get("validator") and passed:
                passed = test["validator"](response)
            
            return {
                "name": test["name"],
                "passed": passed,
                "duration_ms": (time.time() - start) * 1000,
                "response": response.to_dict()
            }
            
        except Exception as e:
            return {
                "name": test["name"],
                "passed": False,
                "error": str(e),
                "duration_ms": (time.time() - start) * 1000
            }
    
    def generate_report(self) -> str:
        """生成测试报告"""
        summary = self.run_all()
        
        lines = [
            "=" * 60,
            "Mock Service Test Report",
            "=" * 60,
            f"Total: {summary['total']}",
            f"Passed: {summary['passed']}",
            f"Failed: {summary['failed']}",
            f"Success Rate: {summary['success_rate']*100:.1f}%",
            "-" * 60,
            "Details:",
            "-" * 60
        ]
        
        for result in summary["results"]:
            status = "PASS" if result["passed"] else "FAIL"
            lines.append(f"[{status}] {result['name']} ({result.get('duration_ms', 0):.1f}ms)")
            if "error" in result:
                lines.append(f"  Error: {result['error']}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


# 测试代码
if __name__ == "__main__":
    print("Mock Services Test")
    print("=" * 60)
    
    # 创建测试harness
    harness = TestHarness()
    harness.setup("full")
    
    # 添加测试用例
    harness.add_test(
        name="Read virtual file",
        tool="file_read",
        arguments={"file_path": "config.json"},
        expected_success=True,
        validator=lambda r: r.data.get("content") == '{"key": "value"}'
    )
    
    harness.add_test(
        name="Bash ls command",
        tool="bash",
        arguments={"command": "ls -la"},
        expected_success=True
    )
    
    harness.add_test(
        name="Web search",
        tool="web_search",
        arguments={"query": "python"},
        expected_success=True
    )
    
    # 运行测试
    report = harness.generate_report()
    print(report)
    
    print("\n" + "=" * 60)
    print("Mock Services module ready!")
