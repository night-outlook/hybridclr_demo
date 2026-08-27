# Milestone 12：发布候选、最终验收与生产试运行

## 目标

完成 Assembly Shadow 的最终发布判定。该 Milestone 不新增核心功能，重点是：

- 冻结范围和兼容组合；
- 从干净仓库重建全部产物；
- 对照需求执行完整验收；
- 演练补丁、回滚、安全和运维流程；
- 以受控灰度方式进入真实项目；
- 形成可审计的 Go/No-Go 决策。

最终交付不是单个 DLL，而是一套版本锁定的运行时、Unity 工具、Demo、测试证据和操作规则。

## 进入条件

- M11 Gate 4B 通过；
- 所有 P0/P1 缺陷关闭；
- Windows x64 和 Android ARM64 完整矩阵稳定；
- 性能和内存预算获得项目负责人批准；
- 有可访问的代码签名、CI artifact 和符号存储；
- Bootstrap、A/B slot、last-known-good 和 kill switch 可演练；
- 目标项目已选定一个低风险垂直切片作为试运行范围。

## 发布原则

1. 发布绑定 exact Unity、HybridCLR、HybridCLR Unity package 和 `il2cpp_plus` commit。
2. 不支持的 Unity patch version 不宣称兼容。
3. 首次生产试运行只选择小闭包、低风险模块。
4. 不以 Demo 通过代替真实项目验证。
5. 任何 Resource ABI 不确定性都按需要重构资源处理。
6. Shadow Runtime 错误优先回退，不尝试继续运行半一致状态。
7. 发布说明必须写清限制，而不是只描述成功路径。
8. 生产 build 必须能远程禁用补丁。
9. 每个补丁都可追溯到源码、编译器、Manifest 和签名。
10. 无法解释的 native crash、类型错配或静默状态错误一票否决。

---

## 任务 12.1：冻结 Release Candidate 范围

创建范围文档：

```text
Docs/Release/RC-Scope.md
```

明确：

### 支持

```text
Unity 2022.3.<exact patch>
IL2CPP
Windows x64
Android ARM64
一次进程一次Shadow Commit
同名程序集整包Interpreter切换
反向依赖闭包
旧AssetBundle在Resource ABI不变时复用
Assembly/Type/Reflection/AppDomain
构造/静态/虚表/接口/delegate/泛型
Add/GetComponent
ScriptableObject
Prefab/Scene AssetBundle
签名、A/B slot、回滚、kill switch
```

### 不支持或延后

示例：

```text
同进程卸载/二次补丁
方法级AOT/Interpreter混合
未验证的Unity版本
WebGL
未验证的主机平台
Shadow前已经加载业务资源
Resource ABI变化但不重构资源
任意跨闭包具体类型泄漏
Bootstrap热更新
```

每个限制给出检测方式和失败行为。

---

## 任务 12.2：建立需求追踪矩阵

创建：

```text
Docs/Release/Requirements-Traceability.md
```

表结构：

| Req ID | 需求 | 设计章节 | 实现提交 | 测试 ID | 平台 | 结果 | 证据 |
|---|---|---|---|---|---|---|---|

至少覆盖：

```text
REQ-ASM-001 同名assembly active解析
REQ-CLOSURE-001 反向依赖闭包
REQ-TXN-001 Stage/Validate/Commit原子性
REQ-TYPE-001 Class/Type统一
REQ-REFL-001 Reflection统一
REQ-EXEC-001 执行语义
REQ-UNITY-001 Component API
REQ-ASSET-001 旧Prefab/Scene Bundle
REQ-ABI-001 Resource ABI
REQ-BOOT-001 Commit前无业务使用
REQ-ROLLBACK-001 pre/post commit失败
REQ-SEC-001 签名和完整性
REQ-PERF-001 feature-off预算
REQ-PERF-002 active resolver预算
REQ-UPGRADE-001 exact source lock
```

没有测试证据的需求不能标记完成。

---

## 任务 12.3：创建四仓库 RC 分支与 Tag

推荐：

```text
hybridclr:
    release/assembly-shadow-rc1
    assembly-shadow-runtime-v0.1.0-rc1

hybridclr_unity:
    release/assembly-shadow-rc1
    assembly-shadow-tooling-v0.1.0-rc1

il2cpp_plus:
    release/unity2022-assembly-shadow-rc1
    unity2022-assembly-shadow-v0.1.0-rc1

hybridclr_demo:
    release/assembly-shadow-rc1
    assembly-shadow-demo-v0.1.0-rc1
```

Tag 前要求：

- working tree clean；
- submodule/外部 source pin 明确；
- changelog；
- compatibility lock；
- generated files 可重现；
- 不包含本机绝对路径；
- 不包含测试私钥；
- license/notice 更新；
- API 文档生成。

Tag 必须是 signed tag，若团队流程支持。

---

## 任务 12.4：干净环境重建

使用一台没有开发缓存的构建机或全新 CI workspace：

```text
clone四仓库指定tag
安装exact Unity 2022.3
安装Android toolchain
运行Installer
验证il2cpp source commit
生成baseline
生成patch P00-P09
构建Windows Player
构建Android Player
运行全部测试
```

禁止复用：

```text
开发机已修改Unity安装目录
未记录的Library缓存
手工拷贝的libil2cpp
旧生成器输出
旧AssetBundle
未归档签名文件
```

输出：

```text
clean-room-build-log
source-revisions.json
toolchain-lock.json
installer-report.json
binary hashes
symbols
test results
```

成功后再验证第二次干净构建的确定性。完全二进制确定性若受 Unity 构建时间戳影响，应至少保证：

- Manifest canonical 内容一致；
-程序集 identity/MVID 策略符合预期；
-Resource ABI hash 一致；
-依赖闭包一致；
-生成源码语义一致；
-package文件 hash 可解释。

---

## 任务 12.5：最终功能验收场景

### Scenario A：Baseline Only

```text
无补丁
→ 所有业务AOT
→ 旧资源正常
→ Shadow diagnostics显示Inactive
```

### Scenario B：Internal-only Patch

```text
AssemblyA.Implementation.Internal变化
→ 仅Internal Interpreter
→ Contracts/Extensibility保持AOT
→ 旧Prefab和旧Scene执行新逻辑
```

### Scenario C：Extensibility Closure

```text
Extensibility变化
→ Extensibility + Internal +白名单Consumer Interpreter
→ Contracts和无关Consumer保持AOT
→ 基类virtual/interface行为正确
```

### Scenario D：Contracts Full Closure

```text
Contracts变化
→ 所有反向依赖程序集Interpreter
→ 同一次编译快照
→ AppDomain/Reflection只看到active逻辑世界
→ 新契约功能可执行
```

### Scenario E：Resource ABI Change

```text
序列化字段变化
→ DLL-only构建被拒绝
→ 重新构建受影响Bundle后通过
→ 未受影响Bundle不重构
```

### Scenario F：Invalid Patch

逐项：

```text
签名错误
hash错误
缺失DLL
多余未声明DLL
错误baseline
错误平台
错误runtime ABI
错误load order
重复assembly identity
```

全部应 Commit 前失败并安全 baseline。

### Scenario G：Post-commit Failure

```text
module initializer/warmup/business entry失败
→ 当前进程退出
→ patch标bad
→ 下次启动回退
```

### Scenario H：Remote Kill Switch

```text
已安装有效patch
→ 远程禁用
→ 下次启动跳过patch
→ baseline或last-known-good启动
```

---

## 任务 12.6：最终 API 路径验收

形成签字表，不只依赖自动汇总：

### Assembly

- `Assembly.Load`
- `Assembly.GetExecutingAssembly`
- `Assembly.GetCallingAssembly`（若支持并验证）
- `Assembly.GetEntryAssembly`
- `Assembly.GetType`
- `Assembly.GetTypes`
- `Assembly.GetReferencedAssemblies`
- `AppDomain.CurrentDomain.GetAssemblies`

### Type/Reflection

- `Type.GetType`
- `object.GetType`
- `typeof`
- `RuntimeTypeHandle`
- assignability
- Activator
- constructor/method/field/property reflection
- attribute
- generic reflection
- reflection cache identity

### Execution

- new/static/cctor/module initializer
- direct/virtual/interface
- base/abstract
- delegate/event/lambda
- generic/value type
- exception/async/iterator

### Unity

- Add/Get/TryGet/GetComponents
- parent/children/interface/base
- ScriptableObject
- old Prefab
- old Scene
- nested prefab/variant
- SerializeReference
- UnityEngine.Object reference
- load/unload/reload

每项记录：

```text
测试ID
Windows结果
Android结果
active identity证据
关联缺陷
```

---

## 任务 12.7：数据与状态兼容验收

Assembly Shadow 解决代码和类型解析，不自动解决业务持久化。

对试运行模块检查：

```text
PlayerPrefs
本地存档
数据库/缓存
网络协议
序列化DTO
Addressables catalog
资源版本
配置表
单例状态
静态注册
```

要求：

- patch business state schema 有版本；
- 迁移是幂等的；
- patch 回退不会读取不可逆新格式，或有兼容策略；
- Contracts 变化与服务端协议兼容；
- last-known-good 能处理已有数据；
- 失败迁移不在 Commit 前执行；
- 不把业务迁移放在 native module initializer。

创建：

```text
Docs/Release/State-Migration-Policy.md
```

---

## 任务 12.8：安全验收

由非实现者执行：

- Manifest 签名验证；
- 公钥版本；
- 重放旧 patch；
- baseline build ID 绕过；
- package 路径穿越；
- 文件替换竞态；
- A/B slot 原子切换；
- 下载中间人/错误 CDN；
- patch 撤销；
- 本地篡改；
- diagnostics 信息泄漏；
- 测试入口是否出现在 release；
- fault injection 是否被编译掉；
- 未签名 PDB/资源处理策略。

高危或关键问题全部关闭才允许 Go。

---

## 任务 12.9：性能与内存最终验收

在批准的设备档位执行：

```text
低端Android
主流Android
Windows目标机
```

至少采集：

```text
baseline启动
P01启动
P03启动
Commit各阶段
first prefab
first scene
关键业务ready
P50/P95/P99
native/managed memory
patch磁盘占用
包体增量
steady resolver overhead
first transform/warmup
```

比较：

```text
未修改upstream build
feature-on无patch
P01
P03
```

结果写入：

```text
Docs/Release/Performance-Acceptance.md
```

若因 closure 过大导致性能不可接受，优先调整程序集边界和 Contracts 变化频率，不通过关闭正确性检查解决。

---

## 任务 12.10：回滚与灾难恢复演练

在真实设备上演练：

1. 下载中断；
2. 安装中被 kill；
3. Commit 前 native error；
4. Commit 后 managed exception；
5. Commit 后 native crash；
6. health marker 未写入；
7. 连续启动崩溃；
8. last-known-good损坏；
9.两个slot都损坏；
10.远程kill switch；
11.设备长期离线；
12.应用升级后残留旧patch。

每项记录：

```text
初始磁盘状态
注入点
当前进程行为
下次启动选择
用户可见结果
日志/诊断
最终恢复步骤
```

目标：

- 不出现永久启动循环；
- 能回到 embedded baseline；
- 不需要用户手工删除文件；
- 错误 patch 不重复尝试超过策略；
- 诊断能识别 patch id 和失败阶段。

---

## 任务 12.11：生产运维材料

创建：

```text
Docs/Operations/
├─ Patch-Build-Runbook.md
├─ Patch-Release-Runbook.md
├─ Patch-Rollback-Runbook.md
├─ Kill-Switch-Runbook.md
├─ Crash-Triage-Runbook.md
├─ Resource-ABI-Runbook.md
├─ Unity-Upgrade-Runbook.md
├─ Key-Rotation-Runbook.md
└─ Known-Limitations.md
```

内容至少包括：

- 谁可以构建/签名/发布；
- build source lock；
-补丁审批；
-closure报告；
-Resource ABI报告；
-发布前测试；
-CDN/版本配置；
-灰度比例；
-成功指标；
-回滚阈值；
-crash定位；
-symbol获取；
-补丁撤销；
-Unity/HybridCLR升级步骤。

---

## 任务 12.12：真实项目垂直切片

选择满足以下条件的模块：

- 闭包小；
- 无关键支付/账号风险；
- 有独立业务入口；
- 可构造纯逻辑变化；
- 资源序列化简单；
- 有明确健康检查；
- 可快速回滚。

建议阶段：

### Phase 0：开发环境

```text
工程接入
依赖规则检查
baseline player
Internal patch
旧资源验证
```

### Phase 1：内部 QA

```text
数十台设备
P01实际业务修复
持续数日
观察crash/启动/内存
```

### Phase 2：员工或白名单

```text
远程patch
A/B slot
kill switch
真实CDN
```

### Phase 3：小比例灰度

示例：

```text
1% → 5% → 20%
```

具体比例由项目发布策略决定。每级必须满足观测窗口和成功阈值后再扩大。

### Phase 4：常规使用

只在至少一次真实 patch 成功发布和回滚演练后进入。

---

## 任务 12.13：灰度指标

至少监控：

```text
patch选择率
下载成功率
签名/Hash失败率
Stage失败率
Validate失败率
Commit成功率
post-commit失败率
启动成功率
启动耗时P95/P99
native crash率
managed exception率
回滚率
kill switch触发
内存峰值
资源加载失败
Missing Script
GetComponent失败
类型转换异常
```

按：

```text
baseline build
patch id
platform
device model
OS
closure size
```

分组。

出现以下任一信号立即暂停扩大：

- native crash 明显升高；
- Missing Script；
- invalid cast/type identity；
- post-commit failure；
-启动循环；
-无法自动回退；
-资源ABI误判；
-数据损坏；
-诊断缺失导致无法定位。

---

## 任务 12.14：Release Artifact 清单

每个 release 保存：

```text
release/
├─ compatibility-lock.json
├─ source-revisions.json
├─ changelog.md
├─ runtime-abi.json
├─ installer-profile.json
├─ hybridclr-unity-package.tgz
├─ il2cpp-plus-source-tag.txt
├─ demo-baseline/
├─ demo-patches/
├─ test-results/
├─ performance/
├─ security-review/
├─ symbols/
├─ notices/
└─ sha256sums.txt
```

实际产品 patch 单独保存：

```text
manifest
signature
assemblies
resources（若有）
resource catalog
warmup profile
release metadata
```

私钥、未脱敏 token 和本机配置不得进入 artifact。

---

## 任务 12.15：文档和 API 冻结

发布前审阅：

- Runtime managed API；
- InternalCall API；
- native enum/error codes；
- Manifest schema；
- compatibility lock schema；
- diagnostics schema；
- build command；
- settings asset；
- resource ABI report。

对外 API 标注：

```text
Stable
Experimental
Internal
Testing-only
```

MVP 不应将底层 pointer/diagnostic mutation API 暴露为 stable。

Manifest schema 修改后必须有版本迁移或明确拒绝规则。

---

## 任务 12.16：已知限制登记

`Known-Limitations.md` 至少列出：

- 必须在业务类型首次使用前 Commit；
- 每进程仅一次 Commit；
- baseline 元数据不能卸载；
- Shadow 闭包整体 Interpreter；
- Contracts 变化可能形成大闭包；
- Resource ABI 变化需更新资源；
- Bootstrap 不可热更；
- 未验证平台；
- Unity patch version 锁定；
- 反射/Unity 特殊路径若有限制需逐项列出；
- Interpreter 性能差异；
- 主包中直接加载的业务 Scene/Resources 限制；
- 同进程回滚不支持；
- post-commit failure 需重启。

所有限制应由工具检测或运行时明确失败；不能只写文档而静默允许。

---

## 任务 12.17：最终独立审查

至少包括：

### Runtime Review

由 IL2CPP/HybridCLR native reviewer 检查：

```text
transaction
active snapshot
class/type mapping
reflection
static/vtable/generic
thread/memory
error handling
```

### Unity Resource Review

检查：

```text
MonoScript
Prefab/Scene
AssetBundle
TypeTree
SerializeReference
resource ABI
load order
```

### Security Review

检查：

```text
signature
package
rollback
kill switch
input hardening
```

### Operations Review

检查：

```text
build/release/rollback runbook
monitoring
symbols
on-call triage
```

输出：

```text
Docs/Reviews/M12-Runtime-Review.md
Docs/Reviews/M12-Unity-Resource-Review.md
Docs/Reviews/M12-Security-Review.md
Docs/Reviews/M12-Operations-Review.md
```

---

## 任务 12.18：Go/No-Go 会议材料

准备一页摘要和完整证据包。

### Go 必须全部满足

- Gate 0～4B 全部通过；
- exact source lock；
- clean-room build；
- P00～P09；
- Windows + Android；
- 旧 Bundle 证据；
- feature-off 性能；
- active resolver 性能；
- 安全 review；
- rollback 演练；
- 符号和诊断；
- 运维 runbook；
- 真实项目内部 QA；
- 无 P0/P1；
- 所有限制已接受。

### No-Go 条件

任一项成立即 No-Go：

- Unity 资源恢复仍可能解析 baseline class；
- active logical world 出现双 Type；
- closure 漏算；
- Commit 非原子；
- post-commit 同进程错误回退；
- Resource ABI 漏判；
- native crash 无法解释；
- 数据损坏；
- 安全校验可绕过；
- 无法自动回到 baseline；
- Unity/HybridCLR source 版本不确定；
- 性能超预算且无批准；
- 关键路径仅在 Editor 验证。

会议结论必须书面记录责任人和批准范围。

---

## 任务 12.19：发布后观察与维护

首次生产发布后：

```text
24小时高频观察
7天稳定观察
首个真实补丁复盘
首个回滚演练复盘
```

建立周期性任务：

- 上游 release 监控；
- 依赖/签名库安全更新；
- 测试设备 OS 更新；
- parser fuzz；
- crash trend；
- ABI false-positive/false-negative；
- closure size trend；
- warmup profile 更新；
- 文档/runbook 演练。

每次 Unity 升级都视为新的 Runtime 兼容项目，至少重跑 Gate 1～4。

---

## 最终完成条件 / Release

只有全部满足才宣布 v0.1 正式可用：

- 四仓库 RC tag 和 compatibility lock 完整；
- 干净环境可复现安装、构建和测试；
- 需求追踪矩阵无缺口；
- P01：Internal 逻辑变更复用旧 Bundle；
- P02：Extensibility 反向闭包；
- P03：Contracts 完整反向闭包；
- Resource ABI 变化被阻止或正确重构资源；
- Assembly/Type/Reflection/AppDomain/Unity API 全部 active；
- 执行语义矩阵通过；
- Windows x64、Android ARM64 完整通过；
- feature-off 与 active 性能符合预算；
- 故障、OOM、崩溃和回滚演练通过；
- 安全、Runtime、Unity Resource、Operations review 通过；
- 真实项目垂直切片内部 QA 通过；
- kill switch 和 last-known-good 可用；
- 发布负责人签署 Go。

## 最终交付

```text
1. design.md
2. M00～M12开发计划和review记录
3. 四仓库版本tag
4. compatibility lock
5. HybridCLR Unity package
6. il2cpp_plus source fork/tag
7. Demo baseline和patch fixtures
8. 自动化测试与结果
9. 性能/内存报告
10. 安全报告
11. 符号与诊断说明
12. Build/Release/Rollback runbook
13. Known Limitations
14. 生产灰度与复盘记录
```
