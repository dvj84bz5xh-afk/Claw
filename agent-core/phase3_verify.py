"""
Phase 3 Module Verification Script
"""

import sys
sys.path.insert(0, '.')

print('=' * 60)
print('Phase 3 Module Verification')
print('=' * 60)

# Test 1: Tool Registry Trait
try:
    from tool_registry_trait import ToolRegistry, FileReadTool, BashTool, ToolCall
    registry = ToolRegistry()
    registry.register(FileReadTool())
    registry.register(BashTool())
    
    # Test execution
    result = registry.execute('bash', {'command': 'echo Phase3_Test', 'timeout': 10})
    
    if result.success:
        print('[OK] Tool Registry Trait: Working')
        output = result.data.get('stdout', '').strip()
        print(f'  Output: {output}')
    else:
        print('[ERR] Tool Registry Trait: Execution failed')
        print(f'  Error: {result.error_message}')
except Exception as e:
    print(f'[ERR] Tool Registry Trait: {e}')

print()

# Test 2: Git Context Enhanced
try:
    from git_context_enhanced import GitContextProvider, GitContextInjector
    provider = GitContextProvider()
    
    if provider.is_git_repository():
        context = provider.get_context()
        print('[OK] Git Context Enhanced: Working')
        print(f'  Repo: {context.repo_name}')
        print(f'  Branch: {context.current_branch}')
        print(f'  Commits: {len(context.recent_commits)}')
    else:
        print('[WARN] Git Context Enhanced: Not in git repo')
except Exception as e:
    print(f'[ERR] Git Context Enhanced: {e}')

print()

# Test 3: Task Registry
try:
    from task_registry import TaskRegistry, TaskExecutor, TaskPriority
    registry = TaskRegistry()
    
    task = registry.create_task(
        name='Phase3_Test_Task',
        target=lambda: 'Task completed',
        priority=TaskPriority.HIGH
    )
    
    executor = TaskExecutor(registry)
    executor.execute_task(task.task_id, sync=True)
    
    completed_task = registry.get_task(task.task_id)
    if completed_task.status.name == 'COMPLETED':
        print('[OK] Task Registry: Working')
        print(f'  Task: {completed_task.name}')
        print(f'  Result: {completed_task.result}')
    else:
        print(f'[WARN] Task Registry: Status is {completed_task.status.name}')
except Exception as e:
    print(f'[ERR] Task Registry: {e}')

print()
print('=' * 60)
print('Phase 3 Verification Complete')
print('=' * 60)
