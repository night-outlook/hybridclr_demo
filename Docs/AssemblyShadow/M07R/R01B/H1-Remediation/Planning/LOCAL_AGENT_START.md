# 本地启动：仅 M00.A

本目录位置：`Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/`。

完整计划供协调者查阅；不要将整包内容粘贴到单任务上下文。当前最早未完成任务是 M00.A。以下提示词只读取 demo 工作区，不读取全部四仓库、不构建、不实施修复。

```text
在当前本地 hybridclr_demo checkout 执行 M00.A。
目标：记录 demo 的实际根目录、branch、HEAD、dirty/untracked 状态，并确认
9534c7c775d69b79ecd612917231bef3d202a5aa 对象是否存在。
只读文件：本计划 source-pins.original.json，以及 milestones/M00-entry-and-contract-freeze.md 的 M00.A 行。
动作：仅只读 git 盘点；输出记录到仓库外新的目录。
验证：在实际 demo root 执行 git status --porcelain=v1 --untracked-files=all，核对工作区未被修改。
不切分支、不改文件/pins、不提交、不构建/运行项目测试、不进入 R02。
完成后报告实际路径、版本、dirty 列表、固定对象可用性和下一停止点，然后停止。
```

只读对象检查用 `git cat-file -e <SHA>^{commit}`；盘点命令及输出一起保存，不把本机 HEAD 当 reviewed pin。找不到仓库或对象时如实记录，不自动 clone/reset 用户工作区。

## 后续调度

协调者填写 [任务卡](templates/task-card.md)，再分别启动其它 M00 任务。runtime 修复任务只携带相关方法、必要 direct caller、测试入口和合同子集，不重复全历史。

本次文档提交不授权后续 runtime 编辑、正式构建或 remote push；按实际开发任务授权执行。M03/M04 共享文件串行。M08 后保留人工 H1 停止点；不得将本提示词扩大为自动完成所有 milestones。
