# 新增验证矩阵与证据门禁

本表是**待执行要求**。当前仓库已有的 M03–M07 测试继续保留；本次没有运行它们。`analysis/source-algorithm-results.json` 只覆盖容量与伪环的源码算法复算，不给下表的 native/Player 测试记为 Passed。

## 1. 元数据容量与索引

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| Q01 | 1/4/16/64 MiB 的前一字节和恰好边界 | 与当前或声明的新 encoding profile 完全一致；拒绝不分配 index | 原生 helper / R01 |
| Q02 | fresh 小 DLL 连续分配到上限再加一个 | 当前 profile 为 338 成功、第 339 次拒绝；不是 1024 | 原生 helper / R01 |
| Q03 | 先加载普通 interpreter，再 Stage closure | 共享实际配额；不忽略 ordinary 消耗 | native + Player / R01 |
| Q04 | 部分 skeleton/metadata 失败后再次查询预算 | 不假定返还 index；无二次事务或索引重用 | native + Player / R01 |
| Q05 | 不同大小混合、顺序变化、并发 ordinary load | dry-run/预留与最终分配一致；无 TOCTOU 超卖 | native / R01 |
| Q06 | 大闭包达到项目目标，再超限 | 支持范围内完整成功；超限发布前拒绝，无半活动世界 | Player / R01、R01B |
| Q07 | 新 codec 中大 AOT raw index、哨兵、跨页 offset | 不与 Interpreter 范围混淆；roundtrip 正确 | native / R01B |
| Q08 | 新 codec 的 private/active image、数组/泛型/反射 | staged 不可见，发布后 active 正确，旧资源不退化 | native + Player / R01B |

## 2. 分配与执行热路径

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| P01 | 同类型 1/10/10000 次 new | admission proof 仅首次构建；warm path 不全表扫描/临时 native 分配 | native 仪表 + Player / R02 |
| P02 | patch-added type 无 baseline counterpart，重复分配 | “无 baseline”也缓存；不重复线性扫描 | native + Player / R02 |
| P03 | G<A>/G<B>、array、boxing、嵌套泛型 | 证书按完整物理类型区分；旧成分不借缓存通过 | native + Player / R02 |
| P04 | 多线程首次/重复分配和 reflection | 无死锁、无竞争读写 map、无重复可见半证书 | native stress + Player / R02 |
| P05 | OFF、ON 未注册、ON 无补丁、P01、P03 | 分别测量，不把 OFF 结果当作 ON/no-patch | Player / R02 |
| P06 | virtual/interface/delegate/闭合泛型 + diagnostics on/off | guard 仍生效；诊断开销单独量化 | Player / R02 |
| P07 | 超过 1024 个执行 class 观察 | dropped 明确，业务/guard 正确；不虚报完整类型证明 | native + Player / M11 |

## 3. 演进兼容与逻辑身份

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| E01 | 纯托管同名 class 新增 private primitive/reference | V1 只允许已证明规则；不支持的 reference 变化构建前拒绝；V2 需资格 Gate | compiled DLL + Player / R03 |
| E02 | 纯托管字段删除/重排、interface/base change | 准入域有明确结论，不以 Resource ABI 相同自动通过 | compiled DLL + Player / R03 |
| E03 | Unity-bound private reference 或 serialized 字段变化 | native 与资源策略联合验证；重建资源不是唯一条件 | compiled DLL + Player / R03 |
| E04 | value type 增长、嵌入、AOT generic/interop 使用 | 按实际物理边界验证/拒绝，不放宽为普通 reference class | native + Player / R03 |
| E05 | 在既有 virtual 之前新增 virtual，slot 改变 | 合法 baseline MethodInfo→active 描述映射不依赖旧 slot | native + Player / R03 |
| E06 | Method token 重排、实现 flags、泛型/重载 | identity 与 compatibility 分离，不误映射同名重载 | native + Player / R03 |
| E07 | 直接执行旧 AOT MethodInfo | 仍拒绝；反射 key 修复不得授权旧执行 | native + Player / R03 |
| E08 | exception stack trace 返回物理 baseline 方法描述 | 映射正确或明确支持边界；不得错误 poison 合法新方法 | Player / R03 |

## 4. 闭包与运行集合

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| G01 | baseline A→B；target B→A | 安全闭包 A+B，target order 合法；不误报并图伪环 | 实际 DLL 的 Editor 测试 + Player / R03 |
| G02 | target 本身 A↔B | 未声明 SCC 支持时仍拒绝 | Editor + native / R03 |
| G03 | A0/B0→A1/B0→A1/B1 | 第二目标运行 A1+B1，不退回 A0 | Editor + fresh Player / M08B |
| G04 | 删除显式/隐式依赖声明但 baseline consumer 仍保留 | 闭包不漏；同时不错误改变 target load graph | Editor / R03 |
| G05 | ordinary interpreter consumer 与 Shadow provider | 按显式角色契约处理，不伪造 AOT baseline | Editor + Player / X01 或支持域内 |

## 5. 部署能力与版本合同

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| B01 | 新 struct/native signature，资源不变 | 缺 baseline native capability 时发布前拒绝 | builder + reopening verifier / M08B |
| B02 | reverse callback 容量不足 | coverage 不能只比较名称，容量不足拒绝 | generator + builder / M08B |
| B03 | 可由受支持 supplemental metadata 满足的泛型需求 | 与必须 native bridge 的需求分开，不一概拒绝/一概批准 | builder + Player / M08B |
| B04 | 仅 Editor 工具/测试改动，runtime contract 不变 | 真实新 provenance + 显式兼容记录可支持旧 runtime | builder / M08A |
| B05 | native/encoding/managed runtime API 改动 | 旧 Player 明确拒绝新需求 | builder + Player / M08A、R01B |
| B06 | 不同 target snapshots 混 DLL，或 generator 被覆盖 | 在发布/构建 Gate 拒绝 | builder + verifier / M08B |
| B07 | P05 DLL 与旧 catalog 或缺少 rebuilt bundle | code/resource 原子集合不成立，拒绝 | builder + Bootstrap / M08B、M09 |
| B08 | Shadow 被普通 HotUpdate filter 删除 | baseline build 失败，不让 fixture Interpreter 冒充 AOT 首包 | Editor + Player / M08A |

## 6. 启动、状态与恢复

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| S01 | Configure 前 Type/MethodInfo、cctor、对象或 native script 使用 | 在声明层面阻止提交或构建必拒；不靠新 counter=0 | compiled policy + Player / R01 |
| S02 | Stage 输入可纠正拒绝 | 正确 state/error；合法 Abort 后才按许可恢复 | native + Bootstrap / R01、M09 |
| S03 | 部分 skeleton/Validate metadata 失败，state=Failed | 不假装 Abort 成功；按 disposition 重启 | native + Bootstrap / M09 |
| S04 | 发布前后并发读取和故障 | 无半快照、无 staged 泄漏；是否可回退判定正确 | native stress + Player / R01、M11 |
| S05 | module initializer/warmup/入口异常 | 已发布不原地回 baseline；新进程恢复完整 LKG | Player / M09 |
| S06 | catch guard 异常后继续合法业务调用 | 启动 poison/协调器策略真正阻止继续业务；诊断仍可完成 | native + Player / M09 |
| S07 | 临时写、fsync/pointer 切换、healthy 写入任一点结束进程 | 新进程不选未完成集合；健康不是 Commit 成功 | storage + fresh Player / M09 |
| S08 | 篡改签名/hash/size、重复字段、路径逃逸、磁盘不足 | 确定性拒绝，无业务加载，无部分覆盖 | verifier + Bootstrap / M09 |
| S09 | 合法 envelope 但 table/heap/signature/EH/PDB 损坏 | sanitizer 无越界；明确拒绝/错误处置 | native fuzz + selected Player / M11 |

## 7. 新模块和平台范围

| ID | 输入/动作 | 预期 | 层次 / 阶段 |
|---|---|---|---|
| X01 | 首包不存在的新纯托管程序集 | 真正新增身份和能力，不依赖假 baseline | fresh Player / X-Managed |
| X02 | 新程序集中的 MB/SO/SerializeReference + 新 Bundle | 新 Unity 注册/恢复确实成立 | fresh Player / X-Unity |
| X03 | 删除仍被代码/资源/native callback 引用的程序集 | 拒绝；合法删除的逻辑 lookup 不复活 baseline | Editor + Player / X-Remove |
| X04 | 新增/删除后失败和回滚 | code/resource/操作集合恢复完整 | fresh Player / X01、M09 |
| V01 | macOS、Windows、Android 所需 ON/OFF/Dev/Release | 各自真实构建/进程/设备，不复制标签 | M10 |
| V02 | MonoScript direct/fallback 与实际 Addressables 版本 | 逐条记录支持标签，不由 fallback 推广直接 API | M10 |
| V03 | 新编码/新 allocation/Invoke Hook 后历史关键路径 | 用新 executable pairing 重跑受影响 M03–M07 | R00、M10 |
| V04 | 真实复杂模块 + 连续补丁 + 全新安装/LKG | 功能、容量、端到端收益同时达标 | M11、M12 |

## 8. 统一结果要求

每个结果绑定 TestId、source pairing、Unity/target/architecture、compiler mode、baselineBuildId、runtime/encoding/native capability 身份、输入/资源 hash、实际 native library、fresh process 或设备标识、原始日志与断言。

正例同时检查逻辑身份、物理来源、业务结果和资源数据。负例必须证明真实错误触发点以及“没有发布/没有返回对象/没有继续业务”等安全结论；只有 exception 字符串或退出码不足以证明正确拒绝。

原有 M07 strict Gate 记录仅作为历史已记录证据。新增测试保持 Pending/NotRun，直到上述真实验证完成；模型/静态检查不能把这个状态改成 Passed。
