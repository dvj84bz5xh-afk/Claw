"""
Git上下文增强实战场景演示
在实际开发场景中应用Git上下文增强
"""

import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from git_context_integration import (
    GitContextProvider,
    GitContextAwareTaskPatcher,
    GitContextUncertaintyAnalyzer,
    inject_git_context_to_prompt,
    GitEnhancedTimesFMAgent
)


class ScenarioManager:
    """场景管理器"""
    
    def __init__(self):
        self.provider = GitContextProvider()
        self.scenarios = {
            "code_review": self.scenario_code_review,
            "feature_development": self.scenario_feature_development,
            "bug_fixing": self.scenario_bug_fixing,
            "documentation": self.scenario_documentation,
            "refactoring": self.scenario_refactoring
        }
    
    def run_scenario(self, scenario_name: str, **kwargs):
        """运行指定场景"""
        if scenario_name in self.scenarios:
            print(f"\n{'='*70}")
            print(f"场景: {scenario_name}")
            print(f"{'='*70}")
            return self.scenarios[scenario_name](**kwargs)
        else:
            print(f"未知场景: {scenario_name}")
            return None
    
    def scenario_code_review(self, file_path: str = None):
        """场景1: 代码审查"""
        print("场景描述: AI协助进行代码审查，需要了解当前Git状态")
        
        # 获取Git上下文
        git_context = self.provider.get_context()
        
        if not git_context.is_git_repo:
            print("   [警告] 当前目录不是Git仓库，无法进行代码审查")
            return
        
        # 构建审查请求
        review_request = f"""
请帮我审查以下代码：
"""
        
        # 如果指定了文件，添加文件上下文
        if file_path:
            content = self.provider.get_file_content(file_path)
            if content:
                review_request += f"""
文件: {file_path}
内容预览:
```
{content[:200]}...
```
"""
        
        # 自动检测相关修改
        if git_context.file_changes:
            relevant_changes = []
            for change in git_context.file_changes:
                if change.change_type in ["modified", "added"]:
                    # 只关注代码文件
                    if change.path.endswith(('.py', '.js', '.ts', '.java')):
                        relevant_changes.append(change)
            
            if relevant_changes:
                review_request += f"\n当前有 {len(relevant_changes)} 个代码文件修改：\n"
                for change in relevant_changes[:3]:
                    review_request += f"- {change.path} ({change.display_type})\n"
        
        # 注入Git上下文
        enhanced_review = inject_git_context_to_prompt(review_request, self.provider)
        
        # 分析Git不确定性
        analyzer = GitContextUncertaintyAnalyzer(self.provider)
        uncertainties = analyzer.analyze_git_uncertainties({
            "task": "code_review",
            "file": file_path
        })
        
        # 输出结果
        print(f"\n1. Git状态:")
        print(f"   分支: {git_context.current_branch}")
        print(f"   状态: {git_context.status_text}")
        
        print(f"\n2. 审查建议:")
        if uncertainties:
            print(f"   发现 {len(uncertainties)} 个Git相关注意事项:")
            for unc in uncertainties:
                print(f"   [警告] {unc['description']}")
                print(f"     建议: {unc['recommendation']}")
        else:
            print("   当前Git状态良好，可以直接进行代码审查")
        
        print(f"\n3. 增强后的审查请求:")
        print(enhanced_review[:300] + "..." if len(enhanced_review) > 300 else enhanced_review)
        
        return {
            "scenario": "code_review",
            "git_context": {
                "branch": git_context.current_branch,
                "status": git_context.status_text,
                "is_clean": git_context.is_clean
            },
            "uncertainties": uncertainties,
            "enhanced_request": enhanced_review
        }
    
    def scenario_feature_development(self, feature_name: str = "新功能"):
        """场景2: 功能开发"""
        print(f"场景描述: 开发新功能 '{feature_name}'，需要了解项目当前状态")
        
        git_context = self.provider.get_context()
        
        if not git_context.is_git_repo:
            print("   [警告] 当前目录不是Git仓库，建议先初始化Git")
            return
        
        # 获取相关代码上下文
        analyzer = GitContextUncertaintyAnalyzer(self.provider)
        code_context = analyzer.get_relevant_code_context(["python", "feature"])
        
        # 构建开发指导
        guidance = f"""
# 功能开发指导: {feature_name}

## 当前项目状态
"""
        
        if git_context.current_branch:
            guidance += f"- 当前分支: {git_context.current_branch}\n"
        
        if git_context.status_text:
            guidance += f"- 工作区状态: {git_context.status_text}\n"
        
        if git_context.recent_commits:
            guidance += f"- 最近提交: {len(git_context.recent_commits)}个\n"
        
        guidance += f"""
## 建议工作流程
"""
        
        # 根据Git状态给出不同的建议
        if git_context.is_clean:
            guidance += f"""
1. 创建功能分支:
   git checkout -b feature/{feature_name.lower().replace(' ', '-')}

2. 开始开发:
   # 编写代码...

3. 提交功能:
   git add .
   git commit -m "feat: add {feature_name}"

4. 合并到主分支:
   git checkout main
   git merge feature/{feature_name.lower().replace(' ', '-')}
"""
        else:
            guidance += f"""
1. 先处理当前修改:
   - git status 查看当前状态
   - git stash 暂存修改（如果需要）
   - git commit -m "..." 提交当前修改

2. 创建功能分支:
   git checkout -b feature/{feature_name.lower().replace(' ', '-')}

3. 开始开发...
"""
        
        # 输出结果
        print(f"\n1. 项目状态:")
        print(f"   分支: {git_context.current_branch}")
        print(f"   是否干净: {'是' if git_context.is_clean else '否'}")
        
        print(f"\n2. 相关代码上下文:")
        if code_context.get("relevant_files"):
            print(f"   发现 {len(code_context['relevant_files'])} 个相关文件")
            for file_info in code_context["relevant_files"][:3]:
                print(f"   - {file_info['path']}")
        
        print(f"\n3. 开发指导摘要:")
        print(guidance[:400] + "..." if len(guidance) > 400 else guidance)
        
        return {
            "scenario": "feature_development",
            "feature_name": feature_name,
            "git_state": {
                "is_clean": git_context.is_clean,
                "current_branch": git_context.current_branch
            },
            "guidance": guidance,
            "relevant_files": code_context.get("relevant_files", [])
        }
    
    def scenario_bug_fixing(self, bug_description: str = "未知错误"):
        """场景3: 缺陷修复"""
        print(f"场景描述: 修复Bug - {bug_description}")
        
        git_context = self.provider.get_context()
        
        if not git_context.is_git_repo:
            print("   [警告] 当前目录不是Git仓库")
            return
        
        # 分析不确定性
        analyzer = GitContextUncertaintyAnalyzer(self.provider)
        uncertainties = analyzer.analyze_git_uncertainties({
            "task": "bug_fixing",
            "description": bug_description
        })
        
        # 构建修复指导
        guidance = f"""
# Bug修复指导

## Bug描述
{bug_description}

## 当前Git状态
- 分支: {git_context.current_branch}
- 状态: {git_context.status_text}
"""
        
        # 根据状态给出不同建议
        if not git_context.is_clean:
            guidance += f"""
## [警告] 注意事项
当前工作区有未提交的修改，建议:
"""
            if uncertainties:
                for unc in uncertainties:
                    guidance += f"- {unc['recommendation']}\n"
            
            guidance += f"""
## 建议工作流程
1. 暂存或提交当前修改:
   git add .
   git commit -m "WIP: current changes before bug fix"
   
2. 创建修复分支:
   git checkout -b bugfix/{bug_description[:20].lower().replace(' ', '-')}
   
3. 修复Bug并测试
   
4. 提交修复:
   git add .
   git commit -m "fix: {bug_description[:50]}"
   
5. 合并到当前分支:
   git checkout {git_context.current_branch}
   git merge bugfix/{bug_description[:20].lower().replace(' ', '-')}
"""
        else:
            guidance += f"""
## 建议工作流程
1. 创建修复分支:
   git checkout -b bugfix/{bug_description[:20].lower().replace(' ', '-')}
   
2. 修复Bug并测试
   
3. 提交修复:
   git add .
   git commit -m "fix: {bug_description[:50]}"
   
4. 合并到主分支:
   git checkout main
   git merge bugfix/{bug_description[:20].lower().replace(' ', '-')}
"""
        
        # 获取相关代码上下文
        keywords = ["bug", "error", "fix", "issue"]
        code_context = analyzer.get_relevant_code_context(keywords)
        
        print(f"\n1. Git状态:")
        print(f"   分支: {git_context.current_branch}")
        print(f"   是否干净: {'是' if git_context.is_clean else '否'}")
        
        print(f"\n2. 风险分析:")
        if uncertainties:
            for unc in uncertainties:
                print(f"   [警告]  [{unc['severity']}] {unc['description']}")
        else:
            print("   没有发现明显的Git相关风险")
        
        print(f"\n3. 修复指导摘要:")
        print(guidance[:400] + "..." if len(guidance) > 400 else guidance)
        
        return {
            "scenario": "bug_fixing",
            "bug_description": bug_description,
            "uncertainties": uncertainties,
            "guidance": guidance
        }
    
    def scenario_documentation(self, doc_type: str = "API文档"):
        """场景4: 文档编写"""
        print(f"场景描述: 编写{doc_type}")
        
        git_context = self.provider.get_context()
        
        if not git_context.is_git_repo:
            print("   [警告] 当前目录不是Git仓库")
            return
        
        # 查找相关的代码文件
        analyzer = GitContextUncertaintyAnalyzer(self.provider)
        
        # 根据文档类型选择关键词
        if doc_type == "API文档":
            keywords = ["api", "route", "endpoint", "controller"]
        elif doc_type == "用户手册":
            keywords = ["ui", "user", "interface", "frontend"]
        elif doc_type == "技术设计":
            keywords = ["design", "architecture", "diagram", "component"]
        else:
            keywords = ["doc", "readme", "manual"]
        
        code_context = analyzer.get_relevant_code_context(keywords)
        
        # 构建文档编写指导
        guidance = f"""
# {doc_type}编写指导

## 当前项目状态
- 仓库: {Path(git_context.repo_root).name if git_context.repo_root else '未知'}
- 分支: {git_context.current_branch}
"""
        
        # 添加相关文件信息
        if code_context.get("relevant_files"):
            guidance += f"""
## 相关代码文件
建议参考以下文件编写{doc_type}:
"""
            for file_info in code_context["relevant_files"][:5]:
                guidance += f"- {file_info['path']} ({file_info['type']})\n"
        
        # 添加提交历史信息
        if code_context.get("relevant_commits"):
            guidance += f"""
## 相关提交历史
以下提交可能对编写{doc_type}有帮助:
"""
            for commit_info in code_context["relevant_commits"][:3]:
                guidance += f"- [{commit_info['short_hash']}] {commit_info['message'][:60]}\n"
        
        guidance += f"""
## 建议工作流程
1. 创建文档分支:
   git checkout -b docs/{doc_type.lower().replace(' ', '-')}
   
2. 编写{doc_type}:
   # 在docs/目录下创建文档文件
   
3. 提交文档:
   git add docs/
   git commit -m "docs: add {doc_type}"
   
4. 合并到主分支:
   git checkout main
   git merge docs/{doc_type.lower().replace(' ', '-')}
"""
        
        print(f"\n1. 项目状态:")
        print(f"   仓库: {Path(git_context.repo_root).name if git_context.repo_root else '未知'}")
        print(f"   分支: {git_context.current_branch}")
        
        print(f"\n2. 相关代码文件:")
        if code_context.get("relevant_files"):
            for file_info in code_context["relevant_files"][:3]:
                print(f"   - {file_info['path']}")
        else:
            print("   没有找到直接相关的代码文件")
        
        print(f"\n3. 文档编写指导摘要:")
        print(guidance[:400] + "..." if len(guidance) > 400 else guidance)
        
        return {
            "scenario": "documentation",
            "doc_type": doc_type,
            "relevant_files": code_context.get("relevant_files", []),
            "guidance": guidance
        }
    
    def scenario_refactoring(self, scope: str = "代码重构"):
        """场景5: 代码重构"""
        print(f"场景描述: {scope}")
        
        git_context = self.provider.get_context()
        
        if not git_context.is_git_repo:
            print("   [警告] 当前目录不是Git仓库")
            return
        
        # 分析重构风险
        analyzer = GitContextUncertaintyAnalyzer(self.provider)
        uncertainties = analyzer.analyze_git_uncertainties({
            "task": "refactoring",
            "scope": scope
        })
        
        # 查找可能受影响的文件
        code_context = analyzer.get_relevant_code_context(["refactor", "optimize", "improve"])
        
        # 构建重构指导
        guidance = f"""
# {scope}指导

## [警告] 重构风险提示
代码重构是高风险操作，请谨慎执行。
"""
        
        # 添加风险信息
        if uncertainties:
            guidance += "发现以下Git相关风险:\n"
            for unc in uncertainties:
                guidance += f"- {unc['description']} (建议: {unc['recommendation']})\n"
        
        guidance += f"""
## 当前Git状态
- 分支: {git_context.current_branch}
- 状态: {git_context.status_text}
- 是否干净: {'是' if git_context.is_clean else '否'}

## 建议工作流程
"""
        
        if not git_context.is_clean:
            guidance += f"""
1. 先保存当前工作:
   git stash  # 暂存所有修改
   # 或 git commit -m "WIP: before refactoring"
   
2. 创建重构分支:
   git checkout -b refactor/{scope.lower().replace(' ', '-')}
   
3. 执行重构:
   # 小步提交，频繁测试
   git add .
   git commit -m "refactor: step 1 - ..."
   
4. 合并到主分支:
   git checkout main
   git merge refactor/{scope.lower().replace(' ', '-')}
   # 如果冲突，需要手动解决
"""
        else:
            guidance += f"""
1. 创建重构分支:
   git checkout -b refactor/{scope.lower().replace(' ', '-')}
   
2. 执行重构（建议步骤）:
   a) 首先运行现有测试确保通过
   b) 小范围重构，频繁提交
   c) 每次提交后运行测试
   
3. 示例提交:
   git add .
   git commit -m "refactor: extract method for clarity"
   
4. 完成重构后:
   git checkout main
   git merge refactor/{scope.lower().replace(' ', '-')}
"""
        
        # 添加相关文件信息
        if code_context.get("relevant_files"):
            guidance += f"""
## 可能受影响的文件
以下文件可能在重构范围内:
"""
            for file_info in code_context["relevant_files"][:5]:
                guidance += f"- {file_info['path']}\n"
        
        print(f"\n1. Git状态:")
        print(f"   分支: {git_context.current_branch}")
        print(f"   是否干净: {'是' if git_context.is_clean else '否'}")
        
        print(f"\n2. 重构风险:")
        if uncertainties:
            for unc in uncertainties:
                print(f"   [警告]  [{unc['severity']}] {unc['description']}")
        else:
            print("   没有发现明显的Git相关风险")
        
        print(f"\n3. 重构指导摘要:")
        print(guidance[:400] + "..." if len(guidance) > 400 else guidance)
        
        return {
            "scenario": "refactoring",
            "scope": scope,
            "uncertainties": uncertainties,
            "guidance": guidance
        }


def run_all_scenarios():
    """运行所有场景"""
    print("Git上下文增强实战场景演示")
    print("="*70)
    
    manager = ScenarioManager()
    results = {}
    
    # 运行各个场景
    scenarios = [
        ("code_review", {"file_path": "agent-core/config_system.py"}),
        ("feature_development", {"feature_name": "Git上下文增强"}),
        ("bug_fixing", {"bug_description": "配置加载失败问题"}),
        ("documentation", {"doc_type": "API文档"}),
        ("refactoring", {"scope": "TimesFM集成架构优化"})
    ]
    
    for scenario_name, params in scenarios:
        result = manager.run_scenario(scenario_name, **params)
        if result:
            results[scenario_name] = result
    
    # 生成总结报告
    print(f"\n\n{'='*70}")
    print("实战场景演示总结")
    print(f"{'='*70}")
    
    total_scenarios = len(results)
    scenarios_with_uncertainties = sum(1 for r in results.values() if r.get("uncertainties"))
    
    print(f"共演示 {total_scenarios} 个场景")
    print(f"其中 {scenarios_with_uncertainties} 个场景发现了Git相关不确定性")
    
    # 输出每个场景的关键发现
    for scenario_name, result in results.items():
        print(f"\n[{scenario_name.upper()}]")
        if "uncertainties" in result and result["uncertainties"]:
            print(f"  发现 {len(result['uncertainties'])} 个注意事项")
        else:
            print("  没有发现Git相关风险")
    
    print(f"\n{'='*70}")
    print("Git上下文增强的价值:")
    print("1. 提供项目状态感知")
    print("2. 识别潜在风险")
    print("3. 给出上下文相关的建议")
    print("4. 优化开发工作流程")
    print("5. 减少人为失误")
    print(f"{'='*70}")
    
    return results


def interactive_demo():
    """交互式演示"""
    print("Git上下文增强交互式演示")
    print("="*70)
    
    manager = ScenarioManager()
    
    while True:
        print("\n请选择要演示的场景:")
        print("1. 代码审查 (code_review)")
        print("2. 功能开发 (feature_development)")
        print("3. 缺陷修复 (bug_fixing)")
        print("4. 文档编写 (documentation)")
        print("5. 代码重构 (refactoring)")
        print("6. 运行所有场景")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-6): ").strip()
        
        if choice == "0":
            print("退出演示")
            break
        elif choice == "1":
            file_path = input("请输入要审查的文件路径 (可选，直接回车跳过): ").strip()
            params = {}
            if file_path:
                params["file_path"] = file_path
            manager.run_scenario("code_review", **params)
        elif choice == "2":
            feature_name = input("请输入功能名称 (默认: 新功能): ").strip()
            if not feature_name:
                feature_name = "新功能"
            manager.run_scenario("feature_development", feature_name=feature_name)
        elif choice == "3":
            bug_desc = input("请输入Bug描述: ").strip()
            if not bug_desc:
                bug_desc = "未知错误"
            manager.run_scenario("bug_fixing", bug_description=bug_desc)
        elif choice == "4":
            doc_type = input("请输入文档类型 (默认: API文档): ").strip()
            if not doc_type:
                doc_type = "API文档"
            manager.run_scenario("documentation", doc_type=doc_type)
        elif choice == "5":
            scope = input("请输入重构范围 (默认: 代码重构): ").strip()
            if not scope:
                scope = "代码重构"
            manager.run_scenario("refactoring", scope=scope)
        elif choice == "6":
            run_all_scenarios()
            break
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    # 自动运行所有场景
    run_all_scenarios()
    
    # 或者运行交互式演示（注释掉上面的调用）
    # interactive_demo()