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
