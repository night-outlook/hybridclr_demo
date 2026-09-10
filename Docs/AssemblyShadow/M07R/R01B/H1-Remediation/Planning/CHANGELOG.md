# v2.0：目标不变，执行单位收窄

输入是已确认1A+2A的完整v1计划与用户planning notes。本版不是对原H1源码的新review，也不改变BLOCKED历史结论。

## 按笔记的逐项处理

| 笔记规则 | 本版落实 | 保留的正确性约束 |
|---|---|---|
| 单一结果/文件/命令/停止点 | 各milestone任务表+填写后的单任务卡 | 84+variants及全部回归最终集合不变 |
| 只传必要上下文 | 协调者完整计划、执行者合同子集 | raw审计任务必须读相应raw；完整review不省略 |
| 准确技术表达 | 使用原API/文件名，不加无关修辞 | 不删真实失败场景，不改名隐瞒目的 |
| 不重复授权/意图声明 | 每卡一次明确read/write范围 | 保护用户dirty、分支和实际权限 |
| 实现/验证/review分阶段 | M00盘点与Plan分开；M05准备/build/test分开 | 实现或helper通过不等于真实loader通过 |
| 明确人工checkpoint | 普通任务返回协调者；M08后STOP/H1 | 不新增每小步人审，也不替人放行 |
| 最小委派 | 子代理一张卡、一个phase、不自调度 | 集成pairing必要时仍覆盖四仓库 |
| 维护仓库正确性 | exact pins、single writer、依赖影响审计 | 历史raw不重贴新候选标签 |
| 标准任务模板 | task-card与task-result | 命令未绑定不派发运行 |
| 持续服务问题 | 如实记录并按支持流程处理 | 不自动改词循环重试，不保证消除检查 |

## 实质性组织修正

M00.A仅盘点demo；其余仓库、规范、命令和协议分别登记。M01分bytes/members/references/source/raw层；缺失历史证明仍阻止最终H1，但不阻碍无关独立修复。

M02按参数/nested family分开；generator与独立shape oracle分开；probe/runner/verifier按组件分开。M03/M04只改直接count路径，共享文件串行。M05测量准备在freeze前完成，构建按配置分卡，真实计数按family/path/config分片；M06按suite/mode/capacity拆分，M07按配对schedule拆分。

M08保留不可被局部PASS替代的整体独立复核。M09保留原人工H1，不自动开始R02。oldPlayer、OFF观察、合法255+return Param、sibling非深度、真实Release assertions-disabled、retained reservations的细节均保留。

## 文件组织

全部规范以分文件为准，取消重复全文拼接作为仓库内第二份规范；README和plan提供完整入口。原review/status/notes原字节保存。模板仅Pending/null/false，不制造测试或人审事实。文档提交权限与未来runtime工作权限分开。
