## 学习日期: 2026-10-19

### 学习项目: rohitg00/pro-workflow
- URL: https://github.com/rohitg00/pro-workflow
- Stars: 2,918
- 语言: JavaScript (Node CLI + SQLite) | License: MIT
- 规模: 41 skills / 8 agents / 23 commands / 33 hook scripts across 22 hook events

### 项目概述
把"每次会话都要重新教一遍"的痛点做成基础设施：单个 SQLite store 承载**自我纠错记忆** + **持久化 FTS5 研究 wiki（知识面）** + **质量门禁 hooks**。核心承诺是"纠正一次，永不重犯"——50 个会话后纠正率趋近于零。

### 核心发现
1. **纠错即规则（Self-correction memory）**：一句 "Don't mock the database in tests" → 提议规则 → 用户批准 → 存入 SQLite（FTS5 索引）→ 未来每次 `SessionStart` 自动加载。`/insights` 提供**纠错热力图 + 纠正率趋势**，用"纠正次数下降曲线"作为学习效果的唯一 KPI。
2. **免命令自动捕获**：`Stop` hook 的 `learn-capture.js` 解析输出里的 `[LEARN]` 块自动入库，不依赖用户记得敲 `/learn-rule`。捕获与检索彻底解耦。
3. **知识面（Knowledge Plane）**：wiki 以 Markdown 落盘 + FTS5 影子索引，`UserPromptSubmit` 在提示命中索引时**自动注入 top-3 命中片段**；wiki 可按 research/paper/domain/person/org/incident 等 9 种"flavor"初始化，路径穿越防护。
4. **自主研究环的工程治理**：`wiki-research-loop` = 预算封顶的 BFS + 可插拔 fetcher（web/arXiv/GitHub/自定义）+ **收敛检测** + **原子 seed 认领**（防并发重复抓取）+ `try/finally` 状态守卫 + **全局 kill switch（`touch ~/.pro-workflow/STOP`）**。
5. **压缩感知状态保全**：`PreCompact` 保存关键上下文摘要 → `PostCompact` 回注，解决"压缩后 learnings 蒸发、错误重犯"。
6. **成本/权限/工具三类运维技能**：`mcp-audit`（逐 MCP server 的 token 开销排行）、`permission-tuner`（分析 PermissionDenied 模式 → 自动生成 allow/deny 规则）、`token-efficiency`（反谄媚 + 工具调用预算 + read-before-write）、`reread-tracker`（同一未变文件重复 Read 时提醒/可阻断）。
7. **架构分层**：Command → Agent → Skill 三层，统一压在一个 SQLite store 上；知识面与学习规则共用同一个库，避免"记忆/知识/技能三套存储各说各话"。

### 可借鉴点
| 优点 | 优先级 | 说明 |
|------|--------|------|
| `[LEARN]` 块自动捕获 + SessionStart 全量注入纠错规则 | P0 | Claw 已有"纠正层立即生效"，但缺**免命令捕获**与**纠正率度量** |
| PreCompact/PostCompact 双钩子（存摘要→回注） | P0 | Claw 有 Auto Compact，压缩后无回注，长会话易丢约束 |
| MCP server 级 token 开销审计 | P1 | Claw 已有 MCP 按需检索，缺"谁最贵"的量化视图 |
| PermissionDenied 模式挖掘 → 自动生成 allow/deny 规则 | P1 | 降低审批疲劳，且规则库可持续收敛 |
| 自主循环四件套（预算封顶/收敛检测/原子认领/STOP） | P2 | 可直接套用到 Claw 的自动研究、自动整理、自动学习循环 |

### 改进建议
1. **[P0][memory_system] 纠错规则库 + 纠正率度量**：Stop 钩子解析 `[LEARN]` 块自动入库（无需用户显式命令）；规则带 scope（全局/项目）、命中计数、最后命中时间；SessionStart 按相关度注入 top-N；`/insights` 输出纠正率周趋势，作为进化引擎的北极星指标。
2. **[P0][context_injector] 压缩前后状态保全双钩子**：PreCompact 抽取"当前目标/已确认约束/未完成项/关键文件"存快照，PostCompact 以固定块回注；避免长任务在压缩后重复踩坑。
3. **[P1][tool_registry] MCP 开销审计**：统计每个 MCP server 的工具数 × schema token，输出排行榜与精简建议（禁用/懒加载/合并），把"按需检索"从策略变成可度量结果。
4. **[P1][claw_integration] 权限拒绝模式分析器**：聚合 PermissionDenied 事件 → 聚类高频拒绝 → 生成候选 allow/deny 规则并附证据，人工一键采纳。
5. **[P2][eval_observability] 自主循环治理模板**：所有自主动作（研究/整理/学习）统一走"预算封顶 + 收敛检测 + 原子任务认领 + 全局 STOP 文件"，并提供单条命令熔断。

### 对 Claw 的定位判断
Claw 的记忆与技能体系（Skill-as-Memory、Disclosure Routing、四实体图、技能路由）在**表达能力**上已超过该项目；差距在**闭环验证与运维面**——缺少"纠正率"这类可下降的量化指标，以及压缩/权限/MCP 三类日常运维的可观测工具。建议优先补 P0 两项，把"学到了"变成"可测量地少犯错"。
