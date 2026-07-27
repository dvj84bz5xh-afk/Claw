# 学习报告: TencentCloud/TencentDB-Agent-Memory

## 学习日期: 2026-07-27

### 学习项目: TencentCloud/TencentDB-Agent-Memory
- URL: https://github.com/TencentCloud/TencentDB-Agent-Memory
- Stars: 9,312
- Language: TypeScript
- License: Other
- 相关度: 40

### 项目概述
腾讯云出品的团队级 AI Agent 记忆中枢，将对话、文档和代码转化为四种可复用记忆资产（Chat Memory / Skill / LLM-Wiki / Code-Graph）。核心公式：**符号化短期记忆 + 分层长期记忆**。在 OpenClaw 集成场景下，Token 使用量降低最高 61.38%，任务通过率相对提升 51.52%。

### 核心发现

#### 1. Mermaid 符号化记忆 — 最小符号承载最大语义
用 Mermaid 语法编码任务状态转换图，替代冗长散文或扁平 JSON。Agent 在符号图上推理，需验证细节时通过 `node_id` grep 回溯原始文本。实现"数百 Token 替代数十万 Token"的压缩比。

```
冗长日志 → 1.卸载全文至 refs/*.md → 2.提取关系为 Mermaid 画布(含node_id) → 3.轻量注入Agent上下文 → 4.通过node_id按需召回
```

#### 2. L0→L3 分层长期记忆管道
语义金字塔架构，渐进式披露：
- **L0 Conversation** — 原始对话
- **L1 Atom** — 原子事实提取（每N轮触发，最多20条/次，向量去重+冲突检测）
- **L2 Scenario** — 场景块聚合（从原子事实提取模式）
- **L3 Persona** — 用户画像蒸馏（每50条新记忆触发）

上层承载判断和方向，下层承载证据和精度。

#### 3. 全可追溯与无损恢复
维护从高层抽象到地面真实证据的确定性路径：
```
顶层符号(Persona/画布) → 中层索引(Scenario/jsonl) → 底层原始文本(L0/refs)
```
压缩不等于牺牲可追溯性 — 可折叠可展开，抽象但可审计。

#### 4. 白盒可调试性
所有中间产物以人类可读格式保存：
- L2 Scenario 块: 纯 Markdown
- L3 Persona: `persona.md` 可追溯至生成它的 Scenarios
- 短期任务画布: Mermaid 格式
- 原始载荷: 通过 `result_ref` 和 `node_id` 关联

#### 5. 混合检索 + 召回安全控制
- BM25（jieba中文分词）+ 向量 + RRF 融合
- 召回结果数限制（默认5）
- 单条记忆字符限制
- 总字符预算控制
- 超时保护（默认5000ms，超时跳过不阻塞）

#### 6. 本地优先 + 生产就绪
- SQLite + sqlite-vec 零外部依赖
- OpenClaw 插件 + Hermes Gateway 适配器
- Docker 部署 + Windows 原生支持
- API Key + CORS 安全机制

### 可借鉴点
| 优点 | 优先级 | 模块 |
|------|--------|------|
| Mermaid 符号化记忆 — node_id 追溯的上下文压缩 | P0 | context_injector |
| L0→L3 分层记忆管道 — 渐进式事实提取+画像蒸馏 | P0 | memory_system |
| 全可追溯链 — 高层抽象→地面证据的确定性路径 | P0 | memory_system |
| 白盒可调试 — Markdown/Mermaid 中间产物 | P1 | eval_observability |
| 混合RRF检索+召回安全控制 — 超时/预算/数量限制 | P1 | rag_engine |
| 预热指数退避 — 新会话1→2→4翻倍触发 | P1 | memory_system |

### 改进建议

1. **context_injector: Mermaid 符号化上下文压缩**
   - 在 context_injector 模块中实现 Mermaid 画布注入
   - 冗长工具日志卸载至 `refs/*.md`，仅保留轻量 Mermaid 图 + node_id
   - Agent 通过 node_id 按需 grep 回溯原始文本
   - 预期效果: 上下文 Token 消耗降低 50-60%

2. **memory_system: L0→L3 分层记忆管道**
   - 实现 Conversation→Atom→Scenario→Persona 四层渐进式提取
   - 每 N 轮触发 L1 提取（向量去重+冲突检测）
   - L2 场景聚合 + L3 画像蒸馏
   - 替代当前扁平向量存储方案

3. **memory_system: 全可追溯链设计**
   - 维护 Persona→Scenario→Atom→Conversation 确定性路径
   - 避免不可逆压缩，支持无损恢复
   - 每层记忆产物可独立检查和审计

4. **eval_observability: 白盒记忆可调试性**
   - 所有记忆中间产物以 Markdown/Mermaid 格式保存
   - 提供记忆可视化调试界面（persona.md / scenario blocks / task canvas）
   - 召回出错时可定位问题（非黑盒向量分数列表）

5. **rag_engine: 混合 RRF 检索 + 召回安全控制**
   - BM25（jieba中文分词）+ 向量 + RRF 融合检索
   - 召回结果数限制 + 单条字符限制 + 总预算控制
   - 超时保护（5000ms，超时跳过不阻塞对话）

6. **memory_system: 预热指数退避机制**
   - 新会话从第1轮开始触发记忆提取，每次翻倍（1→2→4→…）
   - 避免新会话冷启动期的过度 LLM 调用
   - 空闲超时触发（默认600秒）+ L2 聚合间隔（默认900秒）

### 与 Claw 系统对比

| 维度 | Claw 现状 | TencentDB-Agent-Memory | 差距 |
|------|----------|----------------------|------|
| 记忆架构 | 扁平向量+SQLite | L0→L3分层+渐进式披露 | 缺少层次化 |
| 上下文压缩 | reactive_compact | Mermaid符号化+node_id追溯 | 缺少符号化 |
| 可追溯性 | 日志记录 | 全链路确定性路径 | 缺少白盒 |
| 检索策略 | 语义向量 | BM25+向量+RRF混合 | 缺少混合检索 |
| 可调试性 | 黑盒 | Markdown/Mermaid白盒 | 缺少可视化 |
| 召回安全 | 无限制 | 数量+预算+超时三重控制 | 缺少安全控制 |
