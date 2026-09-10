# H1R/M07 — 受控对照执行与解释

状态 Pending；用户2A；前置 M05 测量方法/双侧构建、M06 必需功能就绪。此阶段不默认开发新 candidate 代码。

| ID | Phase | 一个范围 | 停止点 |
|---|---|---|---|
| M07.A | Inspect | 两侧真实 source/build/harness/input 和环境可比性 | comparability-entry；停止 |
| M07.B-{mode} | Validate | 一个 mode 的预声明 pilot pair | raw、分辨率/时序/业务核对；停止 |
| M07.C | IndependentReview | 正式协议与 pilot 可比性 | 通过后封存 formal schedule；否则返回测量准备 |
| M07.D-{mode,pair/batch} | Validate | 一个 mode 的一对或已封存小批 pair IDs | 双侧 fresh processes/raw，停止 |
| M07.E | Validate | 完整 samples index 的独立重算 | paired summary 与集合完整性；停止 |
| M07.F | IndependentReview | 计时语义、paired 数据及差异解释 | 2A 是否完成；风险单列；停止 |

## 执行合同

遵守 [PERFORMANCE_PROTOCOL.md](../PERFORMANCE_PROTOCOL.md)。四模式每个至少10正式配对 fresh-process样本，balanced AB/BA、固定seed，pilot预先排除且保留；同机/Unity/SDK/compiler，Development=true、匹配C++Release、diagnostics/GC/计时策略。每次只执行冻结schedule中的当前片，不自行扩大/裁剪。

A=固定旧R01 native+必要明示measurement overlay；B=新candidate。真实ABI/profile/manifests分开，timed core、共同业务输入/资源/方法一致；不可比时先解决，不能只附一句“条件不同”关闭2A。旧profile不测8k；候选8k仍在M06完成。

不并发Player/build/压力验证。record pair/run IDs、PID/start nonce、原始ticks/frequency、input/source/library hashes、system状态。失败/无效样本保存并按规则重跑整对，不挑最快样本。

## 分析与回流

区分first-observed、warm、真实readiness和端到端load；不把预触达路径称绝对cold，不把loop次数当独立样本。RSS current/peak/managed时点一致。过程级median/IQR/min/max、配对差/比值重算，近零分母按预注册分辨率规则处理。

ComparabilityPassed 与 Measured 是证据状态，不是性能达标；未批准SLA不自动容许全部退化。稳定退化/额外内存/高方差写明确finding供H1判断，不顺势做R02优化。任何方法/代码/flags变更返回M05 freeze/build及受影响M06，再开新series，不重贴旧结果。

## 退出

protocol/schedule、双侧source/build、common-core/overlay、pilot和正式全部raw/launch/log、paired-results、comparability-report、performance-comparison、independent review。仅原R00历史48cells无法满足本阶段。保持Development范围，无非Development/P99/RAM阈值承诺。
