# Agency-Agents 整合与适配分析

**分析日期**: 2026-05-11  
**项目**: msitarzewski/agency-agents（96k Stars）  
**目标**: 
1. Task #4: 与现有技术栈（GenericAgent、RAG-Anything、GitContext等）整合分析
2. Task #3: 筛选最适合诈骗调查工作的代理

---

## 一、现有技术栈全景

| 组件 | 类型 | 核心能力 | 代码量 |
|------|------|----------|--------|
| **GenericAgent** | 自进化 Agent 框架 | L0-L4分层记忆、技能固化、9原子工具、Token效率极高 | ~3K行核心 |
| **RAG-Anything** | 多模态 RAG | PDF/Office/图像/表格/公式解析、跨模态知识图谱 | 完整框架 |
| **Git Context System** | Git上下文增强 | 状态检测、Prompt注入、不确定性分析 | Python |
| **Multi-solution System** | 多方案生成 | TimesFM分位数预测、多维度评估排序 | Python |
| **Claude Code** | 底层 AI 引擎 | 代码编写、文件操作、网络搜索 | 外部工具 |

---

## 二、任务#4: Agency-agents 与现有技术栈整合深度分析

### 2.1 整合总纲

Agency-agents 提供的是 **"人格 x 流程 x 交付"** 的 Agent 定义层（Markdown），而现有技术栈提供的是 **"记忆 x 进化 x 知识库"** 的执行与基础设施层。两者是天然的互补关系，不存在竞争。

```
┌─────────────────────────────────────────────────┐
│              应用层（诈骗调查工作流）              │
├─────────────────────────────────────────────────┤
│  Agency-Agents (144个专业Agent人格+工作流)       │
│  ↑ 调用              ↑ 引用知识              ↑ 编排  │
├──────────┼──────────────┼──────────────────────┤
│  GenericAgent  │  RAG-Anything  │  GitContext   │
│  (记忆+进化)   │  (知识库)      │  (上下文感知)  │
├─────────────────────────────────────────────────┤
│              Claude Code / AI引擎                │
└─────────────────────────────────────────────────┘
```

### 2.2 整合点1: Agency-Agents x GenericAgent（最核心）

**各有所长**:
- Agency-agents: 144个经过打磨的专业人格和工作流（广度、专业化）
- GenericAgent: 分层记忆系统（L0-L4）和技能固化机制（深度、进化）

**具体整合方案**:

#### A. 将 Agency-Agents 转化为 GenericAgent Skills

Agency-agents 的每个 Agent 定义（Markdown）包含完整的工作流和交付标准。可以将关键的 Agent 转化为 GenericAgent 的 L3 层 Skill：

```
Agency-Agent (.md) ──[转换]──> GenericAgent Skill (L3)

转换规则：
- Agent 核心使命 → Skill 描述
- 工作流过程 → Skill 执行步骤（可执行脚本/代码）
- 技术交付物 → Skill 输出格式定义
- 关键规则 → Skill 前置条件
```

**示例**: 将 "Evidence Collector（证据收集者）" Agent 转化为 Skill
```python
# L3 Skill: evidence_collector
# 来源: Agency Agents - Testing/evidence-collector.md

description: "收集并验证调查过程中的证据"
triggers: ["收集证据", "验证证据", "整理证据"]
steps:
  1. scan_target: web_scan → 获取目标信息
  2. download_evidence: code_run → 调用yt-dlp下载视频
  3. verify: 交叉验证信息来源
  4. organize: 按项目归类存档
  5. output: 生成证据摘要报告
```

#### B. 用 GenericAgent 的记忆系统增强 Agency-Agents

Agency-agents 的每个 Agent 目前是"无状态"的（每次对话从零开始）。整合 GenericAgent 后：

| 层次 | 容量 | 内容 | 来源 |
|------|------|------|------|
| L0 元规则 | 必加载 | 诈骗调查安全规则、数据脱敏标准 | Agency Core |
| L1 索引 | 小 | 已用过的 Agent 列表和效果评分 | 自动生成 |
| L2 全局事实 | 中 | 已知诈骗模式、关键地址、关联实体 | 调查积累 |
| L3 任务Skill | 中 | 各个 Agency-Agent 转换的 Skill | Agency → GenericAgent |
| L4 归档 | 大 | 已完成案例的归档记录 | 历史调查 |

**效果**: 每次使用某个 Agent 调查后，GenericAgent 自动将"什么方法有效"固化到记忆层，下次更高效。

#### C. 创建 "Scam Investigation Orchestrator"

结合 Agency-agents 的 `agents-orchestrator.md` 和 GenericAgent 的 `L0` 层，创建一个专门用于诈骗调查的多 Agent 编排器：

```
Scam Investigation Orchestrator
├── [阶段1] 数据采集 → 调用 Engineering 部门 Agent
│   ├── Crawl4AI 代理 → 抓取公开信息
│   ├── TikTok 证据下载 Skill → 下载视频素材
│   └── Crypto Path Tracer Skill → 追踪交易路径
├── [阶段2] 分析归类 → 调用 Testing/Finance 部门 Agent
│   ├── Evidence Collector → 验证并组织证据
│   ├── Financial Analyst → 分析资金流向
│   └── Pattern Recognizer → 识别诈骗模式
├── [阶段3] 报告生成 → 调用 Marketing/Support 部门 Agent
│   ├── Content Creator → 编写调查报告
│   ├── Data Visualizer → 生成可视化图表
│   └── Analysis Reporter → 输出最终文档
└── [阶段4] 知识沉淀 → GenericAgent 固化
    ├── 将本次调查 Skill 化 → L3记忆
    ├── 更新全局事实 → L2记忆
    └── 归档案例 → L4记忆
```

### 2.3 整合点2: Agency-Agents x RAG-Anything

**互补关系**:
- RAG-Anything: 多模态文档处理 + 知识图谱检索
- Agency-agents: 需要知识输入来驱动 Agent 的决策

**具体方案**:

```
Agency-Agent 询问 ──> RAG-Anything 检索 ──> 返回相关文档片段
    │                                                         
    ├── "这个案例和之前哪个相似？" → 跨模态图谱检索 → 返回相似案例
    ├── "这个交易模式是什么？" → 知识图谱实体检索 → 返回模式描述
    └── "帮我分析这个证据" → 图像+文本联合检索 → 返回分析结果
```

**关键整合**: 将 RAG-Anything 封装为 Agency-Agent 的"知识库工具"，任何 Agent 在调查过程中都可以通过专用接口调用。

### 2.4 整合点3: Agency-Agents x GitContext + Multi-solution

- **GitContext**: 能感知当前 Git 状态，为决策提供上下文。当 Agency-agent 生成报告时，GitContext 注入"当前已收集的证据文件列表"。
- **Multi-solution**: 可以用于评估不同 Agent 组合方案的效果。例如："用 Agent A+E（3人方案）vs Agent B+F+C（5人方案）哪个调查效果更好？"

### 2.5 整合难度评估

| 整合点 | 难度 | 工作量 | 优先级 | 关键依赖 |
|--------|------|--------|--------|----------|
| Agency x GenericAgent Skill 转换 | ⭐⭐⭐ | 中（每Agent约1h） | **最高** | 需熟悉两者格式 |
| Agency x RAG-Anything 知识桥接 | ⭐⭐ | 低（封装API调用） | **高** | RAG已就绪 |
| Agency x GitContext | ⭐ | 低（配置即可） | 中 | - |
| Agency x Multi-solution | ⭐⭐⭐⭐ | 高（需设计评估框架） | 低 | 先完成基础集成 |
| Orchestrator 编排器 | ⭐⭐⭐⭐ | 高（需定制开发） | 中 | 需先完成基础集成 |

---

## 三、任务#3: 最适合诈骗调查工作的 Agent 筛选

### 3.1 筛选标准

从 144 个 Agent 中按以下维度筛选：

1. **直接相关度**: 工作内容是否直接匹配诈骗调查场景（权重 40%）
2. **可转化度**: 能否转化为 GenericAgent Skill 并融入工作流（权重 30%）
3. **独特价值**: 是否有现有技术栈未覆盖的能力（权重 20%）
4. **优先级**: 能否在短期内带来明显效率提升（权重 10%）

### 3.2 筛选结果（按优先级排序）

以下是从 12 个部门 144 个 Agent 中筛选出的 **Top 15** 最相关 Agent：

#### Tier 1: 核心调查 Agent（立即整合，极高价值）

| # | 部门 | Agent 名称 | 适配场景 | 核心价值 |
|---|------|-----------|----------|----------|
| 1 | Engineering | **Security Engineer** | 区块链安全、资金链路分析、地址聚类 | 加密货币追踪的核心技术支撑 |
| 2 | Testing | **Evidence Collector** | 证据收集、交叉验证、来源可信度评估 | 诈骗调查的命脉环节 |
| 3 | Finance | **Financial Analyst** | 交易记录分析、资金流向图、异常交易识别 | 直接对应你的加密货币洗钱课程 |
| 4 | Marketing | **Content Creator** | 调查报告撰写、案情描述、可交付文档 | 产出最终报告的核心角色 |
| 5 | Testing | **Reality Checker** | 事实核查、数据验证、逻辑一致性检查 | 调查结论质量保障 |

#### Tier 2: 辅助增强 Agent（1-2周内整合，高价值）

| # | 部门 | Agent 名称 | 适配场景 | 核心价值 |
|---|------|-----------|----------|----------|
| 6 | Engineering | **Data Analyst** | 数据清洗、统计分析、异常值检测 | 处理批量交易数据 |
| 7 | Product | **Trend Researcher** | 诈骗趋势监测、新手法识别 | 保持对诈骗手法演进的跟踪 |
| 8 | Support | **Analysis Reporter** | 生成结构化报告、数据分析汇总 | 标准化报告输出 |
| 9 | Design | **Data Visualizer** | 可视化交易路径图、资金流向图 | 课件和报告中的可视化 |
| 10 | Project Mgmt | **Studio Producer** | 案件管理、时间线编排、资源协调 | 多案件并行管理 |

#### Tier 3: 进阶 Agent（长期适配，中等价值）

| # | 部门 | Agent 名称 | 适配场景 | 核心价值 |
|---|------|-----------|----------|----------|
| 11 | Engineering | **AI Engineer** | 自定义 AI 工具开发、自动化脚本 | 扩展调查工具箱 |
| 12 | Sales | **Discovery Coach** | 信息挖掘、线索追问、深度访谈 | 采访受害者的结构化方法 |
| 13 | Paid Media | **Search Query Analyst** | 搜索引擎调查技巧、信息检索 | 深网/暗网信息收集 |
| 14 | Testing | **Performance Benchmarker** | 对比分析、基准数据建立 | 不同案件模式对比 |
| 15 | Marketing | **Community Builder** | 社群情报收集、社交网络分析 | 监控诈骗相关社交群组 |

### 3.3 不适合的 Agent（明确排除）

| 部门 | 原因 |
|------|------|
| Spatial Computing（空间计算） | 诈骗调查不涉及 XR/visionOS 开发 |
| Game Dev（游戏开发） | 无游戏相关需求 |
| Paid Media（大部分） | 广告投放与诈骗调查无关 |

### 3.4 快速启动方案（建议本周完成）

**第一步：配置 Agency-agents 到 Claude Code**
```bash
# 克隆仓库
git clone https://github.com/msitarzewski/Agency-agents.git
cd Agency-agents

# 直接复制核心调查 Agent 到 Claude Code
cp agents/specialized/security-engineer.md ~/.claude/agents/
cp agents/specialized/evidence-collector.md ~/.claude/agents/
cp agents/specialized/financial-analyst.md ~/.claude/agents/
cp agents/specialized/content-creator.md ~/.claude/agents/
cp agents/specialized/reality-checker.md ~/.claude/agents/

# 或在Claude Code中使用 @agent-name 激活
```

**第二步：测试核心 Agent 效果**
```markdown
在Claude Code中输入：
"Use the Evidence Collector agent to help me organize the TikTok videos
I downloaded from Poipet scam compounds."

"Use the Financial Analyst agent to analyze this crypto transaction
path from address 0x..."
```

**第三步：选择 2-3 个核心 Agent 转化为 GenericAgent Skill**
- 首选：Evidence Collector（证据工作流最成熟）
- 次选：Financial Analyst（直接支撑资金追踪）
- 三选：Content Creator（报告产出自动化）

---

## 四、综合建议

### 短期（本周）
1. 将 Tier 1 的 5 个 Agent 配置到 Claude Code 并测试
2. 选择 Evidence Collector 尝试转化为 GenericAgent Skill
3. 验证 RAG-Anything 能否作为 Agent 的知识库后端

### 中期（1-2周）
4. 完成 Tier 2 的 5 个 Agent 配置和测试
5. 构建 Scam Investigation Orchestrator 原型
6. 将运行稳定的 Agent 转化为 GenericAgent Skill

### 长期（1个月）
7. 实现多 Agent 自动编排（数据采集→分析→报告→知识沉淀全链路）
8. 开发专用 UI 面板，统一管理 Agent 活动和调查进度

---

## 五、关键结论

1. **Agency-agents 和 GenericAgent 是天然搭档**：前者提供专业人格和流程，后者提供记忆和进化能力。整合后 = 144个专家 + 自我进化。

2. **Agency-agents 和 RAG-Anything 互补**：前者定义"谁来分析和怎么分析"，后者提供"分析所需的知识"。整合后 = 专家 + 知识库。

3. **短期收益最大的是直接使用 Claude Code 配置**：5分钟即可让 5 个核心 Agent 可用，无需任何开发和转换工作。

4. **长期最大价值在 Skill 化**：将 Agency-agents 的工作流转化为 GenericAgent 的 L3 Skill，可以"一次配置，持续复用，自动进化"。

---

**报告生成时间**: 2026-05-11 18:10  
**覆盖任务**: Task #4（整合分析）+ Task #3（Agent筛选）
