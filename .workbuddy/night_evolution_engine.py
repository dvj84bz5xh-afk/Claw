"""
小龙虾夜间进化引擎 v2.0
=======================
功能：
1. 搜索GitHub Trending AI/Agent项目
2. 深度分析项目架构和核心思想（MiMo API深度分析README）
3. 比对现有Claw系统能力
4. 生成改进项并评分（去重+状态跟踪）
5. 更新学习追踪系统
6. 生成HTML进化仪表盘
7. 发送QQ邮箱通知（需配置环境变量）

v2.0 新增：
- MiMo API深度分析README（P0-1）
- 改进项状态跟踪 + 已跟踪项不再重复生成（P0-2）
- 动态搜索关键词生成（P1-1）
- 项目健康度过滤（P1-2）
- HTML进化仪表盘（P2-1）
- QQ邮箱推送优化（P2-2）

触发：每2小时运行一次
设计：自动化友好，所有输出为结构化日志
"""
import os
import json
import hashlib
import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import base64
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# ============================================================
# 配置区
# ============================================================
WORKSPACE = Path("C:/Users/10127/WorkBuddy/Claw")
MEMORY_DIR = WORKSPACE / ".workbuddy" / "memory"
EVOLUTION_LOG = WORKSPACE / ".workbuddy" / "evolution_log.jsonl"
TRACKING_FILE = WORKSPACE / ".workbuddy" / "learning_tracking.json"
DASHBOARD_FILE = WORKSPACE / "docs" / "evolution-dashboard.html"

# GitHub Token（用于API调用）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 小米MiMo Token Plan API（深度分析用）
MIMO_API_KEY = os.environ.get("MIMO_API_KEY", "")
MIMO_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

# 静态搜索关键词（基础方向）
STATIC_SEARCH_QUERIES = [
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

# QQ邮箱配置
QQ_EMAIL = os.environ.get("QQ_EMAIL_ACCOUNT", "1012701669@qq.com")
QQ_AUTH = os.environ.get("QQ_EMAIL_AUTH_CODE", "jbdksdgqsprubdjf")

# 飞书配置
FEISHU_APP_ID = "cli_aa9ccbc13c789cc7"
FEISHU_APP_SECRET = "e8gx7PBQxEad2Pdh5RdasfLePy7n24b8"
FEISHU_CHAT_ID = "oc_a21fbaa09500d12e205c1769403d13f1"

# ============================================================
# 基础工具
# ============================================================

def log(msg: str, level: str = "INFO"):
    """结构化日志"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    print(f"[{level}] {datetime.now().strftime('%H:%M:%S')} {msg}")
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def github_api(url: str, timeout: int = 30) -> Optional[Dict]:
    """统一GitHub API调用"""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "Claw-Evolution-Engine/2.0")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log(f"GitHub API HTTP {e.code}: {url[:80]}", "WARN")
        return None
    except Exception as e:
        log(f"GitHub API失败: {e}", "WARN")
        return None

def mimo_analyze(prompt: str, system: str = "你是一个AI项目分析专家。", max_tokens: int = 500) -> str:
    """调用MiMo API进行深度分析"""
    if not MIMO_API_KEY:
        return ""
    try:
        url = f"{MIMO_BASE_URL}/chat/completions"
        payload = json.dumps({
            "model": "mimo-v2.5-pro",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_completion_tokens": max_tokens,
            "temperature": 0.3,
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {MIMO_API_KEY}")

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log(f"MiMo API调用失败: {e}", "WARN")
        return ""

def send_feishu_message(text: str) -> bool:
    """通过飞书发送群消息"""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET or not FEISHU_CHAT_ID:
        log("飞书未配置，跳过", "WARN")
        return False
    try:
        # 获取tenant_access_token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode("utf-8")
        req = urllib.request.Request(token_url, data=token_payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
        token = token_data.get("tenant_access_token", "")
        if not token:
            log(f"飞书token获取失败: {token_data}", "ERROR")
            return False

        # 发送消息
        msg_url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        msg_payload = json.dumps({
            "receive_id": FEISHU_CHAT_ID,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }).encode("utf-8")
        req2 = urllib.request.Request(msg_url, data=msg_payload, method="POST")
        req2.add_header("Content-Type", "application/json")
        req2.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            result = json.loads(resp2.read().decode("utf-8"))
        if result.get("code") == 0:
            log("飞书消息已发送")
            return True
        else:
            log(f"飞书发送失败: {result}", "ERROR")
            return False
    except Exception as e:
        log(f"飞书发送异常: {e}", "ERROR")
        return False

def send_qq_email(subject: str, body: str) -> bool:
    """通过QQ邮箱SMTP发送通知（微信绑定QQ邮箱后可推送到微信）"""
    if not QQ_EMAIL or not QQ_AUTH:
        log("QQ邮箱未配置，跳过邮件发送", "WARN")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = QQ_EMAIL
        msg["To"] = QQ_EMAIL  # 发给自己
        msg["Subject"] = subject

        # 纯文本 + HTML双格式
        text_part = MIMEText(body, "plain", "utf-8")
        html_body = body.replace("\n", "<br>").replace(" ", "&nbsp;")
        html_part = MIMEText(f"<pre style='font-family:monospace;font-size:13px;'>{html_body}</pre>", "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30) as server:
            server.login(QQ_EMAIL, QQ_AUTH)
            server.sendmail(QQ_EMAIL, [QQ_EMAIL], msg.as_string())
        log(f"邮件已发送: {subject}")
        return True
    except Exception as e:
        log(f"邮件发送失败: {e}", "ERROR")
        return False

def count_evolution_entries() -> int:
    """统计进化日志条目数"""
    if not EVOLUTION_LOG.exists():
        return 0
    return sum(1 for _ in open(EVOLUTION_LOG, "r", encoding="utf-8"))

# ============================================================
# P1-1: 动态搜索关键词生成
# ============================================================

def generate_dynamic_queries(tracking: Dict) -> List[str]:
    """根据已学习项目动态生成新搜索方向"""
    dynamic = []

    # 从已学习项目的创新点中提取高频方向
    innovation_freq = {}
    for proj in tracking.get("projects", []):
        for inn in proj.get("key_innovations", []):
            innovation_freq[inn] = innovation_freq.get(inn, 0) + 1

    # 创新点 → 搜索关键词映射
    innovation_to_query = {
        "多智能体协作架构": "multi-agent collaboration framework",
        "记忆/状态持久化机制": "agent memory persistent store",
        "工具调用/函数调用能力": "LLM function calling framework",
        "检索增强生成(RAG)": "agentic RAG framework 2025",
        "工作流编排": "AI agent workflow orchestration",
        "代码生成能力": "AI code generation autonomous",
        "提示工程优化": "prompt engineering techniques 2025",
        "Model Context Protocol集成": "MCP server client implementation",
        "智能体编排": "agent orchestration platform",
        "自我改进/学习能力": "self-improving AI agent",
    }

    # 优先选择高频但搜索次数少的方向
    for inn, freq in sorted(innovation_freq.items(), key=lambda x: -x[1]):
        query = innovation_to_query.get(inn, "")
        if query and query not in STATIC_SEARCH_QUERIES:
            dynamic.append(query)
        if len(dynamic) >= 5:
            break

    # 补充新兴方向（固定列表，定期更新）
    emerging = [
        "agentic AI platform 2025",
        "A2A agent protocol",
        "AI agent security guardrails",
        "structured output LLM agent",
        "local AI agent offline",
    ]
    for q in emerging:
        if q not in dynamic:
            dynamic.append(q)
        if len(dynamic) >= 8:
            break

    return dynamic

# ============================================================
# P1-2: 项目健康度过滤
# ============================================================

def check_project_health(repo: Dict) -> Tuple[bool, str]:
    """检查项目健康度，返回(是否健康, 原因)"""
    updated_at = repo.get("updatedAt", "")
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            days_since = (datetime.now(last_update.tzinfo) - last_update).days
            if days_since > 365:
                return False, f"超过{days_since}天未更新"
        except Exception:
            pass

    # 检查是否归档（需要额外API调用，只对高星项目做）
    if repo.get("stargazersCount", 0) >= 500:
        full_name = repo.get("fullName", "")
        if full_name:
            data = github_api(f"https://api.github.com/repos/{full_name}")
            if data and data.get("archived", False):
                return False, "仓库已归档"

    return True, "健康"

# ============================================================
# 核心功能
# ============================================================

def search_github_trending(query: str) -> List[Dict]:
    """搜索GitHub热门项目"""
    log(f"搜索GitHub: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&per_page=5"
    data = github_api(url)
    if data and "items" in data and data["items"]:
        repos = []
        for item in data["items"]:
            repos.append({
                "name": item.get("name", ""),
                "fullName": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "description": item.get("description", ""),
                "stargazersCount": item.get("stargazers_count", 0),
                "language": item.get("language", ""),
                "updatedAt": item.get("updated_at", ""),
            })
        log(f"找到 {len(repos)} 个仓库")
        return repos
    return []

def fetch_readme(full_name: str) -> str:
    """获取项目README内容"""
    data = github_api(f"https://api.github.com/repos/{full_name}/readme")
    if data and "content" in data:
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content[:3000]  # 截取前3000字符，避免token过多
        except Exception:
            pass
    return ""

def analyze_project(repo: Dict) -> Dict:
    """分析单个项目（v2.0: 结合关键词+MiMo深度分析）"""
    analysis = {
        "name": repo.get("fullName", repo.get("name", "unknown")),
        "url": repo.get("url", ""),
        "stars": repo.get("stargazersCount", 0),
        "language": repo.get("language", ""),
        "description": repo.get("description", ""),
        "analyzed_at": datetime.now().isoformat(),
        "relevance_score": 0,
        "key_innovations": [],
        "applicable_to_claw": [],
        "improvement_suggestions": [],
        "health_status": "unknown",
        "mimo_analysis": ""
    }

    # P1-2: 健康度过滤
    healthy, reason = check_project_health(repo)
    analysis["health_status"] = reason
    if not healthy:
        log(f"跳过不健康项目: {analysis['name']} ({reason})")
        analysis["relevance_score"] = -1
        return analysis

    name_lower = analysis["name"].lower()
    desc_lower = (analysis["description"] or "").lower()
    all_text = f"{name_lower} {desc_lower}"

    # 基础关键词评分
    keywords_score = {
        "agent": 5, "llm": 5, "tool": 4, "memory": 4, "rag": 4,
        "workflow": 3, "automation": 3, "multi-agent": 5, "mcp": 5,
        "prompt": 3, "orchestrat": 4, "skill": 4, "plugin": 3,
        "code-generation": 4, "vector": 3, "embedding": 3,
        "agentic": 4, "a2a": 3, "guardrail": 3, "benchmark": 3,
    }
    for kw, score in keywords_score.items():
        if kw in all_text:
            analysis["relevance_score"] += score

    # 识别创新点
    innovation_patterns = {
        "multi-agent": "多智能体协作架构",
        "memory": "记忆/状态持久化机制",
        "tool-calling": "工具调用/函数调用能力",
        "rag": "检索增强生成(RAG)",
        "workflow": "工作流编排",
        "code-generation": "代码生成能力",
        "prompt-engineering": "提示工程优化",
        "mcp": "Model Context Protocol集成",
        "orchestration": "智能体编排",
        "self-improving": "自我改进/学习能力",
        "agentic": "Agent化架构",
        "benchmark": "评估基准测试",
        "guardrail": "安全护栏/防护",
    }
    for pattern, desc in innovation_patterns.items():
        if pattern.replace("-", "") in all_text.replace("-", ""):
            analysis["key_innovations"].append(desc)

    # 生成改进建议（v2.0: 更精细的建议）
    suggestions_map = {
        "memory": {
            "module": "memory",
            "suggestion_tpl": "借鉴 {name} 的记忆管理方案，优化memory系统的持久化和检索能力",
            "priority": "P1", "effort": "medium"
        },
        "multi-agent_orchestrat": {
            "module": "agent_orchestration",
            "suggestion_tpl": "参考 {name} 的多智能体编排模式，实现Agent协作和任务分配",
            "priority": "P0", "effort": "high"
        },
        "tool_mcp": {
            "module": "tool_system",
            "suggestion_tpl": "研究 {name} 的工具注册/发现机制，增强ToolRegistry能力",
            "priority": "P1", "effort": "medium"
        },
        "rag_vector": {
            "module": "knowledge_retrieval",
            "suggestion_tpl": "引入 {name} 的检索增强方案，构建Claw的RAG能力",
            "priority": "P1", "effort": "medium"
        },
        "workflow": {
            "module": "workflow_engine",
            "suggestion_tpl": "借鉴 {name} 的工作流编排方案，实现任务自动化流水线",
            "priority": "P1", "effort": "medium"
        },
        "benchmark": {
            "module": "evaluation",
            "suggestion_tpl": "参考 {name} 的评估方法，建立Claw能力评测体系",
            "priority": "P1", "effort": "low"
        },
    }

    if "memory" in all_text:
        analysis["applicable_to_claw"].append("记忆系统")
        tpl = suggestions_map["memory"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    if "multi-agent" in all_text or "orchestrat" in all_text:
        analysis["applicable_to_claw"].append("多智能体系统")
        tpl = suggestions_map["multi-agent_orchestrat"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    if "tool" in all_text or "mcp" in all_text:
        analysis["applicable_to_claw"].append("工具/插件系统")
        tpl = suggestions_map["tool_mcp"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    if "rag" in all_text or "vector" in all_text:
        analysis["applicable_to_claw"].append("知识检索")
        tpl = suggestions_map["rag_vector"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    if "workflow" in all_text:
        analysis["applicable_to_claw"].append("工作流引擎")
        tpl = suggestions_map["workflow"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    if "benchmark" in all_text or "evaluat" in all_text:
        analysis["applicable_to_claw"].append("评估体系")
        tpl = suggestions_map["benchmark"]
        analysis["improvement_suggestions"].append({
            "module": tpl["module"],
            "suggestion": tpl["suggestion_tpl"].format(name=analysis["name"]),
            "priority": tpl["priority"],
            "effort": tpl["effort"]
        })

    # P0-1: MiMo深度分析README（仅对高相关项目）
    if MIMO_API_KEY and analysis["relevance_score"] >= 8:
        readme = fetch_readme(analysis["name"])
        if readme:
            prompt = f"""分析以下GitHub项目，评估其对AI Agent系统的参考价值。

项目: {analysis['name']}
描述: {analysis['description']}
Stars: {analysis['stars']}
语言: {analysis['language']}

README摘要:
{readme[:2000]}

请用JSON格式回答（不要其他文字）：
{{"relevance": 0-30, "innovations": ["创新点1", "创新点2"], "applicable": ["可借鉴点1"], "summary": "一句话总结"}}"""
            result = mimo_analyze(prompt, max_tokens=300)
            if result:
                try:
                    # 提取JSON
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        mimo_data = json.loads(result[json_start:json_end])
                        # 合并MiMo分析结果
                        mimo_relevance = mimo_data.get("relevance", 0)
                        analysis["relevance_score"] = max(analysis["relevance_score"], mimo_relevance)
                        for inn in mimo_data.get("innovations", []):
                            if inn not in analysis["key_innovations"]:
                                analysis["key_innovations"].append(inn)
                        analysis["mimo_analysis"] = mimo_data.get("summary", "")
                        log(f"MiMo深度分析: {analysis['name']} -> 相关度{mimo_relevance}")
                except json.JSONDecodeError:
                    log(f"MiMo返回非JSON: {result[:100]}", "WARN")

    return analysis

def compare_with_claw(analysis: Dict) -> Dict:
    """与Claw系统比对"""
    comparison = {
        "existing_capability_gap": [],
        "integration_feasibility": "",
        "estimated_benefit": 0
    }
    claw_modules = {
        "memory": "memory_retriever + memory_scorer + memory_tagger",
        "agent_orchestration": "agent-team-orchestration skill",
        "tool_system": "ToolRegistry + agent-core",
        "knowledge_retrieval": "RAG待建设",
        "workflow_engine": "workflow待建设",
        "evaluation": "评估体系待建设",
    }
    for suggestion in analysis.get("improvement_suggestions", []):
        module = suggestion["module"]
        existing = claw_modules.get(module, "未覆盖")
        comparison["existing_capability_gap"].append({
            "module": module, "existing": existing, "gap": suggestion["suggestion"]
        })
    if analysis["relevance_score"] >= 15:
        comparison["estimated_benefit"] = 8
        comparison["integration_feasibility"] = "高 - 直接相关"
    elif analysis["relevance_score"] >= 10:
        comparison["estimated_benefit"] = 5
        comparison["integration_feasibility"] = "中 - 需适配"
    else:
        comparison["estimated_benefit"] = 2
        comparison["integration_feasibility"] = "低 - 参考价值"
    return comparison

# ============================================================
# P0-2: 改进项状态跟踪
# ============================================================

def load_existing_improvements() -> Tuple[Set[str], Dict[str, Dict]]:
    """加载已有改进项，返回(已跟踪建议集合, {id: improvement})"""
    seen_suggestions = set()
    improvements_by_id = {}
    if TRACKING_FILE.exists():
        try:
            data = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
            for imp in data.get("improvements", []):
                seen_suggestions.add(imp.get("suggestion", ""))
                improvements_by_id[imp.get("id", "")] = imp
        except Exception:
            pass
    return seen_suggestions, improvements_by_id

def update_tracking_system(analyses: List[Dict]):
    """更新学习追踪系统（v2.0: 改进项去重+状态跟踪）"""
    tracking = {"projects": [], "improvements": [], "last_updated": "", "round_stats": []}
    if TRACKING_FILE.exists():
        try:
            tracking = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 添加新项目（健康且相关度>=8）
    new_projects = 0
    for analysis in analyses:
        if analysis["relevance_score"] >= 8 and analysis["health_status"] != "不健康":
            tracking["projects"].append({
                "name": analysis["name"],
                "url": analysis["url"],
                "stars": analysis["stars"],
                "relevance": analysis["relevance_score"],
                "key_innovations": analysis["key_innovations"],
                "analyzed_at": analysis["analyzed_at"],
                "language": analysis["language"],
                "mimo_summary": analysis.get("mimo_analysis", ""),
            })
            new_projects += 1

    # P0-2: 改进项 - 跳过已跟踪的建议
    existing_suggestions, _ = load_existing_improvements()
    new_improvements = 0
    skipped_improvements = 0

    for analysis in analyses:
        for imp in analysis.get("improvement_suggestions", []):
            suggestion_text = imp["suggestion"]
            if suggestion_text in existing_suggestions:
                skipped_improvements += 1
                continue  # 已跟踪，跳过
            imp_hash = hashlib.md5(suggestion_text.encode()).hexdigest()[:8]
            tracking["improvements"].append({
                "id": imp_hash,
                "source": analysis["name"],
                "priority": imp["priority"],
                "module": imp["module"],
                "suggestion": suggestion_text,
                "effort": imp["effort"],
                "status": "pending",
                "created_at": analysis["analyzed_at"],
                "updated_at": analysis["analyzed_at"],
            })
            existing_suggestions.add(suggestion_text)
            new_improvements += 1

    log(f"改进项: 新增{new_improvements}个, 跳过已跟踪{skipped_improvements}个")

    # 只保留最近100个项目
    tracking["projects"] = tracking["projects"][-100:]

    # 记录本轮统计
    tracking.setdefault("round_stats", []).append({
        "time": datetime.now().isoformat(),
        "new_projects": new_projects,
        "new_improvements": new_improvements,
        "skipped_improvements": skipped_improvements,
    })
    # 只保留最近50轮统计
    tracking["round_stats"] = tracking["round_stats"][-50:]

    tracking["last_updated"] = datetime.now().isoformat()
    TRACKING_FILE.write_text(json.dumps(tracking, ensure_ascii=False, indent=2), encoding="utf-8")

# ============================================================
# P2-1: HTML进化仪表盘
# ============================================================

def generate_dashboard(tracking: Dict):
    """生成HTML进化仪表盘"""
    projects = tracking.get("projects", [])
    improvements = tracking.get("improvements", [])
    round_stats = tracking.get("round_stats", [])
    p0 = [i for i in improvements if i.get("priority") == "P0"]
    p1 = [i for i in improvements if i.get("priority") == "P1"]
    pending = [i for i in improvements if i.get("status") == "pending"]

    # 按模块统计
    module_counts = {}
    for imp in improvements:
        mod = imp.get("module", "unknown")
        module_counts[mod] = module_counts.get(mod, 0) + 1

    # 按语言统计
    lang_counts = {}
    for p in projects:
        lang = p.get("language", "Unknown") or "Unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # 趋势数据（最近20轮）
    trend_labels = [s.get("time", "")[:16] for s in round_stats[-20:]]
    trend_projects = [s.get("new_projects", 0) for s in round_stats[-20:]]
    trend_improvements = [s.get("new_improvements", 0) for s in round_stats[-20:]]

    # Top 10 项目
    top_projects = sorted(projects, key=lambda x: x.get("relevance", 0), reverse=True)[:10]
    top_labels = [p.get("name", "").split("/")[-1][:15] for p in top_projects]
    top_relevance = [p.get("relevance", 0) for p in top_projects]
    top_stars = [p.get("stars", 0) for p in top_projects]

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claw 进化仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
.header {{ text-align: center; margin-bottom: 30px; }}
.header h1 {{ color: #58a6ff; font-size: 2em; }}
.header p {{ color: #8b949e; margin-top: 5px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; }}
.card h3 {{ color: #58a6ff; margin-bottom: 15px; font-size: 1.1em; }}
.stat-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; }}
.stat-label {{ color: #8b949e; }}
.stat-value {{ color: #f0f6fc; font-weight: bold; }}
.stat-value.p0 {{ color: #f85149; }}
.stat-value.p1 {{ color: #d29922; }}
.chart-container {{ position: relative; height: 250px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; font-size: 0.9em; }}
th {{ color: #58a6ff; }}
td a {{ color: #58a6ff; text-decoration: none; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
.badge-p0 {{ background: #f8514922; color: #f85149; }}
.badge-p1 {{ background: #d2992222; color: #d29922; }}
.badge-pending {{ background: #8b949e22; color: #8b949e; }}
</style>
</head>
<body>
<div class="header">
<h1>Claw 进化仪表盘</h1>
<p>最后更新: {tracking.get('last_updated', 'N/A')[:19].replace('T', ' ')} | 已运行 {len(round_stats)} 轮</p>
</div>

<div class="grid">
<div class="card">
<h3>📊 核心指标</h3>
<div class="stat-row"><span class="stat-label">扫描项目总数</span><span class="stat-value">{len(projects)}</span></div>
<div class="stat-row"><span class="stat-label">改进项总数</span><span class="stat-value">{len(improvements)}</span></div>
<div class="stat-row"><span class="stat-label">P0待实施</span><span class="stat-value p0">{len(p0)}</span></div>
<div class="stat-row"><span class="stat-label">P1待评估</span><span class="stat-value p1">{len(p1)}</span></div>
<div class="stat-row"><span class="stat-label">待处理总数</span><span class="stat-value">{len(pending)}</span></div>
<div class="stat-row"><span class="stat-label">进化日志</span><span class="stat-value">{count_evolution_entries()} 条</span></div>
</div>

<div class="card">
<h3>🏗️ 改进项分布（按模块）</h3>
<div class="chart-container"><canvas id="moduleChart"></canvas></div>
</div>

<div class="card">
<h3>🔤 项目语言分布</h3>
<div class="chart-container"><canvas id="langChart"></canvas></div>
</div>

<div class="card">
<h3>📈 进化趋势（最近20轮）</h3>
<div class="chart-container"><canvas id="trendChart"></canvas></div>
</div>
</div>

<div class="card" style="margin-bottom:20px;">
<h3>🔥 Top 10 高相关项目</h3>
<div class="chart-container" style="height:300px;"><canvas id="topChart"></canvas></div>
</div>

<div class="card" style="margin-bottom:20px;">
<h3>📋 学习项目列表</h3>
<table>
<tr><th>#</th><th>项目</th><th>Stars</th><th>相关度</th><th>语言</th><th>关键创新</th></tr>
"""

    for i, p in enumerate(sorted(projects, key=lambda x: x.get("relevance", 0), reverse=True)[:30]):
        name = p.get("name", "")
        url = p.get("url", "#")
        stars = p.get("stars", 0)
        rel = p.get("relevance", 0)
        lang = p.get("language", "") or "-"
        inns = ", ".join(p.get("key_innovations", [])[:2])
        html += f'<tr><td>{i+1}</td><td><a href="{url}" target="_blank">{name}</a></td><td>{stars:,}</td><td>{rel}</td><td>{lang}</td><td>{inns}</td></tr>\n'

    html += """</table></div>

<div class="card">
<h3>⚠️ P0改进项（待实施）</h3>
<table>
<tr><th>#</th><th>来源</th><th>模块</th><th>建议</th><th>状态</th></tr>
"""

    for i, imp in enumerate(p0):
        src = imp.get("source", "")
        mod = imp.get("module", "")
        sug = imp.get("suggestion", "")[:60]
        status = imp.get("status", "pending")
        badge_cls = "badge-pending" if status == "pending" else "badge-p0"
        html += f'<tr><td>{i+1}</td><td>{src}</td><td>{mod}</td><td>{sug}</td><td><span class="badge {badge_cls}">{status}</span></td></tr>\n'

    html += f"""</table></div>

<script>
const chartColors = ['#58a6ff','#f85149','#d29922','#3fb950','#bc8cff','#f778ba','#79c0ff','#ffa657'];

// 模块分布饼图
new Chart(document.getElementById('moduleChart'), {{
  type: 'doughnut',
  data: {{
    labels: {json.dumps(list(module_counts.keys()), ensure_ascii=False)},
    datasets: [{{ data: {json.dumps(list(module_counts.values()))}, backgroundColor: chartColors }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#c9d1d9' }} }} }} }}
}});

// 语言分布饼图
new Chart(document.getElementById('langChart'), {{
  type: 'doughnut',
  data: {{
    labels: {json.dumps(list(lang_counts.keys()), ensure_ascii=False)},
    datasets: [{{ data: {json.dumps(list(lang_counts.values()))}, backgroundColor: chartColors }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#c9d1d9' }} }} }} }}
}});

// 进化趋势折线图
new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: {json.dumps(trend_labels)},
    datasets: [
      {{ label: '新项目', data: {json.dumps(trend_projects)}, borderColor: '#58a6ff', tension: 0.3 }},
      {{ label: '新改进项', data: {json.dumps(trend_improvements)}, borderColor: '#3fb950', tension: 0.3 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, scales: {{ x: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#21262d' }} }}, y: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#21262d' }} }} }}, plugins: {{ legend: {{ labels: {{ color: '#c9d1d9' }} }} }} }}
}});

// Top 10 项目柱状图
new Chart(document.getElementById('topChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(top_labels, ensure_ascii=False)},
    datasets: [
      {{ label: '相关度', data: {json.dumps(top_relevance)}, backgroundColor: '#58a6ff' }},
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, scales: {{ x: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#21262d' }} }}, y: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#21262d' }} }} }}, plugins: {{ legend: {{ labels: {{ color: '#c9d1d9' }} }} }} }}
}});
</script>

<div style="text-align:center;color:#8b949e;margin-top:30px;padding:10px;">
<p>Generated by Claw Evolution Engine v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
</body></html>"""

    DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_FILE.write_text(html, encoding="utf-8")
    log(f"仪表盘已生成: {DASHBOARD_FILE}")

# ============================================================
# 报告生成
# ============================================================

def generate_evolution_report(analyses: List[Dict], comparisons: List[Dict], skipped: int = 0) -> str:
    """生成进化报告（v2.0）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    healthy_analyses = [a for a in analyses if a["relevance_score"] >= 0]
    total_improvements = sum(len(a["improvement_suggestions"]) for a in healthy_analyses)
    mimo_count = sum(1 for a in healthy_analyses if a.get("mimo_analysis"))

    report = f"""
========================================
  小龙虾夜间进化报告 v2.0
  时间: {now}
========================================

  本轮进化扫描
  搜索方向: 7 个（静态+动态）
  发现项目: {len(healthy_analyses)} 个（新学习）
  跳过已学习: {skipped} 个
  健康度过滤: {len(analyses) - len(healthy_analyses)} 个
  MiMo深度分析: {mimo_count} 个
  高相关项目: {sum(1 for a in healthy_analyses if a['relevance_score'] >= 10)} 个
  生成改进项: {total_improvements} 个（已去重）

  高相关项目 Top 3:
"""

    sorted_analyses = sorted(healthy_analyses, key=lambda x: x["relevance_score"], reverse=True)
    for i, a in enumerate(sorted_analyses[:3]):
        mimo_tag = f" [MiMo: {a['mimo_analysis'][:30]}]" if a.get("mimo_analysis") else ""
        report += f"  {i+1}. {a['name']} (Stars:{a['stars']}, 相关度:{a['relevance_score']}){mimo_tag}\n"
        report += f"     {a['description'][:80]}\n"
        report += f"     创新点: {', '.join(a['key_innovations'][:3])}\n"

    report += f"""
  系统状态
  学习追踪: {TRACKING_FILE.exists()}
  进化日志: 共 {count_evolution_entries()} 条记录
  仪表盘: docs/evolution-dashboard.html

  待确认改进项 (P0):
"""

    p0_items = []
    for a in healthy_analyses:
        for imp in a.get("improvement_suggestions", []):
            if imp["priority"] == "P0":
                p0_items.append(f"  - [{imp['module']}] {imp['suggestion'][:60]}...")

    if p0_items:
        report += "\n".join(p0_items[:5])
    else:
        report += "  (无新增P0项)\n"

    report += f"""
========================================
  进化引擎持续运行中... 下次扫描: 2小时后
========================================
"""
    return report

def append_daily_memory(report: str):
    """追加到当日记忆文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"
    entry = f"""

## 夜间进化引擎 - {datetime.now().strftime('%H:%M')}

{report}

"""
    if memory_file.exists():
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(f"# {today} 工作日志\n{entry}")

def load_learned_projects() -> set:
    """加载已学习过的项目名称集合"""
    learned = set()
    if TRACKING_FILE.exists():
        try:
            data = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
            for proj in data.get("projects", []):
                learned.add(proj.get("name", "").lower())
        except Exception:
            pass
    return learned

# ============================================================
# 主流程
# ============================================================

def main():
    """主进化流程 v2.0"""
    log("========================================")
    log("小龙虾夜间进化引擎 v2.0 启动")
    log("========================================")

    # 加载已学习项目
    learned_projects = load_learned_projects()
    log(f"已学习项目数: {len(learned_projects)}，将跳过重复项目")

    # P1-1: 生成动态搜索关键词
    tracking_data = {}
    if TRACKING_FILE.exists():
        try:
            tracking_data = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    dynamic_queries = generate_dynamic_queries(tracking_data)
    log(f"动态关键词: {len(dynamic_queries)} 个")

    # 合并静态+动态关键词，随机选7个
    all_queries = STATIC_SEARCH_QUERIES + dynamic_queries
    selected_queries = random.sample(all_queries, min(7, len(all_queries)))
    log(f"本轮搜索方向: {len(selected_queries)} 个")

    all_analyses = []
    all_comparisons = []
    skipped_count = 0

    # Phase 1: 搜索与获取
    log("Phase 1: GitHub搜索与项目获取")
    MIN_STARS = 50

    for query in selected_queries:
        repos = search_github_trending(query)
        for repo in repos:
            if repo.get("stargazersCount", 0) < MIN_STARS:
                continue

            repo_full_name = repo.get("fullName", repo.get("name", "")).lower()
            if repo_full_name in learned_projects:
                skipped_count += 1
                log(f"跳过已学习: {repo_full_name}")
                continue

            analysis = analyze_project(repo)
            if analysis["relevance_score"] >= 5:
                all_analyses.append(analysis)
            elif analysis["relevance_score"] == -1:
                skipped_count += 1  # 健康度过滤
        time.sleep(3)

    # 本轮内去重
    seen_names = set()
    unique_analyses = []
    for a in all_analyses:
        if a["name"].lower() not in seen_names:
            seen_names.add(a["name"].lower())
            unique_analyses.append(a)
    all_analyses = unique_analyses

    log(f"Phase 1 完成: {len(all_analyses)} 个新项目，跳过 {skipped_count} 个")

    # Phase 2: 深度分析
    log("Phase 2: 深度分析与比对")
    for analysis in all_analyses:
        comparison = compare_with_claw(analysis)
        all_comparisons.append(comparison)

    # Phase 3: 更新追踪系统
    log("Phase 3: 更新学习追踪系统")
    update_tracking_system(all_analyses)

    # Phase 4: 生成报告
    log("Phase 4: 生成进化报告")
    report = generate_evolution_report(all_analyses, all_comparisons, skipped_count)

    # Phase 5: 生成HTML仪表盘
    log("Phase 5: 生成HTML仪表盘")
    if TRACKING_FILE.exists():
        fresh_tracking = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        generate_dashboard(fresh_tracking)

    # Phase 6: 写入记忆
    log("Phase 6: 写入记忆文件")
    append_daily_memory(report)

    # Phase 7: 发送通知（飞书 + QQ邮箱）
    log("Phase 7: 发送进化通知")
    p0_count = sum(
        1 for a in all_analyses
        for imp in a.get("improvement_suggestions", [])
        if imp["priority"] == "P0"
    )
    subject = f"[小龙虾进化v2.0] {datetime.now().strftime('%m/%d %H:%M')} - {len(all_analyses)}个项目, {p0_count}个P0"

    # 飞书推送
    feishu_text = f"Claw进化报告 v2.0\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n新项目: {len(all_analyses)}个\nP0改进: {p0_count}个\n跳过已学习: {skipped_count}个\n\nTop 3项目:\n"
    sorted_analyses = sorted([a for a in all_analyses if a["relevance_score"] >= 0], key=lambda x: x["relevance_score"], reverse=True)
    for i, a in enumerate(sorted_analyses[:3]):
        feishu_text += f"{i+1}. {a['name']} (相关度:{a['relevance_score']})\n"
    feishu_ok = send_feishu_message(feishu_text)

    # QQ邮箱推送
    email_ok = send_qq_email(subject, report)

    log("========================================")
    log(f"进化完成: {len(all_analyses)} 项目, {p0_count} P0改进")
    log(f"通知状态: 飞书{'已发送' if feishu_ok else '未发送'}, QQ邮箱{'已发送' if email_ok else '未发送'}")
    log("========================================")

    return {
        "projects_found": len(all_analyses),
        "p0_improvements": p0_count,
        "notification_sent": success,
        "report": report
    }

if __name__ == "__main__":
    result = main()
    print("\n" + result["report"])
    sys.exit(0)
