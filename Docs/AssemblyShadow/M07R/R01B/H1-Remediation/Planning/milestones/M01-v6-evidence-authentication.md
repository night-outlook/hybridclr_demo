# H1R/M01 — 原 v6 独立认证

状态 Pending；前置 M00 相关入口；关闭 H1-B01。只读原 v6，不修改 archive/index，不用新候选结果替换旧声明。

## 分项任务

| ID | Phase | 范围与结果 | 验证入口/产物 |
|---|---|---|---|
| M01.A | Inspect | fixed commit 的 archive/index 实际字节 | C1 提取与 shasum；byte-audit；停止 |
| M01.B-I | Implement | 仅审计工具的一项缺失功能及定向测试，不改 runtime | 一次实现 bytes/members/references 等一个操作；格式检查；停止 |
| M01.B-V | Validate | 对对应操作跑坏 hash/重复 member/错版本/missing/zero-case 测试 | 已绑定定向测试命令；停止 |
| M01.B-Q | IndependentReview | 对应操作的读取、oracle 与副作用 | code/test review；停止；通过后才正式使用 |
| M01.C | Validate | index 与 archive 全成员集合/size/hash | audit operation=members；member-audit；停止 |
| M01.D | Validate | rawPath/index 引用与 external 分类 | operation=references；resolution/external 表；停止 |
| M01.E-{build} | Validate | 一个选择 build 的 source/install/generated/launch 链 | operation=sources 的冻结 input-map；停止 |
| M01.F-{group} | Validate | 一组被认证 raw 的实值重算 | operation=raw；Editor/Python/startup/M07/R00/capacity/lazy/oldPlayer 分卡；停止 |
| M01.G | IndependentReview | B01 的各层链路与缺项处置 | 全部审计输入，不能只读各行 PASS；停止 |

工具已有且满足合同时不重写；B-I/B-V/B-Q 是条件开发任务。每张 raw 卡只读其 exact receipts 和对应 oracle，不加载全部历史日志；M01.G 仍负责完整认证范围。

## 必须认证

[EVIDENCE_CONTRACT.md](../EVIDENCE_CONTRACT.md) 固定两项用户 hash；逐文件重算 329 声明，不只核数量。检查成员/JSON 重复、正规化冲突、不安全条目、未索引/未解析引用，不运行包内脚本。

source inventory 按四仓库 fixed bytes 重算，区分 200 unique paths/201 version entries；核对 demo executable→metadata→final diff。每 selected build/launch 核对 installed/generated 来源、实际编译配置、library/buildGuid/PID、input before/after/raw hash。

native-v6 的 v5 reuse 按 transitive dependencies 审计；metadata-only 变化是否影响生成/合同必须证明。外部 binary 被排除不自动 Failed；没读 bytes 也不能声称复算。关键 claim 不可证明时保持 exact blocker。

从 raw 重算原 1021/492、11/14 modes、四 R00 modes/48 timing cells、ordinary/mixed 8191/8192/8193 与 inputs/pages、61 checks 和实际两个 dense fixtures、immutable old Player 拒绝及无发布/业务。Python 排除 zero-test attempt；负向模式检查真实触发点，不只异常字符串。

冻结 current-status 是 pre-review snapshot，后继 final review/handoff 单独解释；历史失败、当前选择与缺失分类不混用。

## 退出与阻塞

产物：bytes/members/references/source-provenance/raw-results/external-artifacts audit 和 H1-B01-disposition。每项有方法、input hash、重算值和可复核定位。缺证据仍 Blocked/Unavailable，不自动风险接受。

历史审计未完可继续独立修复及不依赖该缺项的新测试；每次新执行自身必需输入仍须就绪。M08/H1 不得跳过必要原认证。
