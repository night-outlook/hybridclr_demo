# 证据与阅读覆盖

本表记录本次实际打开的源文件及区段；不是自动化全仓审计清单。链接均固定到本次 review HEAD，不使用会移动的分支链接。

GitHub comparison 另用于核对 runtime/native/package 相对基线的差异范围；大 diff 的文件统计不能当作逐文件阅读证明。M07 source inventory 用于区分可执行修改与证据修改。

| ID | 仓库 / 文件 | 本次阅读覆盖 |
|---|---|---|
| S01 | [hybridclr_demo/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/design.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/design.md) | 核心正文 1–1550；引用尾部未逐项展开 |
| S02 | [hybridclr_demo/Docs/AssemblyShadow/M07/M07-report.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-report.md) | 全文 |
| S03 | [hybridclr_demo/Docs/AssemblyShadow/M07/M07-resource-contract.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-resource-contract.md) | 全文 |
| S04 | [hybridclr_demo/Docs/AssemblyShadow/M07/Evidence/verification/m07-strict-gate-3b-v6.json](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/Evidence/verification/m07-strict-gate-3b-v6.json) | 全文；只读取记录，未重放 |
| S05 | [hybridclr_demo/Docs/AssemblyShadow/M07/M07-source-inventory.json](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M07/M07-source-inventory.json) | 1–430；定向核对执行版本和差异 |
| S06 | [hybridclr_demo/Docs/AssemblyShadow/M03/M03-report.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M03/M03-report.md) | 当前 v4 接受记录；历史部分定向阅读 |
| S07 | [hybridclr_demo/Docs/AssemblyShadow/M05/M05-type-contract.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M05/M05-type-contract.md) | 1–240 |
| S08 | [hybridclr_demo/Docs/AssemblyShadow/M05/M05-report.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M05/M05-report.md) | 1–170 |
| S09 | [hybridclr_demo/Docs/AssemblyShadow/M06/M06-report.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Docs/AssemblyShadow/M06/M06-report.md) | 1–200 |
| S10 | [hybridclr_demo/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-08-editor-build-integration.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-08-editor-build-integration.md) | 1–310 |
| S11 | [hybridclr_demo/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-09-bootstrap-security-rollback.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-09-bootstrap-security-rollback.md) | 1–300 |
| S12 | [hybridclr_demo/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-11-performance-hardening-rebase.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-11-performance-hardening-rebase.md) | 1–220 |
| S13 | [il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadow.cpp) | 全文，1–1489 |
| S14 | [il2cpp_plus/libil2cpp/vm/AssemblyShadowTypeResolver.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowTypeResolver.cpp) | 全文，1–714 |
| S15 | [il2cpp_plus/libil2cpp/vm/Assembly.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/Assembly.cpp) | 全文 |
| S16 | [il2cpp_plus/libil2cpp/vm/Object.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/Object.cpp) | 1–320 |
| S17 | [il2cpp_plus/libil2cpp/vm/Reflection.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/Reflection.cpp) | 170–490 |
| S18 | [il2cpp_plus/libil2cpp/vm/AssemblyShadowVisibility.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/vm/AssemblyShadowVisibility.cpp) | 全文 |
| S19 | [il2cpp_plus/libil2cpp/icalls/mscorlib/System.Reflection/Assembly.cpp](https://github.com/night-outlook/il2cpp_plus/blob/666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8/libil2cpp/icalls/mscorlib/System.Reflection/Assembly.cpp) | 全文 |
| S20 | [hybridclr/hybridclr/metadata/StagedAssembly.cpp](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/StagedAssembly.cpp) | 全文，1–487 |
| S21 | [hybridclr/hybridclr/AssemblyShadowRuntimeApi.cpp](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/AssemblyShadowRuntimeApi.cpp) | 1–275 |
| S22 | [hybridclr/hybridclr/metadata/InterpreterImage.cpp](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/InterpreterImage.cpp) | 1–220 |
| S23 | [hybridclr/hybridclr/metadata/MetadataUtil.h](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/MetadataUtil.h) | 1–150 |
| S24 | [hybridclr/hybridclr/metadata/Assembly.cpp](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/Assembly.cpp) | 1–200 |
| S25 | [hybridclr/hybridclr/metadata/Assembly.h](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/Assembly.h) | 全文 |
| S26 | [hybridclr/hybridclr/metadata/RawImageBase.h](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/RawImageBase.h) | 1–260 |
| S27 | [hybridclr/hybridclr/metadata/RawImage.h](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/metadata/RawImage.h) | 全文 |
| S28 | [hybridclr/hybridclr/interpreter/Interpreter_Execute.cpp](https://github.com/night-outlook/hybridclr/blob/a19db144751f4f016769b90e61a80b8c27578678/hybridclr/interpreter/Interpreter_Execute.cpp) | 1–220；只核对 guard 宏，未声称逐条 opcode 审计 |
| S29 | [hybridclr_unity/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs) | 全文 |
| S30 | [hybridclr_unity/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs) | 全文 |
| S31 | [hybridclr_unity/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs) | 全文 |
| S32 | [hybridclr_unity/Editor/AssemblyShadow/Build/ShadowSourcePins.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowSourcePins.cs) | 全文 |
| S33 | [hybridclr_unity/Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Validation/ShadowAssemblyPolicyValidator.cs) | 1–255；编译策略入口与作用域 |
| S34 | [hybridclr_unity/Editor/AssemblyShadow/Validation/ShadowExecutionPolicy.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Validation/ShadowExecutionPolicy.cs) | 全文，1–370 |
| S35 | [hybridclr_unity/Editor/AssemblyShadow/Serialization/UnitySerializedTypeAnalyzer.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Serialization/UnitySerializedTypeAnalyzer.cs) | 1–250 |
| S36 | [hybridclr_unity/Editor/AssemblyShadow/Hashing/AssemblySemanticHasher.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Hashing/AssemblySemanticHasher.cs) | 1–305 |
| S37 | [hybridclr_unity/Editor/AssemblyShadow/Generation/ShadowGenerationPlan.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Generation/ShadowGenerationPlan.cs) | 1–277；末尾响应截断，不作全文覆盖声明 |
| S38 | [hybridclr_unity/Editor/AssemblyShadow/Generation/ShadowGenerationOutput.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Generation/ShadowGenerationOutput.cs) | 全文 |
| S39 | [hybridclr_unity/Editor/MethodBridge/GenerationInventory.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/MethodBridge/GenerationInventory.cs) | 全文 |
| S40 | [hybridclr_demo/Assets/AssemblyShadowDemo/Bootstrap/M07Probe.cs](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Assets/AssemblyShadowDemo/Bootstrap/M07Probe.cs) | 1–230 |
| S41 | [hybridclr_unity/Editor/AssemblyShadow/Build/ShadowManifests.cs](https://github.com/night-outlook/hybridclr_unity/blob/2180b99daf39095cd76301da2bdf34ac945ee8b4/Editor/AssemblyShadow/Build/ShadowManifests.cs) | 全文 |
| S42 | [hybridclr_demo/Tools/AssemblyShadow/README.md](https://github.com/night-outlook/hybridclr_demo/blob/41b047b153d2d816306fe9e0253a58b96fe72c05/Tools/AssemblyShadow/README.md) | 1–120、310–末尾；核对现有执行命令 |

## 没有执行的验证

没有 checkout/编译四仓库；没有 Unity Editor/Test Runner；没有 macOS/Windows/Android Player 启动；没有独立核验归档内每个文件 SHA；没有全面审计每个 native Hook 或每个测试文件。

## 本次执行的复算

`analysis/reproduce_source_algorithms.py` 不依赖外部包，输出 `analysis/source-algorithm-results.json`。它仅使用源代码已读取的常量/分配逻辑和图操作构造可检查的算法结论，不能替代真实 metadata/Unity 测试。

运行：

```text
python analysis/reproduce_source_algorithms.py
```

容量表按“fresh process、没有既有 image、每个 DLL 同尺寸”假设计算。混合尺寸必须按实际序列模拟；不得把单行上限直接作为所有项目的剩余预算。
