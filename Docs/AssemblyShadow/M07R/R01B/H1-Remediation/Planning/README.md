# R01B H1 整改与补验计划

版本：2.0；日期：2026-09-10；策略：**1A + 2A**；实施状态：**未开始**。

**当前首任务：M00.A（仅盘点 demo 工作区）。H1 未通过，R02 不得启动。**

## 阅读入口

| 读者 | 阅读材料 |
|---|---|
| 协调者 | [总计划](plan.md)、[设计增补](design.h1-remediation.md)、[执行规则](AGENT_EXECUTION.md)及当前相关合同 |
| 单任务执行者 | 一张已填写的[任务卡](templates/task-card.md)、目标文件及该卡列出的合同条款；不加载整包或历史对话 |
| 整体复核者 | 设计、全部阶段、四仓库固定源码、证据和[覆盖矩阵](VALIDATION_MATRIX.md)；局部审查不能代替整体复核 |
| 本地首任务 | [LOCAL_AGENT_START.md](LOCAL_AGENT_START.md) |

本计划完整范围是：认证原 v6 证据；修复两个计数问题；验证新候选；补受控 Development 对照；形成独立整体复核材料；停在人工 H1。它不替代原 R02–M12 计划。

## 完整文件集

[十阶段及依赖](plan.md)；[验证矩阵](VALIDATION_MATRIX.md)；[性能协议](PERFORMANCE_PROTOCOL.md)；[证据合同](EVIDENCE_CONTRACT.md)；[命令登记规则](COMMAND_CATALOG.md)；[来源](SOURCE_BASIS.md)；[本版调整](CHANGELOG.md)；[一致性检查](PLAN_CONSISTENCY_CHECK.md)。`milestones/` 保存详细任务规格，`templates/` 保存待填记录，`references/` 保存参考材料。

仓库位置：`Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/`。本次只提交计划文档；不改原 v6 archive、index、review、handoff、冻结 status、项目源码或 source pins。不在仓库维护重复的全文拼接文件：本目录全部规范分文件共同组成完整计划。

## 不可降低的目标

1A：两个 count 问题必须在 H1 前修复并经真实 loader 验证，不延期。2A：H1 前必须取得新旧共同负载的受控 Development 对照，不能仅重用历史描述性比较。原证据缺口必须独立认证，缺失不冒充失败，未核验不冒充通过。

任务拆小只改变执行组织，不改变目标规模、测试集合、四仓库版本绑定或人工 gate。具体规则以 [AGENT_EXECUTION.md](AGENT_EXECUTION.md) 为准。
