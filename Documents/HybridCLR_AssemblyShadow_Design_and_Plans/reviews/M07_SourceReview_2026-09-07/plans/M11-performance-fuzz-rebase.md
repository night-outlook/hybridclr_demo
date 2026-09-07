# M11 · 全面性能、输入加固与上游升级演练

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M10；基础容量/性能已在 M07R 完成。关联 findings：ASR-003, ASR-013。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

把 M07R 已验证的快路径扩展成项目级收益与可维护性证据。此处才做完整长期加固，不把第一次收益判断拖到本阶段。

## 实施步骤

### 1. 端到端预算

复用 R00/R02 对照，记录读取、验证、Stage、metadata、publish、initializer、warmup、first resource、first new 与 BusinessReady。明确进程冷、文件缓存冷、设备温度/频率状态。样本数不足不报告稳定 P99；统计脚本保留原始样本。

### 2. 累积版本与规模

用实际 DLL 分布和最大 closure 压力，测补丁从少量 Internal 变化到 Contracts 大闭包时的时间、内存和 interpreter 比例。测试 1024 class observation 以上规模，防止以有限 diagnostics 证明全覆盖。metadata capacity 准入与运行占用一致。

### 3. Native/managed 内存

分别记录 DLL/PDB retained bytes、metadata/cache/native allocations、managed heap 和进程 RSS/峰值。Abort 后保留是明确生命周期成本，不把它当作已释放；warmup 不能把峰值移出计时区间。闭合泛型证书增长有上限或可解释预算。

### 4. Parser/资源包加固

对合法 DLL/PDB 系统变异 PE、stream、table、heap index、coded index、signature、method body/EH、递归深度和超大计数。使用 ASan/UBSan 等适合目标工具链的原生 harness；分别测试 Stage/Validate/Abort 和普通 load。签名验证不能作为跳过格式验证的理由。

### 5. 并发与故障注入

并行 metadata/reflection/diagnostics、分配证书建立、ordinary load 与预算预留，覆盖每个 publication/失败边界。不能存在死锁、半快照、staged 可见、误用缓存或静默继续旧 AOT 方法。

### 6. 上游演练

选择明确的 HybridCLR/il2cpp_plus 上游 revision，在独立分支升级并记录冲突、Hook 变化、编码 ABI 和 generator 变化。重新安装、构建新 Player、跑受影响/最终矩阵；不能只做编译或 cherry-pick 成功就宣称支持新 Unity 版本。

## 退出条件

达到先前冻结的项目预算，没有无法解释的 crash/死锁；native correctness-only 模式收益成立；parser negatives 真正拒绝且不越界；升级手册能由干净工作树重现。任何阈值调整必须有数据和 review，不能在失败后临时放宽。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
