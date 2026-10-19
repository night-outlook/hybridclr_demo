# Primary Implementation → Local Validation — ONE 15-component P1 zero-class execution/R02 source/SDK cycle

**ONE NEW source-pinned SOURCE/HOST + official installed Unity2022.3.62f2 SDK SYNTAX-ONLY cycle is authorized.** Objective: validate the **inactive, fail-closed zero-observed-class execution/R02 live-source bridge** together with every previously retained P1 child, managed SDK contract and exact 85 native C++17 arm64 syntax profiles. This is not authority to launch Unity Editor, Test Runner, Player, linked native binaries, seven-root runtime acceptance, engine-owner tests, SNAP-01, Human Review Gate, H2/X02/M08A, or another milestone. **Local must not modify nontrivial code/design/tests/compiler tooling.**

**Consumed Local evidence:** `20261019-f0c5` 14/14 PASS / `PassedSourceHostAndSDKOnly`, 80 official native SDK syntax configurations, 53 command-failure tests, owned-execution 6×35 host groups, unchanged five official managed products plus `OriginalUnsignedCounts` negative. This run and all prior 13/12/11/10-component P1 PASS/FAIL cycles, SNAP-01/N/M/K/I/E failed results and strict S custody Blocked are immutable. Never rerun, reuse roots, or reclassify historical evidence.

## Required read order

1. `Docs/AssemblyShadow/README.md` then `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`.
2. Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` **first**, then `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md`, including the original `20261019-f0c5` PASS and all consumed failures.
3. [Primary bounded source design](../History/M07R/R03/IR_Remediation/P1_EMPTY_EXECUTION_LIVE_2026-10-19/DESIGN.md), [review](../History/M07R/R03/IR_Remediation/P1_EMPTY_EXECUTION_LIVE_2026-10-19/PRIMARY_REVIEW.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_EMPTY_EXECUTION_LIVE_2026-10-19/EVIDENCE.json).
4. This entire exact handoff, without borrowing assumptions from chat, then the unchanged remaining production plan.

## Four canonical repositories, branch, and complete exact source pins

Each nested path is a **separate Git working tree** on `codex/assembly-shadow-r01b-h1`, with canonical HTTPS or corresponding SSH origin for `night-outlook/<repo>`, clean status and local HEAD exactly matching live remote HEAD. Default workspace root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`. Parent directory is not itself a repository. Use clean ancestor-only fast-forwards; never `git reset --hard`, `git clean`, overwrite dirty files, force-push or merge unrelated commits.

| Canonical repository | Absolute Local checkout | Required published head |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final pushed and independently verified Docs-only handoff-containing commit**, exactly equal to `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, demo remote HEAD and the accompanying Primary final prompt's full 40-hex demo SHA. Tested source anchor `84d9360903573dc473e9dd5cbee25883d07e1a0c`. Changes after this anchor must be `Docs/**` ONLY. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `d16d2f7eee4c0f2333f31c4ec6e40422956d8fd1` |

The source anchor is not the final demo execution commit; take final demo HEAD **only from the Primary prompt plus remote verification**, not an older Local/published document commit. A later modification, even Docs-only, to the final handoff-containing demo HEAD invalidates this assignment until Primary reviews/reissues it.

Do **not** update historical `Tools/AssemblyShadow/R03/source-pins.json` at earlier native `74dbdbea80d83923863303bd2b2c0a87f36541b1`; it is original provenance, not this source candidate. The candidate `--candidate-native-sha d16d2f7...` is passed explicitly by this outer script. Retain all historical source and ABI fingerprint FAILs without rebasing.

**Current host-only CI:** [native zero-class source run 39218817115](https://github.com/night-outlook/il2cpp_plus/actions/runs/39218817115) Passed 3/3 macOS Clang, Linux Clang/GCC. [Demo managed/aggregate run 39219174802](https://github.com/night-outlook/hybridclr_demo/actions/runs/39219174802) and [command-failure run 39219174857](https://github.com/night-outlook/hybridclr_demo/actions/runs/39219174857) Passed, with explicitly mocked child compilers/source. These results are not installed Unity SDK, linked Player or full runtime evidence. The original immutable R02 whole-file fingerprint CI failed after the `AssemblyShadow.cpp` inclusion; do not recast it as a new Player failure or silently rebaseline.

## Implementation completed by Primary, not delegated

Native `libil2cpp/vm/AssemblyShadowBoundedExecutionEmptyLive.h` and `AssemblyShadowBoundedExecutionEmptyLiveSource.inl` declare/implement the actual `AssemblyShadow::TryCaptureBoundedEmptyExecutionLive` method. It is included once by `AssemblyShadow.cpp`, gated by the existing Assembly Shadow compilation switch, and has no original public getter/managed/Player caller. It is safe only within its **bounded zero-observed-class subset**: one outer metadata admission ticket; three fixed-array/observation-lock stamps (count only, no physical pointer dereference); `Snapshot::TryCaptureCurrent` before and after `Record::Begin`/`Freeze`; typed R02 full metric equality and complete coverage required. The method rejects a single nonempty class, mismatched count, dropped/saturated counters, closed ticket, source change, output reuse, formatting errors or invalid/incomplete input. It **does not** prove class pointer lifetime, VM-wide coherence, ABA freedom or real Shutdown/deadlock/GC/RSS costs.

Actual native test `tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py` compiles the exact checked-in method header/inl bytes against explicitly mocked VM/counter/record types, checks source before/after and single source inclusion. **20 distinct groups per strict/sanitized profile; five direct command receipts** (compiler-version + two compile/two execute), all expected to pass. Host mock C++ new allocations or memory are **not** Unity runtime acceptance. New output explicitly states `zeroClassSubsetOnly=true`, `completeExecutionSource=false`, `coherentVmEpochProven=false`, `classPointerOriginProven=false`, `officialUnitySdkCompiled=false`, `UnityPlayerExecuted=false`, `runtimeAcceptance=false`.

Demo one-shot `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py` now adds the 15th independently checked `empty-live` cell, retains 53 command-failure contract tests and every 14 previous host/SDK cells, and refuses incomplete/failure/unknown-lifetime sources without turning them into PASS. Official installed native SDK candidate syntax is **85 commands** = **17 actual C++17 arm64 translation units × five original candidate/debug/probe-off/diagnostics-off/feature-off profiles**. The 17th `AssemblyShadowExecutionEmptyLiveSyntax.cpp` checks the typed method/API/budget surface; `AssemblyShadow.cpp` itself is compiled in all five modes with the actual new `.inl` method. Existing five positive managed products plus the `OriginalUnsignedCounts` expected-negative compiler error (exit1, precisely two CS0266, no DLL), original receipts, warnings and report predicates remain unchanged.

## One unused raw/SDK/audit/checkpoint set — ONLY this cycle

Confirm ALL four names below are **absent**, canonical, mutually disjoint, outside checkout, installed SDK/Unity, and all prior raw/scratch/audit/checkpoint roots, with sufficient independently approved external disk. Preserve prior original `20261019-f0c5` raw/SDK scratch/audit/checkpoint and all older consumed roots, original 24+ symlink historical negative controls and original FAILs exactly.

- New raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-EMPTY-LIVE-20261019-d16d`
- New SDK copy scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-EMPTY-LIVE-20261019-d16d`
- New independent Local authority/audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-EMPTY-LIVE-20261019-d16d`
- New versioned Local checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-empty-live-20261019-d16d/`

Read-only official SDK anchor (**do not run the Unity executable**):
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
Keep inherited TMPDIR, existing owned/private child SDK compiler lifecycle rules, no copied vendor binaries into Git or into previously consumed evidence. Local may create only its own audit and checkpoint after verifying source/remote/space/evidence admission; Primary runner must not precreate those.

## EXACTLY one invocation after all preflight checks

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=84d9360903573dc473e9dd5cbee25883d07e1a0c
NATIVE=d16d2f7eee4c0f2333f31c4ec6e40422956d8fd1
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-EMPTY-LIVE-20261019-d16d" \
  --sdk-scratch "$B/Scratch-R03-P1-EMPTY-LIVE-20261019-d16d"
```

This ONE invocation consumes the new roots on PASS, FAIL, interruption or Blocked. **NO retries**, child resumes, duplicate root names with suffix, or manual compilation to manufacture a pass. A true command timeout/unknown descendant lifetime stops the outer batch; mark remaining cells `NotRun`, preserve partial output and do not start postflight Git subprocesses while a child may remain active. No source/compiler/test fixes are delegated to Local.

## Local validation and evidence checklist

Require **15 distinct** independent cells, not aggregate alone: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, **new `empty-live`**, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`. To classify exact new **PASS / PassedSourceHostAndSDKOnly**, require 15/15 `Passed`, `sourcePreserved=true`, `postflightError=null`, `stoppedAfter=null`, accurate attempted/passed SDK flags, stable exact four-repo pins and no historical status reclassification.

**New `empty-live`:** inner result exactly `PassedWithinInactiveZeroClassHostScope`; host mocks explicitly acknowledged; strict and ASan/UBSan profiles each **20 unique source groups**, 5 direct version/compile/run receipts exits0 and complete source hash preservation, no test skip or automatic host/runtime acceptance. Validate output receipt markers remain `zeroClassSubsetOnly=true`, `completeExecutionSource=false` and all nonacceptance/provenance flags false. Verify real `AssemblyShadow.cpp` includes the method once and original getters remain unchanged. Nonempty observed class rows must never be treated as complete successful `classes:[]`.

**Existing components:** command-failures retains 53 unique source-bound tests (5+14+24+10, zero failures/skips); live-general retains 13/profile under VM mocks, owned-general 11/profile and first-use 15/profile. Owned-execution retains six profiles of 35 groups/profile and all 13 successful compiler/source receipts, typed R02 tests and exact V1 parity under host fixture. Legacy/metadata/class/physical/transaction/frozen-V2 remain distinct source-preserved results; no historical case removed. Managed official result must bind exact nested file path/hash, five positive products and unchanged expected-negative exit1/two CS0266/no DLL. Native SDK must independently execute all **85** actual arm64 C++17 syntax commands (17 unique units × 5 profiles); source compile includes exact `AssemblyShadow.cpp` and the new probe. Warnings are observations, not a reason to suppress diagnostics or change expected flags.

Preserve current source+SDK input hashes and installed Unity SDK (before/after), all prior P1 original raw/batch/manifest and external scratch/ownership receipts, 24+ deliberate historical symlink controls, original R02 immutable fingerprint failure, SNAP-01/N/M/K/I/E FAIL, strict S custody Blocked and full-stage R03 independent FAIL/re-review NotRun. Retain complete command binaries+hashes, signed nested receipts/aggregate, `MANIFEST` with every regular file and separately authenticated symlink controls, source/SDK copy bindings, independent audit receipt and exact Local execution command/time/PID.

Local may update **only** `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and the newly additive checkpoint, plus bounded environment-only diagnosis, then commit/push factual evidence. Do not edit production headers, source, tests, branch pins, V1/V2 semantics, vendor SDK, native runtime/engine owner or old evidence. Return evidence and all four latest remote SHA tuples to Primary Implementation.

## Stop and remaining acceptance restrictions

**STOP after this single bounded batch** regardless of outcome; no second batch, Unity Editor/Player, scheduler experiment, future milestone or Human Review Gate. A source/SDK syntax PASS would still mean P1 **Incomplete**: original live general+execution getters, nonempty class capture/pointer provenance, VM-wide coherent epoch/ABA, allocation/GC/RSS, metadata lock/deadlock/Shutdown still unresolved. P2 `NotIntegrated`, E0 `Blocked/Unavailable`, E1 `BlockedByE0`, full P3 `Incomplete`; original 500ms/1–64 uncapped reporting, logger/GC/canary/recovery and V1/V2 size predicates unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
