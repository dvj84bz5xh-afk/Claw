"""
环境优化器 - 自动修复健康检查中的问题

功能:
1. 完善Git配置
2. 优化权限系统
3. 修复工作区结构
4. 建立舒适的开发环境
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class OptimizationResult:
    """优化结果"""
    component: str
    status: str  # 'fixed', 'already_ok', 'failed'
    message: str
    details: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            'component': self.component,
            'status': self.status,
            'message': self.message,
            'details': self.details or {}
        }


class GitConfigurator:
    """Git配置优化器"""
    
    def __init__(self):
        self.config_checks = [
            ('user.name', 'Agent-User'),
            ('user.email', 'agent@workbuddy.local'),
            ('core.autocrlf', 'true'),
            ('core.longpaths', 'true'),
            ('init.defaultBranch', 'main'),
            ('fetch.prune', 'true'),
            ('pull.rebase', 'false'),
            ('credential.helper', 'store'),
            ('core.editor', 'code --wait'),
            ('color.ui', 'auto'),
            ('push.default', 'simple'),
            ('merge.tool', 'vscode'),
            ('mergetool.vscode.cmd', 'code --wait "$MERGED"'),
        ]
    
    def optimize(self) -> OptimizationResult:
        """优化Git配置"""
        results = []
        
        for key, value in self.config_checks:
            try:
                # 检查当前值
                current = subprocess.run(
                    ['git', 'config', '--global', key],
                    capture_output=True,
                    text=True
                )
                
                if current.returncode != 0 or current.stdout.strip() != value:
                    # 需要设置
                    subprocess.run(
                        ['git', 'config', '--global', key, value],
                        check=True,
                        capture_output=True
                    )
                    results.append(f"{key} = {value} (已设置)")
                else:
                    results.append(f"{key} = {value} (已存在)")
                    
            except subprocess.CalledProcessError as e:
                return OptimizationResult(
                    component='Git配置',
                    status='failed',
                    message=f'配置 {key} 失败: {e}',
                    details={'error': str(e)}
                )
        
        return OptimizationResult(
            component='Git配置',
            status='fixed',
            message=f'Git配置已优化，共 {len(self.config_checks)} 项',
            details={'configs': results}
        )


class PermissionSystemOptimizer:
    """权限系统优化器"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.agent_core_dir = workspace_root / 'agent-core'
        
    def optimize(self) -> OptimizationResult:
        """优化权限系统"""
        optimizations = []
        
        # 1. 确保agent-core目录结构完整
        required_files = [
            '__init__.py',
            'permission_enhanced.py',
            'session_compaction.py',
            'health_check.py',
            'environment_optimizer.py',
        ]
        
        missing_files = []
        for file in required_files:
            file_path = self.agent_core_dir / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            return OptimizationResult(
                component='权限系统',
                status='failed',
                message=f'缺少核心文件: {missing_files}',
                details={'missing': missing_files}
            )
        
        optimizations.append(f'核心文件检查通过: {len(required_files)} 项')
        
        # 2. 创建权限策略配置文件
        policy_config = self.agent_core_dir / 'policy_config.json'
        if not policy_config.exists():
            policy = {
                'default_mode': 'workspace-write',
                'dangerous_commands': [
                    'rm -rf',
                    'format',
                    'del /f',
                    'rd /s',
                ],
                'protected_paths': [
                    str(Path.home()),
                    'C:\\Windows',
                    '/etc',
                    '/usr',
                ],
                'auto_approve_patterns': [
                    'read_*',
                    'search_*',
                    'list_*',
                ],
                'version': '2.0.0'
            }
            with open(policy_config, 'w', encoding='utf-8') as f:
                json.dump(policy, f, indent=2, ensure_ascii=False)
            optimizations.append('创建权限策略配置文件')
        else:
            optimizations.append('权限策略配置文件已存在')
        
        # 3. 验证权限模块可导入
        try:
            sys.path.insert(0, str(self.workspace_root))
            from agent_core.permission_enhanced import PermissionEnforcer
            enforcer = PermissionEnforcer(self.workspace_root)
            test_result = enforcer.check_bash('ls -la', auto_approve=False)
            optimizations.append(f'权限系统测试通过: {test_result.status}')
        except Exception as e:
            return OptimizationResult(
                component='权限系统',
                status='failed',
                message=f'权限模块测试失败: {e}',
                details={'error': str(e)}
            )
        
        return OptimizationResult(
            component='权限系统',
            status='fixed',
            message='权限系统已优化至增强版',
            details={
                'optimizations': optimizations,
                'level': 'enhanced',
                'mode': 'workspace-write'
            }
        )


class WorkspaceStructureOptimizer:
    """工作区结构优化器"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        
    def optimize(self) -> OptimizationResult:
        """优化工作区结构"""
        optimizations = []
        
        # 1. 确保核心目录存在
        directories = {
            'agent-core': '核心模块目录',
            '.workbuddy': '工作伙伴配置目录',
            '.workbuddy/memory': '记忆系统目录',
            '.workbuddy/skills': '技能目录',
            '.claw/sessions': '会话存储目录',
            '.claw/health-reports': '健康报告目录',
            'logs': '日志目录',
            'temp': '临时文件目录',
        }
        
        for dir_name, description in directories.items():
            dir_path = self.workspace_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                optimizations.append(f'创建目录: {dir_name} ({description})')
            else:
                optimizations.append(f'目录已存在: {dir_name}')
        
        # 2. 创建.gitignore（如果不存在）
        gitignore = self.workspace_root / '.gitignore'
        if not gitignore.exists():
            gitignore_content = """# Agent Core
.claw/sessions/*.json
.claw/health-reports/
logs/
temp/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Secrets
.env
*.key
*.pem
.git-credentials.bak
"""
            with open(gitignore, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            optimizations.append('创建.gitignore文件')
        
        # 3. 创建工作区配置文件
        workspace_config = self.workspace_root / '.workbuddy' / 'workspace.json'
        if not workspace_config.exists():
            config = {
                'name': 'Claw Workspace',
                'version': '2.0.0',
                'created_at': datetime.now().isoformat(),
                'features': {
                    'permission_system': 'enhanced',
                    'session_compaction': True,
                    'health_check': True,
                    'git_integration': True,
                },
                'paths': {
                    'agent_core': 'agent-core',
                    'memory': '.workbuddy/memory',
                    'sessions': '.claw/sessions',
                    'logs': 'logs',
                },
                'session': {
                    'retention_days': None,  # None = 无限保留
                    'auto_cleanup': False,   # 不自动清理
                    'max_sessions': None,    # None = 不限制数量
                    'compression_enabled': True,
                    'persistence_enabled': True,
                }
            }
            with open(workspace_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            optimizations.append('创建工作区配置文件（会话无限保留）')
        
        # 4. 验证目录权限
        readable_dirs = []
        writable_dirs = []
        
        for dir_name in ['agent-core', '.workbuddy', 'logs', 'temp']:
            dir_path = self.workspace_root / dir_name
            if dir_path.exists():
                try:
                    # 测试读权限
                    list(dir_path.iterdir())
                    readable_dirs.append(dir_name)
                    
                    # 测试写权限
                    test_file = dir_path / '.write_test'
                    test_file.write_text('test')
                    test_file.unlink()
                    writable_dirs.append(dir_name)
                except Exception as e:
                    optimizations.append(f'警告: {dir_name} 权限问题: {e}')
        
        return OptimizationResult(
            component='工作区结构',
            status='fixed',
            message=f'工作区结构已优化',
            details={
                'optimizations': optimizations,
                'directories_created': len([o for o in optimizations if '创建' in o]),
                'readable_dirs': readable_dirs,
                'writable_dirs': writable_dirs
            }
        )


class EnvironmentOptimizer:
    """环境优化主控器"""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.optimizers = [
            GitConfigurator(),
            PermissionSystemOptimizer(self.workspace_root),
            WorkspaceStructureOptimizer(self.workspace_root),
        ]
    
    def run_optimization(self) -> List[OptimizationResult]:
        """运行所有优化"""
        results = []
        
        print("=" * 60)
        print("环境优化器 - 自动修复环境")
        print("=" * 60)
        print()
        
        for optimizer in self.optimizers:
            print(f"正在优化: {optimizer.__class__.__name__}...")
            try:
                result = optimizer.optimize()
                results.append(result)
                
                status_icon = {
                    'fixed': '[OK]',
                    'already_ok': '[OK]',
                    'failed': '[ERR]'
                }.get(result.status, '[?]')
                
                print(f"  {status_icon} {result.component}: {result.message}")
                
                if result.details:
                    if 'optimizations' in result.details:
                        for opt in result.details['optimizations'][:5]:
                            print(f"      - {opt}")
                        if len(result.details['optimizations']) > 5:
                            print(f"      ... 还有 {len(result.details['optimizations']) - 5} 项")
                
            except Exception as e:
                error_result = OptimizationResult(
                    component=optimizer.__class__.__name__,
                    status='failed',
                    message=f'优化过程中出错: {e}',
                    details={'error': str(e)}
                )
                results.append(error_result)
                print(f"  [ERR] {error_result.component}: {error_result.message}")
            
            print()
        
        return results
    
    def generate_report(self, results: List[OptimizationResult]) -> str:
        """生成优化报告"""
        fixed = sum(1 for r in results if r.status == 'fixed')
        already_ok = sum(1 for r in results if r.status == 'already_ok')
        failed = sum(1 for r in results if r.status == 'failed')
        
        lines = [
            "=" * 60,
            "环境优化报告",
            "=" * 60,
            "",
            f"优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"工作区: {self.workspace_root}",
            "",
            "优化结果统计:",
            f"  - 已修复: {fixed} 项",
            f"  - 已是最优: {already_ok} 项",
            f"  - 失败: {failed} 项",
            "",
            "详细结果:",
        ]
        
        for result in results:
            icon = {'fixed': '[OK]', 'already_ok': '[OK]', 'failed': '[ERR]'}.get(result.status, '[?]')
            lines.append(f"  {icon} {result.component}: {result.status}")
            lines.append(f"    {result.message}")
        
        lines.extend([
            "",
            "=" * 60,
            "优化完成！建议运行健康检查验证结果。",
            "=" * 60,
        ])
        
        return '\n'.join(lines)


def main():
    """主函数"""
    # 确定工作区根目录
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    
    optimizer = EnvironmentOptimizer(workspace_root)
    results = optimizer.run_optimization()
    
    report = optimizer.generate_report(results)
    print(report)
    
    # 保存报告
    report_file = workspace_root / 'logs' / f'optimization-report-{datetime.now():%Y%m%d-%H%M%S}.txt'
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_file}")
    
    return 0 if all(r.status in ('fixed', 'already_ok') for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
