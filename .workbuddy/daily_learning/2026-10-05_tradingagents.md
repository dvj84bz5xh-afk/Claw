## 学习日期: 2026-10-05

### 学习项目: TauricResearch/TradingAgents
- URL: https://github.com/TauricResearch/TradingAgents
- Stars: 109,782 (Python)
- 相关度: 38 (多Agent金融交易框架, 角色分工+辩论决策+分层模型路由)

### 核心发现
1. **多Agent角色分工 + 动态辩论决策** — 基本面分析师/情绪专家/技术分析师/交易员/风控团队各司其职, 产出后动态讨论制衡, 才定最终策略 (镜像真实交易公司)。
2. **provider per model tier (分层模型路由)** — managers 与 analysts 运行在不同模型, 强模型管决策、便宜模型管分析, 成本与能力分层匹配。
3. **point-in-time integrity (时间点完整性)** — 每个 dated path 严格按时间点取数, 回测只看分析日期前已发布的数据, 杜绝 look-ahead 未来信息泄漏。
4. **checkpoint resume 断点续跑** — LangGraph checkpoint + graph-shape-aware, 工作流任意节点中断后从检查点恢复, 不重复计算。
5. **decision-log memory (决策日志记忆)** — 持久化决策轨迹, 支持回溯审计与模式学习。
6. **structured-output agents** — 研究员/交易员/组合经理输出结构化, 便于下游消费与校验。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| 多Agent辩论式决策 + 风险团队制衡 (交叉验证提升决策质量) | P0 |
| provider per model tier 按角色层级路由不同模型 | P0 |
| point-in-time integrity 时间点完整性 (杜绝未来信息泄漏) | P1 |
| checkpoint resume 断点续跑 (graph-shape-aware) | P1 |
| decision-log memory 决策日志记忆 (回溯审计+模式学习) | P2 |

### 改进建议
1. agent_orchestrator: 引入多Agent辩论式决策机制 — 子Agent产出后由审核方(如风控/评估Agent)交叉制衡、动态辩论后才定案, 提升复杂决策质量。
2. model_scheduler: 引入 provider per model tier — 按Agent角色层级路由不同模型(决策层强模型、执行/分析层轻量模型), 成本与能力分层匹配。
3. eval_observability: 引入 point-in-time integrity — 评估/回测严格按时间点取数, 只看"当时已发布"数据, 杜绝 look-ahead 未来信息泄漏导致的虚高指标。
4. agent_orchestrator: 引入 checkpoint resume 断点续跑 — 工作流任意节点中断后从检查点恢复(graph-shape-aware), 避免重复计算与状态丢失。
5. memory_system: 引入 decision-log memory — 持久化决策轨迹(输入/推理/结论), 支持回溯审计与模式学习。
