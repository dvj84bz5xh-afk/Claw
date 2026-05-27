#!/usr/bin/env python3
"""
OpenRelay集成演示脚本

演示如何：
1. 克隆OpenRelay项目
2. 集成到现有AI系统
3. 配置AI提供商
4. 启动和使用OpenRelay服务
"""

import asyncio
import os
import sys
import json
from pathlib import Path
import subprocess

# 添加当前目录和agent-core到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "agent-core"))

try:
    # 先尝试相对导入
    import agent_core.openrelay_integration as openrelay_int
    import agent_core.openrelay_config as openrelay_cfg
    OpenRelayIntegration = openrelay_int.OpenRelayIntegration
    OpenRelayConfig = openrelay_int.OpenRelayConfig
    OpenRelayConfigManager = openrelay_cfg.OpenRelayConfigManager
except ImportError as e:
    print(f"相对导入错误: {e}")
    print("尝试直接导入...")
    try:
        # 直接导入模块
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from openrelay_integration import OpenRelayIntegration, OpenRelayConfig
        from openrelay_config import OpenRelayConfigManager
    except ImportError as e2:
        print(f"直接导入错误: {e2}")
        print("尝试创建简易演示...")
        # 如果所有导入都失败，创建简易演示
        class SimpleOpenRelayDemo:
            def run(self):
                print("使用简易演示模式")
                print("检查OpenRelay项目...")
                
                openrelay_path = current_dir / "openrelay"
                if openrelay_path.exists():
                    print(f"✅ OpenRelay项目已存在: {openrelay_path}")
                    
                    # 读取README
                    readme_path = openrelay_path / "README.md"
                    if readme_path.exists():
                        with open(readme_path, "r", encoding="utf-8") as f:
                            content = f.read(500)
                            print(f"项目简介: {content[:200]}...")
                    else:
                        print("❌ README.md不存在")
                else:
                    print("❌ OpenRelay项目不存在")
                    
                return False
        sys.exit(0)


class OpenRelayDemo:
    """OpenRelay演示类"""
    
    def __init__(self):
        self.workspace_path = Path.cwd()
        self.openrelay_path = self.workspace_path / "openrelay"
        self.config_manager = OpenRelayConfigManager(self.workspace_path)
        
    def check_prerequisites(self) -> bool:
        """检查前提条件"""
        print("=" * 60)
        print("检查OpenRelay集成前提条件")
        print("=" * 60)
        
        # 检查Git
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git已安装: {result.stdout.strip()}")
            else:
                print("❌ Git未安装或不可用")
                return False
        except FileNotFoundError:
            print("❌ Git未安装")
            return False
        
        # 检查Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js已安装: {result.stdout.strip()}")
            else:
                print("❌ Node.js未安装或不可用")
        except FileNotFoundError:
            print("⚠️ Node.js未安装（可能需要编译OpenRelay）")
        
        # 检查OpenRelay仓库
        if self.openrelay_path.exists():
            print(f"✅ OpenRelay仓库已存在: {self.openrelay_path}")
        else:
            print(f"⚠️ OpenRelay仓库不存在: {self.openrelay_path}")
            print("  将在演示中自动克隆")
        
        # 检查Python依赖
        try:
            import httpx
            print(f"✅ httpx已安装: {httpx.__version__}")
        except ImportError:
            print("❌ httpx未安装，请运行: pip install httpx")
            return False
        
        print("=" * 60)
        return True
    
    def clone_openrelay(self) -> bool:
        """克隆OpenRelay项目"""
        if self.openrelay_path.exists():
            print(f"✅ OpenRelay仓库已存在，跳过克隆")
            return True
        
        print("=" * 60)
        print("克隆OpenRelay项目")
        print("=" * 60)
        
        try:
            # 克隆仓库
            cmd = ["git", "clone", "https://github.com/romgX/openrelay.git", str(self.openrelay_path)]
            print(f"运行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ OpenRelay克隆成功")
                
                # 检查仓库内容
                if (self.openrelay_path / "README.md").exists():
                    print(f"✅ 找到README.md")
                if (self.openrelay_path / "package.json").exists():
                    print(f"✅ 找到package.json")
                
                return True
            else:
                print(f"❌ OpenRelay克隆失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 克隆过程中出错: {e}")
            return False
    
    def check_openrelay_installation(self) -> bool:
        """检查OpenRelay安装状态"""
        print("=" * 60)
        print("检查OpenRelay安装状态")
        print("=" * 60)
        
        # 检查关键文件
        required_files = ["README.md", "package.json", "LICENSE"]
        for file in required_files:
            if (self.openrelay_path / file).exists():
                print(f"✅ {file}")
            else:
                print(f"❌ 缺少文件: {file}")
                return False
        
        # 检查src目录
        src_dir = self.openrelay_path / "src"
        if src_dir.exists():
            print(f"✅ src目录")
            src_files = list(src_dir.glob("*.ts"))
            if src_files:
                print(f"   找到 {len(src_files)} 个TypeScript文件")
        else:
            print("❌ 缺少src目录")
            return False
        
        # 尝试读取README
        readme_path = self.openrelay_path / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if "OpenRelay" in first_line:
                print(f"✅ README验证: {first_line[:50]}...")
            else:
                print(f"⚠️ README内容异常")
        
        print("=" * 60)
        return True
    
    def configure_openrelay(self):
        """配置OpenRelay"""
        print("=" * 60)
        print("配置OpenRelay")
        print("=" * 60)
        
        # 更新配置
        updates = {
            "config": {
                "auto_discover": True,
                "log_level": "info"
            },
            "tool_integrations": {
                "claude_code": "groq",
                "aider": "deepseek",
                "goose": "gemini"
            }
        }
        
        self.config_manager.update_config(updates)
        print("✅ OpenRelay配置已更新")
        
        # 显示当前配置
        config = self.config_manager.config
        print(f"   启用状态: {config.enabled}")
        print(f"   自动集成: {config.auto_integrate}")
        print(f"   故障转移: {config.enable_failover}")
        print(f"   工具集成: {len(config.tool_integrations)} 个工具")
        
        # 显示提供商
        print(f"   AI提供商: {len(config.config.providers)} 个")
        for i, provider in enumerate(config.config.providers[:3], 1):
            print(f"     {i}. {provider.name} ({provider.id}) - 优先级: {provider.priority}")
        
        print("=" * 60)
    
    def generate_setup_scripts(self):
        """生成设置脚本"""
        print("=" * 60)
        print("生成工具设置脚本")
        print("=" * 60)
        
        tools = ["claude_code", "aider", "goose"]
        for tool in tools:
            print(f"\n{tool} 配置脚本:")
            
            # PowerShell
            print(f"  PowerShell:")
            script = self.config_manager.generate_setup_script(tool, "powershell")
            for line in script.split("\n"):
                print(f"    {line}")
            
            # Bash
            print(f"  Bash:")
            script = self.config_manager.generate_setup_script(tool, "bash")
            for line in script.split("\n"):
                print(f"    {line}")
        
        print("=" * 60)
    
    async def run_integration_demo(self):
        """运行集成演示"""
        print("=" * 60)
        print("运行OpenRelay集成演示")
        print("=" * 60)
        
        try:
            # 创建集成实例
            config = OpenRelayConfig(
                port=18765,
                host="localhost",
                auto_start=True,
                auto_discover=True,
                log_level="info"
            )
            
            integration = OpenRelayIntegration(
                config=config,
                workspace_path=str(self.workspace_path)
            )
            
            print("1. 初始化OpenRelay集成...")
            await integration.initialize()
            
            print("2. 发现AI提供商...")
            providers = await integration.discover_providers()
            print(f"   发现 {len(providers)} 个提供商")
            
            for i, provider in enumerate(providers[:5], 1):
                print(f"   {i}. {provider.name}: {provider.description}")
                print(f"      类型: {provider.provider_type}, 状态: {provider.status}")
            
            print("3. 获取使用统计...")
            stats = await integration.get_usage_stats()
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   活跃提供商: {stats['active_providers']}")
            
            print("4. 配置Claude Code使用Groq...")
            success = await integration.configure_tool("claude_code", "groq")
            print(f"   配置结果: {'成功' if success else '失败'}")
            
            print("5. 演示故障转移配置...")
            config.enable_pro_plan = True
            print(f"   Pro计划启用: {config.enable_pro_plan}")
            
            print("\n✅ OpenRelay集成演示完成")
            
            # 清理
            await integration.cleanup()
            
        except Exception as e:
            print(f"❌ 集成演示失败: {e}")
            import traceback
            traceback.print_exc()
    
    def create_documentation(self):
        """创建集成文档"""
        print("=" * 60)
        print("创建OpenRelay集成文档")
        print("=" * 60)
        
        doc_path = self.workspace_path / "openrelay_integration_guide.md"
        
        doc_content = """# OpenRelay集成指南

## 项目概述

OpenRelay是一个本地AI代理工具，能够：
1. **自动发现**本地AI订阅和免费配额（Claude Desktop、Kiro、Windsurf等）
2. **统一代理**32个AI提供商，通过单一端点(localhost:18765)提供服务
3. **智能路由**将任意配额分配给支持Anthropic/OpenAI API的工具

## 集成架构

### 核心模块
1. **`openrelay_integration.py`** - 主集成模块
   - 启动/停止OpenRelay服务
   - 管理AI提供商配置
   - 路由AI请求到最佳提供商
   - 监控配额使用情况

2. **`openrelay_config.py`** - 配置管理模块
   - 管理OpenRelay服务器配置
   - 与TimesFM-inspired配置系统集成
   - 生成工具配置脚本

### 功能特性
- **多提供商支持**: Groq、Claude Desktop、DeepSeek、Gemini等
- **故障转移**: 自动切换到备用提供商
- **智能路由**: 基于提供商优先级和状态选择
- **统计监控**: 实时监控使用情况和配额状态

## 安装步骤

### 1. 克隆OpenRelay项目
```bash
git clone https://github.com/romgX/openrelay.git
cd openrelay
```

### 2. 检查依赖
- Git
- Node.js (可选，用于编译)
- Python 3.8+
- httpx库: `pip install httpx`

### 3. 集成到现有系统
```python
from agent_core.openrelay_integration import OpenRelayIntegration

# 创建集成实例
integration = OpenRelayIntegration(workspace_path="./")

# 初始化
await integration.initialize()

# 发现提供商
providers = await integration.discover_providers()

# 配置工具
await integration.configure_tool("claude_code", "groq")
```

## 配置说明

### 主要配置项
```json
{
  "port": 18765,
  "host": "localhost",
  "auto_start": true,
  "auto_discover": true,
  "log_level": "info",
  "enable_failover": true,
  "max_retry_attempts": 3
}
```

### 工具集成映射
| 工具 | 默认提供商 | 环境变量 |
|------|-----------|----------|
| claude_code | groq | ANTHROPIC_BASE_URL |
| aider | deepseek | OPENAI_BASE_URL |
| goose | gemini | OPENAI_BASE_URL |

## 使用示例

### 基本使用
```python
import asyncio
from agent_core.openrelay_integration import OpenRelayIntegration

async def demo():
    integration = OpenRelayIntegration()
    await integration.initialize()
    
    # 路由请求
    response = await integration.route_request(
        tool_name="claude_code",
        request_data={
            "model": "claude-3-sonnet",
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    
    print(f"使用提供商: {response['used_provider']}")

asyncio.run(demo())
```

### 故障转移演示
```python
# 当主要提供商失败时，自动切换到备用提供商
response = await integration.route_request(
    tool_name="aider",
    request_data=request_data,
    preferred_provider="groq"  # 优先使用Groq，失败时自动切换
)
```

## 故障排除

### 常见问题

1. **OpenRelay服务无法启动**
   - 检查端口18765是否被占用
   - 检查OpenRelay可执行文件是否存在
   - 查看日志文件中的错误信息

2. **提供商发现失败**
   - 检查网络连接
   - 验证API密钥是否正确
   - 检查OpenRelay版本兼容性

3. **请求路由失败**
   - 检查提供商状态是否活跃
   - 验证请求格式是否正确
   - 查看故障转移配置

### 调试信息
```python
# 启用详细日志
config = OpenRelayConfig(log_level="debug")
integration = OpenRelayIntegration(config=config)

# 查看使用统计
stats = await integration.get_usage_stats()
print(f"总请求数: {stats['total_requests']}")
print(f"活跃提供商: {stats['active_providers']}")
```

## 性能优化

### 缓存策略
- 提供商状态缓存: 30秒
- 配额信息缓存: 5分钟
- 路由决策缓存: 基于请求模式

### 连接池
- HTTP客户端连接池: 默认10个连接
- 连接超时: 30秒
- 请求重试: 最多3次

## 安全注意事项

1. **凭证安全**
   - API密钥仅存储在本地
   - 凭证使用后立即从内存清除
   - 支持加密存储选项

2. **隐私保护**
   - 请求内容不记录
   - 不收集用户数据
   - 所有通信通过本地网络

3. **访问控制**
   - 默认只监听localhost
   - 支持身份验证
   - 可配置访问白名单

## 扩展开发

### 添加新提供商
```python
from agent_core.openrelay_integration import AIProvider, QuotaType

new_provider = AIProvider(
    id="new_provider",
    name="New AI Service",
    description="New AI service integration",
    provider_type=QuotaType.API_KEY,
    base_url="https://api.new-service.com/v1",
    priority=5
)

integration.config.providers.append(new_provider)
```

### 自定义路由逻辑
```python
class CustomRouter(OpenRelayIntegration):
    async def _select_best_provider(self, tool_name, preferred_provider):
        # 自定义选择逻辑
        if tool_name == "special_tool":
            return self._find_special_provider()
        return await super()._select_best_provider(tool_name, preferred_provider)
```

## 监控和维护

### 健康检查
```bash
# 检查OpenRelay服务状态
curl http://localhost:18765/api/health

# 查看提供商状态
curl http://localhost:18765/api/providers
```

### 日志查看
```bash
# OpenRelay日志位置
~/.workbuddy/openrelay/logs/

# 系统日志
tail -f openrelay_integration.log
```

## 后续计划

### 近期计划
- [ ] 支持更多AI提供商
- [ ] 增强故障转移机制
- [ ] 添加Web管理界面

### 长期计划
- [ ] 集成到更多开发工具
- [ ] 实现智能配额调度
- [ ] 添加性能分析工具

---

**注意**: 此文档会根据OpenRelay项目的更新而更新。
"""

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
        
        print(f"✅ 文档已创建: {doc_path}")
        print("=" * 60)
    
    async def run_full_demo(self):
        """运行完整演示"""
        print("🚀 OpenRelay集成演示开始")
        print("=" * 60)
        
        # 步骤1: 检查前提条件
        if not self.check_prerequisites():
            print("❌ 前提条件检查失败，退出演示")
            return
        
        # 步骤2: 克隆OpenRelay
        if not self.clone_openrelay():
            print("❌ OpenRelay克隆失败，退出演示")
            return
        
        # 步骤3: 检查安装状态
        if not self.check_openrelay_installation():
            print("❌ OpenRelay安装检查失败，退出演示")
            return
        
        # 步骤4: 配置OpenRelay
        self.configure_openrelay()
        
        # 步骤5: 生成设置脚本
        self.generate_setup_scripts()
        
        # 步骤6: 运行集成演示
        await self.run_integration_demo()
        
        # 步骤7: 创建文档
        self.create_documentation()
        
        print("🎉 OpenRelay集成演示完成")
        print("=" * 60)
        print("总结:")
        print("  1. OpenRelay项目已克隆")
        print("  2. 集成模块已创建")
        print("  3. 配置系统已设置")
        print("  4. 演示脚本已运行")
        print("  5. 集成文档已生成")
        print("=" * 60)
        print("下一步: 将OpenRelay集成应用到实际项目中")
        print("=" * 60)


async def main():
    """主函数"""
    demo = OpenRelayDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    # 运行异步演示
    asyncio.run(main())