# Milestone 00：仓库、源码固定与可重复基线

## 目标

建立可重复、可回滚、可 bisect 的四仓库开发基线，确认 Unity 2022.3.62f2 的 HybridCLR 原生链路可正常安装和构建。此阶段不实现 Shadow 功能。

## 进入条件

- 本地已 clone：
  - `night-outlook/hybridclr`
  - `night-outlook/hybridclr_unity`
  - `night-outlook/hybridclr_demo`
- 已安装 Unity 2022.3.62f2，并包含目标平台 IL2CPP Build Support。
- 至少有一个可执行的 IL2CPP 目标平台，推荐 Windows x64。

## 关键判断

`hybridclr_unity` 安装器不仅使用 `hybridclr`，还会取得 `il2cpp_plus` 并将前者放入后者的 `libil2cpp/hybridclr`。Assembly、MetadataCache、Image 和 Reflection 的核心改动必须进入 `il2cpp_plus`。因此本 Milestone 必须建立第四个源码真相。

## 任务 00.1：记录当前工作区状态

在每个现有仓库执行：

```bash
git status --short
git remote -v
git branch --show-current
git rev-parse HEAD
git log -1 --date=iso-strict --format="%H%n%ad%n%s"
```

保存到：

```text
hybridclr_demo/Docs/AssemblyShadow/Baseline/source-pins.md
```

内容至少包括：

```text
Repository
Origin URL
Upstream URL
Branch
Commit SHA
Commit Date
Dirty State
Unity Version
Host OS
Compiler/SDK
```

要求：

- 若存在未提交修改，先创建独立备份分支；
- 不允许在 dirty working tree 上开始 runtime 改造；
- 不使用“main 最新”作为可复现版本描述。

## 任务 00.2：创建 `il2cpp_plus` fork

推荐流程：

1. 在 GitHub fork：
   ```text
   focus-creative-games/il2cpp_plus
       → night-outlook/il2cpp_plus
   ```
2. clone Unity 2022 对应分支：
   ```bash
   git clone --branch v2022-8.14.0 \
     https://github.com/night-outlook/il2cpp_plus.git
   ```
3. 添加 upstream：
   ```bash
   git remote add upstream \
     https://github.com/focus-creative-games/il2cpp_plus.git
   ```
4. 创建开发分支：
   ```bash
   git switch -c feature/unity-2022-assembly-shadow
   ```
5. 添加说明文件：
   ```text
   ASSEMBLY_SHADOW_FORK.md
   ```

说明文件写明：

- 基于哪个 upstream branch/commit；
- 为什么 fork；
- 改动只面向 Unity 2022.3；
- 与 HybridCLR runtime commit 的配对关系；
- rebase 流程；
- 禁止直接 merge 无审查的上游大版本。

若暂时不能建立远程 fork，可先 clone upstream 并创建本地分支，但在 M03 前必须迁移到独立 fork。

## 任务 00.3：建立四仓库配对清单

在 demo 新增：

```text
ProjectSettings/AssemblyShadowSourcePins.json
```

建议结构：

```json
{
  "schemaVersion": 1,
  "unityVersion": "2022.3.62f2",
  "hybridclr": {
    "url": "https://github.com/night-outlook/hybridclr",
    "revision": "<sha>"
  },
  "hybridclrUnity": {
    "url": "https://github.com/night-outlook/hybridclr_unity",
    "revision": "<sha>"
  },
  "il2cppPlus": {
    "url": "https://github.com/night-outlook/il2cpp_plus",
    "branch": "feature/unity-2022-assembly-shadow",
    "revision": "<sha>"
  },
  "demo": {
    "url": "https://github.com/night-outlook/hybridclr_demo",
    "revision": "<sha>"
  }
}
```

该文件属于构建输入。后续 Patch Manifest 必须包含至少：

```text
Unity exact version
hybridclr revision
il2cpp_plus revision
shadow runtime ABI version
```

## 任务 00.4：安装器最小改造方案评审

先阅读并记录：

```text
hybridclr_unity/Editor/Installer/InstallerController.cs
hybridclr_unity/Data~/hybridclr_version.json
hybridclr_unity/Editor/Settings/HybridCLRSettings.cs
```

输出 ADR：

```text
hybridclr_demo/Docs/AssemblyShadow/ADR/
    ADR-0001-il2cpp-plus-source-of-truth.md
```

ADR 必须选择：

### 选择 A：安装器直接 clone fork

新增配置：

```text
hybridclrRepoURL
hybridclrRevision
il2cppPlusRepoURL
il2cppPlusRevision
```

安装流程：

```text
clone --no-checkout
→ checkout exact revision
→ verify HEAD
→ copy hybridclr into libil2cpp/hybridclr
```

### 选择 B：本地源码安装模式

配置本地路径：

```text
hybridclrLocalPath
il2cppPlusLocalPath
```

安装器复制当前工作树到 `HybridCLRData/LocalIl2CppData-*`，并把 SHA 写入安装记录。

推荐最终同时支持：

- CI：remote URL + exact revision；
- 本地开发：local path + SHA 检查。

禁止仅通过 branch 名安装，因为 branch 会移动。

## 任务 00.5：建立干净的普通 HybridCLR 基线

在 `hybridclr_demo` 中：

1. 将 package manifest 指向本地 `hybridclr_unity`：
   ```json
   "com.code-philosophy.hybridclr":
       "file:../../hybridclr_unity"
   ```
   实际相对路径按本地目录调整。
2. 打开 Unity，确认 package 可导入。
3. 配置安装器使用固定源码。
4. 执行 HybridCLR 安装。
5. 验证：
   ```text
   HybridCLRData/LocalIl2CppData-*/il2cpp/libil2cpp/hybridclr
   ```
   内容 commit 与 pin 相符。
6. 暂时创建一个普通、非 Shadow 的最小 HotUpdate asmdef。
7. 执行：
   ```text
   HybridCLR/Generate/All
   ```
8. 构建 IL2CPP Player。
9. 运行并验证普通热更 DLL 可加载和执行。

这一步用于证明后续问题来自 Shadow 改动，而不是安装或环境错误。

## 任务 00.6：建立原生构建可观察性

为开发构建打开：

- Development Build；
- Script Debugging，必要时开启；
- 原生符号；
- Player 日志；
- HybridCLR DEBUG 宏，按需开启；
- Windows 上生成 PDB；
- Android 上保留 `libil2cpp.so` 符号映射。

记录原生构建产物位置：

```text
Library/Bee/...
Library/Il2cppBuildCache/...
<Build>/.../GameAssembly.dll
<Build>/.../libil2cpp.so
```

建立脚本：

```text
hybridclr_demo/Tools/AssemblyShadow/
├─ print-source-pins.ps1
├─ print-source-pins.sh
├─ clean-il2cpp-cache.ps1
├─ clean-il2cpp-cache.sh
└─ verify-installed-runtime.py
```

`verify-installed-runtime.py` 至少校验：

- installed hybridclr 文件存在；
- installed source revision marker 一致；
- `AssemblyShadow` 宏状态；
- Unity 版本；
- package revision；
- 目标平台。

## 任务 00.7：定义编译开关

在 `il2cpp_plus` 增加规划但暂不启用：

```cpp
#ifndef HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 0
#endif
```

要求：

- 默认关闭；
- 关闭时生成代码和原有行为完全一致；
- 后续所有 Hook 都放在该宏或轻量 no-op API 后；
- 构建脚本能分别构建 OFF/ON 两种模式。

可在 HybridCLR 生成的配置头或 Unity Player 编译定义中控制，但不要让业务 C# 宏成为 native 真相来源。

## 任务 00.8：建立分支与提交策略

建议：

```text
hybridclr:
  feature/assembly-shadow-runtime

hybridclr_unity:
  feature/assembly-shadow-tooling

il2cpp_plus:
  feature/unity-2022-assembly-shadow

hybridclr_demo:
  feature/assembly-shadow-demo
```

每个 Milestone 最少一个 tag：

```text
assembly-shadow-m00-baseline
assembly-shadow-m01-poc
...
```

跨仓库改动必须在 demo 的 pin 文件中同步更新，避免只有某个仓库知道配对关系。

## 验证

### 自动检查

```bash
python Tools/AssemblyShadow/verify-installed-runtime.py
```

期望：

```text
[PASS] Unity version
[PASS] hybridclr source revision
[PASS] il2cpp_plus source revision
[PASS] HybridCLR installed
[PASS] Shadow feature disabled
```

### 手工检查

- 普通 HybridCLR HotUpdate Demo 可运行；
- 未启用 Shadow 时 `Assembly.Load`、Prefab 和反射行为与上游一致；
- 清理 IL2CPP cache 后可完整重构；
- 重复安装得到一致源码。

## Code Review 检查点

- 是否固定 exact SHA，而非只记录 branch；
- 是否明确新增 `il2cpp_plus` 源码真相；
- 安装器是否可验证复制内容；
- 是否存在对上游行为的无关修改；
- Shadow 宏关闭时是否零行为变化；
- demo 是否仍是可构建的 Unity 2022.3.62f2 工程。

## 完成标准

- 四仓库 commit pin 已保存；
- `il2cpp_plus` fork/本地分支已建立；
- 安装器能安装固定 runtime 源码；
- 普通 HybridCLR IL2CPP Player 测试通过；
- Shadow 编译开关存在且默认关闭；
- 基线 tag 已创建；
- 独立 review 通过。

## 失败处理

若普通 HybridCLR 基线无法通过：

- 不开始 M01；
- 清理 Unity Library 与 HybridCLRData 后重试；
- 核对 Unity exact patch version；
- 核对 `hybridclr` main 与 Unity 2022 `il2cpp_plus` branch 的兼容性；
- 必要时先把 runtime pin 到已知兼容 tag，再逐步 rebase 到 main；
- 将兼容性差异写入 ADR，而不是在 Shadow 代码中绕过。
