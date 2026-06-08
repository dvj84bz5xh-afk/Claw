"""Apply ruff fixes and formatting to Python files.
Usage: python scripts/apply_fixes.py [agent-core/]
"""
import subprocess, sys, os

target = sys.argv[1] if len(sys.argv) > 1 else 'agent-core'
ruff = sys.executable  # use the same python that has ruff installed

def fix_file(py_path):
    """Read file, pass through ruff, write back if changed."""
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1) Lint fixes
    result = subprocess.run(
        [ruff, '-m', 'ruff', 'check', '--fix', '--stdin-filename', py_path, '-'],
        input=content, capture_output=True, text=True
    )
    fixed = result.stdout
    if result.returncode == 0 and fixed and fixed != content:
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        return True, result.stderr
    
    # 2) Format
    result = subprocess.run(
        [ruff, '-m', 'ruff', 'format', '--stdin-filename', py_path, '-'],
        input=content, capture_output=True, text=True
    )
    formatted = result.stdout
    if formatted and formatted != content:
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        return True, result.stderr
    
    return False, ''

count = fixed = 0
for root, dirs, files in os.walk(target):
    for f in sorted(files):
        if f.endswith('.py'):
            count += 1
            changed, err = fix_file(os.path.join(root, f))
            if changed:
                fixed += 1
                sys.stdout.write('.')
            if err and err.strip():
                sys.stdout.write('x')

print(f'\nDone: {fixed}/{count} files changed')
