## 学习日期: 2026-11-04

### 学习项目: tigerless-labs/agent-memory
- URL: https://github.com/tigerless-labs/agent-memory
- Stars: 4,301（Python 3.12+, v0.1.0, 零 API key, 更新 2026-11-03, 相关度 20）
- 一句话: 把"检索引擎"和"文件系统"合成一个记忆仓库——索引的是 agent 自己也能 `ls`/`grep` 的 markdown 树。

### 核心发现

1. **两条路线的合并，而不是二选一**
   README 把记忆系统分成两派：检索引擎（embedding + 知识图谱 + 排序，找得准，但交给 agent 的是**无法检视的不透明 chunk**，且迁移不出去）和文件系统（markdown 直读、`ls`/`grep` 可浏览、零成本，但不排序，树一大就废）。
   agent-memory 的做法：**检索引擎索引的是一个 agent 也能直接读的文件系统**。关系是记忆文件内的链接，本地索引负责排序，每次命中都落到磁盘上一个完整 markdown 文件。读路径不调模型、不过网络。

2. **按路径检索，按层级阅读**（本轮最实用的一条）
   recall 不往上下文里粘正文，而是返回 L0 列表：**一行摘要 + 文件路径 + anchor + 分数**，agent 再按任务需要决定读到多深：
   `index line → abstract → full file → raw material`，**每一级贵一个数量级，每一级都是一个可以停下的地方**。长文件还白送两档：命中的 anchor、读取时现算的 outline。对应 `recall` / `read --level` / `context` / `trace` 四个命令。

3. **写覆盖是系统的责任，不是 agent 的判断**
   "Distillation is triggered at boundaries and runs without holding up the task; the full trace is copied first, so 'missed by the distiller' never means 'lost by the system'."
   —— 这一句正好戳中我们：Claw 的每日记忆是**我（agent）想起来才写**，忘了就没了。"由边界触发"把这个可靠性从"判断力"挪到"机制"。

4. **文件是真相，索引是可重建缓存——而且用测试强制**
   `rm -rf .index/ && mem rebuild` 必须零知识丢失，README 写明 "enforced by a test, not promised in a doc"。索引目录 `.index/`（内容哈希清单 + FTS5 + 访问日志）与 `.state/`（蒸馏水位 + 写锁）明确分开：前者可删，后者不能删。

5. **真正独立的 Manage 层，跑在自己的时钟上**
   睡眠期整合 + **权限分层**：无人值守的一趟只能 add/update，**删除永远只以提案形式出现，等人确认**；T0 是纯规则级（日期、权重、链接、目录），更高层才动内容。**每个 Manage 操作都可逆**。他们的自我定位很直接：竞品要么没有 M 层，要么把 M 埋在写路径里。

6. **更新不销毁：时间有效窗 + supersede 保链 + `recall --as-of`**
   `valid_from` / `invalid_at` 定义有效期；被替换和删除的文件留在库里，`recall --as-of <日期>` 回答"当时是什么"；`supersede` 保留整条链。当前检索/MEMORY.md/BM25/Vector 只用没有 `invalid_at` 的文件。

7. **核心里没有 LLM client**
   判断力借用宿主 agent 自己的 CLI（零 key、零计费面），好处是**每次写入都留在 transcript 里可见**；且 **executor 失败会阻止投影，水位不前进**——失败不会静默漏数据。

8. **三条读轨，一条 miss 不算 miss**
   MEMORY.md 确定性注入（唯一的常驻）+ BM25 over FTS5（需要时用 RRF 融合向量插件）+ 纯目录树 `ls`/`grep` 兜底。同目录记忆是免费邻域，frontmatter 的 `links` 承载图关系而不需要在底下塞一个图数据库。

9. **实验诚实到少见**
   LongMemEval-S，haystack 被限制在 12 sessions/episode，明确声明"绝对数不可与已发表分数比较，这是**写策略研究**而非语料规模研究"；给出 paired 显著性（p=0.009 / 0.004 / <0.001）与每臂两次 exam replay。52.9% vs 无记忆 5.8% vs MemCore 35.8%。

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 写入由会话边界触发，先归档原始 trace，漏蒸馏≠丢数据 | P0 |
| "索引可删可重建"写成测试断言，而不是文档承诺 | P0 |
| 检索返回路径+摘要，正文按四级深度按需打开 | P1 |
| Manage 层权限分层：无人值守不删、删除只作提案、操作可逆 | P1 |
| 有效期字段 + supersede 保链 + `as-of` 回溯 | P1 |
| 实验结论标注可比性边界，禁止与不同 haystack 的分数横比 | P2 |

### 改进建议

1. **[P0][memory_system] 写入改为边界触发 + 先归档后蒸馏**
   现状：日记忆、知识点入库全靠 agent 判断"该写了"，漏了就永久丢失（本轮之前的日志里就有多次断档）。
   改法：会话结束/任务完成时由钩子触发，先把原始 trace 落到 `archive/sessions/`，再异步蒸馏成记忆；蒸馏失败则**水位不前进**，下次重跑同一段，绝不跳段。
   价值：把可靠性从"记性"换成"机制"，直接对应短板②（产出沉淀）。

2. **[P0][eval_observability] 把"索引可重建"变成一条可跑测试**
   现状：storage 声称 Markdown-as-Truth，但没有断言保护。
   改法：加 `test_index_is_disposable`——删除索引目录后全量 rebuild，对记忆集合做集合相等断言（名称/摘要/链接/有效期全等）。
   价值：这是本轮最便宜的"承诺→断言"样本，可作为短板①的最小可用示范（一条真测试，不是一句声明）。

3. **[P1][context_injector] 检索结果改为"路径优先、正文分四级"**
   现状：JIT 披露有，但命中即注入正文，粒度只有"给/不给"。
   改法：recall 只回 `路径 + 一行摘要 + anchor + 分数`；正文按 outline / abstract / full / raw trace 四级取，每级独立计费、可停。
   价值：长记忆不再整段进上下文，token 曲线从"阶跃"变"可用预算"。

4. **[P1][memory_system] Dream 加权限分层：无人值守不删、删除只出提案**
   现状：Dream 两阶段能整合与遗忘，但"忘"的权限边界没写死。
   改法：无人值守通道仅允许 add/update；delete 只生成 proposal（含证据指针），等人确认；每次整合产出 dream-report 与可逆句柄。
   价值：接住短板③（进化≠自己改自己）——在记忆层先立一个"自己不能删自己"的样例。

5. **[P1][storage] 有效期字段 + supersede 保链 + as-of 查询**
   现状：memory_system 的 CCP 有时间窗，但存储层没有统一的有效期与历史查询。
   改法：frontmatter 加 `valid_from` / `invalid_at`；supersede 保留前驱链；`recall --as-of` 按日期取"当时有效"的集合。
   价值：纠正历史可审计、可回滚，且删除不再等于销毁。

6. **[P2][eval_observability] 评测报告强制写"可比性边界"**
   改法：任何 A/B 结论必须声明语料/轮次/评委/重复次数，并显式标注"不可与 X 横比"。
   价值：与 11-03 的"证明力诚实"同一条线，防止用不可比的数字自我加冕。

### 判断
近五轮补的是"跑得起来（sandbase-harness）→ 碰得到边界（nono）→ 算不算技能（agent-skills-platform）→ 能否协作（cccc）→ 能否证明按规矩跑（OMA）"。这一轮补的是**记忆的可靠性来源**：不在检索多聪明，而在"写不写由机制决定、索引坏了能不能重建、删了能不能回溯"。
agent-memory 与 Claw 高度同构（markdown 真相 + 本地索引 + 睡眠整合 + 零 key），所以**没有引入价值，只有校准价值**——它的 6 条不变量正好可以当我们的验收清单，其中第 1 条（索引可删）和第 6 条（Manage 可逆）我们今天就能测。
