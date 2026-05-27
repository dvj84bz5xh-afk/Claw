#!/usr/bin/env python3
"""
Performance Profiler - 性能分析器
分析瓶颈，提供优化建议
"""

import time
import functools
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class FunctionMetrics:
    """函数性能指标"""
    name: str
    call_count: int = 0
    total_time_ms: float = 0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0
    avg_time_ms: float = 0
    last_call_time: Optional[datetime] = None


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.metrics: Dict[str, FunctionMetrics] = defaultdict(
            lambda: FunctionMetrics(name="")
        )
        self.enabled = True
    
    def profile(self, func: Callable) -> Callable:
        """装饰器：分析函数性能"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            func_name = f"{func.__module__}.{func.__name__}"
            
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self._record_metrics(func_name, elapsed_ms)
        
        return wrapper
    
    def _record_metrics(self, func_name: str, elapsed_ms: float):
        """记录性能指标"""
        if func_name not in self.metrics:
            self.metrics[func_name] = FunctionMetrics(name=func_name)
        
        metrics = self.metrics[func_name]
        metrics.call_count += 1
        metrics.total_time_ms += elapsed_ms
        metrics.min_time_ms = min(metrics.min_time_ms, elapsed_ms)
        metrics.max_time_ms = max(metrics.max_time_ms, elapsed_ms)
        metrics.avg_time_ms = metrics.total_time_ms / metrics.call_count
        metrics.last_call_time = datetime.now()
    
    def get_slow_functions(self, threshold_ms: float = 100) -> List[FunctionMetrics]:
        """获取慢函数列表"""
        slow = [m for m in self.metrics.values() if m.avg_time_ms > threshold_ms]
        return sorted(slow, key=lambda m: m.avg_time_ms, reverse=True)
    
    def get_hotspot_functions(self, top_n: int = 10) -> List[FunctionMetrics]:
        """获取热点函数（调用最频繁）"""
        hotspots = sorted(self.metrics.values(), key=lambda m: m.call_count, reverse=True)
        return hotspots[:top_n]
    
    def get_report(self) -> Dict:
        """生成性能报告"""
        total_calls = sum(m.call_count for m in self.metrics.values())
        total_time = sum(m.total_time_ms for m in self.metrics.values())
        
        # 慢函数（>100ms）
        slow_functions = self.get_slow_functions(100)
        
        # 热点函数
        hotspot_functions = self.get_hotspot_functions(10)
        
        # 优化建议
        suggestions = []
        
        if slow_functions:
            suggestions.append(f"发现 {len(slow_functions)} 个慢函数，建议优化")
        
        high_freq = [m for m in self.metrics.values() if m.call_count > 100]
        if high_freq:
            suggestions.append(f"发现 {len(high_freq)} 个高频调用函数，建议添加缓存")
        
        return {
            "summary": {
                "total_functions": len(self.metrics),
                "total_calls": total_calls,
                "total_time_ms": round(total_time, 2),
                "avg_time_per_call_ms": round(total_time / total_calls, 2) if total_calls > 0 else 0
            },
            "slow_functions": [
                {
                    "name": m.name,
                    "avg_time_ms": round(m.avg_time_ms, 2),
                    "call_count": m.call_count,
                    "max_time_ms": round(m.max_time_ms, 2)
                }
                for m in slow_functions[:5]
            ],
            "hotspot_functions": [
                {
                    "name": m.name,
                    "call_count": m.call_count,
                    "avg_time_ms": round(m.avg_time_ms, 2)
                }
                for m in hotspot_functions[:5]
            ],
            "suggestions": suggestions
        }
    
    def reset(self):
        """重置所有指标"""
        self.metrics.clear()


# 全局性能分析器实例
global_profiler = PerformanceProfiler()


class CodeOptimizer:
    """代码优化建议生成器"""
    
    def __init__(self):
        self.optimization_rules = {
            "loop_in_file_ops": {
                "pattern": "for.*in.*read_file",
                "suggestion": "避免在循环中重复读取文件，建议缓存文件内容"
            },
            "redundant_api_calls": {
                "pattern": "execute_command.*execute_command",
                "suggestion": "合并多个execute_command调用，减少进程启动开销"
            },
            "inefficient_search": {
                "pattern": "for.*search_content",
                "suggestion": "使用更精确的搜索模式，减少遍历范围"
            }
        }
    
    def analyze_code(self, code: str, filename: str = "") -> List[Dict]:
        """分析代码并提供优化建议"""
        suggestions = []
        
        for rule_name, rule in self.optimization_rules.items():
            import re
            if re.search(rule["pattern"], code, re.IGNORECASE):
                suggestions.append({
                    "rule": rule_name,
                    "suggestion": rule["suggestion"],
                    "severity": "medium"
                })
        
        return suggestions
    
    def suggest_architecture_improvements(self, current_metrics: Dict) -> List[str]:
        """建议架构改进"""
        suggestions = []
        
        # 基于性能指标的建议
        avg_response = current_metrics.get("avg_response_time_ms", 0)
        if avg_response > 500:
            suggestions.append("响应时间超过500ms，建议引入异步处理或缓存机制")
        
        cache_hit = current_metrics.get("cache_hit_rate", 0)
        if cache_hit < 50:
            suggestions.append("缓存命中率低于50%，建议优化缓存策略或增加缓存覆盖")
        
        memory_usage = current_metrics.get("memory_usage_mb", 0)
        if memory_usage > 1024:
            suggestions.append("内存使用超过1GB，建议检查内存泄漏或优化数据结构")
        
        return suggestions


def main():
    """测试性能分析器"""
    profiler = PerformanceProfiler()
    
    # 模拟一些函数调用
    @profiler.profile
    def slow_function():
        time.sleep(0.2)
        return "done"
    
    @profiler.profile
    def fast_function():
        time.sleep(0.01)
        return "done"
    
    # 调用函数
    for _ in range(10):
        slow_function()
    
    for _ in range(100):
        fast_function()
    
    # 生成报告
    report = profiler.get_report()
    
    print("=" * 60)
    print("Performance Profiler 报告")
    print("=" * 60)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
