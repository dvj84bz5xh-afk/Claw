"""
健康检查系统 - 基于 Claw Code /doctor 设计

提供系统诊断、健康状态检查和故障排除指南
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional


class CheckStatus(Enum):
    """检查状态"""
    OK = "ok"                    # 正常
    WARNING = "warning"          # 警告
    ERROR = "error"              # 错误
    INFO = "info"                # 信息


@dataclass
class HealthCheckItem:
    """健康检查项"""
    name: str                    # 检查项名称
    category: str                # 类别
    status: CheckStatus          # 状态
    message: str                 # 检查结果消息
    details: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""     # 建议


@dataclass
class HealthReport:
    """健康报告"""
    timestamp: datetime
    overall_status: CheckStatus
    checks: List[HealthCheckItem]
    summary: Dict[str, int] = field(default_factory=dict)  # 各状态计数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status.value,
            "summary": self.summary,
            "checks": [
                {
                    "name": c.name,
                    "category": c.category,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                    "recommendation": c.recommendation
                }
                for c in self.checks
            ]
        }
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = [
            "# Agent Core 健康检查报告",
            "",
            f"**检查时间**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**整体状态**: {self._status_emoji(self.overall_status)} {self.overall_status.value.upper()}",
            "",
            "## 检查摘要",
            ""
        ]
        
        # 摘要表格
        lines.append("| 状态 | 数量 |")
        lines.append("|------|------|")
        for status, count in self.summary.items():
            lines.append(f"| {status} | {count} |")
        
        lines.extend(["", "## 详细检查结果", ""])
        
        # 按类别分组
        categories = {}
        for check in self.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)
        
        for category, checks in categories.items():
            lines.append(f"### {category}")
            lines.append("")
            for check in checks:
                emoji = self._status_emoji(check.status)
                lines.append(f"**{emoji} {check.name}**")
                lines.append(f"- 状态: {check.status.value}")
                lines.append(f"- 消息: {check.message}")
                if check.details:
                    lines.append(f"- 详情: {json.dumps(check.details, ensure_ascii=False)}")
                if check.recommendation:
                    lines.append(f"- 建议: {check.recommendation}")
                lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _status_emoji(status: CheckStatus) -> str:
        """状态对应的标记"""
        return {
            CheckStatus.OK: "[OK]",
            CheckStatus.WARNING: "[WARN]",
            CheckStatus.ERROR: "[ERR]",
            CheckStatus.INFO: "[INFO]"
        }.get(status, "[?]")


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.checks: List[HealthCheckItem] = []
    
    def run_all_checks(self) -> HealthReport:
        """运行所有检查"""
        self.checks = []
        
        # 系统环境检查
        self._check_python_version()
        self._check_git_installation()
        self._check_node_installation()
        
        # 核心模块检查
        self._check_agent_core_modules()
        self._check_tool_registry()
        self._check_session_storage()
        
        # 配置检查
        self._check_git_config()
        self._check_github_credentials()
        
        # 权限系统检查
        self._check_permission_system()
        self._check_session_compaction()
        
        # 工作区检查
        self._check_workspace_structure()
        self._check_memory_system()
        
        # 计算整体状态
        overall_status = self._calculate_overall_status()
        summary = self._calculate_summary()
        
        return HealthReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            checks=self.checks,
            summary=summary
        )
    
    def _add_check(self, item: HealthCheckItem):
        """添加检查项"""
        self.checks.append(item)
    
    def _calculate_overall_status(self) -> CheckStatus:
        """计算整体状态"""
        if any(c.status == CheckStatus.ERROR for c in self.checks):
            return CheckStatus.ERROR
        if any(c.status == CheckStatus.WARNING for c in self.checks):
            return CheckStatus.WARNING
        return CheckStatus.OK
    
    def _calculate_summary(self) -> Dict[str, int]:
        """计算摘要统计"""
        summary = {"ok": 0, "warning": 0, "error": 0, "info": 0}
        for check in self.checks:
            summary[check.status.value] += 1
        return summary
    
    # ========== 具体检查项 ==========
    
    def _check_python_version(self):
        """检查Python版本"""
        import sys
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 10:
            status = CheckStatus.OK
            message = f"Python {version_str} 符合要求 (>= 3.10)"
        else:
            status = CheckStatus.WARNING
            message = f"Python {version_str} 版本较低，建议升级到 3.10+"
        
        self._add_check(HealthCheckItem(
            name="Python版本",
            category="系统环境",
            status=status,
            message=message,
            details={"version": version_str, "executable": sys.executable}
        ))
    
    def _check_git_installation(self):
        """检查Git安装"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self._add_check(HealthCheckItem(
                    name="Git安装",
                    category="系统环境",
                    status=CheckStatus.OK,
                    message=f"Git已安装: {version}",
                    details={"version": version}
                ))
            else:
                self._add_check(HealthCheckItem(
                    name="Git安装",
                    category="系统环境",
                    status=CheckStatus.ERROR,
                    message="Git安装异常",
                    recommendation="请重新安装Git"
                ))
        except FileNotFoundError:
            self._add_check(HealthCheckItem(
                name="Git安装",
                category="系统环境",
                status=CheckStatus.ERROR,
                message="Git未安装或不在PATH中",
                recommendation="请安装Git并添加到PATH"
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="Git安装",
                category="系统环境",
                status=CheckStatus.ERROR,
                message=f"检查Git时出错: {str(e)}"
            ))
    
    def _check_node_installation(self):
        """检查Node.js安装"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self._add_check(HealthCheckItem(
                    name="Node.js安装",
                    category="系统环境",
                    status=CheckStatus.OK,
                    message=f"Node.js已安装: {version}",
                    details={"version": version}
                ))
            else:
                self._add_check(HealthCheckItem(
                    name="Node.js安装",
                    category="系统环境",
                    status=CheckStatus.WARNING,
                    message="Node.js安装异常",
                    recommendation="某些功能可能需要Node.js"
                ))
        except FileNotFoundError:
            self._add_check(HealthCheckItem(
                name="Node.js安装",
                category="系统环境",
                status=CheckStatus.INFO,
                message="Node.js未安装",
                recommendation="如需使用JavaScript相关功能，请安装Node.js"
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="Node.js安装",
                category="系统环境",
                status=CheckStatus.WARNING,
                message=f"检查Node.js时出错: {str(e)}"
            ))
    
    def _check_agent_core_modules(self):
        """检查Agent Core核心模块"""
        agent_core_path = self.workspace_root / "agent-core"
        
        # 检查目录是否存在
        if not agent_core_path.exists():
            self._add_check(HealthCheckItem(
                name="核心模块",
                category="核心模块",
                status=CheckStatus.ERROR,
                message="agent-core目录不存在",
                details={"path": str(agent_core_path)},
                recommendation="请检查工作区结构"
            ))
            return
        
        # 旧版模块列表（向后兼容）
        legacy_modules = [
            "tool_registry.py",
            "permission_context.py",
            "session_manager.py",
            "command_router.py"
        ]
        
        # 新版增强模块列表
        enhanced_modules = [
            "__init__.py",
            "permission_enhanced.py",
            "session_compaction.py",
            "health_check.py",
            "environment_optimizer.py"
        ]
        
        legacy_existing = [m for m in legacy_modules if (agent_core_path / m).exists()]
        enhanced_existing = [m for m in enhanced_modules if (agent_core_path / m).exists()]
        
        # 如果新版模块存在，优先报告新版
        if enhanced_existing:
            self._add_check(HealthCheckItem(
                name="核心模块",
                category="核心模块",
                status=CheckStatus.OK,
                message=f"增强版核心模块正常 ({len(enhanced_existing)}个)",
                details={
                    "enhanced_modules": enhanced_existing,
                    "legacy_modules": legacy_existing,
                    "agent_core_path": str(agent_core_path)
                }
            ))
        elif legacy_existing:
            self._add_check(HealthCheckItem(
                name="核心模块",
                category="核心模块",
                status=CheckStatus.WARNING,
                message=f"基础核心模块存在，建议升级到增强版",
                details={
                    "legacy_modules": legacy_existing,
                    "missing_enhanced": [m for m in enhanced_modules if m not in enhanced_existing]
                },
                recommendation="请安装增强版模块: permission_enhanced.py, session_compaction.py"
            ))
        else:
            self._add_check(HealthCheckItem(
                name="核心模块",
                category="核心模块",
                status=CheckStatus.ERROR,
                message=f"缺少核心模块: {', '.join(missing)}",
                details={"missing": missing, "existing": existing},
                recommendation="请检查agent-core目录完整性"
            ))
        
        # 检查新增强模块
        enhanced_modules = [
            "permission_enhanced.py",
            "session_compaction.py",
            "health_check.py"
        ]
        
        enhanced_existing = [
            m for m in enhanced_modules 
            if (agent_core_path / m).exists()
        ]
        
        self._add_check(HealthCheckItem(
            name="增强模块",
            category="核心模块",
            status=CheckStatus.OK if len(enhanced_existing) == len(enhanced_modules) else CheckStatus.INFO,
            message=f"增强模块: {len(enhanced_existing)}/{len(enhanced_modules)} 已安装",
            details={"installed": enhanced_existing}
        ))
    
    def _check_tool_registry(self):
        """检查工具注册表"""
        # 检查文件是否存在
        registry_file = self.workspace_root / "agent-core" / "tool_registry.py"
        
        if not registry_file.exists():
            self._add_check(HealthCheckItem(
                name="工具注册表",
                category="核心模块",
                status=CheckStatus.INFO,
                message="工具注册表模块未安装（可选）",
                details={"status": "optional"},
                recommendation="如需使用，请创建tool_registry.py"
            ))
            return
        
        try:
            # 动态添加路径
            import sys
            agent_core_path = str(self.workspace_root / "agent-core")
            if agent_core_path not in sys.path:
                sys.path.insert(0, agent_core_path)
            
            from tool_registry import ToolRegistry
            registry = ToolRegistry()
            tools = registry.list_tools()
            
            self._add_check(HealthCheckItem(
                name="工具注册表",
                category="核心模块",
                status=CheckStatus.OK,
                message=f"工具注册表正常，已注册 {len(tools)} 个工具",
                details={"tool_count": len(tools)}
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="工具注册表",
                category="核心模块",
                status=CheckStatus.INFO,
                message=f"工具注册表检查失败: {str(e)}",
                recommendation="请检查tool_registry.py文件或稍后重试"
            ))
    
    def _check_session_storage(self):
        """检查会话存储"""
        session_path = Path.home() / ".claw" / "sessions"
        
        try:
            session_path.mkdir(parents=True, exist_ok=True)
            
            # 检查读写权限
            test_file = session_path / ".test"
            test_file.write_text("test")
            test_file.unlink()
            
            # 统计现有会话
            sessions = list(session_path.glob("*.json"))
            
            self._add_check(HealthCheckItem(
                name="会话存储",
                category="核心模块",
                status=CheckStatus.OK,
                message=f"会话存储正常，现有 {len(sessions)} 个会话",
                details={
                    "storage_path": str(session_path),
                    "session_count": len(sessions)
                }
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="会话存储",
                category="核心模块",
                status=CheckStatus.ERROR,
                message=f"会话存储检查失败: {str(e)}",
                recommendation=f"请检查目录权限: {session_path}"
            ))
    
    def _check_git_config(self):
        """检查Git配置"""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "--list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                configs = result.stdout.strip().split("\n")
                
                # 检查关键配置
                has_user = any("user.name" in c for c in configs)
                has_email = any("user.email" in c for c in configs)
                
                if has_user and has_email:
                    status = CheckStatus.OK
                    message = "Git全局配置完整"
                else:
                    status = CheckStatus.WARNING
                    message = "Git用户配置不完整"
                
                self._add_check(HealthCheckItem(
                    name="Git配置",
                    category="配置",
                    status=status,
                    message=message,
                    details={
                        "has_user_name": has_user,
                        "has_user_email": has_email,
                        "config_count": len(configs)
                    },
                    recommendation="如未配置，请运行: git config --global user.name/email"
                ))
            else:
                self._add_check(HealthCheckItem(
                    name="Git配置",
                    category="配置",
                    status=CheckStatus.WARNING,
                    message="无法读取Git配置"
                ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="Git配置",
                category="配置",
                status=CheckStatus.WARNING,
                message=f"检查Git配置时出错: {str(e)}"
            ))
    
    def _check_github_credentials(self):
        """检查GitHub凭据"""
        cred_path = Path.home() / ".git-credentials"
        
        if cred_path.exists():
            try:
                content = cred_path.read_text()
                if "github.com" in content:
                    self._add_check(HealthCheckItem(
                        name="GitHub凭据",
                        category="配置",
                        status=CheckStatus.OK,
                        message="GitHub凭据已配置",
                        details={"credential_file": str(cred_path)}
                    ))
                else:
                    self._add_check(HealthCheckItem(
                        name="GitHub凭据",
                        category="配置",
                        status=CheckStatus.INFO,
                        message="凭据文件存在但未找到GitHub配置"
                    ))
            except Exception as e:
                self._add_check(HealthCheckItem(
                    name="GitHub凭据",
                    category="配置",
                    status=CheckStatus.WARNING,
                    message=f"读取凭据文件失败: {str(e)}"
                ))
        else:
            self._add_check(HealthCheckItem(
                name="GitHub凭据",
                category="配置",
                status=CheckStatus.INFO,
                message="GitHub凭据未配置",
                recommendation="如需使用GitHub功能，请配置凭据"
            ))
    
    def _check_permission_system(self):
        """检查权限系统"""
        # 首先检查文件是否存在
        permission_file = self.workspace_root / "agent-core" / "permission_enhanced.py"
        
        if not permission_file.exists():
            self._add_check(HealthCheckItem(
                name="权限系统",
                category="核心模块",
                status=CheckStatus.WARNING,
                message="未找到增强版权限系统文件",
                details={"fallback": "使用基础权限系统"}
            ))
            return
        
        # 尝试导入并测试
        try:
            # 动态添加路径
            import sys
            agent_core_path = str(self.workspace_root / "agent-core")
            if agent_core_path not in sys.path:
                sys.path.insert(0, agent_core_path)
            
            from permission_enhanced import (
                PermissionLevel, PermissionEnforcer, BashCommandClassifier,
                PermissionContext
            )
            
            # 测试权限系统
            context = PermissionContext(mode=PermissionLevel.READ)
            enforcer = PermissionEnforcer(context)
            
            # 测试基础功能
            result = enforcer.check_bash("ls -la")
            
            self._add_check(HealthCheckItem(
                name="权限系统",
                category="核心模块",
                status=CheckStatus.OK,
                message="增强版权限系统正常工作",
                details={
                    "permission_levels": ["read-only", "workspace-write", "danger-full-access"],
                    "features": ["bash_classification", "path_validation", "dynamic_permission"],
                    "test_result": str(result.outcome)
                }
            ))
        except ImportError as e:
            self._add_check(HealthCheckItem(
                name="权限系统",
                category="核心模块",
                status=CheckStatus.WARNING,
                message=f"权限系统导入失败: {str(e)}",
                details={"fallback": "使用基础权限系统"}
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="权限系统",
                category="核心模块",
                status=CheckStatus.ERROR,
                message=f"权限系统检查失败: {str(e)}"
            ))
    
    def _check_session_compaction(self):
        """检查会话压缩"""
        # 首先检查文件是否存在
        compaction_file = self.workspace_root / "agent-core" / "session_compaction.py"
        
        if not compaction_file.exists():
            self._add_check(HealthCheckItem(
                name="会话压缩",
                category="核心模块",
                status=CheckStatus.INFO,
                message="会话压缩系统未安装",
                recommendation="如需使用，请安装session_compaction.py"
            ))
            return
        
        # 尝试导入并测试
        try:
            # 动态添加路径
            import sys
            agent_core_path = str(self.workspace_root / "agent-core")
            if agent_core_path not in sys.path:
                sys.path.insert(0, agent_core_path)
            
            from session_compaction import (
                SessionManager, TokenEstimator
            )
            
            # 测试Token估算
            tokens = TokenEstimator.estimate_text("Hello World")
            
            self._add_check(HealthCheckItem(
                name="会话压缩",
                category="核心模块",
                status=CheckStatus.OK,
                message="会话压缩系统正常工作",
                details={
                    "features": ["token_estimation", "auto_compaction", "session_persistence"],
                    "test_tokens": tokens
                }
            ))
        except ImportError as e:
            self._add_check(HealthCheckItem(
                name="会话压缩",
                category="核心模块",
                status=CheckStatus.INFO,
                message=f"会话压缩导入失败: {str(e)}",
                recommendation="如需使用，请安装session_compaction.py"
            ))
        except Exception as e:
            self._add_check(HealthCheckItem(
                name="会话压缩",
                category="核心模块",
                status=CheckStatus.WARNING,
                message=f"会话压缩检查失败: {str(e)}"
            ))
    
    def _check_workspace_structure(self):
        """检查工作区结构"""
        required_dirs = [
            ("agent-core", True),  # (目录名, 是否必需)
            (".workbuddy", False),
            (".claw", False),
        ]
        
        missing = []
        existing = []
        optional_missing = []
        
        for dir_name, is_required in required_dirs:
            dir_path = self.workspace_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                existing.append(dir_name)
            else:
                if is_required:
                    missing.append(dir_name)
                else:
                    optional_missing.append(dir_name)
        
        if not missing:
            msg = f"工作区结构正常 ({len(existing)}个目录)"
            if optional_missing:
                msg += f"，可选目录: {optional_missing}"
            self._add_check(HealthCheckItem(
                name="工作区结构",
                category="工作区",
                status=CheckStatus.OK,
                message=msg,
                details={
                    "existing": existing,
                    "optional_missing": optional_missing
                }
            ))
        else:
            self._add_check(HealthCheckItem(
                name="工作区结构",
                category="工作区",
                status=CheckStatus.WARNING,
                message=f"缺少目录: {', '.join(missing)}",
                details={"missing": missing, "existing": existing}
            ))
    
    def _check_memory_system(self):
        """检查记忆系统"""
        memory_path = self.workspace_root / ".workbuddy" / "memory"
        
        if memory_path.exists():
            # 检查今天的记忆文件
            today_file = memory_path / datetime.now().strftime("%Y-%m-%d.md")
            
            self._add_check(HealthCheckItem(
                name="记忆系统",
                category="工作区",
                status=CheckStatus.OK,
                message="记忆系统已配置",
                details={
                    "memory_path": str(memory_path),
                    "today_file_exists": today_file.exists()
                }
            ))
        else:
            self._add_check(HealthCheckItem(
                name="记忆系统",
                category="工作区",
                status=CheckStatus.INFO,
                message="记忆系统未初始化",
                recommendation="系统将在首次使用时自动创建"
            ))


# 便捷函数
def run_health_check(workspace_root: Optional[Path] = None) -> HealthReport:
    """运行健康检查"""
    checker = HealthChecker(workspace_root)
    return checker.run_all_checks()


def doctor_command():
    """/doctor 命令入口"""
    print("Agent Core Health Check")
    print("=" * 60)
    print()
    
    report = run_health_check()
    
    print(report.to_markdown())
    
    # 保存报告
    report_path = Path.home() / ".claw" / "health-reports"
    report_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = report_path / f"health-report-{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"\nReport saved: {report_file}")
    
    return report


# 测试
if __name__ == "__main__":
    doctor_command()
