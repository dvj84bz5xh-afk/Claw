## 学习日期: 2026-06-23

### 学习项目: TheDotMack/claude-mem
- URL: https://github.com/TheDotMack/claude-mem
- Stars: 83,764
- Language: JavaScript
- 相关度: 29 (记忆系统高度对标)
- 作者: Alex Newman (@thedotmack)
- 版本: v13.4.0

### 核心发现

1. **渐进式披露(Progressive Disclosure)** — 3层MCP搜索工作流(search→timeline→get_observations)，先展示紧凑索引(~50-100 tokens)再按需获取详情(~500-1000 tokens)，实现约10x token节省。Claw当前三层记忆全部一次性注入context，无渐进披露机制。

2. **5个生命周期钩子全覆盖** — SessionStart、UserPromptSubmit、PostToolUse、Stop、SessionEnd，在会话全生命周期自动捕获和压缩上下文。Claw目前仅通过system prompt注入memory，无自动化钩子。

3. **混合搜索架构** — Chroma向量数据库(语义搜索) + SQLite FTS5(关键词搜索)，替代纯文件glob查找。Claw当前仅支持按日期glob匹配memory文件，无向量/全文搜索。

4. **Web Viewer实时仪表盘** — 端口37777的HTTP服务，实时展示记忆流(Memory Stream)、会话历史、搜索界面。Claw无任何可视化界面。

5. **隐私控制标签** — `<private>`标签自动排除敏感内容不被logging/compression。Claw无此机制。

### 可借鉴点

| 优点 | 优先级 | 说明 |
|------|--------|------|
| Progressive Disclosure 3层检索 | P0 | 减少记忆注入token 70%+，实现按需记忆加载 |
| Chroma+SQLite FTS5混合搜索 | P0 | 语义+关键词双通道检索，替换纯文件glob |
| 5生命周期钩子自动捕获 | P1 | 自動捕获PostToolUse等事件写入memory |
| Web Viewer实时仪表盘 | P1 | 记忆流可视化，降低调试/观察成本 |
| Privacy标签机制 | P2 | 敏感内容<private>自动排除 |

### 改进建议

1. **P0: Progressive Disclosure记忆注入** — 实现3层检索(search→timeline→get_observations)，先在SessionStart注入紧凑索引(每个memory分段≤100 tokens)，当Agent需要时再通过工具调用获取详情。预期降低70%记忆相关token消耗。

2. **P0: 混合搜索后端** — 引入Chroma向量数据库或langchain向量存储，建立memory语义索引，同时保留SQLite FTS5关键词搜索。用RRF(Reciprocal Rank Fusion)融合两种搜索结果。

3. **P1: 自动化记忆捕获钩子** — 在PostToolUse阶段自动提取关键工具调用结果摘要写入daily log，减少手动memory更新依赖。

4. **P1: Memory Web Dashboard** — 构建轻量级记忆流可视化页面，展示今日/本周/本月memory活动、实体关联图。

5. **P2: 隐私过滤器** — 支持`<private>...</private>`标签在memory压缩时自动脱敏。

### Claw对标分析

| 维度 | Claw现状 | claude-mem方案 | 差距 |
|------|---------|---------------|------|
| 记忆检索 | 一次性注入+glob文件 | Progressive Disclosure 3层 | 大 |
| 搜索后端 | 纯文件glob | Chroma向量+FTS5混合 | 大 |
| 自动捕获 | 手动规则(MEMORY.md) | 5钩子全覆盖 | 中 |
| 可视化 | 无 | Web Viewer实时流 | 大 |
| 隐私控制 | 无 | `<private>`标签 | 小 |
| 成本优化 | 无量化 | 10x token节省+99.9%账单降低 | 大 |
