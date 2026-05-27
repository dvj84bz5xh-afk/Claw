#!/usr/bin/env python3
"""
Skill Transparency Enhancer - 技能透明度增强器

基于CL4R1T4S项目的学习收获，增强技能系统的透明度：
1. 工作流程可视化
2. 约束条件明确化
3. 决策过程可追溯
4. 用户指导优化

设计原则：
- 用户有权了解AI背后的约束和偏见
- 系统应该清晰展示工作流程
- 技能应该模块化、可组合、可扩展
- 自动化验证机制保证质量
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

class TransparencyLevel(Enum):
    """透明度级别"""
    BASIC = "basic"      # 基本信息
    DETAILED = "detailed"  # 详细说明
    FULL = "full"       # 完整跟踪
    DEBUG = "debug"     # 调试信息

class DecisionType(Enum):
    """决策类型"""
    SKILL_SELECTION = "skill_selection"
    PARAMETER_CHOICE = "parameter_choice"
    WORKFLOW_PATH = "workflow_path"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_HANDLING = "error_handling"
    QUALITY_CHECK = "quality_check"

class ConstraintType(Enum):
    """约束类型"""
    SYSTEM_LIMIT = "system_limit"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    COMPATIBILITY = "compatibility"
    POLICY = "policy"

@dataclass
class DecisionRecord:
    """决策记录"""
    id: str
    timestamp: datetime
    decision_type: DecisionType
    context: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    chosen_option: Dict[str, Any]
    reasons: List[str]
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "decision_type": self.decision_type.value,
            "context": self.context,
            "alternatives": self.alternatives,
            "chosen_option": self.chosen_option,
            "reasons": self.reasons,
            "confidence_score": self.confidence_score
        }

@dataclass
class ConstraintRecord:
    """约束记录"""
    id: str
    constraint_type: ConstraintType
    description: str
    impact: str
    justification: Optional[str] = None
    workaround: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "constraint_type": self.constraint_type.value,
            "description": self.description,
            "impact": self.impact,
            "justification": self.justification,
            "workaround": self.workaround,
            "severity": self.severity
        }

@dataclass
class WorkflowStep:
    """工作流程步骤"""
    step_id: str
    name: str
    description: str
    skill_used: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    status: str = "pending"  # pending, running, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "skill_used": self.skill_used,
            "tools_used": self.tools_used,
            "parameters": self.parameters,
            "duration_ms": self.duration_ms,
            "status": self.status
        }

@dataclass
class TransparencyReport:
    """透明度报告"""
    report_id: str
    session_id: str
    created_at: datetime
    
    # 核心信息
    task_description: str
    skill_configuration: Dict[str, Any]
    
    # 透明度记录
    workflow_steps: List[WorkflowStep] = field(default_factory=list)
    decisions: List[DecisionRecord] = field(default_factory=list)
    constraints: List[ConstraintRecord] = field(default_factory=list)
    
    # 用户指导
    user_guidance: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 质量保证
    verification_results: List[Dict[str, Any]] = field(default_factory=list)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    transparency_level: TransparencyLevel = TransparencyLevel.DETAILED
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "transparency_level": self.transparency_level.value,
            "task_description": self.task_description,
            "skill_configuration": self.skill_configuration,
            "workflow": [step.to_dict() for step in self.workflow_steps],
            "decisions": [decision.to_dict() for decision in self.decisions],
            "constraints": [constraint.to_dict() for constraint in self.constraints],
            "user_guidance": self.user_guidance,
            "tips": self.tips,
            "warnings": self.warnings,
            "verification_results": self.verification_results,
            "quality_metrics": self.quality_metrics
        }
    
    def to_html(self) -> str:
        """生成HTML格式的报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>透明度报告 - {self.report_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .section {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-top: 0; }}
        .step {{ background: #f7fafc; border-left: 4px solid #4299e1; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .step.completed {{ border-left-color: #48bb78; }}
        .step.running {{ border-left-color: #ed8936; }}
        .step.failed {{ border-left-color: #f56565; }}
        .decision {{ background: #fff5f5; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #fed7d7; }}
        .constraint {{ background: #fefcbf; padding: 15px; margin: 10px 0; border-radius: 8px; border: 1px solid #f6e05e; }}
        .severity-critical {{ border: 2px solid #c53030; background: #fff5f5; }}
        .severity-high {{ border: 2px solid #ed8936; background: #fffaf0; }}
        .severity-medium {{ border: 2px solid #ecc94b; background: #fffff0; }}
        .severity-low {{ border: 2px solid #48bb78; background: #f0fff4; }}
        .warning {{ background: #feebc8; border-left: 4px solid #ed8936; padding: 15px; margin: 15px 0; }}
        .tip {{ background: #c6f6d5; border-left: 4px solid #38a169; padding: 15px; margin: 15px 0; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: #edf2f7; padding: 15px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2d3748; }}
        .metric-label {{ font-size: 14px; color: #718096; }}
        .timestamp {{ color: #718096; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI 透明度报告</h1>
        <p class="timestamp">报告ID: {self.report_id} | 生成时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>任务: {self.task_description}</p>
    </div>
"""
        
        # 工作流程部分
        if self.workflow_steps:
            html += f"""
    <div class="section">
        <h2>📋 工作流程 ({len(self.workflow_steps)}个步骤)</h2>
"""
            for step in self.workflow_steps:
                step_class = f"step {step.status}"
                html += f"""
        <div class="{step_class}">
            <h3>步骤 {step.step_id}: {step.name}</h3>
            <p>{step.description}</p>
"""
                if step.skill_used:
                    html += f'            <p><strong>使用的技能:</strong> {step.skill_used}</p>\n'
                if step.tools_used:
                    html += f'            <p><strong>使用的工具:</strong> {", ".join(step.tools_used)}</p>\n'
                if step.duration_ms:
                    html += f'            <p><strong>耗时:</strong> {step.duration_ms}ms</p>\n'
                html += f'            <p><strong>状态:</strong> {step.status}</p>\n'
                html += "        </div>\n"
            html += "    </div>\n"
        
        # 决策记录部分
        if self.decisions:
            html += f"""
    <div class="section">
        <h2>🧠 决策记录 ({len(self.decisions)}个决策)</h2>
"""
            for decision in self.decisions[:10]:  # 最多显示10个
                html += f"""
        <div class="decision">
            <h3>{decision.decision_type.value.replace('_', ' ').title()}</h3>
            <p><strong>选择:</strong> {json.dumps(decision.chosen_option, ensure_ascii=False)}</p>
            <p><strong>理由:</strong> {", ".join(decision.reasons)}</p>
            <p><strong>置信度:</strong> {decision.confidence_score:.2f}</p>
            <p><strong>时间:</strong> {decision.timestamp.strftime('%H:%M:%S')}</p>
            <p><strong>备选方案:</strong> {len(decision.alternatives)}个</p>
        </div>
"""
            if len(self.decisions) > 10:
                html += f"        <p><em>...还有 {len(self.decisions) - 10} 个决策记录</em></p>\n"
            html += "    </div>\n"
        
        # 约束条件部分
        if self.constraints:
            html += f"""
    <div class="section">
        <h2>⚠️ 系统约束 ({len(self.constraints)}个约束)</h2>
"""
            for constraint in self.constraints:
                severity_class = f"constraint severity-{constraint.severity}"
                html += f"""
        <div class="{severity_class}">
            <h3>{constraint.constraint_type.value.replace('_', ' ').title()} - 严重程度: {constraint.severity}</h3>
            <p>{constraint.description}</p>
            <p><strong>影响:</strong> {constraint.impact}</p>
"""
                if constraint.justification:
                    html += f'            <p><strong>理由:</strong> {constraint.justification}</p>\n'
                if constraint.workaround:
                    html += f'            <p><strong>替代方案:</strong> {constraint.workaround}</p>\n'
                html += "        </div>\n"
            html += "    </div>\n"
        
        # 用户指导部分
        if self.user_guidance or self.tips or self.warnings:
            html += """
    <div class="section">
        <h2>💡 用户指导</h2>
"""
            if self.warnings:
                html += """
        <div class="warning">
            <h3>⚠️ 重要警告</h3>
            <ul>
"""
                for warning in self.warnings:
                    html += f'                <li>{warning}</li>\n'
                html += """
            </ul>
        </div>
"""
            
            if self.user_guidance:
                html += """
        <h3>📝 使用指导</h3>
        <ul>
"""
                for guidance in self.user_guidance:
                    html += f'            <li>{guidance}</li>\n'
                html += """
        </ul>
"""
            
            if self.tips:
                html += """
        <div class="tip">
            <h3>💡 实用技巧</h3>
            <ul>
"""
                for tip in self.tips:
                    html += f'                <li>{tip}</li>\n'
                html += """
            </ul>
        </div>
"""
            html += "    </div>\n"
        
        # 质量保证部分
        if self.quality_metrics or self.verification_results:
            html += """
    <div class="section">
        <h2>✅ 质量保证</h2>
"""
            if self.quality_metrics:
                html += """
        <div class="metric-grid">
"""
                for metric_name, metric_value in self.quality_metrics.items():
                    if isinstance(metric_value, (int, float)):
                        html += f"""
            <div class="metric">
                <div class="metric-value">{metric_value:.2f}</div>
                <div class="metric-label">{metric_name}</div>
            </div>
"""
                html += """
        </div>
"""
            
            if self.verification_results:
                html += """
        <h3>🔍 验证结果</h3>
"""
                for verification in self.verification_results:
                    status = verification.get('status', 'unknown')
                    result_emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
                    html += f"""
        <div class="step">
            <h4>{result_emoji} {verification.get('check_name', '未知检查')}</h4>
            <p>{verification.get('description', '')}</p>
"""
                    if 'details' in verification:
                        html += f'            <p><strong>详情:</strong> {verification["details"]}</p>\n'
                    html += f'            <p><strong>状态:</strong> {status}</p>\n'
                    html += "        </div>\n"
                html += "    </div>\n"
        
        # 技能配置部分
        html += f"""
    <div class="section">
        <h2>🔧 技能配置</h2>
        <pre style="background: #f7fafc; padding: 15px; border-radius: 8px; overflow-x: auto;">
{json.dumps(self.skill_configuration, ensure_ascii=False, indent=2)}
        </pre>
    </div>
"""
        
        # 总结部分
        html += f"""
    <div class="section">
        <h2>📊 总结</h2>
        <p>透明度级别: <strong>{self.transparency_level.value}</strong></p>
        <p>总步骤数: <strong>{len(self.workflow_steps)}</strong></p>
        <p>决策次数: <strong>{len(self.decisions)}</strong></p>
        <p>约束数量: <strong>{len(self.constraints)}</strong></p>
"""
        if self.completed_at:
            duration = (self.completed_at - self.created_at).total_seconds()
            html += f'        <p>总耗时: <strong>{duration:.2f}秒</strong></p>\n'
        
        html += """
        <p style="margin-top: 20px; color: #718096; font-size: 14px;">
            🔍 此报告展示了AI系统的工作流程、决策过程和约束条件，旨在提高系统透明度。
            用户可以借此了解AI如何工作以及为什么做出特定决策。
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def save_report(self, output_dir: str = "transparency_reports") -> str:
        """保存报告到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存JSON
        json_path = output_path / f"{self.report_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 保存HTML
        html_path = output_path / f"{self.report_id}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.to_html())
        
        return str(html_path)

class TransparencyEnhancer:
    """透明度增强器"""
    
    def __init__(self, transparency_level: TransparencyLevel = TransparencyLevel.DETAILED):
        self.transparency_level = transparency_level
        self.current_report = None
        self.workflow_step_counter = 0
    
    def start_new_report(self, task_description: str, skill_config: Dict[str, Any]) -> TransparencyReport:
        """开始新的透明度报告"""
        self.current_report = TransparencyReport(
            report_id=str(uuid.uuid4())[:8],
            session_id=str(uuid.uuid4())[:8],
            created_at=datetime.now(),
            task_description=task_description,
            skill_configuration=skill_config,
            transparency_level=self.transparency_level
        )
        self.workflow_step_counter = 0
        return self.current_report
    
    def add_workflow_step(self, name: str, description: str, skill_used: str = None, 
                          tools_used: List[str] = None, parameters: Dict[str, Any] = None) -> str:
        """添加工作流程步骤"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        self.workflow_step_counter += 1
        step_id = f"step_{self.workflow_step_counter:03d}"
        
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            description=description,
            skill_used=skill_used,
            tools_used=tools_used or [],
            parameters=parameters or {},
            status="completed"
        )
        
        self.current_report.workflow_steps.append(step)
        return step_id
    
    def record_decision(self, decision_type: DecisionType, context: Dict[str, Any], 
                       alternatives: List[Dict[str, Any]], chosen_option: Dict[str, Any], 
                       reasons: List[str], confidence_score: float = 1.0) -> str:
        """记录决策"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        decision_id = str(uuid.uuid4())[:8]
        
        decision = DecisionRecord(
            id=decision_id,
            timestamp=datetime.now(),
            decision_type=decision_type,
            context=context,
            alternatives=alternatives,
            chosen_option=chosen_option,
            reasons=reasons,
            confidence_score=confidence_score
        )
        
        self.current_report.decisions.append(decision)
        return decision_id
    
    def add_constraint(self, constraint_type: ConstraintType, description: str, impact: str,
                       justification: str = None, workaround: str = None, severity: str = "medium"):
        """添加约束条件"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        constraint = ConstraintRecord(
            id=str(uuid.uuid4())[:8],
            constraint_type=constraint_type,
            description=description,
            impact=impact,
            justification=justification,
            workaround=workaround,
            severity=severity
        )
        
        self.current_report.constraints.append(constraint)
    
    def add_user_guidance(self, guidance: str):
        """添加用户指导"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        self.current_report.user_guidance.append(guidance)
    
    def add_tip(self, tip: str):
        """添加实用技巧"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        self.current_report.tips.append(tip)
    
    def add_warning(self, warning: str):
        """添加警告"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        self.current_report.warnings.append(warning)
    
    def add_verification_result(self, check_name: str, description: str, status: str, details: str = None):
        """添加验证结果"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        result = {
            "check_name": check_name,
            "description": description,
            "status": status,
            "details": details
        }
        
        self.current_report.verification_results.append(result)
    
    def add_quality_metric(self, metric_name: str, metric_value: Any):
        """添加质量指标"""
        if not self.current_report:
            raise ValueError("没有活动的报告，请先调用start_new_report()")
        
        self.current_report.quality_metrics[metric_name] = metric_value
    
    def complete_report(self):
        """完成报告"""
        if not self.current_report:
            raise ValueError("没有活动的报告")
        
        self.current_report.completed_at = datetime.now()
        return self.current_report
    
    def generate_guidance_for_skill(self, skill_config: Dict[str, Any]) -> List[str]:
        """为技能生成指导信息"""
        guidance = []
        
        # 基于技能类型生成指导
        skill_type = skill_config.get("type", "unknown")
        if skill_type == "data_analysis":
            guidance.append("此技能需要数据文件作为输入，支持CSV、Excel和JSON格式")
            guidance.append("分析结果将以表格和图表形式呈现")
            guidance.append("如果需要特定分析功能，请明确说明需求")
        elif skill_type == "code_generation":
            guidance.append("此技能生成代码片段，请指定编程语言和功能要求")
            guidance.append("生成的代码需要人工审查和测试")
            guidance.append("可以要求特定编码风格或遵循特定规范")
        elif skill_type == "file_operation":
            guidance.append("此技能操作文件系统，请确保有适当的文件权限")
            guidance.append("敏感操作需要确认，请仔细阅读警告信息")
            guidance.append("建议操作前备份重要文件")
        
        # 基于约束生成指导
        constraints = skill_config.get("constraints", [])
        for constraint in constraints:
            if constraint.get("severity") in ["high", "critical"]:
                guidance.append(f"⚠️ 重要限制: {constraint.get('description')}")
        
        return guidance

# 测试函数
def test_transparency_enhancer():
    """测试透明度增强器"""
    print("="*70)
    print("Transparency Enhancer Test")
    print("="*70)
    
    enhancer = TransparencyEnhancer(TransparencyLevel.DETAILED)
    
    # 模拟技能配置
    skill_config = {
        "name": "数据分析技能",
        "type": "data_analysis",
        "version": "1.0.0",
        "capabilities": ["数据清洗", "统计分析", "可视化"],
        "constraints": [
            {
                "type": "system_limit",
                "description": "最大文件大小100MB",
                "severity": "medium"
            }
        ]
    }
    
    # 开始新报告
    report = enhancer.start_new_report(
        task_description="分析销售数据并提供洞察报告",
        skill_config=skill_config
    )
    
    print(f"报告ID: {report.report_id}")
    print(f"任务: {report.task_description}")
    
    # 添加工作流程步骤
    enhancer.add_workflow_step(
        name="数据加载",
        description="加载并验证销售数据文件",
        skill_used="file_loader_skill",
        tools_used=["read_file", "validate_data"],
        parameters={"file_format": "csv", "encoding": "utf-8"}
    )
    
    enhancer.add_workflow_step(
        name="数据清洗",
        description="处理缺失值和异常值",
        skill_used="data_cleaning_skill",
        tools_used=["pandas", "numpy"],
        parameters={"missing_strategy": "mean", "outlier_threshold": 3}
    )
    
    enhancer.add_workflow_step(
        name="分析洞察",
        description="执行统计分析和趋势检测",
        skill_used="analysis_skill",
        tools_used=["scipy", "matplotlib"],
        parameters={"analysis_type": "trend", "confidence_level": 0.95}
    )
    
    # 记录决策
    enhancer.record_decision(
        decision_type=DecisionType.SKILL_SELECTION,
        context={"task": "数据清洗", "available_skills": ["pandas_cleaner", "custom_cleaner"]},
        alternatives=[
            {"skill": "pandas_cleaner", "speed": "fast", "customization": "low"},
            {"skill": "custom_cleaner", "speed": "slow", "customization": "high"}
        ],
        chosen_option={"skill": "pandas_cleaner", "reason": "速度快，满足基本需求"},
        reasons=["时间效率优先", "基本清洗需求", "兼容性好"]
    )
    
    # 添加约束
    enhancer.add_constraint(
        constraint_type=ConstraintType.SYSTEM_LIMIT,
        description="最大处理行数：1,000,000行",
        impact="超过限制的数据将被截断",
        justification="内存限制和性能考虑",
        workaround="分批处理或使用数据库",
        severity="medium"
    )
    
    enhancer.add_constraint(
        constraint_type=ConstraintType.SECURITY,
        description="不支持包含敏感信息的数据文件",
        impact="系统会自动过滤敏感字段",
        justification="隐私保护政策",
        workaround="脱敏处理后上传",
        severity="high"
    )
    
    # 添加用户指导
    enhancer.add_user_guidance("上传数据前，请确保数据格式正确（CSV或Excel）")
    enhancer.add_user_guidance("分析结果以交互式图表形式呈现，可点击查看更多细节")
    enhancer.add_tip("使用描述性列名可以获得更好的分析结果")
    enhancer.add_warning("处理大量数据时可能需要较长时间，请耐心等待")
    
    # 添加验证结果
    enhancer.add_verification_result(
        check_name="数据完整性检查",
        description="验证数据文件是否完整无损坏",
        status="passed",
        details="所有数据行完整，无损坏记录"
    )
    
    enhancer.add_verification_result(
        check_name="隐私安全检查",
        description="检查是否包含敏感个人信息",
        status="passed",
        details="未发现明显敏感信息"
    )
    
    # 添加质量指标
    enhancer.add_quality_metric("数据质量评分", 8.5)
    enhancer.add_quality_metric("处理速度(行/秒)", 2500)
    enhancer.add_quality_metric("内存使用峰值(MB)", 125)
    
    # 完成报告
    completed_report = enhancer.complete_report()
    
    # 生成指导信息
    guidance = enhancer.generate_guidance_for_skill(skill_config)
    print(f"\n生成的指导信息 ({len(guidance)}条):")
    for item in guidance:
        print(f"  - {item}")
    
    # 保存报告
    html_path = completed_report.save_report()
    print(f"\n报告已保存到: {html_path}")
    
    # 显示报告摘要
    print(f"\n报告摘要:")
    print(f"  工作流程步骤: {len(completed_report.workflow_steps)}")
    print(f"  决策记录: {len(completed_report.decisions)}")
    print(f"  约束条件: {len(completed_report.constraints)}")
    print(f"  用户指导: {len(completed_report.user_guidance)}")
    print(f"  验证结果: {len(completed_report.verification_results)}")
    
    print("\n" + "="*70)
    print("Transparency Enhancer Test Completed!")
    print("="*70)
    
    return html_path

if __name__ == "__main__":
    # 运行测试
    html_path = test_transparency_enhancer()
    print(f"\nHTML报告路径: {html_path}")
    print("可以在浏览器中打开该文件查看完整的透明度报告")