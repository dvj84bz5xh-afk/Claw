#!/usr/bin/env python3
"""
Git上下文与多方案生成系统集成演示
展示基于Git状态的智能方案生成和推荐
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from git_multi_solution_integration import (
    GitContextAwareSolutionGenerator,
    GitSolutionStrategy,
    GitEnhancedSolutionCandidate
)

from git_context_integration import GitContextProvider
from multi_solution_generator import MultiSolutionGenerator


class GitMultiSolutionDemo:
    """Git多方案集成演示类"""
    
    def __init__(self):
        print("=" * 70)
        print("Git上下文与多方案生成系统集成演示")
        print("=" * 70)
        
        # 初始化组件
        self.git_provider = GitContextProvider()
        self.solution_gen = MultiSolutionGenerator()
        self.integrated_gen = GitContextAwareSolutionGenerator()
        
    def demo_current_git_status(self):
        """演示当前Git状态分析"""
        print("\n1. 当前Git状态分析")
        print("-" * 40)
        
        git_status = self.git_provider.get_detailed_status()
        
        print(f"仓库: {Path.cwd().name}")
        print(f"分支: {git_status.current_branch}")
        print(f"是否干净: {'是' if git_status.is_clean else '否'}")
        
        if git_status.modified_files:
            print(f"修改文件: {len(git_status.modified_files)}个")
            for i, file in enumerate(git_status.modified_files[:3], 1):
                print(f"  {i}. {file}")
            if len(git_status.modified_files) > 3:
                print(f"  ... 还有{len(git_status.modified_files) - 3}个文件")
        
        if git_status.untracked_files:
            print(f"未跟踪文件: {len(git_status.untracked_files)}个")
        
        if git_status.has_conflicts:
            print("[警告] 存在合并冲突")
        
        print(f"领先远程分支: {git_status.ahead_count}个提交")
        print(f"落后远程分支: {git_status.behind_count}个提交")
    
    def demo_strategy_selection(self):
        """演示策略选择"""
        print("\n2. Git状态到解决方案策略映射")
        print("-" * 40)
        
        git_status = self.git_provider.get_detailed_status()
        
        # 模拟不同场景的策略选择
        test_scenarios = [
            {
                "name": "冲突解决场景",
                "status": self._create_mock_status(has_conflicts=True, modified_count=3)
            },
            {
                "name": "大量未跟踪文件",
                "status": self._create_mock_status(untracked_count=15, modified_count=1)
            },
            {
                "name": "核心文件修改",
                "status": self._create_mock_status(modified_files=["agent-core/config_system.py", 
                                                                  "agent-core/timesfm_integration.py",
                                                                  "agent-core/git_context_integration.py"])
            },
            {
                "name": "功能开发中",
                "status": self._create_mock_status(current_branch="feature/new-module", ahead_count=5)
            },
            {
                "name": "发布准备",
                "status": self._create_mock_status(current_branch="release/v1.0", is_clean=True)
            }
        ]
        
        from git_multi_solution_integration import GitSolutionStrategySelector
        selector = GitSolutionStrategySelector()
        
        for scenario in test_scenarios:
            strategy = selector.select_strategy(scenario["status"])
            print(f"{scenario['name']}: → {strategy.value}")
    
    def _create_mock_status(self, **kwargs):
        """创建模拟Git状态"""
        from git_context_integration import GitStatus
        
        # 获取真实状态作为基础
        real_status = self.git_provider.get_detailed_status()
        
        # 创建新状态对象，覆盖指定属性
        mock_status = GitStatus(
            is_git_repo=kwargs.get('is_git_repo', real_status.is_git_repo),
            git_root=kwargs.get('git_root', real_status.git_root),
            current_branch=kwargs.get('current_branch', real_status.current_branch),
            is_clean=kwargs.get('is_clean', real_status.is_clean),
            has_conflicts=kwargs.get('has_conflicts', real_status.has_conflicts),
            modified_files=kwargs.get('modified_files', real_status.modified_files),
            staged_files=kwargs.get('staged_files', real_status.staged_files),
            untracked_files=kwargs.get('untracked_files', real_status.untracked_files),
            ahead_count=kwargs.get('ahead_count', real_status.ahead_count),
            behind_count=kwargs.get('behind_count', real_status.behind_count),
            is_detached=kwargs.get('is_detached', real_status.is_detached),
            has_uncommitted_changes=kwargs.get('has_uncommitted_changes', real_status.has_uncommitted_changes)
        )
        
        # 处理数量参数
        if 'modified_count' in kwargs:
            mock_status.modified_files = [f"test_file_{i}.py" for i in range(kwargs['modified_count'])]
        
        if 'untracked_count' in kwargs:
            mock_status.untracked_files = [f"untracked_{i}.tmp" for i in range(kwargs['untracked_count'])]
        
        return mock_status
    
    def demo_solution_generation(self):
        """演示解决方案生成"""
        print("\n3. 基于Git上下文的解决方案生成")
        print("-" * 40)
        
        # 定义测试问题
        test_problems = [
            {
                "title": "优化agent-core模块的代码结构",
                "description": "重构agent-core模块，提高代码可维护性和性能",
                "context": {"priority": "maintainability"}
            },
            {
                "title": "实现高效的缓存系统",
                "description": "为TimesFM集成添加缓存层，提高响应速度",
                "context": {"priority": "performance"}
            },
            {
                "title": "处理大量未跟踪文件",
                "description": "清理项目中的临时文件和未跟踪文件",
                "context": {"priority": "cleanup"}
            }
        ]
        
        for i, problem in enumerate(test_problems, 1):
            print(f"\n问题 {i}: {problem['title']}")
            print(f"描述: {problem['description']}")
            
            # 生成解决方案
            solutions = self.integrated_gen.generate_solutions_for_context(
                problem=problem['description'],
                context=problem['context'],
                num_solutions=3
            )
            
            print(f"生成 {len(solutions)} 个解决方案:")
            
            for j, solution in enumerate(solutions[:2], 1):  # 只显示前2个
                print(f"  {j}. [{solution.id[:8]}] {solution.type.value}")
                print(f"     总分: {solution.total_score_with_git:.2f}")
                print(f"     Git兼容性: {solution.git_compatibility_score:.2f}")
                print(f"     实施风险: {solution.implementation_risk_score:.2f}")
                print(f"     推荐工作流: {solution.recommended_git_workflow[:50]}...")
            
            if len(solutions) > 2:
                print(f"  ... 还有{len(solutions) - 2}个方案")
    
    def demo_comparison_report(self):
        """演示比较报告生成"""
        print("\n4. 解决方案比较报告生成")
        print("-" * 40)
        
        # 生成复杂问题的解决方案
        problem = "重构TimesFM集成架构以支持多模型并行推理"
        
        print(f"问题: {problem}")
        print("生成解决方案中...")
        
        solutions = self.integrated_gen.generate_solutions_for_context(
            problem=problem,
            context={"complexity": "high", "time_constraint": "moderate"},
            num_solutions=4
        )
        
        # 生成比较报告
        report = self.integrated_gen.generate_comparison_report(solutions)
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"git_solution_comparison_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"[完成] 已生成比较报告: {report_file}")
        
        # 显示报告摘要
        print("\n报告摘要:")
        print("-" * 30)
        
        if solutions:
            best = solutions[0]
            print(f"最佳方案: {best.id[:8]}")
            print(f"综合评分: {best.total_score_with_git:.2f}")
            print(f"方案类型: {best.type.value}")
            print(f"风险等级: {best.risk_level.value}")
            print(f"Git工作流: {best.recommended_git_workflow}")
            
            # 显示其他方案对比
            if len(solutions) > 1:
                print(f"\n其他候选方案:")
                for i, solution in enumerate(solutions[1:4], 2):
                    print(f"  {i}. {solution.id[:8]} - 评分: {solution.total_score_with_git:.2f} "
                          f"({solution.type.value}, {solution.risk_level.value})")
    
    def demo_real_world_scenarios(self):
        """演示真实世界场景"""
        print("\n5. 真实世界场景演示")
        print("-" * 40)
        
        scenarios = [
            {
                "name": "场景1: 合并冲突解决",
                "setup": "模拟存在合并冲突的Git状态",
                "problem": "解决agent-core模块中的合并冲突",
                "expected": "生成保守型冲突解决方案"
            },
            {
                "name": "场景2: 大规模重构",
                "setup": "模拟修改了10+个核心文件的Git状态",
                "problem": "重构整个配置系统",
                "expected": "生成增量式重构方案，注重风险控制"
            },
            {
                "name": "场景3: 紧急Bug修复",
                "setup": "模拟生产环境Bug，需要快速修复",
                "problem": "修复配置加载失败的问题",
                "expected": "生成快速修复方案，注重速度和安全性"
            },
            {
                "name": "场景4: 新功能开发",
                "setup": "在新的功能分支上开发",
                "problem": "实现多方案并行生成的可视化界面",
                "expected": "生成创新性方案，支持迭代开发"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}")
            print(f"设置: {scenario['setup']}")
            print(f"问题: {scenario['problem']}")
            print(f"预期: {scenario['expected']}")
            
            # 在实际演示中，这里会调用生成器
            # 为了演示简洁，我们只显示预期结果
            print("[完成] 场景准备完成")
    
    def run_full_demo(self):
        """运行完整演示"""
        try:
            self.demo_current_git_status()
            self.demo_strategy_selection()
            self.demo_solution_generation()
            self.demo_comparison_report()
            self.demo_real_world_scenarios()
            
            print("\n" + "=" * 70)
            print("演示完成!")
            print("=" * 70)
            
            print("\n[报告] 演示总结:")
            print("1. Git上下文增强系统 [OK] - 正常运行")
            print("2. 多方案生成系统 [OK] - 正常运行")
            print("3. 集成模块 [OK] - 成功生成上下文感知的解决方案")
            print("4. 策略选择 [OK] - 基于Git状态智能选择生成策略")
            print("5. 报告生成 [OK] - 生成完整的解决方案比较报告")
            
            print("\n[建议] 下一步建议:")
            print("1. 在实际项目中测试集成系统")
            print("2. 根据团队工作流程定制生成策略")
            print("3. 集成到CI/CD流程中")
            print("4. 收集用户反馈持续优化")
            
        except Exception as e:
            print(f"\n[错误] 演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    demo = GitMultiSolutionDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()