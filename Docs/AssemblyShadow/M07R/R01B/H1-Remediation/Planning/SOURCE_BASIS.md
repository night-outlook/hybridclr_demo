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

本版逐份优化原 `H1_R01B_Remediation_Plan_1A_2A.zip` 的规划内容；[原独立review](references/H1_R01B_Independent_Review.md)、[原status](references/H1_R01B_Review_Status.json)、[用户planning notes](references/AGENT_PLANNING_SAFETY_NOTES.md)作为不改字节的参考副本保存。副本中的历史“未写仓库/未测试”只描述原review，不描述本次文档提交。原review的可延期建议已由用户1A+2A进一步收紧。

`input-artifact-hashes.json` 记录实际输入字节hash。notes只交协调者/任务编排审查，不自动成为每个执行者必读上下文。

## 4. 官方说明与作者笔记的区别

已核对 [OpenAI官方说明](https://help.openai.com/en/articles/20001326-additional-safety-checks-for-biological-and-cybersecurity-requests-in-chatgpt-codex-and-the-api)：允许的请求可缩小范围，仅保留必要上下文；措辞变化不改变允许性，也不保证交付；持续问题可反馈/联系支持并提供必要脱敏信息。

官方说明不证明某份历史上下文已经“污染”，也不提供关键词删除保证。本版采用笔记的工程拆分规则，不以规避检查为目标；保留真实Patch/Stage/Abort/API名称和必要失败语义。实际拒绝按服务支持流程处理。

## 5. 本版组织约定

任务卡、分片IDs、共享资源单writer和独立全链路复核是执行组织；84基础cells、附加variants、每模式10配对和4模式来自原已交付计划，继续保留，不冒称全部由规范逐字要求。

解除无关历史审计对独立新测试的调度阻塞，不解除原认证的最终H1条件或每次运行实际输入就绪性。source freeze前准备测量层，OFF只读诊断、等价更早生产count拒绝是正确性澄清，不是扩大runtime功能。

本次只生成/检查并提交计划文档，没有进行新的runtime修复、项目测试、archive认证或H1放行。
