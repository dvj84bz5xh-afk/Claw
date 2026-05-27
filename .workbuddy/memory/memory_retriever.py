#!/usr/bin/env python3
"""
记忆检索工具 - Hermes-inspired Memory Retriever
支持关键词搜索、标签过滤、分区检索

使用方法：
    python memory_retriever.py "查询内容"
    python memory_retriever.py "区块链追踪" --tag [PROJECT]
    python memory_retriever.py "Python" --section [TECH]
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

MEMORY_DIR = Path(__file__).parent
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
DAILY_PATTERN = "YYYY-MM-DD.md"


def load_memory_file(filepath: Path) -> str:
    """加载记忆文件内容"""
    if not filepath.exists():
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_sections(content: str) -> Dict[str, str]:
    """
    提取 MEMORY.md 中各分区内容
    返回: { "[USER]": "内容...", "[PROJECT]": "内容..." }
    """
    sections = {}
    current_section = "[UNKNOWN]"
    current_lines = []

    for line in content.split('\n'):
        # 检测分区标题（如 ## [USER] 用户画像与偏好）
        section_match = re.match(r'^##\s+(\[.+?\])\s', line)
        if section_match:
            # 保存上一个分区
            if current_lines:
                sections[current_section] = '\n'.join(current_lines)
            current_section = section_match.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)

    # 保存最后一个分区
    if current_lines:
        sections[current_section] = '\n'.join(current_lines)

    return sections


def search_in_text(query: str, text: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
    """
    在文本中搜索查询词，返回匹配的行号和内容
    支持中文分词（简单实现）
    """
    results = []
    query_lower = query.lower()

    # 简单分词：按空格、标点分割
    keywords = re.findall(r'[\w\u4e00-\u9fff]+', query_lower)

    for i, line in enumerate(text.split('\n'), 1):
        line_lower = line.lower() if not case_sensitive else line

        # 检查是否包含任意关键词
        if any(kw in line_lower for kw in keywords):
            # 高亮匹配关键词
            highlighted = line
            for kw in keywords:
                highlighted = re.sub(
                    f'({re.escape(kw)})',
                    r'**\1**',
                    highlighted,
                    flags=re.IGNORECASE
                )
            results.append((i, highlighted))

    return results


def search_memory(query: str, section_filter: str = None,
                  tag_filter: str = None, days: int = 365) -> Dict:
    """
    主搜索函数

    参数：
        query: 搜索关键词
        section_filter: 只搜索特定分区（如 "[PROJECT]"）
        tag_filter: 按标签过滤（预留功能）
        days: 搜索最近N天的日志

    返回：
        {
            "query": 查询词,
            "total_matches": 总匹配数,
            "results": [
                {"file": "MEMORY.md", "section": "[PROJECT]", "line": 12, "content": "..."},
                ...
            ]
        }
    """
    results = []
    query_lower = query.lower()

    # 1. 搜索 MEMORY.md
    memory_content = load_memory_file(MEMORY_FILE)
    if memory_content:
        sections = extract_sections(memory_content)

        for section_name, section_content in sections.items():
            # 分区过滤
            if section_filter and section_filter not in section_name:
                continue

            matches = search_in_text(query, section_content)

            for line_num, highlighted in matches:
                # 提取匹配的上下文（前后各1行）
                lines = section_content.split('\n')
                ctx_start = max(0, line_num - 2)
                ctx_end = min(len(lines), line_num + 1)
                context = '\n'.join(lines[ctx_start:ctx_end])

                results.append({
                    'file': 'MEMORY.md',
                    'section': section_name,
                    'line': line_num,
                    'content': highlighted,
                    'context': context[:200]
                })

    # 2. 搜索日期日志文件
    cutoff_date = datetime.now() - timedelta(days=days)
    date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\.md$')

    if MEMORY_DIR.exists():
        for filepath in sorted(MEMORY_DIR.glob('*.md')):
            if filepath.name == 'MEMORY.md' or filepath.name == 'MEMORY_NEW.md':
                continue

            # 检查日期
            m = date_pattern.match(filepath.name)
            if m:
                file_date = datetime.strptime(m.group(1), '%Y-%m-%d')
                if file_date < cutoff_date:
                    continue

            content = load_memory_file(filepath)
            if not content:
                continue

            matches = search_in_text(query, content)

            for line_num, highlighted in matches:
                lines = content.split('\n')
                ctx_start = max(0, line_num - 2)
                ctx_end = min(len(lines), line_num + 1)
                context = '\n'.join(lines[ctx_start:ctx_end])

                results.append({
                    'file': filepath.name,
                    'section': '',
                    'line': line_num,
                    'content': highlighted,
                    'context': context[:200]
                })

    return {
        'query': query,
        'total_matches': len(results),
        'results': results
    }


def format_results(search_result: Dict, max_results: int = 20) -> str:
    """格式化搜索结果为可读文本"""
    output = []
    output.append(f"\n🔍 搜索词: 「{search_result['query']}」")
    output.append(f"📊 共找到 {search_result['total_matches']} 处匹配\n")
    output.append("=" * 60)

    for i, r in enumerate(search_result['results'][:max_results], 1):
        section_str = f"  [{r['section']}]" if r['section'] else ""
        output.append(f"\n[{i}] {r['file']}{section_str} (行{r['line']})")
        output.append(f"   内容: {r['content'][:100]}")
        if r['context']:
            output.append(f"   上下文:\n{r['context']}")
        output.append("-" * 60)

    if search_result['total_matches'] > max_results:
        output.append(f"\n... 还有 {search_result['total_matches'] - max_results} 处匹配（未显示）")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Hermes-inspired 记忆检索工具')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--section', '-s', help='只搜索特定分区（如 [PROJECT]）')
    parser.add_argument('--days', '-d', type=int, default=365, help='搜索最近N天的日志（默认365天）')
    parser.add_argument('--max', '-m', type=int, default=20, help='最多显示结果数（默认20）')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')

    args = parser.parse_args()

    # 执行搜索
    result = search_memory(
        query=args.query,
        section_filter=args.section,
        days=args.days
    )

    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_results(result, max_results=args.max))

    # 如果没有结果，给出建议
    if result['total_matches'] == 0:
        print("\n💡 未找到匹配，建议：")
        print("  1. 尝试更短的关键词")
        print("  2. 检查分区过滤是否正确")
        print("  3. 增大 --days 参数")


if __name__ == '__main__':
    main()
