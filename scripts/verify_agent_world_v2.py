#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent World 集成功能验证脚本 v2
增强版：打印原始响应，帮助调试
"""

import requests
import json
import sys

# 强制 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

API_KEY = 'agent-world-b798445eb16399cd899cf4889e20ef8067f41c70f60af2d0'

print('=' * 70)
print('Agent World 集成功能验证 v2 - 2026-05-01 23:39')
print('=' * 70)
print()

# ===== 1. Signal Arena 验证 =====
print('【1/3】Signal Arena（策场）- 虚拟炒股平台')
print('-' * 70)
headers1 = {'agent-auth-api-key': API_KEY, 'Content-Type': 'application/json'}

# 检查我的状态
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/me', headers=headers1, timeout=15)
    print(f'  [连接] HTTP状态码: {r.status_code}')
    print(f'  [连接] 响应类型: {r.headers.get("content-type", "unknown")}')
    print(f'  [连接] 响应前100字符: {r.text[:100]}')
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get('success'):
                me_data = data.get('data', {})
                print(f'  [连接] ✅ API连接正常')
                print(f'  [用户] {me_data.get("agent_name", "Unknown")}')
                print(f'  [现金] ${me_data.get("cash", 0):,.2f}')
                print(f'  [总资产] ${me_data.get("total_value", 0):,.2f}')
                print(f'  [收益率] {me_data.get("return_rate", 0)*100:.2f}%')
            else:
                print(f'  [连接] ❌ API返回失败: {data.get("message")}')
        except json.JSONDecodeError:
            print(f'  [连接] ❌ JSON解析失败')
    else:
        print(f'  [连接] ❌ HTTP错误: {r.status_code}')
except Exception as e:
    print(f'  [连接] ❌ 异常: {type(e).__name__}: {e}')
print()

# 检查持仓
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/portfolio', headers=headers1, timeout=15)
    print(f'  [持仓] HTTP状态码: {r.status_code}')
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get('success'):
                portfolio = data.get('data', {}).get('portfolio', {})
                cash = portfolio.get('cash', 0)
                positions = portfolio.get('positions', [])
                print(f'  [持仓] ✅ 获取成功')
                print(f'  [持仓] 可用资金: ${cash:,.2f}')
                print(f'  [持仓] 持仓数量: {len(positions)}')
                if positions:
                    for p in positions:
                        print(f'         - {p.get("symbol")}: {p.get("quantity")}股 @ ${p.get("avg_cost", 0):.2f}')
                else:
                    print('         (暂无持仓)')
            else:
                print(f'  [持仓] ❌ 失败: {data.get("message")}')
        except json.JSONDecodeError as e:
            print(f'  [持仓] ❌ JSON解析失败: {e}')
            print(f'  [持仓] 原始响应: {r.text[:200]}')
    else:
        print(f'  [持仓] ❌ HTTP错误: {r.status_code}')
except Exception as e:
    print(f'  [持仓] ❌ 异常: {type(e).__name__}: {e}')
print()

# 检查交易记录
try:
    r = requests.get('https://signal.coze.site/api/v1/arena/trades?limit=5', headers=headers1, timeout=15)
    print(f'  [交易] HTTP状态码: {r.status_code}')
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get('success'):
                trades = data.get('data', {}).get('trades', [])
                print(f'  [交易] ✅ 获取成功')
                print(f'  [交易] 历史交易: {len(trades)} 笔')
                for t in trades[:5]:
                    symbol = t.get('symbol', 'N/A')
                    side = t.get('side', 'N/A')
                    qty = t.get('quantity', 0)
                    price = t.get('price', 0)
                    status = t.get('status', 'N/A')
                    print(f'         - {symbol} {side} {qty}股 @ ${price:.2f} [{status}]')
            else:
                print(f'  [交易] ❌ 失败: {data.get("message")}')
        except json.JSONDecodeError as e:
            print(f'  [交易] ❌ JSON解析失败: {e}')
            print(f'  [交易] 原始响应: {r.text[:200]}')
    else:
        print(f'  [交易] ❌ HTTP错误: {r.status_code}')
except Exception as e:
    print(f'  [交易] ❌ 异常: {type(e).__name__}: {e}')
print()
print('=' * 70)
print()

# ===== 2. 虾评 Skill 验证 =====
print('【2/3】虾评 Skill - 技能交易平台')
print('-' * 70)
headers2 = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# 检查登录状态 - 尝试不同的端点
endpoints_to_try = [
    'https://xiaping.coze.site/api/auth/me',
    'https://xiaping.coze.site/api/me',
    'https://xiaping.coze.site/api/user/me'
]

for endpoint in endpoints_to_try:
    print(f'  尝试端点: {endpoint}')
    try:
        r = requests.get(endpoint, headers=headers2, timeout=15)
        print(f'  HTTP状态码: {r.status_code}')
        print(f'  响应前150字符: {r.text[:150]}')
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'  ✅ JSON解析成功')
                print(f'  响应数据: {json.dumps(data, ensure_ascii=False)[:300]}')
                break  # 成功，退出循环
            except json.JSONDecodeError:
                print(f'  ❌ JSON解析失败')
    except Exception as e:
        print(f'  ❌ 异常: {type(e).__name__}: {e}')
    print()

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
    print(f'  [题目] HTTP状态码: {r.status_code}')
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get('success'):
                questions = data.get('data', {}).get('questions', [])
                print(f'  [题目] ✅ 题目获取成功')
                print(f'  [题目] 题目总数: {len(questions)}')
                if questions:
                    q_text = questions[0].get('text', '')[:60]
                    print(f'  [题目] 示例: {q_text}...')
            else:
                print(f'  [题目] ❌ 失败: {data.get("message")}')
        except json.JSONDecodeError as e:
            print(f'  [题目] ❌ JSON解析失败: {e}')
            print(f'  [题目] 原始响应: {r.text[:200]}')
    else:
        print(f'  [题目] ❌ HTTP错误: {r.status_code}')
except Exception as e:
    print(f'  [题目] ❌ 异常: {type(e).__name__}: {e}')
print()

# 检查是否已完成测试
try:
    r = requests.get('https://abtitest.coze.site/api/v1/my-result', headers=headers3, timeout=15)
    print(f'  [结果] HTTP状态码: {r.status_code}')
    print(f'  [结果] 响应前150字符: {r.text[:150]}')
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get('success'):
                result = data.get('data', {})
                print(f'  [结果] ✅ 已获取测试结果')
                print(f'  [结果] 人格类型: {result.get("type", "N/A")}')
                print(f'  [结果] 完成时间: {result.get("completed_at", "N/A")}')
            else:
                msg = data.get('message', '')
                print(f'  [结果] ⚠️ {msg}')
        except json.JSONDecodeError as e:
            print(f'  [结果] ❌ JSON解析失败: {e}')
            print(f'  [结果] 原始响应: {r.text[:200]}')
    else:
        print(f'  [结果] ⚠️ HTTP错误 {r.status_code} - 可能尚未完成测试')
except Exception as e:
    print(f'  [结果] ❌ 异常: {type(e).__name__}: {e}')
print()
print('=' * 70)
print()

# ===== 总结 =====
print('验证总结')
print('=' * 70)
print('请根据上方详细信息检查各站点连接状态')
print('如有 ❌ 或异常，请查看具体错误信息')
print('=' * 70)
print()
