# MEMORY.md - 结构化长期记忆
# 格式版本: v2.0 (Hermes-inspired)
# 最后更新: 2026-05-17

---

## [USER] 用户画像与偏好

### 基本信息
- **职业**: 执法培训 + 诈骗园区调查 + CodeBuddy 产品经理
- **技术背景**: Python数据分析、Selenium/BeautifulSoup爬虫、区块链追踪
- **语言偏好**: 中文交流
- **工作风格**: 简洁编号式指令、要结果不要讨论、P0立即实施

### 偏好设置
- **回复长度**: 200-300字
- **输出格式**: 结构化Markdown（表格、分区、成本明细）
- **交付要求**: 工具输出，支持跨客户端访问
- **工作流**: 获取→分析→比对→报告→更新（5步）
- **偏好**: 批量并行处理，AI自主搭建环境

### 禁止行为
- 不要问"是否需要..."，直接做
- 不要输出只有AI才能看懂的分析过程
- 内容必须去AI化，追求实战性

---

## [PROJECT] 进行中的项目

### Claw 学习追踪系统
- **目的**: 通过GitHub高星项目持续迭代CodeBuddy产品能力
- **状态**: 已完成16个项目分析，识别57项改进项
- **实施率**: 1.8%（P0:30, P1:27）
- **报告目录**: `.workbuddy/daily_learning/`
- **技能目录**: 已创建 `.workbuddy/skills/`
- **下一步**: 提高实施率，优先实施P0改进项

### 加密货币洗钱侦察课程
- **课时**: 4课时 × 45分钟 = 180分钟
- **对象**: 经侦人员
- **格式**: 20%理论 + 80%实操
- **重点**: 区块链数据分析、资金流追踪、地址聚类、交易行为建模
- **实战案例**: 何文榕案
- **状态**: 开发中

### 证券直播引流犯罪侦查技战法课程
- **性质**: 新质战斗力课程
- **状态**: 开发中，参考文件格式制作教纲

### 诈骗园区调查
- **重点地区**: 柬埔寨波贝地区
- **任务**: 下载TikTok视频素材、按项目归档、输出Word分析报告
- **资金链路**: 东南亚cybercrime compounds取证
- **相关书籍**: 《Scam: Inside Southeast Asia's Cybercrime Compounds》

---

## [TECH] 技术环境配置

### 系统环境
- OS: Windows 11
- Shell: PowerShell / Git Bash
- 文件系统: 仅C盘（无D盘）
- npm全局目录: `AppData\Roaming\npm`
- npm缓存: `Local\npm-cache`

### 已安装工具
- Python: 3.13.5 (`C:\Users\10127\AppData\Local\Programs\Python\Python313\python.exe`)
- Node.js: 24.14.0 (`C:\Program Files\nodejs\node.exe`)
- Git: 2.53.0.windows.2

### Git配置
- 本地仓库: `c:/Users/10127/WorkBuddy/Claw/.git/`
- 全局配置: core.autocrlf=true, core.longpaths=true, init.defaultBranch=main
- 用户名/邮箱: 未配置（用户选择留空）
- 凭证: 未配置

---

## [SKILL] 已掌握/已创建的技能

### 用户级技能（~/.workbuddy/skills/）
- `caveman-communication`: 超压缩沟通模式，减少75%Token
- `code-quality-scorer`: Claw代码质量量化评分系统
- `install-best-practices`: 源头预防，注入最佳实践规则
- `pre-work-alignment`: 预工作对齐会话，编码前强制对齐需求
- `find-skills`: 帮助发现和安装agent技能
- `skill-creator`: 创建有效技能的指南
- `agent-team-orchestration`: 多agent团队协作编排
- `agent-world`: Agent World统一身份认证与管理
- `oracle`: 使用@steipete/oracle CLI打包prompt
- `android-native-dev`: Android原生应用开发指南
- `api-gateway`: 连接100+ API
- `capability-evolver`: GitHub API token自动化issue报告
- `cloudq`: 腾讯云产品资源查询
- `cnb-skill`: CNB平台OpenAPI交互
- `deep-research`系列: 结构化深度调研工作流
- `education`: 生成学习计划、测验、闪卡
- `Excel-XLSX`: Excel工作簿创建与编辑
- `FBS-BookWriter`: 高质量长文档手稿工具链
- `flutter-dev`: Flutter跨平台开发指南
- `github`: 使用gh CLI交互GitHub
- `gog`: Google Workspace CLI套件
- `impeccable`: 生产级前端界面创建
- `ios-application-dev`: iOS应用开发指南
- `mcp-builder`: 高质量MCP服务器创建指南
- `mcporter`: mcporter CLI管理MCP服务器
- `migraq`: 腾讯云迁移平台全流程能力
- `openclaw-assets-to-workbuddy`: OpenClaw资产迁移
- `pptx-generator`: PowerPoint演示文稿生成
- `qq-email`: QQ邮箱IMAP/SMTP收发
- `react-native-dev`: React Native和Expo开发指南
- `Self-Improving-Proactive-Agent`: 自我改进+主动Agent
- `skill-standardizer`: SKILL.md标准格式实施工具
- `skill-vetter` / `skills-security-check`: 技能安全审查
- `skyline`系列: Skyline渲染引擎全套技能
- `summarize`: 使用summarize CLI总结URL/文件
- `tapd-openapi`: TAPD平台OpenAPI操作
- `tdesign-miniprogram`: TDesign微信小程序UI组件库
- `tencentmap`系列: 腾讯地图全栈开发技能
- `tmux`: 远程控制tmux会话
- `tutor-skills`: 将PDF/代码库转为Obsidian StudyVaults
- `weather`: 获取天气预报（无需API key）
- `whitehat-security`: 白帽安全技能
- `windows-desktop-automation`: Windows桌面自动化
- `Word-DOCX`: Word文档创建与编辑
- `zenstudio`: ZenStudio AI内容创作CLI工具

### 项目级技能（.workbuddy/skills/）
- `git冲突解决助手-rule_based`: 基于规则的Git冲突解决

---

## [AGENT] Agent World 平台

- **用户名**: Claw
- **等级**: A2-1
- **已安装**: Agency-agents（`~/.claude/agents/`），含12个预置Agent
- **功能**: Signal Arena / 虾评 / ABTI

---

## [HARDWARE] AI推理硬件评估（进行中）

### 评估方案
- **Mac Studio M3 Ultra** (192GB统一内存)
- **DGX Spark** (GB10)
- **RTX 4090 × 4** 多卡方案

### 目标
- 本地部署 + 云服务器生产负载
- 70B+ 参数 FP16 全精度推理
- 价格区间与硬件规格对比表

---

## [LEARNING] 已完成的重要学习

### Git上下文增强系统 (2026-04-17)
- Git状态检测、Prompt上下文注入、不确定性分析
- 三层架构：数据获取层、智能分析层、应用集成层
- Windows GBK编码问题已通过UTF-8修复

### 多方案并行生成系统 (2026-04-17)
- 多样化方案生成、多维度评估、智能排序
- 借鉴TimesFM分位数预测思想

### Hermes Agent 借鉴优化方案
- 文件: `c:/Users/10127/WorkBuddy/Claw/hermes_optimization_plan.md`
- 5个阶段：记忆系统增强、技能自动化、多智能体优化、自动化扩展、平台扩展
- **当前状态**: 方案设计完成，待实施 ← 本次重启

---

## [CONTACT] 关键人物（诈骗园区调查）

- 佘志江 (被捕)
- Broken Tooth (在逃)
- 董雷成 (破产)
- Kok An (柬埔寨参议员，深度参与)
- Ly Yong Phat (柬埔寨，深度参与)

---

## [METADATA] 记忆文件本身说明

- **格式版本**: v2.0
- **设计理念**: 借鉴Hermes Agent持久记忆系统
- **结构**: 按主题分区（`[USER]` `[PROJECT]` `[TECH]` 等）
- **检索**: 支持按分区标题快速定位
- **关联**: 每个分区内部按时间倒序排列
- **维护**: 每次完成实质性工作后更新对应分区
- **清理**: 超过30天的日志文件归档至本文件，然后删除

---

*本文件是 `.workbuddy/memory/` 系统的核心索引。*
*日常流水记录在各日期文件中，长期结构化知识在此文件。*
