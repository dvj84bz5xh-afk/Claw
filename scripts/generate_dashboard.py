#!/usr/bin/env python3
"""生成进化仪表盘 HTML — 从 learning_tracking.json 读取最新数据"""
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRACKING = ROOT / ".workbuddy" / "learning_tracking.json"
OUTPUT = ROOT / "docs" / "evolution-dashboard.html"

with open(TRACKING, encoding="utf-8") as f:
    data = json.load(f)

projects = data["projects"]
improvements = data["improvements"]
p0 = [i for i in improvements if i.get("priority") == "P0"]
p1 = [i for i in improvements if i.get("priority") == "P1"]
done = [i for i in improvements if i.get("status") == "done"]
impl_rate = round(len(done) / max(len(improvements), 1) * 100)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# 最近10个项目（逆序）
recent_rows = ""
for p in reversed(projects[-10:]):
    name = p.get("name", "")
    stars = p.get("stars", 0)
    learned = (p.get("learned_at") or "")[:10]
    relevance = p.get("relevance_score", "-")
    url = p.get("url", "#")
    recent_rows += (
        f'<tr><td><a href="{url}" target="_blank">{name}</a></td>'
        f"<td>&#11088;{stars:,}</td><td>{relevance}</td><td>{learned}</td></tr>\n"
    )

# P0 前10条
p0_rows = ""
for i in p0[:10]:
    module = i.get("module", "")
    suggestion = i.get("suggestion", "")[:65]
    source = i.get("source", "")
    p0_rows += f"<tr><td>{module}</td><td>{suggestion}</td><td>{source}</td></tr>\n"

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>小龙虾进化仪表盘</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Microsoft YaHei',Arial,sans-serif;background:#0f1117;color:#e0e0e0;padding:20px}}
h1{{text-align:center;color:#00d4ff;margin-bottom:6px;font-size:1.6em}}
.subtitle{{text-align:center;color:#888;font-size:.85em;margin-bottom:24px}}
.stats{{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;margin-bottom:28px}}
.stat-card{{background:#1a1d2e;border-radius:10px;padding:18px 28px;text-align:center;border:1px solid #2a2d3e;min-width:130px}}
.stat-card .num{{font-size:2.2em;font-weight:700;color:#00d4ff}}
.orange .num{{color:#ff9900}}.green .num{{color:#00cc88}}.red .num{{color:#ff4466}}
.stat-card .label{{font-size:.8em;color:#888;margin-top:4px}}
.section{{background:#1a1d2e;border-radius:10px;padding:20px;margin-bottom:20px;border:1px solid #2a2d3e}}
.section h2{{color:#00d4ff;font-size:1.1em;margin-bottom:14px;border-bottom:1px solid #2a2d3e;padding-bottom:8px}}
table{{width:100%;border-collapse:collapse;font-size:.85em}}
th{{background:#0f1117;color:#888;padding:8px 10px;text-align:left;font-weight:500}}
td{{padding:7px 10px;border-bottom:1px solid #2a2d3e}}
tr:hover td{{background:#21253a}}
a{{color:#00aaff;text-decoration:none}}
a:hover{{text-decoration:underline}}
.progress-wrap{{background:#0f1117;border-radius:4px;height:10px;margin:12px 0}}
.progress-fill{{height:10px;border-radius:4px;background:linear-gradient(90deg,#00d4ff,#00cc88);width:{impl_rate}%}}
</style>
</head>
<body>
<h1>&#x1F99E; 小龙虾进化仪表盘</h1>
<div class="subtitle">最后更新: {now} &nbsp;|&nbsp; Claw AI 学习追踪系统</div>

<div class="stats">
  <div class="stat-card"><div class="num">{len(projects)}</div><div class="label">已学习项目</div></div>
  <div class="stat-card orange"><div class="num">{len(improvements)}</div><div class="label">改进项总数</div></div>
  <div class="stat-card red"><div class="num">{len(p0)}</div><div class="label">P0 紧急</div></div>
  <div class="stat-card"><div class="num">{len(p1)}</div><div class="label">P1 优化</div></div>
  <div class="stat-card green"><div class="num">{len(done)}</div><div class="label">已实施</div></div>
  <div class="stat-card"><div class="num">{impl_rate}%</div><div class="label">实施率</div></div>
</div>

<div class="section">
  <h2>&#x1F4C8; 实施进度</h2>
  <div style="color:#888;font-size:.85em">已实施 {len(done)} / {len(improvements)} 条改进项</div>
  <div class="progress-wrap"><div class="progress-fill"></div></div>
</div>

<div class="section">
  <h2>&#x1F4DA; 最近学习的项目（最新10个）</h2>
  <table>
    <tr><th>项目</th><th>Stars</th><th>相关度</th><th>学习日期</th></tr>
    {recent_rows}
  </table>
</div>

<div class="section">
  <h2>&#x1F534; P0 紧急改进项（前10条）</h2>
  <table>
    <tr><th>模块</th><th>建议</th><th>来源项目</th></tr>
    {p0_rows}
  </table>
</div>

</body>
</html>"""

OUTPUT.write_text(html, encoding="utf-8")
print(f"✅ 仪表盘已更新 -> {OUTPUT}")
