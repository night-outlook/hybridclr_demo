# R01B H1 — Protected Reproduction Validation Tooling Repair

## Status

Primary Implementation completed. Candidate source/implementation anchor: `1b1cc9fe192b88be2a20fad31ea030b1e30be669`.

Protected reproduction remains unchanged:

- branch/head: `codex/assembly-shadow-h1-count-repro` / `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`
- unfixed behavior source pin: `4e3d2035991ab5629265ac663e61bcb2ca62828b`
- reproduction native: `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`
- shared package/IL2CPP: `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`

Separate tooling-only successor:

- branch: `codex/assembly-shadow-h1-count-repro-tooling`
- revision: `0c9c2508d94a097dff50028212a01695c8e29c60`

This branch is validation infrastructure only and is not the reproduction behavior authority.

## Root cause

Local Validation at `9dbe8ee7549b105a29a94bd7ec7383b2909ba066` proved candidate V02 and all four candidate V03 modes, then showed the protected reproduction Player could build while its older project-local native provenance policy rejected the real 446-action Apple graph. Review also found the protected managed-source bridge predates the current schema-3 cache proof. Candidate replay is useful diagnostic evidence but cannot become fresh build provenance.

## Selected design

Use a separately authenticated tooling-only reproduction successor. Candidate authority (`h1_reproduction_tooling.py`) proves before a reproduction build:

1. protected behavior source/head and runtime pins are exact;
2. behavior → protected head → tooling revision ancestry is exact;
3. protected head has no non-metadata behavior change after its source pin;
4. tooling revision differs from protected head at exactly **nine** declared validation-only override paths;
5. the complete **eleven-file** native+managed validation dependency set has exact Git blobs equal to candidate source anchor `1b1cc9fe...`;
6. all non-metadata working bytes match Git and there are no untracked Unity build inputs.

Candidate-owned `h1_count_build_batch_tooling.py` then uses normal candidate validation, runs reproduction Unity from the authenticated tooling checkout, verifies installed runtime against protected reproduction pins, applies candidate-owned strict native/managed verification, re-authenticates the split source after restoration, and writes `validation-tooling-binding.json` bound to the verified build-receipt SHA.

The sidecar status is `ToolingBoundToVerifiedBuildReceiptNotRuntimeAccepted`; it is not runtime/M08/human acceptance.

## Tool identity

Complete candidate-authenticated tool set:

| Path | Git blob |
| --- | --- |
| `Assets/AssemblyShadowDemo/Editor/H1CompilerProvenance.cs` | `b92a8cdb045c563d8339aad5c358e170e5a081ca` |
| `Assets/AssemblyShadowDemo/Editor/H1CountDiagnosticBuildWithManagedProvenance.cs` | `faf90624cf9812efcfc50a817369a26ead231eb0` |
| `Assets/AssemblyShadowDemo/Editor/H1EvidenceProcess.cs` | `f4dccd836bf61076048dba95b4de0c15621bf3be` |
| `Assets/AssemblyShadowDemo/Editor/H1ManagedSourceProvenance.cs` | `2fdddcde4e9f1c62b93cd5f162aa922c67697628` |
| `Tools/AssemblyShadow/h1_bee_macro_domains.py` | `6c87c3134a2ae63fbf933687afdd28ed51b6bfc2` |
| `Tools/AssemblyShadow/h1_capture_attempt.py` | `1cd7b993234ef3d39e5a69f98d55a207adeb1dd2` |
| `Tools/AssemblyShadow/h1_compiler_actions.py` | `e89c97c553793a8866c25b3090972a550f91b751` |
| `Tools/AssemblyShadow/h1_macro_domain_census.py` | `b89059a7d50fdb4026bad3d6f0bef09c2d0f62f7` |
| `Tools/AssemblyShadow/h1_managed_provenance.py` | `0f2d158cb93ca01be8d5cc6e288efddd7dbd8063` |
| `Tools/AssemblyShadow/h1_native_capture.py` | `d1e1153de9c0784e4d202a573cb31c81ac888ef7` |
| `Tools/AssemblyShadow/h1_pch_provenance.py` | `42019759411a076a982149dd654f6347c0e6c65b` |

`H1EvidenceProcess.cs` and `h1_compiler_actions.py` were already byte-identical on the protected head; the other nine paths are the exact tooling delta.

## Primary validation

Workflow `35081136990` at candidate anchor `1b1cc9fe...` passed **294/294**, zero nonpasses.

- artifact ID: `10439663711`
- artifact SHA-256: `a7ad62cbd34200056448374b69f942c0cd7e9d3515bb7e499fe2d64c44d3dd7d`

This is bounded Primary/tool evidence only. Fresh macOS Unity reproduction builds and independent whole-chain M08 remain required.

## Evidence preservation

`local-validation-20260916-9568ea3` remains historical Local evidence. Its candidate V02/V03 results remain valid for their original source/handoff and are not deleted or relabeled. Fresh V00–V05 are required for the new candidate/tooling authority.

H1 remains InProgress; last independent M08 remains FAIL; `humanGatePassed=false`; `mayEnterR02=false`.
