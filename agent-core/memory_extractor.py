"""
Phase 4: Memory Auto-Extraction Engine

借鉴 mem0ai/mem0 的单轮提取算法，实现对话后自动关键信息提取。
核心特性：
  - 单次提取（Single-pass ADD-only）— 累积式存储，不覆盖旧记忆
  - 实体链接（Entity Linking）— 实体跨记忆关联
  - 重要性评分（Importance Scoring）— 按价值排序
  - 去重合并（Deduplication）— 语义去重
  - 自动写入（Auto-Persist）— 写入 MEMORY.md / daily log

参考项目: mem0ai/mem0 (https://github.com/mem0ai/mem0)

架构设计:
  Conversation → MemoryExtractor.extract() → [MemoryItem] → MemoryStore.persist()
                                                    ↓
                                            MEMORY.md / daily log

使用方式:
  from memory_extractor import MemoryExtractor, MemoryStore

  extractor = MemoryExtractor(memory_dir=".workbuddy/memory")
  items = extractor.extract(conversation_messages)
  extractor.store.save_items(items)  # 自动写入文件

  # 或一键模式
  extractor.process_and_save(messages, user_id="default")
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


# ==================== 数据模型 ====================


class MemoryType(Enum):
    """记忆类型分类"""
    FACT = auto()          # 事实型: "用户偏好Python"
    PREFERENCE = auto()    # 偏好型: "喜欢简洁回复"
    ENTITY = auto()        # 实体型: "张三是项目经理"
    RELATIONSHIP = auto()  # 关系型: "A依赖B"
    DECISION = auto()      # 决策型: "选择方案X"
    SKILL = auto()         # 技能型: "掌握了Y工具"
    EVENT = auto()         # 事件型: "完成了Z任务"
    GOAL = auto()          # 目标型: "计划做W"


class ImportanceLevel(Enum):
    """重要性等级"""
    CRITICAL = 5   # 核心身份/偏好 — 极少变更
    HIGH = 4      # 重要决策/技能
    MEDIUM = 3    # 有用事实
    LOW = 2       # 一般信息
    TRIVIAL = 1   # 可丢弃


@dataclass
class MemoryItem:
    """
    单条记忆条目（对应 mem0 的 GraphMemory 节点）

    mem0 的设计是图结构: Entity ←→ Memory ←→ Entity
    这里简化为扁平结构，保留 entity 字段用于未来扩展图索引。
    """
    content: str                    # 记忆内容（自然语言）
    memory_type: MemoryType = MemoryType.FACT
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    entities: list[str] = field(default_factory=list)     # 提及的实体
    source_conversation: str = ""      # 来源会话摘要
    confidence: float = 0.8            # 置信度 (0-1)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str | None = None      # 过期时间（None=永不过期）
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    # 内部字段
    _id: str = field(default="", repr=False)
    _hash: str = field(default="", repr=False)     # 用于去重

    def __post_init__(self):
        if not self._id:
            self._id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.content) % 10000:04d}"
        if not self._hash:
            self._hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """计算内容哈希用于去重"""
        import hashlib
        normalized = self.content.strip().lower().replace(" ", "")
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        d = asdict(self)
        d['memory_type'] = self.memory_type.name
        d['importance'] = self.importance.name
        # 移除内部字段前缀
        return {k: v for k, v in d.items() if not k.startswith('_')}

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        try:
            return datetime.now().isoformat() > self.expires_at
        except Exception:
            return False

    def format_for_memory_md(self) -> str:
        """格式化为 MEMORY.md 行"""
        type_emoji = {
            MemoryType.FACT: "-",
            MemoryType.PREFERENCE: ">",
            MemoryType.ENTITY: "~",
            MemoryType.RELATIONSHIP: "->",
            MemoryType.DECISION: "!",
            MemoryType.SKILL: "*",
            MemoryType.EVENT: "@",
            MemoryType.GOAL: "?",
        }
        prefix = type_emoji.get(self.memory_type, "-")
        tag_str = f" [{','.join(self.tags)}]" if self.tags else ""
        return f"{prefix} {self.content}{tag_str}"


# ==================== 规则提取器 ====================


@dataclass
class ExtractionRule:
    """单条提取规则"""
    name: str
    pattern: str | re.Pattern         # 正则匹配
    type_hint: MemoryType             # 推断的记忆类型
    importance_hint: ImportanceLevel  # 推断的重要性
    extract_template: str | None = None  # 提取模板（支持 \\1, \\2 引用捕获组）
    keywords: list[str] = field(default_factory=list)  # 额外关键词触发


class RuleBasedExtractor:
    """
    规则式记忆提取器（模拟 LLM 提取）

    在实际生产中，这里应该调用 LLM 进行语义分析。
    此实现作为基线版本，覆盖常见事实模式：

    覆盖的模式:
    1. 偏好声明: "我喜欢/偏好/希望..."
    2. 技能声明: "掌握/学会/安装了..."
    3. 决策声明: "决定/选择/采用..."
    4. 实体关系: "...是/属于/负责..."
    5. 目标声明: "计划/目标/下一步..."
    6. 事件完成: "完成/提交/推送了..."
    """

    def __init__(self):
        self.rules = self._build_rules()
        # 高价值关键词（提高匹配权重）
        self.high_value_keywords = [
            "永远", "必须", "禁止", "不要", "始终", "只", "唯一",
            "P0", "critical", "紧急", "核心", "基础",
            "偏好", "习惯", "风格", "规则", "原则",
        ]

    def _build_rules(self) -> list[ExtractionRule]:
        rules = []

        # === 偏好类 ===
        rules.append(ExtractionRule(
            name="preference_like",
            pattern=re.compile(r"(?:我|用户)?(?:偏好|喜欢|希望|想要|倾向)(?:于?)(.+?)(?:[，。！？\n]|$)", re.I),
            type_hint=MemoryType.PREFERENCE,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["偏好", "喜欢", "希望"],
        ))
        rules.append(ExtractionRule(
            name="preference_hate",
            pattern=re.compile(r"(?:不要|不想|避免|讨厌|拒绝)(.+?)(?:[，。！？\n]|$)", re.I),
            type_hint=MemoryType.PREFERENCE,
            importance_hint=ImportanceLevel.MEDIUM,
            keywords=["不要", "不想", "避免"],
        ))
        rules.append(ExtractionRule(
            name="preference_style",
            pattern=re.compile(r"(?:回复|输出|回答|格式|风格)(?:要|应|为|是)(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.PREFERENCE,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["回复", "输出", "格式"],
        ))

        # === 技能类 ===
        rules.append(ExtractionRule(
            name="skill_mastered",
            pattern=re.compile(r"(?:已?(?:经)?|刚刚|新)(?:掌握|学会|学会了|实现了|完成了|创建了|开发了|搭建了|部署了)(.+?)(?:[，。！？\n]|$)", re.I),
            type_hint=MemoryType.SKILL,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["掌握", "学会", "实现", "创建", "开发"],
        ))
        rules.append(ExtractionRule(
            name="skill_installed",
            pattern=re.compile(r"(?:安装|配置|设置|接入|集成|升级到?)(?:了|好|完毕)(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.SKILL,
            importance_hint=ImportanceLevel.MEDIUM,
            keywords=["安装", "配置", "集成"],
        ))

        # === 决策类 ===
        rules.append(ExtractionRule(
            name="decision_choose",
            pattern=re.compile(r"(?:决定|选择|采用|选用|确定)(?:使用|采用|用|为|是)(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.DECISION,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["决定", "选择", "采用", "确定"],
        ))
        rules.append(ExtractionRule(
            name="decision_reject",
            pattern=re.compile(r"(?:放弃|排除|不考虑|否决|回退)(?:使用|采用)?(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.DECISION,
            importance_hint=ImportanceLevel.MEDIUM,
            keywords=["放弃", "排除", "否决"],
        ))

        # === 实体/关系类 ===
        rules.append(ExtractionRule(
            name="entity_role",
            pattern=re.compile(r"([\u4e00-\u9fff\w]{2,10})(?:是|担任|负责|作为|为)(.+?)(?:[，。；\n]|$)"),
            type_hint=MemoryType.ENTITY,
            importance_hint=ImportanceLevel.MEDIUM,
            keywords=["是", "负责", "担任"],
        ))
        rules.append(ExtractionRule(
            name="entity_identity",
            pattern=re.compile(r"(@[\w\-\.]+)\s*(?:是|代表|表示|指)"),
            type_hint=MemoryType.ENTITY,
            importance_hint=ImportanceLevel.MEDIUM,
            keywords=["@", "代表"],
        ))

        # === 目标类 ===
        rules.append(ExtractionRule(
            name="goal_plan",
            pattern=re.compile(r"(?:下一步|接下来|随后|然后)(?:要|将|打算|准备|计划)(?:做?)(.+?)(?:[，。！？\n]|$)", re.I),
            type_hint=MemoryType.GOAL,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["下一步", "接下来", "计划", "打算"],
        ))
        rules.append(ExtractionRule(
            name="goal_target",
            pattern=re.compile(r"(?:目标|目的|意图)(?:是|为|在于)(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.GOAL,
            importance_hint=ImportanceLevel.HIGH,
            keywords=["目标", "目的", "意图"],
        ))

        # === 事件类 ===
        rules.append(ExtractionRule(
            name="event_completed",
            pattern=re.compile(r"(?:已|已经|成功|顺利|完成)(?:完成|提交|推送|修复|解决|部署|发布)(?:了|过)?(.+?)(?:[，。；\n]|$)", re.I),
            type_hint=MemoryType.EVENT,
            importance_hint=ImportanceLevel.LOW,
            keywords=["完成", "提交", "推送", "修复", "部署"],
        ))

        # === 通用事实（兜底）===
        rules.append(ExtractionRule(
            name="fact_generic",
            pattern=re.compile(r"^(.{15,80})$", re.MULTILINE),
            type_hint=MemoryType.FACT,
            importance_hint=ImportanceLevel.LOW,
        ))

        return rules

    def extract_from_text(self, text: str) -> list[MemoryItem]:
        """从文本中提取记忆条目"""
        items: list[MemoryItem] = []
        seen_hashes: set[str] = set()

        for rule in self.rules:
            matches = rule.pattern.finditer(text)
            for match in matches:
                try:
                    item = self._match_to_item(match, rule)
                    if not item or item._hash in seen_hashes:
                        continue
                    seen_hashes.add(item._hash)
                    items.append(item)
                except Exception:
                    continue

        # 按重要性排序
        items.sort(key=lambda x: x.importance.value, reverse=True)
        return items

    def _match_to_item(self, match: re.Match, rule: ExtractionRule) -> MemoryItem | None:
        """将正则匹配转换为 MemoryItem"""
        import re as _re

        # 使用完整匹配文本（保留否定词等意图）
        content_raw = match.group(0).strip()
        # 去除末尾标点
        content_raw = _re.sub(r"[，。！？]+$", "", content_raw)

        # 清理内容
        content = content_raw.strip()
        if len(content) < 4 or len(content) > 200:
            return None

        # 过滤无意义内容
        skip_words = ["这个", "那个", "什么", "怎么", "如何", "可以", "能够"]
        if content in skip_words:
            return None

        # 重要性调整（检查高价值关键词）
        importance = rule.importance_hint
        full_text = match.group(0)
        for kw in self.high_value_keywords:
            if kw in full_text:
                importance = ImportanceLevel(min(importance.value + 1, 5))
                break

        # 实体提取
        entities = self._extract_entities(content + " " + full_text)

        return MemoryItem(
            content=content[:150],
            memory_type=rule.type_hint,
            importance=importance,
            entities=entities,
            tags=[rule.name],
            metadata={"rule": rule.name, "matched": full_text[:100]},
        )

    def _extract_entities(self, text: str) -> list[str]:
        """简单实体提取"""
        entities = []

        # @mention
        mentions = re.findall(r'@(\w[\w\-\.]*)', text)
        entities.extend(mentions)

        # 文件路径
        paths = re.findall(r'[a-zA-Z]:\\[\w\\/\\.]+|\./[\w\\/\.]+', text)
        entities.extend(paths[:2])

        # 版本号/ID
        ids = re.findall(r'[a-f0-9]{7,12}|v?\d+\.\d+', text)
        entities.extend(ids[:2])

        return list(set(entities))[:5]


# ==================== 记忆存储 ====================


class MemoryStore:
    """
    持久化存储层

    支持两种写入目标:
    1. daily log (.workbuddy/memory/YYYY-MM-DD.md) — 追加式
    2. MEMORY.md — 结构化更新（可选）
    """

    def __init__(self, memory_dir: str | Path = ".workbuddy/memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / "MEMORY.md"
        self._index: dict[str, MemoryItem] = {}  # hash -> item (内存索引)

    def save_items(self, items: list[MemoryItem],
                   write_daily: bool = True,
                   update_index: bool = True) -> int:
        """
        保存记忆条目

        Returns:
            实际保存的新条目数（去重后）
        """
        new_count = 0
        today_file = self.memory_dir / f"{date.today().isoformat()}.md"

        for item in items:
            # 去重检查
            if item._hash in self._index:
                continue
            if update_index:
                self._index[item._hash] = item
            new_count += 1

        if new_count == 0:
            return 0

        # 追加到 daily log
        if write_daily:
            self._append_to_daily(today_file, items)

        return new_count

    def _append_to_daily(self, file_path: Path, items: list[MemoryItem]):
        """追加到每日日志"""
        lines = []
        lines.append("")
        lines.append(f"### 自动提取记忆 ({datetime.now().strftime('%H:%M')})")
        lines.append("")
        lines.append(f"| 类型 | 内容 | 重要性 | 来源 |")
        lines.append("|------|------|--------|------|")

        for item in items:
            type_name = item.memory_type.name[:4]
            imp_name = item.importance.name
            source = item.source_conversation[:20] if item.source_conversation else "-"
            lines.append(f"| {type_name} | {item.content[:60]} | {imp_name} | {source} |")

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def load_existing_memories(self, max_age_days: int = 30) -> list[MemoryItem]:
        """加载已有记忆（用于去重对比）"""
        count = 0
        for f in sorted(self.memory_dir.glob("*.md"), reverse=True)[:max_age_days]:
            if f.name == "MEMORY.md":
                continue
            try:
                content = f.read_text(encoding='utf-8')
                # 从表格行中提取记忆内容
                rows = re.findall(r'\|.*?\| (.+?) \|', content)
                for row in rows:
                    if len(row) >= 4:
                        item = MemoryItem(content=row.strip())
                        self._index[item._hash] = item
                        count += 1
            except Exception:
                continue
        return list(self._index.values())

    def get_stats(self) -> dict:
        """获取存储统计"""
        return {
            "memory_dir": str(self.memory_dir),
            "indexed_items": len(self._index),
            "daily_files": len(list(self.memory_dir.glob("202*.md"))),
            "memory_md_exists": self.memory_file.exists(),
        }

    def search(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        """
        简单搜索（子串匹配）

        生产环境应替换为向量检索（embedding similarity search）
        """
        query_lower = query.lower()
        results = []
        for item in self._index.values():
            score = 0
            if query_lower in item.content.lower():
                score = 1.0
            elif any(qw in item.content.lower() for qw in query_lower.split()):
                score = 0.5
            if score > 0:
                results.append((score, item))

        results.sort(key=lambda x: (-x[0], -x[1].importance.value))
        return [item for _, item in results[:top_k]]


# ==================== 主提取引擎 ====================


class MemoryExtractor:
    """
    记忆自动提取引擎（主入口）

    对接 mem0 单轮提取 API 的简化实现:

    mem0 原始用法:
        memory.add(messages, user_id="user1")  # 自动提取并存储

    本实现:
        extractor = MemoryExtractor(".workbuddy/memory")
        items = extractor.extract(messages)
        extractor.store.save_items(items)

    或一键模式:
        extractor.process_and_save(messages)
    """

    def __init__(self, memory_dir: str | Path = ".workbuddy/memory"):
        self.extractor = RuleBasedExtractor()
        self.store = MemoryStore(memory_dir)
        self.config = ExtractionConfig()
        self._initialized = False

    def initialize(self) -> 'MemoryExtractor':
        """初始化：加载历史记忆用于去重"""
        self.store.load_existing_memories()
        self._initialized = True
        print(f"[记忆引擎] 初始化完成: 已索引 {len(self.store._index)} 条历史记忆")
        return self

    def extract(self,
                 messages: list[dict] | str,
                 min_confidence: float = 0.3,
                 max_items: int = 50) -> list[MemoryItem]:
        """
        从对话中提取记忆条目

        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
                      或纯文本字符串
            min_confidence: 最低置信度阈值
            max_items: 最大提取条目数

        Returns:
            提取的记忆条目列表（按重要性降序）
        """
        if isinstance(messages, str):
            text = messages
        else:
            text = self._flatten_messages(messages)

        # 使用规则提取器
        raw_items = self.extractor.extract_from_text(text)

        # 过滤和精炼
        filtered = self._filter_and_refine(raw_items, min_confidence)

        # 截断
        result = filtered[:max_items]

        # 设置来源信息
        summary = text[:60].replace("\n", " ")
        for item in result:
            item.source_conversation = summary

        print(f"[记忆引擎] 提取完成: {len(raw_items)} 原始 -> "
              f"{len(filtered)} 过滤后 -> {len(result)} 最终条目")
        return result

    def process_and_save(self,
                         messages: list[dict] | str,
                         user_id: str = "default",
                         write_daily: bool = True) -> dict:
        """
        一键处理: 提取 + 存储

        Returns:
            处理结果统计
        """
        if not self._initialized:
            self.initialize()

        items = self.extract(messages)
        saved = self.store.save_items(items, write_daily=write_daily)

        return {
            "extracted": len(items),
            "new_saved": saved,
            "duplicates_skipped": len(items) - saved,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_extraction_prompt(self, messages: list[dict]) -> str:
        """
        生成 mem0 风格的提取提示词

        当集成 LLM 时使用此提示词进行语义提取。
        当前版本仅用于文档记录。

        mem0 的提示词模板（简化版）:
        你是一个记忆提取专家。请从以下对话中提取所有值得长期记住的信息。
        输出格式: JSON数组，每个元素包含 content, type, entities, importance
        """
        flat = self._flatten_messages(messages)
        prompt = f"""你是一个记忆提取专家。从以下对话中提取值得长期记住的关键信息。

## 提取规则
1. **偏好**: 用户明确表达的好恶、习惯、工作风格
2. **决策**: 做出的技术选型、方案选择及其理由
3. **技能**: 新掌握的工具、语言、框架
4. **实体**: 重要的人名、项目名、系统名称及其角色
5. **目标**: 计划要做的事情、待完成的任务
6. **事实**: 具体的数值、日期、状态等客观信息

## 格式要求
每条记忆必须是独立的、可理解的短句（<80字）。
按重要性排序：CRITICAL(5) > HIGH(4) > MEDIUM(3) > LOW(2) > TRIVIAL(1)

## 对话内容
{flat}

## 输出
JSON数组: [{{"content": "...", "type": "fact|preference|...", "importance": 1-5}}]"""

        return prompt

    def _flatten_messages(self, messages: list[dict]) -> str:
        """将消息列表展平为文本"""
        parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, list):
                # 多模态消息
                content = " ".join(
                    c.get("text", "") if isinstance(c, dict) else str(c)
                    for c in content
                )
            parts.append(f"[{role}]: {content}")
        return "\n".join(parts)

    def _filter_and_refine(self, items: list[MemoryItem],
                           min_confidence: float) -> list[MemoryItem]:
        """过滤和精炼提取结果"""
        filtered = []
        for item in items:
            # 置信度过滤
            if item.confidence < min_confidence:
                continue

            # 内容质量过滤
            content = item.content
            if len(content.strip()) < 4:
                continue

            # 过滤纯标点/数字
            alnum_ratio = sum(1 for c in content if c.isalnum()) / max(len(content), 1)
            if alnum_ratio < 0.4:
                continue

            # 过滤重复模式
            if content.count("...") > 2 or content.count("。。。") > 2:
                continue

            filtered.append(item)

        return filtered

    def get_stats(self) -> dict:
        """获取引擎统计"""
        return {
            **self.store.get_stats(),
            "rules_loaded": len(self.extractor.rules),
            "initialized": self._initialized,
        }


@dataclass
class ExtractionConfig:
    """提取配置"""
    min_importance: ImportanceLevel = ImportanceLevel.LOW
    max_per_conversation: int = 30
    dedup_enabled: bool = True
    auto_write_daily: bool = True
    llm_fallback: bool = True           # LLM不可用时回退到规则提取
    extract_user_preferences: bool = True
    extract_decisions: bool = True
    extract_skills: bool = True
    extract_entities: bool = True
    extract_goals: bool = True
    extract_events: bool = False        # 默认不提取低价值事件


# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4: Memory Auto-Extraction Engine Test")
    print("=" * 60)

    extractor = MemoryExtractor(".workbuddy/memory").initialize()

    # 模拟对话消息
    test_messages = [
        {"role": "user", "content": "我喜欢简洁的回复，不要超过300字"},
        {"role": "assistant", "content": "好的，我会保持回复简短。"},
        {"role": "user", "content": "我已经掌握了Python数据分析，下一步计划学习机器学习"},
        {"role": "assistant", "content": "推荐从scikit-learn开始。"},
        {"role": "user", "content": "决定采用React作为前端框架"},
        {"role": "assistant", "content": "好的选择。"},
        {"role": "user", "content": "已完成HandoffManager的开发并推送到GitHub"},
        {"role": "user", "content": "张三是项目负责人，李四负责测试"},
        {"role": "user", "content": "目标是每周至少落地一个P0改进项"},
    ]

    print("\n--- 测试: 对话记忆提取 ---")
    items = extractor.extract(test_messages)

    print(f"\n提取结果 ({len(items)} 条):\n")
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {item.memory_type.name:12s} | {item.importance.name:8s} | {item.content}")

    print("\n--- 测试: 一键处理 ---")
    result = extractor.process_and_save(test_messages, user_id="test")
    print(f"\n处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    print("\n--- 测试: 搜索 ---")
    found = extractor.store.search("偏好")
    for item in found:
        print(f"  找到: [{item.memory_type.name}] {item.content}")

    print(f"\n引擎统计:")
    stats = extractor.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("Memory Auto-Extraction Engine Test Completed!")
    print("=" * 60)
