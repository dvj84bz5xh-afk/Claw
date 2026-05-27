"""
Learning Integration System - 学习成果吸收系统

将GitHub学习成果转化为实际改进的实施系统。
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from github_learning_engine import (
    GitHubLearningEngine, Priority, Applicability, Complexity,
    LearnedInsight, ImprovementSuggestion
)


@dataclass
class ImplementationPlan:
    """实施计划"""
    suggestion_title: str
    source_project: str
    priority: Priority
    steps: list[str]
    estimated_hours: float
    dependencies: list[str]
    test_plan: str
    rollback_plan: str


class LearningIntegrationSystem:
    """学习成果吸收系统"""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.learning_engine = GitHubLearningEngine(workspace_path)
        
        # 实施跟踪
        self.implementation_dir = self.workspace_path / ".workbuddy" / "implementations"
        self.implementation_dir.mkdir(parents=True, exist_ok=True)
        
        # 实施日志
        self.implementation_log = self.workspace_path / ".workbuddy" / "implementation_log.json"
        self.log = self._load_log()
    
    def _load_log(self) -> dict:
        """加载实施日志"""
        if self.implementation_log.exists():
            with open(self.implementation_log, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "total_planned": 0,
            "total_implemented": 0,
            "total_rolled_back": 0,
            "implementations": []
        }
    
    def _save_log(self):
        """保存实施日志"""
        with open(self.implementation_log, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def create_implementation_plan(
        self,
        suggestion: ImprovementSuggestion,
        source_project: str
    ) -> ImplementationPlan:
        """为改进建议创建实施计划"""
        
        # 根据复杂度和优先级生成实施步骤
        steps = []
        estimated_hours = 0.0
        
        if suggestion.complexity == Complexity.LOW:
            steps = [
                f"1. 分析{suggestion.title}的实现需求",
                f"2. 编写{suggestion.title}的核心代码",
                f"3. 添加单元测试",
                f"4. 更新相关文档",
                f"5. 运行健康检查验证"
            ]
            estimated_hours = 2.0
        elif suggestion.complexity == Complexity.MEDIUM:
            steps = [
                f"1. 设计{suggestion.title}的架构方案",
                f"2. 创建模块接口定义",
                f"3. 实现核心功能模块",
                f"4. 编写单元测试和集成测试",
                f"5. 编写使用文档",
                f"6. 进行性能测试",
                f"7. 更新系统架构文档"
            ]
            estimated_hours = 8.0
        else:  # HIGH
            steps = [
                f"1. 深入调研{suggestion.title}相关技术",
                f"2. 设计详细技术方案",
                f"3. 创建原型验证",
                f"4. 设计完整架构",
                f"5. 分阶段实施开发",
                f"6. 编写完整测试套件",
                f"7. 性能优化和压力测试",
                f"8. 编写完整文档",
                f"9. 灰度发布和验证"
            ]
            estimated_hours = 24.0
        
        # 生成测试计划
        test_plan = self._generate_test_plan(suggestion)
        
        # 生成回滚计划
        rollback_plan = self._generate_rollback_plan(suggestion)
        
        return ImplementationPlan(
            suggestion_title=suggestion.title,
            source_project=source_project,
            priority=suggestion.priority,
            steps=steps,
            estimated_hours=estimated_hours,
            dependencies=self._identify_dependencies(suggestion),
            test_plan=test_plan,
            rollback_plan=rollback_plan
        )
    
    def _generate_test_plan(self, suggestion: ImprovementSuggestion) -> str:
        """生成测试计划"""
        base_plan = """
1. 单元测试 - 覆盖核心功能路径
2. 集成测试 - 验证与其他模块的协作
3. 健康检查 - 确保整体系统稳定
4. 性能测试 - 验证性能指标
        """
        
        if suggestion.applicability == Applicability.HIGH:
            base_plan += "5. 回归测试 - 确保现有功能不受影响\n"
        
        return base_plan.strip()
    
    def _generate_rollback_plan(self, suggestion: ImprovementSuggestion) -> str:
        """生成回滚计划"""
        return """
1. 保留修改前的代码备份
2. 使用git revert快速回滚
3. 检查依赖模块状态
4. 运行健康检查确认恢复
        """.strip()
    
    def _identify_dependencies(self, suggestion: ImprovementSuggestion) -> list[str]:
        """识别依赖项"""
        dependencies = []
        
        # 根据建议内容识别可能的依赖
        desc_lower = suggestion.description.lower()
        
        if "async" in desc_lower or "异步" in desc_lower:
            dependencies.append("asyncio")
        
        if "message" in desc_lower or "消息" in desc_lower:
            dependencies.append("消息队列")
        
        if "agent" in desc_lower or "agent" in suggestion.title.lower():
            dependencies.append("Agent基类")
        
        if "tool" in desc_lower or "工具" in desc_lower:
            dependencies.append("ToolRegistry")
        
        return dependencies
    
    def plan_implementations(self, priority: Optional[Priority] = None):
        """为待实施项创建实施计划"""
        pending = self.learning_engine.get_pending_implementations(priority)
        
        plans_created = 0
        for item in pending:
            # 创建实施计划文档
            plan = self._create_plan_document(item)
            
            # 保存计划
            plan_file = self.implementation_dir / f"{self._sanitize_filename(item['suggestion'])}.md"
            with open(plan_file, "w", encoding="utf-8") as f:
                f.write(plan)
            
            plans_created += 1
            
            # 更新日志
            self.log["total_planned"] += 1
            self.log["implementations"].append({
                "suggestion": item["suggestion"],
                "project": item["project"],
                "priority": item["priority"],
                "planned_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "planned",
                "plan_file": str(plan_file)
            })
        
        self._save_log()
        
        print(f"[学习吸收] 已创建 {plans_created} 个实施计划")
        return plans_created
    
    def _create_plan_document(self, item: dict) -> str:
        """创建实施计划文档"""
        return f"""# 实施计划: {item['suggestion']}

## 基本信息

- **来源项目**: {item['project']}
- **优先级**: {item['priority']}
- **计划日期**: {datetime.now().strftime("%Y-%m-%d")}
- **状态**: 计划中

## 实施步骤

1. 分析需求和技术方案
2. 设计接口和架构
3. 实现核心功能
4. 编写测试
5. 更新文档
6. 验证和优化

## 测试计划

- 单元测试覆盖主要路径
- 集成测试验证协作
- 健康检查确保稳定

## 回滚计划

1. 保留代码备份
2. 使用git revert回滚
3. 验证系统状态

## 进度跟踪

- [ ] 步骤1完成
- [ ] 步骤2完成
- [ ] 步骤3完成
- [ ] 步骤4完成
- [ ] 步骤5完成
- [ ] 步骤6完成

## 备注

来自GitHub学习项目的改进建议，需要根据实际架构进行调整。
"""
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        import re
        return re.sub(r'[^\w\-_.]', '_', name)[:50]
    
    def start_implementation(self, suggestion_title: str):
        """开始实施"""
        for impl in self.log["implementations"]:
            if impl["suggestion"] == suggestion_title and impl["status"] == "planned":
                impl["status"] = "in_progress"
                impl["started_date"] = datetime.now().strftime("%Y-%m-%d")
                break
        
        self._save_log()
        print(f"[学习吸收] 开始实施: {suggestion_title}")
    
    def complete_implementation(self, suggestion_title: str, success: bool = True):
        """完成实施"""
        for impl in self.log["implementations"]:
            if impl["suggestion"] == suggestion_title and impl["status"] == "in_progress":
                if success:
                    impl["status"] = "completed"
                    self.log["total_implemented"] += 1
                    self.learning_engine.mark_implemented(suggestion_title)
                    print(f"[学习吸收] 完成实施: {suggestion_title}")
                else:
                    impl["status"] = "failed"
                    print(f"[学习吸收] 实施失败: {suggestion_title}")
                
                impl["completed_date"] = datetime.now().strftime("%Y-%m-%d")
                break
        
        self._save_log()
    
    def rollback_implementation(self, suggestion_title: str):
        """回滚实施"""
        for impl in self.log["implementations"]:
            if impl["suggestion"] == suggestion_title:
                impl["status"] = "rolled_back"
                impl["rollback_date"] = datetime.now().strftime("%Y-%m-%d")
                self.log["total_rolled_back"] += 1
                break
        
        self._save_log()
        print(f"[学习吸收] 回滚实施: {suggestion_title}")
    
    def get_implementation_stats(self) -> dict:
        """获取实施统计"""
        return {
            "total_planned": self.log["total_planned"],
            "total_implemented": self.log["total_implemented"],
            "total_rolled_back": self.log["total_rolled_back"],
            "success_rate": (
                self.log["total_implemented"] / self.log["total_planned"] * 100
                if self.log["total_planned"] > 0 else 0
            ),
            "in_progress": len([
                i for i in self.log["implementations"]
                if i["status"] == "in_progress"
            ]),
            "pending": len([
                i for i in self.log["implementations"]
                if i["status"] == "planned"
            ])
        }
    
    def generate_integration_report(self) -> str:
        """生成学习吸收报告"""
        stats = self.get_implementation_stats()
        
        report = f"""# 学习成果吸收报告

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 实施统计

| 指标 | 数值 |
|------|------|
| 计划实施 | {stats['total_planned']} |
| 已完成 | {stats['total_implemented']} |
| 已回滚 | {stats['total_rolled_back']} |
| 进行中 | {stats['in_progress']} |
| 待开始 | {stats['pending']} |
| 成功率 | {stats['success_rate']:.1f}% |

## 近期实施项

### 进行中
"""
        
        for impl in self.log["implementations"][-10:]:
            if impl["status"] == "in_progress":
                report += f"- {impl['suggestion']} (来自: {impl['project']})\n"
        
        report += "\n### 最近完成\n"
        completed = [
            i for i in self.log["implementations"]
            if i["status"] == "completed"
        ][-5:]
        for impl in completed:
            report += f"- {impl['suggestion']}\n"
        
        report += """
## 优化建议

1. 优先实施P0级改进
2. 每周审查实施进度
3. 及时记录实施经验
4. 定期更新学习方向

"""
        
        return report


def main():
    """测试学习吸收系统"""
    integration = LearningIntegrationSystem()
    
    # 创建实施计划
    print("=" * 60)
    print("创建实施计划")
    print("=" * 60)
    plans = integration.plan_implementations(Priority.P0)
    
    # 显示统计
    print("\n" + "=" * 60)
    print("实施统计")
    print("=" * 60)
    stats = integration.get_implementation_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("学习吸收报告")
    print("=" * 60)
    print(integration.generate_integration_report())


if __name__ == "__main__":
    main()
