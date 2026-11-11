## 学习日期: 2026-11-11

### 学习项目: ai-boost/awesome-harness-engineering
- URL: https://github.com/ai-boost/awesome-harness-engineering
- Stars: 5,118
- 语言/许可: Python(索引仓库) · 更新 2026-11-10 · 相关度 31（今日最高）
- 性质说明: **这是一份学科索引（curated index），不是可运行系统**。学它的价值不在代码，而在于它给"我们正在做的事"命了名，并给出验收矩阵与四个可落地机制。

### 核心发现

1. **它给这门学科下了定义，而这正是 Claw 在做的事**
   > "Harness engineering is the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."
   列表明确聚焦 *harness 而非模型*："Every component here exists because the model can't do it alone."
   我们的 12 个模块、463 条改进项，本质上都在做 harness engineering，但 MEMORY.md 里从没有这个词 —— 缺一个统一的名字，就缺一个统一的验收标准。

2. **可靠性面在 harness，不在 prompt（有硬证据）**
   - 据列表引述 Mitchell Hashimoto《My AI Adoption Journey》（2026-02，造词出处）：Ghostty 项目**需人工修正的提交从 40% 降到 3%**，靠的是三个月里把每一次 agent 出错都变成永久修复——"whether an AGENTS.md line or a purpose-built tool, so the error class never recurs"。
   - 据列表引述 LangChain《Improving Deep Agents with Harness Engineering》：**不换模型**，只改 harness（结构化验证循环、上下文注入含目录地图与时间预算警告、循环检测中间件、"推理三明治"把思考集中到规划与验证两段），Terminal Bench 2.0 排名**从第 30 升到前 5**。
   两条合起来的结论：`harness 改动 = 主要性能杠杆`，而不是"等更强的模型"。

3. **最关键的一句设计立场：脚手架应该设计成"将来会被删掉"**
   > "the best harnesses are designed knowing those components will become unnecessary as models improve."
   我们从未这样想过。Claw 的改进项只增不减（463 条、逐日累加），没有任何一条写过"什么条件下这条可以删"。这是脚手架债，与代码债同构。

4. **失败多数是接口失配，不是推理不足**
   据列表引述 Life-Harness：在**环境契约 / 程序性技能 / 动作实现 / 轨迹调节**四层上做 harness 侧适配，效果**跨 18 个模型骨干迁移**。推论：如果同一 harness 换模型就崩，问题在接口层，不在模型。我们目前遇到失败只会说"模型不行/任务太难"，不做这个二分。

5. **循环检测与预算警告是被反复验证的两个便宜杠杆**
   - 循环检测中间件（loop-detection middleware）：识别"同一动作重复 / 无状态推进"，主动打断。
   - 上下文注入含**目录地图 + 时间预算警告**：告诉 agent "你还有多少预算"，而不只是给它更多资料。
   Claw 有输出预算、有 Auto Compact，但**没有"剩余预算告知"**，也没有"重复调用检测"。

6. **协议边界：MCP 覆盖工具，覆盖不了会话**
   据列表引述 OpenAI《Unlocking the Codex Harness》：Codex App Server 另建 Item/Turn/Thread 协议（JSON-RPC/JSONL over stdio），原因是 **MCP 的工具导向模型撑不起审批流、流式 diff、线程持久化**。
   这条对我们有校准意义：Claw 的 Runtime 契约层（/v1 + 可续播 SSE）方向是对的，但 MCP 与会话协议的职责边界在文档里没写清。

7. **成熟度自查矩阵（列表目录即清单）**
   Agent Loop / Planning & Decomposition / Context Delivery & Compaction / Tool Design / Skills & MCP / Permissions & Authorization / Memory & State / Task Runners & Orchestration / Verification & CI / Observability & Tracing / Debugging & DX / Human-in-the-Loop / Security-Sandbox-Permissions / Evals & Verification / Production Ops。
   与 Claw 12 模块对照：**11/15 有对应物**，明显偏薄的三格是 **Debugging & DX**、**Verification & CI**、**Production Ops**；Human-in-the-Loop 我们有四道审批闸门但缺"人可随时中途介入"的自由度。

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 错误类别台账：每个观察到的失败必须归类，每类必须挂一个永久修复（规则/工具/文档行），指标改为"已退役错误类占比"而非"改进项数量" | P0 |
| 循环检测：同一 tool+args 重复 N 次或连续 M 轮无状态推进 → 打断并要求换策略，同时记一条错误类 | P0 |
| 预算感知注入：每 K 轮把"剩余 token/时间 + 目录地图"注入上下文，让"别在最后 20% 上下文做大事"从规范变成可执行 | P1 |
| 推理三明治：按阶段分配思考预算（规划、验证高；执行低），写进 Stage Contract 而非全局统一 | P1 |
| 失败二分诊断：先判"接口失配 vs 推理不足"，接口失配改 harness，不许归因给模型 | P1 |
| 淘汰条款（sunset clause）：每条脚手架/改进项声明"模型具备何种能力后即可删除"+ 复审日期，定期重估，防脚手架债 | P2 |

### 改进建议

1. **[P0][eval_observability] 错误类别台账 + 退役率主指标**
   新增 `error_classes.json`：`{class_id, 现象, 触发条件, permanent_fix(指针: 规则/工具/文档行), retired_at, 复发计数}`。任何一次任务失败/返工必须先归类再修；未归类不允许关闭任务。仪表盘主指标从"改进项总数"换成 **已退役错误类 / 已观察错误类**，复发即重开。价值：把短板①（缺 fitness 闭环）从"计数"变成"可验证的退役"。

2. **[P0][agent_orchestrator] 循环检测中间件**
   在工具调用边界统计 `(tool_name, args_hash)` 连续重复次数与"状态是否推进"；超阈值（同调用重复 3 次 / 连续 5 轮无新文件与无新结论）则中断当前策略，注入"换方法或上报"提示，并记 error class `loop-no-progress`。价值：这是列表里被两处独立引述的便宜杠杆，我们目前完全没有。

3. **[P1][context_injector] 预算感知注入**
   在上下文里周期性附带"剩余预算条"：`已用轮次/上限、剩余 token 估算、剩余时间、当前目录地图（一级/二级）`。触发点：每 K 轮或每完成一个子任务。价值：让 SOUL.md 2.5 的"避免最后 20% 上下文做大操作"从人工自觉变成机制。

4. **[P1][model_scheduler] 分阶段思考预算（推理三明治）**
   Stage Contract 增加 `thinking_budget` 字段：规划段与验证段给高预算，执行段给低预算；同一任务内可不同，但**必须在阶段开始前声明**并记入 run 记录。价值：LangChain 那条排名的四个杠杆之一，成本几乎为零（只是分配策略）。

5. **[P1][eval_observability] 失败二分诊断**
   失败报告强制两栏：`interface_mismatch`（契约/工具签名/上下文格式/权限）与 `reasoning_deficit`（模型判断错）。默认先假设接口失配（Life-Harness 的证据：harness 侧适配跨 18 个骨干迁移）。价值：阻止"模型不行"成为万能借口，把失败导向可修的层。

6. **[P2][skill_system] 脚手架淘汰条款**
   每个技能/钩子/改进项登记 `sunset_when`（"当模型原生支持 X 时可删"）与 `review_at` 日期；季度复审，能删的删，删不掉的说明理由。价值：463 条改进项只增不减是隐性债，这条给它装上出水口。

### 与 Claw 的关系判断
不引入依赖（这是索引仓库，无代码可引）。它的价值是**三样东西**：
1. **一个名字**：我们做的是 harness engineering，不是"造 Agent 框架"。名字带来验收标准。
2. **一套矩阵**：15 格自查，Claw 11 格有对应物，薄在 Debugging/DX、Verification/CI、Production Ops。
3. **一条我们完全缺失的立场**：脚手架要设计成将来会被删掉。我们只有"加"，没有"减"。

今天最该抄的不是任何一个组件，而是**"错误必须入账、且每个错误类必须被永久修复"**这条纪律 —— 它把 Claw 现有的 463 条"建议"和真实失败之间缺失的那根线接上了。
