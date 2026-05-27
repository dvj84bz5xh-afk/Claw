#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Signal Arena 交易 + 虾评技能下载 一键执行"""
import requests, json, os, sys

# ==================== Signal Arena ====================
API_SA = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
H_SA = lambda: {'agent-auth-api-key': API_SA, 'Content-Type': 'application/json'}
BASE_SA = 'https://signal.coze.site/api/v1'

print('=== Signal Arena 虚拟炒股 ===\n')

# 1. 买入 Apple 1股
print('[1] 买入 Apple (gb_aapl) 1股...')
r = requests.post(f'{BASE_SA}/arena/trade',
    json={'symbol':'gb_aapl','action':'buy','shares':1,'reason':'auto test'},
    headers=H_SA(), timeout=15)
t = r.json()
print(json.dumps(t, ensure_ascii=False, indent=2))

# 2. 查看持仓
print('\n[2] 查看持仓...')
r = requests.get(f'{BASE_SA}/arena/portfolio', headers=H_SA(), timeout=15)
p = r.json()
print(json.dumps(p, ensure_ascii=False, indent=2))

# 3. 查看排行榜前5
print('\n[3] 排行榜 Top5...')
r = requests.get(f'{BASE_SA}/arena/leaderboard?limit=5', headers=H_SA(), timeout=15)
lb = r.json()
print(json.dumps(lb, ensure_ascii=False, indent=2))

# ==================== 虾评平台 ====================
print('\n' + '='*50)
print('=== 虾评平台 技能下载 ===\n')

API_XP = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
H_XP = lambda: {'Authorization': f'Bearer {API_XP}', 'Content-Type': 'application/json'}
BASE_XP = 'https://xiaping.coze.site/api'

# 1. 获取账号信息
print('[1] 账号信息...')
r = requests.get(f'{BASE_XP}/auth/me', headers=H_XP(), timeout=15)
me = r.json()
if me.get('success'):
    d = me['data']
    print(f'  用户名: {d["name"]}')
    print(f'  虾米: {d["coins"]}')
    print(f'  等级: {d["level"]}')
    coins = d['coins']
else:
    print('  失败:', me)
    coins = 0

# 2. 获取热门技能（有试用版的）
print('\n[2] 查找试用技能...')
r = requests.get(f'{BASE_XP}/skills?sort=downloads&limit=30', timeout=15)
data = r.json()
trial_skills = []
if data.get('success'):
    for sk in data['skills']:
        if sk.get('has_trial'):
            trial_skills.append(sk)
        if len(trial_skills) >= 5:
            break
    print(f'  找到 {len(trial_skills)} 个试用技能:')
    for sk in trial_skills:
        print(f'    - {sk["name"]} (评分:{sk.get("avg_stars","-")})')

# 3. 下载试用技能
os.makedirs('downloads/skills', exist_ok=True)
print(f'\n[3] 下载 {len(trial_skills)} 个试用技能...')
downloaded = 0
for sk in trial_skills:
    url = f'{BASE_XP}/skills/{sk["id"]}/download'
    rr = requests.get(url, headers=H_XP(), timeout=30)
    if rr.status_code == 200:
        fpath = f'downloads/skills/{sk["name"]}.zip'
        with open(fpath, 'wb') as f:
            f.write(rr.content)
        print(f'  ✅ {sk["name"]} ({len(rr.content)//1024}KB)')
        downloaded += 1
    else:
        print(f'  ❌ {sk["name"]}: {rr.json().get("message","")}')

print(f'\n下载完成: {downloaded} 个技能')
print(f'剩余虾米: {coins}')
print('\n=== 全部完成 ===')
