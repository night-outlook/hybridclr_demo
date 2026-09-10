# 证据合同：原包审计、新候选、性能 reference

## E1. 三条证据链

ReviewedV6ArchiveAudit 认证原记录；RemediationCandidate 证明修复后行为；R01PerformanceReference 与 candidate 构成受控对照。它们的源码、构建、运行日期和范围分别记录，不能相互重新贴标签。

原 reviewed commit：9534c7c775d69b79ecd612917231bef3d202a5aa。原 Evidence 目录位于 `Docs/AssemblyShadow/M07R/R01B/Evidence/`。

```text
r01b-v6-evidence.tar.gz
SHA-256 d50193ad9e5ebe93998b6d5d412d32696a57925f4b05b55de91027011f0bd0d9
evidence-v6-index.json
SHA-256 e82126f75efb96a83b51caa3c2d2b1cdbedb2b34ca2351c8871cfb3cf3711606
```

86,092,066 archive bytes、329 files、200 unique source paths/201 range entries 是待独立重算的原声明，不以字符串相等作为证明。原 archive/index 不重新生成；错下载先识别 HTML/LFS pointer/截断对象，真 mismatch 保留并报告，不修改 expected hash。

## E2. 分层证明

| 层 | 实际检查 | 不可推出 |
|---|---|---|
| Bytes/Members | 实际 digest、集合、每 size/hash、无歧义引用 | 测试逻辑自动正确 |
| Source | fixed commit bytes、installed/generated transitive inputs | 仅 HEAD/header 就证明执行身份 |
| Build | Unity/SDK/compiler、flags、feature/Development/assertion、library/metadata/buildGuid | 对应 binary 已被选中运行 |
| Launch | binary/input hash、PID/start/fresh process、before/after hash、raw result 配对 | 仅退出码就证明正确拒绝 |
| Raw semantics | exact cases、phase/state、业务/资源/可见性/账本 observed | 未测范围也正确 |

每个关键 claim 独立贯通所有必要层。finalizer/作者统计可辅助，但验证器及 oracle 自身要审查。审计任务按一层/一组 raw 分发，整体 reviewer 仍负责全链路。

## E3. 归档与引用解析

先流式审计再决定是否提取；拒绝 absolute/traversal member、重复/规范化歧义、symlink/hardlink/设备条目、未声明成员及重复 index 条目。PAX 元数据按实际格式处理，文件数以真实常规业务成员为准。JSON 重复 key 拒绝，整数精确保存。认证不执行包内脚本或 receipt argv。

索引 rawPath 是 capture locator；用 rawPath→archiveMember 或带明确 repository/version root 的唯一对应解析。禁止 basename 猜测、跨 v5/v6/R00 同名文件替换或伪建历史绝对路径。成员 hash 相同也不自动拥有相同语义身份。缺项保存 exact unresolved reference。

## E4. 外部 artifact

原包排除 DLL、app、native binary、source trees 等不自动构成失败。逐对象登记 expected hash/size、引用 receipt、实际位置及状态：ExternalBytesVerified；ReceiptAuthenticated_ExternalBytesUnavailable；ExternalMismatch；UnresolvedCriticalReference。

只认证 receipt/raw 不可宣称复算了 binary 字节。关键 claim 无来源证明时保留具体阻塞；非关键明确排除项可带范围说明。新候选运行时必须实际核验被用 binary/fixture 的前后 bytes，保留可供独立审查的对象或稳定保留定位；不能事后补“相信它存在”。不要求把 SDK/Unity 缓存全部塞入 Git。

## E5. 复用

按 suite 比较 old/new production、test、generated、fixture、compiler/flags/target 和原 raw hashes。相关 executable input 改变则 FreshRequired。所有相关 transitive inputs/配置/语义相同才可 ReusedAudited，保留原日期和 stub/平台边界，分开统计 fresh/reused。

InterpreterImage.cpp 改变后，依赖真实 loader 的 native/Player 结果必须新执行。unchanged codec-only 结果可有依据复用，但不证明实际 DLL 初始化。metadata-only 差异需验证不影响生成/合同，不能凭文件扩展名认定无关。

## E6. Raw 和冻结状态

原 Editor 1021、Python 492、startup 11、M07 14、R00 4/48、lazy 61、capacity counts 全从选中的原 raw 重算；Editor 按 XML IDs，Python 排除 zero-test discovery，Player 按 process/phase/semantic assertions。历史失败与当前选择运行分类，不删除。

原 frozen current-status SHA-256：`bcec34889cf99eb4828edd7824595c0a2f4eaa0d89bf44bfb6eafade01e88b37`。它是 pre-review 快照；单独 final-stage review/handoff 是后继记录，不能覆盖快照消除 pending 字样。

新链顺序为 source freeze→build/raw→archive/index→independent stage review→H1 handoff→human decision。archive 不包含自己的摘要/index 摘要来制造循环；index 可绑定 archive，后继 review 再绑定两者。文档后继 commit 与 executable commit 的差异须真实核对。

## E7. 新包与完成定义

新证据使用新版本名称，不替换 v6。结构可为 audits/v6、sources、builds、count-tests、regressions、capacity、performance、indexes；每个 block/文件均入 index。保留 failed/invalid attempts 与 selected run 集合。只有 summary 的包不完整。

每 finding 绑定 source commit/lines、test IDs、raw evidence 和独立 review。Failed、Unavailable、NotRun、NoCoverage、ReusedAudited 不归并为 Passed；材料齐备仅为 ReadyForHumanH1。本次计划提交不认证任何原 archive，也不构成新执行证据。
