"""
GitHub Learning Engine - GitHub高星项目学习引擎

自动学习GitHub热门项目，分析优点，生成改进建议。
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


class Priority(Enum):
    """改进优先级"""
    P0 = "P0"  # 立即实施
    P1 = "P1"  # 近期实施
    P2 = "P2"  # 远期考虑


class Applicability(Enum):
    """适用性评估"""
    HIGH = "high"      # 高度适用
    MEDIUM = "medium"  # 中度适用
    LOW = "low"        # 低度适用


class Complexity(Enum):
    """实施复杂度"""
    HIGH = "high"      # 高复杂度
    MEDIUM = "medium"  # 中度复杂度
    LOW = "low"        # 低复杂度


@dataclass
class LearnedInsight:
    """学习发现"""
    category: str  # 类别: architecture, mechanism, code_quality, innovation
    description: str  # 描述
    source_file: Optional[str] = None  # 来源文件
    code_snippet: Optional[str] = None  # 代码片段


@dataclass
class ImprovementSuggestion:
    """改进建议"""
    title: str  # 标题
    description: str  # 描述
    applicability: Applicability  # 适用性
    complexity: Complexity  # 复杂度
    priority: Priority  # 优先级
    expected_benefit: str  # 预期收益
    implementation_approach: str  # 实施方法
    reference_code: Optional[str] = None  # 参考代码


@dataclass
class LearningReport:
    """学习报告"""
    date: str
    project_name: str
    project_url: str
    stars: int
    language: str
    insights: list[LearnedInsight] = field(default_factory=list)
    suggestions: list[ImprovementSuggestion] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        md = f"""## 学习日期: {self.date}

### 学习项目: {self.project_name}
- URL: {self.project_url}
- Stars: {self.stars}
- 语言: {self.language}

### 核心发现
"""
        for i, insight in enumerate(self.insights, 1):
            md += f"{i}. **{insight.category}**: {insight.description}\n"
            if insight.source_file:
                md += f"   - 来源: `{insight.source_file}`\n"
            if insight.code_snippet:
                md += f"   - 代码片段:\n```python\n{insight.code_snippet}\n```\n"
        
        md += "\n### 可吸收优点\n"
        md += "| 优点 | 适用性 | 复杂度 | 优先级 | 预期收益 |\n"
        md += "|------|--------|--------|--------|----------|\n"
        for suggestion in self.suggestions:
            md += f"| {suggestion.title} | {suggestion.applicability.value} | {suggestion.complexity.value} | {suggestion.priority.value} | {suggestion.expected_benefit} |\n"
        
        md += "\n### 详细改进建议\n"
        for i, suggestion in enumerate(self.suggestions, 1):
            md += f"\n#### {i}. {suggestion.title} ({suggestion.priority.value})\n"
            md += f"- **描述**: {suggestion.description}\n"
            md += f"- **适用性**: {suggestion.applicability.value}\n"
            md += f"- **复杂度**: {suggestion.complexity.value}\n"
            md += f"- **预期收益**: {suggestion.expected_benefit}\n"
            md += f"- **实施方法**: {suggestion.implementation_approach}\n"
            if suggestion.reference_code:
                md += f"- **参考代码**:\n```python\n{suggestion.reference_code}\n```\n"
        
        md += "\n### 行动计划\n"
        for i, action in enumerate(self.action_items, 1):
            md += f"- [ ] {action}\n"
        
        return md


class GitHubLearningEngine:
    """GitHub学习引擎"""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.learning_dir = self.workspace_path / ".workbuddy" / "daily_learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # 学习进度跟踪
        self.progress_file = self.workspace_path / ".workbuddy" / "learning_progress.json"
        self.progress = self._load_progress()
    
    def _load_progress(self) -> dict:
        """加载学习进度"""
        if self.progress_file.exists():
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "total_projects_learned": 0,
            "total_suggestions": 0,
            "implemented_suggestions": 0,
            "daily_streak": 0,
            "last_learning_date": None,
            "learned_projects": [],
            "pending_implementations": []
        }
    
    def _save_progress(self):
        """保存学习进度"""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def analyze_project(
        self,
        project_name: str,
        project_url: str,
        stars: int,
        language: str,
        insights: list[LearnedInsight],
        suggestions: list[ImprovementSuggestion]
    ) -> LearningReport:
        """分析项目并生成学习报告"""
        
        # 生成行动计划
        action_items = []
        for suggestion in suggestions:
            if suggestion.priority == Priority.P0:
                action_items.append(
                    f"[P0] 实施: {suggestion.title} - {suggestion.implementation_approach[:50]}..."
                )
            elif suggestion.priority == Priority.P1:
                action_items.append(
                    f"[P1] 规划: {suggestion.title}"
                )
        
        report = LearningReport(
            date=datetime.now().strftime("%Y-%m-%d"),
            project_name=project_name,
            project_url=project_url,
            stars=stars,
            language=language,
            insights=insights,
            suggestions=suggestions,
            action_items=action_items
        )
        
        # 保存报告
        self._save_report(report)
        
        # 更新进度
        self._update_progress(project_name, suggestions)
        
        return report
    
    def _save_report(self, report: LearningReport):
        """保存学习报告"""
        filename = f"{report.date}_{self._sanitize_filename(report.project_name)}.md"
        filepath = self.learning_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())
        
        print(f"[学习引擎] 学习报告已保存: {filepath}")
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        return re.sub(r'[^\w\-_.]', '_', name)[:50]
    
    def _update_progress(self, project_name: str, suggestions: list[ImprovementSuggestion]):
        """更新学习进度"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 更新连续学习天数
        if self.progress["last_learning_date"] == today:
            pass  # 今天已经学习过
        elif self.progress["last_learning_date"] == (
            datetime.now() - __import__('datetime').timedelta(days=1)
        ).strftime("%Y-%m-%d"):
            self.progress["daily_streak"] += 1
        else:
            self.progress["daily_streak"] = 1
        
        self.progress["last_learning_date"] = today
        self.progress["total_projects_learned"] += 1
        self.progress["total_suggestions"] += len(suggestions)
        
        if project_name not in self.progress["learned_projects"]:
            self.progress["learned_projects"].append(project_name)
        
        # 添加待实施项
        for suggestion in suggestions:
            if suggestion.priority in [Priority.P0, Priority.P1]:
                self.progress["pending_implementations"].append({
                    "project": project_name,
                    "suggestion": suggestion.title,
                    "priority": suggestion.priority.value,
                    "date_added": today,
                    "status": "pending"
                })
        
        self._save_progress()
    
    def get_learning_stats(self) -> dict:
        """获取学习统计"""
        return {
            "total_projects": self.progress["total_projects_learned"],
            "total_suggestions": self.progress["total_suggestions"],
            "implemented": self.progress["implemented_suggestions"],
            "daily_streak": self.progress["daily_streak"],
            "pending_count": len(self.progress["pending_implementations"]),
            "p0_pending": len([
                p for p in self.progress["pending_implementations"]
                if p["priority"] == "P0" and p["status"] == "pending"
            ])
        }
    
    def get_pending_implementations(self, priority: Optional[Priority] = None) -> list:
        """获取待实施项"""
        pending = [
            p for p in self.progress["pending_implementations"]
            if p["status"] == "pending"
        ]
        
        if priority:
            pending = [p for p in pending if p["priority"] == priority.value]
        
        return pending
    
    def mark_implemented(self, suggestion_title: str):
        """标记已实施"""
        for item in self.progress["pending_implementations"]:
            if item["suggestion"] == suggestion_title:
                item["status"] = "implemented"
                item["date_implemented"] = datetime.now().strftime("%Y-%m-%d")
                self.progress["implemented_suggestions"] += 1
                break
        
        self._save_progress()
    
    def generate_weekly_summary(self) -> str:
        """生成周学习总结"""
        stats = self.get_learning_stats()
        
        # 获取本周学习报告
        week_reports = []
        today = datetime.now()
        for i in range(7):
            date_str = (today - __import__('datetime').timedelta(days=i)).strftime("%Y-%m-%d")
            for file in self.learning_dir.glob(f"{date_str}_*.md"):
                week_reports.append(file)
        
        summary = f"""# 周学习总结 ({(today - __import__('datetime').timedelta(days=6)).strftime("%Y-%m-%d")} ~ {today.strftime("%Y-%m-%d")})

## 学习统计

| 指标 | 数值 |
|------|------|
| 累计学习项目 | {stats['total_projects']} |
| 累计改进建议 | {stats['total_suggestions']} |
| 已实施改进 | {stats['implemented']} |
| 连续学习天数 | {stats['daily_streak']} |
| 待实施P0项 | {stats['p0_pending']} |
| 本周学习报告 | {len(week_reports)} 份 |

## 本周学习项目

"""
        for report_file in week_reports:
            # 从文件名提取项目名称
            project_name = report_file.stem.split('_', 1)[1].replace('_', '/')
            summary += f"- {project_name}\n"
        
        summary += f"\n## 待实施P0项\n\n"
        p0_items = self.get_pending_implementations(Priority.P0)
        for item in p0_items[:5]:  # 只显示前5个
            summary += f"- [ ] {item['suggestion']} (来自: {item['project']})\n"
        
        summary += "\n## 下周计划\n\n"
        summary += "- [ ] 继续每日GitHub学习\n"
        summary += f"- [ ] 实施至少{min(3, len(p0_items))}个P0改进\n"
        summary += "- [ ] 复习本周学习内容\n"
        
        return summary


# 预设的学习模板
class LearningTemplates:
    """学习模板"""
    
    @staticmethod
    def create_autogen_insights() -> list[LearnedInsight]:
        """AutoGen项目学习模板"""
        return [
            LearnedInsight(
                category="architecture",
                description="事件驱动的异步架构，支持分布式Agent部署",
                source_file="autogen-core/src/autogen_core/base.py"
            ),
            LearnedInsight(
                category="mechanism",
                description="Agent间通过消息总线进行异步通信，支持多种消息类型",
                code_snippet="""
class AgentRuntime:
    async def send_message(self, message: Message, recipient: AgentId):
        await self._message_queue.put((message, recipient))
                """
            ),
            LearnedInsight(
                category="innovation",
                description="GroupChat机制实现多Agent协作，支持多种选择策略"
            )
        ]
    
    @staticmethod
    def create_autogen_suggestions() -> list[ImprovementSuggestion]:
        """AutoGen改进建议模板"""
        return [
            ImprovementSuggestion(
                title="实现消息总线机制",
                description="引入异步消息队列，支持Agent间的松耦合通信",
                applicability=Applicability.HIGH,
                complexity=Complexity.MEDIUM,
                priority=Priority.P0,
                expected_benefit="提升多Agent协作效率，支持异步执行",
                implementation_approach="使用asyncio.Queue实现消息总线，添加消息路由机制"
            ),
            ImprovementSuggestion(
                title="添加GroupChat支持",
                description="实现多Agent组聊天机制，支持不同的发言选择策略",
                applicability=Applicability.MEDIUM,
                complexity=Complexity.HIGH,
                priority=Priority.P1,
                expected_benefit="支持复杂的多Agent协作场景",
                implementation_approach="设计GroupChat类，实现轮询/随机/智能选择策略"
            )
        ]
    
    @staticmethod
    def create_mcp_insights() -> list[LearnedInsight]:
        """MCP项目学习模板"""
        return [
            LearnedInsight(
                category="architecture",
                description="标准化的工具协议，分离工具提供者和使用者"
            ),
            LearnedInsight(
                category="mechanism",
                description="基于JSON-RPC的通信协议，支持工具发现、调用、资源访问",
                code_snippet="""
class Server:
    @app.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        return await tool_registry.execute(name, arguments)
                """
            ),
            LearnedInsight(
                category="innovation",
                description="声明式工具定义，自动生成功能描述"
            )
        ]
    
    @staticmethod
    def create_mcp_suggestions() -> list[ImprovementSuggestion]:
        """MCP改进建议模板"""
        return [
            ImprovementSuggestion(
                title="实现MCP协议兼容",
                description="使工具系统兼容MCP协议，可与外部MCP Server集成",
                applicability=Applicability.HIGH,
                complexity=Complexity.MEDIUM,
                priority=Priority.P0,
                expected_benefit="接入MCP生态，扩展工具能力",
                implementation_approach="实现MCP Client，支持工具发现和调用"
            )
        ]


def main():
    """测试学习引擎"""
    engine = GitHubLearningEngine()
    
    # 使用模板创建学习报告
    insights = LearningTemplates.create_autogen_insights()
    suggestions = LearningTemplates.create_autogen_suggestions()
    
    report = engine.analyze_project(
        project_name="microsoft/autogen",
        project_url="https://github.com/microsoft/autogen",
        stars=56800,
        language="Python",
        insights=insights,
        suggestions=suggestions
    )
    
    print("\n" + "="*60)
    print("学习报告已生成")
    print("="*60)
    print(report.to_markdown())
    
    # 显示统计
    stats = engine.get_learning_stats()
    print("\n" + "="*60)
    print("学习统计")
    print("="*60)
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
