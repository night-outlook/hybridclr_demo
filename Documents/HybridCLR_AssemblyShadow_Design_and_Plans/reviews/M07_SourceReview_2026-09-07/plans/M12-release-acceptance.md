# M12 · 发布候选与独立端到端验收

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M11；产品要求的 X01 Gate 已合入。关联 findings：ASR-012。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 实施步骤

### 1. 冻结支持合同

列出 exact Unity/平台/架构、布局准入域、assembly operations、native capacity、interop/Burst/reflection 限制和资源变化政策。明确不能由 DLL-only 改变的安装包能力。未验证路径不是默认支持。

### 2. 干净构建

从四仓库固定版本和真实工具链重新安装 runtime、编译、生成、构建 baseline Player 和两代 cumulative patches。验证源码、native library、metadata、完整 app-tree、code/resources、signed manifest 与验证结果一致。不得利用历史可写目录补齐缺失证据。

### 3. 独立验证

独立 reviewer 先检查 design/plan 是否覆盖原目标，再看代码和真实反例，最后重放 required acceptance。单独记录人/模型审查、确定性 verifier、真实 Player 执行，不能把 detached-worktree verifier 自动称为独立人工审查。

### 4. 发布/回滚演练

全新安装、已有 LKG、离线、磁盘不足、候选被撤销、post-commit failure、恢复后再次正常启动、错误资源组合和签名轮换均验证。不能把修改业务状态的补丁回滚问题简化为仅删除 DLL。

### 5. 生产试运行准入

以可控范围启用，监控启动失败率、readiness 时间、native crash、closure 大小和 image quota。保留完整 code/resource LKG。试运行失败停用对应能力/平台，重新生成新版本证据，不覆盖既有记录。

## 最终交付

正式设计、developer guide、支持矩阵、容量/性能预算、schema/API、四仓库 source manifest、可复现 baseline/patch 工具、签名/恢复手册、原始测试证据和升级/回滚操作说明。

## 退出条件

所有必需 Gate 均对应当前可执行版本；无未关闭 P1；真实项目收益达标；超限项目已完成编码扩容；动态新增在目标范围内时 X-Managed/X-Unity/X-Remove 的相应项均有独立证据。仅完成 Replace-only 时只能发布明确受限的 Replace 产品，不宣称完整模块生命周期支持。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
