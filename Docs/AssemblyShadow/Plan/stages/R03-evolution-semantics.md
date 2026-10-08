# R03 · 布局准入、逻辑成员身份与跨版本图修复

状态：**S 已完成规定的 Local 90/90 验证；R03 仍待独立完整审查。** 2026-10-08 业主明确选择 D1=A、D2=A：R03 限定于已有 NativeLayoutAdmissionV1 保守能力，开发性能数据仅作观察。PureInterpreter 结构扩展禁用；H2 尚未发起。

前置：R01、R02。关联 findings：ASR-004, ASR-005, ASR-006。

当前证据与剩余工作：S 已完成规定的 Local 验证，实际 source/evidence 和限制见 [`S_Reconciliation`](../../History/M07R/R03/S_Reconciliation/PRIMARY_RECONCILIATION.md)；先前 H/J 证据及 A–I 历史只读。原第 3 步未证明的结构扩展正向目标经 D1=A 明确递延到 X02，不以此宣称第 3 步原始扩展能力 Passed。第 4–7 步已具备 S 规定范围证据，但仍须独立审查实际运行时、资源、图和集成各项支持/拒绝边界。主设计以 `../DESIGN.md` 和经业主批准的限定修订为准；所有未递延的退出条件、负向要求及独立审查保持有效。


## 修改面

native `AssemblyShadowTypeResolver.cpp`；Editor `ShadowPatchManifestBuilder`、`AssemblyReferenceGraph`、类型/资源分析；新增 `NativeLayoutAdmissionValidator`、逻辑方法 key helper 和对应测试。不要在资源 hasher 内塞入全部 native/interop 规则。

## 实施步骤

### 1. 先确认三个真实反例

创建独立的 baseline/patch 字节输入：普通纯托管类新增 private reference；同名 virtual 方法前新增 virtual 导致 slot 变化；baseline A→B/target B→A 的合法方向反转。分别记录现有 build/native 结果，不用伪造 MethodInfo、手写 PASS JSON 或仅字符串比较宣布复现。

### 2. NativeLayoutAdmissionV1 前置

从既有 CheckLayout 提炼规范：字段签名/偏移、实例大小、种类、父类、接口、private primitive append、value-type 限制。Editor 能确定不支持的变化在输出前拒绝；目标平台偏移未知时保留 NeedsNativeProof，不冒充兼容。为相关变更类型增加发布前有界 metadata-only 验证，不运行 cctor。

### 3. PureInterpreter 扩展 Gate

**限定 R03（D1=A）：**保留 V1 的保守物理布局准入与静态资格筛查；没有完整原生、资源、旧对象和执行边界证明的情况必须拒绝或标识 NeedsProof。静态资格报告不能授权新布局。原本在此步骤计划的 private reference 增删等超出 V1 的结构扩展**已明确递延到独立的 X02 工作包**，不属于本阶段已支持或已完成的正向能力。不得全局移除原生布局检查。

### 4. 分离方法 key 与兼容判定

从 lookup key 去掉 token/slot 和不属于身份的实现 flags；保留 declaring TypeKey、名称、arity、调用约定和完整签名。instance/static、byref、modifier、generic constraints 等用独立 compatibility 检查。禁止执行 guard 调用反射 remap 来批准旧 AOT 方法。

### 5. 拆分图的职责

`G_safety` 继续合并 baseline 与 target 及声明边，ReverseClosure 不再要求它自身拓扑可排；`G_load` 用 target 实际装载依赖排序。统一 generation plan 与 patch manifest 的目标加载算法。真正 target AssemblyRef 环仍给出明确拒绝，不能借伪环修复掩盖真实环。

### 6. 累积闭包与角色矩阵

验证 baseline→v1→v2 及回到 baseline 的源码变化，确保 roots 不只按上一补丁。保留被删历史依赖对闭包的必要影响，但不让它影响 target load order。普通热更消费者是否允许引用 Shadow 要有明确角色规则；本阶段不偷偷把 NormalHotUpdate 当成有 baseline 的 Shadow。

### 7. 回归

Editor/dnlib：实际程序集字节的 field/interface/method/AssemblyRef 变化。Native：TypeKey、MethodInfo 映射、执行拒绝、单次证书。Player：异常 stack trace、虚接口/delegate、P01/P02/P03、旧资源 P04/P05，以及新准入场景。新特性不支持的输入必须在宣称的阶段拒绝。

## 退出条件

**限定 R03 退出条件（D1=A；D2=A）：**不再误用 slot 作为逻辑身份；方向反转不误报环；真实 target 环仍拒绝；Editor admission 与 native 保守能力一致。V1 内每个宣称支持的行为应有源绑定运行时证据；未证明路径安全拒绝。扩展布局的任何正向承诺必须通过独立 X02 资格审查、Player 证据和新授权 Gate，不得以本阶段完成替代。逻辑身份、泛型、虚接口、资源、闭包、旧句柄等其它 RC2–RC4 要求不豁免。S 性能数据仅观察，不构成生产性能预算或延期风险接受。该阶段不自动支持 Add/Remove，也不自动通过 H2。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。

## 2026-10-08 业主范围修订与证据边界

以上 D1=A、D2=A 由业主明确批准，仅修改 R03 所宣称的能力范围，不重写旧测试/结论。原较广的资格和结构扩展目标保留追踪，递延至 [X02](X02-pure-interpreter-structural-expansion.md)，并非 Passed。现有静态报告的 `authorizesExpansion`、`qualificationApproved`、`runtimeProofExecuted`、`expansionAuthorized` 仍为 false。

Local S 的运行源码为 `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`，完整的 90/90 证据发布于 `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`。此前 R/Q/P/O/N 原始证据保留。具体选择见 [业主决策](../../History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md)。仍须由不同审查者完成 design→plan→implementation→evidence 全链路审查；发现的未递延问题不能因 D1/D2 消失。`R03Accepted=false`、`H2Passed=false`、`ReadyForHumanReviewGate=false`、`qualificationApproved=false`。无新 Local batch、M08A 或 X02 执行授权。
