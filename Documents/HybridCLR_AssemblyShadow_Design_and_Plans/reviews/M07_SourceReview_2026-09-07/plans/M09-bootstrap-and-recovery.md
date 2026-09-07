# M09 · 生产启动、签名、健康确认与分状态恢复

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M08B。关联 findings：ASR-008, ASR-011, ASR-013。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

实现真正的固定 AOT startup coordinator。M07Probe 是测试边界，不直接复制为生产下载器。所有安全输入/恢复决策都可故障注入，任何失败不加载混合代码/资源世界。

## 实施步骤

### 1. 输入与可信边界

嵌入 baseline build/runtime/capability 身份和验证公钥；对 manifest 大小/schema/重复字段/未知关键字段/路径作有界解析，再验证签名和文件 size/hash。使用项目已审核密码组件或经过 IL2CPP 平台验证的实现，不自造密码算法。私钥不进 Player。

### 2. 完整版本集合

A/B 或内容寻址 slot 中保存完整目标 closure、普通热更集合和资源/catalog。网络可下载差异，激活只能选择一个完整 ready 集合。禁止在 Commit 前注册业务资源或由 DI/SDK 提前反射业务类型。

### 3. 激活状态机

按准备、选择/验证、Stage/Validate、单次 publish、warmup、资源、入口、健康确认执行。配置候选身份早于可能访问业务的步骤；没有补丁时冻结 baseline 选择。API 结果同时记录 native state/active generation。

### 4. RecoveryDisposition

实现 R01 的表：Begin 前失败无需 Abort；Staging/Staged/Validated 中仅已知安全拒绝可 Abort 后 baseline；Failed 默认重启；FailedAfterCommit 不得原地 baseline。Abort 返回非 Success 时不能吞掉。用实际 state 而非方法名称推断是否已发布。

### 5. Poison 与异常捕获

协调器捕获错误后先标记 failed attempt，再停止业务入口/资源请求；受支持 native/Interpreter 业务入口保留 poison 约束。诊断和必要固定 AOT 退出逻辑可执行。reverse callback 使用不跨 ABI 抛异常的 fatal 路径。不能声称一个状态 enum 已经停止了所有线程。

### 6. 存储与崩溃恢复

临时写、校验、持久化、原子 pointer switch 和 install.complete 有清楚顺序。每个边界模拟断电/进程结束，下一进程忽略未完成 slot。LKG 同时选择其代码与资源；健康判据是定义好的业务 readiness，而非 Commit 成功。

### 7. 撤销与重放策略

定义已撤销 patch、旧 baseline、签名轮换、下载重试、容量/磁盘不足和离线策略。日志不泄露密钥。补丁输入在验真后保持受控不可变；Stage 期间调用者不得并发修改 byte[] 的契约写进 developer guide。

## 验收

对下载、签名、每个 Stage、Validate、publish 前后、module initializer、warmup、资源恢复、入口及健康写入逐点注入失败。每次检查新进程选择、slot 完整性、是否产生业务副作用和原生状态。错误路径可记录为正确拒绝，但不能用返回零的 harness 代替真正故障发生。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
