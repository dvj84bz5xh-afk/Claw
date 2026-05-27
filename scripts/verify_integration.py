#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 Agent World 三个联盟站点的集成连接"""
import requests, json, sys

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'
headers_signal = {'agent-auth-api-key': API_KEY}
headers_xp = {'Authorization': f'Bearer {API_KEY}'}
headers_abti = {'agent-auth-api-key': API_KEY}

print('=== Agent World 集成功能连接验证 ===\n')

# ─── 1. Signal Arena ───
print('【1】Signal Arena（策场）- 连接测试')
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/portfolio',
                      headers=headers_signal, timeout=15)
    data = r.json()
    if data.get('success'):
        p = data['data']
        print(f'  ✅ 连接正常')
        print(f'  现金: {p["cash"]:,.0f}')
        print(f'  持仓市值: {p["holdings_value"]:,.0f}')
        print(f'  总市值: {p["total_value"]:,.0f}')
        print(f'  收益率: {p["return_rate"]}%')
        holdings = p.get('holdings', [])
        if holdings:
            print(f'  持仓明细({len(holdings)}只):')
            for h in holdings:
                print(f'    - {h["symbol"]}: {h["shares"]}股, '
                      f'成本{h["cost_basis"]:.2f}, 现价{h["current_price"]:.2f}')
        else:
            print('  持仓: 空仓（订单可能未结算）')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()

# ─── 2. 虾评 - 登录状态 ───
print('【2】虾评 Skill - 连接测试')
try:
    r = requests.get('https://xiaping.coze.site/api/auth/me',
                     headers=headers_xp, timeout=15)
    data = r.json()
    if data.get('success'):
        u = data['data']
        print(f'  ✅ 连接正常')
        print(f'  用户名: {u["name"]}')
        print(f'  虾米余额: {u["coins"]}')
        print(f'  等级: {u["level"]}')
        print(f'  累计赚取: {u["total_earned"]}')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('【3】虾评 - 下载记录')
try:
    r2 = requests.get('https://xiaping.coze.site/api/me/downloads',
                       headers=headers_xp, timeout=15)
    data2 = r2.json()
    if data2.get('success'):
        items = data2.get('data', {}).get('items', [])
        print(f'  ✅ 下载记录: {len(items)} 条')
        for item in items[:5]:
            print(f'    - {item.get("skill_name", "未知")}')
    else:
        print(f'  ❌ 失败: {data2.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()

# ─── 4. ABTI ───
print('【4】ABTI - 连接测试')
try:
    r = requests.get('https://abtitest.coze.site/api/v1/questions',
                     headers=headers_abti, timeout=15)
    data = r.json()
    if data.get('success'):
        q = data['data']
        print(f'  ✅ 连接正常')
        print(f'  题目总数: {q["total_questions"]}')
        print(f'  正式题: {len(q["questions"])} 道')
    else:
        print(f'  ❌ 失败: {data.get("message")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('【5】ABTI - 查看测试结果')
try:
    r2 = requests.get('https://abtitest.coze.site/api/v1/result/claw-investigator-v5',
                      timeout=15)
    data2 = r2.json()
    if data2.get('success'):
        d = data2.get('data', {})
        print(f'  ✅ 已测试')
        print(f'  人格类型: {d.get("personality", "未知")}')
        scores = d.get('scores', {})
        if scores:
            print(f'  各维度得分: {json.dumps(scores, ensure_ascii=False)}')
    else:
        print(f'  ⚠️ 未测试: {data2.get("message", "")}')
except Exception as e:
    print(f'  ❌ 异常: {e}')

print()
print('=' * 50)
print('验证完成')
