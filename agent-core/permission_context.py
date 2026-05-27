"""
权限上下文 - 基于 Claude Code 权限系统设计

核心改进:
- 三级权限模式: read-only | workspace-write | danger-full-access
- 工具级别的权限控制
- 操作前的权限检查
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class PermissionLevel(Enum):
    """权限级别"""
    READ_ONLY = "read-only"
    WORKSPACE_WRITE = "workspace-write"
    DANGER_FULL_ACCESS = "danger-full-access"


@dataclass
class PermissionContext:
    """
    权限上下文 - 应用 Claude Code ToolPermissionContext 模式
    
    字段:
    - level: 当前权限级别
    - denied_tools: 明确禁用的工具
    - allowed_tools: 白名单模式下的允许工具
    - deny_prefixes: 按前缀禁用
    """
    level: PermissionLevel = PermissionLevel.READ_ONLY
    denied_tools: frozenset[str] = field(default_factory=frozenset)
    allowed_tools: frozenset[str] = field(default_factory=frozenset)
    deny_prefixes: frozenset[str] = field(default_factory=frozenset)
    
    # 工具所需的最小权限映射
    TOOL_PERMISSION_MAP: dict[str, PermissionLevel] = field(default_factory=lambda: {
        # 只读工具
        "read_file": PermissionLevel.READ_ONLY,
        "list_dir": PermissionLevel.READ_ONLY,
        "search_file": PermissionLevel.READ_ONLY,
        "search_content": PermissionLevel.READ_ONLY,
        "web_search": PermissionLevel.READ_ONLY,
        "web_fetch": PermissionLevel.READ_ONLY,
        
        # 写入工具
        "write_to_file": PermissionLevel.WORKSPACE_WRITE,
        "replace_in_file": PermissionLevel.WORKSPACE_WRITE,
        "delete_file": PermissionLevel.WORKSPACE_WRITE,
        "execute_command": PermissionLevel.WORKSPACE_WRITE,
        
        # 危险工具
        "bash": PermissionLevel.DANGER_FULL_ACCESS,
        "eval": PermissionLevel.DANGER_FULL_ACCESS,
        "exec": PermissionLevel.DANGER_FULL_ACCESS,
    })
    
    def can_use_tool(self, tool_name: str) -> tuple[bool, str]:
        """
        检查是否可以使用工具
        
        返回: (是否允许, 拒绝原因)
        """
        # 检查是否被明确禁用
        if tool_name in self.denied_tools:
            return False, f"工具 '{tool_name}' 已被明确禁用"
        
        # 检查前缀禁用
        for prefix in self.deny_prefixes:
            if tool_name.startswith(prefix):
                return False, f"工具 '{tool_name}' 匹配禁用前缀 '{prefix}'"
        
        # 检查白名单
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return False, f"工具 '{tool_name}' 不在允许列表中"
        
        # 检查权限级别
        required_level = self.TOOL_PERMISSION_MAP.get(tool_name, PermissionLevel.WORKSPACE_WRITE)
        
        level_order = {
            PermissionLevel.READ_ONLY: 0,
            PermissionLevel.WORKSPACE_WRITE: 1,
            PermissionLevel.DANGER_FULL_ACCESS: 2,
        }
        
        if level_order[self.level] < level_order[required_level]:
            return False, f"工具 '{tool_name}' 需要 {required_level.value} 权限，当前为 {self.level.value}"
        
        return True, ""
    
    def assert_can_use_tool(self, tool_name: str) -> None:
        """断言可以使用工具，否则抛出异常"""
        allowed, reason = self.can_use_tool(tool_name)
        if not allowed:
            raise PermissionError(reason)
    
    def with_level(self, level: PermissionLevel) -> PermissionContext:
        """创建具有新权限级别的上下文"""
        return PermissionContext(
            level=level,
            denied_tools=self.denied_tools,
            allowed_tools=self.allowed_tools,
            deny_prefixes=self.deny_prefixes,
        )
    
    def deny_tool(self, tool_name: str) -> PermissionContext:
        """禁用特定工具"""
        new_denied = set(self.denied_tools) | {tool_name}
        return PermissionContext(
            level=self.level,
            denied_tools=frozenset(new_denied),
            allowed_tools=self.allowed_tools,
            deny_prefixes=self.deny_prefixes,
        )
    
    def allow_only(self, tool_names: list[str]) -> PermissionContext:
        """仅允许特定工具（白名单模式）"""
        return PermissionContext(
            level=self.level,
            denied_tools=self.denied_tools,
            allowed_tools=frozenset(tool_names),
            deny_prefixes=self.deny_prefixes,
        )
    
    def get_allowed_tools(self, all_tools: list[str]) -> list[str]:
        """从所有工具中筛选出允许使用的"""
        allowed = []
        for tool in all_tools:
            can_use, _ = self.can_use_tool(tool)
            if can_use:
                allowed.append(tool)
        return allowed
    
    def wrap_tool(self, tool_name: str, executor: Callable) -> Callable:
        """
        包装工具执行器，添加权限检查
        
        用法:
            @context.wrap_tool("bash")
            def bash_executor(cmd):
                return os.system(cmd)
        """
        def wrapper(*args, **kwargs):
            self.assert_can_use_tool(tool_name)
            return executor(*args, **kwargs)
        return wrapper
    
    def as_markdown(self) -> str:
        """生成权限配置的 Markdown 报告"""
        lines = [
            "# 权限上下文配置",
            "",
            f"**当前级别**: `{self.level.value}`",
            "",
        ]
        
        if self.denied_tools:
            lines.extend([
                "## 禁用工具",
                *(f"- `{tool}`" for tool in sorted(self.denied_tools)),
                "",
            ])
        
        if self.allowed_tools:
            lines.extend([
                "## 允许工具（白名单）",
                *(f"- `{tool}`" for tool in sorted(self.allowed_tools)),
                "",
            ])
        
        if self.deny_prefixes:
            lines.extend([
                "## 禁用前缀",
                *(f"- `{prefix}*`" for prefix in sorted(self.deny_prefixes)),
                "",
            ])
        
        lines.extend([
            "## 工具权限映射",
            *(f"- `{tool}` → {level.value}" for tool, level in sorted(self.TOOL_PERMISSION_MAP.items())),
        ])
        
        return "\n".join(lines)
