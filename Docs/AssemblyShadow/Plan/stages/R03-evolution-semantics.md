# R03 · 布局准入、逻辑成员身份与跨版本图修复

状态：**执行中；focused batch H 已通过并完成 Primary reconciliation，完整 R03 尚未完成。** H 为 37/37 cells Passed；不得将其提升为 R03/H2 验收。当前由 Primary Implementation 负责剩余工作，暂无新的 Local Validation 执行任务；PureInterpreter 结构扩展仍禁用。

前置：R01、R02。关联 findings：ASR-004, ASR-005, ASR-006。

当前证据与剩余工作：`../../History/M07R/R03/J_H_FOCUSED_RECONCILIATION.md`、`../../History/M07R/R03/J_H_EVIDENCE_AUDIT.json`、`R03-remaining-completion.md`。最早未完成的编号实施步骤为第 3 步资格判定/扩展 Gate；第 4–7 步还有完整运行时、资源和集成回归义务。主设计以 `../DESIGN.md` 为准；下列规范性实施步骤、退出条件和独立审查要求保持不变。首轮实现及 A–I 历史记录仍保留，不覆盖旧证据。


## 修改面

native `AssemblyShadowTypeResolver.cpp`；Editor `ShadowPatchManifestBuilder`、`AssemblyReferenceGraph`、类型/资源分析；新增 `NativeLayoutAdmissionValidator`、逻辑方法 key helper 和对应测试。不要在资源 hasher 内塞入全部 native/interop 规则。

## 实施步骤

### 1. 先确认三个真实反例

创建独立的 baseline/patch 字节输入：普通纯托管类新增 private reference；同名 virtual 方法前新增 virtual 导致 slot 变化；baseline A→B/target B→A 的合法方向反转。分别记录现有 build/native 结果，不用伪造 MethodInfo、手写 PASS JSON 或仅字符串比较宣布复现。

### 2. NativeLayoutAdmissionV1 前置

从既有 CheckLayout 提炼规范：字段签名/偏移、实例大小、种类、父类、接口、private primitive append、value-type 限制。Editor 能确定不支持的变化在输出前拒绝；目标平台偏移未知时保留 NeedsNativeProof，不冒充兼容。为相关变更类型增加发布前有界 metadata-only 验证，不运行 cctor。

### 3. PureInterpreter 扩展 Gate

先让 V1 报错可预测，再增加严格资格判定：没有旧对象、Unity native binding、固定 AOT 具体类型依赖、值类型物理表示或未证明 generic/interop 边界。通过资格证明的类型才能试验 private reference 增删等结构变化。默认仍保守；不能全局移除原生布局检查。

### 4. 分离方法 key 与兼容判定

从 lookup key 去掉 token/slot 和不属于身份的实现 flags；保留 declaring TypeKey、名称、arity、调用约定和完整签名。instance/static、byref、modifier、generic constraints 等用独立 compatibility 检查。禁止执行 guard 调用反射 remap 来批准旧 AOT 方法。

### 5. 拆分图的职责

`G_safety` 继续合并 baseline 与 target 及声明边，ReverseClosure 不再要求它自身拓扑可排；`G_load` 用 target 实际装载依赖排序。统一 generation plan 与 patch manifest 的目标加载算法。真正 target AssemblyRef 环仍给出明确拒绝，不能借伪环修复掩盖真实环。

### 6. 累积闭包与角色矩阵

验证 baseline→v1→v2 及回到 baseline 的源码变化，确保 roots 不只按上一补丁。保留被删历史依赖对闭包的必要影响，但不让它影响 target load order。普通热更消费者是否允许引用 Shadow 要有明确角色规则；本阶段不偷偷把 NormalHotUpdate 当成有 baseline 的 Shadow。

### 7. 回归

Editor/dnlib：实际程序集字节的 field/interface/method/AssemblyRef 变化。Native：TypeKey、MethodInfo 映射、执行拒绝、单次证书。Player：异常 stack trace、虚接口/delegate、P01/P02/P03、旧资源 P04/P05，以及新准入场景。新特性不支持的输入必须在宣称的阶段拒绝。

## 退出条件

不再误用 slot 作为逻辑身份；方向反转不误报环；真实 target 环仍拒绝；Editor admission 与实际 native 能力对齐；任何扩大布局范围的承诺都有独立 Player 证据。该阶段完成不自动表示 Add/Remove 支持。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
