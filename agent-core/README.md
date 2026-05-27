# agent-core 模块说明

## 概述
本目录包含 WorkBuddy Claw 项目的核心 AI 智能体模块，共计 48 个 Python 文件。

## 核心模块分类

### Git 上下文增强
| 文件 | 功能 |
|:-----|:-------|
| `git_context_integration.py` | Git 状态感知与集成核心 |
| `git_context_enhanced.py` | 增强版 Git 上下文处理 |
| `git_context_real_scenarios.py` | 实战场景模拟 |

### 多方案并行生成（TimesFM-inspired）
| 文件 | 功能 |
|:-----|:-------|
| `multi_solution_generator.py` | 多方案生成算法 |
| `git_multi_solution_integration.py` | Git 上下文与多方案集成 |
| `timesfm_integration.py` | TimesFM 架构融合主模块 |

### 系统配置与验证
| 文件 | 功能 |
|:-----|:-------|
| `config_system.py` | TimesFM 风格配置-能力分离架构 |
| `config_validator.py` | 配置验证器 |
| `task_patcher.py` | 任务 Patch 化处理 |
| `uncertainty_quantifier.py` | 不确定性量化（分位数预测风格） |
| `zero_shot_knowledge.py` | 零样本知识库 |

### 自动化与调度
| 文件 | 功能 |
|:-----|:-------|
| `task_scheduler.py` | 定时任务调度器（cron 风格） |
| `browser_automation.py` | 浏览器自动化（Playwright/Selenium） |
| `async_processor.py` | 异步任务处理器 |

### 错误处理与恢复
| 文件 | 功能 |
|:-----|:-------|
| `error_recovery.py` | 错误恢复机制 |
| `audit_logger.py` | 审计日志 |
| `health_check.py` | 系统健康检查 |

### 其他核心模块
| 文件 | 功能 |
|:-----|:-------|
| `command_router.py` | 命令路由 |
| `environment_optimizer.py` | 环境优化器 |
| `session_manager.py` | 会话管理 |
| `skill_auto_creator.py` | 技能自动创建器 |
| `skill_transparency_enhancer.py` | 技能透明度增强器 |
| `smart_cache.py` | 智能缓存 |
| `smart_predictor.py` | 智能预测器 |

## 技术特点
- **TimesFM-inspired 架构**：配置驱动、任务自动分解、概率化输出
- **Git 上下文感知**：实时检测 Git 状态，智能增强任务处理
- **多方案并行生成**：借鉴分位数预测思想，生成多样化解决方案
- **Windows 兼容**：已修复 GBK 编码问题，确保 PowerShell 环境稳定运行

## 使用方式
各模块均包含示例脚本（以 `_demo.py` 或 `example_usage.py` 结尾），可直接运行查看效果。

## 依赖
- Python 3.13.5+
- Git 2.53.0+
- 可选：playwright / selenium（浏览器自动化）
