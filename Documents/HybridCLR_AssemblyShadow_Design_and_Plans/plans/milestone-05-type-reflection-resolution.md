# Milestone 05：Image、Class、Type、Reflection 与缓存统一

## 目标

在 Assembly 级解析统一的基础上，让所有类型级语义查询和反射对象都指向 Active Shadow 类型世界。解决：

- baseline `Il2CppImage*` 继续被调用；
- Unity/native 路径携带 baseline `Il2CppClass*`；
- `Type.GetType`、`Assembly.GetType` 不一致；
- Reflection cache 以 baseline pointer 命中旧对象；
- `MonoScript.GetClass`、对象创建前仍可能拿到 baseline class；
- nested/generic type 的稳定映射。

完成后达到 Gate 2：

> Shadow Commit 后，普通业务可观察到的 Assembly、Image、Class、Type 和 Reflection 对象形成唯一的 active 逻辑世界；任何 baseline 类型使用都被阻止或明确诊断。

## 进入条件

- M04 Assembly/AppDomain 一致；
- M01 记录了 Prefab/Scene 的实际类型恢复路径；
- P01/P03 可稳定 Commit；
- Usage Guard 最小骨架存在。

## 核心安全原则

1. 映射的是**类型句柄解析结果**，不是改写已经创建的对象。
2. 不允许把 baseline 对象 reinterpret 成 shadow 对象。
3. `ResolveClass` 只对已 Committed 的 candidate 生效。
4. 类型不存在或布局不兼容时必须失败。
5. Reflection cache 必须在 key 生成前解析 active pointer。
6. Commit 前 baseline Reflection/Class 使用应被 Usage Guard 阻止。
7. 固定 AOT 代码不得持有业务具体 `typeof(T)`；构建工具负责阻止。
8. 泛型映射必须基于 active generic definition 和 active generic arguments，不复制 baseline runtime generic instance 指针。

## 任务 05.1：定义稳定 TypeKey

新增：

```text
libil2cpp/vm/AssemblyShadowTypeKey.h
libil2cpp/vm/AssemblyShadowTypeKey.cpp
```

`TypeKey`：

```cpp
struct ShadowTypeKey
{
    std::string assemblyName;
    std::string namespaze;
    std::vector<std::string> nestingPath;
    std::string typeName;
    uint16_t genericArity;
};
```

规范化：

- nested type 使用声明链，不只用 `Outer/Inner` 字符串；
- generic arity 从 metadata 读取；
- 不用 metadata token；
- 不把 assembly version 当作 logical key；
- name comparison 与 CLR/IL2CPP 实际规则一致，类型名通常区分大小写；
- 数组、指针、byref、generic instance 不是 definition key，另行重建。

提供：

```cpp
ShadowTypeKey MakeTypeKey(const Il2CppClass*);
ShadowTypeKey MakeTypeKey(const Il2CppType*);
```

Development 构建可输出字符串：

```text
AssemblyA.Implementation.Internal::
AssemblyA.Implementation.Internal.VersionedPrefabComponent`0
```

## 任务 05.2：建立 baseline definition → shadow definition 映射

Commit 后不立即 materialize 所有 class，优先 lazy：

```cpp
Il2CppClass* ResolveClassDefinition(Il2CppClass* baseline);
```

流程：

1. 判定 baseline class 所属 assembly；
2. 若不被 Shadow，原样返回；
3. 生成 TypeKey；
4. 查 active shadow image；
5. 按 namespace/nested/type name 查 class；
6. 核对 generic arity；
7. 缓存 baseline pointer → shadow pointer；
8. 记录 resolver hit/miss。

错误：

```text
ShadowTypeNotFound
ShadowTypeKindMismatch
ShadowGenericArityMismatch
```

MVP 对 patch 删除 baseline 类型采取严格失败。如果被旧 AssetBundle 引用，更早由 Resource ABI 检查阻止。

## 任务 05.3：复合 Type 映射

实现：

```cpp
const Il2CppType* ResolveType(const Il2CppType* type);
```

分支：

- class/value type：ResolveClass；
- array/szarray：active element type + 重新构造 array class；
- pointer：active element；
- byref：active element；
- generic parameter：保持当前 context；
- generic instance：
  - active generic definition；
  - 每个 generic arg 递归 ResolveType；
  - 使用 MetadataCache/GenericClass API inflate；
- function pointer：按 Unity 2022 支持情况；
- modified type：保留修饰并映射 underlying type。

禁止直接复制 baseline `Il2CppGenericClass*` 到 shadow definition。

测试中加入：

```text
List<ShadowType>
Dictionary<string, ShadowType>
ShadowGeneric<int>
ShadowGeneric<ShadowDto>
ShadowType[]
ShadowType&
```

## 任务 05.4：Image 解析 Hook

根据 M01 调用链，修改至少：

```text
Image::ClassFromName
Image::ClassFromNameCaseInsensitive
Image::FromTypeNameParseInfo
Image::GetTypes
Image::GetEntryPoint
```

统一：

```cpp
image = AssemblyShadow::ResolveImage(image);
```

要求：

- active shadow image 输入保持原样；
- non-shadow image 快速返回；
- staging context 不泄露给普通业务；
- 避免 `ResolveImage → ResolveAssembly → Assembly API → ResolveImage` 递归；
- 图像映射命中率可诊断。

## 任务 05.5：Class 获取与初始化入口

检查并根据调用链选择修改：

```text
Class::FromIl2CppType
Class::FromName
Class::Init
Class::GetNestedTypes
Class::GetParent
Class::IsAssignableFrom
Class::HasParent
```

策略：

### 查询入口

返回 active class。

### `Class::Init`

不要简单在函数开头把任意 baseline class 替换后继续，因为调用者可能期望原 pointer 被原地初始化。更安全：

- 语义级调用点在进入 `Class::Init` 前 resolve；
- 若 `Class::Init` 直接收到 shadowed baseline：
  - Development：记录 BaselineUseKind.ClassInit 并 fail；
  - Release：返回受控 fatal，不能初始化 baseline；
- 对 Unity 资源恢复路径，确保更早 `ResolveClass`。

M01 若证明 Unity 直接对 baseline class 调 `Class::Init`，可在受控宏下重定向，但必须检查调用者后续是否继续使用原 pointer。

## 任务 05.6：Object 创建入口

检查：

```text
Object::New
Object::NewAllocSpecific
Array::NewSpecific
Runtime::ObjectInit
```

规则：

- 正常 active class：原路径；
- shadowed baseline class：
  - 先尝试 `ResolveClass`；
  - Resource ABI 已验证；
  - 记录 `ClassHandleRemappedAtAllocation`；
- 若 baseline class 已初始化或有实例：
  - Usage Guard 失败；
- value type boxing 同样需要 active class/type。

在 Development 中为每个映射分配记录：

```text
source class
target class
call path
object size baseline/shadow
```

若大小不同且来源是旧 AssetBundle：

- Resource ABI 检查理论上已阻止；
- runtime 再次 fail-fast。

## 任务 05.7：`Type.GetType` 路径

检查：

```text
vm/Type.cpp
icalls/mscorlib/System/Type.cpp
TypeNameParser
Image::FromTypeNameParseInfo
Assembly::Load
```

覆盖：

```csharp
Type.GetType("Namespace.Type, Assembly")
Type.GetType(name, throwOnError: true)
Type.GetType(name, assemblyResolver, typeResolver)
Type.GetType("Namespace.Outer+Inner, Assembly")
Type.GetType("Namespace.Generic`1[[...]], Assembly")
```

期望：

- assembly resolver 得到 active assembly；
- type parser 使用 active image；
- 返回 reflection Type 的 native type 是 active；
- baseline Type 不进入 Reflection cache。

## 任务 05.8：`Assembly.GetType` 与 Module

检查 `System.Reflection.Assembly` icall：

```text
assembly reflection object
→ active assembly pointer
→ active image
→ active class
→ active Type object
```

验证：

```csharp
assembly.GetType(fullName)
assembly.ManifestModule.GetType(fullName)
assembly.GetTypes()
assembly.DefinedTypes
assembly.ExportedTypes
```

全部只枚举 patch 类型定义。

如果 patch 新增类型：

- `Assembly.GetTypes` 必须能看到；
- baseline AssetBundle不会引用新增类型，但运行时代码可以创建。

如果 patch 删除类型：

- `GetTypes` 不再看到；
- baseline 资源若引用则 patch build 应拒绝。

## 任务 05.9：Reflection Assembly/Module cache

修改：

```cpp
Reflection::GetAssemblyObject
Reflection::GetModuleObject
```

先映射：

```cpp
assembly = ResolveAssembly(assembly);
image = ResolveImage(image);
```

然后构造 cache key。

Commit 前若为 candidate baseline 创建 Reflection object：

```text
RecordBaselineUse(AssemblyReflection/ModuleReflection)
```

Commit 必须失败。

不要尝试遍历 managed heap 删除旧 Reflection Assembly。

## 任务 05.10：Reflection Type cache

当前 Type cache 以 `Il2CppType*` 为 key。流程改为：

```cpp
type = AssemblyShadow::ResolveType(type);
cache.TryGetValue(type)
```

注意：

- ResolveType 可能创建 generic/array type，需要 metadata lock；
- Reflection cache lock与metadata lock顺序要符合 M03；
- 不在 cache lock 内执行复杂 type inflate；
- 对 non-shadow type 应接近零开销。

Commit 前 baseline Type object：

```text
RecordBaselineUse(TypeReflection)
```

## 任务 05.11：Reflection Member 对象

对于：

```text
GetMethodObject
GetFieldObject
GetPropertyObject
GetEventObject
GetParamObjects
```

主要原则是调用方 class/method 应已经 active。增加 Development 断言：

```text
method->klass不属于shadowed baseline
field->parent不属于shadowed baseline
refclass不属于shadowed baseline
parameter type已active
```

若某路径传入 baseline member：

- 不按 token 映射；
- 通过 TypeKey + member canonical signature 在 active class 中重新查找；
- 仅在确定必要时实现；
- 先用日志定位实际路径。

MemberKey：

```text
TypeKey
member name
member kind
generic arity
parameter canonical types
return/field type
```

不要只用 metadata token。

## 任务 05.12：Assignability 与 cast

闭包内 Interpreter 代码应自然使用 shadow class。仍需测试：

```csharp
obj is IVersionTextProvider
(IVersionTextProvider)obj
baseRef is VersionedPrefabComponent
typeof(Base).IsAssignableFrom(typeof(Derived))
interfaceType.IsInstanceOfType(obj)
```

Contracts 若不在 P01 closure，接口 Type 是 AOT；Internal shadow class 可以实现 AOT Contracts 接口，这是一种合法跨边界：

```text
Shadow Internal class
→ stable AOT Contracts interface
```

但当 Contracts 也 Shadow（P03）时，Internal patch 必须实现 Shadow Contracts interface，所有消费者进入 closure。

测试必须分别覆盖 P01 与 P03。

## 任务 05.13：Usage Guard 完整化

扩展记录入口：

```text
Assembly/GetAssemblyObject
Image/Class name lookup that materializes baseline class
Reflection Type
Class Init
VTable setup
Static field
Object allocation
MonoScript.GetClass
```

候选注册后，baseline 仅“被物理枚举”不算使用；以下算使用：

- class 被初始化；
- object 被创建；
- reflection object 暴露给 managed；
- static storage 被访问；
- vtable 被 setup；
- Unity script class 被绑定到资源实例。

Commit error report：

```json
{
  "code": "BaselineAlreadyUsed",
  "assembly": "AssemblyA.Implementation.Internal",
  "kind": "MonoScript",
  "type": "...VersionedPrefabComponent",
  "firstUseSequence": 17,
  "thread": 1,
  "detail": "Business bundle loaded before shadow commit"
}
```

## 任务 05.14：Active Type diagnostics

新增 C#：

```csharp
AssemblyShadowRuntime.GetTypeResolutionInfo(Type type)
```

返回：

```text
logical assembly
execution mode
is active
physical image kind
baseline type pointer（development）
active type pointer（development）
type key
```

测试不能只依靠业务返回字符串，应验证 runtime 类型身份。

## Demo 测试

### T05-01 Type.GetType

P01/P03 所有名称形式返回 active。

### T05-02 Assembly.GetTypes

Patch 新增一个 Internal 类型，列表可见。

### T05-03 Reflection cache

Commit 前不访问；Commit 后多次查询返回 same managed Type/Assembly object。

### T05-04 早期反射

Commit 前创建 baseline Type，Commit 返回 BaselineAlreadyUsed。

### T05-05 Nested/generic/array

所有复合类型由 active definition 构造。

### T05-06 Interface P01

Shadow Internal instance 可 cast 到 AOT Contracts。

### T05-07 Interface P03

Shadow Internal instance只实现 Shadow Contracts，所有 shadow consumer 正确。

### T05-08 old Prefab

旧 Bundle 的 `MonoScript.GetClass`、component.GetType、Object allocation 全部 active。

### T05-09 Object size mismatch

构造故意不兼容 patch，runtime fail-fast且 patch build 已提前拒绝。

### T05-10 AppDomain/Reflection identity

```text
Assembly.Load(name)
Type.Assembly
AppDomain assembly
ManifestModule.Assembly
```

managed reference 全部一致。

## Code Review 检查点

- 是否映射 handle 而不是 reinterpret 旧 object；
- TypeKey 是否稳定；
- generic type 是否重新 inflate；
- Reflection cache 是否先 resolve 再 key；
- 是否有 token-only member mapping；
- Class::Init/Object::New 的重定向是否有充分调用链证据；
- Usage Guard 是否覆盖早期反射；
- P01 AOT Contracts 与 P03 Shadow Contracts 是否都测；
- non-shadow 快速路径是否保持；
- 锁顺序是否安全。

## 完成标准

- T05-01 至 T05-10 通过；
- Gate 2 获批；
- Shadow Commit 后不再有普通 API 可观察的 baseline Type；
- 早期 baseline 使用能阻止 Commit；
- old Prefab/Scene 仍通过；
- 独立 review 通过并创建 M05 tag。
