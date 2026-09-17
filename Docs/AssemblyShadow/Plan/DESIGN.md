# HybridCLR Assembly Shadow — Canonical Design

The 2026-09-07 revised design is authoritative where it amends the original design. The original design follows as retained detail.

# Assembly Shadow 设计修订提案 v2

状态：**PROPOSED，尚未实现或完成 Player 验证**。基于 2026-09-07 固定四仓库源码审查。原始设计、M00–M07 的历史契约和证据保持不变；本提案说明继续开发时应如何收口，而不是给旧证据换一个更大的支持范围。

## 1. 目标与非目标

保留首包业务全部 AOT、按安装包基线计算变化根与反向依赖闭包、重启后闭包整体 Interpreter、闭包外 AOT 的方案。保留 `Contracts`、`Implementation.Extensibility`、`Implementation.Internal` 三层边界：跨模块默认依赖 Contracts；Extensibility 白名单；Internal 不被外部直接依赖。

最小固定 AOT Bootstrap 不引用业务具体类型，不关闭安全 guard 来换性能。一个进程最多一次成功 Shadow 发布，不迁移已存在的 baseline 对象，不卸载或复用被保留的 interpreter metadata。程序集级模式不是方法级 DHE。

DLL-only 改为明确的联合准入条件：资源兼容、native 类型准入、bridge/泛型支撑、索引容量、启动时序、逻辑依赖与部署完整性都必须成立。`Resource ABI 不变` 不单独授权所有补丁。

跨进程恢复和模块动态新增保留为独立能力，不把“已有程序集内添加类型”当作“新程序集支持”。当前 Replace-only 可以作为研发中间 Gate；若最终产品要求动态新增程序集，相应 X Gate 不能省略。

## 2. 继续复用的架构

四仓库职责不改变：`hybridclr` 管解释器 image 与 staging 字节生命周期；`il2cpp_plus` 管活动身份、物理边界和 native guard；`hybridclr_unity` 管目标编译、静态策略、生成能力与发布输入；`hybridclr_demo` 提供真实基线、旧资源和运行证据。

保留 `ActiveSnapshot` 的单一发布点、staging TLS resolver、发布后 module initializer、非闭包 AOT 路径，以及 Unity 稳定 image alias。不要通过全局改写固定 AOT metadata index、清空未知 Unity 缓存或修改实际对象 klass 来实现“统一”。[S13–S20]

新增的不是另一套 runtime，而是三个明确层次：

| 层次 | 内容 | 生命周期 |
|---|---|---|
| 不可变活动选择 | logical assembly、baseline/active pointers、Unity alias | 单次发布，进程终身 |
| 已证明能力 | metadata quota、native bridge、类型 allocation certificate | 安装包固定或按完整物理类型惰性建立 |
| 部署状态 | package set、code/resource 配对、health、恢复决策 | 跨进程持久化；不用于篡改 native 身份 |

## 3. 必须写入主设计的不变量

| 编号 | 不变量 |
|---|---|
| I01 | 一个 logical assembly 在一个 committed world 中只有一个活动选择；物理 baseline 可以保留。 |
| I02 | Stage 不执行补丁业务代码，不通过公开枚举/语义查找泄漏 staged 类型；全局缓存中的保留对象仍受可见性规则约束。 |
| I03 | 发布前所有闭包 DLL 身份和真实引用已验证；发布过程不是多个公开映射的可见中间态。 |
| I04 | 旧对象、旧物理布局和旧 AOT 方法不能通过 remap 被“改造成”新对象/新执行。 |
| I05 | Unity startup image identity、active metadata image 与物理所有权是三个不同概念。 |
| I06 | 类分配兼容证明可以缓存，但对真实 baseline 使用、失败状态和 execution context 的检查不能被缓存绕过。 |
| I07 | 闭包按安装包 baseline 与完整目标状态计算；增量下载不等于增量运行集合。 |
| I08 | 安全闭包图不用于冒充 target 的真实加载顺序。 |
| I09 | 跨版本逻辑成员身份不含 token/slot/运行地址；必要 ABI 兼容另行验证。 |
| I10 | 每个发布补丁满足安装包已有 native 能力及本进程 metadata index 预算。 |
| I11 | 错误处理以实际 native state、是否发布及恢复许可为准，不只以 API 名称或错误码推断。 |
| I12 | 所有支持声明绑定 exact source、Unity、平台/架构、编译模式和测试种类。 |

## 4. Metadata Image 容量成为一级设计输入

### 4.1 当前可证明的限制

当前 `MetadataUtil.h` 为 22 位基础索引、2 位 kind；四桶 image cursor 步长 64/16/4/1。`AllocImageIndex` 根据 `dllLength * 4` 选择桶并向大容量 metadata 桶回退。[S22–S24]

| 全部 DLL 的单文件大小；fresh allocator | 理论最大 image 数 |
|---|---:|
| 0 < size < 1 MiB | 338 |
| 1 MiB ≤ size < 4 MiB | 83 |
| 4 MiB ≤ size < 16 MiB | 19 |
| 16 MiB ≤ size < 64 MiB | 3 |
| size ≥ 64 MiB | 当前算法无合适 kind |

这是同尺寸、没有普通 interpreter/先前失败消耗的上界，不是项目当前剩余容量。候选 AOT 数量本身不占这些 interpreter 槽；实际 Stage/普通 load 才占用。`s_images[1024]` 不能解读为支持 1024 个任意大小 DLL。包内算法复算可重复执行，但不是原生验收。

### 4.2 第一阶段：可审计预算

基线输出 `MetadataEncodingProfile`，记录编码版本、桶参数、保留槽和普通 interpreter 需求。Patch Builder 按真实 DLL 大小和实际计划顺序模拟分配，产出 `MetadataCapacityReport`。原生 Begin/Stage 在最终生效前再次校验已有使用量，不信任纯 Editor 估算。

预算必须覆盖所有将进入进程的普通 Interpreter image、Shadow closure 和保守保留消耗。失败后不得靠重置全局 cursor“释放名额”；任何可恢复的预检查都应发生在分配 index 之前。

### 4.3 第二阶段：目标规模超限时必须扩容

单纯加上拒绝提示不算满足超限项目的目标。基于实际项目的 DLL 尺寸分布、最大累计闭包和普通热更开销确定容量需求，建议先用 100/300/1000 个小程序集作为压力档位，而不是宣称全部已支持。

扩容 ADR 至少比较：现有分桶的位宽/步长再分配；保持 32 位字段的页式/区间编码与 image 页别名；更大索引表示的完整 ABI 成本。优先探索**保持 AOT 零 image 语义和 IL2CPP 结构字段宽度的 32 位区间/页式方案**，而不是未经审查把索引全部改成 64 位。

页式方案仅为需验证的候选：将 image 的索引空间视为若干连续页，encoded value 可定位页及页内 offset，页表再映射实际 image 与其基址；大 image 占多页，小 image 减少分桶浪费。必须验证 private TLS lookup、未发布页的可见性、所有 Encode/Decode 使用点、负数/invalid sentinel、RawIndex 推导、泛型和字符串路径。不能只修改 `kMetadataIndexBits`：那会同时改变单 image 可表示范围、大小阈值和 ABI。

扩容后的 profile 是新的 RuntimeContract，需要重新构建安装包基线，并重新跑 M03–M07 受影响的完整 native/Player Gate。不能向旧 Player 发布要求新编码的补丁。

## 5. 三种身份与解析边界

**Logical identity**：简单程序集名、大小写敏感的 namespace/nested type 名及 generic arity。它描述跨版本实体，不包含 token、地址或虚表 slot。

**Physical identity**：`Il2CppAssembly/Image/Class/Type/MethodInfo` 的具体地址及归属，决定真实对象、静态存储和执行来源。它不能被资源展示名覆盖。

**Unity registration identity**：M05 已证明需要保留的 startup-registered image pointer alias。导出 `class_get_image/assembly_get_image` 可返回稳定身份；对该身份的 metadata 查询再解析到 active image。真实 `klass->image` 和物理诊断不被改写。[S07,S13]

任何新的 native Hook 都先标明它属于哪一类。禁止对所有 `GetImage` 或 metadata index getter 一刀切 active 化。AppDomain 普通逻辑枚举和物理诊断枚举使用不同 API/字段名，不让计数含义依赖猜测。

## 6. 类型与资源准入分层

### 6.1 当前保守模式必须完整前置

将 native 的既有字段/偏移、类型种类、父类/接口、value type 和 private primitive append 规则规范化为 `NativeLayoutAdmissionV1`。Editor 先判断可确定的结构变化；涉及目标原生偏移或尚未物化的构造类型时，标记为需要原生证明，不以 Resource ABI hash 相同代替证明。

新增、删除、重排或改变私有引用字段的部署在 V1 中必须给出明确的 `NativeLayoutIncompatible` 诊断，而不是在资源兼容报告中误写“安全 DLL-only”，然后 Commit 后首次 new 才报 ResourceAbiMismatch。

现有错误码不能重编号；新错误 domain/diagnostic schema 必须版本化。历史 M05/M07 的错误码 16 和严格诊断校验保留为旧契约测试，不直接改写旧 evidence。

### 6.2 逐步扩展，而不是全局放宽

| 准入域 | 所需证明 | 初始策略 |
|---|---|---|
| PureInterpreter | 全部执行/对象来自补丁；无旧对象；无固定 AOT/native 对旧具体类型布局的消费 | V1 先保守；独立 Gate 后扩大私有字段等结构变化 |
| Unity-bound | Unity 类型注册/资源恢复/生命周期/缓存对布局的真实要求 | 保留已验证 alias 与 V1；结合重建资源逐条扩展 |
| AOT/interop-exposed | 值复制、boxing、generic ABI、delegate/native wrapper、结构布局和 native capability | 最严格；不能只凭 managed Type 名称相同批准 |

一个类型可落入多个域，取要求并集。尤其是 value type 嵌入或 AOT 泛型参数，不因“这是纯 C# 文件”就被认为纯 Interpreter。

Resource ABI 继续单独描述序列化字段、继承语义、SerializeReference 具体类型和 callback 契约。资源重建不能自动授权旧 native layout 不支持的变化；native 可分配也不能自动授权旧 Bundle 数据兼容。

## 7. Admission cache 与热路径

新增 `ClassAdmissionCertificate`，至少包含 active generation、实际 active Class、baseline counterpart/无 counterpart 的判定、admission domain/profile、证明状态与失败理由。

Key 必须表示完整构造类型。只缓存泛型 definition 不能代表 `G<A>` 与 `G<B>` 的相同物理布局；arrays/byref/pointer 的组件边界也必须保留。正向证明只在 metadata 完整后发布，负向证明使事务/启动失败，不产生对象。

缓存建立不得持有 resolver cache mutex 再递归进入 metadata 初始化。惰性写入要遵守现有锁序；发布后的 map 不能一边无锁读一边直接修改 `std::unordered_map`。可用只增的分段原子表、不可变 shard snapshot 或其他已经测量并证明的策略。最初允许明确的单次慢路径，禁止每次分配重做完整证明。

把 TypeKey→physical definition index 建在受控 metadata 阶段，或首次查找后缓存，包括 patch-added type 的“不存在 baseline”结果。后续 allocation cache hit 不再扫描 image 的全部 TypeDef，不构造字段/接口字符串，也不分配 native 临时容器。

正确性 guard 与可观测性分离：生产保留 active/baseline/poison 检查；高频总量 counters 使用可关闭、线程局部或有界汇总机制；详细 type/class 观察为 Development 或显式诊断模式。任何优化前后均测 feature-OFF、ON/no patch 和 committed Shadow。

## 8. 闭包、加载与初始化使用不同图

`G_baseline`：实际安装包及其声明依赖。`G_target`：本次完整目标编译集合。`G_safety`：二者和必要声明边的保守并集，用于反向闭包。`G_load`：target 中真实 AssemblyRef/必须装载的依赖，用于 provider-before-consumer。初始化额外顺序用独立且有来源的 `G_init` 声明。

算法顺序：比较安装包 baseline/current 得到全部 changed roots；在 G_safety 上求闭包；验证每个闭包成员的执行角色；在 G_load 的闭包投影上排序；runtime 对 DLL 自身的 AssemblyRef 重新检查。

保留真正 target 环的拒绝，直到单独支持 SCC。不要为了修复跨版本伪环而跳过闭包校验。反射/资源影响边可以扩大闭包，但不默认等价于 module initializer 先后关系。

累计更新例子：基线 A0/B0，目标 v1=A1/B0，目标 v2=A1/B1。v2 的运行集合仍相对于 A0/B0 计算；只下载 B1 的网络差异可以，但启动前必须物化 A1+B1。原 `DetectChangedRoots` 已是 baseline/current 比较，后续只补强 regression，不重新写成 last-patch diff。[S30,S31]

## 9. 方法身份与执行隔离

`LogicalMethodKey` 与 `MethodCompatibility` 分离。前者表示 declaring TypeKey、方法名、generic arity、CLI 签名和 instance/static 调用形状；物理 token/slot、实现优化 flags 不作为 lookup key。后者再决定返回类型、调用约定、byref/custom modifiers、泛型约束变化是否满足当前调用者/句柄契约。

反射描述对象可以按逻辑 key 映射到 active MethodInfo；执行检查继续拒绝旧 AOT MethodInfo。`ResolveReflectionMethod` 不能被复用于“允许旧 AOT 地址继续执行”。stack trace 构建和 Unity 回调也是反射映射测试入口，不只测试业务显式 `GetMethod()`。

在未证明之前，baseline Field/Property/Event 句柄继续精确拒绝，不按 token 猜测新成员。真实需求出现后再增加完整逻辑键，不无界扩展所有元数据表 remap。

## 10. 安装包能力与产物身份

分开四种身份：

| 身份 | 覆盖 | 是否可以因 Editor-only 修复变化 |
|---|---|---|
| RuntimeContractId | exact Unity/平台/架构、native runtime、metadata 编码、managed runtime ABI | 不应仅因 Editor-only 内容改变 |
| NativeCapabilityInventoryId | 已编入 Player 的 bridge、struct mapping、reverse callback 容量、native features | 不能由 DLL-only 补丁增加 |
| ToolchainProvenanceId | 实际编译/分析/打包工具源码及配置 | 可以变化，但须与 runtime contract 有已验证兼容关系 |
| BuildEvidenceId | 四仓库输入、编译结果、原生库、资源和测试 hash | 每次构建真实记录，不允许伪造旧 SHA |

新 manifest 必须要求 native capacity report、admission report 和 capability coverage report。复用 `ShadowGenerationOutput.RequireCoverage` 的结构 ABI/容量比较，而不是重复实现另一份比较规则。[S38,S41]

补充 AOT metadata 与新增原生 bridge 是不同情况。前者在受支持模式中可能由额外元数据支持泛型解释；后者已受安装包 native 代码约束，不能通过下载新生成的 C++ 文件生效。

旧 schema 的严格来源校验不松绑。新 schema/兼容记录由测试证明，包含工具版本可升级但 native contract 不变的正例，以及 metadata/bridge ABI 改变的拒绝例。

## 11. 启动、失败与恢复

候选身份注册应尽可能早于可触及候选的 managed/native 操作。将 `ConfigureCandidates` 前的信任前提写成可审查的 startup contract；已存在的有限编译分析不宣传为完整全程序 effects proof。[S13,S34]

建议 startup coordinator 分为准备、验证/选择、激活、业务启动、健康确认五个明确阶段。没有补丁时应一次性冻结 baseline 选择；这与“以后仍可能 Commit”的状态不同。新增 FrozenBaseline 能力需 API/schema 版本化，也可先在协调器层禁止第二次激活并保留保守 runtime guard。

| 观察到的状态/失败 | Abort 是否可调用 | 推荐恢复 |
|---|---|---|
| Begin 前下载/签名/目标不匹配 | 无须调用 | 隔离 candidate，选择完整 baseline/LKG 集合 |
| Staging/Staged/Validated 的已知可纠正拒绝 | 现 API 可调用 | 成功 Abort 且私有可见性/启动前提仍成立时，才允许当前进程 baseline |
| 部分 skeleton/metadata 初始化失败，state=Failed | 现 API 不接受 | 默认 RestartRequired；不得忽略 Abort 错误继续业务 |
| 已发布，state=FailedAfterCommit | 不可回退 active world | 终止业务启动；下次进程使用完整 LKG/baseline |
| Guard 异常被业务 catch | 状态不自动恢复 | 受支持业务入口继续识别 poison；固定诊断可运行；协调器仍终止本次启动 |

RecoveryDisposition 由原生事实和协调器阶段联合决定，不能仅由 `error != Success` 推导。unknown native failure 默认需要重启。原生外部回调不跨 C ABI 抛 managed exception，保留或改进现有 fatal guard 模式。

补丁 DLL、相关资源/catalog 和完整目标集合是一个原子部署单元。候选槽更新与健康标记独立，只有业务 readiness 达到预先定义的判据才标记健康；“Commit 返回 Success”不是用户可用。回退到 LKG 时必须同时回退它的代码和资源，不能混用候选资源。

## 12. 正式构建工作流

M08 应复用现有 snapshot、semantic hasher、资源 receipt、reflection/codegen policy、source installer 和 generation output，提取 demo 编排为标准 API/CLI。不要再次生成一套并列真相。

推荐流程：一次目标编译 → 同源 closure/静态策略 → 资源差异 → native admission/capability/quota → 完整包物化 → 独立 reopening verification → 可选签名 → 以不可变名字发布。

Baseline native 变更后必须重建新 Player；旧 M07 Player 和证据归档保持不变。输出目录新建，失败不覆盖 last-known-good，不修改历史 receipt 使它“匹配”新工具。

业务应用只需少量稳定配置：程序集角色/白名单、显式动态依赖、启动资源边界和固定入口。有限 reflection acquisition 规则保留；原始枚举/反射压力测试辅助代码不要扩大成生产 Bootstrap 的复杂业务职责。若准备简化现有分析器，必须先证明等价覆盖，不能用“简化设计”作为删除负向测试的理由。

## 13. 新增与删除程序集的独立能力

| 操作 | 基础要求 | Gate |
|---|---|---|
| Replace | 既有 baseline；完整 closure；活动替换与 Unity alias | 现有 M03–M07 的继承线 |
| AddManaged | 无 baseline；新 logical registry entry；真实依赖和 image quota | X-Managed |
| AddUnityTypes | 新 image 的 Unity 可见注册；新 Bundle 脚本/序列化类型恢复 | X-Unity |
| Remove | 无保留 AOT 调用/资源引用；逻辑 tombstone；LKG 能恢复 | X-Remove |

AddManaged 通过不授权 AddUnityTypes。Unity 冷启动前下载 manifest、placeholder、原生 launcher 都只是待实验的路径选择，必须证明 Player 实际读取和使用的是该信息；不以文件存在推断引擎注册表已更新。

保持资源脚本原逻辑程序集名是目标之一，不把重命名所有类型/程序集、强制所有资源固定到一个稳定程序集当成默认解决方案。

## 14. 性能与验证 Gate

初始对照必须包含：原未改运行时、同 fork native OFF、ON/no patch、常规 Interpreter、Shadow P01/P03；保持目标、Development/Release、stripping、PDB 和资源输入可比。

分别测启动到交互、Stage/Validate/Publish、初始化器、warmup、首次 new/资源恢复、重复 new/virtual/interface/delegate，以及 native/managed 内存。进程冷启动与操作系统文件缓存冷状态分开描述。少量样本不得宣称稳定 P99。

继承原 M11 的方向性预算：无补丁/feature OFF 相对控制组接近零回归，原初始目标 <1%；已证明 cache hit O(1)、无额外 native 临时分配、不获取可竞争全局锁。具体设备阈值在 baseline 上校准并固定，不能每次失败后临时放宽。[S12]

M07R 先执行容量、分配和主要 guard 的收益判断。M10 扩展 Windows x64/Android ARM64，保留 macOS；M11 做全量 soak/fuzz/rebase；M12 做从干净输入到安装包/补丁/回滚的独立验收。当前已记录的 14 模式不是这些新 Gate 的替代品。

## 15. 迁移与交付方式

仅开发计划落地时修改仓库，本提案本身不应用任何代码。先固定新 review baseline 和问题到测试映射，再以小闭合变更提交：容量 → 缓存/guard 分层 → 类型/方法/图语义 → 构建发布 → 恢复 → 平台/扩容 → 生产验收。

每个变更保持 native feature OFF 回归。接口/编码变更时同步四仓库和 generator/DTO/verifier，不能只在 demo 里绕过。历史 M00–M07 证据仅作不可变对照，新的测试输出绑定新可执行版本。

参考来源：见 `evidence-map.md`，特别是 S01–S24、S29–S41。详细工作项和失败处理见 `plans/`。


---

# Original Design Detail

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
