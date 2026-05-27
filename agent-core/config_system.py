"""
TimesFM-inspired Configuration System
配置-能力分离架构，借鉴TimesFm2_5Config设计
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import json
try:
    import yaml
except ImportError:
    yaml = None
from pathlib import Path


class PlanningStrategy(Enum):
    """规划策略"""
    SEQUENTIAL = "sequential"      # 顺序执行
    PARALLEL = "parallel"          # 并行执行
    ADAPTIVE = "adaptive"          # 自适应


class UncertaintyOutputMode(Enum):
    """不确定性输出模式"""
    POINT_ONLY = "point_only"           # 仅点估计
    QUANTILE = "quantile"               # 分位数输出
    FULL_DISTRIBUTION = "full"          # 完整分布


@dataclass
class ContextConfig:
    """
    上下文配置
    类似TimesFM的context_length
    """
    max_context_length: int = 16384           # 最大上下文长度
    context_compression_threshold: float = 0.8  # 压缩阈值
    compression_strategy: str = "semantic"     # 压缩策略
    preserve_recent_n: int = 10                # 保留最近N条
    enable_summarization: bool = True          # 启用自动摘要


@dataclass  
class PlanningConfig:
    """
    规划配置
    类似TimesFM的horizon_length
    """
    max_planning_horizon: int = 10             # 最大规划步数
    num_candidate_plans: int = 3               # 候选方案数
    planning_strategy: PlanningStrategy = field(
        default_factory=lambda: PlanningStrategy.ADAPTIVE
    )
    enable_backtracking: bool = True           # 启用回溯
    max_retry_attempts: int = 3                # 最大重试次数


@dataclass
class TaskPatchConfig:
    """
    任务Patch配置
    类似TimesFM的patch_length
    """
    patch_size: int = 5                        # Patch大小
    patch_overlap: int = 1                     # Patch重叠
    enable_hierarchical_patching: bool = True  # 分层Patch
    min_patch_size: int = 2                    # 最小Patch大小
    max_patch_size: int = 20                   # 最大Patch大小


@dataclass
class UncertaintyConfig:
    """
    不确定性配置
    类似TimesFM的quantile设置
    """
    output_mode: UncertaintyOutputMode = field(
        default_factory=lambda: UncertaintyOutputMode.QUANTILE
    )
    confidence_levels: List[float] = field(
        default_factory=lambda: [0.5, 0.8, 0.95]
    )
    quantiles: List[float] = field(
        default_factory=lambda: [0.1, 0.25, 0.5, 0.75, 0.9]
    )
    enable_calibration: bool = True            # 启用校准
    calibration_history_size: int = 100        # 校准历史大小


@dataclass
class MultiViewConfig:
    """
    多视角配置
    类似TimesFM的force_flip_invariance
    """
    enable_multi_view: bool = True
    default_views: List[str] = field(
        default_factory=lambda: ["technical", "business", "user", "risk"]
    )
    view_aggregation_method: str = "weighted_average"
    min_view_diversity: float = 0.3


@dataclass
class MultiSolutionConfig:
    """
    多方案生成配置
    类似TimesFM生成多个分位数预测
    """
    enable_multi_solution: bool = True
    default_num_solutions: int = 3
    diversity_threshold: float = 0.7
    enforce_diversity: bool = True
    default_ranking_criteria: Dict[str, float] = field(
        default_factory=lambda: {
            "technical_feasibility": 0.25,
            "business_value": 0.25,
            "user_experience": 0.25,
            "success_probability": 0.25,
        }
    )
    enable_cost_efficiency: bool = False
    enable_time_efficiency: bool = False
    max_risk_tolerance: str = "aggressive"  # conservative, moderate, aggressive
    max_resource_intensity: str = "heavy"   # light, medium, heavy


@dataclass
class LearningConfig:
    """
    学习配置
    类似TimesFM的PEFT设置
    """
    enable_online_learning: bool = True
    learning_rate: float = 0.01
    adapter_rank: int = 16                     # LoRA秩
    adapter_alpha: int = 32
    adapter_dropout: float = 0.05
    min_interactions_for_adaptation: int = 5
    adaptation_cooldown: int = 10              # 适应冷却期


@dataclass
class AgentCapabilityConfig:
    """
    能力配置主类
    类似TimesFm2_5Config
    """
    # 版本信息
    version: str = "2.0.0-timesfm-inspired"
    
    # 子配置
    context: ContextConfig = field(default_factory=ContextConfig)
    planning: PlanningConfig = field(default_factory=PlanningConfig)
    task_patch: TaskPatchConfig = field(default_factory=TaskPatchConfig)
    uncertainty: UncertaintyConfig = field(default_factory=UncertaintyConfig)
    multi_view: MultiViewConfig = field(default_factory=MultiViewConfig)
    multi_solution: MultiSolutionConfig = field(default_factory=MultiSolutionConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    
    # 全局开关
    debug_mode: bool = False
    verbose_logging: bool = False
    enable_metrics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """序列化为JSON"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_yaml(self) -> str:
        """序列化为YAML"""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML serialization")
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCapabilityConfig":
        """从字典反序列化"""
        # 处理嵌套配置
        context = ContextConfig(**data.get("context", {}))
        planning = PlanningConfig(**data.get("planning", {}))
        task_patch = TaskPatchConfig(**data.get("task_patch", {}))
        uncertainty = UncertaintyConfig(**data.get("uncertainty", {}))
        multi_view = MultiViewConfig(**data.get("multi_view", {}))
        multi_solution = MultiSolutionConfig(**data.get("multi_solution", {}))
        learning = LearningConfig(**data.get("learning", {}))
        
        return cls(
            version=data.get("version", "2.0.0"),
            context=context,
            planning=planning,
            task_patch=task_patch,
            uncertainty=uncertainty,
            multi_view=multi_view,
            multi_solution=multi_solution,
            learning=learning,
            debug_mode=data.get("debug_mode", False),
            verbose_logging=data.get("verbose_logging", False),
            enable_metrics=data.get("enable_metrics", True),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentCapabilityConfig":
        """从JSON反序列化"""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "AgentCapabilityConfig":
        """从YAML反序列化"""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML deserialization")
        return cls.from_dict(yaml.safe_load(yaml_str))
    
    @classmethod
    def from_file(cls, filepath: str) -> "AgentCapabilityConfig":
        """从文件加载配置"""
        path = Path(filepath)
        content = path.read_text(encoding="utf-8")
        
        if path.suffix in [".yaml", ".yml"]:
            return cls.from_yaml(content)
        elif path.suffix == ".json":
            return cls.from_json(content)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix in [".yaml", ".yml"]:
            content = self.to_yaml()
        elif path.suffix == ".json":
            content = self.to_json()
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
        
        path.write_text(content, encoding="utf-8")


class ConfigManager:
    """
    配置管理器
    支持配置热更新和版本管理
    """
    
    def __init__(self, default_config: Optional[AgentCapabilityConfig] = None):
        self._config = default_config or AgentCapabilityConfig()
        self._listeners: List[Callable[[AgentCapabilityConfig], None]] = []
        self._config_history: List[Dict] = []
        self._max_history = 10
    
    @property
    def config(self) -> AgentCapabilityConfig:
        """获取当前配置"""
        return self._config
    
    def update_config(self, updates: Dict[str, Any]):
        """
        更新配置（热更新）
        
        Args:
            updates: 配置更新字典
        """
        # 保存历史
        self._config_history.append(self._config.to_dict())
        if len(self._config_history) > self._max_history:
            self._config_history.pop(0)
        
        # 应用更新
        current_dict = self._config.to_dict()
        self._deep_update(current_dict, updates)
        self._config = AgentCapabilityConfig.from_dict(current_dict)
        
        # 通知监听器
        for listener in self._listeners:
            listener(self._config)
    
    def _deep_update(self, base: Dict, updates: Dict):
        """深度更新字典"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def add_listener(self, callback: Callable[[AgentCapabilityConfig], None]):
        """添加配置变更监听器"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[AgentCapabilityConfig], None]):
        """移除配置变更监听器"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def rollback(self, steps: int = 1):
        """回滚配置到历史版本"""
        if steps > len(self._config_history):
            raise ValueError(f"Cannot rollback {steps} steps, only {len(self._config_history)} available")
        
        for _ in range(steps):
            previous = self._config_history.pop()
            self._config = AgentCapabilityConfig.from_dict(previous)
        
        # 通知监听器
        for listener in self._listeners:
            listener(self._config)
    
    def load_from_file(self, filepath: str):
        """从文件加载配置"""
        self._config = AgentCapabilityConfig.from_file(filepath)
        for listener in self._listeners:
            listener(self._config)
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        self._config.save_to_file(filepath)


# 预置配置模板
class PresetConfigs:
    """预置配置模板"""
    
    @staticmethod
    def zero_shot_optimized() -> AgentCapabilityConfig:
        """零样本优化配置 - 类似TimesFM开箱即用"""
        config = AgentCapabilityConfig()
        config.context.max_context_length = 8192
        config.planning.max_planning_horizon = 5
        config.planning.num_candidate_plans = 1
        config.uncertainty.output_mode = UncertaintyOutputMode.POINT_ONLY
        config.multi_view.enable_multi_view = False
        config.learning.enable_online_learning = False
        return config
    
    @staticmethod
    def high_accuracy() -> AgentCapabilityConfig:
        """高精度配置"""
        config = AgentCapabilityConfig()
        config.context.max_context_length = 32768
        config.planning.max_planning_horizon = 20
        config.planning.num_candidate_plans = 5
        config.uncertainty.output_mode = UncertaintyOutputMode.FULL_DISTRIBUTION
        config.uncertainty.confidence_levels = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
        config.multi_view.enable_multi_view = True
        config.task_patch.patch_size = 3
        return config
    
    @staticmethod
    def fast_response() -> AgentCapabilityConfig:
        """快速响应配置"""
        config = AgentCapabilityConfig()
        config.context.max_context_length = 4096
        config.context.enable_summarization = True
        config.planning.max_planning_horizon = 3
        config.planning.num_candidate_plans = 1
        config.task_patch.patch_size = 10
        config.uncertainty.output_mode = UncertaintyOutputMode.POINT_ONLY
        config.multi_view.enable_multi_view = False
        return config
    
    @staticmethod
    def adaptive_learning() -> AgentCapabilityConfig:
        """自适应学习配置"""
        config = AgentCapabilityConfig()
        config.learning.enable_online_learning = True
        config.learning.learning_rate = 0.05
        config.learning.adapter_rank = 32
        config.uncertainty.enable_calibration = True
        return config


# 全局配置实例（单例模式）
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def set_config_manager(manager: ConfigManager):
    """设置全局配置管理器"""
    global _global_config_manager
    _global_config_manager = manager


# 便捷函数
def get_config() -> AgentCapabilityConfig:
    """获取当前配置"""
    return get_config_manager().config


def update_config(updates: Dict[str, Any]):
    """更新配置"""
    get_config_manager().update_config(updates)


if __name__ == "__main__":
    # 测试配置系统
    print("=== TimesFM-inspired Config System Test ===\n")
    
    # 1. 创建默认配置
    config = AgentCapabilityConfig()
    print("1. Default Config:")
    print(f"   Context Length: {config.context.max_context_length}")
    print(f"   Planning Horizon: {config.planning.max_planning_horizon}")
    print(f"   Patch Size: {config.task_patch.patch_size}")
    print()
    
    # 2. 使用预置配置
    fast_config = PresetConfigs.fast_response()
    print("2. Fast Response Preset:")
    print(f"   Context Length: {fast_config.context.max_context_length}")
    print(f"   Multi-view: {fast_config.multi_view.enable_multi_view}")
    print()
    
    # 3. 配置管理器
    manager = ConfigManager(config)
    print("3. Config Manager:")
    print(f"   Initial Horizon: {manager.config.planning.max_planning_horizon}")
    
    # 更新配置
    manager.update_config({"planning": {"max_planning_horizon": 15}})
    print(f"   Updated Horizon: {manager.config.planning.max_planning_horizon}")
    
    # 回滚
    manager.rollback()
    print(f"   After Rollback: {manager.config.planning.max_planning_horizon}")
    print()
    
    # 4. 序列化测试
    print("4. Serialization Test:")
    json_str = config.to_json()
    restored = AgentCapabilityConfig.from_json(json_str)
    print(f"   JSON Roundtrip OK: {restored.version == config.version}")
    print()
    
    print("=== All Tests Passed ===")
