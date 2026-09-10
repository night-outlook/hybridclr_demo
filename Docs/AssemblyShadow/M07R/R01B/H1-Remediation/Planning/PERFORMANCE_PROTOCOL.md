# 受控 Development 对照协议（2A）

版本 2.0；尚无新测量结果。以下采样组织为原计划约定及本版细化，不是用户批准的性能 SLA。

## P1. 要回答的问题

相同且双方支持的业务负载/方法下，旧 R01 profile 1 与修复后的 R01B profile 2 的 first-observed/warm witness、readiness、明确时点内存有何差异？比较的是已列明 R01→候选整体变化，不直接把差值归因于 codec。

reference 使用 [source-pins.original.json](source-pins.original.json) 的 acceptedR01ReferencePins；candidate 使用 M05 新冻结 pairing。旧 native sources 不回移新 codec 或优化。必要共同测量 overlay 单列源/diff/hash，reference 不冒充 immutable old-Player 拒绝测试的原对象。

## P2. 预注册与冻结顺序

M00 记录问题、四模式、方法、采样单位、最小样本、无效样本处理和环境字段；这是协调者协议任务，不混入首个只读工作区盘点。M05.A 完成共同测量层 inspection/必要实现/验证/review，再 freeze candidate executable sources；不能默认到 M07 才改候选代码。

正式采样前冻结 protocol、source/build map、case/operation set、balanced schedule 和 hash。protocol 不包含自身 hash 或后生成 schedule 的 hash；schedule 可引用 protocol，最后由 sample index 绑定 protocol/schedule/build map，避免循环。pilot 仅用于链路、分辨率及可比性检查，原始 pilot 保留并预先排除正式统计。需要调整两边测量代码/iterations 时重新版本化并返回受影响 freeze/build/retest，不用正式快慢结果选择方法。

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
