# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-07-13

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
- **进度**: 95项目 / 217改进项 / 实施率约44.2% (96/217)
- **最新学习**: agentscope-ai/agentscope (⭐27,857, 相关度30) — 2026-07-15
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
1. **EvoMap/evolver** (⭐9K, 相关度34) - GEP基因编码+6阶段进化管道+ATP市场 ✅已学习
2. **NousResearch/hermes-agent** (⭐200K, 相关度29) - 学习循环+轨迹压缩 ✅已学习
3. **TheDotMack/claude-mem** (⭐84K, 相关度29) - 3层MCP搜索+记忆可视化 ✅已学习
4. **langchain-ai/langchain** (⭐132K, 相关度28) - 分层抽象+全生命周期 ✅已学习
5. **pydantic/pydantic-ai** (⭐18K, 相关度28) - 依赖注入+Graph+A2A ✅已学习
7. **agentscope-ai/agentscope** (⭐27K, 相关度30) - 中间件系统+三重记忆+零侵入追踪 ✅已学习
7. **agentscope-ai/agentscope** (⭐27K, 相关度30) - 中间件系统+三重记忆+零侵入追踪 ✅已学习

### P0待实施
- agent_core: MiddlewareBase中间件钩子系统（来自AgentScope）
- eval_observability: TracingMiddleware零侵入追踪（来自AgentScope）
- progressive_loader: GEP基因编码替代自由文本改进建议（来自Evolver）
- claw_integration: 6阶段结构化进化管道（来自Evolver）
- agent_orchestration: Claw ACP适配器（来自OpenHands）
- skill_system: SkillsHub自动化模板市场

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
