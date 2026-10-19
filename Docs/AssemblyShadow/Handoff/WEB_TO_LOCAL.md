# Primary Implementation → Local Validation — ONE opaque-inventory lifetime-receipt source/SDK cycle

**ONE NEW source-pinned 16-component SOURCE/HOST + installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation batch is authorized**, and only after the exact remote/custody checks below. The objective is to validate Primary's typed lifetime receipt/fail-stop correction together with the unchanged inactive opaque nonempty inventory source and all retained components. No Unity Editor, Test Runner, Player, native linked runtime, seven-root SNAP-01, vendor engine-owner experiment, Human Review Gate, H2/X02/M08A or other milestone is authorized. Local must not modify nontrivial native, demo, compiler, test or design code.

## Historical authority — consumed vs superseded

- The **latest actual Local result** is 20261019-48ee **PASS / PassedSourceHostAndSDKOnly**: 15/15 components, 70 regression tests, five real managed positive products plus the original exact compiler-negative, 85/85 native SDK syntax. It is **consumed**. Its Local-owned raw, SDK scratch, independent audit, checkpoint, and earlier PASS/FAIL/Blocked source tuples are immutable.
- The prior opaque inventory source handoff at demo d4daea59682ffd14a8ff8b282c280733bcecb3d8 has been **superseded by a new source commit**, not retroactively reported as PASS/FAIL or consumed. No Local return for that old handoff is currently present in the published Local-owned report. If any of its roots exist, preserve their factual state and **do not** rerun or reuse them. Do not infer status from GitHub host CI.
- Historical SNAP-01/N/M/K/I/E/R02 immutable fingerprint FAIL, original strict S custody Blocked, and R03 independent full-stage FAIL/re-review NotRun all remain exactly as documented. No evidence may be reclassified.

## Mandatory read order

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md` at exact final demo SHA.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` first, then `Handoff/RETURN_TO_WEB.md`. Treat their original 20261019-48ee and earlier tuples as authoritative and immutable.
3. [Focused design](../History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/DESIGN.md), [Primary review](../History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/PRIMARY_REVIEW.md), [source/CI evidence](../History/M07R/R03/IR_Remediation/P1_OPAQUE_LIFETIME_2026-10-19/EVIDENCE.json), and original [opaque inventory design](../History/M07R/R03/IR_Remediation/P1_OPAQUE_EXECUTION_INVENTORY_2026-10-19/DESIGN.md).
4. This complete WEB_TO_LOCAL.md and the original remaining implementation plan; do not substitute an older chat or branch/tag hash.

## Four exact repositories, branch and working copy paths

All use branch `codex/assembly-shadow-r01b-h1`. The four nested directories are separate Git working trees; `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` itself is NOT one repository. Check canonical night-outlook origin, branch, local SHA, live `git ls-remote` SHA, clean working-tree status, registered worktrees and submodules before any action. Fast-forward clean ancestors only; never `git reset --hard`, `git clean`, force-push or overwrite unrelated files.

| Canonical GitHub repository | Existing Local checkout | Required exact pushed SHA |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | **Final pushed handoff-containing Docs-only HEAD**, exactly equal to `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, the live remote branch HEAD, and the Primary final handoff prompt's full 40-character SHA. The source/test/CI anchor is `d548799cc026b2ca78b40b7289fed404a3e8ec96`; every commit after the anchor MUST change `Docs/**` only. |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `5e2326a45bd6070aa25830ca8c0236e1915bde13` |

Any new branch push after the final Primary SHA (even Docs-only) invalidates this authorization until a separately reviewed handoff is published. Preserve historical `Tools/AssemblyShadow/R03/source-pins.json` and all original SHA/fingerprint failures; candidate native is explicitly selected by `--candidate-native-sha` and must not rewrite historical pins.

## Primary implementation that Local must verify, not modify

**Corrected opaque lifetime contract:** For completed `opaque-inventory` and `empty-live` child results, the actual `read_component_result()` requires a present boolean `commandLifetimeUnverified` value. A missing/invalid result or missing/string/null marker after completed native child is **FailedOrIncomplete**, `commandLifetimeUnverified=true` and `NativeLiveReceiptUnavailableOrInvalid` stop. Subsequent scheduled components are `NotRun` **without component roots**; postflight Git/source calls are not launched while command lifetime is uncertain. A reported true marker also stops; a known completed exit!=0 with a valid false marker remains Failed but does NOT automatically stop unrelated independent checks. Other historical components retain original optional marker policy.

**Regression proof:** Five new opaque-specific negative cases, retaining all 70 original tests; **75 unique tests (5+14+34+10+12)**. Source/host CI [39256679075](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679075), [39256679128](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679128), [39256679215](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679215) passed on Mac/Linux; native opaque CI [39244090056](https://github.com/night-outlook/il2cpp_plus/actions/runs/39244090056) passed 3/3. These are HOST/mock source tests, not installed SDK or native Player evidence.

**Unchanged native opaque inventory:** `TryCaptureOpaqueExecutionInventory` is inactive and provides only fixed-size zero/nonzero **opaque pointer identity census** from a native observation table. It does not dereference, serialize or return class pointers. Source bounds: 2,048 slots, maximum 1,024 values, two slot samples under the short native lock and metadata-lifetime ticket; it does NOT prove physical pointer origin/lifetime, ABA-free global epoch, full execution type keys, GC/RSS, native teardown, linked Player or full acceptance.

**Retained preflight:** Existing 16 independently receipted components, including `opaque-inventory` (expected `PassedWithinInactiveOpaqueHostScope`). The new native component runs 18 distinct groups in each of strict and ASan/UBSan, with five exact compiler-version/compile/run receipts. Existing empty-live remains 20×2; owned-execution/R02 35×6; live-general 13 per strict/sanitized; owned-general 11 per profile; first-use 15 per profile. Managed: five positive compilation products and separate original expected-negative `OriginalUnsignedCounts` exit1, exactly two CS0266 and no DLL; canonical nested producer result+hash binding remains unchanged. Native official syntax candidate: **90 C++17 arm64 -fsyntax-only configurations = 18 actual units × five original candidate/debug/probe-off/diagnostics-off/feature-off profiles**, including full real `AssemblyShadow.cpp` and the new opaque signature probe. No SDK/compiler source code or runtime entry-point changed in this increment.

## ONE fresh unused evidence root set

Every following path MUST be absent before admission, canonical, disjoint from the four checkout directories, Unity installation, older raw/scratch/audit/checkpoints, and one another, with adequate approved external disk space. The prior 20261019-48ee raw/scratch/audit/checkpoint remain immutable. Do not precreate independent Local audit/checkpoint in the Primary runner. No vendor SDK binaries may be committed.

- Raw result: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-OPAQUE-LIFETIME-20261019-d548`
- SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-OPAQUE-LIFETIME-20261019-d548`
- Independent Local audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-OPAQUE-LIFETIME-20261019-d548`
- Additive evidence checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-opaque-lifetime-20261019-d548/`

The read-only official SDK anchor is `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. **Do not launch Unity**. Preserve inherited TMPDIR/CXX and existing controlled SDK subprocess behavior; do not modify or suppress compiler warnings.

## Exactly one invocation after independent admission checks

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=d548799cc026b2ca78b40b7289fed404a3e8ec96
NATIVE=5e2326a45bd6070aa25830ca8c0236e1915bde13
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-OPAQUE-LIFETIME-20261019-d548" \
  --sdk-scratch "$B/Scratch-R03-P1-OPAQUE-LIFETIME-20261019-d548"
```

**Exactly one** invocation is permitted. PASS, FAIL, interruption, timeout and Blocked all consume the attempted roots. Do not resume/retry/relabel or launch skipped children separately. A known or unknown lifetime-unsafe child must stop all later scheduled subprocesses and skip postflight source/Git subprocesses; record `NotRun` cells explicitly and retain raw stream prefixes/null exit/availability rather than inventing quiescence.

## Independent results and evidence requirements

Inspect all **16** cells individually: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, `empty-live`, `opaque-inventory`, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`. To record a fresh source/SDK-only PASS, require 16/16 `Passed`, all authentic expected inner scope results, sourcePreserved=true, postflightError=null, stoppedAfter=null, SDK attempted/passed flags true and exact four source/remote SHAs. Verify new **75/75** command contracts, opaque native strict/sanitized **18 group cases each**, five successful command receipts, byte-authenticated source arrays, sourceMethodSha256 `574ed4a99e7664686f2093cbf27a6c95df06e35440aef1c3331229aac2542152`, and all pointer/VM/runtime acceptance flags false. Verify exact **90/90** official native arm64 syntax compiler receipts and the five positive/one negative managed control, warnings preserved as observed.

Independently verify preserved SDK before/after, full consumed P1 results/manifests/raw/scratch and negative symlink controls, historical FAIL/Blocked/NotRun, direct child command binary/hash receipts, and full raw/scratch input inventory/copy bindings. Preserve unknown-lifetime results and the distinction between host source mocks, installed SDK syntax and full runtime. No past result can be promoted or corrected retroactively.

Local may update **only** factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and the ONE new checkpoint under the path above, plus bounded environment diagnosis. Commit/push those results without changing Primary design/native/tests/compiler/SDK or any older evidence. Return exact latest four SHA tuples to Primary Implementation.

## Mandatory stop

STOP after this one source/SDK batch. This result cannot authorize Unity Editor/Player, native linking, restart/engine-owner work, Human Review Gate or another milestone. P1 remains incomplete (actual class provenance/owned metadata, nonempty type-key rows, coherent all-VM epoch/ABA, original getters, GC/RSS, locks/Shutdown); P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Preserve all original SNAP-01/N/M/K/I/E/R02 fingerprint failures, S custody Blocked, R03 independent failure/re-review NotRun, and original uncapped 500ms/1–64 report, logger/GC/canary/recovery and V1/V2 transport predicates. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
