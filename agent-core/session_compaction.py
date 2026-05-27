"""
会话压缩系统 - 基于 Claw Code 的 compact/session 设计

核心功能:
1. Token估算机制
2. 自动会话压缩
3. 摘要生成算法
4. 关键消息保留策略
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import List, Dict, Any, Optional


class CompactionStrategy(Enum):
    """压缩策略"""
    SUMMARY = "summary"              # 生成摘要
    TRUNCATE = "truncate"            # 截断旧消息
    KEY_PRESERVE = "key_preserve"    # 保留关键消息
    HYBRID = "hybrid"                # 混合策略


@dataclass
class CompactionConfig:
    """压缩配置"""
    # Token阈值
    warning_threshold: int = 4000     # 警告阈值
    compaction_threshold: int = 6000  # 压缩阈值
    max_tokens: int = 8000            # 最大Token限制
    
    # 压缩策略
    strategy: CompactionStrategy = CompactionStrategy.HYBRID
    
    # 保留设置
    preserve_system_messages: bool = True
    preserve_recent_messages: int = 10  # 保留最近N条消息
    preserve_critical_tools: List[str] = field(default_factory=lambda: [
        "execute_command", "write_file", "replace_in_file"
    ])
    
    # 摘要设置
    summary_max_length: int = 500     # 摘要最大长度
    include_tool_outputs: bool = True  # 摘要中包含工具输出


@dataclass
class CompactionResult:
    """压缩结果"""
    original_tokens: int
    compacted_tokens: int
    messages_removed: int
    messages_preserved: int
    summary: str
    compression_ratio: float
    strategy_used: CompactionStrategy


@dataclass
class Message:
    """消息结构"""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None  # tool name
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_critical: bool = False   # 是否为关键消息
    
    def estimate_tokens(self) -> int:
        """估算消息Token数"""
        # 使用简单的字符估算: ~4 characters per token
        content_length = len(self.content)
        # 角色和元数据的额外开销
        overhead = 4  # <im_start>, role, etc.
        return (content_length // 4) + overhead


class TokenEstimator:
    """
    Token估算器
    
    基于 Claw Code 的 estimate_session_tokens 实现
    提供准确的Token数估算
    """
    
    # 不同模型的token计算方式略有不同
    CHARS_PER_TOKEN = 4  # 平均每个token约4个字符
    
    @classmethod
    def estimate_text(cls, text: str) -> int:
        """估算文本的token数"""
        if not text:
            return 0
        
        # 简单的字符数估算
        char_count = len(text)
        
        # 考虑中文字符(通常1-2个token per char)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = char_count - chinese_chars
        
        # 中文按1.5 token/char, 英文按0.25 token/char
        estimated = int(chinese_chars * 1.5 + english_chars * 0.25)
        
        return max(1, estimated)
    
    @classmethod
    def estimate_message(cls, message: Message) -> int:
        """估算单条消息的token数"""
        base_tokens = 3  # 消息格式开销 <im_start>, role, <im_end>
        content_tokens = cls.estimate_text(message.content)
        
        # 工具消息有额外开销
        if message.role == "tool":
            base_tokens += 2  # tool_call_id, name
        
        return base_tokens + content_tokens
    
    @classmethod
    def estimate_messages(cls, messages: List[Message]) -> int:
        """估算消息列表的总token数"""
        total = 0
        for msg in messages:
            total += cls.estimate_message(msg)
        return total
    
    @classmethod
    def estimate_tool_output(cls, output: str) -> int:
        """估算工具输出的token数"""
        return cls.estimate_text(output)


class SessionCompactor:
    """
    会话压缩器
    
    基于 Claw Code 的 compact_session 实现
    实现智能的会话压缩策略
    """
    
    def __init__(self, config: Optional[CompactionConfig] = None):
        self.config = config or CompactionConfig()
        self.estimator = TokenEstimator()
    
    def should_compact(self, messages: List[Message]) -> bool:
        """判断是否需要压缩"""
        total_tokens = self.estimator.estimate_messages(messages)
        return total_tokens > self.config.compaction_threshold
    
    def compact(
        self, 
        messages: List[Message],
        strategy: Optional[CompactionStrategy] = None
    ) -> CompactionResult:
        """
        压缩会话
        
        Args:
            messages: 消息列表
            strategy: 压缩策略，默认使用配置中的策略
            
        Returns:
            CompactionResult: 压缩结果
        """
        if not messages:
            return CompactionResult(
                original_tokens=0,
                compacted_tokens=0,
                messages_removed=0,
                messages_preserved=0,
                summary="",
                compression_ratio=0.0,
                strategy_used=strategy or self.config.strategy
            )
        
        original_tokens = self.estimator.estimate_messages(messages)
        strategy = strategy or self.config.strategy
        
        # 根据策略执行压缩
        if strategy == CompactionStrategy.SUMMARY:
            compacted_messages, summary = self._compact_by_summary(messages)
        elif strategy == CompactionStrategy.TRUNCATE:
            compacted_messages, summary = self._compact_by_truncate(messages)
        elif strategy == CompactionStrategy.KEY_PRESERVE:
            compacted_messages, summary = self._compact_by_key_preserve(messages)
        else:  # HYBRID
            compacted_messages, summary = self._compact_hybrid(messages)
        
        compacted_tokens = self.estimator.estimate_messages(compacted_messages)
        
        return CompactionResult(
            original_tokens=original_tokens,
            compacted_tokens=compacted_tokens,
            messages_removed=len(messages) - len(compacted_messages),
            messages_preserved=len(compacted_messages),
            summary=summary,
            compression_ratio=(original_tokens - compacted_tokens) / max(original_tokens, 1),
            strategy_used=strategy
        )
    
    def _compact_by_summary(self, messages: List[Message]) -> tuple[List[Message], str]:
        """通过生成摘要压缩"""
        # 分离系统消息
        system_msgs = [m for m in messages if m.role == "system"]
        other_msgs = [m for m in messages if m.role != "system"]
        
        # 保留最近的消息
        recent_msgs = other_msgs[-self.config.preserve_recent_messages:]
        old_msgs = other_msgs[:-self.config.preserve_recent_messages]
        
        # 生成旧消息的摘要
        summary = self._generate_summary(old_msgs)
        
        # 组合: 系统消息 + 摘要 + 最近消息
        summary_msg = Message(
            role="system",
            content=f"[会话摘要] {summary}",
            is_critical=True
        )
        
        compacted = system_msgs + [summary_msg] + recent_msgs
        return compacted, summary
    
    def _compact_by_truncate(self, messages: List[Message]) -> tuple[List[Message], str]:
        """通过截断压缩"""
        # 保留系统消息和最近消息
        system_msgs = [m for m in messages if m.role == "system"]
        other_msgs = [m for m in messages if m.role != "system"]
        
        # 计算可保留的消息数
        system_tokens = self.estimator.estimate_messages(system_msgs)
        remaining_budget = self.config.compaction_threshold - system_tokens
        
        preserved = []
        token_count = 0
        
        # 从最新的消息开始保留
        for msg in reversed(other_msgs):
            msg_tokens = self.estimator.estimate_message(msg)
            if token_count + msg_tokens <= remaining_budget:
                preserved.insert(0, msg)
                token_count += msg_tokens
            else:
                break
        
        compacted = system_msgs + preserved
        summary = f"截断了 {len(other_msgs) - len(preserved)} 条旧消息"
        
        return compacted, summary
    
    def _compact_by_key_preserve(self, messages: List[Message]) -> tuple[List[Message], str]:
        """通过保留关键消息压缩"""
        # 标记关键消息
        critical_msgs = []
        normal_msgs = []
        
        for msg in messages:
            if self._is_critical_message(msg):
                msg.is_critical = True
                critical_msgs.append(msg)
            else:
                normal_msgs.append(msg)
        
        # 保留系统消息 + 关键消息 + 最近几条普通消息
        system_msgs = [m for m in critical_msgs if m.role == "system"]
        critical_non_system = [m for m in critical_msgs if m.role != "system"]
        
        # 保留最近的几条普通消息
        recent_normal = normal_msgs[-5:] if len(normal_msgs) > 5 else normal_msgs
        
        # 生成普通消息的摘要
        if len(normal_msgs) > len(recent_normal):
            old_normal = normal_msgs[:-len(recent_normal)] if len(recent_normal) > 0 else normal_msgs
            summary = self._generate_summary(old_normal)
        else:
            summary = ""
        
        compacted = system_msgs + critical_non_system + recent_normal
        
        if summary:
            summary_msg = Message(
                role="system",
                content=f"[会话摘要] {summary}",
                is_critical=True
            )
            compacted.insert(len(system_msgs), summary_msg)
        
        return compacted, summary
    
    def _compact_hybrid(self, messages: List[Message]) -> tuple[List[Message], str]:
        """混合压缩策略"""
        # 先使用关键保留策略
        compacted, summary = self._compact_by_key_preserve(messages)
        
        # 如果还是超过阈值，使用截断策略
        tokens = self.estimator.estimate_messages(compacted)
        if tokens > self.config.compaction_threshold:
            compacted, truncate_summary = self._compact_by_truncate(compacted)
            summary = f"{summary}; {truncate_summary}"
        
        return compacted, summary
    
    def _is_critical_message(self, message: Message) -> bool:
        """判断消息是否关键"""
        # 系统消息通常关键
        if message.role == "system" and self.config.preserve_system_messages:
            return True
        
        # 检查是否是工具调用结果
        if message.role == "tool" and message.name:
            if message.name in self.config.preserve_critical_tools:
                return True
        
        # 检查内容中是否有关键信息
        critical_keywords = [
            "错误", "error", "失败", "failed",
            "创建", "created", "修改", "modified",
            "删除", "deleted", "警告", "warning"
        ]
        content_lower = message.content.lower()
        if any(kw in content_lower for kw in critical_keywords):
            return True
        
        return False
    
    def _generate_summary(self, messages: List[Message]) -> str:
        """生成消息摘要"""
        if not messages:
            return ""
        
        # 提取关键信息
        tool_calls = []
        user_queries = []
        key_results = []
        
        for msg in messages:
            if msg.role == "user":
                # 简化用户查询
                query = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                user_queries.append(query)
            
            elif msg.role == "tool":
                tool_calls.append(msg.name or "unknown")
                # 提取关键结果
                if len(msg.content) < 200:
                    key_results.append(msg.content)
            
            elif msg.role == "assistant":
                # 提取关键决策
                if "完成" in msg.content or "成功" in msg.content:
                    key_results.append(msg.content[:150])
        
        # 构建摘要
        summary_parts = []
        
        if user_queries:
            summary_parts.append(f"用户查询: {len(user_queries)}条")
        
        if tool_calls:
            unique_tools = list(set(tool_calls))
            summary_parts.append(f"使用工具: {', '.join(unique_tools[:5])}")
        
        if key_results:
            summary_parts.append(f"关键结果: {key_results[-1][:100]}")
        
        summary = "; ".join(summary_parts)
        
        # 限制长度
        if len(summary) > self.config.summary_max_length:
            summary = summary[:self.config.summary_max_length] + "..."
        
        return summary


class SessionManager:
    """
    会话管理器 - 增强版
    
    整合持久化、压缩、Token估算
    支持工作区配置中的会话保留设置
    """
    
    def __init__(
        self, 
        session_id: Optional[str] = None,
        config: Optional[CompactionConfig] = None,
        storage_path: Optional[Path] = None
    ):
        self.session_id = session_id or self._generate_session_id()
        self.config = config or CompactionConfig()
        self.compactor = SessionCompactor(self.config)
        self.estimator = TokenEstimator()
        
        # 存储设置
        self.storage_path = storage_path or Path.home() / ".claw" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载工作区会话配置
        self.session_settings = self._load_session_settings()
        
        # 消息列表
        self.messages: List[Message] = []
        self.compaction_history: List[CompactionResult] = []
    
    def _load_session_settings(self) -> Dict[str, Any]:
        """加载会话保留配置"""
        default_settings = {
            'retention_days': None,  # None = 无限保留
            'auto_cleanup': False,
            'max_sessions': None,
            'compression_enabled': True,
            'persistence_enabled': True,
        }
        
        try:
            # 尝试从工作区配置加载
            workspace_config = Path.cwd() / '.workbuddy' / 'workspace.json'
            if not workspace_config.exists():
                workspace_config = Path.home() / '.workbuddy' / 'workspace.json'
            
            if workspace_config.exists():
                with open(workspace_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'session' in config:
                        default_settings.update(config['session'])
        except Exception:
            pass
        
        return default_settings
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def add_message(
        self, 
        role: str, 
        content: str, 
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """添加消息"""
        message = Message(
            role=role,
            content=content,
            name=name,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # 检查是否需要压缩
        if self.compactor.should_compact(self.messages):
            self._auto_compact()
        
        return message
    
    def _auto_compact(self) -> CompactionResult:
        """自动压缩"""
        result = self.compactor.compact(self.messages)
        
        # 重构消息列表
        # 注意：这里简化处理，实际应该根据compact返回的消息列表重建
        self.compaction_history.append(result)
        
        return result
    
    def get_token_count(self) -> int:
        """获取当前Token数"""
        return self.estimator.estimate_messages(self.messages)
    
    def get_status(self) -> Dict[str, Any]:
        """获取会话状态"""
        token_count = self.get_token_count()
        
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "token_count": token_count,
            "warning_threshold": self.config.warning_threshold,
            "compaction_threshold": self.config.compaction_threshold,
            "needs_compaction": token_count > self.config.compaction_threshold,
            "compression_history": len(self.compaction_history),
            "session_settings": {
                "retention_days": self.session_settings.get('retention_days'),
                "auto_cleanup": self.session_settings.get('auto_cleanup'),
                "max_sessions": self.session_settings.get('max_sessions'),
                "compression_enabled": self.session_settings.get('compression_enabled'),
                "persistence_enabled": self.session_settings.get('persistence_enabled'),
            }
        }
    
    def save(self) -> Path:
        """保存会话"""
        session_file = self.storage_path / f"{self.session_id}.json"
        
        data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "name": m.name,
                    "timestamp": m.timestamp.isoformat(),
                    "is_critical": m.is_critical
                }
                for m in self.messages
            ],
            "compaction_history": [
                {
                    "original_tokens": r.original_tokens,
                    "compacted_tokens": r.compacted_tokens,
                    "compression_ratio": r.compression_ratio,
                    "strategy": r.strategy_used.value
                }
                for r in self.compaction_history
            ]
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return session_file
    
    @classmethod
    def load(cls, session_id: str, storage_path: Optional[Path] = None) -> SessionManager:
        """加载会话"""
        storage = storage_path or Path.home() / ".claw" / "sessions"
        session_file = storage / f"{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manager = cls(session_id=session_id, storage_path=storage)
        
        # 恢复消息
        for msg_data in data.get("messages", []):
            msg = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                name=msg_data.get("name"),
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                is_critical=msg_data.get("is_critical", False)
            )
            manager.messages.append(msg)
        
        return manager


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("会话压缩系统测试")
    print("=" * 60)
    
    # 测试Token估算
    print("\n[测试1] Token估算")
    text = "这是一段测试文本，用于估算Token数量。"
    tokens = TokenEstimator.estimate_text(text)
    print(f"  文本: {text[:30]}...")
    print(f"  估算Token: {tokens}")
    
    # 测试消息Token估算
    print("\n[测试2] 消息Token估算")
    msg = Message(role="user", content="请帮我创建一个Python文件")
    msg_tokens = TokenEstimator.estimate_message(msg)
    print(f"  消息: {msg.content}")
    print(f"  估算Token: {msg_tokens}")
    
    # 测试会话管理器
    print("\n[测试3] 会话管理器")
    manager = SessionManager()
    
    # 添加一些消息
    for i in range(20):
        manager.add_message(
            role="user" if i % 2 == 0 else "assistant",
            content=f"这是第{i+1}条消息，用于测试会话压缩功能。" * 10
        )
    
    status = manager.get_status()
    print(f"  会话ID: {status['session_id']}")
    print(f"  消息数: {status['message_count']}")
    print(f"  Token数: {status['token_count']}")
    print(f"  需要压缩: {status['needs_compaction']}")
    
    # 测试压缩
    if status['needs_compaction']:
        print("\n[测试4] 执行压缩")
        result = manager._auto_compact()
        print(f"  原始Token: {result.original_tokens}")
        print(f"  压缩后Token: {result.compacted_tokens}")
        print(f"  压缩率: {result.compression_ratio:.2%}")
        print(f"  使用策略: {result.strategy_used.value}")
    
    # 测试保存
    print("\n[测试5] 保存会话")
    session_file = manager.save()
    print(f"  保存到: {session_file}")
    
    # 测试加载
    print("\n[测试6] 加载会话")
    loaded = SessionManager.load(manager.session_id)
    loaded_status = loaded.get_status()
    print(f"  加载成功")
    print(f"  消息数: {loaded_status['message_count']}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
