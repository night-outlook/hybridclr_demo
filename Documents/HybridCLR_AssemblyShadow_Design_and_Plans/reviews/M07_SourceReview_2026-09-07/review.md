# Assembly Shadow M07 源码审查与设计再评估

日期：2026-09-07。对象：四仓库 `codex/assembly-shadow-m07`。这是**源码静态审查、仓库证据复核和改进提案**，不是已执行的修复，也不是本次重新跑过的 Unity/IL2CPP 验收。

## 1. 结论

保留 Assembly-level Shadow 路线，不推倒已验证的事务、活动解析、Unity 稳定 image 身份适配和测试框架。但不建议机械进入原 M08：先插入容量、热路径、布局准入、方法身份和图语义的 M07R 收口。

最需要优先解决的并非“有没有 Stage/Commit”，而是：细粒度程序集能否装得下；已提交世界能否以可接受成本持续运行；编辑器允许的补丁是否真能在 native 层使用；跨版本逻辑身份有没有掺入物理布局；失败状态与生产恢复协议是否一致。

**没有将未复现的 native crash 或假设的攻击升级为 P0。** 下文逐项给出静态事实、适用条件、改进动作和所需复现。

## 2. 审查基线与限制

| 仓库 | 固定 review HEAD |
|---|---|
| `hybridclr_demo` | `41b047b153d2d816306fe9e0253a58b96fe72c05` |
| `hybridclr` | `a19db144751f4f016769b90e61a80b8c27578678` |
| `hybridclr_unity` | `2180b99daf39095cd76301da2bdf34ac945ee8b4` |
| `il2cpp_plus` | `666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8` |

M07 文档记录的 demo 可执行源为 `3aab779a3304dd9785ab14fb5fcdc73a107066f7`，随后 pin-only 提交为 `671737c082effa5094bed16b087f6da5c3c666c9`；当前 HEAD 还包含证据和收尾文档。不能把 review HEAD、Player 实际编译输入和证据提交混为一个 SHA。

参考聊天链接无法取得全文。因此历史理解以当前项目可见上下文、仓库原 `design.md` 和 M03/M05/M06/M07 后续契约为依据。关键 native 文件全文阅读，外围工具/测试/集成文件定向阅读；准确覆盖见 `evidence-map.md` 和 `source-baseline.json`。本环境没有四仓库完整工作树、Unity 或目标 Player；没有运行仓库的 912/356/824 套件，没有重新解包校验 8,816 个归档成员。

本次实际执行的只有 `analysis/reproduce_source_algorithms.py`：复算 image 分配容量、普通 image 占用，以及两个版本合并图的伪环。结果明确标注 `nativeRuntimeExecuted=false`、`unityPlayerExecuted=false`。

## 3. 应保留的已有成果

| 已有机制 | 本次核对结果 | 后续原则 |
|---|---|---|
| 私有 staging resolver、完整 closure skeleton、发布后初始化器 | 已在核心实现中读到；不是仍待从零设计的空白 | 保留并建立影响面回归 |
| 原子 ActiveSnapshot | 构建完整 map、batch append、release-store；有锁序和 usage recheck | 不换成多个可变表的逐步发布 |
| Stage 失败的保留式生命周期 | 私有 metadata process-lifetime 保留、索引不重用、可见性过滤 | 不能把 retained memory 当作可随意 free 的普通临时对象 |
| 逻辑/物理/Unity image 身份区分 | M05 契约和 native alias 实现明确 | 不以“全部返回 Interpreter image 指针”为名破坏 Unity startup 注册身份 |
| 累积变更与 baseline 依赖保护 | roots 比较安装包 baseline/current；graph 合并 baseline edges | 修正加载图复用，不重写成只比较上一补丁 |
| Resource ABI 与旧 Bundle 验证 | M07 有 P01–P04 旧资源、P05 重建资源、结构变化拒绝和 14 模式记录 | 不再把旧 Prefab/Scene 路径称为完全未验证 |
| bridge generation/coverage | M06 已实现结构 ABI 和 capacity 比较 | 补齐部署入口集成，不重复造生成器 |

[S02](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-report.md)；[S03](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-resource-contract.md)；[S04](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/Evidence/verification/m07-strict-gate-3b-v6.json)；[S06](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M03/M03-report.md)；[S07](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M05/M05-type-contract.md)；[S09](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md)；[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)；[S18](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowVisibility.cpp)；[S20](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/StagedAssembly.cpp)；[S30](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs)；[S38](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Generation/ShadowGenerationOutput.cs)

## 4. Findings 总表

优先级表示后续处理顺序；“生产缺口”不追溯性否定 M07 的明确里程碑范围。“已确认”表示代码条件已经读到，不代表相关 Player 反例已经执行。

| ID | 优先级 | 分类 | 问题 |
|---|---|---|---|
| ASR-001 | P1 | 已确认：容量/目标适配 | Interpreter Image 索引容量与细粒度程序集目标存在硬约束 |
| ASR-002 | P1 | 已确认：性能实现 | 每次对象分配重复做定义查找和布局证明 |
| ASR-003 | P1 | 已确认：性能边界 | 执行保护和诊断尚未分层，无补丁不等于零成本 |
| ASR-004 | P1 | 已确认：设计能力/准入差异 | 当前 Native Layout 契约比 Resource ABI 更窄，并可能在 Commit 后才拒绝 |
| ASR-005 | P1 | 已确认：条件性功能拒绝 | 反射方法的逻辑身份键混入物理 slot 和实现 flags |
| ASR-006 | P2 | 已确认：图算法功能拒绝 | 安全闭包图与目标加载图混用，产生跨版本伪环 |
| ASR-007 | P2 | 已确认：发布架构耦合 | 整个 Editor package 的 commit 被用作 Runtime ABI |
| ASR-008 | P1 | 已确认：计划/运行时契约需要收口 | 原 M09 的统一 Pre-commit→Abort→baseline 流程不覆盖 Failed 状态 |
| ASR-009 | P1 | 生产缺口：原计划 M08 范围 | 生成能力证据尚需成为每个可部署 Patch 的强制门禁 |
| ASR-010 | P2 | 已确认：未实现能力 | 同名 Replace 与程序集 Add/Remove 不是同一能力 |
| ASR-011 | P1 | 待实证风险：启动边界 | ConfigureCandidates 之前不是原生使用监测覆盖区 |
| ASR-012 | P2 | 验证边界：非代码缺陷 | 接受记录不能扩展为全部平台、全路径及本次重跑 |
| ASR-013 | P1 | 待验证加固项：不是已确认漏洞 | PE/CLI envelope 检查不是完整 metadata/IL 安全验证 |

## 5. 逐项分析

### ASR-001 · Interpreter Image 索引容量与细粒度程序集目标存在硬约束

**P1｜已确认：容量/目标适配**

**定位：** MetadataUtil.h 的索引常量；InterpreterImage::GetImageKindByDllLength / AllocImageIndex；普通 Assembly::Create 和 Shadow CreateStagedSkeleton。

**代码事实：** 当前并非可自由使用 1024 个 image 槽。编码分为四种 kind，步长为 64/16/4/1；大桶保留起始槽，小桶保留末尾哨兵。新进程、同尺寸 DLL、没有任何既有消耗时，小于 1 MiB 的理论总容量为 255+64+16+3=338。1–4 MiB 档为 83，4–16 MiB 为 19，16–64 MiB 为 3；恰好 64 MiB 已无法取得合适 kind。普通热更和 Shadow 都调用同一分配器。

**影响及边界：** 113 个三层模块若全部进入闭包，会需要 339 个 image，即使 DLL 都很小也越过理论上限；这不是候选 AOT 程序集总数上限，而是本进程实际分配的 Interpreter Image 预算。部分失败已经消耗的索引不应假定会返还。M07 的五个候选不能覆盖该规模。

**建议：** 立即加入按真实 DLL 字节数和加载顺序计算的 baseline/patch 容量准入及原生剩余预算查询。若目标最大闭包超过预算，必须在正式基线发布前实施独立索引编码扩容里程碑；不能以减少程序集粒度代替原目标，也不能把修改一个常量当作完整修复。

**验收：** 使用原分配器的原生定向测试验证桶边界、混合尺寸、普通热更先占用和失败消耗；再以真实 Player 做代表性大闭包。交付包已执行源码算法等价复算，未执行这些原生/Player 测试。

**证据等级：** 容量为源码推导并经 Python 算法复算；并非设备实测。

来源：[S22](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/InterpreterImage.cpp)；[S23](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/MetadataUtil.h)；[S24](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/Assembly.cpp)；[S20](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/StagedAssembly.cpp)。执行计划：R01, R01B, M08B, X01。

### ASR-002 · 每次对象分配重复做定义查找和布局证明

**P1｜已确认：性能实现**

**定位：** Object::NewAllocSpecific → ResolveAllocationClass → AssemblyShadowTypeResolver::ResolveAllocation → CheckActiveComponents → FindDefinition / CheckLayout。

**代码事实：** 即使传入的已经是 active Class，ResolveAllocation 仍调用 CheckActiveComponents。它按类型名再次搜索 baseline image 的类型表，并重新构造字段布局向量、字段签名和接口集合。现有 definitions cache 只缓存 baseline→active 定义映射，不缓存 allocation admission proof。

**影响及边界：** 重复 new、数组/泛型参数包含 Shadow 类型的分配以及 boxing 路径可能持续支付扫描、字符串/容器分配和布局遍历成本。这是稳态路径，不是一次性 first-call；与原 M11 的 O(1)、零额外 native allocation 目标冲突。尚未测量百分比退化，不能虚构倍数。

**建议：** 新增独立的不可变 ClassAdmissionCertificate，以 generation + 完整物理 Class 身份区分定义和构造泛型。首次证明后缓存；baseline 使用检查不能被缓存绕过。建立元数据 TypeKey 索引，禁止缓存命中路径再遍历整个 assembly 或构造签名。

**验收：** 记录同一类型 1/10/10000 次分配的 layoutProofBuildCount、typeRowsScanned 和 native allocation。首次之外应不再构建证明；多线程、泛型、数组、Unity 旧资源及被拒类型仍正确。

**证据等级：** 调用链和重复工作已静态确认；耗时和分配字节数待原生仪表/Player 测量。

来源：[S14](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowTypeResolver.cpp)；[S16](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/Object.cpp)。执行计划：R02。

### ASR-003 · 执行保护和诊断尚未分层，无补丁不等于零成本

**P1｜已确认：性能边界**

**定位：** AssemblyShadow::AssertMethodIsActive / ObserveExecutionClass / CapturedArgumentVisitor。

**代码事实：** AssertMethodIsActive 首先执行共享原子 methodChecks 递增；候选 class 观察使用自旋锁，候选使用记录和部分泛型上下文检查也使用 usage lock。即使没有 active snapshot，代码也不等于一个 IsActive 分支立即返回。这里指受保护的 Invoke、虚/接口、解释器、delegate 等入口；普通直接非虚 AOT 调用仍没有统一 dispatch stub。

**影响及边界：** native feature OFF、feature ON 但无补丁、ON 且提交补丁是三个不同性能状态。保留全部生产诊断可能把优化收益转移为热路径共享缓存行竞争。1024 个执行 class 观察上限另有 dropped counter，不能把有限观察当成全类型覆盖。

**建议：** 区分不可关闭的正确性 guard 与可采样/开发专用诊断；冻结 baseline 选择后允许经过证明的快路径。闭合泛型执行上下文可缓存授权结果，但必须保留 generation 和失败状态约束。不要直接删除运行时 guard。

**验收：** 同配置 AOT/feature-OFF/ON-no-patch/P01/P03 对照，覆盖多线程泛型、virtual/interface/delegate，分别验证 counters-off/on。

**证据等级：** 代码开销来源已确认；项目级性能收益尚未复测。

来源：[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)；[S09](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md)；[S12](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-11-performance-hardening-rebase.md)。执行计划：R02, M11。

### ASR-004 · 当前 Native Layout 契约比 Resource ABI 更窄，并可能在 Commit 后才拒绝

**P1｜已确认：设计能力/准入差异**

**定位：** CompatibleInstanceFields / CheckLayout / CheckActiveComponents；ShadowPatchManifestBuilder.BuildCore。

**代码事实：** native 检查应用到存在同名 baseline 的 active 类型，不只应用到 Unity 序列化类型：已有实例字段的签名/偏移、父类和接口集合受约束；只保守允许 reference type 尾部的 private primitive 新存储，value type 不能增长。纯 active-first 分配同样要检查。Editor 的 Resource ABI 和当前编译策略不是该原生布局规则的等价前置校验。

**影响及边界：** 给普通纯托管业务类新增 private object/string/自定义类引用，或新增接口，可能不改变 Unity Resource ABI，却在首次分配时失败。新名字的类型可以没有 baseline，而同名旧类型受到强约束，说明这是一项真实的演进能力边界。P04 的 private primitive 成功不能推广为任意非序列化字段变化均可。

**建议：** 短期建立 NativeLayoutAdmissionReport，构建期明确拒绝当前不支持的变化，对无法静态确定的物理偏移在发布前进行有界验证。长期分离 PureInterpreter、Unity-bound、AOT/interop-exposed 三类准入；只有证明无旧对象/无 baseline 物理表示逃逸后，才扩展纯托管布局变化。不要全局去掉 CheckLayout。

**验收：** 新增 pure class private reference、字段删除/重排、private struct、interface/base change、closed generic、Unity private reference、P04/P05 的正负矩阵；断言不支持的部署不能直到业务首次使用才暴露。

**证据等级：** 原生限制和 build entry 缺少等价准入已静态确认；具体 Unity 工程补丁流程需实际 DLL/Player 验证。

来源：[S14](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowTypeResolver.cpp)；[S31](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs)；[S33](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs)；[S34](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Validation/ShadowExecutionPolicy.cs)；[S35](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Serialization/UnitySerializedTypeAnalyzer.cs)；[S03](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-resource-contract.md)。执行计划：R03, M08B。

### ASR-005 · 反射方法的逻辑身份键混入物理 slot 和实现 flags

**P1｜已确认：条件性功能拒绝**

**定位：** AssemblyShadowTypeResolver.cpp::MethodSignature / FindMethodDefinition / ResolveReflectionMethod。

**代码事实：** MethodSignature 将 method->slot、完整 flags、iflags 拼入匹配串，并对 baseline 与 active 的字符串作严格相等比较。slot 是版本内的虚表布局值，而不是跨版本方法身份。M06 实施记录已经说明真实 stack-trace/reflection 路径可能带来 baseline MethodInfo，所以该映射不是仅供测试的死代码。

**影响及边界：** 当补丁在既有 virtual 方法之前新增 virtual 方法导致 slot 改变时，旧方法的名称/参数/返回类型可保持不变，但 baseline MethodInfo→active 的映射仍会失败。该问题取决于确实经过 baseline 方法映射入口；并非声称所有普通反射调用都会失败。

**建议：** 把 LogicalMethodKey 与 MethodCompatibility 分开。逻辑键包含 declaring TypeKey、名称、泛型 arity、调用约定/instance-static 形状及完整参数/返回类型；slot、token、实现优化 flags 不参与逻辑键，必要兼容性另行判断。执行 guard 仍拒绝旧 AOT 方法，绝不把执行地址悄悄重定向。

**验收：** 真实 baseline/patch DLL 中新增前置 virtual、改变实现优化 attribute、token 重排、重载/泛型/显式接口；通过定向 native baseline MethodInfo 测试和异常 stack trace 测试验证映射，不以字符串拼接单测代替。

**证据等级：** 导致拒绝的匹配条件已静态确认；尚未在 Player 构造此反例。

来源：[S14](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowTypeResolver.cpp)；[S17](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/Reflection.cpp)；[S09](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md)。执行计划：R03。

### ASR-006 · 安全闭包图与目标加载图混用，产生跨版本伪环

**P2｜已确认：图算法功能拒绝**

**定位：** AssemblyReferenceGraph 构造函数合并 requiredBaselineEdges；ReverseClosure 末尾调用 LoadOrder；BuildCore 再用同一 graph.LoadOrder。

**代码事实：** baseline A→B、target B→A 各自无环，但并集包含 A↔B。并集用于保守反向闭包是合理的；用它决定当前 target 的 provider-before-consumer 加载顺序则会拒绝这个本可加载的补丁。

**影响及边界：** 正常的依赖重构可能被 DependencyCycle 阻断。此发现不是建议忽略真正的 target AssemblyRef 环，也不否认保留 baseline 依赖能防止闭包漏算。

**建议：** 保留 G_safety=baseline∪target∪声明依赖用于闭包；另建 G_load=target 的真实装载依赖。运行时仍校验 staged DLL 的真实 AssemblyRef；真实 target 环可先保持明确不支持。模块初始化顺序与反射/资源影响边也应区分。

**验收：** 加入两个快照方向反转的编译字节测试；两端单独排序通过、旧并图排序失败、新安全闭包完整且 target load order 通过。包内已执行独立图算法反例复算。

**证据等级：** 确定性的算法反例；未运行仓库原 C# 测试或 Unity 编译。

来源：[S30](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs)；[S31](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs)；[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)。执行计划：R03。

### ASR-007 · 整个 Editor package 的 commit 被用作 Runtime ABI

**P2｜已确认：发布架构耦合**

**定位：** ShadowSourcePins.RuntimeAbiHash / RequireCompatible。

**代码事实：** RuntimeAbiHash 直接纳入 hybridclrUnity.revision，因此同包仅 Editor 工具或测试的修复也会改变被部署补丁要求匹配的 Runtime ABI。当前严格版本绑定适合作为研发证据，但不能自动等价为长期二进制兼容规则。

**影响及边界：** 已发布 Player 可能无法使用修复后的 patch builder，除非继续冻结旧工具或重建 Player。不能通过把新工具伪装成旧 SHA 来绕过这一限制。

**建议：** 区分 RuntimeContractId、Generator/MetadataEncoding ABI、ToolchainProvenanceId 与完整 BuildEvidenceId。旧 schema 保持原校验；新旧兼容必须由显式、已测试的兼容记录授权，而非简单移除 SHA 检查。

**验收：** Editor-only 改动在相同 runtime contract 下可生成兼容补丁；native metadata 编码、bridge ABI 或 Runtime API 改动仍必须拒绝旧 Player。

**证据等级：** 哈希输入和拒绝路径已确认；属于生产工具链演进改进，不否定 M07 版本证据。

来源：[S32](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowSourcePins.cs)；[S31](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs)。执行计划：M08A。

### ASR-008 · 原 M09 的统一 Pre-commit→Abort→baseline 流程不覆盖 Failed 状态

**P1｜已确认：计划/运行时契约需要收口**

**定位：** StageAssembly、ValidateTransaction、AbortTransaction、AssertMethodIsActive、RequireUserCodeAllowed。

**代码事实：** 部分 skeleton/metadata 失败会设置 Failed；AbortTransaction 只接受 Staging/Staged/Validated，不接受 Failed。原 M09 却把多类 pre-commit 失败统一接到 Abort 再继续 baseline。此外 FailedAfterCommit 是状态封存，不是全进程停止机制：一个后续本身合法的方法检查并不会仅因该状态自动拒绝。

**影响及边界：** 机械执行原 M09 会错误处理 Abort 返回值，或将未经证明可恢复的状态当成安全 baseline fallback。不能把“错误路径被拒绝/事务无法重试”表述成“业务进程已自动停止”。M07 的测试 runner 遇错退出不等于通用生产协调器已实现。

**建议：** 新增明确的 RecoveryDisposition，联合 error/state/activeGeneration/失败阶段决定 Skip、AbortThenBaseline 或 RestartRequired；未知 native failure 默认重启。Bootstrap 负责停止业务启动，受支持业务入口增加 poison 约束，同时允许必要的固定 AOT 诊断；原生回调继续采用不跨 ABI 抛异常的 fatal 策略。

**验收：** 对可纠正输入拒绝、部分 skeleton 失败、Validate 失败、模块初始化异常、捕获异常后再次调用、Abort 不合法状态分别故障注入；不能把所有非 Success 归为同一个回退分支。

**证据等级：** 状态/返回路径已确认；生产恢复协调器属于后续 M09 工作。

来源：[S11](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-09-bootstrap-security-rollback.md)；[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)；[S20](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/StagedAssembly.cpp)；[S29](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs)。执行计划：R01, M09。

### ASR-009 · 生成能力证据尚需成为每个可部署 Patch 的强制门禁

**P1｜生产缺口：原计划 M08 范围**

**定位：** ShadowGenerationOutput.RequireCoverage 已实现；ShadowPatchManifestBuilder.BuildCore 的可部署输出入口。

**代码事实：** M06 已有 structural ABI/capacity coverage 比较，不能再说 bridge 生成完全缺失。但当前 BuildCore 没有调用该 coverage 检查，也没有把安装包内原生能力库存作为正式 patch publication 的必需输入。

**影响及边界：** 为未来补丁生成了新的 C++ bridge 文件，并不能把新原生能力放入已经安装的 Player。相同 target、资源 ABI 和程序集闭包不代表新 struct/callback/calli 或 bridge capacity 一定可执行。

**建议：** 将 baseline 已编入的 native capability inventory 冻结进发布契约；每个 patch 生成需求，再调用现有 coverage 机制校验。区分可由补充元数据支持的泛型需求与必须预编译的 native bridge 需求；缺失后者必须拒绝或要求新安装包。

**验收：** 构造资源 ABI 不变但新增 native struct signature/reverse callback 容量需求的 patch，确保包发布前拒绝；已有 P01/P02/P03 继续通过。

**证据等级：** 生成器已有实现及公开 builder 调用链已确认；这是 planned integration gap，不计作 M07 未履行的安全承诺。

来源：[S38](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Generation/ShadowGenerationOutput.cs)；[S39](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/MethodBridge/GenerationInventory.cs)；[S31](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs)；[S41](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowManifests.cs)；[S09](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md)；[S10](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-08-editor-build-integration.md)。执行计划：M08B。

### ASR-010 · 同名 Replace 与程序集 Add/Remove 不是同一能力

**P2｜已确认：未实现能力**

**定位：** DetectChangedRoots 的 AssemblyRemoved / BaselineMissing；ConfigureCandidates 的 BaselineAssemblyNotFound。

**代码事实：** 当前实现明确拒绝新增/删除 runtime assembly；候选注册必须找到物理 AOT baseline。新增类型到已有程序集与新增程序集也不能混同。Unity public image alias 依赖已有 startup-registered image。

**影响及边界：** 现有 Replace 成功不能推出动态新增模块程序集可用。该限制对细粒度模块随版本增长尤其重要，但应作为独立能力评估，不追溯性地把整个 M07 Gate 判为失败。

**建议：** 定义 Replace/AddManaged/AddUnityTypes/Remove 四种操作、能力位和独立 Gate。AddUnityTypes 必须以真实新名称、真实新 Bundle、干净进程证明注册/恢复；不预设下载 ScriptingAssemblies.json 或 placeholder 自动解决。

**验收：** 新增纯托管、新 MB/SO/SerializeReference 程序集、移除仍被代码/资源引用的程序集、逻辑墓碑和回滚；目标含动态新增时 X Gate 是最终验收必需项。

**证据等级：** 明确的代码拒绝路径；扩展方案尚未实现。

来源：[S30](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs)；[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)；[S07](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M05/M05-type-contract.md)。执行计划：X01。

### ASR-011 · ConfigureCandidates 之前不是原生使用监测覆盖区

**P1｜待实证风险：启动边界**

**定位：** RecordBaselineUse 在 s_candidates 为空时返回；ConfigureCandidates 建立新 registry；ShadowExecutionPolicy 的有限启动分析。

**代码事实：** 当前 runtime 无法仅凭 firstUse 为空证明“引擎启动以来从未用过 baseline”。现有构建限制和固定 Bootstrap 时序承担了这部分安全前提。代码没有事后恢复全部早期反射对象/原生句柄历史。

**影响及边界：** 第三方 SDK、native 插件、启动回调或配置变化越过该前提时可能产生不可见早期使用。尚未证明当前 M07 的实际启动路径触发了这个问题，不能将风险写成已发生的混合世界。

**建议：** 正式记录 pre-Configure 信任边界；优先生成嵌入的候选身份表并尽早注册观测，或用可审计启动闭包证明覆盖。新增原生/托管早用负向实验，禁止通过清空计数掩盖。

**验收：** 在 Configure 前创建 Type/MethodInfo、触发 .cctor、构造对象、解析 Unity script；验证可阻止提交或构建必拒，而不以 Configure 后 counter=0 作为唯一证据。

**证据等级：** 监测起点已确认；实际项目绕过风险未运行复现。

来源：[S13](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp)；[S34](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Validation/ShadowExecutionPolicy.cs)；[S03](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-resource-contract.md)。执行计划：R01, M09, M10。

### ASR-012 · 接受记录不能扩展为全部平台、全路径及本次重跑

**P2｜验证边界：非代码缺陷**

**定位：** M07 report/contract/strict Gate receipt；历史 M03–M06 不同 source pairing 的记录。

**代码事实：** M07 明确限定 Unity 2022.3.62f2 StandaloneOSX arm64、14 个模式、unsigned local evidence。MonoScript.GetClass 允许明确标注的 fallback，不能表述为所有 Player 可直接调用该 API。历史 M06 的 Development/Release 记录不等于当前 M07 全部组合重跑。

**影响及边界：** 测试数量和字节绑定提高可信度，却不能替代当前改动影响面上的 integration regression、Windows/Android 实机或大闭包性能证据。

**建议：** 维护 claim→source→artifact→platform→mode 的能力矩阵，按变更影响重跑；保留所有旧证据但不改写其版本。最终将真实项目切片、累积补丁和容量边界纳入 Gate。

**验收：** 从干净四仓库输入重新构建 required matrix，校验源、生成产物、native library 与结果一致。

**证据等级：** 范围和记录已读取；本审查未重放原始归档或 Player。

来源：[S02](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-report.md)；[S03](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-resource-contract.md)；[S04](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/Evidence/verification/m07-strict-gate-3b-v6.json)；[S05](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-source-inventory.json)；[S09](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md)。执行计划：R00, M08A, M10, M12。

### ASR-013 · PE/CLI envelope 检查不是完整 metadata/IL 安全验证

**P1｜待验证加固项：不是已确认漏洞**

**定位：** BorrowedCheckedImage / ParseIdentity；RawImageBase 的字符串、blob 和 row getter；InitializeStagedRuntimeMetadata。

**代码事实：** 新增 parser 认真检查了 envelope、stream/table 大小及 assembly/module/reference identity，但后续仍使用含 assert-only 索引访问的既有 metadata reader。不能由 envelope fuzz 数量推导出所有 coded index、signature、方法体及深度均安全。Stage API 文档只保证返回后可复用输入，不保证调用期间并发修改数组安全。

**影响及边界：** 签名不能修复合法签名但损坏/错误构建的输入；异常捕获也不等于可以捕获 native 越界或进程终止。本次没有构造完整 PE 触发崩溃，也不声称可远程利用。

**建议：** 在签名前离线校验，并为 native parser 增加长度/行/堆索引、递归、总字节和时间预算；使用 sanitizer fuzz 覆盖 Stage/Validate。可把 copy→validate→parse 合并为私有不可变字节流程以减少重复解析，保留调用期间不得并发修改的契约。

**验收：** 从合法 DLL 定向变异 TypeDef/Field/Method/Blob/coded index/EH/PDB，要求确定性拒绝、无越界、无未授权发布，区分原生 harness 与真实 Player。

**证据等级：** 防护边界静态分析；未报告新的已证实崩溃/漏洞。

来源：[S20](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/StagedAssembly.cpp)；[S26](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/RawImageBase.h)；[S22](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/InterpreterImage.cpp)；[S21](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/AssemblyShadowRuntimeApi.cpp)；[S29](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs)。执行计划：M11, M09。

## 6. 对原 design/plan 的整体修正

原设计把“一个逻辑程序集统一到 active 世界”作为正确的主轴；后续实现已经加入严格 native layout、Unity public image alias、有限 reflection acquisition、source/byte proof 等重要前提。主设计仍应合并这些后续决策，而不是让接入者阅读大量历史报告后自行推断。

建议建立四层契约：逻辑身份/闭包；native 物理与边界能力；Unity 资源兼容；部署与恢复。把 code semantic hash、Resource ABI、Native Layout Admission、bridge capability、metadata image quota 分开。资源 ABI 相同只是 DLL-only 的必要条件之一，不再被表达为充分条件。

原 M11 已有良好的性能预算，但其进入条件在 M10 之后。这会把本项目最重要的收益验证放得过晚。前移容量与基础性能 Gate，M11 保留完整加固、压测和上游演练。原 M08 已有不少基础类，后续是统一入口和部署准入集成，不应重新实现同名 Settings/Hasher/Graph/Generation 类。

## 7. 接受/不接受的审查推论

接受：现有静态证据足以要求修正热路径、容量准入、slot 身份和加载图算法；也足以确认 Add/Remove 不在当前支持范围。

不接受：仅凭本报告宣布所有 native 路径安全、宣称某平台性能提升若干百分比、把算法模型当成实际 IL2CPP 测试、把 M07 unsigned evidence 当作发行签名，或把旧版本的 green suite 直接标记为修复后通过。

详细的新设计见 `design.revised.md`，执行顺序见 `plans/README.md`，回归用例见 `validation-matrix.md`。原始 M00–M07 文档与证据保留不动；本包没有修改任何仓库。
