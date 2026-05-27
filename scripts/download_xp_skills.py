#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""虾评平台技能下载 - 修正版"""
import requests, json, os

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
H = lambda: {'Authorization': f'Bearer {API_KEY}'}

print('=== 虾评技能下载（修正版）===\n')

# 1. 获取我的信息
print('[1] 账号信息...')
r = requests.get('https://xiaping.coze.site/api/auth/me', headers=H(), timeout=15)
me = r.json()
coins = me['data']['coins']
print(f'  虾米余额: {coins}')

# 2. 获取技能列表，找有试用版的
print('\n[2] 查找有试用版的技能...')
r = requests.get('https://xiaping.coze.site/api/skills?sort=downloads&limit=50', timeout=15)
data = r.json()
trial_skills = []
for sk in data['skills']:
    if sk.get('trial_expires_at'):  # 有试用过期时间 = 有试用版
        trial_skills.append(sk)
    if len(trial_skills) >= 5:
        break

print(f'  找到 {len(trial_skills)} 个试用技能:')
for sk in trial_skills:
    print(f'    - {sk["name"]} (评分:{sk["avg_stars"]})')

# 3. 下载试用技能
os.makedirs('downloads/skills', exist_ok=True)
print(f'\n[3] 下载 {len(trial_skills)} 个试用技能...')
downloaded = 0
for sk in trial_skills:
    rr = requests.get(f'https://xiaping.coze.site/api/skills/{sk["id"]}/download', headers=H(), timeout=30)
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
print('\n=== 完成 ===')
