# H1 整改设计增补

版本 2.0；设计/验证规格，非实现完成声明。依据见 [SOURCE_BASIS.md](SOURCE_BASIS.md)。

## D1. 固定不变量

保持 profile 2：signed int32；AOT 非负 raw 域；`-1` sentinel；4096 values/page；8192 lifetime identities；524287 usable pages；393215 charged-page ceiling；至少 131072 free pages。保持 native metadata 字段宽度、错误码编号、一次 Shadow transaction、私有构造、单一 active publication、既有对象/class 指针不变。

ordinary、Shadow 和已提交 reservation 后的失败共享进程终身账本；Abort 不退款、不复用 ID、不允许第二事务。reservation 前失败不消耗；reservation 后失败保留。Failed/FailedAfterCommit 不因异常被 catch 就恢复健康，按实际 recovery disposition 检查。

目标输入：ordinary 8192 有效 DLL 共 536870912 bytes；mixed 8184 ordinary + 5 Shadow + 3 retained failures，8189 有效 DLL 共 536870912 bytes，另 12 failed-input bytes；最大有效 DLL 33554432 bytes。mixed 不声明 64 KiB 有效 DLL 均值。输入字节不代表 metadata RAM 或任意形状容量保证。

## D2. 参数计数修复

目标：`hybridclr/metadata/InterpreterImage.cpp::InitMethodDefs` 及必要的直接签名读取路径。先检查实际宽计数/长度差，再与 255 比较，最后赋给窄字段。不得先 cast 再比较，诊断输出真实 count。允许在生产签名解析路径中更早拒绝已解码的超限 count，不要求先构造巨大的参数向量。

区分 signature 形参数、Param 表行数与最终 `md.parameterCount`。255 形参加 sequence=0 的返回元数据仍可合法；部分命名、实例方法及不同参数种类保持原语义。检查 early temporary count、actual/named start 和 sequence 是否已提前窄化；必要的结构范围检查只覆盖直接相关路径，不开展全面 parser 重构。

默认沿用既有超限拒绝错误域，不加宽 ABI、改 profile 或生成额外桥接能力。0/1 等小方法实际调用；254/255 验证完整反射参数，不要求 Invoke 不受支持的巨型签名。

## D3. Nested count 修复

目标：`InterpreterImage.cpp::InitNestedClass`。优先最小 pre-increment guard：现有 direct-child count 达 65535 后，在递增前拒绝下一项；最终 vector size 写回 native 字段前也作运行时检查。不得依赖 Debug assertion，不得让 wrap=0 重启分组或覆盖 nestedTypesStart。

核对 nested/enclosing rows 和临时 group index→最终 raw start 的直接前提；合法 sibling group、多个 declaring types 的合法交错行、正常组邻接边界组及重复查询保持正确。65535 是兄弟数量，不是嵌套深度。

部分 private 构造失败可保留对象和预约，但不能公开 image/type/method，不退款或伪造 baseline 可继续状态。

## D4. 实际验证路径

helper/codec 算术测试、真实 native loader、IL2CPP Player 是不同证明。opaque-pointer/TLS-stub harness 不等于实际 InterpreterImage 构造。最终 count 矩阵使用真实 DLL，走 ordinary ON、ordinary OFF、Shadow ON，各在真实 C++ Debug/Release 配置执行。

开发过程保留 original line 的来源定位，但不把行号当 oracle：在等价或更早的生产 count guard 拒绝，只要证明已读取该 fixture 的真实计数并按正确状态处置，可满足要求；PE、身份、ABI 或无关格式错误提前退出是 NoCoverage。

OFF 的 Shadow API/capability 不应被开启来取统计。若现有 OFF 诊断不足，单独设计并审查只读 diagnostic-only 观察入口，读取相同真实 allocator，不替换加载逻辑、不改变 feature flag、不加入 timed benchmark；否则该观察项保持缺证据，不能编造值。

## D5. 身份和冻结

ReviewedV6 永久只读。RemediationCandidate 包含两个修复及已审查的必要 fixture/probe/measurement 源。R01PerformanceReference 固定旧 R01 native sources，必要测量 overlay 单列完整 diff/hash，不能冒充原 immutable old Player。

四仓库 pairing 必须完整；无必要改动的仓库沿用真实 SHA，不为凑数修改。source freeze 前完成候选测量层接入及测试保留配置，之后产生 build/launch/raw 身份。更改 executable/generated/相关 harness/flags 必须新冻结并复验受影响项。metadata-only commit 可关联先前 executable，须提供实际 diff。

## D6. 性能与证据

2A 对照比较真实 R01→修复候选的已列明整体差异，不自动归因于 codec。相同共同负载、timed core、计时边界、设备和构建条件；profile-specific 未计时接入及 ABI/manifest 身份保持各自真实。8k 压力仅用于候选容量验收。

[性能协议](PERFORMANCE_PROTOCOL.md) 不设未经批准的性能/RAM SLA；[证据合同](EVIDENCE_CONTRACT.md) 区分历史审计、当前新运行和可审计复用。两个已选修复与受控对照都不可默认延期。

## D7. 全链路审查

任务拆小不改变 M08 的设计→计划→四仓库实现→source/build/launch→raw→声明边界审查。ReadyForHumanH1 不代表 Passed；M09 只在用户明确通过后准备 R02 交接，不自动实施 R02。
