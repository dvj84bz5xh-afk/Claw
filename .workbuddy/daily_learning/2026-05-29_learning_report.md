## 学习日期: 2026-05-29

### 学习项目: microsoft/agent-framework
- URL: https://github.com/microsoft/agent-framework
- Stars: 10,835
- 语言: Python / C# (.NET)
- 维护方: Microsoft 官方

### 核心发现

1. **生产级Agent框架**: 微软官方出品，支持 .NET + Python 双语言，定位是帮助团队将Agent从原型推进到生产环境
2. **图结构多Agent编排**: 支持 sequential（顺序）、concurrent（并发）、handoff（交接）、group collaboration（群组协作）四种工作流模式
3. **内置可观测性**: 集成 OpenTelemetry，提供分布式追踪、监控和调试能力
4. **Agent Skills 知识库**: 从文件、内联代码、类库等多来源构建领域知识，Agent可自动发现和调用
5. **声明式Agent**: 使用 YAML 定义Agent，加速配置和版本管理
6. **检查点与时间旅行**: 工作流可保存检查点、重启、回溯，适合长时间运行的复杂任务

### 可借鉴点

| 优点 | 优先级 |
|------|--------|
| 图结构工作流编排（sequential/concurrent/handoff/group） | P0 |
| OpenTelemetry 可观测性集成 | P1 |
| Agent Skills 多来源知识库机制 | P1 |
| 声明式Agent（YAML定义） | P2 |
| 检查点/时间旅行机制 | P2 |

### 改进建议

1. **P0**: 参考 MAF 的图结构工作流编排，实现 Claw 多Agent协作（sequential/concurrent/handoff/group 四种模式），解决当前 P0 多Agent编排长期pending问题
2. **P1**: 引入 OpenTelemetry 可观测性，为 Claw 添加分布式追踪和监控，提升调试效率和运维能力
3. **P1**: 借鉴 Agent Skills 多来源加载机制（文件/内联代码/类库），增强 Claw Skill 市场的灵活性和扩展性
