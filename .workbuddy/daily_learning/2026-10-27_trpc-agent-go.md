## 学习日期: 2026-10-27

### 学习项目: trpc-group/trpc-agent-go
- URL: https://github.com/trpc-group/trpc-agent-go
- Stars: 1,877 ⭐ (Go, Apache-2.0, 更新 2026-10-26, Trendshift 当日 Go 榜 #1 / 总榜 #3)
- 背景: 腾讯 tRPC 团队的 Agent 框架，定位"生产级 Go 原生 Agent 运行时"。可与 Claw 直接对照——同一公司语境、同样的"框架而非产品"取向。

### 核心发现

1. **包即架构，13 个包各管一段，没有万能模块**：`runner`(执行流+会话) / `agent`(核心执行单元) / `planner`(策略与工具选择) / `tool` / `session` / `memory` / `knowledge`(RAG) / `artifact`(**版本化产物**) / `skill` / `evolution`(会话评审→受管技能) / `event`(流式载荷) / `evaluation`(eval set+指标) / `server`(Gateway/AG-UI/A2A) / `telemetry`(OTel)。
   **关键点：`skill`、`evolution`、`evaluation`、`artifact` 各自独立成包**，而非塞进 orchestrator。Claw 把 runner 与 agent 合并成 `agent_orchestrator`，缺少独立的 `artifact`（产物版本化）与 `evolution`（评审→发布）边界。
2. **三协议分工写得很清楚**：`AG-UI` 管 agent↔前端，`A2A` 管 agent↔agent 互操作，`MCP` 管 agent↔工具，三者由一个 **Gateway Server** 统一出口。Claw 目前只有 MCP + ACP 适配器，缺 AG-UI 与 A2A 两个方向，也没有"单一出口"的概念。
3. **技能是可分发资产，四种机制齐备**：
   - 目录 + `SKILL.md` 规范（遵循 Anthropic Agent Skills 规范）
   - `NewFSRepository` 支持 **HTTP(S) 的 zip/tar.gz 直接拉取并本地缓存**（`SKILLS_CACHE_DIR` 可改）
   - **多根目录叠加**：共享技能库 + 用户私有库同时挂载
   - 长驻进程靠 **显式 `repo.Refresh()`** 让下一轮看到新装的技能（不做文件监听，避免不确定性）
   - `skill_load` 与 `skill_run` 是**两个工具**，加载与执行分离
4. **进化是服务，不是脚本**：`evolution.NewService(reviewerModel, WithManagedSkillsDir, WithSkillRepository)` 挂在 runner 上；**会话完成后异步评审**，过**质量门**后**发布回受管技能目录**。发布物是 `SKILL.md`（可被下一轮直接加载的技能），不是"改进建议条目"。注意其门是**评审模型**，不是量化 fitness（与 10-25 EvoAgentX 的评估驱动是两条路线，前者重可读性、后者重可比性）。
5. **双执行路径必须互斥**：启用 `skill_run` 时，要显式 `WithEnableCodeExecutionResponseProcessor(false)`，否则助手回复里 markdown 围栏代码块会被自动执行，同一段代码跑两遍。这是"两个执行入口忘了互斥"的典型踩坑，文档主动写明。
6. **取消按 `requestID`**：终端 Ctrl+C、代码内 context cancel、服务器按 requestID 取消，三条路径统一到同一套取消语义——服务化场景必须能"从外部杀掉一个正在跑的 run"。
7. **Prompt Caching 自动生效**，官方称缓存内容省 90% 成本；evaluation 用 `WithNumRuns(3)` 多次跑再判 `OverallStatus`，不靠单次结果下结论。

### 可借鉴点

| 优点 | 优先级 |
|---|---|
| 进化产物与手写技能**物理隔离**（managed_skills 独立目录），可整目录丢弃回滚 | P0 |
| 技能库四件套：远程归档拉取+本地缓存 / 多根叠加 / 显式 Refresh / load 与 run 分离 | P0 |
| 三协议职责边界（AG-UI 前端 / A2A Agent 互操作 / MCP 工具）+ 单一 Gateway 出口 | P1 |
| 双执行路径互斥（skill_run 开启即关闭代码块自动执行） | P1 |
| 缓存命中率与节省额单列计量，避免成本指标失真 | P2 |

### 改进建议

1. **【P0 · skill_system】进化产物与手写技能物理隔离**。当前 Claw 的所有技能都在 SkillsHub/`~/.workbuddy/skills/` 两级副本里，自动生成与人工维护混居，一旦自动技能质量差，只能逐条删。应新增独立 `managed_skills/` 根目录：进化产物只写这里，加载时与手写库**叠加但优先级更低**；整目录可丢弃、可 diff、可回滚，不影响人工资产。
2. **【P0 · claw_integration】进化服务化，发布物是 SKILL.md 而非建议条目**。现状：进化引擎产出"改进建议"写进 `learning_tracking.json`，424 条里 96 条被标为已实施，但**没有一条沉淀成可复用技能**。应改为：会话结束 → 异步评审 → 质量门（可读性/可执行性/是否重复）→ 通过则写 `SKILL.md` 落到 `managed_skills/` → 下一轮可直接加载。这样"进化"的产物才是有用的东西，而不是计数。
3. **【P1 · agent_orchestrator】明确三协议职责边界 + 单一 Gateway**。补一句能力矩阵式声明：MCP 管工具、ACP/A2A 管 Agent 互操作、AG-UI 管前端事件流；并收敛到一个 Gateway 出口，避免每个方向各自开端口。
4. **【P1 · tool_registry】双执行路径互斥开关**。凡同时存在"技能执行"与"代码块自动执行"两个入口时，默认只留一个，另一个必须显式关闭，并在启动自检里报冲突。
5. **【P2 · eval_observability】缓存计量单列**。token 成本拆成"命中缓存/未命中"两项分别计，否则 prompt caching 生效后成本曲线会突然跳变，误判为优化有效。

### 判断

与昨天的 EvoAgentX 正好互补：EvoAgentX 解决"**怎么判断改动是否更好**"（量化 fitness），trpc-agent-go 解决"**改进怎么沉淀成资产**"（评审门 → SKILL.md）。Claw 两样都缺，但**后者更便宜**——不需要评估数据集，只要把已有 96 项实施成果写成 SKILL.md 落到独立目录，就能立刻验证"进化到底有没有产出"。建议本周先做 P0-1 + P0-2：建 `managed_skills/`，把 3 项已实施改进写成技能，看下一轮能否被自动加载。
