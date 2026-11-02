# Primary Implementation → Local Validation — CONDITIONAL R03 oneuse-F (2026-11-02)

**Authority:** A new one-use R03 source-pinned combined validation cycle, F, is authorized **only if** all the source, CI, Mac preflight and absence checks below pass. The old E cycle is consumed/FAIL: all 3 real Unity C++11 builds Passed; five Players were launched, OFF Passed and four ON Failed. Three ON raw reports were zero bytes due to native field14 262144-byte text bound; real engine-observer count was 51211 in 500ms (bound64). The official installed-source audit was Blocked, although Local's independent 129-pair read-only comparison matched. Do not misclassify these results or reuse any A/B/C/D/E root.

## 1. Exact source pins and ownership

All four checkouts must be clean, canonical `night-outlook` origins, at branch `codex/assembly-shadow-r01b-h1`, with remote HEADs matching the closing Primary handoff prompt (the final demo commit cannot be written into this document before committing it). The previous Mac workspace paths are *expected* but must be independently verified:

| Repository | Expected source pin / checkout |
| --- | --- |
| night-outlook/hybridclr_demo | latest final pushed HEAD from closing handoff; `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de`; `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| night-outlook/il2cpp_plus | `ecb9f010f84915b6fa0924dfd66174f812c52fc0`; `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

Historical S native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, historical R03 `74dbdbea80d83923863303bd2b2c0a87f36541b1`, D native `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`, E native `ca0aab8e0abcbcb60a1532223d9e1bdb0aea86c4`, and current F native **must never be conflated**. The original `R03/source-pins.json` is immutable. The new source manifest contains **45 changed native VM paths**; three installed source trees must supply **135** byte-equal source pairs, including the two newer native engine reporter files.

## 2. Mandatory read/preservation and limitations

Read `Docs/AssemblyShadow/README.md`, this canonical file, `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, then full unchanged E evidence under `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-e/`, especially README, RUNTIME_FINDINGS, five raw/Player logs and actual build receipts. Preserve E's three empty raw files, engine count51211, OFF PASS, archival/129-pair scoped PASSES, original-S archive and seven previous checkpoint states exactly.

Primary source remediation candidate consists of a **test-only** native `AssemblyShadowR03Probe.cpp` full-general diagnostic sidecar (fixed `3932160`-byte general upper bound, original `262144`-byte ordinary text field bound unchanged; no truncation or fabricated JSON), strict host verifier `complete_general_diagnostic.py` (byte size, CRC, schema, source arrays, generation comparison, no global-epoch acceptance), preopened raw/sidecar binding, and a native one-shot Unity owner-quit request on the engine sentinel. Actual runtime containment and shutdown remain unproved. The native owner-quit request must not mask completedReports, relax bound64/500ms, introduce callback sleeps, or bypass terminal execution guards. The general sidecar's independently collected source views **do not establish an atomic whole-VM epoch**.

## 3. Required host/source CI gate (before any Local F invocation)

Verify at the **exact final demo commit** successful current-source contracts: `r03-ir-current-native-local-cycle-host.yml`, `r03-ir-current-native-source-only.yml`, `r03-ir-current-native-vm-delta-source-only.yml`, `r03-ir-current-native-oracle-source-only.yml`, `r03-ir-fixture.yml`, and the R03IR/K/L host suites changed by this candidate. Confirm tests include actual C++11 compiled `snapshot_general_transport_contracts.py`, `engine_owner_quit_contracts.py`, `complete_general_diagnostic_contracts.py`, and `failed_player_receipt_contracts.py`, plus strict positive and adversarial verifier contracts. Verify source blobs/remote heads, not merely workflow titles. Native current source: verify source identity of both engine reporter VM files and C++11 compatibility; source-host compilation is **not** actual Unity execution. If required CI is Failed, queued, cancelled, unavailable or mismatched, STOP; send the exact failure to Primary without using F.

## 4. Read-only Mac prerequisite and unused one-use output

Retain original-S sparse detached worktree `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse` at `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, 16978 protected checkpoint files, exact registered tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`. Do not resparsify, recreate, clean or alter it. Check Unity **2022.3.62f2 arm64** at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, real .NET SDK8.0.318/runtime8.0.21, Python, Git, clang++, lipo, clean source/installed pins, and absence of conflicting Editor/IL2CPP processes. The **20 GiB hard floor** remains; **40 GiB advisory** requires Primary go/no-go when below. No SDK installs, compiler flag overrides, or old binaries as substitutes.

Choose F root ONLY if canonical, disjoint and confirmed absent:
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261102-oneuse-F`.
Never pre-create or auto-suffix it. If present, STOP and request fresh Primary authority. Preserve standalone-CLI preflight stdout/stderr and actual free space OUTSIDE F and protected historic roots.

Set `WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, `ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`, `UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, `RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261102-oneuse-F`, and `DEMO_COMMIT` equal to the exact 40-digit latest pushed demo HEAD in the closing handoff.

Read-only admission (MUST PASS before root creation):
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```
Require `PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun`, real unassisted standalone fresh Python CLI help, exact 45 VM blobs/4 remote HEADs, original S, SDK, host, space. On failed preflight report PrerequisiteBlocked, coordinator0, F stages NotRun.

## 5. Exactly one F coordinator

**ONLY when all required CI and read-only prerequisites pass**, run the existing source-pinned ten-stage combined coordinator ONCE at that fresh F output:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```
The coordinator reauthenticates current/source/VM/remote and original-S and runs 5 source/host suites, original nine-part 15713-member/90-cell archive, 59 original process joins, native host diagnostics, three fresh ON release/ON debug/OFF release Unity IL2CPP builds, five real Players (baseline release/debug, type release, OFF, engine-unhandled), then **135 actual installed VM source pairs** if prerequisites pass. Preserve native full-general sidecar raw exact bytes and verifier results alongside the original raw.json, including CRC/hash/size and failure-path receipts. Require real post-poison reflection/delegate/AOT denied entry, no canary or instance-field side effect, identical first/final recovery, actual engine sentinel, single owner-quit native callback, `1<=completedReports<=64` over500ms, and genuine Player termination. **Do not** count a synthetically passing host oracle or existing E build as F evidence. If any Player fails, preserve failed raw and first causal log, do not retry or invent verifier PASS.

## 6. Publication and stop

Publish a new additive F checkpoint under `Docs/AssemblyShadow/History/M07R/R03/`, update **Local-owned** `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, bind all actual commands, PIDs, source/SDK/build/Player/sidecar/installed-parity hashes and preserve the complete evidence. Commit/push and verify four remote heads. Return factual Passed/Failed/Blocked/NotRun and stop. Local can apply bounded fixes only; all nontrivial architecture/native and verifier changes return to Primary.

Even a full focused F PASS is only `FocusedEvidenceReadyForIndependentReview`. The October 8 independent R03 FAIL and High IR-R03-01/02, D1=A/D2=A, incomplete P1/P2/E0/E1/P3, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false and PureInterpreter disabled all remain. No H2/M08A/X02/SNAP-01 or Human Review Gate approval.
