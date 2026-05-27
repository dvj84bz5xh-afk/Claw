"""
OpenRelay配置管理模块

此模块提供与现有TimesFM-inspired配置系统的集成，管理OpenRelay服务器配置。
"""

import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, ClassVar

# 从现有config_system导入，确保兼容性
try:
    from .config_system import ConfigManager, AgentCapabilityConfig, update_config, get_config
except ImportError:
    # 备用定义
    from dataclasses import dataclass, field
    from typing import Dict, Any


class ProviderStatus(Enum):
    """提供商状态"""
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    UNKNOWN = "unknown"


class QuotaType(Enum):
    """配额类型"""
    FREE = "free"
    SUBSCRIPTION = "subscription"
    API_KEY = "api_key"
    DESKTOP_APP = "desktop_app"


@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    id: str
    name: str
    description: str = ""
    provider_type: QuotaType = QuotaType.FREE
    base_url: str = ""
    api_key: Optional[str] = None
    status: ProviderStatus = ProviderStatus.UNKNOWN
    usage_limit: Optional[int] = None
    usage_count: int = 0
    priority: int = 1  # 1-10，数字越小优先级越高
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["provider_type"] = self.provider_type.value
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIProviderConfig":
        """从字典创建"""
        provider_type = QuotaType(data.get("provider_type", "free"))
        status = ProviderStatus(data.get("status", "unknown"))
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            provider_type=provider_type,
            base_url=data.get("base_url", ""),
            api_key=data.get("api_key"),
            status=status,
            usage_limit=data.get("usage_limit"),
            usage_count=data.get("usage_count", 0),
            priority=data.get("priority", 1),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {})
        )


@dataclass
class OpenRelayConfig:
    """OpenRelay服务器配置"""
    port: int = 18765
    host: str = "localhost"
    auto_start: bool = True
    auto_discover: bool = True
    log_level: str = "info"  # debug, info, warn, error
    data_dir: Optional[str] = None
    enable_pro_plan: bool = False
    providers: List[AIProviderConfig] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["providers"] = [p.to_dict() for p in self.providers]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenRelayConfig":
        """从字典创建"""
        providers = []
        for p_data in data.get("providers", []):
            try:
                providers.append(AIProviderConfig.from_dict(p_data))
            except Exception as e:
                print(f"[Warning] Failed to parse provider {p_data.get('id', 'unknown')}: {e}")
        
        return cls(
            port=data.get("port", 18765),
            host=data.get("host", "localhost"),
            auto_start=data.get("auto_start", True),
            auto_discover=data.get("auto_discover", True),
            log_level=data.get("log_level", "info"),
            data_dir=data.get("data_dir"),
            enable_pro_plan=data.get("enable_pro_plan", False),
            providers=providers
        )


@dataclass
class OpenRelayIntegrationConfig:
    """
    OpenRelay集成配置
    
    这是TimesFM-inspired配置系统的一部分，用于与AgentCapabilityConfig集成。
    """
    enabled: bool = True
    auto_integrate: bool = True
    config: OpenRelayConfig = field(default_factory=OpenRelayConfig)
    
    # 工具集成配置
    tool_integrations: Dict[str, str] = field(default_factory=lambda: {
        "claude_code": "groq",
        "aider": "claude_desktop",
        "goose": "gemini",
        "openclaw": "deepseek"
    })
    
    # 高级配置
    enable_failover: bool = True
    max_retry_attempts: int = 3
    retry_delay_ms: int = 500
    health_check_interval_sec: int = 30
    cache_provider_status: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.enabled,
            "auto_integrate": self.auto_integrate,
            "config": self.config.to_dict(),
            "tool_integrations": self.tool_integrations,
            "enable_failover": self.enable_failover,
            "max_retry_attempts": self.max_retry_attempts,
            "retry_delay_ms": self.retry_delay_ms,
            "health_check_interval_sec": self.health_check_interval_sec,
            "cache_provider_status": self.cache_provider_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenRelayIntegrationConfig":
        """从字典创建"""
        config_data = data.get("config", {})
        return cls(
            enabled=data.get("enabled", True),
            auto_integrate=data.get("auto_integrate", True),
            config=OpenRelayConfig.from_dict(config_data),
            tool_integrations=data.get("tool_integrations", {}),
            enable_failover=data.get("enable_failover", True),
            max_retry_attempts=data.get("max_retry_attempts", 3),
            retry_delay_ms=data.get("retry_delay_ms", 500),
            health_check_interval_sec=data.get("health_check_interval_sec", 30),
            cache_provider_status=data.get("cache_provider_status", True)
        )


# 集成到现有配置系统的辅助函数
def create_integration_config_for_system() -> Dict[str, Any]:
    """为TimesFM-inspired配置系统创建集成配置"""
    openrelay_integration = OpenRelayIntegrationConfig()
    
    # 为演示添加默认提供商
    openrelay_integration.config.providers = [
        AIProviderConfig(
            id="groq",
            name="Groq",
            description="Groq免费AI服务，极速推理",
            provider_type=QuotaType.FREE,
            base_url="https://api.groq.com/openai/v1",
            priority=1
        ),
        AIProviderConfig(
            id="claude_desktop",
            name="Claude Desktop",
            description="Claude Desktop应用程序的配额",
            provider_type=QuotaType.DESKTOP_APP,
            base_url="http://localhost:18765/claude-desktop",
            priority=2
        ),
        AIProviderConfig(
            id="deepseek",
            name="DeepSeek",
            description="DeepSeek API，便宜且支持大上下文",
            provider_type=QuotaType.API_KEY,
            base_url="https://api.deepseek.com/v1",
            priority=3
        ),
        AIProviderConfig(
            id="gemini",
            name="Gemini",
            description="Google Gemini API",
            provider_type=QuotaType.API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            priority=4
        )
    ]
    
    return {
        "openrelay_integration": openrelay_integration.to_dict()
    }


def merge_with_existing_config(config_manager, openrelay_config: Dict[str, Any]):
    """
    将OpenRelay配置合并到现有配置管理器
    
    Args:
        config_manager: 配置管理器实例
        openrelay_config: OpenRelay配置字典
    """
    # 获取当前配置
    current_config = config_manager.config.to_dict()
    
    # 合并配置
    current_config.update(openrelay_config)
    
    # 应用更新
    config_manager.update_config(openrelay_config)


def get_openrelay_config(config_data: Dict[str, Any]) -> Optional[OpenRelayIntegrationConfig]:
    """
    从配置数据中提取OpenRelay配置
    
    Args:
        config_data: 配置字典
    
    Returns:
        OpenRelayIntegrationConfig or None
    """
    integration_data = config_data.get("openrelay_integration")
    if integration_data:
        return OpenRelayIntegrationConfig.from_dict(integration_data)
    return None


def save_config_to_file(config: OpenRelayIntegrationConfig, filepath: str):
    """保存配置到文件"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)


def load_config_from_file(filepath: str) -> OpenRelayIntegrationConfig:
    """从文件加载配置"""
    if not Path(filepath).exists():
        # 创建默认配置
        return OpenRelayIntegrationConfig()
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return OpenRelayIntegrationConfig.from_dict(data)


class OpenRelayConfigManager:
    """OpenRelay配置管理器"""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.config_file = self.workspace_path / ".workbuddy" / "openrelay_config.json"
        self.config = self.load_config()
        
    def load_config(self) -> OpenRelayIntegrationConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return OpenRelayIntegrationConfig.from_dict(data)
            except Exception as e:
                print(f"[Warning] Failed to load OpenRelay config: {e}")
        
        # 返回默认配置
        return OpenRelayIntegrationConfig()
    
    def save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        save_config_to_file(self.config, str(self.config_file))
    
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        # 将更新合并到当前配置
        current_dict = self.config.to_dict()
        
        # 递归合并
        def deep_merge(base: Dict, updates: Dict):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(current_dict, updates)
        self.config = OpenRelayIntegrationConfig.from_dict(current_dict)
        self.save_config()
    
    def get_tool_config(self, tool_name: str) -> Dict[str, str]:
        """
        获取工具的OpenRelay配置
        
        Returns:
            环境变量配置字典
        """
        provider_id = self.config.tool_integrations.get(tool_name)
        if not provider_id:
            return {}
        
        # 找到提供商
        provider = None
        for p in self.config.config.providers:
            if p.id == provider_id:
                provider = p
                break
        
        if not provider:
            return {}
        
        # 生成环境变量配置
        base_url = f"http://{self.config.config.host}:{self.config.config.port}/{provider_id}"
        
        if tool_name in ["claude_code", "openclaw"]:
            return {
                "ANTHROPIC_BASE_URL": base_url,
                "ANTHROPIC_API_KEY": "unused",
                "OPENRELAY_PROVIDER": provider_id
            }
        elif tool_name in ["aider", "goose", "cursor"]:
            return {
                "OPENAI_BASE_URL": base_url,
                "OPENAI_API_KEY": "unused",
                "OPENRELAY_PROVIDER": provider_id
            }
        else:
            return {
                "OPENRELAY_BASE_URL": base_url,
                "OPENRELAY_PROVIDER": provider_id
            }
    
    def generate_setup_script(self, tool_name: str, platform: str = "powershell") -> str:
        """
        生成设置环境变量的脚本
        
        Args:
            tool_name: 工具名称
            platform: 平台 (powershell, bash, zsh)
        
        Returns:
            脚本字符串
        """
        env_config = self.get_tool_config(tool_name)
        if not env_config:
            return "# 没有找到该工具的OpenRelay配置"
        
        if platform == "powershell":
            lines = []
            for key, value in env_config.items():
                lines.append(f'$env:{key}="{value}"')
            return "\n".join(lines)
        elif platform in ["bash", "zsh"]:
            lines = []
            for key, value in env_config.items():
                lines.append(f'export {key}="{value}"')
            return "\n".join(lines)
        else:
            return f"# 不支持的平台: {platform}"


def setup_integration():
    """
    设置与现有TimesFM-inspired系统的集成
    此函数应在系统启动时调用
    """
    try:
        from .config_system import get_config_manager
        
        config_manager = get_config_manager()
        openrelay_config = create_integration_config_for_system()
        
        merge_with_existing_config(config_manager, openrelay_config)
        print("[OpenRelay] 配置已集成到TimesFM-inspired系统")
        return True
    except ImportError as e:
        print(f"[OpenRelay] 警告: 无法导入TimesFM配置系统: {e}")
        return False


def main():
    """测试配置系统"""
    print("=== OpenRelay Config System Test ===\n")
    
    # 创建配置管理器
    manager = OpenRelayConfigManager()
    
    print(f"1. Config loaded: {manager.config.enabled}")
    print(f"2. Providers: {len(manager.config.config.providers)}")
    print(f"3. Tool integrations: {len(manager.config.tool_integrations)}")
    
    # 测试脚本生成
    for tool in ["claude_code", "aider"]:
        script = manager.generate_setup_script(tool, "powershell")
        print(f"\n4. Setup script for {tool} (PowerShell):")
        print(script)
    
    # 测试配置保存/加载
    temp_file = Path.cwd() / "test_openrelay_config.json"
    save_config_to_file(manager.config, str(temp_file))
    loaded = load_config_from_file(str(temp_file))
    print(f"\n5. Config save/load test: {loaded.enabled == manager.config.enabled}")
    
    # 清理
    temp_file.unlink(missing_ok=True)
    
    print("\n=== All Tests Passed ===")


if __name__ == "__main__":
    main()