# 智能进化学习自动化 — 执行记忆

自动化ID: automation-1779863408739
频率: 每日 09:00 (细水长流模式, 每日1项目)

## 执行历史

### 2026-10-19 (第85轮)
- 学习项目: rohitg00/pro-workflow (⭐2,918, 相关度27, JavaScript, MIT) — 把"每次会话重教一遍"做成基础设施: 单一SQLite store承载自我纠错记忆+FTS5研究wiki+质量门禁hooks
- 核心创新: 纠错即规则(纠正→存SQLite FTS5→SessionStart自动加载, /insights纠正率趋势作唯一KPI) / 免命令捕获(Stop hook解析[LEARN]块) / 知识面Markdown落盘+FTS5影子索引+UserPromptSubmit命中注入top-3 / 自主研究环治理(预算封顶BFS+收敛检测+原子seed认领+try/finally+全局STOP) / PreCompact存摘要→PostCompact回注 / 运维三件套mcp-audit+permission-tuner+token-efficiency / Command→Agent→Skill共用单一store
- 改进建议: 5项 (P0×2: memory_system 纠错规则库+纠正率度量 / context_injector PreCompact-PostCompact双钩子; P1×2: tool_registry MCP开销审计 / claw_integration 权限拒绝模式分析器; P2×1: eval_observability 自主循环治理模板)
- 判断: Claw 记忆/技能体系表达力已超该项目, 差距在闭环验证与运维面(缺可下降量化指标)
- 输出: daily_learning/2026-10-19_pro-workflow.md, 更新 tracking(133项目/404改进项)/MEMORY.md/memory日志/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push origin main

### 2026-10-16 (第84轮)
- 学习项目: foryourhealth111-pixel/Vibe-Skills (⭐3,704, 相关度23, Python, v4.1.0) — 通用Skill: 自动路由本地Skills并智能编排harness工作流
- 核心创新: 四步编排(明确目标→拆可验证子任务→从大池只挑极少相关能力→依赖序执行→交付前逐项验收) / 两阶段技能选择记录(agent_skill_organization规划 vs module_assignments执行, 区分"找到≠已参与") / 三级token控制(本地紧凑索引→候选短名单→按需读完整SKILL.md) / 任务分级L(顺序)XL(最多并行2互不冲突部分) / 多技能根目录skill-roots.json + install-receipt.json完整性校验 / SkillsBench量化(195技能池: +21.12pp/-29.6%token/-33.1%工具调用)
- 改进建议: 5项 (P0×2: skill_system 技能路由两阶段记录+依赖序编排 / context_injector 技能索引三级token控制; P1×2: agent_orchestrator 任务分级+交付前验收闸门 / skill_system 多技能根目录; P2×1: eval_observability 技能路由量化基准)
- 输出: daily_learning/2026-10-16_vibe-skills.md, 更新 tracking(132项目/399改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 6fe6956)

### 2026-10-13 (第83轮)
- 学习项目: agentic-community/mcp-gateway-registry (⭐972, 相关度18, Python) — 企业级MCP网关与注册中心(统一治理MCP server/agent/skill/自定义资产)
- 核心创新: Gateway数据面/Registry控制面分离(单一受治理入口) / 统一AI资产注册表(servers/A2A agents/skills/自定义schema实体同控制面) / 动态工具发现(自然语言语义搜索)+Virtual MCP servers(多后端工具聚合一端点+per-tool ACL) / Per-user egress auth凭证代理(3LO/OBO/PAT三层resolver, token不落用户机器, purpose绑定AEAD) / fail-closed准入闸门+工具级安全block(注册即扫描, 一误报不连累全服务器) / A2A默认peer-to-peer+外部注册表联邦+审计留痕+OpenTelemetry
- 改进建议: 5项 (P0×2: tool_registry Gateway/Registry控制面分离 / tool_registry 动态工具发现+Virtual MCP; P1×2: tool_registry fail-closed准入闸门+工具级block / claw_integration Per-user egress auth凭证代理; P2×1: skill_system 统一AI资产注册表+外部联邦)
- 输出: daily_learning/2026-10-13_mcp-gateway-registry.md, 更新 tracking(131项目/394改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 6cb970b)

### 2026-10-12 (第82轮)
- 学习项目: Deuz-AI/Deuz-SDK (⭐682, 相关度33, TypeScript) — 零运行时依赖的生产级AI Agent框架(durable execution/memory/RAG/MCP/HITL/swarm/evolve)
- 核心创新: Durable Execution双机制(Lease心跳续租决定驱动进程+Revision提交版本围栏拒陈旧写, 跨进程接管/僵尸防护/cancel跨持有人投递/drain随lease丢弃) / 持久化预算BudgetStore(user/thread/org维度token+USD, reserve-then-settle准入) / Guardrails四钩子三判决(onInput/onToolCall/onToolResult/onOutput × pass/block/rewrite, 纯函数+审计留痕) / Evolve进化式程序搜索(EVOLVE-BLOCK+SEARCH/REPLACE diff+评估级联+islands+模型bandit+强制预算+zero-call resume) / Swarm事务化调度(先持久化dispatch再执行+原子提交) / 零运行时依赖core+optional peers+edge可跑
- 改进建议: 5项 (P0×2: claw_integration Durable Execution双机制 / model_scheduler 持久化预算层; P1×2: agent_orchestrator Guardrails四钩子三判决 / eval_observability Evolve进化式程序搜索; P2×1: agent_orchestrator Swarm事务化调度)
- 输出: daily_learning/2026-10-12_deuz-sdk.md, 更新 tracking(130项目/389改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 24d74a9)

### 2026-10-11 (第81轮)
- 学习项目: doobidoo/mcp-memory-service (⭐2,007, 相关度27, Python) — AI Agent管线(LangGraph/CrewAI/AutoGen/Claude)的开源持久化共享记忆后端
- 核心创新: 多传输统一记忆服务(REST+MCP+Remote MCP/OAuth一体) / Agent身份作用域记忆(X-Agent-ID自动tag+按作用域检索隔离) / 因果类型化知识图谱(causes/fixes/contradicts) / SSE事件总线(记忆变更实时通知) / 自主整理+Insight Cards(旧记忆压缩为模式/趋势/缺口洞察) / 混合后端(SQLite本地5ms+Cloudflare云同步+Milvus, ONNX本地embedding)
- 改进建议: 4项 (P0×1: memory_system Agent身份作用域记忆; P1×2: memory_system 因果类型化图谱边 / claw_integration SSE事件总线; P2×1: memory_system 自主整理守护+Insight Cards)
- 输出: daily_learning/2026-10-11_mcp-memory-service.md, 更新 tracking(129项目/384改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 29f0084)

### 2026-10-10 (第80轮)
- 学习项目: Dataojitori/nocturne_memory (⭐1,388, 相关度40, Python) — MCP 长期记忆服务器(Say goodbye to Vector RAG)
- 核心创新: 条件触发路由(Disclosure Routing按情境精准注入替代cosine盲盒) / Node-Memory-Edge-Path四实体图模型(身份/内容/关系/路由四层分离) / 记忆版本快照+一键回滚 / URI路径化寻址(domain://path+Alias别名) / System Boot身份协议+按需调取(96.9万字库首条仅7.2K字) / 豆辞典Aho-Corasick自动超链接自织网
- 改进建议: 5项 (P0×2: memory_system 条件触发路由 / memory_system 四实体图模型含版本回滚; P1×2: storage URI路径寻址+Alias / context_injector Boot身份协议按需调取; P2×1: memory_system 豆辞典自动超链接)
- 输出: daily_learning/2026-10-10_nocturne_memory.md, 更新 tracking(128项目/380改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 3d284cc)

### 2026-10-09 (第79轮)
- 学习项目: memodb-io/Acontext (⭐3,696, 相关度40, TypeScript/Python) — Skill-as-Memory 记忆层
- 核心理念: "Skill is Memory, Memory is Skill" — 记忆即 agent skill Markdown 文件
- 核心创新: 任务结果触发蒸馏学习(complete/failed→Distillation→Skill Agent路由) / 渐进式披露召回(get_skill/get_skill_file, agent in the loop, 替代embedding top-k) / Plain file any framework(无embedding/无API锁定, 可Git/grep/mount) / 用户设计结构(SKILL.md定义schema) / Context Engineering摘要压缩+editing strategies
- 改进建议: 5项 (P0×2: memory_system Skill-as-Memory统一记忆层 / skill_system 任务结果触发蒸馏学习; P1×2: tool_registry Skill Content Tools工具化召回 / storage mountable skills挂载sandbox; P2×1: context_injector Context Engineering摘要压缩)
- 输出: daily_learning/2026-10-09_acontext.md, 更新 tracking(127项目/375改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 1613102, 同时补齐了 10-08 OpenHands 提交 862291e)

### 2026-10-08 (第78轮)
- 学习项目: All-Hands-AI/OpenHands (⭐90,207, 相关度42, TypeScript) — Agent Canvas自托管编码Agent控制中心
- 核心创新: ACP统一协议+多agent后端路由 / Automations事件驱动自动化 / 多Docker Sandbox会话隔离 / 可插拔后端切换 / frontend/backend分离部署
- 改进建议: 5项 (P0×2: agent_orchestrator ACP统一协议抽象层 / claw_integration Automations事件驱动自动化; P1×2: agent_orchestrator 多Docker Sandbox会话隔离+可插拔后端切换; P2×1: claw_integration frontend/backend分离部署)
- 输出: daily_learning/2026-10-08_openhands.md, 更新 tracking(126项目/370改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git commit 成功, git push 失败(网络无法连接 github.com:443, 连续3次失败) — 待下次运行重试

### 2026-10-07 (第77轮)
- 学习项目: assafelovic/gpt-researcher (⭐29,930, 相关度38, Python) — 自主深度研究Agent
- 核心创新: Planner-Executor-Publisher三段式编排 / source-tracking来源追踪+引用 / 并行化executor agent采集 / Plan-and-Solve+RAG结合 / 任务特定agent动态创建 / 反幻觉设计
- 改进建议: 5项 (P0×2: agent_orchestrator三段式编排 / rag_engine source-tracking来源追踪; P1×2: agent_orchestrator并行化executor / context_injector Plan-and-Solve; P2×1: skill_system任务特定agent动态创建)
- 输出: daily_learning/2026-10-07_gpt-researcher.md, 更新 tracking(125项目/365改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit ba2e808)

### 2026-10-06 (第76轮)
- 学习项目: oraios/serena (⭐30,025, 相关度40, Python) — coding agent 的 IDE 级符号工具层
- 核心创新: 符号级代码工具(symbol-level) / 关系结构利用(referencing/type hierarchy) / 符号化编辑(symbolic editing) / 精确重构(rename/move/inline) / agent-first tool design / MCP集成+LSP抽象层(40+语言) / 交互式调试(REPL)
- 改进建议: 5项 (P0×2: tool_registry符号级工具抽象 / 符号化编辑; P1×2: agent-first tool design / 精确重构工具; P2×1: claw_integration交互式调试工具)
- 输出: daily_learning/2026-10-06_serena.md, 更新 tracking(124项目/360改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 3a57a2b)

### 2026-10-05 (第75轮)
- 学习项目: TauricResearch/TradingAgents (⭐109,782, 相关度38, Python) — 多Agent金融交易框架
- 核心创新: 多Agent角色分工+动态辩论决策(风险团队制衡) / provider per model tier分层模型路由 / point-in-time integrity时间点完整性 / checkpoint resume断点续跑 / decision-log memory决策日志记忆 / structured-output agents
- 改进建议: 5项 (P0×2: agent_orchestrator辩论式决策+风险制衡 / model_scheduler provider per model tier; P1×2: eval_observability point-in-time / agent_orchestrator checkpoint resume; P2×1: memory_system decision-log记忆)
- 输出: daily_learning/2026-10-05_tradingagents.md, 更新 tracking(123项目/355改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit 38dcf35)

### 2026-10-04 (第74轮)
- 学习项目: QwenLM/qwen-code (⭐28,288, 相关度40, TypeScript) — 通义千问官方开源编码Agent
- 核心创新: Agent Arena多模型同任务对抗评估 / Daemon Mode(qwen serve)多客户端共享Agent / Auto-Memory+Auto-Skills零配置 / Built-in Skills内置原子技能集(/review /batch /loop /bugfix) / Self-iterating dogfooding自举开发 / SWE-bench工程化评估(500例3trials7版本, 77.8%均分)
- 改进建议: 5项 (P0×2: eval_observability Agent Arena对抗评估 / claw_integration Daemon Mode多客户端共享; P1×2: memory_system Auto-Memory零配置 / skill_system Built-in Skills原子技能集; P2×1: claw_integration Self-iterating dogfooding)
- 输出: daily_learning/2026-10-04_qwen-code.md, 更新 tracking(122项目/350改进项)/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: git push 成功 (commit c0eb059)

### 2026-10-03 (第73轮)
- 学习项目: bojieli/ai-agent-book (⭐52,112, 相关度45, Python) — 《深入理解 AI Agent》开源书
- 核心创新: 核心公式 Agent=LLM+上下文+工具 / 上下文工程四支柱 / 工具三分类+主动发现 / 观察与动作空间扩展 / 评估统计显著性+驱动选型 / 持续进化四层面
- 改进建议: 5项 (P0×2: tool_registry工具三分类+主动发现 / eval_observability评估统计显著性+驱动选型; P1×2: claw_integration异步事件驱动交互 / context_injector上下文工程四支柱; P2×1: claw_integration持续进化四层面)
- 输出: daily_learning/2026-10-03_ai-agent-book.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅

### 2026-10-02 (第72轮)
- 学习项目: zhayujie/CowAgent (⭐47,205, 相关度44, Python) — 原 chatgpt-on-wechat 更名
- 核心创新: 记忆三轨互补双系统(时间序+主题序) + 按主题知识库/可视化知识图谱 + Deep Dream蒸馏 + Self-Evolution主动跟进 + 多模态能力路由矩阵 + MCP按需检索/热重载 + Tools/Skills分层
- 改进建议: 5项 (P0×2: rag_engine按主题知识库+可视化图谱 / memory_system时间序+主题序双系统; P1×2: model_scheduler多模态路由矩阵 / tool_registry MCP按需检索+热重载; P2×1: agent_orchestrator多Agent团队独立上下文)
- 输出: daily_learning/2026-10-02_cowagent.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅

### 2026-10-01 (第71轮)
- 学习项目: browser-use/browser-harness (⭐18,247, 相关度33, Python)
- 核心创新: Self-healing harness(自愈) + Protected core+agent-writable workspace分离 + 工具选择纪律+升级阶梯 + MCP stdio单层暴露 + Daemon状态保持
- 改进建议: 5项 (P0×2: 自愈harness/Protected core+workspace; P1×2: 工具选择纪律/MCP stdio单层; P2×1: Daemon状态保持)
- 输出: daily_learning/2026-10-01_browser-harness.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅

### 2026-09-30 (第70轮)
- 学习项目: shareAI-lab/learn-claude-code (⭐77,815, 相关度42, Python)
- 核心创新: Harness工程化17课 + Agency来自模型/harness是载体 + Permission三级权限 + Context Compact四步压缩顺序 + Memory三子系统 + Goal Loop独立评估器
- 改进建议: 5项 (P0×2: Goal Loop独立评估器/Context Compact四步压缩; P1×2: Subagent上下文隔离/记忆三子系统; P2×1: task-bound worktrees)
- 输出: daily_learning/2026-09-30_learn-claude-code.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 状态修复: 发现 09-19/09-20 部分写入丢失(疑并发触发), 本轮全量重写 MEMORY.md + 补齐仪表盘 jcode/CopilotKit/learn-claude-code 三行

### 2026-09-20 (第69轮)
- 学习项目: 1jehuang/jcode (⭐19,907, 相关度36, Rust)
- 核心创新: 极致RAM效率harness + 语义记忆图(被动提取) + Swarm编辑冲突通知 + 自主spawn swarm + 多provider统一接入
- 改进建议: 5项 (P0×2: 语义记忆图/Swarm编辑冲突通知; P1×2: 自主spawn swarm/统一provider; P2×1: 资源效率公开基准)
- 备注: 该轮因中断未 commit/通知/更新 memory.md, 由 09-30 轮补记并合并提交

### 2026-09-19 (第68轮)
- 学习项目: CopilotKit/CopilotKit (⭐37,408, 相关度40, TypeScript)
- 核心创新: AG-UI协议 + BYO Agent Any Channel + Human-in-the-Loop + Generative UI三型 + Shared State + 自动学习管道 + Backend Tool Rendering
- 改进建议: 5项 (P0×2: Human-in-the-Loop暂停确认/自动学习管道; P1×2: Backend Tool Rendering/BYO Any Channel; P2×1: Product Analytics)
- 输出: daily_learning/2026-09-19_copilotkit.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 顺带修正: learning_tracking.json 统计字段滞后问题(用 Python 程序化更新对齐 projects/improvements/统计字段)

### 2026-09-18 (第67轮)
- 学习项目: feder-cr/AIHawk (⭐31,625, 相关度31)
- 核心创新: 反检测浏览器(seed→fingerprint确定性指纹) + 代理地理定位联动 + MCP server一键接入(uvx) + 配置优先级链+密钥脱敏日志
- 改进建议: 4项 (P0×1: tool_registry MCP工具一键接入; P1×3: 确定性指纹/代理联动/密钥脱敏)
- 输出: daily_learning/2026-09-18_aihawk.md, 更新 tracking/MEMORY.md/evolution_log.jsonl/dashboard
- 通知: QQ邮箱✅ + 飞书✅
- 同步: 本地 commit 113d5d5 已生成, **git push 因 github.com:443 网络超时失败**, 待网络恢复重试

### 2026-09-17 (第66轮)
- 学习项目: Panniantong/Agent-Reach (⭐82,532, 相关度35)
- 核心创新: 能力层设计 + 首选/备选有序后端列表 + 真实探测健康检查(doctor) + 可插拔channel架构 + 默认安全dry-run
- 改进建议: 5项 (P0×2: tool_registry后端多路冗余+真实探测; P1×2: 可插拔channel+默认安全dry-run; P2×1: 能力层与实现层分离)
- 输出: daily_learning/2026-09-17_agent-reach.md, 更新 learning_tracking.json / MEMORY.md / evolution_log.jsonl / evolution-dashboard.html
- 通知: QQ邮箱✅ + 飞书✅
- 同步: 已 push 到 GitHub (main)

### 2026-09-16 (第65轮) — 上一轮补记
- 学习项目: titanwings/distilly (⭐24,769, 相关度38)
- 核心创新: 专家知识蒸馏 + 双层Skill(Work+Persona) + 增量合并 + 纠正层 + 版本控制回滚
- 改进建议: 5项 (P0×2: memory_system增量合并+纠正层; P1×2: 版本控制回滚+双层结构; P2×1: 专家知识蒸馏管道)
- 备注: 该轮 git push 因审批超时未完成, 于 09-17 轮补提交 (commit e3753ec)
- 附带: 重写压缩了 MEMORY.md (从6000+字符精简到~2800字符, 按模块归并 P0/P1/P2 待实施项)

## 关键注意事项
- 去重源: .workbuddy/learning_tracking.json (projects 数组)
- 已学高相关项目(勿重复): EverOS, context-mode, nanobot, fastmcp, Raven, TencentDB-Agent-Memory, hermes-agent, claude-mem, haystack, distilly, Agent-Reach 等 60+ 项目
- 通知双通道: QQ邮箱 smtp.qq.com:465 (1012701669@qq.com) + 飞书 (App cli_aa9ccbc13c789cc7, Chat oc_a21fbaa09500d12e205c1769403d13f1)
- evolution_log.jsonl 采用双转义 JSON 格式 (引号前加反斜杠), 追加时保持一致
