# Canonical Source Basis

This file records the sources merged into the sole active plan package. Historical GitHub links intentionally retain their original committed paths.

# 来源、权威顺序与本版新增约定

## 1. 权威顺序

用户目标和1A+2A决策、规范H1/design/validation约束优先；固定源码与原review用于定位问题；用户 planning notes 用于组织执行。不得以减少上下文为由改验收范围、隐瞒真实目的或省掉全链路审查。

## 2. 规范和固定源码

以下均固定到原 reviewed commits，不以提交本计划后的 branch HEAD 冒充旧执行来源。

- [HUMAN_REVIEW_GATES.md](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md#L12-L94)：完整review、版本绑定和人工H1。此次通过GitHub只读核对。
- [修订设计](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/design.revised.md)、[R01B规范计划](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01B-metadata-index-expansion.md)、[验证矩阵](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md)：原计划/前序review已提供内容，本版没有重新进行全部源码review。
- [原R01B执行边界](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/R01B-execution-plan.md)：声明规模；一次transaction按用户已明确范围解释。
- [参数路径](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L1725-L1825)、[nested路径](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L2045-L2090)、[native字段](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/GlobalMetadataFileInternals.h#L50-L180)：原review的H02/H03来源。
- [codec](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexCodec.h)、[runtime adapter](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp)、[transaction](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/AssemblyShadow.cpp)：容量/生命周期/可见性来源，具体实施前仍需查看直接调用者。
- [capability negotiation](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Runtime/AssemblyShadow/AssemblyShadowDiagnostics.cs#L85-L148)、[profile builder](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Editor/AssemblyShadow/Build/MetadataCapacityPlanner.cs#L92-L140)：managed/native配对及OFF范围。
- [R00 runner](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Tools/AssemblyShadow/run-r00-players.py)、[performance probe](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs)、[index-runtime runner](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Tools/AssemblyShadow/run-r01b-index-runtime-tests.py)：旧计划已核对的入口；本地派发前仍需绑定实际parser/source。
- [原证据索引](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/Evidence/evidence-v6-index.json)、[原acceptance matrix](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/runtime-acceptance-matrix.md)、[final review](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/R01B-final-stage-review.json)：待认证历史输入，不是本版已完成的验证。

## 3. 输入附件

本版逐份优化原 `H1_R01B_Remediation_Plan_1A_2A.zip` 的规划内容；[原独立review](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/references/H1_R01B_Independent_Review.md)、[原status](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/references/H1_R01B_Review_Status.json)、[用户planning notes](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/references/AGENT_PLANNING_SAFETY_NOTES.md)作为不改字节的参考副本保存。副本中的历史“未写仓库/未测试”只描述原review，不描述本次文档提交。原review的可延期建议已由用户1A+2A进一步收紧。

`input-artifact-hashes.json` 记录实际输入字节hash。notes只交协调者/任务编排审查，不自动成为每个执行者必读上下文。

## 4. 官方说明与作者笔记的区别

已核对 [OpenAI官方说明](https://help.openai.com/en/articles/20001326-additional-safety-checks-for-biological-and-cybersecurity-requests-in-chatgpt-codex-and-the-api)：允许的请求可缩小范围，仅保留必要上下文；措辞变化不改变允许性，也不保证交付；持续问题可反馈/联系支持并提供必要脱敏信息。

官方说明不证明某份历史上下文已经“污染”，也不提供关键词删除保证。本版采用笔记的工程拆分规则，不以规避检查为目标；保留真实Patch/Stage/Abort/API名称和必要失败语义。实际拒绝按服务支持流程处理。

## 5. 本版组织约定

任务卡、分片IDs、共享资源单writer和独立全链路复核是执行组织；84基础cells、附加variants、每模式10配对和4模式来自原已交付计划，继续保留，不冒称全部由规范逐字要求。

解除无关历史审计对独立新测试的调度阻塞，不解除原认证的最终H1条件或每次运行实际输入就绪性。source freeze前准备测量层，OFF只读诊断、等价更早生产count拒绝是正确性澄清，不是扩大runtime功能。

本次只生成/检查并提交计划文档，没有进行新的runtime修复、项目测试、archive认证或H1放行。


---

# HybridCLR Assembly Shadow · M07 源码审查交付

日期：2026-09-07。此次交付替代先前“无法读取实现时”的初步设计评估，提供固定四仓库关键源码上的实际静态分析。**没有修改仓库，没有执行 Unity 编译/Player 测试，也没有重新校验原始证据归档全部成员。**

## 先读什么

| 文件 | 用途 |
|---|---|
| [review.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/review.md) | 13 项 findings，逐项区分已确认代码条件、设计/发布缺口和待验证风险 |
| [design.revised.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/design.revised.md) | 修订后的架构提案；仍为 PROPOSED，不是已实现能力 |
| [plans/README.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/README.md) | M07R、M08–M12 与 X01 的顺序及 12 个详细阶段计划 |
| [plans/HUMAN_REVIEW_GATES.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md) | 后续开发强制执行的 5+1 人工完整 Review Gate；到 Gate 必须暂停，不能由 agent 自审替代 |
| [validation-matrix.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md) | 新增容量、性能、兼容、部署、恢复、平台和模块生命周期测试 |
| [evidence-map.md](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/evidence-map.md) | 42 个固定提交源文件/文档的实际阅读覆盖 |
| [source-baseline.json](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/source-baseline.json) | 四仓库 review HEAD、记录的 demo executable pairing 与验证边界 |
| [review-findings.json](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/review-findings.json) / [plan-index.json](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plan-index.json) | 机器可读的问题与计划映射 |
| [analysis/source-algorithm-results.json](https://github.com/night-outlook/hybridclr_demo/blob/7cb710fa38464b1977a69619fea2b5fc93f79966/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/analysis/source-algorithm-results.json) | 本次执行的源码算法复算；不是 native/Player 测试 |

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
