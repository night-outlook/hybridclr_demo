# Primary Implementation → Local Validation — ONE P1 owned-execution source/SDK cycle

**Authorized: exactly one fresh 14-component source/host + installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation batch.** The underlying owned execution/R02 feature, frozen-general bridge, original Player getters and V1/V2 semantic transport remain inactive/unchanged. This does NOT authorize launching Unity Editor, Test Runner, Player, linked native runtime, SNAP-01, another seven-root runtime batch, engine scheduler experimentation, Human Review Gate, H2/X02/M08A or other milestones.

**Prior Local evidence is consumed.** The original `20261019-cmdfail-e29a` Local return is PASS / `PassedSourceHostAndSDKOnly`, 13/13 including 53 command-failure tests and 75/75 official SDK syntax; the earlier `20261018-5667` 12/12 PASS and earlier 11/10-component cycles are also consumed. Do not rerun or reclassify any original PASS/FAIL/Blocked evidence. This is one new source-pinned successor, not a retry.

## Mandatory next-agent read order

1. `night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md` and `Plan/CURRENT_STATUS.md`.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` **first**, then `Handoff/RETURN_TO_WEB.md`; preserve exact original factual states and the latest cmdfail-e29a checkpoint.
3. [Primary P1 design](../History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/DESIGN.md), [review](../History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/PRIMARY_REVIEW.md), [evidence](../History/M07R/R03/IR_Remediation/P1_OWNED_EXECUTION_SOURCE_2026-10-19/EVIDENCE.json).
4. This entire handoff; follow source checks/one command/stop without inferring missing commits or authorizations from chat.

## Source authority — four exact canonical repositories

Every local checkout is a separate clean Git repository on `codex/assembly-shadow-r01b-h1`, with canonical `night-outlook/<repo>` origin and local HEAD exactly equal to its verified remote HEAD. Workspace root is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; the parent directory itself is not a repository. Fast-forward clean ancestor working trees only; do not reset, clean, force-push, overwrite or silently include unrelated work.

| Canonical repository | Local absolute checkout | Required commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final pushed HEAD containing this exact `WEB_TO_LOCAL.md`**, equal to `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` and the exact 40-hex demo SHA in Primary's accompanying final Local prompt. Source/tests/CI anchor `35c5a02e90f32be4f6da8307d0a539bdf696a10f`; ALL later changes must be under `Docs/**` only. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `f0c5afe43fe256ac09fabacd5d40f82956988fe2` |

The demo source anchor is not the Local execution SHA: Local must use the final handoff-containing remote HEAD from Primary's exact prompt. A subsequent source or Docs-only update invalidates this authorization until Primary publishes another reviewed handoff. The native fix retains preceding inactive owned execution/R02 source commit `d8a1df3007e93aeb65dd9fe97ab96b4771de8f17`; the original macOS CI FAIL 39208403669 is historical. [Native CI 39212760872](https://github.com/night-outlook/il2cpp_plus/actions/runs/39212760872) PASSED 3/3 after the compiler `-I vm` → `-iquote vm` fix, but is host-only. [Demo managed receipt/aggregate CI 39213798210](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213798210), [command failure CI 39213581041](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213581041), and [new owned syntax host CI 39213944245](https://github.com/night-outlook/hybridclr_demo/actions/runs/39213944245) PASSED; none are installed SDK/Player evidence.

Historical `Tools/AssemblyShadow/R03/source-pins.json` **must not be edited**: it records earlier real executions. Candidate native source `f0c5afe...` is provided explicitly through `--candidate-native-sha` by the orchestration script, which must preserve historical on-disk pins and originally failed results.

## Primary changes completed — Local must only validate

- Inactive native owned execution/R02 record `AssemblyShadowFrozenExecutionRecord.h`, `AssemblyShadowR02Snapshot.h`, `AssemblyShadowFrozenR02Serializer.h` retains its bounded/immutable type design and source-bound 35-case per profile strict/sanitized host fixture. No active original getter/caller/Player invokes it.
- New `owned-execution` fourteenth host child invokes `tools/r03/diagnostic_stream/run_frozen_execution.py` and independently expects `PassedWithinOwnedExecutionHostScope`. Six profiles = diagnostics 0/1/2 × strict/ASan+UBSan; retained source hashes, original reference headers, actual counter-source host controls, 13 compiler/version/run receipts and zero watched-new assertion. All observed source equality is bounded and not a coherent all-VM epoch; host class rows are fixtures.
- Existing 13 child checks, all error paths, fail-stop/NotRun receipts, original 53 command-failure regressions, managed five positive product builds plus separate `OriginalUnsignedCounts` expected-negative exit1/two CS0266/no DLL, historical source and SDK preservation are retained, without changing semantic guards.
- Native SDK candidate matrix expands from **75 → 80 actual C++17 arm64 `-fsyntax-only` configurations**: 16 real translation units × existing 5 candidate/debug/probe-off/diagnostics-off/feature-off profiles. The new 16th unit `Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowExecutionComposeSyntax.cpp` compiles actual record/counters types, capacities and signature pointers against the installed official SDK; it is NOT a stub-only substitute. Original noncandidate unit count remains 12×5.
- New mock negative aggregate integration tests reject failures in both `live-general` and `owned-execution` even when managed/native SDK children pass. No fake receipt, default PASS, policy relaxation, R02 fingerprint rebasing, test skip or threshold increase is permitted.

## ONE authorized unused root set and original SDK anchor

All four paths below must be **ABSENT before preflight**, canonical, mutually disjoint, outside all checkout/Unity installation/prior evidence, with approved external disk space. The prior cmdfail-e29a raw/scratch/audit/checkpoint roots and all earlier evidence must remain untouched.

- Raw batch: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-OWNED-EXECUTION-20261019-f0c5`
- SDK copy scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-OWNED-EXECUTION-20261019-f0c5`
- Independent Local authority/audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-OWNED-EXECUTION-20261019-f0c5`
- Additive checked-in checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-execution-20261019-f0c5/`

Installed official read-only Unity2022.3.62f2 SDK anchor (do NOT launch): `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Keep original inherited TMPDIR and existing child/private/tmp compiler ownership policy; no Local workaround or vendor SDK change.

### Exact one-shot invocation

Only after all four clean canonical source/remote pins, pre-evidence/historical inventories, SDK before-hashes, audit-root absence and space admission are verified:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=35c5a02e90f32be4f6da8307d0a539bdf696a10f
NATIVE=f0c5afe43fe256ac09fabacd5d40f82956988fe2
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-OWNED-EXECUTION-20261019-f0c5" \
  --sdk-scratch "$B/Scratch-R03-P1-OWNED-EXECUTION-20261019-f0c5"
```

ONE invocation only. A failed or blocked attempt consumes these roots and must not be retried or resumed. Do not execute a second batch under a renamed root, patch compiler/SDK/native source locally, or run a skipped child separately to turn a result green. An unknown child lifetime halts later commands and requires preserved `NotRun` receipts; do not assume descendant quiescence from process exit.

## Independent validation and output requirements

Inspect all **14 outer cells**, not merely the aggregate: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, new `owned-execution`, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`.

For fresh **PASS / PassedSourceHostAndSDKOnly**: 14/14 `Passed`, all child inner results match exact documented scope; sourcePreserved=true, postflightError=null, stoppedAfter=null, both SDK attempted and passed, exact four source/remote pins, no historical evidence reinterpretation. Verify `owned-execution` has 6 profiles each 35 distinct case groups, 13 successful version/compile/run receipts, exact original reference content hashes, type ownership/V1 parity, actual **host** R02 source cases, expected negative cases, and retained `officialSdkCompile=false`, `UnityPlayerExecuted=false`, `coherentVmEpochProven=false`, `classPointerOriginProven=false`, `runtimeAcceptance=false` flags. Source/host counters and mocks cannot prove live VM epoch/race/teardown.

Confirm 80 actual native SDK syntax receipts = 16 distinct units × five profiles, including the exact new owned execution probe and the retained existing `AssemblyShadow.cpp` real live-general body. Verify SDK file/input hashes and warning/error inventories; retain diagnostics even on failure. Managed must preserve exact producer nested path+SHA join, five positive products and one expected-negative compiler with exactly two CS0266/no DLL. Warn counts are observations, not silently forced to historical values.

Rehash all consumed P1 root/manifests and external SDK scratch/source before/after, including the original historical symlink negative controls; source and installed SDK must remain unchanged, no Unity vendor/product binaries uploaded. Retain original failures and individual error statuses if any child fails, do not recompute historical success. Collect command stdout/stderr binary receipt hashes, original checked result/manifest, independently audited artifact inventories and copy bindings to unchanged external inputs. Create a new additively versioned checkpoint under the single path listed above. Local may update ONLY factual `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, and this new checkpoint, with strictly bounded environment diagnosis; all nontrivial fixes remain Primary-owned.

## Required stop / next-agent state

Immediately after ONE factual source/host/SDK preflight, commit and push exact evidence and four source/remote tuples, then return to **Primary Implementation**. Even a 14/14 PASS **does not** authorize linked native Player, Unity Editor, new engine scheduler, P2 production integration, runtime seven-root acceptance, Human Review Gate or next milestone. P1 coherent global VM epoch/ABA, live getter integration, real class pointer origin, allocation/GC/RSS/Shutdown safety remain Incomplete; P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Original SNAP-01/N/M/K/I/E FAIL, historic R02 fingerprint FAIL, strict S custody Blocked and independent R03 full-stage FAIL/re-review NotRun remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
