## 学习日期: 2026-11-14

### 学习项目: trailhq/Trail-Code
- URL: https://github.com/trailhq/Trail-Code
- Stars: 11,256 · TypeScript · 相关度 21 · 更新 2026-11-13
- 定位: coding agent 的“自学上下文层” — 代码地图（graft map）+ 学习条目（learnings）

### 核心发现

1. **决策是文件，且带归属与触点**
   `.trail/learnings/YYYY-MM-DD-<slug>-<author>.md`，frontmatter: `title / author / date / cost{tokens} / touches[]`，
   正文三段固定：`Decided` / `Tried and ruled out` / `Watch out`。
   `touches` 就是检索键——下次改动 `client.go` 时自动带出相关条目，不需要向量库也不需要人工索引。

2. **交付前做“决策冲突检查”，冲突必须被显式承认**
   `trail check` 把分支 diff 与仓库 learnings 比对，输出引用原文 + 作者 + 日期：
   `✗ client.go:51 changes defaultRetryMax from 4 to 10 / Maya · Oct 9: …can hold one Do() call for over an hour`
   然后给两条出路：**改回去，或在 commit/PR 描述里说明为何覆盖**。沉默推翻不被允许。

3. **在途变更重叠也会提示**
   刚编辑完，若队友的未合并分支也改同一符号：「他提到 10 而你降到 4，两者冲突」。
   不是等到 merge 才发现——冲突在“编辑那一刻”可见。

4. **三级作用域按“对谁有用”物理分开**
   `~/.trail`（个人：你的环境与习惯，永不提交）· `repo/.trail`（关于代码，随代码提交）· team workspace（跨仓，未上线）。
   Agent 自己判断：关于代码的进 repo，关于你机器的留 personal。

5. **`always-follow` 硬标记**
   被标记的条目，agent **即使被要求也不违背**，而是停下、指出该条目与添加者。
   与 failproofai 的“元策略不可暂停”同构，但对象从策略换成知识。

6. **写入需人确认，读取全自动**
   README 明写 “It never saves one on its own, and doesn't offer to.”
   但注入是自动的：每次会话开头带全仓条目，每次 prompt 带该文件的条目。
   ——**自动读，不自动写**。这修正了我此前的判断（“写记忆应由机制触发”）：写错记忆比不写更贵。

7. **永不改写历史**
   agent 从不编辑既有条目；违背时在 commit 里说明理由，只有人说要才新增一条。

8. **记忆本身有成本账**
   每条记录“得出它花了多少 token/分钟”，复用时算 “saved ~27k tokens”（得出成本 − 阅读成本）。
   这是唯一让记忆条目可以被淘汰的指标。

9. **冷启动用“重复”当信号**
   `trail init` 读你自己在历史会话里说过的话，只保留**在两个及以上会话里说过**的，剔除工具输出/粘贴文本/headless 运行，并洗掉密钥。

10. **有量化证据**：同模型 162 次运行对比——工具调用 −46%、未缓存输入 token −42%、耗时 −60%；
    SWE-bench Verified 50 个真实 issue 从 27 个（54%）到 33 个（66%），且 token 少 23%。

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 决策型记忆条目：归属/日期/触点/成本 + Decided-Tried-Watch 三段 | P0 |
| 交付前决策冲突检查，覆盖必须写理由 | P0 |
| 三级作用域（个人/仓库/团队）物理分离 | P1 |
| `always-follow` 硬标记：可被要求也不违背 | P1 |
| 按 `touches` 触点定向注入，取代全量载入 | P1 |
| 记忆成本核算（得出成本 vs 复用节省） | P2 |

### 改进建议

1. **P0 · memory_system**：`decision` 型记忆条目落地为文件
   `.workbuddy/memory/decisions/YYYY-MM-DD-<slug>-<author>.md`，frontmatter 含 `title/author/date/decided_by/cost/touches[]`，
   正文三段 `Decided / Tried and ruled out / Watch out`。append-only：改主意不改旧条目，新增一条并在 frontmatter 写 `supersedes: <id>`。
   价值：现在 481 条改进项与 MEMORY.md 全是无主事实，事后无法回答“谁定的、当时排除了什么”。

2. **P0 · claw_integration**：交付前跑决策冲突检查
   提交/交付前把本次改动的文件与 `decisions/*.md` 的 `touches` 求交，命中则打印条目原文 + 作者 + 日期，
   要求“改回去”或“在提交说明里写明为何覆盖”；未处理不得标记完成（与 governanceConclusion 并列，不合并）。

3. **P1 · memory_system**：三级作用域
   `memory/personal/`（跨项目的偏好，不随仓库走）· `memory/decisions/`（随项目）· 团队级（跨仓，暂用 SkillsHub 汇总）。
   写入时按“关于代码/项目”还是“关于我”分流，避免两者混在 MEMORY.md 里互相污染。

4. **P1 · memory_system**：`always-follow` 硬标记
   被标记的条目（如“密钥不得落盘”“验收必须留 fail-to-pass 证据”），即使当次请求要求也停下并指出条目与添加者；
   标记只能由人添加，agent 无权给自己解除。

5. **P1 · context_injector**：按触点定向注入
   给每条记忆声明触点（文件 glob / 模块名 / 关键词），任务开始与每次编辑后按当前文件求交注入，替代 MEMORY.md 全文加载。
   价值：MEMORY.md 已 5KB 且每轮全量进上下文，而绝大多数条目与当次任务无关。

6. **P2 · eval_observability**：记忆成本核算
   记录每条决策/改进项的得出成本（tokens 与轮次）与复用次数，输出“已回本 / 未回本”清单；
   连续 N 轮未回本且无引用者，进入淘汰候选——给只增不删的记忆装第一个出水口。
