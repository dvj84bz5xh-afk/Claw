#!/usr/bin/env python3
"""
Hermes Integration - Hermes Agent 功能集成
将Hermes Agent的核心特性集成到现有系统中

功能：
1. 记忆系统集成 - 增强的记忆管理和检索
2. 技能自动创建 - 解决方案自动转为技能
3. 多智能体协作 - 优化的子智能体通信
4. 定时任务调度 - 自动化的定时任务
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import uuid

# 导入现有模块
try:
    from memory_enhancement import MemoryManager, MemoryItem, MemoryType
except ImportError:
    print("[警告] 记忆增强模块不可用，创建空实现")
    class MemoryManager:
        def __init__(self, *args, **kwargs):
            pass
    
    class MemoryItem:
        pass
    
    class MemoryType(Enum):
        FACT = "fact"

try:
    from skill_auto_creator import SkillAutoCreator
except ImportError:
    print("[警告] 技能自动创建器不可用，创建空实现")
    class SkillAutoCreator:
        def __init__(self, *args, **kwargs):
            pass

try:
    from multi_solution_generator import SolutionCandidate, MultiSolutionGenerator
except ImportError:
    print("[警告] 多方案生成器不可用，创建空实现")
    class SolutionCandidate:
        pass
    
    class MultiSolutionGenerator:
        pass

try:
    from git_multi_solution_integration import GitMultiSolutionIntegration
except ImportError:
    print("[警告] Git多方案集成不可用，创建空实现")
    class GitMultiSolutionIntegration:
        pass

class AgentRole(Enum):
    """智能体角色"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    ANALYZER = "analyzer"
    COORDINATOR = "coordinator"

class MessageType(Enum):
    """消息类型"""
    TASK_ASSIGNMENT = "task_assignment"
    RESULT_REPORT = "result_report"
    STATUS_UPDATE = "status_update"
    REQUEST_HELP = "request_help"
    SHARE_KNOWLEDGE = "share_knowledge"
    COMPLETE = "complete"

@dataclass
class AgentMessage:
    """智能体消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.TASK_ASSIGNMENT
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1-5，越高越重要
    requires_ack: bool = False
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "requires_ack": self.requires_ack,
            "acknowledged": self.acknowledged
        }

class AgentCommunicationBus:
    """智能体通信总线"""
    
    def __init__(self):
        self.message_queue = queue.Queue()
        self.agents = {}  # agent_id -> agent_info
        self.message_history: List[AgentMessage] = []
        self.callbacks = {}  # message_type -> [callback]
        
    def register_agent(self, agent_id: str, agent_name: str, agent_role: AgentRole):
        """注册智能体"""
        self.agents[agent_id] = {
            "name": agent_name,
            "role": agent_role,
            "registered_at": datetime.now(),
            "last_activity": datetime.now(),
            "status": "active"
        }
    
    def send_message(self, sender: str, recipient: str, message_type: MessageType, content: Dict):
        """发送消息"""
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            priority=3
        )
        
        self.message_queue.put(message)
        self.message_history.append(message)
        
        # 触发回调
        if message_type in self.callbacks:
            for callback in self.callbacks[message_type]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"[错误] 消息回调失败: {e}")
        
        return message.id
    
    def broadcast_message(self, sender: str, message_type: MessageType, content: Dict):
        """广播消息到所有智能体"""
        message_ids = []
        for agent_id in self.agents:
            if agent_id != sender:  # 不发送给自己
                msg_id = self.send_message(sender, agent_id, message_type, content)
                message_ids.append(msg_id)
        return message_ids
    
    def receive_messages(self, agent_id: str, max_messages: int = 10) -> List[AgentMessage]:
        """接收智能体的消息"""
        messages = []
        temp_queue = []
        
        # 从队列中取出消息
        while not self.message_queue.empty() and len(messages) < max_messages:
            try:
                message = self.message_queue.get_nowait()
                if message.recipient == agent_id or message.recipient == "all":
                    messages.append(message)
                else:
                    temp_queue.append(message)
            except queue.Empty:
                break
        
        # 将非目标消息放回队列
        for message in temp_queue:
            self.message_queue.put(message)
        
        # 更新智能体活动时间
        if agent_id in self.agents:
            self.agents[agent_id]["last_activity"] = datetime.now()
        
        return messages
    
    def acknowledge_message(self, message_id: str):
        """确认消息接收"""
        for message in self.message_history:
            if message.id == message_id:
                message.acknowledged = True
                break
    
    def register_callback(self, message_type: MessageType, callback: Callable):
        """注册消息回调"""
        if message_type not in self.callbacks:
            self.callbacks[message_type] = []
        self.callbacks[message_type].append(callback)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        status = {
            "total_agents": len(self.agents),
            "queued_messages": self.message_queue.qsize(),
            "total_messages": len(self.message_history),
            "agents": {}
        }
        
        for agent_id, info in self.agents.items():
            status["agents"][agent_id] = info
        
        return status

class HermesIntegration:
    """Hermes Agent功能集成主类"""
    
    def __init__(self):
        # 初始化组件
        self.memory_manager = MemoryManager(memory_dir=".workbuddy/hermes_memory")
        self.skill_creator = SkillAutoCreator(skills_dir=".workbuddy/hermes_skills")
        self.communication_bus = AgentCommunicationBus()
        
        # 定时任务调度器
        self.scheduled_tasks = []
        self.task_thread = None
        self.running = False
        
        # 注册自身智能体
        self.agent_id = "hermes_integration"
        self.communication_bus.register_agent(
            self.agent_id,
            "HermesIntegration",
            AgentRole.COORDINATOR
        )
        
        # 设置消息回调
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """设置消息回调"""
        # 任务完成回调：自动创建技能
        self.communication_bus.register_callback(
            MessageType.RESULT_REPORT,
            self._handle_result_report
        )
        
        # 知识分享回调：存储到记忆
        self.communication_bus.register_callback(
            MessageType.SHARE_KNOWLEDGE,
            self._handle_share_knowledge
        )
    
    def _handle_result_report(self, message: AgentMessage):
        """处理结果报告：自动创建技能"""
        try:
            if "solutions" in message.content:
                solutions_data = message.content["solutions"]
                if isinstance(solutions_data, list) and solutions_data:
                    # 创建技能
                    for solution_data in solutions_data:
                        try:
                            # 转换为SolutionCandidate（简化版）
                            solution = SolutionCandidate(
                                id=solution_data.get("id", str(uuid.uuid4())),
                                title=solution_data.get("title", "未知解决方案"),
                                description=solution_data.get("description", ""),
                                type=solution_data.get("type", "rule_based"),
                                # 其他字段需要根据实际数据结构处理
                            )
                            
                            skill_file = self.skill_creator.create_skill_from_solution(solution)
                            print(f"[Hermes] 自动创建技能: {skill_file}")
                        except Exception as e:
                            print(f"[Hermes] 技能创建失败: {e}")
        except Exception as e:
            print(f"[Hermes] 处理结果报告失败: {e}")
    
    def _handle_share_knowledge(self, message: AgentMessage):
        """处理知识分享：存储到记忆"""
        try:
            if "knowledge" in message.content:
                knowledge = message.content["knowledge"]
                
                memory = MemoryItem(
                    content=str(knowledge),
                    memory_type=MemoryType.FACT,
                    tags=["shared_knowledge", message.sender],
                    source=f"agent_{message.sender}"
                )
                
                self.memory_manager.save_memory(memory)
                print(f"[Hermes] 知识已存储到记忆: {len(str(knowledge))} 字符")
        except Exception as e:
            print(f"[Hermes] 处理知识分享失败: {e}")
    
    def integrate_with_git_system(self, git_integration: GitMultiSolutionIntegration):
        """与Git系统集成"""
        print(f"[Hermes] 正在集成Git系统...")
        
        # 创建Git解决方案技能生成器
        git_skill_creator = GitSkillGenerator(self.skill_creator, git_integration)
        
        # 注册Git相关回调
        self.communication_bus.register_callback(
            MessageType.TASK_ASSIGNMENT,
            lambda msg: git_skill_creator.handle_git_task(msg)
        )
        
        return git_skill_creator
    
    def create_multi_agent_team(self, team_config: Dict[str, Any]):
        """创建多智能体团队"""
        print(f"[Hermes] 创建智能体团队: {team_config.get('name', '未命名团队')}")
        
        team = {
            "id": str(uuid.uuid4()),
            "name": team_config.get("name", "default_team"),
            "agents": [],
            "created_at": datetime.now(),
            "communication_bus": self.communication_bus
        }
        
        # 创建团队成员
        for agent_config in team_config.get("agents", []):
            agent_id = self._create_agent(agent_config)
            if agent_id:
                team["agents"].append(agent_id)
        
        return team
    
    def _create_agent(self, agent_config: Dict[str, Any]) -> Optional[str]:
        """创建单个智能体"""
        try:
            agent_id = agent_config.get("id", str(uuid.uuid4()))
            agent_name = agent_config.get("name", f"agent_{agent_id[:8]}")
            agent_role = AgentRole(agent_config.get("role", "executor"))
            
            self.communication_bus.register_agent(agent_id, agent_name, agent_role)
            print(f"[Hermes] 智能体已创建: {agent_name} ({agent_role.value})")
            
            return agent_id
        except Exception as e:
            print(f"[Hermes] 创建智能体失败: {e}")
            return None
    
    def start_task_scheduler(self):
        """启动定时任务调度器"""
        if self.task_thread and self.task_thread.is_alive():
            print("[Hermes] 任务调度器已在运行")
            return
        
        self.running = True
        self.task_thread = threading.Thread(target=self._scheduler_loop)
        self.task_thread.daemon = True
        self.task_thread.start()
        
        print("[Hermes] 定时任务调度器已启动")
    
    def stop_task_scheduler(self):
        """停止定时任务调度器"""
        self.running = False
        if self.task_thread:
            self.task_thread.join(timeout=5)
        print("[Hermes] 定时任务调度器已停止")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            current_time = datetime.now()
            
            # 检查并执行任务
            for task in self.scheduled_tasks[:]:
                if task.get("next_run") and current_time >= task["next_run"]:
                    self._execute_scheduled_task(task)
            
            # 休眠
            asyncio.sleep(60)  # 每分钟检查一次
    
    def _execute_scheduled_task(self, task: Dict[str, Any]):
        """执行定时任务"""
        try:
            task_type = task.get("type", "unknown")
            print(f"[Hermes] 执行定时任务: {task_type}")
            
            # 发送任务消息
            self.communication_bus.send_message(
                sender=self.agent_id,
                recipient=task.get("agent", "all"),
                message_type=MessageType.TASK_ASSIGNMENT,
                content={
                    "task_type": task_type,
                    "task_data": task.get("data", {}),
                    "scheduled": True
                }
            )
            
            # 更新下次执行时间
            if task.get("interval_minutes"):
                task["next_run"] = datetime.now() + timedelta(minutes=task["interval_minutes"])
            elif task.get("cron_expression"):
                # 这里可以实现cron表达式解析（简化版）
                pass
        except Exception as e:
            print(f"[Hermes] 执行定时任务失败: {e}")
    
    def schedule_task(self, task_config: Dict[str, Any]):
        """调度定时任务"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            **task_config,
            "created_at": datetime.now(),
            "next_run": task_config.get("start_time", datetime.now())
        }
        
        self.scheduled_tasks.append(task)
        print(f"[Hermes] 定时任务已调度: {task_config.get('type', 'unknown')}")
        return task_id
    
    def get_integration_report(self) -> Dict[str, Any]:
        """获取集成报告"""
        memory_stats = self.memory_manager.get_statistics() if hasattr(self.memory_manager, 'get_statistics') else {}
        agent_status = self.communication_bus.get_agent_status()
        
        # 检查技能目录
        skills_dir = Path(".workbuddy/hermes_skills")
        skill_files = list(skills_dir.glob("*/SKILL.md")) if skills_dir.exists() else []
        
        return {
            "integration": {
                "name": "Hermes Integration",
                "version": "1.0.0",
                "status": "active"
            },
            "components": {
                "memory_system": {
                    "status": "enabled" if hasattr(self.memory_manager, 'save_memory') else "disabled",
                    "stats": memory_stats
                },
                "skill_system": {
                    "status": "enabled" if hasattr(self.skill_creator, 'create_skill_from_solution') else "disabled",
                    "total_skills": len(skill_files)
                },
                "communication_system": {
                    "status": "enabled",
                    "stats": agent_status
                }
            },
            "scheduled_tasks": len(self.scheduled_tasks),
            "total_messages": len(self.communication_bus.message_history)
        }

class GitSkillGenerator:
    """Git技能生成器（专用）"""
    
    def __init__(self, skill_creator: SkillAutoCreator, git_integration: GitMultiSolutionIntegration):
        self.skill_creator = skill_creator
        self.git_integration = git_integration
    
    def handle_git_task(self, message: AgentMessage):
        """处理Git任务"""
        if "git_task" in message.content:
            task_type = message.content["git_task"]
            
            if task_type == "generate_solutions":
                self._generate_git_solutions(message)
            elif task_type == "create_skill_from_context":
                self._create_skill_from_git_context(message)
    
    def _generate_git_solutions(self, message: AgentMessage):
        """生成Git解决方案"""
        try:
            context = message.content.get("context", {})
            problem = message.content.get("problem", "")
            
            # 使用Git集成生成解决方案
            solutions = self.git_integration.generate_solutions_for_context(
                problem=problem,
                context=context,
                num_solutions=3
            )
            
            # 发送结果报告
            self.git_integration.communication_bus.send_message(
                sender="git_skill_generator",
                recipient=message.sender,
                message_type=MessageType.RESULT_REPORT,
                content={
                    "solutions": [s.to_dict() for s in solutions],
                    "context_used": context,
                    "git_state": self.git_integration.get_current_git_state()
                }
            )
        except Exception as e:
            print(f"[GitSkill] 生成解决方案失败: {e}")
    
    def _create_skill_from_git_context(self, message: AgentMessage):
        """从Git上下文创建技能"""
        try:
            git_state = self.git_integration.get_current_git_state()
            skill_name = f"git_state_{git_state.get('branch', 'unknown')}_{datetime.now().strftime('%Y%m%d')}"
            
            # 创建Git状态解决方案
            solution = SolutionCandidate(
                id=str(uuid.uuid4()),
                title=f"Git状态处理: {git_state.get('branch', 'unknown')}",
                description=f"处理当前Git状态: {json.dumps(git_state, indent=2)}",
                type="rule_based",
                risk_level="moderate",
                resource_intensity="light",
                technical_approach="Git状态分析和智能处理",
                key_technologies=["Git", "Python", "Automation"],
                implementation_steps=[
                    "分析Git当前状态",
                    "识别潜在问题和风险",
                    "生成处理建议",
                    "执行智能操作"
                ],
                estimated_time=1,
                estimated_cost=2,
                success_probability=0.9,
                technical_feasibility=0.95,
                business_value=0.8,
                user_experience=0.85,
                tags=["git", "automation", "state_management"],
                source_strategy="git_context_aware"
            )
            
            # 创建技能
            skill_file = self.skill_creator.create_skill_from_solution(solution)
            
            # 发送完成通知
            self.git_integration.communication_bus.send_message(
                sender="git_skill_generator",
                recipient=message.sender,
                message_type=MessageType.COMPLETE,
                content={
                    "skill_created": True,
                    "skill_file": skill_file,
                    "solution_id": solution.id
                }
            )
        except Exception as e:
            print(f"[GitSkill] 创建Git技能失败: {e}")

def demo_hermes_integration():
    """演示Hermes集成功能"""
    print("[启动] Hermes Agent 集成演示")
    
    # 创建集成实例
    hermes = HermesIntegration()
    
    # 获取集成报告
    report = hermes.get_integration_report()
    print(f"[Hermes] 集成报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 创建智能体团队示例
    team_config = {
        "name": "开发团队",
        "agents": [
            {"id": "planner_1", "name": "规划者", "role": AgentRole.PLANNER},
            {"id": "executor_1", "name": "执行者", "role": AgentRole.EXECUTOR},
            {"id": "reviewer_1", "name": "审查者", "role": AgentRole.REVIEWER}
        ]
    }
    
    team = hermes.create_multi_agent_team(team_config)
    print(f"[Hermes] 团队已创建: {team['id']}")
    
    # 发送示例消息
    hermes.communication_bus.send_message(
        sender="planner_1",
        recipient="executor_1",
        message_type=MessageType.TASK_ASSIGNMENT,
        content={"task": "处理Git冲突", "priority": "high"}
    )
    
    # 检查消息队列
    messages = hermes.communication_bus.receive_messages("executor_1")
    print(f"[Hermes] 执行者收到 {len(messages)} 条消息")
    
    # 广播知识分享
    hermes.communication_bus.broadcast_message(
        sender="reviewer_1",
        message_type=MessageType.SHARE_KNOWLEDGE,
        content={"knowledge": "Git最佳实践: 频繁提交，清晰的消息"}
    )
    
    print("[完成] Hermes 集成演示结束")

if __name__ == "__main__":
    demo_hermes_integration()