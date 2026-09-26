# H1 Human Review Gate — 用户发起的委托审查

日期：2026-09-25。

审查对象：R01 / R01B 的底层容量、metadata 索引编码、失败恢复模型，以及进入 R02 的条件。

发起依据：用户明确要求“你代替用户完成HumanReviewGate，提交review报告，如果有需要用户做的决策就一并列举出来询问用户（一次性批量询问）”。

## 1. 审查结论

**最终结论：H1 以 `PassedWithExplicitDeferredRisk` 关闭。用户已明确选择 `D1=A，D2=A`，因此 `humanGatePassed=true`、`mayEnterR02=true`。R02 仅具备进入资格，本次未启动 R02。**

本次已完成针对所列材料的 design → plan → 相关源码 → 测试与证据 → 性能和范围限制的委托审查。它不是重新执行所有测试，也不冒充 C10 中独立 `code-gate-reviewer` 的审查。新增源码核对是第 3 节列明的定点审查；其余完整执行链采用已提交的 Local Validation 和独立 M08 证据，保留其原有范围。

判断依据：

- 最新独立 M08 为 `MILESTONE PASS`，原三个证据阻塞已有可追踪的后继处置。新 count 执行补上了原先缺失的 Launch/Raw 层；不能把旧 12cf 记录改写为通过。[S02–S05]
- 六套必需 suite 的当前闭合方式是 **一套 FreshCurrentSourceExecution + 五套 AcceptedReusedAudited**，不是六套重新运行。[S03]
- 在已核对的源码和所选证据范围内，没有发现需要重新打开已关闭 count/容量/恢复问题的新阻塞性证据；这不是对四仓库全部代码或未测平台的无缺陷保证。
- 性能可比性成立，但 P01/P03 的暖态操作耗时和 RSS 存在实测退化；没有产品 SLA 不代表这些代价自动合格。用户已明确接受 D1/D2 为研发阶段延期风险，关闭条件转移为 R02 处置并在 H2 前复核。[S06–S08]
- live `Plan/CURRENT_STATUS.md` 滞后于最新 Local return。该文档应随本次报告更正为 M08 PASS、H1 等待风险决策；历史 checkpoint、V05、独立 review 和 Local 所有的报告保持不变。

当前状态：

```text
reviewDisposition = Completed
humanGateVerdict = PassedWithExplicitDeferredRisk
H1 = PassedWithExplicitDeferredRisk
M08Passed = true
humanGatePassed = true
mayEnterR02 = true
R02Started = false
```

用户决定已单独记录于 `HUMAN_REVIEW_DECISION.md`，首次记录提交为 `da4668d456763559d624e561cb265608d9ea443a`。该决定只关闭 H1，并不构成 R02 已开始、性能 SLA 已通过或 release 已批准。

## 2. 固定版本与工作区

所有候选分支均为 `codex/assembly-shadow-r01b-h1`。以下 HEAD 已通过 GitHub Connector 读取；它们是本报告的审查输入，不是本报告发布后才产生的文档提交。

| Repository | 审查输入 remote HEAD | Local Validation 记录的绝对路径 |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `2cbf68658a5b73189930fcdfe250835b72639515` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| night-outlook/hybridclr | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| night-outlook/hybridclr_unity | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| night-outlook/il2cpp_plus | `6be7f38bec2fa4677d24efc1a4a1294240789933` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

这些绝对路径来自 Local 的版本记录，本审查没有访问用户 Mac 文件系统。

必须区分的 demo 版本：

| 身份 | Commit |
| --- | --- |
| 当前可执行工具/分析源码 anchor | `0388479f7073289e3505b992956a7cbe78c302ce` |
| source-038 fresh count 的 Primary handoff | `df14afd618edd408356ee9559937ccf9080caef8` |
| 独立 M08 实际审查的已提交 checkpoint | `3754d35bed4efa62e16401453aa4f7edec185355` |
| 本次委托审查输入 HEAD | `2cbf68658a5b73189930fcdfe250835b72639515` |
| 历史正式性能执行 source | `27df1a3d60811dc121f296ab561ae313a382b363` |

本次 Connector compare 核实 `3754d35b… → 2cbf6865…` 仅有一个后继提交、八个文档/证据元数据路径：两个 live Local handoff、C10 review/receipt、FINAL_STATUS、两个 handoff 快照和 88 行 final manifest；没有运行时代码变更。source-038 到 M08 checkpoint 的源码等价性采用已提交的 Local/M08 审计，不声称本次重新完整计算了该较长差异。

本报告的包含提交及其后继状态文档提交只负责发布审查结果，不改变 source anchor，不重新生成历史 source/runtime pins，也不产生新的 Player 验证身份。

## 3. 实际审查范围、方法及限制

### 3.1 直接检查

- 规范性 `HUMAN_REVIEW_GATES.md`、`EVIDENCE_CONTRACT.md`、roadmap、R01/R01B plan、已记录的 R01B 用户容量合同，以及 R02 计划；主 DESIGN 中与 H1 有关的目标、不变量、容量和分配缓存章节。[S01, S06, S09, S10]
- 最新 LOCAL_VALIDATION、RETURN_TO_WEB、C08/C09/C10、历史 corrected E04、source-038 V05、此前 M08 findings 及性能分析的可比性、关键 operation/readiness/memory 统计段。[S02–S08]
- HybridCLR 固定版本的 `MetadataUtil.h:89–126`、`MetadataUtil.cpp:19–65`、`InterpreterMetadataIndexCodec.h:1–225`、`InterpreterMetadataIndexRuntime.h`、`InterpreterMetadataIndexRuntime.cpp:1–220`、`InterpreterImage.cpp:1715–1855`。[S11]
- IL2CPP Plus 固定版本的 `libil2cpp/vm/AssemblyShadow.cpp:1–130` 和完整 `AssemblyShadowRecovery.h`；Unity package 当前提交中 compiler-reference/ILPP diagnostic capture 的相关 diff。[S12, S13]
- 四个远端候选 ref，独立 M08 checkpoint 到本次输入 HEAD 的变更集合，以及下文公开给用户的百分比和 MiB 算术。

### 3.2 本次没有执行或不能声称执行的项目

| 项目 | 本次状态 / 采用方式 |
| --- | --- |
| Unity、IL2CPP、Editor/Player 构建及运行 | `NotRun`；采用已提交 Local 结果，不把本次文档审查算作新测试 |
| 完整四仓库逐行重新 code review | 未执行；仅上述定点源码检查，其余采用既有 review 和版本绑定证据 |
| 132 cell 的本地 launch/raw/binary 字节重新认证 | 本次未重新执行；C10 明确记录独立 reviewer 已逐条核验 |
| 七个大归档及用户本地 build roots 的重新 hash | 本次不可直接访问；采用 Local/C10 已提交认证，不声称 ExternalBytesVerifiedByThisReview |
| 88 项 final manifest 完整重新 hash | 本次未重算；直接核对后继路径集合，保留 Local 的 manifest 结果 |
| V04 全量严格 analyzer、V05 重新执行 | `NotRun`；读取版本绑定的输出及独立 review；本次只核对所引用统计和算术 |
| 新的独立 M08 审查 | 未委派；引用已存在的 C10 PASS，不替换其身份或报告 |

例如，E04 引用的历史 `local-validation-20260919-authority925e/V04/capacity-verify.log` 本次通过 GitHub 内容接口返回 404。该路径在 Local 审计中记录为本地可用且 hash 匹配；此 404 不能推出本地证据丢失，也不能声称该日志已由本审查直接读取。容量 suite 的执行准入采用 E04/C09/C10 的明确证据分类。此限制符合 EVIDENCE_CONTRACT 对外部对象和 receipt 认证的区分，不制造新的“全部外部字节已验证”声明。

## 4. H1 条件逐项判断

| H1 条件 | 证据和源码判断 | 本次处置 |
| --- | --- | --- |
| 实际目标规模及计数域 | 用户已经选择 8192 个进程生命周期累计 interpreter image；ordinary、Shadow 和 retained failed reservations 共同计数，AOT 不计入该 image 数 | 沿用已决合同，不重新询问，不恢复旧 65536 目标 |
| DLL 分布和余量 | 单文件最大 32 MiB、目标总字节 512 MiB、8192 数量档平均 64 KiB；至少 25% 可用编码容量余量，已保留未映射 reservation 也算消耗 | 保留 mixed/outlier、dense/sparse、实际内存各自证据边界；padding 不能证明 metadata 密度 |
| Codec / AOT / sentinel | 源码保留 AOT 非负 raw 域和 `-1` sentinel；interpreter 使用独立负数编码，ID 1..8192；错误走异常而非仅依赖 Debug assert | 在定点检查范围内一致；不声称普通 32 位整数里的所有数值都可作合法 token |
| 共享预算与不可回收语义 | 单一 codec/reservation ledger；整批校验后提交，所有权和发布映射分离；construction/private/public 路径区分 | 支持进程生命周期预算模型；不能以 Abort、换补丁或修改 manifest 重置预算 |
| 参数计数修复 | `InterpreterImage.cpp` 分离命名参数表范围与真实 signature 数量，使用宽类型校验，`actualParamCount >= 256` 在 narrowing 之前拒绝 | 与 fresh parameter/nested 132-cell 负向链共同支持原 count 问题关闭；不把它推广为任意畸形元数据安全性证明 |
| publication / recovery | pure recovery classifier 优先检查 terminal failure、poison 和 publication 一致性；未知/internal 错误要求 restart；clean Abort 只提供 baseline eligibility，仍需启动验证 | 保留“可纠正输入 / 必须 Abort / 必须 restart / active Shadow”区别，不能把 catch 成功等同健康 |
| ordinary / mixed 容量执行 | 当前 C09 选用已审计的 925e 历史容量/混合容量 suite，相关源码和 runtime pins 等价；C10 认可其复用链 | `AcceptedReusedAudited`，不是 source-038 新运行；不能承诺任意 8192 个 DLL 都一定满足 metadata、内存或 ABI 准入 |
| M00–M07 受影响回归 | 所选 M07 14/14、startup11、failure/publication/recovery、native matrix 等通过记录由 E04/C09 指定复用 | 保留 bounded/平台边界；不能据此宣布所有历史能力在所有平台均重新通过 |
| 相对旧 profile 的性能 | 40 对正式受控 A/B 进程样本及当前严格分析，比较的是 R01 → 当前候选整体，不是 codec-only 因果实验 | 可比性可接受；耗时和 RSS 风险分别交 D1、D2 |
| 下一阶段 / release 范围 | H1 通过只允许进入 R02；Windows/Android、生产集成及后续生命周期能力仍按原 roadmap 的 M10/X01 等验证 | 不因为 H1 review 或 M08 PASS 扩大产品支持范围 |

Codec 常量为 `usablePages=524287`、`maxChargedPages=393215`，差额 `131072`，对应约 25.00005% 的可用页数。这是源码常量算术，不是本次 Player 的实际余量测量。也不能用页数余量代替真实运行 RAM 余量。[S09, S11]

## 5. 证据闭合及历史 findings

### 5.1 当前执行分类

| 范围 | 当前所选证据 | 不得扩大为 |
| --- | --- | --- |
| count-chain | source-038 新 fixture、新构建、新 132-cell Player chain；118 正常通过 + 14 符合预期的拒绝；132 verifier、launch、semantic raw、unique run IDs/PIDs | 14 个失败；或者任意未测畸形输入也通过 |
| startup11 | `AcceptedReusedAudited` | 本次/本日重新执行的全部启动路径 |
| failure-publication-recovery | `AcceptedReusedAudited` | 完整生产 M09 coordinator 已交付 |
| ordinary-capacity | `AcceptedReusedAudited` | 无输入分布限制的通用 8192-image 保证 |
| mixed-capacity | `AcceptedReusedAudited` | 可在同进程无限成功 Shadow/复用预算 |
| M07/native | `AcceptedReusedAudited` | 未运行平台或所有未测回归路径通过 |
| source-038 bounded tests | Local 记录 387/387 | 本次重新运行 |
| source-038 Python discovery | Local 记录 1071 leaves：1043 Passed、28 明确 Skipped、零 Failed/Error；wrapper exit 2 保留 | 1071/1071 Passed，或所有 Python 当前环境覆盖完整 |
| performance | source-27df 原执行经认证复用，source-038 analyzer 重新分析；40 正式 pair、4 valid pilot、1 preserved invalid pilot | source-038 fresh performance Player；P99 / 非 Development / 跨平台性能 |

C08 的六个 build 中只有四个 candidate ON/OFF × C++ Debug/Release tuple 是 count 接受输入；两个 reproduction build 是诊断来源。managed `SourceGraphBound` 不能改写为每一次都重新执行了 Csc。首个 A attempt 的 stale installed-runtime receipt 失败被保留，后续 pinned installer 与 B root 正常完成，不删除失败或改写 source pin 让预检过关。[S02, S03]

### 5.2 先前 M08 三类阻塞的处置

| 历史问题 | 后继闭合 | 保留限制 |
| --- | --- | --- |
| prior review / per-finding closure 来源缺失 | 恢复并认证原记录，Local 与 C10 重新核对其来源及后继证据 | 不将此前缺失记录改写成当时已完整 |
| 旧 manifest 不完整 | 925e 使用认证的历史 handoff 外部成员形成 effective 293/293；6913 明确 29 verified + 1 unavailable/excluded；source-27df 后继 checkpoint 92/92 | 6913 原 manifest 不能宣称 30/30；排除项不是已恢复 |
| whole-H1 reuse / count Launch-Raw 缺口 | 五套 suite 完成 audited reuse；count 单独采用 fresh source-038 完整链，C10 PASS | 旧 12cf count 仍为历史 blocked，不从 summary 倒造 raw/launch |

上述是对已提交后继证据的审查接受，不是本次重新恢复、重跑或重新独立认证这些原始对象。[S02–S05]

## 6. 性能审查

### 6.1 比较与统计口径

A = R01 profile-1 reference；B = R01B candidate。Unity `2022.3.62f2` / `StandaloneOSX` / `arm64`；Development Player、C++ Release、Low stripping、OptimizeSpeed。四模式各 10 对正式 fresh-process A/B 样本，pilot 不计入正式统计。源码、ABI 和运行身份的必要差异在协议中显式记录。[S06–S08]

下面 operation 百分比取 JSON 中 **paired B/A ratio 的中位数**，不是两个独立中位数相除。RSS 和 readiness 表使用 A/B 各自中位数，其差额明确是边际中位数之差，不冒充 paired-delta 中位数。MiB = 1048576 bytes。

### 6.2 暖态 repeat10000

| 模式 / 操作 | A 中位数 μs/op | B 中位数 μs/op | 配对 B/A 中位数 | 耗时变化 |
| --- | ---: | ---: | ---: | ---: |
| ON-P01 / allocation | 10.35378 | 11.78746 | 1.133375 | +13.34% |
| ON-P01 / reflectionInvoke | 2.68341 | 3.372115 | 1.265703 | +26.57% |
| ON-P01 / closedGeneric | 3.889145 | 4.71052 | 1.204152 | +20.42% |
| ON-P03 / allocation | 10.45765 | 11.95852 | 1.150110 | +15.01% |
| ON-P03 / reflectionInvoke | 2.941075 | 3.677905 | 1.275901 | +27.59% |
| ON-P03 / closedGeneric | 4.12906 | 5.023015 | 1.220929 | +22.09% |

六个 mode/operation 组合的配对比率最小值均大于 1；因此在这组正式样本中，退化不是仅由某一个极端慢样本产生。它仍不证明全平台、任意业务负载的同等退化，也不能换算成全游戏帧时间增加 13–28%。[S07]

### 6.3 启动、first-observed 与内存

| 指标 | ON-P01 A → B | ON-P03 A → B |
| --- | ---: | ---: |
| readiness 各自中位数，ms | 1261.92 → 1095.67 | 1278.73 → 1116.09 |
| readiness 边际中位数差，ms | -166.26 | -162.64 |
| before-benchmark RSS，各自中位数 MiB | 215.0547 → 233.2656 | 215.9375 → 235.0938 |
| RSS 边际中位数差，MiB | +18.2109 | +19.1563 |
| RSS 边际中位数变化 | +8.47% | +8.87% |
| managed bytes，各自中位数 MiB | 14.8984 → 12.0762 | 15.0000 → 12.4863 |

RSS 原字节值：P01 `225501184 → 244596736`；P03 `226426880 → 246513664`。managed memory 下降不能抵消或否定进程 RSS 上升。RSS 使用 Darwin resident size；managed 使用 `GC.GetTotalMemory(false)`、未强制 GC。lifetime peak 是进程生命期峰值，不能解释为只由这次 benchmark 新增的内存。[S07]

readiness 的改善不能与每次方法调用的退化相互抵销：它们是不同维度。first-observed allocation 的配对 B/A 中位数分别约为 P01 0.965、P03 1.005，不支持“所有首调用路径都显著改善”的结论。first-observed reflection/generic 波动更大，也不宜从暖态结果推导首调用的确定效果。

对照并非所有模式都退化：既有独立 review 记录 ON-NoPatch 的三项暖态配对比率约为 0.874 / 0.945 / 0.980；OFF-NoPatch readiness 中位数约为 858.34 → 868.03 ms。ON-NoPatch 的候选 readiness 最大样本约 1615.05 ms，显著高于其中位数 954.08 ms，因此也不能只报中位数而忽略方差。该部分对照采用已提交独立 review 和对应已读取统计，不声称本次全量重建原进程样本。[S05, S07]

### 6.4 工程结论

- `ComparabilityPassed` 有效；`performanceAcceptance=NotClaimedNoSLA` 应保留到用户作出风险处置，不能自动转成性能合格。
- CPU 和 RSS 分开决策。二者可能有共同原因，但目前所选材料不能证明同一根因，更不能把全部差异归因于 codec。
- R02 本就负责 allocation proof cache、definition scan、guard/diagnostic 分层及 native heap 测量，因此把这两项列为 R02 的显式输入有架构上的合理性。但这只是本审查建议，不是“R02 一定会消除全部退化”的保证。[S10]
- 本 gate 不批准生产 RAM 上限、非 Development 性能、跨平台性能或 P99；不以小型 fixture 的平均结果代替真实项目准入。

## 7. Findings 与处置

| ID | 类型 / 重要性 | 处置与关闭条件 |
| --- | --- | --- |
| H1-GR-01 | 暖态性能退化；已接受延期风险 | **D1=A**。H1 不再阻塞；R02 必须定位和配对复测，在进入 H2 审查前提交结果及剩余代价，不能直接拖到 M11 才首次解释 |
| H1-GR-02 | 额外 RSS；已接受延期风险 | **D2=A**。H1 不再阻塞；R02 分离 codec 常驻存储、native allocation/cache、managed 与 process RSS 的测量；不能未经实验证明就认定泄漏或固定 19 MiB 常数 |
| H1-GR-03 | live coordination 文档滞后；文档一致性问题 | 更正 live CURRENT_STATUS，明确最新 M08 PASS、两个决定待处理。保留旧状态的 Git 历史及 immutable checkpoints；不重新写 Local 所有的验证报告 |
| H1-GR-04 | 审查可访问性 / 保留范围；运行约束 | 七归档、四 candidate build roots、历史复用及性能原始证据继续保留。外部字节当前由 Local/C10 认证，后续不能用本报告替代其保存或复验 |

这四项不等于独立 M08 有四项新发现。C10 的历史结果仍是零 findings；GR-01/02 是 H1 风险判断，GR-03 是当前协调文档问题，GR-04 是证据可访问性和保留边界。

另见 `InterpreterMetadataIndexCodec.h` 开头“not yet wired into the runtime”注释，与本次读取的实际 runtime adapter 已接入状态不一致。这属于旧注释滞后，不是证明实现未接入的证据。建议在后续授权的源码维护周期更正；本次不改 native pin，也不为注释更改触发新的安装/构建链。

## 8. H1 通过后的后续工作边界

以下执行约束随 `PassedWithExplicitDeferredRisk` 生效，但本次仍不启动 R02：

1. 用户决定已记录于 `HUMAN_REVIEW_DECISION.md`，绑定本报告版本、四仓库审查 tuple、D1/D2 选择和延期关闭条件。历史 Local/M08 文档不回写为“当时人工已经批准”。
2. 下一 Primary Implementation 周期只进入既有 R02 范围，建立现状 B 与 R02 候选的受控对照；同时保留 A 的历史 reference，避免移动参照掩盖回归。源码/构建变化后，旧性能 series 仍是旧 source 身份。
3. CPU 诊断区分 definition scans、layout proofs、cache hits、临时 native allocation、guard 和 observation contention；不得通过关闭必要 baseline-use/poison/上下文检查取得表面性能收益。
4. 内存记录 before/after、常驻容量结构、native 与 managed 字节、RSS 和 lifetime peak 的各自语义；对根因只作证据支持的归因。
5. R02 修改涉及的 count、容量、private/publication、failure、early-use、M07 路径执行受影响回归；未影响 suite 只能经明确等价性审计复用，不能默认全部复用。
6. R02 退出时提供性能解释、优化前后数据、负向测试和剩余风险；若代价仍无法接受，停止推进并返回同一风险决定。H2 审查必须看到其处置，不能把 H1 延期理解为永久豁免。
7. 保留 roadmap 的后续 Human Review Gates、M10 平台/生产集成以及用户要求的 X01 独立能力。H1 不缩减既定容量目标，不授予 release 结论，不自动批准后续阶段。

## 9. 用户决策（已完成）

用户于 2026-09-25 明确回复 `D1=A，D2=A`。容量、计数域、已有平台计划和普通工程修正均保持既有决定。

| 决定 | A：建议选项 | B：不接受延期 |
| --- | --- | --- |
| D1：暖态耗时 | 接受本报告中 P01/P03 allocation +13.34/+15.01%、reflection +26.57/+27.59%、closedGeneric +20.42/+22.09% 作为 **H1 研发阶段显式延期风险**；R02 定位/优化/受控复测，进入 H2 审查前提交处置。不等于性能 SLA 通过 | H1 保持未通过；先制定并授权局限于该性能问题的修复与验证方案，再重新关闭 H1；不能借机启动完整 R02 |
| D2：RSS | 接受 P01/P03 before-benchmark RSS 边际中位数增加 **18.2109/19.1563 MiB** 作为 **H1 研发阶段显式延期风险**；R02 解释和复测；生产设备 RAM 预算仍须在后续目标平台验证前明确 | H1 保持未通过；先处理内存代价并提供可接受证据，再重新关闭 H1 |

最终选择为两个 A，因此本 Gate 记录为 `PassedWithExplicitDeferredRisk`，`humanGatePassed=true`、`mayEnterR02=true`。D1/D2 仍不是生产 SLA 或 release 验收；它们的延期关闭义务在 R02/H2 边界继续有效。

## 10. 版本绑定来源与复核入口

除 S11–S13 外，以下来源统一固定在 demo commit `2cbf68658a5b73189930fcdfe250835b72639515`。文中行范围用于说明实际读取范围；读取全文的短文件不另列行号。

- **S01** — `Docs/AssemblyShadow/Plan/HUMAN_REVIEW_GATES.md`、`EVIDENCE_CONTRACT.md`、`ROADMAP.md`、`DESIGN.md` 的 H1 相关章节，以及 `Plan/completed/R01-metadata-budget-and-failure-contract.md`、`R01B-metadata-index-expansion.md`。
- **S02** — `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` 当前 2026-09-25 fresh-count 段、`RETURN_TO_WEB.md` 当前 return；两份报告的历史段仍为历史。
- **S03** — `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260925-authority038-fresh-count-m08/C08/fresh-count-matrix-closure.json`、`C09/whole-h1-suite-closure-v2.json`。
- **S04** — 同 checkpoint 的 `C10/independent-review.md`，Git blob `0f342d6eb830611943036a4e701b08d7681708a3`；review 时间 2026-09-25 11:41:32–11:57:00 UTC，审查 HEAD `3754d35bed4efa62e16401453aa4f7edec185355`。
- **S05** — `local-validation-20260925-authority038-m08-re-review/E04/corrected-whole-h1-suite-reuse-authentication.json`；`local-validation-20260924-authority038-v05-m08/M08/independent-review.md`；`local-validation-20260919-authority925e/README.md`、`results-summary.json`。以上 checkpoint 均位于 `Docs/AssemblyShadow/History/M07R/H1/`。
- **S06** — `Docs/AssemblyShadow/Plan/PERFORMANCE_PROTOCOL.md` 的 P1、P3–P6 和 analysis-only successor 限制；`local-validation-20260924-authority038-v05-m08/V05/successor-evidence.json`。
- **S07** — `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-pre-v05-v04/V04/historical-performance-analysis.json`，Git blob `15ed13d496eeee3753122031e8b305ac13c6b916`。直接读取可比性/要求、ON-NoPatch readiness、P01/P03 operations 和 memory/readiness 的有关段；没有在此环境重新执行全量 analyzer。
- **S08** — V05 将 S07 绑定为 SHA-256 `c02c4ffd0ad93759ef4f2ffb3a7482b3c9d5ed96cf4c9a122f35135478323053`、379746 bytes；V05 自身在 C09 绑定为 `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f`。这些是所审 receipt 的绑定值，不宣称本次重新对全文件字节算出了它们。
- **S09** — `Docs/AssemblyShadow/History/M07R/R01B/R01B-execution-plan.md` 中 Revised workload contract — 2026-09-08；`R01B-report.md` 仅作为明确标记的历史 v6 记录，不代替 current selected suite。
- **S10** — `Docs/AssemblyShadow/Plan/stages/R02-allocation-cache-and-guards.md`，Git blob `c31247dd2de68054e06e3abe9b724c3157a33cdf`。
- **S11** — `night-outlook/hybridclr@1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`，第 3.1 节所列文件/行段。Codec blob `2020d4e2da6dea8601525203e7ab307d21c40a73`；InterpreterImage blob `afe4b3b9e29fa4023c6025e0b35e13d53a6ff15b`。
- **S12** — `night-outlook/il2cpp_plus@6be7f38bec2fa4677d24efc1a4a1294240789933`，`libil2cpp/vm/AssemblyShadow.cpp` 开头与 `AssemblyShadowRecovery.h`；Recovery blob `2c209c65c23577344bd2baaa365f35fb19e2b7bc`。
- **S13** — `night-outlook/hybridclr_unity@0ea633a2c5b936b5af69d944593c55bd2783fca9`，当前 commit 中 CapturedCompilerReferences、ILPP failure capture/replay 的相关 diff；不是该 package 全代码重新审查。

C09 的其它重要绑定：fresh count closure `1e70e5450c3eac7d05c281699d6c78198af6b7cbfc8c010fbe092bd6222f509c`；aggregate `c7d26a74bbe9d5cf4192e04e7f3905555c0de4e70b328f18e4c34dc53e684e37`；Launch/Raw audit `af4ffb9a947a605154cd50e0b1348d15eed3b31791eccc382b5df1e39e6c67be`；seal index `f3c3fbae4ca79a7883b4ecc5cf7357f3038b2358b2046affa5914023583b06c1`。

## 11. 交付与停止点

本次产品源码、测试源码、安装 runtime、source pins、历史证据和 Local 所有的 handoff 均不修改。交付限于本报告及 live CURRENT_STATUS 的后继协调更正。

GitHub Connector 的 contents API 写入路径已在本会话前一轮通过四仓库 disposable commit/read-back smoke test。保留的临时分支 `codex/connector-smoke-20260925-pio-7f6d2a91` 不是产品或交付版本，不能合并；当前 Connector 未提供分支删除操作。它们的存在不授予产品验收。

**停止点：H1 已按用户决定关闭为 `PassedWithExplicitDeferredRisk`。本次不运行新的 Player、不启动 R02；下一 Primary Implementation 周期可在明确启动后进入既有 R02 范围。**
