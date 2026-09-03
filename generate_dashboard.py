import json, datetime

with open('.workbuddy/learning_tracking.json', 'r', encoding='utf-8') as f:
    tracking = json.load(f)

projects = tracking['projects']
improvements = tracking['improvements']

total_projects = len(projects)
total_improvements = len(improvements)
done_count = sum(1 for i in improvements if i.get('status') == 'done')
impl_rate = done_count / total_improvements * 100 if total_improvements > 0 else 0

p0_total = sum(1 for i in improvements if i.get('priority') == 'P0')
p0_done = sum(1 for i in improvements if i.get('priority') == 'P0' and i.get('status') == 'done')
p0_pending = p0_total - p0_done
p1_total = sum(1 for i in improvements if i.get('priority') == 'P1')
p1_done = sum(1 for i in improvements if i.get('priority') == 'P1' and i.get('status') == 'done')
p2_total = sum(1 for i in improvements if i.get('priority') == 'P2')
p2_done = sum(1 for i in improvements if i.get('priority') == 'P2' and i.get('status') == 'done')

modules = {}
for imp in improvements:
    m = imp.get('module', 'other')
    if m not in modules:
        modules[m] = {'total': 0, 'done': 0}
    modules[m]['total'] += 1
    if imp.get('status') == 'done':
        modules[m]['done'] += 1

recent = sorted(projects, key=lambda p: p.get('analyzed_at', ''), reverse=True)[:10]

langs = {}
for p in projects:
    lang = p.get('language', 'N/A')
    langs[lang] = langs.get(lang, 0) + 1

p0_rate = f"{p0_done/p0_total*100:.1f}%" if p0_total > 0 else "0%"
p1_rate = f"{p1_done/p1_total*100:.1f}%" if p1_total > 0 else "0%"
p2_rate = f"{p2_done/p2_total*100:.1f}%" if p2_total > 0 else "0%"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claw 智能进化仪表盘</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e4e6eb; min-height: 100vh; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; background: linear-gradient(135deg, #4fc3f7, #ab47bc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.subtitle {{ color: #8b9099; font-size: 14px; margin-bottom: 24px; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
.stat-card {{ background: #1a1d28; border: 1px solid #2a2d3a; border-radius: 12px; padding: 20px; transition: transform 0.2s; }}
.stat-card:hover {{ transform: translateY(-2px); border-color: #4fc3f7; }}
.stat-label {{ font-size: 13px; color: #8b9099; margin-bottom: 8px; }}
.stat-value {{ font-size: 32px; font-weight: 700; }}
.stat-value.green {{ color: #4caf50; }}
.stat-value.blue {{ color: #4fc3f7; }}
.stat-value.red {{ color: #f44336; }}
.stat-value.purple {{ color: #ab47bc; }}
.stat-sub {{ font-size: 12px; color: #8b9099; margin-top: 4px; }}
.section {{ margin-bottom: 32px; }}
.section-title {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #2a2d3a; }}
.priority-bar {{ display: flex; gap: 4px; height: 24px; border-radius: 6px; overflow: hidden; margin-bottom: 8px; }}
.priority-bar div {{ display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; }}
.bar-p0 {{ background: #f44336; }}
.bar-p1 {{ background: #ff9800; }}
.bar-p2 {{ background: #4caf50; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #2a2d3a; font-size: 13px; }}
th {{ color: #8b9099; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
tr:hover {{ background: #1a1d28; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
.badge-p0 {{ background: rgba(244,67,54,0.15); color: #f44336; }}
.badge-p1 {{ background: rgba(255,152,0,0.15); color: #ff9800; }}
.lang-bar {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.lang-tag {{ background: #1a1d28; border: 1px solid #2a2d3a; padding: 4px 12px; border-radius: 16px; font-size: 12px; }}
.lang-tag span {{ color: #4fc3f7; font-weight: 600; }}
.module-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
.module-name {{ width: 180px; font-size: 13px; }}
.module-bar {{ flex: 1; height: 20px; background: #1a1d28; border-radius: 4px; overflow: hidden; }}
.module-fill {{ height: 100%; background: linear-gradient(90deg, #4fc3f7, #ab47bc); transition: width 0.5s; }}
.module-stats {{ width: 80px; text-align: right; font-size: 12px; color: #8b9099; }}
.update-time {{ text-align: center; color: #8b9099; font-size: 12px; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
<h1>Claw 智能进化仪表盘</h1>
<p class="subtitle">通过 GitHub 高星项目迭代 CodeBuddy 能力 | 细水长流模式 | 每日1项目</p>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">学习项目总数</div><div class="stat-value blue">{total_projects}</div><div class="stat-sub">累计分析GitHub项目</div></div>
<div class="stat-card"><div class="stat-label">改进项总数</div><div class="stat-value purple">{total_improvements}</div><div class="stat-sub">已识别可借鉴改进点</div></div>
<div class="stat-card"><div class="stat-label">已实施</div><div class="stat-value green">{done_count}</div><div class="stat-sub">实施率 {impl_rate:.1f}%</div></div>
<div class="stat-card"><div class="stat-label">P0 待实施</div><div class="stat-value red">{p0_pending}</div><div class="stat-sub">高优先级待处理</div></div>
</div>

<div class="section">
<div class="section-title">优先级分布</div>
<div class="priority-bar">
<div class="bar-p0" style="flex:{p0_total}">P0: {p0_total}</div>
<div class="bar-p1" style="flex:{p1_total}">P1: {p1_total}</div>
<div class="bar-p2" style="flex:{p2_total}">P2: {p2_total}</div>
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:12px;">
<div class="stat-card" style="text-align:center;padding:12px;"><div class="stat-label">P0 (高优先级)</div><div style="font-size:20px;font-weight:600;color:#f44336;">{p0_done}/{p0_total}</div><div class="stat-sub">实施率 {p0_rate}</div></div>
<div class="stat-card" style="text-align:center;padding:12px;"><div class="stat-label">P1 (中优先级)</div><div style="font-size:20px;font-weight:600;color:#ff9800;">{p1_done}/{p1_total}</div><div class="stat-sub">实施率 {p1_rate}</div></div>
<div class="stat-card" style="text-align:center;padding:12px;"><div class="stat-label">P2 (低优先级)</div><div style="font-size:20px;font-weight:600;color:#4caf50;">{p2_done}/{p2_total}</div><div class="stat-sub">实施率 {p2_rate}</div></div>
</div>
</div>

<div class="section">
<div class="section-title">模块改进分布</div>
"""

for mod_name in sorted(modules.keys(), key=lambda m: modules[m]['total'], reverse=True):
    m = modules[mod_name]
    pct = m['done'] / m['total'] * 100 if m['total'] > 0 else 0
    html += f"""<div class="module-row">
<div class="module-name">{mod_name}</div>
<div class="module-bar"><div class="module-fill" style="width:{pct:.0f}%"></div></div>
<div class="module-stats">{m['done']}/{m['total']}</div>
</div>
"""

html += """</div>

<div class="section">
<div class="section-title">最近学习项目 (Top 10)</div>
<table>
<thead><tr><th>项目</th><th>Stars</th><th>相关度</th><th>语言</th><th>日期</th><th>改进项</th><th>P0</th><th>P1</th></tr></thead>
<tbody>
"""

for p in recent:
    name = p['name']
    stars = p.get('stars', 0)
    rel = p.get('relevance', 0)
    lang = p.get('language', 'N/A')
    date = p.get('analyzed_at', '')[:10]
    imp_count = p.get('improvements_count', 0)
    pb = p.get('priority_breakdown', {})
    p0 = pb.get('P0', 0)
    p1 = pb.get('P1', 0)
    url = p.get('url', '')
    html += f"""<tr>
<td><a href="{url}" target="_blank" style="color:#4fc3f7;text-decoration:none;">{name}</a></td>
<td>&#11088;{stars:,}</td>
<td>{rel}</td>
<td>{lang}</td>
<td>{date}</td>
<td>{imp_count}</td>
<td><span class="badge badge-p0">{p0}</span></td>
<td><span class="badge badge-p1">{p1}</span></td>
</tr>
"""

html += """</tbody>
</table>
</div>

<div class="section">
<div class="section-title">语言分布</div>
<div class="lang-bar">
"""

for lang, count in sorted(langs.items(), key=lambda x: x[1], reverse=True):
    html += f'<div class="lang-tag">{lang} <span>{count}</span></div>'

html += """</div>
</div>

<div class="section">
"""

# 动态"最新学习"区块: 取最近学习的项目
if recent:
    latest = recent[0]
    lname = latest['name']
    ldate = latest.get('analyzed_at', '')[:10]
    lurl = latest.get('url', '#')
    lstars = latest.get('stars', 0)
    lrel = latest.get('relevance', 0)
    innovs = latest.get('key_innovations', [])
    html += f'<div class="section-title">最新学习: <a href="{lurl}" target="_blank" style="color:#4fc3f7;text-decoration:none;">{lname}</a> ({ldate} | &#11088;{lstars:,} | 相关度{lrel})</div>\n'
    html += '<div class="stat-card" style="padding:16px;">\n<div style="font-size:14px;line-height:1.8;">\n<strong>核心创新:</strong><br>\n'
    if innovs:
        for j, inv in enumerate(innovs, 1):
            html += f'{j}. {inv}<br>\n'
    else:
        html += '（无详细记录）<br>\n'
    html += '</div>\n</div>\n</div>\n'

now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
html += f'<div class="update-time">最后更新: {now_str} | 自动化ID: automation-1779863408739 | 细水长流模式</div>\n'
html += """</div>
</body>
</html>"""

with open('docs/evolution-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard generated: docs/evolution-dashboard.html")
print(f"Stats: {total_projects} projects, {total_improvements} improvements, {done_count} done ({impl_rate:.1f}%), {p0_pending} P0 pending")
