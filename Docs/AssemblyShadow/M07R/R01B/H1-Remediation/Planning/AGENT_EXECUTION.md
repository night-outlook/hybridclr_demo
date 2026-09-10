# 有界任务执行规则

本页采用用户 [AGENT_PLANNING_SAFETY_NOTES.md](references/AGENT_PLANNING_SAFETY_NOTES.md) 的任务粒度、必要上下文、真实命名与停止点原则。优先级为：**用户目标与已定 1A+2A → 规范 H1/正确性要求 → 本计划合同 → 任务拆分与措辞简化**。

## 1. 协调者保留全局，执行者只读必需输入

协调者维护 requirements→source→tests→evidence 映射、依赖、权限和候选版本；需要四仓库时必须检查完整 pairing。执行者只获得当前卡、指定文件/符号、直接调用关系和所需合同条款。不得把整份计划、历史对话、全量日志或无关仓库作为每张卡的开场上下文。

必要的失败状态、ordinary/Shadow 共享预算、profile/ABI 和相关 raw 证据不能因“减上下文”被删除。缺少直接依赖时向协调者申请有界补充，先明确新增范围再编辑。

## 2. 单卡合同

采用 [task-card.md](templates/task-card.md)。卡必须填满：task ID；一个可验证结果；一个 phase；exact repository roots/commit；read/write allowlist；必要输入；完整 argv/cwd/env；expected result；output；stop point。一个集成配对任务可以包含四仓库只读身份信息，因为这正是其结果，不顺带编辑四仓库。

`Proposed` 工具或未解析变量不能进入运行卡。M00 或对应工具实现任务应先检查源码/parser并绑定真实命令。inspect 阶段可使用只读 git/source 检查；实现阶段可做最小格式/静态检查，但正式验证与独立 review 另建卡，不谎称实现即通过。

每张卡只有一个正式验证入口；该入口可运行一个明确的 case family/suite，但必须记录 requested/executed IDs。以脚本包装全部十阶段不符合单卡合同。

## 3. 标准阶段与返回点

运行时整改采用 `Inspect → Implement（必要时）→ Validate → IndependentReview → 返回协调者`。Plan、Integrate、Build、Package、Document 也必须分别派发，准确标明其实际动作和输出权限。每个箭头都是新的有界任务，不要求一个执行者贯穿全部阶段。只读任务不能在发现问题后直接写代码；reviewer 报 finding，由新修复卡处理。

子代理不得自行调度其它代理；只接受当前一张卡。对共享文件实施单 writer；集成负责人独占相应安装树/构建树/设备。并行以无共享可变状态为前提，不以仓库名不同为依据。

每次结束报告：实际 commit/tree、读取/修改文件、执行命令、raw 证据定位、expected/observed、状态、未运行范围及下一停止点。任务报告不是 human H1。

## 4. 停止点与人类 gate

普通任务结束后停止并交还协调者，不自行跨任务；不增加“每个子步骤都重新征求用户策略”的开销。已确认 1A+2A 不再询问。

M08 完成后停止自动开发，用户发起完整 H1 复核并明确 Passed/PassedWithExplicitDeferredRisk 后才可交接 R02。整体 reviewer 必须重新贯通设计、实现、四仓库 pairing 和证据；可分段阅读，但不能把局部 PASS 汇总冒充整体结论。

## 5. 技术表达与异常处理

准确使用原有 `Assembly Shadow`、`Stage`、`Abort`、`Patch`、FieldRVA、文件和 API 名称；不改名、不隐瞒实际目的、不通过词语替换改变任务性质。不重复无关免责声明，不将术语删除设为成功条件。

用户笔记是工程组织参考，不是对平台检查机制的保证。官方说明仅建议允许的任务缩小范围、保留必要上下文，且措辞变化不改变是否允许，也不保证返回内容；见 [来源](SOURCE_BASIS.md)。笔记关于上下文“污染”的描述不作为可证实技术结论。

若工具或服务拒绝请求，区分访问错误、工程失败与服务限制；不循环改词重试来规避限制。确认任务范围及真实用途后，仅按支持流程处理；需要重新发起合法任务时仍保留必要约束和权限，不复制无关历史。持续问题报告原消息、模型/时间区/请求 ID 和脱敏描述，禁止包含凭据。

## 6. 范围不可用时

记录 exact blocker、受影响 requirement、可继续的独立任务。不得降低测试边界、把 Unavailable 写为 Failed、把没跑写为 Passed，或将强制修复推迟。合规的任务粒度优化不替代工程证明。
