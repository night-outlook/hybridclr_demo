# H1R/M00 — 分项盘点与合同登记

状态 Pending。此页是协调规格，不是一次执行全部工作的指令。**首任务 M00.A 只读 demo**，不 freeze 协议、不改源码、不构建。各卡遵守 [执行规则](../AGENT_EXECUTION.md)。

## 任务表

| ID | Phase | 一个结果；最小范围 | 验证/返回产物 |
|---|---|---|---|
| M00.A | Inspect | demo root/HEAD/branch/dirty、reviewed object 可用性；只读 demo 和 source-pins.original.json | C1 只读 git；demo-entry.json；停止 |
| M00.B-{repo} | Inspect | 每次一个 native/package repo 的同类身份及隔离输出位置 | C1；该 repo-entry.json；停止 |
| M00.C | Inspect | H1 gate、R01B 规范、review 四项 findings 与本计划目标对应 | 对固定规范/来源逐项链接；requirements-entry.json；停止 |
| M00.D-{suite} | Inspect | 每次一个 build/test suite 的真实入口、parser、环境、输入依赖 | 绑定 COMMAND_CATALOG 的命令条目，不执行 suite；停止 |
| M00.E | Plan | 汇集四仓库 pairing 和 workspace map；只写新盘点记录 | 根目录/commit/dirty 对应、无冲突安装/生成路径；停止 |
| M00.F | Plan | 预注册验收集合与受控对照协议；不测量 | 矩阵、样本单位、配置与不可删约束一致；停止 |
| M00.G | IndependentReview | 审查入口/权限/合同是否足够派发下一卡 | command readiness、前置无环、版本字段完整；停止 |

Plan phase 只产生规划记录，明确其输出写权限；不以“只读”名义修改 tracked 计划、源码或 pins。

## 要记录的事实

每个 canonical repository root、branch/HEAD、dirty/untracked、reviewed object。不能从 branch 最新值推断被审版本；demo 的 final/executable/metadata 身份分开，git diff 确认差异。Unity exact version、目标架构、Python/clang/SDK 和 installed native root 由单独环境盘点卡记录，不启动 Unity 导入。

只在仓库外新 `$H1_AUDIT/entry/` 写记录。HEAD 不同、对象缺失或工作区有用户改动时报告，禁止 reset/clean/覆盖。提出隔离 ReviewedV6、R01 reference、candidate 的 checkout/安装树/Library/输出位置；此阶段不创建分支或切换工作区。

每个命令必须有 script/symbol hash、实际 argv/cwd/env、输入与输出合同。未实现工具 Proposed；已有但没查 parser 为 NeedsLocalVerification。`--help` 前先审脚本副作用。不得臆造 executeMethod、配置参数或用零 testcase 的 exit 0 填通过。

## 合同冻结

M00.F 按矩阵登记 provisional expected IDs 的来源；M01 的认证 raw 和 M02 的实际 fixture 审计完成后再固定最终 sets，不能因暂缺原 evidence 降低覆盖。性能字段和采样规则预注册；source/harness/build 具体 hashes 在对应阶段绑定，不提前伪造。

用户已定 1A+2A，不新增重复选择。Development、C++ Debug/Release、assertions、diagnostics 分栏；旧 profile 不承担 8k，对照不引入生产 SLA。

## 退出

产物：workspace-map、source-entry、command-manifest、acceptance-contract、performance-protocol、findings-ledger。每条任务单独结束；协调者只派发已满足前置的 M01/M02 或测量准备卡。当前 H1/R02 布尔值保持 false。
