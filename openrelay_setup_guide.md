# OpenRelay 接入 WorkBuddy 指南

## 一、项目概述

OpenRelay 是一个开源的 AI 提供商代理/路由器，能够：
1. **聚合 32 个 AI 提供商** (Groq, Claude Desktop, DeepSeek, 等)
2. **智能路由** - 根据优先级自动选择最佳提供商
3. **故障转移** - 主要提供商失败时自动切换备用
4. **统一配置** - 通过单一端点 `localhost:18765` 提供服务

## 二、已完成的集成工作

### 1. 项目克隆
- ✅ 已克隆 `romgX/openrelay` 仓库到 `c:/Users/10127/WorkBuddy/Claw/openrelay/`
- ✅ 已克隆 `msitarzewski/agency-agents` 仓库到 `c:/Users/10127/WorkBuddy/Claw/agency-agents/`

### 2. 代码集成
- ✅ 已创建集成模块:
  - `agent-core/openrelay_config.py` - 配置管理模块
  - `agent-core/openrelay_integration.py` - 主集成模块
- ✅ 已创建演示脚本:
  - `simple_openrelay_demo.py` - 基础演示
  - `simple_openrelay_demo_fixed.py` - Windows兼容版本
  - `openrelay_integration_summary.py` - 集成总结报告

### 3. Windows 兼容性修复
- ✅ 修复 Windows GBK 编码问题 (Unicode 字符替换为 ASCII 标记)
- ✅ 所有脚本已通过 Windows 环境测试

## 三、接入 WorkBuddy 的配置

### 1. MCP 服务器配置

已更新 MCP 配置文件 `c:/Users/10127/.workbuddy/mcp.json`:

```json
{
  "mcpServers": {
    "openrelay": {
      "command": "openrelay-windows-x64.exe",
      "args": [],
      "env": {
        "PORT": "18765"
      }
    }
  }
}
```

### 2. 下载 OpenRelay 可执行文件

运行下载脚本:
```powershell
# 切换到项目目录
cd c:/Users/10127/WorkBuddy/Claw

# 运行下载脚本
.\openrelay_download.ps1
```

或者手动下载:
- 访问: https://github.com/romgX/openrelay/releases/latest
- 下载: `openrelay-windows-x64.exe`
- 保存到: `c:/Users/10127/WorkBuddy/Claw/`

### 3. 启动 OpenRelay

方法一: 双击 `openrelay-windows-x64.exe`
方法二: 命令行启动:
```powershell
cd c:/Users/10127/WorkBuddy/Claw
.\openrelay-windows-x64.exe
```

启动后访问: http://localhost:18765

## 四、环境变量配置

### 基本配置 (PowerShell):
```powershell
# 设置Groq提供商
$env:ANTHROPIC_BASE_URL="http://localhost:18765/groq"
$env:ANTHROPIC_API_KEY="unused"

# 设置DeepSeek提供商  
$env:OPENAI_BASE_URL="http://localhost:18765/deepseek"
$env:OPENAI_API_KEY="unused"
```

### AI工具专用配置:
```powershell
# Claude Code 使用 Kiro 免费配额
$env:ANTHROPIC_BASE_URL="http://localhost:18765/kiro"
$env:ANTHROPIC_API_KEY="unused"

# Aider 使用 Groq 免费配额
$env:ANTHROPIC_BASE_URL="http://localhost:18765/groq"
$env:ANTHROPIC_API_KEY="unused"
```

## 五、Python 集成代码示例

```python
from agent_core.openrelay_integration import OpenRelayIntegration

# 创建集成实例
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

# 获取使用统计
stats = await integration.get_usage_stats()
print(f"总请求数: {stats['total_requests']}")
print(f"活跃提供商: {stats['active_providers']}")
```

## 六、支持的 AI 提供商

### IDE 提供商 (8个，自动提取，无需API密钥):
- Claude Desktop (您的订阅)
- Claude Code (您的订阅)
- Kiro (AWS) - 每月50积分 + 500新用户额度
- Windsurf (Codeium) - 无限自动补全 + 每月25积分
- Antigravity (IDE内置)
- OpenCode (无限) - 内置 GLM-4.7
- VS Code Copilot (您的订阅)
- OpenAI Codex (限时免费 GPT-5.4)

### 直接 API 提供商 (24个，需要API密钥):
- Groq - 30 RPM, 每天最多14,400请求
- DeepSeek - 500万token注册积分
- Gemini - 100万上下文，慷慨的免费层
- 智谱AI (GLM) - GLM-4-Flash永久免费
- Moonshot (Kimi) - 每天150万token
- 阿里云DashScope - ¥450积分，200+模型
- 火山引擎 (字节跳动) - ¥100积分，每天200万token

## 七、故障排除

### 常见问题:
1. **OpenRelay 无法启动**
   - 检查是否已下载可执行文件
   - 检查端口 18765 是否被占用
   - 以管理员身份运行

2. **无法连接到 AI 提供商**
   - 检查网络连接
   - 确认提供商配置正确
   - 检查 API 密钥是否有效

3. **WorkBuddy 无法识别 OpenRelay**
   - 重启 WorkBuddy 应用
   - 检查 MCP 配置文件位置
   - 确认路径正确

### 调试命令:
```powershell
# 检查OpenRelay是否运行
curl http://localhost:18765/health

# 检查可用提供商
curl http://localhost:18765/api/providers

# 检查MCP配置
type $env:USERPROFILE\.workbuddy\mcp.json
```

## 八、高级功能

### 1. 模型组合
```powershell
# 创建虚拟模型组
$env:ANTHROPIC_BASE_URL="http://localhost:18765/fast-group"
# fast-group = Groq (Llama 90B) + Cerebras (Llama 70B) + SambaNova (Llama 405B)
```

### 2. 故障转移配置
在 OpenRelay Web 面板配置:
- 设置提供商优先级
- 配置自动故障转移
- 设置请求超时时间

### 3. 使用统计
- 实时监控请求量
- 查看提供商使用情况
- 分析响应时间和成功率

## 九、文件位置

- **OpenRelay项目**: `c:/Users/10127/WorkBuddy/Claw/openrelay/`
- **可执行文件**: `c:/Users/10127/WorkBuddy/Claw/openrelay-windows-x64.exe`
- **集成模块**: `c:/Users/10127/WorkBuddy/Claw/agent-core/`
- **MCP配置**: `c:/Users/10127/.workbuddy/mcp.json`
- **快速入门**: `c:/Users/10127/WorkBuddy/Claw/openrelay_quick_start.md`

## 十、后续步骤

1. **下载并启动 OpenRelay**
2. **配置 WorkBuddy 环境变量**
3. **测试集成功能**
4. **根据需求定制配置**

---

**集成状态**: ✅ 已配置完成  
**系统状态**: 🟢 准备就绪  
**下一步**: 下载并启动 OpenRelay，配置环境变量即可使用。