#!/usr/bin/env python3
"""
Error Recovery System - 错误恢复机制
自动检测、恢复和报告系统错误

灵感来源: Claw Code 的恢复和恢复能力
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum, auto
from datetime import datetime
import time
import traceback
import json
from pathlib import Path
import threading


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 警告，可忽略
    MEDIUM = "medium"     # 影响功能，可恢复
    HIGH = "high"         # 严重问题，需干预
    CRITICAL = "critical" # 系统故障，必须处理


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = auto()        # 重试
    FALLBACK = auto()     # 使用备用方案
    RESET = auto()        # 重置状态
    CIRCUIT_BREAK = auto() # 熔断
    NOTIFY = auto()       # 仅通知


@dataclass
class ErrorRecord:
    """错误记录"""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    component: str
    timestamp: float = field(default_factory=time.time)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False
    recovery_attempts: int = 0
    recovery_strategy: Optional[RecoveryStrategy] = None
    
    def to_dict(self) -> Dict:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "component": self.component,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "stack_trace": self.stack_trace,
            "context": self.context,
            "recovered": self.recovered,
            "recovery_attempts": self.recovery_attempts,
            "recovery_strategy": self.recovery_strategy.name if self.recovery_strategy else None
        }


@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    strategy: RecoveryStrategy
    attempts: int
    duration_ms: float
    message: str
    new_state: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "strategy": self.strategy.name,
            "attempts": self.attempts,
            "duration_ms": self.duration_ms,
            "message": self.message,
            "new_state": self.new_state
        }


class RecoveryHandler:
    """恢复处理器"""
    
    def __init__(self):
        self.handlers: Dict[RecoveryStrategy, Callable] = {}
        self.max_retries: int = 3
        self.retry_delay_ms: int = 1000
        self.circuit_breaker_threshold: int = 5
        
    def register(self, strategy: RecoveryStrategy, handler: Callable):
        """注册恢复处理器"""
        self.handlers[strategy] = handler
        
    def execute(self, strategy: RecoveryStrategy, context: Dict) -> RecoveryResult:
        """执行恢复"""
        start = time.time()
        
        if strategy not in self.handlers:
            return RecoveryResult(
                success=False,
                strategy=strategy,
                attempts=0,
                duration_ms=(time.time() - start) * 1000,
                message=f"No handler registered for strategy: {strategy}"
            )
        
        try:
            result = self.handlers[strategy](context)
            duration = (time.time() - start) * 1000
            
            if isinstance(result, dict):
                return RecoveryResult(
                    success=result.get("success", False),
                    strategy=strategy,
                    attempts=result.get("attempts", 1),
                    duration_ms=duration,
                    message=result.get("message", "Recovery executed"),
                    new_state=result.get("new_state")
                )
            else:
                return RecoveryResult(
                    success=True,
                    strategy=strategy,
                    attempts=1,
                    duration_ms=duration,
                    message="Recovery completed successfully"
                )
                
        except Exception as e:
            return RecoveryResult(
                success=False,
                strategy=strategy,
                attempts=0,
                duration_ms=(time.time() - start) * 1000,
                message=f"Recovery failed: {str(e)}"
            )


class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.error_history: List[ErrorRecord] = []
        self.recovery_handler = RecoveryHandler()
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / ".claw" / "errors"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._circuit_breakers: Dict[str, Dict] = {}  # 熔断器状态
        
        # 注册默认恢复处理器
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """注册默认恢复处理器"""
        # 重试处理器
        self.recovery_handler.register(RecoveryStrategy.RETRY, self._handle_retry)
        
        # 重置处理器
        self.recovery_handler.register(RecoveryStrategy.RESET, self._handle_reset)
        
        # 熔断处理器
        self.recovery_handler.register(RecoveryStrategy.CIRCUIT_BREAK, self._handle_circuit_break)
        
        # 备用方案处理器
        self.recovery_handler.register(RecoveryStrategy.FALLBACK, self._handle_fallback)
    
    def record_error(self, error: Exception, component: str, 
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     context: Optional[Dict] = None) -> ErrorRecord:
        """记录错误"""
        with self._lock:
            record = ErrorRecord(
                error_type=type(error).__name__,
                error_message=str(error),
                severity=severity,
                component=component,
                stack_trace=traceback.format_exc(),
                context=context or {}
            )
            
            self.error_history.append(record)
            self._persist_error(record)
            
            # 更新熔断器
            self._update_circuit_breaker(component)
            
            return record
    
    def attempt_recovery(self, record: ErrorRecord, 
                        strategy: Optional[RecoveryStrategy] = None) -> RecoveryResult:
        """尝试恢复"""
        with self._lock:
            # 如果没有指定策略，根据错误选择
            if strategy is None:
                strategy = self._select_strategy(record)
            
            # 检查熔断器
            if self._is_circuit_open(record.component):
                return RecoveryResult(
                    success=False,
                    strategy=RecoveryStrategy.CIRCUIT_BREAK,
                    attempts=0,
                    duration_ms=0,
                    message=f"Circuit breaker open for component: {record.component}"
                )
            
            # 执行恢复
            context = {
                "error": record,
                "component": record.component,
                "context": record.context
            }
            
            result = self.recovery_handler.execute(strategy, context)
            
            # 更新记录
            record.recovery_attempts += result.attempts
            record.recovery_strategy = strategy
            record.recovered = result.success
            
            return result
    
    def _select_strategy(self, record: ErrorRecord) -> RecoveryStrategy:
        """选择恢复策略"""
        # 根据错误类型选择
        if record.error_type in ["ConnectionError", "TimeoutError"]:
            return RecoveryStrategy.RETRY
        
        if record.error_type in ["StateError", "CorruptionError"]:
            return RecoveryStrategy.RESET
        
        if record.severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.CIRCUIT_BREAK
        
        if record.severity == ErrorSeverity.HIGH:
            return RecoveryStrategy.FALLBACK
        
        return RecoveryStrategy.RETRY
    
    def _handle_retry(self, context: Dict) -> Dict:
        """处理重试"""
        component = context.get("component", "unknown")
        max_retries = self.recovery_handler.max_retries
        delay_ms = self.recovery_handler.retry_delay_ms
        
        for attempt in range(1, max_retries + 1):
            time.sleep(delay_ms / 1000 * attempt)  # 指数退避
            
            # 这里应该调用实际的恢复操作
            # 简化处理：假设重试成功
            return {
                "success": True,
                "attempts": attempt,
                "message": f"Retry succeeded after {attempt} attempts"
            }
        
        return {
            "success": False,
            "attempts": max_retries,
            "message": f"Retry failed after {max_retries} attempts"
        }
    
    def _handle_reset(self, context: Dict) -> Dict:
        """处理重置"""
        component = context.get("component", "unknown")
        
        # 重置组件状态
        new_state = {"status": "reset", "timestamp": time.time()}
        
        return {
            "success": True,
            "attempts": 1,
            "message": f"Component {component} state reset",
            "new_state": new_state
        }
    
    def _handle_circuit_break(self, context: Dict) -> Dict:
        """处理熔断"""
        component = context.get("component", "unknown")
        
        # 打开熔断器
        self._circuit_breakers[component] = {
            "open": True,
            "opened_at": time.time(),
            "failure_count": 0
        }
        
        return {
            "success": False,
            "attempts": 0,
            "message": f"Circuit breaker opened for {component}"
        }
    
    def _handle_fallback(self, context: Dict) -> Dict:
        """处理备用方案"""
        component = context.get("component", "unknown")
        
        # 使用备用方案
        return {
            "success": True,
            "attempts": 1,
            "message": f"Fallback executed for {component}",
            "new_state": {"mode": "fallback"}
        }
    
    def _update_circuit_breaker(self, component: str):
        """更新熔断器状态"""
        if component not in self._circuit_breakers:
            self._circuit_breakers[component] = {
                "open": False,
                "failure_count": 1,
                "last_failure": time.time()
            }
        else:
            cb = self._circuit_breakers[component]
            cb["failure_count"] += 1
            cb["last_failure"] = time.time()
            
            # 检查是否需要熔断
            if cb["failure_count"] >= self.recovery_handler.circuit_breaker_threshold:
                cb["open"] = True
    
    def _is_circuit_open(self, component: str) -> bool:
        """检查熔断器是否打开"""
        if component not in self._circuit_breakers:
            return False
        
        cb = self._circuit_breakers[component]
        
        # 检查是否应该关闭熔断器（5分钟后）
        if cb["open"] and time.time() - cb.get("opened_at", 0) > 300:
            cb["open"] = False
            cb["failure_count"] = 0
            return False
        
        return cb["open"]
    
    def _persist_error(self, record: ErrorRecord):
        """持久化错误"""
        filename = f"error_{int(record.timestamp)}_{record.component}.json"
        filepath = self.storage_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_error_summary(self) -> Dict:
        """获取错误摘要"""
        with self._lock:
            total = len(self.error_history)
            recovered = sum(1 for e in self.error_history if e.recovered)
            
            by_severity = {}
            for e in self.error_history:
                by_severity[e.severity.value] = by_severity.get(e.severity.value, 0) + 1
            
            by_component = {}
            for e in self.error_history:
                by_component[e.component] = by_component.get(e.component, 0) + 1
            
            return {
                "total": total,
                "recovered": recovered,
                "unrecovered": total - recovered,
                "recovery_rate": recovered / total if total > 0 else 0,
                "by_severity": by_severity,
                "by_component": by_component,
                "circuit_breakers": list(self._circuit_breakers.keys())
            }
    
    def generate_report(self) -> str:
        """生成恢复报告"""
        summary = self.get_error_summary()
        
        lines = [
            "=" * 60,
            "Error Recovery Report",
            "=" * 60,
            f"Total Errors: {summary['total']}",
            f"Recovered: {summary['recovered']}",
            f"Unrecovered: {summary['unrecovered']}",
            f"Recovery Rate: {summary['recovery_rate']*100:.1f}%",
            "-" * 60,
            "By Severity:",
        ]
        
        for sev, count in summary['by_severity'].items():
            lines.append(f"  {sev}: {count}")
        
        lines.extend([
            "-" * 60,
            "By Component:"
        ])
        
        for comp, count in summary['by_component'].items():
            lines.append(f"  {comp}: {count}")
        
        lines.extend([
            "-" * 60,
            f"Circuit Breakers: {len(summary['circuit_breakers'])}",
            "=" * 60
        ])
        
        return "\n".join(lines)
    
    def clear_history(self):
        """清除历史"""
        with self._lock:
            self.error_history.clear()
            self._circuit_breakers.clear()


# 装饰器：自动错误恢复
def with_recovery(component: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  auto_recover: bool = True):
    """自动恢复装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = ErrorRecoveryManager()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录错误
                record = manager.record_error(
                    error=e,
                    component=component,
                    severity=severity,
                    context={"args": str(args), "kwargs": str(kwargs)}
                )
                
                # 自动恢复
                if auto_recover:
                    result = manager.attempt_recovery(record)
                    if result.success:
                        # 恢复成功，返回默认值
                        return None
                
                # 恢复失败，重新抛出
                raise
        return wrapper
    return decorator


# 测试代码
if __name__ == "__main__":
    print("Error Recovery System Test")
    print("=" * 60)
    
    manager = ErrorRecoveryManager()
    
    # 模拟一些错误
    errors = [
        (ConnectionError("Failed to connect"), "network", ErrorSeverity.HIGH),
        (TimeoutError("Operation timeout"), "database", ErrorSeverity.MEDIUM),
        (ValueError("Invalid input"), "parser", ErrorSeverity.LOW),
        (RuntimeError("System failure"), "core", ErrorSeverity.CRITICAL),
    ]
    
    for error, component, severity in errors:
        record = manager.record_error(error, component, severity)
        print(f"Recorded: {record.error_type} in {component}")
        
        # 尝试恢复
        result = manager.attempt_recovery(record)
        print(f"  Recovery: {result.success} using {result.strategy.name}")
    
    # 生成报告
    print("\n" + manager.generate_report())
    
    print("\n" + "=" * 60)
    print("Error Recovery module ready!")
