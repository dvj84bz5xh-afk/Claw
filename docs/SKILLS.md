# Claw 技能清单

## 核心技能

### 1. 夜间进化引擎
- **位置**: `.workbuddy/night_evolution_engine.py`
- **功能**: 自动扫描GitHub高星AI项目，学习先进架构
- **频率**: 每2小时运行一次
- **特性**: 跨轮去重、智能分析、改进项生成

### 2. 小米MiMo API工具
- **位置**: `.workbuddy/mimo.py`
- **功能**: 调用小米MiMo大模型API
- **模型**: mimo-v2.5-pro, mimo-v2.5, mimo-v2-omni, mimo-v2-pro
- **用途**: AI推理、代码生成、文本分析

### 3. 学习追踪系统
- **数据**: `.workbuddy/learning_tracking.json`
- **功能**: 记录学习项目和改进项
- **格式**: JSON结构化数据

### 4. 进化日志系统
- **数据**: `.workbuddy/evolution_log.jsonl`
- **功能**: 完整记录进化过程
- **格式**: JSONL（每行一个JSON对象）

## 工作记忆系统

### 记忆文件结构
```
.workbuddy/memory/
├── MEMORY.md              # 长期记忆（跨会话）
├── YYYY-MM-DD.md          # 每日记忆（按日期）
└── archived_*.md          # 归档记忆（>30天）
```

### 记忆内容
- **用户画像**: 职业、技术背景、偏好设置
- **项目状态**: 进行中的项目、已完成的任务
- **技术配置**: 环境配置、工具版本、镜像源
- **进化数据**: 高相关项目、P0改进项、系统状态

## 项目配置

### CLAUDE.md
- **位置**: `CLAUDE.md`
- **功能**: 项目级配置和规则
- **内容**:
  - 项目概述
  - 可用Agent列表
  - 工作区结构
  - 技术栈
  - 强制指令（模型路由规则）

### SOUL.md
- **位置**: `.workbuddy/SOUL.md`
- **功能**: Agent人格和行为准则
- **内容**: Agent列表、工作模式、行为规范

## 工具链

### 开发工具
- **Python**: 3.13.13
- **Node.js**: 24.16.0
- **Git**: 2.54.0
- **npm**: 11.13.0

### 镜像源
- **pip**: mirrors.aliyun.com/pypi/simple/
- **npm**: registry.npmmirror.com

### API配置
- **GitHub**: REST API（无需gh CLI）
- **小米MiMo**: Token Plan API
- **进化引擎**: urllib直连

## 自动化任务

### 夜间进化引擎
- **自动化ID**: automation-1779269888569
- **频率**: 每2小时（HOURLY/INTERVAL=2）
- **有效期**: 2026-05-20 ~ 2026-12-31
- **状态**: 运行中

### 执行流程
1. 加载已学习项目（跨轮去重）
2. 随机选择7个搜索方向
3. 搜索GitHub高星项目
4. 分析项目相关性和创新点
5. 生成改进建议
6. 更新学习追踪系统
7. 生成进化报告
8. 写入记忆文件
9. 发送通知（QQ邮箱，未配置）

## 数据格式

### learning_tracking.json
```json
{
  "projects": [
    {
      "name": "项目名称",
      "url": "GitHub URL",
      "stars": 12345,
      "relevance": 21,
      "key_innovations": ["创新点1", "创新点2"],
      "analyzed_at": "2026-05-27T11:20:25"
    }
  ],
  "improvements": [
    {
      "id": "abc123",
      "source": "来源项目",
      "priority": "P0",
      "module": "agent_orchestration",
      "suggestion": "改进建议",
      "effort": "high",
      "status": "pending",
      "created_at": "2026-05-27T11:20:25"
    }
  ],
  "last_updated": "2026-05-27T11:20:25"
}
```

### evolution_log.jsonl
```json
{"timestamp": "2026-05-27T11:20:25", "level": "INFO", "message": "日志内容"}
```

## 使用指南

### 运行进化引擎
```bash
# 手动运行
python .workbuddy/night_evolution_engine.py

# 查看学习数据
cat .workbuddy/learning_tracking.json | python -m json.tool

# 查看进化日志
tail -20 .workbuddy/evolution_log.jsonl
```

### 使用MiMo API
```bash
# 设置环境变量
export MIMO_API_KEY="your-token-plan-key"

# 对话
python .workbuddy/mimo.py chat "你的问题"

# 带系统提示
python .workbuddy/mimo.py chat --system "你是AI助手" "你的问题"

# 列出模型
python .workbuddy/mimo.py models
```

### 查看学习成果
```bash
# 查看项目追踪文档
cat docs/learning-projects.md

# 查看架构文档
cat docs/ARCHITECTURE.md

# 查看技能清单
cat docs/SKILLS.md
```

---

*最后更新: 2026-05-27*
*技能版本: v1.0*
