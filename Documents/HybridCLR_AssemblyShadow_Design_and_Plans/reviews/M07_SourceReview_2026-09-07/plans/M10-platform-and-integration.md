# M10 · 平台扩展与受影响历史路径集成回归

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M09；平台 runner 准备可在 M08 阶段并行。关联 findings：ASR-011, ASR-012。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

将 macOS ARM64 已有证据扩展为目标平台证据，并把新 native 变更影响到的 M03–M07 路径重新放到同一可执行版本上验证。不是简单复制原 JSON 到新平台标签。

## 实施步骤

### 1. 精确平台清单

优先 Windows x64 与 Android ARM64，持续保留 Unity 2022.3.62f2 macOS ARM64。iOS、WebGL 和其他 Unity 小版本单独 Gate，不由前两者推导。明确 Player stripping、Development/Release、PDB/无 PDB、线程和运行资源模式。

### 2. 真正构建和部署

每个平台构建真实 ON/OFF Player，绑定 managed/compiler/generator/native library/metadata/resource 输入。Android 使用实际设备安装/拉起/日志/结果获取流程和不同 OS 进程；Windows 不复用 macOS 原生结果。应用完整目录在测试前后校验。

### 3. 功能矩阵

复跑 M07 的 P01/P02/P03/P04/P05 与资源结构拒绝；补充本报告的容量、普通托管布局、slot、方向反转、状态恢复和 generator coverage。对变化触及的 M03 transaction、M05 reflection、M06 dispatch/generic/exception 再做 current-pairing Player 回归。

### 4. 启动污染与第三方库

验证 SDK startup callbacks、preloaded assets、Resources、ProjectSettings 引用、native plugin/MonoScript 缓存和显式支持的 Addressables 版本。pre-Configure 使用负例必须在声称的层面被阻止。没有验证的集成保持 NotSupported/NotRun，不用 delayed catalog 样本代表全部 Addressables。

### 5. 真实复杂业务样本

接入一个包含继承、静态初始化、实例引用、接口/delegate、泛型、异常、async/iterator 和旧资源的模块切片。编译多个连续版本，记录 closure 膨胀与解释比例。不把测试专用的字符串 marker 正确当成全部类型/资源证明。

### 6. 证据标准化

每项 claim 记录直接 API/fallback/明确不支持。实际对象类型的物理 image、执行来源、序列化值和旧 bundle hash 独立断言。重复、丢失、过期结果文件以及重复进程结果一律拒绝。

## 退出条件

必需平台/配置矩阵全绿，无 relevant skips；新的 executable pairing 的整体回归成立；X01 在产品范围内时对应能力已进入本矩阵；任何平台缺失均显式阻断该平台发布，而不否定已完成平台的有限 Gate。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
