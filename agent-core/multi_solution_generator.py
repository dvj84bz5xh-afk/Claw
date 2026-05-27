#!/usr/bin/env python3
"""
Multi-Solution Generator - 多方案并行生成系统
借鉴TimesFM生成多个分位数预测的思想，针对同一问题生成多样化的解决方案

设计理念：
1. 多样性优先 - 确保不同方案具有明显差异
2. 多维度评估 - 从技术、业务、用户体验等角度评分
3. 可配置性 - 支持不同生成策略和偏好
4. 集成友好 - 与现有TimesFM架构无缝集成
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import random
import hashlib
import json
from datetime import datetime


class SolutionType(Enum):
    """解决方案类型"""
    RULE_BASED = "rule_based"        # 规则驱动
    ML_BASED = "ml_based"            # 机器学习驱动
    HYBRID = "hybrid"                # 混合方法
    HEURISTIC = "heuristic"          # 启发式方法
    OPTIMIZATION = "optimization"    # 优化方法


class RiskLevel(Enum):
    """风险等级"""
    CONSERVATIVE = "conservative"    # 保守方案
    MODERATE = "moderate"            # 中等风险
    AGGRESSIVE = "aggressive"        # 激进方案


class ResourceIntensity(Enum):
    """资源密集度"""
    LIGHT = "light"                  # 轻量级
    MEDIUM = "medium"                # 中等
    HEAVY = "heavy"                  # 重型


@dataclass
class SolutionCandidate:
    """
    解决方案候选
    """
    id: str
    title: str
    description: str
    type: SolutionType
    risk_level: RiskLevel
    resource_intensity: ResourceIntensity
    
    # 技术细节
    technical_approach: str
    key_technologies: List[str]
    implementation_steps: List[str]
    
    # 评估指标
    estimated_time: int  # 小时
    estimated_cost: int  # 相对成本 (1-10)
    success_probability: float  # 0-1
    technical_feasibility: float  # 0-1
    business_value: float  # 0-1
    user_experience: float  # 0-1
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    source_strategy: str = ""  # 生成策略
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type.value,
            "risk_level": self.risk_level.value,
            "resource_intensity": self.resource_intensity.value,
            "technical_approach": self.technical_approach,
            "key_technologies": self.key_technologies,
            "implementation_steps": self.implementation_steps,
            "estimated_time": self.estimated_time,
            "estimated_cost": self.estimated_cost,
            "success_probability": self.success_probability,
            "technical_feasibility": self.technical_feasibility,
            "business_value": self.business_value,
            "user_experience": self.user_experience,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "source_strategy": self.source_strategy,
        }
    
    def calculate_overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        计算综合评分
        
        Args:
            weights: 权重配置，默认均衡权重
                - technical_feasibility: 0.25
                - business_value: 0.25
                - user_experience: 0.25
                - success_probability: 0.25
        """
        default_weights = {
            "technical_feasibility": 0.25,
            "business_value": 0.25,
            "user_experience": 0.25,
            "success_probability": 0.25,
        }
        weights = weights or default_weights
        
        score = (
            self.technical_feasibility * weights.get("technical_feasibility", 0.25) +
            self.business_value * weights.get("business_value", 0.25) +
            self.user_experience * weights.get("user_experience", 0.25) +
            self.success_probability * weights.get("success_probability", 0.25)
        )
        return score


@dataclass
class RankingCriteria:
    """
    排序标准
    """
    prioritize_technical_feasibility: float = 0.0  # 0-1权重
    prioritize_business_value: float = 0.0
    prioritize_user_experience: float = 0.0
    prioritize_success_probability: float = 0.0
    prioritize_cost_efficiency: bool = False
    prioritize_time_efficiency: bool = False
    max_risk_tolerance: RiskLevel = RiskLevel.AGGRESSIVE
    max_resource_intensity: ResourceIntensity = ResourceIntensity.HEAVY
    
    def normalize_weights(self) -> Dict[str, float]:
        """归一化权重"""
        weights = {
            "technical_feasibility": self.prioritize_technical_feasibility,
            "business_value": self.prioritize_business_value,
            "user_experience": self.prioritize_user_experience,
            "success_probability": self.prioritize_success_probability,
        }
        
        # 如果所有权重为0，使用均衡权重
        if sum(weights.values()) == 0:
            weights = {k: 0.25 for k in weights.keys()}
        else:
            # 归一化
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
        
        return weights


@dataclass
class RankedSolution:
    """
    排序后的解决方案
    """
    solution: SolutionCandidate
    rank: int
    overall_score: float
    weighted_scores: Dict[str, float]
    meets_constraints: bool
    recommendation_reason: str


class MultiSolutionGenerator:
    """
    多方案生成器
    
    类似TimesFM生成多个分位数预测，为同一问题生成多样化的解决方案
    
    生成策略：
    1. 不同技术路线 (rule-based vs ML-based vs hybrid)
    2. 不同风险偏好 (保守 vs 中等 vs 激进)
    3. 不同资源消耗 (轻量 vs 中型 vs 重型)
    """
    
    def __init__(self):
        # 技术路线模板
        self.technical_approaches = {
            SolutionType.RULE_BASED: {
                "name": "规则驱动方法",
                "description": "基于预定义规则和逻辑的解决方案",
                "technologies": ["正则表达式", "规则引擎", "决策树", "状态机"],
                "typical_steps": ["定义规则集", "实现规则引擎", "测试规则覆盖", "优化规则性能"],
            },
            SolutionType.ML_BASED: {
                "name": "机器学习方法",
                "description": "基于数据驱动和模型训练的解决方案",
                "technologies": ["深度学习", "传统机器学习", "特征工程", "模型评估"],
                "typical_steps": ["数据收集", "特征工程", "模型训练", "模型评估", "部署优化"],
            },
            SolutionType.HYBRID: {
                "name": "混合方法",
                "description": "结合规则和机器学习的混合解决方案",
                "technologies": ["规则引擎", "机器学习模型", "集成系统", "决策融合"],
                "typical_steps": ["规则部分设计", "ML部分设计", "系统集成", "联合优化"],
            },
            SolutionType.HEURISTIC: {
                "name": "启发式方法",
                "description": "基于领域知识和启发式规则的解决方案",
                "technologies": ["启发式算法", "领域知识库", "专家系统", "近似算法"],
                "typical_steps": ["领域知识提取", "启发式规则设计", "算法实现", "参数调优"],
            },
            SolutionType.OPTIMIZATION: {
                "name": "优化方法",
                "description": "基于数学优化和搜索算法的解决方案",
                "technologies": ["线性规划", "遗传算法", "模拟退火", "约束满足"],
                "typical_steps": ["问题建模", "目标函数定义", "优化算法选择", "参数调优", "结果验证"],
            },
        }
        
        # 风险配置
        self.risk_profiles = {
            RiskLevel.CONSERVATIVE: {
                "success_probability_range": (0.8, 0.95),
                "technical_feasibility_range": (0.7, 0.9),
                "time_multiplier": 1.2,
                "cost_multiplier": 1.1,
            },
            RiskLevel.MODERATE: {
                "success_probability_range": (0.6, 0.8),
                "technical_feasibility_range": (0.5, 0.8),
                "time_multiplier": 1.0,
                "cost_multiplier": 1.0,
            },
            RiskLevel.AGGRESSIVE: {
                "success_probability_range": (0.4, 0.7),
                "technical_feasibility_range": (0.3, 0.6),
                "time_multiplier": 0.8,
                "cost_multiplier": 0.9,
            },
        }
        
        # 资源强度配置
        self.resource_profiles = {
            ResourceIntensity.LIGHT: {
                "estimated_time_range": (10, 40),  # 小时
                "estimated_cost_range": (1, 4),    # 1-10
                "team_size": "1-2人",
                "infrastructure": "最小化",
            },
            ResourceIntensity.MEDIUM: {
                "estimated_time_range": (40, 120),
                "estimated_cost_range": (4, 7),
                "team_size": "2-4人",
                "infrastructure": "标准",
            },
            ResourceIntensity.HEAVY: {
                "estimated_time_range": (120, 300),
                "estimated_cost_range": (7, 10),
                "team_size": "4+人",
                "infrastructure": "扩展",
            },
        }
        
        # 业务价值评估模板
        self.business_value_templates = [
            ("直接收入增长", 0.7, 0.9),
            ("成本节约", 0.6, 0.8),
            ("效率提升", 0.5, 0.7),
            ("风险降低", 0.4, 0.6),
            ("用户体验改善", 0.3, 0.5),
            ("技术债务减少", 0.2, 0.4),
        ]
        
        # 用户体验评估模板
        self.user_experience_templates = [
            ("直观易用", 0.8, 0.95),
            ("功能完整", 0.7, 0.9),
            ("性能优秀", 0.6, 0.85),
            ("界面美观", 0.5, 0.8),
            ("学习成本低", 0.4, 0.7),
            ("可访问性好", 0.3, 0.6),
        ]
    
    def generate_solutions(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        num_solutions: int = 3,
        diversity_threshold: float = 0.7,
        enforce_diversity: bool = True
    ) -> List[SolutionCandidate]:
        """
        生成多样化的解决方案
        
        Args:
            problem: 问题描述
            context: 上下文信息，如领域、约束等
            num_solutions: 生成方案数量
            diversity_threshold: 多样性阈值 (0-1)，越高方案差异越大
            enforce_diversity: 是否强制执行多样性
        
        Returns:
            解决方案候选列表
        """
        context = context or {}
        domain = context.get("domain", "general")
        
        solutions = []
        attempts = 0
        max_attempts = num_solutions * 3  # 防止无限循环
        
        while len(solutions) < num_solutions and attempts < max_attempts:
            attempts += 1
            
            # 随机选择生成策略
            solution_type = random.choice(list(SolutionType))
            risk_level = random.choice(list(RiskLevel))
            resource_intensity = random.choice(list(ResourceIntensity))
            
            # 生成方案
            candidate = self._generate_single_solution(
                problem=problem,
                domain=domain,
                solution_type=solution_type,
                risk_level=risk_level,
                resource_intensity=resource_intensity,
                context=context
            )
            
            # 检查多样性
            if enforce_diversity:
                diverse_enough = self._check_diversity(candidate, solutions, diversity_threshold)
                if not diverse_enough:
                    continue
            
            solutions.append(candidate)
        
        # 如果无法生成足够多样化的方案，返回已生成的方案
        return solutions
    
    def _generate_single_solution(
        self,
        problem: str,
        domain: str,
        solution_type: SolutionType,
        risk_level: RiskLevel,
        resource_intensity: ResourceIntensity,
        context: Dict[str, Any]
    ) -> SolutionCandidate:
        """生成单个解决方案"""
        # 生成唯一ID
        solution_id = hashlib.md5(
            f"{problem}{solution_type}{risk_level}{resource_intensity}{datetime.now().timestamp()}".encode()
        ).hexdigest()[:8]
        
        # 获取技术路线信息
        tech_info = self.technical_approaches[solution_type]
        
        # 生成标题和描述
        title = f"{tech_info['name']} ({risk_level.value})"
        description = (
            f"使用{tech_info['description']}解决'{problem[:50]}...'问题。"
            f"风险偏好：{risk_level.value}，资源要求：{resource_intensity.value}。"
        )
        
        # 风险评估
        risk_profile = self.risk_profiles[risk_level]
        success_probability = random.uniform(*risk_profile["success_probability_range"])
        technical_feasibility = random.uniform(*risk_profile["technical_feasibility_range"])
        
        # 资源评估
        resource_profile = self.resource_profiles[resource_intensity]
        estimated_time = random.randint(*resource_profile["estimated_time_range"])
        estimated_cost = random.randint(*resource_profile["estimated_cost_range"])
        
        # 应用风险乘数
        estimated_time = int(estimated_time * risk_profile["time_multiplier"])
        estimated_cost = int(estimated_cost * risk_profile["cost_multiplier"])
        
        # 业务价值评估 (基于领域和问题复杂度)
        business_value_template = random.choice(self.business_value_templates)
        business_value = random.uniform(business_value_template[1], business_value_template[2])
        
        # 用户体验评估
        user_experience_template = random.choice(self.user_experience_templates)
        user_experience = random.uniform(user_experience_template[1], user_experience_template[2])
        
        # 生成实现步骤
        implementation_steps = []
        base_steps = tech_info["typical_steps"]
        for i, step in enumerate(base_steps, 1):
            implementation_steps.append(f"{i}. {step}")
        
        # 添加领域特定步骤
        if domain != "general":
            implementation_steps.append(f"{len(base_steps) + 1}. {domain}领域适配和优化")
        
        # 生成策略描述
        source_strategy = f"技术路线:{solution_type.value}|风险偏好:{risk_level.value}|资源强度:{resource_intensity.value}"
        
        return SolutionCandidate(
            id=solution_id,
            title=title,
            description=description,
            type=solution_type,
            risk_level=risk_level,
            resource_intensity=resource_intensity,
            technical_approach=tech_info["description"],
            key_technologies=tech_info["technologies"],
            implementation_steps=implementation_steps,
            estimated_time=estimated_time,
            estimated_cost=estimated_cost,
            success_probability=success_probability,
            technical_feasibility=technical_feasibility,
            business_value=business_value,
            user_experience=user_experience,
            tags=[domain, solution_type.value, risk_level.value, resource_intensity.value],
            source_strategy=source_strategy,
        )
    
    def _check_diversity(
        self,
        candidate: SolutionCandidate,
        existing_solutions: List[SolutionCandidate],
        threshold: float
    ) -> bool:
        """检查方案多样性"""
        if not existing_solutions:
            return True
        
        # 计算与现有方案的相似度
        similarities = []
        for existing in existing_solutions:
            similarity = self._calculate_similarity(candidate, existing)
            similarities.append(similarity)
        
        # 如果与任何现有方案的相似度超过阈值，则多样性不足
        max_similarity = max(similarities) if similarities else 0
        return max_similarity < threshold
    
    def _calculate_similarity(self, sol1: SolutionCandidate, sol2: SolutionCandidate) -> float:
        """计算两个方案的相似度 (0-1)"""
        # 类型相似度
        type_similarity = 1.0 if sol1.type == sol2.type else 0.0
        
        # 风险等级相似度
        risk_similarity = 1.0 if sol1.risk_level == sol2.risk_level else 0.0
        
        # 资源强度相似度
        resource_similarity = 1.0 if sol1.resource_intensity == sol2.resource_intensity else 0.0
        
        # 标签相似度 (Jaccard相似度)
        tags1 = set(sol1.tags)
        tags2 = set(sol2.tags)
        if tags1 or tags2:
            tag_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
        else:
            tag_similarity = 0.0
        
        # 加权平均
        weights = {"type": 0.3, "risk": 0.3, "resource": 0.2, "tags": 0.2}
        similarity = (
            type_similarity * weights["type"] +
            risk_similarity * weights["risk"] +
            resource_similarity * weights["resource"] +
            tag_similarity * weights["tags"]
        )
        
        return similarity
    
    def rank_solutions(
        self,
        solutions: List[SolutionCandidate],
        criteria: Optional[RankingCriteria] = None
    ) -> List[RankedSolution]:
        """
        多维度方案排序
        
        Args:
            solutions: 待排序的方案列表
            criteria: 排序标准，如未提供使用默认标准
        
        Returns:
            排序后的方案列表
        """
        criteria = criteria or RankingCriteria()
        
        # 过滤不符合约束的方案
        filtered_solutions = []
        for solution in solutions:
            meets_constraints = self._check_constraints(solution, criteria)
            if meets_constraints:
                filtered_solutions.append(solution)
        
        # 计算权重
        weights = criteria.normalize_weights()
        
        # 计算评分并排序
        ranked_solutions = []
        for solution in filtered_solutions:
            overall_score = solution.calculate_overall_score(weights)
            
            # 应用额外权重 (成本和时间效率)
            final_score = overall_score
            
            if criteria.prioritize_cost_efficiency:
                # 成本越低越好，归一化到0-1
                cost_score = 1.0 - (solution.estimated_cost / 10.0)
                final_score = final_score * 0.7 + cost_score * 0.3
            
            if criteria.prioritize_time_efficiency:
                # 时间越短越好，归一化到0-1 (假设最大300小时)
                time_score = 1.0 - (solution.estimated_time / 300.0)
                final_score = final_score * 0.7 + time_score * 0.3
            
            # 计算各维度得分
            weighted_scores = {
                "technical_feasibility": solution.technical_feasibility * weights.get("technical_feasibility", 0.25),
                "business_value": solution.business_value * weights.get("business_value", 0.25),
                "user_experience": solution.user_experience * weights.get("user_experience", 0.25),
                "success_probability": solution.success_probability * weights.get("success_probability", 0.25),
            }
            
            ranked_solutions.append((solution, final_score, weighted_scores))
        
        # 按最终得分排序
        ranked_solutions.sort(key=lambda x: x[1], reverse=True)
        
        # 构建RankedSolution对象
        result = []
        for i, (solution, final_score, weighted_scores) in enumerate(ranked_solutions, 1):
            meets_constraints = self._check_constraints(solution, criteria)
            
            # 生成推荐理由
            recommendation_reason = self._generate_recommendation_reason(
                solution, i, final_score, weighted_scores
            )
            
            result.append(RankedSolution(
                solution=solution,
                rank=i,
                overall_score=final_score,
                weighted_scores=weighted_scores,
                meets_constraints=meets_constraints,
                recommendation_reason=recommendation_reason,
            ))
        
        return result
    
    def _check_constraints(self, solution: SolutionCandidate, criteria: RankingCriteria) -> bool:
        """检查方案是否符合约束条件"""
        # 风险容忍度检查
        risk_order = {RiskLevel.CONSERVATIVE: 1, RiskLevel.MODERATE: 2, RiskLevel.AGGRESSIVE: 3}
        solution_risk_level = risk_order.get(solution.risk_level, 3)
        max_risk_level = risk_order.get(criteria.max_risk_tolerance, 3)
        if solution_risk_level > max_risk_level:
            return False
        
        # 资源强度检查
        resource_order = {ResourceIntensity.LIGHT: 1, ResourceIntensity.MEDIUM: 2, ResourceIntensity.HEAVY: 3}
        solution_resource = resource_order.get(solution.resource_intensity, 3)
        max_resource = resource_order.get(criteria.max_resource_intensity, 3)
        if solution_resource > max_resource:
            return False
        
        return True
    
    def _generate_recommendation_reason(
        self,
        solution: SolutionCandidate,
        rank: int,
        overall_score: float,
        weighted_scores: Dict[str, float]
    ) -> str:
        """生成推荐理由"""
        strengths = []
        
        # 识别优势维度
        if solution.technical_feasibility > 0.8:
            strengths.append("技术可行性高")
        if solution.business_value > 0.8:
            strengths.append("商业价值显著")
        if solution.user_experience > 0.8:
            strengths.append("用户体验优秀")
        if solution.success_probability > 0.8:
            strengths.append("成功概率高")
        
        if strengths:
            strength_text = "，".join(strengths)
            reason = f"该方案在{strength_text}方面表现突出"
        else:
            # 找最高分维度
            max_dimension = max(weighted_scores.items(), key=lambda x: x[1])
            dimension_names = {
                "technical_feasibility": "技术可行性",
                "business_value": "商业价值",
                "user_experience": "用户体验",
                "success_probability": "成功概率",
            }
            reason = f"该方案在{dimension_names.get(max_dimension[0], '综合评估')}方面表现最佳"
        
        # 添加风险资源信息
        risk_text = {"conservative": "保守", "moderate": "中等", "aggressive": "激进"}.get(
            solution.risk_level.value, solution.risk_level.value
        )
        resource_text = {"light": "轻量", "medium": "中等", "heavy": "重型"}.get(
            solution.resource_intensity.value, solution.resource_intensity.value
        )
        
        reason += f"，采用{risk_text}风险策略和{resource_text}资源配置。"
        
        return reason
    
    def generate_comparison_report(
        self,
        solutions: List[SolutionCandidate],
        ranked_solutions: Optional[List[RankedSolution]] = None
    ) -> Dict[str, Any]:
        """生成方案比较报告"""
        if ranked_solutions is None:
            ranked_solutions = self.rank_solutions(solutions)
        
        # 基本统计
        stats = {
            "total_solutions": len(solutions),
            "solution_types": {},
            "risk_distribution": {},
            "resource_distribution": {},
        }
        
        for solution in solutions:
            stats["solution_types"][solution.type.value] = stats["solution_types"].get(solution.type.value, 0) + 1
            stats["risk_distribution"][solution.risk_level.value] = stats["risk_distribution"].get(solution.risk_level.value, 0) + 1
            stats["resource_distribution"][solution.resource_intensity.value] = stats["resource_distribution"].get(solution.resource_intensity.value, 0) + 1
        
        # 评分统计
        if ranked_solutions:
            scores = [rs.overall_score for rs in ranked_solutions]
            if scores:
                stats["score_range"] = {"min": min(scores), "max": max(scores), "avg": sum(scores)/len(scores)}
        
        return {
            "statistics": stats,
            "solutions": [s.to_dict() for s in solutions],
            "rankings": [
                {
                    "rank": rs.rank,
                    "solution_id": rs.solution.id,
                    "overall_score": rs.overall_score,
                    "recommendation_reason": rs.recommendation_reason,
                    "meets_constraints": rs.meets_constraints,
                }
                for rs in ranked_solutions
            ],
            "recommendations": [
                f"第{rs.rank}名: {rs.solution.title} (评分: {rs.overall_score:.2f}) - {rs.recommendation_reason}"
                for rs in ranked_solutions[:3]  # 只显示前三名
            ],
            "generated_at": datetime.now().isoformat(),
        }


def create_multi_solution_generator() -> MultiSolutionGenerator:
    """创建多方案生成器实例"""
    return MultiSolutionGenerator()


# 便捷函数
def generate_and_rank_solutions(
    problem: str,
    context: Optional[Dict[str, Any]] = None,
    num_solutions: int = 3,
    criteria: Optional[RankingCriteria] = None
) -> Dict[str, Any]:
    """快速生成并排序解决方案"""
    generator = create_multi_solution_generator()
    solutions = generator.generate_solutions(problem, context, num_solutions)
    ranked = generator.rank_solutions(solutions, criteria)
    report = generator.generate_comparison_report(solutions, ranked)
    return report


if __name__ == "__main__":
    print("=" * 70)
    print("多方案并行生成系统测试")
    print("=" * 70)
    
    # 测试问题
    test_problem = """
    我需要开发一个企业级的用户行为分析系统，要求：
    1. 能够实时处理用户行为数据
    2. 提供用户画像和个性化推荐
    3. 支持大规模并发访问
    4. 集成到现有电商平台中
    """
    
    context = {"domain": "ecommerce", "budget_constraint": "medium"}
    
    print(f"\n📋 测试问题: {test_problem[:100]}...")
    print(f"领域: {context['domain']}")
    print("-" * 70)
    
    # 生成解决方案
    generator = create_multi_solution_generator()
    solutions = generator.generate_solutions(
        problem=test_problem,
        context=context,
        num_solutions=4,
        diversity_threshold=0.6
    )
    
    print(f"\n🎯 生成了 {len(solutions)} 个多样化解决方案:")
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution.title}")
        print(f"   技术路线: {solution.type.value}")
        print(f"   风险等级: {solution.risk_level.value}")
        print(f"   资源要求: {solution.resource_intensity.value}")
        print(f"   预估时间: {solution.estimated_time}小时")
        print(f"   预估成本: {solution.estimated_cost}/10")
        print(f"   成功概率: {solution.success_probability:.1%}")
    
    # 排序方案
    criteria = RankingCriteria(
        prioritize_business_value=0.4,
        prioritize_user_experience=0.3,
        prioritize_technical_feasibility=0.2,
        prioritize_success_probability=0.1,
        prioritize_cost_efficiency=True,
        max_risk_tolerance=RiskLevel.MODERATE,
    )
    
    ranked = generator.rank_solutions(solutions, criteria)
    
    print(f"\n🏆 排序结果 (按业务价值和成本效率优先):")
    for rs in ranked:
        print(f"\n第{rs.rank}名: {rs.solution.title}")
        print(f"   综合评分: {rs.overall_score:.3f}")
        print(f"   推荐理由: {rs.recommendation_reason}")
    
    # 生成报告
    report = generator.generate_comparison_report(solutions, ranked)
    
    print(f"\n📊 统计信息:")
    print(f"   方案类型分布: {report['statistics']['solution_types']}")
    print(f"   风险分布: {report['statistics']['risk_distribution']}")
    print(f"   资源分布: {report['statistics']['resource_distribution']}")
    
    print(f"\n💡 推荐方案:")
    for rec in report['recommendations']:
        print(f"   • {rec}")
    
    print("\n" + "=" * 70)
    print("测试完成，多方案生成系统运行正常")
    print("=" * 70)
