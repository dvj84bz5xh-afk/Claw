# Claw 架构文档

## 系统架构概览

Claw 是一个自驱动的 AI Agent 进化系统，采用**扫描-分析-学习-改进**四阶段架构。

```
┌─────────────────────────────────────────────────────────────┐
│                    Claw 进化系统架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   GitHub     │───▶│   搜索引擎   │───▶│   分析引擎   │  │
│  │   API        │    │  (关键词轮换) │    │  (相关性评分) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  项目获取    │    │  去重过滤    │    │  创新识别    │  │
│  │  (REST API)  │    │  (跨轮学习)  │    │  (关键词匹配) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  学习追踪    │◀──│   改进生成   │◀──│   能力比对   │  │
│  │  (JSON存储)  │    │  (P0/P1分级) │    │  (Claw比对)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  进化日志    │    │   报告生成   │                      │
│  │  (JSONL追加) │    │  (Markdown)  │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 搜索引擎 (`search_github_trending`)
- **输入**: 搜索关键词（从14个方向随机选7个）
- **处理**: GitHub REST API搜索，按Stars排序
- **输出**: 仓库列表（名称、URL、Stars、描述）
- **限流**: 每次请求间隔3秒，避免API限制

### 2. 分析引擎 (`analyze_project`)
- **输入**: 仓库信息
- **处理**:
  - 关键词匹配评分（16个关键词，3-5分）
  - 创新点识别（10个模式）
  - 改进建议生成（4个模块）
- **输出**: 分析结果（相关度、创新点、改进建议）

### 3. 去重系统 (`load_learned_projects`)
- **数据源**: `learning_tracking.json`
- **逻辑**: 跨轮去重，跳过已学习项目
- **效果**: 避免重复分析，专注新项目

### 4. 学习追踪 (`update_tracking_system`)
- **存储**: `learning_tracking.json`
- **内容**:
  - 项目列表（名称、URL、Stars、相关度、创新点、分析时间）
  - 改进项列表（ID、来源、优先级、模块、建议、状态）
- **去重**: 改进项按建议内容去重
- **限制**: 只保留最近50个项目

### 5. 进化日志 (`evolution_log.jsonl`)
- **格式**: JSONL（每行一个JSON对象）
- **内容**: 时间戳、日志级别、消息
- **用途**: 完整记录进化过程

### 6. 报告生成 (`generate_evolution_report`)
- **格式**: Markdown
- **内容**:
  - 扫描统计（项目数、跳过数、高相关数、改进项数）
  - Top 3 高相关项目
  - P0改进项列表
  - 系统状态

## 数据流

```
GitHub API
    │
    ▼
搜索结果（5个/关键词 × 7个关键词 = 35个）
    │
    ▼
去重过滤（跨轮 + 本轮）
    │
    ▼
分析评分（≥5分保留）
    │
    ▼
学习追踪（JSON存储）
    │
    ▼
报告生成（Markdown）
    │
    ▼
记忆文件（按日期）
```

## 配置项

### 搜索关键词（14个方向）
```python
SEARCH_QUERIES = [
    "AI agent framework",
    "LLM agent tool calling",
    "multi-agent orchestration",
    "AI workflow automation agent",
    "prompt engineering LLM",
    "RAG retrieval augmented",
    "model context protocol MCP",
    "AI code generation agent",
    "agent memory persistent",
    "autonomous AI agent",
    "agent skill system",
    "browser automation agent",
    "agent evaluation benchmark",
    "open source AI agent",
]
```

### 相关性评分关键词
```python
keywords_score = {
    "agent": 5, "llm": 5, "tool": 4, "memory": 4, "rag": 4,
    "workflow": 3, "automation": 3, "multi-agent": 5, "mcp": 5,
    "prompt": 3, "orchestrat": 4, "skill": 4, "plugin": 3,
    "code-generation": 4, "vector": 3, "embedding": 3
}
```

### 改进项模块
- `memory`: 记忆系统
- `agent_orchestration`: 多智能体编排
- `tool_system`: 工具/插件系统
- `knowledge_retrieval`: 知识检索

## 性能指标

| 指标 | 数值 |
|------|------|
| 单轮扫描项目 | 30-35个 |
| 单轮分析时间 | 30-60秒 |
| API请求间隔 | 3秒 |
| 已学习项目数 | 50+ |
| 累计改进项 | 62个 |
| 进化日志条数 | 700+ |

## 扩展点

### 1. 新增搜索方向
在 `SEARCH_QUERIES` 列表中添加新关键词。

### 2. 新增评分规则
在 `keywords_score` 字典中添加新关键词和分数。

### 3. 新增创新模式
在 `innovation_patterns` 字典中添加新模式。

### 4. 新增改进模块
在 `analyze_project` 函数中添加新模块的改进建议生成逻辑。

### 5. 新增通知方式
实现新的通知函数（如钉钉、Slack等），在 `main` 函数中调用。

---

*最后更新: 2026-05-27*
*架构版本: v1.0*
