"""
Phase 3.2: Git Context Enhancement Module

增强的 Git 上下文感知系统
- 自动检测 Git 状态
- 最近提交信息注入
- 修改文件列表
- 分支信息感知
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json
import re
from enum import Enum


class GitStatus(Enum):
    """Git 仓库状态"""
    CLEAN = "clean"
    MODIFIED = "modified"
    STAGED = "staged"
    UNTRACKED = "untracked"
    MERGING = "merging"
    REBASING = "rebasing"


@dataclass
class GitCommit:
    """Git 提交信息"""
    hash: str
    short_hash: str
    message: str
    author: str
    email: str
    timestamp: datetime
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    
    @classmethod
    def from_log_line(cls, line: str) -> Optional['GitCommit']:
        """从 git log 行解析提交信息"""
        # 格式: hash|short_hash|message|author|email|timestamp
        parts = line.split('|', 5)
        if len(parts) < 6:
            return None
        
        try:
            timestamp = datetime.fromtimestamp(int(parts[5]))
        except:
            timestamp = datetime.now()
        
        return cls(
            hash=parts[0],
            short_hash=parts[1],
            message=parts[2],
            author=parts[3],
            email=parts[4],
            timestamp=timestamp
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash,
            "short_hash": self.short_hash,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions
        }


@dataclass
class GitFileChange:
    """Git 文件变更"""
    path: str
    status: str  # M (modified), A (added), D (deleted), R (renamed), ?? (untracked)
    staged: bool = False
    
    @property
    def status_text(self) -> str:
        status_map = {
            'M': '修改',
            'A': '新增',
            'D': '删除',
            'R': '重命名',
            '??': '未跟踪',
            'C': '复制'
        }
        return status_map.get(self.status, self.status)


@dataclass
class GitBranch:
    """Git 分支信息"""
    name: str
    is_current: bool = False
    is_remote: bool = False
    upstream: Optional[str] = None
    ahead: int = 0
    behind: int = 0


@dataclass
class GitContext:
    """完整的 Git 上下文"""
    # 仓库基本信息
    is_git_repo: bool = False
    repo_root: Optional[str] = None
    repo_name: Optional[str] = None
    
    # 当前分支
    current_branch: Optional[str] = None
    
    # 状态
    status: GitStatus = GitStatus.CLEAN
    status_summary: str = ""
    
    # 变更文件
    modified_files: List[GitFileChange] = field(default_factory=list)
    staged_files: List[GitFileChange] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    
    # 最近提交
    recent_commits: List[GitCommit] = field(default_factory=list)
    
    # 分支信息
    local_branches: List[GitBranch] = field(default_factory=list)
    remote_branches: List[GitBranch] = field(default_factory=list)
    
    # 统计
    total_commits: int = 0
    contributors: List[str] = field(default_factory=list)
    
    # 时间戳
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_git_repo": self.is_git_repo,
            "repo_root": self.repo_root,
            "repo_name": self.repo_name,
            "current_branch": self.current_branch,
            "status": self.status.value,
            "status_summary": self.status_summary,
            "modified_files": [
                {"path": f.path, "status": f.status, "staged": f.staged}
                for f in self.modified_files
            ],
            "staged_files": [
                {"path": f.path, "status": f.status}
                for f in self.staged_files
            ],
            "untracked_files": self.untracked_files,
            "recent_commits": [c.to_dict() for c in self.recent_commits[:5]],
            "branch_count": len(self.local_branches),
            "generated_at": self.generated_at.isoformat()
        }
    
    def to_prompt_context(self) -> str:
        """转换为适合注入到 Prompt 的上下文文本"""
        if not self.is_git_repo:
            return ""
        
        lines = [
            "## Git 上下文",
            f"- 当前分支: {self.current_branch or '未知'}",
            f"- 仓库状态: {self.status_summary or '干净'}",
        ]
        
        # 修改的文件
        if self.modified_files:
            lines.append(f"- 修改文件: {len(self.modified_files)} 个")
            for f in self.modified_files[:5]:
                lines.append(f"  - {f.path} ({f.status_text})")
            if len(self.modified_files) > 5:
                lines.append(f"  ... 还有 {len(self.modified_files) - 5} 个文件")
        
        # 最近提交
        if self.recent_commits:
            lines.append("- 最近提交:")
            for commit in self.recent_commits[:3]:
                time_str = commit.timestamp.strftime("%m-%d %H:%M")
                lines.append(f"  - [{commit.short_hash}] {commit.message[:50]} ({time_str})")
        
        return "\n".join(lines)


class GitContextProvider:
    """
    Git 上下文提供者
    
    自动检测和收集 Git 仓库信息
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self._git_root: Optional[Path] = None
    
    def _run_git(self, args: List[str], cwd: Optional[Path] = None) -> Tuple[str, str, int]:
        """运行 git 命令"""
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=cwd or self.workspace_path,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), -1
    
    def find_git_root(self) -> Optional[Path]:
        """查找 Git 仓库根目录"""
        if self._git_root:
            return self._git_root
        
        stdout, _, code = self._run_git(['rev-parse', '--show-toplevel'])
        if code == 0:
            self._git_root = Path(stdout.strip())
            return self._git_root
        return None
    
    def is_git_repository(self) -> bool:
        """检查当前目录是否为 Git 仓库"""
        return self.find_git_root() is not None
    
    def get_current_branch(self) -> Optional[str]:
        """获取当前分支名称"""
        stdout, _, code = self._run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
        if code == 0:
            branch = stdout.strip()
            if branch != 'HEAD':
                return branch
        
        # 可能是 detached HEAD，尝试获取最近的 tag 或 commit
        stdout, _, code = self._run_git(['describe', '--tags', '--always'])
        if code == 0:
            return f"detached ({stdout.strip()})"
        return None
    
    def get_status(self) -> Tuple[GitStatus, str]:
        """获取仓库状态"""
        stdout, _, code = self._run_git(['status', '--porcelain'])
        if code != 0:
            return GitStatus.CLEAN, "无法获取状态"
        
        lines = [l for l in stdout.strip().split('\n') if l]
        
        if not lines:
            return GitStatus.CLEAN, "干净的工作区"
        
        # 解析状态
        staged = any(l[0] in 'MADRC' for l in lines if len(l) > 1)
        modified = any(l[1] in 'MAD' for l in lines if len(l) > 1)
        untracked = any(l.startswith('??') for l in lines)
        
        if staged and modified:
            return GitStatus.MODIFIED, f"已暂存 {sum(1 for l in lines if l[0] != ' ')} 个, 未暂存修改 {sum(1 for l in lines if l[1] != ' ')} 个"
        elif staged:
            return GitStatus.STAGED, f"已暂存 {len(lines)} 个文件"
        elif modified:
            return GitStatus.MODIFIED, f"有 {len(lines)} 个文件被修改"
        elif untracked:
            return GitStatus.UNTRACKED, f"有 {len(lines)} 个未跟踪文件"
        
        return GitStatus.CLEAN, "干净"
    
    def get_file_changes(self) -> Tuple[List[GitFileChange], List[GitFileChange], List[str]]:
        """获取文件变更列表"""
        stdout, _, code = self._run_git(['status', '--porcelain'])
        if code != 0:
            return [], [], []
        
        modified = []
        staged = []
        untracked = []
        
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            
            if line.startswith('??'):
                untracked.append(line[3:])
            elif len(line) >= 3:
                index_status = line[0]
                worktree_status = line[1]
                file_path = line[3:]
                
                # 解析重命名
                if ' -> ' in file_path:
                    file_path = file_path.split(' -> ')[1]
                
                if index_status != ' ':
                    staged.append(GitFileChange(path=file_path, status=index_status, staged=True))
                
                if worktree_status != ' ':
                    modified.append(GitFileChange(path=file_path, status=worktree_status, staged=False))
        
        return modified, staged, untracked
    
    def get_recent_commits(self, count: int = 10) -> List[GitCommit]:
        """获取最近提交"""
        # 使用自定义格式输出
        format_str = '%H|%h|%s|%an|%ae|%at'
        stdout, _, code = self._run_git([
            'log', f'-{count}',
            f'--pretty=format:{format_str}'
        ])
        
        if code != 0:
            return []
        
        commits = []
        for line in stdout.strip().split('\n'):
            commit = GitCommit.from_log_line(line)
            if commit:
                # 获取统计信息
                stat_stdout, _, _ = self._run_git([
                    'show', '--stat', '--format=', commit.hash
                ])
                if stat_stdout:
                    # 解析统计
                    lines = stat_stdout.strip().split('\n')
                    if lines:
                        last_line = lines[-1]
                        # 格式: " 3 files changed, 25 insertions(+), 10 deletions(-)"
                        match = re.search(r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?', last_line)
                        if match:
                            commit.files_changed = int(match.group(1) or 0)
                            commit.insertions = int(match.group(2) or 0)
                            commit.deletions = int(match.group(3) or 0)
                
                commits.append(commit)
        
        return commits
    
    def get_branches(self) -> Tuple[List[GitBranch], List[GitBranch]]:
        """获取分支列表"""
        local_branches = []
        remote_branches = []
        
        # 本地分支
        stdout, _, code = self._run_git(['branch', '-vv'])
        if code == 0:
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                
                is_current = line.startswith('*')
                line = line[2:] if is_current else line[2:]
                parts = line.split()
                
                if parts:
                    branch_name = parts[0]
                    upstream = None
                    ahead = behind = 0
                    
                    # 解析 upstream 信息
                    if len(parts) > 1 and parts[1].startswith('['):
                        upstream_info = parts[1][1:-1]  # 去掉 []
                        upstream = upstream_info
                        # 解析 ahead/behind
                        match = re.search(r'ahead (\d+)', upstream_info)
                        if match:
                            ahead = int(match.group(1))
                        match = re.search(r'behind (\d+)', upstream_info)
                        if match:
                            behind = int(match.group(1))
                    
                    local_branches.append(GitBranch(
                        name=branch_name,
                        is_current=is_current,
                        upstream=upstream,
                        ahead=ahead,
                        behind=behind
                    ))
        
        # 远程分支
        stdout, _, code = self._run_git(['branch', '-r'])
        if code == 0:
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                branch_name = line.strip()
                if 'HEAD' not in branch_name:
                    remote_branches.append(GitBranch(
                        name=branch_name,
                        is_remote=True
                    ))
        
        return local_branches, remote_branches
    
    def get_total_commits(self) -> int:
        """获取总提交数"""
        stdout, _, code = self._run_git(['rev-list', '--count', 'HEAD'])
        if code == 0:
            try:
                return int(stdout.strip())
            except:
                pass
        return 0
    
    def get_contributors(self) -> List[str]:
        """获取贡献者列表"""
        stdout, _, code = self._run_git([
            'log', '--format=%an', '--all', '--no-merges'
        ])
        if code == 0:
            contributors = {}
            for name in stdout.strip().split('\n'):
                if name:
                    contributors[name] = contributors.get(name, 0) + 1
            # 按提交数排序
            return [name for name, _ in sorted(contributors.items(), key=lambda x: -x[1])[:10]]
        return []
    
    def get_context(self) -> GitContext:
        """获取完整的 Git 上下文"""
        context = GitContext()
        
        # 检查是否为 Git 仓库
        git_root = self.find_git_root()
        if not git_root:
            context.is_git_repo = False
            return context
        
        # 基本信息
        context.is_git_repo = True
        context.repo_root = str(git_root)
        context.repo_name = git_root.name
        
        # 当前分支
        context.current_branch = self.get_current_branch()
        
        # 状态
        context.status, context.status_summary = self.get_status()
        
        # 文件变更
        context.modified_files, context.staged_files, context.untracked_files = \
            self.get_file_changes()
        
        # 最近提交
        context.recent_commits = self.get_recent_commits(10)
        
        # 分支
        context.local_branches, context.remote_branches = self.get_branches()
        
        # 统计
        context.total_commits = self.get_total_commits()
        context.contributors = self.get_contributors()
        
        return context


class GitContextInjector:
    """
    Git 上下文注入器
    
    将 Git 上下文自动注入到 Prompt
    """
    
    def __init__(self, provider: GitContextProvider):
        self.provider = provider
        self._last_context: Optional[GitContext] = None
        self._last_update: Optional[datetime] = None
        self._cache_ttl = timedelta(seconds=30)  # 缓存30秒
    
    def get_context(self, force_refresh: bool = False) -> GitContext:
        """获取上下文（带缓存）"""
        now = datetime.now()
        
        if (not force_refresh and 
            self._last_context and 
            self._last_update and 
            now - self._last_update < self._cache_ttl):
            return self._last_context
        
        context = self.provider.get_context()
        self._last_context = context
        self._last_update = now
        return context
    
    def inject_to_prompt(self, prompt: str, force_refresh: bool = False) -> str:
        """将 Git 上下文注入到 Prompt"""
        context = self.get_context(force_refresh)
        
        if not context.is_git_repo:
            return prompt
        
        git_context_text = context.to_prompt_context()
        
        # 在 Prompt 开头注入 Git 上下文
        return f"{git_context_text}\n\n{prompt}"
    
    def get_summary(self) -> str:
        """获取 Git 上下文摘要"""
        context = self.get_context()
        
        if not context.is_git_repo:
            return "不在 Git 仓库中"
        
        lines = [
            f"📁 仓库: {context.repo_name}",
            f"🌿 分支: {context.current_branch}",
            f"📊 状态: {context.status_summary}",
        ]
        
        if context.modified_files:
            lines.append(f"📝 修改: {len(context.modified_files)} 个文件")
        if context.staged_files:
            lines.append(f"✅ 暂存: {len(context.staged_files)} 个文件")
        
        lines.append(f"💾 提交: {context.total_commits} 个")
        
        return " | ".join(lines)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3.2: Git Context Enhancement Test")
    print("=" * 60)
    
    # 创建提供者
    provider = GitContextProvider()
    
    # 检查是否为 Git 仓库
    if not provider.is_git_repository():
        print("\n当前目录不是 Git 仓库")
        print("切换到正确的目录或使用示例数据测试")
    else:
        print(f"\n[OK] Git 仓库根目录: {provider.find_git_root()}")
        
        # 获取完整上下文
        context = provider.get_context()
        
        print(f"\n仓库名称: {context.repo_name}")
        print(f"当前分支: {context.current_branch}")
        print(f"仓库状态: {context.status_summary}")
        
        # 修改的文件
        if context.modified_files:
            print(f"\n修改的文件 ({len(context.modified_files)} 个):")
            for f in context.modified_files[:5]:
                print(f"  - {f.path} ({f.status_text})")
        
        # 暂存的文件
        if context.staged_files:
            print(f"\n暂存的文件 ({len(context.staged_files)} 个):")
            for f in context.staged_files[:5]:
                print(f"  - {f.path} ({f.status_text})")
        
        # 最近提交
        if context.recent_commits:
            print(f"\n最近提交:")
            for commit in context.recent_commits[:5]:
                time_str = commit.timestamp.strftime("%m-%d %H:%M")
                stats = f"+{commit.insertions}/-{commit.deletions}" if commit.insertions or commit.deletions else ""
                print(f"  [{commit.short_hash}] {commit.message[:40]}... ({time_str}) {stats}")
        
        # 分支
        print(f"\n本地分支: {len(context.local_branches)} 个")
        for branch in context.local_branches[:5]:
            current = "* " if branch.is_current else "  "
            ahead_behind = ""
            if branch.ahead:
                ahead_behind += f" ↑{branch.ahead}"
            if branch.behind:
                ahead_behind += f" ↓{branch.behind}"
            print(f"  {current}{branch.name}{ahead_behind}")
        
        # 统计
        print(f"\n总提交数: {context.total_commits}")
        print(f"主要贡献者: {', '.join(context.contributors[:3])}")
        
        # 测试注入器
        print("\n" + "-" * 60)
        print("测试 Git 上下文注入器:")
        print("-" * 60)
        
        injector = GitContextInjector(provider)
        
        # 获取摘要
        print(f"\n摘要: {injector.get_summary()}")
        
        # 测试注入
        test_prompt = "请帮我分析代码"
        injected = injector.inject_to_prompt(test_prompt)
        print(f"\n注入后的 Prompt 预览:\n{injected[:500]}...")
    
    print("\n" + "=" * 60)
    print("Git Context Enhancement Test Completed!")
    print("=" * 60)
