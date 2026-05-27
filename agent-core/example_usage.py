"""
Agent Core 使用示例

展示如何应用从 Claude Code 泄露源码中学到的架构设计
"""

import sys
from pathlib import Path

# 确保 agent_core 模块可以被找到
agent_core_path = Path(__file__).parent
if str(agent_core_path) not in sys.path:
    sys.path.insert(0, str(agent_core_path))

from tool_registry import ToolRegistry
from session_manager import SessionManager
from permission_context import PermissionContext, PermissionLevel
from command_router import CommandRouter


def demo_tool_registry():
    """演示工具注册表"""
    print("=" * 60)
    print("演示 1: 工具注册表 (ToolRegistry)")
    print("=" * 60)
    
    # 创建工具注册表
    registry = ToolRegistry()
    
    # 列出所有内置工具
    print("\n内置工具列表:")
    for tool in registry.list_tools():
        print(f"  - {tool.name}: {tool.description} [{tool.permission_level}]")
    
    # 动态注册新工具
    def my_custom_tool(prompt: str, context: dict):
        return f"自定义工具处理: {prompt}"
    
    registry.register_tool(
        name="my_custom",
        description="我的自定义工具",
        executor=my_custom_tool,
        permission_level="read"
    )
    
    print("\n动态注册工具 'my_custom'")
    
    # 工具路由 - 根据提示词匹配最佳工具
    matches = registry.route_prompt("帮我搜索文件", limit=3)
    print("\n路由匹配 '帮我搜索文件':")
    for tool, score in matches:
        print(f"  - {tool.name} (匹配度: {score})")
    
    # 执行工具
    result = registry.execute_tool("my_custom", "测试参数")
    print(f"\n执行结果: {result.message}")


def demo_permission_context():
    """演示权限上下文"""
    print("\n" + "=" * 60)
    print("演示 2: 权限上下文 (PermissionContext)")
    print("=" * 60)
    
    # 创建只读权限上下文
    readonly_ctx = PermissionContext(level=PermissionLevel.READ_ONLY)
    print("\n只读权限模式:")
    
    for tool in ["read_file", "write_to_file", "execute_command", "bash"]:
        allowed, reason = readonly_ctx.can_use_tool(tool)
        status = "OK" if allowed else "NO"
        print(f"  [{status}] {tool}: {reason if not allowed else '允许'}")
    
    # 创建工作区写入权限
    workspace_ctx = PermissionContext(level=PermissionLevel.WORKSPACE_WRITE)
    print("\n工作区写入权限:")
    
    for tool in ["read_file", "write_to_file", "execute_command", "bash"]:
        allowed, reason = workspace_ctx.can_use_tool(tool)
        status = "OK" if allowed else "NO"
        print(f"  [{status}] {tool}: {reason if not allowed else '允许'}")
    
    # 禁用特定工具
    restricted_ctx = workspace_ctx.deny_tool("execute_command")
    print("\n禁用 execute_command 后:")
    allowed, reason = restricted_ctx.can_use_tool("execute_command")
    print(f"  [NO] execute_command: {reason}")


def demo_session_manager():
    """演示会话管理器"""
    print("\n" + "=" * 60)
    print("演示 3: 会话管理器 (SessionManager)")
    print("=" * 60)
    
    # 创建会话管理器
    manager = SessionManager()
    
    # 创建新会话
    session = manager.create_session(
        prompt="分析代码仓库",
        context={"workspace": "/home/user/project", "task": "code_review"}
    )
    print(f"\n创建会话: {session.session_id}")
    
    # 添加对话历史
    session.add_history("user", "请分析这个文件")
    session.add_history("assistant", "好的，我来分析...")
    
    # 记录工具使用
    session.add_tool_usage("read_file")
    session.add_tool_usage("search_content")
    
    # 保存会话
    path = manager.save_session(session)
    print(f"会话已保存: {path}")
    
    # 加载会话
    loaded = manager.load_session(session.session_id)
    print(f"加载会话: {loaded.session_id}")
    print(f"   历史记录数: {len(loaded.history)}")
    print(f"   使用工具: {', '.join(loaded.tools_used)}")
    
    # 列出所有会话
    sessions = manager.list_sessions()
    print(f"\n所有会话 ({len(sessions)} 个):")
    for sid, created_at in sessions:
        print(f"   - {sid}: {created_at}")


def demo_command_router():
    """演示命令路由器"""
    print("\n" + "=" * 60)
    print("演示 4: 命令路由器 (CommandRouter)")
    print("=" * 60)
    
    # 创建命令路由器
    router = CommandRouter()
    router.bind_help_command()
    
    # 注册自定义命令
    def status_handler(args: str, context: dict):
        return "系统状态: 正常运行"
    
    router.register_simple(
        name="my_status",
        description="显示我的系统状态",
        handler=status_handler
    )
    
    print("\n可用命令:")
    print(router.render_help())
    
    # 测试命令路由
    test_commands = ["/help", "/status", "/unknown"]
    print("\n命令路由测试:")
    for cmd_text in test_commands:
        is_cmd, result = router.route_prompt(cmd_text)
        if is_cmd and result:
            status = "OK" if result.handled else "FAIL"
            print(f"  {cmd_text}: {status} - {result.message}")


def demo_integration():
    """演示集成使用"""
    print("\n" + "=" * 60)
    print("演示 5: 完整集成示例")
    print("=" * 60)
    
    # 初始化所有组件
    registry = ToolRegistry()
    session_mgr = SessionManager()
    permissions = PermissionContext(level=PermissionLevel.WORKSPACE_WRITE)
    router = CommandRouter()
    router.bind_help_command()
    
    # 创建工作流
    print("\n启动 Agent 工作流...")
    
    # 1. 创建会话
    session = session_mgr.create_session(
        prompt="分析项目代码",
        context={"workspace": str(Path.cwd())}
    )
    print(f"  会话ID: {session.session_id}")
    
    # 2. 处理用户输入
    user_input = "/tools"
    
    # 3. 命令路由
    is_cmd, result = router.route_prompt(user_input)
    if is_cmd:
        print(f"  识别为命令: {result.name if result else 'unknown'}")
        session.add_history("user", user_input)
    else:
        # 4. 工具路由
        matches = registry.route_prompt(user_input)
        print(f"  工具匹配: {len(matches)} 个")
        for tool, score in matches[:3]:
            print(f"    - {tool.name} ({score})")
    
    # 5. 权限检查
    allowed, reason = permissions.can_use_tool("execute_command")
    print(f"  权限检查 execute_command: {'允许' if allowed else '拒绝'}")
    
    # 6. 保存会话
    session.add_history("assistant", "任务已完成")
    session_mgr.save_session(session)
    print(f"  会话已保存")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Agent Core - 基于 Claude Code 架构的改进实现")
    print("=" * 60)
    
    demo_tool_registry()
    demo_permission_context()
    demo_session_manager()
    demo_command_router()
    demo_integration()
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)
    print("\n核心改进已应用到实际工作中:")
    print("  1. 工具注册表模式 - 动态发现和路由工具")
    print("  2. 权限分层系统 - 三级权限控制")
    print("  3. 会话持久化 - 保存和恢复工作状态")
    print("  4. 命令路由器 - 支持 /command 风格交互")
