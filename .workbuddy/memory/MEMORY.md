# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-09-05

---

## [USER] 用户偏好

- **职业**: 执法培训 + 诈骗园区调查 + CodeBuddy 产品经理
- **技术栈**: Python数据分析、爬虫、区块链追踪
- **风格**: 简洁编号式指令、要结果不要讨论、P0立即实施
- **回复**: 200-300字、结构化Markdown、工具输出
- **禁止**: 不问"是否需要"、不输出AI-only分析、去AI化

---

## [PROJECT] Claw 学习追踪系统

- **目的**: 通过GitHub高星项目迭代CodeBuddy能力
- **进度**: 111项目 / 310改进项 / 实施率约31.0% (96/310)
- **最新学习**: ComposioHQ/composio (⭐30K, 相关度18) — 2026-09-05
- **agent_core版本**: v2.1.0-p1-complete
- **模块**: model_scheduler, unified_registry, progressive_loader, agent_orchestrator, context_injector, tool_registry, rag_engine, memory_system, eval_observability, claw_integration
- **下一步**: 处理P0 pending项

---

## [EVOLUTION] 智能进化引擎

- **自动化ID**: automation-1779863408739
- **频率**: 每日09:00
- **日志**: .workbuddy/evolution_log.jsonl
- **仪表盘**: docs/evolution-dashboard.html
- **状态**: 细水长流模式，每日1项目

### 高相关项目候选
1. **EverMind-AI/EverOS** (⭐11K, 相关度43·最高) - Markdown-as-Truth+Cascade Daemon+OME离线反思 ✅已学习
2. **EverMind-AI/Raven** (⭐2.5K, 相关度40) - Spine脊柱+Sentinel主动引擎+Evolver自进化+SkillForge ✅已学习
3. **zeroclaw-labs/zeroclaw** (⭐32K, 相关度38) - 单二进制+SOP-Graph+工具回执审计 ✅已学习
3. **mastra-ai/mastra** (⭐26K, 相关度36) - 统一存储抽象+14可观测集成+LLM-as-Judge+工作流持久化 ✅已学习
4. **wanshuiyin/ARIS** (⭐13K, 相关度35) - 睡眠自主研究+Markdown Skill+交叉审查+元进化 ✅已学习
5. **EvoMap/evolver** (⭐9K, 相关度34) - GEP基因编码+6阶段进化管道+ATP市场 ✅已学习
4. **NousResearch/hermes-agent** (⭐200K, 相关度29) - 学习循环+轨迹压缩 ✅已学习
5. **TheDotMack/claude-mem** (⭐84K, 相关度29) - 3层MCP搜索+记忆可视化 ✅已学习
6. **agentscope-ai/agentscope** (⭐27K, 相关度30) - 中间件系统+三重记忆+零侵入追踪 ✅已学习
7. **langchain-ai/langchain** (⭐132K, 相关度28) - 分层抽象+全生命周期 ✅已学习
9. **CopilotKit/CopilotKit** (⭐36K, 相关度32) - AG-UI Protocol+Generative UI+Shared State+CLHF自学习 ✅已学习
8. **pydantic/pydantic-ai** (⭐18K, 相关度28) - 依赖注入+Graph+A2A ✅已学习
10. **musistudio/claude-code-router** (⭐36K, 相关度35) - 声明式路由规则+凭证池轮转+Fusion能力注入+AgentClaw多渠道中继+ToolHub市场+成本可观测 ✅已学习
11. **TencentCloud/TencentDB-Agent-Memory** (⭐9.3K, 相关度40) - Mermaid符号化记忆+L0-L3分层管道+全可追溯链+白盒可调试+RRF混合检索+预热退避 ✅已学习
12. **code-yeongyu/oh-my-openagent** (⭐66.7K, 相关度37) - Hash-Anchored Edit+Category-Based Delegation+IntentGate+Skill-Embedded MCPs+Goal Continuation+Hierarchical AGENTS.md+Team Mode+Multi-Harness Adapter ✅已学习
13. **humanlayer/12-factor-agents** (⭐24.9K, 相关度38) - 12因子Agent方法论+Prompt一等代码+拥有上下文窗口+工具结构化输出+统一执行状态+小而专注Agent ✅已学习
14. **PrefectHQ/fastmcp** (⭐27K, 相关度41) - @tool装饰器自动Schema+MCP Server Composition+FastAPI自动生成MCP+Proxy+llms.txt ✅已学习
15. **HKUDS/nanobot** (⭐46.5K, 相关度42·最高) - Dream两阶段记忆整合+AgentLoop/Runner分离+Heartbeat主动任务+Model Presets+AgentHook三层+Auto Compact ✅已学习
16. **mksglu/context-mode** (⭐19.6K, 相关度43·最高) - Tool Output Sandbox+Think-in-Code+Session Continuity+Intent-Driven Filtering+Batch Execute+6-Hook Lifecycle ✅已学习
17. **refly-ai/refly** (⭐7.5K, 相关度34) - Vibe DSL Skill编译器+SOP 3分钟上线+Intervenable Runtime可介入热修+Universal Export单源多形态+Central Skill Registry资产治理 ✅已学习
18. **katanemo/plano** (⭐7K, 相关度36) - 进程外数据平面(Envoy)+YAML声明式Agent编排+轻量4B路由模型+Model Agility统一路由+零代码Signals+OTEL+Filter Chain护栏 ✅已学习
19. **ComposioHQ/composio** (⭐30K, 相关度18) - Meta-tools按需工具发现+工具语义搜索+Per-session工具作用域+认证托管+Provider Adapter层+会话级MCP端点 ✅已学习

### P0待实施
- agent_orchestrator: Spine脊柱架构 submit/emit单入单出+per-session lane（来自Raven）— **新增**
- agent_orchestrator: Sentinel主动引擎 nudge策略+调度器+非被动响应（来自Raven）— **新增**
- claw_integration: Evolver基准驱动自进化 线束内评估→参数优化循环（来自Raven）— **新增**
- storage: Markdown-as-Truth存储架构（来自EverOS）
- memory_system: Cascade Daemon级联守护自动索引同步（来自EverOS）— **新增**
- claw_integration: OME离线反思引擎episode合并+profile提炼（来自EverOS）— **新增**
- memory_system: 正交五维分区检索（来自EverOS）— **新增**
- storage: StorageAdapter统一存储抽象层（来自Mastra）
- eval_observability: 14可观测性集成矩阵升级（来自Mastra）
- eval_observability: LLM-as-Judge工具验证评估闭环（来自Mastra）
- agent_orchestration: 工作流检查点断点续传（来自Mastra）
- agent_core: MiddlewareBase中间件钩子系统（来自AgentScope）
- eval_observability: TracingMiddleware零侵入追踪（来自AgentScope）
- progressive_loader: GEP基因编码替代自由文本改进建议（来自Evolver）
- claw_integration: 6阶段结构化进化管道（来自Evolver）
- agent_orchestration: Claw ACP适配器（来自OpenHands）
- skill_system: SkillsHub自动化模板市场
- skill_system: `/meta-optimize` 自进化命令（来自ARIS）
- skill_system: Markdown Skill标准零锁定规范（来自ARIS）
- agent_orchestration: 交叉模型审查机制（来自ARIS）
- eval_observability: 反进化完整性审计61信号（来自ARIS）
- agent_orchestration: AG-UI Protocol适配器 ~16种标准事件类型 Agent→UI通信层（来自CopilotKit）— **新增**
- context_injector: Shared State双向状态同步 Agent+UI共享读写+增量delta推送（来自CopilotKit）— **新增**
- model_scheduler: 声明式路由规则引擎 条件路由+前缀匹配+请求重写+自动重试+有序故障转移模型链（来自CCR）— **新增**
- model_scheduler: 凭证池与密钥轮转 多API Key自动轮转+限流检测+Key级故障转移（来自CCR）— **新增**
- context_injector: Mermaid符号化上下文压缩 冗长日志卸载至refs/*.md+Mermaid画布+node_id按需回溯（来自TencentDB-Agent-Memory）— **新增**
- memory_system: L0-L3分层记忆管道 Conversation-Atom-Scenario-Persona渐进式提取+向量去重+冲突检测（来自TencentDB-Agent-Memory）— **新增**
- memory_system: 全可追溯链 Persona-Scenario-Atom-Conversation确定性路径+避免不可逆压缩+无损恢复（来自TencentDB-Agent-Memory）— **新增**
- context_injector: Hash-Anchored Edit (Hashline) LINE#ID内容哈希行标签+编辑前校验+消除stale-line错误（来自OmO）— **新增**
- model_scheduler: Category-Based Agent Delegation 工作类别枚举+类别→模型自动映射（来自OmO）— **新增**
- agent_orchestrator: IntentGate 任务分发前意图分析层+真实意图提取+字面误解校正（来自OmO）— **新增**
- tool_registry: Skill-Embedded MCPs Skill自带MCP+按需启动+作用域限定+自动销毁（来自OmO）— **新增**
- agent_orchestrator: Goal Continuation+Todo Enforcer 持久目标+空闲强制拉回+完成证据审计（来自OmO）— **新增**
- context_injector: Hierarchical AGENTS.md /init-deep自动生成分层上下文+自动加载相关层（来自OmO）— **新增**
- agent_orchestrator: ExecutionState统一模型 执行态与业务态分离，支持检查点/恢复/迁移（来自12-factor-agents）— **新增**
- tool_registry: 工具输出Schema标准化 统一success/result/error/context schema（来自12-factor-agents）— **新增**
- agent_orchestrator: lane级小Agent架构 拆解monolithic为submit/emit/handoff单职责lane（来自12-factor-agents）— **新增**
- context_injector: Prompt版本化管理 提取为独立.prompt.md文件，纳入版本控制（来自12-factor-agents）— **新增**
- memory_system: Dream两阶段记忆整合 Consolidator实时压缩→Dream定期整合MEMORY.md/SOUL.md/USER.md（来自nanobot）— **新增**
- agent_orchestrator: AgentLoop/AgentRunner分离 Loop负责turn编排+hook，Runner负责provider+stream+tool（来自nanobot）— **新增**
- claw_integration: Heartbeat主动任务执行 读取Active Tasks定时触发，抑制无用结果（来自nanobot）— **新增**
- model_scheduler: Model Presets命名配置 fast/smart/vision preset+fallback链+per-session切换（来自nanobot）— **新增**
- agent_orchestrator: AgentHook三层生命周期 per-iteration/run/turn级hook+before_run/after_run/on_stream（来自nanobot）— **新增**
- context_injector: Auto Compact空闲主动压缩 检测空闲状态时自动压缩旧会话上下文（来自nanobot）— **新增**
- context_injector: Tool Output Sandbox 工具输出隔离子进程+仅stdout入上下文(98%减少)（来自context-mode）— **新增**
- context_injector: Think-in-Code范式 Agent写代码分析数据而非读入原始数据(100x节省)（来自context-mode）— **新增**
- memory_system: Session Continuity Engine SQLite+FTS5+BM25事件追踪+压缩后按需检索恢复（来自context-mode）— **新增**
- skill_system: Vibe DSL Skill编译器 自然语言SOP/意图→自动编译标准SKILL.md+3分钟上线（来自refly）— **新增**
- agent_orchestrator: Intervenable Runtime 执行中暂停/审计/改向+hot-fix热修不整链重启（来自refly）— **新增**
- model_scheduler: Agent声明式路由 YAML声明Agent端点+NL描述自动生成语义意图分类路由（来自plano）— **新增**
- agent_orchestrator: 编排数据面解耦 Orchestrator独立为进程外服务+业务Agent注册即接入+扩容不改代码（来自plano）— **新增**
- tool_registry: Meta-tools按需工具发现 discover/auth/execute元工具替代全量Schema预注入（来自composio）— **新增**
- tool_registry: 工具语义搜索 按任务意图检索注册表中相关工具子集（来自composio）— **新增**

### P1待实施
- memory_system: User+Agent双轨记忆表面（来自EverOS）
- rag_engine: Knowledge Wiki知识百科系统（来自EverOS）
- storage: 本地栈替代外部DB SQLite+LanceDB（来自EverOS）
- eval_observability: 白盒记忆可调试 Markdown/Mermaid中间产物+记忆可视化调试界面（来自TencentDB-Agent-Memory）— **新增**
- rag_engine: BM25+Vector+RRF混合检索+jieba中文分词+召回安全控制（来自TencentDB-Agent-Memory）— **新增**
- memory_system: 预热指数退避 新会话1→2→4翻倍触发+空闲超时+L2聚合间隔（来自TencentDB-Agent-Memory）— **新增**
- tool_registry: human_contact工具化 将human-in-the-loop重构为标准tool(contact_human/approve/reject)（来自12-factor-agents）— **新增**
- eval_observability: 错误压缩+自愈策略 错误摘要器(stack trace→LLM简洁错误)+内置重试/降级（来自12-factor-agents）— **新增**
- memory_system: 无状态Reducer 纯函数状态转换，便于测试和回滚（来自12-factor-agents）— **新增**
- context_injector: 拥有上下文窗口 自定义上下文格式，非强制标准消息列表（来自12-factor-agents）— **新增**
- context_injector: Intent-Driven Output Filter 输出超阈值时按意图过滤保留相关行（来自context-mode）— **新增**
- tool_registry: Batch Execute Tool 多命令/查询一次调用+可选并发（来自context-mode）— **新增**
- agent_orchestrator: 6-Hook生命周期协作 补全PreCompact和Stop Hook（来自context-mode）— **新增**
- skill_system: Skill资产化注册表 版本控制+变更审计+团队共享+回滚（SkillsHub升级）（来自refly）— **新增**
- skill_system: Universal Export SKILL.md单源定义→导出MCP/API/Webhook/多IDE（来自refly）— **新增**
- model_scheduler: 轻量意图路由模型 本地小模型(≤4B)做任务→Agent映射+替代大模型判定降成本延迟（来自plano）— **新增**
- eval_observability: 零代码信号采集 调度层自动捕获Agent调用追踪与信号+采样率配置（来自plano）— **新增**
- tool_registry: Per-session工具作用域 会话级限定可用工具与凭证+防越权与上下文污染（来自composio）— **新增**
- tool_registry: 统一认证托管 凭证集中管理+调用时自动注入+Agent侧零密钥（来自composio）— **新增**

### P2待实施
- tool_registry: Skill确定性Schema input/output校验+失败恢复内置于Skill元数据(非自由文本prompt)（来自refly）— **新增**
- agent_orchestrator: Filter Chain护栏链 入口模块化过滤器(安全审核/敏感词/记忆注入)+全Agent统一挂载（来自plano）— **新增**
- tool_registry: Provider Adapter层 工具定义单源适配OpenAI/Claude/MCP等多格式（来自composio）— **新增**

---

## [TECH] 关键环境

- Python: 3.13.13 (完整路径), Node: 24.16.0, Git: 2.54.0
- GitHub API: urllib直连，无gh CLI
- Python路径: `C:\Users\10127\AppData\Local\Programs\Python\Python313\python.exe`
- 注意: `python`命令可能解析到WindowsApps，使用完整路径

---

## [SKILLSHUB] 中央技能工作区

- **路径**: `C:\Users\10127\WorkBuddy\SkillsHub\`
- **规则**: 新技能先存SkillsHub，再同步到`~/.workbuddy/skills/`
- **权威来源**: SkillsHub为唯一权威

---

## [TEAM] 飞书协作群

- **平台**: 飞书群
- **成员**: WorkBuddy(我) + Claude Code + Hermes
- **协作模式**: 自主分工 + 相互监督 + 交叉验证
- **原则**: 不抢活、不甩锅、主动验证、发现问题立即反馈
- **我的定位**: 全栈开发/数据分析/链追踪/课程开发/Skill生态

---

*日常流水记录在各日期文件中。*
