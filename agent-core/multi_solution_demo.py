#!/usr/bin/env python3
"""
多方案并行生成系统演示
测试TimesFM-inspired的多方案生成能力
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timesfm_integration import create_timesfm_agent
from multi_solution_generator import SolutionType, RiskLevel, ResourceIntensity, RankingCriteria


def main():
    print("="*70)
    print("多方案并行生成系统演示")
    print("="*70)
    
    # 创建Agent
    agent = create_timesfm_agent(preset="high_accuracy")
    
    # 测试问题1: 技术架构选择
    problem1 = """
    我们需要为一家中型电商公司开发一个商品推荐系统。
    要求:
    1. 基于用户历史行为和实时点击数据
    2. 支持个性化推荐和相似商品推荐
    3. 处理每天100万次推荐请求
    4. 与现有Java后台系统集成
    5. 3个月内上线
    
    请提供多种技术方案并进行比较。
    """
    
    print(f"\n[测试问题1] 电商推荐系统")
    print("-"*70)
    
    # 生成并排序解决方案
    report1 = agent.generate_multiple_solutions(
        problem=problem1,
        context={"domain": "ecommerce", "budget": "medium"},
        num_solutions=4
    )
    
    print(f"\n[生成] 生成了 {report1['statistics']['total_solutions']} 个解决方案")
    print(f"[分布] 方案类型分布: {report1['statistics']['solution_types']}")
    print(f"[分布] 风险分布: {report1['statistics']['risk_distribution']}")
    print(f"[分布] 资源分布: {report1['statistics']['resource_distribution']}")
    
    print(f"\n[推荐] 推荐方案:")
    for rec in report1['recommendations']:
        print(f"   - {rec}")
    
    # 测试问题2: 数据处理流水线
    problem2 = """
    我们需要构建一个实时数据处理流水线，用于分析IoT设备数据。
    要求:
    1. 处理每秒10万条传感器数据
    2. 实时异常检测和预警
    3. 数据存储至少30天
    4. 支持多数据源集成
    5. 开发团队有Python和Go经验
    """
    
    print(f"\n\n[测试问题2] IoT数据处理流水线")
    print("-"*70)
    
    # 自定义排序标准 (技术可行性优先)
    criteria = RankingCriteria(
        prioritize_technical_feasibility=0.6,
        prioritize_business_value=0.2,
        prioritize_user_experience=0.1,
        prioritize_success_probability=0.1,
        prioritize_cost_efficiency=True,
        max_risk_tolerance=RiskLevel.MODERATE,
        max_resource_intensity=ResourceIntensity.MEDIUM
    )
    
    report2 = agent.generate_multiple_solutions(
        problem=problem2,
        context={"domain": "iot", "team_experience": ["python", "go"]},
        num_solutions=5,
        ranking_criteria=criteria
    )
    
    print(f"\n[生成] 生成了 {report2['statistics']['total_solutions']} 个解决方案")
    print(f"[分布] 方案类型分布: {report2['statistics']['solution_types']}")
    
    print(f"\n[推荐] 推荐方案 (技术可行性优先):")
    for rec in report2['recommendations']:
        print(f"   - {rec}")
    
    # 显示详细方案信息
    print(f"\n[详细] 详细方案信息 (前2名):")
    for i, solution in enumerate(report2['solutions'][:2], 1):
        print(f"\n{i}. {solution['title']}")
        print(f"   类型: {solution['type']}")
        print(f"   风险等级: {solution['risk_level']}")
        print(f"   资源要求: {solution['resource_intensity']}")
        print(f"   预估时间: {solution['estimated_time']}小时")
        print(f"   预估成本: {solution['estimated_cost']}/10")
        print(f"   技术可行性: {solution['technical_feasibility']:.1%}")
        print(f"   商业价值: {solution['business_value']:.1%}")
        print(f"   用户体验: {solution['user_experience']:.1%}")
        print(f"   成功概率: {solution['success_probability']:.1%}")
        print(f"   实现步骤:")
        for step in solution['implementation_steps'][:3]:
            print(f"     - {step}")
        if len(solution['implementation_steps']) > 3:
            print(f"     - ...等 {len(solution['implementation_steps'])} 个步骤")
    
    # 测试问题3: 快速原型验证
    problem3 = """
    我们需要快速验证一个新功能: 基于用户位置的个性化推送。
    要求:
    1. 2周内出可演示原型
    2. 最小可行性产品(MVP)
    3. 使用现有技术栈(Python/Django)
    4. 优先考虑开发速度而非完美架构
    """
    
    print(f"\n\n[测试问题3] 快速原型验证")
    print("-"*70)
    
    # 使用快速响应配置
    fast_agent = create_timesfm_agent(preset="fast_response")
    
    report3 = fast_agent.generate_multiple_solutions(
        problem=problem3,
        context={"domain": "mobile_app", "urgency": "high"},
        num_solutions=3
    )
    
    print(f"\n[推荐] 推荐方案 (快速原型):")
    for rec in report3['recommendations']:
        print(f"   - {rec}")
    
    # 系统能力展示
    print(f"\n" + "="*70)
    print("系统能力展示")
    print("="*70)
    
    capabilities = agent.get_capabilities()
    print(f"[配置] 配置版本: {capabilities.config.version}")
    print(f"[任务] 任务Patch大小: {capabilities.config.task_patch.patch_size}")
    print(f"[多视角] 多视角分析: {'启用' if capabilities.config.multi_view.enable_multi_view else '禁用'}")
    print(f"[多方案] 多方案生成: {'启用' if capabilities.config.multi_solution.enable_multi_solution else '禁用'}")
    print(f"  默认方案数: {capabilities.config.multi_solution.default_num_solutions}")
    print(f"  多样性阈值: {capabilities.config.multi_solution.diversity_threshold}")
    
    stats = agent.get_stats()
    print(f"\n[统计] 系统统计:")
    print(f"  处理任务数: {stats.get('tasks_processed', 0)}")
    print(f"  生成方案数: {stats.get('solutions_generated', 0)}")
    print(f"  知识检索次数: {stats.get('knowledge_retrievals', 0)}")
    
    print(f"\n" + "="*70)
    print("演示完成")
    print("="*70)


if __name__ == "__main__":
    main()