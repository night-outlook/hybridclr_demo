# Milestone 08：HybridCLR Unity Editor、安装器与补丁构建集成

## 目标

把 M02-M07 的实验脚本和手工步骤集成进 `night-outlook/hybridclr_unity`，形成可供项目长期使用的标准工作流：

- Shadow Settings；
- 固定源码安装；
- baseline build；
- patch compile；
- closure package；
- Link/MethodBridge/AOT generic 生成；
- resource ABI；
- validator；
- 命令行 CI；
- 清晰菜单；
- 不破坏普通 HybridCLR hot update。

## 进入条件

- Gate 3A/3B 通过；
- runtime API 基本稳定；
- M02 tooling 已在 demo 验证；
- P01/P02/P03 patch 可手工构建；
- source pin 和 installer ADR 已批准。

## 设计原则

1. 普通 HotUpdate 与 Shadow 是并列模式。
2. Shadow baseline 一定进入 AOT Player。
3. 普通 `FilterHotFixAssemblies` 不移除 Shadow assemblies。
4. patch closure DLL来自一次 Unity target compile。
5. generator 输入只包含当前实际运行时 DLL。
6. 安装器固定 exact revision。
7. 所有菜单功能也必须提供无 UI 的 CI API。
8. 工具失败必须给出可执行修复建议。
9. package API 不直接依赖 demo 类型。
10. 上游目录改动最小，AssemblyShadow 功能尽量放新增目录。

## 任务 08.1：正式目录与 asmdef

在 `hybridclr_unity`：

```text
Runtime/AssemblyShadow/
Editor/AssemblyShadow/
├─ Settings/
├─ Installer/
├─ Metadata/
├─ Dependency/
├─ Hashing/
├─ Serialization/
├─ Build/
├─ Manifest/
├─ Validation/
├─ Generation/
├─ Diagnostics/
└─ Tests/
```

决定是否单独 asmdef：

```text
HybridCLR.AssemblyShadow.Runtime
HybridCLR.AssemblyShadow.Editor
```

推荐单独 asmdef：

- runtime API可独立裁剪；
- Editor 第三方 dnlib 依赖隔离；
- 普通 HybridCLR 用户不开启时少引入；
- 测试更清楚。

如果上游 package 结构限制单 asmdef，至少 namespace 独立：

```text
HybridCLR.AssemblyShadow
HybridCLR.Editor.AssemblyShadow
```

## 任务 08.2：Settings UI

Project Settings 页面分区：

```text
Enable Assembly Shadow
Shadow-capable assemblies
Fixed bootstrap assemblies
Extensibility whitelist
Explicit dependency config
Baseline output
Patch output
Resource ABI policy
Runtime source pins
Diagnostics level
```

即时验证：

- assembly name duplicate；
- 与 ordinary hotUpdate 重叠；
- bootstrap 与 shadow 重叠；
- asmdef 不存在；
- Internal dependency violation；
- Extensibility whitelist violation；
- output path invalid；
- source pin missing。

禁止保存无效配置，或至少在 build 前硬失败。

## 任务 08.3：修改 `SettingsUtil`

新增只读集合：

```csharp
ShadowAssemblyNames
ShadowAssemblyFiles
BootstrapAssemblyNames
RuntimeGenerationAssemblyNames
```

定义：

```text
RuntimeGenerationAssemblyNames(target, patchContext)
    = ordinary hot update
    + current shadow closure
```

不要修改现有：

```text
HotUpdateAssemblyNamesExcludePreserved
```

语义，避免上游行为回归。

## 任务 08.4：保护 `FilterHotFixAssemblies`

增加测试确保：

```text
ordinary hot update assemblies
    → 从Player过滤

shadow assemblies
    → 保留在Player

preserved ordinary hot update
    → 按上游规则
```

如果设置重叠：

```text
same assembly in hotUpdate and shadow
    → BuildFailedException
```

不要通过修改 filter 顺序解决重叠。

## 任务 08.5：Patch Compile Command

新增：

```text
HybridCLR/Assembly Shadow/Compile Patch Assemblies
```

API：

```csharp
ShadowCompileResult Compile(
    BuildTarget target,
    bool development,
    string outputDir);
```

内部调用：

```csharp
PlayerBuildInterface.CompilePlayerScripts(...)
```

输出：

```text
<patch-temp>/AllCompiledAssemblies/
```

然后由 closure builder选择 DLL。不要单独逐程序集调用 Roslyn，避免条件编译、Unity references 和 compiler options 不一致。

记录：

```text
target
scripting backend
api compatibility
define symbols
development flag
compiler response
compile result
```

`ScriptCompilationResult` 的错误必须转为 build failure。

## 任务 08.6：Baseline Build Command

新增：

```text
HybridCLR/Assembly Shadow/Build Baseline Metadata
```

必须绑定到实际 Player build snapshot。推荐流程：

```text
CompilePlayerScripts
→ Generate baseline metadata
→ Generate HybridCLR outputs
→ Build Player using same source state
```

为了防止源码在两步之间变化：

- 记录 source tree fingerprint；
- build 开始与结束校验；
- CI 中使用 clean checkout；
- local 若变动则 warning/fail。

Baseline output：

```text
HybridCLRData/AssemblyShadow/Baselines/<target>/<buildId>/
```

## 任务 08.7：Patch Build Command

新增：

```text
HybridCLR/Assembly Shadow/Build Patch
```

对话框/参数：

```text
Baseline manifest
Patch ID
Target
Development/Release
Explicit changed roots optional
Bundle output/catalog optional
Signing profile
```

执行：

```text
compile
→ analyze
→ closure
→ policy validate
→ resource ABI
→ generators
→ package
→ verify package by reopening
```

输出：

```text
Patches/<patchId>/
├─ manifest.json
├─ manifest.sig
├─ assemblies/
├─ pdb/
├─ warmup/
├─ resources/（可选）
├─ reports/
└─ patch.index
```

## 任务 08.8：Generator 集成

逐个改造并加测试：

### Link Generator

扫描：

```text
ordinary hot update
+ shadow closure
```

避免 baseline AOT 类型因补丁反射/泛型被裁剪。

### MethodBridge

输入 closure DLL，生成：

- AOT → Interpreter；
- Interpreter → AOT；
- value-type signatures；
- delegate；
- virtual/interface；
- reverse P/Invoke。

### AOTGenericReference

扫描 closure，收集新增 AOT generic instantiations。

### Il2CppDef

确保 Shadow feature native 宏和配置进入生成。

### Strip AOT DLL

仍用于补充元数据；不要把 shadow patch DLL误当 AOT stripped source。

每个 generator report 中标记 assembly source：

```text
OrdinaryHotUpdate
ShadowClosure
```

## 任务 08.9：安装器固定 revision

扩展：

```text
InstallerController
hybridclr_version.json或新的source profile
```

支持：

```text
Repo URL
Exact revision
Optional branch for display
Local source path
Expected tree hash
```

安装日志：

```json
{
  "unity": "2022.3.62f2",
  "hybridclr": {
    "url": "...night-outlook/hybridclr",
    "revision": "..."
  },
  "il2cppPlus": {
    "url": "...night-outlook/il2cpp_plus",
    "revision": "..."
  },
  "assemblyShadowAbi": 1
}
```

复制后写：

```text
HybridCLRData/LocalIl2CppData-*/assembly-shadow-source-lock.json
```

Player build 前检查 lock 与 Project source pins一致。

## 任务 08.10：Installer 本地开发模式

支持：

```text
UseLocalSource
hybridclr path
il2cpp_plus path
```

流程：

- 检查 git root；
- 读取 HEAD；
- 检查 dirty；
- 默认拒绝 dirty，开发选项可允许但写 tree hash；
- copy 到 LocalIl2CppData；
- 验证关键文件；
- 生成 lock。

不要通过 symlink 直接让 Unity build 使用工作区，除非平台稳定验证；复制更可重复。

## 任务 08.11：CLI API

新增 public Editor API：

```csharp
AssemblyShadowBuildPipeline.BuildBaseline(options);
AssemblyShadowBuildPipeline.BuildPatch(options);
AssemblyShadowBuildPipeline.Validate(options);
AssemblyShadowBuildPipeline.BuildDemoFixtures(options);
```

命令行入口：

```text
AssemblyShadowCi.BuildBaseline
AssemblyShadowCi.BuildPatch
AssemblyShadowCi.RunEditorTests
```

支持：

```bash
Unity \
  -batchmode \
  -quit \
  -projectPath ... \
  -executeMethod AssemblyShadowCi.BuildPatch \
  -shadowBaseline ... \
  -shadowPatchId P03 \
  -buildTarget StandaloneWindows64 \
  -logFile ...
```

参数解析失败必须退出非零码。

## 任务 08.12：报告

每次 build 输出：

```text
summary.md
dependency-graph.json
changed-roots.json
closure.json
semantic-diff.json
resource-abi-diff.json
generator-inputs.json
source-pins.json
validation.json
```

`summary.md` 至少回答：

```text
为什么这些程序集进入closure
哪些程序集仍AOT
是否需要重构Bundle
哪些bridge/generic新增
是否可以发布
```

## 任务 08.13：Package 兼容与版本

在 package 增加：

```text
Assembly Shadow Runtime ABI version
Manifest schema version
Resource ABI schema version
Semantic hash schema version
```

任何不兼容修改：

- bump 版本；
- baseline/patch mismatch 时拒绝；
- 提供 migration 文档；
- 不靠字符串日志猜版本。

## 任务 08.14：Demo 迁移到正式 package API

删除或禁用 demo 中重复实现：

- 临时 closure builder；
- 临时 manifest；
- prototype runtime API；
- 手工 patch copy。

Demo 只保留：

- assembly fixtures；
- resource fixtures；
- test runner；
- CI wrapper；
- expected results。

## Editor 测试

### T08-01 配置重叠

HotUpdate + Shadow 同名，失败。

### T08-02 Shadow AOT 保留

Player assembly filter 输出包含三个 AssemblyA。

### T08-03 Patch P01

正式 command 只打包 Internal。

### T08-04 Patch P02

闭包正确，generator inputs正确。

### T08-05 Patch P03

full business closure；所有 DLL 同 compile snapshot。

### T08-06 P05

Resource ABI变化，DLL-only失败。

### T08-07 Source pin mismatch

build 失败并给出 reinstall 命令。

### T08-08 CLI

batchmode exit code和报告正确。

### T08-09 ordinary HybridCLR

普通 hot update sample 仍通过。

## Code Review 检查点

- 是否保持 Shadow AOT；
- 是否与 ordinary hot update 解耦；
- generator input 是否当前 closure；
- installer 是否 exact revision；
- baseline/patch 是否同 target/defines；
- CLI 是否无 UI；
- reports 是否可解释 closure；
- source dirty handling 是否明确；
- package 版本是否管理 ABI；
- demo 是否不再复制 package 逻辑。

## 完成标准

- T08-01 至 T08-09 通过；
- 一条 CLI 命令可生成 P01/P02/P03 patch；
- installer 可重复安装 fork runtime；
- source pin mismatch 会阻止 build；
- ordinary HybridCLR 回归通过；
- 独立 review 通过并创建 M08 tag。
