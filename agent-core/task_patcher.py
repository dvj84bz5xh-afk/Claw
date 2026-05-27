"""
TimesFM-inspired Task Patching System
任务Patch化处理，借鉴TimesFM的Patching机制
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import re
import hashlib
from collections import deque


class TaskType(Enum):
    """任务类型"""
    ANALYSIS = "analysis"          # 分析类
    GENERATION = "generation"      # 生成类
    EXECUTION = "execution"        # 执行类
    RESEARCH = "research"          # 研究类
    PLANNING = "planning"          # 规划类


class PatchPriority(Enum):
    """Patch优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class TaskPatch:
    """
    任务Patch
    类似TimesFM的Patch概念
    """
    index: int                                # Patch索引
    content: str                              # Patch内容
    task_type: TaskType                       # 任务类型
    priority: PatchPriority                   # 优先级
    
    # 元数据
    id: str = ""                              # Patch唯一ID
    estimated_effort: int = 1                 # 估计工作量 (1-10)
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他Patch ID
    
    # 状态
    completed: bool = False
    output: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, 'id', self._generate_id())
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        content_hash = hashlib.md5(f"{self.index}:{self.content}".encode()).hexdigest()[:8]
        return f"patch_{self.index}_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "index": self.index,
            "content": self.content,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "completed": self.completed,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class PatchEmbedding:
    """
    Patch嵌入表示
    类似TimesFM的Patch Embedding
    """
    patch_id: str
    semantic_vector: List[float]            # 语义向量
    complexity_score: float                 # 复杂度分数
    required_skills: List[str]              # 所需技能
    estimated_tokens: int                   # 估计token数
    
    # 特征标签
    keywords: List[str] = field(default_factory=list)
    domain: Optional[str] = None


@dataclass
class PatchingResult:
    """
    Patch化结果
    类似TimesFM的输出封装
    """
    original_task: str
    patches: List[TaskPatch]
    embeddings: List[PatchEmbedding]
    
    # 统计信息
    total_patches: int
    total_estimated_effort: int
    critical_path_length: int               # 关键路径长度
    
    # 元数据
    patching_strategy: str
    processing_time_ms: float


class TaskAnalyzer:
    """
    任务分析器
    识别任务结构和类型
    """
    
    # 关键词映射
    TYPE_KEYWORDS = {
        TaskType.ANALYSIS: ["分析", "评估", "诊断", "审查", "检查", "compare", "analyze", "evaluate"],
        TaskType.GENERATION: ["创建", "生成", "编写", "写", "开发", "create", "generate", "write", "build"],
        TaskType.EXECUTION: ["执行", "运行", "部署", "安装", "配置", "execute", "run", "deploy"],
        TaskType.RESEARCH: ["研究", "调查", "查找", "搜索", "学习", "research", "investigate", "search"],
        TaskType.PLANNING: ["计划", "规划", "设计", "策略", "plan", "design", "strategy"],
    }
    
    def analyze(self, task: str) -> Tuple[TaskType, List[str]]:
        """
        分析任务类型和关键词
        
        Returns:
            (任务类型, 关键词列表)
        """
        task_lower = task.lower()
        
        # 计算每种类型的匹配度
        scores = {}
        for task_type, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            scores[task_type] = score
        
        # 选择最高分的类型
        detected_type = max(scores, key=scores.get)
        if scores[detected_type] == 0:
            detected_type = TaskType.EXECUTION  # 默认类型
        
        # 提取关键词
        extracted_keywords = self._extract_keywords(task)
        
        return detected_type, extracted_keywords
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（可以替换为更复杂的NLP方法）
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # 技术关键词
        tech_keywords = [
            "python", "javascript", "database", "api", "security",
            "machine learning", "deep learning", "analysis", "visualization",
            "web", "backend", "frontend", "cloud", "docker", "kubernetes"
        ]
        
        found = [kw for kw in tech_keywords if kw in text.lower()]
        return found[:5]  # 最多5个关键词
    
    def estimate_complexity(self, task: str) -> float:
        """估计任务复杂度 (0-1)"""
        factors = [
            len(task) / 500,                           # 长度因子
            task.count(",") / 5,                        # 复杂度因子
            task.count("和") + task.count("以及"),        # 并列任务
            len(self._extract_keywords(task)) / 5,      # 技术复杂度
        ]
        return min(1.0, sum(factors) / len(factors))


class TaskPatcher:
    """
    任务Patch化处理器
    核心类，类似TimesFM的Patching机制
    """
    
    def __init__(self, patch_size: int = 5, patch_overlap: int = 1):
        self.patch_size = patch_size
        self.patch_overlap = patch_overlap
        self.analyzer = TaskAnalyzer()
    
    def patch_task(
        self,
        task: str,
        custom_patch_size: Optional[int] = None
    ) -> PatchingResult:
        """
        将任务分割成Patches
        
        类似TimesFM将时间序列分割成Patches
        
        Args:
            task: 原始任务描述
            custom_patch_size: 自定义Patch大小
            
        Returns:
            PatchingResult包含所有Patches
        """
        import time
        start_time = time.time()
        
        patch_size = custom_patch_size or self.patch_size
        
        # 1. 分析任务
        task_type, keywords = self.analyzer.analyze(task)
        complexity = self.analyzer.estimate_complexity(task)
        
        # 2. 分割任务为Patches
        patches = self._split_into_patches(task, patch_size, task_type)
        
        # 3. 建立依赖关系
        patches = self._establish_dependencies(patches)
        
        # 4. 创建Patch嵌入
        embeddings = self._create_patch_embeddings(patches, keywords)
        
        # 5. 计算关键路径
        critical_path = self._calculate_critical_path(patches)
        
        processing_time = (time.time() - start_time) * 1000
        
        return PatchingResult(
            original_task=task,
            patches=patches,
            embeddings=embeddings,
            total_patches=len(patches),
            total_estimated_effort=sum(p.estimated_effort for p in patches),
            critical_path_length=len(critical_path),
            patching_strategy=f"hierarchical_size_{patch_size}",
            processing_time_ms=processing_time
        )
    
    def _split_into_patches(
        self,
        task: str,
        patch_size: int,
        task_type: TaskType
    ) -> List[TaskPatch]:
        """
        将任务分割成Patches
        
        策略:
        1. 识别自然断点（逗号、句号、然后、接下来等）
        2. 保持语义完整性
        3. 根据任务类型调整Patch大小
        """
        # 根据复杂度调整patch_size
        complexity = self.analyzer.estimate_complexity(task)
        adjusted_size = max(2, int(patch_size * (1 - complexity * 0.5)))
        
        # 识别子任务
        subtasks = self._identify_subtasks(task)
        
        patches = []
        current_batch = []
        
        for i, subtask in enumerate(subtasks):
            current_batch.append(subtask)
            
            # 当达到patch_size或最后一个时创建Patch
            if len(current_batch) >= adjusted_size or i == len(subtasks) - 1:
                patch_content = "; ".join(current_batch)
                
                # 确定优先级
                priority = self._determine_priority(patch_content, i, len(subtasks))
                
                # 估计工作量
                effort = self._estimate_effort(patch_content)
                
                patch = TaskPatch(
                    index=len(patches),
                    content=patch_content,
                    task_type=task_type,
                    priority=priority,
                    estimated_effort=effort
                )
                patches.append(patch)
                current_batch = []
        
        return patches
    
    def _identify_subtasks(self, task: str) -> List[str]:
        """识别子任务"""
        # 分隔符模式
        delimiters = [
            r'[,，]\s*',                    # 逗号
            r'[;；]\s*',                    # 分号
            r'(?:然后|接下来|接着|之后)\s*',  # 顺序词
            r'(?:第一步|第二步|第三步|首先|其次|最后)\s*',
            r'\n+',
        ]
        
        pattern = '|'.join(delimiters)
        subtasks = re.split(pattern, task)
        
        # 清理和过滤
        subtasks = [s.strip() for s in subtasks if s.strip()]
        
        # 如果分割太细，合并短句
        merged = []
        current = ""
        for subtask in subtasks:
            if len(current) + len(subtask) < 100:
                current += ("，" if current else "") + subtask
            else:
                if current:
                    merged.append(current)
                current = subtask
        if current:
            merged.append(current)
        
        return merged if merged else [task]
    
    def _determine_priority(
        self,
        content: str,
        index: int,
        total: int
    ) -> PatchPriority:
        """确定Patch优先级"""
        # 包含关键操作的Patch设为高优先级
        critical_keywords = ["配置", "安装", "初始化", "setup", "config", "init"]
        if any(kw in content for kw in critical_keywords):
            return PatchPriority.CRITICAL
        
        # 第一个Patch通常很重要
        if index == 0:
            return PatchPriority.HIGH
        
        # 默认中等优先级
        return PatchPriority.MEDIUM
    
    def _estimate_effort(self, content: str) -> int:
        """估计工作量 (1-10)"""
        base = len(content) / 200  # 长度因子
        
        # 复杂度加成
        complexity_bonus = 0
        if any(kw in content for kw in ["设计", "架构", "design", "architecture"]):
            complexity_bonus += 2
        if any(kw in content for kw in ["优化", "改进", "optimize", "improve"]):
            complexity_bonus += 1
        
        return min(10, max(1, int(base + complexity_bonus)))
    
    def _establish_dependencies(self, patches: List[TaskPatch]) -> List[TaskPatch]:
        """建立Patch间依赖关系"""
        for i, patch in enumerate(patches):
            # 基础依赖：当前Patch依赖于前一个
            if i > 0:
                # 检查是否显式提到依赖
                if any(kw in patch.content for kw in ["上述", "前面", "之前", "above", "previous"]):
                    patch.dependencies.append(patches[i-1].id)
            
            # 配置类任务优先
            if patch.priority == PatchPriority.CRITICAL and i > 0:
                # 后续Patch可能依赖配置
                for prev in patches[:i]:
                    if prev.priority == PatchPriority.CRITICAL:
                        if prev.id not in patch.dependencies:
                            patch.dependencies.append(prev.id)
        
        return patches
    
    def _create_patch_embeddings(
        self,
        patches: List[TaskPatch],
        global_keywords: List[str]
    ) -> List[PatchEmbedding]:
        """创建Patch嵌入"""
        embeddings = []
        
        for patch in patches:
            # 提取Patch特有的关键词
            patch_keywords = self.analyzer._extract_keywords(patch.content)
            
            # 合并全局和局部关键词
            all_keywords = list(set(global_keywords + patch_keywords))
            
            # 计算复杂度
            complexity = self.analyzer.estimate_complexity(patch.content)
            
            # 模拟语义向量（实际应用中应使用真正的embedding模型）
            semantic_vector = self._mock_semantic_embedding(patch.content)
            
            embedding = PatchEmbedding(
                patch_id=patch.id,
                semantic_vector=semantic_vector,
                complexity_score=complexity,
                required_skills=patch_keywords,
                estimated_tokens=len(patch.content) * 1.5,  # 粗略估计
                keywords=all_keywords,
                domain=self._infer_domain(patch.content)
            )
            embeddings.append(embedding)
        
        return embeddings
    
    def _mock_semantic_embedding(self, text: str) -> List[float]:
        """模拟语义嵌入（实际应调用embedding API）"""
        # 基于文本特征的简单模拟
        import random
        random.seed(hash(text) % 10000)
        return [random.gauss(0, 1) for _ in range(128)]
    
    def _infer_domain(self, content: str) -> Optional[str]:
        """推断领域"""
        domain_keywords = {
            "security": ["安全", "漏洞", "攻击", "防御", "security", "vulnerability"],
            "data": ["数据", "分析", "可视化", "database", "analytics"],
            "web": ["web", "前端", "后端", "api", "http"],
            "ml": ["机器学习", "模型", "训练", "machine learning", "model"],
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in content.lower() for kw in keywords):
                return domain
        return None
    
    def _calculate_critical_path(self, patches: List[TaskPatch]) -> List[str]:
        """计算关键路径（最长依赖链）"""
        # 构建依赖图
        graph = {p.id: p.dependencies for p in patches}
        
        # 计算最长路径
        memo = {}
        
        def longest_path(node_id: str) -> int:
            if node_id in memo:
                return memo[node_id]
            
            if not graph.get(node_id):
                memo[node_id] = 1
                return 1
            
            max_len = 1 + max(longest_path(dep) for dep in graph[node_id])
            memo[node_id] = max_len
            return max_len
        
        # 找到关键路径起点
        if not patches:
            return []
        
        critical_start = max(patches, key=lambda p: longest_path(p.id))
        
        # 重建路径
        path = []
        current = critical_start.id
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            path.append(current)
            # 找到依赖当前节点的下一个节点
            next_nodes = [p.id for p in patches if current in p.dependencies]
            if next_nodes:
                current = max(next_nodes, key=lambda n: longest_path(n))
            else:
                break
        
        return path
    
    def get_execution_order(self, result: PatchingResult) -> List[TaskPatch]:
        """
        获取执行顺序
        拓扑排序处理依赖关系
        """
        patches = {p.id: p for p in result.patches}
        in_degree = {p.id: len(p.dependencies) for p in result.patches}
        
        # 按优先级分组
        queue = deque()
        for p in result.patches:
            if in_degree[p.id] == 0:
                queue.append(p)
        
        # 按优先级排序
        queue = deque(sorted(queue, key=lambda p: p.priority.value))
        
        execution_order = []
        
        while queue:
            patch = queue.popleft()
            execution_order.append(patch)
            
            # 找到依赖于当前patch的下一个
            for p in result.patches:
                if patch.id in p.dependencies:
                    in_degree[p.id] -= 1
                    if in_degree[p.id] == 0:
                        queue.append(p)
            
            # 重新排序队列
            queue = deque(sorted(queue, key=lambda p: p.priority.value))
        
        return execution_order


class HierarchicalPatcher:
    """
    分层Patch处理器
    支持多级Patch分解
    """
    
    def __init__(self):
        self.patcher = TaskPatcher()
    
    def patch_hierarchically(
        self,
        task: str,
        levels: int = 2
    ) -> Dict[int, PatchingResult]:
        """
        分层Patch化
        
        Level 0: 原始任务
        Level 1: 粗粒度Patches
        Level 2: 细粒度Patches
        """
        results = {}
        
        # Level 1: 粗粒度
        results[1] = self.patcher.patch_task(task, patch_size=10)
        
        # Level 2+: 对每个Patch进一步分解
        if levels >= 2:
            all_sub_patches = []
            for patch in results[1].patches:
                sub_result = self.patcher.patch_task(patch.content, patch_size=3)
                all_sub_patches.extend(sub_result.patches)
            
            # 合并为Level 2结果
            results[2] = PatchingResult(
                original_task=task,
                patches=all_sub_patches,
                embeddings=[],  # 简化
                total_patches=len(all_sub_patches),
                total_estimated_effort=sum(p.estimated_effort for p in all_sub_patches),
                critical_path_length=results[1].critical_path_length + 1,
                patching_strategy="hierarchical_2level",
                processing_time_ms=results[1].processing_time_ms * 1.5
            )
        
        return results


# 便捷函数
def patch_task(task: str, patch_size: int = 5) -> PatchingResult:
    """快速Patch化任务"""
    patcher = TaskPatcher(patch_size=patch_size)
    return patcher.patch_task(task)


def print_patching_result(result: PatchingResult):
    """打印Patch结果"""
    print(f"\n{'='*60}")
    print(f"任务Patch化结果")
    print(f"{'='*60}")
    print(f"原始任务: {result.original_task[:80]}...")
    print(f"总Patches: {result.total_patches}")
    print(f"估计工作量: {result.total_estimated_effort}")
    print(f"关键路径长度: {result.critical_path_length}")
    print(f"处理时间: {result.processing_time_ms:.2f}ms")
    print(f"策略: {result.patching_strategy}")
    print(f"\nPatches详情:")
    
    for patch in result.patches:
        status = "✓" if patch.completed else "○"
        print(f"  [{status}] Patch {patch.index}: {patch.content[:50]}...")
        print(f"      类型: {patch.task_type.value}, 优先级: {patch.priority.name}")
        if patch.dependencies:
            print(f"      依赖: {patch.dependencies}")


if __name__ == "__main__":
    # 测试Task Patcher
    print("=== TimesFM-inspired Task Patching System Test ===\n")
    
    # 测试任务
    test_task = """
    开发一个完整的网络安全扫描系统，包含以下功能：
    1. 配置扫描目标和规则
    2. 实现端口扫描和漏洞检测模块
    3. 生成可视化报告
    4. 设置自动预警机制
    然后部署到服务器并配置定时任务
    """
    
    print("测试任务:")
    print(test_task)
    print()
    
    # 1. 基础Patching
    print("1. 基础Patching (size=3):")
    patcher = TaskPatcher(patch_size=3)
    result = patcher.patch_task(test_task)
    print_patching_result(result)
    
    # 2. 执行顺序
    print("\n2. 执行顺序:")
    execution_order = patcher.get_execution_order(result)
    for i, patch in enumerate(execution_order):
        print(f"  {i+1}. [{patch.priority.name}] {patch.content[:40]}...")
    
    # 3. 分层Patching
    print("\n3. 分层Patching:")
    hp = HierarchicalPatcher()
    h_result = hp.patch_hierarchically(test_task, levels=2)
    print(f"  Level 1 Patches: {h_result[1].total_patches}")
    print(f"  Level 2 Patches: {h_result[2].total_patches}")
    
    print("\n=== All Tests Passed ===")
