## 学习日期: 2026-09-30

### 学习项目: shareAI-lab/learn-claude-code
- URL: https://github.com/shareAI-lab/learn-claude-code
- Stars: 77,815
- 语言: Python | 相关度: 42

### 核心发现
1. **Harness 工程化 17 课** — 把 Claude Code 拆成 17 个可隔离的 harness 机制, 每个机制一句话格言: Agent Loop / Tool Use / Permission / Hooks / TodoWrite / Subagent / Skill Loading / Context Compact / Memory / Task System / Background Tasks / Cron / Agent Teams / MCP / Integrated Harness / Workflow Runtime / Goal Loop
2. **核心理念「Agency 来自模型, harness 是载体」** — 模型是司机, harness 是车; 工程要做的是"车"不是"智能"
3. **s03 Permission「先设边界, 再给自由」** — 检查什么能跑/什么必须停/什么需审批 (三级权限模型)
4. **s04 Hooks「环绕 loop 加钩子, 永不重写 loop」** — 扩展点不改主循环
5. **s08 Context Compact「先压 tool results, 再总结历史」** — 四步压缩的顺序策略 (上下文总满, 要有腾挪方式)
6. **s09 Memory「记该记的, 忘该忘的」** — 三子系统: selection(选择)/extraction(提取)/consolidation(整合)
7. **s17 Goal Loop「目标决定 loop 何时停」** — 独立 evaluator 审核每次 stop 提议; impossible/failed/over-limit 目标回退给用户

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| Goal Loop 独立评估器 (evaluator 审核 stop 提议, 失败目标回退用户) | P0 |
| Context Compact 四步压缩顺序 (先压 tool results 再总结历史) | P0 |
| Subagent 上下文隔离 (fresh messages[] + 最终文本作单一 tool_result) | P1 |
| 记忆三子系统 (selection/extraction/consolidation 分离) | P1 |
| task-bound worktrees (每任务独立工作目录并行编辑) | P2 |

### 改进建议
1. **P0 agent_orchestrator**: Goal Loop 独立评估器 — 每次提议停止由独立 evaluator 审核, impossible/failed/over-limit 目标优雅回退用户而非死循环
2. **P0 context_injector**: Context Compact 四步压缩顺序 — 先压缩 tool results, 再总结历史, 仍超限才继续降级
3. **P1 agent_orchestrator**: Subagent 上下文隔离 — 子任务拿 fresh messages[], 最终文本作为单一 tool_result 返回, 避免污染主上下文
4. **P1 memory_system**: 记忆三子系统 — selection(选择)/extraction(提取)/consolidation(整合) 三阶段分离
5. **P2 agent_orchestrator**: task-bound worktrees — 每任务独立工作目录, 并行编辑互不干扰
