# HybridCLR Assembly Shadow · M07 源码审查交付

日期：2026-09-07。此次交付替代先前“无法读取实现时”的初步设计评估，提供固定四仓库关键源码上的实际静态分析。**没有修改仓库，没有执行 Unity 编译/Player 测试，也没有重新校验原始证据归档全部成员。**

## 先读什么

| 文件 | 用途 |
|---|---|
| [review.md](review.md) | 13 项 findings，逐项区分已确认代码条件、设计/发布缺口和待验证风险 |
| [design.revised.md](design.revised.md) | 修订后的架构提案；仍为 PROPOSED，不是已实现能力 |
| [plans/README.md](plans/README.md) | M07R、M08–M12 与 X01 的顺序及 12 个详细阶段计划 |
| [plans/HUMAN_REVIEW_GATES.md](plans/HUMAN_REVIEW_GATES.md) | 后续开发强制执行的 5+1 人工完整 Review Gate；到 Gate 必须暂停，不能由 agent 自审替代 |
| [validation-matrix.md](validation-matrix.md) | 新增容量、性能、兼容、部署、恢复、平台和模块生命周期测试 |
| [evidence-map.md](evidence-map.md) | 42 个固定提交源文件/文档的实际阅读覆盖 |
| [source-baseline.json](source-baseline.json) | 四仓库 review HEAD、记录的 demo executable pairing 与验证边界 |
| [review-findings.json](review-findings.json) / [plan-index.json](plan-index.json) | 机器可读的问题与计划映射 |
| [analysis/source-algorithm-results.json](analysis/source-algorithm-results.json) | 本次执行的源码算法复算；不是 native/Player 测试 |

## 首要结论

保留已有 Stage/Validate/Commit、active mapping、Unity image 身份适配和已记录的资源 Gate。先解决 image 预算、分配热路径、native layout 与构建准入差异、物理 slot 混入逻辑方法键、跨版本并图伪环，再进入原 M08–M12。

当前源码分配器的小 DLL 理论上限是 338 个 Interpreter Image，而不是可自由使用 1024 个；普通热更也消耗同一预算。该值按 fresh allocator、同尺寸且每个 DLL <1 MiB 推导，不能直接作为项目剩余容量。

## 后续执行的人工 Review 规则

从 R00 开始，`plans/HUMAN_REVIEW_GATES.md` 是后续开发的规范性执行规则。本地 agent 可以在同一 Gate 区间内连续实施并执行阶段内 code review；一旦到达 H1–H5 暂停点，必须整理修改、测试和证据后停止，等待人为显式发起完整 Review。人工 Review 通过前不得进入下一 milestone。

M11 完成后同样必须停止；M12 作为“+1”最终独立 Release Review，只能由人为显式发起。阶段内 agent 自审、CI 或自动化验证均不能替代这些 Gate。

## 实际做过与没做过

已读取四仓库核心实现及后续契约；以源代码常量和算法独立复算容量/伪环；生成并校验本包交叉引用。

未完整 checkout 仓库、未运行它们的测试套件、未运行 Unity 或目标 Player。M07 14 模式、912 Editor/356 Python/824 focused native checks 是仓库记录的证据，不是本次执行结果。参考聊天全文未能读取；目标理解来自当前项目可见上下文和仓库设计/实施文档。

`delivery-checks.json` 只记录本包文档/算法交付检查。`SHA256SUMS.txt` 校验本包文件，不是对用户四仓库原始归档的重新签名或验证。
