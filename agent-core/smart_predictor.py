#!/usr/bin/env python3
"""
Smart Predictor - 智能预测和预警系统
基于历史数据预测趋势，提前预警潜在问题

Phase 4 额外优化模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
import time
import json
import statistics
from collections import deque
from pathlib import Path
import threading


class AlertSeverity(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"     # 计数器
    GAUGE = "gauge"         # 瞬时值
    HISTOGRAM = "histogram" # 分布
    RATE = "rate"           # 速率


@dataclass
class Metric:
    """指标数据点"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "type": self.metric_type.value
        }


@dataclass
class Alert:
    """预警"""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolved_at: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at
        }


@dataclass
class Prediction:
    """预测结果"""
    metric_name: str
    predicted_value: float
    confidence: float  # 0-1
    horizon_minutes: int
    trend: str  # "increasing", "decreasing", "stable"
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "metric_name": self.metric_name,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "horizon_minutes": self.horizon_minutes,
            "trend": self.trend,
            "timestamp": self.timestamp
        }


class TimeSeriesStore:
    """时间序列存储"""
    
    def __init__(self, max_points: int = 1000):
        self.data: Dict[str, deque] = {}
        self.max_points = max_points
        self._lock = threading.RLock()
    
    def add(self, metric: Metric):
        """添加数据点"""
        with self._lock:
            if metric.name not in self.data:
                self.data[metric.name] = deque(maxlen=self.max_points)
            
            self.data[metric.name].append(metric)
    
    def get_series(self, name: str, 
                   since: Optional[float] = None) -> List[Metric]:
        """获取时间序列"""
        with self._lock:
            series = list(self.data.get(name, []))
        
        if since:
            series = [m for m in series if m.timestamp >= since]
        
        return series
    
    def get_latest(self, name: str) -> Optional[Metric]:
        """获取最新值"""
        with self._lock:
            series = self.data.get(name)
            return series[-1] if series else None
    
    def get_statistics(self, name: str) -> Dict:
        """获取统计信息"""
        series = self.get_series(name)
        
        if not series:
            return {}
        
        values = [m.value for m in series]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "latest": values[-1]
        }


class AlertRule:
    """预警规则"""
    
    def __init__(self, name: str, metric_name: str,
                 threshold: float, severity: AlertSeverity = AlertSeverity.WARNING,
                 comparison: str = "gt",  # gt, lt, eq, neq
                 duration_seconds: int = 60,
                 message_template: str = "{metric} is {value}, exceeds threshold {threshold}"):
        self.name = name
        self.metric_name = metric_name
        self.threshold = threshold
        self.severity = severity
        self.comparison = comparison
        self.duration_seconds = duration_seconds
        self.message_template = message_template
        self.first_triggered: Optional[float] = None
        self.last_triggered: Optional[float] = None
    
    def check(self, value: float) -> bool:
        """检查是否触发"""
        triggered = False
        
        if self.comparison == "gt":
            triggered = value > self.threshold
        elif self.comparison == "lt":
            triggered = value < self.threshold
        elif self.comparison == "eq":
            triggered = value == self.threshold
        elif self.comparison == "neq":
            triggered = value != self.threshold
        
        now = time.time()
        
        if triggered:
            if self.first_triggered is None:
                self.first_triggered = now
            self.last_triggered = now
            
            # 检查持续时间
            return (now - self.first_triggered) >= self.duration_seconds
        else:
            self.first_triggered = None
            return False
    
    def format_message(self, value: float) -> str:
        """格式化消息"""
        return self.message_template.format(
            metric=self.metric_name,
            value=f"{value:.2f}",
            threshold=self.threshold
        )


class SmartPredictor:
    """智能预测器"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage = TimeSeriesStore()
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / ".claw" / "metrics"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        
        self._lock = threading.RLock()
        self._check_interval: int = 30  # 秒
        self._check_timer: Optional[threading.Timer] = None
        
        # 启动检查循环
        self._start_check_loop()
        
        # 加载历史数据
        self._load_history()
    
    def record(self, name: str, value: float, 
               metric_type: MetricType = MetricType.GAUGE,
               labels: Optional[Dict[str, str]] = None):
        """记录指标"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            labels=labels or {}
        )
        
        self.storage.add(metric)
        self._persist_metric(metric)
    
    def add_alert_rule(self, rule: AlertRule):
        """添加预警规则"""
        self.alert_rules.append(rule)
    
    def add_alert_handler(self, handler: Callable):
        """添加预警处理器"""
        self.alert_handlers.append(handler)
    
    def check_alerts(self):
        """检查预警"""
        with self._lock:
            for rule in self.alert_rules:
                latest = self.storage.get_latest(rule.metric_name)
                
                if latest is None:
                    continue
                
                triggered = rule.check(latest.value)
                alert_id = f"{rule.name}:{rule.metric_name}"
                
                if triggered:
                    if alert_id not in self.active_alerts:
                        # 创建新预警
                        alert = Alert(
                            alert_id=alert_id,
                            name=rule.name,
                            severity=rule.severity,
                            message=rule.format_message(latest.value),
                            metric_name=rule.metric_name,
                            current_value=latest.value,
                            threshold=rule.threshold
                        )
                        
                        self.active_alerts[alert_id] = alert
                        
                        # 通知处理器
                        for handler in self.alert_handlers:
                            try:
                                handler(alert)
                            except Exception:
                                pass
                
                else:
                    if alert_id in self.active_alerts:
                        # 解决预警
                        alert = self.active_alerts[alert_id]
                        alert.resolved = True
                        alert.resolved_at = time.time()
                        del self.active_alerts[alert_id]
    
    def predict(self, metric_name: str, 
                horizon_minutes: int = 10) -> Optional[Prediction]:
        """预测未来值"""
        series = self.storage.get_series(metric_name)
        
        if len(series) < 5:
            return None
        
        # 简单线性回归预测
        values = [m.value for m in series[-20:]]  # 使用最近20个点
        n = len(values)
        
        if n < 2:
            return None
        
        # 计算趋势
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        # 计算斜率
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 预测
        future_x = n + horizon_minutes
        predicted = y_mean + slope * (future_x - x_mean)
        
        # 计算置信度（基于方差）
        if n > 2:
            try:
                variance = statistics.variance(values)
                confidence = max(0, 1 - variance / (y_mean ** 2 + 1)) if y_mean != 0 else 0.5
            except statistics.StatisticsError:
                confidence = 0.5
        else:
            confidence = 0.5
        
        # 趋势
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return Prediction(
            metric_name=metric_name,
            predicted_value=predicted,
            confidence=confidence,
            horizon_minutes=horizon_minutes,
            trend=trend
        )
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活动预警"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_metric_stats(self, metric_name: str) -> Dict:
        """获取指标统计"""
        return self.storage.get_statistics(metric_name)
    
    def _start_check_loop(self):
        """启动检查循环"""
        def check_and_reschedule():
            self.check_alerts()
            self._start_check_loop()
        
        self._check_timer = threading.Timer(self._check_interval, check_and_reschedule)
        self._check_timer.daemon = True
        self._check_timer.start()
    
    def _persist_metric(self, metric: Metric):
        """持久化指标"""
        filename = f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        filepath = self.storage_dir / filename
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(metric.to_dict(), ensure_ascii=False) + "\n")
    
    def _load_history(self):
        """加载历史数据"""
        # 简化：仅加载今天的数据
        filename = f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        filepath = self.storage_dir / filename
        
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        metric = Metric(
                            name=data["name"],
                            value=data["value"],
                            timestamp=data["timestamp"],
                            labels=data.get("labels", {}),
                            metric_type=MetricType(data.get("type", "gauge"))
                        )
                        self.storage.add(metric)
            except Exception:
                pass
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = [
            "=" * 60,
            "Smart Predictor Report",
            "=" * 60,
            f"Active Alerts: {len(self.active_alerts)}",
            f"Alert Rules: {len(self.alert_rules)}",
            f"Metrics Tracked: {len(self.storage.data)}",
            "-" * 60,
            "Active Alerts:"
        ]
        
        if self.active_alerts:
            for alert in self.active_alerts.values():
                lines.append(f"  [{alert.severity.value.upper()}] {alert.name}")
                lines.append(f"    {alert.message}")
        else:
            lines.append("  None")
        
        lines.extend(["-" * 60, "Metric Statistics:"])
        
        for name in list(self.storage.data.keys())[:5]:  # 显示前5个
            stats = self.storage.get_statistics(name)
            if stats:
                lines.append(f"  {name}:")
                lines.append(f"    Latest: {stats['latest']:.2f}, Mean: {stats['mean']:.2f}")
                
                # 预测
                pred = self.predict(name, horizon_minutes=10)
                if pred:
                    lines.append(f"    Predicted (10min): {pred.predicted_value:.2f} ({pred.trend})")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def close(self):
        """关闭"""
        if self._check_timer:
            self._check_timer.cancel()


# 便捷函数
def create_default_predictor() -> SmartPredictor:
    """创建默认预测器"""
    predictor = SmartPredictor()
    
    # 添加默认预警规则
    predictor.add_alert_rule(AlertRule(
        name="high_memory_usage",
        metric_name="memory_usage_percent",
        threshold=85.0,
        severity=AlertSeverity.WARNING,
        comparison="gt",
        message_template="High memory usage: {value}% (threshold: {threshold}%)"
    ))
    
    predictor.add_alert_rule(AlertRule(
        name="disk_space_low",
        metric_name="disk_free_gb",
        threshold=5.0,
        severity=AlertSeverity.CRITICAL,
        comparison="lt",
        message_template="Low disk space: {value}GB free (threshold: {threshold}GB)"
    ))
    
    predictor.add_alert_rule(AlertRule(
        name="high_error_rate",
        metric_name="error_rate",
        threshold=0.1,
        severity=AlertSeverity.WARNING,
        comparison="gt",
        message_template="High error rate: {value} (threshold: {threshold})"
    ))
    
    return predictor


# 测试代码
if __name__ == "__main__":
    print("Smart Predictor Test")
    print("=" * 60)
    
    predictor = create_default_predictor()
    
    # 模拟记录一些指标
    print("\nRecording metrics...")
    for i in range(20):
        predictor.record("memory_usage_percent", 60 + i * 2)
        predictor.record("disk_free_gb", 10 - i * 0.2)
        time.sleep(0.01)  # 短暂延迟
    
    # 检查预警
    predictor.check_alerts()
    
    # 获取活动预警
    active = predictor.get_active_alerts()
    print(f"\nActive alerts: {len(active)}")
    for alert in active:
        print(f"  [{alert.severity.value}] {alert.name}: {alert.message}")
    
    # 预测
    print("\nPredictions:")
    pred = predictor.predict("memory_usage_percent", horizon_minutes=10)
    if pred:
        print(f"  memory_usage_percent in 10min: {pred.predicted_value:.2f} ({pred.trend}, confidence: {pred.confidence:.2f})")
    
    # 统计
    print("\nStatistics:")
    stats = predictor.get_metric_stats("memory_usage_percent")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # 报告
    print("\n" + predictor.generate_report())
    
    predictor.close()
    print("\n" + "=" * 60)
    print("Smart Predictor module ready!")
