#!/usr/bin/env python3
"""
记忆标签管理工具 v2 - 完整实现
为记忆片段添加标签，构建标签索引，支持标签搜索

标签格式（写入文件的分区标题后）：
    ## [PROJECT] 项目进行中  <!-- tags: 区块链,洗钱,课程 -->
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set

MEMORY_DIR = Path(__file__).parent
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
TAG_INDEX_FILE = MEMORY_DIR / "tag_index.json"

# 预定义常用标签（自动补全参考）
KNOWN_TAGS = {
    "用户": ["偏好", "习惯", "背景", "职业", "语言", "工作风格"],
    "项目": ["Claw学习追踪", "加密货币课程", "诈骗园区调查", "Hermes优化", "CodeBuddy产品", "证券直播引流"],
    "技术": ["Python", "Node.js", "Git", "Windows", "PowerShell", "区块链", "BSC", "BSCScan"],
    "技能": ["创建", "优化", "审查", "安全", "自动化", "去AI化"],
    "紧急": ["P0", "P1", "阻断", "今天完成"],
    "长期": ["原理", "方法论", "最佳实践", "架构设计"],
}


def load_tag_index() -> Dict:
    if TAG_INDEX_FILE.exists():
        with open(TAG_INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tags": {}, "files": {}, "all_tags": [], "last_update": ""}


def save_tag_index(index: Dict):
    index['last_update'] = datetime.now().isoformat()
    with open(TAG_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def parse_tags_from_line(line: str) -> List[str]:
    """从行中提取 <!-- tags: ... --> 中的标签"""
    m = re.search(r'<!-- tags:\s*(.+?)\s*-->', line)
    if m:
        return [t.strip() for t in m.group(1).split(',')]
    return []


def add_tags_to_file(filepath: Path, section_name: str, tags: List[str]) -> bool:
    """
    为指定分区添加/合并标签
    在 ## [XXX] 标题行后添加 <!-- tags: ... --> 注释行
    """
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    added = False

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # 匹配分区标题
        section_m = re.match(r'^(##\s+\[.+?\])(.*)', line)
        if section_m and section_name in line:
            # 检查下一行是否已有标签
            if i + 1 < len(lines) and '<!-- tags:' in lines[i + 1]:
                # 合并标签
                existing_tags = parse_tags_from_line(lines[i + 1])
                merged = list(set(existing_tags + tags))
                new_lines.append(f"<!-- tags: {', '.join(merged)} -->\n")
                i += 2  # 跳过原标签行
                added = True
                continue
            else:
                # 插入新标签行
                new_lines.append(f"<!-- tags: {', '.join(tags)} -->\n")
                added = True
                i += 1
                continue
        i += 1

    if added:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ 已为 {section_name} 添加标签: {', '.join(tags)}")
        return True
    else:
        print(f"⚠️  未找到分区: {section_name}")
        return False


def build_tag_index() -> Dict:
    """
    扫描所有记忆文件，构建标签索引
    返回完整索引字典
    """
    index = {"tags": {}, "files": {}, "all_tags": [], "last_update": ""}
    all_tags_set = set()

    md_files = list(MEMORY_DIR.glob("*.md"))
    # 排除备份和新文件
    md_files = [f for f in md_files if f.name not in ('MEMORY_NEW.md', 'tag_index.json')]

    for filepath in md_files:
        file_key = filepath.name
        index['files'][file_key] = []

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            # 提取标签
            tags_in_line = parse_tags_from_line(line)
            if tags_in_line:
                all_tags_set.update(tags_in_line)
                index['files'][file_key].extend(tags_in_line)

                # 记录标签出现在哪个文件、哪一行
                # 上一行是分区标题
                if i > 0:
                    section_line = lines[i - 1].strip()
                    for tag in tags_in_line:
                        if tag not in index['tags']:
                            index['tags'][tag] = []
                        index['tags'][tag].append({
                            'file': file_key,
                            'line': i,
                            'section': section_line
                        })

    index['all_tags'] = sorted(all_tags_set)
    return index


def search_by_tags(tags: List[str], match_all: bool = False) -> List[Dict]:
    """按标签搜索，返回匹配的记忆片段"""
    index = load_tag_index()
    if not index['tags']:
        print("⚠️  标签索引为空，请先运行 --build-index")
        return []

    results = []
    matched_files = set()

    for tag in tags:
        if tag in index['tags']:
            for entry in index['tags'][tag]:
                matched_files.add((entry['file'], entry['line'], entry['section']))

    # 读取匹配内容
    for file_name, line_num, section in matched_files:
        filepath = MEMORY_DIR / file_name
        if not filepath.exists():
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 提取该分区内容（直到下一个 ## 或文件结束）
        content_lines = []
        i = max(0, line_num - 1)
        if i < len(lines):
            content_lines.append(lines[i].strip())  # 分区标题
            i += 1
            while i < len(lines):
                if lines[i].startswith('## '):
                    break
                content_lines.append(lines[i].rstrip())
                i += 1

        results.append({
            'file': file_name,
            'section': section,
            'line': line_num,
            'content': '\n'.join(content_lines[:10])  # 前10行
        })

    return results


def archive_old_logs(days: int = 30) -> int:
    """
    归档30天前的日志：
    1. 提取关键信息合并到 MEMORY.md 对应分区
    2. 备份到 archived_ 前缀文件
    3. 删除原日志文件
    """
    cutoff = datetime.now() - timedelta(days=days)
    date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\.md$')

    archived = 0

    for filepath in MEMORY_DIR.glob("*.md"):
        if filepath.name == 'MEMORY.md' or filepath.name.startswith('archived_'):
            continue
        if filepath.name == '2026-05-17.md':
            continue  # 今天的日志不归档

        m = date_pattern.match(filepath.name)
        if not m:
            continue

        file_date = datetime.strptime(m.group(1), '%Y-%m-%d')
        if file_date >= cutoff:
            continue

        print(f"\n📦 归档: {filepath.name} ({m.group(1)})")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 备份
        backup_path = MEMORY_DIR / f"archived_{filepath.name}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(f"# 归档自 {filepath.name}\n\n{content}")

        # 提取关键内容合并到 MEMORY.md（追加到对应分区）
        # 简化版：追加到 [PROJECT] 分区
        _append_to_memory_section(content, filepath.name)

        # 删除原文件
        filepath.unlink()
        print(f"  ✅ 已归档至 {backup_path.name}，原文件已删除")
        archived += 1

    return archived


def _append_to_memory_section(content: str, source: str):
    """将内容追加到 MEMORY.md 的对应分区（简化实现）"""
    if not MEMORY_FILE.exists():
        return

    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 在文件末尾前追加（在 --- 分隔线前）
    new_lines = []
    for line in lines:
        if line.strip() == '---' or line.strip().startswith('*本文件'):
            # 在这里插入归档内容
            new_lines.append(f"\n\n## 归档自 {source}\n\n")
            new_lines.append(content)
            new_lines.append("\n")
        new_lines.append(line)

    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def list_all_tags() -> Dict[str, int]:
    """列出所有标签及使用次数"""
    index = load_tag_index()
    if not index['all_tags']:
        print("⚠️  标签索引为空，请先运行 --build-index")
        return {}

    tag_counts = {}
    for tag, entries in index['tags'].items():
        tag_counts[tag] = len(entries)

    return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))


def main():
    parser = argparse.ArgumentParser(description='记忆标签管理工具 v2')
    parser.add_argument('--add', nargs='+',
                        help='添加标签: --add 文件名 分区名 标签1,标签2,标签3')
    parser.add_argument('--search', '-s', help='按标签搜索')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有标签')
    parser.add_argument('--build-index', action='store_true', help='重建标签索引')
    parser.add_argument('--archive', action='store_true', help='归档30天前的日志')

    args = parser.parse_args()

    if args.add:
        # --add MEMORY.md "[PROJECT]" 区块链,洗钱,课程
        if len(args.add) < 3:
            print("用法: --add <文件名> <分区名> <标签1,标签2,...>")
            return
        filepath = MEMORY_DIR / args.add[0]
        section = args.add[1]
        tags = []
        for t in args.add[2:]:
            tags.extend([x.strip() for x in t.split(',')])
        add_tags_to_file(filepath, section, tags)

    elif args.build_index:
        print("🔄 重建标签索引...")
        index = build_tag_index()
        save_tag_index(index)
        print(f"✅ 索引已保存，共 {len(index['all_tags'])} 个不同标签")

    elif args.search:
        results = search_by_tags([args.search])
        print(f"\n🔍 标签搜索: {args.search}")
        print("=" * 60)
        for r in results[:20]:
            print(f"\n[{r['file']}] {r['section']}")
            print(f"{r['content'][:200]}")
            print("-" * 60)

    elif args.list:
        tag_counts = list_all_tags()
        if tag_counts:
            print("\n📋 所有标签（按使用次数排序）:")
            print("=" * 60)
            for tag, count in tag_counts.items():
                print(f"  {tag}: {count} 处")

    elif args.archive:
        print("📦 开始归档30天前的日志...")
        count = archive_old_logs(30)
        print(f"\n✅ 共归档 {count} 个文件")

    else:
        print("用法：")
        print('  python memory_tagger.py --add MEMORY.md "[USER]" "偏好,工作风格"')
        print('  python memory_tagger.py --build-index')
        print('  python memory_tagger.py --search "区块链"')
        print('  python memory_tagger.py --list')
        print('  python memory_tagger.py --archive')


if __name__ == '__main__':
    main()
