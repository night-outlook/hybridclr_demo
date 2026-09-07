# R00 · 固定基线、能力边界和证据账本

状态：待执行。本文不表示代码已修改或测试已通过。

前置：无；开始任何修复前。关联 findings：ASR-012。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

建立可复现的修复起点，区分 review HEAD、可执行 source commit、pin-only commit 和 evidence commit。读取本报告未覆盖的相关 native Hook/测试全文，不能把定向阅读扩大成全仓无缺陷结论。

## 工作步骤

### 1. 固定四仓库与工程边界

在本地记录四个 HEAD、工作区修改、子模块/安装器输入、Unity 2022.3.62f2 的实际路径和模块。保留原分支及原 demo，不复用正在打开的 Unity 工程。建立专用集成工作树和唯一输出根。每次 native 修改后更新真正的 source pin，重新安装；不得只改 expected SHA。

### 2. 建立问题—代码—测试映射

导入 `review-findings.json`。为 ASR-001–013 各写最小确认任务，分成确定性算法、源码条件性行为、发布范围缺口和需真实运行的风险。尤其单独确认 slot 变化反例和纯托管布局例子，不将静态分析描述成已发生的 native crash。

### 3. 确定实际规模和支持范围

从本地 baseline/target snapshots 统计 candidate 数、DLL 大小分布、普通 interpreter image、最大直接/传递依赖及已发布补丁的累计 closure。列出目标平台、Development/Release、是否要求新增程序集和 AddUnityTypes。若没有生产规模数据，先记录 100/300/1000 个小程序集压力档位为测试要求，而非支持声明。

### 4. 重建证据索引

保留已有 M07 `strict-gate-3b`、Player/build/安装/source receipts。建立 ClaimId、代码 SHA、配置、输入 hash、native library hash、测试平台、结果和重放命令的 ledger。标明 MonoScript 直接调用与 fallback 标签，Addressables/delayed catalog 的实际覆盖不同。

### 5. 先做未修复基线

运行现有 Editor/Python/native 定向 suite，记录本次实际计数，不机械期望永远等于 912/356/824。以当前 M07 配对跑 14 模式；对后续会触及的 allocation、Runtime::Invoke、reflection、泛型执行路径补跑相关 M05/M06 Player 用例。负向故障必须由真实错误输入触发，不以手写 JSON 代替。

已存在的 Python 入口，在 demo 根执行：

```text
python3 -m unittest discover -s Tools/AssemblyShadow/tests -v
python3 Tools/AssemblyShadow/verify-installed-runtime.py --expect-shadow on
```

现有 native runners 为 `run-m03-native-tests.py`、`run-m03-visibility-tests.py`、`run-m04-native-tests.py`、`run-m05-native-tests.py`、`run-m06-native-tests.py`。其平台参数及安装根按本地脚本帮助选择，不套用历史 `/Users/ah/...`。

### 6. 冻结初始性能

在未修复版本记录 ON/no patch、P01、P03 的 allocation/Invoke/泛型微基准和启动到业务 readiness。保存至少一个 10000 次重复 new 的计数实验，并区分 first-call、warm steady state 和 native diagnostics 模式。

## 退出条件

四仓库、安装的实际 runtime、生成代码、Player 和证据之间没有未解释的不一致；所有新增 finding 有确认/复现负责人和判据；未执行平台明确排队；容量是否触发 R01B 已有数据或显式压力要求。不能以原报告“已接受”代替本次 baseline 记录。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
