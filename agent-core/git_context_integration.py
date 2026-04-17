"""
Git Context Integration Module
TimesFM能力 + Git上下文增强

将Git仓库上下文自动注入到任务处理中：
1. 实时Git状态感知
2. 修改文件上下文
3. 提交历史智能检索
4. 与TimesFM架构无缝集成
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import subprocess
import re
from pathlib import Path
from enum import Enum

# 导入TimesFM核心模块
from config_system import AgentCapabilityConfig, get_config
from task_patcher import TaskPatch, TaskType
from uncertainty_quantifier import UncertaintySource, ConfidenceLevel


class GitChangeType(Enum):
    """Git变更类型"""
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNTRACKED = "untracked"


@dataclass
class GitFileChange:
    """Git文件变更详情"""
    path: str
    change_type: GitChangeType
    staged: bool = False
    diff: Optional[str] = None
    
    @property
    def display_type(self) -> str:
        """显示类型"""
        type_map = {
            GitChangeType.MODIFIED: "修改",
            GitChangeType.ADDED: "新增",
            GitChangeType.DELETED: "删除",
            GitChangeType.RENAMED: "重命名",
            GitChangeType.UNTRACKED: "未跟踪"
        }
        return type_map.get(self.change_type, "未知")


@dataclass
class GitCommit:
    """Git提交信息"""
    hash: str
    short_hash: str
    message: str
    author: str
    timestamp: datetime
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash,
            "short_hash": self.short_hash,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "files_changed": self.files_changed,
            "stats": f"+{self.insertions}/-{self.deletions}"
        }


@dataclass
class GitContext:
    """Git上下文完整信息"""
    is_git_repo: bool = False
    repo_root: Optional[str] = None
    current_branch: Optional[str] = None
    
    # 状态信息
    status_text: str = "未知"
    is_clean: bool = True
    
    # 变更文件
    file_changes: List[GitFileChange] = field(default_factory=list)
    
    # 最近提交
    recent_commits: List[GitCommit] = field(default_factory=list)
    
    # 统计
    total_commits: int = 0
    contributors: List[str] = field(default_factory=list)
    
    # 元数据
    generated_at: datetime = field(default_factory=datetime.now)
    
    def has_modified_files(self) -> bool:
        """是否有修改的文件"""
        return any(c.change_type in [GitChangeType.MODIFIED, GitChangeType.ADDED] 
                  for c in self.file_changes)
    
    def get_modified_file_paths(self) -> List[str]:
        """获取修改的文件路径"""
        return [c.path for c in self.file_changes 
                if c.change_type in [GitChangeType.MODIFIED, GitChangeType.ADDED]]
    
    def get_relevant_commits(self, keywords: List[str], limit: int = 5) -> List[GitCommit]:
        """获取与关键词相关的提交"""
        relevant = []
        for commit in self.recent_commits:
            for keyword in keywords:
                if keyword.lower() in commit.message.lower():
                    relevant.append(commit)
                    break
            if len(relevant) >= limit:
                break
        return relevant


class GitContextProvider:
    """Git上下文提供者"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self._cache = None
        self._cache_time = None
    
    def _run_git(self, args: List[str]) -> Tuple[str, str, int]:
        """运行git命令"""
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=True,
                text=True,
                cwd=self.workspace_path,
                timeout=10
            )
            return result.stdout, result.stderr, result.returncode
        except Exception:
            return "", "执行失败", -1
    
    def get_context(self, force_refresh: bool = False) -> GitContext:
        """获取Git上下文"""
        # 检查缓存
        if not force_refresh and self._cache and self._cache_time:
            if (datetime.now() - self._cache_time).seconds < 30:  # 缓存30秒
                return self._cache
        
        context = GitContext()
        
        # 检查是否为Git仓库
        stdout, stderr, code = self._run_git(['rev-parse', '--is-inside-work-tree'])
        if code != 0 or stdout.strip() != 'true':
            context.is_git_repo = False
            return context
        
        context.is_git_repo = True
        
        # 获取仓库根目录
        stdout, _, _ = self._run_git(['rev-parse', '--show-toplevel'])
        context.repo_root = stdout.strip()
        
        # 获取当前分支
        stdout, _, _ = self._run_git(['branch', '--show-current'])
        context.current_branch = stdout.strip() or 'detached'
        
        # 获取状态
        stdout, _, _ = self._run_git(['status', '--porcelain'])
        lines = stdout.strip().split('\n') if stdout.strip() else []
        
        if not lines:
            context.status_text = "工作区干净"
            context.is_clean = True
        else:
            context.status_text = f"有 {len(lines)} 个文件变更"
            context.is_clean = False
            
            # 解析文件变更
            for line in lines:
                if not line.strip():
                    continue
                    
                status = line[:2].strip()
                file_path = line[3:]
                
                if status == 'M':
                    change_type = GitChangeType.MODIFIED
                elif status == 'A':
                    change_type = GitChangeType.ADDED
                elif status == 'D':
                    change_type = GitChangeType.DELETED
                elif status == 'R':
                    change_type = GitChangeType.RENAMED
                elif status == '??':
                    change_type = GitChangeType.UNTRACKED
                else:
                    change_type = GitChangeType.MODIFIED
                
                context.file_changes.append(GitFileChange(
                    path=file_path,
                    change_type=change_type,
                    staged=status[0] != ' '
                ))
        
        # 获取最近提交
        stdout, _, _ = self._run_git([
            'log', '--oneline', '--format=%H|%h|%s|%an|%at', '-10'
        ])
        
        if stdout:
            for line in stdout.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 5:
                    try:
                        timestamp = datetime.fromtimestamp(int(parts[4]))
                        commit = GitCommit(
                            hash=parts[0],
                            short_hash=parts[1],
                            message=parts[2],
                            author=parts[3],
                            timestamp=timestamp
                        )
                        context.recent_commits.append(commit)
                    except:
                        pass
        
        # 缓存结果
        self._cache = context
        self._cache_time = datetime.now()
        
        return context
    
    def get_file_content(self, filepath: str) -> Optional[str]:
        """获取文件内容（优先获取暂存版本）"""
        try:
            # 先尝试获取暂存版本
            stdout, _, code = self._run_git(['show', f':{filepath}'])
            if code == 0 and stdout:
                return stdout
            
            # 如果没有暂存版本，读取工作区文件
            file_path = self.workspace_path / filepath
            if file_path.exists():
                return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            pass
        return None
    
    def get_file_diff(self, filepath: str) -> Optional[str]:
        """获取文件差异"""
        stdout, _, code = self._run_git(['diff', '--no-color', filepath])
        if code == 0 and stdout:
            return stdout
        return None


class GitContextAwareTaskPatcher:
    """
    Git上下文感知的任务patcher
    
    增强TimesFM任务patcher，考虑Git上下文：
    1. 自动检测相关修改文件
    2. 避免重复工作
    3. 提供代码变更上下文
    """
    
    def __init__(self, git_provider: GitContextProvider, base_patcher=None):
        self.git_provider = git_provider
        self.base_patcher = base_patcher
    
    def enhance_with_git_context(self, task: str, patches: List[TaskPatch]) -> List[TaskPatch]:
        """用Git上下文增强patches"""
        git_context = self.git_provider.get_context()
        
        if not git_context.is_git_repo or git_context.is_clean:
            return patches
        
        enhanced_patches = []
        
        for patch in patches:
            enhanced_patch = TaskPatch(
                index=patch.index,
                content=self._add_git_context_to_patch(patch, git_context),
                task_type=patch.task_type,
                priority=patch.priority
            )
            enhanced_patches.append(enhanced_patch)
        
        return enhanced_patches
    
    def _add_git_context_to_patch(self, patch: TaskPatch, git_context: GitContext) -> str:
        """为patch添加Git上下文"""
        original_content = patch.content
        
        # 检测patch是否与修改的文件相关
        related_files = []
        for file_change in git_context.file_changes:
            if self._is_relevant_to_patch(file_change.path, patch):
                related_files.append(file_change)
        
        if not related_files:
            return original_content
        
        # 构建Git上下文注释
        git_context_note = "\n\n" + "="*60 + "\n"
        git_context_note += "[GIT] 上下文 (相关文件):\n"
        git_context_note += "="*60 + "\n"
        
        for file_change in related_files:
            git_context_note += f"\n[文件] {file_change.path} ({file_change.display_type})"
            
            if file_change.change_type in [GitChangeType.MODIFIED, GitChangeType.ADDED]:
                # 获取文件内容预览
                content = self.git_provider.get_file_content(file_change.path)
                if content:
                    lines = content.split('\n')
                    preview = '\n'.join(lines[:10])
                    if len(lines) > 10:
                        preview += f"\n... 还有 {len(lines) - 10} 行"
                    git_context_note += f"\n```\n{preview}\n```\n"
            
            # 获取diff
            diff = self.git_provider.get_file_diff(file_change.path)
            if diff:
                diff_lines = diff.split('\n')
                significant_diff = [line for line in diff_lines 
                                  if line.startswith('+') or line.startswith('-')]
                if significant_diff:
                    git_context_note += f"\n[差异] 变更摘要:\n```diff\n"
                    git_context_note += '\n'.join(significant_diff[:20])
                    if len(significant_diff) > 20:
                        git_context_note += f"\n... 还有 {len(significant_diff) - 20} 处变更"
                    git_context_note += "\n```\n"
        
        return original_content + git_context_note
    
    def _is_relevant_to_patch(self, filepath: str, patch: TaskPatch) -> bool:
        """检查文件是否与patch相关"""
        patch_content_lower = patch.content.lower()
        filename = Path(filepath).name.lower()
        
        # 检查文件名是否在patch中提到
        if filename in patch_content_lower:
            return True
        
        # 检查文件扩展名是否相关
        ext = Path(filepath).suffix.lower()
        if ext:
            # 常见扩展名映射
            ext_mapping = {
                '.py': ['python', '脚本', '代码'],
                '.js': ['javascript', '前端', '代码'],
                '.html': ['html', '网页', '前端'],
                '.css': ['css', '样式', '前端'],
                '.md': ['文档', 'readme', '说明'],
                '.json': ['配置', 'json', '数据'],
                '.yml': ['配置', 'yaml', '部署'],
                '.sql': ['数据库', 'sql', '查询'],
            }
            
            if ext in ext_mapping:
                keywords = ext_mapping[ext]
                for keyword in keywords:
                    if keyword in patch_content_lower:
                        return True
        
        return False


class GitContextUncertaintyAnalyzer:
    """
    Git上下文不确定性分析
    
    分析Git上下文带来的不确定性：
    1. 未提交的修改
    2. 冲突风险
    3. 代码质量风险
    """
    
    def __init__(self, git_provider: GitContextProvider):
        self.git_provider = git_provider
    
    def analyze_git_uncertainties(self, plan_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Git相关的不确定性"""
        git_context = self.git_provider.get_context()
        uncertainties = []
        
        if not git_context.is_git_repo:
            uncertainties.append({
                "source": "git_missing",
                "severity": "low",
                "description": "当前目录不是Git仓库，缺乏版本控制上下文",
                "recommendation": "建议初始化Git仓库以跟踪变更"
            })
            return uncertainties
        
        # 分析未提交的修改
        if git_context.has_modified_files():
            modified_count = len(git_context.get_modified_file_paths())
            severity = "medium" if modified_count < 5 else "high"
            
            uncertainties.append({
                "source": "uncommitted_changes",
                "severity": severity,
                "description": f"有 {modified_count} 个未提交的文件修改",
                "recommendation": "建议提交当前修改后再执行新任务"
            })
        
        # 分析冲突风险
        if git_context.current_branch and git_context.current_branch != 'main':
            uncertainties.append({
                "source": "non_main_branch",
                "severity": "low",
                "description": f"当前在 '{git_context.current_branch}' 分支，不在main分支",
                "recommendation": "确认是否需要合并到main分支"
            })
        
        return uncertainties
    
    def get_relevant_code_context(self, keywords: List[str]) -> Dict[str, Any]:
        """获取与关键词相关的代码上下文"""
        git_context = self.git_provider.get_context()
        result = {
            "relevant_files": [],
            "relevant_commits": [],
            "suggested_edits": []
        }
        
        if not git_context.is_git_repo:
            return result
        
        # 查找相关文件
        for file_change in git_context.file_changes:
            for keyword in keywords:
                if keyword.lower() in file_change.path.lower():
                    result["relevant_files"].append({
                        "path": file_change.path,
                        "type": file_change.display_type,
                        "staged": file_change.staged
                    })
                    break
        
        # 查找相关提交
        result["relevant_commits"] = [
            c.to_dict() for c in git_context.get_relevant_commits(keywords, limit=3)
        ]
        
        return result


def inject_git_context_to_prompt(prompt: str, git_provider: GitContextProvider) -> str:
    """将Git上下文注入到prompt"""
    git_context = git_provider.get_context()
    
    if not git_context.is_git_repo:
        return prompt
    
    git_context_header = "\n" + "="*60 + "\n"
    git_context_header += "[GIT] 上下文信息\n"
    git_context_header += "="*60 + "\n"
    git_context_header += f"仓库: {Path(git_context.repo_root).name}\n"
    git_context_header += f"分支: {git_context.current_branch}\n"
    git_context_header += f"状态: {git_context.status_text}\n"
    
    if git_context.file_changes:
        git_context_header += f"\n[文件] 变更文件 ({len(git_context.file_changes)}个):\n"
        for i, change in enumerate(git_context.file_changes[:5], 1):
            git_context_header += f"  {i}. {change.path} ({change.display_type})"
            if change.staged:
                git_context_header += " [已暂存]"
            git_context_header += "\n"
        
        if len(git_context.file_changes) > 5:
            git_context_header += f"  ... 还有 {len(git_context.file_changes) - 5} 个文件\n"
    
    if git_context.recent_commits:
        git_context_header += f"\n[提交] 最近提交:\n"
        for i, commit in enumerate(git_context.recent_commits[:3], 1):
            time_str = commit.timestamp.strftime("%m-%d %H:%M")
            git_context_header += f"  {i}. [{commit.short_hash}] {commit.message[:50]}... ({time_str})\n"
    
    git_context_header += "\n" + "="*60 + "\n\n"
    
    return git_context_header + prompt


# 集成到TimesFM架构
class GitEnhancedTimesFMAgent:
    """
    Git增强的TimesFM Agent
    """
    
    def __init__(self, base_agent=None):
        self.git_provider = GitContextProvider()
        self.base_agent = base_agent
        self.git_patcher = GitContextAwareTaskPatcher(self.git_provider)
        self.uncertainty_analyzer = GitContextUncertaintyAnalyzer(self.git_provider)
    
    def process_with_git_context(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用Git上下文处理任务"""
        # 注入Git上下文到prompt
        enhanced_prompt = inject_git_context_to_prompt(task, self.git_provider)
        
        # 获取基础结果
        base_result = {}
        if self.base_agent:
            base_result = self.base_agent.process_task(enhanced_prompt, context or {})
        
        # 分析Git不确定性
        git_uncertainties = self.uncertainty_analyzer.analyze_git_uncertainties(
            base_result.get("patching", {})
        )
        
        # 获取相关代码上下文
        keywords = self._extract_keywords_from_task(task)
        code_context = self.uncertainty_analyzer.get_relevant_code_context(keywords)
        
        # 合并结果
        result = {
            **base_result,
            "git_context": {
                "is_git_repo": self.git_provider.get_context().is_git_repo,
                "current_branch": self.git_provider.get_context().current_branch,
                "has_uncommitted_changes": self.git_provider.get_context().has_modified_files(),
                "modified_file_count": len(self.git_provider.get_context().get_modified_file_paths()),
                "uncertainties": git_uncertainties,
                "relevant_code": code_context
            }
        }
        
        # 添加Git相关的建议
        if git_uncertainties:
            recommendations = base_result.get("uncertainty", {}).get("recommended_actions", [])
            for unc in git_uncertainties:
                recommendations.append(f"[Git] {unc['recommendation']}")
            if "uncertainty" in result:
                result["uncertainty"]["recommended_actions"] = recommendations
        
        return result
    
    def _extract_keywords_from_task(self, task: str) -> List[str]:
        """从任务中提取关键词"""
        # 简单的关键词提取
        keywords = []
        common_tech_keywords = [
            "python", "代码", "函数", "类", "模块", "文件",
            "前端", "后端", "数据库", "api", "接口",
            "配置", "部署", "测试", "文档"
        ]
        
        task_lower = task.lower()
        for keyword in common_tech_keywords:
            if keyword in task_lower:
                keywords.append(keyword)
        
        # 添加文件名扩展名
        import re
        file_patterns = r'(\w+\.(py|js|ts|html|css|md|json|yml|yaml|sql))'
        matches = re.findall(file_patterns, task, re.IGNORECASE)
        for match in matches:
            keywords.append(match[0])
        
        return list(set(keywords))  # 去重


# 测试函数
def test_git_context_integration():
    """测试Git上下文集成"""
    print("="*70)
    print("Git Context Integration Test")
    print("="*70)
    
    provider = GitContextProvider()
    context = provider.get_context()
    
    print(f"\nGit仓库: {'是' if context.is_git_repo else '否'}")
    if context.is_git_repo:
        print(f"仓库根目录: {context.repo_root}")
        print(f"当前分支: {context.current_branch}")
        print(f"状态: {context.status_text}")
        print(f"是否干净: {'是' if context.is_clean else '否'}")
        
        if context.file_changes:
            print(f"\n变更文件 ({len(context.file_changes)}个):")
            for change in context.file_changes[:3]:
                print(f"  - {change.path} ({change.display_type})")
        
        if context.recent_commits:
            print(f"\n最近提交:")
            for commit in context.recent_commits[:2]:
                time_str = commit.timestamp.strftime("%m-%d %H:%M")
                print(f"  - [{commit.short_hash}] {commit.message[:40]}... ({time_str})")
    
    # 测试prompt注入
    test_prompt = "请帮我分析当前的代码结构"
    injected = inject_git_context_to_prompt(test_prompt, provider)
    
    print(f"\n\nPrompt注入测试:")
    print("-"*40)
    print(injected[:200] + "..." if len(injected) > 200 else injected)
    
    # 测试不确定性分析
    analyzer = GitContextUncertaintyAnalyzer(provider)
    uncertainties = analyzer.analyze_git_uncertainties({})
    
    if uncertainties:
        print(f"\n\nGit不确定性分析:")
        for unc in uncertainties:
            print(f"  - [{unc['source']}] {unc['description']}")
    
    print("\n" + "="*70)
    print("Git Context Integration Test Completed!")
    print("="*70)


if __name__ == "__main__":
    test_git_context_integration()