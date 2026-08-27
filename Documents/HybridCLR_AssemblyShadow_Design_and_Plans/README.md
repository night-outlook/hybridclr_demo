# HybridCLR Assembly Shadow 设计与开发计划

本交付用于在 Unity 2022.3 + HybridCLR fork 上实现：

```text
AOT baseline
    +
same-name Interpreter Assembly Shadow
    +
reverse-dependency HotUpdate Closure
```

业务程序集示例：

```text
AssemblyA.Contracts
AssemblyA.Implementation.Extensibility
AssemblyA.Implementation.Internal
```

当一个程序集变化时，该程序集及所有直接/间接依赖它的程序集在下一次应用进程启动中整体切换为 Interpreter；闭包外程序集继续 AOT。

## 文件

```text
design.md
plans/
├─ README.md
├─ milestone-00-repository-baseline.md
├─ milestone-01-demo-poc-feasibility.md
├─ milestone-02-dependency-manifest-abi.md
├─ milestone-03-native-transaction-staging.md
├─ milestone-04-assembly-reference-resolution.md
├─ milestone-05-type-reflection-resolution.md
├─ milestone-06-execution-semantics.md
├─ milestone-07-unity-assets-and-apis.md
├─ milestone-08-editor-build-integration.md
├─ milestone-09-bootstrap-security-rollback.md
├─ milestone-10-automated-test-matrix.md
├─ milestone-11-performance-hardening-rebase.md
└─ milestone-12-release-acceptance.md
```

## 执行顺序

1. 先阅读 `design.md`。
2. 阅读 `plans/README.md` 中的 Gate 和统一完成标准。
3. 严格按 M00 → M12 执行。
4. M01 的旧 Prefab/Scene AssetBundle PoC 是 Go/No-Go 闸门；未通过前不要进入完整改造。
5. 每个 Milestone 单独分支、测试、review 和记录偏差。
6. 本地执行时先把文档中的 `<WORKSPACE>` 替换为实际路径。

## 关键前提

现有三个本地仓库不足以单独实现全部 Shadow 路径。Unity 2022 的 Assembly、MetadataCache、Class、Reflection 等核心解析位于 `il2cpp_plus/libil2cpp`，因此 M00 要求增加：

```text
night-outlook/il2cpp_plus
```

或在 PoC 阶段由 `hybridclr_unity` 维护等价补丁集。长期维护推荐独立 fork。

## 关键限制

- 所有业务程序集都可 Shadow，但仍需固定的最小 AOT Bootstrap。
- MVP 每次进程只允许一次 Shadow Commit；换补丁必须重启。
- Shadow 必须在任何闭包内 baseline 类型、反射对象或业务资源被使用前完成。
- 纯方法逻辑变化目标为复用旧 AssetBundle。
- Unity 序列化 ABI 变化必须重构受影响资源。
- M01 若证明 Unity 原生层缓存无法通过 `libil2cpp` Hook 统一，必须停止或调整“旧 AssetBundle 无需重构”的目标。
- `main` 是移动分支；开始开发前必须记录四仓库 exact commit。

## 建议首次阅读

```text
design.md:
    1 摘要与最终决策
    2 可行性判断
    6 总体架构
    10 两阶段Stage/Commit
    13～14 类型与反射
    16～17 Unity API与资源
    25～26 风险与Gate

plans/milestone-00-repository-baseline.md
plans/milestone-01-demo-poc-feasibility.md
```
