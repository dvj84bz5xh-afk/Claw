#!/usr/bin/env python3
"""Generate Claw Evolution Dashboard HTML from learning_tracking.json"""
import json, datetime, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK = os.path.join(BASE, '.workbuddy', 'learning_tracking.json')
OUT = os.path.join(BASE, 'docs', 'evolution-dashboard.html')

with open(TRACK, 'r', encoding='utf-8') as f:
    data = json.load(f)

projects = data['projects']
improvements = data['improvements']

total_projects = len(projects)
total_improvements = len(improvements)
done_count = sum(1 for i in improvements if i['status'] == 'done')
pending_count = sum(1 for i in improvements if i['status'] == 'pending')

p0 = [i for i in improvements if i['priority'] == 'P0']
p0_done = sum(1 for i in p0 if i['status'] == 'done')
p0_pending = sum(1 for i in p0 if i['status'] == 'pending')
p1 = [i for i in improvements if i['priority'] == 'P1']
p1_done = sum(1 for i in p1 if i['status'] == 'done')
p1_pending = sum(1 for i in p1 if i['status'] == 'pending')
p2 = [i for i in improvements if i['priority'] == 'P2']
p2_done = sum(1 for i in p2 if i['status'] == 'done')
p2_pending = sum(1 for i in p2 if i['status'] == 'pending')

modules = {}
for i in improvements:
    m = i.get('module', 'unknown')
    modules[m] = modules.get(m, 0) + 1

recent = sorted(projects, key=lambda p: p.get('analyzed_at', ''), reverse=True)[:10]
top_rel = sorted(projects, key=lambda p: p.get('relevance', 0), reverse=True)[:10]

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

p0_pct = round(p0_done/len(p0)*100)
p1_pct = round(p1_done/len(p1)*100)
p2_pct = round(p2_done/len(p2)*100) if len(p2) > 0 else 0
total_pct = round(done_count/total_improvements*100)
total_pct_f = round(done_count/total_improvements*100, 1)

latest = recent[0] if recent else {}

def row(p):
    return f'<tr><td>{p["name"]}</td><td>{p.get("stars",0)}</td><td><b>{p.get("relevance",0)}</b></td><td>{p.get("language","N/A")[:15]}</td><td>{p.get("analyzed_at","N/A")[:10]}</td></tr>\n'

def imp_row(i):
    return f'<tr><td>{i["id"][:12]}</td><td>{i["source"][:20]}</td><td>{i.get("module","N/A")[:15]}</td><td>{i["suggestion"][:50]}</td><td><span class="tag tag-pending">pending</span></td></tr>\n'

p0_pending_items = sorted([i for i in improvements if i['priority']=='P0' and i['status']=='pending'],
                          key=lambda x: x.get('created_at',''), reverse=True)[:10]

module_json = json.dumps(list(modules.items()))
trend_json = json.dumps([{'name': p['name'][:20], 'relevance': p.get('relevance',0)} for p in recent[:10]])

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claw Evolution Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
h1 {{ text-align: center; color: #58a6ff; margin-bottom: 10px; font-size: 24px; }}
.subtitle {{ text-align: center; color: #8b949e; margin-bottom: 30px; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }}
.card-title {{ color: #58a6ff; font-size: 16px; margin-bottom: 12px; }}
.stat {{ font-size: 28px; font-weight: bold; color: #f0f6fc; }}
.stat-label {{ font-size: 12px; color: #8b949e; }}
.progress-bar {{ background: #21262d; border-radius: 4px; height: 8px; margin-top: 8px; }}
.progress-fill {{ border-radius: 4px; height: 8px; }}
.p0-fill {{ background: #f85149; }}
.p1-fill {{ background: #d29922; }}
.p2-fill {{ background: #3fb950; }}
.total-fill {{ background: #58a6ff; }}
.chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
.chart-container {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: #21262d; color: #58a6ff; padding: 10px; text-align: left; font-size: 13px; }}
td {{ padding: 10px; border-bottom: 1px solid #30363d; font-size: 13px; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; }}
.tag-pending {{ background: #30363d; color: #8b949e; }}
.highlight {{ background: #161b22; border: 1px solid #58a6ff; border-radius: 8px; padding: 16px; margin-bottom: 24px; }}
.highlight-title {{ color: #58a6ff; font-size: 18px; margin-bottom: 8px; }}
.highlight-desc {{ color: #c9d1d9; font-size: 14px; line-height: 1.6; }}
</style>
</head>
<body>
<div class="container">
<h1>Claw Evolution Dashboard</h1>
<p class="subtitle">智能进化学习系统 - 第30轮更新 | {now}</p>
<div class="highlight">
<div class="highlight-title">本轮学习: {latest.get('name','N/A')} ({latest.get('stars',0)}K stars, 相关度{latest.get('relevance',0)})</div>
<div class="highlight-desc">A2A Agent-to-Agent开放协议 - 传输无关设计 + AgentCard能力发现 + Task生命周期 + 不透明性原则 + A2A/MCP互补。新增5项改进(P0x2, P1x2, P2x1)</div>
</div>
<div class="grid">
<div class="card"><div class="card-title">项目总数</div><div class="stat">{total_projects}</div><div class="stat-label">已分析的GitHub项目</div></div>
<div class="card"><div class="card-title">改进项总数</div><div class="stat">{total_improvements}</div><div class="stat-label">{done_count} 已实施 / {pending_count} 待实施</div><div class="progress-bar"><div class="progress-fill total-fill" style="width:{total_pct}%"></div></div></div>
<div class="card"><div class="card-title">总实施率</div><div class="stat">{total_pct_f}%</div><div class="stat-label">{done_count}/{total_improvements} 已完成</div></div>
</div>
<div class="grid">
<div class="card"><div class="card-title">P0 (紧急)</div><div class="stat">{p0_done}/{len(p0)}</div><div class="stat-label">{p0_pending} 项待实施</div><div class="progress-bar"><div class="progress-fill p0-fill" style="width:{p0_pct}%"></div></div></div>
<div class="card"><div class="card-title">P1 (重要)</div><div class="stat">{p1_done}/{len(p1)}</div><div class="stat-label">{p1_pending} 项待实施</div><div class="progress-bar"><div class="progress-fill p1-fill" style="width:{p1_pct}%"></div></div></div>
<div class="card"><div class="card-title">P2 (优化)</div><div class="stat">{p2_done}/{len(p2)}</div><div class="stat-label">{p2_pending} 项待实施</div><div class="progress-bar"><div class="progress-fill p2-fill" style="width:{p2_pct}%"></div></div></div>
</div>
<div class="chart-row">
<div class="chart-container"><div class="card-title">模块分布</div><canvas id="moduleChart" height="300"></canvas></div>
<div class="chart-container"><div class="card-title">相关度趋势</div><canvas id="trendChart" height="300"></canvas></div>
</div>
<div class="card"><div class="card-title">最高相关度项目 (Top 10)</div><table><tr><th>项目</th><th>星数</th><th>相关度</th><th>语言</th><th>分析日期</th></tr>{"".join(row(p) for p in top_rel)}</table></div>
<div class="card"><div class="card-title">最近学习项目</div><table><tr><th>项目</th><th>星数</th><th>相关度</th><th>改进项</th><th>日期</th></tr>{"".join(f'<tr><td>{p["name"]}</td><td>{p.get("stars",0)}</td><td>{p.get("relevance",0)}</td><td>{p.get("improvements_count",0)}</td><td>{p.get("analyzed_at","N/A")[:10]}</td></tr>' for p in recent)}</table></div>
<div class="card"><div class="card-title">P0 待实施改进项</div><table><tr><th>ID</th><th>来源</th><th>模块</th><th>建议</th><th>状态</th></tr>{"".join(imp_row(i) for i in p0_pending_items)}</table></div>
</div>
<script>
const md={module_json}; const tp={trend_json};
new Chart(document.getElementById('moduleChart'),{{type:'doughnut',data:{{labels:md.map(d=>d[0]),datasets:[{{data:md.map(d=>d[1]),backgroundColor:['#f85149','#d29922','#3fb950','#58a6ff','#bc8cff','#ff7b72','#79c0ff','#d2a8ff','#a5d6ff','#ffd33d']}}]}},options:{{responsive:true,plugins:{{legend:{{position:'right',labels:{{color:'#c9d1d9'}}}}}}}}}});
new Chart(document.getElementById('trendChart'),{{type:'bar',data:{{labels:tp.map(p=>p.name),datasets:[{{label:'相关度',data:tp.map(p=>p.relevance),backgroundColor:'#58a6ff'}}]}},options:{{responsive:true,scales:{{y:{{beginAtZero:true,grid:{{color:'#30363d'}},ticks:{{color:'#c9d1d9'}}}},x:{{ticks:{{color:'#c9d1d9',font:{{size:10}}}}}}}},plugins:{{legend:{{labels:{{color:'#c9d1d9'}}}}}}}}}});
</script>
</body></html>"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Dashboard generated: {total_projects} projects, {total_improvements} improvements, {done_count} done ({total_pct_f}%)')
