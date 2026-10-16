## 学习日期: 2026-10-16

### 学习项目: foryourhealth111-pixel/Vibe-Skills
- URL: https://github.com/foryourhealth111-pixel/Vibe-Skills
- Stars: 3,704 | 相关度: 23 | 语言: Python | License: 见仓库 | 版本: v4.1.0 (pushed 2026-10-14)

> 一个"通用 Skill"——自动路由本地 Skills 并智能编排 harness 工作流。解决"装了几百个技能后，Agent 不知道装了哪些、不知道该用哪个、复杂任务跨域组技能困难"的痛点。

### 核心发现
1. **任务分解 → 技能短名单 → 依赖序执行 → 交付前验收** 四步编排
   - 先明确目标与交付要求，把复杂任务拆成**可验证的子任务**；再从大候选池中只挑**极少数真正相关**的能力，按依赖顺序执行；最后**交付前逐项比对**计划与实际，未完成/失败/阻塞项阻止最终验收。
2. **两阶段技能选择记录（关键创新）**
   - `agent_skill_organization`（规划阶段：每个子任务"打算"用哪些 Skill）与 `module_assignments`（执行阶段：实际分配）。
   - 明确区分"**找到 Skill ≠ Skill 已参与工作**"，让规划与执行解耦、可审计。
3. **三级 token 控制**：本地索引生成（提取每个 Skill 的 name/description/intended-use/boundaries 紧凑信息）→ 候选短名单 → 仅对入选候选按需读取完整 `SKILL.md`。**不等于把整个本地技能库塞进上下文**。
4. **任务分级 L / XL**：L 拆分后按序推进（省时省上下文）；XL 更细拆解，**最多并行 2 个互不冲突的部分** + 额外协调与结果收集。
5. **多技能根目录**：`~/.vibeskills/skill-roots.json` 或项目级 `.vibeskills/skill-roots.json`，可挂共享/团队/第三方技能；`install-receipt.json` 记录安装写入的文件，`check` 可发现缺失/被改动文件；**安装状态与任务完成状态分开记录**。

### 量化验证（SkillsBench，195 个技能全局池，DeepSeekV4Flash-VE + OpenHands 基线）
- 平均任务得分 **+21.12pp**（50.3% → 71.4%），满分任务 39 → 57
- 总 token **-29.6%**（491.1M → 345.8M），工具调用 **-33.1%**（9,954 → 6,664）
- 结论：**不是靠调用更多 Skill 取胜**，而是靠更清晰的规划 + 更少的无效试错

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| 两阶段技能选择记录（规划 agent_skill_organization / 执行 module_assignments，区分"找到≠已用"） | **P0** |
| 本地索引 + 候选短名单 + 按需读取三级 token 控制 | **P0** |
| 可验证子任务分解 + 交付前逐项验收闸门（未完成/失败/阻塞阻止验收） | P1 |
| 多技能根目录（skill-roots.json）聚合共享/团队/第三方技能 | P1 |
| 技能路由效果量化基准（大技能池下 reward/token/工具调用 delta） | P2 |

### 改进建议
1. **[P0] skill_system** — 技能路由两阶段记录 + 依赖序编排：规划阶段记录"每子任务打算用哪些 Skill"（agent_skill_organization），执行阶段记录"实际分配"（module_assignments），明确区分"发现≠参与"；从大技能池只挑极少数相关技能并按依赖顺序执行，升级 Claw 当前"渐进式技能发现"为真正的**技能路由编排**。
2. **[P0] context_injector** — 技能索引三级 token 控制：本地生成紧凑索引（name/description/intended-use/boundaries）→ 候选短名单 → 仅入选候选按需读完整 SKILL.md，避免全量技能库进上下文。
3. **[P1] agent_orchestrator** — 任务分级（L 顺序 / XL 最多并行 2 个互不冲突部分）+ 交付前验收闸门：把复杂任务拆成可验证子任务，交付前逐项比对计划与实际，未完成/失败/阻塞项阻止最终验收。
4. **[P1] skill_system** — 多技能根目录（skill-roots.json）：共享/团队/第三方技能可通过配置文件挂载，无需等待主仓库收录；配 `install-receipt.json` 做文件完整性校验。
5. **[P2] eval_observability** — 技能路由量化基准：在大技能池（如 195 技能）下测量技能路由对 reward / token / 工具调用数的影响，用统计显著性判断路由策略是否真实有效。

### 对 Claw 的价值
Claw 的 skill_system 已有"SkillsHub 市场 / Markdown 零锁定 / 渐进式技能发现 / 自动学习管道"，但缺**大规模技能池下的"选得准 + 排得对"**：Vibe-Skills 给出的"两阶段选择记录 + 依赖序编排 + 三级 token 控制 + 交付前验收"正好补上从"技能仓库"到"技能编排器"的关键一环，且有 SkillsBench 公开可复现数据支撑。
