# R01B · 按实际规模扩展 metadata 索引容量

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R01；当目标规模超过现有 profile 时必需。关联 findings：ASR-001。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标与边界

满足声明的最大累计闭包及 DLL 大小分布，同时保留 AOT 元数据语义和 feature-OFF 回归。这是 native 编码改造，不是运行时增大 vector 或修改 manifest 的问题。该阶段未通过时，不得向超限项目宣称方案已经满足细粒度需求。

## 实施步骤

### 1. 完整索引使用清单

在 hybridclr/il2cpp_plus 中搜索并记录 EncodeWithIndex、DecodeImageIndex、DecodeMetadataIndex、image token、类型/方法/字段 index、负数与 invalid sentinel、private image lookup 及所有定长表。包含生成代码和 Debug/Release 条件分支。记录每种索引的最大真实值，而非只看 DLL 文件总长。

### 2. 选择编码 ADR

用 R00 的真实大小直方图比较：旧分桶重新分配位数/步长；32 位页式/区间分配；更宽字段表示。优先维持 IL2CPP 结构字段宽度。必须保护 AOT raw-index 区域，不能假设 AOT 永远只占一个低地址页；还要处理最大 metadata/string/blob offset 与哨兵。

ADR 输出理论可达容量、最坏单 image 范围、混合大小碎片、查询开销、安装包兼容性和失败策略。可用小型独立原生原型验证分配/编码，不以原型通过代替 Player。

### 3. 实现唯一 Codec

引入一个显式 `MetadataEncodingProfile` 和唯一 encode/decode 实现。所有调用者经集中 codec，旧格式保留为测试对照；禁止不同文件隐含不同 bit layout。若采用页表，private/active 页映射仍有单一所有权，查询不得公开 staged 元数据，GC/枚举能识别同一 image 的多个编码段。

### 4. 原生表与生命周期

调整所有与 image 槽相关的表、范围校验和预算算法。映射进程终身、失败不重用；skeleton 分配中途失败仍可诊断占用。对原有引用地址、type handle 和 existing AOT 索引做 roundtrip/随机边界验证。不能修改现存对象的 class 指针。

### 5. 四仓库 ABI 联动

新的 encoding profile 进入 RuntimeContractId、baseline native capability、installed-source proof、patch manifest 和 Stage 兼容检查。构建新的 Player baseline；旧 M07 安装包明确拒绝要求新编码的补丁。不要通过改旧源码 pin 来模拟兼容。

### 6. 扩容压力及回归

测试声明规模和上限前后一个 image、混合大小、长期普通 load、一次事务多 image、Abort、private visibility、泛型/数组/反射、旧 Bundle 与 Unity alias。增加大 AOT metadata 区域样本，覆盖 AOT raw index 与 Interpreter encoding 的不重叠。

## 退出条件

目标最大闭包具有明确余量，所有 encode/decode 与 lifecycle Gate 通过；性能相对旧 profile 有实测结果；Windows/Android/macOS 的必需组合纳入 M10。若当前原型不满足约束，回到 ADR 调整，而不是缩小记录中的目标规模或放宽索引检查。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
