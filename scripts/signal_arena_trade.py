#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena 虚拟炒股脚本 v2
- 修复字段名：price / change_rate
- 优先交易美股（当前时段可交易）
"""
import requests
import json

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
BASE = 'https://signal.coze.site/api/v1'

def H():
    return {'agent-auth-api-key': API_KEY, 'Content-Type': 'application/json'}

print('=== Signal Arena 虚拟炒股 ===\n')

# 1. 获取美股列表
print('[1] 获取美股列表...')
r = requests.get(f'{BASE}/arena/stocks?market=US&limit=10', headers=H(), timeout=15)
d = r.json()
if not d.get('success'):
    print('失败:', d)
    exit()
us = d['data']['stocks']
print(f'美股共 {d["data"]["total"]} 只，显示前10只：')
for i, s in enumerate(us):
    print(f'  {i+1:2d}. {s["symbol"]:6s} {s["name"]:20s}  现价={s["price"]:.2f}  涨跌={s["change_rate"]:+.2%}')

# 2. 选择一只买入（选涨跌幅适中的）
target = us[2]  # 第3只，通常是科技股
print(f'\n[2] 准备买入：{target["name"]} ({target["symbol"]})')
print(f'    现价：{target["price"]:.2f}')
print(f'    涨跌：{target["change_rate"]:+.2%}')

# 3. 查看可用资金
print('\n[3] 查看账户资金...')
r = requests.get(f'{BASE}/arena/portfolio', headers=H(), timeout=15)
pdata = r.json()
if not pdata.get('success'):
    print('失败:', pdata)
    exit()
cash = pdata['data']['portfolio']['cash']
print(f'    可用现金：{cash:,.0f}')

# 4. 计算买入数量（用5%资金）
max_shares = int(cash * 0.05 / target["price"])
print(f'    计划买入：{max_shares} 股 (5% 资金)')

if max_shares < 1:
    print('    资金不足，无法买入')
    exit()

# 5. 提交买入订单
print(f'\n[4] 提交买入订单...')
order = {
    'symbol': target['symbol'],
    'action': 'buy',
    'shares': max_shares,
    'reason': '自动买入测试 - 美股'
}
r = requests.post(f'{BASE}/arena/trade', json=order, headers=H(), timeout=15)
tdata = r.json()
print(json.dumps(tdata, ensure_ascii=False, indent=2))

# 6. 查看持仓
print('\n[5] 查看持仓...')
r = requests.get(f'{BASE}/arena/portfolio', headers=H(), timeout=15)
pdata = r.json()
if pdata.get('success'):
    p = pdata['data']['portfolio']
    print(f'  现金：{p["cash"]:,.2f}')
    print(f'  持仓市值：{p["positions_value"]:,.2f}')
    print(f'  总资产：{p["total_value"]:,.2f}')
    print(f'  收益率：{p["return_rate"]:+.2f}%')
    if p.get('positions'):
        print('  持仓明细：')
        for pos in p['positions']:
            print(f'    {pos["symbol"]} {pos["name"]} {pos["shares"]}股  成本={pos["cost_basis"]:.2f}  现价={pos["current_price"]:.2f}  盈亏={pos["pnl"]:+.2f} ({pos["pnl_pct"]:+.2f}%)')

print('\n=== 完成 ===')
