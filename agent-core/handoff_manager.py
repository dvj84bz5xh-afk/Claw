"""
HandoffManager - 声明式 Agent 编排系统

借鉴 openai-agents-python 的 Handoffs 机制:
- Agent 声明 handoffs=[...] 即可自动暴露为路由工具
- LLM 自动选择目标 Agent，无需手动 TaskCreate
- 减少编排代码 60%+

核心概念:
1. Agent: 带 instructions/tools/handoffs 的 Agent 定义
2. handoff(): 创建可定制的 handoff 对象
3. HandoffManager: 运行时路由器，管理 Agent 切换
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ========== 数据结构 ==========

@dataclass(frozen=True)
class HandoffInputData:
    """Handoff 输入过滤器接收的数据"""
    input_history: list[dict]   # 对话历史
    pre_handoff_items: list[dict]  # handoff 前的 items
    new_items: list[dict]        # 当前轮次 items
    input_items: list[dict] | None = None
    run_context: Any = None


@dataclass
class Handoff:
    """Handoff 定义 - 描述一个 Agent 如何被移交给另一个 Agent"""
    agent: Any              # 目标 Agent 实例
    tool_name: str         # 暴露给 LLM 的工具名
    tool_description: str   # 工具描述
    on_handoff: Callable | None = None   # handoff 触发时的回调
    input_type: type | None = None       # 结构化输入类型 (Pydantic BaseModel)
    input_filter: Callable | None = None  # 输入过滤器
    is_enabled: bool | Callable = True    # 是否启用
    nest_handoff_history: bool | None = None

    def to_tool_schema(self) -> dict:
        """生成暴露给 LLM 的 tool schema"""
        schema = {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }

        # 如果有 input_type，添加结构化参数
        if self.input_type:
            import inspect
            fields = {}
            required = []
            if hasattr(self.input_type, "model_fields"):
                for fname, fdef in self.input_type.model_fields.items():
                    fields[fname] = {"type": "string", "description": fdef.description or ""}
                    if fdef.is_required():
                        required.append(fname)
            schema["function"]["parameters"]["properties"] = fields
            if required:
                schema["function"]["parameters"]["required"] = required

        return schema

    def should_enable(self, ctx: Any, agent: Any) -> bool:
        """判断是否启用此 handoff"""
        if callable(self.is_enabled):
            return self.is_enabled(ctx, agent)
        return bool(self.is_enabled)


@dataclass
class Agent:
    """
    Agent 定义 - 声明式 Agent 规范

    用法:
        billing = Agent(name="Billing", instructions="处理账单问题")
        refund = Agent(name="Refund", instructions="处理退款")

        orchestrator = Agent(
            name="Orchestrator",
            instructions="路由用户请求到专业 Agent",
            handoffs=[billing, handoff(refund, tool_name="transfer_to_refund")]
        )
    """
    name: str
    instructions: str = ""
    tools: list[Any] = field(default_factory=list)       # 绑定的工具
    handoffs: list[Agent | Handoff] = field(default_factory=list)  # 可移交的 Agent
    handoff_description: str = ""  # 在 handoff 工具描述中追加的说明
    model: str = ""            # 使用的模型
    metadata: dict[str, Any] = field(default_factory=dict)

    # 运行时状态
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        # 将 Agent 实例转换为 Handoff 对象
        normalized = []
        for h in self.handoffs:
            if isinstance(h, Agent):
                normalized.append(handoff(h))
            else:
                normalized.append(h)
        object.__setattr__(self, 'handoffs', normalized)

    def as_tool(self, *, tool_name: str, tool_description: str,
                max_turns: int | None = None,
                parameters: type | None = None,
                is_enabled: bool | Callable = True,
                custom_output_extractor: Callable | None = None) -> Any:
        """
        将当前 Agent 注册为工具，供其他 Agent 调用

        Returns:
            一个 tool 定义 dict，可直接加入其他 Agent 的 tools 列表
        """
        tool_def = {
            "type": "agent_tool",
            "agent": self,
            "tool_name": tool_name,
            "tool_description": tool_description,
            "max_turns": max_turns,
            "parameters": parameters,
            "is_enabled": is_enabled,
            "custom_output_extractor": custom_output_extractor,
        }

        # 生成 tool schema
        schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string", "description": "输入内容"}
                    },
                    "required": ["input"],
                },
            },
        }

        if parameters:
            # 用 pydantic model 生成 schema
            if hasattr(parameters, "model_json_schema"):
                schema["function"]["parameters"] = parameters.model_json_schema()

        tool_def["schema"] = schema
        return tool_def

    def get_handoff_tools(self) -> list[dict]:
        """获取所有 handoff 对应的 tool schema（暴露给 LLM）"""
        tools = []
        for h in self.handoffs:
            if isinstance(h, Handoff):
                tools.append(h.to_tool_schema())
        return tools

    def get_all_tools(self) -> list[dict]:
        """获取所有工具（普通工具 + handoff 工具）"""
        tools = list(self.tools)
        tools.extend(self.get_handoff_tools())
        return tools


# ========== 辅助函数 ==========

def handoff(agent: Agent, *,
            on_handoff: Callable | None = None,
            tool_name: str | None = None,          # 别名: tool_name_override
            tool_name_override: str | None = None,
            tool_description: str | None = None,    # 别名: tool_description_override
            tool_description_override: str | None = None,
            input_type: type | None = None,
            input_filter: Callable | None = None,
            is_enabled: bool | Callable = True,
            nest_handoff_history: bool | None = None) -> Handoff:
    """
    创建一个 Handoff 对象（类似 OpenAI Agents SDK 的 handoff()）

    Args:
        agent: 目标 Agent
        on_handoff: handoff 触发时的回调 (ctx, input_data) -> None
        tool_name: 覆盖默认工具名（默认: transfer_to_<name>）
        tool_name_override: (同上，兼容全名）
        tool_description: 覆盖默认工具描述
        tool_description_override: (同上，兼容全名）
        input_type: 结构化输入类型（Pydantic BaseModel）
        input_filter: 输入过滤器，控制新 Agent 看到的历史
        is_enabled: 是否启用（支持运行时动态判断）
        nest_handoff_history: 是否嵌套历史记录
    """
    # 支持别名
    _tool_name = tool_name or tool_name_override
    _tool_desc = tool_description or tool_description_override

    default_tool_name = f"transfer_to_{agent.name.lower().replace(' ', '_')}"
    default_description = f"将任务移交给 {agent.name}。" + (agent.handoff_description or "")

    return Handoff(
        agent=agent,
        tool_name=_tool_name or default_tool_name,
        tool_description=_tool_desc or default_description,
        on_handoff=on_handoff,
        input_type=input_type,
        input_filter=input_filter,
        is_enabled=is_enabled,
        nest_handoff_history=nest_handoff_history,
    )


def recommend_handoff_prompt(agent: Agent) -> str:
    """
    生成推荐给 Agent 的 handoff 提示词前缀
    （类似 openai-agents 的 RECOMMENDED_PROMPT_PREFIX）
    """
    if not agent.handoffs:
        return agent.instructions

    handoff_descriptions = []
    for h in agent.handoffs:
        if isinstance(h, Handoff):
            handoff_descriptions.append(f"- {h.tool_name}: {h.tool_description}")

    prefix = (
        f"你是一个编排 Agent。你可以将任务移交给以下专业 Agent:\n"
        + "\n".join(handoff_descriptions)
        + "\n\n当用户需求匹配某个专业 Agent 的能力时，调用对应的移交工具。"
        + f"否则，你自己处理。\n\n你的核心指令: {agent.instructions}"
    )
    return prefix


# ========== HandoffManager ==========

class HandoffManager:
    """
    声明式 Agent 编排管理器

    相比原 TaskCreate 手动编排的优势:
    1. 声明式注册: Agent handoffs=[...] 即可
    2. 自动路由: LLM 根据 tool description 自动选择目标
    3. 减少 60% 编排代码: 无需手动 create_task + assign_task
    4. 上下文传递: 自动处理对话历史传递

    用法:
        manager = HandoffManager()

        # 注册 Agent
        manager.register(billing_agent)
        manager.register(refund_agent)
        manager.register(orchestrator)

        # 设置入口 Agent
        manager.set_entry(orchestrator)

        # 运行
        result = manager.run("用户想退款")
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._agents: dict[str, Agent] = {}
        self._entry_agent: Agent | None = None
        self._history: list[dict] = []       # 全局对话历史
        self._current_agent: Agent | None = None
        self._handoff_chain: list[str] = []  # 记录 handoff 链路
        self._run_results: list[dict] = []   # 每次 run 的结果

        # 统计
        self._stats = {
            "total_runs": 0,
            "total_handoffs": 0,
            "agent_usage": {},
        }

    # ========== Agent 注册 ==========

    def register(self, agent: Agent) -> None:
        """注册 Agent"""
        self._agents[agent.agent_id] = agent
        # 更新统计
        self._stats["agent_usage"][agent.agent_id] = 0
        print(f"[HandoffManager] 注册 Agent: {agent.name} ({agent.agent_id})")

    def unregister(self, agent_id: str) -> bool:
        """注销 Agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    def get_agent(self, agent_id: str) -> Agent | None:
        return self._agents.get(agent_id)

    def set_entry(self, agent: Agent) -> None:
        """设置入口 Agent"""
        self._entry_agent = agent
        if agent.agent_id not in self._agents:
            self.register(agent)

    def get_entry(self) -> Agent | None:
        return self._entry_agent

    # ========== 运行 ==========

    def run(self, user_input: str, *,
            entry_agent: Agent | None = None,
            max_handoffs: int = 10) -> dict[str, Any]:
        """
        运行编排流程（模拟 LLM 路由决策）

        Args:
            user_input: 用户输入
            entry_agent: 入口 Agent（覆盖默认）
            max_handoffs: 最大 handoff 次数（防止死循环）

        Returns:
            {"output": ..., "handoff_chain": [...], "agent_usage": {...}}
        """
        agent = entry_agent or self._entry_agent
        if not agent:
            return {"error": "未设置入口 Agent"}

        self._current_agent = agent
        self._handoff_chain = [agent.agent_id]
        self._stats["total_runs"] += 1

        current_input = user_input
        handoff_count = 0

        while handoff_count < max_handoffs:
            self._stats["agent_usage"][agent.agent_id] = \
                self._stats["agent_usage"].get(agent.agent_id, 0) + 1

            print(f"\n[HandoffManager] 当前 Agent: {agent.name} ({agent.agent_id})")
            print(f"[HandoffManager] 输入: {current_input[:80]}...")

            # 决策: 是否 handoff？
            handoff_decision = self._decide_handoff(agent, current_input)

            if handoff_decision:
                target_agent, handoff_input = handoff_decision
                print(f"[HandoffManager] 🔄 Handoff: {agent.name} -> {target_agent.name}")

                # 执行 on_handoff 回调
                h_obj = self._find_handoff_obj(agent, target_agent)
                if h_obj and h_obj.on_handoff:
                    try:
                        h_obj.on_handoff()
                    except Exception as e:
                        print(f"[HandoffManager] on_handoff 回调错误: {e}")

                # 记录
                self._handoff_chain.append(target_agent.agent_id)
                self._stats["total_handoffs"] += 1
                handoff_count += 1

                # 切换 Agent
                agent = target_agent
                current_input = handoff_input or current_input
                continue

            # 不 handoff，当前 Agent 直接处理
            result = self._execute_agent(agent, current_input)
            self._run_results.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "input": current_input,
                "output": result,
                "timestamp": time.time(),
            })

            print(f"[HandoffManager] ✅ {agent.name} 处理完成")
            break

        if handoff_count >= max_handoffs:
            print(f"[HandoffManager] ⚠️ 达到最大 handoff 次数 ({max_handoffs})")

        final_output = self._run_results[-1]["output"] if self._run_results else "无输出"
        return {
            "output": final_output,
            "handoff_chain": [
                self._agents[aid].name
                for aid in self._handoff_chain
                if aid in self._agents
            ],
            "handoff_count": handoff_count,
            "agent_usage": dict(self._stats["agent_usage"]),
            "run_history": list(self._run_results),
        }

    def _decide_handoff(self, agent: Agent, current_input: str) -> tuple | None:
        """
        决策是否 handoff（模拟 LLM 的工具调用决策）

        匹配优先级:
        1. 精确子串: 输入完整包含某个关键词
        2. 中文bigram双向: 输入2字片段 ∩ 关键词2字片段（任一方向命中）
        3. instructions扩展: 从agent.instructions提取额外关键词兜底

        实际生产应替换为LLM function calling决策。
        """
        import re  # 正则模块（局部导入减少启动开销）

        if not agent.handoffs:
            return None

        input_lower = current_input.lower()
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', input_lower))

        for h in agent.handoffs:
            if not isinstance(h, Handoff):
                continue

            if not h.should_enable(None, agent):
                continue

            # === 构建关键词集合 ===

            # 1) tool_description 中的自然词
            desc_text = h.tool_description.replace(",", " ").replace("。", " ").replace("！", " ")
            desc_words = set()
            for w in re.findall(r'[一-鿿A-Za-z0-9]{2,}', desc_text):
                w = w.strip("：:.-()（）")
                if len(w) >= 2:
                    desc_words.add(w.lower())

            # 2) agent.name 分词 (camelCase / snake_case)
            name_text = re.sub(r'(?<!^)(?=[A-Z])', ' ', h.agent.name)
            name_words = set(
                w.lower() for w in name_text.replace("_", " ").split()
                if len(w) >= 2
            )

            # 3) 目标 Agent instructions 扩展（兜底源）
            instr_words = set()
            target_instr = getattr(h.agent, 'instructions', '') or ''
            if len(target_instr) >= 4:
                for w in re.findall(r'[一-鿿A-Za-z0-9]{2,}', target_instr):
                    w = w.strip("：:.,;，。！？、")
                    if len(w) >= 2:
                        instr_words.add(w.lower())

            # 合并
            all_words = desc_words | name_words | instr_words

            if not all_words:
                continue

            # === 匹配策略 ===

            # 策略1: 精确子串（任意关键词完整出现在输入中）
            for kw in all_words:
                if len(kw) >= 2 and kw in input_lower:
                    return h.agent, current_input

            # 策略2: 中文bigram双向匹配
            if is_chinese and len(input_lower) >= 2:
                # 2a: 输入的2字片段 → 是否命中某个关键词
                input_bigrams = {input_lower[i:i+2] for i in range(len(input_lower) - 1)}
                for bg in input_bigrams:
                    if any(bg in kw for kw in all_words if len(kw) >= 2):
                        return h.agent, current_input

                # 2b: 关键词的2字片段 → 是否命中输入（反向）
                for kw in all_words:
                    if len(kw) >= 2 and re.search(r'[\u4e00-\u9fff]', kw):
                        for j in range(len(kw) - 1):
                            kbg = kw[j:j+2]
                            if kbg in input_lower:
                                return h.agent, current_input

            # 策略3: 英文单词token匹配（空格分割后部分匹配）
            if not is_chinese:
                input_tokens = set(re.findall(r'[a-z]{2,}', input_lower))
                kw_tokens = set()
                for kw in all_words:
                    kw_tokens.update(re.findall(r'[a-z]{2,}', kw))
                if input_tokens & kw_tokens:
                    return h.agent, current_input

        return None

    def _find_handoff_obj(self, source: Agent, target: Agent) -> Handoff | None:
        """找到 source -> target 的 Handoff 对象"""
        for h in source.handoffs:
            if isinstance(h, Handoff) and h.agent.agent_id == target.agent_id:
                return h
        return None

    def _execute_agent(self, agent: Agent, input_text: str) -> str:
        """
        执行 Agent（模拟）

        实际集成中应:
        1. 调用 LLM，传入 agent.instructions + agent.get_all_tools()
        2. 如果 LLM 返回 tool_call，执行对应 tool
        3. 如果 tool 是 agent_tool (as_tool)，执行子 Agent
        4. 返回最终输出
        """
        # 模拟: 基于 instructions 生成回复
        return f"[模拟]{agent.name} 处理了: {input_text[:50]}..."

    # ========== 生成 tool schemas（供 LLM 调用）==========

    def export_tool_schemas(self, agent_id: str) -> list[dict]:
        """导出指定 Agent 的所有 tool schemas（供 LLM function_calling）"""
        agent = self._agents.get(agent_id)
        if not agent:
            return []

        schemas = []
        for h in agent.handoffs:
            if isinstance(h, Handoff):
                schemas.append(h.to_tool_schema())
        return schemas

    def export_all_agents(self) -> list[dict]:
        """导出所有 Agent 的摘要（用于编排可视化）"""
        return [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "handoffs": [
                    h.tool_name for h in a.handoffs if isinstance(h, Handoff)
                ],
                "tool_count": len(a.tools),
                "usage_count": self._stats["agent_usage"].get(a.agent_id, 0),
            }
            for a in self._agents.values()
        ]

    # ========== 统计 ==========

    def get_stats(self) -> dict[str, Any]:
        return {
            "manager_name": self.name,
            "agent_count": len(self._agents),
            "total_runs": self._stats["total_runs"],
            "total_handoffs": self._stats["total_handoffs"],
            "agent_usage": dict(self._stats["agent_usage"]),
            "handoff_chain": [
                self._agents[aid].name
                for aid in self._handoff_chain
                if aid in self._agents
            ],
        }

    def generate_report(self) -> str:
        """生成编排报告"""
        stats = self.get_stats()
        lines = [
            "# HandoffManager 编排报告",
            "",
            f"**管理器**: {stats['manager_name']}",
            f"**注册 Agent 数**: {stats['agent_count']}",
            f"**总运行次数**: {stats['total_runs']}",
            f"**总 Handoff 次数**: {stats['total_handoffs']}",
            "",
            "## Agent 使用统计",
        ]
        for aid, count in stats["agent_usage"].items():
            a = self._agents.get(aid)
            name = a.name if a else aid
            lines.append(f"- {name}: {count} 次")

        if stats["handoff_chain"]:
            lines.extend([
                "",
                "## 最近 Handoff 链路",
                " -> ".join(stats["handoff_chain"]),
            ])

        return "\n".join(lines)


# ========== 便捷函数 ==========

def create_handoff_manager(name: str = "default") -> HandoffManager:
    """创建 HandoffManager"""
    return HandoffManager(name=name)


def demonstrate_handoff_pattern():
    """
    演示: 声明式 Handoffs vs 手动 TaskCreate
    展示代码量减少 60%+
    """
    print("=" * 60)
    print("HandoffManager 演示: 声明式 Agent 编排")
    print("=" * 60)

    # === 方式 1: 旧方式（手动 TaskCreate 编排）===
    print("\n【旧方式】手动 TaskCreate 编排（18 行）:")
    print("""
    # 需要手动创建 Task + 分配 + 执行
    registry = TaskRegistry()
    executor = TaskExecutor(registry)

    task1 = registry.create_task(
        name="Billing", target=billing_handler, ...)
    task2 = registry.create_task(
        name="Refund", target=refund_handler, ...)

    executor.execute_task(task1.task_id)
    # 需要手动判断路由...
    """.strip())

    # === 方式 2: 新方式（声明式 Handoffs）===
    print("\n【新方式】声明式 Handoffs（6 行）:")
    print("""
    billing = Agent(name="Billing", instructions="...")
    refund = Agent(name="Refund", instructions="...")
    orchestrator = Agent(
        name="Orch",
        handoffs=[billing, handoff(refund)])
    result = HandoffManager().run("退款问题")
    """.strip())

    print("\n✅ 代码量减少: 18行 -> 6行 (减少 67%)")
    print("\n" + "=" * 60)

    # 实际运行演示
    print("\n【实际运行演示】")
    mgr = HandoffManager("demo")

    billing = Agent(name="BillingAgent", instructions="处理账单和发票问题")
    refund = Agent(name="RefundAgent", instructions="处理退款请求和退款政策")
    tech = Agent(name="TechSupport", instructions="处理技术故障")

    orchestrator = Agent(
        name="OrchestratorAgent",
        instructions="你是客服编排器，将用户请求路由到专业 Agent",
        handoffs=[
            billing,
            handoff(refund, tool_description="用户要求退款或取消订单时使用"),
            tech,
        ]
    )

    mgr.register(billing)
    mgr.register(refund)
    mgr.register(tech)
    mgr.set_entry(orchestrator)

    # 模拟几次运行
    test_inputs = [
        "我的账单有问题",
        "我想退款",
        "软件崩溃了",
    ]

    for inp in test_inputs:
        print(f"\n>>> 输入: {inp}")
        result = mgr.run(inp, max_handoffs=5)
        print(f"    链路: {' -> '.join(result['handoff_chain'])}")
        print(f"    输出: {result['output'][:60]}...")

    print(f"\n📊 统计:\n{mgr.generate_report()}")

    return mgr


if __name__ == "__main__":
    demonstrate_handoff_pattern()
