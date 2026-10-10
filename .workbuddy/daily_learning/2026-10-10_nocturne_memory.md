## 学习日期: 2026-10-10

### 学习项目: Dataojitori/nocturne_memory
- URL: https://github.com/Dataojitori/nocturne_memory
- Stars: 1,388
- 语言: Python (Backend FastAPI + MCP Server + React Dashboard)
- 定位: 面向 MCP Agent 的长期记忆服务器（Say goodbye to Vector RAG）

### 核心发现

1. **条件触发路由 (Disclosure Routing)** — 每条记忆绑定人类可读的触发条件（`disclosure`，如"当用户提到项目X时读这条"），AI 按当前情境**精准注入**，而非 cosine 相似度盲盒抽取
2. **Node–Memory–Edge–Path 四实体图记忆模型** — 四层分离：身份层(Node/UUID永久不变) / 内容层(Memory版本快照 + `deprecated`/`migrated_to` 版本链 + 一键回滚任意历史版本) / 关系层(Edge 有向关系带 priority/disclosure) / 路由层(Path URI)
3. **URI 路径化记忆寻址** — 记忆以 `domain://path` 组织（如 `core://agent/identity`、`project://architecture`），**路径本身就是语义**，支持 Alias 别名构建多维关联网络；后端图拓扑、前端降维成树操作
4. **System Boot 身份协议 + 按需调取** — 启动时只加载 `system://boot` 中配置的核心设定，其余按需 `read_memory` 拉取。**96.9 万字记忆库，首条消息仅载入 7.2K 字**（30天内 78% 记忆被想起过）
5. **豆辞典自动超链接 (Glossary Auto-Hyperlinking)** — 关键词绑定记忆节点，任意正文出现该关键词时用 **Aho-Corasick 多模式匹配**自动检出并生成跨节点超链接，记忆网络"自己织网"
6. **自主 CRUD + 人类可视化审计** — AI 自己 create/update/delete 记忆；每次写入自动生成快照，Dashboard 提供可视化 diff 一键 Integrate/Reject（回滚），清理需人类确认
7. **记忆与 LLM 解耦（One Soul, Any Engine）+ Namespace 隔离** — 记忆存于独立 MCP Server，换模型不丢记忆；Namespace 隔离支持多个 Agent 人格各自独立记忆空间

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 条件触发路由（disclosure 按情境精准注入，替代 cosine 盲盒） | P0 |
| Node-Memory-Edge-Path 四实体图模型（记忆版本快照+一键回滚） | P0 |
| URI 路径化寻址 + Alias 别名多维关联 | P1 |
| System Boot 身份协议 + 按需调取（极致 token 效率） | P1 |
| 豆辞典自动超链接（Aho-Corasick 自织网） | P2 |

### 改进建议

1. **P0｜memory_system**: 条件触发路由（Disclosure Routing）—— 每条记忆绑定人类可读触发条件，按当前情境精准注入，替代 Claw 当前语义记忆图的 cosine 盲盒召回
2. **P0｜memory_system**: Node-Memory-Edge-Path 四实体图记忆模型 —— 身份层(UUID不变)/内容层(版本快照+deprecated/migrated_to+一键回滚)/关系层(Edge priority/disclosure)/路由层(Path URI) 四层分离，支持回滚到任意历史版本
3. **P1｜storage**: URI 路径化记忆寻址（`domain://path`）+ Alias 别名 —— 路径即语义、类文件系统命名空间、多维关联网络
4. **P1｜context_injector**: System Boot 身份协议 + 按需调取 —— 启动只加载核心设定，其余按需拉取（96.9万字库首条仅7.2K字），极致 token 效率
5. **P2｜memory_system**: 豆辞典自动超链接（Glossary + Aho-Corasick 多模式匹配）—— 关键词绑定记忆节点，正文出现即自动跨节点超链接，记忆网络自织网

### 价值评估
Nocturne Memory 针对性批判了"Vector RAG 做记忆"的六大架构缺陷（语义降维/只读/盲盒检索/孤岛记忆/无身份层/代理式记忆），并给出结构化替代方案。其 **条件触发路由** 与 **四实体图模型（含记忆版本回滚）** 是 Claw memory_system 当前未覆盖的新范式，可直接补齐"记忆精准召回 + 可审计回滚"能力；**Boot 按需调取** 则是 context_injector 的极致 token 优化参照。
