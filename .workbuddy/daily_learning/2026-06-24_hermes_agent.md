## 学习日期: 2026-06-24

### 学习项目: NousResearch/hermes-agent
- URL: https://github.com/NousResearch/hermes-agent
- Stars: 200,203
- 语言: Python
- 当前版本: v0.17.0 (2026.6.19)
- 提交数: 12,672+
- 相关度评分: 29/30

### 项目定位
"The agent that grows with you" — Nous Research出品的自改进AI Agent，唯一内置学习循环的Agent框架。

### 核心发现

1. **内置学习循环 (Built-in Learning Loop)**
   - Agent从经验中**自动创建Skill**，使用过程中**持续改进Skill**
   - 主动提醒自己保存知识（self-nudge to persist knowledge）
   - 跨会话搜索历史对话构建用户画像
   - 区别于其他框架的静态工具集，Hermes是动态自进化的

2. **`/learn` 万能学习命令**
   - 输入：目录/URL/对话工作流/粘贴笔记 — 任意来源
   - 输出：标准化 SKILL.md（≤60字符描述+标准章节顺序+工具框架）
   - 零引擎依赖，纯prompt驱动（agent用自己的工具收集→编写→标准化）
   - 在Dashboard/TUI/CLI全表面可用

3. **轨迹压缩器 (Trajectory Compressor)**
   - 自动压缩对话历史，管理上下文窗口
   - 库代码设计（不使用logging.basicConfig污染根日志）
   - 解决长对话token爆炸问题

4. **插件化架构 + MCP生态**
   - `optional-mcps/` 内置MCP目录（Unreal Engine 5.8, Cloudflare等）
   - `optional-skills/` 内置Skills目录
   - `plugins/platforms/` 消息平台插件（Telegram/Discord/Slack/飞书/钉钉等9个）
   - 声明式插件发现（目录扫描 + entry-point）

5. **ACP协议 (Agent Collaboration Protocol)**
   - 跨Agent通信协议，类似A2A
   - acp_adapter + acp_registry 模块

6. **多表面统一架构**
   - CLI / TUI / Desktop / Telegram / Discord / Web Dashboard
   - 同一Agent后端，多前端入口
   - Gateway + TUI Gateway 双模式

### 可借鉴点

| 优点 | 优先级 | 对应Claw模块 |
|------|--------|-------------|
| `/learn` 万能学习命令（零引擎纯prompt驱动） | **P0** | 技能学习系统 |
| 内置学习循环（创建Skill→使用中改进→主动保存） | **P0** | 进化引擎 |
| 轨迹压缩器（上下文窗口管理） | P1 | 记忆系统 |
| 插件化MCP目录（optional-mcps/声明式manifest） | P1 | MCP集成 |
| 多表面统一后端（Gateway架构） | P2 | 多客户端 |
| 主动知识持久化提醒（self-nudge） | P2 | 记忆系统 |

### 改进建议

1. **P0: 实现 `/learn` 命令** — 借鉴Hermes零引擎prompt驱动模式，让Claw工作区对话可直接提取Skill，无需手动编写SKILL.md
2. **P0: 升级学习循环** — 从"夜间离线批处理"升级为"持续在线学习"，每次对话后自动触发Skill创建/改进检查
3. **P1: 轨迹压缩器** — 长对话自动摘要+关键信息保留，解决Claw记忆系统纯文件存储的性能瓶颈
4. **P2: 插件化MCP目录** — 参考optional-mcps/结构，将Claw的MCP Connector管理标准化为声明式manifest

### 与Claw系统对比

| 维度 | Hermes Agent | Claw 当前 | 差距 |
|------|-------------|----------|------|
| 技能学习 | `/learn`自动提取 | 手动编写SKILL.md | 自动化不足 |
| 进化模式 | 持续在线学习 | 夜间批处理 | 时效性差 |
| 上下文管理 | 轨迹压缩器 | 纯文件存储 | 缺少压缩 |
| MCP管理 | 声明式manifest目录 | 分散配置 | 标准化不够 |
| 多表面 | Gateway统一后端 | 单一客户端 | 架构差距 |
