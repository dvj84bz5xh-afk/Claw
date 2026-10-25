## 学习日期: 2026-10-25

### 学习项目: ANative-Lab/EvoAgentX
- URL: https://github.com/ANative-Lab/EvoAgentX
- Stars: 3,402 ⭐ (Python, 更新 2026-10-22, 论文 arXiv 2507.03616)
- 定位: 不是 Agent 框架，而是**给 Agent 工作流做自动优化的实验台**——生成 → 评估 → 进化

### 核心发现

1. **工作流是一等可序列化对象**：`WorkFlowGenerator(goal)` 从一句自然语言目标生成 `WorkFlowGraph`，可 `display()` 可视化、`save_module()` / `from_file()` 存取。**拓扑先生成，Agent 后物化**——`AgentManager.add_agents_from_workflow(graph)` 按图节点反推 Agent，而不是先注册 Agent 再连成图。一个 workflow 文件就带齐了 Agent 规格，换模型配置即可重新实例化。
2. **进化 = 拟合函数，不是灵感**：固定三段——数据集（HotPotQA/MBPP/MATH，各随机 50 验证 + 100 测试）、评估器打分、优化算子提出候选并择优。**验证集调优、测试集报数**，两者严格分离，避免自证。
3. **四类优化器 = 四类搜索空间，没有通吃**：
   | 算子 | 搜索空间 / 方法 | 最强项 |
   |---|---|---|
   | TextGrad | 对 prompt 与推理链求"文本梯度"，可微式规划 | MATH 66 → 76 (+10) |
   | AFlow | 用 MCTS 在**工作流结构**上做 RL 式搜索 | MBPP 69 → 79 (+10) |
   | MIPRO | 黑盒评估 + 候选自适应重排 | HotPotQA 63.58 → 69.16 |
   | EvoPrompt | 反馈驱动的 prompt 演化 | — |

   同一系统上，**结构搜索擅长代码、文本梯度擅长推理、黑盒重排擅长检索问答**——说明"用哪个优化器"本身就是个 bandit 问题。
4. **HITL 是图内拦截器，不是特殊分支**：`HITLInterceptorAgent(target_agent_name, target_action_name, interaction_type=APPROVE_REJECT, mode=PRE_EXECUTION)` 挂到 AgentManager，图结构不变；批准结果通过 `hitl_input_output_mapping` 映射回工作流输入字段保持连续性。默认关闭，`activate()` 才生效。
5. **真实外部系统验证**：拿 EvoAgentX 去优化 GAIA 榜上的 Open Deep Research 与 OWL——只调 prompt 就提升分数，证明优化器可外挂到别人的框架上。
6. **边界很清楚**：所谓"自进化"是**离线在固定数据集上做优化**，不是运行时自我学习；优化对象限于 prompt 与工作流结构，**不碰代码**。

### 可借鉴点

| 优点 | 优先级 |
|---|---|
| 进化必须挂 fitness：数据集 + 评估器 + 算子 + 候选池，验证/测试分离 | P0 |
| 搜索空间显式声明（prompt / 结构 / 记忆 / 代码），算子按任务路由 | P0 |
| HITL 做成图内拦截器 Agent（带 mode 与字段映射），而非 if-else 分支 | P1 |
| 拓扑优先：goal → graph → 按节点物化 Agent，workflow 可存取复用 | P1 |
| 优化器可外挂到第三方框架（只改 prompt 也能涨分） | P2 |

### 改进建议

1. **【P0 · eval_observability】给进化引擎装 fitness 闭环**。现状：`learning_tracking.json` 只统计"改进项数量"，没有任何质量信号，所以"419 项改进、实施率 23%"本身无法证明有价值。应定义 `fitness = w1·单测通过率 + w2·任务成功率 + w3·(−token 成本)`，固定留出集（如 20 个历史任务），每次进化跑一次，**只在留出集上判定采纳**。
2. **【P0 · claw_integration】进化循环四段式**：数据集 → 评估器 → 算子 → 候选池。当前引擎是"读 README → 写建议入库"的单向管道，缺"改 → 测 → 留优"回流。补上 mutation 算子（改 prompt / 改编排图 / 改记忆策略）+ 候选池（islands 分区）+ 淘汰规则。
3. **【P1 · agent_orchestrator】HITL 拦截器化**：把"暂停等确认"从编排层 if-else 改为可插拔 `InterceptorAgent(目标Agent, 目标动作, PRE/POST, 批准/输入, 字段映射)`，图结构不变，默认关闭。
4. **【P1 · agent_orchestrator】拓扑优先 + workflow 可移植**：支持 `goal → graph → 物化 Agent`，并把 workflow 存成带 Agent 规格的单一文件，换模型配置即可复用（与 10-20 Stage Contract、10-24 Runtime 契约互补）。
5. **【P2 · model_scheduler】算子按任务类型路由**：不同优化器在不同任务胜出，把"选哪个优化器"交给 bandit，而不是全局固定一个。

### 判断

Claw 的进化引擎与 EvoAgentX 差一个**闭环**：Claw 有 419 条建议、23% 实施率，但没有任何一条被"测过是否更好"；EvoAgentX 只有 4 个算子，却每条改动都有前后分数。**建议本月只做一件事：把 419 项里挑 3 项，配上留出集做 A/B，拿到第一组真实 delta**——这比继续攒建议有用得多。
