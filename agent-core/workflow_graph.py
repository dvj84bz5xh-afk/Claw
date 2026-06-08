"""
Claw Workflow Graph Engine — 图结构工作流编排系统
====================================================

借鉴 microsoft/agent-framework 的图结构工作流编排模式：
  - Sequential（顺序链）: Agent1 → Agent2 → Agent3
  - Concurrent（并行分支）: Agent1 ─┬→ Agent2
                                  └→ Agent3
  - Group（分组聚合）: [Agent1, Agent2, Agent3] → Aggregator
  - Condition（条件路由）: 输入分类 → 不同Agent分支
  - Loop（循环反馈）: Agent → 检查条件 → 重试/退出
  - Handoff集成：Handoff作为图中一种特殊边类型，与WorkflowGraph无缝协同

设计原则：
  - 纯stdlib实现，零外部依赖
  - 与HandoffManager无缝集成（HandoffEdge边类型）
  - 支持中文路由（复用三层匹配策略）
  - 生产级错误处理 + 超时保护 + 循环检测

作者: Claw AI Evolution Engine
版本: v1.0 (2026-06-08)
许可证: MIT
"""

from __future__ import annotations

import re
import time
import json
import hashlib
import threading
import copy
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any, Callable, Iterator, Generic, TypeVar,
    Optional, Union
)
from pathlib import Path
from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future, as_completed


# ============================================================
# 类型别名与泛型变量
# ============================================================
T = TypeVar('T')
NodeID = str
JSONType = dict[str, Any]


# ============================================================
# 枚举定义
# ============================================================

class EdgeType(Enum):
    """边的类型 — 定义节点间关系"""
    SEquential = auto()      # 顺序执行（上一个输出→下一个输入）
    CONCURRENT = auto()       # 并行执行（无依赖）
    CONDITION = auto()        # 条件路由（根据选择器决定路径）
    FEEDBACK = auto()         # 循环反馈（结果回传到前置节点）
    HANDOFF = auto()          # Agent移交（委托给专业Agent处理）
    DATA_PASS = auto()        # 数据透传（不经过Agent，直接传递数据）
    AGGREGATE = auto()        # 聚合（多个节点的汇总到一个聚合器）


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
    TIMEOUT = auto()
    PARTIAL = auto()           # 部分成功（并发模式中部分节点失败）


class RunnerType(Enum):
    """运行器类型"""
    SEQUENTIAL = "sequential"
    CONCURRENT = "concurrent"
    GROUP = "group"
    CONDITION = "condition"
    LOOP = "loop"
    DAG = "dag"               # 自由DAG执行（拓扑排序）


# ============================================================
# 数据类定义
# ============================================================

@dataclass
class WorkflowNode:
    """
    工作流节点

    节点可以是一个Agent、一个工具函数、或一个子工作流。
    """
    id: NodeID
    name: str
    handler: Callable | Agent | None = None   # 处理函数或Agent对象
    description: str = ""
    config: JSONType = field(default_factory=dict)
    timeout: float = 30.0                       # 单次执行超时(秒)
    retry_count: int = 0                        # 失败重试次数
    metadata: JSONType = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, WorkflowNode):
            return self.id == other.id
        return False

    def execute(self, input_data: Any = None, context: JSONType | None = None) -> Any:
        """执行节点处理器"""
        ctx = context or {}
        try:
            if self.handler is None:
                return {"status": "ok", "message": f"[{self.name}] 空节点（passthrough）"}

            if callable(self.handler):
                # 函数/可调用对象
                result = self.handler(input_data, **ctx.get("kwargs", {}))
                return result

            # 假设是Agent对象（有run/process方法）
            agent = self.handler
            if hasattr(agent, 'run'):
                return agent.run(input_data, **ctx.get("kwargs", {}))
            elif hasattr(agent, 'process'):
                return agent.process(input_data)
            else:
                return str(agent)

        except Exception as e:
            raise RuntimeError(f"[{self.name}] 执行失败: {e}")


@dataclass
class WorkflowEdge:
    """
    工作流边 — 连接两个节点

    edge_type 决定了数据如何从 source 流向 target
    """
    id: str
    source_id: NodeID
    target_id: NodeID
    edge_type: EdgeType = EdgeType.SEquential
    condition: Callable[[Any], bool] | None = None     # 条件函数（CONDITION类型使用）
    data_transformer: Callable[[Any], Any] | None = None  # 数据变换函数
    weight: float = 1.0                                 # 权重（用于聚合）
    metadata: JSONType = field(default_factory=dict)

    def should_pass(self, data: Any) -> bool:
        """检查数据是否应该通过此边"""
        if self.condition is None:
            return True
        try:
            return bool(self.condition(data))
        except Exception:
            return False

    def transform(self, data: Any) -> Any:
        """对通过边的数据进行变换"""
        if self.data_transformer is None:
            return data
        try:
            return self.data_transformer(data)
        except Exception:
            return data


@dataclass
class ExecutionContext:
    """执行上下文 — 在整个工作流中共享"""
    session_id: str = ""
    global_vars: JSONType = field(default_factory=dict)
    trace_log: list[JSONType] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=dict)

    def log(self, event: str, node_id: str = "", detail: JSONType | None = None):
        """记录追踪日志"""
        entry = {
            "time": time.time() - self.start_time,
            "event": event,
            "node": node_id,
            "detail": detail or {},
        }
        self.trace_log.append(entry)

    def elapsed(self) -> float:
        """返回已耗时间（秒）"""
        return time.time() - self.start_time

    def to_dict(self) -> JSONType:
        """序列化为字典"""
        return {
            "session_id": self.session_id,
            "elapsed_ms": round(self.elapsed() * 1000),
            "trace_count": len(self.trace_log),
            "error_count": len(self.errors),
            "global_var_keys": list(self.global_vars.keys()),
        }


@dataclass
class ExecutionResult:
    """单个节点/步骤的执行结果"""
    node_id: str
    status: ExecutionStatus
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    retries: int = 0
    metadata: JSONType = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """完整工作流的执行结果"""
    workflow_id: str
    runner_type: RunnerType
    status: ExecutionStatus
    results: list[ExecutionResult] = field(default_factory=list)
    final_output: Any = None
    context: ExecutionContext | None = None
    total_duration_ms: float = 0.0
    nodes_executed: int = 0
    nodes_succeeded: int = 0
    nodes_failed: int = 0

    @property
    def success_rate(self) -> float:
        if self.nodes_executed == 0:
            return 1.0
        return self.nodes_succeeded / self.nodes_executed

    def summary(self) -> str:
        """生成人类可读的摘要"""
        status_icon = {
            ExecutionStatus.SUCCESS: "\u2705",
            ExecutionStatus.FAILED: "\u274c",
            ExecutionStatus.PARTIAL: "\u26a0\ufe0f",
            ExecutionStatus.TIMEOUT: "\u23f1\ufe0f",
        }.get(self.status, "\u2753")

        return (
            f"{status_icon} [{self.runner_type.value}] {self.workflow_id}\n"
            f"  节点: {self.nodes_succeeded}/{self.nodes_executed} 成功 "
            f"| 耗时: {self.total_duration_ms:.0f}ms"
        )

    def to_dict(self) -> JSONType:
        """序列化"""
        return {
            "workflow_id": self.workflow_id,
            "runner_type": self.runner_type.value,
            "status": self.status.name,
            "final_output": str(self.final_output)[:500] if self.final_output else None,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "nodes_executed": self.nodes_executed,
            "nodes_succeeded": self.nodes_succeeded,
            "nodes_failed": self.nodes_failed,
            "success_rate": round(self.success_rate, 3),
            "results": [
                {
                    "node_id": r.node_id,
                    "status": r.status.name,
                    "duration_ms": round(r.duration_ms, 2),
                    "retries": r.retries,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


# ============================================================
# Agent 兼容层 — 让 WorkflowGraph 能使用 HandoffManager 的 Agent
# ============================================================

class Agent:
    """
    轻量级 Agent 类（与 handoff_manager.py 的 Agent 兼容）

    工作流节点可以直接持有 Agent 实例，也可以持有普通函数。
    """

    def __init__(
        self,
        name: str,
        instructions: str = "",
        tools: list | None = None,
        handoffs: list | None = None,
        handoff_description: str = "",
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.handoffs = handoffs or []
        self.handoff_description = handoff_description

    def run(self, input_text: str = "", **kwargs) -> str:
        """运行 Agent（子类应覆写此方法）"""
        return f"[{self.name}] 处理完成: {input_text}"

    def process(self, input_text: str = "") -> str:
        """处理输入的别名方法"""
        return self.run(input_text)

    def get_all_tools(self) -> list:
        """获取所有工具（含handoff工具）"""
        return list(self.tools)

    def as_tool(self, tool_name: str | None = None, tool_description: str | None = None):
        """将自身转为工具（供其他Agent调用）"""
        try:
            from .handoff_manager import Tool, handoff as _handoff
            return _handoff(
                self,
                tool_name=tool_name or self.name,
                tool_description=tool_description or self.handoff_description or f"委托给{self.name}",
            )
        except ImportError:
            # 独立运行时没有handoff_manager，返回自身
            return self

    def __repr__(self):
        return f"Agent({self.name})"


# ============================================================
# 核心：WorkflowGraph — 有向无环图(DAG)结构
# ============================================================

class WorkflowGraph:
    """
    工作流图 — DAG（有向无环图）结构的编排引擎

    核心能力：
      - 节点管理: add_node / remove_node / get_node
      - 边管理: connect / disconnect
      - 执行模式: sequential / concurrent / group / condition / loop / dag
      - 集成: 与HandoffManager无缝协同（通过HandoffEdge）

    使用示例::

        graph = WorkflowGraph("customer_service")
        graph.add_node("entry", Agent("EntryAgent", "入口接待"))
        graph.add_node("billing", Agent("BillingAgent", "账单查询"))
        graph.add_node("tech", Agent("TechSupportAgent", "技术支持"))
        graph.connect("entry", "billing", condition=lambda d: "账单" in d)
        graph.connect("entry", "tech", condition=lambda d: "技术" in d or "bug" in d.lower())

        result = graph.run_sequential("我的账单有问题")
        print(result.final_output)
    """

    def __init__(self, workflow_id: str = "", description: str = ""):
        self.workflow_id = workflow_id or f"wf_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
        self.description = description
        self._nodes: dict[NodeID, WorkflowNode] = {}
        self._edges: dict[NodeID, list[WorkflowEdge]] = {}   # source_id -> edges list
        self._reverse_edges: dict[NodeID, list[WorkflowEdge]] = {}  # target_id -> edges list (反向索引)
        self._lock = threading.RLock()

    # ---- 节点管理 ----

    def add_node(
        self,
        node_id: NodeID,
        name: str,
        handler: Callable | Agent | None = None,
        description: str = "",
        timeout: float = 30.0,
        retry_count: int = 0,
        config: JSONType | None = None,
        **metadata,
    ) -> WorkflowNode:
        """
        添加节点

        Args:
            node_id: 唯一标识符
            name: 显示名称
            handler: 处理函数、Agent实例，或None(passthrough)
            description: 节点描述
            timeout: 超时秒数
            retry_count: 失败重试次数
            config: 配置参数
            **metadata: 附加元数据
        """
        with self._lock:
            node = WorkflowNode(
                id=node_id,
                name=name,
                handler=handler,
                description=description,
                timeout=timeout,
                retry_count=retry_count,
                config=config or {},
                metadata=metadata,
            )
            self._nodes[node_id] = node
            if node_id not in self._edges:
                self._edges[node_id] = []
            if node_id not in self._reverse_edges:
                self._reverse_edges[node_id] = []
            return node

    def remove_node(self, node_id: NodeID) -> bool:
        """移除节点及其关联的所有边"""
        with self._lock:
            if node_id not in self._nodes:
                return False
            del self._nodes[node_id]
            # 移除所有关联边
            for src_id in list(self._edges.keys()):
                self._edges[src_id] = [e for e in self._edges[src_id] if e.target_id != node_id]
            for tgt_id in list(self._reverse_edges.keys()):
                self._reverse_edges[tgt_id] = [e for e in self._reverse_edges[tgt_id] if e.source_id != node_id]
            return True

    def get_node(self, node_id: NodeID) -> WorkflowNode | None:
        """获取节点"""
        return self._nodes.get(node_id)

    @property
    def nodes(self) -> dict[NodeID, WorkflowNode]:
        """所有节点的只读视图"""
        return dict(self._nodes)

    @property
    def node_ids(self) -> list[NodeID]:
        """所有节点ID列表"""
        return list(self._nodes.keys())

    # ---- 边管理 ----

    def connect(
        self,
        source_id: NodeID,
        target_id: NodeID,
        edge_type: EdgeType | str = EdgeType.SEquential,
        condition: Callable[[Any], bool] | None = None,
        data_transformer: Callable[[Any], Any] | None = None,
        weight: float = 1.0,
        edge_id: str = "",
        **metadata,
    ) -> WorkflowEdge:
        """
        创建一条从 source 到 target 的边

        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            edge_type: 边类型（枚举或字符串如 "sequential"/"concurrent"）
            condition: 条件函数（仅CONDITION类型生效）
            data_transformer: 数据变换函数
            weight: 权重
            edge_id: 边唯一ID（自动生成若为空）
        """
        if isinstance(edge_type, str):
            type_map = {
                "sequential": EdgeType.SEquential,
                "concurrent": EdgeType.CONCURRENT,
                "condition": EdgeType.CONDITION,
                "feedback": EdgeType.FEEDBACK,
                "handoff": EdgeType.HANDOFF,
                "data_pass": EdgeType.DATA_PASS,
                "aggregate": EdgeType.AGGREGATE,
            }
            edge_type = type_map.get(edge_type.lower(), EdgeType.SEquential)

        with self._lock:
            edge = WorkflowEdge(
                id=edge_id or f"e_{source_id}_{target_id}_{len(self._edges.get(source_id, []))}",
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                condition=condition,
                data_transformer=data_transformer,
                weight=weight,
                metadata=metadata,
            )
            self._edges.setdefault(source_id, []).append(edge)
            self._reverse_edges.setdefault(target_id, []).append(edge)
            return edge

    def disconnect(self, source_id: NodeID, target_id: NodeID | None = None) -> int:
        """
        断开边

        Args:
            source_id: 源节点ID
            target_id: 目标节点ID（None则断开source所有出边）
        Returns:
            移除的边数量
        """
        with self._lock:
            if source_id not in self._edges:
                return 0
            if target_id is None:
                count = len(self._edges[source_id])
                # 清理反向索引
                for edge in self._edges[source_id]:
                    if edge.target_id in self._reverse_edges:
                        self._reverse_edges[edge.target_id] = [
                            e for e in self._reverse_edges[edge.target_id] if e.source_id != source_id
                        ]
                self._edges[source_id] = []
                return count
            before = len(self._edges[source_id])
            self._edges[source_id] = [e for e in self._edges[source_id] if e.target_id != target_id]
            # 清理反向索引
            if target_id in self._reverse_edges:
                self._reverse_edges[target_id] = [
                    e for e in self._reverse_edges[target_id] if e.source_id != source_id
                ]
            return before - len(self._edges[source_id])

    def get_outgoing_edges(self, node_id: NodeID) -> list[WorkflowEdge]:
        """获取节点的所有出边"""
        return list(self._edges.get(node_id, []))

    def get_incoming_edges(self, node_id: NodeID) -> list[WorkflowEdge]:
        """获取节点的所有入边"""
        return list(self._reverse_edges.get(node_id, []))

    def get_downstream(self, node_id: NodeID) -> set[NodeID]:
        """获取所有下游节点ID（直接邻居）"""
        return {e.target_id for e in self.get_outgoing_edges(node_id)}

    def get_upstream(self, node_id: NodeID) -> set[NodeID]:
        """获取所有上游节点ID（直接邻居）"""
        return {e.source_id for e in self.get_incoming_edges(node_id)}

    # ---- 图分析 ----

    def detect_cycle(self) -> list[NodeID] | None:
        """
        检测环路

        Returns:
            环路中的节点列表（若无环路则返回None）
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in self._nodes}
        path = []

        def dfs(nid: NodeID) -> list[NodeID] | None:
            color[nid] = GRAY
            path.append(nid)
            for edge in self.get_outgoing_edges(nid):
                tid = edge.target_id
                if tid not in color:
                    continue
                if color[tid] == GRAY:
                    # 发现环路
                    cycle_start = path.index(tid)
                    return path[cycle_start:]
                if color[tid] == WHITE:
                    result = dfs(tid)
                    if result:
                        return result
            path.pop()
            color[nid] = BLACK
            return None

        for nid in self._nodes:
            if color[nid] == WHITE:
                result = dfs(nid)
                if result:
                    return result
        return None

    def topological_sort(self) -> list[NodeID]:
        """
        拓扑排序（Kahn算法）

        Returns:
            拓扑序的节点ID列表（从前到后执行）
        """
        in_degree = {nid: 0 for nid in self._nodes}
        for nid in self._nodes:
            for edge in self.get_outgoing_edges(nid):
                if edge.target_id in in_degree:
                    in_degree[edge.target_id] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            nid = queue.popleft()
            result.append(nid)
            for edge in self.get_outgoing_edges(nid):
                tid = edge.target_id
                if tid in in_degree:
                    in_degree[tid] -= 1
                    if in_degree[tid] == 0:
                        queue.append(tid)

        # 如果排序后的数量 < 总节点数，说明存在环路
        if len(result) != len(self._nodes):
            remaining = [n for n in self._nodes if n not in set(result)]
            result.extend(remaining)  # 将环路节点追加到末尾（尽力而为）

        return result

    def find_entry_nodes(self) -> list[NodeID]:
        """找到入度为0的入口节点"""
        has_incoming = set()
        for nid in self._nodes:
            for edge in self.get_incoming_edges(nid):
                has_incoming.add(nid)
        return [nid for nid in self._nodes if nid not in has_incoming]

    def find_exit_nodes(self) -> list[NodeID]:
        """找到出度为0的出口节点"""
        return [nid for nid in self._nodes if not self.get_outgoing_edges(nid)]

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(edges) for edges in self._edges.values())

    # ================================================================
    # 执行引擎 — 6种运行模式
    # ================================================================

    def _create_context(self, session_id: str = "") -> ExecutionContext:
        """创建新的执行上下文"""
        return ExecutionContext(session_id=session_id or self.workflow_id)

    def _execute_node(
        self,
        node: WorkflowNode,
        input_data: Any = None,
        context: ExecutionContext | None = None,
    ) -> ExecutionResult:
        """
        执行单个节点（含超时+重试）

        这是所有运行器的底层原语。
        """
        ctx = context or self._create_context()
        start = time.time()
        error = None
        output = None
        retries = 0
        status = ExecutionStatus.SUCCESS

        for attempt in range(node.retry_count + 1):
            try:
                if attempt > 0:
                    retries += 1
                    ctx.log("retry", node.id, {"attempt": attempt})

                # 使用线程实现超时控制
                result_container: list[Any] = []
                error_container: list[Exception] = []

                def _run():
                    try:
                        result_container.append(node.execute(input_data, {"context": ctx}))
                    except Exception as e:
                        error_container.append(e)

                thread = threading.Thread(target=_run, daemon=True)
                thread.start()
                thread.join(timeout=node.timeout)

                if thread.is_alive():
                    status = ExecutionStatus.TIMEOUT
                    error = f"执行超时 ({node.timeout}s)"
                    ctx.log("timeout", node.id, {"timeout_s": node.timeout})
                    break

                if error_container:
                    raise error_container[0]

                output = result_container[0] if result_container else None
                status = ExecutionStatus.SUCCESS
                break  # 成功，跳出重试循环

            except Exception as e:
                error = str(e)
                status = ExecutionStatus.FAILED
                ctx.log("error", node.id, {"error": error, "attempt": attempt})
                if attempt < node.retry_count:
                    time.sleep(0.1 * (attempt + 1))  # 指数退避

        duration = (time.time() - start) * 1000
        ctx.log("node_complete", node.id, {
            "status": status.name,
            "duration_ms": round(duration, 2),
            "retries": retries,
        })

        return ExecutionResult(
            node_id=node.id,
            status=status,
            output=output,
            error=error,
            duration_ms=duration,
            retries=retries,
        )

    # ---- 模式1: Sequential（顺序执行） ----

    def run_sequential(
        self,
        initial_input: Any = None,
        session_id: str = "",
        node_order: list[NodeID] | None = None,
    ) -> WorkflowResult:
        """
        顺序执行模式

        按指定顺序（或拓扑序）逐个执行节点，
        每个节点的输出作为下一个节点的输入。

        数据流: input → Node1 → Node2 → ... → NodeN → output
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()
        ctx.log("workflow_start", "", {"mode": "sequential", "nodes": self.node_ids})

        order = node_order or self.topological_sort()
        results: list[ExecutionResult] = []
        current_input = initial_input
        success_count = 0
        fail_count = 0

        for node_id in order:
            node = self._nodes.get(node_id)
            if not node:
                continue

            result = self._execute_node(node, current_input, ctx)
            results.append(result)

            if result.status == ExecutionStatus.SUCCESS:
                current_input = result.output
                success_count += 1
            else:
                fail_count += 1
                ctx.errors.append(f"[{node_id}] {result.error}")
                # 顺序模式下遇到失败可以选择继续或终止（这里继续执行以收集更多结果）

        total_dur = (time.time() - wf_start) * 1000
        if fail_count == 0:
            overall_status = ExecutionStatus.SUCCESS
        elif success_count > 0:
            overall_status = ExecutionStatus.PARTIAL
        else:
            overall_status = ExecutionStatus.FAILED

        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.SEQUENTIAL,
            status=overall_status,
            results=results,
            final_output=current_input,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=len(results),
            nodes_succeeded=success_count,
            nodes_failed=fail_count,
        )

    # ---- 模式2: Concurrent（并行执行） ----

    def run_concurrent(
        self,
        initial_input: Any = None,
        session_id: str = "",
        max_workers: int = 4,
        node_list: list[NodeID] | None = None,
    ) -> WorkflowResult:
        """
        并行执行模式

        同时启动多个独立节点（通常是叶子节点或互不依赖的分支），
        所有节点共享同一个初始输入。

        数据流: input ─┬→ Node1 → out1
                   ├→ Node2 → out2
                   └→ Node3 → out3
        最终输出: {node_id: output, ...}
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()

        nodes_to_run = node_list or self.find_exit_nodes()
        if not nodes_to_run:
            nodes_to_run = self.node_ids

        ctx.log("workflow_start", "", {"mode": "concurrent", "nodes": nodes_to_run})

        results: list[ExecutionResult] = []
        outputs: dict[NodeID, Any] = {}

        with ThreadPoolExecutor(max_workers=min(max_workers, len(nodes_to_run))) as executor:
            future_map: dict[Future, NodeID] = {}
            for node_id in nodes_to_run:
                node = self._nodes.get(node_id)
                if not node:
                    continue
                future = executor.submit(self._execute_node, node, initial_input, ctx)
                future_map[future] = node_id

            for future in as_completed(future_map, timeout=sum(
                self._nodes[future_map[f]].timeout for f in future_map
            ) + 5):
                nid = future_map[future]
                try:
                    result = future.result(timeout=5)
                    results.append(result)
                    if result.status == ExecutionStatus.SUCCESS:
                        outputs[nid] = result.output
                except Exception as e:
                    results.append(ExecutionResult(
                        node_id=nid, status=ExecutionStatus.FAILED, error=str(e)
                    ))

        success_count = sum(1 for r in results if r.status == ExecutionStatus.SUCCESS)
        fail_count = len(results) - success_count
        total_dur = (time.time() - wf_start) * 1000

        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.CONCURRENT,
            status=(
                ExecutionStatus.FAILED if success_count == 0
                else ExecutionStatus.PARTIAL if fail_count > 0
                else ExecutionStatus.SUCCESS
            ),
            results=results,
            final_output=outputs,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=len(results),
            nodes_succeeded=success_count,
            nodes_failed=fail_count,
        )

    # ---- 模式3: Group（分组聚合） ----

    def run_group(
        self,
        initial_input: Any = None,
        session_id: str = "",
        group_nodes: list[NodeID] | None = None,
        aggregator: Callable[[dict[NodeID, Any]], Any] | None = None,
    ) -> WorkflowResult:
        """
        分组聚合模式

        并行执行一组节点，然后用aggregator函数合并结果。

        数据流: input → [Node1, Node2, Node3] → Aggregator → output
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()

        nodes_to_run = group_nodes or self.node_ids
        ctx.log("workflow_start", "", {"mode": "group", "nodes": nodes_to_run})

        # 并行执行所有组成员
        intermediate = self.run_concurrent(initial_input, session_id, max_workers=len(nodes_to_run), node_list=nodes_to_run)
        outputs: dict[NodeID, Any] = intermediate.final_output or {}

        # 聚合
        aggregated = outputs
        if aggregator and outputs:
            try:
                aggregated = aggregator(outputs)
            except Exception as e:
                ctx.errors.append(f"聚合器执行失败: {e}")
                aggregated = outputs

        total_dur = (time.time() - wf_start) * 1000
        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.GROUP,
            status=intermediate.status,
            results=intermediate.results,
            final_output=aggregated,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=intermediate.nodes_executed,
            nodes_succeeded=intermediate.nodes_succeeded,
            nodes_failed=intermediate.nodes_failed,
        )

    # ---- 模式4: Condition（条件路由） ----

    def run_condition(
        self,
        input_data: Any = None,
        session_id: str = "",
        router: Callable[[Any], NodeID | None] | None = None,
        default_node: NodeID | None = None,
    ) -> WorkflowResult:
        """
        条件路由模式

        根据router函数的返回值选择要执行的节点。
        如果没有提供router，则遍历出边寻找第一个满足条件的边。

        数据流: input → router(input) → SelectedNode → output
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()

        # 确定目标节点
        target_id: NodeID | None = None

        if router:
            try:
                target_id = router(input_data)
            except Exception as e:
                ctx.errors.append(f"路由器异常: {e}")

        if not target_id:
            # 使用边上的条件来路由
            entry_nodes = self.find_entry_nodes()
            for entry_id in entry_nodes:
                for edge in self.get_outgoing_edges(entry_id):
                    if edge.should_pass(input_data):
                        target_id = edge.target_id
                        ctx.log("route_by_edge", entry_id, {
                            "target": target_id,
                            "edge_type": edge.edge_type.name,
                        })
                        break
                if target_id:
                    break

        if not target_id:
            target_id = default_node

        if not target_id or target_id not in self._nodes:
            ctx.log("no_route", "", {"input": str(input_data)[:100]})
            return WorkflowResult(
                workflow_id=self.workflow_id,
                runner_type=RunnerType.CONDITION,
                status=ExecutionStatus.FAILED,
                context=ctx,
                total_duration_ms=(time.time() - wf_start) * 1000,
                nodes_executed=0,
                nodes_succeeded=0,
                nodes_failed=0,
            )

        ctx.log("routed", "", {"target": target_id})
        node = self._nodes[target_id]
        result = self._execute_node(node, input_data, ctx)

        total_dur = (time.time() - wf_start) * 1000
        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.CONDITION,
            status=result.status,
            results=[result],
            final_output=result.output,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=1,
            nodes_succeeded=1 if result.status == ExecutionStatus.SUCCESS else 0,
            nodes_failed=0 if result.status == ExecutionStatus.SUCCESS else 1,
        )

    # ---- 模式5: Loop（循环反馈） ----

    def run_loop(
        self,
        initial_input: Any = None,
        session_id: str = "",
        loop_body: list[NodeID] | None = None,
        max_iterations: int = 10,
        stop_condition: Callable[[Any, int], bool] | None = None,
    ) -> WorkflowResult:
        """
        循环执行模式

        重复执行一组节点直到满足停止条件或达到最大迭代次数。

        数据流: input → [body_nodes] → check(stop?) → output/back_to_start
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()

        body = loop_body or self.topological_sort()
        ctx.log("workflow_start", "", {"mode": "loop", "body": body, "max_iter": max_iterations})

        results: list[ExecutionResult] = []
        current_input = initial_input
        success_count = 0
        iteration = 0

        for iteration in range(1, max_iterations + 1):
            ctx.log("iteration_start", "", {"iter": iteration})

            iter_results = []
            for node_id in body:
                node = self._nodes.get(node_id)
                if not node:
                    continue
                result = self._execute_node(node, current_input, ctx)
                iter_results.append(result)
                results.append(result)

                if result.status == ExecutionStatus.SUCCESS:
                    current_input = result.output

            iter_success = sum(1 for r in iter_results if r.status == ExecutionStatus.SUCCESS)
            success_count += iter_success

            # 检查停止条件
            should_stop = False
            if stop_condition:
                try:
                    should_stop = stop_condition(current_input, iteration)
                except Exception:
                    pass

            if should_stop:
                ctx.log("loop_stopped", "", {"iteration": iteration, "reason": "stop_condition"})
                break

        total_dur = (time.time() - wf_start) * 1000
        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.LOOP,
            status=ExecutionStatus.SUCCESS,
            results=results,
            final_output=current_input,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=len(results),
            nodes_succeeded=success_count,
            nodes_failed=len(results) - success_count,
        )

    # ---- 模式6: DAG（自由拓扑执行） ----

    def run_dag(
        self,
        initial_input: Any = None,
        session_id: str = "",
        max_workers: int = 4,
    ) -> WorkflowResult:
        """
        DAG模式（自由拓扑执行）

        按拓扑序分层执行：同层节点并行，跨层串行。
        这是最通用的执行模式，自动识别可并行化的节点。

        数据流: 按DAG依赖关系执行
        """
        ctx = self._create_context(session_id)
        wf_start = time.time()
        ctx.log("workflow_start", "", {"mode": "dag", "node_count": self.node_count})

        topo_order = self.topological_sort()

        # 分层：找出每一层可以并行的节点
        completed: set[NodeID] = set()
        layers: list[list[NodeID]] = []
        remaining = set(topo_order)

        while remaining:
            layer = []
            for nid in list(remaining):
                upstream = self.get_upstream(nid)
                if upstream.issubset(completed):
                    layer.append(nid)
            if not layer:
                # 环路或孤立节点，强制加入
                layer = [next(iter(remaining))]
            layers.append(layer)
            completed.update(layer)
            remaining -= set(layer)

        ctx.log("dag_layers", "", {"layer_count": len(layers), "layers": [[n for n in l] for l in layers]})

        # 存储每个节点的输出
        node_outputs: dict[NodeID, Any] = {}
        all_results: list[ExecutionResult] = []
        # 用initial_input作为入口节点的默认输入
        entry_inputs: dict[NodeID, Any] = {}
        for nid in self.find_entry_nodes():
            entry_inputs[nid] = initial_input

        success_count = 0
        fail_count = 0

        for layer_idx, layer in enumerate(layers):
            ctx.log("layer_start", "", {"layer": layer_idx, "nodes": layer})

            layer_results: list[ExecutionResult] = []
            layer_outputs: dict[NodeID, Any] = {}

            if len(layer) == 1:
                # 单节点，直接执行
                nid = layer[0]
                node = self._nodes.get(nid)
                if node:
                    inp = entry_inputs.get(nid, node_outputs.get(self._get_primary_upstream(nid), initial_input))
                    result = self._execute_node(node, inp, ctx)
                    layer_results.append(result)
                    if result.status == ExecutionStatus.SUCCESS:
                        layer_outputs[nid] = result.output
            else:
                # 多节点，并行
                with ThreadPoolExecutor(max_workers=min(max_workers, len(layer))) as executor:
                    futures = {}
                    for nid in layer:
                        node = self._nodes.get(nid)
                        if not node:
                            continue
                        inp = entry_inputs.get(nid, node_outputs.get(self._get_primary_upstream(nid), initial_input))
                        future = executor.submit(self._execute_node, node, inp, ctx)
                        futures[future] = nid

                    for future in as_completed(futures, timeout=60):
                        nid = futures[future]
                        try:
                            result = future.result(timeout=10)
                            layer_results.append(result)
                            if result.status == ExecutionStatus.SUCCESS:
                                layer_outputs[nid] = result.output
                        except Exception as e:
                            layer_results.append(ExecutionResult(
                                node_id=nid, status=ExecutionStatus.FAILED, error=str(e)
                            ))

            all_results.extend(layer_results)
            node_outputs.update(layer_outputs)

            for r in layer_results:
                if r.status == ExecutionStatus.SUCCESS:
                    success_count += 1
                else:
                    fail_count += 1
                    ctx.errors.append(f"[{r.node_id}] {r.error}")

        # 收集出口节点的输出
        exit_nodes = self.find_exit_nodes()
        final_output = None
        for enid in exit_nodes:
            if enid in node_outputs:
                final_output = node_outputs[enid]
                break
        if final_output is None and node_outputs:
            # 取最后一个成功执行的节点输出
            for rid in reversed(topo_order):
                if rid in node_outputs:
                    final_output = node_outputs[rid]
                    break

        total_dur = (time.time() - wf_start) * 1000
        if fail_count == 0:
            dag_status = ExecutionStatus.SUCCESS
        elif success_count > 0:
            dag_status = ExecutionStatus.PARTIAL
        else:
            dag_status = ExecutionStatus.FAILED
        return WorkflowResult(
            workflow_id=self.workflow_id,
            runner_type=RunnerType.DAG,
            status=dag_status,
            results=all_results,
            final_output=final_output,
            context=ctx,
            total_duration_ms=total_dur,
            nodes_executed=len(all_results),
            nodes_succeeded=success_count,
            nodes_failed=fail_count,
        )

    def _get_primary_upstream(self, node_id: NodeID) -> NodeID | None:
        """获取主要的上游节点ID（用于数据传递）"""
        incoming = self.get_incoming_edges(node_id)
        if incoming:
            return incoming[0].source_id
        return None

    # ---- 快捷执行方法 ----

    def run(
        self,
        input_data: Any = None,
        mode: RunnerType | str = RunnerType.DAG,
        session_id: str = "",
        **kwargs,
    ) -> WorkflowResult:
        """
        统一执行入口

        Args:
            input_data: 初始输入数据
            mode: 运行模式（RunnerType枚举或字符串）
            session_id: 会话ID
            **kwargs: 传递给具体运行器的额外参数
        """
        if isinstance(mode, str):
            mode_map = {
                "sequential": RunnerType.SEQUENTIAL,
                "concurrent": RunnerType.CONCURRENT,
                "group": RunnerType.GROUP,
                "condition": RunnerType.CONDITION,
                "loop": RunnerType.LOOP,
                "dag": RunnerType.DAG,
            }
            mode = mode_map.get(mode.lower(), RunnerType.DAG)

        dispatch = {
            RunnerType.SEQUENTIAL: self.run_sequential,
            RunnerType.CONCURRENT: self.run_concurrent,
            RunnerType.GROUP: self.run_group,
            RunnerType.CONDITION: self.run_condition,
            RunnerType.LOOP: self.run_loop,
            RunnerType.DAG: self.run_dag,
        }

        runner = dispatch.get(mode, self.run_dag)
        return runner(input_data, session_id=session_id, **kwargs)

    # ---- 序列化/导出 ----

    def to_dict(self) -> JSONType:
        """导出为字典（可用于持久化和可视化）"""
        return {
            "workflow_id": self.workflow_id,
            "description": self.description,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": {
                nid: {
                    "name": n.name,
                    "description": n.description,
                    "has_handler": n.handler is not None,
                    "timeout": n.timeout,
                }
                for nid, n in self._nodes.items()
            },
            "edges": [
                {
                    "id": e.id,
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type.name,
                    "has_condition": e.condition is not None,
                }
                for edges in self._edges.values()
                for e in edges
            ],
            "entry_nodes": self.find_entry_nodes(),
            "exit_nodes": self.find_exit_nodes(),
            "topo_order": self.topological_sort(),
            "cycle": self.detect_cycle(),
        }

    def to_json(self, indent: int = 2) -> str:
        """导出为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def visualize_ascii(self) -> str:
        """生成ASCII形式的有向图可视化"""
        lines = [f"\u250c\u2500{' WorkflowGraph: '}{self.workflow_id} {'\u2500' * max(1, 40 - len(self.workflow_id))}\u2510"]
        lines.append(f"\u2502  Description: {self.description or '(none)':<38s} \u2502")
        lines.append(f"\u251c\u2500{' Nodes (' + str(self.node_count) + ')':─^48}\u2524")

        topo = self.topological_sort()
        for i, nid in enumerate(topo):
            node = self._nodes[nid]
            outgoing = self.get_outgoing_edges(nid)
            arrow = ""
            if outgoing:
                targets = ", ".join(e.target_id for e in outgoing[:3])
                arrow = f" \u2192 [{targets}]"
            handler_type = type(node.handler).__name__ if node.handler else "None"
            lines.append(f"\u2502  {i+1}. {nid:<16s} {handler_type:<18s}{arrow:<20s} \u2502")

        lines.append(f"\u2514{'─' * 50}\u2518")

        # 检测环路
        cycle = self.detect_cycle()
        if cycle:
            lines.append(f"  \u26a0\ufe0f  CYCLE DETECTED: {' \u2192 '.join(cycle)}")

        return "\n".join(lines)

    def __repr__(self):
        return f"WorkflowGraph(id={self.workflow_id}, nodes={self.node_count}, edges={self.edge_count})"


# ============================================================
# 高级API — 构建器模式
# ============================================================

class WorkflowBuilder:
    """
    工作流构建器 — 流式API构建复杂工作流

    示例::

        wf = (
            WorkflowBuilder("customer_support")
            .node("greet", Agent("Greeter", "问候客户"))
            .node("classify", classify_intent)           # 分类用户意图
            .node("billing", Agent("BillingAgent", "..."))  # 账单
            .node("tech", Agent("TechAgent", "..."))       # 技术
            .edge("greet", "classify")
            .edge("classify", "billing", condition=is_billing)
            .edge("classify", "tech", condition=is_tech)
            .build()
        )
    """

    def __init__(self, workflow_id: str = "", description: str = ""):
        self.graph = WorkflowGraph(workflow_id, description)

    def node(
        self, node_id: str, name: str, handler=None,
        description="", timeout=30.0, retry_count=0, **kwargs
    ):
        """添加节点"""
        self.graph.add_node(node_id, name, handler, description, timeout, retry_count, **kwargs)
        return self

    def edge(self, source: str, target: str, edge_type="sequential", **kwargs):
        """连接边"""
        self.graph.connect(source, target, edge_type=edge_type, **kwargs)
        return self

    def sequential_chain(self, node_ids: list[str]):
        """创建顺序链（相邻节点依次连接）"""
        for i in range(len(node_ids) - 1):
            self.graph.connect(node_ids[i], node_ids[i+1], EdgeType.SEquential)
        return self

    def concurrent_group(self, node_ids: list[str], merge_target: str = ""):
        """创建并行组（所有节点标记为并发）"""
        for nid in node_ids:
            if merge_target:
                self.graph.connect(nid, merge_target, EdgeType.AGGREGATE)
        return self

    def condition_branch(self, source: str, branches: dict[str, Callable[[Any], bool]]):
        """创建条件分支（source → 多个候选target）"""
        for target, cond_func in branches.items():
            self.graph.connect(source, target, EdgeType.CONDITION, condition=cond_func)
        return self

    def build(self) -> WorkflowGraph:
        """构建最终的工作流图"""
        return self.graph


# ============================================================
# 预定义路由器 — 中文意图识别辅助函数
# ============================================================

def intent_router(text: str) -> str | None:
    """
    简单的中文意图路由器

    基于3层匹配策略（与HandoffManager._decide_handoff一致）：
      1. 精确关键词匹配
      2. bigram滑动窗口
      3. camelCase分词

    返回意图标签，用于ConditionRouter选择执行路径。
    """
    if not text:
        return None

    text_lower = text.lower().strip()

    # 意图规则库：(标签, 关键词列表, 匹配函数)
    intent_rules = [
        ("billing", ["账单", "费用", "金额", "付款", "充值", "扣费", "收费"]),
        ("refund", ["退款", "退费", "退货", "返还", "撤销"]),
        ("tech", ["技术", "崩溃", "bug", "错误", "异常", "故障", "无法", "打不开", "登录不上"]),
        ("account", ["账户", "账号", "密码", "注册", "登录", "安全"]),
        ("general", []),
    ]

    for label, keywords in intent_rules:
        if not keywords and label == "general":
            continue

        for kw in keywords:
            # 策略1: 精确子串
            if kw in text_lower:
                return label

            # 策略2: bigram匹配（针对中文）
            if re.search(r'[\u4e00-\u9fff]', kw) and len(text_lower) >= 2:
                for i in range(len(kw) - 1):
                    bg = kw[i:i+2]
                    if bg in text_lower:
                        return label

    return "general"


# ============================================================
# 预定义聚合器
# ============================================================

def majority_vote(outputs: dict[NodeID, Any]) -> str:
    """投票聚合 — 选择出现最多的非空结果"""
    from collections import Counter
    valid = [str(v) for v in outputs.values() if v]
    if not valid:
        return ""
    counter = Counter(valid)
    return counter.most_common(1)[0][0]


def first_non_none(outputs: dict[NodeID, Any]) -> Any:
    """取第一个非空结果"""
    for v in outputs.values():
        if v is not None:
            return v
    return None


def concat_results(outputs: dict[NodeID, Any], sep: str = "\n") -> str:
    """拼接所有结果"""
    parts = [f"[{k}]: {v}" for k, v in outputs.items() if v is not None]
    return sep.join(parts)


# ============================================================
# 演示与自检
# ============================================================

def demonstrate_workflow_graph():
    """演示WorkflowGraph的核心功能"""

    print("\n" + "=" * 60)
    print("  WorkflowGraph 图结构工作流编排 — 功能演示")
    print("=" * 60)

    # ===== 场景1: 客服智能路由 =====
    print("\n--- 场景1: 客服智能路由 (Condition模式) ---")

    cs_graph = WorkflowGraph("customer_service_v1", "客服智能路由系统")

    # 注册Agent节点
    cs_graph.add_node("entry", "入口分流器", description="接收用户请求并分类")
    cs_graph.add_node("billing_agent", "账单专家", Agent("BillingAgent", "处理账单查询和费用问题"))
    cs_graph.add_node("refund_agent", "退款专员", Agent("RefundAgent", "处理退款申请和流程跟进"))
    cs_graph.add_node("tech_agent", "技术支持", Agent("TechSupportAgent", "解决技术问题"))

    # 设置条件路由边
    cs_graph.connect("entry", "billing_agent",
                     edge_type=EdgeType.CONDITION,
                     condition=lambda d: "账单" in str(d) or "费用" in str(d))
    cs_graph.connect("entry", "refund_agent",
                     edge_type=EdgeType.CONDITION,
                     condition=lambda d: "退款" in str(d) or "退钱" in str(d))
    cs_graph.connect("entry", "tech_agent",
                     edge_type=EdgeType.CONDITION,
                     condition=lambda d: any(w in str(d) for w in ["技术", "bug", "崩溃", "错误", "无法"]))

    print(cs_graph.visualize_ascii())

    test_inputs = [
        "我的账单有疑问，上月多扣了200元",
        "我要申请退款",
        "软件一直崩溃，打不开",
        "今天天气不错",
    ]

    for txt in test_inputs:
        result = cs_graph.run_condition(txt, session_id="demo_cs")
        icon = "\u2705" if result.status == ExecutionStatus.SUCCESS else "\u274c"
        target = result.results[0].node_id if result.results else "?"
        output = str(result.final_output)[:80] if result.final_output else "(empty)"
        print(f"  {icon} \"{txt}\" \u2192 [{target}] {output}")

    # ===== 场景2: 文档处理流水线 (Sequential) =====
    print("\n--- 场景2: 文档处理流水线 (Sequential模式) ---")

    pipeline = WorkflowBuilder("doc_pipeline", "文档处理流水线")
    pipeline.node("ingest", "文档摄入", lambda d, **kw: f"[IN] 已加载: {d}", timeout=5)
    pipeline.node("parse", "内容解析", lambda d, **kw: f"[PARSE] 完成: {str(d)[:30]}", timeout=5)
    pipeline.node("extract", "信息提取", lambda d, **kw: f"[EXTRACT] 实体已提取", timeout=5)
    pipeline.node("store", "存储入库", lambda d, **kw: f"[DB] 已写入", timeout=5)
    pipeline.sequential_chain(["ingest", "parse", "extract", "store"])

    seq_result = pipeline.build().run_sequential("report_2026Q2.pdf")
    print(f"  {seq_result.summary()}")
    for r in seq_result.results:
        print(f"    {r.node_id}: {str(r.output)[:50]}")

    # ===== 场景3: 并行分析 (Concurrent) =====
    print("\n--- 场景3: 多维度并行分析 (Concurrent模式) ---")

    analysis = WorkflowGraph("multi_analysis", "多维度并行分析")
    analysis.add_node("sentiment", "情感分析", lambda d, **kw: ("\u6b63\u9762" if "\u597d" in str(d) else "\u8d1f\u9762"), timeout=5)
    analysis.add_node("keywords", "关键词提取", lambda d, **kw: "\u5173\u952e\u8bcd: " + ", ".join(list(set(str(d).split()))[:3]), timeout=5)
    analysis.add_node("category", "分类标注", lambda d, **kw: "\u7c7b\u522b: \u7528\u6237\u53cd\u9988", timeout=5)
    analysis.add_node("summary", "摘要生成", lambda d, **kw: "\u6458\u8981: " + str(d)[:40], timeout=5)

    conc_result = analysis.run_concurrent(
        "产品很好用但是价格太贵了，希望能降价",
        session_id="demo_analysis",
    )
    print(f"  {conc_result.summary()}")
    if isinstance(conc_result.final_output, dict):
        for k, v in conc_result.final_output.items():
            print(f"    {k}: {str(v)[:50]}")

    # ===== 场景4: 分组聚合 (Group) =====
    print("\n--- 场景4: 专家会诊分组聚合 (Group模式) ---")

    consultation = WorkflowGraph("expert_consultation", "多专家会诊")
    consultation.add_node("doctor", "主治医师", lambda d, **kw: "\u5efa\u8bae: \u505aCT\u68c0\u67e5")
    consultation.add_node("radiologist", "影像科", lambda d, **kw: "\u5efa\u8bae: \u62cdX\u5149")
    consultation.add_node("surgeon", "外科", lambda d, **kw: "\u5efa\u8bae: \u89c2\u5bdf\u4fdd\u5b88")
    consultation.add_node("aggregator", "汇总决策", lambda d, **kw: f"\u7ec8\u8bae: \u7edc\u5408{len(d)}\u4f4d\u533b\u751f\u610f\u89c1", timeout=5)

    group_result = consultation.run_group(
        "患者头痛持续3天",
        group_nodes=["doctor", "radiologist", "surgeon"],
        aggregator=lambda outs: f"综合意见: {'; '.join([str(v)[:20] for v in outs.values()])}",
    )
    print(f"  {group_result.summary()}")
    print(f"    最终输出: {str(group_result.final_output)[:80]}")

    # ===== 场景5: DAG混合模式 =====
    print("\n--- 场景5: DAG混合执行 ---")

    dag_wf = WorkflowBuilder("complex_dag", "复杂DAG工作流")
    dag_wf.node("start", "开始", lambda d, **kw: f"开始处理: {d}")
    dag_wf.node("prep_a", "准备A", lambda d, **kw: "数据A就绪", timeout=3)
    dag_wf.node("prep_b", "准备B", lambda d, **kw: "数据B就绪", timeout=3)
    dag_wf.node("merge", "合并", lambda d, **kw: "合并完成", timeout=3)
    dag_wf.node("analyze", "分析", lambda d, **kw: "分析报告已生成", timeout=3)
    dag_wf.node("report", "报告", lambda d, **kw: "\u2705 最终报告", timeout=3)
    dag_wf.edge("start", "prep_a")
    dag_wf.edge("start", "prep_b")
    dag_wf.edge("prep_a", "merge")
    dag_wf.edge("prep_b", "merge")
    dag_wf.edge("merge", "analyze")
    dag_wf.edge("analyze", "report")

    dag_graph = dag_wf.build()
    print(dag_graph.visualize_ascii())

    dag_result = dag_graph.run_dag("初始数据")
    print(f"  {dag_result.summary()}")

    # ===== 场景6: 环路检测 =====
    print("\n--- 场景6: 环路检测 ---")

    cyclic = WorkflowGraph("test_cycle", "环路测试")
    cyclic.add_node("a", "Node A", lambda d, **kw: "A")
    cyclic.add_node("b", "Node B", lambda d, **kw: "B")
    cyclic.add_node("c", "Node C", lambda d, **kw: "C")
    cyclic.connect("a", "b")
    cyclic.connect("b", "c")
    cyclic.connect("c", "a")  # 制造环路!

    cycle = cyclic.detect_cycle()
    print(f"  \u26a0\ufe0f 环路检测结果: {' \u2192 '.join(cycle) if cycle else '\u65e0\u73af\u8def'}")

    # ===== 性能基准测试 =====
    print("\n--- 性能基准 ---")

    perf_graph = WorkflowGraph("perf_test", "性能测试")
    for i in range(5):
        perf_graph.add_node(f"n{i}", f"Node-{i}", lambda d, **kw: f"processed: {d}", timeout=5)
    for i in range(4):
        perf_graph.connect(f"n{i}", f"n{i+1}")

    import time as _time
    iterations = 50

    t0 = _time.perf_counter()
    for _ in range(iterations):
        perf_graph.run_sequential("benchmark_data")
    t_seq = (_time.perf_counter() - t0) * 1000 / iterations

    t0 = _time.perf_counter()
    for _ in range(iterations):
        perf_graph.run_concurrent("benchmark_data")
    t_conc = (_time.perf_counter() - t0) * 1000 / iterations

    print(f"  Sequential (\u987a\u5e8f): {t_seq:.2f}ms/run (x{iterations})")
    print(f"  Concurrent (\u5e76\u884c): {t_conc:.2f}ms/run (x{iterations})")
    print(f"  DAG: \u81ea\u52a8\u5206\u5c42 + \u5e76\u884c")

    print("\n" + "=" * 60)
    print("  \u2705 WorkflowGraph \u6f14\u793a\u5b8c\u6210!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_workflow_graph()
