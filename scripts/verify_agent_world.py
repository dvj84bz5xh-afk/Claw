#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent World 集成功能验证脚本
验证三个站点的连接和功能
"""

import requests
import json
import sys

# 强制 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'

print('=' * 70)
print('Agent World 集成功能验证 - 2026-05-01 23:39')
print('=' * 70)
print()

# ===== 1. Signal Arena 验证 =====
print('【1/3】Signal Arena（策场）- 虚拟炒股平台')
print('-' * 70)
headers1 = {'agent-auth-api-key': API_KEY, 'Content-Type': 'application/json'}

# 检查我的状态
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/me', headers=headers1, timeout=15)
    data = r.json()
    if data.get('success'):
        me_data = data.get('data', {})
        print(f'  [连接] ✅ API连接正常')
        print(f'  [用户] {me_data.get("agent_name", "Unknown")}')
        print(f'  [现金] ${me_data.get("cash", 0):,.2f}')
        print(f'  [总资产] ${me_data.get("total_value", 0):,.2f}')
        print(f'  [收益率] {me_data.get("return_rate", 0)*100:.2f}%')
    else:
        print(f'  [连接] ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  [连接] ❌ 异常: {e}')
print()

# 检查持仓
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/portfolio', headers=headers1, timeout=15)
    data = r.json()
    if data.get('success'):
        portfolio = data.get('data', {}).get('portfolio', {})
        cash = portfolio.get('cash', 0)
        positions = portfolio.get('positions', [])
        print(f'  [持仓] 可用资金: ${cash:,.2f}')
        print(f'  [持仓] 持仓数量: {len(positions)}')
        if positions:
            for p in positions:
                symbol = p.get('symbol', 'N/A')
                qty = p.get('quantity', 0)
                cost = p.get('avg_cost', 0)
                print(f'         - {symbol}: {qty}股 @ ${cost:.2f}')
        else:
            print('         (暂无可持仓)')
    else:
        print(f'  [持仓] ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  [持仓] ❌ 异常: {e}')
print()

# 检查交易记录
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/trades?limit=5', headers=headers1, timeout=15)
    data = r.json()
    if data.get('success'):
        trades = data.get('data', {}).get('trades', [])
        print(f'  [交易] 历史交易: {len(trades)} 笔')
        for t in trades[:3]:
            symbol = t.get('symbol', 'N/A')
            side = t.get('side', 'N/A')
            qty = t.get('quantity', 0)
            price = t.get('price', 0)
            status = t.get('status', 'N/A')
            print(f'         - {symbol} {side} {qty}股 @ ${price:.2f} [{status}]')
    else:
        print(f'  [交易] ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  [交易] ❌ 异常: {e}')
print()
print('=' * 70)
print()

# ===== 2. 虾评 Skill 验证 =====
print('【2/3】虾评 Skill - 技能交易平台')
print('-' * 70)
headers2 = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 检查登录状态
try:
    r = requests.get('https://xiaping.coze.site/api/auth/me', headers=headers2, timeout=15)
    data = r.json()
    if data.get('success') or 'user' in data:
        user_data = data.get('data', {}).get('user', data.get('user', {}))
        print(f'  [登录] ✅ 已登录')
        print(f'  [用户] {user_data.get("username", "Unknown")}')
        print(f'  [虾米] {user_data.get("coins", user_data.get("balance", "N/A"))}')
        print(f'  [等级] {user_data.get("level", "N/A")}')
    else:
        print(f'  [登录] ❌ 失败: {data.get("message", "Unknown error")}')
except Exception as e:
    print(f'  [登录] ❌ 异常: {e}')
print()

# 检查技能列表
try:
    r = requests.get('https://xiaping.coze.site/api/skills?limit=5&offset=0', headers=headers2, timeout=15)
    data = r.json()
    if data.get('success'):
        skills = data.get('data', {}).get('skills', [])
        total = data.get('data', {}).get('total', 0)
        print(f'  [技能] 平台总技能数: {total}')
        print(f'  [技能] 预览（前5个）:')
        for s in skills[:5]:
            name = s.get('name', 'N/A')
            rating = s.get('rating', 0)
            author = s.get('author', 'N/A')
            print(f'         - {name} (评分:{rating:.1f}) by {author}')
    else:
        print(f'  [技能] ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  [技能] ❌ 异常: {e}')
print()
print('=' * 70)
print()

# ===== 3. ABTI 验证 =====
print('【3/3】ABTI - Agent 人格测试平台')
print('-' * 70)
headers3 = {'agent-auth-api-key': API_KEY, 'Content-Type': 'application/json'}

# 检查题目列表
try:
    r = requests.get('https://abtitest.coze.site/api/v1/questions', headers=headers3, timeout=15)
    data = r.json()
    if data.get('success'):
        questions = data.get('data', {}).get('questions', [])
        print(f'  [题目] ✅ 题目获取成功')
        print(f'  [题目] 题目总数: {len(questions)}')
        if questions:
            print(f'  [题目] 示例: {questions[0].get("text", "")[:50]}...')
    else:
        print(f'  [题目] ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  [题目] ❌ 异常: {e}')
print()

# 检查是否已完成测试
try:
    r = requests.get('https://abtitest.coze.site/api/v1/my-result', headers=headers3, timeout=15)
    data = r.json()
    if data.get('success'):
        result = data.get('data', {})
        print(f'  [结果] ✅ 已获取测试结果')
        print(f'  [结果] 人格类型: {result.get("type", "N/A")}')
        print(f'  [结果] 完成时间: {result.get("completed_at", "N/A")}')
    else:
        msg = data.get('message', '')
        if 'not found' in msg.lower() or 'no result' in msg.lower():
            print(f'  [结果] ⚠️ 尚未完成测试')
        else:
            print(f'  [结果] ❌ 失败: {msg}')
except Exception as e:
    print(f'  [结果] ❌ 异常: {e}')
print()
print('=' * 70)
print()

# ===== 总结 =====
print('验证总结')
print('=' * 70)
print('Signal Arena:  虚拟炒股平台 - 请查看上方详细信息')
print('虾评 Skill:    技能交易平台 - 请查看上方详细信息')
print('ABTI:          Agent人格测试 - 请查看上方详细信息')
print('=' * 70)
print()
print('建议下一步操作:')
print('  1. 检查 Signal Arena 持仓是否成交')
print('  2. 在虾评平台浏览并下载技能')
print('  3. 完成 ABTI 人格测试（32道题）')
print()
