"""
Phase 3.3: Task Registry System

任务注册、管理和执行系统
- 任务注册和状态管理
- 任务依赖关系
- 任务输出收集
- 任务优先级调度
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from enum import Enum, auto
from datetime import datetime, timedelta
from uuid import uuid4
import threading
import json
from pathlib import Path
import time


class TaskStatus(Enum):
    """任务状态"""
    PENDING = auto()      # 等待中
    RUNNING = auto()      # 运行中
    COMPLETED = auto()    # 已完成
    FAILED = auto()       # 失败
    CANCELLED = auto()    # 已取消
    PAUSED = auto()       # 已暂停


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 0    # 关键
    HIGH = 1        # 高
    NORMAL = 2      # 正常
    LOW = 3         # 低
    BACKGROUND = 4  # 后台


@dataclass
class TaskOutput:
    """任务输出"""
    timestamp: datetime
    content: Any
    output_type: str = "text"  # text, json, binary, error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": str(self.content) if self.content else "",
            "type": self.output_type
        }


@dataclass
class Task:
    """任务定义"""
    # 基本信息
    task_id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    
    # 状态
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    
    # 时间
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 执行
    target: Optional[Callable] = None
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # 输出
    outputs: List[TaskOutput] = field(default_factory=list)
    result: Any = None
    error_message: Optional[str] = None
    
    # 依赖
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # 进度
    progress: float = 0.0  # 0.0 - 100.0
    progress_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.name,
            "priority": self.priority.name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dependencies": list(self.dependencies),
            "progress": self.progress,
            "progress_message": self.progress_message,
            "output_count": len(self.outputs),
            "has_result": self.result is not None,
            "error": self.error_message,
            "tags": self.tags
        }
    
    def get_duration(self) -> Optional[float]:
        """获取执行持续时间（秒）"""
        if self.started_at:
            end = self.completed_at or datetime.now()
            return (end - self.started_at).total_seconds()
        return None
    
    def add_output(self, content: Any, output_type: str = "text"):
        """添加输出"""
        self.outputs.append(TaskOutput(
            timestamp=datetime.now(),
            content=content,
            output_type=output_type
        ))
    
    def update_progress(self, progress: float, message: str = ""):
        """更新进度"""
        self.progress = max(0.0, min(100.0, progress))
        if message:
            self.progress_message = message


@dataclass
class TaskGroup:
    """任务组"""
    group_id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    task_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "name": self.name,
            "task_count": len(self.task_ids),
            "created_at": self.created_at.isoformat()
        }


class TaskRegistry:
    """
    任务注册表
    
    核心功能:
    - 任务注册和存储
    - 状态管理
    - 依赖关系处理
    - 查询和过滤
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self._tasks: Dict[str, Task] = {}
        self._groups: Dict[str, TaskGroup] = {}
        self._lock = threading.RLock()
        self._storage_path = Path(storage_path) if storage_path else None
        
        # 统计
        self._stats = {
            "total_created": 0,
            "total_completed": 0,
            "total_failed": 0
        }
        
        # 加载持久化数据
        self._load_from_disk()
    
    # ==================== 任务管理 ====================
    
    def create_task(self, name: str, description: str = "",
                   target: Optional[Callable] = None,
                   args: Tuple = (),
                   kwargs: Optional[Dict] = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   dependencies: Optional[Set[str]] = None,
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict] = None) -> Task:
        """创建新任务"""
        with self._lock:
            task = Task(
                name=name,
                description=description,
                target=target,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                dependencies=dependencies or set(),
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self._tasks[task.task_id] = task
            self._stats["total_created"] += 1
            
            # 更新依赖关系
            for dep_id in task.dependencies:
                if dep_id in self._tasks:
                    self._tasks[dep_id].dependents.add(task.task_id)
            
            print(f"[任务] 创建 '{name}' ({task.task_id}) [{priority.name}]")
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                
                # 更新依赖关系
                for dep_id in task.dependencies:
                    if dep_id in self._tasks:
                        self._tasks[dep_id].dependents.discard(task_id)
                
                for dep_id in task.dependents:
                    if dep_id in self._tasks:
                        self._tasks[dep_id].dependencies.discard(task_id)
                
                del self._tasks[task_id]
                return True
            return False
    
    def update_task_status(self, task_id: str, status: TaskStatus,
                          error_message: Optional[str] = None) -> bool:
        """更新任务状态"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            old_status = task.status
            task.status = status
            
            if status == TaskStatus.RUNNING and not task.started_at:
                task.started_at = datetime.now()
            
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.now()
                if status == TaskStatus.COMPLETED:
                    self._stats["total_completed"] += 1
                elif status == TaskStatus.FAILED:
                    self._stats["total_failed"] += 1
            
            if error_message:
                task.error_message = error_message
            
            print(f"[任务] '{task.name}' {old_status.name} -> {status.name}")
            self._save_to_disk()
            return True
    
    # ==================== 查询功能 ====================
    
    def list_tasks(self, status: Optional[TaskStatus] = None,
                   priority: Optional[TaskPriority] = None,
                   tags: Optional[List[str]] = None) -> List[Task]:
        """列出符合条件的任务"""
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        if tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]
        
        # 按优先级和时间排序
        tasks.sort(key=lambda t: (t.priority.value, t.created_at))
        
        return tasks
    
    def get_ready_tasks(self) -> List[Task]:
        """获取可以执行的任务（依赖已完成）"""
        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查所有依赖是否已完成
            deps_satisfied = all(
                self._tasks.get(dep_id) and 
                self._tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if deps_satisfied:
                ready.append(task)
        
        # 按优先级排序
        ready.sort(key=lambda t: t.priority.value)
        return ready
    
    def get_dependency_chain(self, task_id: str) -> List[str]:
        """获取任务的依赖链"""
        chain = []
        visited = set()
        
        def visit(tid: str):
            if tid in visited or tid not in self._tasks:
                return
            visited.add(tid)
            task = self._tasks[tid]
            for dep_id in task.dependencies:
                visit(dep_id)
            chain.append(tid)
        
        visit(task_id)
        return chain
    
    # ==================== 任务组管理 ====================
    
    def create_group(self, name: str, description: str = "") -> TaskGroup:
        """创建任务组"""
        with self._lock:
            group = TaskGroup(name=name, description=description)
            self._groups[group.group_id] = group
            return group
    
    def add_to_group(self, group_id: str, task_id: str) -> bool:
        """添加任务到组"""
        with self._lock:
            if group_id not in self._groups or task_id not in self._tasks:
                return False
            
            if task_id not in self._groups[group_id].task_ids:
                self._groups[group_id].task_ids.append(task_id)
            return True
    
    def get_group_tasks(self, group_id: str) -> List[Task]:
        """获取组内所有任务"""
        group = self._groups.get(group_id)
        if not group:
            return []
        
        return [self._tasks[tid] for tid in group.task_ids if tid in self._tasks]
    
    # ==================== 统计和报告 ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            status_counts = {}
            for task in self._tasks.values():
                status_name = task.status.name
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
            
            return {
                "total_tasks": len(self._tasks),
                "total_groups": len(self._groups),
                "status_distribution": status_counts,
                "total_created": self._stats["total_created"],
                "total_completed": self._stats["total_completed"],
                "total_failed": self._stats["total_failed"]
            }
    
    def generate_report(self) -> str:
        """生成任务报告"""
        stats = self.get_stats()
        
        lines = [
            "# 任务注册表报告",
            "",
            f"**生成时间**: {datetime.now().isoformat()}",
            "",
            "## 统计",
            f"- 总任务数: {stats['total_tasks']}",
            f"- 总任务组: {stats['total_groups']}",
            f"- 累计创建: {stats['total_created']}",
            f"- 累计完成: {stats['total_completed']}",
            f"- 累计失败: {stats['total_failed']}",
            "",
            "## 状态分布"
        ]
        
        for status, count in stats['status_distribution'].items():
            lines.append(f"- {status}: {count}")
        
        lines.extend(["", "## 最近任务"])
        
        recent_tasks = sorted(
            self._tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )[:10]
        
        for task in recent_tasks:
            lines.append(f"- [{task.status.name}] {task.name} ({task.task_id})")
        
        return "\n".join(lines)
    
    # ==================== 持久化 ====================
    
    def _save_to_disk(self):
        """保存到磁盘"""
        if not self._storage_path:
            return
        
        try:
            data = {
                "tasks": {tid: task.to_dict() for tid, task in self._tasks.items()},
                "groups": {gid: group.to_dict() for gid, group in self._groups.items()},
                "stats": self._stats,
                "saved_at": datetime.now().isoformat()
            }
            
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[错误] 保存任务注册表失败: {e}")
    
    def _load_from_disk(self):
        """从磁盘加载"""
        if not self._storage_path or not self._storage_path.exists():
            return
        
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复统计
            self._stats = data.get("stats", self._stats)
            
            print(f"[任务] 从磁盘加载 {len(data.get('tasks', {}))} 个任务")
        except Exception as e:
            print(f"[警告] 加载任务注册表失败: {e}")


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    
    @classmethod
    def success_result(cls, data: Any) -> 'TaskResult':
        return cls(success=True, data=data)
    
    @classmethod
    def error_result(cls, error: str) -> 'TaskResult':
        return cls(success=False, data=None, error=error)


class TaskExecutor:
    """
    任务执行器
    
    负责任务的实际执行
    """
    
    def __init__(self, registry: TaskRegistry):
        self.registry = registry
        self._running: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
    
    def execute_task(self, task_id: str, sync: bool = False) -> Optional['TaskResult']:
        """
        执行单个任务
        
        Args:
            task_id: 任务ID
            sync: 是否同步执行
        
        Returns:
            同步执行时返回结果，异步执行返回None
        """
        task = self.registry.get_task(task_id)
        if not task:
            print(f"[错误] 任务不存在: {task_id}")
            return None
        
        if task.status != TaskStatus.PENDING:
            print(f"[警告] 任务状态不是PENDING: {task.status.name}")
            return None
        
        if not task.target:
            print(f"[错误] 任务没有执行目标: {task_id}")
            return None
        
        def run():
            self.registry.update_task_status(task_id, TaskStatus.RUNNING)
            task.add_output(f"任务开始执行: {task.name}")
            
            try:
                # 执行目标函数
                result = task.target(*task.args, **task.kwargs)
                
                # 更新结果
                task.result = result
                task.add_output(f"任务执行完成，结果: {result}", "json" if isinstance(result, dict) else "text")
                self.registry.update_task_status(task_id, TaskStatus.COMPLETED)
                
            except Exception as e:
                error_msg = str(e)
                task.add_output(f"执行错误: {error_msg}", "error")
                self.registry.update_task_status(task_id, TaskStatus.FAILED, error_msg)
            
            finally:
                with self._lock:
                    if task_id in self._running:
                        del self._running[task_id]
        
        if sync:
            run()
            return TaskResult.success_result(task.result) if task.status == TaskStatus.COMPLETED else TaskResult.error_result(task.error_message or "未知错误")
        else:
            thread = threading.Thread(target=run, name=f"Task-{task_id}")
            with self._lock:
                self._running[task_id] = thread
            thread.start()
            return None
    
    def execute_ready_tasks(self, max_concurrent: int = 3) -> int:
        """
        执行所有就绪的任务
        
        Returns:
            启动的任务数量
        """
        ready_tasks = self.registry.get_ready_tasks()
        
        # 限制并发数
        with self._lock:
            current_running = len(self._running)
            available_slots = max_concurrent - current_running
            
            if available_slots <= 0:
                print(f"[执行器] 并发数已满 ({current_running}/{max_concurrent})")
                return 0
            
            tasks_to_run = ready_tasks[:available_slots]
        
        started = 0
        for task in tasks_to_run:
            self.execute_task(task.task_id, sync=False)
            started += 1
        
        return started
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            task = self.registry.get_task(task_id)
            if not task:
                return False
            
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self._running:
                # 注意: Python线程无法强制停止，只能标记状态
                self.registry.update_task_status(task_id, TaskStatus.CANCELLED)
                del self._running[task_id]
                return True
        return False
    
    def get_running_count(self) -> int:
        """获取正在运行的任务数"""
        with self._lock:
            return len(self._running)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3.3: Task Registry System Test")
    print("=" * 60)
    
    # 创建注册表
    registry = TaskRegistry()
    
    # 测试1: 创建任务
    print("\n测试1: 创建任务")
    task1 = registry.create_task(
        name="数据分析",
        description="分析CSV文件",
        target=lambda x: f"分析结果: {x}",
        args=("data.csv",),
        priority=TaskPriority.HIGH,
        tags=["data", "analysis"]
    )
    print(f"  创建任务: {task1.name} ({task1.task_id})")
    
    task2 = registry.create_task(
        name="生成报告",
        description="基于分析结果生成报告",
        target=lambda: "报告已生成",
        priority=TaskPriority.NORMAL,
        dependencies={task1.task_id},
        tags=["report"]
    )
    print(f"  创建任务: {task2.name} ({task2.task_id})，依赖: {task1.task_id}")
    
    # 测试2: 查询任务
    print("\n测试2: 查询任务")
    all_tasks = registry.list_tasks()
    print(f"  总任务数: {len(all_tasks)}")
    
    pending_tasks = registry.list_tasks(status=TaskStatus.PENDING)
    print(f"  等待中任务: {len(pending_tasks)}")
    
    ready_tasks = registry.get_ready_tasks()
    print(f"  就绪任务: {len(ready_tasks)}")
    for t in ready_tasks:
        print(f"    - {t.name} [{t.priority.name}]")
    
    # 测试3: 任务组
    print("\n测试3: 任务组")
    group = registry.create_group(name="数据处理流程", description="完整的数据处理流程")
    registry.add_to_group(group.group_id, task1.task_id)
    registry.add_to_group(group.group_id, task2.task_id)
    print(f"  创建组: {group.name} ({group.group_id})")
    
    group_tasks = registry.get_group_tasks(group.group_id)
    print(f"  组内任务: {len(group_tasks)} 个")
    
    # 测试4: 执行器
    print("\n测试4: 任务执行")
    executor = TaskExecutor(registry)
    
    # 执行任务1
    executor.execute_task(task1.task_id, sync=True)
    task1_result = registry.get_task(task1.task_id)
    print(f"  任务1状态: {task1_result.status.name}")
    print(f"  任务1结果: {task1_result.result}")
    
    # 现在任务2应该就绪了
    ready_tasks = registry.get_ready_tasks()
    print(f"  就绪任务: {len(ready_tasks)} 个")
    
    # 执行任务2
    executor.execute_task(task2.task_id, sync=True)
    task2_result = registry.get_task(task2.task_id)
    print(f"  任务2状态: {task2_result.status.name}")
    print(f"  任务2结果: {task2_result.result}")
    
    # 测试5: 统计
    print("\n测试5: 统计信息")
    stats = registry.get_stats()
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  状态分布: {stats['status_distribution']}")
    
    # 测试6: 报告
    print("\n测试6: 生成报告")
    report = registry.generate_report()
    print(report[:500] + "...")
    
    print("\n" + "=" * 60)
    print("Task Registry System Test Completed!")
    print("=" * 60)
