# 学习日期: 2026-10-11

## 学习项目: doobidoo/mcp-memory-service
- URL: https://github.com/doobidoo/mcp-memory-service
- Stars: 2,007 | 相关度: 27 | 语言: Python | License: Apache-2.0
- 简介: 面向 AI Agent 管线（LangGraph/CrewAI/AutoGen/Claude）的开源持久化共享记忆后端 — REST API + MCP + OAuth + CLI + Dashboard 一体，自托管、无云锁定

## 核心发现
1. **多传输统一记忆服务** — 同一记忆后端同时暴露 REST API（框架管线）+ MCP（CLI/IDE）+ Remote MCP over HTTPS+OAuth（浏览器端 claude.ai/ChatGPT），"一个服务，所有传输"
2. **Agent 身份感知记忆** — `X-Agent-ID` 头自动给记忆打 `agent:<id>` 标签，实现按 Agent 身份的检索作用域隔离；`conversation_id` 绕过去重支持增量会话存储
3. **因果知识图谱** — 记忆之间带类型化边（causes / fixes / contradicts），Agent 共享因果链而非孤立事实；D3.js 3D 可视化
4. **SSE 实时事件** — 任意 Agent 存储/删除记忆时实时推送通知，多 Agent 协作时记忆状态可感知
5. **自主整理(Consolidation)** — 自动压缩旧记忆、抽出 Insight Cards（模式/趋势/知识缺口）；实体抽取自动链接 @mentions/#tags/URL/文件路径
6. **混合后端** — SQLite(本地5ms) / Cloudflare(多设备同步) / Hybrid(本地读+后台云同步) / Milvus；Embedding 用 ONNX 本地跑，数据不出基础设施
7. **质量评分** — 可对任意 OpenAI 兼容端点（Ollama/LiteLLM/vLLM）做记忆质量点评分

## 可借鉴点
| 优点 | 优先级 |
|------|--------|
| Agent 身份作用域记忆(X-Agent-ID自动tag+按tag检索隔离) | P0 |
| 因果类型化知识图谱边(causes/fixes/contradicts) | P1 |
| SSE事件总线(记忆写入/删除实时通知多Agent) | P1 |
| 自主整理+Insight Cards(旧记忆压缩+模式/缺口洞察) | P2 |

## 改进建议
1. [P0] Claw 记忆系统引入 Agent 身份作用域：每条记忆自动携带产生者 Agent ID 标签，检索时按身份/会话作用域过滤，实现多 Agent 记忆隔离与共享的平衡
2. [P1] 在语义记忆图上增加因果类型化边（导致/修复/矛盾），让记忆检索返回因果链而非孤立事实
3. [P2] 增加记忆自主整理守护：定期压缩陈旧记忆为 Insight Cards（模式/趋势/知识缺口），控制记忆库无限膨胀
