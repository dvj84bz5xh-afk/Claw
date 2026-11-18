## 学习日期: 2026-11-18

### 学习项目: traccia-ai/traccia-py
- URL: https://github.com/traccia-ai/traccia-py
- Stars: 134 (Python, 更新 11-15, Apache 2.0, 基于 OpenTelemetry)
- 定位: "The AI agent control plane. Observe, evaluate, govern and prove what your agents do." — 单 Python SDK 覆盖追踪/评估/提示管理/运行时治理

### 选题依据
GitHub 搜索 API 触发 403 限流，用户指定的 4 个重点方向（autogen/python-sdk/claude-mem/genericagent）均已学。从首轮 18 个候选（关键词评分法）中选定 traccia-py：它同时命中 Claw 学习重点第 5 项"可观测性"以及长期空转的短板①fitness 闭环、⑥验收等价、⑪验收无复现载体。与 11-13 的 Tracely-ai（轨迹原生 CI）不同：Tracely 是"事后把失败轨迹变回归用例"，traccia 是"事前/事中就把质量·成本·延迟做成 PR 闸门 + 运行时策略拦截 + 合规证据"，是同一方向的另一半（govern+prove），且与昨天 prime-agent 的 gate 语义纪律形成呼应。纯 Python 栈可立即校准。

### 核心发现
1. **四合一控制面 Observe/Evaluate/Govern/Prove**：一个 SDK 里 `init()` 追踪、`evaluate()` 评估、`@govern` 运行时治理、Compliance Hub 合规存证，全部基于 OpenTelemetry span（模型/token/cost/延迟都挂在 span 上）。可导出到任意 OTLP 后端（Jaeger/Tempo/SigNoz）不锁定。
2. **三维度 CI 闸门（本轮最强）**：`traccia eval` 在 PR 时不只看质量分——**quality 掉、cost 超、latency 超任一即 fail job**。这正是 Claw 短板①"改进项只计数不验证、缺 fitness 闭环"的可抄范式：fitness 不是单一分数，而是质量/成本/延迟三条独立红线。
3. **`@govern` 四态决策 allow/reshape/deny/hold**：比 failproofai 的 allow/deny/instruct 三态多两维——`reshape`（自动降级到便宜模型/更少 token）、`hold`（抛 ApprovalPending 排队等人工审批）。策略放服务端可热更新（改阈值不用重新部署），第 4 次工具调用被 deny 时 provider 根本不会被调用。
4. **Observe/Warn/Block 三模式灰度**：每条策略可先在 Observe（只记录命中）→ Warn（告警）→ Block（真拦截）逐档开启，先看"这条策略会拦什么"再上线。对上 Claw 短板⑩"守卫自身无保护"的审慎落地方式。
5. **Prompt 版本溯源到 span**：`load_prompt(label="production")` + `compile()` 把 prompt 名与版本写进当前 span——每条 trace 能回答"是哪个 prompt 版本产生了这次输出"，且带 fallback 保证 registry 挂掉也能跑。直接补 Claw 短板⑥"上下文无溯源 lineage"。
6. **fail-closed 默认 + 覆盖面诚实声明**：治理服务不可达时**默认阻断调用**（`policy_fail_mode="open"` 才放行）；并诚实标注 Gateway（只能改 base URL 的闭源工具）看不到 tools/嵌套步骤、只有 SDK `@govern` 覆盖整条 run——能力边界按接入点分级披露。
7. **decision_id + reasons 可审计**：被拦截时抛 `AgentBlockedError(exc.reasons, exc.decision_id)`，每次策略命中都有可追的编号与理由，供合规 Hub 存证（EU AI Act / HIPAA）。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| CI 三维度闸门：质量掉/成本超/延迟超任一即 fail PR——fitness 闭环是三条独立红线而非单一分数 | P0 |
| `@govern` 四态 allow/reshape/deny/hold：reshape 自动降级模型、hold 排队人工审批；deny 时底层 provider 不被调用 | P0 |
| prompt name+version 写入 span，每条 trace 可溯源产出它的提示版本 + fallback 降级 | P1 |
| Observe→Warn→Block 策略灰度三档 + 策略服务端热更新（改阈值不重新部署） | P1 |
| 覆盖面按接入点诚实分级（SDK 看全 run / Gateway 只看 model call）+ 治理不可达 fail-closed 默认 | P1 |
| decision_id + reasons 每次拦截可审计，供合规存证 | P2 |

### 改进建议
1. **[P0][eval_observability] fitness 闭环升级为三维度红线**：在现有 glass-box run 落盘 + replay 之上，给每条改进项/eval 增加 `quality_pass / cost_within_budget / latency_within_budget` 三个独立判定字段，CI 里任一不达标即 fail，而非只计数"已实施"。把短板①从"缺闭环"推进到"闭环有三条可量化红线"。
2. **[P0][claw_integration] 交付前控制面补四态决策**：现有可写可执行信任门 + fail closed 是二态（allow/deny）；扩展为 allow/reshape/deny/hold——reshape 触发 model_scheduler 降级到便宜档、hold 抛审批挂起等人工，deny 时确保工具/provider 根本不被调用（强制点在调用前，呼应 OpenShell）。
3. **[P1][context_injector] prompt lineage 写入 trace**：`load_prompt` + `compile()` 式机制——注入的提示模板名与版本记进当前 run 的 trace，使每条记录能回答"哪个提示版本产生此输出"；带 fallback 避免注册表故障导致停摆。补短板⑥的溯源维度。
4. **[P1][eval_observability] 策略灰度三档 + 决策留痕**：给 Guardrails/策略加 Observe/Warn/Block 三模式，新策略默认 Observe 只记录命中，人工确认后再升 Block；每次命中写 `decision_id + reasons` 进 trace，与已有"元策略不可暂停"叠加。
5. **[P1][eval_observability] 能力覆盖面按接入点诚实分级**：在能力矩阵里为每条治理能力标注"SDK 内可强制 / 网关代理仅 model call / 不可见"，避免把部分覆盖说成全覆盖——与 11-11 harness 工程的 15 格矩阵对仗。
6. **[P2][claw_integration] 合规证据 Hub**：把拦截决策、prompt 版本、成本/延迟判定汇总成可导出证据链（对标 EU AI Act/HIPAA 存证），供审计而非仅调试。

### 判断
traccia-py 星数不高（134）但工程完整度很高，是"可观测性治理一体机"。独有价值有二：一是把 fitness 从单一分数拆成**质量/成本/延迟三条独立红线**并做成 PR 闸门——这是 Claw 短板①一直缺的可执行形态；二是 `@govern` 的 **reshape/hold 两态**补上了 Claw 二态信任门（allow/deny）缺失的"自动降级"与"人工挂起"中间地带。与昨天 prime-agent 的 gate 语义纪律（gate 通过≠成功）连起来：prime-agent 讲"门通过只说明门验的那件事过了"，traccia 讲"门的判定要拆成三四条独立的、各自可失败的维度"。不引入整套（商业 control plane + OTLP 基建），取三维度闸门 + 四态决策 + prompt lineage 三个设计。
