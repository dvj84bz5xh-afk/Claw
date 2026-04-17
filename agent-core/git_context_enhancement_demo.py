"""
Git上下文增强演示
展示如何在实际任务中使用Git上下文增强功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from git_context_integration import (
    GitContextProvider, 
    GitContextAwareTaskPatcher,
    GitContextUncertaintyAnalyzer,
    inject_git_context_to_prompt,
    GitEnhancedTimesFMAgent
)

class SimpleDemoAgent:
    """简单演示Agent"""
    
    def process_task(self, prompt: str, context: dict) -> dict:
        """处理任务的基础方法"""
        return {
            "task": prompt,
            "status": "processed",
            "steps": ["分析需求", "制定计划", "执行"],
            "confidence": 0.8
        }


def demo_basic_git_context():
    """基础Git上下文演示"""
    print("="*70)
    print("基础Git上下文演示")
    print("="*70)
    
    # 1. 创建Git上下文提供者
    provider = GitContextProvider()
    context = provider.get_context()
    
    print(f"\n1. 基础Git上下文:")
    print(f"   是否为Git仓库: {'是' if context.is_git_repo else '否'}")
    print(f"   仓库根目录: {context.repo_root}")
    print(f"   当前分支: {context.current_branch}")
    print(f"   状态: {context.status_text}")
    print(f"   是否干净: {'是' if context.is_clean else '否'}")
    
    # 2. 文件变更详情
    if context.file_changes:
        print(f"\n2. 文件变更详情 ({len(context.file_changes)}个):")
        categories = {}
        for change in context.file_changes:
            cat = change.display_type
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"   {cat}: {count}个文件")
        
        # 显示前3个文件
        print(f"\n   前3个变更文件:")
        for i, change in enumerate(context.file_changes[:3], 1):
            print(f"   {i}. {change.path}")
    
    # 3. 最近提交
    if context.recent_commits:
        print(f"\n3. 最近提交:")
        for commit in context.recent_commits[:2]:
            time_str = commit.timestamp.strftime("%m-%d %H:%M")
            print(f"   [{commit.short_hash}] {commit.message[:60]}... ({time_str})")
    
    return context


def demo_prompt_injection():
    """Prompt注入演示"""
    print(f"\n\n" + "="*70)
    print("Prompt注入演示")
    print("="*70)
    
    provider = GitContextProvider()
    
    # 原始prompt
    original_prompt = """请帮我完成以下任务：
1. 优化agent-core模块中的代码结构
2. 添加必要的测试用例
3. 编写文档说明
"""
    
    print(f"\n1. 原始Prompt:")
    print(original_prompt)
    
    # 注入Git上下文后的prompt
    enhanced_prompt = inject_git_context_to_prompt(original_prompt, provider)
    
    print(f"\n2. 增强后的Prompt:")
    print(enhanced_prompt[:300] + "..." if len(enhanced_prompt) > 300 else enhanced_prompt)


def demo_uncertainty_analysis():
    """不确定性分析演示"""
    print(f"\n\n" + "="*70)
    print("Git不确定性分析演示")
    print("="*70)
    
    provider = GitContextProvider()
    analyzer = GitContextUncertaintyAnalyzer(provider)
    
    # 分析Git相关的不确定性
    uncertainties = analyzer.analyze_git_uncertainties({
        "task": "代码重构",
        "scope": ["agent-core/*.py"],
        "deadline": "2026-04-18"
    })
    
    print(f"\nGit不确定性分析结果:")
    
    if not uncertainties:
        print("   没有发现明显的Git相关不确定性")
    else:
        for i, unc in enumerate(uncertainties, 1):
            print(f"\n   {i}. [{unc['source']}]")
            print(f"      描述: {unc['description']}")
            print(f"      严重程度: {unc['severity']}")
            print(f"      建议: {unc['recommendation']}")
    
    # 获取相关代码上下文
    keywords = ["python", "agent", "core"]
    code_context = analyzer.get_relevant_code_context(keywords)
    
    if code_context.get("relevant_files") or code_context.get("relevant_commits"):
        print(f"\n相关代码上下文:")
        
        if code_context["relevant_files"]:
            print(f"   相关文件:")
            for file_info in code_context["relevant_files"][:3]:
                print(f"     - {file_info['path']} ({file_info['type']})")
        
        if code_context["relevant_commits"]:
            print(f"   相关提交:")
            for commit_info in code_context["relevant_commits"][:2]:
                print(f"     - [{commit_info['short_hash']}] {commit_info['message'][:50]}...")


def demo_task_patching_with_git():
    """任务Patching与Git集成演示"""
    print(f"\n\n" + "="*70)
    print("任务Patching与Git集成演示")
    print("="*70)
    
    # 模拟任务patches
    class MockTaskPatch:
        def __init__(self, index, content, task_type, priority):
            self.index = index
            self.content = content
            self.task_type = task_type
            self.priority = priority
    
    patches = [
        MockTaskPatch(
            index=1,
            content="优化config_system.py的配置加载逻辑",
            task_type="code_optimization",
            priority=1
        ),
        MockTaskPatch(
            index=2,
            content="为uncertainty_quantifier.py添加单元测试",
            task_type="testing",
            priority=2
        ),
        MockTaskPatch(
            index=3,
            content="编写git_context_integration.md文档",
            task_type="documentation",
            priority=3
        ),
    ]
    
    provider = GitContextProvider()
    git_patcher = GitContextAwareTaskPatcher(provider)
    
    print(f"\n1. 原始任务Patches:")
    for patch in patches:
        print(f"   Patch {patch.index}: {patch.content}")
    
    print(f"\n2. Git上下文增强后:")
    
    # 检查Git上下文
    context = provider.get_context()
    if not context.is_git_repo or context.is_clean:
        print("   当前没有修改的文件，跳过Git上下文增强")
        return
    
    # 演示增强逻辑
    print(f"   检测到{len(context.file_changes)}个文件变更")
    
    # 查找与patches相关的文件
    for patch in patches:
        related_files = []
        for file_change in context.file_changes[:5]:  # 只检查前5个文件
            patch_content_lower = patch.content.lower()
            filepath_lower = file_change.path.lower()
            
            # 简单的相关性检查
            if Path(file_change.path).name.lower() in patch_content_lower:
                related_files.append(file_change)
        
        if related_files:
            print(f"\n   Patch {patch.index} 相关文件:")
            for file_change in related_files:
                print(f"     - {file_change.path} ({file_change.display_type})")


def demo_full_integration():
    """完整集成演示"""
    print(f"\n\n" + "="*70)
    print("完整Git上下文增强集成演示")
    print("="*70)
    
    # 创建基础agent
    base_agent = SimpleDemoAgent()
    
    # 创建Git增强的agent
    git_enhanced_agent = GitEnhancedTimesFMAgent(base_agent)
    
    # 测试任务
    test_tasks = [
        "请帮我优化agent-core模块的代码结构",
        "分析当前项目中存在的技术债务",
        "为TimesFM集成编写文档"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. 任务: {task}")
        print("-"*50)
        
        try:
            # 使用Git上下文处理任务
            result = git_enhanced_agent.process_with_git_context(task)
            
            # 显示Git上下文部分
            if "git_context" in result:
                git_info = result["git_context"]
                print(f"   Git上下文:")
                print(f"     - 是否Git仓库: {git_info.get('is_git_repo', '未知')}")
                print(f"     - 当前分支: {git_info.get('current_branch', '未知')}")
                print(f"     - 有未提交修改: {git_info.get('has_uncommitted_changes', False)}")
                print(f"     - 修改文件数: {git_info.get('modified_file_count', 0)}")
                
                uncertainties = git_info.get("uncertainties", [])
                if uncertainties:
                    print(f"     - Git不确定性: {len(uncertainties)}项")
            
            # 显示相关代码上下文
            if "git_context" in result and result["git_context"].get("relevant_code"):
                code_context = result["git_context"]["relevant_code"]
                if code_context.get("relevant_files"):
                    print(f"   - 相关代码文件: {len(code_context['relevant_files'])}个")
        
        except Exception as e:
            print(f"   处理出错: {str(e)}")


def demo_workflow_recommendations():
    """工作流程建议演示"""
    print(f"\n\n" + "="*70)
    print("Git工作流程建议演示")
    print("="*70)
    
    provider = GitContextProvider()
    context = provider.get_context()
    
    print(f"\n基于当前Git状态的工作流程建议:")
    
    if not context.is_git_repo:
        print("1. 当前目录不是Git仓库")
        print("   建议: git init 初始化仓库")
        return
    
    # 检查状态并给出建议
    recommendations = []
    
    # 检查未跟踪文件
    untracked = [f for f in context.file_changes if f.change_type == GitChangeType.UNTRACKED]
    if untracked:
        recommendations.append({
            "type": "untracked_files",
            "description": f"有{len(untracked)}个未跟踪文件",
            "actions": [
                "git add . 添加所有文件到暂存区",
                "或 git add <file> 选择性添加重要文件",
                "git status 查看具体文件状态"
            ]
        })
    
    # 检查修改的文件
    modified = [f for f in context.file_changes if f.change_type == GitChangeType.MODIFIED]
    if modified:
        modifications = [f.path for f in modified if not f.staged]
        staged = [f.path for f in modified if f.staged]
        
        if modifications:
            recommendations.append({
                "type": "unstaged_modifications",
                "description": f"有{len(modifications)}个已修改但未暂存的文件",
                "actions": [
                    "git diff 查看具体修改内容",
                    "git add <file> 将重要修改添加到暂存区",
                    "git commit -m 'message' 提交已暂存的修改"
                ]
            })
        
        if staged:
            recommendations.append({
                "type": "staged_changes",
                "description": f"有{len(staged)}个已暂存的修改",
                "actions": [
                    "git commit -m 'descriptive message' 提交修改",
                    "git commit --amend 修改最近一次提交（如需修改）",
                    "git reset HEAD <file> 取消暂存"
                ]
            })
    
    # 检查分支状态
    if context.current_branch:
        if context.current_branch != "main":
            recommendations.append({
                "type": "feature_branch",
                "description": f"当前在'{context.current_branch}'分支",
                "actions": [
                    "git status 确认修改状态",
                    "git commit -m 'complete feature' 提交当前功能",
                    "git checkout main 切换回主分支",
                    "git merge {context.current_branch} 合并功能到主分支"
                ]
            })
    
    # 显示建议
    if not recommendations:
        print("   当前Git状态良好，无需特殊操作")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['type']}] {rec['description']}")
            print("   建议操作:")
            for action in rec["actions"]:
                print(f"     - {action}")


from pathlib import Path
from git_context_integration import GitChangeType

def main():
    """主演示函数"""
    print("Git上下文增强演示套件")
    print("="*70)
    
    try:
        # 1. 基础Git上下文演示
        demo_basic_git_context()
        
        # 2. Prompt注入演示
        demo_prompt_injection()
        
        # 3. 不确定性分析演示
        demo_uncertainty_analysis()
        
        # 4. 任务Patching演示
        demo_task_patching_with_git()
        
        # 5. 工作流程建议
        demo_workflow_recommendations()
        
        # 6. 完整集成演示
        demo_full_integration()
        
        print(f"\n\n" + "="*70)
        print("演示完成!")
        print("="*70)
        print("\n总结:")
        print("1. Git上下文增强可以让AI智能体:")
        print("   - 了解当前的Git仓库状态")
        print("   - 识别相关的代码文件")
        print("   - 提供上下文感知的建议")
        print("   - 减少重复工作和冲突")
        print("\n2. 主要功能模块:")
        print("   - GitContextProvider: 获取Git状态信息")
        print("   - GitContextAwareTaskPatcher: 增强任务patches")
        print("   - GitContextUncertaintyAnalyzer: 分析Git风险")
        print("   - GitEnhancedTimesFMAgent: 完整集成Agent")
        
    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()