## 学习日期: 2026-06-04

### 学习项目: modelcontextprotocol/python-sdk
- URL: https://github.com/modelcontextprotocol/python-sdk
- Stars: 23,225
- Language: Python
- License: MIT
- 最近更新: 2026-06-04

### 项目概述
MCP (Model Context Protocol) 官方 Python SDK，由 Anthropic 主导的开放协议实现。提供 Server/Client 双端 API，支持 stdio 和 Streamable HTTP 两种传输方式。当前稳定版 v1.x，v2 (pre-alpha) 在开发中。

### 核心发现

1. **双层服务器架构** — `FastMCP`（装饰器驱动，快速开发）+ `Server` lowlevel（完全控制协议细节），同一 SDK 提供两个抽象层次
2. **结构化输出（Structured Output）** — 工具返回类型注解（BaseModel/TypedDict/Dataclass）自动序列化为 JSON Schema，无需手动定义 outputSchema
3. **Context 依赖注入** — 通过函数签名类型注解自动注入 Context 对象（参数名任意），支持泛型 `Context[SessionType, LifespanContextType]` 类型安全
4. **Lifespan API** — 用 `@asynccontextmanager` 管理服务器启动/关闭资源，工具中通过 `ctx.request_context.lifespan_context` 类型安全访问
5. **Progressive Disclosure（渐进式暴露）** — Context 提供 `report_progress()`/`elicit()`/`create_message()` 等 API，支持进度报告、用户确认、LLM 采样回调
6. **分页支持** — `ListResourcesResult` 原生支持 cursor-based 分页，适合大数据集场景
7. **认证与安全** — 内置 `SimpleTokenVerifier` + OAuth2 `AuthSettings`，生产级安全配置

### 可借鉴点

| 优点 | 优先级 | 适用模块 |
|------|--------|---------|
| Context 依赖注入模式（类型注解自动注入） | P0 | skill_system / tool_system |
| Lifespan API 资源生命周期管理 | P0 | agent_orchestration |
| 结构化输出自动推导（返回类型→Schema） | P1 | tool_system |
| 双层 API 设计（高层Fast + 低层Control） | P1 | 整体架构 |
| cursor-based 分页支持 | P2 | knowledge_retrieval |
| 内置进度报告/用户确认回调 | P1 | 可观测性 |

### 改进建议

1. **P0: 为 Claw Skill 系统引入 Context 注入机制** — 参考 MCP 的 `Context[Session, LifespanContext]` 泛型设计，让 Skill 函数通过类型注解自动获取会话上下文、项目配置、记忆系统引用，无需全局变量传递。这是 MCP SDK 最核心的架构创新，直接解决了 Agent 工具系统中上下文传递的痛点。

2. **P0: 实现资源生命周期管理（Lifespan API）** — 参考 MCP 的 `@asynccontextmanager` lifespan 模式，为 Claw 的进化引擎和 Agent 编排实现优雅的资源初始化/清理机制（数据库连接、文件句柄、API Session）。

3. **P1: 工具返回值自动 Schema 推导** — 借鉴 MCP 结构化输出机制，Claw 工具系统可自动从返回类型注解生成输入/输出 Schema，简化工具注册流程。
