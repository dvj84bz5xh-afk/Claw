# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-07-19

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
- **进度**: 102项目 / 257改进项 / 实施率约37.4% (96/257)
- **最新学习**: musistudio/claude-code-router (⭐36K, 相关度35) — 2026-07-26
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

### P1待实施
- memory_system: User+Agent双轨记忆表面（来自EverOS）
- rag_engine: Knowledge Wiki知识百科系统（来自EverOS）
- storage: 本地栈替代外部DB SQLite+LanceDB（来自EverOS）

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
