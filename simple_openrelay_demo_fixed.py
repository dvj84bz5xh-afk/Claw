#!/usr/bin/env python3
"""
简易OpenRelay集成演示脚本 (Windows兼容版)

在不依赖复杂导入的情况下演示OpenRelay集成。
"""

import asyncio
import json
import subprocess
from pathlib import Path
import sys

class SimpleOpenRelayDemo:
    """简易OpenRelay演示"""
    
    def __init__(self):
        self.workspace = Path.cwd()
        self.openrelay_path = self.workspace / "openrelay"
    
    def check_installation(self):
        """检查安装状态"""
        print("=" * 60)
        print("OpenRelay集成状态检查")
        print("=" * 60)
        
        # 检查项目目录
        if self.openrelay_path.exists():
            print(f"[OK] OpenRelay项目已克隆")
            
            # 检查关键文件
            files_to_check = ["README.md", "package.json", "LICENSE", "src/"]
            for file in files_to_check:
                file_path = self.openrelay_path / file
                if file_path.exists() or (file.endswith("/") and (self.openrelay_path / file[:-1]).exists()):
                    print(f"  [OK] {file}")
                else:
                    print(f"  [NO] 缺少: {file}")
            
            # 显示项目信息
            readme = self.openrelay_path / "README.md"
            if readme.exists():
                with open(readme, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[:10]:
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith("<"):
                            print(f"  项目描述: {line[:80]}...")
                            break
        else:
            print("[NO] OpenRelay项目未克隆")
            print("   请先运行: git clone https://github.com/romgX/openrelay.git")
            return False
        
        # 检查Git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("[OK] Git已安装")
        except:
            print("[WARN] Git未安装或不可用")
        
        # 检查Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] Node.js已安装: {result.stdout.strip()}")
            else:
                print("[WARN] Node.js未安装或不可用")
        except:
            print("[WARN] Node.js未安装（可选）")
        
        print("=" * 60)
        return True
    
    def show_project_structure(self):
        """显示项目结构"""
        print("=" * 60)
        print("OpenRelay项目结构")
        print("=" * 60)
        
        def list_dir(path: Path, prefix="", depth=0, max_depth=2):
            if depth > max_depth:
                return
            
            items = []
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith(".") and depth > 0:
                        continue
                    
                    if item.is_dir():
                        items.append((item, "dir"))
                    else:
                        items.append((item, "file"))
            except PermissionError:
                return
            
            for i, (item, item_type) in enumerate(items):
                is_last = i == len(items) - 1
                marker = "└── " if is_last else "├── "
                
                if item_type == "dir":
                    print(f"{prefix}{marker}[DIR] {item.name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    list_dir(item, new_prefix, depth + 1, max_depth)
                else:
                    print(f"{prefix}{marker}[FILE] {item.name}")
        
        if self.openrelay_path.exists():
            print(f"[DIR] openrelay/")
            list_dir(self.openrelay_path, "", 0, 2)
        else:
            print("目录不存在")
        
        print("=" * 60)
    
    def create_integration_plan(self):
        """创建集成计划"""
        print("=" * 60)
        print("OpenRelay集成计划")
        print("=" * 60)
        
        plan = {
            "阶段一": "项目克隆与验证",
            "阶段二": "核心功能分析",
            "阶段三": "配置系统集成",
            "阶段四": "工具连接实现",
            "阶段五": "测试与验证"
        }
        
        for stage, description in plan.items():
            print(f"{stage}: {description}")
        
        print("\n具体任务:")
        tasks = [
            "1. 分析OpenRelay架构设计",
            "2. 提取核心API接口",
            "3. 创建Python封装模块",
            "4. 集成到现有AI系统",
            "5. 配置AI提供商路由",
            "6. 实现故障转移机制",
            "7. 编写使用文档",
            "8. 创建演示脚本"
        ]
        
        for task in tasks:
            print(f"  {task}")
        
        print("=" * 60)
    
    def create_sample_config(self):
        """创建示例配置"""
        print("=" * 60)
        print("OpenRelay示例配置")
        print("=" * 60)
        
        config = {
            "openrelay": {
                "enabled": True,
                "server": {
                    "port": 18765,
                    "host": "localhost",
                    "auto_start": True,
                    "log_level": "info"
                },
                "providers": [
                    {
                        "id": "groq",
                        "name": "Groq",
                        "type": "free",
                        "base_url": "https://api.groq.com/openai/v1",
                        "priority": 1,
                        "enabled": True
                    },
                    {
                        "id": "claude_desktop",
                        "name": "Claude Desktop",
                        "type": "desktop_app",
                        "base_url": "http://localhost:18765/claude-desktop",
                        "priority": 2,
                        "enabled": True
                    },
                    {
                        "id": "deepseek",
                        "name": "DeepSeek",
                        "type": "api_key",
                        "base_url": "https://api.deepseek.com/v1",
                        "priority": 3,
                        "enabled": True
                    }
                ],
                "tools": {
                    "claude_code": {
                        "provider": "groq",
                        "env_vars": {
                            "ANTHROPIC_BASE_URL": "http://localhost:18765/groq",
                            "ANTHROPIC_API_KEY": "unused"
                        }
                    },
                    "aider": {
                        "provider": "deepseek",
                        "env_vars": {
                            "OPENAI_BASE_URL": "http://localhost:18765/deepseek",
                            "OPENAI_API_KEY": "unused"
                        }
                    }
                }
            }
        }
        
        # 保存配置
        config_file = self.workspace / "openrelay_sample_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] 示例配置已保存到: {config_file}")
        
        # 显示配置摘要
        print("\n配置摘要:")
        print(f"  服务器端口: {config['openrelay']['server']['port']}")
        print(f"  AI提供商: {len(config['openrelay']['providers'])} 个")
        print(f"  集成工具: {len(config['openrelay']['tools'])} 个")
        
        print("\n工具配置示例 (PowerShell):")
        for tool, tool_config in config["openrelay"]["tools"].items():
            print(f"\n# {tool} 配置")
            for env_var, value in tool_config["env_vars"].items():
                print(f'$env:{env_var} = "{value}"')
        
        print("=" * 60)
        return config_file
    
    def create_integration_module_stub(self):
        """创建集成模块存根"""
        print("=" * 60)
        print("创建OpenRelay集成模块存根")
        print("=" * 60)
        
        stub_code = '''"""
OpenRelay集成模块存根

这是一个简化版的OpenRelay集成模块，用于演示集成概念。
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AIProvider:
    """AI提供商"""
    id: str
    name: str
    type: str  # free, subscription, api_key, desktop_app
    base_url: str
    priority: int = 1
    enabled: bool = True
    
    def __str__(self):
        return f"{self.name} ({self.id}) - 类型: {self.type}, 优先级: {self.priority}"


class OpenRelayManager:
    """OpenRelay管理器"""
    
    def __init__(self, config_path: str = "openrelay_config.json"):
        self.config_path = config_path
        self.providers: List[AIProvider] = []
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            openrelay_config = config.get("openrelay", {})
            providers_data = openrelay_config.get("providers", [])
            
            for p_data in providers_data:
                provider = AIProvider(
                    id=p_data["id"],
                    name=p_data["name"],
                    type=p_data["type"],
                    base_url=p_data["base_url"],
                    priority=p_data.get("priority", 1),
                    enabled=p_data.get("enabled", True)
                )
                self.providers.append(provider)
                
            print(f"[OK] 已加载 {len(self.providers)} 个AI提供商")
            
        except FileNotFoundError:
            print(f"[WARN] 配置文件未找到: {self.config_path}")
            print("   使用默认配置...")
            self._create_default_providers()
        except Exception as e:
            print(f"[ERROR] 配置加载失败: {e}")
            self._create_default_providers()
    
    def _create_default_providers(self):
        """创建默认提供商"""
        self.providers = [
            AIProvider("groq", "Groq", "free", "https://api.groq.com/openai/v1", 1),
            AIProvider("claude_desktop", "Claude Desktop", "desktop_app", 
                      "http://localhost:18765/claude-desktop", 2),
            AIProvider("deepseek", "DeepSeek", "api_key", "https://api.deepseek.com/v1", 3)
        ]
    
    def list_providers(self):
        """列出所有提供商"""
        print(f"可用AI提供商 ({len(self.providers)} 个):")
        for i, provider in enumerate(self.providers, 1):
            status = "[ENABLED] " if provider.enabled else "[DISABLED]"
            print(f"  {i}. {provider} {status}")
    
    def get_provider_config(self, tool_name: str) -> Optional[Dict[str, str]]:
        """获取工具配置"""
        # 简单映射规则
        tool_mapping = {
            "claude_code": "groq",
            "aider": "deepseek",
            "goose": "claude_desktop"
        }
        
        provider_id = tool_mapping.get(tool_name)
        if not provider_id:
            print(f"[ERROR] 未找到工具 {tool_name} 的配置")
            return None
        
        # 查找提供商
        provider = None
        for p in self.providers:
            if p.id == provider_id and p.enabled:
                provider = p
                break
        
        if not provider:
            print(f"[ERROR] 提供商 {provider_id} 未启用或不存在")
            return None
        
        # 生成配置
        base_url = f"http://localhost:18765/{provider.id}"
        
        if tool_name in ["claude_code"]:
            return {
                "ANTHROPIC_BASE_URL": base_url,
                "ANTHROPIC_API_KEY": "unused"
            }
        else:
            return {
                "OPENAI_BASE_URL": base_url,
                "OPENAI_API_KEY": "unused"
            }
    
    def generate_setup_script(self, tool_name: str, platform: str = "powershell") -> str:
        """生成设置脚本"""
        config = self.get_provider_config(tool_name)
        if not config:
            return f"# 无法为 {tool_name} 生成配置"
        
        if platform == "powershell":
            lines = [f"# {tool_name} OpenRelay配置"]
            for key, value in config.items():
                lines.append(f'$env:{key} = "{value}"')
            return "\\n".join(lines)
        elif platform == "bash":
            lines = [f"# {tool_name} OpenRelay配置"]
            for key, value in config.items():
                lines.append(f'export {key}="{value}"')
            return "\\n".join(lines)
        else:
            return f"# 不支持的平台: {platform}"


def main():
    """主函数"""
    print("=== OpenRelay集成演示 ===")
    
    # 创建管理器
    manager = OpenRelayManager()
    
    # 列出提供商
    manager.list_providers()
    
    # 生成配置脚本
    tools = ["claude_code", "aider"]
    print("\\n=== 工具配置脚本 ===")
    
    for tool in tools:
        print(f"\\n# {tool} 配置")
        print(manager.generate_setup_script(tool, "powershell"))
    
    print("\\n=== 演示完成 ===")


if __name__ == "__main__":
    main()
'''
        
        stub_file = self.workspace / "openrelay_stub.py"
        with open(stub_file, "w", encoding="utf-8") as f:
            f.write(stub_code)
        
        print(f"[OK] 集成模块存根已创建: {stub_file}")
        print("\n用法:")
        print(f"  python {stub_file}")
        print("  将加载配置并生成工具设置脚本")
        
        print("=" * 60)
        return stub_file
    
    def run_demo(self):
        """运行完整演示"""
        print("\n>>> OpenRelay集成演示")
        print("=" * 60)
        
        # 检查安装
        if not self.check_installation():
            print("[ERROR] 安装检查失败，请先克隆OpenRelay项目")
            return
        
        # 显示项目结构
        self.show_project_structure()
        
        # 显示集成计划
        self.create_integration_plan()
        
        # 创建示例配置
        config_file = self.create_sample_config()
        
        # 创建集成模块
        stub_file = self.create_integration_module_stub()
        
        print("\n[DONE] 演示完成")
        print("=" * 60)
        print("创建的资产:")
        print(f"  1. 项目结构分析")
        print(f"  2. 集成计划")
        print(f"  3. 示例配置: {config_file}")
        print(f"  4. 集成模块存根: {stub_file}")
        print("\n下一步:")
        print("  1. 阅读openrelay/README.md了解详细功能")
        print("  2. 运行集成模块存根: python openrelay_stub.py")
        print("  3. 根据实际需求扩展集成模块")
        print("=" * 60)


def main():
    """主函数"""
    demo = SimpleOpenRelayDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()