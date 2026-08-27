# Milestone 03：Native Shadow 事务、两阶段 Stage 与 Runtime API

## 目标

将 M01 的 hard-coded prototype 重构为正式、可验证、单次提交的 Shadow 事务系统。核心输出：

- `AssemblyShadow` 状态机；
- Shadow candidate 注册；
- 多程序集 Stage；
- Interpreter Assembly 两阶段创建；
- 闭包级 Validate；
- 原子 Commit；
- module initializer 延迟；
- C# InternalCall；
- 完整错误码和诊断；
- Shadow 宏关闭时零行为变化。

本阶段只保证事务模型，不要求所有 Assembly/Type 路径已经统一；后续 M04-M07 完成 Resolver 覆盖。

## 进入条件

- M01 Gate 1 为 GO/CONDITIONAL GO；
- M02 能生成 closure 和 manifest；
- prototype 调用链记录完整；
- 四仓库配对 commit 已更新；
- `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW` 可打开。

## 设计约束

1. 一次进程最多一个 Commit。
2. Stage 期间不运行补丁业务代码。
3. Stage 期间不向普通 Assembly 枚举公开补丁。
4. 所有闭包 DLL 先建立 skeleton，再初始化 runtime metadata。
5. Commit 前可 Abort；Commit 后不能回滚内存状态。
6. module initializer 在 Active Mapping 发布后运行。
7. initializer 失败时当前进程 fail-fast，下次启动回退。
8. 所有 native API 必须在 metadata/assembly lock 顺序上明确，禁止死锁。
9. 不在 `Il2CppAssembly` 等上游 ABI 结构中直接增加字段，优先外部 registry。

## 任务 03.1：建立 native 文件

### `il2cpp_plus`

新增：

```text
libil2cpp/vm/AssemblyShadow.h
libil2cpp/vm/AssemblyShadow.cpp
libil2cpp/vm/AssemblyShadowTypes.h
libil2cpp/vm/AssemblyShadowDiagnostics.h
libil2cpp/vm/AssemblyShadowDiagnostics.cpp
```

### `hybridclr`

新增：

```text
hybridclr/metadata/StagedAssembly.h
hybridclr/metadata/StagedAssembly.cpp
hybridclr/metadata/AssemblyShadowBridge.h
hybridclr/metadata/AssemblyShadowBridge.cpp
hybridclr/AssemblyShadowRuntimeApi.h
hybridclr/AssemblyShadowRuntimeApi.cpp
```

修改：

```text
hybridclr/metadata/Assembly.h
hybridclr/metadata/Assembly.cpp
hybridclr/RuntimeApi.h
hybridclr/RuntimeApi.cpp
```

### `hybridclr_unity`

新增：

```text
Runtime/AssemblyShadow/
├─ AssemblyShadowState.cs
├─ AssemblyShadowErrorCode.cs
├─ AssemblyExecutionMode.cs
├─ AssemblyShadowRuntime.cs
├─ AssemblyShadowDiagnostics.cs
└─ AssemblyShadowException.cs
```

## 任务 03.2：定义状态与错误码

Native/C# 共享整数值。不要依赖 enum 自动排序，显式赋值。

建议错误码：

```text
0   Success
1   FeatureDisabled
2   InvalidState
3   InvalidArgument
4   CandidateNotRegistered
5   DuplicateAssemblyName
6   BaselineAssemblyNotFound
7   BaselineBuildMismatch
8   AssemblyNameMismatch
9   BadImage
10  UnsupportedAssembly
11  ClosureMemberMissing
12  UnexpectedClosureMember
13  ReferenceResolutionFailed
14  ReferenceEscapesClosure
15  BaselineAlreadyUsed
16  ResourceAbiMismatch
17  RuntimeAbiMismatch
18  AlreadyCommitted
19  ModuleInitializerFailed
20  InternalError
```

状态：

```text
Disabled
CandidatesRegistered
Staging
Staged
Validated
Committing
Committed
Aborted
Failed
```

所有 public API 都必须声明允许的前置状态。

## 任务 03.3：Shadow candidate 注册

API：

```cpp
AssemblyShadowError ConfigureCandidates(
    const char* baselineBuildId,
    const std::vector<std::string>& names);
```

实现：

1. 规范化 names；
2. 检查 duplicate；
3. 使用原始 AOT-only 查找取得 baseline `Il2CppAssembly*`；
4. 不允许 candidate 本身是 Interpreter；
5. 保存 baseline Assembly/Image；
6. 初始化 usage state；
7. 状态进入 `CandidatesRegistered`。

C#：

```csharp
AssemblyShadowRuntime.ConfigureCandidates(
    baselineBuildId,
    manifest.ShadowCandidates);
```

必须在 Bootstrap 的最早安全点调用。

### AOT-only 查找

新增不经过 Active Resolver 的物理 API：

```cpp
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(
    const char* name);
```

该 API只供 registry 初始化和诊断使用，普通业务代码不得调用。

## 任务 03.4：BeginTransaction

输入：

```text
patchId
expectedBaselineBuildId
closure assembly names
runtime ABI version
```

步骤：

1. 状态必须为 CandidatesRegistered；
2. baseline build ID 完全匹配；
3. closure names 非空且均为 candidate；
4. duplicate 检查；
5. 记录期望集合；
6. 清空上次 staging 临时状态；
7. 状态进入 Staging。

不要在 native 层解析完整 JSON。C# 已验证签名和 JSON；native 接收最小必要数据并再次验证 DLL 自身身份。

## 任务 03.5：拆分 `Assembly::Create`

当前创建流程需分为可测试步骤。建议抽取：

```cpp
StagedAssembly* Assembly::CreateStagedSkeleton(
    const byte* assemblyData,
    uint64_t length,
    const byte* pdbData,
    uint64_t pdbLength);

void Assembly::InitializeStagedRuntimeMetadata(
    StagedAssembly* staged);

void Assembly::PublishStagedAssembly(
    StagedAssembly* staged);

void Assembly::RunStagedModuleInitializer(
    StagedAssembly* staged);
```

`StagedAssembly` 建议包含：

```cpp
InterpreterImage* interpreterImage;
Il2CppAssembly* assembly;
Il2CppImage* image;
std::string canonicalName;
std::vector<std::string> references;
bool skeletonBuilt;
bool runtimeMetadataInitialized;
bool published;
bool moduleInitializerRan;
```

### Skeleton 阶段

执行：

- 复制 DLL/PDB bytes；
- `InterpreterImage::AllocImageIndex`；
- 解析 Assembly row；
- 建 `Il2CppAssembly/Il2CppImage`；
- `InitBasic`；
- `BuildIl2CppAssembly`；
- `BuildIl2CppImage`；
- 设置 name/image/assembly；
- 读取 AssemblyRef 名称。

禁止：

- `InitRuntimeMetadatas`；
- `MetadataCache::RegisterInterpreterAssembly`；
- `Assembly::Register`；
- `RunModuleInitializer`；
- Class Init；
- 解释器方法执行。

### Metadata 阶段

在所有 skeleton 已加入 transaction staging map 后执行：

```text
InitRuntimeMetadatas
```

此时引用解析可通过 staging resolver 找到同一闭包中尚未 publish 的 skeleton。

如果 `InitRuntimeMetadatas` 内部假定程序集已公开注册，需要将其依赖改为：

```text
AssemblyShadow::ResolveForStaging
```

不要为通过测试而提前加入普通 `s_cliAssemblies`。

## 任务 03.6：StageAssembly

C#：

```csharp
AssemblyShadowRuntime.StageAssembly(dllBytes, pdbBytes);
```

Native：

1. 校验状态 Staging；
2. CreateStagedSkeleton；
3. 从 DLL 读取 simple name；
4. 检查名字在 expected closure；
5. 检查 baseline 同名存在；
6. 检查本事务 duplicate；
7. 保存 Hash/MVID，由 native 可选核验；
8. 加入 staging map；
9. 当 expected 集合全部存在后状态可变为 Staged，或显式调用 `FinishStaging`。

PDB：

- Development patch 可包含；
- Release 可为空；
- PDB 失败是否阻止 DLL 由设置决定；
- DLL bytes 必须保持到 InterpreterImage 生命周期结束。

## 任务 03.7：Staging resolver

实现线程/事务受控解析：

```cpp
const Il2CppAssembly* ResolveForStaging(const char* name);
```

规则：

```text
if current state in Staging/Staged/Validated
and name in transaction staging map:
    return staged assembly

if name in closure but not yet staged:
    return Missing, not baseline

otherwise:
    return active/baseline external assembly
```

最关键约束：

> 如果引用名属于闭包但对应 DLL 未 Stage，绝不能静默解析到 AOT baseline。

否则 patch metadata 会混入旧类型世界。

## 任务 03.8：ValidateTransaction

校验顺序：

1. expected closure 与 actual staged 集合完全相同；
2. 每个 staged assembly 内部 name 与 manifest 相同；
3. baseline exists；
4. source/runtime ABI 匹配；
5. AssemblyRef：
   - 对 closure 成员必须解析到 staged；
   - 对外部依赖必须解析到允许的稳定 AOT；
   - 不得引用固定 Bootstrap 之外的非-shadow业务 AOT；
6. 所有 runtime metadata 初始化成功；
7. 无 candidate baseline use；
8. 依赖顺序有效；
9. 无 module initializer 已运行；
10. 无程序集已 ordinary publish。

输出详细 report，不只返回 bool。

## 任务 03.9：锁模型

明确锁顺序，写入源码注释和文档：

```text
1. AssemblyShadow transaction lock
2. vm::g_MetadataLock
3. vm::Assembly s_assemblyLock
4. Reflection/cache specific lock
```

若现有上游代码顺序不同，应减少同时持锁范围，而不是建立反向顺序。

要求：

- Stage 主要在单线程 Bootstrap 中执行；
- 不在持 metadata lock 时调用可能进入 managed 的方法；
- module initializer 运行时不能持 registry lock；
- diagnostics 不可在锁内做大 JSON 分配。

使用 ThreadSanitizer 的平台有限，但至少写并发压力单元测试：

- 非 Shadow 线程反复 `Assembly.Load`；
- Bootstrap Stage；
- Commit 前后查询；
- 不死锁、不读半成品 snapshot。

## 任务 03.10：CommitTransaction

建议分五步：

### Step 1：最后验证

状态必须 `Validated`；再次检查 usage generation 和 expected set。

### Step 2：物理 publish

对 staged assemblies：

```text
MetadataCache::RegisterInterpreterAssembly
Assembly::Register
```

但普通逻辑查询仍由 old snapshot 控制，直到 Step 3。

需要修改 `RegisterInterpreterAssembly`，避免重复调用 `Assembly::Register` 或支持明确 publish mode。

### Step 3：发布 Active Snapshot

在锁内构建 immutable snapshot：

```text
name → staged assembly
baseline assembly → staged assembly
baseline image → staged image
generation++
```

一次交换指针，不逐条暴露半提交状态。

### Step 4：刷新枚举版本

通知 `Assembly::GetAllAssemblies` snapshot 失效。M04 实现逻辑去重，此阶段至少 bump version。

### Step 5：退出锁并运行 module initializer

按依赖拓扑顺序：

```text
Contracts
Extensibility
Internal
Consumers
```

若失败：

- state = FailedAfterCommit；
- 写 diagnostics；
- 抛 managed exception 或 fail-fast；
- Bootstrap 必须终止业务启动；
- 不允许 `AbortTransaction` 后继续 baseline。

全部成功后：

```text
state = Committed
frozen = true
```

## 任务 03.11：AbortTransaction

只允许：

```text
Staging
Staged
Validated
```

执行：

- 移除 staging map；
- 释放可安全释放的临时结构；
- InterpreterImage 当前可能缺少完整释放能力，若无法释放，记录内存泄漏但不公开程序集；
- state = Aborted；
- 本进程是否允许回到 CandidatesRegistered：
  - MVP 推荐允许一次重新 Begin 仅在没有创建 global image metadata 时；
  - 若无法证明清理完整，则 Abort 后直接回退 baseline 并禁止第二事务。

文档必须明确实际选择。

## 任务 03.12：InternalCall 注册

在 `hybridclr/RuntimeApi.cpp` 注册：

```text
HybridCLR.AssemblyShadowRuntime::ConfigureCandidates
HybridCLR.AssemblyShadowRuntime::BeginTransaction
HybridCLR.AssemblyShadowRuntime::StageAssembly
HybridCLR.AssemblyShadowRuntime::ValidateTransaction
HybridCLR.AssemblyShadowRuntime::CommitTransaction
HybridCLR.AssemblyShadowRuntime::AbortTransaction
HybridCLR.AssemblyShadowRuntime::GetState
HybridCLR.AssemblyShadowRuntime::GetAssemblyExecutionMode
HybridCLR.AssemblyShadowRuntime::GetDiagnosticsJson
```

要求：

- `byte[]` pin/copy 生命周期明确；
- native 异常映射为稳定 error code，非预期异常才 Raise；
- Release 构建不返回原始内存地址，Development 可返回；
- API 有 XML docs；
- Editor simulation 明确返回 `NotSupported` 或模拟状态。

## 任务 03.13：Usage Guard 最小骨架

新增：

```cpp
enum class BaselineUseKind
{
    AssemblyReflection,
    TypeReflection,
    ClassInit,
    ObjectAllocation,
    StaticField,
    VTable,
    MonoScript,
};
```

Candidate 注册后，记录：

```text
first use kind
assembly
type
detail
thread
timestamp
```

M03 先在 M01 已确认的关键入口接入；M05-M07 扩展覆盖。

Commit 时若 closure candidate 有 use record：

```text
BaselineAlreadyUsed
```

## Demo 测试

### T03-01 单程序集成功

- Configure candidates；
- Begin P01；
- Stage Internal；
- Validate；
- Commit；
- state = Committed。

### T03-02 多程序集成功

P03：

- Stage 顺序随机；
- skeleton 全部可见后 metadata 初始化；
- Commit load order 稳定。

### T03-03 缺少程序集

Manifest closure 有 3 个，只 Stage 2 个：

```text
Validate = ClosureMemberMissing
```

### T03-04 多余程序集

Stage 非 expected candidate：

```text
Stage = UnexpectedClosureMember
```

### T03-05 同名重复

第二次 Stage 同一 DLL：

```text
DuplicateAssemblyName
```

### T03-06 错 baseline build ID

Begin 失败，不创建任何 image。

### T03-07 initializer 时序

补丁 module initializer 写入日志：

- Stage 后未执行；
- Validate 后未执行；
- Active Snapshot publish 后执行一次。

### T03-08 initializer 失败

- Commit 进入 FailedAfterCommit；
- 业务入口不执行；
- 下次启动回退标记由 demo 模拟。

### T03-09 Shadow 关闭

宏关闭时所有 API返回 FeatureDisabled；普通 HybridCLR 回归通过。

## 诊断样例

```json
{
  "state": "Validated",
  "patchId": "P03",
  "expected": 5,
  "staged": 5,
  "assemblies": [
    {
      "name": "AssemblyA.Contracts",
      "baseline": "0x...",
      "staged": "0x...",
      "metadataInitialized": true,
      "published": false,
      "moduleInitializerRan": false
    }
  ],
  "baselineUses": []
}
```

## Code Review 检查点

- Stage 是否真正不公开；
- module initializer 是否真正延迟；
- closure missing 是否禁止 baseline fallback；
- Active Snapshot 是否一次发布；
- 锁顺序是否明确；
- Commit 后失败是否没有伪装成可回退；
- InternalCall 的 byte 生命周期是否安全；
- Shadow 关闭是否保持原行为；
- 是否还有 M01 hard-coded prototype 残留；
- state transition 是否有单元测试覆盖。

## 完成标准

- T03-01 至 T03-09 通过；
- 多程序集可任意 Stage 顺序并正确初始化；
- Commit 前普通 Assembly 枚举看不到 staged；
- Commit 后状态冻结；
- module initializer 时序通过；
- Usage Guard 最小版本工作；
- 独立 review 通过；
- 创建 M03 tag并更新 source pins。
