# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-09-30

## [USER] 用户偏好
- 职业: 执法培训 + 诈骗园区调查 + CodeBuddy产品经理
- 技术栈: Python数据分析、爬虫、区块链追踪
- 风格: 简洁编号式指令、要结果、P0立即实施、结构化Markdown
- 禁止: 不问"是否需要"、AI-only分析、去AI化

## [PROJECT] Claw 学习追踪系统
- 目的: 通过GitHub高星项目迭代CodeBuddy能力
- 进度: 118项目 / 330改进项 / 实施率约29%
- 最新学习: shareAI-lab/learn-claude-code (⭐77.8K, 相关度42) — 2026-09-30
- agent_core: v2.1.0-p1-complete
- 模块: model_scheduler, unified_registry, progressive_loader, agent_orchestrator, context_injector, tool_registry, rag_engine, memory_system, eval_observability, claw_integration, storage, skill_system

## [EVOLUTION] 智能进化引擎
- 自动化ID: automation-1779863408739 | 每日09:00 | 细水长流1项目/日
- 日志: .workbuddy/evolution_log.jsonl | 仪表盘: docs/evolution-dashboard.html
- 已学60+高相关项目(完整见learning_tracking.json): EverOS(43)、context-mode(43)、nanobot(42)、fastmcp(41)、Raven(40)、TencentDB-Agent-Memory(40) 等

### 待实施改进(按模块分组)
**P0**
- agent_orchestrator: Spine脊柱、Sentinel主动引擎、IntentGate、Goal Continuation、ExecutionState、lane级小Agent、AgentLoop/Runner分离、AgentHook三层、Intervenable Runtime、编排数据面解耦、ACP适配器、AG-UI Protocol、工作流检查点、Human-in-the-Loop(暂停/确认机制)、Swarm编辑冲突通知(code shifting under feet检测)、Goal Loop独立评估器(evaluator审核stop提议+失败目标回退用户)
- memory_system: Cascade Daemon、正交五维分区、L0-L3分层管道、全可追溯链、Dream两阶段、Session Continuity、增量合并(delta分区不覆盖)、纠正层(立即生效)、语义记忆图(每turn向量化+cosine召回+被动提取+自动整合)
- context_injector: Shared State、Mermaid符号化压缩、Hash-Anchored Edit、Hierarchical AGENTS.md、Prompt版本化、Auto Compact、Tool Output Sandbox、Think-in-Code、Context Compact四步压缩顺序(先压tool results再总结历史)
- model_scheduler: 声明式路由、凭证池轮转、Category-Based Delegation、Model Presets、Agent声明式路由
- tool_registry: Skill-Embedded MCPs、输出Schema标准化、Meta-tools、工具语义搜索、后端多路冗余(首选+备选降级路由)、真实探测健康检查、MCP工具一键接入(uvx打包)、确定性指纹身份(seed→fingerprint)
- skill_system: SkillsHub市场、/meta-optimize、Markdown零锁定、Vibe DSL编译器、渐进式技能发现、自动学习管道(threads→Insights→reviewed Skills)
- storage: Markdown-as-Truth、StorageAdapter统一抽象
- claw_integration: Evolver自进化、OME离线反思、6阶段进化管道、Heartbeat主动任务
- eval_observability: 14可观测矩阵、LLM-as-Judge、TracingMiddleware、反进化审计、token_usage追踪
- agent_core: MiddlewareBase | progressive_loader: GEP基因编码

**P1**
- memory_system: User+Agent双轨、预热指数退避、无状态Reducer、记忆三子系统(selection/extraction/consolidation)
- rag_engine: Knowledge Wiki、BM25+Vector+RRF混合检索 | storage: SQLite+LanceDB本地栈
- eval_observability: 白盒记忆可调试、错误压缩+自愈、零代码信号采集
- tool_registry: human_contact工具化、Batch Execute、Per-session作用域、统一认证托管、可插拔channel架构(按能力域组织)、Backend Tool Rendering(工具返回UI组件)
- context_injector: 拥有上下文窗口、Intent-Driven Filter、显式上下文路由
- agent_orchestrator: 6-Hook补齐、before_llm/tool/on_exit钩子、自主spawn swarm+root/worker effort分离、Subagent上下文隔离(fresh messages[]+单一tool_result)
- skill_system: Skill资产化注册表、Universal Export、版本控制+回滚、双层结构(Work+Persona)
- model_scheduler: 轻量意图路由模型(≤4B)、统一OpenAI-compatible provider+WebSocket预预热+HTTPS回退
- claw_integration: 默认安全dry-run(安装/配置默认只读预览, 显式授权才写入)、代理与地理定位联动(timezone/locale/egress跟随)、密钥脱敏日志(日志不打印密钥值)+配置优先级链(flag>env>.env>default)、BYO Agent Any Channel(编排层与前端/channel解耦)

**P2**
- tool_registry: Skill确定性Schema、Provider Adapter层
- agent_orchestrator: Filter Chain护栏链、task-bound worktrees(每任务独立工作目录并行编辑)
- claw_integration: Pipeline部署层、专家知识蒸馏管道、能力层与实现层分离
- eval_observability: Product Analytics(从交互数据洞察agent行为与价值分布)、资源效率公开基准(RAM/首帧时间对比)

## [TECH] 关键环境
- Python 3.13.13 / Node 24.16.0 / Git 2.54.0
- GitHub API urllib直连 | Python用完整路径

## [SKILLSHUB]
- 路径: C:\Users\10127\WorkBuddy\SkillsHub\ (唯一权威)
- 新技能先存SkillsHub再同步~/.workbuddy/skills/

## [TEAM] 飞书协作群
- 成员: WorkBuddy + Claude Code + Hermes
- 协作: 自主分工 + 相互监督 + 交叉验证
