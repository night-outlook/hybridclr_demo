# H1R/M05 — 测量准备、候选构建、实际 loader

状态 Pending。此页含不同工作阶段，但**必须按下表分卡执行**。历史 M01 尚有无关访问阻塞不妨碍新构建；本次执行自身所需 inputs 必须已核验，最终 H1 仍等待 M01。

## 分阶段任务

| ID | Phase | 单次范围 | 退出/产物 |
|---|---|---|---|
| M05.A-I | Inspect | R00 timed core、操作集合及 reference 接入差异 | comparability source map；停止 |
| M05.A-E-{component} | Implement | 一个必要共同测量/DTO/取样或 profile adapter 组件 | 无 R02 优化；停止 |
| M05.A-V/Q | Validate / IndependentReview（分卡） | 共同代码/输入/时序和 diagnostic 隔离 | 测量方法就绪；停止 |
| M05.B | Integrate | 两 count 修复+已审测量/测试源码的四仓库冻结 | candidate-source-freeze；停止 |
| M05.C-{role,config,feature} | Build | 一种构建配置；独占安装/生成目录 | install/build/native artifact 证明；停止 |
| M05.D-{family,path,config} | Validate | 一个 count family、一个 path、一个配置 | fresh-process 子集 raw；停止 |
| M05.E | Validate | 完整 84+variants result index | required set=executed set 的独立 verifier；停止 |
| M05.F | IndependentReview | count 验证与新 source/build/launch 绑定 | H02/H03 FixedAndLoaderValidated 或明确缺项；停止 |

Integrate/Build 是专门有界动作，任务卡准确写其 phase、权限和副作用，不与其它动作串成一个总命令。

## 1. 冻结前完成测量层

共同 timed core 源和 operation IDs、profile-specific 未计时接入提前确认；可严格复用则不新增代码。必要 Serializable/Preserve/输出 raw samples 修正在 freeze 前完成独立 review。reference overlay 放独立 workspace，旧 native 不改；不让 candidate M06 验证结束后才默认增加测量代码。

## 2. 源和权限

形成实际四 SHA pairing；不改的仓库保留原 SHA，变过的不能贴 clean old SHA。future implementation/local commit 以实际授权执行；未能合法形成 commit 时只能描述 base+diff/tree 的诊断 snapshot，正式四-SHA H1 交接保持阻塞。

隔离 ReviewedV6、R01 reference、candidate 的 file package、native 安装、Library 和生成路径。source freeze 后改 executable/generated/harness/flags 需要新 source/build 和受影响复验。metadata-only 后继用 diff 单独证明。

## 3. 最小构建角色

Count：C++ Debug ON/OFF；C++ Release ON/OFF，Release 的计数拒绝至少具备实际 assertions-disabled 证据。Functional：与原验收范围相同的 Development ON/OFF。Performance candidate/reference：Development=true、匹配 C++ Release 和协议条件。

角色不等于必须重复构建：来源、配置和输入完全一致的实际 build 可复用角色，但必须登记同一 artifact；不同配置不能只换标签。Development bool 不推导 C++ config/断言状态。必要 count diagnostic Player 在非 Development 中仍须 Preserve 并输出结果。

每 build 留 Unity/SDK/compiler、实际 argv/response files、优化/Strip/CodeGen、feature、Development、assertions/diagnostics、四仓库/installed/generated hashes、native library/metadata、buildGuid、input snapshot。不只核 codec header；必须核修复后的 InterpreterImage.cpp 真正安装并参与构建。

## 4. 真实加载

每 family/path/config 单批执行，case 每进程独立。完整矩阵 14×3×2=84，variants 另计；最终 E 只读聚合不能补写缺失结果。

合法 case 检查完整反射/分组。超限必须生产 count guard 拒绝，不能 public return/Commit/initializer；Crash、timeout、assertion abort 不合格。ledger 根据实际 reservation 时点处理；whole batch 不强求一 ID。Failed Shadow 只作许可诊断，合法 Abort 独立进程测试。OFF 观察不启用 Shadow，按设计 D4 审查。

## 5. 退出

candidate-source-freeze、installed-source proof、build matrix、全部 raw count results、matrix verifier 和独立 review。ABI 宽度、错误编号、codec/sentinel、active/retention 不变量保持。可声明 FixedAndLoaderValidated，但 H1 closure 尚待 M06/M08/M09。
