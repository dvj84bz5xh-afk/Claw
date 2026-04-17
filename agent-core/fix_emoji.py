"""
修复文件中的表情符号编码问题
"""

import re

def fix_emojis_in_file(filepath):
    """修复文件中的表情符号"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换常见表情符号
    replacements = {
        '⚠️': '[警告]',
        '📁': '[GIT]',
        '📝': '[文件]',
        '🔍': '[差异]',
        '💾': '[提交]'
    }
    
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复文件: {filepath}")

if __name__ == "__main__":
    # 修复所有相关文件
    files_to_fix = [
        r'c:\Users\10127\WorkBuddy\Claw\agent-core\git_context_integration.py',
        r'c:\Users\10127\WorkBuddy\Claw\agent-core\git_context_real_scenarios.py'
    ]
    
    for filepath in files_to_fix:
        try:
            fix_emojis_in_file(filepath)
        except Exception as e:
            print(f"修复文件 {filepath} 失败: {e}")