# M08A · 标准工作流与 Runtime/Toolchain 身份分离

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R03；需扩容时 R01B 已通过。关联 findings：ASR-007, ASR-012。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 修改面

复用现有 `AssemblyShadowBuildCommands`、`AssemblySnapshot`、`ShadowBaselineManifestBuilder`、`ShadowPatchManifestBuilder`、`ShadowSourcePins`、Settings、PinnedSourceInstaller 和 generation output。新增统一 coordinator/CLI 层，不新造平行 snapshot/hasher。

## 实施步骤

### 1. 从 demo 提取编排

盘点 M07Build/structural workflow 的 baseline resource、ON/OFF Player、P05 prepare/compile/restore、replay 功能。通用 API 不依赖 AssemblyA、M07 固定 bundle 名或测试 patch ID；demo 以输入配置调用通用流程。保留 exact-project Unity 锁和 finally 恢复逻辑。

### 2. 拆分来源与兼容身份

设计 RuntimeContractId、NativeCapabilityInventoryId、ToolchainProvenanceId、BuildEvidenceId。RuntimeContract 绑定 actual native/runtime ABI、encoding profile 和生成 ABI；工具源码 revision 完整记录在 provenance，但不自动等价为 native 不兼容。

### 3. Schema 迁移

保留旧 schema 的严格校验及已发布 baseline。新增 schema 必须显式适配；不把新工具写成旧 hybridclrUnity SHA。兼容矩阵精确声明哪些 tooling-only 更新可服务旧 runtime，负例覆盖 native/编码/bridge/API 变化。旧 Player 读到新能力需求必须清楚拒绝。

### 4. Build/Compile/Analyze/Publish 分层

一次 `CompilePlayerScripts` 形成不可变 target snapshot；closure DLL 从同一快照提取。CompileOnlyGeneration 仍明确 NotDeployable。只有通过 M08B 的发布准入后才能产生 deployable manifest。source changed during build、native generator 被覆盖、stripping 输入缺失都失败。

### 5. 路径与可移植性

运行时包只使用受限相对路径，不携带 `/Users/ah` 等历史根。工具证据保留原始来源另设可重定位内容索引；复制/解包后重新 hash。禁止 symlink/path traversal 和原地覆盖 immutable baseline。失败输出只位于本次 staging root。

### 6. 最小 developer 接口

Settings 明确模式、候选/Bootstrap、依赖声明、资源图、源 pin、输出和诊断级别。菜单与无 UI CLI 同一核心 API。禁止 ordinary HotUpdate 与 Shadow 配置重叠；验证 Player filter 保留 Shadow AOT baseline。

### 7. 验证

新建干净 demo 完成一次 baseline 与两个连续 patch；Editor-only 修复的兼容正例和 native ABI 改动的拒绝负例；中断/编译错误/设置恢复；源目录移动；生成输出覆盖；native feature OFF 普通 HybridCLR 回归。

## 退出条件

无需依赖 M07 硬编码 fixture 即可构建，来源真实、兼容规则可解释，旧契约未被静默放宽。该阶段只提供工作流，发布必须同时满足 M08B。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
