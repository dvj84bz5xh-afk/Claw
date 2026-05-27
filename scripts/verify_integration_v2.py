#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 Agent World 三个联盟站点的集成连接（修正版）"""
import requests, json, sys

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
headers_signal = {'agent-auth-api-key': API_KEY}
headers_xp = {'Authorization': f'Bearer {API_KEY}'}
headers_abti = {'agent-auth-api-key': API_KEY}

print('=== Agent World 集成功能连接验证（修正版）===\n')

# ─── 1. Signal Arena - 持仓查询 ───
print('【1】Signal Arena（策场） - 连接测试')
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/portfolio',
                     headers=headers_signal, timeout=15)
    data = r.json()
    if data.get('success'):
        d = data['data']
        agent = d.get('agent', {})
        portfolio = d.get('portfolio', {})
        holdings = d.get('holdings', [])

        print(f'  ✅ 连接正常')
        print(f'  账号: {agent.get("username", "未知")}')
        print(f'  现金: {portfolio.get("cash", 0):,.0f}')
        print(f'  持仓市值: {portfolio.get("holdings_value", 0):,.0f}')
        print(f'  总市值: {portfolio.get("total_value", 0):,.0f}')
        print(f'  收益率: {portfolio.get("return_rate", 0)}%')
        print(f'  总手续费: {portfolio.get("total_fees", 0):,.0f}')

        if holdings:
            print(f'  持仓明细({len(holdings)}只):')
            for h in holdings:
                cost = h.get('cost_basis', 0)
                curr = h.get('current_price', 0)
                profit = (curr - cost) * h.get('shares', 0) if cost else 0
                print(f'    - {h.get("symbol", "?")}: {h.get("shares", 0)}股  '
                      f'成本{cost:.2f} 现价{curr:.2f} 盈亏{profit:+.2f}')
        else:
            print('  持仓: 空仓（买入订单可能未结算）')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()

# ─── 2. Signal Arena - 排行榜 ───
print('【2】Signal Arena - 排行榜（前3名）')
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/leaderboard?limit=3',
                     headers=headers_signal, timeout=15)
    data = r.json()
    if data.get('success'):
        agents = data.get('data', {}).get('agents', [])
        print(f'  ✅ 获取成功（共{len(agents)}名）')
        for i, a in enumerate(agents, 1):
            print(f'    {i}. {a.get("username", "?")}  '
                  f'收益率{a.get("return_rate", 0):.2f}%  '
                  f'市值{a.get("total_value", 0):,.0f}')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()

# ─── 3. 虾评 - 登录状态 ───
print('【3】虾评 Skill - 连接测试')
try:
    r = requests.get('https://xiaping.coze.site/api/auth/me',
                     headers=headers_xp, timeout=15)
    data = r.json()
    if data.get('success'):
        u = data['data']
        print(f'  ✅ 连接正常')
        print(f'  用户名: {u.get("name", "?")}')
        print(f'  虾米余额: {u.get("coins", 0)}')
        print(f'  等级: {u.get("level", "?")}')
        print(f'  累计赚取: {u.get("total_earned", 0)}')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('【4】虾评 - 已下载技能')
try:
    r = requests.get('https://xiaping.coze.site/api/me/downloads',
                     headers=headers_xp, timeout=15)
    data = r.json()
    if data.get('success'):
        items = data.get('data', {}).get('items', [])
        print(f'  ✅ 下载记录: {len(items)} 条')
        for item in items[:5]:
            print(f'    - {item.get("skill_name", "未知")}')
        if not items:
            print('    （试用版下载可能不记录到此列表）')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()

# ─── 5. ABTI - 连接测试 ───
print('【5】ABTI - 连接测试')
try:
    r = requests.get('https://abtitest.coze.site/api/v1/questions',
                     headers=headers_abti, timeout=15)
    data = r.json()
    if data.get('success'):
        q = data['data']
        print(f'  ✅ 连接正常')
        print(f'  题目总数: {q.get("total_questions", 0)}')
        print(f'  正式题: {len(q.get("questions", []))} 道')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('【6】ABTI - 查看我的测试结果')
try:
    r = requests.get('https://abtitest.coze.site/api/v1/result/claw-investigator-v5',
                     timeout=15)
    data = r.json()
    if data.get('success'):
        d = data.get('data', {})
        print(f'  ✅ 已测试')
        print(f'  人格类型: {d.get("personality", "未知")}')
        scores = d.get('scores', {})
        if scores:
            print(f'  各维度得分:')
            for k, v in list(scores.items())[:5]:
                print(f'    {k}: {v}')
    else:
        msg = data.get('message', '')
        print(f'  ⚠️ 未测试: {msg}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('=' * 50)
print('✅ 集成连接验证完成')
