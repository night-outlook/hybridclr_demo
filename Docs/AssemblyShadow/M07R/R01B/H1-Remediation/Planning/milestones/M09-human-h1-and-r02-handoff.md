# H1R/M09 — 人工 H1 停止点

状态 Pending；前置M08 ReadyForHumanH1。**不得自动执行此gate或R02。**规范见 [SOURCE_BASIS.md](../SOURCE_BASIS.md) 的H1 gate。

## 人工发起前

只交付材料：新candidate四SHA、exe/metadata/document关系、原v6 audit、新archive/index实际hash、independent stage review、finding closure、完整coverage、受控performance及明确NotRun/Unavailable/reuse/平台限制。

明确回答：两个count问题是否真实Debug/Release loader已修复；原包是否认证；安装/构建/执行身份是否一致；8k/mixed/25%是否成立；2A是否可比。开发者完成、agent PASS、本次计划commit和1A+2A确认均不替代H1。

## 用户决定

用户显式发起完整独立H1 review；review有问题先整改复核同一gate。只有用户明确 `Passed` 或逐项接受允许延期风险的 `PassedWithExplicitDeferredRisk` 才放行。Failed、Blocked或无结论继续停止。

已经选择的1A两个修复、必做证据认证及2A对照不能默认延期。非Development/P99、额外平台或业务形状未纳入本轮不自动成为H1缺陷，也不能被宣称已通过。实际剩余风险依证据判断，不预设必须是哪一种Passed。

## 记录与有条件交接

用 [human decision模板](../templates/h1-decision.template.json) 记录人类原始指令引用、日期/决定人、independent review、四SHA、evidence hashes、接受范围/风险/owner/后续gate。模板默认null/false；程序不得据绿灯填true。

只有决定有效且绑定当前candidate时，准备一张原 `R02-allocation-cache-and-guards.md` 的只读启动交接卡：固定pairing、count regression入口、证据、受控性能基线和限制、一次事务/终身预算、原H2停止点。准备交接不自动实施R02，也不授权无关提交/合并。

本整改计划到此结束。
