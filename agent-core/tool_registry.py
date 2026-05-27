"""
工具注册表 - 基于 Claude Code tools_snapshot.json 模式

核心改进:
- 工具清单从代码分离，便于动态扩展
- 自动发现并注册工具
- 工具执行结果标准化
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Any
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class ToolDefinition:
    """工具定义 - 不可变数据结构"""
    name: str
    description: str
    source_hint: str  # 工具来源路径
    parameters: dict[str, Any] = field(default_factory=dict)
    permission_level: str = "read"  # read | write | danger


@dataclass
class ToolExecution:
    """工具执行结果"""
    name: str
    source_hint: str
    prompt: str
    handled: bool
    message: str
    result: Any = None
    error: str | None = None


class ToolRegistry:
    """
    工具注册表 - 管理所有可用工具
    
    应用 Claude Code 的设计:
    1. 从 JSON 加载工具清单
    2. 支持动态注册
    3. 权限检查
    """
    
    def __init__(self, snapshot_path: Path | None = None):
        self._tools: dict[str, ToolDefinition] = {}
        self._executors: dict[str, Callable] = {}
        self._snapshot_path = snapshot_path or Path(__file__).parent / 'tools_snapshot.json'
        self._load_builtin_tools()
    
    def _load_builtin_tools(self) -> None:
        """从快照文件加载工具清单"""
        if self._snapshot_path.exists():
            with open(self._snapshot_path, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
                for tool_data in tools_data:
                    tool = ToolDefinition(**tool_data)
                    self._tools[tool.name] = tool
    
    def register_tool(
        self, 
        name: str, 
        description: str,
        executor: Callable,
        permission_level: str = "read",
        parameters: dict | None = None
    ) -> None:
        """动态注册工具"""
        tool = ToolDefinition(
            name=name,
            description=description,
            source_hint=f"runtime/{name}.py",
            parameters=parameters or {},
            permission_level=permission_level
        )
        self._tools[name] = tool
        self._executors[name] = executor
    
    def get_tool(self, name: str) -> ToolDefinition | None:
        """获取工具定义"""
        return self._tools.get(name)
    
    def list_tools(self, permission_filter: str | None = None) -> list[ToolDefinition]:
        """列出所有工具，可选权限过滤"""
        tools = list(self._tools.values())
        if permission_filter:
            tools = [t for t in tools if t.permission_level == permission_filter]
        return tools
    
    def execute_tool(
        self, 
        name: str, 
        prompt: str = "", 
        context: dict | None = None
    ) -> ToolExecution:
        """执行工具"""
        tool = self.get_tool(name)
        if tool is None:
            return ToolExecution(
                name=name,
                source_hint="",
                prompt=prompt,
                handled=False,
                message=f"未知工具: {name}"
            )
        
        executor = self._executors.get(name)
        if executor is None:
            return ToolExecution(
                name=name,
                source_hint=tool.source_hint,
                prompt=prompt,
                handled=False,
                message=f"工具 {name} 没有注册执行器"
            )
        
        try:
            result = executor(prompt, context or {})
            return ToolExecution(
                name=name,
                source_hint=tool.source_hint,
                prompt=prompt,
                handled=True,
                message=f"工具 '{name}' 执行成功",
                result=result
            )
        except Exception as e:
            return ToolExecution(
                name=name,
                source_hint=tool.source_hint,
                prompt=prompt,
                handled=False,
                message=f"工具执行失败: {str(e)}",
                error=str(e)
            )
    
    def route_prompt(self, prompt: str, limit: int = 5) -> list[tuple[ToolDefinition, int]]:
        """
        基于提示词匹配最佳工具
        
        应用 Claude Code 的 route_prompt 算法
        """
        tokens = {token.lower() for token in prompt.replace('/', ' ').replace('-', ' ').split() if token}
        
        matches = []
        for tool in self._tools.values():
            score = 0
            tool_tokens = set(tool.name.lower().replace('_', ' ').split())
            tool_tokens.update(tool.description.lower().split())
            
            # 计算匹配分数
            matching_tokens = tokens & tool_tokens
            score = len(matching_tokens) * 10
            
            # 额外加分：名称完全匹配
            if any(token == tool.name.lower() for token in tokens):
                score += 50
            
            if score > 0:
                matches.append((tool, score))
        
        # 按分数排序
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
