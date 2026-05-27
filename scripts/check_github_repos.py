#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查三个GitHub仓库的最新状态（绕过代理）"""
import requests, json

# 绕过系统代理
no_proxy = {'http': None, 'https': None}

repos = [
    'forrestchang/andrej-karpathy-skills',
    'lsdefine/GenericAgent',
    'HKUDS/RAG-Anything'
]

for repo in repos:
    try:
        r = requests.get(f'https://api.github.com/repos/{repo}', 
                        timeout=15, proxies=no_proxy)
        d = r.json()
        print(f'{repo}')
        print(f'  Stars: {d.get("stargazers_count", 0)}')
        print(f'  Forks: {d.get("forks_count", 0)}')
        print(f'  Updated: {d.get("updated_at", "")[:10]}')
        print(f'  URL: {d.get("html_url", "")}')
        print()
    except Exception as e:
        print(f'{repo} - 错误: {e}')
        print()
