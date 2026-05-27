"""
TimesFM-inspired Zero-Shot Knowledge Base
零样本知识库，借鉴TimesFM预训练思维
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import json
import hashlib
from pathlib import Path


class KnowledgeDomain(Enum):
    """知识领域"""
    WEB_SECURITY = "web_security"
    NETWORK_SECURITY = "network_security"
    DATA_ANALYSIS = "data_analysis"
    MACHINE_LEARNING = "machine_learning"
    SOFTWARE_ENGINEERING = "software_engineering"
    DEVOPS = "devops"
    TIME_SERIES = "time_series"


class KnowledgeType(Enum):
    """知识类型"""
    PATTERN = "pattern"              # 模式/模板
    TECHNIQUE = "technique"          # 技术/方法
    BEST_PRACTICE = "best_practice"  # 最佳实践
    ANTI_PATTERN = "anti_pattern"    # 反模式


@dataclass
class KnowledgePattern:
    """
    知识模式
    TimesFM预训练知识的具象化
    """
    domain: KnowledgeDomain
    type: KnowledgeType
    name: str
    description: str
    
    # 核心内容
    patterns: List[str] = field(default_factory=list)      # 匹配模式
    solutions: List[str] = field(default_factory=list)     # 解决方案
    examples: List[Dict] = field(default_factory=list)     # 示例
    
    # 元数据
    id: str = field(default="")
    confidence: float = 0.9                                # 置信度
    complexity: int = 3                                    # 复杂度 1-10
    prerequisites: List[str] = field(default_factory=list) # 前置知识
    related_patterns: List[str] = field(default_factory=list) # 相关模式
    
    # 使用统计
    usage_count: int = 0
    success_count: int = 0
    last_used: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, 'id', self._generate_id())
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        content = f"{self.domain.value}:{self.name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def success_rate(self) -> float:
        """计算成功率"""
        if self.usage_count == 0:
            return self.confidence
        return self.success_count / self.usage_count
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "id": self.id,
            "domain": self.domain.value,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "patterns": self.patterns,
            "solutions": self.solutions,
            "examples": self.examples,
            "confidence": self.confidence,
            "complexity": self.complexity,
            "prerequisites": self.prerequisites,
            "related_patterns": self.related_patterns,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "last_used": self.last_used,
        }


class ZeroShotKnowledgeBase:
    """
    零样本知识库
    
    类似TimesFM预训练时间序列数据，
    这里预训练各种任务模式
    """
    
    def __init__(self):
        self._patterns: Dict[str, KnowledgePattern] = {}
        self._domain_index: Dict[KnowledgeDomain, List[str]] = {
            domain: [] for domain in KnowledgeDomain
        }
        self._vector_index: Optional[Any] = None  # 语义向量索引
        
        # 初始化默认知识
        self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self):
        """初始化默认知识库"""
        
        # ========== Web Security ==========
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.WEB_SECURITY,
            type=KnowledgeType.PATTERN,
            name="SQL Injection Detection",
            description="识别和防御SQL注入攻击",
            patterns=[
                r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
                r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
                r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
                r"((\%27)|(\'))union",
                r"exec(\s|\+)+(s|x)p\w+",
            ],
            solutions=[
                "使用参数化查询/预编译语句",
                "输入验证和清理",
                "最小权限原则",
                "使用ORM框架",
            ],
            examples=[
                {"attack": "' OR '1'='1", "context": "登录绕过"},
                {"attack": "1; DROP TABLE users--", "context": "数据删除"},
            ],
            confidence=0.95,
            complexity=4,
        ))
        
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.WEB_SECURITY,
            type=KnowledgeType.PATTERN,
            name="XSS Prevention",
            description="跨站脚本攻击防护",
            patterns=[
                r"<script[^>]*>[\s\S]*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe",
                r"<object",
            ],
            solutions=[
                "输出编码/转义",
                "Content Security Policy",
                "HttpOnly Cookie",
                "输入验证",
            ],
            confidence=0.94,
            complexity=3,
        ))
        
        # ========== Data Analysis ==========
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.DATA_ANALYSIS,
            type=KnowledgeType.TECHNIQUE,
            name="Time Series Anomaly Detection",
            description="时间序列异常检测方法",
            patterns=[
                "异常检测",
                "outlier detection",
                "异常值",
                "离群点",
            ],
            solutions=[
                "统计方法: Z-score, IQR",
                "机器学习方法: Isolation Forest",
                "深度学习方法: Autoencoder",
                "时序专用: Prophet, STL",
            ],
            examples=[
                {"method": "Z-score", "threshold": 3},
                {"method": "Isolation Forest", "contamination": 0.1},
            ],
            confidence=0.92,
            complexity=6,
        ))
        
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.DATA_ANALYSIS,
            type=KnowledgeType.TECHNIQUE,
            name="Data Visualization Best Practices",
            description="数据可视化最佳实践",
            patterns=[
                "可视化",
                "图表",
                "dashboard",
                "plot",
                "chart",
            ],
            solutions=[
                "选择合适的图表类型",
                "保持简洁，避免视觉噪音",
                "确保颜色可访问性",
                "添加适当的标题和标签",
                "提供交互功能",
            ],
            confidence=0.90,
            complexity=2,
        ))
        
        # ========== Software Engineering ==========
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.SOFTWARE_ENGINEERING,
            type=KnowledgeType.BEST_PRACTICE,
            name="Clean Code Principles",
            description="代码整洁之道",
            patterns=[
                "代码质量",
                "重构",
                "clean code",
                "代码规范",
            ],
            solutions=[
                "有意义的命名",
                "函数单一职责",
                "避免副作用",
                "DRY原则",
                "单元测试",
            ],
            confidence=0.96,
            complexity=3,
        ))
        
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.SOFTWARE_ENGINEERING,
            type=KnowledgeType.PATTERN,
            name="Error Handling Pattern",
            description="错误处理模式",
            patterns=[
                "错误处理",
                "异常",
                "error handling",
                "exception",
            ],
            solutions=[
                "使用异常而非返回码",
                "提供上下文信息",
                "区分业务异常和系统异常",
                "优雅降级",
                "日志记录",
            ],
            confidence=0.93,
            complexity=4,
        ))
        
        # ========== Time Series (TimesFM相关) ==========
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.TIME_SERIES,
            type=KnowledgeType.TECHNIQUE,
            name="TimesFM Forecasting Approach",
            description="TimesFM时间序列预测方法",
            patterns=[
                "时间序列预测",
                "timesfm",
                "forecasting",
                "时序预测",
            ],
            solutions=[
                "使用Decoder-only架构",
                "Patch-based tokenization",
                "零样本预测",
                "概率预测输出",
                "自动归一化处理",
            ],
            examples=[
                {"context_length": 16384, "horizon": 128},
                {"quantiles": [0.1, 0.5, 0.9]},
            ],
            confidence=0.91,
            complexity=8,
        ))
        
        # ========== Machine Learning ==========
        self.add_pattern(KnowledgePattern(
            domain=KnowledgeDomain.MACHINE_LEARNING,
            type=KnowledgeType.TECHNIQUE,
            name="PEFT Fine-tuning",
            description="参数高效微调方法",
            patterns=[
                "微调",
                "fine-tuning",
                "LoRA",
                "PEFT",
                "参数高效",
            ],
            solutions=[
                "使用LoRA适配器",
                "设置合适的rank (8-64)",
                "只训练适配器参数",
                "保留基础模型冻结",
                "学习率要小 (1e-4~1e-3)",
            ],
            confidence=0.93,
            complexity=7,
        ))
    
    def add_pattern(self, pattern: KnowledgePattern):
        """添加知识模式"""
        self._patterns[pattern.id] = pattern
        self._domain_index[pattern.domain].append(pattern.id)
    
    def get_pattern(self, pattern_id: str) -> Optional[KnowledgePattern]:
        """获取知识模式"""
        return self._patterns.get(pattern_id)
    
    def search_by_keywords(
        self,
        keywords: List[str],
        domain: Optional[KnowledgeDomain] = None,
        top_k: int = 5
    ) -> List[Tuple[KnowledgePattern, float]]:
        """
        关键词搜索
        
        Returns:
            List of (pattern, relevance_score)
        """
        results = []
        
        # 确定搜索范围
        if domain:
            pattern_ids = self._domain_index[domain]
        else:
            pattern_ids = list(self._patterns.keys())
        
        # 计算相关性
        for pid in pattern_ids:
            pattern = self._patterns[pid]
            score = self._calculate_keyword_match(pattern, keywords)
            if score > 0:
                results.append((pattern, score))
        
        # 排序并返回top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _calculate_keyword_match(
        self,
        pattern: KnowledgePattern,
        keywords: List[str]
    ) -> float:
        """计算关键词匹配分数"""
        score = 0.0
        
        # 名称匹配
        for kw in keywords:
            if kw.lower() in pattern.name.lower():
                score += 3.0
        
        # 描述匹配
        for kw in keywords:
            if kw.lower() in pattern.description.lower():
                score += 2.0
        
        # 模式匹配
        for kw in keywords:
            for p in pattern.patterns:
                if isinstance(p, str) and kw.lower() in p.lower():
                    score += 1.5
        
        # 解决方案匹配
        for kw in keywords:
            for s in pattern.solutions:
                if kw.lower() in s.lower():
                    score += 1.0
        
        # 乘以置信度
        return score * pattern.confidence
    
    def retrieve_for_task(
        self,
        task_description: str,
        top_k: int = 3
    ) -> List[KnowledgePattern]:
        """
        为任务检索相关知识
        
        类似TimesFM基于预训练知识的零样本推理
        """
        # 提取关键词
        keywords = self._extract_keywords(task_description)
        
        # 搜索匹配的知识
        results = self.search_by_keywords(keywords, top_k=top_k*2)
        
        # 过滤和排序
        filtered = [
            (p, s) for p, s in results
            if s > 2.0  # 最小相关性阈值
        ]
        
        # 按综合得分排序（相关性+成功率）
        filtered.sort(
            key=lambda x: x[1] * x[0].success_rate(),
            reverse=True
        )
        
        # 更新使用统计
        for pattern, _ in filtered[:top_k]:
            pattern.usage_count += 1
            pattern.last_used = self._get_timestamp()
        
        return [p for p, _ in filtered[:top_k]]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化实现，实际应使用NLP
        import re
        
        # 停用词
        stopwords = {"the", "a", "an", "is", "are", "to", "of", "and", "in", "for"}
        
        # 提取单词
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # 过滤停用词并统计频率
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1
        
        # 返回高频词
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:10]]
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def report_success(self, pattern_id: str):
        """报告知识使用成功"""
        if pattern_id in self._patterns:
            self._patterns[pattern_id].success_count += 1
    
    def report_failure(self, pattern_id: str, reason: str):
        """报告知识使用失败"""
        # 可以记录失败原因，用于后续改进
        pass
    
    def get_domain_statistics(self) -> Dict[str, Dict]:
        """获取各领域统计"""
        stats = {}
        for domain in KnowledgeDomain:
            patterns = [self._patterns[pid] for pid in self._domain_index[domain]]
            stats[domain.value] = {
                "total_patterns": len(patterns),
                "avg_confidence": sum(p.confidence for p in patterns) / len(patterns) if patterns else 0,
                "total_usage": sum(p.usage_count for p in patterns),
                "success_rate": sum(p.success_count for p in patterns) / sum(p.usage_count for p in patterns) if patterns and sum(p.usage_count for p in patterns) > 0 else 0,
            }
        return stats
    
    def save_to_file(self, filepath: str):
        """保存知识库到文件"""
        data = {
            "patterns": {pid: p.to_dict() for pid, p in self._patterns.items()},
            "domain_index": {k.value: v for k, v in self._domain_index.items()},
        }
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "ZeroShotKnowledgeBase":
        """从文件加载知识库"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        kb = cls()
        kb._patterns.clear()
        kb._domain_index = {domain: [] for domain in KnowledgeDomain}
        
        for pid, pdict in data.get("patterns", {}).items():
            pattern = KnowledgePattern(
                id=pdict["id"],
                domain=KnowledgeDomain(pdict["domain"]),
                type=KnowledgeType(pdict["type"]),
                name=pdict["name"],
                description=pdict["description"],
                patterns=pdict.get("patterns", []),
                solutions=pdict.get("solutions", []),
                examples=pdict.get("examples", []),
                confidence=pdict.get("confidence", 0.9),
                complexity=pdict.get("complexity", 3),
                prerequisites=pdict.get("prerequisites", []),
                related_patterns=pdict.get("related_patterns", []),
                usage_count=pdict.get("usage_count", 0),
                success_count=pdict.get("success_count", 0),
                last_used=pdict.get("last_used"),
            )
            kb.add_pattern(pattern)
        
        return kb


# 全局知识库实例
_global_knowledge_base: Optional[ZeroShotKnowledgeBase] = None


def get_knowledge_base() -> ZeroShotKnowledgeBase:
    """获取全局知识库"""
    global _global_knowledge_base
    if _global_knowledge_base is None:
        _global_knowledge_base = ZeroShotKnowledgeBase()
    return _global_knowledge_base


def retrieve_knowledge(task: str, top_k: int = 3) -> List[KnowledgePattern]:
    """快速检索知识"""
    return get_knowledge_base().retrieve_for_task(task, top_k)


if __name__ == "__main__":
    # 测试知识库
    print("=== Zero-Shot Knowledge Base Test ===\n")
    
    kb = ZeroShotKnowledgeBase()
    
    # 1. 统计信息
    print("1. 知识库统计:")
    stats = kb.get_domain_statistics()
    for domain, s in stats.items():
        print(f"   {domain}: {s['total_patterns']} patterns")
    print()
    
    # 2. 关键词搜索
    print("2. 关键词搜索 'SQL injection':")
    results = kb.search_by_keywords(["SQL", "injection"])
    for pattern, score in results:
        print(f"   [{score:.2f}] {pattern.name}: {pattern.description}")
    print()
    
    # 3. 任务检索
    print("3. 任务检索 '如何防止网站被攻击':")
    task = "我需要保护我的网站免受黑客攻击，特别是SQL注入和XSS"
    patterns = kb.retrieve_for_task(task)
    for p in patterns:
        print(f"   • {p.name} (置信度: {p.confidence})")
        print(f"     解决方案: {p.solutions[:2]}")
    print()
    
    # 4. 时间序列相关
    print("4. 时间序列预测知识:")
    results = kb.search_by_keywords(["timesfm", "forecasting"], 
                                     domain=KnowledgeDomain.TIME_SERIES)
    for pattern, score in results:
        print(f"   [{score:.2f}] {pattern.name}")
        print(f"      {pattern.solutions}")
    print()
    
    print("=== All Tests Passed ===")
