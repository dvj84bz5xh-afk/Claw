## 学习日期: 2026-07-07

### 学习项目: shareAI-lab/learn-claude-code
- URL: https://github.com/shareAI-lab/learn-claude-code
- Stars: 70,074
- Language: Python
- License: MIT
- 相关度: 35

### 核心发现

1. **线束工程范式 (Harness Engineering)**: 核心理念 "Agency Comes from the Model. An Agent Product = Model + Harness." — 线束工程师的职责不是编写智能，而是构建智能运行的世界（Tools + Knowledge + Observation + Action Interfaces + Permissions）

2. **20课渐进式架构教学**: 从基础 agent loop 到多agent团队协作，每章叠加一个机制，所有机制最终回归同一个不变的核心循环

3. **自组织任务认领**: 多Agent通过 MessageBus + inbox 异步协调，空闲Agent自动轮询认领任务，无需领导者逐一分配

4. **Worktree隔离并行执行**: 每个Agent在独立 git worktree 中工作，通过 ID 绑定任务与目录，实现真正的文件系统级隔离

5. **多层上下文压缩**: snipCompact(简单裁剪) → microCompact(细粒度) → reactive_compact(保留近期原文+摘要历史) → autoCompact(自动触发)

### 可借鉴点

| 优点 | 优先级 | 模块 |
|------|--------|------|
| Worktree隔离的多Agent并行执行（文件系统级隔离） | P0 | agent_orchestrator |
| Self-organizing任务认领（无领导者+自动轮询） | P0 | agent_orchestrator |
| reactive_compact上下文压缩（保留近期尾部原文） | P1 | context_injector |
| SkillManifest按需注入（先列元数据，后展开完整内容） | P1 | skill_system |
| 后台线程+通知队列（慢操作非阻塞化） | P2 | agent_core |

### 改进建议

1. **P0-agnet_orchestrator**: 引入 Worktree 隔离模式，使多Agent并行执行时拥有独立文件系统命名空间，避免文件冲突
2. **P0-agent_orchestrator**: 实现自组织任务认领（MessageBus + inbox轮询），减少集中调度开销
3. **P1-context_injector**: 借鉴 reactive_compact 策略 — 保留最近N轮原文，对更早历史进行摘要压缩，平衡保真度和token预算
4. **P1-skill_system**: 将当前"全量注入"改为 SkillManifest 模式 — 先展示技能列表和描述，仅在被调用时注入完整内容
5. **P2-agent_core**: 引入后台任务队列，将慢操作(如大文件处理)异步化，主循环不阻塞

### 姊妹项目参考
- **claw0** (shareAI-lab): 常驻Agent harness — heartbeat + cron + IM多渠道 + memory + Soul人格系统，与Claw的自动化引擎设计高度契合
