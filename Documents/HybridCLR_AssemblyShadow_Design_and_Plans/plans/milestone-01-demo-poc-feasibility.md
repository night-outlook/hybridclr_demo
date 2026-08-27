# Milestone 01：空 Demo 工程、最小 Shadow PoC 与 Prefab/Scene 可行性闸门

## 目标

在 `night-outlook/hybridclr_demo` 中建立最小、可重复的 Assembly Shadow 场景，并以尽可能少的 runtime 改动回答最关键问题：

> 首包 AssetBundle 中直接引用 AOT 业务程序集脚本，启动后加载同名 Interpreter DLL 并激活 Shadow，能否在不重构 AssetBundle 的情况下实例化补丁类型并执行新方法体？

此 Milestone 是 **Go/No-Go 闸门**。不要在它通过前实现完整生产工具链。

## 进入条件

- M00 完成；
- Unity 2022.3.62f2 IL2CPP Player 可构建；
- 四仓库 pin 已固定；
- Shadow native 宏可以开启；
- 能对 `GameAssembly.dll` 或 `libil2cpp.so` 进行 native 调试。

## 总体策略

本阶段允许：

- hard-code 三个 Shadow 程序集名；
- 手工复制 DLL；
- 使用简化 Manifest；
- 暂时只支持一个补丁；
- 暂时只在 Windows x64 验证。

本阶段不允许：

- 用重命名 Hot Assembly 规避同名问题；
- 重构测试 AssetBundle；
- 把脚本改挂到固定 AOT Host；
- 只验证反射调用，不验证 Prefab/Scene；
- 只在 Editor/Mono 验证；
- 将旧 AOT 脚本组件删除后运行时重新 AddComponent 作为替代结论。

## 任务 01.1：建立 Demo 程序集结构

在 demo 中新增：

```text
Assets/AssemblyShadowDemo/
├─ Bootstrap/
│  ├─ AssemblyShadowDemo.Bootstrap.asmdef
│  ├─ ShadowBootstrap.cs
│  ├─ ShadowPatchFileProvider.cs
│  └─ ShadowDemoResultWriter.cs
├─ AssemblyA/
│  ├─ Contracts/
│  │  ├─ AssemblyA.Contracts.asmdef
│  │  ├─ IVersionTextProvider.cs
│  │  ├─ DemoValue.cs
│  │  └─ AssemblyAContractVersion.cs
│  ├─ Implementation/
│  │  ├─ Extensibility/
│  │  │  ├─ AssemblyA.Implementation.Extensibility.asmdef
│  │  │  └─ VersionedComponentBase.cs
│  │  └─ Internal/
│  │     ├─ AssemblyA.Implementation.Internal.asmdef
│  │     ├─ VersionedPrefabComponent.cs
│  │     ├─ VersionedScriptableObject.cs
│  │     └─ InternalEntry.cs
├─ Consumers/
│  ├─ ContractsConsumer/
│  │  ├─ AssemblyShadowDemo.ContractsConsumer.asmdef
│  │  └─ ContractsConsumer.cs
│  └─ ExtensibilityConsumer/
│     ├─ AssemblyShadowDemo.ExtensibilityConsumer.asmdef
│     └─ DerivedExternalComponent.cs
├─ Editor/
│  ├─ AssemblyShadowDemo.Editor.asmdef
│  ├─ BuildBaselineBundles.cs
│  ├─ BuildBaselinePlayer.cs
│  ├─ CompilePatchDlls.cs
│  └─ GeneratePatchVariant.cs
├─ Scenes/
│  ├─ Bootstrap.unity
│  └─ Business.unity
├─ ResourcesSource/
│  ├─ VersionedPrefab.prefab
│  └─ VersionedData.asset
└─ Tests/
   ├─ Editor/
   └─ Runtime/
```

### asmdef 引用

```text
AssemblyA.Contracts
    无业务依赖

AssemblyA.Implementation.Extensibility
    → AssemblyA.Contracts

AssemblyA.Implementation.Internal
    → AssemblyA.Contracts
    → AssemblyA.Implementation.Extensibility

ContractsConsumer
    → AssemblyA.Contracts

ExtensibilityConsumer
    → AssemblyA.Contracts
    → AssemblyA.Implementation.Extensibility

Bootstrap
    → HybridCLR.Runtime
    不引用任何AssemblyA程序集
```

Bootstrap 通过字符串读取：

```text
AssemblyA.Implementation.Internal
AssemblyA.InternalEntry
```

禁止 Bootstrap 源码出现业务类型的 `using`、`typeof` 或泛型参数。

## 任务 01.2：定义基线与补丁标记

### Contracts

```csharp
namespace AssemblyA.Contracts
{
    public interface IVersionTextProvider
    {
        string GetVersionText();
    }

    [Serializable]
    public sealed class DemoValue
    {
        public int number;
        public string text;
    }
}
```

### Extensibility

```csharp
namespace AssemblyA.Implementation.Extensibility
{
    public abstract class VersionedComponentBase : MonoBehaviour
    {
        [SerializeField] private int baseSerializedValue = 7;

        public virtual string GetBaseVersion()
        {
            return "BASELINE-EXT";
        }
    }
}
```

### Internal

```csharp
namespace AssemblyA.Implementation.Internal
{
    public sealed class VersionedPrefabComponent :
        VersionedComponentBase,
        IVersionTextProvider
    {
        [SerializeField] private DemoValue value;

        public string GetVersionText()
        {
            return "BASELINE-INTERNAL";
        }

        public string GetCombinedText()
        {
            return $"{GetBaseVersion()}|{GetVersionText()}|{value.number}";
        }
    }
}
```

P01 补丁只把：

```text
BASELINE-INTERNAL
```

改为：

```text
PATCH-P01-INTERNAL
```

不修改：

- 程序集名；
- namespace；
- type name；
- 字段；
- base type；
- interface；
- prefab；
- scene；
- bundle。

这样可以将“逻辑变化”与“序列化变化”完全分离。

## 任务 01.3：建立基线资源

### Bootstrap Scene

只能包含：

- Unity 内建组件；
- `AssemblyShadowDemo.Bootstrap` 中脚本；
- 补丁加载 UI 或日志；
- 不允许引用任何 AssemblyA ScriptableObject、Prefab 或 Type。

设置为 Player 第一个 Scene。

### Business Scene

包含：

- 一个 GameObject，直接挂 `VersionedPrefabComponent`；
- 一个 GameObject，挂 `DerivedExternalComponent`；
- 对 `VersionedData.asset` 的引用。

### Prefab Bundle

创建 `VersionedPrefab.prefab`：

- 直接挂 `VersionedPrefabComponent`；
- 序列化字段写入固定值，例如 `number = 1234`；
- 添加一个公开按钮或启动测试入口，读取 `GetCombinedText()`。

### Bundle 构建

第一次构建后将产物复制到不可修改目录：

```text
BaselineArtifacts/<platform>/<baselineBuildId>/
├─ Bundles/
│  ├─ business-scene.bundle
│  ├─ versioned-prefab.bundle
│  └─ versioned-data.bundle
├─ Catalog/
├─ AssemblySnapshot/
└─ baseline-manifest.json
```

设置文件只读，后续 P01 测试不得重新生成或覆盖。

记录：

```text
Bundle SHA256
Unity version
Target
Script assembly MVID
Prefab GUID
MonoScript GUID
```

## 任务 01.4：建立基线 Player

首包中三个 AssemblyA 程序集均正常进入 AOT：

- 不放入 `hotUpdateAssemblies`；
- 暂时不使用新增 Shadow tooling；
- Build 前保存编译输出 DLL，供生成 patch 对照。

运行无补丁模式，输出：

```json
{
  "mode": "Baseline",
  "componentAssembly": "AssemblyA.Implementation.Internal",
  "componentResult": "BASELINE-EXT|BASELINE-INTERNAL|1234"
}
```

必须验证：

- Prefab 和 Scene 都可加载；
- `MonoScript.GetClass()` 返回正确基线类型；
- `GetComponent` 正常；
- ScriptableObject 正常；
- 无 Missing Script。

## 任务 01.5：手工编译同名 Patch DLL

修改 Internal 方法体后，使用：

```csharp
PlayerBuildInterface.CompilePlayerScripts(...)
```

将 DLL 输出到独立目录：

```text
PatchArtifacts/P01/
├─ AssemblyA.Implementation.Internal.dll
└─ AssemblyA.Implementation.Internal.pdb
```

核对：

```text
Assembly simple name:
  AssemblyA.Implementation.Internal

Baseline MVID != Patch MVID

Namespace/type:
  完全相同

Serialized fields:
  完全相同
```

注意：

- Patch DLL 名称不能加 `.Hot`；
- 不把 Internal 配为普通 HotUpdate assembly；
- Player 仍保留 AOT 基线；
- 本阶段只 Shadow Internal，符合反向依赖闭包。

## 任务 01.6：实现最小 Stage API

在 `hybridclr` 暂时新增实验 API：

```cpp
Il2CppAssembly* Assembly::CreateShadowPrototype(
    const byte* assemblyData,
    uint64_t length,
    const byte* pdbData,
    uint64_t pdbLength);
```

该 API先按最小改动实现：

1. 复用当前 `Assembly::Create`；
2. 暂时允许创建与 AOT 同名的 Interpreter Assembly；
3. 保存返回的 `Il2CppAssembly*`；
4. 不要求完整事务；
5. 记录 baseline 与 patch 指针；
6. 延迟或禁用 module initializer。

若 `Create` 当前立即 `RegisterInterpreterAssembly`，PoC 可暂时允许注册，但必须在日志中记录物理双程序集；M03 会正式拆分 Stage/Commit。

C# 暂时新增：

```csharp
RuntimeApi.LoadAssemblyShadowPrototype(byte[] dll, byte[] pdb);
RuntimeApi.ActivateAssemblyShadowPrototype(string assemblyName);
RuntimeApi.GetAssemblyShadowPrototypeDiagnostics();
```

## 任务 01.7：实现最小 Active Resolver

在 `il2cpp_plus` 新增：

```text
libil2cpp/vm/AssemblyShadowPrototype.h
libil2cpp/vm/AssemblyShadowPrototype.cpp
```

只保存：

```cpp
canonical assembly name
baseline assembly pointer
shadow assembly pointer
active flag
```

先修改：

```text
MetadataCache::GetAssemblyByName
Assembly::GetLoadedAssembly
Assembly::Load
```

规则：

```text
若prototype active且名称匹配
    → 返回shadow assembly
否则
    → 原逻辑
```

增加日志：

```text
[AssemblyShadowPoC] ResolveByName
name=...
baseline=...
shadow=...
caller-path=...
```

先验证：

```csharp
Assembly.Load("AssemblyA.Implementation.Internal")
```

返回的反射 Assembly 对象绑定 shadow pointer。

## 任务 01.8：普通反射 PoC

在加载任何业务 Bundle 前：

```csharp
Assembly patchAssembly =
    Assembly.Load("AssemblyA.Implementation.Internal");

Type type = patchAssembly.GetType(
    "AssemblyA.Implementation.Internal.InternalEntry");

object obj = Activator.CreateInstance(type);
string result = ...
```

期望：

```text
PATCH-P01-INTERNAL
```

同时检查：

```csharp
patchAssembly.IsDynamic
patchAssembly.FullName
type.Assembly == patchAssembly
AppDomain.CurrentDomain.GetAssemblies()
```

本阶段 AppDomain 可能仍看到重复项，可以记录但不作为最终失败；M04 修正。

## 任务 01.9：跟踪 Prefab/Scene 类型恢复调用链

在以下候选入口增加开发日志和断点：

```text
MetadataCache::GetAssemblyByName
Assembly::Load
Assembly::GetLoadedAssembly
Image::ClassFromName
Image::FromTypeNameParseInfo
Class::FromIl2CppType
Reflection::GetAssemblyObject
Reflection::GetTypeObject
Object::New
Class::Init
```

加载**第一次构建的只读旧 Bundle**。

记录：

```text
1. Unity是否按Assembly Name查询
2. 是否调用Image::ClassFromName
3. 传入的是baseline image还是shadow image
4. 是否直接传入baseline Il2CppClass*
5. MonoScript.GetClass返回的native class pointer
6. Object::New使用的class pointer
7. 最终component.GetType的assembly pointer
```

将调用链记录在：

```text
Docs/AssemblyShadow/Investigations/
    unity-2022-prefab-script-resolution.md
```

必须包含 native stack trace 或最接近的函数序列，不能只记录现象。

## 任务 01.10：逐步增加最小映射

根据调用链，只加入必要 Hook，推荐顺序：

### Step A：Image 映射

在 `Image::ClassFromName` 等入口：

```cpp
image = AssemblyShadowPrototype::ResolveImage(image);
```

### Step B：Class 映射

若 Unity 直接持有 baseline class：

```cpp
klass = AssemblyShadowPrototype::ResolveClassByName(klass);
```

初始映射 Key：

```text
assembly name + namespace + class name
```

仅处理非泛型测试类。

### Step C：对象创建

若 `Object::New` 收到 baseline class，开发 PoC 中先映射：

```cpp
klass = ResolveClass(klass);
```

必须记录是否只有 Unity 资源路径触发，避免把未知 AOT 生成代码静默重定向。

### Step D：MonoScript

调用：

```csharp
MonoScript.GetClass()
```

必须返回 shadow Type。若 Unity 内部绕过所有可修改入口，记录 native stack 和不可控边界。

## 任务 01.11：旧 Prefab Bundle 验证

Shadow Commit/Activate 后加载旧 Bundle：

```csharp
AssetBundle.LoadFromFile(...)
GameObject prefab = bundle.LoadAsset<GameObject>(...)
GameObject instance = Object.Instantiate(prefab)
```

验证：

```csharp
Component component =
    instance.GetComponent("VersionedPrefabComponent");

Type runtimeType = component.GetType();
Assembly runtimeAssembly = runtimeType.Assembly;
string result = InvokeGetCombinedText(component);
```

必须满足：

```text
runtimeAssembly对应shadow physical assembly
result == "BASELINE-EXT|PATCH-P01-INTERNAL|1234"
serialized number == 1234
无Missing Script
无InvalidCast
无native crash
```

Extensibility 在此补丁中仍 AOT，因此 `BASELINE-EXT` 是预期。Internal 整体 Interpreter。

## 任务 01.12：旧 Scene Bundle 验证

使用同一个 baseline Scene Bundle：

1. Commit Shadow；
2. 异步加载 Scene；
3. 找到组件；
4. 验证类型和方法；
5. 卸载再加载一次；
6. 验证无缓存回退。

如果第一次正确、第二次错误，说明 Unity/Reflection/Image cache 仍未统一。

## 任务 01.13：负面时序测试

在 Shadow Activate 前故意执行以下任一操作：

```csharp
Type.GetType(...)
Assembly.Load(...).GetType(...)
Resources.Load业务资源
加载Business Scene
typeof业务类型（只能放在业务AOT测试程序集）
```

然后再 Activate。

记录：

- 是否仍能映射；
- 是否存在已经创建的 baseline object；
- 是否出现两套类型；
- 后续正式 Usage Guard 应拦截哪个点。

本阶段不要求完美拦截，但必须形成清单。

## 任务 01.14：判定 Gate 1

### GO 条件

全部满足：

- 同名 Interpreter DLL 能创建；
- 普通反射返回补丁类型；
- 旧 Prefab Bundle 不重构即可实例化补丁组件；
- 旧 Scene Bundle 同样通过；
- 序列化字段值正确保留；
- 方法体补丁生效；
- 能明确定位所有关键 native 解析入口；
- 未发现不可拦截的 Unity 引擎早期 class cache。

### CONDITIONAL GO

可以继续，但必须记录设计约束：

- 只有在 Bootstrap 后加载的 AssetBundle 支持；
- Player 首场景、Resources 或 Preloaded Assets 不支持 Shadow 业务脚本；
- 某些 API 需通过特定入口；
- 需要全局 Class handle 映射。

### NO-GO 条件

任一成立：

- Unity 在可执行 Bootstrap 前已固定绑定所有业务 script class；
- 旧 Bundle 使用不可修改的 engine-internal AOT type index，无法通过公开 libil2cpp 路径映射；
- Object 以 baseline layout 创建后才进入可 Hook 路径；
- 即使序列化 ABI 完全相同也无法替换 class；
- 需要修改 Unity Player 闭源引擎代码才能实现。

NO-GO 时停止 M02-M12，重新选择：

- 官方 DHE；
- AOT Host + Hot Logic；
- Bundle 与 DLL 一起更新；
- 不同名 Hot Island。

## 自动测试输出

生成：

```text
PersistentDataPath/AssemblyShadowTests/m01-result.json
```

至少包含：

```json
{
  "gate": "GO",
  "baselineBundleSha256": "...",
  "patchDllSha256": "...",
  "assemblyResolution": {
    "assemblyLoad": "shadow",
    "assemblyGetType": "shadow",
    "monoScriptGetClass": "shadow",
    "objectNew": "shadow"
  },
  "prefab": {
    "missingScript": false,
    "serializedValue": 1234,
    "result": "BASELINE-EXT|PATCH-P01-INTERNAL|1234"
  },
  "scene": {
    "passed": true
  },
  "baselineUsesBeforeActivate": []
}
```

## Code Review 检查点

- 是否确实使用第一次构建的旧 Bundle；
- Patch 是否保持同名程序集和同名类型；
- 是否只改方法体；
- 是否有 AOT Host 或运行时重新挂脚本等规避；
- 是否记录 native 调用链；
- PoC Hook 是否被明确标记为临时；
- Shadow 宏关闭时是否恢复原行为；
- 是否对 Gate 结论保持诚实。

## 完成标准

- `unity-2022-prefab-script-resolution.md` 完成；
- P01 Prefab 和 Scene 实机结果保存；
- Gate 1 结论由 code review 批准；
- 若 GO，创建 tag：
  ```text
  assembly-shadow-m01-poc
  ```
- 所有临时硬编码和已知缺口已列入 M03-M07 待办。
