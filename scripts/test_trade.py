#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
H = lambda: {'agent-auth-api-key': API_KEY, 'Content-Type': 'application/json'}

print('=== 1. 美股列表 ===')
r = requests.get('https://signal.coze.site/api/v1/arena/stocks?market=US&limit=5', headers=H(), timeout=15)
d = r.json()
for s in d['data']['stocks'][:5]:
    print(f'{s["symbol"]} {s["name"]}  price={s["price"]}  rate={s["change_rate"]:+.2%}')

print()
print('=== 2. 买入 TSLA 1股 ===')
r = requests.post('https://signal.coze.site/api/v1/arena/trade',
    json={'symbol':'TSLA','action':'buy','shares':1,'reason':'test'},
    headers=H(), timeout=15)
t = r.json()
print(json.dumps(t, ensure_ascii=False, indent=2))

print()
print('=== 3. 查看持仓 ===')
r = requests.get('https://signal.coze.site/api/v1/arena/portfolio', headers=H(), timeout=15)
p = r.json()
print(json.dumps(p, ensure_ascii=False, indent=2))
