## 学习日期: 2026-10-01

### 学习项目: browser-use/browser-harness
- URL: https://github.com/browser-use/browser-harness
- Stars: 18,247
- 语言: Python | 相关度: 33

### 核心发现
1. **Self-healing harness (自愈)** — agent 工作时遇到缺失的 helper 就自己写一个, 写入 `agent_helpers.py` 持久化, harness 随每个任务自我改进
2. **Protected core + agent-writable workspace 分离** — `src/browser_harness/` 核心受保护不可变, agent 只能在 `agent-workspace/` 扩展区安全地写自定义 helper
3. **CDP websocket 单层直连** — 一条可编辑 CDP websocket 把 LLM 直连真实浏览器, 无中间包装层
4. **工具选择纪律 + 升级阶梯** — SKILL.md 明确「何时不用」: 公开内容的普通 fetch 用 curl 不用浏览器; fetch 失败/JS渲染/登录态/反爬页才升级到浏览器
5. **MCP stdio 单层暴露** — `browser-harness-mcp` 把浏览器控制暴露为 stdio MCP 工具, 任意 MCP client (Claude Code/Devin/Cursor) 可直接驱动, 不重复写第二层 CDP
6. **Daemon 状态保持** — 本地 daemon 跨 CLI 调用保持已 attach 的 tab, 避免每个任务重复开连接/重复开 tab

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| 自愈 harness (agent 遇缺失能力即时写 reusable helper, 随任务持续改进) | P0 |
| Protected core + agent-writable workspace (核心受保护, 扩展区 agent 安全自扩展) | P0 |
| 工具选择纪律 + 升级阶梯 (工具声明"何时不用", fetch失败自动升级) | P1 |
| MCP stdio 单层暴露 (单一 CDP 层, 任意 MCP client 驱动, 不重复写适配层) | P1 |
| Daemon 状态保持 (跨调用保持会话状态, 避免重复建连接) | P2 |

### 改进建议
1. **P0 claw_integration**: 自愈 harness — agent 遇缺失能力时即时写 reusable helper 持久化, 让 harness 随任务持续改进
2. **P0 tool_registry**: Protected core + agent-writable workspace — 核心实现受保护不可变, 扩展区供 agent 安全自扩展
3. **P1 tool_registry**: 工具选择纪律 + 升级阶梯 — 每个工具声明「何时不用」, 轻量方案失败才升级重工具
4. **P1 tool_registry**: MCP stdio 单层暴露 — 能力用单一协议层暴露, 任意 MCP client 驱动, 避免重复写适配层
5. **P2 claw_integration**: Daemon 状态保持 — 跨调用保持会话状态, 避免重复建连接/重复操作
