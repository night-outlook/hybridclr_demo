# 验证矩阵：拆批不删覆盖

状态：全部待执行。`H1R-*` 是本整改包 requirement/test IDs，不修改历史用例身份。

## V1. Count 基础输入

| ID | 方法 signature 参数数 | oracle |
|---|---:|---|
| H1R-P01-a / b / c / d | 0 / 1 / 254 / 255 | 成功；完整反射参数数、类型和顺序；0/1 做实际调用 |
| H1R-P02-a / b | 256 / 65535 | 生产 count 检查受控拒绝 |
| H1R-P03-a / b | 65536 / 65537 | 宽计数拒绝；不产生被截成 0/1 的公开 method |

| ID | 同一 declaring type 的 direct children | oracle |
|---|---:|---|
| H1R-N01-a / b / c / d | 0 / 1 / 65534 / 65535 | 成功；精确枚举数、首尾 identity、declaring 关系和重复查询 |
| H1R-N02-a / b | 65536 / 65537 | 受控拒绝；无 wrap、假新分组或公开半组 |

基础输入共 14。每个输入执行 `Ordinary-ON / Ordinary-OFF / Shadow-ON` × `CppDebug / CppRelease`，共 **84 基础 cells**；每 cell 独立进程。family/path/config 是执行分片，不是删减范围的开关。可分 12 张 family/path/config 验证卡，最终集合必须与完整 manifest 相等。

附加必需 variants：H1R-P04 包含合法 255 形参+return Param metadata、部分命名参数、实例方法及不同参数种类；H1R-N03 包含合法交错 declaring groups；H1R-N04 包含正常组邻接合法边界组/超限组；H1R-N05 包含最终 size cast 与重复反射。P04/N03/N04 在三路径、两配置的适用 cells 另计，不抵扣 84。任何 N/A 需证明不适用，不能因为难生成而取消。H1R-P05 为转换顺序/ABI/错误编号源审查。

## V2. 每个加载 cell 的共同证明

H1R-L01：exact fixture hash、独立 shape 读取结果、真实 build/library/source pairing、run ID、PID+启动时间/nonce。

H1R-L02：负例由实际生产计数检查拒绝，无成功返回新 assembly，无公开 image/type/method，无 Commit/initializer。修复后的等价更早 count guard 可接受；PE/ABI/无关格式拒绝为 NoCoverage；Crash/timeout/assertion abort 为失败，不计预期拒绝通过。

H1R-L03：明确分配时点。pre-reservation 失败不消耗；post-reservation 失败保留实际 ID/credits；whole-batch Shadow 预约按真实预算合同记账，不强求只增加一个 ID。

H1R-L04：此前有效 ordinary witness 的物理/逻辑 mapping 不变。Failed Shadow 状态只用受允许诊断检查；不要求非法 Abort 或继续业务，不据此宣称健康。合法 Abort 另用独立事务进程覆盖。

H1R-L05：分别记录 Development、C++ 配置、assertions、diagnostics、ON/OFF；至少真实 C++ Release 的 count 负例在 assertions disabled 时正确拒绝。Editor/Mono 不能替代 OFF IL2CPP。OFF ledger 观察按设计 D4，不以开启 Shadow 功能取得数据。

## V3. H1 既有能力回归

| ID | 规范关联/行为 | 必需证据 |
|---|---|---|
| H1R-R01 | Q03/Q04/Q05；共享 budget、retention、Abort、并发 | 真实 allocator/transaction tests，无超卖/退款/ID 重用 |
| H1R-R02 | Q07；AOT、sentinel、owner、跨页 raw 算术 | codec/MetadataUtil/GlobalMetadata 的对应实际源与 native 结果 |
| H1R-R03 | Q08/S04；private/active、publication、stale mapping | 并发/失败前后证据，GC/枚举不泄露 staged metadata |
| H1R-R04 | Q08；generic/array/reflection/attribute/lazy/dense | 原 61 checks 的 exact ID 或语义映射；两个 dense fixture 实跑 |
| H1R-R05 | B05；capability/profile/installed identity | immutable old Player 拒绝新要求，无发布/业务；builder-only 不替代 |
| H1R-R06 | startup/恢复 | 原 11 exact modes 新源运行；真实 phase/state/disposition |
| H1R-R07 | 资源/Unity/M07 | 原 14 exact modes；旧资源、alias、序列化、消息/API/cache、P04/P05/OFF |
| H1R-R08 | Editor/Python/native | 原 1021/492 用例语义覆盖+新增；正确 discovery、实际 compiler inputs、无零测试假通过 |
| H1R-R09 | R00/handoff | 四模式新候选功能；历史 48 timing cells 另由 M01 认证 |

精确 mode/case/operation 名从 fixed source 与认证 raw 提取。M00 先登记来源和 provisional set，M01/M02 完成后冻结正式 expected set；不得因一个来源缺项就缩小另一个的要求。总数只是历史声明和完整性报警值，不是覆盖证明。

## V4. Capacity 与内存

| ID | 要求 | oracle |
|---|---|---|
| H1R-C01 | Ordinary 8192 | 实际有效 DLL 8192 个、536870912 bytes、最大 33554432 bytes、真实 load/invoke/RVA |
| H1R-C02 | Ordinary 8191/8192/8193 | remaining 1/0，distinct 8193 拒绝；账本与既有 mapping 保持 |
| H1R-C03 | Mixed | 8184 ordinary successes + 5 Shadow + 3 retained ordinary failures = 8192；有效 DLL 8189 共 536870912 bytes，失败另 12 bytes |
| H1R-C04 | Mixed 边界 | 8191/8192/8193，同一既有 active world，不遗漏失败消耗 |
| H1R-C05 | 25% usable capacity free | free=524287−reservedPages；free≥131072；reserved 含未 mapped 和失败 credits |
| H1R-C06 | 实际 metadata、lazy/dense/FieldRVA | 独立 shape 审计、4095/4096 边界、高 RVA；padding 不等于 density |
| H1R-C07 | 时间/内存观测 | initial/current/peak RSS、managed bytes、采样 API/阶段；peak 与端到端耗时范围准确 |

余量在最后成功、拒绝及指定 post-rejection/lazy 查询后检查。区分查询合法 lazy binding 与拒绝本身的账本变化。原 reserved page 数不是新结果的硬编码期望。被选中且声明必需的 workload 失败须整改，不能静默缩小输入。

## V5. Evidence 与 performance

| IDs | 必需结果 |
|---|---|
| H1R-E01/E02 | 原 archive/index 实际 digest；成员集合、size/hash、路径/重复项完整性 |
| H1R-E03/E04 | source→install/generated→build→launch→raw 配对；不是只核 codec header/HEAD |
| H1R-E05/E06/E07 | 原 raw 重算；external/reuse/fresh 分类；冻结 status 与后继 review 正确解释 |
| H1R-T01/T02 | 同业务输入和 timed core；同设备/构建/启动语义；差异明确 |
| H1R-T03/T04 | 四模式各至少 10 对 fresh-process samples；原样本可重算，不择优删数据 |
| H1R-T05/T06 | first-observed/warm/readiness/RSS 语义准确；稳定退化/方差解释，不虚构 SLA |

闭环映射：B01→E01–E07；H02→P01–P05+L01–L05；H03→N01–N05+L01–L05；M04→T01–T06。R/C 是新候选 H1 回归条件，不因四项局部 finding 关闭而自动通过。

## V6. Row schema

每行记录 requirementId/testId、input hash、sourcePairing/buildReceipt hash、config/feature/Development/assertions、fresh/reused、run ID/PID/start、expected/observed、phase/publication/ledger、raw hash、状态。允许增加 IDs，不允许用总数相同掩盖替换或漏跑。
