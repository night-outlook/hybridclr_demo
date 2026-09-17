# M08B · 部署补丁的联合准入与能力库存

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M08A。关联 findings：ASR-001, ASR-004, ASR-009。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 修改面

`ShadowManifests`、Baseline/Patch builders、`ShadowGenerationOutput.RequireCoverage`、`GenerationInventory`、RuntimeGeneration 输入、resource receipt；新增可部署 admission report。统一使用 R01 quota 和 R03 layout 结果。

## 实施步骤

### 1. 冻结安装包已有能力

将真正编入 native Player 的 managed-to-native/native-to-managed bridge、adjust thunk、struct mapping、reverse callback capacity 和已允许 feature 集合写入 baseline inventory，并绑定 native library/build GUID。不能用未安装的 generation plan 代替。

### 2. 每个补丁计算需求

基于完整 target closure 和普通热更运行集合生成 demand inventory。分别标记需要 native 预编译、可由受支持 supplemental metadata 满足、或明确不支持的需求。calli/native pointer 边界不能因生成器有输出字段就被默认允许。

### 3. 强制 coverage

在可部署输出前调用已有 structural ABI/capacity coverage，包含 struct key mapping。相同逻辑 type 名但物理 ABI 改变不能通过；生成新 C++ 文件不增加旧安装包能力。缺口返回 required/provided/受影响 DLL/修复方式，不执行部分 publish。

### 4. 联合 admission

发布条件同时包括：exact baseline/runtime contract；完整累积 closure；target load order；Bootstrap/隐式依赖政策；native layout；metadata index/总字节预算；native capability；资源/catalog 一致；完整文件 hash。所有结果引用同一 target snapshot，不能拼接不同源码状态。

### 5. 资源原子性

DLL-only 必须所有要求均成立。重建资源模式要求 affected bundle 完整、code/resource generation 配对、旧不变 bundle hash 仍相同。不能仅把 `resourceBundlesRequired` 写到 JSON 就视为资源已经存在且可部署。

### 6. 不依赖作者调用栈的重开验证

在新验证进程中读取最终包，重新校验每个文件/清单/报告身份与关系。产出 deployable receipt；未完成的临时目录没有有效 ready 标记。签名由 M09 接入，但 unsigned 样本必须明确不用于发行。

## 回归用例

资源 ABI 相同但新增 struct/native signature；reverse callback 容量不足；缺少目标 generic metadata；索引预算超限；非序列化 native 布局变化；v1→v2 漏带 A1；缺少重建资源；wrong native inventory；ordinary filter 误删候选。所有负例在部署包发布前拒绝，已有 P01–P05 正例通过。

## 退出条件

不存在绕过联合 admission 的公开 deployable builder 路径；能力与安装包真实字节绑定；发布目录没有半套 closure 或混合资源版本。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
