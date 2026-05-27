#!/usr/bin/env python3
"""
Skill Auto Creator - 技能自动创建器
基于Hermes Agent的SKILL.md开放标准，自动将解决方案转换为技能文档

设计理念：
1. 开放标准 - 遵循Hermes SKILL.md格式
2. 自动转换 - 解决方案到技能的自动化转换
3. 元数据完整 - 包含完整的技能元数据
4. 知识复用 - 技能可搜索、可分享、可复用
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid

from multi_solution_generator import SolutionCandidate, SolutionType, RiskLevel, ResourceIntensity

class SkillPlatform(Enum):
    """技能支持的平台"""
    ALL = "all"
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WSL2 = "wsl2"

class ToolsetRequirement(Enum):
    """工具集需求"""
    WEB = "web"
    BROWSER = "browser"
    GIT = "git"
    SHELL = "shell"
    DATABASE = "database"
    API = "api"

@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "AutoSkillCreator"
    license: str = "MIT"
    platforms: List[SkillPlatform] = field(default_factory=lambda: [SkillPlatform.ALL])
    
    # 高级元数据
    tags: List[str] = field(default_factory=list)
    requires_toolsets: List[ToolsetRequirement] = field(default_factory=list)
    requires_tools: List[str] = field(default_factory=list)
    fallback_for_toolsets: List[ToolsetRequirement] = field(default_factory=list)
    fallback_for_tools: List[str] = field(default_factory=list)
    
    # 配置项
    config: Dict[str, Any] = field(default_factory=dict)
    required_environment_variables: List[Dict[str, str]] = field(default_factory=list)
    required_credential_files: List[Dict[str, str]] = field(default_factory=list)
    
    def to_yaml(self) -> str:
        """转换为YAML格式"""
        data = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "license": self.license,
            "platforms": [p.value for p in self.platforms],
            "metadata": {
                "hermes": {
                    "tags": self.tags,
                    "requires_toolsets": [t.value for t in self.requires_toolsets],
                    "requires_tools": self.requires_tools,
                    "fallback_for_toolsets": [t.value for t in self.fallback_for_toolsets],
                    "fallback_for_tools": self.fallback_for_tools,
                    "config": self.config,
                    "required_environment_variables": self.required_environment_variables,
                    "required_credential_files": self.required_credential_files
                }
            }
        }
        
        # 清理空值
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items() if v or isinstance(v, (int, float, bool))}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d if v or isinstance(v, (int, float, bool))]
            else:
                return d
        
        cleaned = clean_dict(data)
        return yaml.dump(cleaned, allow_unicode=True, sort_keys=False)

class SkillAutoCreator:
    """技能自动创建器"""
    
    def __init__(self, skills_dir: str = ".workbuddy/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
    
    def solution_to_skill_name(self, solution: SolutionCandidate) -> str:
        """解决方案转换为技能名称"""
        # 生成简洁的kebab-case名称
        base_name = solution.title.lower().replace(" ", "-").replace("_", "-")
        # 移除特殊字符
        clean_name = ''.join(c if c.isalnum() or c == '-' else '' for c in base_name)
        # 添加类型后缀
        type_suffix = f"-{solution.type.value}"
        return clean_name[:30] + type_suffix
    
    def extract_tags_from_solution(self, solution: SolutionCandidate) -> List[str]:
        """从解决方案中提取标签"""
        tags = []
        
        # 基本标签
        tags.append(f"solution-{solution.type.value}")
        tags.append(f"risk-{solution.risk_level.value}")
        tags.append(f"resource-{solution.resource_intensity.value}")
        
        # 技术标签
        for tech in solution.key_technologies:
            tags.append(f"tech-{tech.lower()}")
        
        # 内容标签
        tags.extend([tag.lower() for tag in solution.tags])
        
        # 生成策略标签
        if solution.source_strategy:
            tags.append(f"strategy-{solution.source_strategy}")
        
        # 去重并排序
        return sorted(list(set(tags)))
    
    def determine_tool_requirements(self, solution: SolutionCandidate) -> List[ToolsetRequirement]:
        """确定技能需要的工具集"""
        requirements = []
        
        # 基于技术方法判断
        technical_approach = solution.technical_approach.lower()
        
        if any(word in technical_approach for word in ["web", "browser", "selenium", "playwright"]):
            requirements.append(ToolsetRequirement.BROWSER)
        
        if any(word in technical_approach for word in ["git", "version", "commit", "branch"]):
            requirements.append(ToolsetRequirement.GIT)
        
        if any(word in technical_approach for word in ["api", "rest", "http", "request"]):
            requirements.append(ToolsetRequirement.API)
        
        if any(word in technical_approach for word in ["database", "sql", "query"]):
            requirements.append(ToolsetRequirement.DATABASE)
        
        # 默认总是需要web
        if not requirements:
            requirements.append(ToolsetRequirement.WEB)
        
        return requirements
    
    def create_skill_metadata(self, solution: SolutionCandidate) -> SkillMetadata:
        """创建技能元数据"""
        skill_name = self.solution_to_skill_name(solution)
        
        metadata = SkillMetadata(
            name=skill_name,
            description=f"基于解决方案生成: {solution.title} - {solution.description[:100]}...",
            version="1.0.0",
            author="AutoSkillCreator",
            license="MIT",
            platforms=[SkillPlatform.ALL],
            tags=self.extract_tags_from_solution(solution),
            requires_toolsets=self.determine_tool_requirements(solution)
        )
        
        # 添加配置示例
        metadata.config = {
            "solution_id": solution.id,
            "estimated_time_hours": solution.estimated_time,
            "estimated_cost": solution.estimated_cost,
            "success_probability": solution.success_probability
        }
        
        return metadata
    
    def generate_skill_content(self, solution: SolutionCandidate) -> str:
        """生成技能内容文档"""
        skill_name = self.solution_to_skill_name(solution)
        
        # 构建技能内容
        content = f"""# {solution.title}

{solution.description}

## When to Use

此技能适用于以下场景：
- 需要{solution.title}的解决方案时
- 面对类似{solution.type.value}的问题
- 风险偏好为{solution.risk_level.value}时
- 可用资源为{solution.resource_intensity.value}级别时

## Quick Reference

| 操作 | 命令/参数 | 说明 |
|------|----------|------|
| 主要功能 | 自动生成 | {solution.title} |
| 技术方法 | {solution.technical_approach} |  |
| 关键工具 | {', '.join(solution.key_technologies)} |  |
| 时间估计 | {solution.estimated_time}小时 |  |
| 成本估计 | {solution.estimated_cost}（相对） |  |

## Procedure

以下是实现{solution.title}的详细步骤：

"""
        
        # 添加实施步骤
        for i, step in enumerate(solution.implementation_steps, 1):
            content += f"{i}. {step}\n"
        
        content += f"""
## Pitfalls

### 常见问题与解决方法
1. **技术可行性问题**
   - 问题：{solution.technical_feasibility}分（技术可行性评分）
   - 解决方法：采用{solution.type.value}方法，使用{solution.key_technologies[0] if solution.key_technologies else "标准工具"}

2. **成功概率问题**
   - 问题：成功概率{solution.success_probability:.1%}
   - 解决方法：分阶段实施，降低风险

3. **资源需求问题**
   - 问题：资源密集度{solution.resource_intensity.value}
   - 解决方法：采用{solution.resource_intensity.value}优化策略

## Verification

### 验证步骤
1. **功能验证**：确保{solution.title}的核心功能正常工作
2. **性能验证**：验证技术可行性和成功概率
3. **价值验证**：确认业务价值{solution.business_value:.2f}和用户体验{solution.user_experience:.2f}

### 验收标准
- 技术可行性 ≥ {solution.technical_feasibility:.2f}
- 成功概率 ≥ {solution.success_probability:.2f}
- 业务价值 ≥ {solution.business_value:.2f}
- 用户体验 ≥ {solution.user_experience:.2f}

## Metrics

| 指标 | 数值 | 说明 |
|------|------|------|
| 类型 | {solution.type.value} | 解决方案类型 |
| 风险等级 | {solution.risk_level.value} | 风险偏好 |
| 资源密集度 | {solution.resource_intensity.value} | 资源需求 |
| 技术可行性 | {solution.technical_feasibility:.2f} | 技术实现难度 |
| 成功概率 | {solution.success_probability:.2f} | 成功可能性 |
| 业务价值 | {solution.business_value:.2f} | 业务收益 |
| 用户体验 | {solution.user_experience:.2f} | 用户满意度 |
| 估计时间 | {solution.estimated_time}小时 | 实施时间 |
| 估计成本 | {solution.estimated_cost} | 相对成本 |

## Related Skills

- 类似技术：{', '.join(solution.key_technologies)}
- 相关标签：{', '.join(solution.tags)}
- 生成策略：{solution.source_strategy}

---

**自动生成于**: {datetime.now().isoformat()}
**来源解决方案ID**: {solution.id}
"""
        return content
    
    def create_skill_from_solution(self, solution: SolutionCandidate) -> str:
        """从解决方案创建技能"""
        skill_name = self.solution_to_skill_name(solution)
        skill_dir = self.skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建技能文件路径
        skill_file = skill_dir / "SKILL.md"
        
        # 生成元数据和内容
        metadata = self.create_skill_metadata(solution)
        skill_content = self.generate_skill_content(solution)
        
        # 组合完整SKILL.md文件
        full_content = f"""---
{metadata.to_yaml()}---
{skill_content}
"""
        
        # 写入文件
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # 保存解决方案备份（用于调试）
        solution_file = skill_dir / "solution_backup.json"
        with open(solution_file, 'w', encoding='utf-8') as f:
            json.dump(solution.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"[完成] 技能 '{skill_name}' 已创建于: {skill_file}")
        
        # 生成技能索引文件
        self.update_skill_index(skill_name, metadata, solution)
        
        return str(skill_file)
    
    def update_skill_index(self, skill_name: str, metadata: SkillMetadata, solution: SolutionCandidate):
        """更新技能索引"""
        index_file = self.skills_dir / "skill_index.json"
        
        # 读取现有索引
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {
                "skills": [],
                "last_updated": datetime.now().isoformat(),
                "total_skills": 0
            }
        
        # 添加新技能条目
        skill_entry = {
            "name": skill_name,
            "metadata": {
                "description": metadata.description,
                "tags": metadata.tags,
                "requires_toolsets": [t.value for t in metadata.requires_toolsets],
                "version": metadata.version,
                "created_at": datetime.now().isoformat()
            },
            "solution_info": {
                "id": solution.id,
                "title": solution.title,
                "type": solution.type.value,
                "risk_level": solution.risk_level.value,
                "resource_intensity": solution.resource_intensity.value,
                "technical_feasibility": solution.technical_feasibility,
                "success_probability": solution.success_probability
            },
            "skill_file": f"{skill_name}/SKILL.md",
            "solution_backup": f"{skill_name}/solution_backup.json"
        }
        
        # 检查是否已存在
        existing_names = [s.get("name") for s in index["skills"]]
        if skill_name not in existing_names:
            index["skills"].append(skill_entry)
            index["total_skills"] = len(index["skills"])
            index["last_updated"] = datetime.now().isoformat()
            
            # 写入索引文件
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
    
    def batch_create_skills(self, solutions: List[SolutionCandidate]) -> List[str]:
        """批量创建技能"""
        created_skills = []
        
        for solution in solutions:
            try:
                skill_file = self.create_skill_from_solution(solution)
                created_skills.append(skill_file)
            except Exception as e:
                print(f"[错误] 创建技能失败 (解决方案: {solution.title}): {e}")
        
        return created_skills
    
    def search_skills(self, query: str, tags: Optional[List[str]] = None, skill_type: Optional[str] = None) -> List[Dict]:
        """搜索技能"""
        index_file = self.skills_dir / "skill_index.json"
        
        if not index_file.exists():
            return []
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        results = []
        
        for skill in index["skills"]:
            # 关键词匹配
            matches = False
            
            # 查询匹配
            if query:
                query_lower = query.lower()
                skill_text = f"{skill['metadata']['description']} {skill['solution_info']['title']} {' '.join(skill['metadata']['tags'])}".lower()
                if query_lower in skill_text:
                    matches = True
            
            # 标签匹配
            if tags:
                skill_tags = set(skill['metadata']['tags'])
                query_tags = set(tags)
                if query_tags.intersection(skill_tags):
                    matches = True
                elif not query:  # 如果没有查询词，标签匹配即为匹配
                    matches = True
            
            # 类型匹配
            if skill_type:
                if skill['solution_info']['type'] == skill_type:
                    matches = True
                elif not query and not tags:  # 如果没有查询词和标签，类型匹配即为匹配
                    matches = True
            
            # 空查询时返回所有技能
            if not query and not tags and not skill_type:
                matches = True
            
            if matches:
                results.append(skill)
        
        return results

def demo_skill_creation():
    """演示技能创建"""
    print("[启动] Hermes风格技能自动创建器演示")
    
    # 创建示例解决方案
    sample_solution = SolutionCandidate(
        id="test-001",
        title="Git冲突解决助手",
        description="自动化解决Git合并冲突，提供智能解决建议",
        type=SolutionType.RULE_BASED,
        risk_level=RiskLevel.CONSERVATIVE,
        resource_intensity=ResourceIntensity.LIGHT,
        technical_approach="基于规则的冲突检测和解决算法",
        key_technologies=["GitPython", "difflib", "json"],
        implementation_steps=[
            "分析Git状态和冲突文件",
            "识别冲突模式和类型",
            "应用预设的解决规则",
            "生成解决建议和代码补丁",
            "验证解决方案的有效性"
        ],
        estimated_time=2,
        estimated_cost=3,
        success_probability=0.85,
        technical_feasibility=0.9,
        business_value=0.8,
        user_experience=0.85,
        tags=["git", "conflict", "automation", "rule-based"],
        source_strategy="git_conflict_resolution"
    )
    
    # 创建技能创建器
    creator = SkillAutoCreator()
    
    # 生成技能
    skill_file = creator.create_skill_from_solution(sample_solution)
    print(f"[完成] 演示技能已创建: {skill_file}")
    
    # 搜索演示
    print("\n[搜索] 搜索演示:")
    results = creator.search_skills("git", tags=["automation"])
    print(f"找到 {len(results)} 个相关技能:")
    for result in results:
        print(f"  - {result['solution_info']['title']} ({result['solution_info']['type']})")

if __name__ == "__main__":
    demo_skill_creation()