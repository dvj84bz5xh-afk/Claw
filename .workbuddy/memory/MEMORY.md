# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-10-10

## [USER] 用户偏好
- 职业: 执法培训 + 诈骗园区调查 + CodeBuddy产品经理
- 技术栈: Python数据分析、爬虫、区块链追踪
- 风格: 简洁编号式指令、要结果、P0立即实施、结构化Markdown
- 禁止: 不问"是否需要"、AI-only分析、去AI化

## [PROJECT] Claw 学习追踪系统
- 目的: 通过GitHub高星项目迭代CodeBuddy能力
- 进度: 128项目 / 380改进项 / 实施率约25%
- 最新学习: Dataojitori/nocturne_memory (⭐1.4K, 相关度40) — 2026-10-10
- agent_core: v2.1.0-p1-complete
- 模块: model_scheduler, unified_registry, progressive_loader, agent_orchestrator, context_injector, tool_registry, rag_engine, memory_system, eval_observability, claw_integration, storage, skill_system

## [EVOLUTION] 智能进化引擎
- 自动化ID: automation-1779863408739 | 每日09:00 | 细水长流1项目/日
- 日志: .workbuddy/evolution_log.jsonl | 仪表盘: docs/evolution-dashboard.html
- 已学60+高相关项目(完整见learning_tracking.json): EverOS(43)、context-mode(43)、nanobot(42)、fastmcp(41)、Raven(40)、TencentDB-Agent-Memory(40) 等

### 待实施改进(按模块分组)
**P0**
- agent_orchestrator: Spine脊柱、Sentinel主动引擎、IntentGate、Goal Continuation、ExecutionState、lane级小Agent、AgentLoop/Runner分离、AgentHook三层、Intervenable Runtime、编排数据面解耦、ACP适配器、AG-UI Protocol、工作流检查点、Human-in-the-Loop(暂停/确认机制)、Swarm编辑冲突通知(code shifting under feet检测)、Goal Loop独立评估器(evaluator审核stop提议+失败目标回退用户)、多Agent辩论式决策+风险团队制衡(子Agent产出后由审核方交叉制衡、动态辩论后定案)、Planner-Executor-Publisher三段式编排(规划Agent拆解任务、执行Agent并行采集、发布Agent聚合, 用于研究报告/长文档生成流水线)、ACP统一协议抽象层(用ACP统一接入第三方agent如Claude Code/Codex作为Claw执行后端, 编排层与agent实现彻底解耦)
- memory_system: Cascade Daemon、正交五维分区、L0-L3分层管道、全可追溯链、Dream两阶段、Session Continuity、增量合并(delta分区不覆盖)、纠正层(立即生效)、语义记忆图(每turn向量化+cosine召回+被动提取+自动整合)、时间序+主题序双系统互补(何时发生走时间序记忆, 关于什么走主题知识库)、Skill-as-Memory统一记忆层(记忆即技能Markdown文件, 用SKILL.md定义schema/命名/文件布局, 自动extraction/routing/writing, 人类可读可编辑可分享, 统一memory_system与skill_system)、条件触发路由(Disclosure Routing每条记忆绑定人类可读触发条件按当前情境精准注入, 替代cosine盲盒召回)、Node-Memory-Edge-Path四实体图模型(身份层Node/UUID永久不变+内容层Memory版本快照deprecated/migrated_to一键回滚任意历史版本+关系层Edge有向关系priority/disclosure+路由层Path URI, 四层分离)
- rag_engine: 按主题知识库+可视化知识图谱(自动策展Markdown wiki按主题组织, 维护交叉引用, 交互式图谱浏览)、source-tracking来源追踪(每个检索结果摘要强制带引用来源, 过滤聚合后保证事实准确可追溯无偏见)
- context_injector: Shared State、Mermaid符号化压缩、Hash-Anchored Edit、Hierarchical AGENTS.md、Prompt版本化、Auto Compact、Tool Output Sandbox、Think-in-Code、Context Compact四步压缩顺序(先压tool results再总结历史)
- model_scheduler: 声明式路由、凭证池轮转、Category-Based Delegation、Model Presets、Agent声明式路由、provider per model tier(按Agent角色层级路由不同模型: 决策层强模型+执行/分析层轻量模型)
- tool_registry: Skill-Embedded MCPs、输出Schema标准化、Meta-tools、工具语义搜索、后端多路冗余(首选+备选降级路由)、真实探测健康检查、MCP工具一键接入(uvx打包)、确定性指纹身份(seed→fingerprint)、Protected core+agent-writable workspace(核心受保护不可变, 扩展区agent安全自扩展)、工具三分类(感知/执行/协作)+主动工具发现(agent主动检索发现可用工具而非被动全量注入)、符号级代码工具抽象(基于符号而非行号/文本, find symbol/referencing/type hierarchy)、符号化编辑(replace symbol body/safe delete, 省token更可靠)
- skill_system: SkillsHub市场、/meta-optimize、Markdown零锁定、Vibe DSL编译器、渐进式技能发现、自动学习管道(threads→Insights→reviewed Skills)、任务结果触发蒸馏学习(任务complete/failed触发→LLM蒸馏what worked/failed+用户偏好→Skill Agent决定路由到已有或新建skill)
- storage: Markdown-as-Truth、StorageAdapter统一抽象
- claw_integration: Evolver自进化、OME离线反思、6阶段进化管道、Heartbeat主动任务、自愈harness(agent遇缺失能力即时写reusable helper随任务改进)、Daemon Mode常驻服务(claw serve多客户端共享同一会话状态)、Automations事件驱动自动化(定时schedule+Webhook事件触发的工作流引擎, 对接Slack/GitHub/Linear等第三方服务)
- eval_observability: 14可观测矩阵、LLM-as-Judge、TracingMiddleware、反进化审计、token_usage追踪、评估统计显著性+评估驱动选型(用统计显著性判断改进真实有效, 评估结果驱动模型/工具选型)、Agent Arena多模型同任务对抗评估(同一任务head-to-head对比直接驱动选型)
- agent_core: MiddlewareBase | progressive_loader: GEP基因编码

**P1**
- memory_system: User+Agent双轨、预热指数退避、无状态Reducer、记忆三子系统(selection/extraction/consolidation)、Auto-Memory零配置(会话记忆自动捕获无需显式配置)、decision-log memory决策日志记忆(持久化决策轨迹输入/推理/结论, 支持回溯审计+模式学习)
- rag_engine: Knowledge Wiki、BM25+Vector+RRF混合检索 | storage: SQLite+LanceDB本地栈、Skill文件挂载进sandbox(mountable skills, skill Markdown可mount到隔离sandbox供agent用bash/python直接操作)、URI路径化记忆寻址(domain://path路径即语义+Alias别名构建多维关联网络, 后端图拓扑前端降维成树操作)
- eval_observability: 白盒记忆可调试、错误压缩+自愈、零代码信号采集、point-in-time integrity时间点完整性(评估/回测严格按时间点取数, 只看当时已发布数据, 杜绝look-ahead未来信息泄漏虚高指标)
- tool_registry: human_contact工具化、Batch Execute、Per-session作用域、统一认证托管、可插拔channel架构(按能力域组织)、Backend Tool Rendering(工具返回UI组件)、工具选择纪律+升级阶梯(工具声明何时不用, 轻量失败升级重工具)、MCP stdio单层暴露(单一协议层, 任意MCP client驱动)、MCP按需检索+热重载(运行时按需检索MCP工具避免全量注入, mcp.json改动热重载)、agent-first tool design(工具设计面向AI agent, 高层抽象替代行号/正则等低层原语)、精确重构工具(rename/move/inline/propagate deletions符号级重构)、Skill Content Tools工具化召回(get_skill/get_skill_file渐进式披露+agent in the loop, 用工具调用+推理替代语义embedding top-k召回)
- context_injector: 拥有上下文窗口、Intent-Driven Filter、显式上下文路由、上下文工程四支柱(KV Cache管理+提示工程+Agent Skills+上下文压缩统一框架)、Plan-and-Solve规划分解(先规划子问题再逐个检索求解, 突破单次上下文token限制生成超长内容)、System Boot身份协议+按需调取(system://boot启动只载核心设定/身份/用户/使命, 其余按需read_memory拉取, 96.9万字库首条仅7.2K字, 极致token效率)
- agent_orchestrator: 6-Hook补齐、before_llm/tool/on_exit钩子、自主spawn swarm+root/worker effort分离、Subagent上下文隔离(fresh messages[]+单一tool_result)、checkpoint resume断点续跑(graph-shape-aware, 任意节点中断后从检查点恢复避免重复计算)、并行化executor agent采集(多个执行Agent并行工作收集信息, 显著提高吞吐与稳定性)、多Docker Sandbox会话隔离(每会话独立容器+workspace持久化挂载, 安全隔离且状态跨容器存活)、可插拔后端切换(同一前端在local/Docker/VM/cloud多agent-server后端间切换)
- skill_system: Skill资产化注册表、Universal Export、版本控制+回滚、双层结构(Work+Persona)、Built-in Skills内置原子技能集(/review /batch /loop /bugfix)、任务特定agent动态创建(基于查询动态生成领域定制agent)
- model_scheduler: 轻量意图路由模型(≤4B)、统一OpenAI-compatible provider+WebSocket预预热+HTTPS回退、多模态能力路由矩阵(chat/vision/image/ASR/TTS/embedding六能力独立路由不同厂商)
- claw_integration: 默认安全dry-run(安装/配置默认只读预览, 显式授权才写入)、代理与地理定位联动(timezone/locale/egress跟随)、密钥脱敏日志(日志不打印密钥值)+配置优先级链(flag>env>.env>default)、BYO Agent Any Channel(编排层与前端/channel解耦)、异步与事件驱动交互(从请求-响应扩展到事件驱动, 观察与动作空间按模态+时序两维扩展)

**P2**
- tool_registry: Skill确定性Schema、Provider Adapter层
- memory_system: 豆辞典自动超链接(Glossary关键词绑定记忆节点, 任意正文出现即Aho-Corasick多模式匹配自动检出并跨节点超链接, 记忆网络自织网解决孤岛记忆)
- context_injector: Context Engineering摘要压缩+编辑策略(summaries压缩上下文+editing strategies, 强化Auto Compact)
- agent_orchestrator: Filter Chain护栏链、task-bound worktrees(每任务独立工作目录并行编辑)、多Agent团队独立上下文(每Agent独立role/model/skills/knowledge, 共享会话内协作)
- claw_integration: Pipeline部署层、专家知识蒸馏管道、能力层与实现层分离、Daemon状态保持(跨调用保持会话状态, 避免重复建连接)、持续进化四层面(从运行轨迹取学习信号, 按知识/指令/程序/参数分层更新)、Self-iterating dogfooding(Claw自身agent维护仓库: issue/PR/审查/测试自举开发)、交互式调试工具(REPL风格断点/变量检查/表达式求值, 支持agent自调试)、frontend/backend分离部署(前端静态层+agent server+automation backend可拆分独立运行)
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
