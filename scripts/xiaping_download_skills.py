#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虾评平台技能下载脚本 v2
- 移除 max_skills 字段引用
- 根据等级 A2-1 判断权限（可上传3个技能）
"""
import requests
import json
import os

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
BASE = 'https://xiaping.coze.site/api'

def H():
    return {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

print('=== 虾评平台技能下载 ===\n')

# 1. 获取我的信息
print('[1] 获取账号信息...')
r = requests.get(f'{BASE}/auth/me', headers=H(), timeout=15)
me = r.json()
if not me.get('success'):
    print('失败:', me)
    exit()
d = me['data']
print(f'  用户名：{d["name"]}')
print(f'  虾米余额：{d["coins"]}')
print(f'  等级：{d["level"]}')
print(f'  (A2-1 可上传 3 个技能)')

coins = d['coins']

# 2. 获取技能列表（按下载量排序）
print('\n[2] 获取热门技能列表...')
r = requests.get(f'{BASE}/skills?sort=downloads&limit=30', timeout=15)
data = r.json()
if not data.get('success'):
    print('失败:', data)
    exit()

skills = data['skills']
print(f'共 {data["total"]} 个技能')

# 3. 筛选可下载的（试用版优先）
downloadable = []
for sk in skills:
    if sk.get('has_trial'):
        downloadable.append((sk, '试用'))
    elif coins >= 2:  # 假设每个技能2虾米
        downloadable.append((sk, '购买'))

print(f'\n可下载技能数：{len(downloadable)}')
print('\n前10个可下载技能：')
for i, (sk, dtype) in enumerate(downloadable[:10]):
    print(f'  {i+1:2d}. [{dtype}] {sk["name"]}  评分={sk.get("avg_stars","-")}  下载={sk["downloads"]}')

# 4. 下载前3个试用技能
print('\n[3] 下载前3个试用技能...')
os.makedirs('downloads/skills', exist_ok=True)
downloaded = 0
for sk, dtype in downloadable[:3]:
    if dtype == '试用' or (dtype == '购买' and coins >= 2):
        print(f'  下载：{sk["name"]} ({dtype})')
        url = f'{BASE}/skills/{sk["id"]}/download'
        rr = requests.get(url, headers=H(), timeout=30)
        if rr.status_code == 200:
            fname = f'downloads/skills/{sk["name"]}.zip'
            with open(fname, 'wb') as f:
                f.write(rr.content)
            size_kb = len(rr.content) / 1024
            print(f'    ✅ 成功：{fname} ({size_kb:.1f} KB)')
            downloaded += 1
            if dtype == '购买':
                coins -= 2
        else:
            print(f'    ❌ 失败：{rr.json()}')
    else:
        print(f'  跳过：{sk["name"]} (虾米不足)')

print(f'\n本次下载：{downloaded} 个技能')
print(f'剩余虾米：{coins}')

# 5. 查看我的技能
print('\n[4] 查看我的技能...')
r = requests.get(f'{BASE}/me/skills', headers=H(), timeout=15)
mydata = r.json()
if mydata.get('success'):
    my_skills = mydata['data']['skills']
    print(f'  已上传技能数：{len(my_skills)}')
    for ms in my_skills:
        print(f'    {ms["name"]}  下载={ms["downloads"]}')

print('\n=== 完成 ===')
