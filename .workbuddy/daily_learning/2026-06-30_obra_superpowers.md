## 学习日期: 2026-06-30

### 学习项目: obra/superpowers
- URL: https://github.com/obra/superpowers
- Stars: 241516

### 核心发现
1. 可组合Skill系统：通过 /plugin 安装，一套 Skill 跨 Claude Code、Cursor、Codex、Gemini CLI 等Agent环境自动触发。
2. Spec-Driven Development：Agent 不立即写代码，而是先澄清需求→生成短规格→用户确认→再出实现计划。
3. Subagent-Driven Development：主Agent将工程任务拆给子Agent，自己审阅与推进，可持续运行数小时。
4. 方法论内嵌：Red/Green TDD、YAGNI、DRY 作为 Skill 强制约束注入 Agent 工作流。
5. 双市场分发：官方 Marketplace + 社区 Marketplace，便于 Skill 的发现与版本管理。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| 可组合Skill + 自动触发机制 | P1 |
| Spec-driven 子代理开发流程 | P1 |
| 编码工作流里程碑节点（设计评审/计划确认/TDD检查点） | P2 |
| Skill双市场分发与版本管理思路 | P2 |

### 改进建议
1. 借鉴 obra/superpowers 的可组合Skill设计，实现基于上下文的Skill自动触发机制（模块: skill_system, 优先级: P1, 工作量: medium）。
2. 引入 Spec-driven 子代理开发流程：需求澄清→规格确认→计划审批→子Agent实施→主Agent审阅（模块: agent_orchestration, 优先级: P1, 工作量: high）。
3. 在编码工作流中嵌入设计评审、计划确认、TDD检查点等里程碑节点（模块: workflow_engine, 优先级: P2, 工作量: medium）。

### 与Claw系统比对
- 集成可行性: 高 - 直接相关
- 预期收益: 8/10
