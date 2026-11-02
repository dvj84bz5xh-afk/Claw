# MEMORY.md - Claw 项目记忆
# 格式版本: v3.4 (精简索引版) | 最后更新: 2026-11-02

## [USER] 用户偏好
- 职业: 执法培训 + 诈骗园区调查 + CodeBuddy产品经理
- 技术栈: Python数据分析、爬虫、区块链追踪
- 风格: 简洁编号式指令、要结果、P0立即实施、结构化Markdown
- 禁止: 不问"是否需要"、AI-only分析、去AI化

## [PROJECT] Claw 学习追踪系统
- 目的: 通过GitHub高星项目迭代CodeBuddy能力
- 进度: 141项目 / 445改进项 / 实施率约22% (已实施96 / P0待实施141)
- 最新学习: ChesterRa/cccc (⭐1.3K, 相关度20, 协作内核/消息四态+委派单据) — 2026-11-02
- agent_core: v2.1.0-p1-complete
- 模块(12): model_scheduler, unified_registry, progressive_loader, agent_orchestrator, context_injector, tool_registry, rag_engine, memory_system, eval_observability, claw_integration, storage, skill_system
- **改进清单(P0/P1/P2×模块)权威来源是 `.workbuddy/learning_tracking.json` 的 improvements 数组；`.workbuddy/memory/capabilities-full.md` 为 2026-10-25 的人类可读归档快照，需要逐条比对时再读，不要每轮全量载入**

## [EVOLUTION] 智能进化引擎
- 自动化ID: automation-1779863408739 | 每日09:00 | 细水长流1项目/日
- 日志: .workbuddy/evolution_log.jsonl | 仪表盘: docs/evolution-dashboard.html
- 环境铁律: Python 用完整路径 /c/Users/10127/AppData/Local/Programs/Python/Python313/python.exe + heredoc; 系统代理127.0.0.1:7890已失效, urllib 须 build_opener(ProxyHandler({})) 绕过; git push 用 `-c http.sslBackend=openssl -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=20`（HTTP/2 会挂在 fetch 阶段不动）
- **四大短板(10-25/27/28/29 佐证)**: ①缺 fitness 闭环（改进项只计数不验证）；②缺产出沉淀（439项建议无一变技能）；③缺"进化≠自己改自己"的边界（提出者=批准者=验收者）；④缺供应链信任（技能从远程拉取但不验签名，权限靠进程内钩子而非进程外broker，审计由工具自证）；⑤缺协作语义（消息只有'已发'一态，无送达/已读/已回之分，无委派单据，停用agent仍可被投递）。P0 动作: 建 `managed_skills/`，3项成果按**五件套**(SKILL.md+evals+security+run-record+纠错路径)写成技能包并跑一次代表性run；证据落 raw/、草稿落 wiki/，可执行层仅由验证过的变更更新

## [CAPABILITY] 各模块已具备能力(精简索引)
- agent_orchestrator: Hook三/六层 · 子Agent上下文隔离 · 并行executor · checkpoint续跑 · Guardrails四钩三判 · 任务分级+交付验收闸门 · Spine · Sentinel · IntentGate · ACP适配器 · Stage Contract线性流水线 · swarm事务化 · 多Agent辩论制衡 · 消息四态(stored/delivered/read/replied)+三模式投递(打断/待回/邮件)+原子读游标 · 生命周期边界(停用不唤醒) · Foreman/peer路由
- memory_system: 五维分区 · L0-L3管道 · Dream两阶段 · 增量合并 · 纠正层 · 语义记忆图 · Skill-as-Memory · Disclosure Routing · Node-Memory-Edge-Path四实体 · Agent身份作用域 · 纠错规则库+纠正率 · CCP结构化会话记忆+时间有效窗 · 因果类型化图谱边
- context_injector: Shared State · Mermaid压缩 · Hash-Anchored Edit · Hierarchical AGENTS.md · Auto Compact · 五层上下文分层加载(L0-L4)+Inputs表 · 三级技能token控制 · PreCompact/PostCompact双钩子 · 分级读取模式+JIT披露+缓存引用
- tool_registry: Skill-Embedded MCPs · 工具语义搜索 · 多路冗余降级 · 真实探测健康检查 · 三分类+主动发现 · 符号级代码工具 · Gateway/Registry控制面分离 · Virtual MCP servers · 输出压缩规则库+输出预算 · fail-closed准入+工具级block · MCP开销审计 · 审批预授权+凭证vault · 调用级能力派生(每次调用独立能力集不继承会话) + 工具间双向边授权(can_use+from不合并) · 工具面按协议vs机械分级(协议核心常驻其余按需)
- skill_system: SkillsHub市场 · Markdown零锁定 · Vibe DSL · 渐进发现 · 自动学习管道 · 路由两阶段记录 · 资产化注册表 · 双层Work+Persona · Built-in Skills · 统一AI资产注册表 · 多技能根目录 · Workspace可移植打包 · 技能来源证明(includes glob必签名+Sigstore bundle+blocklist优先硬拒+用户级trust anchor不可削弱)
- eval_observability: 14可观测矩阵 · LLM-as-Judge · TracingMiddleware · 反进化审计 · 统计显著性选型 · Agent Arena · Evolve程序搜索(islands+bandit) · point-in-time integrity · 玻璃盒run落盘+replay · 证据分级报告法 · 能力矩阵+漂移测试 · 中介侧审计(工具不自证+封闭decision词表+摘要可验篡改) · 运维策略事件化(idle/静默/notice最多一次且无内容)
- claw_integration: Evolver自进化 · OME离线反思 · Heartbeat · 自愈harness · Daemon Mode · Automations · SSE事件总线 · Durable Execution(Lease+Revision) · Runtime契约层(/v1+可续播SSE+replay) · 默认安全dry-run · 权限拒绝模式分析器 · 人工编辑面交接 · 交付前控制面(PathJail) · 可写可执行信任门+fail closed · 委派单据(owner/outcome/evidence/handoff/acceptance)
- model_scheduler: 声明式路由 · 凭证池轮转 · Model Presets · provider per tier · BudgetStore持久化预算 · 多模态能力路由矩阵 · 单一活动provider+显式激活
- storage: Markdown-as-Truth · StorageAdapter抽象 · SQLite+LanceDB本地栈 · Skill挂载sandbox · URI路径化寻址 · Local-first+渐进鉴权 · 内容寻址快照原子回滚(按文件恢复)
- rag_engine: 主题知识库+可视化图谱 · source-tracking来源追踪 · BM25+Vector+RRF混合检索

## [TECH] 关键环境
- Python 3.13.13 / Node 24.16.0 / Git 2.54.0
- GitHub API 直连(绕过代理) | Python 用完整路径

## [SKILLSHUB]
- 路径: C:\Users\10127\WorkBuddy\SkillsHub\ (唯一权威)
- 新技能先存SkillsHub再同步~/.workbuddy/skills/

## [TEAM] 飞书协作群
- 成员: WorkBuddy + Claude Code + Hermes
- 协作: 自主分工 + 相互监督 + 交叉验证
