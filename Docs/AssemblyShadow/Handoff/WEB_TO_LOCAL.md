# Primary Implementation -> Local Validation — receipt-corrected successor

**ONE NEW SOURCE/SDK-ONLY CYCLE IS AUTHORIZED.** This supersedes the consumed `20261016-0a0b` instruction, not its result. That original aggregate remains **FAIL / FailedOrIncomplete, 9 Passed / 1 Failed**, despite actual five-product managed compilation/negative control and 70 native syntax configurations Passed. Do not retry, resume, rename, modify or reinterpret its roots or receipts.

Objective: validate the corrected managed receipt consumer through the unchanged ten-component source/SDK preflight. No Unity Editor, Test Runner, Player, runtime batch, engine-lifecycle experiment, Human Review Gate or next milestone is authorized. All nontrivial changes remain Primary-owned.

## Read first

1. `Docs/AssemblyShadow/README.md` and `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, including `IR-LOCAL-P1-MANAGED-RECEIPT-01`.
3. [Primary correction/review](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/PRIMARY_RECONCILIATION.md), [evidence](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/EVIDENCE.json) and [raw regression logs](../History/M07R/R03/IR_Remediation/P1_MANAGED_RECEIPT_2026-10-16/HOST_TEST_LOGS.txt).
4. This entire current handoff before any execution.

## Exact repositories and source authority

All branches are `codex/assembly-shadow-r01b-h1`; all remotes must resolve to the listed canonical GitHub repository. The paths are existing Local-owned checkouts, not Primary's container workspace.

| Canonical repository | Exact Local path | Exact tested source commit |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | 06209426b765a805da2cc2f810ba5da390787099 |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | 0a0b70156e75d450d75d0bcfd9132843b8abbbb0 |

**Demo source versus final transport:** the final handoff commit adds Docs only after the tested demo source above. Use the latest pushed demo HEAD stated in the final Primary prompt, not the older source anchor as `--expected-demo`. The command below independently resolves the commit that contains this handoff, requires it to equal checkout HEAD, rejects any non-Docs difference from the tested source, and passes that exact 40-character value to the wrapper. The wrapper also verifies the remote HEAD of all four checkouts. There is no unknown SHA placeholder and no dependence on an uncommitted document.

Safely fetch and fast-forward only clean ancestor histories to the final listed commits. If dirty, divergent, mismatched, unavailable or already consumed, record Blocked and stop; do not reset, clean, force-push, switch unrelated worktrees or infer other paths. Source-pins.json remains historical and must not be changed: native candidate SDK validation already receives the explicit current native SHA.

## Implemented and tested in Primary

The consumer reads only `managed-sdk/build-api/results.json` and verifies the producer's returned path/SHA-256, actual receipt kind/schema/Unity version/non-runtime scope and inner verdict. Outer success still requires child exit 0. It records `innerResultPath`, `innerResultSha256`, and `returnedBindingVerified`; missing/changed/malformed data, symlinks, wrong paths, Failed inner results or nonzero exits cannot be promoted. No root-level fallback or synthetic success file is created.

The new aggregate regression reproduces the original defect against the old source. Thirteen new tests Passed in Primary; macOS/Linux CI **38859685370 passed 18 tests each** (five original plus thirteen new), with both ZIP hashes and ten declared files verified. Git/SDK/child processes in those tests are mocks, not new installed-SDK evidence. Native code, `build_api.py`, `native_validation.py`, legacy suites, the 70-unit matrix and all runtime semantic predicates are unchanged.

## Fresh roots and environment

Require all following output/checkpoint paths to be absent and canonical before creation. Do not rename them to evade an existing consumed root. Parent directories must exist and be suitable for the previously established external SDK-copy/evidence storage policy.

- Evidence: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-MANAGED-RECEIPT-20261016-0620`
- SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-MANAGED-RECEIPT-20261016-0620`
- Local authority/audit receipts: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-MANAGED-RECEIPT-20261016-0620`
- Additive Git checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-managed-receipt-20261016-0620/`

SDK anchor, read-only: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, official macOS arm64 installation. Do not launch it. The SDK is copied only to the separate new scratch root; vendor binaries must not be committed. Preserve installed SDK/source/previous evidence before and after as in the prior Local audit. The original full C/S custody/runtime campaign is not reauthorized here.

## Single successor command

Run once, after verifying clean checkouts, exact final transport commits, source identities, environment, storage and the unused roots above. A failure consumes this attempt; no automatic retry or resume is permitted.

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=06209426b765a805da2cc2f810ba5da390787099
NATIVE=0a0b70156e75d450d75d0bcfd9132843b8abbbb0
DEMO_SHA="$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-MANAGED-RECEIPT-20261016-0620" \
  --sdk-scratch "$B/Scratch-R03-P1-MANAGED-RECEIPT-20261016-0620"
```

## Required results and independent evidence checks

All ten components remain: retained legacy host/general/current-frozen/V2 codec/file/sink/formatter tests; metadata gate; bounded ordinary class; bounded physical assembly; bounded first-use; bounded transaction status; bounded transaction inventory; frozen execution/V2; managed SDK; native SDK. The wrapper records independent failures and completes the authorized independent components within the one invocation. Do not manually rerun a failing component.

Require ten Passed outer cells, aggregate `PassedSourceHostAndSDKOnly`, source preservation and both SDK attempted/passed flags true for a successful new batch. For `managed-sdk`, independently join the exact returned stdout path/hash, `build-api/results.json`, its five product outputs and expected-negative compiler receipts, outer `innerResultPath`, `innerResultSha256`, `returnedBindingVerified=true`, `innerResult=Passed`, exit0 and status Passed. Never create `managed-sdk/results.json`. Verify all **70** native syntax configurations (14 distinct units x 5 profiles), not just the outer exit code.

Preserve every compiler warning and error, expected negative exit1/two CS0266/no DLL, exact commands/exit codes, returned stdout/stderr, source/SDK joins and per-component manifests. Do not assume warning counts will be identical to history or suppress warnings to force agreement. Verify aggregate RESULT/MANIFEST, nested results, original command stream hashes and source/SDK preservation. Retain and authenticate the four intentional host negative-control symlinks through the nested legacy manifests; do not interpret their omission from the outer regular-file list as deletion or success.

The old `R03-P1-METADATA-SOURCE-20261016-0a0b` RESULT (`13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565`), MANIFEST (`b0f6c0597a7311ce2ec8647d807da8dcfbef34ee41140a104ef79dc84a10a13f`) and actual managed receipt (`43f38be35063559bcb156c31968f6b80d8707982692aef55fd6ab05285ea916e`) must remain unchanged. Do not run the corrected consumer over old evidence and replace its historical verdict.

Publish factual results, raw compiler/command streams, source/SDK/preservation audits and an additive checkpoint. Record external binaries and their hashes instead of uploading SDK binaries. Update Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` as needed; preserve the entire previous outcome. Commit/push factual evidence and report all four final repository tuples.

## Ownership, limitations and stop

Local may diagnose environmental prerequisites and collect evidence, but must not edit production, compiler procedures, the receipt consumer/tests, source-pins.json, V2 transport, guards, limits or acceptance predicates. No nontrivial fix belongs to Local. On unavailable input record Blocked; on test failure record Failed; preserve NotRun/Unavailable distinctly. Return exact file/line/log findings to Primary after this one cycle.

P1 full coherent bounded live VM capture, original getter integration, shutdown/lock safety and GC/RSS remain incomplete. P2 V2 semantic integration and E0/E1 engine-owner lifecycle are unresolved. Neither the prior 70-unit Pass nor a successor Pass proves linking, Player behavior, metadata lifetime safety or engine quiescence.

All historical SNAP-01/N/M/K/I/E failures, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. **Stop and return to Primary after this cycle. No Unity/Player runtime, seven-root batch, H2/X02/M08A or Human Review Gate.**
