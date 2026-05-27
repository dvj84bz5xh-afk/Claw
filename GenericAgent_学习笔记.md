# GenericAgent 学习笔记

**项目地址**：https://github.com/lsdefine/GenericAgent  
**Star 数**：5,496（本周新增 +3,914）  
**论文**：*GenericAgent: A Token-Efficient Self-Evolving LLM Agent via Contextual Information Density Maximization*（arXiv:2604.17091）  
**核心特点**：~3K 行核心代码，自我进化，Token 消耗仅为同类产品的 1/10

---

## 一、核心设计哲学

GenericAgent 的核心假设是：**AI Agent 的能力不应该来自更大的模型或更多的训练，而应该来自更好的上下文组织**。

传统 Agent 的问题：
- 上下文窗口越大，噪声越多，幻觉越多
- Token 消耗与上下文长度成正比
- 每次任务都从零开始，无法积累经验

GenericAgent 的解决方案：
- **分层记忆系统**：L0-L4 五级记忆，按需加载
- **技能沉淀机制**：每次任务自动固化为可复用 Skill
- **极简工具集**：9 个原子工具，其余能力按需安装

---

## 二、分层记忆系统详解

### L0 — 元规则
- Agent 的基础行为规则（类似 `CLAUDE.md`）
- 每次会话都必须加载
- 内容：工具使用规范、输出格式要求、安全标准

### L1 — 记忆索引
- 极简索引层，用于快速路由与召回
- 不存储完整内容，只存储"有什么记忆、在哪里"
- 类似图书馆的目录卡

### L2 — 全局事实
- 长期运行过程中积累的稳定知识
- 例如："用户使用 Windows 11"、"用户偏好 PowerShell 命令"
- 跨任务、跨会话生效

### L3 — 任务 Skills / SOPs
- 完成特定任务类型的可复用流程
- 例如："下载 TikTok 视频" → 安装 yt-dlp → 构造命令 → 执行
- 下次同类任务直接调用，无需重新摸索

### L4 — 会话归档
- 从已完成任务中提炼的归档记录
- 用于长程召回（几周前的类似任务）
- 压缩存储，仅保留关键信息

---

## 三、自我进化机制详解

完整的技能生成流程：

```
[用户提出新任务]
    ↓
[Agent 首次执行：安装依赖 → 编写脚本 → 调试验证]
    ↓
[任务成功完成]
    ↓
[自动将执行路径固化为 Skill 文件]
    ↓
[写入 L3 记忆层]
    ↓
[下次同类任务：直接调用 Skill，无需重新摸索]
```

### 实证案例（来自 README）

| 用户指令 | 首次执行操作 | 后续执行 |
|---|---|---|
| "读我的微信消息" | 安装依赖 → 逆向数据库 → 编写读取脚本 → 保存 Skill | 一行命令调用 |
| "监控股票并提醒我" | 安装 mootdx → 构建选股流程 → 配置定时任务 → 保存 Skill | 一句话启动 |
| "用 Gmail 发这个文件" | 配置 OAuth → 编写发送脚本 → 保存 Skill | 直接可用 |

### 技能库的复利效应

- 初始状态：每次任务都从零开始，Token 消耗 100%
- 积累 10 个 Skill：同类任务 Token 消耗降低到 30%
- 积累 50-100 个 Skill：同类任务 Token 消耗降低到 10%（官方宣称比基线低 6 倍）

---

## 四、最小工具集详解

GenericAgent 仅提供 9 个原子工具，构成外部交互基础能力：

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `code_run` | 执行任意代码 | 安装 Python 包、运行脚本、调用 API |
| `file_read` | 读取文件 | 读取配置、查看数据文件 |
| `file_write` | 写入文件 | 保存 Skill、记录结果 |
| `file_patch` | 修改文件 | 更新配置、修复脚本 |
| `web_scan` | 感知网页内容 | 获取网页文本、提取信息 |
| `web_execute_js` | 控制浏览器行为 | 点击按钮、填写表单、截图 |
| `ask_user` | 人机协作确认 | 需要用户确认时暂停 |
| `update_working_checkpoint` | 更新工作检查点 | 长任务中间状态保存 |
| `start_long_term_update` | 启动长期更新 | 将当前会话内容写入 L4 归档 |

### 为什么只有 9 个工具？

传统 Agent 框架（如 OpenAI Agents、LangChain）提供几十上百个工具，问题是：
- 工具越多，选择困难，错误率越高
- 大部分工具很少用到，浪费上下文窗口
- Agent 容易"过度使用工具"

GenericAgent 的哲学：
- 9 个原子工具足够完成任何任务（因为 `code_run` 可以动态安装任何能力）
- 常用能力固化为 Skill，放入 L3 记忆层
- 工具集保持最小，降低选择错误

---

## 五、与您的诈骗调查工作的结合点

### 应用点1：自动化每日 GitHub AI 项目学习

**当前流程**：
1. 您手动告诉我"学习本周 GitHub 热门 AI 项目"
2. 我调用 `web_search` + `web_fetch` 获取信息
3. 生成学习报告

**使用 GenericAgent 优化**：
1. 将"GitHub AI 项目学习"固化为 Skill
2. Skill 内容：
   - 调用 GitHub API 获取 Trending 列表
   - 使用 `web_fetch` 获取项目 README
   - 生成结构化学习报告
3. 下次您只需要说"学习本周 GitHub"，Agent 直接调用 Skill

**Token 节省**：首次生成 Skill 约消耗 10K Token，后续每次调用仅需 2K Token。

---

### 应用点2：TikTok 视频下载与整理

**当前流程**：
1. 您提供 TikTok 视频链接
2. 我调用 Python 脚本下载
3. 手动整理到桌面文件夹

**使用 GenericAgent 优化**：
1. 将"TikTok 视频下载 + 按项目分类整理"固化为 Skill
2. 下次您说"下载这个 TikTok 视频并归入波贝诈骗园区项目"
3. Agent 直接调用 Skill，自动完成下载 + 分类 + 重命名

---

### 应用点3：加密货币洗钱路径分析

**当前流程**：
1. 您提供交易哈希或地址
2. 我调用区块链浏览器 API 获取交易数据
3. 手动分析并生成报告

**使用 GenericAgent 优化**：
1. 将"加密货币交易路径追踪"固化为 Skill
2. Skill 内容：
   - 调用 Etherscan/Blockchain.com API
   - 递归追踪资金流向
   - 生成可视化路径图
3. 下次同类任务直接调用

---

### 应用点4：调查报告自动生成

**当前流程**：
1. 收集数据（TikTok 视频、交易记录、公开信息）
2. 手动编写 Markdown 报告
3. 导出为 PDF 或 PPT

**使用 GenericAgent 优化**：
1. 将"调查报告生成"固化为 Skill
2. Skill 内容：
   - 读取数据文件（CSV/JSON/Markdown）
   - 按照预定义模板生成报告
   - 自动插入图表（如果数据支持）
3. 下次您说"生成波贝园区诈骗调查报告"
4. Agent 自动汇总近期数据，生成标准化报告

---

## 六、部署建议（为您的工作环境）

### 方案A：本地部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/lsdefine/GenericAgent.git
cd GenericAgent

# 2. 使用 uv 安装依赖（比 pip 更快）
uv pip install -e ".[ui]"

# 3. 配置 API Key
copy mykey_template.py mykey.py
# 编辑 mykey.py，填入您的 Claude API Key

# 4. 启动
python launch.pyw
```

### 方案B：让 GenericAgent 自己完成部署（自举演示）

```bash
# 启动 GenericAgent（空白环境）
python launch.pyw

# 然后对它说：
"帮我克隆 GenericAgent 仓库到本地，安装所有依赖，配置我的 Claude API Key，然后重启"
```

根据 README，GenericAgent 的所有操作（从安装 Git、git init 到每一条 commit message）均由 GenericAgent 自主完成。

---

## 七、与您已使用的工具的协同

| 工具 | 用途 | 与 GenericAgent 的关系 |
|------|------|------------------------|
| Claude Code | 代码编写、项目开发 | GenericAgent 可调用 Claude Code 作为底层模型 |
| RAG-Anything | 私有知识库、文档语义检索 | GenericAgent 可将 RAG 查询封装为 Skill |
| 虾评技能 | 扩展 Agent 能力 | GenericAgent 的 Skill 可发布到虾评平台 |
| Signal Arena | 虚拟炒股 | 无直接关系（除非您想让 Agent 自动交易） |

---

## 八、学习路径建议

### 第一周：理解理念
1. 阅读 arXiv 论文（https://arxiv.org/abs/2604.17091）
2. 理解"上下文信息密度最大化"的核心思想
3. 对比 GenericAgent 与 OpenAI Agents、LangChain 的架构差异

### 第二周：本地部署测试
1. 按照"方案A"完成本地部署
2. 通过 Streamlit UI 完成 5 个简单任务
3. 观察 Skill 目录的变化（应该新增了 5 个 Skill 文件）

### 第三周：定制 Skill
1. 为您的诈骗调查工作编写第一个自定义 Skill
2. 例如："TikTok 视频下载 + 按项目分类"
3. 测试 Skill 的复用性和鲁棒性

### 第四周：集成到工作流
1. 将 GenericAgent 接入您的微信（可选）
2. 实现"发微信消息 → Agent 执行任务 → 返回结果"的工作流
3. 评估 Token 节省效果

---

## 九、注意事项与限制

### 注意事项
1. **API Key 费用**：GenericAgent 虽然 Token 效率高，但仍然调用商业 LLM API（如 Claude），需要自费
2. **技能质量依赖**：自动生成的 Skill 可能不够鲁棒，需要人工审核
3. **学习曲线**：理解分层记忆系统需要时间，不要期望立即上手

### 限制
1. **不支持多模态**：当前版本主要处理文本和代码，图像处理能力有限
2. **依赖外部 API**：某些 Skill 需要外部 API Key（如 Etherscan、GitHub API）
3. **社区生态早期**：相比 LangChain，第三方 Skill 数量较少

---

## 十、下一步行动

1. **Star + Fork** 此仓库（https://github.com/lsdefine/GenericAgent）
2. **本地部署**：按照"方案A"完成安装
3. **阅读论文**：理解 Token 效率的数学原理
4. **设计第一个 Skill**：思考"诈骗调查工作中最重复的任务是什么？"
5. **加入社区**：按照 README 中的二维码加入官方微信群

---

**学习总结**：GenericAgent 的核心价值不在于"更聪明的模型"，而在于"更聪明的上下文组织"。对您的诈骗调查工作，最直接的收益是：**将重复性任务（TikTok 视频下载、交易路径追踪、报告生成）固化为 Skill，让 Agent 越用越聪明，Token 消耗越来越低**。
