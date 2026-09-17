# X01 · 新增/删除程序集能力；与 Replace 分离

状态：待执行。本文不表示代码已修改或测试已通过。

前置：R01、R03、M08B；独立 feature 分支，进入目标平台 M10 验收。关联 findings：ASR-001, ASR-010。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

满足模块随版本增长的需求，而不让新逻辑 registry entry 破坏已有 Replace 的 baseline/Unity alias 规则。该分支不应阻止已证明的核心修复，但产品宣称此能力前必须合流验收。

## 实施步骤

### 1. 操作与清单

扩展版本化 operation 为 Replace、AddManaged、AddUnityTypes、Remove。每个 operation 写明 baseline 是否必须存在、预期资源、执行角色、是否需要 Unity startup 注册、配额与 native capability。旧 schema 不接收未知 operation。

### 2. AddManaged 纵向切片

构建一个首包完全不存在的程序集，包含普通 class、interface/generic 使用与反射入口；通过真实新 registry identity、Stage/Validate/Commit 加入。没有 baseline 的 entry 不进入 baseline remap；新类型路径必须能生成 active metadata，而不是返回伪造 baseline。

### 3. AddUnityTypes 可行性 Gate

使用新程序集名中的 MonoBehaviour、ScriptableObject 和 SerializeReference 具体类型构建新 Bundle，在未装载这些资源的新进程恢复。追踪 Unity startup image 注册与实际类型查询。分别实验可用的提前注册、预留 placeholder、native launcher/manifest 入口，但以 Player 实际使用的信息为准，不能只证明文件下载成功。

若某路径依赖安装包预留清单，明确它是“预留空间内新增”而非任意新增。若必须改变原生 Player 启动集成，单独记录平台实现和安装包约束，不把假设写为已解决。

### 4. Remove 与逻辑墓碑

先验证没有保留 AOT 直接/隐式调用、业务资源、反射字符串或 native callback 可触达该逻辑程序集；否则拒绝。物理 baseline 保留不等于逻辑上仍可查到它。Tombstone 必须作用于普通 lookup/enumeration/入口，诊断仍可报告物理保留身份。

### 5. 闭包与普通热更角色

为新增 image 和普通 interpreter consumer 定义真实角色：重新编译/重新装载不要求假想 AOT baseline。安全图、target load graph、配额和 generation demand 一致，不能把普通热更静默标记 shadow-capable 来绕过现有政策。

### 6. 资源与回滚

新增/移除代码与资源 catalog 原子发布；LKG 恢复所有 operation 的完整目标状态。测试新类型引用旧类型、旧更新 consumer 引用新类型、删除仍被序列化资源引用、移除后按原名字查询、失败重启和再次选择 baseline。

## 退出条件

X-Managed、X-Unity、X-Remove 分开给结果。任一项成功不为其余背书；现有 M07 Replace 全部回归继续通过。严格保持原来偏好的细粒度边界，不默认把资源类型合并到一个永久稳定程序集来回避目标。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。
