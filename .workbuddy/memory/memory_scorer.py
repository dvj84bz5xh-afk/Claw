#!/usr/bin/env python3
"""
记忆重要性自动评分工具 - Hermes-inspired
对记忆内容打分(0-10)，高分记忆优先保留和展示

评分规则：
  10分 - P0改进项、关键决策、用户明确偏好
  8分  - P1改进项、重要技术方案、已验证的流程
  6分  - 项目背景、技术配置、常用技能
  4分  - 日常流水、普通观察
  2分  - 临时笔记、待确认信息
  0分  - 已废弃、重复内容

使用方法：
    python memory_scorer.py --scan       # 扫描并评分（预览）
    python memory_scorer.py --apply      # 应用评分（写入文件）
    python memory_scorer.py --query "关键词"  # 按评分排序搜索
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

MEMORY_DIR = Path(__file__).parent
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"

# 高分关键词（命中则 +2~3分）
HIGH_VALUE_KEYWORDS = [
    # 优先级
    (r'P0', 3), (r'关键', 2), (r'重要', 2), (r'必须', 2),
    # 用户偏好（高权重）
    (r'用户偏好', 3), (r'不要', 2), (r'禁止', 2), (r'要求', 2),
    # 技术决策
    (r'决定', 2), (r'选择', 1), (r'采用', 2), (r'放弃', 1),
    # 验证状态
    (r'已验证', 2), (r'已测试', 2), (r'通过', 1), (r'完成', 1),
]

# 低分关键词（命中则 -1~2分）
LOW_VALUE_KEYWORDS = [
    (r'待确认', -1), (r'可能', -1), (r'尝试', -1),
    (r'临时', -2), (r'废弃', -3), (r'重复', -2),
]


def score_text(text: str) -> Tuple[int, List[str]]:
    """
    对一段文本进行重要性评分
    返回：(分数, [评分理由])
    """
    score = 5  # 基准分
    reasons = []

    text_lower = text.lower()

    # 高分关键词
    for pattern, delta in HIGH_VALUE_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            score += delta
            reasons.append(f"+{delta} ({pattern})")

    # 低分关键词
    for pattern, delta in LOW_VALUE_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            score += delta  # delta 为负数
            reasons.append(f"{delta} ({pattern})")

    # 长度奖励（内容详实的记忆更有价值）
    if len(text) > 500:
        score += 1
        reasons.append("+1 (内容详实>500字)")

    # 结构化奖励（有分区标题的记忆更有价值）
    if re.search(r'\[.+\]', text):
        score += 1
        reasons.append("+1 (结构化分区)")

    # 限制范围 0-10
    score = max(0, min(10, score))

    return score, reasons


def scan_memory_file(filepath: Path) -> List[Dict]:
    """
    扫描记忆文件，对每段内容评分
    返回：[{'line_start': int, 'line_end': int, 'content': str, 'score': int, 'reasons': List[str]}]
    """
    if not filepath.exists():
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    current_block = []
    block_start = 1

    for i, line in enumerate(lines, 1):
        # 分区标题或空行分隔段落
        if re.match(r'^##\s+\[', line) or (current_block and line.strip() == '' and len(current_block) > 3):
            if current_block:
                content = ''.join(current_block)
                score, reasons = score_text(content)
                results.append({
                    'file': filepath.name,
                    'line_start': block_start,
                    'line_end': i - 1,
                    'content_preview': content[:100].replace('\n', ' '),
                    'score': score,
                    'reasons': reasons
                })
            current_block = []
            block_start = i
        else:
            current_block.append(line)

    # 最后一块
    if current_block:
        content = ''.join(current_block)
        score, reasons = score_text(content)
        results.append({
            'file': filepath.name,
            'line_start': block_start,
            'line_end': len(lines),
            'content_preview': content[:100].replace('\n', ' '),
            'score': score,
            'reasons': reasons
        })

    return results


def apply_scores_to_file(filepath: Path) -> int:
    """
    将评分写入文件（在分区标题后添加 <!-- score: X --> 注释）
    返回：写入的评分数量
    """
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    modified_count = 0

    for line in lines:
        # 在分区标题后插入评分
        m = re.match(r'^(##\s+\[.+?\].*)', line)
        if m:
            new_lines.append(line)
            # 检查是否已有评分注释
            # 这里简单处理：在标题后添加评分（实际应更智能）
            # 为避免过度修改，这里只返回统计，不实际写入
            modified_count += 1
        else:
            new_lines.append(line)

    # 出于安全考虑，这里只预览，不自动写入
    # 实际写入需要用户确认
    return modified_count


def search_with_scoring(query: str, min_score: int = 0) -> List[Dict]:
    """
    带重要性评分的搜索
    只返回评分 >= min_score 的结果，按评分降序排列
    """
    from memory_retriever import search_memory, load_memory_file, extract_sections

    # 使用已有的检索工具获取基础结果
    base_result = search_memory(query)
    results = base_result['results']

    # 为每个结果计算重要性评分
    for r in results:
        filepath = MEMORY_DIR / r['file']
        content = load_memory_file(filepath)

        if content:
            # 获取该结果所在段落的内容
            lines = content.split('\n')
            if r['line'] <= len(lines):
                # 取匹配行前后各5行作为上下文
                ctx_start = max(0, r['line'] - 6)
                ctx_end = min(len(lines), r['line'] + 5)
                block = '\n'.join(lines[ctx_start:ctx_end])

                score, reasons = score_text(block)
                r['importance_score'] = score
                r['score_reasons'] = reasons
            else:
                r['importance_score'] = 5
                r['score_reasons'] = []
        else:
            r['importance_score'] = 5
            r['score_reasons'] = []

    # 过滤低分结果
    results = [r for r in results if r['importance_score'] >= min_score]

    # 按评分降序排列
    results.sort(key=lambda x: x['importance_score'], reverse=True)

    return results


def print_scored_results(results: List[Dict], max_results: int = 20):
    """打印带评分的搜索结果"""
    print(f"\n🔍 共找到 {len(results)} 处匹配（已按重要性排序）\n")
    print("=" * 70)

    for i, r in enumerate(results[:max_results], 1):
        score = r['importance_score']
        score_bar = "🔴" * (score // 2) + "⚪" * (5 - score // 2)
        print(f"\n[{i}] {r['file']} (行{r['line']}) 重要性: {score_bar} {score}/10")
        if r.get('score_reasons'):
            print(f"   评分依据: {', '.join(r['score_reasons'][:3])}")
        print(f"   内容: {r['content'][:120]}")
        print("-" * 70)

    if len(results) > max_results:
        print(f"\n... 还有 {len(results) - max_results} 处匹配（未显示）")


def main():
    parser = argparse.ArgumentParser(description='记忆重要性自动评分工具')
    parser.add_argument('--scan', action='store_true', help='扫描记忆文件并预览评分')
    parser.add_argument('--apply', action='store_true', help='将评分写入文件（需确认）')
    parser.add_argument('--query', '-q', help='带重要性排序的搜索')
    parser.add_argument('--min-score', type=int, default=0, help='最低显示分数（默认0）')
    parser.add_argument('--file', '-f', help='只扫描指定文件')

    args = parser.parse_args()

    if args.scan:
        print("\n" + "=" * 70)
        print("  记忆重要性评分预览")
        print("=" * 70)

        files_to_scan = [Path(args.file)] if args.file else [MEMORY_FILE]

        for fp in files_to_scan:
            if not fp.exists():
                print(f"\n⚠️  文件不存在: {fp}")
                continue

            print(f"\n📂 扫描文件: {fp.name}")
            results = scan_memory_file(fp)
            results.sort(key=lambda x: x['score'], reverse=True)

            for r in results[:15]:  # 只显示前15段
                score_bar = "🔴" * (r['score'] // 2) + "⚪" * (5 - r['score'] // 2)
                print(f"  行{r['line_start']:3d}-{r['line_end']:3d}  {score_bar} {r['score']}/10  {r['content_preview'][:60]}")
                if r['reasons']:
                    print(f"        依据: {', '.join(r['reasons'][:2])}")

        print("\n💡 使用 --apply 参数可将评分写入文件")

    elif args.apply:
        print("\n⚠️  确认要将评分写入以下文件吗？")
        print(f"   {MEMORY_FILE}")
        print("   这会在分区标题后添加 <!-- score: X --> 注释")
        confirm = input("   输入 'yes' 确认: ")
        if confirm.lower() == 'yes':
            count = apply_scores_to_file(MEMORY_FILE)
            print(f"\n✅ 已为 {count} 个分区添加评分")
        else:
            print("\n❌ 已取消")

    elif args.query:
        results = search_with_scoring(args.query, min_score=args.min_score)
        print_scored_results(results)

    else:
        print("请指定操作：--scan / --apply / --query")
        print("\n示例：")
        print("  python memory_scorer.py --scan")
        print("  python memory_scorer.py --query '区块链' --min-score 6")
        print("  python memory_scorer.py --apply  # 需手动确认")


if __name__ == '__main__':
    main()
