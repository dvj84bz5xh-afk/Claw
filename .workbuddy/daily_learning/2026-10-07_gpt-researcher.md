## 学习日期: 2026-10-07

### 学习项目: assafelovic/gpt-researcher
- URL: https://github.com/assafelovic/gpt-researcher
- Stars: 29,930 (Python)
- 相关度: 38 (自主深度研究Agent, 多Agent研究管道 + 来源追踪)

### 核心发现
1. **Planner-Executor-Publisher 三段式架构** — planner 拆解研究问题 → 并行 executor(crawler) 采集信息 → publisher 聚合汇总成报告。
2. **source-tracking 来源追踪** — 每个资源摘要带引用来源, 过滤聚合后保证事实准确、无偏见、可追溯。
3. **并行化 agent 工作** — 多个 crawler agent 并行采集, 显著提高研究速度与稳定性。
4. **Plan-and-Solve + RAG 结合** — 先规划子问题再逐个检索求解, 突破 LLM token 限制生成长报告。
5. **任务特定 agent 动态创建** — 基于研究查询动态生成领域定制 agent(支持 web + 本地文档)。
6. **反幻觉设计** — 针对 LLM 过时知识、token 限制、单一信源偏见等痛点逐一解决。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| Planner-Executor-Publisher 三段式编排 (规划/执行/发布分离) | P0 |
| source-tracking 来源追踪 + 引用 (保证事实准确可追溯) | P0 |
| 并行化 executor agent 采集 | P1 |
| Plan-and-Solve 规划分解 (突破上下文限制) | P1 |
| 任务特定 agent 动态创建 (领域定制) | P2 |

### 改进建议
1. agent_orchestrator: 引入 Planner-Executor-Publisher 三段式编排 — 规划Agent拆解任务、执行Agent并行采集、发布Agent聚合, 用于研究报告/长文档生成流水线。
2. rag_engine: 引入 source-tracking 来源追踪 — 每个检索结果摘要强制带引用来源, 过滤聚合后保证事实准确、可追溯、无偏见。
3. agent_orchestrator: 引入并行化 executor agent 采集 — 多个执行Agent并行工作收集信息, 显著提高吞吐与稳定性。
4. context_injector: 引入 Plan-and-Solve 规划分解 — 先规划子问题再逐个检索求解, 突破单次上下文 token 限制生成超长内容。
5. skill_system: 引入任务特定 agent 动态创建 — 基于查询动态生成领域定制 agent, 支持领域专属研究。
