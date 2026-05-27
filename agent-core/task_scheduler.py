#!/usr/bin/env python3
"""
Task Scheduler - 定时任务调度器
借鉴Hermes Agent的cron调度器理念，实现简单高效的定时任务系统

特性:
1. 支持一次性/循环任务
2. 任务优先级调度
3. 任务执行监控和日志
4. 故障恢复机制
5. 内存持久化存储
"""

import time
import json
import threading
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from collections import deque

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型"""
    ONCE = "once"
    RECURRING = "recurring"

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """任务定义"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.ONCE
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    
    # 时间相关
    scheduled_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    recurrence: Optional[str] = None  # cron表达式（简化版）
    
    # 执行参数
    func_name: str = ""
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # 执行结果
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "scheduled_at": self.scheduled_at.isoformat(),
            "func_name": self.func_name,
            "args": self.args,
            "kwargs": self.kwargs,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags
        }
        
        if self.executed_at:
            data["executed_at"] = self.executed_at.isoformat()
        if self.finished_at:
            data["finished_at"] = self.finished_at.isoformat()
        if self.result:
            data["result"] = str(self.result)
        if self.error:
            data["error"] = self.error
        
        return data
    
    def should_run_now(self) -> bool:
        """检查是否应该运行"""
        if self.status == TaskStatus.PENDING:
            now = datetime.now()
            return now >= self.scheduled_at
        return False

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, max_workers: int = 3, storage_file: str = ".workbuddy/tasks.json"):
        self.max_workers = max_workers
        self.storage_file = Path(storage_file)
        
        # 初始化存储
        self.tasks: Dict[str, Task] = {}
        self.task_queue = deque()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.scheduler_thread = None
        self.running = False
        
        # 函数注册表
        self.function_registry: Dict[str, Callable] = {}
        
        # 加载任务
        self.load_tasks()
        
        # 启动调度器线程
        self.start_scheduler()
    
    def start_scheduler(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("[任务调度器] 已启动，最大工作线程: %d", self.max_workers)
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        logger.info("[任务调度器] 已停止")
    
    def register_function(self, func_name: str, func: Callable):
        """注册函数"""
        self.function_registry[func_name] = func
        logger.info("[函数注册] 已注册函数: %s", func_name)
    
    def schedule_task(self, task: Task) -> str:
        """调度任务"""
        self.tasks[task.id] = task
        
        # 根据优先级插入队列
        self._insert_into_queue(task)
        
        # 保存到存储
        self.save_tasks()
        
        logger.info("[任务调度] 已调度: %s (ID: %s)", task.name, task.id)
        return task.id
    
    def schedule_once(self, func_name: str, args=None, kwargs=None, **options) -> str:
        """调度一次性任务"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        task = Task(
            name=options.get("name", f"OneTimeTask-{func_name}"),
            description=options.get("description", f"一次性任务: {func_name}"),
            task_type=TaskType.ONCE,
            scheduled_at=options.get("scheduled_at", datetime.now()),
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            priority=options.get("priority", TaskPriority.NORMAL),
            tags=options.get("tags", []),
            created_by=options.get("created_by", "scheduler")
        )
        
        return self.schedule_task(task)
    
    def schedule_recurring(self, func_name: str, interval_seconds: int, **options) -> str:
        """调度重复任务"""
        scheduled_at = options.get("scheduled_at", datetime.now())
        recurrence = f"interval:{interval_seconds}"
        
        task = Task(
            name=options.get("name", f"RecurringTask-{func_name}"),
            description=options.get("description", f"重复任务: {func_name}"),
            task_type=TaskType.RECURRING,
            scheduled_at=scheduled_at,
            func_name=func_name,
            args=options.get("args", []),
            kwargs=options.get("kwargs", {}),
            recurrence=recurrence,
            priority=options.get("priority", TaskPriority.NORMAL),
            tags=options.get("tags", []),
            created_by=options.get("created_by", "scheduler")
        )
        
        return self.schedule_task(task)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            
            # 从队列中移除
            for i, t in enumerate(self.task_queue):
                if t.id == task_id:
                    self.task_queue[i].status = TaskStatus.CANCELLED
                    break
            
            self.save_tasks()
            logger.info("[任务取消] %s (ID: %s)", task.name, task_id)
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status=None, task_type=None, priority=None):
        """列出任务"""
        filtered_tasks = []
        
        for task in self.tasks.values():
            # 状态过滤
            if status and task.status != status:
                continue
            
            # 类型过滤
            if task_type and task.task_type != task_type:
                continue
            
            # 优先级过滤
            if priority and task.priority != priority:
                continue
            
            filtered_tasks.append(task)
        
        return sorted(filtered_tasks, key=lambda x: x.scheduled_at)
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                # 检查新任务
                self._check_new_tasks()
                
                # 检查已运行任务
                self._check_running_tasks()
                
                # 清理任务
                self._cleanup_tasks()
                
                # 保存状态
                self.save_tasks()
                
                time.sleep(1)  # 1秒间隔
                
            except Exception as e:
                logger.error("[调度器] 主循环错误: %s", e)
                time.sleep(5)  # 错误时等待更长时间
    
    def _check_new_tasks(self):
        """检查新任务"""
        for task in self.tasks.values():
            if task.should_run_now() and task.status == TaskStatus.PENDING:
                # 提交到线程池
                future = self.executor.submit(self._execute_task, task)
                
                # 更新任务状态
                task.status = TaskStatus.RUNNING
                task.executed_at = datetime.now()
                self.running_tasks[task.id] = task
                
                logger.info("[任务启动] %s (ID: %s)", task.name, task.id)
    
    def _check_running_tasks(self):
        """检查正在运行的任务"""
        completed = []
        
        for task_id, task in self.running_tasks.items():
            # 这里实际检查线程状态，简化版直接检测
            # 假设任务立即执行完成，实际中应该监控Future状态
            pass
    
    def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 获取函数
            func = self.function_registry.get(task.func_name)
            if not func:
                raise ValueError(f"函数未注册: {task.func_name}")
            
            # 执行函数
            task.result = func(*task.args, **task.kwargs)
            
            # 更新状态
            task.status = TaskStatus.COMPLETED
            task.finished_at = datetime.now()
            logger.info("[任务完成] %s (ID: %s)", task.name, task.id)
            
            # 处理重复任务
            if task.task_type == TaskType.RECURRING:
                # 重新调度
                recurrence = task.recurrence
                if recurrence and recurrence.startswith("interval:"):
                    interval = int(recurrence.split(":")[1])
                    task.scheduled_at = datetime.now() + timedelta(seconds=interval)
                    task.status = TaskStatus.PENDING
                    task.executed_at = None
                    task.finished_at = None
                    task.result = None
                    self._insert_into_queue(task)
        
        except Exception as e:
            task.error = str(e)
            
            # 重试机制
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.scheduled_at = datetime.now() + timedelta(minutes=5)  # 5分钟后重试
                self._insert_into_queue(task)
                logger.warning("[任务重试] %s (ID: %s) 第%d次重试", task.name, task.id, task.retry_count)
            else:
                task.status = TaskStatus.FAILED
                task.finished_at = datetime.now()
                self.failed_tasks.append(task)
                logger.error("[任务失败] %s (ID: %s): %s", task.name, task.id, e)
        
        finally:
            # 从运行中移除
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    def _insert_into_queue(self, task: Task):
        """按优先级插入队列"""
        # 优先级越高，插入越靠前
        priority_level = task.priority.value
        
        for i, queued_task in enumerate(self.task_queue):
            if priority_level > queued_task.priority.value:
                self.task_queue.insert(i, task)
                return
        
        self.task_queue.append(task)
    
    def _cleanup_tasks(self):
        """清理已完成任务"""
        # 保留最近100个已完成的记录，其余保存到历史文件
        if len(self.completed_tasks) > 100:
            self._save_completed_tasks(self.completed_tasks[100:])
            self.completed_tasks = self.completed_tasks[:100]
    
    def load_tasks(self):
        """从存储加载任务"""
        if not self.storage_file.exists():
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tasks.clear()
            self.task_queue.clear()
            
            for task_data in data.get("tasks", []):
                # 解析时间字段
                for time_key in ["scheduled_at", "executed_at", "finished_at", "created_at"]:
                    if time_key in task_data and task_data[time_key]:
                        task_data[time_key] = datetime.fromisoformat(task_data[time_key])
                
                # 创建任务对象
                task = Task(**task_data)
                self.tasks[task.id] = task
                
                # 添加到队列
                if task.status == TaskStatus.PENDING:
                    self._insert_into_queue(task)
            
            logger.info("[任务加载] 已加载 %d 个任务", len(self.tasks))
        
        except Exception as e:
            logger.error("[任务加载] 加载失败: %s", e)
    
    def save_tasks(self):
        """保存任务到存储"""
        try:
            data = {"tasks": [], "last_saved": datetime.now().isoformat()}
            
            for task in self.tasks.values():
                data["tasks"].append(task.to_dict())
            
            # 创建目录
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("[任务保存] 已保存 %d 个任务", len(data["tasks"]))
        
        except Exception as e:
            logger.error("[任务保存] 保存失败: %s", e)
    
    def _save_completed_tasks(self, tasks):
        """保存已完成的记录到历史文件"""
        history_file = self.storage_file.parent / "tasks_history.json"
        
        try:
            # 创建目录
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 加载现有历史
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 添加新记录
            for task in tasks:
                history.append(task.to_dict())
            
            # 保存历史
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.debug("[历史保存] 已保存 %d 条历史记录", len(tasks))
        
        except Exception as e:
            logger.error("[历史保存] 保存失败: %s", e)
    
    def get_stats(self):
        """获取统计信息"""
        stats = {
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "cancelled_tasks": sum(1 for t in self.tasks.values() if t.status == TaskStatus.CANCELLED),
            "task_queue_size": len(self.task_queue),
            "function_registry": len(self.function_registry)
        }
        
        return stats

# 示例函数
def demo_function(message: str, repeat: int = 1) -> str:
    """演示函数"""
    result = f"DemoFunction: {message} repeated {repeat} times"
    logger.info("[演示] 函数执行: %s", result)
    return result

def demo_browser_function(url: str) -> str:
    """演示浏览器函数"""
    from browser_automation import BrowserAutomator
    automator = BrowserAutomator()
    automator.start()
    automator.navigate_to(url, 3)
    content = automator.get_page_content()
    automator.close()
    
    # 简化为页面内容长度
    if content:
        return f"Page content length: {len(content)}"
    return "No content"

def demo_task_scheduler():
    """演示任务调度器"""
    print("[启动] Hermes风格任务调度器演示")
    
    # 创建调度器
    scheduler = TaskScheduler(max_workers=2)
    
    # 注册函数
    scheduler.register_function("demo_function", demo_function)
    scheduler.register_function("demo_browser_function", demo_browser_function)
    
    # 调度一次性任务
    task_id1 = scheduler.schedule_once(
        func_name="demo_function",
        args=["Hello World"],
        kwargs={"repeat": 3},
        name="Demo Task 1",
        description="演示任务1",
        scheduled_at=datetime.now()
    )
    
    # 调度延迟任务
    delayed_time = datetime.now() + timedelta(seconds=5)
    task_id2 = scheduler.schedule_once(
        func_name="demo_function",
        args=["Delayed Hello"],
        name="Demo Task 2",
        description="演示任务2",
        scheduled_at=delayed_time
    )
    
    # 调度重复任务
    task_id3 = scheduler.schedule_recurring(
        func_name="demo_function",
        interval_seconds=10,
        args=["Recurring Task"],
        name="Demo Task 3",
        description="演示任务3"
    )
    
    # 显示任务状态
    print("\n[任务列表]")
    tasks = scheduler.list_tasks()
    for task in tasks:
        print(f"  - {task.name}: {task.status.value} (ID: {task.id})")
    
    # 显示统计信息
    stats = scheduler.get_stats()
    print(f"\n[统计信息]")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 等待几秒钟，让任务执行
    print("\n[等待任务执行...]")
    for i in range(3):
        time.sleep(2)
        
        # 更新状态
        task1 = scheduler.get_task_status(task_id1)
        if task1 and task1.status == TaskStatus.COMPLETED:
            print(f"任务完成: {task1.name} -> {task1.result}")
    
    # 停止调度器
    scheduler.stop_scheduler()
    print("[完成] 任务调度器演示结束")

if __name__ == "__main__":
    demo_task_scheduler()