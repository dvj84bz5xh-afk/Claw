## 学习日期: 2026-10-08

### 学习项目: All-Hands-AI/OpenHands (Agent Canvas)
- URL: https://github.com/All-Hands-AI/OpenHands
- Stars: 90,207 | Language: TypeScript | 相关度: 42

### 核心发现
1. **ACP (Agent-Client Protocol) 统一协议**: 将 OpenHands/Claude Code/Codex/Gemini 或任何 ACP 兼容 agent 无缝接入同一控制中心, 编排层与 agent 实现彻底解耦
2. **多后端架构 (backends)**: 同一前端可在 local/Docker/VM/cloud 多个 agent-server 后端间切换, agent 可运行在团队共享服务器或个人笔记本
3. **Automations 事件驱动自动化**: 定时(schedule)或 Webhook 事件触发的自动化工作流, 集成 Slack/GitHub/Linear/Notion/Datadog
4. **多 Docker Sandbox 会话隔离**: 每个会话独立容器运行, workspace 与持久化状态挂载, 会话历史跨容器替换存活
5. **frontend/backend 分离部署**: `--frontend-only` 静态前端 + `--backend-only` agent server + automation backend 可拆分运行
6. **BYO model + BYO agent**: 任意 LLM + 任意 ACP agent, 完全开放生态

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| ACP 统一协议 + 多 agent 后端路由 | P0 |
| Automations 事件驱动自动化(定时/Webhook) | P0 |
| 多 Docker Sandbox 会话隔离 + workspace 持久化挂载 | P1 |
| 可插拔后端切换(local/Docker/VM/cloud) | P1 |
| frontend/backend 分离部署(前端静态 + agent server 拆分) | P2 |

### 改进建议
1. [P0] 用 ACP 协议抽象层统一接入第三方 agent(Claude Code/Codex 等)作为 Claw 执行后端, 编排层与 agent 实现解耦
2. [P0] Automations 事件驱动自动化: 定时 + Webhook 触发的工作流引擎, 对接 Slack/GitHub/Linear 等第三方服务
3. [P1] 多 Docker Sandbox 会话隔离: 每会话独立容器, workspace 文件与状态持久化挂载, 会话历史跨容器存活
4. [P1] 可插拔后端切换: 同一前端在 local/Docker/VM/cloud 多 agent-server 后端间无缝切换
5. [P2] frontend/backend 分离部署: 前端静态层 + agent server + automation backend 可拆分独立运行
