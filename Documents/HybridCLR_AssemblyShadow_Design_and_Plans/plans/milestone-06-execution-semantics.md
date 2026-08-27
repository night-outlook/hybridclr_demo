# Milestone 06：执行语义、静态状态、虚表、接口、Delegate、泛型与预热

## 目标

证明 Assembly Shadow 不只是“反射能找到新类型”，而是能正确执行复杂业务语义：

- constructor/newobj；
- static field、`.cctor`、module initializer；
- inheritance；
- virtual/interface dispatch；
- delegate；
- generic type/method；
- exception；
- async/state machine；
- AOT ↔ Interpreter bridge；
- first-call warmup。

完成后，Contracts、Extensibility、Internal 的典型调用链可在不同 closure 组合下正确运行。

## 进入条件

- Gate 2 通过；
- Assembly/Type/Reflection 逻辑世界一致；
- Usage Guard 可阻止 baseline class/object；
- Resource ABI 工具可识别明显布局变化；
- M03 module initializer 已延迟。

## 核心原则

1. 不给每个 AOT 方法增加运行时分发；依赖闭包保证基线业务 AOT 不执行。
2. Shadow class 的静态存储独立于 baseline。
3. P01 可合法使用稳定 AOT Contracts；P03 必须使用 Shadow Contracts。
4. MethodBridge/AOT generic generator 必须扫描当前 closure DLL。
5. 解释器首次转换成本在 Commit 后、业务启动前预热。
6. 任何 baseline MethodInfo 执行都视为 closure 违规。
7. 先建立 correctness matrix，再做性能优化。

## 任务 06.1：新增执行模式断言

Native 增加：

```cpp
bool AssemblyShadow::AssertMethodIsActive(
    const MethodInfo* method,
    const char* operation);
```

Development 构建在以下入口检查：

- Interpreter invoke；
- Runtime::Invoke；
- virtual invoke；
- delegate invoke bridge；
- constructor；
- static constructor；
- reverse P/Invoke，若涉及 candidate。

规则：

```text
method->klass属于shadowed baseline
    → fail with BaselineMethodExecution
```

生产构建至少记录 fatal，不允许静默执行旧业务逻辑。

## 任务 06.2：constructor 与 `newobj`

测试类型：

```csharp
public sealed class ComplexHotClass : BaseHotClass, IHotInterface
{
    private static readonly Helper StaticHelper = CreateStaticHelper();

    private readonly Helper _helper;
    private readonly List<DemoValue> _values;

    public ComplexHotClass()
    {
        _helper = new Helper();
        _values = new List<DemoValue>();
        Initialize();
    }
}
```

覆盖：

- base `.ctor`；
- field initializer；
- static field；
- nested object；
- generic collection；
- virtual call，注意 constructor 内虚调用风险；
- exception；
- class with no explicit constructor。

验证第一次和第二次 new：

```text
type/class/method均active
baseline cctor count = 0
shadow cctor count = 1
constructor result = patch
```

## 任务 06.3：静态字段隔离

在 baseline 和 patch 使用不同静态标记：

```csharp
public static int StaticGeneration = 100; // baseline
public static int StaticGeneration = 200; // patch
```

测试：

- Commit 前不得读取 candidate baseline static；
- Commit 后读取 200；
- baseline storage 保持物理存在但未初始化；
- multiple shadow types 独立；
- generic static per closed type：
  ```text
  GenericState<int>
  GenericState<string>
  ```
- `beforefieldinit` 与显式 `.cctor` 分别测试。

增加 native diagnostics：

```text
baselineClassCctorStarted
shadowClassCctorStarted
staticStoragePointer
```

Release 日志不暴露地址。

## 任务 06.4：module initializer

创建：

```csharp
[module: ...] // 按编译器支持方式生成模块初始化器
```

或显式 `<Module>..cctor` fixture。

测试：

1. Stage：未执行；
2. Validate：未执行；
3. Active mapping publish；
4. initializer 按 load order 执行；
5. initializer 中引用 Contracts/Extensibility 得到 staged/active；
6. 每个 assembly 执行一次；
7. initializer 抛异常：
   - state FailedAfterCommit；
   - 业务入口不执行；
   - result file 标记；
   - 下次启动回退。

禁止 initializer：

- 启动线程外并发；
- 下载资源；
- 写不可回滚持久状态；
- 启动业务 Scene。

工具应产生 warning。

## 任务 06.5：inheritance 与虚表

Demo 类型链：

```text
UnityEngine.MonoBehaviour (AOT)
  ↓
VersionedComponentBase (Extensibility)
  ↓
VersionedPrefabComponent (Internal)
  ↓
OptionalInternalDerived (Internal)
```

另有外部：

```text
VersionedComponentBase
  ↓
DerivedExternalComponent (ExtensibilityConsumer)
```

补丁矩阵：

### P01 Internal changed

```text
Extensibility AOT
Internal Shadow
```

验证 Shadow derived 可继承 AOT base，override dispatch 正确。

### P02 Extensibility changed

```text
Extensibility Shadow
Internal Shadow
ExtensibilityConsumer Shadow
```

验证所有派生者进入 closure，虚表全部由 patch metadata 构建。

### P03 Contracts changed

完整闭包 Shadow。

测试：

- base virtual；
- override；
- sealed override；
- abstract method；
- `base.Method()`；
- interface default implementation，按运行时支持；
- property/event virtual accessor；
- Unity message method，例如 `Awake`/`Start`/`Update`，在 M07 扩展。

记录 vtable setup 中是否出现 baseline candidate method pointer。

## 任务 06.6：接口调用

接口来自：

- AOT Contracts（P01）；
- Shadow Contracts（P03）；
- BCL；
- Unity 接口。

测试：

```csharp
IHotInterface x = component;
x.Execute();
((IHotInterface)component).Execute();
typeof(IHotInterface).IsAssignableFrom(component.GetType());
```

P03 中确认：

```text
Internal patch Type的interface pointer
    == Contracts patch Type
```

不应指向 baseline Contracts interface。

## 任务 06.7：Delegate 与事件

覆盖：

- instance delegate；
- static delegate；
- virtual method delegate；
- interface method delegate；
- generic delegate；
- lambda；
- closure display class；
- event add/remove；
- multicast delegate；
- AOT fixed boundary delegate，仅允许 primitive/object 参数；
- delegate 保存到静态字段。

测试场景：

```text
AOT Contracts delegate type + Shadow target method
Shadow Contracts delegate type + Shadow target method
Shadow event publisher + Shadow subscriber
AOT Unity callback + Shadow MonoBehaviour
```

检查 MethodBridge 是否已生成，避免只在 Editor 通过。

## 任务 06.8：泛型类型与方法

测试矩阵：

```text
ShadowGeneric<int>
ShadowGeneric<string>
ShadowGeneric<DemoValue>
ShadowGeneric<VersionedPrefabComponent>
Dictionary<string, DemoValue>
List<VersionedPrefabComponent>
GenericMethod<int>()
GenericMethod<DemoValue>()
GenericVirtual<T>()
GenericInterface<T>
Nullable<ShadowStruct>
```

关键验证：

- generic definition 是 active；
- generic args 按 M05 active resolve；
- AOT shared generic bridge 正确；
- value-type 参数 size/align；
- 泛型 static storage 不混 baseline；
- generic method first-call PreJit；
- reflection `MakeGenericType/MakeGenericMethod`。

若补丁引入新的 AOT 泛型实例，确保补充元数据和桥接生成输入覆盖 closure。

## 任务 06.9：Struct 与布局

即使 Resource ABI 不变，结构体 bridge 也敏感。

测试：

```csharp
public struct SmallStruct { int a; float b; }
public struct NestedStruct { SmallStruct x; long y; }
public struct GenericStruct<T> { T value; int id; }
```

覆盖：

- interface 参数/返回；
- delegate；
- virtual method；
- generic；
- array；
- boxing/unboxing；
- ref/out/in；
- nullable；
- P/Invoke 不允许直接使用 shadow struct，除非固定 ABI 且专门支持。

布局变化：

- 闭包内部纯 runtime struct 可修改，因为调用者一同重编译；
- 与固定 AOT/Unity serialization/native 边界相交的 struct 必须 ABI 冻结；
- 构建工具需区分 Runtime ABI 与 Resource/Bootstrap ABI。

## 任务 06.10：异常与堆栈

覆盖：

- shadow method throw/catch；
- AOT BCL exception；
- exception filter；
- finally；
- nested shadow stack；
- reflection invoke 包装；
- async exception；
- stack trace 中 assembly/type/method name。

期望：

- 不显示 baseline method；
- PDB 存在时 Development 有补丁源码行；
- Release 无 PDB 仍可定位 patch MVID/token；
- exception 不破坏 registry state。

## 任务 06.11：async/iterator/state machine

补丁编译会生成状态机类型。测试：

```csharp
async Task<string> GetAsync()
IEnumerable<int> Iterate()
IEnumerator UnityCoroutine()
```

覆盖：

- 新增 compiler-generated type；
- state machine generic；
- continuation；
- Unity coroutine；
- cancellation；
- exception；
- scene unload。

确认 compiler-generated types 在 `Assembly.GetTypes` 和 type map 中正常，不要求旧 AssetBundle引用。

## 任务 06.12：MethodBridge/生成器输入接入

临时在 demo 中手工把 closure DLL 交给：

- MethodBridge generator；
- ReversePInvoke generator；
- AOT generic reference scanner；
- link.xml scanner。

记录每个 generator 当前获取 assemblies 的路径。新增抽象 provider，输入：

```text
normal hot update DLLs
+ current shadow closure DLLs
```

不要把全部 shadow candidates 永久当成 patch 输入；应使用当前 closure，避免无谓生成。

P01、P02、P03 分别生成并 diff：

- 需要的 bridge；
- AOT generic references；
- link entries。

## 任务 06.13：PreJit/Warmup

新增 Patch Manifest 字段：

```json
"warmup": {
  "types": [
    "AssemblyA...VersionedPrefabComponent"
  ],
  "methods": [
    {
      "assembly": "...",
      "type": "...",
      "method": ".ctor",
      "signature": "()"
    }
  ]
}
```

Bootstrap 顺序：

```text
Commit
→ module initializer
→ resolve warmup types/methods
→ RuntimeApi.PreJitMethod/PreJitClass
→ explicit module Warmup
→ business assets
```

建议先使用 reflection + PreJit；后续可实现 token batch API。

测量：

```text
Assembly.Load/Stage
Metadata init
Commit
Module init
PreJit
First new
Second new
First virtual
First generic
```

目标不是本阶段设定绝对毫秒，而是确保业务帧不再出现未解释的首次转换峰值。

## 任务 06.14：禁止的边界

Build validator 增加：

- Burst assembly → shadow candidate 具体类型：失败；
- native P/Invoke signature 使用 shadow type：失败；
- fixed Bootstrap generic<TShadow>：失败；
- `[RuntimeInitializeOnLoadMethod]` 位于 candidate 且可能在 Commit 前运行：失败或强 warning；
- Preloaded Asset 引用 candidate type：失败；
- Script Execution Order 依赖 candidate 在 Bootstrap 前运行：失败。

## Demo 测试集

### T06-01 Complex new

所有 constructor 链 active。

### T06-02 Static/cctor

baseline count 0，shadow count 1。

### T06-03 P01 mixed stable boundary

AOT Contracts + AOT Extensibility + Shadow Internal。

### T06-04 P02 inheritance closure

Extensibility 与所有派生 consumer shadow。

### T06-05 P03 full business closure

Contracts 到 Internal 全 shadow。

### T06-06 delegate/event

所有 delegate bridge 正确。

### T06-07 generic matrix

reference/value type 均通过。

### T06-08 async/iterator

状态机执行和异常正确。

### T06-09 module initializer failure

业务不启动，下次回退。

### T06-10 warmup

warmup 后 first business invocation 接近 steady-state，且无 baseline method。

## Code Review 检查点

- 是否通过 closure，而非隐藏 AOT dispatch stub；
- static/cctor 是否真正隔离；
- module initializer 失败策略是否明确；
- P01/P02/P03 是否分别测试；
- MethodBridge 是否来自目标平台 closure DLL；
- generic/value-type bridge 是否完整；
- 是否误允许 Burst/native 边界；
- PreJit 是否在 Commit 后；
- 是否有 baseline MethodInfo 执行断言；
- 性能数据是否区分 Transform 与业务逻辑。

## 完成标准

- T06-01 至 T06-10 通过；
- P01/P02/P03 的复杂调用链稳定；
- baseline static/cctor/method 均未执行；
- closure generator 输入覆盖桥接和泛型；
- warmup 流程建立；
- Gate 3A 获批；
- 独立 review 通过并创建 M06 tag。
