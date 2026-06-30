# MEMORY.md - 结构化长期记忆
# 格式版本: v2.0 (Hermes-inspired)
# 最后更新: 2026-06-30

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

### ⚡ 强制规则：模型路由（2026-05-27设定）
- **原则**: MiMo TP API余量>0时，所有AI推理任务必须用MiMo，不得消耗WorkBuddy积分
- **例外**: 用户手动切换模型 / MiMo不可用 / WorkBuddy专属工具调用
- **CLI**: `python .workbuddy/mimo.py chat --system "..." "用户问题"`
- **推荐模型**: mimo-v2.5-pro
- **见CLAUDE.md** 第56-72行完整规则

---

## [PROJECT] 进行中的项目

### Claw 学习追踪系统
- **目的**: 通过GitHub高星项目持续迭代CodeBuddy产品能力
- **状态**: 已完成80个项目分析，识别149项改进项
- **实施率**: P0: 26/46 (56.5%), P1: 70/93 (75.3%), P2: 0/10 (0%), Total: 96/149 (64.4%)
- **最新学习**: ModelEngine-Group/nexent (⭐5356, 相关度34) — 2026-06-29
- **报告目录**: `.workbuddy/daily_learning/`
- **技能目录**: 已创建 `.workbuddy/skills/`
- **P0完成日期**: 2026-06-09（从0%到100%，后因新增P0回落）
- **P1完成日期**: 2026-06-09（从0%到100%，后因新增P1回落）
- **集成完成日期**: 2026-06-09（agent_core 接入主系统，7/7测试PASS）
- **agent_core版本**: v2.1.0-p1-complete
- **模块清单**: model_scheduler, unified_registry, progressive_loader, agent_orchestrator, context_injector, tool_registry, rag_engine, memory_system, eval_observability_skill, **claw_integration**
- **下一步**: 继续新一轮GitHub学习，优先处理P0 pending项

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

## [SKILLSHUB] 中央技能工作区 (2026-06-09新增)

- **路径**: `C:\Users\10127\WorkBuddy\SkillsHub\`
- **用途**: 所有AI生成技能、配置的统一管理中心
- **规则**: 新技能 MUST 优先存放到 SkillsHub/.workbuddy/skills/，然后同步到 ~/.workbuddy/skills/
- **同步**: SkillsHub → 用户级 (单向，SkillsHub为权威来源)
- **详见**: SkillsHub/.workbuddy/CLAUDE.md 和 SkillsHub/.workbuddy/memory/MEMORY.md

## [TECH] 技术环境配置

### 系统环境
- OS: Windows 11 家庭版（Build 26200）, 视觉效果已设为最佳性能
- Shell: PowerShell / Git Bash
- 文件系统: 仅C盘（无D盘）
- npm全局目录: `AppData\Roaming\npm`
- npm缓存: `Local\npm-cache`  
- npm镜像源: registry.npmmirror.com（2026-05-26配置）
- pip镜像源: 阿里云（mirrors.aliyun.com/pypi/simple/）
- **PATH优先级**: Python路径 > Git路径 > Node.js路径 > WindowsApps（2026-05-26修复）

### 已安装工具
- Python: 3.13.13 (`C:\Users\10127\AppData\Local\Programs\Python\Python313\python.exe`) — 2026-05-26重装
- pip: 26.0.1
- Node.js: 24.16.0 (`C:\Program Files\nodejs\node.exe`) — 2026-05-26新装
- npm: 11.13.0
- Git: 2.54.0 (`C:\Program Files\Git\cmd\git.exe`) — 2026-05-26新装
- GitHub API: 通过urllib直连（替换gh CLI） — 2026-05-26修复

### Python 包状态
- **当前状态**: Python 3.13.13 为全新安装，仅包含pip 26.0.1
- **等待安装**: 需要时按需安装（非预装无意义包）
- **进化引擎**: 纯stdlib运行（urllib/json/hashlib），无需额外依赖

### Git配置
- 本地仓库: `c:/Users/10127/WorkBuddy/Claw/.git/`
- 全局配置: core.autocrlf=true, core.longpaths=true, init.defaultBranch=main
- 凭据管理: credential.helper=manager-core（Windows凭据管理器，2026-05-24从store升级）
- 用户名/邮箱: agent@workbuddy.local（Agent-User）
- 长路径支持: Windows LongPathsEnabled=1（已开启）
- **Git别名**: lg (log图), st (状态), ci (提交), br (分支), co (切换), df (差异), dfc (暂存差异), last (最后提交), unstage (取消暂存) — 2026-05-26配置
- **编码**: i18n.commitencoding=utf-8, i18n.logoutputencoding=utf-8, core.quotepath=off — 2026-05-26配置

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

## [EVOLUTION] 夜间进化引擎

- **自动化ID**: automation-1779269888569
- **频率**: 每2小时（HOURLY/INTERVAL=2）
- **有效期**: 2026-05-20 ~ 2026-12-31
- **脚本**: `.workbuddy/night_evolution_engine.py`（v2.0: 2026-05-27全面升级）
- **进化日志**: `.workbuddy/evolution_log.jsonl`
- **学习追踪**: `.workbuddy/learning_tracking.json`
- **仪表盘**: `docs/evolution-dashboard.html`（Chart.js可视化）
- **通知方式**: QQ邮箱（已配置，硬编码于脚本中：1012701669@qq.com）
- **最近执行**: 2026-06-29 08:50 - 1个项目 / 6个改进项（第31轮，细水长流模式）
- **历史累计**: 905条进化日志记录
- **累计改进项**: 149个（P0:26✅+20⏳, P1:70✅+23⏳, P2:0✅+10⏳）
- **v2.0新增功能**: MiMo深度README分析 / 改进项去重+状态跟踪 / 动态搜索关键词 / 项目健康度过滤 / HTML进化仪表盘

### 持续高相关项目 (2026-06-29 更新)
1. **ModelEngine-Group/nexent** (⭐5356, 相关度:34) - 🆕🏆 零代码Agent生成平台，A2A+双层记忆+Skill按需注入
2. **wanxingai/LightAgent** (⭐1005, 相关度:28) - 轻量级Agent框架，memory+MCP+skill+多Agent协作
3. **pydantic/pydantic-ai** (⭐17729, 相关度:28) - 依赖注入+Graph状态机+延迟审批+A2A
4. **NousResearch/hermes-agent** (⭐200203, 相关度:29) - 内置学习循环+万能/learn命令+轨迹压缩
5. **TheDotMack/claude-mem** (⭐83764, 相关度:29) - 3层MCP搜索工作流+Web Viewer记忆流可视化
6. **agno-agi/agno** (⭐40600, 相关度:27) - 三层委托+团队共享状态+LearningMachine跨Agent记忆
7. **mem0ai/mem0** (⭐57829, 相关度:27) - 单轮记忆提取+混合检索+多级记忆架构
8. **raga-ai-hub/RagaAI-Catalyst** (⭐16200, 相关度:27) - 5维追踪+实时护栏+红队测试闭环
9. **langchain-ai/langchain** (⭐132476, 相关度:28) - 分层抽象+模型互操作+全生命周期平台
10. **a2aproject/A2A** (⭐24467, 相关度:29) - Agent Card发现+传输无关协议+Task生命周期

### P0待确认（紧急）
当前P0 pending项集中在 `agent_orchestration` 和 `skill_system` 模块，累计20项未实施。最新候选：
- **trpc-group/trpc-agent-go**（A2A+AG-UI+graph workflows，相关度35）
- **builderz-labs/mission-control**（自托管Agent编排平台，相关度26）
- **headroomlabs-ai/headroom**（LLM上下文压缩，53K stars）
- **历史待实施**: LightAgent/ruflo/nanobrowser等早期项目 pending项
- **实施是唯一出路**

### 基础设施 (2026-05-26)
- Python 3.13 原安装丢失 → winget重装 v3.13.13
- gh CLI 无法安装 → 已切换GitHub REST API
- ⚠️ **新问题**: `python`命令再次解析到WindowsApps桩（需用完整Python路径或重新排序PATH优先级）

---
## [MAINTENANCE] 记忆系统维护

- **2026-05-22**: MEMORY.md 压缩（5587行→199行），旧文件备份为 MEMORY.md.bak2026-05-22
- **过期日志**: 2026-04-16 和 2026-04-17 已归档至 archived_*.md

---
## [METADATA] 记忆文件本身说明
- **格式版本**: v2.0 | **最后更新**: 2026-05-27
- **结构**: 按主题分区（`[USER]` `[PROJECT]` `[TECH]` `[EVOLUTION]` 等）
- **维护**: 每次完成实质性工作后更新对应分区
- **清理**: 超过30天的日志文件归档后删除

---
*本文件是 `.workbuddy/memory/` 系统的核心索引。日常流水记录在各日期文件中。*
