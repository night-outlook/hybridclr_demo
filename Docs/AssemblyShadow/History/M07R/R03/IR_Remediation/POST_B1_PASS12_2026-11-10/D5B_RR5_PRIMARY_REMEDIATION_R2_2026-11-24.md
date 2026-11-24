# R03 D5-B RR5 — Primary source-preflight remediation R2

**Date:** 2026-11-24 UTC. **Status:** `PrimaryRemediationExactSourceCIComplete_PendingIndependentRereview`. This document responds solely to the two findings in the [independent RR5 source-preflight ReturnRequired](D5B_RR5_SOURCE_PREFLIGHT_INDEPENDENT_REVIEW_2026-11-24.md). No authority is inferred from this Primary self-check; Local Validation is closed.

## 1. Exact immutable source scope

All four repositories use `codex/assembly-shadow-r01b-h1`. Exact CI-tested source tuple:

| Role | Commit |
|---|---|
| `night-outlook/hybridclr_demo` **remediation source commit** | `54780df40bddfc9d050b87f64fcd259475d99ba4` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

GitHub compare `hybridclr_demo@fd74c739151d77c94a4f53ddcacd5f01710380eb...54780df40bddfc9d050b87f64fcd259475d99ba4` = four successive source commits, **exactly four changed files**: `d5b_rr5_source_preflight_v1.json` (manifest), `d5b_rr5_source_preflight.py` (verifier), `test_d5b_rr5_source_preflight.py` (regressions), and `.github/workflows/r03-b2-d5b-rr5-source-preflight.yml` (CI trigger/checkout). No C10 producer, native production, old D5-A/D5-B/B1 gate, or Local-owned source altered.

New exact Git blob identities read back through the GitHub Connector: proposal `9956ea49656dc8337f9ab177c40faf29ea20c397`, Python verifier `81e7c3a2eaccb77bff2515c91b173558e4eeba2f`, test suite `d5e8ca47861470db84d7a46221b2d340bfc602aa`, workflow `c70125684856806e329fd92e633eb9a8d0f8d921`. Reviewed C10 v3 link pinset Git blob `66b2e83f8cab4debb71af36d4bcd5eecd80b5629` remains unchanged, with its 13 native+three isolated demo link-source entries, five intended native TUs, nine C exports and excluded allocator host.

## 2. F1 — Evidence producer source not authenticated (High): correction

The preflight still verifies the original immutable C10 link pinset as **16 link-source blob matches**; **separately** the RR5 proposal now pins **14 additional C10 evidence-producer Git blobs**: the v3 native receipt parser and tests, C10 link-material and source-contract analyzers/tests, native autonomous/manual/window host tests and test-only C++ stubs, the C10 pinset file itself, and the full C10 source-host workflow. This 14-file map is anchored in the new proposal Git blob and independently compared against the verifier's source constant.

Every producer file is checked through `verified_source_blob()`, which requires both checked working-tree Git blob and `HEAD:<path>` blob identity. A skipped/no-op low-level verifier returns no authenticated digest and is rejected before any success count is emitted. Distinct receipt fields `checkedNativeAndOverlayFiles=16`, `linkSourceBlobsMatched=true`, `checkedEvidenceProducerFiles=14`, `receiptProducerBlobsMatched=true` are only returned after all comparisons. This prevents a clean descendant Git commit with a modified parser/test/C10 host workflow from receiving the reviewed source-preflight classification.

The preflight GitHub Actions push trigger now includes `Tools/AssemblyShadow/R03IR/D5Probe/**`, the C10 source-host workflow and historical pinned admission/B1 files, in addition to the RR5 preflight itself; the demo sparse checkout explicitly includes the C10 workflow. No historical C10 pinset or C10 source code is rewritten. This remains a **Git-source** check, not evidence that the script/parser was installed into or run in a Unity Player.

## 3. F2 — No negative test of source-blob authentication (Medium): correction

Nine new tests bring the RR5 preflight suite from 27 to **36**. The added cases use isolated, temporary **real Git repositories** with actual `git add`, `git commit` and `rev-parse HEAD:<path>` for precise byte-vs-commit checks. They verify successful matching, dirty worktree, an updated worktree matching a caller's false blob but not the committed blob, symlink and path escapes. Full `inspect()` positive fixtures copy all reviewed CI-checked native/demo/historical materials into temporary Git repos; **only four-role checkout identity checks are mocked** because synthetic fixture SHAs are not the production remotes. They then mutate (a) native `AssemblyShadow.cpp`, (b) v3 receipt parser and (c) C10 workflow, and require rejection.

The modified verifier now returns a verified blob SHA, and the higher-level preflight requires that SHA to match the expected pin. A no-op `checked_source_blob` can no longer produce a false 16/14 positive counter. Two additional regression cases ensure the full preflight rejects a patched no-op verifier and that a direct negative blob test is **killed** when that verifier is disabled (the deliberately mutated nested unittest reports an expected failure; the enclosing mutation-validation test passes). Temporary Git fixtures and mocks **never** constitute authentication of live remote branch state.

## 4. Exact-source CI and raw log proof

**Final [run 45347447165](https://github.com/night-outlook/hybridclr_demo/actions/runs/45347447165)**, attempt 1, at exact demo implementation commit `54780df40bddfc9d050b87f64fcd259475d99ba4`, `completed/success` **1/1** Ubuntu 24.04 Python 3.11 job `138285343137`. Full raw log independently retrieved via GitHub Connector (586 lines, 50,070 characters), containing:

- Four exact checkout SHA records matching the four-source tuple;
- `Ran 36 tests in 0.544s` and `OK`, including `test_32...test_36` source/protocol mutation regressions;
- `RR5PinnedGitSourceVerified_NoLocalExecution`, `checkedNativeAndOverlayFiles=16`, `checkedEvidenceProducerFiles=14`, `checkedHistoricalComparators=5`, and both explicit `linkSourceBlobsMatched=true` / `receiptProducerBlobsMatched=true`;
- `actualUnityBuild=NotRun`, `actualIl2CppNativeLink=NotRun`, `compiledTranslationUnits=0`, `realPlayerCellsPassed=0`, `realPlayerCellsNoCoverage=18`, `APPROVED_LOCAL_HANDOFF_BLOB=null`, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, and `remoteBranchAtReview=NotAuthenticatedBySourceOnlyCLI`.

**Prior intermediate failures are retained as failures:** [run 45347228693](https://github.com/night-outlook/hybridclr_demo/actions/runs/45347228693) at proposal-only `506dc372...` failed during `setUpClass` because the verifier still carried its old proposal blob; [run 45347326839](https://github.com/night-outlook/hybridclr_demo/actions/runs/45347326839) at verifier-only `d1f98cea...` executed 27 Python tests successfully but failed the positive preflight because the earlier sparse checkout omitted `.github/workflows/r03-b2-d5-c10-window-source-host.yml` (receipt `BlockedBeforeUnity`). The final workflow/code commit corrected both integration issues. Neither failed run is promoted to PASS or hidden.

## 5. Scope limits, review gate and stop

**Primary assessment:** F1 and F2 are remedied **at source/preflight level** and have a fresh exactly pinned CI result. This is **not an independent acceptance decision**. The next permitted activity is a **separate independent R2 review of actual new source and run 45347447165 raw log**, including independent mutation/readback checks. The earlier independent `D5BRR5IndependentReview=ReturnRequired` remains in force until a separate review verdict is published.

The existing C10 RR5 independent verdict `D5BC10IndependentReview=PassSourceProducerOnly` remains limited to source/test-producer scope, not real Unity. All four repositories and the latest demo documentation HEAD must be reverified for any future handoff. A current source-only CLI that sees a caller-supplied demo SHA is still not a live GitHub remote-ref authentication and does not license Local execution.

**Unchanged hard stop:** `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. Actual Unity/IL2CPP/native full VM/GC/Bee/Mach-O/PID/Player all `NotRun`; all 18 D5 real Player cases `NoCoverage`. Do not begin Local, D6/H2/M08A/X02/SNAP-01 or Human Review Gate.