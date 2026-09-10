# H1R/M06 — 新候选回归与 8192 容量

状态 Pending；前置 M05 所需构建/计数验证。真实 loader 已变，旧 full-loader/Player 结果不能证明新候选。

## 任务表

| ID | Phase | 一个范围 | 返回 |
|---|---|---|---|
| M06.A | Inspect | suite 的 transitive 影响映射 | fresh/reuse 决策表；停止 |
| M06.B-{suite} | Validate | 一个 Editor/Python/native suite | exact IDs、actual inputs、raw；停止 |
| M06.C-{mode} | Validate | 一个 startup/M07/R00 mode | 对应新候选 launch/raw；停止 |
| M06.D | Validate | ordinary 容量 fresh process | 完整 8192/8193 输入与账本/mapping；停止 |
| M06.E | Validate | mixed 容量 fresh process | 8184+5+3 的完整过程；停止 |
| M06.F-{suite} | Validate | lazy/dense 或 immutable old-Player 拒绝，分别派发 | exact raw 与证据范围；停止 |
| M06.G | Validate | 完整 regression/capacity result index | required sets/实值独立重算；停止 |
| M06.H | IndependentReview | 回归语义、容量和当前 pairing | 独立结果；停止 |

保持旧 runner 真实合同；不能因为它原来多 mode 调度就伪造 --mode。拆分通过经过审查的有界 adapter 或明确一次只派该 runner 的固定 suite，保存其 exact selected set。

## 1. 回归集合

原 Editor 1021 与 Python 492 的用例语义覆盖并增加新测试，不要求总数恰好不变。Python 使用正确 discovery 与新实际 compiler inputs；zero-case/skip/过滤必须显示。

startup 11、M07 14、R00 四模式新候选全部重跑；旧 prefab/scene/bundle/alias、序列化、消息/API/cache、P04/P05/OFF 语义不减少。lazy 原 61 checks 的 ID/语义映射、两个 dense fixtures 和 4095/4096 边界都须实际发生。

native 包含 count、shared budget/contention、transaction/startup/private visibility；codec/range/generic/attribute/type-cache/parser 按 transitive 影响处理。依赖修复文件的必须 Fresh；完全无关的已认证测试可 ReusedAudited，保留原范围并单列，不充当 loader/Player。

old-Player 用原 immutable profile-1 artifact 证明新要求被拒且无发布/业务；重新编译的 performance reference 不能替代。实际原对象不可取时保留具体 NotRun/Unavailable，不谎称已验。

## 2. Ordinary

专用 fresh process，不混入 count fixtures/witness setup 的预算。实际 8192 有效 DLL 共 536870912 bytes，最大33554432；逐项 hash/size、真实 load/invoke/name/RVA。8191 剩一、8192 用完；distinct 8193 因 ImageLimit 拒绝且账本保持，selected existing mapping 重查。

## 3. Mixed

专用 fresh process，先一次 Commit 五 Shadow，再三次真实坏 ordinary input、8184 ordinary 成功。有效 8189 DLL 共536870912 bytes，加失败12 bytes；8192 lifetime IDs。native ordinary allocation 可包含失败，不能混同 successes。逐失败记录 ID/credits 增、mapped 不伪增、既有 Shadow world 不变；记录8191/8192/8193及mapping。

不要在该 committed process 做第二事务或非法 Abort；合法 Abort retention 由独立 transaction suite 完成。

## 4. 余量与测量

free=524287−reservedPages，至少131072（等价4×free≥524287）。未 mapped 和失败 reservations 都收费。最后成功、拒绝、指定 lazy/post-rejection query 后都检查；区分查询合法 binding 与拒绝自身副作用。不得把旧16388/16392页抄为新 observed。

shape audit 区分 padding 与真实 dense/RVA；RAM 记录 initial/current/lifetime-peak RSS、managed bytes、API和时点。端到端 load elapsed 包含的 I/O/hash/invoke/检查/采样明示，不称 codec-only。

## 退出

产物为 impact-map、case inventory、新 raw/launch、ordinary/mixed/lazy/oldPlayer 结果、aggregate verification 和 independent review。必需 workload 失败整改，不改目标；必要缺证据保持阻塞。M07 正式测量期间不并行本阶段压力或构建。
