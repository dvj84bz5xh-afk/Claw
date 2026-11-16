## 学习日期: 2026-11-16

### 学习项目: NVIDIA/OpenShell
- URL: https://github.com/NVIDIA/OpenShell
- Stars: 21,650 (Rust / Python, 更新 11-15, 已转入 CNCF)
- 定位: "the safe, private runtime for **fleets** of autonomous AI agents" — 给 agent 文件/安装包/API/凭证的能力，但不给无限制访问

### 选题依据
在 57 个候选里比较：`stablyai/orca`(⭐125K, 多 agent 各自 worktree 并行)、`herdrdev/herdr`(⭐51K, 终端会话不中断/多机一窗)、`NVIDIA/OpenShell`(⭐21K, 内核强制+策略形式化验证)。
- orca / herdr 补的是"并行编排界面与终端持久化"，Claw 已有 checkpoint 续跑、并行 executor、Durable Execution(Lease+Revision)，重叠度最高。
- OpenShell 补的是**执行点位置**：从"进程内钩子"换成"内核强制"，以及"策略变更先证明再批准"。这是近 8 轮（OMA/agent-memory/ANOLISA/harness-engineering/failproofai/Tracely/Trail-Code/letta-code）全部没碰的一维。

### 核心发现
1. **强制点在进程之外（内核层）**：每个 agent 跑在独立 sandbox，内核控制哪些文件可访问、哪些系统调用可发，**每条网络连接出 sandbox 前都要过策略检查**。对比 Claw：PathJail、fail-closed 准入、工具级 block 都在 harness 进程内 — agent 改配置或换条路径就绕过，且守卫本身可被停（短板④⑩）。
2. **策略变更不是 diff，是"新增能力的可判定集合"**：变更批准前用 **prover** 算出"这条变更会新允许什么"——例如"带凭证访问一个新主机"或"调用一个新的 API method"，命中风险就挂起等人工。**批准对象是可枚举的能力增量，不是文字描述**（短板⑭）。
3. **advisor 与 prover 分离**：advisor 提策略建议，prover 只做形式化判定并产出风险项。提议者与判定者不是一个角色 —— 这正是"进化≠自己改自己"的机制化写法（短板③）。
4. **凭证与端点成对绑定**：agent 永远看不到真凭证；OpenShell 只在**发往已批准 endpoint** 的请求上注入。Claw 的凭证 vault 是"授权后可取"，缺"这条凭证只能去这几个地址"的绑定（短板④）。
5. **三层控制面**：gateway（控制面：sandbox/策略/访问）— supervisor — sandbox（执行面）。策略与审计配置不在 agent 可写目录里。
6. **强制依赖诚实声明**："Your CNI must enforce `NetworkPolicy`" —— 能力清单里写明本项强制依赖下层 X，不满足就不成立，而不是假装已覆盖。
7. **skills 教 agent 自己写策略**：`npx skills add NVIDIA/OpenShell` 让 agent 会驱动 CLI 与写沙箱策略 —— 自助写策略，但仍要过 prover。这与"agent 不可自批"并不矛盾。

### 可借鉴点
| 优点 | 优先级 |
|------|--------|
| 策略变更产出"能力增量证明"（新主机/新 method/新路径 glob），批准存这份集合而非文本 | P0 |
| 凭证-端点绑定注入：每条凭证声明 allowed_endpoints，代理侧匹配才注入，agent 进程内无明文 | P0 |
| advisor（建议）/ prover（判定）/ human（批准）三角分离，判定输出封闭词表风险项 | P1 |
| 控制面(gateway)/监督面(supervisor)/执行面(sandbox)分层，策略与审计移出 agent 可写区 | P1 |
| 沙箱生命周期与工作区快照绑定：destroy 前强制快照，快照即回滚点 | P1 |
| 策略声明覆盖矩阵 + 强制依赖诚实标注（未覆盖的执行点显式标 unguarded） | P2 |

### 改进建议
1. **[P0][claw_integration] 策略变更"能力增量证明"门**：改进项的落地变更在批准前先算 capability delta —— 新增的网络主机、新增的 API method、新增的可写路径 glob、新增的工具权限；命中敏感类别（带凭证的新主机 / 新写路径 / 新 exec）强制人工审，approval 记录里存这份 delta 而不是自然语言描述。→ 493 条改进项至今只能靠人读文字判断风险，这是最短的一块板。
2. **[P0][tool_registry] 凭证-端点绑定注入**：vault 每条凭证加 `allowed_endpoints` 字段，注入只发生在目标匹配时（由代理/网关注入，不进 agent 进程环境变量）。现在凭证一旦取出即全域可用。
3. **[P1][eval_observability] 提议/判定/批准三角分离**：新增 `policy_prover` 角色，只接受策略/变更描述，输出封闭词表的风险项（`new_host`/`new_method`/`new_path`/`new_exec`/`none`）+ 证据；advisor 只提议无判定权；人只批 prover 出的清单。
4. **[P1][claw_integration] 策略与审计配置移出 agent 可写区**：`.workbuddy/policy/` 改为只读拉取（签名校验），agent 只可提交变更提案到 `proposals/`，生效需要 gateway 侧 apply —— 对上短板⑩"可被暂停的策略不是安全边界"。
5. **[P1][storage] 沙箱销毁与工作区快照绑定**：agent 会话/沙箱结束时强制内容寻址快照（已有能力），把"会话能续跑"补齐为"文件能回滚"（短板⑧）。
6. **[P2][eval_observability] 强制覆盖矩阵**：每条策略标注它覆盖的执行点（file/syscall/net/env/proc），未覆盖的执行点显式列为 `unguarded` 并计入报告顶部 —— 不假装全覆盖。

### 判断
近 8 轮一直在补"记忆/治理/验收"的语义层，但所有强制都发生在 harness 进程内 —— 语义再完备，执行点仍在被治理对象手里。OpenShell 给的新事实是：**治理强度取决于强制点位置，而不取决于策略描述得多细**。据此 MEMORY.md 增第十四条短板：策略变更缺少可判定的能力增量证明（批准对象是文字而非能力集合）。
不引入（Rust + eBPF/LSM + Docker/Podman/WSL2，与 Claw 的 Windows + 纯 Python 栈不兼容）；取它的三条机制而非代码。
