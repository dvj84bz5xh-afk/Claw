"""
命令路由器 - 基于 Claude Code Slash Commands 设计

核心改进:
- 支持 /command 风格的命令
- 命令自动发现
- 命令帮助系统
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Any
from functools import lru_cache


@dataclass(frozen=True)
class CommandDefinition:
    """命令定义"""
    name: str  # 不带 / 前缀
    description: str
    source_hint: str
    handler: Callable | None = None
    aliases: tuple[str, ...] = ()
    hidden: bool = False  # 是否在帮助中显示


@dataclass
class CommandExecution:
    """命令执行结果"""
    name: str
    source_hint: str
    prompt: str
    handled: bool
    message: str
    result: Any = None


class CommandRouter:
    """
    命令路由器 - 管理所有斜杠命令
    
    应用 Claude Code 的命令系统:
    - /help, /status, /cost, /doctor 等
    """
    
    COMMAND_PATTERN = re.compile(r"^/(\w+)(?:\s+(.*))?$", re.MULTILINE)
    
    def __init__(self):
        self._commands: dict[str, CommandDefinition] = {}
        self._handlers: dict[str, Callable] = {}
        self._register_builtin_commands()
    
    def _register_builtin_commands(self) -> None:
        """注册内置命令"""
        builtins = [
            CommandDefinition("help", "显示帮助信息", "commands/help.py", hidden=True),
            CommandDefinition("status", "显示当前状态", "commands/status.py"),
            CommandDefinition("cost", "显示成本统计", "commands/cost.py"),
            CommandDefinition("doctor", "运行诊断检查", "commands/doctor.py"),
            CommandDefinition("history", "显示对话历史", "commands/history.py"),
            CommandDefinition("tools", "列出可用工具", "commands/tools.py"),
            CommandDefinition("clear", "清除屏幕", "commands/clear.py"),
            CommandDefinition("exit", "退出会话", "commands/exit.py", aliases=("quit",)),
        ]
        for cmd in builtins:
            self.register_command(cmd)
    
    def register_command(
        self, 
        command: CommandDefinition,
        handler: Callable | None = None
    ) -> None:
        """注册命令"""
        self._commands[command.name] = command
        
        # 注册别名
        for alias in command.aliases:
            self._commands[alias] = command
        
        # 注册处理器
        if handler:
            self._handlers[command.name] = handler
            for alias in command.aliases:
                self._handlers[alias] = handler
        elif command.handler:
            self._handlers[command.name] = command.handler
            for alias in command.aliases:
                self._handlers[alias] = command.handler
    
    def register_simple(
        self,
        name: str,
        description: str,
        handler: Callable,
        aliases: tuple[str, ...] = (),
        hidden: bool = False
    ) -> None:
        """简化的命令注册"""
        cmd = CommandDefinition(
            name=name,
            description=description,
            source_hint=f"runtime/{name}.py",
            aliases=aliases,
            hidden=hidden
        )
        self.register_command(cmd, handler)
    
    def get_command(self, name: str) -> CommandDefinition | None:
        """获取命令定义"""
        # 去掉 / 前缀
        name = name.lstrip('/')
        return self._commands.get(name)
    
    def list_commands(self, include_hidden: bool = False) -> list[CommandDefinition]:
        """列出所有命令"""
        commands = []
        seen = set()
        for cmd in self._commands.values():
            if cmd.name not in seen:  # 避免别名重复
                if include_hidden or not cmd.hidden:
                    commands.append(cmd)
                    seen.add(cmd.name)
        return sorted(commands, key=lambda c: c.name)
    
    def is_command(self, text: str) -> bool:
        """检查文本是否为命令"""
        return bool(self.COMMAND_PATTERN.match(text.strip()))
    
    def parse_command(self, text: str) -> tuple[str, str] | None:
        """解析命令，返回 (命令名, 参数)"""
        match = self.COMMAND_PATTERN.match(text.strip())
        if match:
            return match.group(1), match.group(2) or ""
        return None
    
    def execute_command(
        self, 
        text: str, 
        context: dict | None = None
    ) -> CommandExecution | None:
        """执行命令"""
        parsed = self.parse_command(text)
        if not parsed:
            return None
        
        name, args = parsed
        cmd = self.get_command(name)
        
        if cmd is None:
            return CommandExecution(
                name=name,
                source_hint="",
                prompt=text,
                handled=False,
                message=f"未知命令: /{name}，使用 /help 查看可用命令"
            )
        
        handler = self._handlers.get(name)
        if handler is None:
            return CommandExecution(
                name=name,
                source_hint=cmd.source_hint,
                prompt=text,
                handled=False,
                message=f"命令 /{name} 没有注册处理器"
            )
        
        try:
            result = handler(args, context or {})
            return CommandExecution(
                name=name,
                source_hint=cmd.source_hint,
                prompt=text,
                handled=True,
                message=f"命令 /{name} 执行成功",
                result=result
            )
        except Exception as e:
            return CommandExecution(
                name=name,
                source_hint=cmd.source_hint,
                prompt=text,
                handled=False,
                message=f"命令执行失败: {str(e)}",
                result=None
            )
    
    def route_prompt(self, prompt: str) -> tuple[bool, CommandExecution | None]:
        """
        路由提示词
        
        返回: (是否为命令, 执行结果)
        """
        if self.is_command(prompt):
            return True, self.execute_command(prompt)
        return False, None
    
    def render_help(self) -> str:
        """渲染帮助信息"""
        lines = [
            "# 可用命令",
            "",
            "| 命令 | 描述 | 别名 |",
            "|------|------|------|",
        ]
        
        for cmd in self.list_commands():
            aliases = ", ".join(f"/{a}" for a in cmd.aliases) if cmd.aliases else "-"
            lines.append(f"| /{cmd.name} | {cmd.description} | {aliases} |")
        
        lines.extend([
            "",
            "**用法**: 直接输入 `/命令名` 即可执行",
        ])
        
        return "\n".join(lines)
    
    def create_help_handler(self) -> Callable:
        """创建 /help 命令的处理器"""
        def handler(args: str, context: dict) -> str:
            if args.strip():
                # 查询特定命令的帮助
                cmd = self.get_command(args.strip())
                if cmd:
                    return f"**/{cmd.name}**: {cmd.description}\n\n来源: {cmd.source_hint}"
                return f"未知命令: /{args.strip()}"
            return self.render_help()
        return handler
    
    def bind_help_command(self) -> None:
        """绑定 /help 命令"""
        self.register_simple(
            "help",
            "显示帮助信息",
            self.create_help_handler(),
            hidden=True
        )
