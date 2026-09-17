# R01 · Interpreter Image 预算与失败结果契约

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R00。关联 findings：ASR-001, ASR-008, ASR-011。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 修改面

`hybridclr/metadata/MetadataUtil.h`、`InterpreterImage.cpp`、`StagedAssembly.cpp`；`il2cpp_plus/vm/AssemblyShadow.cpp`；managed runtime API/DTO；Editor Build/Validation。建议新增 `InterpreterImageBudget` 和 `MetadataCapacityReport`，不要复制多份互不一致的分配算法。

## 实施步骤

### 1. 从现有分配器提取可验证的预算逻辑

把 size→kind、fallback 顺序、保留槽和单调 cursor 的纯计算与实际提交分离。生产分配和 dry-run 共用规则，保持旧编码不变。输入包含当前四桶 cursor、DLL 精确字节数序列，输出每个分配、剩余预算和首个失败原因。

### 2. 固定边界测试

测试 1 MiB、4 MiB、16 MiB、64 MiB 的前一字节/恰好边界，fresh homogeneous 容量 338/83/19/3，以及 mixed sizes、顺序变化、普通 load 先占用、失败后不归还。使用真实生产 helper 的 native 测试，不把本包 Python 模型计入 native 通过数。

### 3. 构建期容量准入

在 closure 完整且真实 DLL 已知后运行预算。baseline 记录 ordinary interpreter 需求和编码 profile；patch 报告 required/available/firstFailingAssembly。输出必须区分总候选 AOT 数与实际 interpreter image 数。超限在发布目录产生前失败，不能 Stage 到一半才发现。

### 4. 原生最终校验及并发边界

Editor 估算不能替代实际 cursor。最终预算检查和分配预留必须在正确 metadata 锁序下执行。明确 activation window 中普通 Assembly.Load 的规则：禁止不受控注册，或纳入中央 reservation；否则预检查与实际分配间仍会被其他 load 消耗预算。预留失败不允许重置既有 cursor。

### 5. 恢复结果规范化

盘点所有 error→state 路径，包括 ParseIdentity 可纠正拒绝、skeleton 部分分配失败、Validate metadata 失败、usage rejection、发布后初始化异常。写出 RecoveryDisposition 表和测试，纠正 `Failed` 不能 Abort 的计划假设。未知 native failure 默认 RestartRequired。

### 6. 明确 pre-Configure 监测边界

在基线生成嵌入的候选 identity 清单，调查最早安全注册点；先建立 Configure 前的 Type、object、cctor、native script-resolution 负向实验。若只靠构建 startup policy，必须有明确证据范围，不能把空 usage counter 当作整个启动期无使用。

### 7. 接入诊断但保持 ABI 诚实

新增 capability/budget API 或 diagnostic schema 时显式版本化，保留旧 enum 数值。同步 native registration、managed 声明、DTO、link preservation、verifier 和 OFF 路径。旧 Player 不支持时返回明确能力不足，不读取伪造的预算。

## 验收与失败处理

native helper 的全部边界通过；至少一项真实多程序集 Player 实验验证预算拦截发生于发布前；ordinary/Shadow 共享消耗一致；错误状态与 Abort/恢复处置严格匹配。若最大目标闭包超限，将 R01B 升为必需前置，不能以“已有报错提示”关闭 ASR-001。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
