# Assembly Shadow 后续开发：5+1 人工完整 Review Gate

状态：**规范性执行规则（Normative）**  
适用范围：`R00 → R01 → R01B → R02 → R03 → M08A → M08B → M09 → M10 → M11 → M12`，以及需要并入正式发布范围的 X01 能力。

## 1. 目的

后续阶段允许本地 agent 连续开发，但在架构风险发生显著变化的节点必须暂停，由人重新发起一次完整 Review，避免后续工作建立在错误的底层假设、运行时不变式、部署契约或恢复模型之上。

本规则采用 **5 个中途 Gate + 1 个最终 Release Review**。

## 2. 通用强制规则

1. **到 Gate 必须停止。** 完成 Gate 所对应 milestone 的实现、测试、证据整理和阶段内自审后，本地 agent 不得自动进入下一 milestone。
2. **Review 必须由人显式发起。** 新的完整 Review 任务由用户/开发负责人主动启动；agent 的阶段内 code review、CI、静态分析和自动化测试不能替代它。
3. **完整 Review 是全链路 Review。** 至少重新检查：
   - 当前 `design.revised.md` 与相关设计约束；
   - 对应 plan 与实际实施是否一致；
   - `hybridclr_demo / hybridclr / hybridclr_unity / il2cpp_plus` 的固定版本和相关实现；
   - 测试、Player/平台证据和负向测试；
   - 对 M00–M07 已验证能力的回归影响；
   - 新增限制、未验证假设、性能与发布风险。
4. **修复后仍需关闭同一 Gate。** 若完整 Review 产生 findings，先修复并重新执行受影响测试，再对该 Gate 做必要的复核；不能因为“代码已改”就直接进入下一阶段。
5. **Gate 结果必须明确。** 只有人工明确给出 `Passed`，或明确接受剩余风险的 `PassedWithExplicitDeferredRisk`，才允许继续。`Failed` 或未形成结论均不得推进。
6. **证据必须绑定版本。** 每次 Gate Review 记录四仓库 SHA、实际安装 runtime/source pins、测试产物版本和平台信息，避免用旧证据证明新代码。
7. **历史记录只读。** 不覆盖 M00–M07 或先前 Gate 的验收记录；新的 Review 结论和修复证据追加保存。

## 3. Gate 顺序

```text
R00
 ↓
R01
 ↓
[R01B，仅目标规模超出现有容量 profile 时执行]
 ↓
STOP ── H1 人工完整 Review
 ↓ Passed
R02
 ↓
R03
 ↓
STOP ── H2 人工完整 Review
 ↓ Passed
M08A
 ↓
M08B
 ↓
STOP ── H3 人工完整 Review
 ↓ Passed
M09
 ↓
STOP ── H4 人工完整 Review
 ↓ Passed
M10
 ↓
STOP ── H5 人工完整 Review
 ↓ Passed
M11
 ↓
STOP ── 人工显式启动 M12 Final Release Review（+1）
 ↓ Passed
Release
```

## 4. H1：R01 / R01B 后——底层容量与失败模型

**暂停点：**

- 若 R01 证明现有 metadata/index 容量足够，不执行 R01B：R01 完成后暂停。
- 若 R01B 被触发：必须等 R01B 完成及回归后暂停。

**重点：**

- Interpreter Image / metadata index 的真实容量和共享预算；
- 实际项目程序集数量、DLL 大小分布与加载顺序；
- 若修改索引编码：位宽、编码/解码、范围、ABI 和上游兼容性；
- `Failed / Abort / restart / baseline fallback` 的状态与恢复语义；
- 普通 HybridCLR 热更与 Assembly Shadow 是否共同消耗预算；
- 是否存在只有理论模型、没有真实规模准入的问题。

**通过后：**允许进入 R02。

## 5. H2：R03 后——核心 Assembly Shadow Runtime

这是后续开发中**最重要的中途 Review**。

**重点：**

- logical assembly → active assembly/image → class/type → method/reflection → allocation 的一致性；
- 同一逻辑类型是否只有一个 active world；
- baseline AOT 是否能从受支持路径重新进入；
- Stage 私有性、Commit 可见性和 transaction 不变式；
- type/method identity 是否错误依赖物理 token、slot 等跨版本不稳定属性；
- allocation/layout admission 是否正确且稳态没有重复高成本证明；
- safety closure 与 target load graph 是否分离；
- usage guard、generic、delegate、virtual/interface、reflection 路径；
- M00–M07 已验证能力是否发生回归。

**通过后：**允许进入 M08A。

## 6. H3：M08B 后——构建链与 Deployment Admission

此 Gate 决定“生成出来的 patch 是否有资格交给 runtime”。

**重点：**

- changed roots、reverse closure 与 target load order；
- 同一次编译 snapshot / source provenance；
- Native Layout Admission 是否前置；
- Resource ABI / resource catalog 配对；
- Native Capability coverage；
- metadata capacity admission；
- RuntimeContract、ToolchainProvenance、BuildEvidence 的身份边界；
- manifest 是否完整描述 baseline 与目标 patch；
- 是否存在绕过联合准入直接部署补丁的路径。

**通过后：**允许进入 M09。

## 7. H4：M09 后——Bootstrap、Transaction 与 Recovery

这是另一个**高风险 Review Gate**，必须结合故障注入证据，而不能只做静态审查。

**至少覆盖：**

- 下载失败；
- 验签失败；
- manifest / target mismatch；
- 第 N 个 DLL Stage 失败；
- Validate 失败；
- Commit 前失败；
- Commit/ModuleInitializer 后失败；
- 业务启动或健康确认失败；
- crash 后下一进程恢复。

**重点确认：**

- 哪些失败允许当前进程继续 baseline；
- 哪些失败必须终止当前业务启动；
- 哪些失败要求重启；
- baseline / LKG / patch 的选择规则；
- 是否可能出现 partially committed active world；
- 是否可能出现 code/resource 版本混配；
- catch 异常后是否错误地把进程视为健康。

**通过后：**允许进入 M10。

## 8. H5：M10 后——跨平台与生产集成

此 Gate 用于判断方案是否已从 Demo 能力进入目标生产环境可用状态。

**重点：**

- Windows、Android 及项目要求的其他目标平台；
- Unity Scene / Prefab / AssetBundle 旧资源路径；
- Unity API、reflection、generic、delegate、virtual/interface；
- 实际 HybridCLR 安装与 native source pin 流程；
- 较大的真实业务程序集闭包，而不只是小型 fixture；
- build → deploy → restart → execute 的真实链路；
- 平台差异、性能和内存是否暴露新的架构问题。

**通过后：**允许进入 M11。

## 9. +1：M12 Final Release Review

M12 不作为普通自动连续 milestone 执行。

**强制暂停点：**M11 完成后，本地 agent 停止；由人显式发起 M12。

M12 本身就是最终独立 Release Review，应重新执行：

```text
design
  → plans
  → implementation
  → tests/evidence
  → supported scope / known limitations
  → recovery / rollback
  → clean build / release candidate
```

最终发布必须由人工基于 M12 证据明确给出 Release 结论，不能由开发 agent 自行宣布“Ready for Release”。

## 10. X01 与并行工作的规则

- `AddManaged / AddUnityTypes / Remove` 等 X01 能力不能因为 `Replace` 通过而视为通过。
- 若 X01 属于目标产品发布范围，其实现和证据必须在进入对应 H5/M12 Review 前合入并纳入完整 Review。
- M10 runner、设备和 CI 基础设施可按 plan 提前准备；**准备工作不等于通过前一 Gate，也不能借此开始被 Gate 阻止的正式集成阶段。**
- 四仓库中可并行进行互不冲突的准备工作，但涉及同一 Unity 工程构建、native runtime 安装、source pins 和正式证据生成时，仍按 plan 保持可复现的串行集成。

## 11. Gate 交付最小集合

每次人工完整 Review 开始前，本地 agent 至少应准备：

- milestone 修改摘要；
- 四仓库 SHA / source pins；
- 修改文件列表；
- 编译和测试结果；
- Player/设备证据（适用时）；
- 失败/负向测试结果；
- 已知限制与 NotRun 项；
- 阶段内 code review findings 及修复；
- 与上一 Gate 相比发生变化的设计假设；
- 建议的下一阶段进入条件。

这些材料只是 Review 输入，不代表 Gate 已经通过。
