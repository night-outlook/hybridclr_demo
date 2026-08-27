# Milestone 10：自动化测试体系与平台矩阵

## 目标

建立可以重复生成 AOT 基线、构建 Shadow 补丁、安装旧 AssetBundle、启动 IL2CPP Player、采集结构化结果并判定通过/失败的自动化测试体系。

本 Milestone 不再以“手工运行 Demo 看日志”为主要证据。完成后，每次修改 `hybridclr`、`il2cpp_plus`、`hybridclr_unity` 或 Demo 都必须由同一套流水线验证：

- 未启用 Shadow 时的上游兼容性；
- `Internal`、`Extensibility`、`Contracts` 三种反向依赖闭包；
- Assembly、Type、Reflection、执行语义和 Unity API；
- 旧 Prefab/Scene AssetBundle；
- 失败事务、回滚和崩溃恢复；
- Windows x64 与 Android ARM64 IL2CPP。

## 进入条件

- M09 Bootstrap 能安装、验证、提交和回滚补丁；
- P01、P02、P03 已有可手工验证的 patch package；
- Demo 的 baseline player、baseline AssetBundle 和 patch fixtures 已固定；
- Native diagnostics 能输出 transaction、resolver 和 baseline-use 数据；
- 构建机能够执行 Unity 2022.3 命令行构建；
- Android 环境已安装 SDK、NDK、JDK 和可用设备或模拟器。

## 不变量

1. 运行时正确性结论只接受 IL2CPP Player 结果。
2. Editor/Mono 测试只能验证构建工具、Manifest、依赖图和纯 C# 算法。
3. 每个测试使用全新进程；MVP 不复用已经 Commit 的进程。
4. 每个 patch fixture 与 exact baseline build ID、runtime ABI 和资源版本绑定。
5. 所有结果必须机器可读，不能仅依赖控制台文本。
6. 测试失败时必须保留 Player log、Shadow trace、Manifest、设备信息和崩溃文件。
7. 旧 AssetBundle 必须来自基线提交，测试过程中不得被补丁构建悄悄重建。
8. 测试应同时验证“返回值正确”和“解析到的 Assembly/Image/Class 确实是 active shadow”。
9. 无 Shadow 模式必须作为永久回归基线。
10. 测试生成物不得依赖开发机上未记录的本地状态。

---

## 任务 10.1：建立测试层次

测试分为五层。

### L0：纯工具单元测试

运行位置：

```text
Unity Editor Test Runner / dotnet test（若工具提取为独立库）
```

覆盖：

- asmdef 依赖图；
- 反向依赖闭包；
- SCC/循环依赖；
- load order；
- semantic hash；
- Resource ABI hash；
- Manifest canonical serialization；
- patch closure 校验；
- Internal/Extensibility 依赖约束；
- baseline/patch build ID；
- 签名输入和文件清单；
- package 布局；
- diff 分类。

L0 不证明 Runtime Shadow 正确。

### L1：Native 组件测试

运行位置：

```text
可独立编译的 C++ test target，或 Unity Player 内部测试入口
```

覆盖：

- `AssemblyShadowRegistry` 状态机；
- candidate 注册；
- staged/active map；
- transaction abort；
- commit snapshot；
- logical-name normalization；
- pointer mapping；
- duplicate/closure validation；
- 并发只读；
- 错误码与诊断结构；
- compile flag 关闭时的 passthrough。

若单独编译 `libil2cpp` 测试成本过高，先用 Player 内部 native test icall，但测试 API 必须仅在：

```text
HYBRIDCLR_ASSEMBLY_SHADOW_TESTING
```

开启。

### L2：Unity Editor 工具集成测试

覆盖：

- settings UI；
- candidate assembly 分类；
- baseline player build；
- patch compile；
- generator input；
- Resource ABI index；
- patch package；
- installer exact source pin；
- 构建失败信息；
- 命令行参数；
- CI report。

L2 不把 Editor 中的 AssemblyLoadContext/Mono 行为当作 Player 结果。

### L3：单平台 IL2CPP 场景测试

每个测试启动独立 Player，通过启动参数选择：

```text
baseline
patch-id
test-suite
result-path
fault-point
```

覆盖完整 Runtime 语义和 Unity API。

### L4：跨平台发布矩阵

最低必须：

```text
Windows x64 IL2CPP
Android ARM64 IL2CPP
```

扩展：

```text
macOS Apple Silicon IL2CPP
iOS ARM64
Linux x64 IL2CPP
```

WebGL、主机平台不在 MVP 默认范围；需要单独评估线程、文件系统和动态加载约束。

---

## 任务 10.2：重构 Demo 测试目录

在 `hybridclr_demo` 建议形成：

```text
Assets/AssemblyShadowDemo/
├─ Bootstrap/
├─ Contracts/
├─ Implementation.Extensibility/
├─ Implementation.Internal/
├─ Consumers/
│  ├─ ContractsConsumer/
│  └─ ExtensibilityConsumer/
├─ Components/
├─ ScriptableObjects/
├─ TestFixtures/
│  ├─ Baseline/
│  ├─ PatchP01Internal/
│  ├─ PatchP02Extensibility/
│  ├─ PatchP03Contracts/
│  ├─ PatchP04ResourceAbiBreak/
│  ├─ PatchP05MissingClosure/
│  ├─ PatchP06InvalidSignature/
│  └─ PatchP07RuntimeAbiMismatch/
├─ TestHarness/
│  ├─ Runtime/
│  ├─ Editor/
│  ├─ Protocol/
│  └─ Reports/
├─ Tests/
│  ├─ Editor/
│  ├─ Runtime/
│  └─ NativeBridge/
└─ TestAssets/
   ├─ BaselinePrefab/
   ├─ BaselineScene/
   ├─ ScriptableObject/
   └─ SerializeReference/
```

程序集命名固定为：

```text
AssemblyA.Contracts
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
AssemblyB.ContractsConsumer
AssemblyC.ExtensibilityConsumer
AssemblyShadowDemo.Bootstrap
AssemblyShadowDemo.TestHarness
```

必须由测试检查 asmdef 真实依赖与期望图一致。

---

## 任务 10.3：定义测试补丁集

### P00：无补丁基线

目的：

- 验证所有业务程序集 AOT；
- Shadow feature 关闭和开启但无 candidate 两种状态；
- baseline AssetBundle 正常；
- 性能基线；
- 上游 HybridCLR 标准样例仍可执行。

### P01：仅 Internal 方法体变化

变化例：

```csharp
public string GetVersionMarker() => "P01";
```

期望闭包：

```text
AssemblyA.Implementation.Internal
```

验证：

- Contracts/Extensibility 继续 AOT；
- Internal active assembly 为 Interpreter；
- 旧 Prefab/Scene 不重建；
- `GetComponent`、反射、delegate、构造均执行 P01。

### P02：Extensibility 变化

变化内容包含：

- 基类方法体；
- virtual override 路径；
- 一个受允许的非序列化实现细节；
- Extensibility consumer 的重编译。

期望闭包：

```text
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
AssemblyC.ExtensibilityConsumer
```

验证闭包外 Contracts consumer 仍 AOT。

### P03：Contracts 变化

变化示例：

- 增加不破坏资源 ABI 的接口/DTO 能力；
- 所有依赖者重新编译；
- business entry 使用新契约。

期望闭包：

```text
AssemblyA.Contracts
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
AssemblyB.ContractsConsumer
AssemblyC.ExtensibilityConsumer
```

验证闭包内无 baseline AOT 业务对象。

### P04：Resource ABI 破坏

变化示例：

```text
新增/删除/改名 [SerializeField]
改变序列化字段类型
改变 MonoBehaviour 基类链
改变 SerializeReference 允许类型
```

期望：

- DLL-only package 构建失败；
- 错误报告列出受影响类型、字段和 Bundle；
- 只有显式重构资源后才允许发布。

### P05：缺失 Closure

从 P03 package 删除一个 consumer DLL。

期望：

```text
ValidateTransaction失败
Commit未发生
当前进程使用baseline
结构化错误包含缺失程序集和依赖边
```

### P06：签名或文件 Hash 错误

期望在 Stage 前失败，不接触 runtime transaction。

### P07：Runtime ABI 不匹配

修改 Manifest 中：

```text
Unity version
HybridCLR commit
il2cpp_plus commit
runtime ABI hash
architecture
```

逐项验证拒绝。

### P08：Baseline 已使用

在 Commit 前故意执行：

```text
typeof(AssemblyA.Contracts.SomeType)
Activator.CreateInstance
GetComponent
静态字段访问
反射对象获取
```

分别验证 Usage Guard 能检测并阻止事务，并给出首个使用栈或记录位置。

### P09：Commit 后业务失败

让：

```text
module initializer
warmup
business entry
health check
```

分别失败。

期望：

- 不在同进程切回 baseline；
- 记录 patch 为 post-commit failed；
- 进程结束；
- 下次启动选择 last-known-good/baseline。

---

## 任务 10.4：定义结构化测试协议

结果文件：

```json
{
  "schemaVersion": 1,
  "testRunId": "...",
  "baselineBuildId": "...",
  "patchId": "...",
  "platform": "WindowsPlayer",
  "architecture": "x86_64",
  "unityVersion": "2022.3.62f2",
  "hybridclrCommit": "...",
  "il2cppPlusCommit": "...",
  "shadowState": "Committed",
  "cases": [
    {
      "id": "REFLECTION-001",
      "status": "Passed",
      "durationMs": 12.4,
      "evidence": {
        "logicalAssembly": "AssemblyA.Contracts",
        "activeKind": "Interpreter",
        "baselineAssemblyPtr": "...",
        "activeAssemblyPtr": "...",
        "typeImageName": "AssemblyA.Contracts.dll"
      },
      "messages": []
    }
  ],
  "nativeDiagnostics": {},
  "artifacts": []
}
```

每个 case 至少包含：

```text
case id
预期 active mode
返回值
实际 Assembly/Image/Class 身份摘要
transaction generation
耗时
失败原因
```

测试完成时：

- 写临时文件；
- flush；
- 原子 rename 为 `result.json`；
- 根据整体状态返回进程退出码。

建议退出码：

```text
0  全部通过
10 测试断言失败
11 Bootstrap/patch选择失败
12 Runtime transaction失败
13 Player crash或未生成结果
14 测试环境失败
```

---

## 任务 10.5：实现 IL2CPP Player Test Harness

建议入口：

```csharp
public sealed class ShadowPlayerTestRunner : MonoBehaviour
{
    private IEnumerator Start()
    {
        var options = ShadowTestCommandLine.Parse(Environment.GetCommandLineArgs());
        var result = yield return ShadowTestSuiteExecutor.Execute(options);
        ShadowTestResultWriter.WriteAtomically(result);
        Application.Quit(result.ExitCode);
    }
}
```

命令行示例：

```text
AssemblyShadowDemo.exe
  --shadow-test-suite=P01
  --shadow-patch-root=<path>
  --shadow-result=<path>/result.json
  --shadow-log=<path>/player.log
```

Android 使用：

```text
adb push patch-package ...
adb shell am force-stop <package>
adb shell am start ... --es shadow_test_suite P01
adb pull files/AssemblyShadowTests/result.json
adb logcat -d
```

Android 参数可以通过：

- intent extras；
- persistent data config；
- 测试专用 bootstrap config。

不得在生产 build 暴露任意文件路径加载能力；测试入口受 compile define 和 development build 限制。

---

## 任务 10.6：Assembly 与闭包测试

测试 ID 建议：

```text
ASM-001 GetLoadedAssembly返回active
ASM-002 Assembly.Load后不暴露两个逻辑程序集
ASM-003 AppDomain.GetAssemblies逻辑去重
ASM-004 Assembly.FullName符合逻辑身份
ASM-005 Assembly.GetReferencedAssemblies一致
ASM-006 AssemblyRef解析到closure active image
ASM-007 closure外引用保持AOT
ASM-008 缺失closure拒绝
ASM-009 重复candidate拒绝
ASM-010 commit后不可二次commit
ASM-011 abort后无staged泄漏
ASM-012 feature关闭时行为与upstream一致
```

断言不仅比较字符串，还应通过测试 diagnostics 获取：

```text
physical assembly pointer
logical id
active generation
execution kind
baseline/shadow relation
```

---

## 任务 10.7：Type、Class 与 Reflection 测试

覆盖：

```text
TYPE-001 Assembly.GetType
TYPE-002 Type.GetType(assembly-qualified-name)
TYPE-003 typeof在patch代码中
TYPE-004 object.GetType
TYPE-005 RuntimeTypeHandle
TYPE-006 Type equality
TYPE-007 IsAssignableFrom
TYPE-008 IsSubclassOf
TYPE-009 interface map
TYPE-010 Activator.CreateInstance
TYPE-011 ConstructorInfo.Invoke
TYPE-012 MethodInfo.Invoke
TYPE-013 FieldInfo get/set
TYPE-014 PropertyInfo get/set
TYPE-015 Attribute lookup
TYPE-016 nested/private/generic type
TYPE-017 array/byref/pointer constructed types
TYPE-018 reflection cache重复调用身份稳定
TYPE-019 baseline Type泄漏被Usage Guard捕获
TYPE-020 AppDomain/Assembly/Type组合查询不出现双世界
```

需要分别验证：

```text
AOT→AOT
Interpreter→Interpreter
Interpreter closure→AOT external
固定Bootstrap→反射入口→Interpreter business entry
```

不支持的跨边界应由 validator 拒绝，而不是等到运行时随机失败。

---

## 任务 10.8：执行语义测试

### 构造与静态状态

```text
EXEC-CTOR-001 newobj
EXEC-CTOR-002 base ctor
EXEC-CTOR-003 generic ctor
EXEC-STATIC-001 static field隔离
EXEC-STATIC-002 .cctor仅active版本执行一次
EXEC-STATIC-003 module initializer时序
EXEC-STATIC-004 baseline static未被触发
```

### 调用分发

```text
EXEC-CALL-001 direct call
EXEC-CALL-002 callvirt
EXEC-CALL-003 interface call
EXEC-CALL-004 base virtual
EXEC-CALL-005 abstract base
EXEC-CALL-006 constrained call
EXEC-CALL-007 extension method
```

### Delegate 与事件

```text
EXEC-DELEGATE-001 static delegate
EXEC-DELEGATE-002 instance delegate
EXEC-DELEGATE-003 virtual delegate
EXEC-DELEGATE-004 multicast
EXEC-DELEGATE-005 event add/remove
EXEC-DELEGATE-006 closure/lambda
EXEC-DELEGATE-007 async continuation
```

### 泛型和值类型

```text
EXEC-GEN-001 generic class
EXEC-GEN-002 generic method
EXEC-GEN-003 AOT generic container + active interface
EXEC-GEN-004 constraints
EXEC-GEN-005 nested generic
EXEC-STRUCT-001 small struct
EXEC-STRUCT-002 large struct
EXEC-STRUCT-003 enum
EXEC-STRUCT-004 nullable
EXEC-STRUCT-005 boxing/unboxing
```

### 异常与异步

```text
EXEC-EX-001 throw/catch同程序集
EXEC-EX-002 跨Contracts异常边界
EXEC-EX-003 finally
EXEC-EX-004 stack trace标识
EXEC-ASYNC-001 Task
EXEC-ASYNC-002 async state machine
EXEC-ITER-001 iterator state machine
```

对每一类都记录 active method/declaring image 证据。

---

## 任务 10.9：Unity API 和资源测试

### Component API

```text
UNITY-COMP-001 AddComponent<T>
UNITY-COMP-002 AddComponent(Type)
UNITY-COMP-003 GetComponent<T>
UNITY-COMP-004 GetComponent(Type)
UNITY-COMP-005 TryGetComponent
UNITY-COMP-006 GetComponents
UNITY-COMP-007 GetComponentInChildren
UNITY-COMP-008 GetComponentInParent
UNITY-COMP-009 interface/base query
UNITY-COMP-010 RequireComponent
UNITY-COMP-011 DisallowMultipleComponent
UNITY-COMP-012 SendMessage（若项目允许）
```

### ScriptableObject

```text
UNITY-SO-001 CreateInstance<T>
UNITY-SO-002 CreateInstance(Type)
UNITY-SO-003 AssetBundle载入旧SO
UNITY-SO-004 序列化字段保持
UNITY-SO-005 方法执行patch逻辑
```

### Prefab/Scene/AssetBundle

```text
UNITY-AB-001 旧Prefab instantiate
UNITY-AB-002 旧Scene additive load
UNITY-AB-003 旧Scene single load
UNITY-AB-004 nested prefab
UNITY-AB-005 prefab variant
UNITY-AB-006 inactive object/component
UNITY-AB-007 serialized UnityEngine.Object引用
UNITY-AB-008 SerializeReference
UNITY-AB-009 DontDestroyOnLoad时序
UNITY-AB-010 unload/reload bundle
```

强制验证 Bundle hash 与基线归档一致：

```text
sha256(actual bundle) == sha256(baseline archived bundle)
```

测试报告必须保存该 hash。

---

## 任务 10.10：失败与事务原子性测试

注入点：

```text
AfterCandidateRegistration
AfterFirstSkeleton
AfterAllSkeletons
DuringMetadataInit
BeforeValidate
DuringValidate
BeforePublish
AfterPublishBeforeModuleInitializer
DuringModuleInitializer
DuringWarmup
DuringBusinessEntry
```

预期：

- Commit 前失败：无 active mapping，baseline 可启动；
- Commit 原子点前崩溃：下次启动不认为 patch 成功；
- Commit 后失败：当前进程不回退，patch 标 bad；
- staged assembly 不出现在 AppDomain；
- module initializer 不在 Stage 期间执行；
- 不存在一部分程序集 active、一部分 baseline 的闭包状态。

增加事务快照断言：

```text
all-or-none active generation
```

---

## 任务 10.11：Windows x64 自动化

Editor 构建脚本建议：

```text
-shadowBuildBaseline
-shadowBuildPatch=P01
-shadowBuildPlayer=Windows
-shadowRunSuite=all
-shadowOutput=<dir>
```

执行器负责：

1. 清理测试输出；
2. 校验四仓库 commit；
3. 构建 baseline DLL/Player/Bundle；
4. 归档 baseline Bundle；
5. 构建 patch packages；
6. 逐 patch 启动新进程；
7. 设置超时；
8. 收集 result/log/crash dump；
9. 生成 JUnit XML；
10. 输出 HTML/Markdown summary。

Windows crash 收集：

```text
Player.log
Windows Error Reporting信息
minidump（若测试环境支持）
native shadow trace
```

---

## 任务 10.12：Android ARM64 自动化

构建要求：

```text
IL2CPP
ARM64 only
Development Build
Script Debugging按需要
Internet Access按Bootstrap测试需要
```

执行器：

1. 检查设备在线且 ABI 为 arm64-v8a；
2. 安装干净 APK；
3. 清空 app data；
4. 推送 patch；
5. 启动指定 suite；
6. 等待结构化完成标记；
7. 拉取 result、log、tombstone；
8. 每个 case 强制停止进程；
9. 必要时清空 data；
10. 输出 JUnit。

必须覆盖：

- 首次安装；
- 已安装有 last-known-good；
- 下载中断；
- patch 文件损坏；
- 进程在 commit 前后被 kill；
- 低存储空间模拟；
- 多次冷启动。

Android native crash 时保留：

```text
logcat
/data/tombstones（有权限时）
libil2cpp符号对应build id
mapping/symbol archive
patch manifest
```

---

## 任务 10.13：随机顺序和稳定性循环

单次通过不足以发现静态初始化和缓存污染问题。

最低循环：

```text
P00 × 20 cold starts
P01 × 100 cold starts
P02 × 50 cold starts
P03 × 50 cold starts
commit前故障注入每点 × 20
commit后故障注入每点 × 10
```

在测试时间允许时随机化：

```text
反射查询顺序
资源加载顺序
Component API顺序
泛型实例顺序
场景加载顺序
线程只读查询时序
```

随机种子写入结果，失败可复现。

---

## 任务 10.14：测试报告与证据归档

每次 CI 输出：

```text
artifacts/<run-id>/
├─ source-revisions.json
├─ environment.json
├─ baseline-manifest.json
├─ patch-manifests/
├─ bundles.sha256
├─ results/
├─ junit/
├─ logs/
├─ native-traces/
├─ crash/
├─ performance/
└─ summary.md
```

`source-revisions.json` 必须含：

```text
hybridclr commit
hybridclr_unity commit
il2cpp_plus commit
hybridclr_demo commit
Unity exact version
platform toolchain versions
```

不应将大型二进制永久提交 Git；由 CI artifact 存储并设置保留策略。

---

## 任务 10.15：测试选择与阻断规则

Pull Request 必跑：

```text
L0全部
L2关键构建测试
Windows P00/P01 smoke
feature-off upstream regression
```

合并到集成分支必跑：

```text
Windows完整矩阵
Android P00/P01/P03
事务故障注入核心点
```

夜间：

```text
所有patch
所有Unity API
稳定性循环
性能基线
Android完整矩阵
```

Release Candidate：

```text
M12完整发布矩阵
```

阻断条件：

- 任一 logical double-world；
- 任一 native crash；
- 旧 Bundle hash 不一致；
- closure 不完整却 Commit；
- baseline use guard 漏报；
- Commit 后同进程错误回退；
- feature-off 回归；
- 结构化结果缺失；
- 不能复现的非确定性失败累计超过阈值。

---

## 任务 10.16：独立 Code Review

Review 重点：

- 测试是否真的运行在 IL2CPP；
- 旧 AssetBundle 是否被偷换；
- 断言是否只比较业务字符串而没有检查 active identity；
- 测试入口是否可能进入生产 build；
- Android 自动化是否每次冷启动；
- timeout 是否会把 crash 误判为环境错误；
- failure artifacts 是否足够定位；
- feature-off 是否覆盖；
- fixture 是否由独立源码状态构建；
- P03 closure 是否完整。

输出：

```text
Docs/Reviews/M10-Automated-Test-Matrix-Review.md
```

---

## 完成条件 / Gate 4A

必须全部满足：

- L0/L1/L2/L3 测试框架可重复运行；
- Windows x64 P00～P09 全部通过；
- Android ARM64 P00、P01、P02、P03、P04、P05、P08、P09 通过；
- 旧 Prefab/Scene Bundle hash 与基线一致；
- 所有 Assembly/Type/Reflection/Unity API 测试包含 active identity 证据；
- Commit 事务故障注入满足 all-or-none；
- feature-off 上游行为无回归；
- 结构化 JSON + JUnit +日志可由 CI 收集；
- 稳定性循环无 native crash、双类型世界或静默错误；
- 独立 review 通过。

## 失败处理

若某路径只在特定平台失败：

1. 不将平台标记为“暂时支持”；
2. 缩小到最小 fixture；
3. 判断是 HybridCLR bridge、libil2cpp resolver、Unity native cache 还是工具链；
4. 为失败路径增加永久 regression test；
5. 修复前将该平台列为 unsupported；
6. 不用异常捕获或测试跳过掩盖 native 类型错误。
