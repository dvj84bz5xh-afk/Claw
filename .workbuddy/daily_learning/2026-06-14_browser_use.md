## 学习日期: 2026-06-14

### 学习项目: browser-use/browser-use
- URL: https://github.com/browser-use/browser-use
- Stars: 98,690 (⭐极高)
- Language: Python (核心 Rust)
- License: MIT
- 相关度: 25

### 项目概述
browser-use 是 AI 浏览器自动化领域的标杆项目，定位"让网站可被AI智能体访问"。核心架构：`Python API → Rust Core → Browser Harness → Web Task Done`，通过LLM决策+Playwright执行，让AI像人一样操作网页。已在 Claw 已学习列表中查重（crewAI/pydantic-ai/agno/nanobrowser 等已学），本项目为新引入。

### 核心发现
1. **Rust Core 高性能运行时** (0.13+) — 用Rust重写代理核心，专为前沿AI模型优化，3-5倍速度提升，是Python Agent工程的性能标杆
2. **双轨代理系统 (Traditional + Beta)** — 传统代理稳定+Beta代理高性能，用户可按场景切换，模块化代理抽象
3. **ChatBrowserUse 统一模型接口** — 单一API密钥调用多家LLM(OpenAI/Anthropic/Google/本地Ollama)，抽象Provider差异
4. **持久化浏览器+恢复循环** — 借鉴编码代理的"持久化工具+任务失败恢复"机制，浏览器会话跨任务保留
5. **@tools.action 装饰器扩展** — 开发者通过装饰器即可向Agent注入自定义工具，低代码扩展能力边界
6. **MCP+云集成双形态** — 开源版深度可定制 + 云版 1000+ 集成(Gmail/Slack/Notion)、stealth/代理轮换/验证码处理

### 可借鉴点
| 优点 | 优先级 | 模块 | 说明 |
|------|--------|------|------|
| Rust Core 性能引擎 | P0 | agent_orchestration | Claw 纯Python实现，遇到大规模并发/HTTP密集任务有性能瓶颈；可借鉴Rust/Go重写热点模块思路 |
| 双轨代理(传统+Beta) | P1 | agent_orchestration | Claw 缺少数值化的"实验性/稳定性"代理分级，无法让用户按场景选速度vs稳定 |
| 统一LLM Provider抽象 | P1 | model_scheduler | model_scheduler已支持多Provider，但缺少"单一API key路由多模型"的能力，可借鉴 ChatBrowserUse 设计 |
| 任务恢复循环(Resume Loop) | P1 | agent_orchestration | Claw 长任务失败后无自动恢复机制，需借鉴编码代理的"持久化+Resume"模式 |
| @tools.action 装饰器 | P2 | tool_system | Claw tool_registry 已支持装饰器注册，但缺少 action 命名空间隔离和多工具组管理 |
| CLI 持久化浏览器会话 | P2 | tool_system | Claw 进化引擎命令行调用是无状态的，可借鉴browser-use CLI的"会话持久化"能力 |

### 改进建议
1. **[P0] 引入Rust/Go性能模块化重写Claw热点** — 评估将 Claw 的 HTTP 代理层/事件循环用 Rust 改写，对标 browser-use 的 Rust Core 思路（初期可仅试点 hot path，预期 3-5x 性能提升）
2. **[P1] Claw 代理分级(Stable/Beta)双轨制** — 在 model_scheduler 中新增 `agent_track="stable|beta"` 字段，Beta 走新模型+新工具，Stable 走验证过的组合，降低生产环境风险
3. **[P1] 增强 LLM Provider 抽象支持统一 key 路由** — 借鉴 ChatBrowserUse 设计，让 Claw 单个 API key 即可路由 OpenAI/Anthropic/本地模型，减少用户配置负担
4. **[P1] 进化引擎添加任务恢复循环** — 夜间进化任务失败时自动 Resume，支持断点续传+失败重试，避免长任务中断导致当天学习记录丢失
5. **[P2] Tool Registry 增强 action 命名空间分组** — 引入 `@tools.action(group="browser")` 装饰器语法，按业务域隔离工具集，提升大规模工具下的可维护性
