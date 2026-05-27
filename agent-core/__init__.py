"""
agent-core 包初始化文件

此包包含TimesFM-inspired AI架构的核心模块。
"""

__version__ = "2.0.0-timesfm-inspired"
__author__ = "AI Development Team"

# 公开主要模块
__all__ = [
    "config_system",
    "git_context_integration",
    "multi_solution_generator",
    "openrelay_integration",
    "openrelay_config",
    "github_learning_engine"
]

# 确保Python将目录视为包
import sys
sys.path.insert(0, str(__file__))