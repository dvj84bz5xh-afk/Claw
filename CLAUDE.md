# CLAUDE.md - Claw Workspace Configuration

## Project Overview
Investigation workspace targeting scam compounds in Cambodia-Thailand border region (Poipet focus). Covers crypto money laundering analysis, TikTok evidence collection, and technical research.

## Available Agents

### Pre-loaded in ~/.claude/agents/ (use @agent-name)
| Agent | Best For |
|-------|----------|
| @blockchain-security-auditor | Blockchain forensics, crypto tracing, smart contract audit |
| @security-engineer | Security analysis, threat modeling, vulnerability assessment |
| @evidence-collector | Evidence gathering, source verification, chain of custody |
| @financial-analyst | Transaction analysis, fund flow mapping, anomaly detection |
| @content-creator | Report writing, case summaries, document creation |
| @reality-checker | Fact-checking, data validation, quality assurance |

### Extra agents also available
@agents-orchestrator, @ai-engineer, @data-analyst, @trend-researcher, @community-builder, @performance-benchmarker

### Usage
```bash
# In Claude Code chat, activate any agent by name:
@evidence-collector Help me organize TikTok video evidence from Poipet
@financial-analyst Analyze this crypto transaction path
```

## Workspace Structure
```
c:/Users/10127/WorkBuddy/Claw/
├── .workbuddy/      # WorkBuddy config + memory
├── agent-core/      # GenericAgent + GitContext + Multi-solution
├── RAG-Anything/    # Multi-modal RAG knowledge base
├── agency-agents/   # Official repo (msitarzewski/agency-agents)
├── scripts/         # Python utilities
├── slides/          # Training course slides (crypto money laundering)
├── 课程资料/        # Course materials for crypto AML training
├── downloads/       # Downloaded skills and tools
└── *.md             # Research reports and analysis documents
```

## Key Technical Stack
- Windows 11 / PowerShell 5.1 (zh-CN, GB2312)
- Python 3.13.13 (C:\Users\10127\AppData\Local\Programs\Python\Python313)
- Node.js v24.16.0 (C:\Program Files\nodejs)
- Git 2.54.0 (C:\Program Files\Git\cmd)
- WorkBuddy IDE + Claude Code

## Evolution Engine
Auto-scans GitHub every 2hr via `.workbuddy/night_evolution_engine.py`
- Search: GitHub REST API (no `gh` CLI needed)
- Logs: `.workbuddy/evolution_log.jsonl` (605+ entries)
- Tracking: `.workbuddy/learning_tracking.json` (44 improvements found)
- Notification: QQ email (not configured)

## Conventions
1. All research reports go to workspace root as *.md files
2. Memory logs in .workbuddy/memory/YYYY-MM-DD.md
3. Scripts in scripts/ directory
4. Always log key decisions and findings to working memory
5. Daily GitHub trending AI projects auto-learned

## 🔴 强制指令：模型路由规则
**优先级: P0 · 不可违反 · 除非手动切换模型否则必须遵守**

### 规则
1. **MiMo API可用时**（余量>0），所有涉及AI推理的任务都必须使用小米MiMo Token Plan API
2. **调用方式**: `python .workbuddy/mimo.py chat --system "..." "用户输入"`
3. **例外条件**: 用户手动在WorkBuddy界面切换了模型，则按用户选择执行
4. **仅当MiMo不可用时**（网络故障/API 429/认证失败），才降级使用WorkBuddy默认模型
5. **不适用场景**: 需要使用WorkBuddy内置工具（如PPT生成、Excel处理、浏览器自动化等）的任务不受此限制

### MiMo API配置快查
- **API地址**: `https://token-plan-cn.xiaomimimo.com/v1` (OpenAI兼容)
- **认证方式**: `Authorization: Bearer <tp-xxx>` 或 `api-key: <tp-xxx>`
- **推荐模型**: `mimo-v2.5-pro`（旗舰推理）
- **其他模型**: mimo-v2.5, mimo-v2-omni, mimo-v2-pro
- **CLI工具**: `python .workbuddy/mimo.py`

## Priority Agents for Fraud Investigation
Tier 1 (immediate use): evidence-collector, blockchain-security-auditor, financial-analyst
Tier 2 (within week): content-creator, reality-checker, security-engineer

## Sync Agents Command
```bash
# Sync latest agents from repo to ~/.claude/agents/
powershell -File scripts/sync_agents.ps1
```
