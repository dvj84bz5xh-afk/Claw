import json

with open('.workbuddy/learning_tracking.json', 'r', encoding='utf-8') as f:
    tracking = json.load(f)

projects = tracking['projects']
improvements = tracking['improvements']

total_projects = len(projects)
total_improvements = len(improvements)
done = sum(1 for i in improvements if i.get('status') == 'done')
pending = total_improvements - done
p0_pending = sum(1 for i in improvements if i.get('status') == 'pending' and i.get('priority') == 'P0')
p1_pending = sum(1 for i in improvements if i.get('status') == 'pending' and i.get('priority') == 'P1')
p2_pending = sum(1 for i in improvements if i.get('status') == 'pending' and i.get('priority') == 'P2')
rate = done / total_improvements * 100 if total_improvements > 0 else 0

modules = {}
for i in improvements:
    m = i.get('module', 'unknown')
    if m not in modules:
        modules[m] = {'total': 0, 'done': 0, 'pending': 0}
    modules[m]['total'] += 1
    if i.get('status') == 'done':
        modules[m]['done'] += 1
    else:
        modules[m]['pending'] += 1

recent = sorted(projects, key=lambda p: p.get('analyzed_at', ''), reverse=True)[:15]

module_rows = ""
for m in sorted(modules.keys(), key=lambda x: modules[x]['total'], reverse=True):
    d = modules[m]
    r = d['done']/d['total']*100 if d['total'] > 0 else 0
    module_rows += f"<tr><td>{m}</td><td>{d['total']}</td><td style='color:#34d399'>{d['done']}</td><td style='color:#60a5fa'>{d['pending']}</td><td>{r:.0f}%</td></tr>"

recent_rows = ""
for i, p in enumerate(recent, 1):
    stars = p.get('stars', 0)
    rel = p.get('relevance', 0)
    lang = p.get('language', 'N/A')
    date = p.get('analyzed_at', '')[:10]
    imp = p.get('improvements_count', 0)
    name = p['name']
    if len(name) > 35:
        name = name[:32] + '...'
    recent_rows += f"<tr><td>{i}</td><td>{name}</td><td>{stars:,}</td><td>{rel}</td><td>{lang}</td><td>{date}</td><td>{imp}</td></tr>"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claw 智能进化仪表盘</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
.header {{ text-align: center; margin-bottom: 32px; }}
.header h1 {{ font-size: 28px; color: #818cf8; margin-bottom: 8px; }}
.header .subtitle {{ color: #94a3b8; font-size: 14px; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
.stat-card {{ background: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155; text-align: center; }}
.stat-card .value {{ font-size: 36px; font-weight: 700; }}
.stat-card .label {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
.stat-card.p0 .value {{ color: #f87171; }}
.stat-card.p1 .value {{ color: #fbbf24; }}
.stat-card.blue .value {{ color: #60a5fa; }}
.stat-card.purple .value {{ color: #a78bfa; }}
.section {{ margin-bottom: 32px; }}
.section h2 {{ color: #818cf8; font-size: 20px; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
th {{ background: #334155; padding: 12px 16px; text-align: left; font-size: 13px; color: #cbd5e1; }}
td {{ padding: 10px 16px; border-bottom: 1px solid #334155; font-size: 13px; }}
tr:hover {{ background: #2d3a4e; }}
.progress-bar {{ height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
.progress-fill {{ height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 4px; }}
.protocol-stack {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }}
.protocol-card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; text-align: center; }}
.protocol-card .icon {{ font-size: 32px; margin-bottom: 8px; }}
.protocol-card .name {{ color: #818cf8; font-weight: 600; margin-bottom: 4px; }}
.protocol-card .desc {{ color: #94a3b8; font-size: 12px; }}
.footer {{ text-align: center; color: #475569; font-size: 12px; margin-top: 32px; }}
</style>
</head>
<body>
<div class="header">
<h1>Claw 智能进化仪表盘</h1>
<div class="subtitle">自动学习 GitHub 高星 AI/Agent 项目 | 最后更新: 2026-07-24 08:50</div>
</div>

<div class="stats-grid">
<div class="stat-card purple"><div class="value">{total_projects}</div><div class="label">学习项目总数</div></div>
<div class="stat-card blue"><div class="value">{total_improvements}</div><div class="label">改进项总数</div></div>
<div class="stat-card" style="border-color:#064e3b"><div class="value" style="color:#34d399">{done}</div><div class="label">已实施</div></div>
<div class="stat-card" style="border-color:#1e3a5f"><div class="value" style="color:#60a5fa">{pending}</div><div class="label">待实施</div></div>
<div class="stat-card p0"><div class="value">{p0_pending}</div><div class="label">P0 待实施</div></div>
<div class="stat-card p1"><div class="value">{p1_pending}</div><div class="label">P1 待实施</div></div>
</div>

<div class="stat-card" style="margin-bottom:32px">
<div style="display:flex;justify-content:space-between;align-items:center">
<span style="color:#94a3b8;font-size:14px">实施率</span>
<span style="font-size:24px;font-weight:700;color:#818cf8">{rate:.1f}%</span>
</div>
<div class="progress-bar"><div class="progress-fill" style="width:{rate:.1f}%"></div></div>
</div>

<div class="section">
<h2>协议栈三角 (今日新增: AG-UI)</h2>
<div class="protocol-stack">
<div class="protocol-card">
<div class="icon">🔧</div>
<div class="name">MCP</div>
<div class="desc">Agent → Tools<br>工具标准化协议<br>✅ 已学习</div>
</div>
<div class="protocol-card">
<div class="icon">🤝</div>
<div class="name">A2A</div>
<div class="desc">Agent ↔ Agent<br>跨Agent通信协议<br>✅ 已学习</div>
</div>
<div class="protocol-card" style="border-color:#6366f1">
<div class="icon">🖥️</div>
<div class="name">AG-UI</div>
<div class="desc">Agent → UI<br>用户交互协议<br>🆕 今日新增</div>
</div>
</div>
</div>

<div class="section">
<h2>模块改进分布</h2>
<table>
<thead><tr><th>模块</th><th>总计</th><th>已实施</th><th>待实施</th><th>实施率</th></tr></thead>
<tbody>
{module_rows}
</tbody></table>
</div>

<div class="section">
<h2>最近学习项目 (Top 15)</h2>
<table>
<thead><tr><th>#</th><th>项目</th><th>Stars</th><th>相关度</th><th>语言</th><th>日期</th><th>改进数</th></tr></thead>
<tbody>
{recent_rows}
</tbody></table>
</div>

<div class="section">
<h2>今日学习详情: CopilotKit/CopilotKit</h2>
<div class="stat-card" style="text-align:left;padding:20px">
<p style="color:#818cf8;font-size:16px;font-weight:600;margin-bottom:12px">CopilotKit/CopilotKit (⭐ 36,237 | TypeScript | 相关度 32)</p>
<p style="color:#cbd5e1;font-size:13px;line-height:1.8">
<b>核心创新:</b><br>
1. AG-UI Protocol — Agent→UI标准化事件协议(~16种事件类型), 补全MCP+A2A+AG-UI协议三角<br>
2. Generative UI三层架构 — Static/Declarative/Open-Ended三模式<br>
3. Shared State双向状态同步 — Agent与UI共享实时读写<br>
4. CLHF自学习引擎 — 人类反馈→prompt增强, 无需微调<br>
5. 多平台统一部署 — Web/Mobile/Slack/Teams同一Agent<br>
6. useAgent Hook — 编程级Agent状态操控
</p>
<p style="color:#f87171;font-size:13px;margin-top:12px"><b>P0改进:</b> AG-UI Protocol适配器 + Shared State双向状态同步</p>
</div>
</div>

<div class="footer">
Claw Intelligent Evolution System v2.1.0 | Automation ID: automation-1779863408739 | 2026-07-24
</div>
</body>
</html>"""

with open('docs/evolution-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard generated: {len(html)} chars")
print(f"Stats: {total_projects} projects, {total_improvements} improvements, {done} done, {rate:.1f}% rate")
