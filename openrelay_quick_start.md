## OpenRelay集成快速入门

### 项目状态
- OpenRelay项目已克隆到: C:\Users\10127\WorkBuddy\Claw\openrelay
- 集成模块已创建在: C:\Users\10127\WorkBuddy\Claw\agent-core
- 演示脚本已生成: C:\Users\10127\WorkBuddy\Claw\openrelay_integration_demo.py

### 核心功能
1. **AI提供商聚合** - 统一管理Groq、Claude Desktop、DeepSeek等32个提供商
2. **智能路由** - 根据优先级自动选择最佳AI提供商
3. **故障转移** - 当主要提供商失败时自动切换到备用
4. **统一配置** - 通过单一端点(localhost:18765)提供服务

### 使用步骤
1. **启动OpenRelay服务**:
   ```python
   from agent_core.openrelay_integration import OpenRelayIntegration
   integration = OpenRelayIntegration()
   await integration.initialize()
   ```

2. **配置工具**:
   ```powershell
   # PowerShell
   $env:ANTHROPIC_BASE_URL="http://localhost:18765/groq"
   $env:ANTHROPIC_API_KEY="unused"
   ```

3. **发送请求**:
   ```python
   response = await integration.route_request("claude_code", request_data)
   ```

4. **监控状态**:
   ```python
   stats = await integration.get_usage_stats()
   ```

### 配置文件位置
- 主配置: C:\Users\10127\WorkBuddy\Claw\.workbuddy\openrelay_config.json
- 数据目录: C:\Users\10127\WorkBuddy\Claw\.workbuddy\openrelay

### 支持的AI工具
- Claude Code
- Aider
- Goose
- OpenClaw
- 任何支持Anthropic/OpenAI API的工具

### 故障排除
1. **服务无法启动**: 检查端口18765是否被占用
2. **提供商不可用**: 检查网络连接和API密钥
3. **请求失败**: 查看OpenRelay日志文件

### 下一步
1. 运行演示脚本了解完整功能
2. 根据实际需求修改配置
3. 集成到现有开发工作流中
