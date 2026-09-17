# M03 changed files and API inventory

This inventory compares each repository's `assembly-shadow-m02-tooling` tag with
the exact v4 executable-source pairing below. `A`, `M`, and `D` mean added,
modified, and deleted. Later pins/report-only commits do not change executable
source. Runtime acceptance remains governed by the M03 report.

## HybridCLR runtime

Source commit: `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9`; 16 paths.

```text
A	hybridclr/AssemblyShadowRuntimeApi.cpp
A	hybridclr/AssemblyShadowRuntimeApi.h
M	hybridclr/RuntimeApi.cpp
M	hybridclr/RuntimeApi.h
M	hybridclr/interpreter/Interpreter_Execute.cpp
M	hybridclr/metadata/Assembly.cpp
M	hybridclr/metadata/Assembly.h
A	hybridclr/metadata/AssemblyShadowBridge.cpp
A	hybridclr/metadata/AssemblyShadowBridge.h
M	hybridclr/metadata/Image.cpp
M	hybridclr/metadata/Image.h
M	hybridclr/metadata/InterpreterImage.cpp
M	hybridclr/metadata/InterpreterImage.h
M	hybridclr/metadata/MetadataModule.h
A	hybridclr/metadata/StagedAssembly.cpp
A	hybridclr/metadata/StagedAssembly.h
```

## IL2CPP native

Source commit: `0486098099e7e80176401267538499e611b181f2`; 24 paths.

```text
M	libil2cpp/il2cpp-api.cpp
M	libil2cpp/vm/Assembly.cpp
M	libil2cpp/vm/Assembly.h
A	libil2cpp/vm/AssemblyShadow.cpp
A	libil2cpp/vm/AssemblyShadow.h
A	libil2cpp/vm/AssemblyShadowDiagnostics.cpp
A	libil2cpp/vm/AssemblyShadowDiagnostics.h
A	libil2cpp/vm/AssemblyShadowName.h
D	libil2cpp/vm/AssemblyShadowPrototype.cpp
D	libil2cpp/vm/AssemblyShadowPrototype.h
A	libil2cpp/vm/AssemblyShadowTypes.h
A	libil2cpp/vm/AssemblyShadowVisibility.cpp
A	libil2cpp/vm/AssemblyShadowVisibility.h
M	libil2cpp/vm/Class.cpp
M	libil2cpp/vm/GlobalMetadata.cpp
M	libil2cpp/vm/GlobalMetadata.h
M	libil2cpp/vm/Image.cpp
M	libil2cpp/vm/Image.h
M	libil2cpp/vm/MemoryInformation.cpp
M	libil2cpp/vm/MetadataCache.cpp
M	libil2cpp/vm/MetadataCache.h
M	libil2cpp/vm/Object.cpp
M	libil2cpp/vm/Reflection.cpp
M	libil2cpp/vm/Runtime.cpp
```

## Unity package

Source commit: `0c9302ffa2f420b30774423d4da8305214a78784`; 14 paths.

```text
A	Runtime/AssemblyShadow.meta
A	Runtime/AssemblyShadow/AssemblyShadowDiagnostics.cs
A	Runtime/AssemblyShadow/AssemblyShadowDiagnostics.cs.meta
A	Runtime/AssemblyShadow/AssemblyShadowErrorCode.cs
A	Runtime/AssemblyShadow/AssemblyShadowErrorCode.cs.meta
A	Runtime/AssemblyShadow/AssemblyShadowException.cs
A	Runtime/AssemblyShadow/AssemblyShadowException.cs.meta
A	Runtime/AssemblyShadow/AssemblyShadowRuntime.cs
A	Runtime/AssemblyShadow/AssemblyShadowRuntime.cs.meta
A	Runtime/AssemblyShadow/AssemblyShadowState.cs
A	Runtime/AssemblyShadow/AssemblyShadowState.cs.meta
M	Runtime/RuntimeApi.cs
A	Tests/Editor/AssemblyShadow/M03RuntimeApiTests.cs
A	Tests/Editor/AssemblyShadow/M03RuntimeApiTests.cs.meta
```

## Demo

Source commit: `6369ae8e32b8458c3b7c4180c99e47d15d5a63b3`; 53 paths.

```text
A	Assets/AssemblyShadowDemo/AssemblyA/Contracts/M03ModuleInitializer.cs
A	Assets/AssemblyShadowDemo/AssemblyA/Contracts/M03ModuleInitializer.cs.meta
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M03ModuleInitializer.cs
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M03ModuleInitializer.cs.meta
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M03VisibilityTypes.cs
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M03VisibilityTypes.cs.meta
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M03ModuleInitializer.cs
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M03ModuleInitializer.cs.meta
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M03VisibilityConsumer.cs
A	Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M03VisibilityConsumer.cs.meta
A	Assets/AssemblyShadowDemo/Bootstrap/M03BootstrapRunner.cs
A	Assets/AssemblyShadowDemo/Bootstrap/M03BootstrapRunner.cs.meta
A	Assets/AssemblyShadowDemo/Bootstrap/M03TransactionProbe.cs
A	Assets/AssemblyShadowDemo/Bootstrap/M03TransactionProbe.cs.meta
M	Assets/AssemblyShadowDemo/Bootstrap/link.xml
A	Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M03ModuleInitializer.cs
A	Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M03ModuleInitializer.cs.meta
A	Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M03ModuleInitializer.cs
A	Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M03ModuleInitializer.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M03Build.cs
A	Assets/AssemblyShadowDemo/Editor/M03Build.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M03CompilerLibraryVerifier.cs
A	Assets/AssemblyShadowDemo/Editor/M03CompilerLibraryVerifier.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M03DiagnosticSchemaVerifier.cs
A	Assets/AssemblyShadowDemo/Editor/M03DiagnosticSchemaVerifier.cs.meta
A	Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs
A	Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs.meta
A	Assets/AssemblyShadowDemo/Scenes/M03Bootstrap.unity
A	Assets/AssemblyShadowDemo/Scenes/M03Bootstrap.unity.meta
M	Assets/AssemblyShadowDemo/Tests/Editor/AssemblyShadowDemo.EditorTests.asmdef
A	Assets/AssemblyShadowDemo/Tests/Editor/M03CompilerLibraryTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M03CompilerLibraryTests.cs.meta
A	Assets/AssemblyShadowDemo/Tests/Editor/M03DiagnosticSchemaTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M03DiagnosticSchemaTests.cs.meta
A	Assets/AssemblyShadowDemo/Tests/Editor/M03TransactionTests.cs
A	Assets/AssemblyShadowDemo/Tests/Editor/M03TransactionTests.cs.meta
A	Docs/AssemblyShadow/M03/M03-report.md
A	Docs/AssemblyShadow/M03/M03-transaction-contract.md
M	ProjectSettings/AssemblyShadowDependencies.json
M	ProjectSettings/AssemblyShadowSettings.asset
M	ProjectSettings/AssemblyShadowSourcePins.json
M	ProjectSettings/EditorBuildSettings.asset
M	Tools/AssemblyShadow/README.md
A	Tools/AssemblyShadow/m03_results.py
A	Tools/AssemblyShadow/native-tests/README.md
A	Tools/AssemblyShadow/native-tests/m03_disabled_api.cpp
A	Tools/AssemblyShadow/native-tests/m03_facade_lookup_adapters.cpp
A	Tools/AssemblyShadow/native-tests/m03_private_visibility.cpp
A	Tools/AssemblyShadow/native-tests/m03_staging_identity.cpp
A	Tools/AssemblyShadow/run-m03-native-tests.py
A	Tools/AssemblyShadow/run-m03-visibility-tests.py
A	Tools/AssemblyShadow/tests/test_m03_results.py
A	Tools/AssemblyShadow/verify-m03-results.py
```

## Public managed and Editor surface

`HybridCLR.AssemblyShadowRuntime` exposes exactly nine operations, each returning
`AssemblyShadowErrorCode`:

- `ConfigureCandidates(baselineBuildId, candidateNames, stableAotNames)`
- `BeginTransaction(patchId, expectedBaselineBuildId, closureLoadOrder, runtimeAbiVersion)`
- `StageAssembly(dllBytes, pdbBytes)`
- `ValidateTransaction()`
- `CommitTransaction()`
- `AbortTransaction()`
- `GetState(out state)`
- `GetAssemblyExecutionMode(assemblyName, out mode)`
- `GetDiagnosticsJson(out json)`

The public data/exception surface adds `AssemblyShadowState`,
`AssemblyExecutionMode`, `AssemblyShadowErrorCode`, `AssemblyShadowDiagnostics`
(and its diagnostic records, `Parse`/`TryParse`), and `AssemblyShadowException`.
Execution-mode and state enums share one source file. Six obsolete managed M01
compatibility methods remain in `RuntimeApi`; retired load/activation methods
throw rather than provide an alternate shadow transaction path. Only the native
`AssemblyShadowPrototype.cpp/.h` files were deleted; tags preserve them.

Demo batchmode entrypoints under `AssemblyShadowDemo.Editor` are
`M03Build.Configure`, `M03Build.ValidateCompilerInputs`,
`M03Build.BuildPlayerBaseline`, `M03Build.BuildFixtures`,
`M03Build.BuildFeatureDisabledPlayer`, and `M03EditorValidation.Validate`.
`ValidateCompilerInputs` is optional compiler-only preflight, not a runtime gate.
`ValidateAndWriteReceipt` is the replay receipt helper. The new
`M03CompilerLibraryVerifier.Verify` and `M03CompilerLibraryEvidence` expose
byte/identity-bound Editor compiler-library proof without changing framework
identity-unification authority. Runtime startup uses `M03BootstrapRunner` and
`M03TransactionProbe.RunAndWrite`.
`M03DiagnosticSchemaVerifier.Verify` checks the exact captured prelink and linked
DTO field schema before build/replay receipts. This is an Editor-only proof
helper; field/type preservation does not change the nine-operation runtime API.
The eleven unsigned native diagnostic scalars use managed `ulong`, with
full-range numeric-token tests. Native OFF uses the same diagnostic serializer;
the adapter no longer substitutes a truncated legacy object.

The nine native adapters are declared in `hybridclr/AssemblyShadowRuntimeApi.h`
and registered in its `.cpp`. The VM transaction declarations are in
`libil2cpp/vm/AssemblyShadow.h`; private staging/visibility/resolver helpers are
internal integration surfaces, not managed API additions. The shadow-gated
`Image::ClassFromNameDefinedInImage` checks raw ownership before materialization.

Commands and test/Player flags are in `Tools/AssemblyShadow/README.md`; states,
locking, retained memory, facade constraints, deviations, and later-milestone
boundaries are in `M03-transaction-contract.md`.

## Additional review and evidence metadata

The final review boundary also includes the two new metadata documents below
and 22 evidence files. Together with the 53 executable-boundary paths above,
these make 77 changed demo paths relative to `assembly-shadow-m02-tooling`.
The report and transaction contract were already counted in those 53 paths;
their later status/evidence edits do not add paths. These additions do not change
the source pins, Player bytes, fixtures, or verifier implementation.

```text
A	Docs/AssemblyShadow/M03/M03-file-and-api-inventory.md
A	Docs/AssemblyShadow/M03/M03-review.md
A	Docs/AssemblyShadow/M03/Evidence/baseline-manifest-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/diagnostic-schema-v3.md
A	Docs/AssemblyShadow/M03/Evidence/editor-replay-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/editor-tests-6369ae8.xml
A	Docs/AssemblyShadow/M03/Evidence/editor-tests-b20145a.xml
A	Docs/AssemblyShadow/M03/Evidence/fixture-manifest-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/installed-runtime-verification-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/native-off-build-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/native-on-build-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/native-on-build-b20145a.json
A	Docs/AssemblyShadow/M03/Evidence/native-regression-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/native-regression-b20145a.json
A	Docs/AssemblyShadow/M03/Evidence/ordinary-off-build-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/ordinary-off-player-6369ae8.log
A	Docs/AssemblyShadow/M03/Evidence/ordinary-off-result-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/ordinary-off-verification-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/player-results-6369ae8.index.json
A	Docs/AssemblyShadow/M03/Evidence/player-results-6369ae8.tar.gz
A	Docs/AssemblyShadow/M03/Evidence/python-tests-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/verification-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/visibility-regression-6369ae8.json
A	Docs/AssemblyShadow/M03/Evidence/visibility-regression-b20145a.json
```

Files suffixed `b20145a` and `diagnostic-schema-v3.md` preserve the earlier v3
diagnostic investigation; they are not v4 acceptance evidence. The v4 archive
contains all 49 original Player observation files, with each byte hash recorded
in its index. It does not contain the full compiler, Player, or resource trees;
the receipts retain their original absolute paths to those separate artifacts.
