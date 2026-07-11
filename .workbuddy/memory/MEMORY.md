# MEMORY.md - Claw 项目记忆
# 格式版本: v2.0 | 最后更新: 2026-07-11

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
- **进度**: 91项目 / 195改进项 / 实施率50.0% (96/192)
- **最新学习**: tinyhumansai/openhuman (⭐34,612, 相关度25) — 2026-07-11
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
1. **NousResearch/hermes-agent** (⭐200K, 相关度29) - 学习循环+轨迹压缩
2. **TheDotMack/claude-mem** (⭐84K, 相关度29) - 3层MCP搜索+记忆可视化
3. **langchain-ai/langchain** (⭐132K, 相关度28) - 分层抽象+全生命周期
4. **pydantic/pydantic-ai** (⭐18K, 相关度28) - 依赖注入+Graph+A2A
5. **a2aproject/A2A** (⭐24K, 相关度29) - Agent Card+Task生命周期

### P0待实施
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

*日常流水记录在各日期文件中。*
