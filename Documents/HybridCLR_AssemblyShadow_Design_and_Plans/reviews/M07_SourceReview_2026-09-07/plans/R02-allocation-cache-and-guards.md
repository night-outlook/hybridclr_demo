# R02 · 分配证明缓存与执行 guard 性能分层

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R01；编码实现修改时在 R01B 后重验。关联 findings：ASR-002, ASR-003。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 修改面

主要为 `AssemblyShadowTypeResolver.cpp`、`AssemblyShadow.cpp`、`Object.cpp`、Array/boxing 相关入口和 execution diagnostics。建议新增 `AssemblyShadowAdmission` 以隔离策略/证书，保持上游 Hook 最小。

## 实施步骤

### 1. 先加可关闭的计数实验

分开记录 definition searches、TypeDef rows scanned、layout proof builds/cache hits、临时 native allocation、method guard/泛型上下文检查和观察锁竞争。原有 methodChecks 表示 guard 观察数，不是业务方法体实际执行次数；测试不得混用两者。

### 2. 完整物理类型证书

证书 key 为 active generation + 实际 Il2CppClass；构造泛型、数组等有独立身份。certificate 保存 baseline counterpart 或确认无 counterpart 的结果、准入域与 profile、已证明布局和失败原因。不得仅凭 type name 或 generic definition 重用布局证明。

### 3. 单次慢路径

把 `FindDefinition`、InstanceFieldLayouts、Interfaces 和 CheckLayout 放到首次 admission。元数据 TypeKey 索引建立/查找有确定作用域，不触发 baseline cctor、静态存储或业务代码。创建失败不得发布部分证书。新类型无 baseline 的结果也要缓存，否则仍每次线性查找。

### 4. 并发发布与锁序

保持 metadata/transaction/reflection/cache 的既有锁序。不要在持有 cache mutex 时递归进入 metadata resolver；不要对可变 unordered_map 做无锁并发读写。先实现证明正确的单次写入机制，再测 fast path；可接受 slow path 锁，不接受每次 new 的可竞争全局锁。

### 5. 正确性保护不缓存掉

cache hit 仍检查需要保留的实际 baseline 使用、poison 和执行上下文约束。参数带旧 baseline 值类型的 boxing、旧对象 clone、泛型包含 baseline 成分仍拒绝。禁止直接把 old Class 重新贴到 active certificate 下。

### 6. 诊断层级

支持 correctness-only、bounded counters、detailed development trace。生产高频诊断避免共享原子 cache-line 热点；超过 1024 class 观察时仍报告 dropped，而不是声称全类型证明。对仍可 Shadow 的 baseline 候选，不得为了无补丁速度提前关闭必要 usage 监测；冻结 baseline 选择需明确状态。

### 7. 稳态与冷启动测量

对单类 1/10/10000 次分配、跨 100/1000 类型、closed generic/array/boxing、virtual/interface/delegate 和多线程进行对照。区分 native OFF、ON/no Configure、ON/registered-no-patch、P01/P03。测 first allocation 和后续中位数，记录 native heap，不只看 managed GC。

## 退出条件

同一完整类型的布局证明只构建一次；后续分配不做全 image 扫描/签名临时分配；所有旧资源/早用/错误布局/方法 guard 负向仍通过。性能数据能解释收益与残留开销；达不到目标时不得把成本移到未计时阶段后宣称优化成功。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
