## 学习日期: 2026-08-06

### 学习项目: mksglu/context-mode
- URL: https://github.com/mksglu/context-mode
- Stars: 19,647
- Language: TypeScript
- License: ELv2
- 创建时间: 2026-02-23
- 相关度: 43 (最高之一)

### 项目概述
Context Mode 是一个 MCP 服务器，解决 AI 编码 Agent 的上下文窗口问题。通过四大机制实现 98% 上下文节省：工具输出沙箱化、会话连续性持久化、Think-in-Code 范式、路由强制执行。支持 17 个平台（Claude Code、Gemini CLI、VS Code Copilot、Cursor 等），被 Microsoft、Google、Meta、Amazon、ByteDance 等团队使用。Hacker News #1。

### 核心发现

1. **工具输出沙箱化 (Context Sandboxing)** — 每次 ctx_execute 在隔离子进程中运行，只有 stdout 进入上下文。315KB 原始数据压缩到 5.4KB（98% 减少）。Playwright 快照 56KB→299B，GitHub Issues 59KB→155B。12 种语言运行时（JS/TS/Python/Shell/Ruby/Go/Rust/PHP/Perl/R/Elixir/C#）。

2. **Think-in-Code 范式** — 核心理念：LLM 应该编写分析代码，而非自己计算数据。47 次 Read() = 700KB，改为 1 次 ctx_execute() = 3.6KB（100x 节省）。Agent 写脚本做计数/分析/聚合，只 console.log 结果。这是强制性范式跨越所有 17 个平台。

3. **会话连续性 (Session Continuity)** — SQLite + FTS5 持久化每个有意义事件（文件编辑、git操作、任务、错误、用户决策）。对话压缩时不回灌数据，而是用 BM25 搜索检索相关事件。模型从上次中断处精确恢复。6 个生命周期 Hook 协作：PreToolUse/PostToolUse/UserPromptSubmit/PreCompact/SessionStart/Stop。

4. **Intent-Driven Filtering** — 当输出超过 5KB 且提供了 intent 时，自动切换到意图驱动过滤模式。只保留与 intent 相关的输出行，进一步压缩上下文。

5. **Batch Execution + Concurrency** — ctx_batch_execute 在一次调用中运行多个命令 + 搜索多个查询，支持 concurrency 1-8 的 I/O 密集型并行。986KB→62KB。

6. **双层路由强制** — Hook 层（程序化拦截，可阻止危险命令）+ 指令文件层（prompt 引导）。有 Hook 时 ~98% 节省，无 Hook 时 ~60% 节省。17 平台全覆盖。

7. **URL Fetch + Index Pipeline** — ctx_fetch_and_index 获取 URL、分块、索引到 FTS5，带 24h TTL 缓存。支持多 URL 并行获取。60KB→40B。

### 可借鉴点

| 优点 | 模块 | 优先级 |
|------|------|--------|
| Tool Output Sandbox — 工具输出隔离子进程，仅 stdout 入上下文 (98% 减少) | context_injector | P0 |
| Think-in-Code 范式 — Agent 写代码分析数据而非读入原始数据 (100x 节省) | context_injector | P0 |
| Session Continuity — SQLite+FTS5+BM25 事件追踪，压缩后按需检索恢复 | memory_system | P0 |
| Intent-Driven Filtering — 输出超阈值时按意图过滤保留相关行 | context_injector | P1 |
| Batch Execute + Concurrency — 多命令/查询一次调用+I/O并行 | tool_registry | P1 |
| 6-Hook 生命周期协作 — PreToolUse/PostToolUse/UserPromptSubmit/PreCompact/SessionStart/Stop | agent_orchestrator | P1 |

### 改进建议

1. **[P0] context_injector: Tool Output Sandbox** — 为 Claw 的工具执行引入隔离子进程模式。当前工具调用结果直接注入上下文，改为：工具输出→沙箱缓冲→仅摘要/stdout 注入上下文。预期减少 80%+ 上下文占用。实现路径：在 tool_registry 中添加 output_sandbox 参数，工具执行后先过滤再注入。

2. **[P0] context_injector: Think-in-Code 范式** — 引入 ctx_execute 等价工具，允许 Agent 编写脚本处理大量数据而非逐个读取。对 Claw 的数据分析场景（链追踪/课程开发）尤其有效：写脚本批量处理→只输出结果摘要。从"数据搬运工"转变为"代码生成者"。

3. **[P0] memory_system: Session Continuity Engine** — 实现事件级会话追踪：SQLite 存储（文件编辑/git操作/任务/错误/用户决策）+ FTS5 全文索引 + BM25 按需检索。对话压缩时不回灌全部历史，而是搜索相关事件恢复工作状态。解决 Claw 长会话上下文丢失问题。

4. **[P1] context_injector: Intent-Driven Output Filter** — 工具输出超阈值（如 5KB）时，根据调用 intent 自动过滤保留相关行。减少大输出对上下文的冲击。

5. **[P1] tool_registry: Batch Execute Tool** — 新增 batch_execute 工具，一次调用执行多个命令/查询+可选并发。减少多轮工具调用的上下文开销。

6. **[P1] agent_orchestrator: 6-Hook Lifecycle** — 补全 PreCompact 和 Stop Hook，实现完整的会话生命周期管理。PreCompact 时保存关键状态，Stop 时捕获助手最后输出。
