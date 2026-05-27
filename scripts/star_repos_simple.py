#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查GitHub Token并尝试star三个仓库（无emoji版本）"""
import os
import requests
import json

# 检查环境变量中的Token
print("=== 检查GitHub Token ===")
tokens_found = []
for key in ['GITHUB_TOKEN', 'GH_TOKEN', 'GITHUB_API_KEY', 'OAUTH_TOKEN']:
    val = os.environ.get(key)
    if val:
        tokens_found.append((key, val))
        print(f"  {key}: ***{val[-4:]} (长度: {len(val)})")

if not tokens_found:
    print("  未找到GitHub Token环境变量")
    print("  可用的环境变量（含'token'关键词）:")
    found = False
    for k in os.environ.keys():
        if 'token' in k.lower():
            print(f"    - {k}")
            found = True
    if not found:
        print("    （无）")
else:
    print(f"\n  找到 {len(tokens_found)} 个Token")

# 尝试 star 仓库（如果有Token）
if tokens_found:
    token = tokens_found[0][1]
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repos = [
        'forrestchang/andrej-karpathy-skills',
        'lsdefine/GenericAgent',
        'HKUDS/RAG-Anything'
    ]
    
    print("\n=== 尝试Star仓库 ===")
    for repo in repos:
        url = f'https://api.github.com/user/starred/{repo}'
        try:
            r = requests.put(url, headers=headers, proxies={'http': None, 'https': None}, timeout=10)
            if r.status_code in [204, 201]:
                print(f"  [OK] {repo} - 已star")
            elif r.status_code == 304:
                print(f"  [OK] {repo} - 已star（之前）")
            else:
                print(f"  [FAIL] {repo} - 失败({r.status_code}): {r.text[:100]}")
        except Exception as e:
            print(f"  [ERROR] {repo} - 错误: {e}")
else:
    print("\n[WARN] 无GitHub Token，无法自动star。")
    print("手动star链接:")
    print("  1. https://github.com/forrestchang/andrej-karpathy-skills")
    print("  2. https://github.com/lsdefine/GenericAgent")
    print("  3. https://github.com/HKUDS/RAG-Anything")

# 获取仓库最新状态（绕过代理）
print("\n=== 获取仓库最新状态 ===")
no_proxy = {'http': None, 'https': None}
repos = [
    'forrestchang/andrej-karpathy-skills',
    'lsdefine/GenericAgent',
    'HKUDS/RAG-Anything'
]
for repo in repos:
    try:
        r = requests.get(f'https://api.github.com/repos/{repo}', 
                        timeout=10, proxies=no_proxy)
        d = r.json()
        if 'stargazers_count' in d:
            print(f"{repo}")
            print(f"  Stars: {d['stargazers_count']}")
            print(f"  Forks: {d['forks_count']}")
            print(f"  Updated: {d['updated_at'][:10]}")
        else:
            print(f"{repo} - 错误: {d.get('message', '未知')}")
    except Exception as e:
        print(f"{repo} - 错误: {e}")
