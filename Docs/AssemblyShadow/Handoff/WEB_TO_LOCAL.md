# Primary Implementation → Local Validation — ONE R03 P1 first-use class source/SDK batch

**One NEW ten-component host + official installed-SDK syntax-only Local cycle is authorized.** The previous `20261016-0620` source/SDK PASS and `20261016-0a0b` FAIL are **both consumed**. No rerun, resume, repair, root reuse, upgrade of older verdicts, Unity Editor/Player launch, full runtime seven-root batch, scheduler integration test, next milestone or Human Review Gate is authorized here. Local must record factual evidence, not make nontrivial changes. Primary owns all design and implementation.

## Read first

1. `Docs/AssemblyShadow/README.md`, then `Plan/CURRENT_STATUS.md`.
2. Local-owned `Handoff/LOCAL_VALIDATION.md`, then `Handoff/RETURN_TO_WEB.md` (read-only historical PASS/FAIL records).
3. [First-use Primary review](../History/M07R/R03/IR_Remediation/P1_FIRST_USE_CLASS_METADATA_2026-10-16/PRIMARY_REVIEW.md) and [source/CI evidence](../History/M07R/R03/IR_Remediation/P1_FIRST_USE_CLASS_METADATA_2026-10-16/EVIDENCE.json).
4. The [consumed receipt PASS](../History/M07R/R03/local-validation-p1-managed-receipt-20261016-0620/README.md), its [prior consumed FAIL](../History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/README.md), and the [remaining P1/P2/E0/E1/P3 plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).
5. This entire handoff and its stop conditions.

## Exact canonical source authority

All branches are `codex/assembly-shadow-r01b-h1`; all origins must resolve to canonical `night-outlook/<repo>` GitHub. Each existing Local-owned checkout is under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`.

| Repository | Exact Local checkout path | Required current remote HEAD |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | **the latest pushed commit containing THIS handoff**; resolve as described below and compare with the exact demo SHA in Primary's final handoff message |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `1e1d152f0e05b8038427c76a9c8a9b4b60998a72` |

Native implementation commit: `f598f8da5749e7c09ad5816630ce7e40b3f4ebca`; parent native metadata epoch gate: `f71691407bf9af5544d00dd54bff9e2e7eb77307`. Later native commits update **only `.github/workflows/r03-ir-terminal.yml`** to restore current source assertions. The actual P1 first-use CI [38876310270](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876310270) **Passed 3/3**, macOS Clang and Linux Clang/GCC, strict and ASan/UBSan, 15 first-use groups per profile, three ZIP hashes and 57/57 output files verified. The corrected [terminal source workflow 38876957263](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876957263) Passed 2/2. Historical R02 whole-file source fingerprint failure is not reclassified and does not supply new runtime acceptance.

The demo's earlier tested source/CI anchor is `06209426b765a805da2cc2f810ba5da390787099`. Primary verified all subsequent demo changes outside `Docs/` are absent. Do **not** rewrite `Tools/AssemblyShadow/R03/source-pins.json`: its older native execution pin `74dbdbea80d83923863303bd2b2c0a87f36541b1` remains historical. Candidate SDK syntax is admitted using explicit `--candidate-native-sha` through the wrapper.

Before running, check that every checkout is clean, matches its remote, on the correct branch and safe-ancestor fast-forward only. Never reset, clean, force-update or override an unrelated worktree. If the branch is divergent, dirty or unavailable, record Blocked and stop.

## Exact new output roots — ONE attempt only

Subject to independent Local absence, canonical-path, disk, permission, separation and preservation checks:

- Batch evidence: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-FIRSTUSE-CLASS-20261016-f598`
- Official SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-FIRSTUSE-CLASS-20261016-f598`
- Independent Local audit/authority: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-FIRSTUSE-CLASS-20261016-f598`
- Additive Git checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-firstuse-class-20261016-f598/`

If any root is present, do not rename it and retry to evade a consumed attempt. Preserve all historical source, SDK, evidence and scratch roots exactly. Do not upload Unity vendor binary SDK artifacts.

Use official read-only Unity2022.3.62f2 SDK anchor `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. **Never launch Unity Editor.** The compiler scripts read its installed SDK files and copy required native files into the new distinct scratch tree.

## One exact authorized command

After verifying the remote four-repository tuple and that the latest demo HEAD equals the final SHA in the Primary handoff message:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
DEMO_SOURCE=06209426b765a805da2cc2f810ba5da390787099
NATIVE=1e1d152f0e05b8038427c76a9c8a9b4b60998a72
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
git -C "$D" diff --exit-code "$DEMO_SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-FIRSTUSE-CLASS-20261016-f598" \
  --sdk-scratch "$B/Scratch-R03-P1-FIRSTUSE-CLASS-20261016-f598"
```

Run ONCE; on failure preserve all raw and stop, do not rerun components individually or fix production/test/compiler source locally.

## Required combined validation and evidence

The existing aggregate runner executes **ten** independent components: original 8-suite legacy general/execution/current/frozen host tests; metadata lifetime gate; bounded class inventory; bounded physical assembly inventory; bounded **first-use class-bearing** capture; bounded transaction status and inventory; frozen execution/V2; official managed SDK; official native SDK. The first-use component must use the changed `run_bounded_first_use.py` at the exact native HEAD and produce **strict + sanitized** reports, 15 unique case groups per profile and four Passed compile/run records. Verify the exact physical `namespace + "." + name` source text (including `.Class`), class-name ownership, 4096-row limit, metadata-vs-usage lock nonnesting, initial-epoch-only admission, unchanged generation, and fail-closed mutation/overflow/null/alias tests. These are host mocks and do not prove all-VM metadata ownership.

Require five official managed products and the unchanged expected-negative `OriginalUnsignedCounts` control, the bound `managed-sdk/build-api/results.json` path/hash/Passed verdict and `returnedBindingVerified=true`, plus **14 distinct native translation units x five configurations = 70** real C++17 arm64 syntax-only commands against installed Unity SDK. Record compiler tools, exact source/pins, all warnings and full command results without warning suppression, and preserve original current-frozen byte parity and native V2 tests. The 70-unit syntax matrix is **not** linking or Player execution. Validate all ten outer statuses, source-preservation, SDK-before/after identity and authorized unused root custody. Each child must retain actual raw stdout/stderr, command receipts and nested manifests.

A successful aggregate requires `PassedSourceHostAndSDKOnly`, **ten Passed outer cells**, `officialUnitySdkCompileAttempted=true`, `officialUnitySdkCompilePassed=true`, source preserved, both pinned repository states unchanged, and no real Unity Editor/Player launch. Reconcile independent output/SDK input hashes, including the four intentionally negative symlink fixtures via the nested manifests. Any missing/failed evidence stays Failed/Unavailable/Blocked, not inferred Passed.

**Local modification boundary:** factual `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, additive checkpoint and retained raw evidence ONLY. Do not edit production native/C#, test harness, runner, compiler procedures, V2 transport, historical source-pins.json, performance/safety bounds, source policies, engine adapters or semantic predicates. No nontrivial code fix is delegated. Commit/push factual evidence through canonical repository transport; bind local external binaries by path/hash and do not include vendor SDK bytes.

## Known remaining gates and stopping rule

P1 is still **Incomplete**: admitted class-bearing first-use is an inactive bounded source subset, not complete coherent live general/execution/R02 VM capture or an authenticated pointer-origin proof. Global epoch, type-key lifetime/allocation, real shutdown deadlock freedom, GC/RSS and original getters remain open. P2 native/C# authenticated V2 semantic integration is **NotIntegrated**. E0 Unity2022.3.62f2 StandaloneOSX supported engine safe point remains **Blocked/Unavailable**; E1 real scheduler maintenance, queue-drain and restart is **BlockedByE0**. A passing SDK compile is not runtime acceptance.

Historical `20261016-0620` Local PASS and `20261016-0a0b` Local FAIL remain distinct and consumed. Original SNAP-01/N/M/K/I/E FAIL, strict S custody Blocked, independent R03 review FAIL and rereview NotRun remain untouched. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No full runtime seven-root batch, actual Player, Human Review Gate or H2/X02/M08A.

**Stop after exactly this one new source/SDK-only cycle and return the factual result to Primary Implementation.** No additional Local commands are authorized after its consumption without another separately reviewed, committed, remote-verified handoff.
