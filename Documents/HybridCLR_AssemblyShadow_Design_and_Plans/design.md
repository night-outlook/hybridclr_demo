# HybridCLR Assembly Shadow 设计

> 文档状态：实施设计草案  
> 日期：2026-08-27  
> 目标环境：Unity 2022.3，IL2CPP，HybridCLR `main` fork  
> 目标仓库：
>
> - `night-outlook/hybridclr`
> - `night-outlook/hybridclr_unity`
> - `night-outlook/hybridclr_demo`
> - **新增要求：** `night-outlook/il2cpp_plus`，或由 `hybridclr_unity` 管理的等价 `il2cpp_plus` 补丁集
>
> 本设计不是官方 HybridCLR DHE 的复刻。它采用更粗粒度的 **Assembly 级 Shadow**：一个逻辑程序集在一次进程启动中整体选择 AOT 基线或 Interpreter 补丁版本。

---

## 1. 摘要与最终决策

### 1.1 目标

首包将业务程序集全部编入 IL2CPP，以 AOT 方式运行。更新时：

1. 检测发生变化的程序集。
2. 计算这些程序集的**反向依赖传递闭包**，称为 `HotUpdate Closure`。
3. 用同一次 Unity 编译快照重新编译闭包中的全部程序集。
4. 设备重启应用进程后，先加载并原子提交同名补丁 DLL。
5. 闭包中的逻辑程序集全部解析到补丁 `Interpreter Image`。
6. 闭包之外的程序集继续使用原 AOT Image。
7. Unity Prefab、Scene 和 AssetBundle 仍保存原程序集名；在序列化 ABI 未变化时，仅更新 DLL，不重新构建 AssetBundle。

示例程序集：

```text
AssemblyA.Contracts
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
```

推荐依赖方向：

```text
AssemblyA.Implementation.Internal
    → AssemblyA.Implementation.Extensibility
    → AssemblyA.Contracts
```

外部程序集默认只能依赖 `Contracts`；只有白名单程序集可以依赖 `Implementation.Extensibility`；任何外部程序集不得依赖 `Implementation.Internal`。

### 1.2 闭包规则

假设：

```text
AssemblyA.Implementation.Internal
    → AssemblyA.Implementation.Extensibility
    → AssemblyA.Contracts

AssemblyB.Consumer
    → AssemblyA.Contracts

AssemblyC.Extension
    → AssemblyA.Implementation.Extensibility
```

则：

| 变化根 | 必须进入 Interpreter 的闭包 |
|---|---|
| `AssemblyA.Implementation.Internal` | `AssemblyA.Implementation.Internal` |
| `AssemblyA.Implementation.Extensibility` | `Extensibility + Internal + AssemblyC.Extension` |
| `AssemblyA.Contracts` | `Contracts + Extensibility + Internal + AssemblyB.Consumer + AssemblyC.Extension` |

闭包是**调用者方向的反向依赖闭包**。闭包中的 DLL 必须来自同一次编译，不允许混用不同源码状态。

### 1.3 关键架构决策

1. **保留最小固定 AOT Bootstrap。**  
   所有业务程序集均可 Shadow，但下载、签名验证、事务提交、失败回滚必须由不依赖任何业务具体类型的固定 Bootstrap 执行。

2. **同名逻辑程序集，不卸载 AOT 基线。**  
   AOT Assembly/Image 仍物理存在，但提交后成为逻辑不可见的 baseline；所有受支持的语义查找入口返回 Active Interpreter Assembly/Image/Class。

3. **一次启动只允许一次 Shadow Commit。**  
   MVP 不支持同进程卸载、二次 Shadow 或补丁切换。更换补丁必须重启进程。

4. **先 Stage、再 Validate、最后 Commit。**  
   Stage 期间不得公开程序集，不运行模块初始化器，不执行任何补丁业务代码。

5. **禁止混合对象世界。**  
   一个 Shadow 闭包内不能同时存在基线 AOT 对象和补丁 Interpreter 对象。提交前若基线类型已初始化、实例化或生成反射对象，事务必须失败。

6. **不修改 AssetBundle 的前提是 Resource ABI 不变。**  
   方法体变化不要求重构资源；序列化字段、继承链或 Unity 管理引用类型发生变化时，补丁构建器必须要求重构受影响资源。

7. **采用统一 Active Resolver。**  
   不能只修改 `Assembly.Load`。Assembly、Image、Class、Type、Reflection、AppDomain、Unity 组件创建和序列化路径都必须通过同一映射模型。

---

## 2. 可行性判断

### 2.1 总体可行性

该方案具有工程可行性，但属于对 HybridCLR + Unity 2022 `libil2cpp` 的深度改造。其难度低于“方法级 DHE”，因为不需要让同一类型中的不同方法分别走 AOT 和 Interpreter；但它仍需解决：

- 同名程序集优先级；
- AssemblyRef 的活动版本解析；
- Image/Class/Type 句柄映射；
- Reflection 缓存；
- AppDomain 枚举去重；
- 静态字段和 `.cctor` 隔离；
- 虚表、接口、泛型和 delegate；
- Unity Prefab/Scene 脚本恢复；
- 补丁提交前的使用时序；
- AssetBundle 序列化 ABI。

### 2.2 必须增加 `il2cpp_plus` 修改源

当前 `hybridclr_unity` 安装器会同时取得 `hybridclr` 和 `il2cpp_plus`，再将 `hybridclr` 放入 `il2cpp_plus/libil2cpp/hybridclr`。核心程序集解析与反射缓存位于 `libil2cpp/vm`，不在独立 `hybridclr` 目录内。

因此，仅维护以下三个 fork 不足以完成目标：

```text
night-outlook/hybridclr
night-outlook/hybridclr_unity
night-outlook/hybridclr_demo
```

必须二选一：

#### 推荐：独立 fork

```text
night-outlook/il2cpp_plus
    branch: unity-2022.3-assembly-shadow
    base: focus-creative-games/il2cpp_plus v2022-8.14.0
```

优点：

- 原生代码改动可独立 review；
- 能正常 rebase、bisect 和打 tag；
- 安装器可以固定 commit；
- CI 可以单独编译和检查。

#### 备选：补丁集

由 `hybridclr_unity` 保存：

```text
Data~/AssemblyShadow/Patches/Unity2022/*.patch
```

安装器 clone 官方 `il2cpp_plus` 后应用补丁。

该方式适合临时 PoC，不适合作为长期源代码真相来源。

### 2.3 Unity Prefab/Scene 是早期 Go/No-Go 闸门

普通 C# 反射和 HybridCLR 解释器路径可以通过公开 `libil2cpp` 修改统一，但 Unity 原生资源反序列化可能缓存 `MonoScript → Il2CppClass*`。必须在 Milestone 01 使用旧 AssetBundle 做实机验证：

```text
首包：Prefab绑定AOT脚本
补丁：同名DLL中方法体返回不同标记
启动：Shadow Commit后才加载旧AssetBundle
验证：实例组件类型来自Interpreter Image，执行补丁逻辑
```

若 Unity 在资源加载前按程序集名、命名空间和类型名查询，则 Active Resolver 可以覆盖；若引擎在 Bootstrap 之前已缓存 AOT `Il2CppClass*` 且没有可拦截入口，就需要进一步映射 baseline class handle，甚至可能无法在不修改 Unity Player 原生层的前提下完全实现。

因此本文把 Prefab/Scene 支持定义为**必须通过的实施闸门**，而不是未经验证的既定事实。

---

## 3. 范围

### 3.1 必须支持

- `Assembly.Load(string/byte[])`
- `AppDomain.CurrentDomain.GetAssemblies()`
- `Assembly.GetType`
- `Type.GetType`
- Image/Class 按名称查找
- 反射 Assembly、Module、Type、Method
- `newobj`
- 静态方法、静态字段和 `.cctor`
- 虚函数、接口调用和继承
- delegate 创建和调用
- 泛型类型、泛型方法与共享泛型
- `GameObject.AddComponent(Type)`
- Shadow 闭包内部的 `AddComponent<T>`
- `GetComponent(Type)` 与闭包内部的 `GetComponent<T>`
- `ScriptableObject.CreateInstance(Type)`
- Unity Prefab/Scene/AssetBundle 中原程序集脚本引用
- DLL-only 逻辑更新
- Contracts 变化后反向依赖闭包整体 Interpreter
- 失败回退到 AOT 基线
- 诊断和可验证的执行模式

### 3.2 明确不支持或延后

MVP 不支持：

- 同进程卸载补丁；
- 同进程第二次 Shadow；
- 热切换已创建对象；
- Shadow 前已经加载业务 Scene/Prefab；
- 固定 AOT Bootstrap 直接引用可 Shadow 业务具体类型；
- Burst 代码直接引用可 Shadow 类型或方法；
- 原生插件缓存可 Shadow `Il2CppClass*`、`MethodInfo*`；
- 不重构 AssetBundle 却任意修改 Unity 序列化布局；
- 补丁模块初始化器失败后的无副作用原地回滚；
- Editor/Mono 后端作为最终验收环境。

---

## 4. 术语

| 术语 | 定义 |
|---|---|
| Logical Assembly | 由简单程序集名标识的业务程序集，例如 `AssemblyA.Contracts` |
| Baseline Assembly | 首包中 IL2CPP AOT 编译的物理程序集 |
| Shadow Assembly | 下载的同名 Interpreter 程序集 |
| Active Assembly | 当前进程中逻辑解析应返回的程序集 |
| Physical Assembly | 实际注册在运行时中的 AOT 或 Interpreter 程序集对象 |
| Shadow Candidate | 允许在启动阶段被 Shadow 的业务程序集 |
| Changed Root | 与首包基线相比发生语义变化的程序集 |
| HotUpdate Closure | Changed Root 的反向依赖传递闭包 |
| Stage | 创建 Interpreter Image，但不公开、不运行模块初始化器 |
| Commit | 原子发布 Active Mapping，并冻结本次启动的程序集选择 |
| Resource ABI | Unity 序列化所依赖的类型名、继承链和字段布局契约 |
| Bootstrap ABI | 固定 AOT Bootstrap 与可 Shadow 业务世界之间的最小边界 |

---

## 5. 现状与缺口

### 5.1 现有加载流程

当前 HybridCLR `Assembly::LoadFromBytes` 的主要流程为：

```text
Create InterpreterImage
→ Load DLL/PDB
→ Build Il2CppAssembly/Il2CppImage
→ InitRuntimeMetadatas
→ MetadataCache::RegisterInterpreterAssembly
→ RunModuleInitializer
```

该流程对普通纯热更程序集有效，但不适合 Shadow 事务，因为：

- DLL 创建时立即公开；
- 同名 AOT Assembly 已存在；
- 无法在多个 DLL 全部验证前原子切换；
- 模块初始化器在事务提交前运行；
- 中途失败会留下部分已注册程序集和副作用。

### 5.2 名称解析不一致

Unity 2022 `il2cpp_plus` 当前存在两种不同倾向：

- `vm::Assembly::GetLoadedAssembly` 逆序搜索已加载列表，新注册程序集可能优先；
- `vm::MetadataCache::GetAssemblyByName` 先扫描固定 AOT 表，再扫描 Interpreter 列表，AOT 一定优先。

仅依赖“后加载覆盖”会产生不同 API 返回不同程序集的问题。

### 5.3 Reflection 缓存以原生指针为 Key

Reflection 的 Assembly、Module 和 Type 对象缓存直接以：

```text
Il2CppAssembly*
Il2CppImage*
Il2CppType*
```

作为 Key。若 Shadow Commit 前已经为 baseline 建立缓存，提交后仍可能返回旧对象。

### 5.4 AOT 程序集不能放入普通 HotUpdate 列表

`FilterHotFixAssemblies` 会将配置为普通 HotUpdate 的程序集从 Player 构建中移除。Shadow Assembly 的基线必须进入 AOT Player，因此需要独立配置：

```text
hotUpdateAssemblies       普通HybridCLR热更；不进AOT
shadowAssemblies          Assembly Shadow；首包仍进AOT
```

Patch 编译和 MethodBridge/泛型扫描需要处理 `shadowAssemblies`，但 Player Filter 不得移除它们。

---

## 6. 总体架构

```text
┌────────────────────────────────────────────────────────────┐
│ Fixed AOT Bootstrap                                        │
│ 下载、签名、Manifest、Stage/Commit、回滚、启动业务入口      │
└───────────────────┬────────────────────────────────────────┘
                    │ InternalCall
┌───────────────────▼────────────────────────────────────────┐
│ HybridCLR Runtime API                                      │
│ Stage DLL、验证、预热、诊断                                 │
└───────────────────┬────────────────────────────────────────┘
                    │ Il2CppAssembly*/Il2CppImage*
┌───────────────────▼────────────────────────────────────────┐
│ il2cpp_plus AssemblyShadowRegistry                         │
│ 状态机、Active Mapping、Class Mapping、Usage Guard          │
└───────┬──────────────────┬───────────────────┬──────────────┘
        │                  │                   │
        ▼                  ▼                   ▼
   Assembly/Metadata   Image/Class/Type    Reflection/AppDomain
        │                  │                   │
        └──────────────────┴──────────┬────────┘
                                      ▼
                        Unity script resolution / execution
```

### 6.1 仓库职责

| 仓库 | 主要职责 |
|---|---|
| `hybridclr` | Interpreter Assembly 两阶段创建、Runtime InternalCall、预热与诊断桥 |
| `il2cpp_plus` | Active Resolver、Assembly/Image/Class/Type/Reflection/AppDomain 核心 Hook |
| `hybridclr_unity` | 配置、安装器、补丁编译、依赖闭包、Manifest、ABI Hash、打包工具 |
| `hybridclr_demo` | 基线 Player、旧 AssetBundle、补丁变体、自动测试和平台验收 |

---

## 7. 程序集边界

### 7.1 业务程序集

```text
AssemblyA.Contracts
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
```

#### Contracts

默认跨程序集依赖边界。允许接口、DTO、消息、枚举、delegate 声明和协议定义。

#### Implementation.Extensibility

少数情况下开放的实现扩展层，例如外部必须继承的抽象基类或稳定默认实现。所有依赖者必须列入白名单；修改它会扩大闭包。

#### Implementation.Internal

封闭内部实现。构建检查必须保证任何其他业务程序集均不直接引用它。

### 7.2 固定 Bootstrap

建议单独程序集：

```text
AssemblyShadow.Bootstrap
AssemblyShadow.Runtime.Abi
```

Bootstrap ABI 只允许：

- `string`
- 数值和枚举
- `byte[]`
- `object`（仅作不透明句柄，慎用）
- 固定且永不修改的极小接口

禁止在 Bootstrap 中出现：

```text
AssemblyA.Contracts中的类型
AssemblyA.Implementation.*中的类型
泛型参数为业务类型
业务MonoBehaviour
业务ScriptableObject
业务反射Type缓存
```

业务入口通过程序集名和入口类型名反射一次，再转换为固定 delegate；或使用无业务类型参数的内部调用协议。

---

## 8. Runtime 状态机

```text
Disabled
   │ ConfigureCandidates
   ▼
CandidatesRegistered
   │ BeginTransaction
   ▼
Staging
   │ StageAssembly × N
   ▼
Staged
   │ Validate
   ▼
Validated
   │ Commit
   ▼
Committed ────────────────┐
                          │ 本进程冻结，不允许再次切换
Failed / Aborted ◄────────┘
```

### 8.1 状态约束

- `ConfigureCandidates` 必须在任何业务资源加载前调用。
- `BeginTransaction` 后只能 Stage Manifest 声明的闭包。
- `StageAssembly` 不能运行模块初始化器。
- `Validate` 不得执行补丁业务方法。
- `Commit` 必须持有全局元数据锁与程序集锁，并在单线程启动阶段执行。
- Commit 后进入 Freeze 状态。
- Commit 后模块初始化器失败时，当前进程立即终止启动；下次启动将补丁标记为失败并回退，不尝试继续运行半初始化状态。

---

## 9. Native 数据模型

建议在 `il2cpp_plus/libil2cpp/vm/AssemblyShadow.h/.cpp` 新增：

```cpp
enum class AssemblyShadowState : uint8_t
{
    Disabled,
    CandidatesRegistered,
    Staging,
    Staged,
    Validated,
    Committed,
    Failed,
};

enum class AssemblyExecutionMode : uint8_t
{
    AotBaseline,
    InterpreterShadow,
};

struct ShadowAssemblyEntry
{
    std::string canonicalName;
    const Il2CppAssembly* baselineAssembly;
    Il2CppAssembly* stagedAssembly;

    std::string baselineMvid;
    std::string patchMvid;
    std::string patchHash;

    bool candidate;
    bool staged;
    bool validated;
};

struct ActiveAssemblySnapshot
{
    uint64_t generation;
    // canonical name -> active physical assembly
    Il2CppHashMap<std::string, const Il2CppAssembly*> byName;

    // baseline physical pointers -> active pointers
    Il2CppHashMap<const Il2CppAssembly*, const Il2CppAssembly*> assemblyMap;
    Il2CppHashMap<const Il2CppImage*, const Il2CppImage*> imageMap;

    // lazy class/type map
    Il2CppHashMap<const Il2CppClass*, Il2CppClass*> classMap;
};
```

### 9.1 名称规范化

统一规则：

1. 去掉路径；
2. 去掉 `.dll`；
3. 使用与现有 Assembly 解析一致的大小写无关比较；
4. Manifest 中保留原始名称用于日志；
5. 禁止两个名称规范化后相同的程序集。

### 9.2 Resolver API

```cpp
class AssemblyShadow
{
public:
    static const Il2CppAssembly* ResolveByName(const char* name);
    static const Il2CppAssembly* ResolveAssembly(const Il2CppAssembly* assembly);
    static const Il2CppImage* ResolveImage(const Il2CppImage* image);
    static Il2CppClass* ResolveClass(Il2CppClass* klass);
    static const Il2CppType* ResolveType(const Il2CppType* type);

    static bool IsShadowedBaseline(const Il2CppAssembly* assembly);
    static bool IsActiveShadow(const Il2CppAssembly* assembly);
    static AssemblyShadowState GetState();

    static void RecordBaselineUse(
        const Il2CppAssembly* assembly,
        BaselineUseKind kind,
        const char* detail);
};
```

所有语义级查找入口调用 Resolver；物理元数据索引接口不应盲目改写。

---

## 10. 两阶段 Interpreter Assembly 创建

重构 `hybridclr::metadata::Assembly`：

```cpp
StagedAssembly* ParseAndBuildSkeleton(...);
void RegisterInStagingResolver(StagedAssembly*);
void InitializeRuntimeMetadata(StagedAssembly*);
void PublishInterpreterAssembly(StagedAssembly*);
void RunModuleInitializerAfterCommit(StagedAssembly*);
```

### 10.1 为什么不能直接复用 `LoadFromBytes`

当前 `LoadFromBytes` 在创建后立即运行 `<Module>` 初始化。Shadow 闭包可能有多个程序集，如果第一个模块初始化器执行后第二个 DLL 校验失败，无法可靠回滚。

### 10.2 建议阶段

#### Phase A：Parse

- 校验 PE/CLI；
- 取得简单程序集名、MVID、AssemblyRef；
- 创建 `InterpreterImage`；
- 不加入公开 Assembly 列表。

#### Phase B：Skeleton

- 创建 `Il2CppAssembly` 和 `Il2CppImage`；
- 建立名字、token 和基础表；
- 加入仅 Shadow staging resolver 可见的临时表。

#### Phase C：Metadata

- 在 staging resolver 已包含整个闭包后初始化 runtime metadata；
- 对程序集引用优先解析 staged closure；
- 不运行 `.cctor` 和 module initializer。

#### Phase D：Commit

- 物理注册 Interpreter Assembly；
- 发布 Active Snapshot；
- 刷新逻辑程序集快照；
- 按依赖顺序运行 module initializer；
- 冻结 Shadow 状态。

---

## 11. Runtime C# API

在 `hybridclr_unity/Runtime` 新增：

```text
AssemblyShadowState.cs
AssemblyShadowErrorCode.cs
AssemblyExecutionMode.cs
AssemblyShadowRuntime.cs
AssemblyShadowDiagnostics.cs
```

建议 API：

```csharp
public static class AssemblyShadowRuntime
{
    public static extern AssemblyShadowErrorCode ConfigureCandidates(
        string baselineBuildId,
        string[] candidateAssemblyNames);

    public static extern AssemblyShadowErrorCode BeginTransaction(
        string patchId,
        string expectedBaselineBuildId,
        string[] closureAssemblyNames);

    public static extern AssemblyShadowErrorCode StageAssembly(
        byte[] dllBytes,
        byte[] pdbBytes);

    public static extern AssemblyShadowErrorCode ValidateTransaction();

    public static extern AssemblyShadowErrorCode CommitTransaction();

    public static extern void AbortTransaction();

    public static extern AssemblyExecutionMode GetAssemblyExecutionMode(
        string logicalAssemblyName);

    public static extern string GetDiagnosticsJson();
}
```

约束：

- `StageAssembly` 从 DLL 自身读取名称，不接受调用方伪造名称；
- Manifest 校验在 C# 层和 native 层各做一次；
- Editor 下仅提供模拟实现，不作为运行时正确性依据；
- InternalCall 注册在 `hybridclr/RuntimeApi.cpp`。

---

## 12. Assembly 与 AssemblyRef 统一解析

### 12.1 必须修改的入口

在 `il2cpp_plus/libil2cpp/vm` 中覆盖：

- `Assembly::GetLoadedAssembly`
- `Assembly::Load`
- `Assembly::GetAllAssemblies`
- `Assembly::GetReferencedAssemblies`
- `MetadataCache::GetAssemblyByName`
- `MetadataCache::GetReferencedAssembly`
- 相关 AppDomain icall
- 相关 `System.Reflection.Assembly` icall

### 12.2 Active-first 规则

```text
ResolveByName(name):
    if state == Committed and name in active shadow map:
        return shadow assembly
    if state == Staging and current operation belongs to staging transaction:
        return staged assembly
    return baseline/default resolution
```

### 12.3 AppDomain 枚举

默认逻辑视图只能返回一个程序集：

```text
AppDomain.CurrentDomain.GetAssemblies()
    → 对每个逻辑程序集只返回Active Assembly
```

AOT baseline 仍保留在物理表中，但不应同时暴露给普通业务反射。

诊断 API 可单独返回：

```text
logicalName
baselinePointer
activePointer
mode
generation
```

### 12.4 不直接改写 AOT 固定索引

`MetadataCache::GetAssemblyFromIndex` 被生成 AOT 代码和底层元数据使用。MVP 不应全局把索引结果替换为 Shadow；应在 AssemblyRef、Reflection、Image/Class 和对象创建等语义入口调用 Resolver。

原因：

- 闭包的基线 AOT 代码本来就不允许执行；
- 非闭包 AOT 元数据仍需要稳定物理表；
- 全局替换固定索引容易破坏 IL2CPP 内部不变量。

---

## 13. Image、Class 与 Type 解析

### 13.1 Image

必须让以下操作先执行：

```cpp
image = AssemblyShadow::ResolveImage(image);
```

至少覆盖：

- `Image::ClassFromName`
- `Image::ClassFromNameCaseInsensitive`
- `Image::FromTypeNameParseInfo`
- `Image::GetTypes`
- `Image::GetEntryPoint`
- Assembly/Module 反射对象创建路径

### 13.2 Class

为 Unity 资源恢复和已经携带 baseline class handle 的路径提供：

```cpp
Il2CppClass* AssemblyShadow::ResolveClass(Il2CppClass* baselineClass);
```

映射 Key 不能依赖 metadata token，而应使用：

```text
Logical Assembly Name
Namespace
Nested Type Path
Type Name
Generic Arity
```

规则：

- 仅当该程序集已 Committed 为 Shadow 时映射；
- 目标类型不存在则返回明确错误，不允许静默使用 baseline；
- 泛型实例由 active generic definition + active type arguments 重新 inflate；
- 不能将已经存在的 baseline 对象“改造成”shadow 类型。

### 13.3 Type

`Type.GetType`、`Assembly.GetType` 及 name parser 应直接得到 active type。

对于传入 baseline `Il2CppType*` 的路径：

- 在提交后尝试映射到 active class/type；
- 开发构建记录映射来源和调用栈；
- 若该 Type 来自固定 AOT 程序集对业务具体类型的静态引用，构建规则应在发布前阻止。

---

## 14. Reflection 与缓存

### 14.1 缓存前映射

修改：

- `Reflection::GetAssemblyObject`
- `Reflection::GetModuleObject`
- `Reflection::GetTypeObject`
- 必要时 `GetMethodObject`、`GetFieldObject`、`GetPropertyObject`、`GetEventObject`

原则：

```text
先 Resolve active native pointer
再访问 Reflection cache
```

### 14.2 Commit 前使用检查

无法安全地清除所有已创建的 Reflection 对象，因此必须建立 `BaselineUsageGuard`。

记录事件：

```text
AssemblyReflectionObjectCreated
ModuleReflectionObjectCreated
TypeReflectionObjectCreated
ClassInitialized
ObjectAllocated
StaticFieldAccessed
VTableInitialized
MonoScriptResolved
```

若目标程序集属于本次闭包，Commit 返回：

```text
BaselineAlreadyUsed
```

并输出首个使用点。

### 14.3 Cache invalidation

Commit 时至少：

- 增加 Assembly list version；
- 重建逻辑 `GetAllAssemblies` snapshot；
- 清理只包含名称解析结果、且明确可安全重建的缓存；
- 不尝试释放 baseline Reflection managed objects；
- 依靠“提交前不得使用”保证不存在旧反射对象。

---

## 15. 执行语义

### 15.1 直接调用

不为所有 AOT 调用点生成 dispatch stub。采用闭包约束：

> 任何编译期引用 Shadow 程序集的业务程序集都必须进入同一 Interpreter 闭包。

因此补丁代码中的 `call`、`newobj`、字段访问等均从 Interpreter Image 解析。

固定 Bootstrap 不得静态引用业务具体类型。

### 15.2 静态字段和 `.cctor`

Baseline 与 Shadow Class 拥有不同静态存储。提交后：

- 只允许 Shadow Class 的静态字段被访问；
- Baseline `.cctor` 不得执行；
- Shadow `.cctor` 按正常首次使用语义执行；
- 显式 Warmup 可在业务启动前执行关键 `.cctor`；
- Baseline static use 被 Usage Guard 记录并阻止 Commit。

### 15.3 Module initializer

- Stage 不运行 module initializer；
- Active Snapshot 发布后按依赖顺序运行；
- 任一 initializer 抛异常时中止启动；
- 当前进程不尝试恢复基线继续运行；
- 写入“补丁启动失败”标记，下次进程回退。

### 15.4 虚表和接口

闭包计算必须涵盖：

- 继承基类；
- 接口定义；
- 接口实现者；
- override 调用者；
- delegate 签名提供者。

闭包中的 Interpreter Class 使用补丁元数据重新建立虚表和接口表。UnityEngine、BCL 等外部稳定 AOT 基类可继续作为边界。

### 15.5 泛型

需要覆盖：

- Shadow 泛型类型；
- Shadow 泛型方法；
- AOT 泛型共享；
- value-type 泛型参数；
- delegate bridge；
- reverse P/Invoke。

`hybridclr_unity` 的 Link、MethodBridge 和 AOT generic 扫描输入必须从：

```text
普通HotUpdate DLL
```

扩展为：

```text
普通HotUpdate DLL
+ 当前Shadow Patch Closure DLL
```

但 Shadow Assembly 不得被 `FilterHotFixAssemblies` 从 AOT Player 移除。

---

## 16. Unity API 路径

### 16.1 `AddComponent`

- `AddComponent(Type)`：传入的 Type 必须是 active shadow Type；
- 闭包内部 `AddComponent<T>`：解释器解析 `T` 到 active Type；
- 固定 AOT 代码不得以泛型参数引用 Shadow 具体组件；
- 若 Unity native 最终持有 baseline Class，进入对象创建前调用 `ResolveClass`。

### 16.2 `GetComponent`

- `GetComponent(Type)` 使用 active Type；
- 闭包内部 `GetComponent<T>` 使用 Interpreter generic context；
- 测试必须验证返回对象的 `GetType().Assembly` 为 active Interpreter Assembly。

### 16.3 `ScriptableObject.CreateInstance`

覆盖：

- `CreateInstance(Type)`
- `CreateInstance(string)`
- 闭包内部泛型封装

### 16.4 `Type.GetType` 与 `Assembly.GetType`

必须统一以下形式：

```csharp
Type.GetType("Namespace.Type, AssemblyA.Contracts")
Assembly.Load("AssemblyA.Contracts").GetType("Namespace.Type")
typeof(SomeType).Assembly
```

其中 `typeof(SomeType)` 只有在调用代码属于 Shadow 闭包时才是合法的业务具体类型引用。

### 16.5 `MonoScript.GetClass`

需要在旧 AssetBundle 中显式验证：

```csharp
MonoScript script = ...
Type type = script.GetClass();
```

期望返回 active Shadow Type。

---

## 17. Prefab、Scene 与 AssetBundle

### 17.1 启动顺序

```text
Player启动
→ 只加载固定Bootstrap Scene
→ ConfigureCandidates
→ 下载和校验补丁
→ Stage全部Closure DLL
→ Validate
→ Commit
→ Warmup
→ 加载业务AssetBundle/Addressables/Scene
```

禁止在 Commit 前：

- 加载业务 Prefab；
- 加载业务 Scene；
- 加载引用业务 ScriptableObject 的 Preloaded Asset；
- 执行业务 `[RuntimeInitializeOnLoadMethod]`；
- 调用业务类型反射；
- 初始化业务 DI 容器。

### 17.2 DLL-only 更新条件

允许不重构 AssetBundle：

- 程序集简单名不变；
- namespace/type name 不变；
- MonoBehaviour/ScriptableObject 继承链的序列化语义不变；
- Unity 序列化字段集合与类型不变；
- `[SerializeReference]` 具体类型标识不变；
- 旧资源的字段数据能被新 Shadow Class 按相同布局读取。

### 17.3 必须重构资源的变化

保守规则下，以下任一变化要求重构受影响 Bundle：

- 增删或改名 public / `[SerializeField]` 字段；
- 字段类型、数组/列表元素类型变化；
- 基类中的序列化字段变化；
- MonoBehaviour/ScriptableObject 基类变化；
- namespace、类名或逻辑程序集名变化；
- `[SerializeReference]` 具体类型集合或名称变化；
- 自定义序列化回调契约变化且无法证明兼容；
- `FormerlySerializedAs` 迁移未经验证。

### 17.4 Resource ABI Hash

对每个可序列化业务类型生成：

```text
logical assembly
namespace
nested type path
type name
base type chain
field name
field type canonical name
array/list shape
SerializeField / NonSerialized
SerializeReference
FormerlySerializedAs
serialization callback markers
```

输出：

```json
{
  "type": "AssemblyA.Internal.DemoPrefabComponent",
  "resourceAbiHash": "sha256:...",
  "referencingBundles": [
    "demo-prefabs.bundle",
    "demo-scenes.bundle"
  ]
}
```

Patch Builder 比较基线与补丁：

```text
Code Hash变化，Resource ABI不变
    → DLL-only允许

Resource ABI变化
    → DLL-only构建失败，并列出必须重构的Bundle
```

---

## 18. Patch 构建管线

### 18.1 新配置

在 `HybridCLRSettings` 增加：

```csharp
AssemblyDefinitionAsset[] shadowAssemblyDefinitions;
string[] shadowAssemblies;
string shadowPatchOutputRootDir;
string shadowBaselineManifestPath;
bool enforceShadowDependencyRules;
bool enforceResourceAbi;
```

另建 `AssemblyShadowSettings` 也可，长期更推荐独立 ScriptableObject，避免污染上游设置。

### 18.2 AOT Player 构建

Shadow assemblies：

- 不进入 `hotUpdateAssemblies`；
- 不被 `FilterHotFixAssemblies` 移除；
- 正常进入 IL2CPP；
- 生成 baseline manifest；
- 生成 baseline semantic hash、MVID、AssemblyRef 和 Resource ABI；
- 在 Player 中嵌入最小候选列表和 build ID。

### 18.3 Patch 编译

复用 `PlayerBuildInterface.CompilePlayerScripts`：

```text
当前源码 → 一次编译输出所有DLL
```

然后：

1. 计算 DLL 语义 Hash；
2. 与 baseline 比较，得到 Changed Roots；
3. 计算反向依赖闭包；
4. 校验闭包全部为 shadow-capable；
5. 从同一输出目录提取闭包 DLL；
6. 运行 Link/Bridge/AOT generic 扫描；
7. 计算 Resource ABI 差异；
8. 生成 Patch Manifest；
9. 签名并打包。

### 18.4 语义 Hash

不要只依赖 PE 文件 SHA，因为重新编译可能改变时间戳、MVID 或调试信息。

实现 `AssemblySemanticHasher`，规范化：

- Assembly identity；
- Type/Method/Field 定义；
- IL；
- attributes；
- generic constraints；
- AssemblyRef；
- 排除 PE timestamp、PDB path、MVID 等非语义数据，或将 MVID 单独记录。

第一阶段可允许开发者显式指定 Changed Roots，但正式发布前必须实现稳定语义 Hash。

### 18.5 隐式依赖

dnlib 的 AssemblyRef 能覆盖正常编译引用。以下隐式依赖需要额外扫描或声明：

- 反射字符串；
- DI 类型名；
- `SerializeReference`；
- Addressables 类型注册；
- 代码生成表；
- native callback；
- 配置文件中的 assembly-qualified name。

Manifest 支持：

```json
"declaredReverseDependencies": {
  "AssemblyA.Contracts": [
    "AssemblyD.ReflectionConsumer"
  ]
}
```

---

## 19. Patch Manifest

建议：

```json
{
  "schemaVersion": 1,
  "patchId": "shadow-demo-0007",
  "baselineBuildId": "player-win64-2026.08.27.001",
  "unityVersion": "2022.3.62f2",
  "target": "StandaloneWindows64",
  "architecture": "x86_64",
  "hybridclrRevision": "<git-sha>",
  "il2cppPlusRevision": "<git-sha>",
  "closure": [
    {
      "name": "AssemblyA.Contracts",
      "dll": "AssemblyA.Contracts.dll",
      "sha256": "...",
      "semanticHash": "...",
      "mvid": "...",
      "references": ["mscorlib"],
      "resourceAbiHash": "..."
    }
  ],
  "changedRoots": ["AssemblyA.Contracts"],
  "loadOrder": [
    "AssemblyA.Contracts",
    "AssemblyA.Implementation.Extensibility",
    "AssemblyA.Implementation.Internal"
  ],
  "resourceBundlesRequired": [],
  "entryAssembly": "AssemblyA.Implementation.Internal",
  "entryType": "AssemblyA.BootstrapEntry",
  "signatureAlgorithm": "Ed25519",
  "signature": "..."
}
```

强校验：

- baseline build ID；
- target/platform/architecture；
- Unity exact version；
- HybridCLR/il2cpp_plus ABI revision；
- closure 完整性；
- DLL 名称与内部 AssemblyName；
- Hash 和签名；
- duplicate name；
- resource ABI；
- Bootstrap ABI。

---

## 20. Bootstrap 与回滚

### 20.1 补丁状态

```text
baseline
candidate
committing
last-known-good
bad
```

### 20.2 启动策略

1. 若 candidate 未曾成功启动，尝试一次；
2. Stage/Validate 失败：立即回退 baseline；
3. Commit 前失败：可以在同进程回退；
4. Commit 后或 module initializer 失败：退出进程；
5. 下次启动把 candidate 标记为 bad，使用 last-known-good 或 baseline；
6. 业务首屏成功后写入 success marker。

### 20.3 原子文件更新

```text
patch.tmp
→ 验证
→ fsync
→ rename patch.ready
→ 更新manifest pointer
```

不要原地覆盖正在使用的 DLL。

---

## 21. 诊断

### 21.1 日志事件

```text
Shadow.ConfigureCandidates
Shadow.Begin
Shadow.Stage.Start/Success/Failure
Shadow.Validate.Reference
Shadow.Validate.Closure
Shadow.Commit.Start/Success/Failure
Shadow.Resolve.Assembly
Shadow.Resolve.Image
Shadow.Resolve.Class
Shadow.BaselineUseDetected
Shadow.ModuleInitializer
Shadow.Warmup
Shadow.Rollback
```

### 21.2 必备诊断字段

- patch ID；
- baseline build ID；
- generation；
- logical assembly；
- baseline/active pointer；
- baseline/patch MVID；
- execution mode；
- first baseline use；
- resolver path；
- thread ID；
- elapsed time；
- error code。

### 21.3 开发构建断言

开发构建中：

- Shadow 后尝试实例化 baseline class：直接报错；
- AppDomain 暴露同名两个逻辑程序集：报错；
- 非闭包 AOT 引用闭包程序集：报错；
- Commit 后再次 Begin：报错；
- Resource ABI 不匹配却加载旧 Bundle：报错。

---

## 22. 性能

### 22.1 未更新程序集

继续直接 AOT，不在每次调用前检查 assembly mode。Resolver 只影响：

- 程序集/类型查找；
- 反射；
- 类创建路径；
- Unity 资源类型恢复；
- 首次类/泛型初始化。

### 22.2 Shadow 程序集

整体 Interpreter。首次调用成本通过：

- Commit 后批量 PreJit；
- PGO Warmup Manifest；
- 显式模块 Warmup；
- 关键泛型实例预建；

转移到启动阶段。

### 22.3 Resolver 开销

Commit 后使用 immutable snapshot 和指针快速判断：

```text
非Shadow Image/Class
    → 一次分支后原路径

Shadow baseline pointer
    → hash/pointer map到active
```

后续优化可为 `Il2CppAssembly/Il2CppImage/Il2CppClass` 建旁路标记，但 MVP 不修改 Unity ABI 结构体布局，优先使用外部 map。

---

## 23. 测试 Demo 设计

目标工程：

```text
night-outlook/hybridclr_demo
Unity 2022.3.62f2
```

建议目录：

```text
Assets/AssemblyShadowDemo/
├─ Bootstrap/
│  └─ AssemblyShadowDemo.Bootstrap.asmdef
├─ AssemblyA/
│  ├─ Contracts/
│  │  └─ AssemblyA.Contracts.asmdef
│  ├─ Implementation/Extensibility/
│  │  └─ AssemblyA.Implementation.Extensibility.asmdef
│  └─ Implementation/Internal/
│     └─ AssemblyA.Implementation.Internal.asmdef
├─ Consumers/
│  ├─ ContractsConsumer/
│  └─ ExtensibilityConsumer/
├─ ResourcesSource/
├─ Scenes/
├─ Tests/Editor/
├─ Tests/Runtime/
└─ Editor/Build/
```

### 23.1 基线资源

- Bootstrap Scene：只挂固定 AOT Bootstrap；
- Business Scene AssetBundle；
- Prefab AssetBundle：
  - 直接挂 `AssemblyA.Implementation.Internal` MonoBehaviour；
  - 该组件继承 Extensibility 基类；
  - 字段类型来自 Contracts；
- ScriptableObject AssetBundle；
- `[SerializeReference]` 测试资源。

### 23.2 补丁矩阵

| Patch | 变化 | 期望闭包 | 旧 Bundle |
|---|---|---|---|
| P00 | 无补丁 | 无 | AOT |
| P01 | Internal 方法体 | Internal | 无需重构，执行新逻辑 |
| P02 | Extensibility 基类方法体 | Extensibility + 所有依赖者 | 无需重构 |
| P03 | Contracts API | 所有反向依赖者 | 全闭包 Interpreter |
| P04 | Internal 非序列化字段 | Internal | 通常 DLL-only |
| P05 | `[SerializeField]` 字段变化 | Internal | 构建器要求重构 Bundle |
| P06 | 缺少闭包成员 | 不允许 Commit | 回退 |
| P07 | 错 baseline build ID | 不允许 Stage | 回退 |
| P08 | Commit 前访问 baseline 类型 | 不允许 Commit | 输出 first-use |
| P09 | Reflection | 对应闭包 | 全部 active |
| P10 | Add/GetComponent | 对应闭包 | active 组件 |
| P11 | virtual/interface/delegate/generic | 对应闭包 | 正确 |
| P12 | `.cctor`/module initializer | 对应闭包 | 只执行 Shadow |
| P13 | AppDomain 枚举 | 对应闭包 | 每逻辑名一个 Assembly |

---

## 24. 自动化验收

### 24.1 Editor 测试

验证：

- asmdef 依赖规则；
- 反向闭包；
- semantic hash；
- Resource ABI hash；
- Manifest；
- patch package；
- installer pin；
- 资源引用索引。

### 24.2 IL2CPP Player 测试

Editor/Mono 不能证明原生 Shadow 正确。必须构建并启动 IL2CPP Player：

优先顺序：

1. Windows Standalone x64；
2. Android ARM64；
3. macOS；
4. iOS；
5. WebGL，最后评估其下载与启动限制。

Player 测试输出 JSON：

```json
{
  "result": "Passed",
  "patchId": "P01",
  "assertions": {
    "componentAssemblyIsShadow": true,
    "methodResultIsPatched": true,
    "appDomainLogicalCount": 1,
    "baselineUseCount": 0
  }
}
```

---

## 25. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---:|---|
| Unity 资源系统在 Commit 前缓存 AOT Class | 极高 | Milestone 01 实机闸门；Class mapping；限制启动资源 |
| 反射缓存产生旧对象 | 高 | Commit 前 Usage Guard；缓存前 Active Resolve |
| 漏算反向依赖 | 高 | dnlib + asmdef + 显式依赖；运行时引用校验 |
| Module initializer 副作用无法回滚 | 高 | Commit 后失败即退出；下次启动回退 |
| 序列化布局不兼容 | 高 | Resource ABI Hash；旧 Bundle 测试 |
| 泛型/虚表错误导致 native crash | 高 | 专门测试矩阵；闭包强制；开发断言 |
| 上游 HybridCLR/Unity 更新导致冲突 | 高 | 固定 SHA；独立 il2cpp_plus fork；rebase CI |
| AOT baseline 意外执行 | 高 | Usage Guard；构建依赖规则；启动时序 |
| AppDomain 同名重复暴露 | 中 | 逻辑枚举去重；物理枚举仅诊断 |
| Resolver 性能开销 | 中 | Commit 后 immutable pointer map；基准测试 |

---

## 26. 实施闸门

### Gate 0：可重复基线

- 三个现有 fork 和新增 il2cpp_plus fork 均固定 SHA；
- Unity 2022.3.62f2 Demo 可构建 IL2CPP Player；
- 普通 HybridCLR 测试通过。

### Gate 1：Prefab/Scene 最小 Shadow

- 旧 Bundle 中脚本在 Commit 后恢复为 Interpreter 类型；
- 方法体补丁生效；
- 无 AssetBundle 重构。

未通过 Gate 1，不进入完整实现。

### Gate 2：逻辑类型世界一致

- Assembly/Type/Reflection/AppDomain 全部 active；
- 不出现同名双逻辑类型；
- baseline use guard 有效。

### Gate 3：执行语义

- 虚表、接口、delegate、泛型、静态字段通过；
- Contracts 变化后的完整闭包可运行。

### Gate 4：生产管线

- 自动闭包、Manifest、ABI、签名、回退；
- Windows + Android 验收；
- 性能和内存达标。

---

## 27. 源文件改动索引

### 27.1 `hybridclr`

建议新增：

```text
hybridclr/metadata/StagedAssembly.h
hybridclr/metadata/StagedAssembly.cpp
hybridclr/metadata/AssemblyShadowBridge.h
hybridclr/metadata/AssemblyShadowBridge.cpp
hybridclr/AssemblyShadowRuntimeApi.cpp
hybridclr/AssemblyShadowRuntimeApi.h
```

修改：

```text
hybridclr/metadata/Assembly.h
hybridclr/metadata/Assembly.cpp
hybridclr/RuntimeApi.h
hybridclr/RuntimeApi.cpp
```

### 27.2 `il2cpp_plus`

建议新增：

```text
libil2cpp/vm/AssemblyShadow.h
libil2cpp/vm/AssemblyShadow.cpp
libil2cpp/vm/AssemblyShadowDiagnostics.h
libil2cpp/vm/AssemblyShadowDiagnostics.cpp
```

修改候选：

```text
libil2cpp/vm/Assembly.cpp
libil2cpp/vm/Assembly.h
libil2cpp/vm/MetadataCache.cpp
libil2cpp/vm/MetadataCache.h
libil2cpp/vm/Image.cpp
libil2cpp/vm/Image.h
libil2cpp/vm/Class.cpp
libil2cpp/vm/Type.cpp
libil2cpp/vm/Reflection.cpp
libil2cpp/vm/Runtime.cpp
libil2cpp/vm/Object.cpp
libil2cpp/vm/GlobalMetadata.cpp
libil2cpp/icalls/mscorlib/System/AppDomain.cpp
libil2cpp/icalls/mscorlib/System.Reflection/Assembly.cpp
libil2cpp/icalls/mscorlib/System/Type.cpp
```

实际修改范围由 Milestone 01 调用链跟踪结果确定，禁止未验证地一次性 Hook 全部文件。

### 27.3 `hybridclr_unity`

建议新增：

```text
Runtime/AssemblyShadow/*
Editor/AssemblyShadow/Settings/*
Editor/AssemblyShadow/Dependency/*
Editor/AssemblyShadow/Hashing/*
Editor/AssemblyShadow/Build/*
Editor/AssemblyShadow/Validation/*
Editor/AssemblyShadow/Installer/*
```

修改：

```text
Runtime/RuntimeApi.cs
Editor/Settings/HybridCLRSettings.cs 或新增独立Settings
Editor/Settings/HybridCLRSettingProvider.cs
Editor/SettingsUtil.cs
Editor/Commands/CompileDllCommand.cs
Editor/Commands/PrebuildCommand.cs
Editor/Installer/InstallerController.cs
Data~/hybridclr_version.json 或新增source pin profile
Link/MethodBridge/AOT generic collectors
```

`FilterHotFixAssemblies.cs` 原则上不应移除 Shadow Assembly；只需确保新增配置不会混入现有 HotUpdate 列表。

### 27.4 `hybridclr_demo`

新增完整 Demo 和自动测试，详见各 Milestone Plan。

---

## 28. 代码审查原则

每个 Milestone 独立 review：

1. 不允许用“后注册程序集自然覆盖”代替统一 Resolver；
2. 不允许在 Stage 期间执行业务代码；
3. 不允许通过清空未知 Unity 缓存来掩盖生命周期错误；
4. 不允许忽略错误后继续使用半提交状态；
5. 不允许仅在 Editor/Mono 验证；
6. 不允许让 Bootstrap 引用业务具体类型；
7. 不允许在 Resource ABI 变化时宣称 DLL-only 安全；
8. 不允许把 baseline AOT object 强制 reinterpret 为 Shadow object；
9. 所有 native Hook 必须有关闭开关和非 Shadow 回归测试；
10. 所有上游文件改动必须最小化，优先新增 Resolver 文件。

---

## 29. 推荐实施顺序

```text
M00 仓库与可重复基线
M01 Demo最小PoC和Prefab/Scene可行性闸门
M02 依赖闭包、Manifest和ABI工具
M03 Native事务与两阶段Stage
M04 Assembly/AssemblyRef统一解析
M05 Image/Class/Type/Reflection/AppDomain统一解析
M06 执行语义、静态状态、虚表、泛型和预热
M07 Unity API、Prefab/Scene和序列化完整验证
M08 Editor补丁构建、安装器和生成器集成
M09 Bootstrap、下载、签名和回滚
M10 自动化测试与平台矩阵
M11 性能、诊断、故障注入和上游rebase
M12 发布验收与生产试运行
```

---

## 30. 参考源

实现前应以本地固定 commit 为唯一源代码真相，以下链接仅说明设计依据：

- https://github.com/night-outlook/hybridclr
- https://github.com/night-outlook/hybridclr_unity
- https://github.com/night-outlook/hybridclr_demo
- https://github.com/focus-creative-games/il2cpp_plus/tree/v2022-8.14.0
- `hybridclr/metadata/Assembly.cpp`
- `hybridclr/RuntimeApi.cpp`
- `hybridclr_unity/Editor/Installer/InstallerController.cs`
- `hybridclr_unity/Editor/BuildProcessors/FilterHotFixAssemblies.cs`
- `hybridclr_unity/Editor/Commands/CompileDllCommand.cs`
- `il2cpp_plus/libil2cpp/vm/Assembly.cpp`
- `il2cpp_plus/libil2cpp/vm/MetadataCache.cpp`
- `il2cpp_plus/libil2cpp/vm/Image.cpp`
- `il2cpp_plus/libil2cpp/vm/Reflection.cpp`

---

## 31. 最终判断

该方案可以作为一个明确、可测试、可回滚的 **Assembly-level AOT Baseline / Interpreter Shadow** 系统实施。

真正决定项目是否继续的不是普通 `Assembly.Load`，而是两个结果：

1. 旧 Prefab/Scene AssetBundle 在 Shadow Commit 后能否恢复为 active Interpreter Class；
2. 是否能够严格保证闭包内 baseline AOT 类型在 Commit 前从未被使用。

只要 Gate 1 和 Gate 2 通过，后续工作主要是系统化覆盖解析入口、执行语义和生产工具链；若 Gate 1 无法通过，则必须在投入完整开发前停止或调整“旧 AssetBundle 无需重构”的目标。
