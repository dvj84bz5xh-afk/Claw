#!/usr/bin/env python3
"""
Team Registry - 多代理协调系统
支持多代理团队协作、消息广播、任务分配

灵感来源: Claw Code 的多代理协调机制
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum, auto
from datetime import datetime
import time
import json
import threading
import uuid
from pathlib import Path


class AgentStatus(Enum):
    """代理状态"""
    IDLE = "idle"           # 空闲
    BUSY = "busy"           # 忙碌
    OFFLINE = "offline"     # 离线
    ERROR = "error"         # 错误


class MessageType(Enum):
    """消息类型"""
    TASK = "task"           # 任务分配
    RESULT = "result"       # 结果返回
    BROADCAST = "broadcast" # 广播
    DIRECT = "direct"       # 直接消息
    HEARTBEAT = "heartbeat" # 心跳
    CONTROL = "control"     # 控制命令


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Agent:
    """代理定义"""
    agent_id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "current_task": self.current_task,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata
        }
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.status == AgentStatus.IDLE


@dataclass
class Message:
    """消息定义"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    msg_type: MessageType = MessageType.BROADCAST
    sender: str = "system"
    target: Optional[str] = None  # None表示广播
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "type": self.msg_type.value,
            "sender": self.sender,
            "target": self.target,
            "content": self.content,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "priority": self.priority
        }


@dataclass
class TeamTask:
    """团队任务"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    required_capabilities: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, assigned, running, completed, failed
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他任务ID
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "required_capabilities": self.required_capabilities,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "dependencies": self.dependencies
        }


class TeamRegistry:
    """团队注册表 - 管理多代理团队"""
    
    def __init__(self, team_name: str = "default"):
        self.team_name = team_name
        self.agents: Dict[str, Agent] = {}
        self.messages: List[Message] = []
        self.tasks: Dict[str, TeamTask] = {}
        self._lock = threading.RLock()
        
        # 消息处理器
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        
        # 任务分配策略
        self.task_assignment_strategy: str = "capability_match"  # 或 "round_robin", "load_balance"
        
        # 心跳检查
        self.heartbeat_timeout: float = 60.0
        self._heartbeat_timer: Optional[threading.Timer] = None
        self._start_heartbeat_check()
    
    # ========== 代理管理 ==========
    
    def register_agent(self, name: str, capabilities: List[str],
                       agent_id: Optional[str] = None) -> Agent:
        """注册代理"""
        with self._lock:
            agent = Agent(
                agent_id=agent_id or str(uuid.uuid4())[:8],
                name=name,
                capabilities=capabilities
            )
            self.agents[agent.agent_id] = agent
            return agent
    
    def unregister_agent(self, agent_id: str):
        """注销代理"""
        with self._lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
    
    def update_agent_status(self, agent_id: str, status: AgentStatus,
                           current_task: Optional[str] = None):
        """更新代理状态"""
        with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].status = status
                self.agents[agent_id].current_task = current_task
                self.agents[agent_id].last_heartbeat = time.time()
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取代理"""
        return self.agents.get(agent_id)
    
    def get_available_agents(self) -> List[Agent]:
        """获取可用代理"""
        with self._lock:
            return [a for a in self.agents.values() if a.is_available()]
    
    def get_agents_by_capability(self, capability: str) -> List[Agent]:
        """按能力筛选代理"""
        with self._lock:
            return [
                a for a in self.agents.values()
                if capability in a.capabilities
            ]
    
    # ========== 消息系统 ==========
    
    def send_message(self, msg_type: MessageType, sender: str,
                    content: Dict[str, Any], target: Optional[str] = None,
                    priority: int = 0) -> Message:
        """发送消息"""
        with self._lock:
            message = Message(
                msg_type=msg_type,
                sender=sender,
                target=target,
                content=content,
                priority=priority
            )
            self.messages.append(message)
            
            # 执行消息处理器
            handlers = self.message_handlers.get(msg_type, [])
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Message handler error: {e}")
            
            return message
    
    def broadcast(self, sender: str, content: Dict[str, Any],
                  priority: int = 0) -> Message:
        """广播消息"""
        return self.send_message(
            MessageType.BROADCAST, sender, content, None, priority
        )
    
    def send_direct(self, sender: str, target: str, content: Dict[str, Any],
                   priority: int = 0) -> Message:
        """发送直接消息"""
        return self.send_message(
            MessageType.DIRECT, sender, content, target, priority
        )
    
    def register_message_handler(self, msg_type: MessageType, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[msg_type].append(handler)
    
    def get_messages_for(self, agent_id: str, 
                        since: Optional[float] = None) -> List[Message]:
        """获取代理的消息"""
        with self._lock:
            return [
                m for m in self.messages
                if (m.target is None or m.target == agent_id)  # 广播或指定
                and m.sender != agent_id  # 不是发送者
                and (since is None or m.timestamp > since)
            ]
    
    # ========== 任务系统 ==========
    
    def create_task(self, name: str, description: str,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   required_capabilities: Optional[List[str]] = None,
                   dependencies: Optional[List[str]] = None) -> TeamTask:
        """创建任务"""
        with self._lock:
            task = TeamTask(
                name=name,
                description=description,
                priority=priority,
                required_capabilities=required_capabilities or [],
                dependencies=dependencies or []
            )
            self.tasks[task.task_id] = task
            return task
    
    def assign_task(self, task_id: str, agent_id: Optional[str] = None) -> bool:
        """分配任务"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            # 检查依赖
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    if self.tasks[dep_id].status != "completed":
                        return False
            
            # 自动选择代理
            if agent_id is None:
                candidates = self.get_available_agents()
                if task.required_capabilities:
                    candidates = [
                        a for a in candidates
                        if all(c in a.capabilities for c in task.required_capabilities)
                    ]
                
                if not candidates:
                    return False
                
                # 简单策略：选择第一个
                agent_id = candidates[0].agent_id
            
            # 分配
            task.assigned_to = agent_id
            task.status = "assigned"
            self.agents[agent_id].status = AgentStatus.BUSY
            self.agents[agent_id].current_task = task_id
            
            # 发送任务消息
            self.send_message(
                MessageType.TASK,
                "system",
                {"task": task.to_dict()},
                agent_id,
                priority=task.priority.value
            )
            
            return True
    
    def start_task(self, task_id: str):
        """开始任务"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = "running"
                self.tasks[task_id].started_at = time.time()
    
    def complete_task(self, task_id: str, result: Any = None):
        """完成任务"""
        with self._lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = "completed"
            task.completed_at = time.time()
            task.result = result
            
            # 释放代理
            if task.assigned_to and task.assigned_to in self.agents:
                self.agents[task.assigned_to].status = AgentStatus.IDLE
                self.agents[task.assigned_to].current_task = None
            
            # 发送结果消息
            self.send_message(
                MessageType.RESULT,
                task.assigned_to or "unknown",
                {"task_id": task_id, "result": result},
                priority=task.priority.value
            )
    
    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        with self._lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = "failed"
            task.completed_at = time.time()
            
            # 释放代理
            if task.assigned_to and task.assigned_to in self.agents:
                self.agents[task.assigned_to].status = AgentStatus.ERROR
                self.agents[task.assigned_to].current_task = None
    
    def get_task(self, task_id: str) -> Optional[TeamTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: str) -> List[TeamTask]:
        """按状态获取任务"""
        with self._lock:
            return [t for t in self.tasks.values() if t.status == status]
    
    def get_agent_tasks(self, agent_id: str) -> List[TeamTask]:
        """获取代理的任务"""
        with self._lock:
            return [t for t in self.tasks.values() if t.assigned_to == agent_id]
    
    # ========== 团队协作 ==========
    
    def coordinate(self, task_descriptions: List[Dict]) -> List[str]:
        """协调多个任务"""
        task_ids = []
        
        # 创建所有任务
        for desc in task_descriptions:
            task = self.create_task(
                name=desc["name"],
                description=desc.get("description", ""),
                priority=desc.get("priority", TaskPriority.NORMAL),
                required_capabilities=desc.get("capabilities", []),
                dependencies=desc.get("dependencies", [])
            )
            task_ids.append(task.task_id)
        
        # 分配可执行的任务
        for task_id in task_ids:
            self.assign_task(task_id)
        
        return task_ids
    
    def get_team_status(self) -> Dict:
        """获取团队状态"""
        with self._lock:
            return {
                "team_name": self.team_name,
                "agents": {
                    agent_id: agent.to_dict()
                    for agent_id, agent in self.agents.items()
                },
                "tasks": {
                    task_id: task.to_dict()
                    for task_id, task in self.tasks.items()
                },
                "pending_tasks": len(self.get_tasks_by_status("pending")),
                "running_tasks": len(self.get_tasks_by_status("running")),
                "completed_tasks": len(self.get_tasks_by_status("completed")),
                "message_count": len(self.messages),
                "timestamp": time.time()
            }
    
    # ========== 心跳检查 ==========
    
    def _start_heartbeat_check(self):
        """启动心跳检查"""
        def check_and_reschedule():
            self._check_heartbeats()
            self._start_heartbeat_check()
        
        self._heartbeat_timer = threading.Timer(30.0, check_and_reschedule)
        self._heartbeat_timer.daemon = True
        self._heartbeat_timer.start()
    
    def _check_heartbeats(self):
        """检查心跳"""
        now = time.time()
        with self._lock:
            for agent in self.agents.values():
                if now - agent.last_heartbeat > self.heartbeat_timeout:
                    if agent.status != AgentStatus.OFFLINE:
                        agent.status = AgentStatus.OFFLINE
                        print(f"Agent {agent.name} marked offline (no heartbeat)")
    
    def send_heartbeat(self, agent_id: str):
        """发送心跳"""
        self.update_agent_status(agent_id, AgentStatus.IDLE)
    
    # ========== 持久化 ==========
    
    def save_state(self, filepath: Optional[str] = None):
        """保存状态"""
        filepath = filepath or f"team_{self.team_name}_state.json"
        state = self.get_team_status()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self, filepath: str):
        """加载状态"""
        with open(filepath, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # 恢复代理
        for agent_id, agent_data in state.get("agents", {}).items():
            agent = Agent(
                agent_id=agent_data["agent_id"],
                name=agent_data["name"],
                capabilities=agent_data.get("capabilities", []),
                status=AgentStatus(agent_data.get("status", "idle"))
            )
            self.agents[agent_id] = agent
    
    def close(self):
        """关闭"""
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()


# 便捷函数
def create_research_team() -> TeamRegistry:
    """创建研究团队"""
    team = TeamRegistry("research")
    
    # 注册研究代理
    team.register_agent("researcher_1", ["web_search", "analysis"])
    team.register_agent("researcher_2", ["web_search", "analysis"])
    team.register_agent("writer", ["writing", "summarization"])
    team.register_agent("reviewer", ["review", "qa"])
    
    return team


def create_dev_team() -> TeamRegistry:
    """创建开发团队"""
    team = TeamRegistry("development")
    
    # 注册开发代理
    team.register_agent("frontend_dev", ["frontend", "ui", "react"])
    team.register_agent("backend_dev", ["backend", "api", "database"])
    team.register_agent("tester", ["testing", "qa", "automation"])
    team.register_agent("devops", ["deployment", "ci_cd", "monitoring"])
    
    return team


# 测试代码
if __name__ == "__main__":
    print("Team Registry Test")
    print("=" * 60)
    
    # 创建团队
    team = create_research_team()
    
    print(f"\nRegistered {len(team.agents)} agents:")
    for agent in team.agents.values():
        print(f"  - {agent.name}: {agent.capabilities}")
    
    # 创建任务
    task1 = team.create_task(
        name="Research topic A",
        description="Search for information about topic A",
        required_capabilities=["web_search"],
        priority=TaskPriority.HIGH
    )
    
    task2 = team.create_task(
        name="Write report",
        description="Write a report based on research",
        required_capabilities=["writing"],
        dependencies=[task1.task_id]
    )
    
    print(f"\nCreated tasks: {task1.task_id}, {task2.task_id}")
    
    # 分配任务
    assigned = team.assign_task(task1.task_id)
    print(f"Task 1 assigned: {assigned}")
    
    # 发送消息
    msg = team.broadcast("system", {"type": "test", "data": "hello"})
    print(f"\nBroadcast message: {msg.message_id}")
    
    # 获取状态
    status = team.get_team_status()
    print(f"\nTeam status:")
    print(f"  Pending tasks: {status['pending_tasks']}")
    print(f"  Running tasks: {status['running_tasks']}")
    print(f"  Message count: {status['message_count']}")
    
    # 保存状态
    team.save_state("test_team_state.json")
    print("\nState saved to test_team_state.json")
    
    team.close()
    print("\n" + "=" * 60)
    print("Team Registry module ready!")
