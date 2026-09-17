# Local validation checkpoint — handoff a42b205

## Disposition

**Local Validation → Primary Implementation**

Candidate handoff `a42b205a8eb5c1cf2565a985bb652de94db4d301`, source anchor `29261690798059077e5263de71526867a32bce30`, and reproduction-tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e` were validated in isolated checkouts. Protected reproduction and performance-reference pins were unchanged.

V00 passes. V01 H1 Python passes 478/478 and bounded Primary passes 300/300. The reproduction-tooling Unity compile passes. The candidate's first real Unity 2022.3.62f2 compile fails with one CS0234 error before the required `M07FixedByteBootstrapPolicyTests` can execute:

```text
Assets/AssemblyShadowDemo/Tests/Editor/M07FixedByteBootstrapPolicyTests.cs(5,17): error CS0234: The type or namespace name 'AssemblyShadow' does not exist in the namespace 'HybridCLR'
```

Line 5 imports `HybridCLR.AssemblyShadow.CodeGen`. Its defining asmdef is `Unity.HybridCLR.AssemblyShadow.CodeGen`. `AssemblyShadowDemo.EditorTests.asmdef` does not reference that assembly. The captured Unity C# response includes `HybridCLR.Editor.ref.dll` and the new test source but contains no CodeGen assembly reference. Unity asmdef dependencies are not transitive, so the dependency through `HybridCLR.Editor` is insufficient.

Because the root cause was exact and the correction was a single test-assembly dependency, Local Validation applied a bounded fix: add `Unity.HybridCLR.AssemblyShadow.CodeGen` to `AssemblyShadowDemo.EditorTests.asmdef`. The candidate then compiled with zero errors and `M07FixedByteBootstrapPolicyTests` passed 2/2 in real Unity. No policy, allowlist, runtime, protected pin, or product behavior changed.

The committed preflight correctly rejects the modified asmdef because source anchor `2926169` does not authenticate its new bytes. The fix therefore cannot be used for current-anchor V02–V05 acceptance until Primary reviews and republishes source authority.

The outer M07 failure wrapper was also exercised against the known non-candidate installed runtime. It failed at its first pinned-runtime check and emitted `ExactBytesRestored` for all three owned files. Their pre-restore hashes equaled their originals, so this proves the failure/receipt path but provides no mutation-restoration coverage and is diagnostic only.

V02–V05 remain `Blocked / NotRun`; no accepted current-anchor provenance builds, post-mutation restoration proof, successful runtime/performance chain, successor, or independent M08 exists. `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Evidence

- `source-state.json`: exact candidate, tooling, protected reproduction, native/package/IL2CPP, and performance-reference identities.
- `results-summary.json`: stage dispositions and gate state.
- `failure-analysis.json`: direct issue, root cause, design gap, impact, and recommended Primary direction.
- `v00/`: both authoritative preflight outputs.
- `v01/h1-python-inventory.json` and `h1-python.log`: 478/478 test identities and raw output.
- `v01/bee-primary/results.json` and `tests.log`: 300/300 bounded test identities and raw output.
- `v01/candidate-unity-compile.*`: structured and full raw failed Unity compilation.
- `v01/AssemblyShadowDemo.EditorTests.rsp*`: exact compiler response inputs.
- `v01/candidate-csc-response-audit.txt`: present `HybridCLR.Editor` reference, absent CodeGen reference, and present failing source.
- `v01/candidate-codegen-reference-audit.txt`: source/asmdef blobs, imports, asmdef definitions, and change history.
- `v01/bounded-local-fix.diff`: the single direct asmdef reference added locally.
- `v01/candidate-unity-compile-after-local-fix.*`: successful real-Unity compilation after the bounded fix.
- `v01/m07-policy-tests-after-local-fix/`: 2/2 real-Unity NUnit result, log, and test inventory.
- `v01/candidate-post-local-fix-preflight.*`: expected fail-closed source-authority result for the modified asmdef.
- `v01/reproduction-tooling-unity-compile.*`: successful unchanged tooling compile.
- `v01/*postcompile*`: authority preflights still pass after the compile failure.
- `v04/controlled-failure/`: three-file `ExactBytesRestored` diagnostic at the pre-Unity pinned-runtime failure stage; all before-restore bytes equal originals.
- `v02`–`v05/status.json`: explicit `Blocked / NotRun` dispositions.
- `evidence-manifest.json`: SHA-256 and byte size of every checkpoint file except itself.

No historical checkpoint was overwritten or relabeled. Primary should retain the bounded asmdef fix, publish a new source identity, and rerun fresh V00–V05.
