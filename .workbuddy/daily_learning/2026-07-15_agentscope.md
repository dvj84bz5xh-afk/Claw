## 学习日期: 2026-07-15

### 学习项目: AgentScope 2.0
- URL: https://github.com/agentscope-ai/agentscope
- Stars: 27,857
- 语言: Python
- 相关度: 30（多模块高度相关）

### 核心发现
1. **可组合中间件系统** — `MiddlewareBase` + 7种内建中间件：RAGMiddleware、AgenticMemoryMiddleware、Mem0Middleware、ReMeMiddleware、TracingMiddleware、ReplyBudgetControlMiddleware、TTSMiddleware。通过钩子注入Agent推理-行动循环，无需修改核心代码。
2. **三重长期记忆架构** — AgenticMemory（主动记忆管理）+ Mem0（外部记忆集成）+ ReMe（检索增强记忆）。三种记忆策略可独立启用或叠加使用。
3. **零侵入追踪中间件** — `TracingMiddleware` 通过中间件钩子自动捕获Agent全链路行为（推理→工具调用→结果），无需修改Agent代码即可实现可观测性。
4. **预算控制中间件** — `ReplyBudgetControlMiddleware` 限制单轮回复token/成本，防止过度消耗，适合生产级部署。
5. **多后端沙箱抽象** — Workspace模块统一封装 Local / Docker / E2B / OpenSandbox / Daytona / K8s 多种执行环境，Agent代码在隔离沙箱运行。
6. **统一事件总线** — Event System 支持前端UI实时推送、人机协同（human-in-the-loop）、多Agent消息广播。
7. **细粒度权限系统** — Permission System 在工具级和资源级进行ACL控制，支持多租户隔离。
8. **Agent Team** — 分布式多Agent协作，支持多租户多会话RAG服务。

### 可借鉴点
| 优点 | 优先级 | 目标模块 |
|------|--------|----------|
| 中间件钩子系统（MiddlewareBase） | P0 | agent_core |
| 零侵入TracingMiddleware | P0 | eval_observability |
| 预算控制ReplyBudgetControlMiddleware | P1 | model_scheduler |
| 多后端沙箱Workspace抽象 | P1 | claw_integration |
| 统一事件总线Event System | P2 | claw_integration |
| 三重长期记忆（Agentic+Mem0+ReMe） | P2 | memory_system |

### 改进建议
1. **P0 - 引入MiddlewareBase到agent_core**: 设计可插拔中间件基类，在Agent推理-行动循环的关键节点（pre-reply/post-tool/pre-compact）插入钩子。优先实现TracingMiddleware（自动追踪）和RAGMiddleware（自动检索增强）。
2. **P0 - eval_observability零侵入追踪**: 参考TracingMiddleware设计，通过中间件钩子自动捕获model调用、tool执行、记忆读写的事件，写入.evolution_log.jsonl，无需修改现有Agent代码。
3. **P1 - model_scheduler预算控制**: 引入ReplyBudgetControlMiddleware概念，在model_scheduler层限制单轮/单会话的token消耗上限，超过阈值自动降级模型或提示用户。
4. **P1 - 多后端沙箱抽象**: 为claw_integration引入Workspace概念，支持本地执行、Docker容器、E2B沙箱三种后端，危险操作（文件删除、网络请求）自动路由到隔离环境。
5. **P2 - Event System事件总线**: 引入统一事件总线，解耦各模块（model/tool/memory/eval）间的通信，支持UI实时推送和human-in-the-loop审批。
