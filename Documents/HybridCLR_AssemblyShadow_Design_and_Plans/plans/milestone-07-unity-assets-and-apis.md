# Milestone 07：Unity API、Prefab/Scene、AssetBundle 与序列化完整验证

## 目标

在 M01 最小 PoC 基础上，系统覆盖 Unity 2022 中所有要求的脚本路径：

- Prefab；
- Scene；
- AssetBundle；
- Addressables 风格延迟加载；
- `MonoScript.GetClass`；
- `AddComponent(Type/T)`；
- `GetComponent(Type/T)`；
- `ScriptableObject.CreateInstance(Type/string)`；
- Unity message；
- serialized field；
- `[SerializeReference]`；
- 资源缓存与重复加载；
- DLL-only 与资源重构判定。

完成后达到 Gate 3B。

## 进入条件

- M05 Active Type world 一致；
- M06 执行语义通过；
- M02 Resource ABI 工具可运行；
- M01 旧 Bundle PoC 通过；
- Bootstrap Scene 不引用业务资源。

## 设计原则

1. Shadow 必须在业务资源加载前 Commit。
2. 旧 AssetBundle 是不可修改测试输入。
3. 方法体变化允许 DLL-only。
4. 序列化 ABI 变化默认要求 Bundle 重构。
5. 所有 Unity API 既测 Type 形式，也测泛型形式。
6. 泛型形式只能由 Shadow 闭包代码调用；固定 AOT Bootstrap 不能静态引用业务类型。
7. 资源重复加载、卸载、场景切换后仍应保持 active。
8. 不以“重新挂组件”替代反序列化验证。
9. `Resources` 与 Player 首场景中业务 Shadow 脚本默认禁止。

## 任务 07.1：扩展资源测试集

在 demo 建立并冻结 baseline：

```text
BaselineArtifacts/<target>/<buildId>/Bundles/
├─ versioned-prefab.bundle
├─ nested-prefab.bundle
├─ business-scene.bundle
├─ additive-scene.bundle
├─ scriptable-object.bundle
├─ serialize-reference.bundle
└─ mixed-assets.bundle
```

### `VersionedPrefab`

直接挂：

```text
VersionedPrefabComponent
```

字段：

```text
int
string
DemoValue
List<DemoValue>
UnityEngine.Object引用
嵌套serializable class
```

### `NestedPrefab`

父、子 GameObject 分别挂：

- Internal component；
- ExtensibilityConsumer derived component；
- 组件之间 serialized reference。

### Business Scene

包含：

- prefab instance；
- scene-only component；
- ScriptableObject reference；
- UnityEvent listener；
- serialized interface替代模式；
- `[SerializeReference]` graph。

### ScriptableObject

直接类型来自 Internal，字段类型来自 Contracts。

### SerializeReference

定义：

```text
Contracts接口/抽象契约
Internal具体实现A/B
```

保存 baseline concrete type name，验证 patch 后恢复到 active class。

## 任务 07.2：统一测试入口

在 Shadow Internal 中新增：

```csharp
public static class UnityPathProbe
{
    public static UnityPathProbeResult Run(GameObject root);
}
```

结果包含：

```text
component runtime assembly
base runtime assembly
interface runtime assembly
GetComponent<T>
GetComponent(Type)
AddComponent<T>
AddComponent(Type)
MonoScript.GetClass
ScriptableObject type
serialized values
Unity message counters
resource generation markers
```

Bootstrap 只通过反射调用 `Run`，返回 JSON 字符串或固定 `byte[]`，不引用业务结果类型。

## 任务 07.3：`AddComponent(Type)`

测试：

```csharp
Type t = Assembly.Load(name).GetType(fullName);
Component c = go.AddComponent(t);
```

验证：

- `t` active；
- created object class active；
- Awake/OnEnable 使用 patch method；
- serialized defaults来自 patch；
- `c.GetType() == t`；
- no baseline allocation；
- repeated add/remove 正确。

若 native path 仍收到 baseline class：

- 检查 Type reflection object；
- 检查 Unity icall；
- 在最早可控对象创建入口 ResolveClass；
- 不在已经分配后修正。

## 任务 07.4：`AddComponent<T>`

调用代码必须位于：

```text
AssemblyA.Implementation.Internal
```

或其他 closure assembly：

```csharp
VersionedPrefabComponent c =
    go.AddComponent<VersionedPrefabComponent>();
```

P01：

- caller Internal shadow；
- generic context 中 T active shadow。

P03：

- full closure shadow。

固定 Bootstrap 中故意加入编译期测试，应由 M02 validator 阻止。

## 任务 07.5：`GetComponent`

覆盖：

```csharp
GetComponent(Type)
GetComponent<T>
TryGetComponent<T>
GetComponents<T>
GetComponentInChildren<T>
GetComponentInParent<T>
GetComponentsInChildren
interface GetComponent
base class GetComponent
```

验证：

- active class assignability；
- P01 的 AOT Extensibility base 能找到 Shadow Internal derived；
- P03 的 Shadow Extensibility base 能找到 Shadow Internal；
- interface P01/P03 分别正确；
- 不出现 `null` 因两套 Type identity 不一致。

## 任务 07.6：`ScriptableObject.CreateInstance`

覆盖：

```csharp
CreateInstance(Type)
CreateInstance("Namespace.Type")
CreateInstance<T> // 仅closure内部
Instantiate(existingAsset)
```

验证：

- active Type；
- OnEnable patch；
- serialized fields；
- no baseline class init；
- string overload 经 active name resolver。

## 任务 07.7：Prefab 恢复

对只读 baseline Bundle：

1. Commit P01；
2. LoadAsset；
3. 检查 `MonoScript`；
4. Instantiate；
5. 检查所有 component；
6. 调方法；
7. Destroy；
8. Unload bundle；
9. 重新加载；
10. 再次检查。

验证：

```text
MonoScript.GetClass active
Object.New active
Awake/OnEnable patch
serialized values保留
GetComponent<T/Type> active
第二次加载不回退baseline
```

记录 native resolver counters，确保不是因第一次缓存偶然成功。

## 任务 07.8：Scene 恢复

覆盖：

```text
LoadSceneMode.Single
LoadSceneMode.Additive
重复加载/卸载
激活前allowSceneActivation=false
场景中Prefab instance
场景中直接组件
DontDestroyOnLoad对象
```

启动顺序：

```text
Commit
→ LoadSceneAsync
```

禁止在 Commit 前创建 pending scene operation。

验证 Unity message：

```text
Awake
OnEnable
Start
Update至少一次
OnDisable
OnDestroy
```

都来自 patch method。

## 任务 07.9：`MonoScript.GetClass`

Editor 和 Player 中取得方式不同。Player 可通过资源对象或测试辅助。

验证：

```text
MonoScript assembly name仍为原logical name
GetClass返回active shadow Type
class namespace/name一致
```

如果 `MonoScript` 不公开可直接取得，使用 Editor 生成测试资源和运行时组件类型结果旁证，但 M01 native trace 仍必须保存。

## 任务 07.10：UnityEvent 与序列化回调

Baseline prefab 保存 UnityEvent 到某 component method。

逻辑变化但签名不变：

- old Bundle listener 应调用 patch method；
- PersistentCall 的 target/method name 正确；
- no baseline MethodInfo。

覆盖：

```text
ISerializationCallbackReceiver.OnBeforeSerialize
OnAfterDeserialize
UnityEvent
AnimationEvent，若资源方便
SendMessage
Invoke(string)
```

字符串方法名解析必须落到 active class。

## 任务 07.11：`SerializeReference`

测试：

```csharp
[SerializeReference]
private INode node;
```

baseline data concrete type：

```text
AssemblyA.Implementation.Internal.NodeA
```

P01 方法体变：

- 恢复 NodeA active；
- serialized data 保留；
- virtual/interface method patch。

P03 Contracts 变化：

- all closure recompiled；
- concrete type active；
- contract interface active。

类型名变化 patch：

- Resource ABI diff 必须拒绝 DLL-only；
- 如果使用 `[MovedFrom]` 等迁移，必须单独建立兼容测试后才允许。

## 任务 07.12：Resource ABI 运行时二次检查

Patch Manifest 包含：

```text
baseline resource ABI hash
patch resource ABI hash
required bundle list
```

Bootstrap 在加载旧 Bundle 前：

```text
if current bundle catalog ABI != patch required ABI:
    refuse business startup
```

对于 DLL-only patch：

```text
resourceAbiHash必须相同
```

对于 DLL+Bundle patch：

- 原子切换 DLL 和 resource catalog；
- 不允许新 DLL + 旧 Bundle 混搭；
- M09 完成下载/回滚。

## 任务 07.13：字段变化矩阵

### 允许 DLL-only

- 仅方法体；
- private `[NonSerialized]` field；
- static field；
- compiler-generated非序列化字段；
- 内部纯 runtime 类型字段，且不影响 Unity serialized owner。

仍需实机验证 constructor/default。

### 默认要求 Bundle

- 新增/删除 `[SerializeField]`；
- public serialized field；
- field type；
- base serialized field；
- list element type；
- class/namespace/assembly name；
- SerializeReference concrete type。

### 需要专项验证

- `[FormerlySerializedAs]`；
- 可选新增字段默认值；
- Unity TypeTree 兼容；
- managed reference migration；
- custom serialization；
- `ISerializationCallbackReceiver` 自行迁移。

MVP 不因为 Unity 某些版本“可能兼容”而自动允许。

## 任务 07.14：Resources 与 Preloaded Assets 限制

Build validator 扫描：

- `Resources`；
- Player first scene；
- Preloaded Assets；
- Graphics/Quality 等 ProjectSettings 引用；
- always included shaders 不相关；
- Addressables initialization objects；
- Scriptable Build Pipeline catalog。

若引用 Shadow candidate script/object，默认失败：

```text
Shadow candidate asset may be deserialized before commit.
```

可以提供白名单，但必须附实机证明和明确加载时序。

## 任务 07.15：Addressables 风格验证

即使 demo 不安装完整 Addressables，也至少模拟：

```text
远程catalog
下载bundle
Commit前不初始化业务locator
Commit后加载asset
```

若引入 Addressables package，测试：

- catalog initialize；
- remote bundle；
- dependency bundle；
- scene；
- instantiate async；
- release/unload；
- patch + catalog atomic version。

## 任务 07.16：缓存与重复使用

测试：

- Bundle load → unload(false)；
- unload(true)；
- Asset cache；
- Scene cache；
- `Resources.UnloadUnusedAssets`；
- GC；
- 再次加载；
- application pause/resume；
- domain无 reload。

确保 cache 中不残留 baseline class/type。

## Demo 补丁矩阵

### P01 Internal method

旧全部资源，DLL-only。

### P02 Extensibility method

closure DLL-only，old resources。

### P03 Contracts change

full closure；若 Resource ABI 未变，old resources。

### P04 nonserialized field

DLL-only。

### P05 serialized field

Build rejected for DLL-only；构建新 Bundle后通过。

### P14 class rename

默认 ResourceRebuildRequired。

### P15 SerializeReference type rename

默认 ResourceRebuildRequired或专项 migration。

## 自动结果

每个 test case 写：

```text
patch ID
bundle SHA
resource ABI
runtime assembly modes
type identity
Unity message counters
serialized value checks
resolver counters
baseline use count
```

## Code Review 检查点

- 是否始终使用只读 baseline Bundle；
- 是否绕过反序列化重新挂组件；
- Type 与泛型 API是否都测；
- P01/P02/P03是否覆盖；
- SerializeReference是否真正保存旧类型名；
- UnityEvent是否调用 patch MethodInfo；
- Resource ABI规则是否保守；
- Resources/first scene限制是否自动检查；
- 重复加载是否保持 active；
- 是否存在未解释的 baseline resolver hit。

## 完成标准

- 所有 Unity path tests 通过；
- 旧 Prefab/Scene Bundle 在 P01/P02/P03 逻辑兼容变化下不重构可运行；
- P05 DLL-only 自动拒绝；
- Add/GetComponent、ScriptableObject、UnityEvent、SerializeReference 通过；
- Gate 3B 获批；
- 独立 review 通过并创建 M07 tag。
