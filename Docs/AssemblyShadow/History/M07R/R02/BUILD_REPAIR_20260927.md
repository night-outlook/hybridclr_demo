# R02 build-boundary repair — 2026-09-27

## Authority and scope

Input Local return: `621216751ade64aa39f28ed44a5acdc15c38c6cc` on `codex/assembly-shadow-r01b-h1`.
Read `Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, and the immutable `local-validation-20260927-return-required/FAILURES.json` at that commit. The reported outcome is ReturnRequired: 9 Passed, 2 Failed, 20 Blocked; no accepted controlled graph or D1/D2 Player series. These remain historical results.

Only demo build preparation, process supervision, tests and coordination change. HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, candidate IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`, and control IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933` remain unchanged. No R03 or H2 acceptance is part of this repair.

## Findings and design decisions

### BR-01 — command completion includes owned Roslyn retirement

The actual command may finish while Unity's `dotnet exec .../Contents/DotNetSdkRoslyn/VBCSCompiler.dll` remains in its process group. Environment-only suppression did not solve the reported long M07 invocation. Do not treat an exited parent as a clean command, exempt arbitrary dotnet processes, or stop shared servers globally.

`unity_session.py` is a supervisor inside the existing fresh POSIX session/group created by `evidence.run`. It starts the actual Unity/PowerShell command without creating a second group, preserves the actual exit status, and then enumerates only its owned group. After command completion it can signal only the exact Roslyn DLL belonging to the supplied Unity installation. The DLL is hash-bound before and after. PID, process group and start identity are rechecked immediately before individual TERM/KILL signals. Unknown children, changed identities, unreadable census, or final survivors fail. TERM grace is 5 seconds and KILL grace 3 seconds; neither changes the outer command timeout. Known zombies are waited for, not treated as clean while present. Linux host tests use child adoption/reaping; Darwin uses normal init reaping.

The outer `evidence.run` implementation and its final no-survivor criterion are unchanged. This is supervised completion of a new command, not retroactive acceptance of A/B/C. Player launches/formal timing commands never use this wrapper. Completion JSON, compiler binding, command status, ownership observations, signals, and failures are retained and sealed.

### BR-02 — workspace-local fixed ordinary input

The fresh control lacks an ignored M00 DLL needed before M07 compiler validation. Copying the candidate's ignored output would not prove control preparation. Calling `BaselineBuild.Configure` would also alter unrelated feature, scenes and settings.

`AssemblyShadowBaseline.Editor.R02OrdinaryInput.Prepare` invokes the existing `CompileDllCommand.CompileDll` against current workspace source with StandaloneOSX/Development settings and a new output directory. It records source files, source-pin digest, compiler output, provider identity, staged path and digests. It extracts only `AssemblyShadowBaseline.HotUpdate.dll` for the fixed ordinary witness. Both candidate and control perform this generation independently before M07. No M00 Configure, GenerateAll, Player build, or live-candidate copy is involved.

The existing fixed SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27` remains mandatory. A mismatching output is preserved with expected/actual digests and fails before staging or M07. Existing mismatching destinations are not overwritten. Current-workspace compiler export is not claimed to be a fresh Csc invocation: Unity may use compilation caches. `ordinary_input.py` independently authenticates source membership, pins, configuration, compiled and staged bytes before M07 and again after it. The later full M07 compiler graph still performs its original semantic/provenance checks.

Actual Unity compilation and byte equality are Local validation obligations; host tests cannot establish them. There is deliberately no fallback that rewrites the frozen witness contract, selects a different compiler mode based on output, or imports another workspace's DLL.

### BR-03 — canonical temporary paths and host compile surface

Child environments use a canonical TMPDIR and the three no-server-reuse settings already investigated by Local. Strict linked-parent checks remain unchanged. The affected test root is canonicalized. The managed host project also compiles the new Editor helper against explicitly labelled API stubs; this catches C# surface errors but is not a Unity API/runtime execution claim.

## Test and review coverage

The host Python suite passes 140 tests, including 25 new tests. Real subprocess tests cover clean completion, retained nonzero exits, successful retirement of an owned compiler-shaped native process, an unrelated session left running, and rejection of arbitrary surviving children. Policy tests cover exact compiler paths, spaces, PID/start identity changes, unknown companions, disappearing children and census failure. Input tests cover wrong workspace, stale pins, changed sources/output, incomplete/duplicate source membership, preserved wrong destination bytes, linked paths and mandatory new preparation even when matching bytes already exist. Batch tests keep Player command dispatch unchanged and prevent a completion receipt overriding an outer failure.

An initial host test exposed a zombie-transition race after TERM. The repair now waits for disappearance using the same PID/group/start identity. The final passing run follows that correction; the initial failure was not promoted to PASS. No standalone independent reviewer was available in Primary; this is a focused implementation self-review. Local's genuinely independent R02 stage review remains required after complete evidence.

## Next Local cycle

Publish a new common executable source anchor and a matching H1-runtime control, then regenerate candidate source authority and `WEB_TO_LOCAL.md`. Both roles require fresh installed-runtime/build receipts; do not select the previously internally completed but rejected candidate graph. Use a new batch root and retain Local A/B/C, their seals, all H1 evidence and the older R01 reference.

Run the full existing R02LocalBatch-v1: source and host checks; independently generated M00 inputs; new candidate/control controlled graphs; eight functional sidecars; 44 A/B pairs / 88 timing processes; Editor/native/M07/startup/failure/count132/lazy/dense/capacity regressions; final authority and complete sealing. Independent valid cells continue; invalid dependencies block. Source or byte-generation problems return to Primary with compiled output and receipts, not Local code/pin edits.

H1 remains PassedWithExplicitDeferredRisk. D1/D2 are still pending measured R02 disposition before H2. R02Accepted=false and mayEnterR03=false.

## Transport

The new demo-only Git-object/ref smoke test on `codex/connector-smoke-r02-buildrepair-20260927-81fd` passed read-back at `3f91bd73f1697f825c40172563bc4e928dd39b71`, based on Local return `6212167`. It is not an acceptance or handoff commit and must not be merged. It remains because no branch-deletion operation is exposed. Other repositories are read-only in this repair.

## Repair completion

Primary published the repaired source anchor at `82d64ce415c062729f0082e81c1808eaac9602e4`, paired it with H1-runtime control `6c950eaa98f995084750fe1ea8f80cfe4c59c61b`, and refreshed the candidate source authority. The control commit has the repaired source anchor as explicit ancestry and differs in the working tree only by `ProjectSettings/AssemblyShadowSourcePins.json`.

Final R02 Primary CI run `36318653155` passed, including 145/145 Python tests, both 70/70 native process matrices, and managed host Baseline/P01/P03 assertions. Final legacy-H1 CI run `36318659885` also passed: 384/384 current scoped cases and 6/6 fixed-H1 positives, plus the remaining R01/M07/R01B workflow regressions.

The repair remains unverified in the real macOS Unity/IL2CPP build path until the next Local batch. Previous A/B/C failures and seals remain historical evidence; they are not superseded as executions.
