## 学习日期: 2026-11-12

### 学习项目: FailproofAI/failproofai
- URL: https://github.com/FailproofAI/failproofai
- Stars: 8,618
- 语言/许可: TypeScript · MIT + Commons Clause · 更新 2026-11-11 · 相关度 28（今日最高）
- 一句话: **跨 harness 的策略执行 + 观测**——"Wherever your agents run, we see it — and we can say no."

### 核心发现

1. **一句话说清了定位**："Observability and enforcement for every harness your agents run in." 钩住 12 个 harness（10 个编码 CLI + 2 个 chat/assistant 网关），一套策略 API、一份会话历史。这正是我昨天矩阵里偏薄的 **Verification & CI / Debugging & DX / Production Ops** 三格的产品化形态。

2. **决策有三态，我们只有两态**
   | 决策 | 效果 |
   |---|---|
   | `allow()` | 放行 |
   | `deny(message)` | 阻断，**message 会回给 agent** |
   | `instruct(message)` | **放行，但把上下文注入 agent 下一轮 prompt** |
   `instruct` 是关键缺失：多数真实场景不是"该拦"或"该放"，而是"放过去，但得让它知道"。Claw 的 Guardrails 只有 pass/fail，遇到"不算违规但该提醒"只能二选一，通常选择静默放行 —— 提醒就丢了。

3. **元策略不可暂停（自指防护）——最值得抄的一条**
   有一个 `block-failproofai-commands` 策略**永远开启、不可关闭、不可暂停**，理由写得极准：
   > "an agent that can pause enforcement can switch off every other policy."
   安装后默认不装任何策略时，只有它在生效。也就是说：**守卫自己必须先被守住**，否则"可暂停的守卫"等于没有守卫。

4. **默认不装策略，显式启用（fail-safe 默认）**
   `failproofai config` 只接钩子、**不选任何策略**；要上守卫必须再执行 `policies add`。非交互环境（CI/容器/agent 自己跑）则直接应用而不提问。含义：安装不改变行为，但默认保护自己；改变行为必须是显式动作。

5. **前置拦截与后置检测是两个家族，且诚实区分**
   `block-*` 在调用**执行前**判定，因此在 12 个 harness 上都成立；`sanitize-*` 在工具**返回后**运行——所以它只能"报告工具输出里有密钥"，**不能"阻止密钥进入上下文"**。
   这正是昨天那条分界线的延伸：前置管"发出去的动作"，后置管"回来的内容"，两者不可互相冒充。

6. **能力按接入点分级，逐 harness 标注**
   > "stopping a tool call before it runs is verified on all twelve, turn-end gates on eight."
   每个 harness 只承诺它真做到的事件，附 per-harness 矩阵。无钩子的 agent 走 Python SDK 时明确写成**只有 tracing/sessions/audits，没有 enforcement**——"Enforcement there needs a hook in your own runtime."
   诚实降级，而不是宣称"全面支持"。

7. **audit → 建议策略的闭环（昨天 P0 的产品形态）**
   离线 `failproofai audit` 扫本机历史找风险模式，并**建议用哪些策略去阻止它们**；托管侧有 "scheduled audits that turn recurring failures into evidence-backed findings"。
   这就是"错误类别台账"该长的样子：复发失败 → 有证据的结论 → 一条可执行的策略。

8. **trace 必须包含 hook 决策**
   会话里记录的是 model calls / tool calls / **hook decisions** 的序列，以及"被阻断的是什么、策略对 agent 说了什么"。只记调用不记决策的 trace，回答不了"为什么这次放行了"。

9. 内置 40 条策略里包括 `warn-repeated-tool-calls`（agent 在同一调用上打转）—— 昨天列为 P0 的循环检测，在成熟产品里就是一条默认策略，反证了它的必要性。

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 元策略不可暂停：一条最小硬编码 deny 集（禁改审批/审计配置、禁读密钥文件）不受任何策略与 agent 影响 | P0 |
| 决策三态 allow/deny/instruct：`instruct` 放行但向下轮注入训示，解决"不该拦但该提醒"的空档 | P0 |
| hook 决策写入 run trace（含回给 agent 的原话）+ 离线 audit 从历史复发模式产出建议策略 | P1 |
| 前置拦截（block）与后置检测（sanitize）分家族，文档明写"后置只能报告不能阻止" | P1 |
| 按接入点分级能力矩阵：无钩子的接入点标为"仅观测"，不宣称 enforcement | P1 |
| 安装默认不装策略（fail-safe），改变行为必须是显式动作；非交互环境直接应用不提问 | P2 |

### 改进建议

1. **[P0][claw_integration] 元策略不可暂停（守卫自指防护）**
   定义一条最小硬编码 deny 集，写在配置不可达的层（进程外 broker 或编译进 runtime 的常量）：禁止任何 agent/工具修改或暂停审批与审计配置、禁止读取密钥文件、禁止关闭本层。策略文件的"删除/禁用"接口只对人类 CLI 开放，agent 侧无此通路。文档里写明判据：**可被暂停的策略不是安全边界**。

2. **[P0][eval_observability] 决策入 trace + 审计产建议策略**
   run trace 增加 `hook_decisions` 段：`{时机(PreToolUse/PostToolUse/闸门名), 策略名, 决策, 回给 agent 的原话, 受审对象摘要}`。再提供离线 `audit` 命令扫历史 trace，按复发次数聚类，输出"建议策略（含支持它的 session id 列表）"，由人复核后才进入强制集。

3. **[P1][tool_registry] 引入第三态 `instruct`**
   工具闸门返回值从 bool 扩为三态：`allow` / `deny(reason)` / `instruct(note)`。`instruct` 不阻断执行，但把 note 注入下一轮上下文并记入 trace。用途：路径虽非生产但接近、命令虽未命中破坏模式但风险升高、参数疑似笔误。价值：把现在"静默放行"的那部分风险变成可追溯的提醒。

4. **[P1][tool_registry] 前置拦截与后置检测分家族并显式标注**
   每条策略/钩子声明 `phase: pre|post`。`pre` 承诺"动作不会发生"，`post` 只承诺"发生了会被发现"。输出契约里禁止把 post 类策略描述成"阻止了 X"。价值：防止能力被夸大，也防止我们以为"加了 sanitize 就等于拦住了"。

5. **[P1][eval_observability] 接入点能力矩阵**
   对每个外部接入（CLI adapter / MCP server / ACP / SDK 上报）列出"它能被拦截的事件"，做不到的标注 `observe-only`；启动时把该矩阵写进 run 记录首行。价值：诚实降级，避免"以为拦住了其实只是看见了"。

6. **[P2][claw_integration] fail-safe 安装默认**
   初始化只装钩子不装策略；策略需显式启用；非交互环境（CI/无人值守）直接应用而非交互提问，并把"当前生效策略集"打印进首条日志。价值：默认不改变行为，但默认保护自己；同时避免自动化环境卡在提问上。

### 与 Claw 的关系判断
不引入依赖（Node 守护进程 + 12 个 CLI 适配，与 Claw 的 Python 核心不同栈；且 Commons Clause 限制商用再分发）。
它的价值是**把我们已有的四钩三判往前推一格**：
- 从"允许/拒绝"→"允许/拒绝/训示"（表达力）；
- 从"策略可配"→"守卫不可自关"（安全性）；
- 从"记调用"→"记决策+对 agent 说了什么"（可审性）；
- 从"宣称支持"→"按接入点分级 + 仅观测"（诚实性）。

最该抄的一条是第 3 点那句判据：**"an agent that can pause enforcement can switch off every other policy"** —— 它一句话解释了为什么 Claw 现在这套进程内钩子不能算安全边界。
