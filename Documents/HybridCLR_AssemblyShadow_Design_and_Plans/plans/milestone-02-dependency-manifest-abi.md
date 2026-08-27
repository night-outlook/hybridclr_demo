# Milestone 02：依赖图、反向闭包、Manifest 与 ABI 工具

## 目标

在 `hybridclr_unity` 和 `hybridclr_demo` 中建立确定性的补丁分析工具。输入是一套基线程序集与一次新的 Unity 编译输出，输出是：

- Changed Roots；
- 反向依赖传递闭包；
- 闭包 load order；
- Patch Manifest；
- Bootstrap ABI 检查；
- Resource ABI 差异；
- DLL-only / DLL+Bundle 发布判断。

本阶段不依赖完整 native Shadow 事务，可在 Editor 中完成绝大多数自动测试。

## 进入条件

- M01 Gate 1 为 GO 或 CONDITIONAL GO；
- baseline Player 与只读 Bundle 已保存；
- Patch P01 可以手工生成和运行；
- 已确认 Shadow candidate 的边界约束。

## 设计原则

1. `shadowAssemblies` 与现有 `hotUpdateAssemblies` 是不同集合。
2. Shadow Assembly 必须继续进入首包 AOT。
3. 闭包按**反向依赖**计算。
4. 闭包中的 DLL 必须来自同一次 `CompilePlayerScripts` 输出。
5. 工具必须拒绝“依赖者未进入闭包”的补丁。
6. 资源 ABI 变化时拒绝 DLL-only。
7. 所有 Hash 算法和 Manifest schema 必须版本化。
8. 任何无法可靠静态识别的隐式依赖，必须支持显式声明。

## 任务 02.1：新增独立设置对象

优先在 `hybridclr_unity` 新增：

```text
Editor/AssemblyShadow/Settings/
├─ AssemblyShadowSettings.cs
├─ AssemblyShadowSettingsProvider.cs
├─ AssemblyShadowSettingsUtil.cs
└─ AssemblyShadowSettings.asset.template
```

建议字段：

```csharp
public sealed class AssemblyShadowSettings : ScriptableObject
{
    public bool enableAssemblyShadow;

    public AssemblyDefinitionAsset[] shadowAssemblyDefinitions;
    public string[] shadowAssemblyNames;

    public AssemblyDefinitionAsset[] bootstrapAssemblyDefinitions;
    public string[] bootstrapAssemblyNames;

    public string patchOutputRoot =
        "HybridCLRData/AssemblyShadow/Patches";

    public string baselineOutputRoot =
        "HybridCLRData/AssemblyShadow/Baselines";

    public string sourcePinFile =
        "ProjectSettings/AssemblyShadowSourcePins.json";

    public TextAsset explicitDependencyConfig;
    public TextAsset extensibilityWhitelist;

    public bool enforceResourceAbi = true;
    public bool rejectUnknownReflectionDependencies = true;
    public bool includePdbInDevelopmentPatch = true;
}
```

不要直接复用：

```text
HybridCLRSettings.hotUpdateAssemblies
```

否则 `FilterHotFixAssemblies` 会把 Shadow 基线从 Player 移除。

## 任务 02.2：程序集命名和依赖策略验证器

新增：

```text
Editor/AssemblyShadow/Validation/
├─ ShadowAssemblyPolicyValidator.cs
├─ AssemblyNamePolicy.cs
├─ InternalDependencyRule.cs
├─ ExtensibilityWhitelistRule.cs
└─ BootstrapIsolationRule.cs
```

规则：

### Internal

对：

```text
*.Implementation.Internal
```

要求：

- 只能被同一逻辑模块内部允许的程序集依赖；
- 默认禁止任何其他 asmdef 引用；
- demo 中只允许自身测试程序集，且测试程序集不能进入生产 Player。

### Extensibility

对：

```text
*.Implementation.Extensibility
```

要求：

- 外部引用者必须在白名单；
- 每项白名单包含 owner、reason、reviewer、expiry；
- 过期或不存在则构建失败。

建议白名单：

```json
{
  "schemaVersion": 1,
  "entries": [
    {
      "provider": "AssemblyA.Implementation.Extensibility",
      "consumer": "AssemblyShadowDemo.ExtensibilityConsumer",
      "reason": "Derives VersionedComponentBase for closure test",
      "owner": "RuntimeTeam",
      "expires": "2027-01-01"
    }
  ]
}
```

### Bootstrap

固定 Bootstrap asmdef：

- 不得引用任何 Shadow candidate；
- 不得使用 assembly-qualified 业务类型字符串，除配置中声明的入口字符串外；
- 不得挂载业务资源；
- 不得使用业务类型作为泛型参数。

静态分析无法覆盖所有反射字符串，至少扫描：

```text
typeof
Type.GetType常量
Assembly.Load常量
GetComponent字符串
SerializeReference类型名
DI注册常量
```

## 任务 02.3：读取编译程序集

新增：

```text
Editor/AssemblyShadow/Metadata/
├─ CompiledAssemblySet.cs
├─ DnlibAssemblyLoader.cs
├─ AssemblyDescriptor.cs
├─ AssemblyIdentityUtil.cs
└─ AssemblyReferenceGraph.cs
```

`AssemblyDescriptor` 至少包含：

```csharp
string Name;
Guid Mvid;
string FilePath;
string Sha256;
string SemanticHash;
IReadOnlyList<string> AssemblyReferences;
IReadOnlyList<TypeDescriptor> Types;
bool IsShadowCapable;
bool IsBootstrap;
```

加载器要求：

- 使用 dnlib；
- 按目标平台输出目录解析；
- 统一 `.dll` 后缀和大小写；
- 识别重复 simple name；
- 输出未能解析的引用；
- 不自动从 Editor Domain Assembly 代替目标平台 DLL。

## 任务 02.4：实现稳定语义 Hash

新增：

```text
Editor/AssemblyShadow/Hashing/
├─ AssemblySemanticHasher.cs
├─ SemanticHashSchema.cs
├─ CanonicalSignatureWriter.cs
└─ SemanticHashReport.cs
```

Hash 输入至少包括：

- Assembly simple name；
- public key token；
- AssemblyRef identity；
- 类型名、namespace、nested relation；
- base type；
- interfaces；
- generic parameters/constraints；
- fields 和 attributes；
- methods、parameters、return type；
- method generic constraints；
- normalized IL opcode/operand；
- relevant custom attributes；
- P/Invoke 声明；
- module initializer；
- explicit layout/packing。

排除或单独记录：

- PE timestamp；
- MVID；
- PDB path；
- sequence points；
- 编译器生成的非语义顺序差异，前提是可安全规范化。

不要过度规范化：

- metadata token 本身可排除；
- 但 IL operand 引用的目标语义必须写入 canonical signature；
- exception handler、switch target 和 generic context 必须保留。

输出 report：

```json
{
  "schema": 1,
  "assembly": "AssemblyA.Contracts",
  "semanticHash": "...",
  "sections": {
    "identity": "...",
    "types": "...",
    "methods": "...",
    "attributes": "..."
  }
}
```

先用 demo 建测试：

- 仅 MVID 不同，semantic hash 相同；
- 方法体常量变化，hash 不同；
- field type 变化，hash 不同；
- PDB 变化，hash 相同；
- attribute 变化，按配置决定。

## 任务 02.5：反向依赖图

实现：

```text
Assembly A → B
表示A的编译输出包含AssemblyRef B
```

构建：

```csharp
Dictionary<string, HashSet<string>> forward;
Dictionary<string, HashSet<string>> reverse;
```

闭包算法：

```csharp
Queue<string> pending = changedRoots;
HashSet<string> closure = changedRoots;

while pending:
    provider = Dequeue()
    foreach consumer in reverse[provider]:
        if closure.Add(consumer):
            Enqueue(consumer)
```

约束：

- 只把运行时程序集纳入；
- Editor-only 和 test-only 程序集分类处理；
- 若 consumer 进入 Player 且不是 shadow-capable，则 patch 构建失败；
- 若 consumer 是固定 Bootstrap，立即失败；
- 若引用位于外部预编译 DLL，要求显式声明是否能 Shadow；
- 闭包中存在 asmdef cycle 时构建失败。

## 任务 02.6：Load Order

Patch Stage 的 skeleton 可以先全部注册到 staging resolver，再初始化 metadata；仍需稳定 load order。

使用闭包子图做拓扑排序：

```text
被依赖程序集在前
依赖者在后
```

例如：

```text
Contracts
Extensibility
Internal
Consumer
```

若出现 cycle：

- 输出完整 cycle path；
- 不任意排序；
- patch 构建失败；
- 如果未来要支持 cycle，需要单独的 skeleton/metadata 双阶段，不在此阶段放宽。

## 任务 02.7：显式隐式依赖配置

新增：

```text
ProjectSettings/AssemblyShadowDependencies.json
```

结构：

```json
{
  "schemaVersion": 1,
  "runtimeDependencies": [
    {
      "consumer": "AssemblyD.ReflectionConsumer",
      "provider": "AssemblyA.Contracts",
      "kind": "ReflectionString",
      "evidence": "Type.GetType from config table"
    }
  ],
  "resourceDependencies": [
    {
      "bundle": "versioned-prefab.bundle",
      "assembly": "AssemblyA.Implementation.Internal"
    }
  ]
}
```

合并规则：

```text
effective graph =
    compile-time AssemblyRef
  + explicit runtime dependencies
```

配置中不存在的程序集名、重复边或自依赖应报错。

## 任务 02.8：Resource ABI 描述器

新增：

```text
Editor/AssemblyShadow/Serialization/
├─ UnitySerializedTypeAnalyzer.cs
├─ ResourceAbiDescriptor.cs
├─ ResourceAbiHasher.cs
├─ AssetScriptReferenceIndexer.cs
├─ BundleImpactAnalyzer.cs
└─ ResourceAbiDiff.cs
```

### 类型筛选

至少扫描：

- `UnityEngine.Object` 派生类型；
- `[Serializable]` 且被 Unity 可序列化字段引用的类型；
- `[SerializeReference]` 可能的具体类型；
- `ISerializationCallbackReceiver`；
- custom property drawer 不属于 runtime ABI，但可记录。

### 字段规则

实现 Unity 2022 的保守规则：

- public 非 static、非 const、无 `[NonSerialized]`；
- private/protected 且 `[SerializeField]`；
- `[SerializeReference]`；
- 支持的 primitive、Unity object、struct、array、List；
- 不支持或不确定的类型标为 `Unknown`，不静默忽略。

### 规范化输出

```text
Assembly
Namespace
Type
Base chain
Field declaring type
Field name
Canonical field type
Serialization flags
Former names
Managed-reference mode
```

### 差异等级

```text
None
CodeOnly
ResourceCompatible
ResourceRebuildRequired
UnknownRequiresReview
```

MVP 中 `Unknown` 默认要求重构或人工批准。

## 任务 02.9：Asset/Bundle 脚本引用索引

在 baseline 资源构建时保存：

```text
TypeKey → Asset GUIDs → Bundle Names
```

可使用：

- AssetDatabase；
- SerializedObject；
- prefab/scene dependency；
- AssetBundle build map；
- MonoScript GUID；
- `[SerializeReference]` YAML/serialized data 检查。

输出：

```text
BaselineArtifacts/.../resource-script-index.json
```

Resource ABI 改变后列出精确受影响 Bundle，而不是要求全量重构。

## 任务 02.10：Baseline Manifest

新增 command：

```text
HybridCLR/Assembly Shadow/Build Baseline Manifest
```

输出：

```text
HybridCLRData/AssemblyShadow/Baselines/<target>/<buildId>/
├─ baseline-manifest.json
├─ assemblies/
│  ├─ AssemblyA.Contracts.json
│  └─ ...
├─ resource-abi.json
├─ resource-script-index.json
└─ source-pins.json
```

Manifest 至少包含：

```text
build ID
Unity version
target
architecture
source pins
shadow candidates
bootstrap assemblies
semantic hashes
MVIDs
AssemblyRef graph
Resource ABI
Bootstrap ABI
```

必须来自与 Player 构建相同的 DLL 快照。

## 任务 02.11：Patch Manifest Builder

新增 command：

```text
HybridCLR/Assembly Shadow/Build Patch
```

参数：

```text
Baseline Manifest
Current Compile Output
Target
Patch ID
Optional Explicit Changed Roots
Output Directory
```

流程：

```text
validate source pins
→ load baseline/current descriptors
→ detect changed roots
→ compute reverse closure
→ validate shadow-capable
→ topological sort
→ Resource ABI diff
→ package closure DLL/PDB
→ create manifest
→ generate unsigned patch
```

本阶段签名可留给 M09，但 manifest hash 必须生成。

## 任务 02.12：与现有 HybridCLR 生成器的输入模型

定义统一集合：

```csharp
GenerationInputAssemblies =
    NormalHotUpdateAssemblies
    ∪ CurrentShadowPatchClosure
```

为后续改造准备接口：

```csharp
public interface IRuntimeAssemblyInputProvider
{
    IReadOnlyList<string> GetAssemblies(
        BuildTarget target,
        RuntimeAssemblyInputKind kind);
}
```

`kind`：

```text
Link
MethodBridge
AotGenericReference
ReversePInvoke
Diagnostics
```

本阶段先写单元测试和 adapter，不立即改所有上游 generator。

## Demo 测试

### T02-01 Internal 变化

期望：

```text
ChangedRoots:
  AssemblyA.Implementation.Internal

Closure:
  AssemblyA.Implementation.Internal
```

### T02-02 Extensibility 变化

期望闭包包含：

```text
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
AssemblyShadowDemo.ExtensibilityConsumer
```

### T02-03 Contracts 变化

期望包含所有 AssemblyRef 或显式依赖 Contracts 的 shadow-capable runtime assemblies。

### T02-04 漏配 consumer

把 `ContractsConsumer` 标为非-shadow：

```text
Patch build failed:
Non-shadow AOT consumer depends on changed shadow assembly.
```

### T02-05 Internal 外部依赖违规

外部 asmdef 引用 Internal：

```text
Policy validation failed before compile.
```

### T02-06 Serialized field 变化

P05：

```text
DLL-only rejected
Affected bundle: versioned-prefab.bundle
Reason: field added/removed/type changed
```

### T02-07 仅方法体变化

P01：

```text
Resource ABI unchanged
DLL-only allowed
```

## 交付物

```text
hybridclr_unity:
  AssemblyShadow settings, graph, hash, ABI, manifest code

hybridclr_demo:
  baseline-manifest fixtures
  patch P01/P02/P03/P05 fixtures
  Editor tests
  documentation
```

## Code Review 检查点

- Shadow candidates 是否仍进入 AOT；
- closure 方向是否为 reverse；
- 是否所有 closure DLL 来自同一 compile output；
- semantic hash 是否避免明显非语义变化；
- 是否遗漏 explicit dependencies；
- Resource ABI 是否保守；
- Bootstrap 依赖是否零业务具体类型；
- manifest schema 是否版本化；
- 错误信息是否给出完整依赖路径。

## 完成标准

- T02-01 至 T02-07 全部通过；
- baseline 和 patch manifest 可重复生成；
- 相同输入生成相同 semantic hash 和 closure；
- P01 被判定为 DLL-only；
- P05 被拒绝或要求 Bundle；
- Contracts 变化正确扩大闭包；
- 独立 review 通过并创建 M02 tag。
