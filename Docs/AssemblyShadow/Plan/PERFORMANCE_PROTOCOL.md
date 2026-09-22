# 受控 Development 对照协议（2A）

版本 2.0；尚无新测量结果。以下采样组织为原计划约定及本版细化，不是用户批准的性能 SLA。

## P1. 要回答的问题

相同且双方支持的业务负载/方法下，旧 R01 profile 1 与修复后的 R01B profile 2 的 first-observed/warm witness、readiness、明确时点内存有何差异？比较的是已列明 R01→候选整体变化，不直接把差值归因于 codec。

reference 使用 [source-pins.original.json](references/source-pins.original.json) 的 acceptedR01ReferencePins；candidate 使用 M05 新冻结 pairing。旧 native sources 不回移新 codec 或优化。必要共同测量 overlay 单列源/diff/hash，reference 不冒充 immutable old-Player 拒绝测试的原对象。

## P2. 预注册与冻结顺序

M00 记录问题、四模式、方法、采样单位、最小样本、无效样本处理和环境字段；这是协调者协议任务，不混入首个只读工作区盘点。M05.A 完成共同测量层 inspection/必要实现/验证/review，再 freeze candidate executable sources；不能默认到 M07 才改候选代码。

正式采样前冻结 protocol、source/build map、case/operation set、balanced schedule 和 hash。protocol 不包含自身 hash 或后生成 schedule 的 hash；schedule 可引用 protocol，最后由 sample index 绑定 protocol/schedule/build map，避免循环。pilot 仅用于链路、分辨率及可比性检查，原始 pilot 保留并预先排除正式统计。需要调整两边测量代码/iterations 时重新版本化并返回受影响 freeze/build/retest，不用正式快慢结果选择方法。

## P2A. Pilot 严格验证封存与 Formal admission

Pilot 仍按本协议完整执行且全部排除在 formal 统计之外。四个 pilot pair 全部完成后，在任何 formal Player 启动前必须执行一次独立的严格封存步骤：

1. 对每个被选择的最新成功 pilot pair 的 A/B launch receipt 重新执行现有 `r00_results.verify_suite` 完整重建，共 8 个 side graph；
2. 封存 protocol、schedule、frozen build map、pilot attempt history、每个 pilot launch receipt 和 verifier/tool 实现的内容 hash；
3. 从已经通过严格重建的 launch receipt 中取得完整 `inputHashesBefore == inputHashesAfter` immutable input inventory，并补充 result / early capsule / early result evidence；
4. 在完整严格重建前后记录每个 immutable file 的 canonical path 及 cross-remount-stable filesystem identity guard（inode、mode、size、mtimeNs、ctimeNs），要求前后完全一致；
5. `st_dev` 不属于 acceptance guard：它表示当前 mount/filesystem instance，可在 remount 后变化而文件 canonical path、bytes、inode 和其它稳定 stat identity 完全不变；
6. 输出新的 `H1PilotVerificationReceipt`，并绑定 `guardKind=CrossRemountStableStatGuard`、`guardVersion=2` 和精确 guard field 列表。旧 device-bound seal 不得按新语义继续使用，必须重新 seal。

后续每个 formal admission **不得再次重跑 8 个 pilot graph 的全量内容 hash/reconstruction**。它只允许：

- 内容 hash 验证 protocol、schedule、build map、pilot launch receipt、sealing/formal verifier tools；
- 验证当前 pilot attempt 子集与封存时完全一致；
- 验证从当前 launch receipts 推导的 immutable path/hash inventory 与封存 inventory 完全一致；
- 对每个 sealed immutable file 验证 canonical path 和 filesystem identity guard 未改变。

任一 path/hash/tool/acceptance-guard 改变都必须 fail closed，并要求重新执行一次完整严格 pilot seal；不得自动把 acceptance stat mismatch 当作可接受的 cache miss，也不得在 formal admission 中静默重新生成 seal。仅 `st_dev` 变化不构成 guard mismatch；其它字段仍严格 fail closed。

该机制只消除重复的 **formal pre-launch pilot reconstruction**。它不改变 build-map comparability、pair ordering、whole-pair retry、样本保留、正式统计或最终 analyzer。最终 analyzer 仍对全部选中 pilot/formal launch evidence 执行原有严格验证，pilot seal 不能替代最终证据审计。

## P2B. Retained graph 的 source-pairing bridge

若已通过的 performance graph 来自较早 demo source anchor，而当前 source anchor 只增加了与 Player 构建/运行无关的 performance admission tooling，则不得直接把旧 graph 当作 current-pairing graph，也不得修改 `r00_player_inputs.require_current_pairing`、重写旧 receipt 或移动 source pin。

本 H1 允许的唯一 retained profile-2 graph 是 demo revision `69130bbb3a6df516916dddb5ad263799a7c6e5e3`。复用前必须生成新的 `H1GraphReuseBridge`，并同时满足：

1. current candidate source/runtime authority 通过原有全局 verifier；
2. graph 与 current 的 Unity version、target、architecture 完全一致；
3. graph 与 current 的 HybridCLR、HybridCLR Unity、IL2CPP pin 完全一致；
4. graph demo revision 必须精确为 `69130bbb...`，且它必须是 current source anchor 的 Git ancestor；
5. 忽略现有 metadata-only 规则后，`69130bbb... → current anchor` 的 Git tree delta 必须**精确等于**人工 review 的 CI / `Tools/AssemblyShadow` admission-tooling allowlist；不能是 subset，也不能出现 Assets、Packages、runtime/native、measurement source、protocol/schedule/map producer 等额外路径；
6. bridge 绑定 current source-pin file、frozen build map、完整 old/current source-pin DTO、每个 changed Git blob、bridge/verifier implementation hash 和 current installed-runtime verification。

bridge 验证通过后，默认 R00 contract 仍保持 current-pairing-only。只有 seal/final analyzer 从该 receipt 得到的显式 `H1AuthenticatedGraphReuseAuthority` 可以在 retained candidate side B 上把 expected source pairing 设为旧 graph DTO。protected side A 和其它 R00 调用继续走默认严格路径。

retained candidate 的 ON performance launch 使用 `R01EarlyStartup` 时，outer R00 graph 验证与 nested early-capsule reconstruction 必须使用**同一个已经 bridge-authenticated 的 authority**。该 authority 只允许通过 R00 verifier 传入内部 `_prepare`，并且 nested reuse scope 只允许 `Baseline` / `Control` 两种 performance early mode。direct early verifier、Ordinary、failure、guard mode 保持 current-pairing-only 或直接拒绝 retained authority；不得增加通用 historical-pairing CLI override。

在完整 8-side seal 前，Local 必须先运行 read-only retained-early preflight，对 candidate side B 的 `R00-ON-NoPatch`、`R00-ON-P01`、`R00-ON-P03` 做 strict bridge-aware R00 verification，从而提前覆盖 Baseline 与 Control 的 nested capsule reconstruction。preflight 只作诊断门，不替代完整 pilot seal；失败时必须在 seal 前停止。

`H1PilotVerificationReceipt` 必须绑定 graph-reuse bridge；每个 formal attempt 也必须绑定相同 bridge。正式采样链不能切换 bridge。最终 analyzer 必须再次执行 bridge 的 full authentication，再用该 authority 验证 retained side B；不能用 pilot seal 或 scope audit 替代最终 strict evidence reconstruction。

retained pilot index 中的 `runner` 字段属于**生成该历史 pilot 的不可变 provenance**，不等同于 current formal runner implementation。若 current source 的 `run-r00-players.py` 已因 H1 tooling 修复而变化，seal admission 不能直接要求历史 pilot runner hash 等于 current runner hash。

允许的唯一 historical runner provenance 必须由当前 `H1GraphReuseBridge` 自 Git anchor `69130bbb...:Tools/AssemblyShadow/run-r00-players.py` 重新计算并写入 bridge；调用者不得传入 arbitrary historical path/hash。bridge verification 必须再次计算并匹配该 binding。只有 bridge-authenticated retained **pilot** row 可使用该 historical runner binding；所有新的 formal attempt 仍必须绑定 current runner。

在完整 8-side seal 前必须先运行 `H1RetainedPilotAdmissionPreflight`：full-authenticate bridge，使用其 Git-derived retained runner 验证完整 retained pilot history，并选出四个最新 Passed pilot pair，但不做 deep R00 reconstruction。缺少 bridge、runner path/hash 不等于固定 anchor、或 bridge switching 都必须在 seal 前 fail closed。该 preflight 不能替代 strict seal。

任何 current source-pin、allowed-tool verifier、build map、bridge receipt 或 Git delta 变化都会使 bridge 失效。失效时只能重新做完整 bridge authentication（若仍满足同一规范）或重建 current-pairing graph；不能自动降级为“scope audit 已通过”。
## P2C. Formal fresh-launch subprocess authority

bridge/seal/formal admission 通过并不自动授权新的 R00 runner 子进程读取 retained candidate graph。formal side B 的 fresh execution 必须通过单独的、pair/attempt-bound `H1FormalSideLaunchAuthority` 跨越 parent → subprocess 边界；不得给 `run-r00-players.py` 增加 raw historical revision / source-pin override。

每个 retained candidate formal attempt 的 side B 在启动 runner 前由 paired driver 生成一个新的 authority receipt。receipt 必须绑定：

- pairId、attempt、mode、AB/BA order；
- candidate project；
- protocol、schedule、frozen build map；
- graph-reuse bridge、pilot verification seal；
- fixture manifest、Native ON/OFF receipt、Editor replay；
- formal-authority module、paired driver、R00 runner、R00 input/results verifier、early verifier 等当前 tool hash。

`run-r00-players.py` 只有在收到该 H1-specific receipt 时才允许 retained side-B 路径；它必须重新验证 receipt、same bridge/seal/map/input/tool bindings，并从 bridge 重新得到 `H1AuthenticatedGraphReuseAuthority`。随后 outer input verification 使用 `verify_inputs_with_reuse`；ON mode 的 nested Baseline/Control early preparation继续使用同一个 authority。无 receipt 时 runner 行为保持 current-pairing-only。

protected side A 不得携带 retained formal authority。parent 只有在 runner 生成的 R00 launch receipt 回显完全相同 authority binding 时才能把该 side 标为 Passed。

formal attempt diagnostics 必须保留 `formalLaunchAuthority` binding。若 side B 在生成 R00 launch receipt 前失败，authority receipt 仍作为失败 attempt evidence 保留；retry 不得覆盖旧 authority。resumed formal chain 对所有实际启动/准备过的 retained side-B attempt 必须保持可验证 authority binding。

final analyzer 必须在统计前重新验证每个 formal side-B authority 的 pairId/attempt/input/bridge/seal/tool bindings，并确认 side A 没有 retained authority。successful R00 receipt 还必须回显同一 authority。authority receipt 不能替代原有 launch/raw evidence verification。

source/tool 变化会使旧 bridge、seal 和 formal authority 一并失效；新的 source series 必须重新创建 bridge/seal，并从 retained pilot index 开始新的 formal chain。旧 source 下失败的 formal attempts 作为历史 evidence 保留，但不得混入新 source 的累计 sample index。
## P3. 可比性

| 项目 | 必需处理 |
|---|---|
| 环境 | 同 Unity 2022.3.62f2、StandaloneOSX arm64、同机 SDK/clang；记录 OS/设备、负载/温度或可获得状态 |
| 构建 | 双方 Development=true、相同 C++ Release/优化/Strip/CodeGen、assertion 与 diagnostics 条件；不接 Profiler/deep profiling/debugger |
| 业务输入 | 相同 witness 方法、DLL/资源内容、输出；优先 byte-identical fixtures；不相同时先独立证明可比，不自动认可 |
| timed core | 内容 hash 相同，计时 API、warmup/iterations、GC/内存采样边界相同 |
| startup | early registration/configure/Stage/Validate/Commit 和同进程 handoff 语义对应；一边晚启动另一边 early 不得混为 codec 效应 |
| 必然差异 | 各自真实 profile、ABI、source/buildGuid/manifests；接入差异逐项列在未计时边界，不伪造相同身份 |

每项标 Matched / ExpectedDifferent / Unmatched。影响结论的 Unmatched 导致 ComparabilityFailed/Incomplete；整改前不能完成 2A。框架固有计数器差异须如实说明，不能只关慢的一边。

## P4. 四模式与样本

`R00-OFF-NoPatch`、`R00-ON-NoPatch`、`R00-ON-P01`、`R00-ON-P03`。每模式至少 **10 对正式 A/B fresh-process samples**，另至少一对 pilot；四模式共至少 40 对正式样本，而非把循环次数当进程样本。每对 AB 或 BA 预生成且总体均衡，fixed seed 和 schedule 在采样前封存。

现有 witness 的 warmup=100、repeated=10000 作为默认；完整操作清单由源码/raw 核对，不把历史“48 cells”硬编码为新测量清单。ON-NoPatch 不等于 OFF；P03 多 image 不等于多 transaction。

调度每次只运行一个 mode 的一对或已封存小批 pair IDs，不启动其它 suite。每进程唯一 run ID、PID/start nonce、build/source/fixture hashes、计时原数值。设备上不并发 Unity 构建或容量压力。失败/timeout 保留原因，按预注册规则重跑整对，不择优删除慢样本或只重跑某一边。

共同负载须先在双方真实 admission 下验证。**不得要求旧 profile 运行 8192-image/512 MiB 压力**；候选该规模验收仍完整保留于 M06。可选 codec microbenchmark/共同 ordinary 小规模负载只作补充，不替代 Player 对照或扩张必做范围。

## P5. 测量语义

first-observed 是当前 probe 首次计时，不自动是全路径 cold；列出此前 GetType/反射/early callback 触达。warm 保存 warmup 后总 ticks、frequency、iterations 和派生 per-op。readiness 仅代表实际起止事件；不能把 coroutine 起点到 witness 就绪当完整 native 加载时间。

需要纯 load 分量时两边都在 timer 外准备 bytes，新增 cell 明确命名。包含 I/O/hash/load/invoke/checks/sampling 的时间只能称端到端，不能复用容量 loadMilliseconds 作 codec-only 指标。

相同阶段记录 current RSS、managed bytes；lifetime peak 单列。默认 timed loop 内不强制 GC；若 setup 后显式 GC，两边一致并记录。不得把 peak−initial 称为精确 metadata 占用，或把 512 MiB 输入当 RAM 上限。

## P6. 分析与退出

以 process pair 为统计单位；按 mode/operation/phase 报 n、median/IQR/min/max、配对 B−A 及 B/A。分母近零或低于冻结的分辨率规则时不报夸张比例。可选 process-level bootstrap 须记录算法/seed；不以 10 对数据宣称 P99。

分别输出 ComparabilityPassed/Failed/Incomplete 与 Measured/Invalid；没有 SLA 不等于任何退化自动合格。稳定退化、额外内存或高方差形成解释/定位项，交 H1 判断；不顺带实现 R02 优化。源/构建改变需要新 series、配对重测及受影响功能回归。

产物：protocol/schedule/build map、common-core 和 overlay 证明、pilot/正式全部 launch/raw/log、paired-samples.jsonl、paired-summary.json、comparability-report.json、performance-comparison.md。独立 reviewer 查真实方法和样本；仅重算历史 R00 不关闭 2A。明确不作非 Development、P99、生产 RAM 阈值、跨平台或 codec-only 因果声明。
