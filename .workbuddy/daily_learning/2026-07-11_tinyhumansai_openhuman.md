## 学习日期: 2026-07-11

### 学习项目: tinyhumansai/openhuman
- URL: https://github.com/tinyhumansai/openhuman
- Stars: 34612

### 核心发现
1. **Memory Tree 持久化记忆**：将数据压缩为 SQLite 中的 Markdown 树结构，镜像为 Obsidian 知识库，并配合后台"潜意识"循环自动同步生成每日简报
2. **Graph-based Agent 编排**：基于检查点图（非简单循环）运行 Agent 编排，支持三级子 Agent 舰队调度、可视化工作流、审批门控，以及 Signal 端到端加密的 Agent 间通信
3. **SuperContext 深度研究器**：在模型响应前扫描本地记忆与网络，内置网页搜索、爬虫、浏览器、语音（Whisper）及图像/视频生成工具，还能自动加入会议并生成摘要

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| Memory Tree + SQLite Markdown 树 + Obsidian 同步的本地优先记忆架构 | P0 |
| 检查点图（graph）式 Agent 编排与三级子 Agent 舰队调度 | P0 |
| Signal 协议 Agent 间通信 + x402 USDC 支付经济 | P1 |

### 改进建议
1. 在 Claw memory_system 中引入 Markdown 树结构持久化层，支持与本地知识库（Obsidian）双向同步
2. 在 agent_orchestrator 中引入图式执行引擎，支持检查点、子 Agent 舰队、可视化工作流与审批门控
3. 评估 Signal 协议或类似加密通道用于多 Agent 间安全通信的可行性
