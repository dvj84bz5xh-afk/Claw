## 学习日期: 2026-07-30

### 学习项目: humanlayer/12-factor-agents
- URL: https://github.com/humanlayer/12-factor-agents
- Stars: 24,952 | Forks: 1,891 | Language: TypeScript
- 描述: 生产级LLM软件构建原则 — "What are the principles we can use to build LLM-powered software that is actually good enough to put in the hands of production customers?"
- 相关度: **38** (方法论级，覆盖Claw全部10个模块)

### 核心发现
1. **12因子Agent方法论** — 类比12-Factor App，定义了生产级Agent软件的12条设计原则，从工具调用到状态管理到错误处理全覆盖
2. **"好的Agent不是prompt+tools+bag loop"** — 作者Dex指出大多数生产级Agent是"mostly deterministic code, with LLM steps sprinkled in"，而非全自治loop
3. **Prompt是一等代码** — Factor 2强调不要将Prompt工程外包给框架黑盒，要像管理代码一样管理Prompt（版本控制、审查、测试）
4. **拥有上下文窗口** — Factor 3提出不必使用标准消息格式传递上下文，可以自由设计上下文工程方案
5. **小而专注的Agent** — Factor 10反对单体Agent，主张小Agent作为更大确定性系统的构建块
6. **用工具联系人类** — Factor 7将人机交互抽象为工具调用，与MCP/Function Call统一

### 12因子速览
| # | 因子 | 核心要点 | 对应Claw模块 |
|---|------|---------|-------------|
| 1 | Natural Language to Tool Calls | LLM将自然语言转为结构化工具调用 | tool_registry |
| 2 | Own Your Prompts | Prompt是一等代码，不外包给框架 | context_injector |
| 3 | Own Your Context Window | 自由设计上下文工程，不必标准消息格式 | context_injector |
| 4 | Tools Are Structured Outputs | 工具=结构化输出=触发确定性代码 | tool_registry |
| 5 | Unify Execution State | 统一执行状态，与业务状态分离 | agent_orchestrator |
| 6 | Launch Pause Resume | Agent是程序，支持启动/暂停/恢复 | agent_orchestrator |
| 7 | Contact Humans With Tools | 人机交互抽象为工具调用 | tool_registry |
| 8 | Own Your Control Flow | 拥有控制流，不依赖框架隐式编排 | agent_orchestrator |
| 9 | Compact Errors | 紧凑错误，支持Agent自愈 | eval_observability |
| 10 | Small Focused Agents | 小Agent做一件事，嵌入确定性系统 | agent_orchestrator |
| 11 | Trigger From Anywhere | 从任意入口触发Agent | claw_integration |
| 12 | Stateless Reducer | 无状态Reducer，纯函数状态转换 | memory_system |

### 可借鉴点
| 优点 | 优先级 | 对应模块 |
|------|--------|---------|
| 统一执行状态模型（Factor 5）— 执行态与业务态分离，支持断点续传 | P0 | agent_orchestrator |
| 工具=结构化输出标准化（Factor 4）— 所有工具返回统一schema，简化编排 | P0 | tool_registry |
| 小而专注Agent架构（Factor 10）— 拆解monolithic orchestrator为lane级小Agent | P0 | agent_orchestrator |
| Prompt作为一等代码（Factor 2）— 版本控制+审查+单元测试，不依赖框架黑盒 | P0 | context_injector |
| 人机交互工具化（Factor 7）— 将human-in-the-loop统一为tool call | P1 | tool_registry |
| 紧凑错误+自愈（Factor 9）— 错误摘要+自动重试策略 | P1 | eval_observability |
| 无状态Reducer（Factor 12）— 纯函数状态转换，便于测试和回滚 | P1 | memory_system |
| 拥有上下文窗口（Factor 3）— 自定义上下文格式，非强制消息列表 | P1 | context_injector |
| 启动/暂停/恢复（Factor 6）— Agent生命周期管理标准化 | P2 | agent_orchestrator |
| 从任意触发（Factor 11）— 支持Slack/Email/Webhook等多入口 | P2 | claw_integration |

### 改进建议
1. **P0: 引入ExecutionState统一模型** — 在agent_orchestrator中定义ExecutionState（运行状态）与BusinessState（业务数据）分离的架构，支持检查点、恢复、迁移
2. **P0: 工具输出Schema标准化** — 在tool_registry中强制所有工具返回统一schema（success/result/error/context），使编排层可以统一处理
3. **P0: 重构orchestrator为lane级小Agent** — 借鉴Factor 10，将当前monolithic agent_orchestrator拆分为submit/emit/handoff等单职责lane，每个lane是一个小Agent
4. **P0: Prompt版本化管理** — 在context_injector中将所有system prompt提取为独立文件（.prompt.md），纳入版本控制，支持A/B测试
5. **P1: human_contact工具化** — 将当前human-in-the-loop机制重构为标准tool（contact_human/approve/reject），与LLM工具调用统一
6. **P1: 错误压缩+自愈策略** — 在eval_observability中实现错误摘要器（将stack trace压缩为LLM可理解的简洁错误），并内置重试/降级策略
