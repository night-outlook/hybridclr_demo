# Primary Implementation → Local Validation — ONE P1 empty-live receipt/lifetime source/SDK cycle

**ONE NEW 15-component source/host + installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation cycle is authorized** after complete source, remote, SDK and evidence admission. This focused task validates Primary's fix for `IR-LOCAL-P1-EMPTY-LIVE-RECEIPT-01`: honest native compile receipts, typed summary lifetime propagation, fail-stop of missing/invalid empty-live summary and unchanged existing original source/SDK contracts. It does **not** authorize Unity Editor, Test Runner, Player, linked runtime, native scheduler, SNAP-01/other consumed P1 batch, seven-root runtime acceptance, H2/X02/M08A, Human Review Gate, or another milestone. All nontrivial code/design/test/compiler fixes remain Primary-owned.

**Original Local return (consumed, immutable):** `20261019-d16d` PASS / `PassedSourceHostAndSDKOnly`, 15/15 components, existing empty-live 2×20 host groups, owned execution 6×35, 53 original command failure tests, official managed 5 positive/one expected negative, 85/85 native SDK syntax. Its original `IR-LOCAL-P1-EMPTY-LIVE-RECEIPT-01` is `SourceConfirmed_NotFaultInjected`: issue **not observed during the successful batch**. Preserve exact original source finding, raw evidence, checkouts and historical status. This is a fresh successor for corrected source, **not a retry**.

## Mandatory read order

1. `night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md`, then `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`.
2. Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` **first**, then `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md`. Read the complete `20261019-d16d` PASS and its [original source finding](../History/M07R/R03/local-validation-p1-empty-live-20261019-d16d/FINDING.json) exactly as published.
3. [Primary bounded design](../History/M07R/R03/IR_Remediation/P1_EMPTY_LIVE_RECEIPT_2026-10-19/DESIGN.md), [Primary source review](../History/M07R/R03/IR_Remediation/P1_EMPTY_LIVE_RECEIPT_2026-10-19/PRIMARY_REVIEW.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_EMPTY_LIVE_RECEIPT_2026-10-19/EVIDENCE.json).
4. This entire handoff, then the unchanged [remaining implementation plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md). No chat-dependent state or historical branch/commit assumptions.

## Four exact repository/branch/source pins

Each path is a separate clean Git checkout; the shared parent directory is **not** itself a Git repository. The only branch is `codex/assembly-shadow-r01b-h1`; verify actual `night-outlook/<repo>` origin, current local branch, local SHA, **live** remote SHA, clean status and Git worktree/submodule provenance. Use safe fast-forward of clean ancestor histories only; never reset/clean, overwrite unrelated changes, merge, force-push or change historical evidence.

| Canonical GitHub repository | Existing Local absolute path | Required exact pushed SHA |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final handoff-containing Docs-only commit**, equal to the exact 40-hex demo SHA in Primary's final prompt, the current remote branch HEAD, clean checkout HEAD and `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. Source/test/CI anchor: `22f058f47ba41fbcb72d4dced8b658870d4f1149`; **all commits after this anchor must be `Docs/**`-only.** |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `48ee6468065a6b559f53719dc310d901d8181ab8` |

Do **not** modify original historical `Tools/AssemblyShadow/R03/source-pins.json` at previous native `74dbdbea80d83923863303bd2b2c0a87f36541b1`. Current candidate/native source is explicitly supplied through `--candidate-native-sha` by the one-shot runner. The old exact Local execution SHA `8514c03c...`, latest consumed evidence publication `62b9102bc7...`, former native `d16d2f7...` and older CI/source tuples remain separate immutable facts. A later branch update, including Docs-only after the handoff commit, invalidates this authorization until Primary reissues a reviewed handoff.

## Primary-owned implementation and host CI

- Native `tools/r03/diagnostic_stream/run_bounded_execution_empty_live.py` no longer omits its aggregate `commandLifetimeUnverified` boolean; it equals the OR of the five direct command receipts and is always explicitly present on a new completed result. Timeout/interruption/unknown child outcome retains captured byte prefixes, availability, exact SHA and null unknown exit. **No postflight source hashing when command lifetime is unknown**: `sourcePreserved=false`, `sourceAfter={}`, explanatory `postflightError`, `MANIFEST.inventoryScope=UnsealedObservedFiles` and `commandLifetimeUnverified=true`. No global kill, retries, altered compiler flags, modified timeout or invented descendant quiescence.
- `actualProductionHeaderAndMethodCompiled=true` now requires **both** strict and sanitized direct compiler receipts passed with exit0 and completed source-preservation evidence. A compiler-version-only, missing-compiler, failed compile, runtime child timeout or ambiguous source identity may never claim successful compilation. Known spawn failure/completed nonzero remain ordinary Failed with preserved accurate receipts.
- Demo `run_p1_metadata_local_preflight.py` treats **only the `empty-live` component** as requiring an explicitly present boolean lifetime marker. Missing/invalid/symlink/undecodable summary or marker fails closed with `EmptyLiveReceiptUnavailableOrInvalid`: outer `commandLifetimeUnverified=true`, later cells `NotRun` without creating their roots, no postflight Git verification. All other children retain their existing optional-marker compatibility; a known completed nonzero with explicit false marker remains ordinary Failed while independent checks can run.
- Tests: the new 12 native `test_bounded_execution_empty_live_receipts.py` methods (controlled subprocess/compiler outcomes, real runner/main source); five new demo `test_p1_command_failures.py` native-to-outer consumer cases; original 53 regressions remain. Full source-bound `run_p1_command_failure_tests.py` now requires **70 distinct PASS** methods across five modules: **5 + 14 + 29 + 10 + 12**. The actual Python code/tests/CI are Primary-published. The verified host CI includes [native Mac/Linux runner](https://github.com/night-outlook/il2cpp_plus/actions/runs/39225984719) and [cross-repo 70-test Mac/Linux integration](https://github.com/night-outlook/hybridclr_demo/actions/runs/39227242254); both **PASSED** (3/3 native and 2/2 integrated jobs). These results do not qualify the installed SDK or Player. The earlier macOS fixture-path CI failure and earlier demo mock-marker CI failures remain historical FAILs, not rewritten.

**Unchanged product/runtime**: `AssemblyShadow.cpp`, all VM native API/getter/guard and source method logic, C# Player/managed compiler helper, manifest ABI, V1/V2 budgets and original semantic verifier are unchanged in this cycle. Zero-class live feature remains **inactive**; class pointer origin/VM epoch are not established. The native method's 20 host groups/profile and owned-execution's 35 groups × 6 profiles remain required.

## New ONE unused evidence+scratch+audit+checkpoint set

Confirm ALL four roots **absent before execution**, canonical, mutually disjoint and outside checkouts, Unity Editor/source installations, all original Local raw/scratch/audit roots and each other, with independently approved external disk space. Do not precreate the Local-owned audit or checkpoint in the Primary runner. Original `20261019-d16d` roots are consumed, immutable and MUST NOT be reused.

- Raw batch: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee`
- SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee`
- Independent Local authority/audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee`
- Checked-in new checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-empty-live-receipt-20261019-48ee/`

Read-only official Unity2022.3.62f2 macOS arm64 SDK anchor (**DO NOT LAUNCH**):
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
Preserve the inherited TMPDIR, pinned SDK/vendor files and existing owned-compiler process policy. Never commit SDK/vendor or generated Player binaries.

## Exactly ONE executable invocation after all independent admission checks

Verify clean correct origins/four local+remote SHAs, original evidence hashes/symlink controls, official SDK before hashes, approved storage, absent roots and exact source anchor. Then execute only:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=22f058f47ba41fbcb72d4dced8b658870d4f1149
NATIVE=48ee6468065a6b559f53719dc310d901d8181ab8
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee" \
  --sdk-scratch "$B/Scratch-R03-P1-EMPTY-LIVE-RECEIPT-20261019-48ee"
```

**A failed/interrupted/Blocked invocation consumes this attempt.** No rerun, child resume, renamed suffix/root, original source/SDK patches, compiler workaround, alternate command, or duplicate evidence. If a command lifetime is uncertain, stop all later child processes, write accurate `NotRun` records and unsealed evidence inventory; do not execute further Git/source verification subprocesses while descendants might remain. Return the factual failure to Primary.

## Complete validation and receipt requirements

Require **15 independently verified outer components**, not aggregate alone: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, `empty-live`, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`.

- `command-failures`: one combined native/demo source-bound child, result `PassedWithinHostScope`, **70 unique methods** (5 metadata + 14 managed/aggregate + 29 outer +10 general +12 native empty-live), no failed/errors/skipped/expected/unexpected tests, complete `unittest.log`, exact method inventories, `sourcePreserved=true` and source-hashed SHA/BLOB inputs. Controls cover real Python direct-child timeout prefix, interruption/unknown lifetime, source postflight unavailability, known nonzero, missing compiler, false compile-claim prevention, malformed/missing empty-live summary and outer fail-stop/NotRun. Host CI is not a substituted Unity test.
- `empty-live`: result `PassedWithinInactiveZeroClassHostScope`; actual exact production zero-class header/method source, **2 profiles × 20 independent groups**, 5 successful direct compiler-version/strict/sanitized compile+run receipts, `commandLifetimeUnverified=false`, `actualProductionHeaderAndMethodCompiled=true` backed by exact successful compiler receipts, complete **sourcePreserved=true**, fully sealed original-success manifest and exact original provenance. Host mock/zero-class/acceptance flags remain correctly false. Nonempty class inventory is *always rejected*, not silently dropped.
- Retained native components: owned execution **6×35**, 13 compile/version/run receipts; live-general **13 cases/profile** and owned-general **11/profile** with original byte parity and watched-`new` assertions; first-use 15/profile; legacy, metadata gate, class, physical, transaction, frozen-V2 all retain original distinct verdicts/evidence and source fence limits.
- Official managed SDK: five real positive compiled products plus original separate `OriginalUnsignedCounts` exit1 with exactly two CS0266/no DLL; require original nested `managed-sdk/build-api/results.json` and returned path/SHA/schema/scope join, no fallback/decoy receipt. Preserve all warning logs.
- Official native SDK: all **85 actual C++17 arm64 `-fsyntax-only` commands** (17 translation units × five unchanged feature/debug/probe/diagnostics profiles), including full actual `AssemblyShadow.cpp` source with the already known inactive methods, and the two execution composer/empty-live source syntax probes. No linking, Editor/Player or native runtime acceptance.
- Before and after: original six+ consumed P1 raw/scratch/audit/checkpoints, historical FAIL/PASS, original 28 deliberate P1 symlink negative controls and nested manifests, immutable R02 whole-file fingerprint failure, source/SDK input hashes, all four clean local/remote/source SHAs, installed Unity SDK files, and evidence file/stream digests must remain unchanged. Preserve raw direct-child stdout/stderr and exact size/SHA availability fields; distinguish completed, unavailable, partial, failed, NotRun and reused-audited outcomes.

To report `PassedSourceHostAndSDKOnly`, verify **15/15 passed, zero child errors, sourcePreserved=true, postflightError=null, stoppedAfter=null**, accurate both SDK attempted/passed fields, source/SDK/historical provenance all intact and **no original failure reclassified**. No one child or compiler PASS substitutes for another. `descendantQuiescenceProven=false` remains factual even for a success.

**Ownership:** Local may update ONLY `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and this additive checkpoint, with bounded factual environment diagnosis and no nontrivial implementation. Commit/push the factual evidence, exact tested SHA tuple and external copy bindings. No product/VM/native getter/SDK/manifest/semantic policy modification.

## STOP / unfinished production gates

**STOP immediately after this ONE new source/SDK batch** and return facts to Primary Implementation. A full 15/15 host+SDK syntax pass does **not** prove process-tree liveness, coherent VM epoch/ABA, nonempty class pointer provenance, actual GC/RSS/allocator bounds or Shutdown deadlock freedom; P1 remains **Incomplete**. P2 authenticated native+C# V2 transaction `NotIntegrated`; E0 vendor/source-supported engine-owner safe point `Blocked/Unavailable`; E1 callback-drain/native finalizer maintenance/restart `BlockedByE0`; full P3 linked Player/runtime `Incomplete`. Original SNAP-01/N/M/K/I/E FAIL, immutable R02 source fingerprint FAIL, strict S custody Blocked and R03 independent full-stage FAIL/re-review NotRun remain unchanged. Original 500ms/1..64 uncapped reports, V1/V2 bounds, logger/GC/recovery/canary and semantic verifier unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No Human Review Gate or later milestone is authorized.
