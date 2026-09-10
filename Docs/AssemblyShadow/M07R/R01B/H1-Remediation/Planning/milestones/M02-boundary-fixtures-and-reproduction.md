# H1R/M02 — 边界输入、独立 oracle 与原代码反例

状态 Pending；前置 M00；与 M01 无共享可变输出时可并行。此阶段不修改生产 native 计数逻辑。

## 有界任务

| ID | Phase | 一个目标/文件边界 | 验证与停止 |
|---|---|---|---|
| M02.A-{family} | Inspect | 参数或 nested 的实际加载入口及现有 fixture writer | fixed source/direct caller；路径报告后停止 |
| M02.B-{family} | Implement | 一个 family 的 generator/fixture 单元测试 | Proposed create-h1-count-fixtures 与相关 test；停止 |
| M02.C-I | Implement | 独立 shape auditor（不采用 generator 自报 count） | 仅 h1_count_fixture_audit 及测试；停止 |
| M02.C-V/Q | Validate / IndependentReview（分卡） | 实际 DLL count/结构/size/hash 检查 | 对 family manifest 审计后停止 |
| M02.D-{component} | Implement | 一次一个 probe、build adapter、launcher 或 result verifier | 对应 Proposed 文件及直接依赖；停止 |
| M02.E-{component} | Validate / IndependentReview（分卡） | 诊断保留、真实 loader、错误分类和 runner selector | 定向组件验证/review 后停止 |
| M02.F-{defect,config} | Validate | fixed ReviewedV6 上一个缺陷的代表 count 反例 | 有审计 manifest 的原代码 diagnostic build；停止 |
| M02.G | IndependentReview | 两类 fixture 与目标 guard 路径证据 | 确认正确 oracle/真实计数/原结果分类；停止 |

同一 generator/result 文件的 writer 串行。M02.C-V/Q、M02.E 的两个 phase 必须分成不同任务卡，不将斜杠当自动连续执行。

## 文件与输入合同

Proposed demo 文件：`Tools/AssemblyShadow/create-h1-count-fixtures.py`、`h1_count_fixture_audit.py`、`h1_count_results.py`、`run-h1-count-players.py`、`verify-h1-count-results.py`、对应 `tests/test_h1_*.py`；诊断 probe `Assets/AssemblyShadowR01BDiagnostics/Runtime/H1CountProbe.cs` 与必要 `Assets/AssemblyShadowDemo/Editor/H1CountDiagnosticBuild.cs`。每卡仅取当前组件，不一次编辑全列表。

参数 family：0/1/254/255/256/65535/65536/65537；另 255+return Param、部分命名、实例方法/不同参数类型。signature count 和 Param rows/sequence 分开读取。超限输入可用 metadata writer，不强迫 C# 表达巨型签名，不用 sequence 窄化或坏 PE 伪造反例。

nested family：0/1/65534/65535/65536/65537 个 siblings，不构造极深递归链。另合法交错 declaring types、正常组邻接边界/超限组、重复查询；真实 row 和 table sort 声明必须一致。

每 DLL ≤32 MiB，identity/MVID/AssemblyRef 合法，保存 seed/recipe/tool/source hash、实际 metadata counts、DLL size/hash。独立 auditor 从输入 bytes 读取，不能只比较两个 generator 字段。

## Probe 与原代码运行

每 cell fresh process；Shadow 一次 transaction。基线 candidate/target 身份必须有效，避免 Configure/early use/ABI 不匹配先失败。用已有正常 ordinary witness 保存稳定 mapping；负例不返回公开 assembly，不发布/初始化业务。Failed Shadow 只按许可诊断。

ReviewedV6 生产 native 源固定；新增 diagnostic harness 有独立 tree/diff/build 身份，不冒称完全未改的原 Player。对两个缺陷的 65536/65537 代表 inputs 分 Debug/Release 执行，记录 UnexpectedAccepted / AssertAbort / ControlledRejected / Crash / NoCoverage，不能预设结果。复现成功不是新候选验证通过；未复现继续查路径，不改 oracle。

OFF 不得通过开启 Shadow 来取 ledger；观察能力按设计 D4 独立建立并证明。diagnostic asmdef/.meta/Preserve/link 配置单独审查，不污染 production bootstrap。

## 退出

manifest、independent shape audit、pre-fix raw/launch/build、工具/fixture/probe 的定向 review 就绪。原代码反例不需通过修复后的 oracle；84+variants 的新候选验证属于 M05。
