# Local Validation → Primary Implementation

## Blocker 1: controlled settings restoration is not exact-byte complete

### Symptom

The protected profile-1 workflow at baseline `M07-Baseline-H1-Perf-Reference-3168-20260920A` accepted `native-on-controlled`, built and sealed the Native ON Development IL2CPP Player, emitted a passed controlled-build evidence file, and exactly restored `Assets/HybridCLRGenerate/link.xml`. The next pinned-source guard then failed with:

```text
[FAIL] Working bytes do not match pinned Git blob: .../ProjectSettings/ProjectSettings.asset
```

Native OFF never started and no complete workflow receipt was produced.

### Reproduction and evidence

Run the current candidate coordinator against the exact protected project with `-ControlledPerformanceBuilds`, as recorded in `LOCAL_VALIDATION.md`.

- Full coordinator log: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/controlled-performance-reference.log`
- Passed Native ON evidence and successful Player receipt: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/reference-failure/`
- Mutated bytes and exact diff: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/reference-failure/ProjectSettings.asset.after-native-on` and `project-settings.diff`
- `link.xml` receipt: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/reference-failure/run/native-on-controlled-link-xml-restored.json`
- Declared three-path outer restoration: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/reference-failure/outer-restoration/workflow-inputs-restored.json`

The only tracked residual mutation was:

```diff
-  il2cppCodeGeneration: {}
+  il2cppCodeGeneration:
+    Standalone: 0
```

The failed bytes were preserved, then the file was restored exactly to its protected Git blob. Protected installed-runtime verification passed afterward.

### Root cause and affected scope

`R00ControlledBuild.RestoreSettings` restores the semantic `Il2CppCodeGeneration` value through Unity's setter and calls `AssetDatabase.SaveAssets`. Unity serializes the restored default as an explicit `Standalone: 0` mapping instead of the original empty map. The coordinator's exact outer recovery covers the M07 scene, Assembly Shadow settings, and Editor build settings, but not `ProjectSettings/ProjectSettings.asset`.

This affects successful controlled Player builds on protected inputs whose pinned serialization uses the empty map. It prevents the second controlled stage and invalidates graph completion even though the first Player itself built successfully.

### Recommended implementation direction

Extend the controlled workflow's exact-byte transaction to cover every tracked settings file it can serialize, including `ProjectSettings/ProjectSettings.asset`, and verify its restored hash before the next pinned-source guard. Do not rely on semantic setter restoration alone and do not weaken the source guard.

## Blocker 2: nested native provenance conflicts with outer M07 authority context

### Symptom

The current profile-2 workflow at baseline `M07-Baseline-H1-Perf-Current-3168-20260920A` accepted `native-on-controlled`, passed compiler/resource phases, and entered the controlled Player build. Its preprocessor then failed before Player completion:

```text
Pinned native installation verification failed ...
[FAIL] M07 workflow authority cannot be invoked with --skip-demo-source
```

### Reproduction and evidence

- Full coordinator log: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/controlled-performance-current.log`
- Failed controlled-build evidence: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/current-failure/run/ControlledPerformanceBuilds/native-on-controlled-evidence.json`
- Exact `link.xml` recovery receipt: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/current-failure/run/native-on-controlled-link-xml-restored.json`
- Exact outer restoration receipt: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/current-failure/outer-restoration/workflow-inputs-restored.json`
- Unity log: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/V04/current-failure/native-on-controlled-unity.log`

The failed attempt also materialized the same `ProjectSettings.asset` mapping. Those bytes were preserved and exactly restored; candidate installed-runtime verification passed afterward.

### Root cause and affected scope

The current `H1BuildInputProvenance.CaptureAfterGenerate` launches `verify-installed-runtime.py` with `--skip-demo-source`. The coordinator exports `H1_M07_WORKFLOW_AUTHORITY_ROOT` and `H1_M07_WORKFLOW_BASELINE_ID` for its whole process lifetime, and the Unity child passes them to the nested Python verifier. The current verifier intentionally rejects any M07 workflow-context invocation that directly supplies `--skip-demo-source`, so the native provenance capture is self-conflicting inside the controlled workflow.

This affects the current profile-2 controlled Player before it can seal provenance. The protected project reached a later boundary only because its historical verifier does not implement the current workflow-context guard.

### Recommended implementation direction

Give the nested native-only provenance check a narrowly scoped, explicit execution contract that does not inherit or misuse the outer coordinator authority context, while keeping the outer post-validation source authority check unchanged and fail-closed. Add a real or process-level regression covering `H1BuildInputProvenance` under active M07 workflow environment variables.

## Validation still required

After Primary repairs both boundaries, Local must restart fresh V00 and rerun both complete controlled-performance workflows. Both Native ON and Native OFF must succeed with exact restoration before old-Player rejection, build-map freeze, preregistration, pilots, formal samples, analysis, V05, or M08.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
