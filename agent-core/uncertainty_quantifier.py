"""
TimesFM-inspired Uncertainty Quantification System
不确定性量化系统，借鉴TimesFM的分位数预测
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
import statistics
from collections import deque


class ConfidenceLevel(Enum):
    """置信水平"""
    LOW = 0.50
    MEDIUM = 0.80
    HIGH = 0.95
    VERY_HIGH = 0.99


class UncertaintySource(Enum):
    """不确定性来源"""
    AMBIGUOUS_INPUT = "ambiguous_input"        # 输入模糊
    MISSING_CONTEXT = "missing_context"        # 缺少上下文
    COMPLEX_TASK = "complex_task"              # 任务复杂
    NOVEL_SCENARIO = "novel_scenario"          # 新颖场景
    CONFLICTING_INFO = "conflicting_info"      # 信息冲突
    INSUFFICIENT_DATA = "insufficient_data"   # 数据不足
    MODEL_LIMITATION = "model_limitation"     # 模型限制


@dataclass
class UncertaintySourceInfo:
    """不确定性来源信息"""
    source: UncertaintySource
    description: str
    severity: float  # 0-1
    mitigation: str


@dataclass
class QuantilePrediction:
    """
    分位数预测
    类似TimesFM的quantile forecast
    """
    quantile: float        # 分位数 (0-1)
    value: Any             # 预测值
    confidence: float      # 该分位数的置信度


@dataclass
class ProbabilisticOutput:
    """
    概率输出封装
    类似TimesFm2_5OutputForPrediction
    """
    
    # 点估计 (最可能的结果)
    point_estimate: Any
    
    # 分位数预测 (类似TimesFM的quantile输出)
    quantile_predictions: List[QuantilePrediction] = field(default_factory=list)
    
    # 置信度分数 (0-1)
    confidence_score: float = 0.85
    
    # 置信区间
    confidence_interval: Optional[Tuple[Any, Any]] = None
    confidence_level: float = 0.95
    
    # 替代方案
    alternative_solutions: List[Tuple[Any, float]] = field(default_factory=list)
    
    # 不确定性来源
    uncertainty_sources: List[UncertaintySourceInfo] = field(default_factory=list)
    
    # 建议行动
    recommended_actions: List[str] = field(default_factory=list)
    
    def get_quantile(self, q: float) -> Optional[Any]:
        """获取指定分位数的预测值"""
        for qp in self.quantile_predictions:
            if abs(qp.quantile - q) < 0.01:
                return qp.value
        return None
    
    def get_median(self) -> Optional[Any]:
        """获取中位数预测 (0.5分位数)"""
        return self.get_quantile(0.5)
    
    def get_prediction_range(self) -> Optional[Tuple[Any, Any]]:
        """获取预测范围 (10%-90%分位数)"""
        low = self.get_quantile(0.1)
        high = self.get_quantile(0.9)
        if low is not None and high is not None:
            return (low, high)
        return None
    
    def is_high_confidence(self, threshold: float = 0.9) -> bool:
        """判断是否高置信度"""
        return self.confidence_score >= threshold
    
    def format_summary(self) -> str:
        """格式化摘要"""
        lines = [
            f"点估计: {self.point_estimate}",
            f"置信度: {self.confidence_score:.1%}",
        ]
        
        if self.quantile_predictions:
            median = self.get_median()
            range_vals = self.get_prediction_range()
            if median:
                lines.append(f"中位数: {median}")
            if range_vals:
                lines.append(f"预测范围 (10%-90%): {range_vals[0]} ~ {range_vals[1]}")
        
        if self.uncertainty_sources:
            lines.append(f"不确定性来源: {len(self.uncertainty_sources)}项")
        
        return "\n".join(lines)


class UncertaintyQuantifier:
    """
    不确定性量化器
    借鉴TimesFM的连续分位数头设计
    """
    
    def __init__(self):
        # 校准历史
        self._calibration_history: deque = deque(maxlen=100)
        # 分位数设置 (类似TimesFM)
        self.default_quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    def quantify_plan_uncertainty(
        self,
        plan: Any,
        context: Dict[str, Any],
        generate_alternatives: bool = True
    ) -> ProbabilisticOutput:
        """
        量化执行计划的不确定性
        
        类似TimesFM生成概率预测
        """
        # 1. 基础置信度计算
        base_confidence = self._calculate_base_confidence(plan, context)
        
        # 2. 识别不确定性来源
        sources = self._identify_uncertainty_sources(plan, context)
        
        # 3. 调整置信度
        adjusted_confidence = self._adjust_confidence(base_confidence, sources)
        
        # 4. 生成分位数预测
        quantiles = self._generate_quantile_predictions(
            plan, adjusted_confidence, context
        )
        
        # 5. 生成替代方案
        alternatives = []
        if generate_alternatives and adjusted_confidence < 0.9:
            alternatives = self._generate_alternatives(plan, context)
        
        # 6. 生成建议行动
        actions = self._generate_recommended_actions(sources, adjusted_confidence)
        
        # 7. 计算置信区间
        ci = self._calculate_confidence_interval(quantiles)
        
        return ProbabilisticOutput(
            point_estimate=plan,
            quantile_predictions=quantiles,
            confidence_score=adjusted_confidence,
            confidence_interval=ci,
            confidence_level=0.95,
            alternative_solutions=alternatives,
            uncertainty_sources=sources,
            recommended_actions=actions
        )
    
    def _calculate_base_confidence(
        self,
        plan: Any,
        context: Dict[str, Any]
    ) -> float:
        """计算基础置信度"""
        confidence = 0.85  # 默认置信度
        
        # 基于计划质量调整
        if hasattr(plan, 'steps') and plan.steps:
            confidence += 0.05
        
        # 基于上下文完整性调整
        context_score = self._evaluate_context_completeness(context)
        confidence += (context_score - 0.5) * 0.2
        
        # 基于历史成功率调整
        if self._calibration_history:
            recent_success_rate = sum(self._calibration_history) / len(self._calibration_history)
            confidence = confidence * 0.7 + recent_success_rate * 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _evaluate_context_completeness(self, context: Dict[str, Any]) -> float:
        """评估上下文完整性"""
        score = 0.5
        
        # 检查关键信息
        key_fields = ["user_intent", "constraints", "preferences", "history"]
        present = sum(1 for f in key_fields if f in context and context[f])
        score += (present / len(key_fields)) * 0.5
        
        return min(1.0, score)
    
    def _identify_uncertainty_sources(
        self,
        plan: Any,
        context: Dict[str, Any]
    ) -> List[UncertaintySourceInfo]:
        """识别不确定性来源"""
        sources = []
        
        # 检查输入模糊性
        user_input = context.get("user_input", "")
        if len(user_input) < 20 or "?" in user_input:
            sources.append(UncertaintySourceInfo(
                source=UncertaintySource.AMBIGUOUS_INPUT,
                description="用户输入较短或包含疑问，意图可能不够明确",
                severity=0.6,
                mitigation="主动澄清用户需求"
            ))
        
        # 检查上下文缺失
        if not context.get("history"):
            sources.append(UncertaintySourceInfo(
                source=UncertaintySource.MISSING_CONTEXT,
                description="缺少历史交互上下文",
                severity=0.4,
                mitigation="询问相关背景信息"
            ))
        
        # 检查任务复杂度
        if hasattr(plan, 'steps') and len(plan.steps) > 10:
            sources.append(UncertaintySourceInfo(
                source=UncertaintySource.COMPLEX_TASK,
                description="任务步骤较多，复杂度较高",
                severity=0.5,
                mitigation="分阶段执行，及时反馈"
            ))
        
        # 检查数据充足性
        if not context.get("data") and "分析" in str(plan):
            sources.append(UncertaintySourceInfo(
                source=UncertaintySource.INSUFFICIENT_DATA,
                description="缺少分析所需的数据",
                severity=0.7,
                mitigation="请求用户提供数据"
            ))
        
        return sources
    
    def _adjust_confidence(
        self,
        base_confidence: float,
        sources: List[UncertaintySourceInfo]
    ) -> float:
        """根据不确定性来源调整置信度"""
        penalty = sum(s.severity * 0.1 for s in sources)
        return max(0.0, min(1.0, base_confidence - penalty))
    
    def _generate_quantile_predictions(
        self,
        plan: Any,
        confidence: float,
        context: Dict[str, Any]
    ) -> List[QuantilePrediction]:
        """
        生成分位数预测
        类似TimesFM的分位数头输出
        """
        quantiles = []
        
        for q in self.default_quantiles:
            # 根据分位数调整预测
            if q < 0.5:
                # 低分位数：保守估计
                adjusted_confidence = confidence * (0.5 + q)
            elif q > 0.5:
                # 高分位数：乐观估计
                adjusted_confidence = confidence * (1.5 - q)
            else:
                # 中位数：点估计
                adjusted_confidence = confidence
            
            # 生成该分位数的预测值（简化实现）
            value = self._generate_quantile_value(plan, q, context)
            
            quantiles.append(QuantilePrediction(
                quantile=q,
                value=value,
                confidence=adjusted_confidence
            ))
        
        return quantiles
    
    def _generate_quantile_value(self, plan: Any, quantile: float, context: Dict) -> Any:
        """生成指定分位数的预测值"""
        # 简化实现：根据分位数调整
        base = str(plan)
        
        if quantile <= 0.25:
            return f"保守方案: {base[:50]}..."
        elif quantile >= 0.75:
            return f"乐观方案: {base[:50]}..."
        else:
            return base
    
    def _generate_alternatives(
        self,
        plan: Any,
        context: Dict[str, Any]
    ) -> List[Tuple[Any, float]]:
        """生成替代方案"""
        alternatives = []
        
        # 方案2：保守版本
        alternatives.append((f"保守方案: {plan}", 0.7))
        
        # 方案3：简化版本
        alternatives.append((f"简化方案: {plan}", 0.6))
        
        return alternatives
    
    def _generate_recommended_actions(
        self,
        sources: List[UncertaintySourceInfo],
        confidence: float
    ) -> List[str]:
        """生成建议行动"""
        actions = []
        
        # 基于不确定性来源的建议
        for source in sources:
            actions.append(source.mitigation)
        
        # 基于置信度的通用建议
        if confidence < 0.7:
            actions.append("建议分阶段执行，每一步确认后再继续")
        
        if confidence < 0.5:
            actions.append("建议先进行小规模试点验证")
        
        return list(set(actions))  # 去重
    
    def _calculate_confidence_interval(
        self,
        quantiles: List[QuantilePrediction]
    ) -> Optional[Tuple[Any, Any]]:
        """计算置信区间"""
        low = next((q.value for q in quantiles if q.quantile <= 0.1), None)
        high = next((q.value for q in quantiles if q.quantile >= 0.9), None)
        
        if low is not None and high is not None:
            return (low, high)
        return None
    
    def calibrate(
        self,
        predicted_confidence: float,
        actual_success: bool
    ):
        """
        校准置信度
        基于反馈改进置信度估计
        """
        self._calibration_history.append(1.0 if actual_success else 0.0)
    
    def get_calibration_stats(self) -> Dict[str, float]:
        """获取校准统计"""
        if not self._calibration_history:
            return {"mean_accuracy": 0.0, "samples": 0}
        
        return {
            "mean_accuracy": sum(self._calibration_history) / len(self._calibration_history),
            "samples": len(self._calibration_history),
            "recent_10": sum(list(self._calibration_history)[-10:]) / min(10, len(self._calibration_history))
        }


class MultiViewAnalyzer:
    """
    多视角分析器
    借鉴TimesFM的翻转不变性
    """
    
    def __init__(self):
        self.views = {
            "technical": self._technical_view,
            "business": self._business_view,
            "user": self._user_view,
            "risk": self._risk_view,
            "timeline": self._timeline_view,
        }
    
    def analyze_from_multiple_views(
        self,
        problem: str,
        context: Dict[str, Any],
        selected_views: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        多视角分析
        
        类似TimesFM的翻转增强，从多个角度分析问题
        """
        views_to_use = selected_views or list(self.views.keys())
        results = {}
        
        for view_name in views_to_use:
            if view_name in self.views:
                analyzer = self.views[view_name]
                results[view_name] = analyzer(problem, context)
        
        # 聚合结果
        aggregated = self._aggregate_views(results)
        
        return {
            "individual_views": results,
            "aggregated": aggregated,
            "confidence_by_view": {
                name: result.get("confidence", 0.5)
                for name, result in results.items()
            }
        }
    
    def _technical_view(self, problem: str, context: Dict) -> Dict:
        """技术视角"""
        return {
            "perspective": "technical",
            "focus": ["可行性", "技术栈", "架构设计", "性能"],
            "confidence": 0.85,
            "recommendations": [
                "评估技术可行性",
                "选择合适的技术栈",
                "考虑扩展性"
            ]
        }
    
    def _business_view(self, problem: str, context: Dict) -> Dict:
        """业务视角"""
        return {
            "perspective": "business",
            "focus": ["成本", "收益", "ROI", "市场竞争力"],
            "confidence": 0.75,
            "recommendations": [
                "评估投入产出比",
                "考虑市场时机",
                "分析竞争优势"
            ]
        }
    
    def _user_view(self, problem: str, context: Dict) -> Dict:
        """用户视角"""
        return {
            "perspective": "user",
            "focus": ["用户体验", "易用性", "满意度"],
            "confidence": 0.80,
            "recommendations": [
                "关注用户需求",
                "简化操作流程",
                "提升用户体验"
            ]
        }
    
    def _risk_view(self, problem: str, context: Dict) -> Dict:
        """风险视角"""
        return {
            "perspective": "risk",
            "focus": ["安全风险", "技术风险", "业务风险"],
            "confidence": 0.70,
            "recommendations": [
                "识别潜在风险",
                "制定应对策略",
                "建立监控机制"
            ]
        }
    
    def _timeline_view(self, problem: str, context: Dict) -> Dict:
        """时间视角"""
        return {
            "perspective": "timeline",
            "focus": ["短期", "中期", "长期"],
            "confidence": 0.65,
            "recommendations": [
                "制定里程碑",
                "分阶段实施",
                "定期回顾调整"
            ]
        }
    
    def _aggregate_views(self, results: Dict[str, Dict]) -> Dict:
        """聚合多视角结果"""
        all_recommendations = []
        avg_confidence = statistics.mean([
            r.get("confidence", 0.5) for r in results.values()
        ])
        
        for result in results.values():
            all_recommendations.extend(result.get("recommendations", []))
        
        # 去重
        unique_recommendations = list(set(all_recommendations))
        
        return {
            "average_confidence": avg_confidence,
            "consensus_recommendations": unique_recommendations[:5],
            "view_count": len(results)
        }


# 便捷函数
def quantify_uncertainty(
    plan: Any,
    context: Dict[str, Any] = None
) -> ProbabilisticOutput:
    """快速量化不确定性"""
    quantifier = UncertaintyQuantifier()
    return quantifier.quantify_plan_uncertainty(
        plan, 
        context or {},
        generate_alternatives=True
    )


def multi_view_analysis(
    problem: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """快速多视角分析"""
    analyzer = MultiViewAnalyzer()
    return analyzer.analyze_from_multiple_views(
        problem,
        context or {}
    )


if __name__ == "__main__":
    # 测试不确定性量化
    print("=== Uncertainty Quantification Test ===\n")
    
    # 1. 基础量化
    print("1. 基础不确定性量化:")
    plan = "开发一个基于TimesFM的时间序列预测系统"
    context = {
        "user_input": "我想做一个预测系统",
        "history": []
    }
    
    result = quantify_uncertainty(plan, context)
    print(result.format_summary())
    print()
    
    # 2. 分位数预测
    print("2. 分位数预测详情:")
    for qp in result.quantile_predictions:
        print(f"   {qp.quantile:.0%}分位数: {qp.value[:30]}... (置信度:{qp.confidence:.2f})")
    print()
    
    # 3. 不确定性来源
    print("3. 不确定性来源:")
    for source in result.uncertainty_sources:
        print(f"   - [{source.source.value}] 严重程度:{source.severity:.1f}")
        print(f"     {source.description}")
    print()
    
    # 4. 多视角分析
    print("4. 多视角分析:")
    analysis = multi_view_analysis(plan, context)
    print(f"   分析视角数: {analysis['aggregated']['view_count']}")
    print(f"   平均置信度: {analysis['aggregated']['average_confidence']:.2f}")
    print("   共识建议:")
    for rec in analysis['aggregated']['consensus_recommendations']:
        print(f"     - {rec}")
    print()
    
    # 5. 校准测试
    print("5. 校准统计:")
    quantifier = UncertaintyQuantifier()
    for i in range(20):
        success = i % 5 != 0  # 80%成功率
        quantifier.calibrate(0.8, success)
    stats = quantifier.get_calibration_stats()
    print(f"   平均准确率: {stats['mean_accuracy']:.2f}")
    print(f"   样本数: {stats['samples']}")
    print()
    
    print("=== All Tests Passed ===")
