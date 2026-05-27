#!/usr/bin/env python3
"""
Git上下文与多方案生成系统集成模块
基于Git状态生成多样化、上下文感知的解决方案

设计理念：
1. Git状态作为解决方案生成的上下文
2. 基于Git风险调整方案风险评估
3. 提供与Git工作流程兼容的实施建议
4. 支持多种Git场景的针对性方案生成
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

# 导入Git上下文模块
from git_context_integration import (
    GitContextProvider, 
    GitStatus,
    GitFileChange,
    GitChangeType,
    GitContextUncertaintyAnalyzer
)

# 导入多方案生成模块
from multi_solution_generator import (
    MultiSolutionGenerator,
    SolutionCandidate,
    SolutionType,
    RiskLevel,
    ResourceIntensity
)

# 导入配置系统
from config_system import get_config


class GitSolutionStrategy(Enum):
    """Git解决方案策略"""
    CONFLICT_RESOLUTION = "conflict_resolution"      # 冲突解决策略
    UNTRACKED_MANAGEMENT = "untracked_management"    # 未跟踪文件管理策略
    CORE_FILE_MODIFICATION = "core_file_modification" # 核心文件修改策略
    FEATURE_DEVELOPMENT = "feature_development"      # 功能开发策略
    RELEASE_PREPARATION = "release_preparation"      # 发布准备策略
    CODE_REVIEW = "code_review"                      # 代码审查策略
    BUG_FIXING = "bug_fixing"                        # Bug修复策略
    DEFAULT = "default"                              # 默认策略


@dataclass
class GitSolutionIntegrationConfig:
    """Git解决方案集成配置"""
    # 策略选择参数
    enable_git_aware_strategy: bool = True
    min_git_confidence_for_custom_strategy: float = 0.7
    default_strategy: GitSolutionStrategy = GitSolutionStrategy.DEFAULT
    
    # 评估权重
    git_compatibility_weight: float = 0.15
    implementation_risk_weight: float = 0.20
    rollback_complexity_weight: float = 0.10
    branch_strategy_fit_weight: float = 0.10
    
    # 生成限制
    max_solutions_for_complex_git_state: int = 5
    min_solutions_for_simple_git_state: int = 3
    require_git_safe_solution: bool = True
    
    # 多样性控制
    min_solution_diversity: float = 0.6  # 方案最小多样性阈值
    enforce_git_context_diversity: bool = True
    
    # 性能参数
    cache_git_status_seconds: int = 30   # Git状态缓存时间


@dataclass
class GitEnhancedSolutionCandidate(SolutionCandidate):
    """Git增强的解决方案候选"""
    git_compatibility_score: float = 0.0          # Git兼容性评分 (0-1)
    implementation_risk_score: float = 0.0        # 实施风险评分 (0-1, 越低越好)
    rollback_complexity_score: float = 0.0        # 回滚复杂度评分 (0-1, 越低越好)
    branch_strategy_fit_score: float = 0.0        # 分支策略匹配度评分 (0-1)
    
    # Git相关元数据
    recommended_git_workflow: str = ""            # 推荐的Git工作流程
    git_operations_needed: List[str] = field(default_factory=list)  # 需要的Git操作
    potential_git_conflicts: List[str] = field(default_factory=list) # 潜在的Git冲突
    
    @property
    def total_score_with_git(self) -> float:
        """包含Git维度的总分"""
        base_score = self.calculate_overall_score()
        
        # Git维度加权
        git_weighted_score = (
            self.git_compatibility_score * 0.15 +
            (1 - self.implementation_risk_score) * 0.20 +  # 风险越低越好
            (1 - self.rollback_complexity_score) * 0.10 +  # 复杂度越低越好
            self.branch_strategy_fit_score * 0.10
        )
        
        return base_score * 0.6 + git_weighted_score * 0.4


class GitSolutionStrategySelector:
    """Git状态到解决方案策略的选择器"""
    
    def __init__(self, config: Optional[GitSolutionIntegrationConfig] = None):
        self.config = config or GitSolutionIntegrationConfig()
        
    def select_strategy(self, git_status: GitStatus) -> GitSolutionStrategy:
        """基于Git状态选择生成策略"""
        
        # 检查是否启用Git感知策略
        if not self.config.enable_git_aware_strategy:
            return self.config.default_strategy
        
        # 分析Git状态特征
        features = self._analyze_git_features(git_status)
        
        # 根据特征选择策略
        strategy = self._select_strategy_by_features(features)
        
        return strategy
    
    def _analyze_git_features(self, git_status: GitStatus) -> Dict[str, Any]:
        """分析Git状态特征"""
        features = {
            "has_conflicts": git_status.has_conflicts,
            "untracked_files_count": len(git_status.untracked_files) if git_status.untracked_files else 0,
            "staged_files_count": len(git_status.staged_files) if git_status.staged_files else 0,
            "modified_files_count": len(git_status.modified_files) if git_status.modified_files else 0,
            "current_branch": git_status.current_branch,
            "is_detached": git_status.is_detached,
            "ahead_count": git_status.ahead_count,
            "behind_count": git_status.behind_count,
        }
        
        # 分析文件类型分布
        file_extensions = self._analyze_file_extensions(git_status)
        features["file_extensions"] = file_extensions
        
        return features
    
    def _analyze_file_extensions(self, git_status: GitStatus) -> Dict[str, int]:
        """分析文件扩展名分布"""
        extensions = {}
        all_files = []
        
        if git_status.modified_files:
            all_files.extend(git_status.modified_files)
        if git_status.untracked_files:
            all_files.extend(git_status.untracked_files)
        if git_status.staged_files:
            all_files.extend(git_status.staged_files)
        
        for file_path in all_files:
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
            else:
                extensions["no_extension"] = extensions.get("no_extension", 0) + 1
        
        return extensions
    
    def _select_strategy_by_features(self, features: Dict[str, Any]) -> GitSolutionStrategy:
        """基于特征选择策略"""
        
        # 检查冲突
        if features.get("has_conflicts", False):
            return GitSolutionStrategy.CONFLICT_RESOLUTION
        
        # 检查大量未跟踪文件
        if features.get("untracked_files_count", 0) > 10:
            return GitSolutionStrategy.UNTRACKED_MANAGEMENT
        
        # 检查核心文件修改（基于扩展名）
        file_extensions = features.get("file_extensions", {})
        core_extensions = {"py", "js", "ts", "java", "cpp", "go", "rs"}
        core_file_count = sum(file_extensions.get(ext, 0) for ext in core_extensions)
        
        if core_file_count > 5:
            return GitSolutionStrategy.CORE_FILE_MODIFICATION
        
        # 检查分支状态
        if features.get("ahead_count", 0) > 0 or features.get("behind_count", 0) > 0:
            return GitSolutionStrategy.FEATURE_DEVELOPMENT
        
        # 默认策略
        return self.config.default_strategy


class GitEnhancedSolutionEvaluator:
    """Git增强的解决方案评估器"""
    
    def __init__(self, git_context_provider: GitContextProvider):
        self.git_context = git_context_provider
        self.uncertainty_analyzer = GitContextUncertaintyAnalyzer(git_context_provider)
    
    def evaluate_with_git_context(self, solution: SolutionCandidate, 
                                  git_status: Optional[GitStatus] = None) -> GitEnhancedSolutionCandidate:
        """基于Git上下文增强评估"""
        
        if git_status is None:
            git_status = self.git_context.get_status()
        
        # 转换为增强候选
        enhanced = GitEnhancedSolutionCandidate(**solution.__dict__)
        
        # 计算Git相关评分
        enhanced.git_compatibility_score = self._calculate_git_compatibility(solution, git_status)
        enhanced.implementation_risk_score = self._calculate_implementation_risk(solution, git_status)
        enhanced.rollback_complexity_score = self._calculate_rollback_complexity(solution, git_status)
        enhanced.branch_strategy_fit_score = self._calculate_branch_strategy_fit(solution, git_status)
        
        # 生成Git工作流程建议
        enhanced.recommended_git_workflow = self._generate_git_workflow_recommendation(solution, git_status)
        enhanced.git_operations_needed = self._identify_git_operations(solution, git_status)
        enhanced.potential_git_conflicts = self._identify_potential_conflicts(solution, git_status)
        
        return enhanced
    
    def _calculate_git_compatibility(self, solution: SolutionCandidate, git_status: GitStatus) -> float:
        """计算Git兼容性评分"""
        score = 0.8  # 基础分数
        
        # 基于解决方案类型调整
        if solution.type == SolutionType.RULE_BASED:
            score += 0.1  # 规则驱动方案通常更兼容
        
        # 基于资源强度调整
        if solution.resource_intensity == ResourceIntensity.LIGHT:
            score += 0.05  # 轻量级方案更兼容
        
        # 检查是否有未提交的修改
        if git_status.has_uncommitted_changes and solution.resource_intensity == ResourceIntensity.HEAVY:
            score -= 0.2  # 重型方案在有未提交修改时兼容性降低
        
        return max(0.0, min(1.0, score))
    
    def _calculate_implementation_risk(self, solution: SolutionCandidate, git_status: GitStatus) -> float:
        """计算实施风险评分"""
        base_risk = {
            RiskLevel.CONSERVATIVE.value: 0.2,
            RiskLevel.MODERATE.value: 0.5,
            RiskLevel.AGGRESSIVE.value: 0.8
        }.get(solution.risk_level.value, 0.5)
        
        # 基于Git状态调整风险
        if git_status.has_conflicts:
            base_risk += 0.3
        
        if git_status.is_detached:
            base_risk += 0.2
        
        if git_status.behind_count > 5:
            base_risk += 0.1
        
        return max(0.0, min(1.0, base_risk))
    
    def _calculate_rollback_complexity(self, solution: SolutionCandidate, git_status: GitStatus) -> float:
        """计算回滚复杂度评分"""
        complexity = 0.5  # 基础复杂度
        
        # 基于方案类型调整
        if solution.type in [SolutionType.ML_BASED, SolutionType.OPTIMIZATION]:
            complexity += 0.3  # ML和优化方案更难回滚
        
        # 基于资源强度调整
        if solution.resource_intensity == ResourceIntensity.HEAVY:
            complexity += 0.2
        
        # 基于Git状态调整
        if git_status.has_uncommitted_changes:
            complexity -= 0.1  # 有未提交修改时回滚相对容易
        
        return max(0.0, min(1.0, complexity))
    
    def _calculate_branch_strategy_fit(self, solution: SolutionCandidate, git_status: GitStatus) -> float:
        """计算分支策略匹配度评分"""
        fit_score = 0.7
        
        # 检查是否推荐使用分支
        if solution.resource_intensity == ResourceIntensity.HEAVY:
            fit_score += 0.2  # 重型方案应使用分支
        
        if solution.risk_level == RiskLevel.AGGRESSIVE:
            fit_score += 0.1  # 激进方案应使用分支
        
        # 检查当前是否在主分支
        if git_status.current_branch == "main" or git_status.current_branch == "master":
            if solution.resource_intensity == ResourceIntensity.HEAVY:
                fit_score -= 0.3  # 在主分支进行重型开发不合适
        
        return max(0.0, min(1.0, fit_score))
    
    def _generate_git_workflow_recommendation(self, solution: SolutionCandidate, git_status: GitStatus) -> str:
        """生成Git工作流程建议"""
        recommendations = []
        
        # 基于方案类型
        if solution.resource_intensity == ResourceIntensity.HEAVY:
            recommendations.append("创建功能分支进行开发")
        
        if solution.risk_level == RiskLevel.AGGRESSIVE:
            recommendations.append("频繁提交小改动，便于回滚")
        
        # 基于Git状态
        if git_status.has_uncommitted_changes:
            recommendations.append("先提交当前修改再实施新方案")
        
        if git_status.has_conflicts:
            recommendations.append("先解决合并冲突")
        
        if not recommendations:
            recommendations.append("按照常规Git工作流程实施")
        
        return " → ".join(recommendations)
    
    def _identify_git_operations(self, solution: SolutionCandidate, git_status: GitStatus) -> List[str]:
        """识别需要的Git操作"""
        operations = []
        
        # 基础操作
        operations.append("git status - 查看当前状态")
        
        # 基于方案类型
        if solution.resource_intensity == ResourceIntensity.HEAVY:
            operations.append("git checkout -b feature/xxx - 创建功能分支")
        
        if solution.type == SolutionType.ML_BASED:
            operations.append("git add data/ models/ - 添加数据和模型文件")
        
        # 基于Git状态
        if git_status.has_uncommitted_changes:
            operations.append("git commit -m '描述修改内容'")
        
        if git_status.untracked_files and len(git_status.untracked_files) > 5:
            operations.append("git add . - 添加所有未跟踪文件")
        
        return operations
    
    def _identify_potential_conflicts(self, solution: SolutionCandidate, git_status: GitStatus) -> List[str]:
        """识别潜在的Git冲突"""
        conflicts = []
        
        # 基于方案类型
        if solution.type == SolutionType.OPTIMIZATION:
            conflicts.append("可能与现有优化方案冲突")
        
        if solution.resource_intensity == ResourceIntensity.HEAVY:
            conflicts.append("可能与其他重型功能开发冲突")
        
        # 基于Git状态
        if git_status.behind_count > 0:
            conflicts.append(f"落后远程分支{git_status.behind_count}个提交，合并时可能冲突")
        
        if git_status.ahead_count > 0:
            conflicts.append(f"领先远程分支{git_status.ahead_count}个提交，推送时可能被拒绝")
        
        return conflicts


class GitContextAwareSolutionGenerator:
    """Git上下文感知的解决方案生成器"""
    
    def __init__(self, 
                 git_context_provider: Optional[GitContextProvider] = None,
                 solution_generator: Optional[MultiSolutionGenerator] = None,
                 config: Optional[GitSolutionIntegrationConfig] = None):
        
        self.git_context = git_context_provider or GitContextProvider()
        self.solution_gen = solution_generator or MultiSolutionGenerator()
        self.config = config or GitSolutionIntegrationConfig()
        
        # 初始化子组件
        self.strategy_selector = GitSolutionStrategySelector(self.config)
        self.evaluator = GitEnhancedSolutionEvaluator(self.git_context)
    
    def generate_solutions_for_context(self, 
                                      problem: str, 
                                      context: Optional[Dict[str, Any]] = None,
                                      num_solutions: Optional[int] = None) -> List[GitEnhancedSolutionCandidate]:
        """基于Git上下文生成增强的解决方案"""
        
        # 获取当前Git状态
        git_status = self.git_context.get_detailed_status()
        print(f"[Git上下文] 当前分支: {git_status.current_branch}, 变更文件: {len(git_status.modified_files or []) + len(git_status.untracked_files or [])}")
        
        # 选择生成策略
        strategy = self.strategy_selector.select_strategy(git_status)
        print(f"[Git上下文] 选择策略: {strategy.value}")
        
        # 准备生成参数
        generation_params = self._prepare_generation_params(strategy, git_status, context)
        
        # 确定生成数量
        if num_solutions is None:
            num_solutions = self._determine_num_solutions(git_status)
        
        # 生成基础解决方案
        base_solutions = self.solution_gen.generate_solutions(
            problem=problem,
            context={**(context or {}), **generation_params},
            num_solutions=num_solutions
        )
        
        # 增强解决方案（添加Git维度评估）
        enhanced_solutions = []
        for solution in base_solutions:
            enhanced = self.evaluator.evaluate_with_git_context(solution, git_status)
            enhanced_solutions.append(enhanced)
        
        # 排序（基于总分）
        enhanced_solutions.sort(key=lambda s: s.total_score_with_git, reverse=True)
        
        return enhanced_solutions
    
    def _prepare_generation_params(self, 
                                   strategy: GitSolutionStrategy, 
                                   git_status: GitStatus,
                                   context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """准备生成参数"""
        params = {
            "git_strategy": strategy.value,
            "git_branch": git_status.current_branch,
            "git_has_conflicts": git_status.has_conflicts,
            "git_has_uncommitted_changes": git_status.has_uncommitted_changes,
        }
        
        # 基于策略调整参数
        if strategy == GitSolutionStrategy.CONFLICT_RESOLUTION:
            params["risk_level"] = RiskLevel.CONSERVATIVE.value
            params["resource_intensity"] = ResourceIntensity.LIGHT.value
            params["priority"] = "stability"
            
        elif strategy == GitSolutionStrategy.UNTRACKED_MANAGEMENT:
            params["solution_type"] = SolutionType.RULE_BASED.value
            params["risk_level"] = RiskLevel.CONSERVATIVE.value
            params["priority"] = "organization"
            
        elif strategy == GitSolutionStrategy.CORE_FILE_MODIFICATION:
            params["risk_level"] = RiskLevel.MODERATE.value
            params["resource_intensity"] = ResourceIntensity.MEDIUM.value
            params["priority"] = "quality"
            
        elif strategy == GitSolutionStrategy.FEATURE_DEVELOPMENT:
            params["solution_type"] = SolutionType.HYBRID.value
            params["risk_level"] = RiskLevel.MODERATE.value
            params["priority"] = "delivery"
            
        elif strategy == GitSolutionStrategy.RELEASE_PREPARATION:
            params["risk_level"] = RiskLevel.CONSERVATIVE.value
            params["solution_type"] = SolutionType.RULE_BASED.value
            params["priority"] = "reliability"
        
        # 合并用户提供的上下文
        if context:
            params.update(context)
        
        return params
    
    def _determine_num_solutions(self, git_status: GitStatus) -> int:
        """确定生成解决方案的数量"""
        base_count = self.config.min_solutions_for_simple_git_state
        
        # 基于Git复杂度调整
        complexity_score = 0
        
        if git_status.has_conflicts:
            complexity_score += 2
        
        if git_status.has_uncommitted_changes:
            complexity_score += 1
        
        if git_status.untracked_files and len(git_status.untracked_files) > 10:
            complexity_score += 1
        
        if git_status.is_detached:
            complexity_score += 1
        
        # 计算最终数量
        if complexity_score >= 3:
            return self.config.max_solutions_for_complex_git_state
        elif complexity_score >= 1:
            return max(base_count + 1, self.config.max_solutions_for_complex_git_state - 1)
        else:
            return base_count
    
    def generate_comparison_report(self, 
                                   solutions: List[GitEnhancedSolutionCandidate],
                                   include_git_analysis: bool = True) -> str:
        """生成解决方案比较报告"""
        report = f"# 解决方案比较报告\n\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"评估方案数: {len(solutions)}\n\n"
        
        # 添加Git上下文摘要
        if include_git_analysis:
            git_status = self.git_context.get_detailed_status()
            report += f"## Git上下文摘要\n"
            report += f"- **当前分支**: {git_status.current_branch}\n"
            report += f"- **是否有冲突**: {'是' if git_status.has_conflicts else '否'}\n"
            report += f"- **未提交修改**: {'是' if git_status.has_uncommitted_changes else '否'}\n"
            if git_status.modified_files:
                report += f"- **修改文件数**: {len(git_status.modified_files)}\n"
            if git_status.untracked_files:
                report += f"- **未跟踪文件数**: {len(git_status.untracked_files)}\n"
            report += "\n"
        
        # 方案比较表格
        report += f"## 方案排名\n\n"
        report += f"| 排名 | 方案ID | 总分 | Git兼容分 | 实施风险 | 类型 | 推荐工作流程 |\n"
        report += f"|------|--------|------|-----------|----------|------|--------------|\n"
        
        for i, solution in enumerate(solutions, 1):
            report += f"| {i} | {solution.id[:8]} | {solution.total_score_with_git:.2f} | "
            report += f"{solution.git_compatibility_score:.2f} | {solution.implementation_risk_score:.2f} | "
            report += f"{solution.type.value} | {solution.recommended_git_workflow[:20]}... |\n"
        
        report += "\n"
        
        # 最佳方案详情
        if solutions:
            best = solutions[0]
            report += f"## 推荐方案: {best.id}\n\n"
            report += f"**综合评分**: {best.total_score_with_git:.2f}\n"
            report += f"**方案类型**: {best.type.value}\n"
            report += f"**风险等级**: {best.risk_level.value}\n"
            report += f"**资源强度**: {best.resource_intensity.value}\n\n"
            
            report += f"### 方案描述\n{best.description}\n\n"
            
            report += f"### 评估详情\n"
            report += f"- **技术可行性**: {best.technical_feasibility:.2f}\n"
            report += f"- **商业价值**: {best.business_value:.2f}\n"
            report += f"- **用户体验**: {best.user_experience:.2f}\n"
            report += f"- **成功概率**: {best.success_probability:.2f}\n"
            report += f"- **Git兼容性**: {best.git_compatibility_score:.2f}\n"
            report += f"- **实施风险**: {best.implementation_risk_score:.2f}\n"
            report += f"- **回滚复杂度**: {best.rollback_complexity_score:.2f}\n\n"
            
            report += f"### 推荐Git工作流程\n{best.recommended_git_workflow}\n\n"
            
            if best.git_operations_needed:
                report += f"### 需要的Git操作\n"
                for op in best.git_operations_needed:
                    report += f"- {op}\n"
                report += "\n"
            
            if best.potential_git_conflicts:
                report += f"### 潜在Git冲突\n"
                for conflict in best.potential_git_conflicts:
                    report += f"- {conflict}\n"
                report += "\n"
        
        return report


def main():
    """主函数 - 演示集成功能"""
    print("Git上下文与多方案生成系统集成演示")
    print("=" * 60)
    
    # 创建生成器
    generator = GitContextAwareSolutionGenerator()
    
    # 定义测试问题
    test_problems = [
        "优化agent-core模块的代码结构",
        "实现一个高效的缓存系统",
        "重构TimesFM集成模块以提高性能",
        "添加完整的错误处理机制"
    ]
    
    for problem in test_problems:
        print(f"\n问题: {problem}")
        print("-" * 40)
        
        # 生成解决方案
        solutions = generator.generate_solutions_for_context(problem, num_solutions=3)
        
        # 生成报告
        report = generator.generate_comparison_report(solutions[:3])
        
        # 显示摘要
        print(f"生成 {len(solutions)} 个解决方案")
        if solutions:
            print(f"最佳方案: {solutions[0].id[:8]} (评分: {solutions[0].total_score_with_git:.2f})")
            print(f"Git工作流程: {solutions[0].recommended_git_workflow}")
        
        # 保存报告到文件
        report_file = f"git_solution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"详细报告已保存到: {report_file}")
    
    print("\n演示完成!")


if __name__ == "__main__":
    main()