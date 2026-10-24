## 学习日期: 2026-10-24

### 学习项目: sandbaseai/sandbase-harness
- URL: https://github.com/sandbaseai/sandbase-harness
- Stars: 635 | 语言: TypeScript | 最近更新: 2026-10-18 | License: Apache-2.0 | 版本 v0.3.8
- 一句话: **Agent 的 runtime 层**（不是模型 SDK、不是工作流可视化器）——会话、沙箱化工具、记忆、凭证、审计与回放全部跑在自己机器上

### 项目概述
Agent SDK 解决"模型循环"，但生产环境还需要：持久会话、工具治理、沙箱边界、凭证处理、记忆、可审计、给人看的 Console。SandBase Harness 就做这层：默认 SQLite 存元数据 + 工作区文件存内容，本地起 `/v1` API 与 Console，无必须的托管控制面。沙箱后端可切本地进程 / Docker 每会话容器 / Kubernetes / 自托管 worker 队列。

### 核心发现
1. **可恢复的 SSE 事件流 + 会话重放**：长任务中断后可 resume，事件流可 replay 调试——不是"日志"，而是可续播的会话状态流。
2. **沙箱四后端同一抽象**：本地进程 → Docker(每会话容器) → K8s(kubectl exec/cp) → 自托管 worker 队列，同一会话契约切换执行面。
3. **工具治理四件套**：MCP toolsets 编组 + 凭证保管库(vault) + 权限策略 + 审批(approval)；并提供 `--tool-approval allow` 预授权，避免每个工具调用都打断。
4. **单一活动 provider 边界**：同一时刻只有一个生效的 provider；**保存的配置只在启动时生效**（显式激活语义），agent 自带 model id，id 不匹配直接 `model_not_found` 失败。
5. **默认开放、按需加锁的认证**：默认无鉴权；只要存在任意一个 API key，认证自动激活（Bearer）。渐进式安全而非默认全锁。
6. **能力矩阵"诚实声明"**：`src/core/capabilities/matrix.ts` 逐条标注 Supported / Partial / Unsupported，**每条 Partial 与 Unsupported 必须写原因**（如"无 compatibility header 的请求按本地调用者接受，这是刻意的 local-first 扩展"）；110 条路由 90 挂载、20 条按名拒绝，**没有"推迟"这一档**。
7. **契约诚实性测试**：README 的兼容表由 `npm run docs:compat` 生成，一旦与矩阵漂移测试就失败——"宣称的兼容性 = 被测过的兼容性"。
8. **官方 SDK 一致性用例进 CI**：用 Anthropic 官方 TS SDK 打自己的 `/v1`，完整跑一个 turn（消息→工具调用→工具结果→回复），并在每个 PR 上执行。
9. **release gate 一体化**：typecheck + tests + 两个 build + `npm pack --dry-run` + CLI init 冒烟 + 示例启动冒烟，一条命令。

### 可借鉴点
| 优点 | 优先级 | 说明 |
|------|--------|------|
| Runtime 契约层：`/v1` + 可恢复 SSE + 会话 replay | P0 | Claw 有 Daemon/事件总线设想，但没有"可续播的事件流"契约 |
| 工具审批预授权（`--tool-approval allow`）+ vault + 策略 | P0 | Claw 的 per-tool ACL 缺"一次性放行"这一降摩擦出口 |
| 能力矩阵逐条 Supported/Partial/Unsupported + 原因 + 漂移测试 | P1 | 直接治"宣称支持但实际没有"的文档漂移 |
| 配置只在启动时生效（显式激活）+ 单一 provider 边界 | P2 | 避免运行时热切换导致的隐性不一致 |
| 默认开放 / 有 key 才鉴权 的渐进安全 | P1 | 与 Claw 的"默认安全 dry-run"互补：本地单租户场景不必默认全锁 |

### 改进建议
1. **[P0][claw_integration] Runtime 契约层：`/v1` + 可恢复 SSE 事件流 + replay**：把会话状态机暴露为可续播事件流（带 seq/游标），支持 `claw resume <session>` 断线续跑与 `claw replay <session>` 回放；元数据入 SQLite、产物留文件。价值: 长任务不再"断了重来"，调试从翻日志变为回放时间线。
2. **[P0][tool_registry] 审批预授权 + 凭证保管库 + 策略三件套**：在现有 per-tool ACL 之上增加"本次会话一次性预授权"（如 `--tool-approval allow=pkg_install,net_fetch`）与短期凭证注入（vault → 出口时注入，不落模型上下文）。价值: 既保留治理边界，又消除每个工具都弹确认的审批疲劳。
3. **[P1][eval_observability] 能力矩阵诚实声明 + 漂移测试**：维护 `capabilities.matrix`（Supported/Partial/Unsupported + 必填 reason），文档中的兼容表由脚本从矩阵生成，CI 校验"矩阵 ↔ 文档 ↔ 实际路由"三者一致；禁止出现"推迟/待定"这类含糊档位。价值: 把"支持什么"变成可测事实，防止宣传跑在实际能力前面。
4. **[P1][storage] Local-first 默认栈 + 渐进鉴权**：默认 SQLite 存元数据、文件存内容，无强制托管依赖；认证默认关闭，一旦配置了任一 API key 自动启用 Bearer 校验。价值: 本地单租户零配置即可跑，上云时安全边界随凭证出现而收紧，不需要两套部署形态。
5. **[P2][model_scheduler] 单一活动 provider 边界 + 配置显式激活**：同一时刻只允许一个生效 provider，配置变更需 restart/activate 才生效；agent 绑定自己的 model id，不匹配即明确报错而非静默回退。价值: 消除"改了配置但没生效"与"热切换造成前后半场模型不同"的隐性不一致。

### 对 Claw 的定位判断
Claw 目前是"编排 + 记忆 + 技能"框架，**缺少独立可部署的 runtime 层**：没有 `/v1` 契约、没有可续播事件流、没有凭证保管库与审批预授权、没有能力矩阵这种"自证支持范围"的机制。该项目只有 635 星，但工程诚实度（矩阵必写原因、文档生成、漂移即失败、官方 SDK 用例进 CI）比星数更值得抄。建议把 P0 两项当作"runtime 化"的起点：先有事件流契约与审批出口，再谈多后端沙箱。
