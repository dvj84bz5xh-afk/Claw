## 学习日期: 2026-06-26

### 学习项目: a2aproject/A2A
- URL: https://github.com/a2aproject/A2A
- Stars: 24,467
- 语言: Protocol (protobuf + 多语言SDK)
- 许可证: Apache 2.0
- 版本: v1.0.1 (2026-04-23发布)
- 治理: Linux Foundation, Google贡献
- 相关度: 29

### 项目概述
Google主导的Agent-to-Agent开放协议，解决不同框架/公司的AI智能体无法互操作的痛点。类似HTTP之于Web，A2A之于Agent通信。v1.0.1已发布，提供Python/Go/JS/Java/.NET/Rust六种官方SDK。

### 核心发现

1. **传输无关的协议设计** — 应用协议与传输绑定分离（JSON-RPC/gRPC/HTTP REST三种绑定），protobuf为单一真实来源（Single Source of Truth），ProtoJSON为JSON序列化规范。这种分层设计使协议可以适配任何传输层。

2. **Agent Card能力发现机制** — 每个Agent发布"名片"描述自身能力、连接信息、支持的交互模态。支持签名验证（Agent Card Signing）增强安全性，包含AgentInterface支持多租户路由。这是解决"Agent不知道另一个Agent能做什么"的关键。

3. **Task生命周期管理** — Task是协作核心单元，支持长时间运行任务的完整生命周期（创建→执行→流式更新→完成/取消→重新订阅）。三种交互模式：同步请求/响应、流式传输(SSE)、异步推送通知。

4. **不透明性原则（Preserve Opacity）** — Agent间协作无需暴露内部状态、记忆或工具实现。只通过Message/Artifact交换结果，保护知识产权和安全性。这与MCP的"Agent调用工具"模式形成互补。

5. **A2A与MCP互补关系** — MCP解决Agent↔Tool交互，A2A解决Agent↔Agent协作。两者可组合：Agent通过MCP使用工具，通过A2A与其他Agent协作。这是构建复杂多Agent系统的完整技术栈。

6. **多租户路由** — 单个A2A端点服务多个Agent，路由策略支持基于URL/Header/Body（tenant字段），满足企业级部署需求。

### 可借鉴点

| 优点 | 优先级 | 说明 |
|------|--------|------|
| Agent Card能力声明机制 | P0 | Claw Agent注册时声明能力+接口，支持运行时发现和动态编排 |
| 三种交互模式(同步/流式/异步) | P0 | Claw多Agent编排应支持同步调用+SSE流式+Webhook异步三种模式 |
| 不透明性原则 | P1 | Agent间协作只交换Message/Artifact，不暴露内部实现 |
| Task生命周期管理 | P1 | 长时间运行任务的状态机（创建→执行→流式→完成/取消） |
| protobuf协议定义+多绑定 | P1 | Claw工具系统从返回类型注解自动生成Schema，类似protobuf→JSON Schema |
| 多租户路由 | P2 | 单端点服务多Agent的路由策略，企业级场景需要 |

### 改进建议

1. **[P0] 实现Agent Card能力声明** — 为Claw agent_core添加AgentCard类，包含name/description/skills/interfaces/interactionModes字段。Agent注册时自动生成，支持运行时发现。参考A2A的AgentCard JSON Schema。

2. **[P0] 多模式交互支持** — 在agent_orchestrator.py中增加SSE流式和Webhook异步模式，当前仅支持同步调用。长时间运行的Agent任务需要异步推送通知机制。

3. **[P1] Task状态机** — 为agent_orchestrator添加Task生命周期管理（created→running→streaming→completed/canceled），支持任务取消和重新订阅。替代当前的简单"提交→返回"模式。

4. **[P1] 不透明协作协议** — Agent间通信只传递Message（文本/文件/JSON）和Artifact（任务输出），不传递内部状态。为Claw设计AgentMessage/AgentArtifact数据类。

5. **[P2] 协议版本控制** — 为Claw技能和Agent接口添加版本号，参考A2A的Versioning机制，确保向后兼容。

### 与Claw现有模块映射

| A2A概念 | Claw对应 | 差距 |
|---------|---------|------|
| AgentCard | tool_registry.py (部分) | 缺少能力声明和发现机制 |
| Task | agent_orchestrator.py | 仅同步调用，无生命周期管理 |
| Message | 无 | 完全缺失，Agent间直接调用 |
| Artifact | 无 | 完全缺失 |
| Agent Discovery | 无 | 完全缺失 |
| Multi-transport | 无 | 仅同步模式 |

### 关键启发
A2A揭示了Agent系统的下一个演进方向：**从"Agent调用工具"到"Agent与Agent协作"**。Claw当前的多Agent编排是紧耦合的（同一进程内调用），而A2A提供的是松耦合的协议级通信。这意味着Claw的agent_orchestrator需要从"函数调用"模式升级为"协议通信"模式，为未来的分布式Agent网络做好准备。
