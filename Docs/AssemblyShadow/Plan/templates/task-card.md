# 单任务卡（派发前填写；本文件不是可直接执行的任务）

Task ID：
Phase：Inspect / Plan / Implement / Integrate / Build / Validate / Package / Document / IndependentReview（只选一个实际阶段）
Goal：一个可观察的行为或正确性结论。
Prerequisites：已完成的相关任务、证据/命令登记 ID。
Repository：实际 canonical root、branch/commit；必要时注明 dirty/tree 身份。
Read scope：exact files/symbols 和直接调用者。
Write scope：exact allowlist，或明确 read-only；输出目录单列。
Essential context：本任务需要的合同条款、输入 hashes、expected state；不粘贴全计划/全历史。
Action：本阶段的有界动作。
Validation command：完整 argv、cwd、env；一个验证入口；未实现/未解析时不得派发运行。
Expected result：稳定 case IDs、数值/状态、失败边界；验证子集不得声明全矩阵。
Evidence output：新的输出路径、raw/报告格式。
Stop：完成该命令及报告后返回协调者；不自续、不启动下阶段、不自行实施 review finding。
Remaining gate：当前后续审查点；humanGatePassed=false，mayEnterR02=false。

每次报告实际文件、命令、版本、expected/observed、raw 定位、未运行项和阻塞。实现与正式验证分任务；整体 H1 审查不被本卡替代。
