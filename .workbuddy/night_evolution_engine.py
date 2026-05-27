"""
小龙虾夜间进化引擎 v1.0
=======================
功能：
1. 搜索GitHub Trending AI/Agent项目
2. 深度分析项目架构和核心思想
3. 比对现有Claw系统能力
4. 生成改进项并评分
5. 更新学习追踪系统
6. 发送QQ邮箱通知（需配置环境变量）

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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 配置区
# ============================================================
WORKSPACE = Path("C:/Users/10127/WorkBuddy/Claw")
MEMORY_DIR = WORKSPACE / ".workbuddy" / "memory"
EVOLUTION_LOG = WORKSPACE / ".workbuddy" / "evolution_log.jsonl"
TRACKING_FILE = WORKSPACE / ".workbuddy" / "learning_tracking.json"

# GitHub搜索关键词轮换
# 搜索关键词列表（每轮随机选7个避免API限流）
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

# QQ邮箱配置
QQ_EMAIL = os.environ.get("QQ_EMAIL_ACCOUNT", "")
QQ_AUTH = os.environ.get("QQ_EMAIL_AUTH_CODE", "")

def log(msg: str, level: str = "INFO"):
    """结构化日志"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    print(f"[{level}] {datetime.now().strftime('%H:%M:%S')} {msg}")
    
    # 追加到进化日志
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def send_qq_email(subject: str, body: str) -> bool:
    """通过QQ邮箱发送通知（微信绑定QQ邮箱后可推送到微信）"""
    if not QQ_EMAIL or not QQ_AUTH:
        log("QQ邮箱未配置，跳过邮件发送", "WARN")
        return False
    
    # 使用qq-email skill的脚本
    skill_dir = Path(os.path.expanduser("~/.workbuddy/skills/QQ邮箱"))
    send_script = skill_dir / "scripts" / "send.js"
    
    if not send_script.exists():
        log(f"send.js 不存在: {send_script}", "ERROR")
        return False
    
    try:
        # 写入临时body文件避免命令行转义问题
        tmpfile = WORKSPACE / ".workbuddy" / "email_body_tmp.txt"
        tmpfile.write_text(body, encoding="utf-8")
        
        result = subprocess.run(
            ["node", str(send_script), QQ_EMAIL, subject],
            input=body,
            text=True,
            capture_output=True,
            timeout=30,
            cwd=str(skill_dir)
        )
        
        if tmpfile.exists():
            tmpfile.unlink()
        
        if result.returncode == 0:
            log(f"邮件已发送: {subject}")
            return True
        else:
            log(f"邮件发送失败: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"邮件发送异常: {e}", "ERROR")
        return False

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def search_github_trending(query: str) -> List[Dict]:
    """搜索GitHub热门项目（使用GitHub REST API）"""
    log(f"搜索GitHub: {query}")
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&per_page=5"
        
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "Claw-Evolution-Engine/1.0")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if GITHUB_TOKEN:
            req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            if "items" in data and data["items"]:
                repos = []
                for item in data["items"]:
                    repos.append({
                        "name": item.get("name", ""),
                        "fullName": item.get("full_name", ""),
                        "url": item.get("html_url", ""),
                        "description": item.get("description", ""),
                        "stargazersCount": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "updatedAt": item.get("updated_at", "")
                    })
                log(f"找到 {len(repos)} 个仓库")
                return repos
            else:
                log(f"搜索返回空结果", "WARN")
    except urllib.error.HTTPError as e:
        log(f"GitHub API HTTP错误 {e.code}: {e.reason}", "WARN")
    except Exception as e:
        log(f"GitHub API搜索失败: {e}", "WARN")
    
    return []

def analyze_project(repo: Dict) -> Dict:
    """深度分析单个项目"""
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
        "improvement_suggestions": []
    }
    
    name_lower = analysis["name"].lower()
    desc_lower = analysis["description"].lower()
    all_text = f"{name_lower} {desc_lower}"
    
    # 相关性评分
    keywords_score = {
        "agent": 5, "llm": 5, "tool": 4, "memory": 4, "rag": 4,
        "workflow": 3, "automation": 3, "multi-agent": 5, "mcp": 5,
        "prompt": 3, "orchestrat": 4, "skill": 4, "plugin": 3,
        "code-generation": 4, "vector": 3, "embedding": 3
    }
    
    for kw, score in keywords_score.items():
        if kw in all_text:
            analysis["relevance_score"] += score
    
    # 识别关键创新点
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
        "self-improving": "自我改进/学习能力"
    }
    
    for pattern, desc in innovation_patterns.items():
        if pattern.replace("-", "") in all_text.replace("-", ""):
            analysis["key_innovations"].append(desc)
    
    # 生成改进建议
    if "memory" in all_text:
        analysis["applicable_to_claw"].append("记忆系统")
        analysis["improvement_suggestions"].append({
            "module": "memory",
            "suggestion": f"借鉴 {analysis['name']} 的记忆管理方案优化现有memory系统",
            "priority": "P1",
            "effort": "medium"
        })
    
    if "multi-agent" in all_text or "orchestrat" in all_text:
        analysis["applicable_to_claw"].append("多智能体系统")
        analysis["improvement_suggestions"].append({
            "module": "agent_orchestration",
            "suggestion": f"参考 {analysis['name']} 的编排模式增强Agent协作",
            "priority": "P0",
            "effort": "high"
        })
    
    if "tool" in all_text or "mcp" in all_text:
        analysis["applicable_to_claw"].append("工具/插件系统")
        analysis["improvement_suggestions"].append({
            "module": "tool_system",
            "suggestion": f"研究 {analysis['name']} 的工具注册/发现机制",
            "priority": "P1",
            "effort": "medium"
        })
    
    if "rag" in all_text or "vector" in all_text:
        analysis["applicable_to_claw"].append("知识检索")
        analysis["improvement_suggestions"].append({
            "module": "knowledge_retrieval",
            "suggestion": f"引入 {analysis['name']} 的检索增强方案",
            "priority": "P1",
            "effort": "medium"
        })
    
    return analysis

def compare_with_claw(analysis: Dict) -> Dict:
    """与现有Claw系统进行比对"""
    comparison = {
        "existing_capability_gap": [],
        "integration_feasibility": "",
        "estimated_benefit": 0
    }
    
    claw_modules = {
        "memory": "memory_retriever + memory_scorer + memory_tagger",
        "agent_orchestration": "agent-team-orchestration skill",
        "tool_system": "ToolRegistry + agent-core",
        "knowledge_retrieval": "RAG待建设"
    }
    
    for suggestion in analysis.get("improvement_suggestions", []):
        module = suggestion["module"]
        existing = claw_modules.get(module, "未覆盖")
        comparison["existing_capability_gap"].append({
            "module": module,
            "existing": existing,
            "gap": suggestion["suggestion"]
        })
    
    # 评估收益
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

def update_tracking_system(analyses: List[Dict]):
    """更新学习追踪系统"""
    # 加载现有追踪数据
    tracking = {"projects": [], "improvements": [], "last_updated": ""}
    if TRACKING_FILE.exists():
        try:
            tracking = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        except:
            pass
    
    # 添加新项目
    for analysis in analyses:
        if analysis["relevance_score"] >= 8:
            tracking["projects"].append({
                "name": analysis["name"],
                "url": analysis["url"],
                "stars": analysis["stars"],
                "relevance": analysis["relevance_score"],
                "key_innovations": analysis["key_innovations"],
                "analyzed_at": analysis["analyzed_at"]
            })
    
    # 添加改进项
    for analysis in analyses:
        for imp in analysis.get("improvement_suggestions", []):
            imp_hash = hashlib.md5(imp["suggestion"].encode()).hexdigest()[:8]
            tracking["improvements"].append({
                "id": imp_hash,
                "source": analysis["name"],
                "priority": imp["priority"],
                "module": imp["module"],
                "suggestion": imp["suggestion"],
                "effort": imp["effort"],
                "status": "pending",
                "created_at": analysis["analyzed_at"]
            })
    
    # 去重改进项
    seen = set()
    unique_improvements = []
    for imp in reversed(tracking["improvements"]):
        if imp["suggestion"] not in seen:
            seen.add(imp["suggestion"])
            unique_improvements.append(imp)
    tracking["improvements"] = list(reversed(unique_improvements))
    
    # 只保留最近50个项目
    tracking["projects"] = tracking["projects"][-50:]
    
    tracking["last_updated"] = datetime.now().isoformat()
    
    TRACKING_FILE.write_text(json.dumps(tracking, ensure_ascii=False, indent=2), encoding="utf-8")

def generate_evolution_report(analyses: List[Dict], comparisons: List[Dict], skipped: int = 0) -> str:
    """生成进化报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_stars = sum(a["stars"] for a in analyses)
    total_improvements = sum(len(a["improvement_suggestions"]) for a in analyses)
    
    report = f"""
========================================
  小龙虾夜间进化报告
  时间: {now}
========================================

📊 本轮进化扫描
  搜索方向: 7 个
  发现项目: {len(analyses)} 个（新学习）
  跳过已学习: {skipped} 个
  高相关项目: {sum(1 for a in analyses if a['relevance_score'] >= 10)} 个
  生成改进项: {total_improvements} 个

🔥 高相关项目 Top 3:
"""
    
    sorted_analyses = sorted(analyses, key=lambda x: x["relevance_score"], reverse=True)
    for i, a in enumerate(sorted_analyses[:3]):
        report += f"  {i+1}. {a['name']} (⭐{a['stars']}, 相关度:{a['relevance_score']})\n"
        report += f"     {a['description'][:80]}\n"
        report += f"     创新点: {', '.join(a['key_innovations'][:3])}\n"
    
    report += f"""
📈 系统状态
  学习追踪: {TRACKING_FILE.exists()}
  进化日志: 共 {count_evolution_entries()} 条记录
  
💡 待确认改进项 (P0):
"""
    
    p0_items = []
    for a in analyses:
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

def count_evolution_entries() -> int:
    """统计进化日志条目数"""
    if not EVOLUTION_LOG.exists():
        return 0
    return sum(1 for _ in open(EVOLUTION_LOG, "r", encoding="utf-8"))

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

def main():
    """主进化流程"""
    log("========================================")
    log("小龙虾夜间进化引擎启动")
    log("========================================")
    
    # 加载已学习项目（跨轮去重）
    learned_projects = load_learned_projects()
    log(f"已学习项目数: {len(learned_projects)}，将跳过重复项目")
    
    all_analyses = []
    all_comparisons = []
    skipped_count = 0
    
    # Phase 1: 搜索与获取 - 随机选7个方向避免API限流
    log("Phase 1: GitHub搜索与项目获取")
    import random
    selected_queries = random.sample(SEARCH_QUERIES, min(7, len(SEARCH_QUERIES)))
    
    MIN_STARS = 50  # 最低星数过滤
    
    for query in selected_queries:
        repos = search_github_trending(query)
        for repo in repos:
            if repo.get("stargazersCount", 0) < MIN_STARS:
                continue  # 过滤低星项目
            
            repo_full_name = repo.get("fullName", repo.get("name", "")).lower()
            
            # 跨轮去重：跳过已学习项目
            if repo_full_name in learned_projects:
                skipped_count += 1
                log(f"跳过已学习: {repo_full_name}")
                continue
            
            analysis = analyze_project(repo)
            if analysis["relevance_score"] >= 5:
                all_analyses.append(analysis)
        time.sleep(3)  # API限流
    
    # 本轮内去重
    seen_names = set()
    unique_analyses = []
    for a in all_analyses:
        if a["name"].lower() not in seen_names:
            seen_names.add(a["name"].lower())
            unique_analyses.append(a)
    all_analyses = unique_analyses
    
    log(f"Phase 1 完成: {len(all_analyses)} 个新项目，跳过 {skipped_count} 个已学习项目")
    
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
    
    # Phase 5: 写入记忆
    log("Phase 5: 写入记忆文件")
    append_daily_memory(report)
    
    # Phase 6: 发送通知
    log("Phase 6: 发送进化通知")
    p0_count = sum(
        1 for a in all_analyses
        for imp in a.get("improvement_suggestions", [])
        if imp["priority"] == "P0"
    )
    
    subject = f"[小龙虾进化] {datetime.now().strftime('%m/%d %H:%M')} - 发现{len(all_analyses)}个项目, {p0_count}个P0改进"
    
    # 精简邮件正文
    email_body = report
    
    success = send_qq_email(subject, email_body)
    
    log("========================================")
    log(f"进化完成: {len(all_analyses)} 项目, {p0_count} P0改进")
    log(f"通知状态: {'已发送' if success else '未发送（需配置QQ邮箱）'}")
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
    sys.exit(0 if result["projects_found"] > 0 else 0)
