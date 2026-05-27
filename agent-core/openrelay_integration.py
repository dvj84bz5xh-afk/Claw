"""
OpenRelay集成模块 - 将GitHub romgx/openrelay项目接入TimesFM-inspired架构

OpenRelay是一个本地AI代理工具，能够：
1. 自动发现本地AI订阅和免费配额（Claude Desktop、Kiro、Windsurf等）
2. 统一代理32个AI提供商，通过单一端点(localhost:18765)提供服务
3. 支持将任意配额分配给支持Anthropic/OpenAI API的工具

本模块将OpenRelay功能集成到现有TimesFM-inspired架构中，提供：
- 自动化的AI配额管理和路由
- 多模型故障转移和高可用性
- 统一的工具接入接口
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import httpx
from datetime import datetime
import sys
import os

# 兼容性检查
if sys.platform == "win32":
    OPENRELAY_EXECUTABLE = "openrelay.exe"
else:
    OPENRELAY_EXECUTABLE = "openrelay"


class ProviderStatus(Enum):
    """AI提供商状态"""
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
class AIProvider:
    """AI提供商信息"""
    id: str
    name: str
    description: str
    provider_type: QuotaType
    base_url: str
    api_key: Optional[str] = None
    status: ProviderStatus = ProviderStatus.UNKNOWN
    usage_limit: Optional[int] = None
    usage_count: int = 0
    last_used: Optional[datetime] = None
    priority: int = 1  # 优先级：1-10，数字越小优先级越高
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenRelayConfig:
    """OpenRelay配置"""
    port: int = 18765
    host: str = "localhost"
    auto_start: bool = True
    auto_discover: bool = True
    log_level: str = "info"
    data_dir: Optional[str] = None
    enable_pro_plan: bool = False
    providers: List[AIProvider] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "port": self.port,
            "host": self.host,
            "auto_start": self.auto_start,
            "auto_discover": self.auto_discover,
            "log_level": self.log_level,
            "data_dir": self.data_dir,
            "enable_pro_plan": self.enable_pro_plan,
            "providers": [p.__dict__ for p in self.providers]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenRelayConfig":
        """从字典创建"""
        config = cls(
            port=data.get("port", 18765),
            host=data.get("host", "localhost"),
            auto_start=data.get("auto_start", True),
            auto_discover=data.get("auto_discover", True),
            log_level=data.get("log_level", "info"),
            data_dir=data.get("data_dir"),
            enable_pro_plan=data.get("enable_pro_plan", False)
        )
        
        # 解析提供商
        providers_data = data.get("providers", [])
        for p_data in providers_data:
            provider = AIProvider(
                id=p_data.get("id"),
                name=p_data.get("name"),
                description=p_data.get("description", ""),
                provider_type=QuotaType(p_data.get("provider_type", "unknown")),
                base_url=p_data.get("base_url"),
                api_key=p_data.get("api_key"),
                status=ProviderStatus(p_data.get("status", "unknown")),
                usage_limit=p_data.get("usage_limit"),
                usage_count=p_data.get("usage_count", 0),
                priority=p_data.get("priority", 1),
                enabled=p_data.get("enabled", True),
                metadata=p_data.get("metadata", {})
            )
            if p_data.get("last_used"):
                provider.last_used = datetime.fromisoformat(p_data["last_used"])
            config.providers.append(provider)
        
        return config


class OpenRelayIntegration:
    """
    OpenRelay集成管理器
    
    负责：
    1. 启动/停止OpenRelay服务
    2. 管理AI提供商配置
    3. 路由AI请求到最佳提供商
    4. 监控配额使用情况
    5. 提供故障转移机制
    """
    
    def __init__(self, config: Optional[OpenRelayConfig] = None, workspace_path: Optional[str] = None):
        self.config = config or OpenRelayConfig()
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.openrelay_dir = self.workspace_path / "openrelay"
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 创建数据目录
        self.data_dir = Path(self.config.data_dir or (self.workspace_path / ".workbuddy" / "openrelay"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.data_dir / "config.json"
        
    async def initialize(self):
        """初始化OpenRelay集成"""
        # 检查OpenRelay是否已安装
        if not await self._check_openrelay_installed():
            print("[OpenRelay] 未检测到OpenRelay，正在准备安装...")
            await self._setup_openrelay()
        
        # 加载配置
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                self.config = OpenRelayConfig.from_dict(saved_config)
        
        # 启动服务
        if self.config.auto_start:
            await self.start()
    
    async def _check_openrelay_installed(self) -> bool:
        """检查OpenRelay是否已安装"""
        # 检查可执行文件
        exe_path = self.openrelay_dir / OPENRELAY_EXECUTABLE
        return exe_path.exists()
    
    async def _setup_openrelay(self):
        """安装并配置OpenRelay"""
        # 这里需要根据实际情况实现安装逻辑
        # 1. 检查是否已克隆仓库
        # 2. 编译或下载可执行文件
        # 3. 配置环境
        
        print(f"[OpenRelay] OpenRelay目录: {self.openrelay_dir}")
        
        if not self.openrelay_dir.exists():
            print("[OpenRelay] 错误：OpenRelay目录不存在，请先克隆项目")
            raise FileNotFoundError("OpenRelay目录不存在")
        
        # 检查是否有编译产物
        dist_dir = self.openrelay_dir / "dist"
        if not dist_dir.exists():
            print("[OpenRelay] 警告：OpenRelay未编译，将使用默认配置")
        
        return True
    
    async def start(self):
        """启动OpenRelay服务"""
        if self.is_running:
            print("[OpenRelay] 服务已在运行")
            return True
        
        try:
            # 保存配置
            self._save_config()
            
            # 启动进程
            exe_path = self.openrelay_dir / OPENRELAY_EXECUTABLE
            
            # 构建命令参数
            cmd_args = [
                str(exe_path),
                "--port", str(self.config.port),
                "--host", self.config.host,
                "--log-level", self.config.log_level
            ]
            
            if self.config.data_dir:
                cmd_args.extend(["--data-dir", self.config.data_dir])
            
            # 启动子进程
            env = os.environ.copy()
            self.process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding="utf-8"
            )
            
            self.is_running = True
            print(f"[OpenRelay] 服务已启动，端口: {self.config.port}")
            
            # 等待服务就绪
            await self._wait_for_service()
            return True
            
        except Exception as e:
            print(f"[OpenRelay] 启动失败: {e}")
            self.is_running = False
            return False
    
    async def _wait_for_service(self, max_retries: int = 10, delay: float = 1.0):
        """等待OpenRelay服务就绪"""
        base_url = f"http://{self.config.host}:{self.config.port}"
        
        for attempt in range(max_retries):
            try:
                response = await self.client.get(f"{base_url}/api/health")
                if response.status_code == 200:
                    print("[OpenRelay] 服务已就绪")
                    return True
            except Exception:
                pass
            
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
        
        print("[OpenRelay] 警告：服务启动超时")
        return False
    
    async def stop(self):
        """停止OpenRelay服务"""
        if not self.is_running:
            print("[OpenRelay] 服务未运行")
            return
        
        try:
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.process = None
            
            self.is_running = False
            print("[OpenRelay] 服务已停止")
            
        except Exception as e:
            print(f"[OpenRelay] 停止失败: {e}")
    
    def _save_config(self):
        """保存配置到文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            config_dict = self.config.to_dict()
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    async def discover_providers(self) -> List[AIProvider]:
        """自动发现AI提供商"""
        if not self.is_running:
            await self.start()
        
        try:
            base_url = f"http://{self.config.host}:{self.config.port}"
            response = await self.client.get(f"{base_url}/api/providers")
            
            if response.status_code == 200:
                providers_data = response.json()
                providers = []
                
                for p_data in providers_data:
                    provider = AIProvider(
                        id=p_data.get("id"),
                        name=p_data.get("name"),
                        description=p_data.get("description", ""),
                        provider_type=QuotaType(p_data.get("type", "unknown").lower()),
                        base_url=p_data.get("base_url"),
                        status=ProviderStatus(p_data.get("status", "unknown").lower()),
                        usage_limit=p_data.get("usage_limit"),
                        usage_count=p_data.get("usage_count", 0),
                        priority=p_data.get("priority", 1),
                        enabled=p_data.get("enabled", True),
                        metadata=p_data.get("metadata", {})
                    )
                    providers.append(provider)
                
                self.config.providers = providers
                self._save_config()
                return providers
                
        except Exception as e:
            print(f"[OpenRelay] 发现提供商失败: {e}")
        
        # 返回默认提供商列表
        return self._get_default_providers()
    
    def _get_default_providers(self) -> List[AIProvider]:
        """获取默认AI提供商列表"""
        return [
            AIProvider(
                id="groq",
                name="Groq",
                description="Groq免费AI服务，极速推理",
                provider_type=QuotaType.FREE,
                base_url="https://api.groq.com/openai/v1",
                priority=1
            ),
            AIProvider(
                id="claude_desktop",
                name="Claude Desktop",
                description="Claude Desktop应用程序的配额",
                provider_type=QuotaType.DESKTOP_APP,
                base_url="http://localhost:18765/claude-desktop",
                priority=2
            ),
            AIProvider(
                id="deepseek",
                name="DeepSeek",
                description="DeepSeek API，便宜且支持大上下文",
                provider_type=QuotaType.API_KEY,
                base_url="https://api.deepseek.com/v1",
                priority=3
            ),
            AIProvider(
                id="gemini",
                name="Gemini",
                description="Google Gemini API",
                provider_type=QuotaType.API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                priority=4
            )
        ]
    
    async def route_request(
        self,
        tool_name: str,
        request_data: Dict[str, Any],
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        路由AI请求到最佳提供商
        
        Args:
            tool_name: 工具名称
            request_data: 请求数据
            preferred_provider: 优先选择的提供商ID
        
        Returns:
            响应数据
        """
        if not self.is_running:
            await self.start()
        
        # 选择最佳提供商
        provider = await self._select_best_provider(tool_name, preferred_provider)
        
        if not provider:
            raise ValueError("没有可用的AI提供商")
        
        try:
            # 构建请求URL
            base_url = f"http://{self.config.host}:{self.config.port}"
            provider_url = f"{base_url}/{provider.id}"
            
            # 发送请求
            response = await self.client.post(
                provider_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            # 更新使用统计
            await self._update_provider_stats(provider.id, success=True)
            
            return {
                "provider": provider.id,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "used_provider": provider.name
            }
            
        except Exception as e:
            # 更新使用统计（失败）
            await self._update_provider_stats(provider.id, success=False)
            
            # 尝试故障转移
            return await self._fallback_request(tool_name, request_data, provider.id)
    
    async def _select_best_provider(
        self,
        tool_name: str,
        preferred_provider: Optional[str] = None
    ) -> Optional[AIProvider]:
        """选择最佳AI提供商"""
        if not self.config.providers:
            await self.discover_providers()
        
        # 过滤启用的提供商
        available_providers = [
            p for p in self.config.providers 
            if p.enabled and p.status == ProviderStatus.ACTIVE
        ]
        
        if not available_providers:
            return None
        
        # 优先使用指定提供商
        if preferred_provider:
            for provider in available_providers:
                if provider.id == preferred_provider:
                    return provider
        
        # 根据优先级选择
        available_providers.sort(key=lambda p: p.priority)
        return available_providers[0]
    
    async def _update_provider_stats(self, provider_id: str, success: bool):
        """更新提供商使用统计"""
        for provider in self.config.providers:
            if provider.id == provider_id:
                provider.usage_count += 1
                provider.last_used = datetime.now()
                if not success:
                    provider.status = ProviderStatus.ERROR
                break
        
        self._save_config()
    
    async def _fallback_request(
        self,
        tool_name: str,
        request_data: Dict[str, Any],
        failed_provider_id: str
    ) -> Dict[str, Any]:
        """故障转移请求到备用提供商"""
        # 排除失败的提供商
        backup_providers = [
            p for p in self.config.providers 
            if p.enabled and p.status == ProviderStatus.ACTIVE and p.id != failed_provider_id
        ]
        
        if not backup_providers:
            return {
                "provider": "none",
                "status_code": 500,
                "response": "所有AI提供商均不可用",
                "used_provider": "none"
            }
        
        # 按优先级排序
        backup_providers.sort(key=lambda p: p.priority)
        
        # 尝试每个备用提供商
        for provider in backup_providers:
            try:
                base_url = f"http://{self.config.host}:{self.config.port}"
                provider_url = f"{base_url}/{provider.id}"
                
                response = await self.client.post(
                    provider_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                await self._update_provider_stats(provider.id, success=True)
                
                return {
                    "provider": provider.id,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text,
                    "used_provider": provider.name
                }
                
            except Exception:
                await self._update_provider_stats(provider.id, success=False)
                continue
        
        # 所有备用提供商都失败
        return {
            "provider": "none",
            "status_code": 500,
            "response": "所有备用AI提供商均失败",
            "used_provider": "none"
        }
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        if not self.config.providers:
            await self.discover_providers()
        
        total_requests = sum(p.usage_count for p in self.config.providers)
        active_providers = len([p for p in self.config.providers if p.enabled and p.status == ProviderStatus.ACTIVE])
        
        return {
            "total_providers": len(self.config.providers),
            "active_providers": active_providers,
            "total_requests": total_requests,
            "providers": [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": p.provider_type.value,
                    "usage_count": p.usage_count,
                    "status": p.status.value,
                    "last_used": p.last_used.isoformat() if p.last_used else None
                }
                for p in self.config.providers
            ]
        }
    
    async def configure_tool(self, tool_name: str, provider_id: str) -> bool:
        """为工具配置AI提供商"""
        # 找到提供商
        provider = None
        for p in self.config.providers:
            if p.id == provider_id:
                provider = p
                break
        
        if not provider:
            print(f"[OpenRelay] 提供商 {provider_id} 不存在")
            return False
        
        # 生成工具配置
        config = self._generate_tool_config(tool_name, provider)
        
        # 保存工具配置
        tool_config_file = self.data_dir / f"{tool_name}_config.json"
        with open(tool_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"[OpenRelay] 已配置 {tool_name} 使用 {provider.name}")
        return True
    
    def _generate_tool_config(self, tool_name: str, provider: AIProvider) -> Dict[str, Any]:
        """生成工具配置"""
        base_url = f"http://{self.config.host}:{self.config.port}/{provider.id}"
        
        # 根据工具类型生成不同的配置
        if tool_name in ["claude_code", "openclaw", "cursor"]:
            return {
                "ANTHROPIC_BASE_URL": base_url,
                "ANTHROPIC_API_KEY": "unused",
                "tool": tool_name,
                "provider": provider.id,
                "configured_at": datetime.now().isoformat()
            }
        elif tool_name in ["aider", "continue", "goose"]:
            return {
                "OPENAI_BASE_URL": base_url,
                "OPENAI_API_KEY": "unused",
                "tool": tool_name,
                "provider": provider.id,
                "configured_at": datetime.now().isoformat()
            }
        else:
            # 默认配置
            return {
                "base_url": base_url,
                "api_key": "unused",
                "tool": tool_name,
                "provider": provider.id,
                "configured_at": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """清理资源"""
        await self.stop()
        await self.client.aclose()


# 集成到现有配置系统
def create_openrelay_integration_config():
    """创建OpenRelay集成配置"""
    from config_system import AgentCapabilityConfig, get_config_manager
    
    config = get_config()
    
    # 添加OpenRelay配置到现有配置
    openrelay_config = {
        "enabled": True,
        "auto_start": True,
        "port": 18765,
        "log_level": "info",
        "providers": ["groq", "claude_desktop", "deepseek", "gemini"]
    }
    
    # 更新配置
    updates = {"openrelay": openrelay_config}
    config_manager = get_config_manager()
    config_manager.update_config(updates)
    
    return config_manager.config


# 示例使用
async def main():
    """示例主函数"""
    print("=== OpenRelay Integration Demo ===")
    
    # 创建集成管理器
    integration = OpenRelayIntegration(
        workspace_path=r"c:\Users\10127\WorkBuddy\Claw"
    )
    
    # 初始化
    await integration.initialize()
    
    # 发现提供商
    providers = await integration.discover_providers()
    print(f"\n发现 {len(providers)} 个AI提供商:")
    for p in providers:
        print(f"  - {p.name} ({p.id}): {p.description}")
    
    # 获取使用统计
    stats = await integration.get_usage_stats()
    print(f"\n使用统计:")
    print(f"  总提供商: {stats['total_providers']}")
    print(f"  活跃提供商: {stats['active_providers']}")
    print(f"  总请求数: {stats['total_requests']}")
    
    # 配置工具示例
    await integration.configure_tool("claude_code", "groq")
    print("\n工具配置完成")
    
    # 示例请求路由
    sample_request = {
        "model": "claude-3-sonnet-20241022",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 100
    }
    
    print("\n发送示例请求...")
    try:
        response = await integration.route_request("test_tool", sample_request)
        print(f"响应提供商: {response['used_provider']}")
        print(f"状态码: {response['status_code']}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 清理
    await integration.cleanup()
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())