"""
TimesFM Integration Module
TimesFM能力集成主模块
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# 导入TimesFM-inspired模块
from config_system import (
    AgentCapabilityConfig, 
    ConfigManager, 
    PresetConfigs,
    get_config,
    update_config
)
from task_patcher import (
    TaskPatcher,
    PatchingResult,
    HierarchicalPatcher
)
from zero_shot_knowledge import (
    ZeroShotKnowledgeBase,
    KnowledgePattern,
    retrieve_knowledge
)
from uncertainty_quantifier import (
    UncertaintyQuantifier,
    ProbabilisticOutput,
    MultiViewAnalyzer,
    quantify_uncertainty,
    multi_view_analysis
)

from multi_solution_generator import (
    MultiSolutionGenerator,
    SolutionCandidate,
    RankingCriteria,
    RankedSolution,
    generate_and_rank_solutions
)


@dataclass
class TimesFMCapabilities:
    """TimesFM能力集合"""
    config: AgentCapabilityConfig
    patcher: TaskPatcher
    knowledge_base: ZeroShotKnowledgeBase
    uncertainty_quantifier: UncertaintyQuantifier
    multi_view_analyzer: MultiViewAnalyzer
    multi_solution_generator: MultiSolutionGenerator


class TimesFMIntegratedAgent:
    """
    TimesFM能力集成Agent
    
    融合TimesFM的核心设计思想:
    - 配置驱动架构
    - 任务Patch化处理
    - 零样本知识检索
    - 不确定性量化
    - 多视角分析
    """
    
    def __init__(self, preset: str = "default"):
        # 配置管理器
        self.config_manager = ConfigManager()
        
        # 加载预置配置
        if preset == "zero_shot":
            self.config = PresetConfigs.zero_shot_optimized()
        elif preset == "high_accuracy":
            self.config = PresetConfigs.high_accuracy()
        elif preset == "fast":
            self.config = PresetConfigs.fast_response()
        else:
            self.config = AgentCapabilityConfig()
        
        self.config_manager._config = self.config
        
        # 初始化组件
        self.patcher = TaskPatcher(
            patch_size=self.config.task_patch.patch_size,
            patch_overlap=self.config.task_patch.patch_overlap
        )
        
        self.knowledge_base = ZeroShotKnowledgeBase()
        
        self.uncertainty_quantifier = UncertaintyQuantifier()
        
        self.multi_view_analyzer = MultiViewAnalyzer()
        
        # 初始化多方案生成器
        self.multi_solution_generator = MultiSolutionGenerator()
        
        # 统计信息
        self._stats = {
            "tasks_processed": 0,
            "patches_created": 0,
            "knowledge_retrievals": 0,
            "uncertainty_quantifications": 0,
            "solutions_generated": 0,
        }
    
    def process_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理任务的主入口
        
        整合TimesFM-inspired的完整流程:
        1. 任务Patch化
        2. 零样本知识检索
        3. 不确定性量化
        4. 多视角分析
        """
        context = context or {}
        
        # Step 1: 任务Patch化 (类似TimesFM的Patching)
        patching_result = self.patcher.patch_task(
            task,
            custom_patch_size=self.config.task_patch.patch_size
        )
        
        # Step 2: 检索零样本知识 (类似TimesFM预训练知识)
        relevant_knowledge = self.knowledge_base.retrieve_for_task(
            task,
            top_k=3
        )
        
        # Step 3: 量化不确定性 (类似TimesFM的分位数预测)
        uncertainty_result = self.uncertainty_quantifier.quantify_plan_uncertainty(
            plan=patching_result,
            context=context,
            generate_alternatives=self.config.uncertainty.output_mode.value != "point_only"
        )
        
        # Step 4: 多视角分析 (类似TimesFM的翻转不变性)
        multi_view_result = None
        if self.config.multi_view.enable_multi_view:
            multi_view_result = self.multi_view_analyzer.analyze_from_multiple_views(
                problem=task,
                context=context,
                selected_views=self.config.multi_view.default_views
            )
        
        # 更新统计
        self._stats["tasks_processed"] += 1
        self._stats["patches_created"] += patching_result.total_patches
        self._stats["knowledge_retrievals"] += len(relevant_knowledge)
        self._stats["uncertainty_quantifications"] += 1
        
        # 返回综合结果
        return {
            "task": task,
            "configuration": {
                "preset": self.config.version,
                "patch_size": self.config.task_patch.patch_size,
                "multi_view_enabled": self.config.multi_view.enable_multi_view,
            },
            "patching": {
                "total_patches": patching_result.total_patches,
                "estimated_effort": patching_result.total_estimated_effort,
                "critical_path": patching_result.critical_path_length,
                "patches": [p.to_dict() for p in patching_result.patches],
            },
            "knowledge": {
                "patterns_found": len(relevant_knowledge),
                "patterns": [
                    {
                        "name": p.name,
                        "domain": p.domain.value,
                        "confidence": p.confidence,
                        "solutions": p.solutions[:2],
                    }
                    for p in relevant_knowledge
                ],
            },
            "uncertainty": {
                "confidence_score": uncertainty_result.confidence_score,
                "quantiles_available": len(uncertainty_result.quantile_predictions) > 0,
                "sources": [
                    {
                        "type": s.source.value,
                        "severity": s.severity,
                        "description": s.description,
                    }
                    for s in uncertainty_result.uncertainty_sources
                ],
                "recommended_actions": uncertainty_result.recommended_actions,
            },
            "multi_view": multi_view_result,
            "execution_order": [
                {
                    "index": p.index,
                    "content": p.content[:50] + "..." if len(p.content) > 50 else p.content,
                    "priority": p.priority.name,
                }
                for p in self.patcher.get_execution_order(patching_result)
            ],
        }
    
    def generate_multiple_solutions(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        num_solutions: Optional[int] = None,
        ranking_criteria: Optional[RankingCriteria] = None
    ) -> Dict[str, Any]:
        """
        生成多个解决方案并排序
        
        Args:
            problem: 问题描述
            context: 上下文信息
            num_solutions: 方案数量，如未提供使用配置默认值
            ranking_criteria: 排序标准，如未提供使用配置默认值
        
        Returns:
            包含解决方案和排序结果的字典
        """
        context = context or {}
        
        # 使用配置值或默认值
        if num_solutions is None:
            num_solutions = self.config.multi_solution.default_num_solutions
        
        # 生成解决方案
        solutions = self.multi_solution_generator.generate_solutions(
            problem=problem,
            context=context,
            num_solutions=num_solutions,
            diversity_threshold=self.config.multi_solution.diversity_threshold,
            enforce_diversity=self.config.multi_solution.enforce_diversity
        )
        
        # 如果未提供排序标准，从配置创建
        if ranking_criteria is None:
            # 从配置创建RankingCriteria
            ranking_criteria = RankingCriteria()
            # 这里可以根据配置设置更多参数
        
        # 排序解决方案
        ranked_solutions = self.multi_solution_generator.rank_solutions(
            solutions, ranking_criteria
        )
        
        # 生成报告
        report = self.multi_solution_generator.generate_comparison_report(
            solutions, ranked_solutions
        )
        
        # 更新统计
        self._stats["solutions_generated"] = self._stats.get("solutions_generated", 0) + len(solutions)
        
        return report
    
    def get_capabilities(self) -> TimesFMCapabilities:
        """获取能力集合"""
        return TimesFMCapabilities(
            config=self.config,
            patcher=self.patcher,
            knowledge_base=self.knowledge_base,
            uncertainty_quantifier=self.uncertainty_quantifier,
            multi_view_analyzer=self.multi_view_analyzer,
            multi_solution_generator=self.multi_solution_generator
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._stats.copy()
    
    def update_configuration(self, updates: Dict[str, Any]):
        """更新配置"""
        self.config_manager.update_config(updates)
        self.config = self.config_manager.config
        
        # 重新初始化组件
        self.patcher = TaskPatcher(
            patch_size=self.config.task_patch.patch_size,
            patch_overlap=self.config.task_patch.patch_overlap
        )
    
    def save_state(self, filepath: str):
        """保存状态"""
        import json
        state = {
            "config": self.config.to_dict(),
            "stats": self._stats,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_state(cls, filepath: str) -> "TimesFMIntegratedAgent":
        """加载状态"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        agent = cls()
        agent.config = AgentCapabilityConfig.from_dict(state["config"])
        agent._stats = state.get("stats", {})
        return agent


def create_timesfm_agent(preset: str = "default") -> TimesFMIntegratedAgent:
    """创建TimesFM能力集成的Agent"""
    return TimesFMIntegratedAgent(preset=preset)


# 便捷函数
def timesfm_process(task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """快速使用TimesFM能力处理任务"""
    agent = create_timesfm_agent()
    return agent.process_task(task, context)


if __name__ == "__main__":
    print("="*70)
    print("TimesFM-inspired Integration Test")
    print("="*70)
    
    # 创建Agent
    agent = create_timesfm_agent(preset="high_accuracy")
    
    # 测试任务
    test_task = """
    我需要开发一个企业级的时间序列预测系统，要求：
    1. 基于TimesFM模型进行预测
    2. 支持大规模并发请求
    3. 提供可视化仪表盘
    4. 集成到现有数据中台
    请给出完整的技术方案和实现步骤。
    """
    
    print(f"\n测试任务:\n{test_task}\n")
    print("-"*70)
    
    # 处理任务
    result = agent.process_task(test_task, context={
        "user_input": test_task,
        "domain": "time_series_forecasting"
    })
    
    # 输出结果
    print("\n📊 处理结果:\n")
    
    print(f"配置版本: {result['configuration']['preset']}")
    print(f"多视角分析: {'启用' if result['configuration']['multi_view_enabled'] else '禁用'}")
    
    print(f"\n🔧 任务分解:")
    print(f"  - 总Patches: {result['patching']['total_patches']}")
    print(f"  - 估计工作量: {result['patching']['estimated_effort']}")
    print(f"  - 关键路径: {result['patching']['critical_path']}步")
    
    print(f"\n📚 相关知识:")
    for p in result['knowledge']['patterns']:
        print(f"  - {p['name']} (置信度: {p['confidence']:.2f})")
    
    print(f"\n🎯 不确定性分析:")
    print(f"  - 整体置信度: {result['uncertainty']['confidence_score']:.1%}")
    print(f"  - 不确定性来源: {len(result['uncertainty']['sources'])}项")
    for s in result['uncertainty']['sources']:
        print(f"    • [{s['type']}] 严重程度: {s['severity']:.1f}")
    
    print(f"\n📋 建议行动:")
    for action in result['uncertainty']['recommended_actions']:
        print(f"  - {action}")
    
    print(f"\n🔄 执行顺序:")
    for i, step in enumerate(result['execution_order'], 1):
        print(f"  {i}. [{step['priority']}] {step['content']}")
    
    if result['multi_view']:
        print(f"\n🔍 多视角分析:")
        mv = result['multi_view']['aggregated']
        print(f"  - 视角数量: {mv['view_count']}")
        print(f"  - 平均置信度: {mv['average_confidence']:.2f}")
    
    print("\n" + "="*70)
    print("统计信息:")
    stats = agent.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print("="*70)
