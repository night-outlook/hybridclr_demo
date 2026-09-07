# 后续执行计划总览

状态：提案，所有阶段均未在本次执行。主线保留原 M08–M12，前插 M07R 修复；不是把 M00–M07 全部重新做一遍。

## 执行顺序

```text
R00 基线/证据
 → R01 容量/失败契约
 → R01B 编码扩容（目标超出预算时必需）
 → R02 分配缓存/guard 分层
 → R03 布局/方法/图语义
 → M08A 标准工作流/版本契约
 → M08B 联合部署准入
 → M09 生产 Bootstrap/恢复
 → M10 平台/集成矩阵
 → M11 全面性能/fuzz/rebase
 → M12 发布验收

X01 程序集生命周期：R01/R03/M08B 后独立推进，
产品要求的能力必须进入 M10/M12，不能以 Replace 通过代替。
```

M10 runner/设备准备可与 M08 工作并行，但同一 Unity 工程的构建、安装、native source 变更和 source pins 集成必须串行。任何阶段失败不推进到后续正式 Gate。

## 阶段文件

| ID | 工作 | 前置 | 主要问题 |
|---|---|---|---|
| R00 | [固定基线、能力边界和证据账本](R00-baseline-proof-ledger.md) | 无；开始任何修复前 | ASR-012 |
| R01 | [Interpreter Image 预算与失败结果契约](R01-metadata-budget-and-failure-contract.md) | R00 | ASR-001, ASR-008, ASR-011 |
| R01B | [按实际规模扩展 metadata 索引容量](R01B-metadata-index-expansion.md) | R01；当目标规模超过现有 profile 时必需 | ASR-001 |
| R02 | [分配证明缓存与执行 guard 性能分层](R02-allocation-cache-and-guards.md) | R01；编码实现修改时在 R01B 后重验 | ASR-002, ASR-003 |
| R03 | [布局准入、逻辑成员身份与跨版本图修复](R03-evolution-semantics.md) | R01、R02 | ASR-004, ASR-005, ASR-006 |
| M08A | [标准工作流与 Runtime/Toolchain 身份分离](M08A-workflow-and-version-contracts.md) | R03；需扩容时 R01B 已通过 | ASR-007, ASR-012 |
| M08B | [部署补丁的联合准入与能力库存](M08B-deployment-admission.md) | M08A | ASR-001, ASR-004, ASR-009 |
| M09 | [生产启动、签名、健康确认与分状态恢复](M09-bootstrap-and-recovery.md) | M08B | ASR-008, ASR-011, ASR-013 |
| M10 | [平台扩展与受影响历史路径集成回归](M10-platform-and-integration.md) | M09；平台 runner 准备可在 M08 阶段并行 | ASR-011, ASR-012 |
| M11 | [全面性能、输入加固与上游升级演练](M11-performance-fuzz-rebase.md) | M10；基础容量/性能已在 M07R 完成 | ASR-003, ASR-013 |
| M12 | [发布候选与独立端到端验收](M12-release-acceptance.md) | M11；产品要求的 X01 Gate 已合入 | ASR-012 |
| X01 | [新增/删除程序集能力；与 Replace 分离](X01-assembly-lifecycle-capabilities.md) | R01、R03、M08B；独立 feature 分支，进入目标平台 M10 验收 | ASR-001, ASR-010 |

## 与原计划的关系

M00–M07：保留历史接受范围，按新改动的影响面重新验证。M08：复用已实现的工具类，将 deployment gate 串入标准入口；不重复发明 Settings/Hasher/Generation。M09：修正统一 pre-commit Abort 假设，并实现真正协调器。M10：平台和新旧功能集成。M11：不再承担第一次性能判断，保留完整压力与升级。M12：按明确支持合同发布。

## 通用执行纪律

每阶段包含代码、测试和独立 review，不把所有编译延到计划最后。native 修改同步真实安装来源，重建新的 baseline Player；历史 Player/资源/证据只读。若 CI/平台未运行，记录 NotRun，不由静态/模拟结果替代。

提议的回归结果目录可放 `Docs/AssemblyShadow/M07R/<阶段>/`，大型不可变产物以内容索引管理。证据需要完整来源，但不要求每个小变更复制所有历史多 GB 工作目录；共享内容以 hash 引用，避免无效文档/数据膨胀。

## 现有 M07 执行入口

以下来自固定版本 `Tools/AssemblyShadow/README.md`；尖括号值必须取本次新构建生成的路径，不复用报告中的历史绝对路径。

```powershell
pwsh Tools/AssemblyShadow/Invoke-M07Build.ps1 `
  -ProjectPath <absolute-isolated-demo> `
  -BaselineId <new-M07-Baseline-id> `
  -BuildTarget StandaloneOSX
```

```text
python3 Tools/AssemblyShadow/run-m07-players.py --project-root <isolated-demo> --fixture-manifest <m07-fixtures.json> --on-build <native-on-m07-player-build.json> --off-build <native-off-m07-player-build.json> --replay-receipt <m07-editor-replay.json> --output-root <new-results-root>
python3 Tools/AssemblyShadow/verify-m07-results.py --fixture-manifest <m07-fixtures.json> --result-dir <new-results-root/Results> --on-build <native-on-m07-player-build.json> --off-build <native-off-m07-player-build.json> --replay-receipt <m07-editor-replay.json> --output <new-verification.json>
```

当前这些命令的接受证据是 macOS；不得把命令中的 target 简单替换后视为 Windows/Android 已验证。新增平台适配由 M10 完成。
