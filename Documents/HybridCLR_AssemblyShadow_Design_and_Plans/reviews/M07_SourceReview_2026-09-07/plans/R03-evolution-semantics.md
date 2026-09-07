# R03 · 布局准入、逻辑成员身份与跨版本图修复

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R01、R02。关联 findings：ASR-004, ASR-005, ASR-006。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


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
