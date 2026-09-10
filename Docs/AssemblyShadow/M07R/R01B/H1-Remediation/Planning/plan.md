# 总计划与调度依赖

状态：PlanReady / ImplementationNotStarted。M00–M09 是 **H1 整改工作包编号**，与原项目同名 milestone 不同；记录时加 `H1R/` 前缀。

## 1. 固定结果与边界

| Finding | 必须交付 | 不可用的替代 |
|---|---|---|
| H1-B01 | 原 v6 bytes、成员、来源链、raw outcomes 的独立认证 | prior PASS 或作者汇总 |
| H1-H02 | 方法实际参数数在相关窄化前检查；合法边界与超限 loader 结果 | 仅 helper 算术或扩大 ABI 字段 |
| H1-H03 | nested direct-child count 在递增/写回前检查；合法分组不退化 | assertion-only 拒绝或缩小支持上限 |
| H1-M04 | R01 reference 与修复候选的可比 Development 样本与解释 | 原 R00 48 cells 重新贴为新对照 |

用户已选择 1A+2A，不再询问。当前授权只覆盖优化及提交本计划；未来源码开发、构建、候选提交分别按实际任务授权。人工 H1 放行不在本次授权内。

## 2. 完整阶段

| 阶段 | 目标 | 依赖与退出 |
|---|---|---|
| [M00](milestones/M00-entry-and-contract-freeze.md) | 分开完成工作区盘点、规范映射、命令登记和协议预注册 | 每次一个盘点/登记任务；首任务 M00.A |
| [M01](milestones/M01-v6-evidence-authentication.md) | 原 v6 独立证据认证 | M00；必要历史证明未完成时保持阻塞 |
| [M02](milestones/M02-boundary-fixtures-and-reproduction.md) | 两类 fixture、独立 shape oracle、probe、原代码反例 | M00；工具开发、运行、审查分任务 |
| [M03](milestones/M03-method-parameter-fix.md) | 参数计数修复 | 参数 fixture/oracle 与路径检查就绪；独立定向审查 |
| [M04](milestones/M04-nested-count-fix.md) | nested count 修复 | nested fixture/oracle 就绪；与 M03 的同文件写入串行 |
| [M05](milestones/M05-candidate-build-and-loader-validation.md) | 共同测量层准备、新候选冻结、构建、真实加载矩阵 | M03/M04 定向审查；测量开发必须早于 source freeze |
| [M06](milestones/M06-regressions-and-capacity.md) | 新候选受影响回归与 8k 容量 | M05 对应构建及计数验证完成 |
| [M07](milestones/M07-controlled-performance.md) | reference/candidate 配对运行和分析 | M05 测量构建、M06 必需功能验证；测量期间独占设备 |
| [M08](milestones/M08-seal-and-independent-stage-review.md) | 新证据封存及独立全链路阶段复核 | M01/M05/M06/M07 必需项完成；否则不得 ReadyForHumanH1 |
| [M09](milestones/M09-human-h1-and-r02-handoff.md) | 人工 H1 停止点 | 用户显式发起复核并给出结论；未通过不得进入 R02 |

```text
M00 → M01 原证据认证 ──────────────────────┐
  └→ M02 fixtures/oracle → M03 → M04       │
       └→ M05.A 测量准备 → M05.B source freeze
                            → M05.C builds → M05.D loader
                                            → M06 → M07
M01 + 新候选结果 ─────────────────────────→ M08 → STOP / M09
```

M03/M04 前置只依赖各自相关输入，不强制等无关审计任务完成。M05 的测量准备可在不冲突的文件上提前做，但不得形成未经审查的候选构建。M01 的历史访问阻塞不禁止独立修复、诊断构建或新测试；它必须显示在全局 ledger，并阻止最终 H1 材料宣告完整。不得用新运行替换未认证的旧结果。

## 3. 调度粒度

每个 milestone 是协调者规格，**不是单次执行提示词**。协调者按其任务表生成一张已绑定任务卡：一个行为、一个阶段、明确文件/只读权限、一个验证入口、一个返回点。inspection、implementation、test run、independent review 分别启动；按 family/path/config 或 suite 划分的批次分别生成卡。

任务结束返回协调者。只有已授权的协调任务可另行分配下一个有界任务；执行者不自续、不启动下阶段、不把未运行项移出矩阵。普通任务停止点不新增默认人工审批；人工 H1 仍必须由用户明确决定。完整阶段复核不得被拆成互不关联的局部 PASS。

## 4. 不变验收集合

保留 [VALIDATION_MATRIX.md](VALIDATION_MATRIX.md) 的 14 基础 count inputs × 3 load paths × 2 C++ configurations = **84 基础 cells**，附加合法元数据变体另计。拆批只影响运行方式，最终 verifier 必须检查集合相等而非总数相等。

保留普通 8192 有效 DLL、mixed 8184+5+3、32 MiB 最大有效 DLL、512 MiB 有效输入、25% charged-capacity 余量、原 11/14/4 modes 和相关 native/Editor/Python/lazy/dense/old-Player/OFF 回归。历史总数只是待核验参照，不限制新测试增长。

保留每模式至少 10 对正式 fresh-process 性能样本；此为原计划采样约定，不是性能 SLA。旧 profile 只运行双方支持的共同负载，8k 容量不降级。

## 5. 修改与回流

同一 `InterpreterImage.cpp` 同时仅一个 writer。共享 Unity/native 安装、Library、生成输出或设备由一个集成负责人串行控制。只读审查可并行。

新问题按目标路径返回对应任务；影响 executable/generated/harness/配置时重新冻结并运行受影响验证。source freeze 后开发测量代码不得沿用旧候选结果。任何关键证据缺口或失败保留原记录，不自动推迟到 R02。

H1 通过后的原路线仍是 `R02 → R03 → H2 → M08A → M08B → H3 → M09 → H4 → M10 → H5 → M11 → 人工启动 M12`；本工作包只交接，不执行该路线。

## 6. 状态

执行阶段默认 Pending。区分 ImplementedNotValidated、Passed、Failed、Blocked、NotRun、NoCoverage、ReusedAudited、ExternalBytesUnavailable；聚合时保留每项状态。ReadyForHumanH1 只表示材料就绪。任何程序不得据测试全绿生成 humanGatePassed=true。
