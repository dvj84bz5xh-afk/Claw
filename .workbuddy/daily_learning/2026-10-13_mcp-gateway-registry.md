# 学习日期: 2026-10-13

## 学习项目: agentic-community/mcp-gateway-registry
- URL: https://github.com/agentic-community/mcp-gateway-registry
- Stars: 972 | 相关度: 18 | 语言: Python | License: Apache-2.0
- 简介: 企业级 MCP 网关与注册中心 — 为组织内所有 AI 资产（MCP server / A2A agent / skill / 自定义实体）提供单一受治理控制面：安全 OAuth 认证、动态工具发现、统一访问与审计

## 核心发现
1. **控制面 / 数据面分离** — Gateway 是数据面（nginx 反向代理：TLS、auth_request 校验、路由到后端）；Registry 是控制面（FastAPI 服务，拥有资产清单/访问模型/审计轨迹，**决定 gateway 允许路由到什么**）；auth server 对接 IdP（Keycloak/Entra/Okta/Auth0/Cognito/PingFederate），MongoDB/DocumentDB 存配置/embedding/会话/审计
2. **统一 AI 资产注册表** — 四类内置资产 + 管理员自定义 schema 实体，全部同一控制面：MCP servers / Agents(A2A) / Skills(注册即安全扫描 + 版本化) / Custom entities(n8n workflows、policies、prompt templates、model cards)。统一治理、统一审计、统一访问模型
3. **动态工具发现 + Virtual MCP servers** — agent 与 coding assistant 运行时按**自然语言语义搜索**发现工具（非硬编码配置）；Virtual MCP server 把多个后端工具**聚合到一个端点**并带 **per-tool 访问控制**
4. **Per-user egress auth（3LO/OBO/PAT）凭证代理** — 网关代理第三方 SaaS(OAuth)凭证，token 永不落到用户笔记本；单一 resolver 从三层取至多一个凭证（machine client_credentials / per-user OAuth 2.1 身份由 owner 一次性授权后从 vault 借用 / 网关 app-only token 用于 obo_exchange）；`purpose` 是 vault **地址**的一部分并绑定进 AEAD；**借来的身份只能列工具、永不能调工具**（tools/call 由 nginx 用调用者自己的头代理，不经过 registry 的 Python）
5. **fail-closed 准入闸门 + 工具级安全 block** — 每个注册的 server/agent/skill 都被扫描，不安全项**挂起待审**；被扫描器标记的工具**自带独立 block**（一个误报不再连累同服务器其他工具），block 胜过 admin 与 wildcard 授权，rescan 时重算可清除陈旧 block，并从所有读取投影中隐藏该工具
6. **A2A 默认 peer-to-peer** — registry 只负责 agent 间发现、鉴权、访问控制，agent 之间**直接通信**而非每次调用都穿网关
7. **外部注册表联邦 + 审计 + 可观测** — 联邦 Anthropic MCP Registry / AWS Agent Registry / peer registries 成统一界面；全量可归因审计轨迹（含凭证脱敏）；内置 OpenTelemetry 指标与健康监控
8. **性能工程细节** — 搜索做相关性分级（替代 flat 1.0），应用内延迟 641ms → 86ms；egress 复用按 SSRF 校验 IP 池化的 HTTP client（保持 rebind-safe）；forward proxy 是否使用由 DNS 分类决定（仅当解析出的所有地址都是公网才代理）

## 可借鉴点
| 优点 | 优先级 |
|------|--------|
| Gateway(数据面)/Registry(控制面)分离 + 单一受治理入口(集中发现/治理/审计) | P0 |
| 动态工具发现(自然语言语义搜索) + Virtual MCP servers(多后端工具聚合到一端点, per-tool ACL) | P0 |
| fail-closed 准入闸门 + 工具级 block(注册即扫描, 一个误报不连累全服务器) | P1 |
| Per-user egress auth 凭证代理(3LO/OBO/PAT 三层解析器, token 不落用户机器) | P1 |
| 统一 AI 资产注册表(servers/agents/skills/自定义schema实体同控制面) + 外部注册表联邦 | P2 |

## 改进建议
1. [P0] tool_registry 引入 Gateway/Registry 控制面-数据面分离：单一受治理入口集中路由所有工具调用，registry 拥有资产清单/访问模型/审计轨迹并决定 gateway 可路由范围；工具调用统一经 auth 校验 + 审计留痕
2. [P0] tool_registry 实现动态工具发现 + Virtual MCP：agent 运行时按自然语言语义搜索发现工具（替代全量注入 / 硬编码配置），并把多个后端 MCP server 的工具聚合为单一虚拟端点，带 per-tool 访问控制
3. [P1] tool_registry 增加 fail-closed 准入闸门：工具/skill 注册即安全扫描，不安全项挂起待审；扫描标记落到**工具级**独立 block（胜过 admin/wildcard 授权，从所有读取投影隐藏，rescan 可清除）
4. [P1] claw_integration 引入 Per-user egress auth 凭证代理：以三层 resolver（machine client_credentials / per-user OAuth 借用身份 / app-only token）统一托管第三方凭证，token 存 vault 并在 egress 注入，永不落到用户端；借用身份只能读不能调
5. [P2] skill_system 扩展为统一 AI 资产注册表：MCP server/agent/skill/自定义 schema 实体共用同一控制面与访问模型，并支持外部注册表联邦（Anthropic MCP Registry / AWS Agent Registry）
