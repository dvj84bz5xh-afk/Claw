#!/usr/bin/env python3
"""
Async Processor - 异步任务处理器
提升并发处理能力，减少阻塞
"""

import asyncio
import threading
from typing import List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from queue import Queue
import time


@dataclass
class Task:
    """任务定义"""
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int
    created_at: datetime
    callback: Optional[Callable] = None


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any
    error: Optional[str]
    completed_at: datetime
    execution_time_ms: float


class AsyncProcessor:
    """异步处理器"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        self.max_workers = max_workers
        self.task_queue = Queue(maxsize=queue_size)
        self.results: dict = {}
        self.running = False
        self.workers: List[threading.Thread] = []
        
        # 统计
        self.tasks_submitted = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
    
    def start(self):
        """启动处理器"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止处理器"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=5)
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                self._execute_task(task)
            except Exception:
                continue
    
    def _execute_task(self, task: Task):
        """执行任务"""
        start_time = time.time()
        
        try:
            result = task.func(*task.args, **task.kwargs)
            task_result = TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                error=None,
                completed_at=datetime.now(),
                execution_time_ms=(time.time() - start_time) * 1000
            )
            self.tasks_completed += 1
        except Exception as e:
            task_result = TaskResult(
                task_id=task.id,
                success=False,
                result=None,
                error=str(e),
                completed_at=datetime.now(),
                execution_time_ms=(time.time() - start_time) * 1000
            )
            self.tasks_failed += 1
        
        self.results[task.id] = task_result
        
        # 调用回调
        if task.callback:
            try:
                task.callback(task_result)
            except Exception:
                pass
    
    def submit(self, func: Callable, *args, priority: int = 5, callback: Callable = None, **kwargs) -> str:
        """提交任务"""
        import uuid
        task_id = str(uuid.uuid4())[:8]
        
        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=datetime.now(),
            callback=callback
        )
        
        self.task_queue.put(task)
        self.tasks_submitted += 1
        
        return task_id
    
    def get_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        """获取任务结果"""
        start_time = time.time()
        while timeout is None or (time.time() - start_time) < timeout:
            if task_id in self.results:
                return self.results[task_id]
            time.sleep(0.1)
        return None
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "workers": self.max_workers,
            "queue_size": self.task_queue.qsize(),
            "tasks_submitted": self.tasks_submitted,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "pending": self.tasks_submitted - self.tasks_completed - self.tasks_failed
        }


# 全局异步处理器实例
global_processor = AsyncProcessor()


def parallel_process(items: List[Any], func: Callable, max_workers: int = 4) -> List[Any]:
    """并行处理列表"""
    processor = AsyncProcessor(max_workers=max_workers)
    processor.start()
    
    task_ids = []
    for item in items:
        task_id = processor.submit(func, item)
        task_ids.append(task_id)
    
    # 等待所有任务完成
    results = []
    for task_id in task_ids:
        result = processor.get_result(task_id, timeout=300)
        if result and result.success:
            results.append(result.result)
    
    processor.stop()
    return results


def main():
    """测试异步处理器"""
    processor = AsyncProcessor(max_workers=2)
    processor.start()
    
    # 提交测试任务
    def test_task(n):
        time.sleep(0.5)
        return n * n
    
    task_ids = []
    for i in range(5):
        task_id = processor.submit(test_task, i)
        task_ids.append(task_id)
        print(f"提交任务 {task_id}: 计算 {i}^2")
    
    # 获取结果
    for task_id in task_ids:
        result = processor.get_result(task_id, timeout=5)
        if result:
            print(f"任务 {task_id}: 结果={result.result}, 耗时={result.execution_time_ms:.0f}ms")
    
    print("=" * 60)
    print("统计:", processor.get_stats())
    
    processor.stop()


if __name__ == "__main__":
    main()
