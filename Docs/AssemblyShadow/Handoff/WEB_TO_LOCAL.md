# Primary Implementation → Local Validation — ONE inactive live-general source/SDK cycle

**ONE NEW twelve-component host + installed Unity2022.3.62f2 SDK SYNTAX-ONLY cycle is authorized.** Objective: compile/check the **inactive** actual native `AssemblyShadow::TryCaptureBoundedGeneralLive` source, conservative source fences, owned capture composition and unchanged existing native/managed compiler/diagnostic contracts. The old 11-component owned-general `20261016-3dc9` source/SDK PASS is **consumed**. This is NOT an authorization to launch Unity Editor, Test Runner, Player, run a linked native Player, carry out SNAP-01 or a seven-root runtime batch, invent Unity engine owner/scheduler APIs, modify source policies, begin H2/X02/M08A, or conduct a Human Review Gate.

**Current delegation:** Local Validation may only verify and publish factual results. All nontrivial code/test/compiler/procedure/architecture changes remain Primary Implementation-owned. Failures must be preserved without retrying or editing the compiler/source to make results pass.

## Required read order

1. `Docs/AssemblyShadow/README.md`, then `Plan/CURRENT_STATUS.md`.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` (all old PASS/FAIL outcomes immutable).
3. [Primary source review](../History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/PRIMARY_REVIEW.md) and [machine evidence](../History/M07R/R03/IR_Remediation/P1_INACTIVE_LIVE_GENERAL_2026-10-17/EVIDENCE.json).
4. [Last consumed owned-general PASS](../History/M07R/R03/local-validation-p1-owned-general-20261016-3dc9/README.md), [first-use PASS](../History/M07R/R03/local-validation-p1-firstuse-class-20261016-f598/README.md), [managed receipt PASS](../History/M07R/R03/local-validation-p1-managed-receipt-20261016-0620/README.md) and [earlier consumed FAIL](../History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/README.md).
5. This exact entire handoff, before any execution.

## Four canonical source repositories and exact branch

All repository origins must resolve to canonical `night-outlook/<repo>`, every checkout is a separate clean Git repository on `codex/assembly-shadow-r01b-h1`. All existing actual local paths are rooted at `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`. The current feature heads are:

| Canonical repository | Existing Local checkout path | Required exact current source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final pushed commit containing THIS handoff**, matching current demo HEAD and the 40-character demo SHA in the accompanying final Primary handoff prompt; Demo source+CLI CI anchor `d7b923e9d97b89d67149d6f659d61546a966de6f` and ALL intervening changes must be Docs-only |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `5667e3712f49e4b38c7dd7359e57f81e344626da` |

**Native source + host CI authority:** [39085622437](https://github.com/night-outlook/il2cpp_plus/actions/runs/39085622437) at exact native `5667e371...` Passed 3/3 jobs on macOS Clang and Linux Clang/GCC, 13 distinct strict + 13 sanitized groups/job (78 total). The three ZIP hashes and 57 manifest files independently verified. **Demo CLI/aggregate regression CI:** [39085881448](https://github.com/night-outlook/hybridclr_demo/actions/runs/39085881448) at exact demo source `d7b923e9...` Passed 2/2 Mac/Linux jobs, 19 unittest methods each; two ZIP hashes and 10 manifest files verified. These host tests use explicit VM/SDK/Git subprocess mocks; they are NOT the forthcoming installed Unity SDK evidence.

**Source transport:** the demo's latest pushed `WEB_TO_LOCAL.md` commit is required to equal the clean demo checkout HEAD, the live remote feature HEAD and the final Primary prompt's exact demo SHA. Verify that `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` resolves to the same commit. A later source or Docs-only commit invalidates this authorization until a fresh reviewed handoff. Reject all dirty, noncanonical, unrelated, unavailable or divergent worktrees. Never reset, clean, force-push or overwrite unrelated state; only fast-forward clean ancestor histories. Historical `Tools/AssemblyShadow/R03/source-pins.json` remains unchanged at its earlier native execution pin; this batch explicitly passes candidate native SHA `5667e371...` without updating historical source-pins.json.

## Primary implementation complete, not delegated

- Native: `AssemblyShadowBoundedGeneralLive.h` (preallocated bounded startup scratch/source pointers/receipt) and `AssemblyShadowBoundedGeneralLiveSource.inl`, included exactly once from current `AssemblyShadow.cpp` and exposed only as an inactive native API in `AssemblyShadow.h`. The outer metadata lifetime reader spans all four existing owned source-capture methods and final `Compose`; source controls are compared before collection, after collection, after formatting. Witnessed publication changes invalidate even finished bytes. **Equal read-fence samples do not prove a global coherent VM epoch or ABA freedom.** No original Player/general/execution getter was replaced.
- Native host: `bounded_general_live_fixture.cpp` tests the exact production method under explicitly mocked VM operations, but real owned Capture/Composer/legacy serializer types; `run_bounded_general_live.py` binds the actual native `.inl`, header and `.cpp` inclusion identities and saves raw strict/sanitized command receipts.
- Demo: additive `live-general` twelfth child in the one-shot wrapper, with inner `PassedWithinInactiveSourceHostScope`; source hashes and false-runtime flags retained. The managed receipt/aggregate CLI regression covers a failed live-general child without promoting the aggregate just because managed/native children Passed.
- Existing native official Unity SDK compiler list stays at **75** `-fsyntax-only` configurations (15 C++17 arm64 translation units × five profiles). `AssemblyShadow.cpp` itself now compiles the live source `.inl` under each feature/debug/probe/diagnostics configuration; there is **no** new unbound external source/ABI. Official managed compiler still uses the original five positive products plus `OriginalUnsignedCounts` expected-negative exit1/two CS0266/no DLL.

## One unused evidence+SDK-scratch set, ONE invocation

Require the following exact roots all **absent**, canonical, disjoint from checkout/Unity installation/each other/previous evidence, with sufficient approved external storage:

- Raw batch: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-LIVE-GENERAL-20261018-5667`
- Installed SDK-copy scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-LIVE-GENERAL-20261018-5667`
- Independent Local authority/audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-LIVE-GENERAL-20261018-5667`
- Additive versioned checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-live-general-20261018-5667/`

Installed official Unity2022.3.62f2 arm64 SDK anchor (read-only; **do not launch**):
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.

After source/remote verification, before-input/source/SKD/evidence preservation receipts, space and absence checks, execute exactly **one** invocation:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=d7b923e9d97b89d67149d6f659d61546a966de6f
NATIVE=5667e3712f49e4b38c7dd7359e57f81e344626da
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-LIVE-GENERAL-20261018-5667" \
  --sdk-scratch "$B/Scratch-R03-P1-LIVE-GENERAL-20261018-5667"
```

A failed command **consumes** this attempt. Do not rerun a child manually, resume old roots, construct a second root with a renamed suffix, or edit source to make a failed receipt green.

## What Local must independently validate and publish

All **12** outer components must be independently checked, not inferred from the aggregate: `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, new `live-general`, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk` and `native-sdk`. To report fresh **PASS / PassedSourceHostAndSDKOnly**, require 12/12 Passed, zero child errors, sourcePreserved=true, postflightError=null, both SDK attempted/passed flags true, exact verified four-source tuple, and no historical evidence/state reclassification.

For the **new live-general** child: require inner `PassedWithinInactiveSourceHostScope`, **13 distinct source-case groups/profile**, four strict/sanitized native compile/run receipts with exit0, a matching real method SHA256 `232bd739bc6a54e8047118fbba8eb301a58f67e869ca8ce974902c8c382244a8`, source preservation and 0 watched new allocations after prewarm. Verify exact V1 bytes under host mocks and fail-closed metadata closed gate, four child source failures, startup bounds, mismatched observed usage/state during collection and during formatting, one-shot output, plus explicit `coherentVmEpochProven=false`, `nativeClassPointerOriginProven=false`, `realShutdownDeadlockFreedomProven=false`, `originalLiveGettersReplaced=false` and `runtimeAcceptance=false`. These mocks do NOT prove actual VM race/epoch safety.

The retained `owned-general` component must retain its original `PassedWithinOwnedHostScope`, 11 groups/profile, no allocations after prewarm and exact general V1 byte parity. First-use remains 15 groups/profile and original metadata/physical/class/transaction/frozen-V2 source/host checks are separate. The official managed SDK product/build_api nested result must retain five passed positive DLLs plus exact separate negative compiler result, returned SHA256 and canonical `managed-sdk/build-api/results.json` path, `returnedBindingVerified=true`, inner/outer Passed. Reject missing/mutated/decoy receipts; do not fabricate root `results.json`.

Official native SDK requires all **75 actual arm64 C++17 syntax commands** under the installed Unity2022.3.62f2 SDK, 15 unique source units × candidate/debug/probe-off/diagnostics-off/feature-off; this explicitly includes compiling the real `AssemblyShadow.cpp` containing the new `.inl` method, plus Runtime.cpp, Assembly.cpp, visibility and the previously published composer syntax probe. Retain all commands, compiler warnings/errors and copied SDK input hash receipts; previous 75-unit Local source versions do NOT replace this new compiled candidate. This is **not** linking, Player execution, native Shutdown or GC/RSS qualification.

Verify all historical consumed FAIL/PASS raw result/manifest and external scratch hashes unchanged, source and installed SDK before/after, original four deliberate legacy symlink negative-control fixtures via nested manifests, complete output manifest and localized command streams. Warning counts are observations: never assume they must equal history or suppress anything to pass. Preserve if NativeSDK/managed child fails while others pass; do not rewrite the aggregate.

Local may update ONLY factual [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md), [RETURN_TO_WEB.md](RETURN_TO_WEB.md) and the additive checkpoint, with bounded environment diagnosis; no edits to product, tests, managed/native compiler tooling, historical pins, V1/V2 semantics or engine owner. Commit/push factual source-bound evidence and publish all four remote SHA tuples, including exact copy bindings to external SDK/product binaries, without uploading Unity vendor binaries.

## Ownership, outstanding gates and stop boundary

**P1 still Incomplete:** the native method is real but inactive; a three-sample observed-source fence is not global VM epoch/ABA, class pointer origin, complete R02/execution capture, real type-key allocation/GC/RSS or Shutdown/lock proof. **P2 NotIntegrated**, native/C# authenticated V2 evidence/unchanged semantic verifier missing. **E0 Blocked/Unavailable** for source/vendor-supported Unity2022.3.62f2 StandaloneOSX engine safe point. **E1 BlockedByE0** for native callback drain, GC/finalizer maintenance and restart; **Full P3 Incomplete**. No Player runtime or Human Review Gate.

The prior `20261016-3dc9`, `20261016-f598`, `20261016-0620` PASS cycles and `20261016-0a0b` FAIL are consumed. SNAP-01/N/M/K/I/E, historic R02 fingerprint and R03 independent full-stage FAIL, strict original S custody Blocked remain immutable. Original uncapped 500ms/1–64 native report requirements, V1/V2 budgets, metadata cap, logger/GC/recovery/canary predicates remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

**STOP immediately after the one fresh 12-component SOURCE+SDK batch and return to Primary Implementation.** The returned PASS/FAIL/Blocked result does not authorize a second batch, a Player, a runtime scheduler or the next milestone.
