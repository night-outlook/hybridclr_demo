# Milestone 11：性能优化、运行时加固、故障注入与上游 Rebase

## 目标

在功能和自动测试完成后，将 Assembly Shadow 从“正确的研究实现”加固为可长期维护的生产运行时。主要输出：

- Shadow 关闭时近似零额外成本；
- Commit 后解析读路径稳定、低锁竞争；
- Stage/Validate/Commit 的启动成本可量化、可优化；
- Interpreter 首次转换通过 Profile/Warmup 控制；
- 内存、线程、错误路径和恶意输入得到约束；
- native crash 有完整诊断；
- 四仓库可以跟随 HybridCLR 与 Unity 2022 上游更新；
- 对性能、正确性和升级风险建立长期门禁。

## 进入条件

- M10 Gate 4A 通过；
- Windows 与 Android 自动测试稳定；
- 所有关键 Resolver Hook 已有覆盖；
- feature-off 回归已建立；
- Runtime diagnostics 可以标识 active generation、assembly、image、class 和 method；
- 生产补丁 package、Bootstrap 和回滚流程可用。

## 不变量

1. 优化不能削弱 logical active world 的一致性。
2. 不能通过缓存 baseline 句柄换取速度。
3. Commit 后的 active mapping 对读者不可变。
4. Stage 数据不得进入全局 fast path。
5. 所有新缓存都有 generation、生命周期和失效规则。
6. Shadow 功能关闭时不得引入字符串查找、全局锁或额外分配。
7. 性能指标必须来自 IL2CPP Player 和目标设备。
8. 上游 rebase 后必须重新执行全部 runtime Gate。
9. 任何无法解释的 native crash 都阻断发布。
10. 安全限制和输入上限不能为性能测试临时关闭。

---

## 任务 11.1：建立性能测量模型

将耗时拆成：

```text
PatchRead
SignatureVerify
ManifestParse
CandidateRegister
AssemblyStage
ImageParse
SkeletonCreate
MetadataInitialize
ClosureValidate
ActiveMapBuild
CommitPublish
ModuleInitializer
PreTransform/Warmup
FirstResourceLoad
FirstPrefabInstantiate
FirstSceneLoad
BusinessReady
```

Runtime 解析读路径拆成：

```text
AssemblyByName
AssemblyRef
ImageActiveResolve
ClassActiveResolve
TypeActiveResolve
ReflectionResolve
AppDomainEnumerate
ObjectCreationCheck
UsageGuardCheck
```

每个计时项记录：

```text
count
total ns
min
max
P50/P95/P99（测试汇总层计算）
thread id
transaction generation
assembly/type key（抽样或development only）
```

生产 build 默认只保留低成本 counters；详细 trace 由远程诊断开关或 development build 启用。

---

## 任务 11.2：定义初始性能预算

以下作为首轮目标，最终按项目设备档位校准。

### Feature 关闭或无 Shadow Patch

相对未改 upstream build：

```text
CPU帧耗时回归：< 1%
启动耗时回归：< 1%
managed allocation：0 B/frame新增
native常驻内存：仅固定小型registry
Assembly/Type正常查询：无额外字符串分配
```

### Shadow Commit 后稳态

```text
active resolver命中路径：O(1)
读路径：不获取可竞争的全局互斥锁
每帧额外managed allocation：0 B
每帧额外native allocation：0
普通业务调用不经过assembly-name字符串查找
```

### 启动阶段

预算不设置绝对毫秒作为跨项目通用标准，而设置：

```text
Stage/Validate与DLL大小、类型数近似线性
Commit publish本身不随方法数线性增长
Warmup只包含Profile热点集
补丁Ready前无不可解释长尾
```

Demo 设备记录绝对基线，并在 CI 中限制相对回归，例如：

```text
P01 Shadow startup P95不得比已接受基线增加 > 10%
P03 Shadow startup P95不得增加 > 15%
Prefab首次实例化P95不得增加 > 10%
```

阈值修改必须有 review 和数据说明。

---

## 任务 11.3：优化 feature-off 快速路径

所有 Hook 首先检查一个只读全局状态：

```cpp
if (IL2CPP_UNLIKELY(AssemblyShadow::IsActive()))
{
    return AssemblyShadow::Resolve(...);
}
return upstreamPath(...);
```

要求：

- `IsActive()` 为无锁原子读；
- compile flag 完全关闭时编译器可消除分支；
- 不在 feature-off 路径构造 key；
- 不分配字符串；
- 不记录详细 diagnostics；
- 不改变 upstream 数据结构顺序；
- 不替换函数结果再映射一次。

建立 microbenchmark 比较：

```text
Assembly::Load
GetAssemblyByName
Class::FromName
Type.GetType
Reflection GetTypeObject
GetComponent
Activator.CreateInstance
```

feature-off 和无补丁 active=false 都要测。

---

## 任务 11.4：构建不可变 Active Snapshot

Commit 前构建完整快照：

```cpp
struct AssemblyShadowSnapshot
{
    uint64_t generation;
    LogicalAssemblyMap logicalAssemblies;
    AssemblyPointerMap assemblyMap;
    ImagePointerMap imageMap;
    ClassPointerMap classMap;
    TypePointerMap typeMap;
    MethodPointerMap methodMap; // 仅确有需要的入口
};
```

Commit：

```text
validate snapshot
→ release fence
→ atomic publish snapshot pointer
→ state = Committed
```

Commit 后：

- snapshot 不再修改；
- Resolver 仅执行只读查询；
- 旧 snapshot 在 MVP 中随进程结束释放；
- 不需要读写锁；
- 不支持同进程第二代 snapshot；
- diagnostic enumeration 使用同一 snapshot。

选择 map 结构时基于 benchmark：

```text
unordered_map
sorted flat vector + binary search
dense id table
pointer-key robin-hood hash
```

优先为频繁路径建立 pointer-key map，避免每次按 assembly/type 名称查找。

---

## 任务 11.5：Key 和字符串优化

### LogicalAssemblyId

在 candidate 注册时完成：

```text
normalize simple name
validate culture/public key/version policy
intern name
assign dense LogicalAssemblyId
```

运行期内部使用：

```cpp
uint32_t LogicalAssemblyId
```

而不是重复比较 `Il2CppAssemblyName` 字符串。

### TypeKey

构建期/Stage 期解析：

```text
LogicalAssemblyId
namespace
nested type path
generic arity
```

对已知 baseline `Il2CppClass*` 建立直接映射；只有首次名称入口才构建 TypeKey。

### AssemblyRef

在 Metadata Initialize 时将每个 AssemblyRef 绑定到：

```text
active/staged logical assembly id
```

Commit 后不再按名称扫描程序集列表。

---

## 任务 11.6：减少 Resolver 覆盖范围

通过 M10 trace 统计每个 Hook：

```text
调用次数
shadow命中次数
baseline passthrough次数
是否存在功能必要性
```

移除“为了保险”但从未形成正确性作用的 Hook。原则：

- 只在语义边界映射一次；
- 不在上游每一层重复 active resolve；
- 底层函数已保证 active 时，上层不要重复；
- debug assertion 可验证输入已经 active；
- 任何移除均需完整回归。

目标是形成清晰分层：

```text
Name/AssemblyRef Resolution
    ↓
Active Image
    ↓
Active Class/Type
    ↓
Reflection/Unity API消费
```

而不是任意函数都调用全局 Resolver。

---

## 任务 11.7：Stage 和元数据初始化优化

测量每个程序集：

```text
DLL read
PE/metadata parse
type skeleton
method metadata
generic metadata
vtable/interface
static field layout
class map
resource type index
```

优化顺序：

1. 避免同一 DLL 重复 hash/解析；
2. manifest 提供 size/hash，但仍由 runtime 验证 identity；
3. Stage 使用预分配 arena；
4. closure 全量已知时预估容器容量；
5. 避免 Stage 期间触发 Reflection object；
6. 避免逐方法 C# ↔ native InternalCall；
7. 批量传入 candidate metadata；
8. 将纯构建期数据移到 manifest；
9. 不提前创建永远不会使用的 Type object；
10. 保持失败时 arena 可整体释放。

并行化原则：

- 文件读取、签名、hash 可并行；
- HybridCLR/IL2CPP Metadata 初始化默认主线程串行；
- 未证明线程安全前不并行 `Class::Init`、泛型实例和 Transform；
- Commit 只能在主线程/受控安全点；
- 所有并行优化都需要 ThreadSanitizer 等价验证或强约束证明。

---

## 任务 11.8：Profile-guided PreTransform/Warmup

Assembly 级 Shadow 后，闭包全部 Interpreter，首次方法转换仍可能卡顿。

建立开发环境采样：

```text
method token
declaring logical assembly
generic context
first-transform duration
first-call frame/phase
call path category
```

生成：

```text
shadow-warmup-profile.json
```

示例：

```json
{
  "assembly": "AssemblyA.Implementation.Internal",
  "mvid": "...",
  "methods": [
    {
      "token": "0x06000123",
      "genericInstantiation": null,
      "phase": "BeforeBusinessResources",
      "priority": 100
    }
  ]
}
```

实现批量 native API：

```text
PreTransformMethodsByToken
PreTransformClosedGenericMethods
RunExplicitWarmupEntrypoints
```

分阶段：

```text
BeforeModuleInitializer（通常仅runtime内部）
AfterCommitBeforeResources
BeforeFirstScene
BeforeBattle
Deferred
```

规则：

- profile 绑定 DLL MVID/hash；
- token 不匹配立即丢弃；
- 不全量 PreJit 大程序集；
- `.cctor` 与方法转换分开；
- warmup 必须无业务副作用；
- 记录 warmup 内存增量；
- 每帧 budget 只适用于业务启动允许分帧时；
- 首个必须加载的 Prefab 类型应在资源读取前准备。

---

## 任务 11.9：内存审计

统计：

```text
baseline AOT assembly/image/class metadata
shadow interpreter assembly/image/class metadata
active maps
staging arena
InterpMethodInfo
translated instructions
reflection objects
static field storage
patch bytes
PDB
resource indexes
diagnostics ring buffer
```

由于 baseline 无法卸载，Shadow 模式必然双份持有部分元数据。输出按程序集报告：

```text
baseline retained bytes
shadow metadata bytes
active mapping bytes
warmup bytes
total incremental bytes
```

优化：

- Stage 完成后释放 DLL 临时 buffer（若运行时不再需要）；
- PDB 按配置保留；
- manifest 字符串 intern；
- diagnostics 使用固定容量 ring buffer；
- release build 关闭高粒度 call trace；
- Resource ABI index 使用紧凑 ID；
- closure 过大时提前依据内存预算拒绝 patch。

建立低内存测试：

```text
接近预算上限
Stage中OOM
Validate中OOM
Warmup中OOM
资源加载中OOM
```

Commit 前 OOM 必须安全 abort；Commit 后按 post-commit failure 处理。

---

## 任务 11.10：线程与安全点加固

明确允许的线程模型：

```text
Register/Begin/Stage/Validate/Commit：
    Unity主线程

Commit后Resolver：
    任意已附加IL2CPP线程只读

Diagnostics snapshot：
    任意线程，只读或受控复制

Abort：
    仅事务owner线程，Commit前
```

增加断言：

```text
main thread id
transaction owner
state transition
no active readers during publish（由atomic snapshot保证）
no Stage API after Commit
```

检查：

- GC safe point；
- domain/thread attach；
- Unity Job/worker 线程上的 Type query；
- async continuation；
- native plugin callback；
- shutdown 时序。

Commit 采用 release/acquire 内存序；不允许发布未完全构造对象。

---

## 任务 11.11：Baseline Usage Guard 完善

MVP 的正确性依赖“Commit 前未使用受影响 baseline 类型”。

需要覆盖并分级记录：

```text
Assembly lookup
Image lookup
Class::FromName
Class::Init
static field allocation
cctor
object allocation
reflection Assembly/Type/Method/Field object
generic inflation
vtable/interface setup
delegate creation
MonoScript class resolution
Prefab/Scene deserialize
ScriptableObject create/load
```

事件结构：

```text
timestamp
thread
logical assembly
type/method token
usage category
native callsite id
managed stack（可用时）
first occurrence
count
```

策略：

- candidate 注册后开启 guard；
- 对 closure 之外不记录；
- Commit 前任一 forbidden usage → Validate 失败；
- 查询但未物化是否允许由类别表明确；
- development build 可捕获详细栈；
- release build 至少有首个 category/token；
- guard 本身不得在 feature-off 路径产生显著开销。

新增“早用”模糊测试：随机在 Bootstrap 各阶段调用 API，确保无漏网入口。

---

## 任务 11.12：故障注入框架

Native：

```cpp
ASSEMBLY_SHADOW_FAULT_POINT("Stage.AfterImageParse");
```

Managed：

```csharp
ShadowFaultInjector.ThrowIfEnabled("Bootstrap.AfterCommit");
```

支持动作：

```text
return error
throw managed exception
simulate OOM
sleep/timeout
abort process
corrupt one mapping
skip one closure member（validation应发现）
fail file read
```

生产 build 默认编译掉危险注入，只保留安全的诊断模拟（如远程禁用）。

注入矩阵至少覆盖：

- Manifest parse/signature/hash；
- 每个 Stage 子阶段；
- snapshot build；
- commit 前后；
- module initializer；
- warmup；
- old Bundle load；
- health marker 写入；
- A/B slot 切换；
- patch download/rename；
-磁盘满；
-进程 kill。

任何故障都验证磁盘状态和下次启动选择。

---

## 任务 11.13：恶意/异常输入加固

对输入设置硬上限：

```text
Manifest字节数
程序集数量
单DLL大小
闭包总字节数
类型/方法数量（可由metadata合理限制）
依赖边数量
字符串长度
资源索引数量
PDB大小
压缩包展开大小与比例
```

防御：

- 路径穿越；
- symlink/reparse point；
- 重复文件名；
- Unicode normalization 混淆；
- assembly simple name 大小写/文化差异；
- duplicate logical identity；
- zip bomb；
- 整数溢出；
- token 越界；
- malformed metadata；
- 非预期 native plugin/extern；
- 错误架构 DLL；
- 过期/撤销签名。

使用 corpus fuzz：

```text
manifest parser
dependency graph parser
package extractor
candidate identity reader
shadow transaction API序列
```

Native metadata fuzz 应在隔离进程和 sanitizer build 中执行，不能在生产 Player 里直接喂任意未签名 DLL。

---

## 任务 11.14：Native 诊断与崩溃定位

输出一份轻量 snapshot：

```json
{
  "state": "Committed",
  "generation": 1,
  "baselineBuildId": "...",
  "patchId": "...",
  "closure": [...],
  "activeAssemblies": [...],
  "lastTransition": "...",
  "lastResolverEvents": [...],
  "firstBaselineUsage": null,
  "warmup": {...}
}
```

实现固定容量 native ring buffer，记录：

```text
state transition
assembly stage
active publish
resolver mismatch
baseline use
class mapping miss
reflection mapping miss
Unity resource class resolution
fatal invariant
```

崩溃时尽可能将 ring buffer：

- 写入 Player log；
- 暴露给 managed crash handler；
- 保存到 persistent data；
- 与 native symbol build ID 关联。

每个 release 保存：

```text
libil2cpp symbols
GameAssembly symbols
mapping
source revision
compiler flags
runtime ABI hash
```

不要在 release 日志输出完整下载 token、私钥信息或敏感路径。

---

## 任务 11.15：静态分析和编译器检查

Native：

```text
warnings-as-errors（项目允许的集合）
clang-tidy关键规则
AddressSanitizer测试构建（可支持平台）
UndefinedBehaviorSanitizer
iterator/debug checks
```

Managed/Editor：

```text
nullable
Roslyn analyzer
asmdef dependency analyzer
Bootstrap isolation analyzer
Internal dependency prohibition
Extensibility whitelist
Resource ABI analyzer
no reflection-by-string to Internal（可检测范围）
```

特别检查：

- raw pointer 生命周期；
- snapshot publish；
- unchecked casts；
- string ownership；
- token/int overflow；
- error ignored；
- catch-all 后继续 Commit；
- unordered iteration 导致 manifest 非确定；
- static initialization order。

---

## 任务 11.16：上游改动隔离

`il2cpp_plus` 尽量新增：

```text
vm/AssemblyShadow.h
vm/AssemblyShadow.cpp
vm/AssemblyShadowDiagnostics.*
```

上游文件只保留小型 Hook：

```cpp
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
...
#endif
```

`hybridclr` 尽量新增 staged assembly 和 bridge 文件。

`hybridclr_unity` 将功能放入独立目录：

```text
Editor/AssemblyShadow
Runtime/AssemblyShadow
```

避免修改上游通用命令的核心行为；采用 extension point 或少量明确分支。

建立 `UPSTREAM_CHANGES.md`：

```text
文件
上游基线
修改原因
Hook语义
对应测试
rebase注意事项
```

---

## 任务 11.17：固定和 Rebase 策略

每个可发布组合生成 compatibility lock：

```json
{
  "unity": "2022.3.62f2",
  "hybridclr": "<commit>",
  "hybridclrUnity": "<commit>",
  "il2cppPlus": "<commit>",
  "demo": "<commit>",
  "runtimeAbi": "<hash>"
}
```

Rebase 流程：

1. 创建 `rebase/<upstream-version>` 分支；
2. 阅读 upstream release notes；
3. 比较 `Assembly.cpp`、`MetadataCache.cpp`、`Class.cpp`、`Reflection.cpp` 等关键文件；
4. rebase `il2cpp_plus` 小型 Hook；
5. rebase `hybridclr` staged assembly；
6. 更新 installer pin；
7. 干净安装到 demo；
8. 运行 feature-off；
9. 运行 Gate 1；
10. 运行完整 M10；
11. 运行性能对比；
12. 更新 ABI hash 和 compatibility lock；
13. 独立 review；
14. 合并并打兼容 tag。

禁止只更新 `hybridclr_unity` package 而继续使用旧的 native fork。

---

## 任务 11.18：自动检测上游冲突面

CI 保存关键上游函数的语义监控：

```text
Assembly::Load
Assembly::GetLoadedAssembly
MetadataCache::GetAssemblyByName
RegisterInterpreterAssembly
GetReferencedAssembly
Image::ClassFromName
Class::Init
Reflection::GetAssemblyObject
Reflection::GetTypeObject
AppDomain GetAssemblies
HybridCLR Assembly::Create/LoadFromBytes
```

不要仅 hash 整个文件；使用：

- patch context；
- AST/函数范围 hash（可实现时）；
- 编译测试；
- runtime semantic tests。

上游函数变化时，CI 输出需要人工 review 的清单。

---

## 任务 11.19：性能基准场景

Demo 创建：

```text
Bench-P00-NoShadow
Bench-P01-SmallClosure
Bench-P02-MediumClosure
Bench-P03-FullClosure
Bench-Reflection
Bench-Component
Bench-Prefab
Bench-Scene
Bench-Generic
Bench-Warmup
```

每个场景：

1. 冷启动若干次；
2. 丢弃预热轮；
3. 固定设备温度/电源条件；
4. 记录 raw samples；
5. 汇总 P50/P95/P99；
6. 与 accepted baseline 比较；
7. 输出内存和包体增量。

移动设备避免在严重 thermal throttling 下混合结果；记录设备型号、OS、电量和温度信号（能取得时）。

---

## 任务 11.20：热点路径优化验收

至少检查：

```text
每帧GetComponent/Type查询
大量Prefab实例化
场景批量加载
反射扫描
泛型首次调用
delegate高频调用
多线程只读Type查询
```

目标不是让 Interpreter 等同 AOT，而是：

- Shadow Resolver 不成为额外主要瓶颈；
- 首次转换可在加载阶段控制；
- 后续执行成本符合 HybridCLR Interpreter 预期；
- 无 Shadow 时基本保持原生路径；
- closure 大小对启动和内存影响可预测。

若某热点频繁跨 AOT/Interpreter bridge，优先重构成粗粒度契约调用，而不是在 native 层加入不透明特例。

---

## 任务 11.21：安全与运维演练

演练：

```text
签名密钥轮换
公钥版本升级
patch撤销
CDN返回旧版本
CDN返回部分文件
本地文件被篡改
设备时钟错误
磁盘只读/满
连续启动崩溃
kill switch离线缓存
last-known-good损坏
baseline版本升级后残留旧patch
```

输出操作手册和预期状态变化。

---

## 任务 11.22：独立 Code Review

必须由熟悉 IL2CPP/HybridCLR native runtime 的 reviewer 检查：

- snapshot 原子发布；
- pointer/key 生命周期；
- feature-off 快速路径；
- Stage arena；
- Class/Type/Reflection 映射缓存；
-静态状态；
-异常路径；
-线程模型；
-输入上限；
-故障注入；
-rebase隔离；
-性能数据是否可靠。

输出：

```text
Docs/Reviews/M11-Performance-Hardening-Rebase-Review.md
```

---

## 完成条件 / Gate 4B

必须满足：

- feature-off CPU/启动回归达到批准预算；
- active resolver 稳态无每帧分配和竞争锁；
- Commit 使用不可变 snapshot 原子发布；
- Stage/Validate/Commit 各阶段有可量化指标；
- PGO Warmup 能消除 Demo 关键路径首次调用尖峰；
- Shadow 增量内存按程序集可解释；
- Commit 前/后 OOM 与故障注入行为符合状态机；
- baseline usage guard 覆盖早用模糊测试；
- 恶意输入限制和 parser fuzz 无高危问题；
- Windows/Android 无未解释 native crash；
- 上游 rebase 演练完成一次；
- compatibility lock 可重建相同环境；
- M10 全量矩阵重跑通过；
- 独立 review 通过。

## 失败处理

若达不到性能预算，按以下顺序处理：

1. 确认测量是否可重复；
2. 区分 Interpreter 固有成本与 Shadow Resolver 成本；
3. 去除重复 Hook；
4. 将读路径改为 immutable pointer map；
5. 缩小 closure；
6. 精确 Warmup；
7. 调整模块边界；
8. 最后才考虑复杂的 native 特化。

不得通过跳过正确性校验、允许混合类型世界或关闭 Resource ABI 检查换取性能。
