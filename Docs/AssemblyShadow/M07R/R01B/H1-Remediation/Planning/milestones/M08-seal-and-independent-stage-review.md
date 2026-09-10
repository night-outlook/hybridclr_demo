# H1R/M08 — 封存与独立全链路阶段复核

状态 Pending；前置 M01、M05、M06、M07 必需项完成。任务拆分不降低整体 review 范围。

| ID | Phase | 一个结果 | 停止点 |
|---|---|---|---|
| M08.A | Inspect | 当前候选 selected-run/依赖/缺项清单 | 确认哪些 fresh/reused/unavailable；停止 |
| M08.B | Package | 新版本 archive/index，不含后继review自引用 | 实际bytes/member hashes；停止 |
| M08.C | Validate | 独立重读新archive/index及来源引用 | 不只信packager统计；停止 |
| M08.D-{domain} | IndependentReview | 一个领域的source→raw证据审查 | 精确findings/证据边界；停止 |
| M08.E | IndependentReview | 设计→全部计划→四仓库→测试→证据→范围的整体贯通 | 不仅汇总D的PASS；形成阶段建议后停止 |
| M08.F | Document | 追加完整handoff和finding closure | ReadyForHumanH1或Blocked；停止自动开发 |

Package/Document分别派发且限证据/文档输出，不执行runtime修改。D可分领域/段读取，但E必须负责跨领域一致性、全范围负例和剩余不确定性；不能以多个小代理结论替代完整审查。

## 新交付

位于 `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/` 的新版本，不覆盖本目录 Planning 或旧v6。

必需：design-addendum、execution-report、finding-closure、requirements-coverage、source-pairing、regression-impact-map、performance-comparison、known-limitations、H1-handoff；原raw及完整索引按 [证据合同](../EVIDENCE_CONTRACT.md) 保存。archive/index实际hash只在生成后记录。external artifacts有可核对保留位置，新执行前后已核bytes。

## 整体复核必须重新检查

参数wide check与Param rows；nested increment/group/cast；真实Debug/Release和OFF计数路径；shared reservation、Abort/Failed、private/publication/stale mappings；AOT/sentinel/profile/ABI/installed source；oldPlayer/OFF/旧资源；lazy/dense/FieldRVA；8192/512MiB/max outlier/mixed/25%；原证据认证与新候选覆盖关系；2A可比性与原始样本。

每finding给exact commit/file/line、场景、影响、required correction和关闭证据。旧stage PASS只是历史输入。两count问题不得恢复成延期接受，2A不得降回历史描述性对照。

## 回流

实现问题→M03/M04或对应有界源码任务；fixture/verifier→M02；source/build→M05；raw缺项→M06；测量方法→M05.A/M07。所有重跑新runID，保留旧失败。源变则重新计算影响与配对，不因为“代码已改”跨gate。

## 退出

全链路review完成且必需证据完整才ReadyForHumanH1。后继review绑定新archive/index和candidate；冻结status不被修改成live verdict。M08.F仅组织材料，humanGatePassed=false、mayEnterR02=false；接着停在M09。
