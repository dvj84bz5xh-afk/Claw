#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看虾评技能列表的实际结构，找到可下载的技能"""
import requests, json

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
H = lambda: {'Authorization': f'Bearer {API_KEY}'}

print('=== 虾评技能列表（前5个）===\n')
r = requests.get('https://xiaping.coze.site/api/skills?sort=downloads&limit=5', timeout=15)
d = r.json()
if d.get('success'):
    for sk in d['skills'][:5]:
        print(f'ID: {sk["id"]}')
        print(f'  名称: {sk["name"]}')
        print(f'  评分: {sk.get("avg_stars","-")}')
        print(f'  下载: {sk["downloads"]}')
        print(f'  字段: {list(sk.keys())}')
        print()
else:
    print('失败:', d)
