# Primary source audit — Git postflight manifest lifetime alignment

## Exact authority

Reviewed at last Local-owned demo `2a280f25d5450ba844fa11783555dac053c0b584`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`, branch `codex/assembly-shadow-r01b-h1`. Read exact published `LOCAL_VALIDATION.md`, then `RETURN_TO_WEB.md`, checkpoint `local-validation-p1-git-postflight-20261021-7c2c/FINDING.json` and `EVIDENCE_AUDIT.json`.

The **`7c2c` Local aggregate is PASS / PassedSourceHostAndSDKOnly**, one source/host/installed SDK syntax batch with **24/24** independently Passed components, **85** original test IDs, **seven** source inventory flags, five actual managed-positive outputs + original expected-negative, 100/100 actual Apple arm64 SDK syntax, **20/20** direct Git postflight commands exit0 and four exact remote heads, independent source/SDK/history preservation audit Passed. No retries, Unity Editor/Player/linked native runtime, real GC/RSS/Shutdown. The **`82dd` prior raw aggregate is separate FAIL / FailedOrIncomplete**, 24 child results Passed but remote `hybridclr ls-remote` timed out; its raw `sourcePreserved=false` and `fourRepositoriesAfter=[]` are immutable. Original R02 fingerprint, S custody, independent R03 full-stage statuses and all acceptance flags remain unchanged.

## Finding / actual change

`IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01`, observed in source only with `SourceConfirmed_NotFaultInjected` disposition by Local, identifies a mismatch between:
- `unknown_lifetime = stopped is not None or git_probe.unknown_lifetime` (top-level `RESULT.json` and root manifest `inventoryScope`), versus
- original `MANIFEST.json.commandLifetimeUnverified = stopped is not None`.

When **only** `git_probe.unknown_lifetime` is true, `stopped` remains null. The original serialized result correctly reported unknown lifetime and unsealed inventory, but the generic manifest field falsely reported false. No actual Git timeout happened in the `7c2c` PASS, so this was NOT a live operational failure.

**Exact production change (one expression only):** `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py` now emits `"commandLifetimeUnverified": unknown_lifetime` in final root `MANIFEST.json`, matching the existing aggregate summary and already correct `inventoryScope` calculation. No change to `GitPostflightProbe`, actual subprocess timeout (120 seconds), original Git remote/branch/origin/HEAD/clean checks, SSH transport/environment, no-retry/fail-stop semantics, repo iteration, child runner/SDK/native/product source, historical source-pins or old evidence.

**Only one existing test file additionally changed:** `Tools/AssemblyShadow/R03IR/test_p1_command_failures.py` adds assertions **inside existing discovery leaves**, no new top-level leaf:
- Completed success ⇒ aggregate lifetime false and manifest lifetime false, CompletedBatchFiles.
- An already stopped component/unknown lifetime ⇒ both lifetime flags true and manifest UnsealedObservedFiles.
- **End-to-end synthetic Git-only timeout**: run actual Python aggregate `main` with all 24 controlled child results Passed, one fully verified first repo, fake `TimeoutExpired` during second repo Git authority, actual separately written/parsed `RESULT.json` and `MANIFEST.json`, aggregate FAIL, fourRepositoriesAfter length1, sourcePreserved false, stoppedAfter null, postflightError TimeoutExpired, aggregate/postflight/manifest lifetime true and unsealed inventory; no second Git retry or descendant quiescence claim. The fixture does **not** launch external Git/SSH, Unity SDK or Player; source-host test does not establish actual remote-outage behavior.

## Independently observed host regression: RED before source fix, GREEN after

- **RED** test-only commit `b29b6385b428e1cb3fbc5684306f6a754d1f7664` (original defective runner unchanged), [integrated CI 39710461380](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461380) **FAIL 2/2** macOS/Linux; Git-only negative `test_postflight_failure_cannot_turn_green` fails exactly `assertTrue(manifest['commandLifetimeUnverified'])` because it was `false`. 85 discovered tests executed. [focused CI 39710461363](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461363) **FAIL 2/2**, preserved, same source-only finding. No product-native or Unity SDK run.
- **GREEN** fixed source/test anchor `789655f19bd54c8abdcda67946a1f8195193176c`, [integrated 85-test CI 39710581913](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581913) **PASS 2/2** macOS/Linux, [focused 44-test CI 39710581915](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581915) **PASS 2/2**, [managed-receipt/source-cli CI 39710581907](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581907) **PASS 2/2**. The original 85=5+14+44+10+12 test inventory, 24 scheduled child identities, seven source case inventories, 5+negative/100 SDK compiler contract remain intact.
- CI runs checked-in real Python orchestration and mocked SDK/Git/VM children; they **do not provide new official installed Unity SDK compilation or actual network SSH timeout evidence**. No original `7c2c` source/SDK raw/checkpoint files were modified by Primary; historical `82dd` FAIL and all older acceptance gates remain immutable.

## Human Review / Local validation boundary

Candidate is ready **only** for one new exact-source 24-component source/host/official Unity SDK syntax-only Local batch under final pushed `WEB_TO_LOCAL.md` with four absent, canonical, disjoint roots, independent source/SDK/evidence admission, all seven case inventories and 20 actual Git postflight receipts. A future *real* Git timeout must still result in FAIL, root manifest `commandLifetimeUnverified=true`, unsealed inventory, partial streams/repo data and nonpositive descendant quiescence. No artificially induced timeout is needed or permitted in Local product batch.

Remaining P1/P2/E0/E1/full P3 acceptance unproved. Original R02 fingerprint FAIL, S custody Blocked and independent R03 full-stage FAIL/re-review NotRun persist. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
