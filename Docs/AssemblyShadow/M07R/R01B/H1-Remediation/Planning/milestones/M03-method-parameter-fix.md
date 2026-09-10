# H1R/M03 — 参数数量检查

状态 Pending；前置参数 fixture/oracle 与加载路径已明确。1A 的 H1-H02 不延期；与其它 `InterpreterImage.cpp` writer 串行。

| ID | Phase | 最小范围/结果 | 停止点 |
|---|---|---|---|
| M03.A | Inspect | InitMethodDefs、ReadMethodDefSig 直接路径、native count 字段 | 输出所有相关窄化/临时值的位置后停止 |
| M03.B | Implement | InterpreterImage.cpp 的必要参数路径和定向 regression test | 最小修复+格式检查；不自续全矩阵 |
| M03.C | Validate | 已存在的参数 family 定向入口 | 新 build 如未就绪，只记录可完成层，不谎称 loader 已验证 |
| M03.D | IndependentReview | 参数 diff、fixture oracle、定向 raw | 检查 D2/V1/V2；发现问题转新修复卡 |

## 修复合同

按[设计 D2](../design.h1-remediation.md)：actual count/extent 差值用足够宽类型，范围和 `>255` 判断在任何相关窄化之前，通过后才写 native 字段。可更早在真实生产签名解析中拒绝，避免无意义向量构造；不改支持范围、ABI/profile/错误编号。

核对 early parameterCount 暂存、actual/named start、Param count/sequence；signature 255+return metadata 不得误判为 256 形参。只修直接需要的检查，不开展通用 parser 重构。诊断给实际 count，失败后不继续参数复制/公开注册、不 reset allocator。

## 验证

0/1/254/255 成功，256/65535/65536/65537 受控拒绝；小方法调用，最大合法方法反射完整数量/类型/顺序。P04 variants 必须保留。guard 移早只要实际 count 和正确失败时点有证据即有效；无关预检查拒绝为 NoCoverage。

已有 reservation 保留，未预约不伪造消耗。定向命令由经过审查的 command-manifest 绑定；helper/static 检查不关闭 H02。完整 Debug/Release、ordinary ON/OFF、Shadow ON 在 M05 验证。

## 产物/退出

parameter-fix.diff、source-audit、定向 raw 与独立 review。代码完成可标 ImplementedNotFullyValidated；H02 最终关闭等待 M05/M06/M08。不得在此做 allocation cache、预热或 R02 性能优化。
