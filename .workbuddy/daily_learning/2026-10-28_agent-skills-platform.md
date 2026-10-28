## 学习日期: 2026-10-28

### 学习项目: FrancyJGLisboa/agent-skills-platform
- URL: https://github.com/FrancyJGLisboa/agent-skills-platform
- Stars: 2,407 ⭐ (Python, MIT, v6.1.0, 更新 2026-09-15)
- 一句话: 把"人已经在做的工作"变成**经过测试、可安装、可治理的技能包**——不是技能市场，是技能工厂 + 治理流水线

### 核心发现

1. **技能包是五件套，不是一份 SKILL.md**：instructions + 按需脚本 + evals + 安全检查 + **代表性 run 记录** + 纠错路径。发布前必须齐；只写 prompt 的东西不算技能。
2. **三层分离，既防上下文膨胀又防"自己改自己"**：
   - `raw/` — 分类落盘的运行证据
   - `wiki/` — 反复出现的问题沉淀成**证据链接的草稿模式**（evidence-linked draft patterns）
   - 可执行技能 — **只有经过单独验证的变更才能更新它**
   官方原话：这是 *governed maintenance record, not autonomous self-modification*。运行证据刻意**不进入**运行时 prompt。
3. **技能按"图"整体校验，不是按文件**：skill graph 把 instructions / scripts / evals / expected outputs 连成一体，并强制两条结构不变量：
   - `every_expected_is_reachable` — 每个预期结果都必须有可测路径
   - `deterministic_multistep_has_orchestrator` — 每个可预测的多步流程必须有唯一可靠入口
   四项检查（specification / pipeline / security / evaluation schema）**并行**跑，最后再用一次代表性 run 证明"真的产出有用结果"。
4. **Semantic Recon + 钉住的数据契约**：流程一旦涉及 API / DB / MCP / 代码库 / 结构化文件，**实现之前**自动做语义侦察并钉一份 data contract；想跳过必须显式 `--without-semantic-recon`（仅限本地无源安装）。
5. **三权分立**：SME 拥有业务含义并批准结果 → Creator 构建与验证 → Marketplace 运营方治理与发布 → 同事只安装已批准版本。**没有任何一个角色同时是"提出者、批准者、验收者"**。
6. **Caliper：按运行时认证**。`reliability` 在每个已安装的 agent runtime 里把技能跑 k 次，**只认证 agent 实际发现并遵循了什么**——不是"我们写了文档说支持"。
7. **定位一句话说清了边界**：RAG 供知识，MCP 供能力，harness 供执行，**skill 把它们组织成一条通向已验证结果的治理路径**。技能本身不是 RAG、不是 MCP server、不是 runtime。

### 可借鉴点

| 优点 | 优先级 |
|---|---|
| 技能包五件套（含 evals / 安全检查 / 代表性 run），缺项不得发布 | P0 |
| raw → wiki → executable 三层分离，证据不入运行时上下文，只有验证过的变更能改可执行层 | P0 |
| 结构不变量当门禁（每个预期可达 / 多步有唯一入口）+ 四检查并行 | P1 |
| 实现前 Semantic Recon + 钉住数据契约 | P1 |
| 按运行时认证（k 次实跑，只认证被实际发现的部分） | P2 |

### 改进建议

1. **【P0 · skill_system】技能包五件套 + 发布门禁**。当前 SkillsHub 里的技能实质只有 `SKILL.md` 文本，没有 evals、没有安全检查、没有一次代表性运行记录——所以"82 个技能"这个数字无法证明任何一个能用。应定义技能包最小结构：`SKILL.md` + `evals/`（至少 3 条正例 + 2 条反例）+ `security.md`（能碰什么、不能碰什么）+ `run-record.md`（一次真实运行的输入/输出/判定）+ 纠错路径；**缺任一项状态只能是 draft，不得标 published**。
2. **【P0 · memory_system】三层分离：raw → wiki → executable**。这是对 Claw 进化引擎最重要的一条约束。现状：进化引擎可以读会话、写建议、并把建议标成"已实施"，提出者=批准者=验收者。应改为：会话证据分类落 `raw/`；反复出现的问题写 `wiki/` 且必须链回证据；**可执行技能（SKILL.md 正文）只能由"单独验证过的变更"更新**，验证记录留在 `run-record.md`。明确写下：这是受治理的维护记录，不是自主自我修改。
3. **【P1 · eval_observability】两条结构不变量当门禁**。`every_expected_is_reachable`：技能里每个声明的预期结果都要有对应 eval 覆盖；`deterministic_multistep_has_orchestrator`：凡是可预测的多步流程必须有唯一入口，不允许"文档里描述了三步但入口四处散落"。四项检查（规范/流水线/安全/评估 schema）并行跑完再判。
4. **【P1 · tool_registry】Semantic Recon + pinned data contract**。凡新增工具要接外部依赖（API/DB/MCP/代码库），实现前先做一次语义侦察，产出并钉住数据契约（字段名、类型、可空性、来源、变更策略）；契约变了就必须重新侦察，不允许静默漂移。
5. **【P2 · claw_integration】按运行时认证**。同一个技能在每类 harness（WorkBuddy / Claude Code / Codex）里各跑 k 次，认证结论只覆盖"被实际发现并遵循的部分"，未被发现的功能标 unsupported 而不是"应该可以"。

### 判断

这三个项目连起来是一条完整链路，Claw 缺的正是最后一段：
- 10-25 EvoAgentX → **怎么判断改动是否更好**（量化 fitness）
- 10-27 trpc-agent-go → **改进怎么沉淀成资产**（评审门 → SKILL.md）
- 10-28 本项目 → **沉淀出来的资产怎么证明可用**（五件套 + 结构不变量 + 代表性 run + 按运行时认证）

而且它给出了一条 Claw 一直没想清楚的边界：**"进化"不等于"AI 自己改自己"**。证据可以自动收集、草稿可以自动生成，但可执行层必须由单独验证过的变更推动。把这条写进设计，比再加 100 条改进建议都值钱。

**下周唯一动作**（承 10-27）：建 `managed_skills/`，把 3 项已实施成果按**五件套**写成技能包，跑一次代表性 run，拿到第一份"技能可用"的证据。
