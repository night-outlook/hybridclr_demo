# H1R/M04 — Nested direct-child 计数

状态 Pending；前置 nested fixture/oracle 就绪；M03 同文件写入已结束。1A 的 H1-H03 不延期。

| ID | Phase | 最小范围/结果 | 停止点 |
|---|---|---|---|
| M04.A | Inspect | InitNestedClass grouping、count、最终写回与直接 row 前提 | 标出 group index/raw start 生命周期后停止 |
| M04.B | Implement | 该函数的必要 guard 与定向测试 | 最小 diff/格式检查后停止 |
| M04.C | Validate | nested family 和直接 variants 的已绑定入口 | 记录实际验证层；不替代 M05 全矩阵 |
| M04.D | IndependentReview | nested diff、输入及结果，并核对参数修复未被覆盖 | finding/审查记录后停止 |

## 修复合同

按设计 D3，在 adding child 前检查现有 count=65535 的边界，或采用等价局部宽计数并在写 native 字段前检查。最终 vector size cast 也须运行时检查；assertion 仅辅助。不可使 wrap=0 触发另一次 group 初始化、覆盖 nestedTypesStart，或改变 class/layout 指针与 ABI 宽度。

核查 `_typesDefines[nestedClass-1]`、enclosing row 的直接前提；无效 fixture 修 fixture，必要前置 guard 在同一目标路径修正。保留合法多组交错与 group-index→raw-start 语义。部分 private 初始化失败不可公开；已预约 credits/ID 不退款，不假称可以第二次 Begin。

## 验证

0/1/65534/65535 成功，65536/65537 受控拒绝。合法最大组精确枚举、首尾 type identities、declaring 关系和重复查询正确。正常组邻接边界/超限组、合法交错行不遗漏。Release assertions disabled 下仍需实际拒绝；此处定向结果不能替代 M05。

记录 ordinary/Shadow 对外错误和真实 state；不在 Failed 状态要求非法 Abort 或继续业务。最终两类 source diff 合并检查，避免同文件互相覆盖。

## 产物/退出

nested-fix.diff、grouping-audit、focused raw、独立 review 和联合最小回归记录。整体状态仍待新候选 full-loader 验证，不以 helper PASS 关闭 H03。
