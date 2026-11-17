## 学习日期: 2026-11-17

### 学习项目: PrimeIntellect-ai/prime-agent
- URL: https://github.com/PrimeIntellect-ai/prime-agent
- Stars: 22,783 (Rust, 更新 11-17, MIT, 有 arXiv 论文 2608.23552)
- 定位: "A Self-Improving RLM Harness" — 面向长时运行编码/研究任务的开源 agent

### 选题依据
在 17 个候选中比较：`Human-Agent-Society/reef`(⭐7.8K, 持续自进化基础设施, 2026-11 正在重构 control plane+workers, main 上 recipe 可能跑不通)、`Asymptote-Labs/agent-beacon`(⭐3.5K, 跨 harness 记忆层, 与已学 claude-mem/Trail-Code/letta-code 重叠)。
prime-agent 相关度 38（关键词法，历轮次高）：它同时命中 Claw 三条长期空转的短板——②产出沉淀（499项无一变技能）、③进化≠自己改自己、⑥任务成功=验收通过，而且三者都有**可抄的机制**。与昨天 OpenShell 恰好成对：OpenShell 是真·进程外强制，prime-agent 诚实声明"worker/kernel 改善生命周期隔离但 **not a security sandbox**，不可信代码请跑外部 sandbox"。

### 核心发现
1. **RLM（递归语言模型）：上下文即变量，子 agent 即函数调用**。持久 Python REPL 是内置模型工具；文件操作、shell、工具调用、子 agent（`rlm.spawn(...)`）、上下文管理全部通过代码完成（prompt-as-a-variable / programmatic sub-agent calling）。上下文管理从"字符串拼接"升级为"可编程对象"。
2. **Continual Harness：`/refine` 把轨迹经验沉淀为可持久状态**。审视当前 trajectory，产出小的、evidence-backed 的更新，写入四类 supplemental 状态：补充提示、记忆、技能描述、可复用子 agent 规格。关键纪律：
   - **永不改写 immutable base system prompt**（改进有不可变边界）；
   - 只做局部更新，**默认 session-local**；
   - 有 refinement history + 快照回滚；
   - 明确"这不替代打包和审查真正可执行的技能"——自我改进与正式技能发布分开。
3. **quality gate 语义纪律（本轮最强一条）**：`/autonomous` 在 turn/token/time 预算内运行用户定义的质量门，README 原文——"**A passed gate checks only what that gate verifies; reaching a limit does not imply task success**"。门通过只说明门验的那件事过了；预算耗尽不等于任务成功。这一句直接是 Claw 短板⑥的解药。
4. **技能按来源分级执行权限**：用户配置里的 Python skill 导入 kernel（可执行）；仓库 skill 只提供 Markdown 指令（不自动执行代码）。来源是信任级别。
5. **agent 之间直接通信**：运行中的 agent 与保留的 subagent 可互相发现、交换消息、引导正在进行的工作，不必一切都路由经过用户。
6. **诚实的隔离边界声明**：worker/kernel 进程改善 lifecycle isolation 与 recovery，但**不是安全沙箱**；用一次性 clone / clean worktree / 外部 sandbox 承载不可信代码。
7. **长任务保持进展**：自动 compaction、persistent goals（`/goal`）、heartbeats、schedules、daemon 后台续跑与重连。
8. **终端程序状态协议 OSC 7501**：working / done / error / idle 四态，退出时不再上报（保留最后记录），只在终端询问后才写——与 Claw 消息四态呼应，但多了"问过才写"的克制。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| quality gate 通过 ≠ 任务成功；预算耗尽 ≠ success——gate 结论与任务结论强制分离 | P0 |
| `/refine`：轨迹经验 → supplement prompts/memory/skill描述/subagent规格，evidence-backed + 只改supplement不改immutable base + 快照回滚 | P0 |
| 技能按来源分级：用户Python skill可导入kernel执行 / 仓库Markdown skill仅指令不自动执行 | P1 |
| agent 间直接发现、直接通信、互相引导，不经用户中转 | P1 |
| 诚实标注能力边界：明确"lifecycle isolation 不是 sandbox"，不可信代码外置——与 OpenShell 对仗 | P1 |
| REPL 式持久控制环境：上下文即变量、子agent即函数调用、daemon续跑 | P2 |

### 改进建议
1. **[P0][eval_observability] quality gate 语义分离**：在交付验收闸门与 bounded autonomous 的结论里，把 `gate_passed` / `task_success` / `budget_exhausted` 作为**互不等价**的三个字段输出；判定词表禁止由 gate 通过推导 success，超时/超预算只记 budget_exhausted。现在 Claw 把"任务跑完"当"验收通过"，闸门失去意义（短板⑥⑪）。
2. **[P0][skill_system] 落地 Continual Harness 式 `/refine`**：让每轮结束把可复用经验精炼为四类 supplement（补充提示/记忆/技能描述/子agent规格），每条附**触发它的轨迹证据**，写 refinement history + 快照；**永不改写 SOUL.md/CLAUDE.md 等不可变基线**。这是把 499 条"文字改进"变成可执行技能的具体通道，同时给短板③一个不可变边界。
3. **[P1][skill_system] 技能按来源分级执行权**：用户级 Python 技能可导入执行、仓库/Marketplace 技能默认仅作 Markdown 指令不自动执行；来源即信任级别，与已有的 includes-glob 签名体系叠加。对上短板④供应链信任。
4. **[P1][agent_orchestrator] 运行中 agent 直接互发现互引导**：在现有消息四态 + Foreman/peer 路由之上，补 agent 主动发现彼此并向"正在进行的工作"发 steer 消息的能力，去掉"凡事经用户中转"的瓶颈。
5. **[P1][eval_observability] 能力边界诚实声明**：在所有隔离/沙箱类能力旁强制标注"这是 lifecycle isolation 还是真正的 sandbox"，不满足进程外强制的一律不得称 sandbox。与昨天 OpenShell 形成一致口径。
6. **[P2][claw_integration] REPL 式持久控制环境**：把上下文管理从字符串拼接升级为可编程对象（变量化上下文 + 子 agent 作为函数），配合已有 daemon/Heartbeat/后台续跑。

### 判断
prime-agent 与 OpenShell 构成一组漂亮的互补：一个证明"强制点必须在进程外"，一个坦白"我的隔离不是 sandbox"。但 prime-agent 独有的贡献是**自我改进的三条纪律**——只改 supplement 不改 base、每条更新有轨迹证据、gate 通过不等于成功。这三条正好把 Claw 空转最久的两条短板（②产出沉淀、⑥验收等价）从"口号"变成"可落地的字段和流程"。
短板⑥补注：已找到可抄范式 = quality gate 语义分离（gate_passed / task_success / budget_exhausted 三态不等价）。
不引入整套（Rust + 持久 REPL 内核，与 Claw 纯 Python 栈差异大）；取它的三条纪律与一个 gate 字段设计。
