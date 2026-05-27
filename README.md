# Claw - AI Agent 学习进化系统

> 基于GitHub高星项目的自动化AI Agent能力进化平台

## 项目简介

Claw 是一个自驱动的 AI Agent 进化系统，通过**夜间进化引擎**自动扫描 GitHub 高星 AI/Agent 项目，学习先进架构和设计思想，持续迭代自身能力。

## 核心能力

### 🧬 夜间进化引擎
- **自动化扫描**: 每2小时扫描 GitHub Trending AI 项目
- **智能分析**: 自动评估项目相关性、识别关键创新点
- **跨轮去重**: 已学习项目自动跳过，只分析新项目
- **改进项生成**: 自动生成 P0/P1 改进建议
- **学习追踪**: 完整记录学习历史和改进状态

### 📊 学习数据
- **已扫描项目**: 50+ 个高星 AI/Agent 项目
- **改进项**: 62 个（P0: 13, P1: 49）
- **进化日志**: 700+ 条记录

### 🔧 技术栈
- **Python 3.13**: 核心运行时
- **GitHub REST API**: 项目搜索和数据获取
- **JSON**: 数据存储格式
- **Markdown**: 文档生成

## 目录结构

```
Claw/
├── .workbuddy/                 # 核心配置和记忆系统
│   ├── night_evolution_engine.py  # 夜间进化引擎
│   ├── learning_tracking.json     # 学习追踪数据
│   ├── evolution_log.jsonl        # 进化日志
│   ├── memory/                    # 工作记忆（按日期）
│   └── mimo.py                    # 小米MiMo API工具
├── docs/                       # 生成的文档
│   └── learning-projects.md    # 学习项目追踪
├── CLAUDE.md                   # 项目配置和规则
├── README.md                   # 本文件
└── ...                         # 其他项目文件
```

## 快速开始

### 1. 配置环境
```bash
# 确保 Python 3.13+ 已安装
python --version

# 配置 pip 镜像（中国用户）
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### 2. 运行进化引擎
```bash
# 手动运行一次
python .workbuddy/night_evolution_engine.py

# 查看学习数据
cat .workbuddy/learning_tracking.json | python -m json.tool
```

### 3. 查看学习成果
```bash
# 查看项目追踪文档
cat docs/learning-projects.md

# 查看进化日志
tail -20 .workbuddy/evolution_log.jsonl
```

## 学习项目追踪

详见 [docs/learning-projects.md](docs/learning-projects.md)

### Top 5 高相关项目

| 项目 | Stars | 相关度 | 亮点 |
|------|-------|--------|------|
| langchain4j/langchain4j | 12,114 | 26 | Java LLM库，RAG+MCP |
| ruvnet/ruflo | 55,458 | 21 | Claude原生编排平台 |
| nanobrowser/nanobrowser | 13,048 | 21 | 浏览器多Agent工作流 |
| liyupi/ai-guide | 14,576 | 21 | AI资源大全+MCP |
| open-multi-agent | ~6,240 | 19 | DAG自动编排 |

## P0改进项（待实施）

1. **Agent编排系统** - 参考 ruvnet/ruflo 的编排模式
2. **多智能体协作** - 参考 nanobrowser/nanobrowser 的工作流
3. **MCP集成** - 参考 microsoft/mcp-for-beginners 的课程

## 贡献指南

本项目为个人学习进化系统，欢迎：
- 提 Issue 讨论改进方向
- 提交 PR 增加新能力
- 分享你的学习发现

## 许可证

MIT License

---

*最后更新: 2026-05-27*
*进化引擎已运行 22+ 轮，持续学习中...*
