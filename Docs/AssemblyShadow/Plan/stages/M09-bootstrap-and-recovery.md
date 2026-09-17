# M09 · 生产启动、签名、健康确认与分状态恢复

状态：待执行。本文不表示代码已修改或测试已通过。

前置：M08B。关联 findings：ASR-008, ASR-011, ASR-013。

所有“新增”文件名是建议实现位置，不是对当前仓库存在性的声明。现有路径均以 `source-baseline.json` 及本地固定 checkout 核对。执行前读取主设计 `../design.revised.md` 与验证矩阵 `../validation-matrix.md`。


## 目标

实现真正的固定 AOT startup coordinator。M07Probe 是测试边界，不直接复制为生产下载器。所有安全输入/恢复决策都可故障注入，任何失败不加载混合代码/资源世界。

## 实施步骤

### 1. 输入与可信边界

嵌入 baseline build/runtime/capability 身份和验证公钥；对 manifest 大小/schema/重复字段/未知关键字段/路径作有界解析，再验证签名和文件 size/hash。使用项目已审核密码组件或经过 IL2CPP 平台验证的实现，不自造密码算法。私钥不进 Player。

### 2. 完整版本集合

A/B 或内容寻址 slot 中保存完整目标 closure、普通热更集合和资源/catalog。网络可下载差异，激活只能选择一个完整 ready 集合。禁止在 Commit 前注册业务资源或由 DI/SDK 提前反射业务类型。

### 3. 激活状态机

按准备、选择/验证、Stage/Validate、单次 publish、warmup、资源、入口、健康确认执行。配置候选身份早于可能访问业务的步骤；没有补丁时冻结 baseline 选择。API 结果同时记录 native state/active generation。

### 4. RecoveryDisposition

实现 R01 的表：Begin 前失败无需 Abort；Staging/Staged/Validated 中仅已知安全拒绝可 Abort 后 baseline；Failed 默认重启；FailedAfterCommit 不得原地 baseline。Abort 返回非 Success 时不能吞掉。用实际 state 而非方法名称推断是否已发布。

### 5. Poison 与异常捕获

协调器捕获错误后先标记 failed attempt，再停止业务入口/资源请求；受支持 native/Interpreter 业务入口保留 poison 约束。诊断和必要固定 AOT 退出逻辑可执行。reverse callback 使用不跨 ABI 抛异常的 fatal 路径。不能声称一个状态 enum 已经停止了所有线程。

### 6. 存储与崩溃恢复

临时写、校验、持久化、原子 pointer switch 和 install.complete 有清楚顺序。每个边界模拟断电/进程结束，下一进程忽略未完成 slot。LKG 同时选择其代码与资源；健康判据是定义好的业务 readiness，而非 Commit 成功。

### 7. 撤销与重放策略

定义已撤销 patch、旧 baseline、签名轮换、下载重试、容量/磁盘不足和离线策略。日志不泄露密钥。补丁输入在验真后保持受控不可变；Stage 期间调用者不得并发修改 byte[] 的契约写进 developer guide。

## 验收

对下载、签名、每个 Stage、Validate、publish 前后、module initializer、warmup、资源恢复、入口及健康写入逐点注入失败。每次检查新进程选择、slot 完整性、是否产生业务副作用和原生状态。错误路径可记录为正确拒绝，但不能用返回零的 harness 代替真正故障发生。


## 独立审查与交付

按 design→plan→implementation→evidence 顺序独立 review。审查者检查真实调用链和反例，不只检查断言文本或复述作者报告。每项 finding 记录 fixed/not-fixed/not-reproduced/scope-decision，并链接新测试和 exact executable pairing。

交付本阶段变更清单、源版本/产物哈希、测试命令与原始结果、剩余限制、回滚方式。失败不覆盖历史 M00–M07 evidence，不用 `--allow-incomplete`、`--skip-demo-source` 或修改预期值代替通过。没有运行的检查明确写 NotRun。


---

## Retained Detailed Requirements

The revised requirements above take precedence over conflicting legacy detail.

# Milestone 09：Bootstrap、下载、签名、原子发布与回滚

## 目标

将已验证的 Shadow runtime 接入真实启动流程，保证补丁下载、校验、提交和失败恢复可用于生产环境。核心输出：

- 固定 AOT Bootstrap；
- 补丁存储布局；
- Manifest 签名；
- 原子安装；
- last-known-good；
- Commit 前回退；
- Commit 后崩溃恢复；
- 启动成功确认；
- 远程禁用与诊断。

## 进入条件

- M08 正式 patch package 可生成；
- runtime transaction 已稳定；
- P01/P02/P03 可用 package 加载；
- Resource ABI policy 已落实；
- Bootstrap isolation validator 通过。

## 不变量

1. Bootstrap 不引用任何 Shadow 业务具体类型。
2. Shadow Commit 前不加载业务资源。
3. 下载文件先写临时目录，完整校验后原子切换。
4. Manifest 签名覆盖所有 DLL、PDB、资源和关键元数据。
5. Commit 前错误可在当前进程回退 AOT。
6. Commit 后错误不在当前进程继续 baseline；退出并在下次启动回退。
7. 每个 patch 与 exact baseline build ID 绑定。
8. 补丁可被远程撤销。
9. 不允许半套 closure。
10. 补丁和资源 catalog 是一个原子版本单元。

## 任务 09.1：固定 Bootstrap 程序集

在 demo，后续可提取通用 sample：

```text
Assets/AssemblyShadowDemo/Bootstrap/
├─ AssemblyShadowDemo.Bootstrap.asmdef
├─ ShadowBootstrapBehaviour.cs
├─ ShadowStartupCoordinator.cs
├─ ShadowPatchRepository.cs
├─ ShadowPatchVerifier.cs
├─ ShadowPatchInstaller.cs
├─ ShadowPatchActivator.cs
├─ ShadowPatchHealthStore.cs
├─ ShadowBusinessEntryInvoker.cs
└─ ShadowBootstrapLog.cs
```

asmdef 只引用：

```text
UnityEngine
UnityWebRequest相关模块
HybridCLR.AssemblyShadow.Runtime
必要的系统库
```

不得引用：

```text
AssemblyA.*
任何业务Consumer
业务资源程序集
```

## 任务 09.2：启动状态机

```text
Boot
→ LoadEmbeddedBaselineManifest
→ RegisterCandidates
→ ReadLocalPatchState
→ SelectCandidate
→ VerifyLocalCandidate
→ OptionalDownload
→ InstallCandidateAtomically
→ BeginShadowTransaction
→ StageClosure
→ Validate
→ Commit
→ Warmup
→ LoadBusinessResources
→ InvokeBusinessEntry
→ MarkStartupHealthy
```

状态持久化：

```text
NoPatch
Downloaded
Verified
Ready
CommitStarted
Committed
BusinessStarted
Healthy
FailedPreCommit
FailedPostCommit
Bad
```

每次状态写入必须原子、可崩溃恢复。

## 任务 09.3：磁盘布局

建议：

```text
PersistentDataPath/AssemblyShadow/
├─ baseline/
│  └─ embedded-build-id.txt
├─ slots/
│  ├─ slot-a/
│  │  ├─ manifest.json
│  │  ├─ manifest.sig
│  │  ├─ assemblies/
│  │  ├─ resources/
│  │  └─ install.complete
│  └─ slot-b/
├─ state/
│  ├─ active-slot.json
│  ├─ health.json
│  ├─ boot-attempt.json
│  └─ bad-patches.json
├─ temp/
└─ logs/
```

A/B slot 能避免原地覆盖。

## 任务 09.4：Manifest 签名

建议使用成熟算法和库：

```text
Ed25519
```

或项目现有签名系统。签名输入是 canonical manifest，manifest 中列出每个文件：

```text
relative path
size
SHA-256
role
```

校验顺序：

1. 读取 manifest，限制大小；
2. schema/version；
3. 签名；
4. baseline build ID；
5. platform/architecture；
6. runtime ABI；
7. 每个文件 hash/size；
8. closure；
9. resource catalog；
10. expiration/revocation。

不要信任文件名推断 assembly identity；Stage 仍从 DLL 内读取。

私钥只在 CI/发布环境；Player 仅含公钥。

## 任务 09.5：下载与恢复

支持：

- range/resume，若现有下载框架支持；
- 临时文件；
- 超时；
- 存储空间检查；
- hash 失败重试上限；
- CDN 缓存；
- 代理/离线；
- 下载被杀进程后清理。

下载完成后：

```text
verify
→ write install.complete
→ fsync
→ atomic rename/switch slot
```

未完成 slot 不参与启动选择。

## 任务 09.6：补丁选择

输入：

```text
embedded baseline
local last-known-good
local candidate
remote policy
bad patch list
```

规则：

1. remote kill switch 优先；
2. candidate 若与 baseline 不兼容，忽略并删除/隔离；
3. candidate 曾发生 post-commit failure，标为 bad；
4. last-known-good 优先于未验证 candidate，策略可配置；
5. 无有效 patch 使用 baseline AOT。

输出选择理由到日志。

## 任务 09.7：Stage/Commit 接入

按 Manifest `loadOrder` 读取 DLL：

```csharp
ConfigureCandidates(...)
BeginTransaction(...)
foreach assembly in loadOrder:
    StageAssembly(dll, pdb)
ValidateTransaction()
CommitTransaction()
```

每步错误分类：

### Pre-commit

- 签名；
- Hash；
- missing closure；
- bad image；
- baseline use；
- runtime ABI；
- Resource ABI。

处理：

```text
Abort
→ mark candidate failed-precommit
→ current process continue baseline
```

前提：baseline 业务尚未启动，可直接进入 baseline business entry。

### Post-commit

- module initializer；
- warmup；
- business entry；
- early business health check。

处理：

```text
mark commit/post-commit failure
→ flush logs
→ terminate/restart
→ next boot skip bad candidate
```

不要在同进程调用 baseline business entry。

## 任务 09.8：业务入口

Manifest：

```text
entryAssembly
entryType
entryMethod
```

入口签名固定，不含业务类型：

```csharp
public static int Start(string bootstrapContextJson);
```

或：

```csharp
public static byte[] Start(byte[] context);
```

Bootstrap：

1. `Assembly.Load(entryAssembly)`；
2. `GetType(entryType)`；
3. `GetMethod`；
4. 验证 static/signature；
5. 创建 delegate 或 Invoke 一次；
6. 返回状态码。

入口方法由 active Assembly resolver 保证拿到 patch 或 AOT baseline。

基线模式也通过相同字符串入口调用，使 Bootstrap 不静态引用业务。

## 任务 09.9：Warmup 与资源加载边界

Commit 后：

```text
module initializer
→ warmup manifest
→ explicit entry warmup
→ mark RuntimeReady
→ initialize Addressables/catalog
→ load business scene
```

若 Resource ABI 要求新 Bundle：

- 验证 active resource slot；
- DLL 和 catalog patch ID 一致；
- 不允许 fallback old resource；
- 若资源缺失，属于 post-commit failure，退出并下次回退整个 patch。

## 任务 09.10：健康确认

两级确认：

### Runtime Ready

- Commit；
- initializer；
- warmup；
- entry type resolve。

### Business Healthy

- 首个业务 Scene 完成；
- 关键服务初始化；
- 至少 N 帧；
- 可选后端 handshake；
- 无 fatal exception。

只有 Business Healthy 后：

```text
candidate → last-known-good
bootAttempt reset
```

若进程在 Healthy 前连续崩溃：

```text
attempt count >= threshold
→ patch bad
→ rollback
```

阈值建议 1～3 次，开发与生产可不同。

## 任务 09.11：崩溃恢复

启动时检查：

```text
上次active patch
上次状态CommitStarted/Committed/BusinessStarted
无Healthy marker
```

判定 post-commit crash。

保存：

```text
patch ID
boot session ID
last state
native log path
managed log path
resolver diagnostics
```

将 patch 加入 bad list，并切换 slot。

如果 baseline 也崩溃，不无限重启；进入安全错误界面或上报。

## 任务 09.12：远程禁用

Remote policy：

```json
{
  "disabledPatchIds": ["..."],
  "minimumBaselineBuild": "...",
  "forceBaseline": false,
  "reason": "..."
}
```

签名验证。离线时使用缓存 policy，但设置过期策略。

kill switch 在 Stage 前执行。

## 任务 09.13：安全限制

- Manifest/DLL 最大大小；
- assembly count 上限；
- name length；
- path traversal 防护；
- zip bomb 防护；
- JSON depth；
- PDB production 默认不下发；
- 错误日志不泄露 token/URL；
- 不从不可信路径 `Assembly.Load`；
- 公钥轮换版本；
- 防 downgrade，按项目需要；
- patch ID replay 策略；
- TLS 由现有网络层保证。

## 任务 09.14：故障注入

Demo 支持 command line：

```text
--shadow-fail-after-stage=N
--shadow-fail-before-commit
--shadow-fail-module-init
--shadow-fail-warmup
--shadow-fail-business-start
--shadow-crash-before-healthy
--shadow-corrupt-dll
--shadow-corrupt-manifest
--shadow-disable-patch
```

验证 slot 和 rollback。

## Demo 测试

### T09-01 正常 P01

candidate → committed → healthy → last-known-good。

### T09-02 签名错误

不 Stage，当前进程 baseline。

### T09-03 DLL hash 错误

不 Stage，baseline。

### T09-04 closure missing

Validate失败，Abort，baseline。

### T09-05 baseline use

Commit前失败，baseline。

### T09-06 initializer异常

退出；下次启动标 bad，baseline。

### T09-07 业务入口异常

退出；下次回退。

### T09-08 被杀进程

Commit前/后/Healthy前分别验证。

### T09-09 DLL+Bundle

P05 新 DLL 和新 Bundle 原子切换。

### T09-10 kill switch

已下载 patch 不激活。

## Code Review 检查点

- Bootstrap 是否零业务引用；
- 签名是否覆盖所有文件；
- 是否原子 slot；
- pre/post commit 策略是否区分；
- post-commit 是否错误继续 baseline；
- healthy marker 是否可靠；
- 崩溃循环是否可停止；
- Resource 与 DLL 是否同版本；
- 私钥是否不进入仓库/Player；
- 所有失败是否可诊断。

## 完成标准

- T09-01 至 T09-10 通过；
- A/B slot 和 last-known-good 工作；
- post-commit crash 下一次自动回退；
- 签名/hash/ABI错误安全拒绝；
- Bootstrap isolation validator通过；
- 独立 review 通过并创建 M09 tag。
