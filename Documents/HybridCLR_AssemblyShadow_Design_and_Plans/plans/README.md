# HybridCLR Assembly Shadow 开发计划索引

本目录将 `design.md` 拆成 13 个可独立执行、独立 review、具有明确进入条件与完成条件的 Milestone。

## 执行原则

- 严格按顺序执行；除明确标注可并行的任务外，不跳阶段。
- 每个 Milestone 建议分别创建分支和 tag。
- 每个 Milestone 完成后进行一次独立 code review，并保存 review 记录。
- 只有 Milestone 01 的 Prefab/Scene 可行性闸门通过后，才进入完整实现。
- 所有运行时正确性验收必须在 IL2CPP Player 中完成；Editor 模拟只用于工具测试。
- 本地已有三个仓库，但还需为 Unity 2022 `libil2cpp` 改动准备 `il2cpp_plus` fork 或补丁层。
- `main` 是移动分支。M00 必须记录并固定四个仓库的确切 commit SHA。
- MVP 每次进程只允许提交一个 Shadow 补丁，补丁变化必须重启应用。

## Milestone 列表

| Milestone | 文档 | 核心输出 | 闸门 |
|---:|---|---|---|
| 00 | `milestone-00-repository-baseline.md` | 固定源码、第四仓库、可重复原生构建 | Gate 0 |
| 01 | `milestone-01-demo-poc-feasibility.md` | 旧 AssetBundle + 同名 Shadow 最小 PoC | **Gate 1 / Go-No-Go** |
| 02 | `milestone-02-dependency-manifest-abi.md` | 依赖闭包、语义 Hash、Manifest、Resource ABI | 工具基础 |
| 03 | `milestone-03-native-transaction-staging.md` | Native 状态机、两阶段 Stage、InternalCall | 事务基础 |
| 04 | `milestone-04-assembly-reference-resolution.md` | Assembly、AssemblyRef、AppDomain 活动解析 | Assembly 一致性 |
| 05 | `milestone-05-type-reflection-resolution.md` | Image/Class/Type/Reflection/缓存统一 | Gate 2 |
| 06 | `milestone-06-execution-semantics.md` | 静态状态、虚表、接口、delegate、泛型、预热 | Gate 3A |
| 07 | `milestone-07-unity-assets-and-apis.md` | Add/GetComponent、ScriptableObject、Prefab/Scene | Gate 3B |
| 08 | `milestone-08-editor-build-integration.md` | Unity Editor 构建、安装器、生成器集成 | 生产工具 |
| 09 | `milestone-09-bootstrap-security-rollback.md` | 下载、签名、原子发布、崩溃回滚 | 生产启动 |
| 10 | `milestone-10-automated-test-matrix.md` | Editor + IL2CPP 自动测试和平台矩阵 | Gate 4A |
| 11 | `milestone-11-performance-hardening-rebase.md` | 性能、故障注入、诊断、升级策略 | Gate 4B |
| 12 | `milestone-12-release-acceptance.md` | 发布标准、试运行和最终验收 | Release |

## 推荐分支

```text
night-outlook/hybridclr
    feature/assembly-shadow-runtime

night-outlook/hybridclr_unity
    feature/assembly-shadow-tooling

night-outlook/il2cpp_plus
    feature/unity-2022-assembly-shadow

night-outlook/hybridclr_demo
    feature/assembly-shadow-demo
```

## 每个 Milestone 的标准交付物

```text
1. 代码提交
2. 修改文件清单
3. 新增API清单
4. 自动测试结果
5. 手工测试步骤与结果
6. 已知限制
7. 性能或内存数据（适用时）
8. 独立Code Review记录
9. 对design.md的偏差说明
10. 下一Milestone进入判断
```

## 建议本地目录

以下仅为示例，执行时用本机实际目录替换：

```text
<WORKSPACE>/
├─ hybridclr/
├─ hybridclr_unity/
├─ hybridclr_demo/
└─ il2cpp_plus/
```

统一设置：

```bash
export SHADOW_WORKSPACE=<WORKSPACE>
export HYBRIDCLR_REPO=$SHADOW_WORKSPACE/hybridclr
export HYBRIDCLR_UNITY_REPO=$SHADOW_WORKSPACE/hybridclr_unity
export HYBRIDCLR_DEMO_REPO=$SHADOW_WORKSPACE/hybridclr_demo
export IL2CPP_PLUS_REPO=$SHADOW_WORKSPACE/il2cpp_plus
```

Windows PowerShell 可使用：

```powershell
$env:SHADOW_WORKSPACE = "D:\Work\AssemblyShadow"
$env:HYBRIDCLR_REPO = "$env:SHADOW_WORKSPACE\hybridclr"
$env:HYBRIDCLR_UNITY_REPO = "$env:SHADOW_WORKSPACE\hybridclr_unity"
$env:HYBRIDCLR_DEMO_REPO = "$env:SHADOW_WORKSPACE\hybridclr_demo"
$env:IL2CPP_PLUS_REPO = "$env:SHADOW_WORKSPACE\il2cpp_plus"
```

## 统一完成标准

只有满足下列全部条件才能宣布方案完成：

- P01：Internal 方法体变化，旧 Prefab Bundle 不重构且执行补丁逻辑；
- P02：Extensibility 变化，所有反向依赖程序集 Interpreter；
- P03：Contracts 变化，完整业务闭包 Interpreter；
- 所有 Assembly/Type/Reflection/AppDomain 查询只看到 active 逻辑世界；
- AddComponent/GetComponent/ScriptableObject 路径正确；
- baseline AOT 类型在 Commit 前被使用时能被阻止并定位；
- Resource ABI 变化时 DLL-only 构建被拒绝；
- 缺失闭包、错误版本、错误签名均安全回退；
- Windows x64 和 Android ARM64 IL2CPP 自动测试通过；
- 未启用 Shadow 时，上游 HybridCLR 回归测试无明显退化；
- 无未解释的 native crash、类型错配或静默数据破坏。
