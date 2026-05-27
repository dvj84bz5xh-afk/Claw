"""
会话管理器 - 基于 Claude Code RuntimeSession 设计

核心改进:
- 会话状态持久化
- 历史记录追踪
- 支持会话恢复
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class HistoryEntry:
    """历史记录条目"""
    timestamp: str
    role: str  # user | assistant | tool
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSession:
    """
    代理会话 - 应用 Claude Code RuntimeSession 模式
    
    字段:
    - session_id: 唯一会话ID
    - prompt: 当前提示词
    - context: 工作区上下文
    - history: 对话历史
    - tools_used: 使用过的工具
    - stream_events: 流式事件记录
    - persisted_path: 持久化路径
    """
    session_id: str
    prompt: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    history: list[HistoryEntry] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    stream_events: list[dict] = field(default_factory=list)
    persisted_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_history(self, role: str, content: str, metadata: dict | None = None) -> None:
        """添加历史记录"""
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.history.append(entry)
        self.updated_at = datetime.now().isoformat()
    
    def add_tool_usage(self, tool_name: str) -> None:
        """记录工具使用"""
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)
        self.updated_at = datetime.now().isoformat()
    
    def add_stream_event(self, event_type: str, data: dict) -> None:
        """添加流式事件"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.stream_events.append(event)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "prompt": self.prompt,
            "context": self.context,
            "history": [asdict(h) for h in self.history],
            "tools_used": self.tools_used,
            "stream_events": self.stream_events,
            "persisted_path": self.persisted_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> AgentSession:
        """从字典创建"""
        history = [HistoryEntry(**h) for h in data.get("history", [])]
        return cls(
            session_id=data["session_id"],
            prompt=data.get("prompt", ""),
            context=data.get("context", {}),
            history=history,
            tools_used=data.get("tools_used", []),
            stream_events=data.get("stream_events", []),
            persisted_path=data.get("persisted_path", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
    
    def as_markdown(self) -> str:
        """生成 Markdown 报告"""
        lines = [
            f"# Agent Session: {self.session_id}",
            "",
            f"**创建时间**: {self.created_at}",
            f"**最后更新**: {self.updated_at}",
            "",
            "## 工作区上下文",
            f"```json\n{json.dumps(self.context, indent=2, ensure_ascii=False)}\n```",
            "",
            "## 对话历史",
        ]
        
        for entry in self.history:
            lines.append(f"\n### {entry.role} ({entry.timestamp})")
            lines.append(entry.content)
        
        if self.tools_used:
            lines.extend([
                "",
                "## 使用过的工具",
                *(f"- {tool}" for tool in self.tools_used),
            ])
        
        if self.stream_events:
            lines.extend([
                "",
                "## 流式事件",
                *(f"- [{e['type']}] {e['timestamp']}" for e in self.stream_events[-10:]),  # 只显示最后10个
            ])
        
        return "\n".join(lines)


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_dir: Path | None = None):
        self.storage_dir = storage_dir or Path.home() / ".claw" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._active_sessions: dict[str, AgentSession] = {}
    
    def create_session(self, prompt: str = "", context: dict | None = None) -> AgentSession:
        """创建新会话"""
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        session = AgentSession(
            session_id=session_id,
            prompt=prompt,
            context=context or {},
        )
        
        self._active_sessions[session_id] = session
        return session
    
    def save_session(self, session: AgentSession) -> Path:
        """持久化会话到文件"""
        file_path = self.storage_dir / f"{session.session_id}.json"
        session.persisted_path = str(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def load_session(self, session_id: str) -> AgentSession | None:
        """从文件加载会话"""
        # 先检查活跃会话
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
        
        # 从文件加载
        file_path = self.storage_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session = AgentSession.from_dict(data)
        self._active_sessions[session_id] = session
        return session
    
    def load_latest_session(self) -> AgentSession | None:
        """加载最新的会话"""
        session_files = sorted(
            self.storage_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not session_files:
            return None
        
        session_id = session_files[0].stem
        return self.load_session(session_id)
    
    def list_sessions(self, limit: int = 10) -> list[tuple[str, str]]:
        """列出所有会话"""
        sessions = []
        for file_path in sorted(self.storage_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                session_id = data.get("session_id", file_path.stem)
                created_at = data.get("created_at", "未知")
                sessions.append((session_id, created_at))
        return sessions
