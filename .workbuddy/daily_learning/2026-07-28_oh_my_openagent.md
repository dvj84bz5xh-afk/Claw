## 学习日期: 2026-07-28

### 学习项目: code-yeongyu/oh-my-openagent (OmO)
- URL: https://github.com/code-yeongyu/oh-my-openagent
- Stars: 66,677
- Language: TypeScript
- 相关度: 37

### 项目概述

OmO (Oh My OpenAgent) 是一个多线束Agent操作系统（Multi-Harness Agent OS），支持OpenCode、Codex、Pi、Claude Code等多种Agent线束。核心理念："The future isn't picking one winner; it's orchestrating them all." 专注于Token效率最大化与Agent纪律化执行。

### 核心发现

1. **Hash-Anchored Edit (Hashline)** — 每行代码附加内容哈希标签(`LINE#ID`)，Agent编辑时引用标签而非复现内容。文件变更则哈希不匹配，编辑被拒绝。Grok Code Fast 1成功率从6.7%飙升至68.3%，仅靠更换编辑工具。解决了"线束问题"——大多数Agent失败不是模型问题而是编辑工具问题。

2. **Category-Based Agent Delegation** — Sisyphus编排器按工作类别(visual-engineering/deep/quick/ultrabrain)委派，而非直接选模型。类别自动映射到最优模型。Agent只需声明需要什么类型的工作，线束自动选模型。

3. **IntentGate** — 在分类或行动之前分析用户的真实意图，防止字面误解。不再出现"用户说X但实际想要Y"的执行偏差。

4. **Skill-Embedded MCPs** — 每个Skill自带MCP服务器，按需启动，作用域限定于任务，完成后自动销毁。上下文窗口保持干净，避免MCP吞噬Token预算。

5. **Goal Continuation + Todo Enforcer** — `/goal`持久化每会话目标，空闲时自动重新注入继续提示直到完成审计通过。Agent空闲 → 系统强制拉回。任务必完成。

6. **Hierarchical AGENTS.md (`/init-deep`)** — 自动生成分层AGENTS.md文件（项目级→目录级→组件级），Agent自动读取相关上下文。零手动管理，Token效率最大化。

7. **Ulw Loop Evidence Audit** — 持久化多目标编排，基于`.omo/ulw-loop/`的证据审计。每个目标完成需通过证据验证。

8. **Team Mode v4.0** — Lead Agent + 最多8个并行成员，tmux实时可视化，`team_*`工具族。hyperplan(5个对抗性评审者)和security-research(3猎手+2 PoC工程师)两个预设团队。

9. **Multi-Harness Adapter Layering** — 包分层重构：纯TS核心逻辑 / MCP服务器 / Skills / 适配器垫片各自独立，同一逻辑跨线束复用零重复。

10. **Discipline Agents命名体系** — Sisyphus(编排器) / Hephaestus(深度执行) / Prometheus(战略规划) / Oracle / Librarian / Explore，每个Agent调优到对应模型优势。

### 可借鉴点

| 优点 | 优先级 | 模块 | 说明 |
|------|--------|------|------|
| Hash-Anchored Edit (Hashline) | P0 | context_injector | 内容哈希行标签+编辑前校验，消除stale-line错误，编辑成功率从6.7%→68.3% |
| Category-Based Agent Delegation | P0 | model_scheduler | 按工作类别委派而非直接选模型，类别→模型自动映射 |
| IntentGate意图分析 | P0 | agent_orchestrator | 行动前分析真实意图，防字面误解 |
| Skill-Embedded MCPs | P0 | tool_registry | Skill自带MCP按需启动+作用域限定+自动销毁 |
| Goal Continuation + Todo Enforcer | P0 | agent_orchestrator | 持久目标+空闲强制拉回+完成审计 |
| Hierarchical AGENTS.md | P0 | context_injector | 分层上下文文件自动生成+自动读取相关层 |
| Ulw Loop Evidence Audit | P1 | agent_orchestrator | 持久多目标编排+证据审计 |
| Team Mode (Lead+Parallel) | P1 | agent_orchestration | 并行多Agent团队+tmux可视化+team_*工具 |
| Multi-Harness Adapter Layering | P1 | agent_core | 包分层：核心/MCP/Skills/适配器各自独立 |
| Background Agents | P1 | agent_orchestrator | 5+专家并行+上下文精简+就绪返回 |

### 改进建议

1. **P0: 在context_injector中实现Hash-Anchored Edit** — 读取文件时为每行附加内容哈希(`LINE#ID`)，编辑时通过标签引用而非复现整行。文件变更检测→拒绝stale编辑。这是对GateGuard文件安全机制的根本性升级，从"编辑前先Read"升级为"编辑时哈希校验"。

2. **P0: 在model_scheduler中实现Category-Based Delegation** — 定义工作类别枚举(visual-engineering/deep/quick/ultrabrain/analysis/security)，Agent声明所需类别，调度器自动映射到最优模型。比声明式路由规则更进一步——Agent不需要知道模型名，只需要知道工作类型。

3. **P0: 在agent_orchestrator中实现IntentGate** — 在任务分发前增加意图分析层：解析用户输入→提取真实意图→校正字面误解→生成意图摘要→传递给执行Agent。减少"做了但做错"的情况。

4. **P0: 在tool_registry中实现Skill-Embedded MCPs** — 每个Skill可声明自带的MCP服务器配置，加载Skill时按需启动MCP，卸载Skill时自动停止。MCP作用域限定于当前任务上下文，避免全局MCP吞噬Token。

5. **P0: 在agent_orchestrator中实现Goal Continuation** — 每会话可设置持久目标，空闲超时自动注入继续提示，Todo Enforcer强制Agent回到未完成任务。完成需通过证据审计（类似Ulw Loop）。

6. **P0: 在context_injector中实现Hierarchical Context Files** — `/init-deep`命令自动生成分层AGENTS.md（项目→目录→组件），Agent根据当前工作路径自动加载相关层。替代手动CLAUDE.md管理。
