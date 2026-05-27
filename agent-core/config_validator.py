#!/usr/bin/env python3
"""
Config Validator - 配置验证和诊断系统
验证配置完整性，提供诊断报告和自动修复建议

Phase 4 额外优化模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Callable
from enum import Enum
from pathlib import Path
import json
import os


class ValidationLevel(Enum):
    """验证级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConfigSource(Enum):
    """配置来源"""
    DEFAULT = "default"
    ENV = "environment"
    FILE = "file"
    CLI = "cli"
    OVERRIDDEN = "overridden"


@dataclass
class ValidationIssue:
    """验证问题"""
    path: str  # 配置路径，如 "session.retention_days"
    message: str
    level: ValidationLevel
    current_value: Any = None
    expected_value: Any = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    fix_action: Optional[Callable] = None
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "message": self.message,
            "level": self.level.value,
            "current_value": str(self.current_value)[:100] if self.current_value else None,
            "expected_value": str(self.expected_value)[:100] if self.expected_value else None,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable
        }


@dataclass
class ConfigSchema:
    """配置模式定义"""
    path: str
    type: type
    required: bool = True
    default: Any = None
    allowed_values: Optional[List[Any]] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    pattern: Optional[str] = None  # 正则表达式
    description: str = ""
    
    def validate(self, value: Any) -> List[ValidationIssue]:
        """验证值"""
        issues = []
        
        if value is None:
            if self.required:
                issues.append(ValidationIssue(
                    path=self.path,
                    message=f"Required config '{self.path}' is missing",
                    level=ValidationLevel.ERROR,
                    suggestion=f"Set {self.path} to a valid value"
                ))
            return issues
        
        # 类型检查
        if not isinstance(value, self.type):
            issues.append(ValidationIssue(
                path=self.path,
                message=f"Type mismatch: expected {self.type.__name__}, got {type(value).__name__}",
                level=ValidationLevel.ERROR,
                current_value=value,
                expected_value=f"<{self.type.__name__}>"
            ))
            return issues
        
        # 允许值检查
        if self.allowed_values and value not in self.allowed_values:
            issues.append(ValidationIssue(
                path=self.path,
                message=f"Value not in allowed set",
                level=ValidationLevel.WARNING,
                current_value=value,
                expected_value=self.allowed_values
            ))
        
        # 范围检查
        if self.min_value is not None and value < self.min_value:
            issues.append(ValidationIssue(
                path=self.path,
                message=f"Value below minimum",
                level=ValidationLevel.WARNING,
                current_value=value,
                expected_value=f">= {self.min_value}"
            ))
        
        if self.max_value is not None and value > self.max_value:
            issues.append(ValidationIssue(
                path=self.path,
                message=f"Value above maximum",
                level=ValidationLevel.WARNING,
                current_value=value,
                expected_value=f"<= {self.max_value}"
            ))
        
        return issues


# 预定义配置模式
DEFAULT_SCHEMAS = [
    # Session 配置
    ConfigSchema("session.retention_days", int, required=False, default=None,
                min_value=0, description="会话保留天数"),
    ConfigSchema("session.auto_cleanup", bool, required=False, default=False,
                description="是否自动清理"),
    ConfigSchema("session.max_sessions", int, required=False, default=None,
                min_value=1, description="最大会话数"),
    ConfigSchema("session.compression_enabled", bool, required=False, default=True,
                description="是否启用压缩"),
    ConfigSchema("session.persistence_enabled", bool, required=False, default=True,
                description="是否启用持久化"),
    
    # Cache 配置
    ConfigSchema("cache.max_size_mb", int, required=False, default=100,
                min_value=10, max_value=1000, description="缓存最大大小(MB)"),
    ConfigSchema("cache.ttl_seconds", int, required=False, default=3600,
                min_value=60, description="缓存TTL(秒)"),
    
    # Performance 配置
    ConfigSchema("performance.max_workers", int, required=False, default=4,
                min_value=1, max_value=16, description="最大工作线程数"),
    ConfigSchema("performance.timeout_seconds", int, required=False, default=30,
                min_value=1, description="默认超时(秒)"),
    
    # Logging 配置
    ConfigSchema("logging.level", str, required=False, default="INFO",
                allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"],
                description="日志级别"),
    ConfigSchema("logging.enable_audit", bool, required=False, default=True,
                description="启用审计日志"),
    
    # Security 配置
    ConfigSchema("security.permission_level", str, required=False, default="workspace",
                allowed_values=["read_only", "workspace", "danger"],
                description="权限级别"),
    ConfigSchema("security.require_confirmation", bool, required=False, default=True,
                description="危险操作需要确认"),
]


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, schemas: Optional[List[ConfigSchema]] = None):
        self.schemas = {s.path: s for s in (schemas or DEFAULT_SCHEMAS)}
        self.issues: List[ValidationIssue] = []
        self.custom_validators: List[Callable] = []
    
    def add_schema(self, schema: ConfigSchema):
        """添加模式"""
        self.schemas[schema.path] = schema
    
    def add_validator(self, validator: Callable):
        """添加自定义验证器"""
        self.custom_validators.append(validator)
    
    def validate(self, config: Dict, path_prefix: str = "") -> List[ValidationIssue]:
        """验证配置"""
        self.issues = []
        
        # 验证每个schema
        for schema_path, schema in self.schemas.items():
            value = self._get_nested_value(config, schema_path)
            issues = schema.validate(value)
            self.issues.extend(issues)
        
        # 检查未知配置
        unknown = self._find_unknown_keys(config, set(self.schemas.keys()))
        for key in unknown:
            self.issues.append(ValidationIssue(
                path=key,
                message=f"Unknown configuration key",
                level=ValidationLevel.INFO,
                suggestion="Remove or check for typo"
            ))
        
        # 自定义验证
        for validator in self.custom_validators:
            try:
                custom_issues = validator(config)
                if custom_issues:
                    self.issues.extend(custom_issues)
            except Exception as e:
                self.issues.append(ValidationIssue(
                    path="validator",
                    message=f"Custom validator failed: {e}",
                    level=ValidationLevel.WARNING
                ))
        
        return self.issues
    
    def _get_nested_value(self, config: Dict, path: str) -> Any:
        """获取嵌套值"""
        parts = path.split(".")
        current = config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _find_unknown_keys(self, config: Dict, known_keys: Set[str], prefix: str = "") -> List[str]:
        """查找未知键"""
        unknown = []
        
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if full_key not in known_keys:
                # 检查是否是某个已知键的前缀
                is_prefix = any(k.startswith(full_key + ".") for k in known_keys)
                if not is_prefix and not any(k.startswith(full_key) for k in known_keys):
                    unknown.append(full_key)
            
            if isinstance(value, dict):
                unknown.extend(self._find_unknown_keys(value, known_keys, full_key))
        
        return unknown
    
    def fix_auto_fixable(self, config: Dict) -> Dict:
        """自动修复可修复的问题"""
        fixed_config = config.copy()
        fixed_count = 0
        
        for issue in self.issues:
            if issue.auto_fixable and issue.expected_value is not None:
                self._set_nested_value(fixed_config, issue.path, issue.expected_value)
                fixed_count += 1
        
        return fixed_config
    
    def _set_nested_value(self, config: Dict, path: str, value: Any):
        """设置嵌套值"""
        parts = path.split(".")
        current = config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    def generate_report(self, issues: Optional[List[ValidationIssue]] = None) -> str:
        """生成验证报告"""
        issues = issues or self.issues
        
        by_level = {
            ValidationLevel.CRITICAL: [],
            ValidationLevel.ERROR: [],
            ValidationLevel.WARNING: [],
            ValidationLevel.INFO: []
        }
        
        for issue in issues:
            by_level[issue.level].append(issue)
        
        lines = [
            "=" * 60,
            "Config Validation Report",
            "=" * 60,
            f"Total Issues: {len(issues)}",
            f"  Critical: {len(by_level[ValidationLevel.CRITICAL])}",
            f"  Error: {len(by_level[ValidationLevel.ERROR])}",
            f"  Warning: {len(by_level[ValidationLevel.WARNING])}",
            f"  Info: {len(by_level[ValidationLevel.INFO])}",
            "-" * 60
        ]
        
        for level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR, 
                      ValidationLevel.WARNING, ValidationLevel.INFO]:
            if by_level[level]:
                lines.extend([f"\n{level.value.upper()}:", "-" * 40])
                for issue in by_level[level]:
                    lines.append(f"  [{issue.path}]")
                    lines.append(f"    {issue.message}")
                    if issue.suggestion:
                        lines.append(f"    Suggestion: {issue.suggestion}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def is_valid(self, issues: Optional[List[ValidationIssue]] = None) -> bool:
        """检查是否有效（无ERROR及以上）"""
        issues = issues or self.issues
        return not any(
            i.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]
            for i in issues
        )


class ConfigDiagnostics:
    """配置诊断工具"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.validator = ConfigValidator()
    
    def _find_config_file(self) -> Optional[str]:
        """查找配置文件"""
        candidates = [
            ".workbuddy/workspace.json",
            ".workbuddy/config.json",
            "config.json"
        ]
        
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        
        return None
    
    def load_config(self) -> Dict:
        """加载配置"""
        if not self.config_path or not Path(self.config_path).exists():
            return {}
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def diagnose(self) -> Dict:
        """运行诊断"""
        config = self.load_config()
        
        issues = self.validator.validate(config)
        
        return {
            "config_path": self.config_path,
            "config_loaded": bool(config),
            "valid": self.validator.is_valid(issues),
            "issue_count": len(issues),
            "critical_count": sum(1 for i in issues if i.level == ValidationLevel.CRITICAL),
            "error_count": sum(1 for i in issues if i.level == ValidationLevel.ERROR),
            "warning_count": sum(1 for i in issues if i.level == ValidationLevel.WARNING),
            "info_count": sum(1 for i in issues if i.level == ValidationLevel.INFO),
            "issues": [i.to_dict() for i in issues],
            "report": self.validator.generate_report(issues)
        }
    
    def fix(self, dry_run: bool = True) -> Dict:
        """修复配置"""
        config = self.load_config()
        
        # 验证
        self.validator.validate(config)
        
        # 修复
        fixed_config = self.validator.fix_auto_fixable(config)
        
        result = {
            "dry_run": dry_run,
            "original": config,
            "fixed": fixed_config,
            "changes": self._detect_changes(config, fixed_config)
        }
        
        if not dry_run:
            self._save_config(fixed_config)
            result["saved"] = True
        
        return result
    
    def _detect_changes(self, original: Dict, fixed: Dict) -> List[Dict]:
        """检测变更"""
        changes = []
        
        def compare(path: str, orig: Any, new: Any):
            if isinstance(orig, dict) and isinstance(new, dict):
                all_keys = set(orig.keys()) | set(new.keys())
                for key in all_keys:
                    new_path = f"{path}.{key}" if path else key
                    compare(new_path, orig.get(key), new.get(key))
            elif orig != new:
                changes.append({
                    "path": path,
                    "from": orig,
                    "to": new
                })
        
        compare("", original, fixed)
        return changes
    
    def _save_config(self, config: Dict):
        """保存配置"""
        path = Path(self.config_path) if self.config_path else Path(".workbuddy/workspace.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


# 测试代码
if __name__ == "__main__":
    print("Config Validator Test")
    print("=" * 60)
    
    # 测试配置
    test_config = {
        "session": {
            "retention_days": None,
            "auto_cleanup": False,
            "compression_enabled": True,
            "unknown_key": "value"  # 未知键
        },
        "cache": {
            "max_size_mb": 2000,  # 超出范围
            "ttl_seconds": 3600
        },
        "logging": {
            "level": "VERBOSE"  # 无效值
        }
    }
    
    # 验证
    validator = ConfigValidator()
    issues = validator.validate(test_config)
    
    print(f"\nFound {len(issues)} issues:")
    print(validator.generate_report())
    
    # 诊断
    print("\n" + "=" * 60)
    print("Running diagnostics...")
    
    diagnostics = ConfigDiagnostics()
    result = diagnostics.diagnose()
    
    print(f"Config path: {result['config_path']}")
    print(f"Valid: {result['valid']}")
    print(f"Issues: {result['issue_count']}")
    
    print("\n" + "=" * 60)
    print("Config Validator module ready!")
