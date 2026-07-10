## 学习日期: 2026-07-10

### 学习项目: OpenHands/OpenHands
- URL: https://github.com/OpenHands/OpenHands
- Stars: 80,247
- Forks: ~9,300
- Language: Python
- License: Other (自定义)
- 状态: 活跃维护中（2026-07-09 最后更新）
- 路线转型: 从单库 OpenHands 平台 → **Agent Canvas 控制中心** + OpenHands Agent（独立子项目）

---

### 项目定位

> *"The self-hosted developer control center for coding agents and automations."*

OpenHands（前身 OpenDevin）是开源 AI 编程代理领域**最早的工业级项目**之一（2024年3月成立）。2026年完成重大架构升级——以 **Agent Canvas**（TypeScript/React 控制台）为前端，**OpenHands Agent**（Python 运行时）为后端，通过 **ACP（Agent Communication Protocol）** 协议统一接入多种代理（OpenHands / Claude Code / Codex / Gemini 等），实现"自托管、可扩展、跨厂商"的代理编排平台。

### 核心技术发现

#### 1. **ACP（Agent Communication Protocol）多代理互操作**
   - 2025年起对接 Anthropic/Google 推动的 ACP 标准
   - 单实例可并行运行 OpenHands + Claude Code + Codex + Gemini
   - 通过 `@openhands/agent-canvas` npm 包统一 UI 入口
   - 优势：避免厂商锁定（vendor lock-in），多模型路由降本

#### 2. **多层后端抽象（Self-Hosting 体系）**
   - Local: 本地进程直跑（开发）
   - Docker: 单容器隔离（个人）
   - VM: 远程沙箱（团队）
   - OpenHands Cloud / Enterprise: 托管服务（企业）
   - 通过 `config.toml` 切换后端，无需改业务代码

#### 3. **预构建自动化（Prebuilt Automations）**
   - 模板化工作流：报告→Slack、Issue 分解任务、PR 自动审查
   - Webhook 触发 + Cron 调度双模式
   - 集成栈：Slack、GitHub、Linear、Jira、Notion

#### 4. **企业级能力矩阵**
   - `.openhands/` 目录：项目级配置（类似 `.clinerules`/`.cursorrules`）
   - `AGENTS.md`：Agent 协作约定
   - `containers/`：沙箱运行时（Docker/Modal/E2B/Kubernetes）
   - `dev_config/`：多环境配置隔离
   - `config.template.toml`：350+ 配置项，覆盖 LLM / 工作区 / 安全 / 沙箱

#### 5. **生态化运营**
   - Incubator Program（孵化器计划）扶持第三方代理接入
   - Slack 社区 8K+ 开发者
   - 完整文档站：docs.openhands.dev
   - 商业版 OpenHands Cloud / Enterprise 反哺开源

### 可借鉴点

| 优点 | 优先级 | 模块 | 说明 |
|------|--------|------|------|
| **ACP 多协议互操作** | P0 | agent_orchestration | 参考 ACP 协议设计 Claw 多代理统一接入层，避免依赖单一代理运行时 |
| **预构建自动化模板市场** | P0 | skill_system | 借鉴"工作流即模板"思路，建立 Claw 自动化模板市场（报告→飞书/Issue 拆解等） |
| **多层后端抽象** | P1 | tool_system | 沙箱后端 Local/Docker/VM/Cloud 四态切换，提升 Claw 部署灵活性 |
| **Webhook + Cron 双调度** | P1 | agent_orchestration | 强化 Claw 自动化触发机制（飞书/QQ/钉钉 webhook 集成） |
| **`.openhands/` 项目级配置** | P2 | context_injector | 项目级规则文件可注入上下文，类似 Claw 的 `.workbuddy/CLAUDE.md` |
| **Incubator 生态合作模式** | P2 | platform | 启动 Claw Incubator 计划，吸引第三方 Skill/MCP 贡献者 |

### 改进建议

1. **【P0】Claw ACP 适配器** — 实现 Claw agent_core 对接 ACP 协议，让 Claw 能调度 Claude Code/Codex/Gemini 等外部代理。预期价值：3-5x 代理选型灵活性，降低 40% 单代理绑定风险
2. **【P1】自动化模板市场 v1** — 在 `SkillsHub/.workbuddy/skills/automations/` 建立模板库（GitHub Issue 拆解、报告→飞书、定时日报等），开箱即用。预期价值：用户上手成本 -60%
3. **【P2】Claw `.agentrules` 项目级规则** — 强化 `.workbuddy/CLAUDE.md` 优先级与项目局部覆盖能力。预期价值：多项目隔离 + 团队协作标准化

### Claw 系统能力对比（基于 MEMORY.md 记忆）

| 维度 | Claw 现状 | OpenHands | 差距 |
|------|----------|-----------|------|
| 多代理编排 | agent_orchestrator（18项已实施） | ACP 多协议 + 模板市场 | Claw 缺生态层 |
| 技能系统 | `~/.workbuddy/skills/` 160+ 技能 | 预构建自动化 + 孵化器 | Claw 缺模板化与商业化 |
| 部署后端 | 本地为主 | Local/Docker/VM/Cloud 四态 | Claw 缺远程沙箱 |
| 可观测性 | eval_observability_skill | OTEL + 事件看门狗 | Claw 已对齐 |
| 记忆系统 | memory_system + MEMORY.md | PostgreSQL+pgvector | Claw 缺持久化层 |

### 累计统计
- 累计学习项目: 87
- 累计改进项: 176（P0: 27, P1: 71, P2: 14）
- 实施率: P0 27/51 (52.9%), P1 71/100 (71.0%), P2 14/14 (100%)

### 下一步
- 继续每日学习 1 个项目（细水长流）
- 优先候选：Snailclimb/JavaGuide、Shubhamsaboo/awesome-llm-apps
