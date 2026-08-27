# Milestone 04：Assembly、AssemblyRef 与 AppDomain 统一活动解析

## 目标

让所有程序集级语义查询在 Shadow Commit 后返回同一个 Active Interpreter Assembly，并隐藏同名 AOT baseline。解决 M01/M03 中“某些 API AOT-first、某些 API 后注册优先”的不一致。

本 Milestone 完成后，应满足：

```text
Assembly.Load
Assembly.GetExecutingAssembly相关路径
AppDomain.GetAssemblies
Assembly.GetReferencedAssemblies
MetadataCache按名查询
Interpreter/AOT AssemblyRef解析
```

对同一个逻辑程序集给出一致结果。

## 进入条件

- M03 正式事务可工作；
- Active Snapshot 能原子发布；
- P01/P03 patch 可 Stage/Commit；
- 已有 Assembly resolver 路径日志。

## 核心原则

1. 所有名称解析先查询 Active Snapshot。
2. Staging resolver 与 Committed resolver 是两个明确模式。
3. 物理 AOT Assembly 保留，但普通业务只看到逻辑 active view。
4. 不能依赖 `s_Assemblies` 注册顺序。
5. 不全局改写 `GetAssemblyFromIndex` 物理索引。
6. 闭包内引用找不到 staged member 时立即失败，禁止 fallback baseline。
7. Assembly list snapshot 必须在 Commit 后失效并去重。

## 任务 04.1：整理 Assembly Resolver API

在 `AssemblyShadow` 中固定以下 API：

```cpp
enum class AssemblyResolveContext
{
    Normal,
    Staging,
    DiagnosticsPhysical,
};

const Il2CppAssembly* ResolveByName(
    const char* name,
    AssemblyResolveContext context);

const Il2CppAssembly* ResolveAssembly(
    const Il2CppAssembly* physicalAssembly);

const Il2CppAssembly* ResolveReferencedAssembly(
    const Il2CppAssembly* requester,
    const Il2CppAssembly* physicalReferencedAssembly,
    const char* referencedName);
```

要求：

- 名称规范化只有一个实现；
- 大小写行为与上游一致；
- `.dll` 和路径形式都支持；
- diagnostics physical 模式永不映射；
- 不能从 resolver 内调用会再次进入 resolver 的高层 API。

## 任务 04.2：修改 `MetadataCache::GetAssemblyByName`

现状 AOT table 先于 Interpreter list。改为：

```cpp
if (AssemblyShadow enabled)
{
    if (auto active = AssemblyShadow::ResolveByName(name, currentContext))
        return active;
}
return GetAssemblyByNameOriginal(name);
```

为了避免 resolver 调用自身，拆出：

```cpp
GetAssemblyByNamePhysicalAot
GetAssemblyByNamePhysicalInterpreter
GetAssemblyByNameOriginal
```

单元测试：

- 未启用：结果与上游一致；
- candidate 未 Commit：仍 AOT；
- staging transaction 内部解析 closure member：staged；
-普通业务线程 Stage 时查询：仍 AOT；
- Commit 后：shadow；
- 名称含 `.dll`：shadow；
- 大小写变化：行为一致。

## 任务 04.3：修改 `Assembly::GetLoadedAssembly`

当前逆序扫描不是可靠契约。改为：

```cpp
if (active = AssemblyShadow::ResolveByName(name, Normal))
    return active;

return GetLoadedAssemblyPhysical(name);
```

新增物理 API供 registry 和诊断：

```cpp
const Il2CppAssembly* GetLoadedAssemblyPhysical(
    const char* name,
    PhysicalAssemblyPreference preference);
```

Preference：

```text
AotOnly
InterpreterOnly
AnyNewest
AnyOldest
```

普通业务不得使用物理 API。

## 任务 04.4：修改 `Assembly::Load`

流程：

```text
normalize name
→ active resolver
→ original metadata cache/load hook
→ active resolve result again
```

需要保留上游 resolve hook/event 行为。不要为了 Shadow 直接跳过：

- assembly resolve callback；
- bundle/external assembly resolver；
- Placeholder assembly；
- 标准 HybridCLR load。

测试：

```csharp
Assembly.Load("AssemblyA.Contracts")
Assembly.Load("AssemblyA.Contracts.dll")
Assembly.Load(new AssemblyName("AssemblyA.Contracts"))
```

均返回同一个 Reflection Assembly 对象，M05 会确保 cache key 是 active pointer。

## 任务 04.5：AssemblyRef 解析

重点修改：

```text
MetadataCache::GetReferencedAssembly
Assembly::GetReferencedAssemblies
GlobalMetadata相关AssemblyRef路径
InterpreterImage/MetadataModule的AssemblyRef路径
```

实现步骤：

1. 获取 requester 的 active identity；
2. 取得物理 referenced assembly/name；
3. 调用 `ResolveReferencedAssembly`；
4. 若 referenced name 属于本事务 closure：
   - Staging：必须 staged；
   - Committed：必须 active shadow；
5. 若 referenced name 不在 closure：
   - 必须是允许的外部稳定 AOT；
   - 若它实际是 changed provider 但未进入 closure，返回错误；
6. 记录 requester → provider → resolved pointer。

不要仅根据 requester 是否 Interpreter 决定。Unity native 可能从 baseline image 发起名字查询，仍应得到 active provider。

## 任务 04.6：逻辑 Assembly 枚举

当前 `Assembly::GetAllAssemblies` 有 snapshot。修改 `CopyValidAssemblies` 或增加逻辑构建层：

```cpp
void CopyLogicalActiveAssemblies(
    AssemblyVector& output,
    const AssemblyVector& physical);
```

规则：

1. 遍历物理列表；
2. baseline 若被 Shadow，跳过；
3. active shadow 保留；
4. 未 shadow 物理程序集保留；
5. 以 canonical simple name 去重；
6. 输出顺序稳定：
   - 保持 baseline 逻辑顺序；
   - shadow 占据 baseline 的逻辑位置；
   - 追加普通动态程序集；
7. Placeholder/无 token 仍按上游规则过滤。

Commit 时：

```text
s_assemblyVersion++
invalidate snapshot
```

提供 diagnostics：

```cpp
GetAllPhysicalAssemblies
```

但不通过普通 AppDomain 暴露。

## 任务 04.7：AppDomain icall

检查 Unity 2022：

```text
libil2cpp/icalls/mscorlib/System/AppDomain.cpp
```

所有 `GetAssemblies` 变体应使用逻辑 active list。

验证：

```csharp
Assembly[] assemblies =
    AppDomain.CurrentDomain.GetAssemblies();

assemblies
    .Where(a => a.GetName().Name == "AssemblyA.Contracts")
    .Count() == 1
```

同时验证：

- AOT baseline Reflection Assembly 未被意外返回；
- 普通 dynamic HybridCLR assembly 仍被返回；
- ordering 不影响现有逻辑；
- Commit 前/后 snapshot 正确刷新。

## 任务 04.8：Assembly.GetReferencedAssemblies

对 active shadow Assembly：

```csharp
assembly.GetReferencedAssemblies()
```

应返回逻辑 active identity，不泄露 baseline 物理对象；注意返回值是 `AssemblyName`，名称通常相同，但必须验证版本、公钥 token 与 patch 编译一致。

对未 shadow AOT Assembly：

- 若它没有引用 closure，保持原行为；
- 若它引用 shadow provider，则构建期本应将它纳入 closure；
- Development runtime 应报依赖闭包违规，而不是默默返回 baseline。

## 任务 04.9：Assembly equality 与反射对象一致性准备

M04 先保证 native pointer resolve；M05 修改 reflection cache。增加测试占位：

```csharp
Assembly a1 = Assembly.Load(name);
Assembly a2 = Type.GetType(typeName).Assembly;
Assembly a3 = AppDomain...Single(...);

Assert.AreSame(a1, a2);
Assert.AreSame(a1, a3);
```

若当前失败，诊断应明确指向 Reflection cache，而不是 Assembly resolver。

## 任务 04.10：闭包逃逸检测

在 Development 构建中，当非闭包 AOT requester 解析到 closure provider 时：

```text
ShadowClosureViolation
Requester=...
Provider=...
ReferenceIndex=...
```

处理：

- 在 Validate 阶段可静态发现：Commit 拒绝；
- 运行时才发现：开发构建 fail-fast；
- Release 构建也不能 fallback baseline，返回受控 fatal error。

## 任务 04.11：回归保护

新增 runtime feature off tests：

```text
普通AOT Assembly.Load
普通HybridCLR Assembly.Load
Placeholder assembly
补充元数据加载
AppDomain枚举
AssemblyResolve callback
重复加载错误
```

确保 Active Resolver 未启用时不改变：

- 查找顺序；
- exception；
- assembly count；
- 性能基线。

## Demo 测试

### T04-01 P01

Internal Shadow：

```text
Assembly.Load(Internal) → shadow
Assembly.Load(Contracts) → AOT
AppDomain Internal count = 1
AppDomain Contracts count = 1
```

### T04-02 P03

Contracts + 全依赖闭包 Shadow：

```text
所有闭包Assembly.Load → shadow
外部Unity/BCL → AOT
AppDomain每个逻辑名count=1
```

### T04-03 Stage 可见性

Stage P03 但未 Commit：

```text
普通Assembly.Load → baseline AOT
事务内部AssemblyRef → staged
AppDomain不含staged
```

### T04-04 缺失 closure

Internal staged 但 Contracts 被声明在 closure、未 staged：

```text
metadata init/validate失败
不得解析到AOT Contracts
```

### T04-05 外部 AOT consumer

故意让非-shadow assembly 引用 Contracts：

```text
Validate或runtime guard失败
给出完整依赖路径
```

### T04-06 名称变体

```text
AssemblyA.Contracts
AssemblyA.Contracts.dll
path/AssemblyA.Contracts.dll
大小写变体
```

均按预期。

## 性能测试

在未启用 Shadow 和已 Commit 两种模式各执行 100 万次受控 name lookup 基准；注意这不是游戏常规每帧路径，但用于防止低效字符串分配。

要求：

- resolver 内不反复分配 lowercase string；
- canonical name 可缓存；
- active map lookup 为 O(1)；
- 非 Shadow 名称快速失败；
- 结果记录到 benchmark JSON。

## Code Review 检查点

- 是否还有 AOT-first 绕过；
- staging 与 normal resolver 是否隔离；
- 是否错误修改固定 AOT index；
- AppDomain 是否逻辑去重；
- snapshot 是否在 Commit 后失效；
- closure missing 是否绝不 fallback；
- feature off 是否无回归；
- resolver 是否有递归调用和锁反转；
- 日志是否能指出 requester/provider。

## 完成标准

- T04-01 至 T04-06 全部通过；
- AppDomain 每个 Shadow logical name 只返回一个 active Assembly；
- AssemblyRef 在 P03 中全部指向 staged/active closure；
- 未 Shadow 程序集保持 AOT；
- 回归和性能测试完成；
- 独立 review 通过并创建 M04 tag。
