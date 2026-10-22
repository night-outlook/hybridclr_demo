# Primary reconciliation — completed Local 20261021-7896

**Role:** Primary Implementation. **Disposition:** local finding IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01 correction is **verified within source/host/official Unity SDK syntax scope**, not execution/Player acceptance. **No new Local execution is authorized by this reconciliation.**

## 1. Exact source authority and Local results

Read [Local-owned report](../../../../../Handoff/LOCAL_VALIDATION.md) before [Local-owned return](../../../../../Handoff/RETURN_TO_WEB.md), then [7896 checkpoint](../../local-validation-p1-git-lifetime-20261021-7896/README.md), [independent audit](../../local-validation-p1-git-lifetime-20261021-7896/preflight/EVIDENCE_AUDIT.json), [real aggregate](../../local-validation-p1-git-lifetime-20261021-7896/batch/RESULT.json), [real root manifest](../../local-validation-p1-git-lifetime-20261021-7896/batch/MANIFEST.json), and [lifetime correction verification](../../local-validation-p1-git-lifetime-20261021-7896/preflight/GIT_MANIFEST_LIFETIME_VERIFICATION.json).

The **one** Local batch `20261021-7896` executed these exact SHAs on `codex/assembly-shadow-r01b-h1`:

| Repo | Actual executed commit |
| --- | --- |
| `night-outlook/hybridclr_demo` | `a5c0a4272efc4eee000220f40b7ca769be277917` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `82ddcef9417e3d662fdd39916a92124b5c835094` |

**Actual result:** `PASS / PassedSourceHostAndSDKOnly`, exit 0, 24/24 independently Passed components, 85 original controlled failure tests, seven source case inventories, five real managed positive compiler outputs plus the original distinct `OriginalUnsignedCounts` expected-negative (exit1, exactly two CS0266, no DLL), **100/100** native Apple arm64 C++17 `-fsyntax-only` configurations, and **20/20** actual final Git source-authority direct commands (five×four repos) with exit0 and full exact source-head equality. All Git commands used the original 120-second timeout and no retries. The independently authenticated source/SDK/history preservation audit `PassedFactualEvidenceAudit`; no Unity Editor, Test Runner, Player, product native link, process GC/RSS, or real metadata Shutdown.

**Raw evidence hashes:** `batch/RESULT.json` SHA256 `590a4ff5742ee7837e09d8856a29d5de3d3f5f2105989f806d6fc2e266e1b0a3`; `batch/MANIFEST.json` SHA256 `4af3b865dc9e02bff10d6799c3709cb049c6264c272cf9691d7fd4a7b03467ca`. `regularInventoryEntries=4244` and four intentional negative-test symlinks were separately authenticated.

## 2. Finding correction — accepted only within observed scope

Local finding `IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01` in [original 7c2c FINDING](../../local-validation-p1-git-postflight-20261021-7c2c/FINDING.json) retains its original disposition `SourceConfirmed_NotFaultInjected`. The **new** Local successor disposition in `GIT_MANIFEST_LIFETIME_VERIFICATION.json` is `CorrectedAndRegressionValidatedWithinHostScope_NoRealTimeoutInjected`. Neither original record was rewritten.

Only two Primary-owned demo files changed relative to Local `2a280f25d5450ba844fa11783555dac053c0b584`: `run_p1_metadata_local_preflight.py` and `test_p1_command_failures.py`. Code anchor `789655f19bd54c8abdcda67946a1f8195193176c` changes root `MANIFEST.json.commandLifetimeUnverified` from `stopped is not None` to **`unknown_lifetime`**, the value already used by aggregate `RESULT.json` and unsealed `inventoryScope`. All old 24 child results, 85 original discovered IDs, seven inventory flags, five managed actual positives/one expected-negative, 100 native SDK commands and source/head/timeout guards remain intact.

Actual `7896` **successful Git run** yielded:
- `RESULT.json.commandLifetimeUnverified=false`;
- `MANIFEST.json.commandLifetimeUnverified=false`, `inventoryScope=CompletedBatchFiles`;
- `postflightError=null`, `sourcePreserved=true` and four complete verified final repository results;
- `postflightGitDiagnostics.actualDirectCommandCount=20`, `timedOutCommands=0`, `commandLifetimeUnverified=false`, `noRetry=true`.

The **Git-only timeout branch was NOT fault-injected against a live Git/SSH process**. Within the original 85 controlled Python tests, however, the actual Python batch orchestrator emitted both files after a **synthetic second-repository Git-only timeout** with 24 mocked Passed children, and independently asserted aggregate `FailedOrIncomplete`, only one verified final repo, both lifetime flags **true**, and `UnsealedObservedFiles`. The red-before-source-fix [CI 39710461380](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461380) failed as expected; corrected [CI 39710581913](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581913), [focused 39710581915](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581915) and [managed-source contract 39710581907](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581907) passed 2/2 each on macOS/Linux. None are a substitute for actual Player execution.

## 3. Immutable historical outcomes and limitations

- `20261021-7c2c` — **PASS / PassedSourceHostAndSDKOnly** for its separate source tuple; the original source-only finding disposition remains `SourceConfirmed_NotFaultInjected`.
- `20261021-82dd` — **FAIL / FailedOrIncomplete** for its separate original source tuple; 24 child checks Passed but real final `hybridclr ls-remote` exceeded 120 seconds and aggregate `sourcePreserved=false`/`fourRepositoriesAfter=[]`; subsequent independent auditing did **not** upgrade the raw result.
- Historical SNAP-01/N/M/K/I/E/R02 fingerprint **FAIL**, strict S custody **Blocked**, independent R03 full-stage **FAIL/re-review NotRun** remain factual.

**P1 Incomplete:** canonical generic-aware execution `TypeKey` identity, physical Il2CppClass allocator provenance and lifetime, coherent VM epoch/ABA, complete nonempty execution V1 rows/JSON, original getter integration, real process GC/RSS/latency and MetadataLock/Shutdown. P2 `NotIntegrated`, E0 `Blocked/Unavailable`, E1 `BlockedByE0`, full P3 `Incomplete`. Original 1..64/500ms/logger/recovery/canary and resource/performance requirements still have no new Player acceptance evidence. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

## 4. Stop/next state

This **narrow manifest-lifetime correction is closed within source/host/official SDK syntax**. The existing `WEB_TO_LOCAL.md` one-shot `7896` authorization has been **consumed** and is now archival. Do **not** run `7896` again or repurpose its roots. A later Primary implementation directed at a specified remaining P1 requirement must first produce its own design, code, source-host tests, exact source pins, reviewed acceptance scope and **new one-shot Local handoff**; no later milestone or Human Review Gate is authorized here.
