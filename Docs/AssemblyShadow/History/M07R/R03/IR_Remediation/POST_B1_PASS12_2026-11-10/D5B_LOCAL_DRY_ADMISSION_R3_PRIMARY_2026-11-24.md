# D5-B dry-admission — Primary R3 final-receipt and cleanup remediation

**Date:** 2026-11-24 UTC. **Primary state:** `D5BDryAdmissionR3Primary=SourceOnlyCIComplete_PendingIndependentR3Review`. This is a factual Primary implementation record, **not an independent pass, approved envelope, or executable Local handoff**. Responds to [independent D5-B R2 ReturnRequired findings R2-IR-01/02](D5B_LOCAL_DRY_ADMISSION_R2_INDEPENDENT_REREVIEW_2026-11-24.md) with the [R3 protocol design](D5B_LOCAL_DRY_ADMISSION_R3_DESIGN_2026-11-24.md).

## 1. Source/branch provenance and review scope

All repositories: branch `codex/assembly-shadow-r01b-h1`. Exact CI-tested source: **`night-outlook/hybridclr_demo@eeba27a51e46dd5304da108e14285a1ad5ccd10d`**, other repos unchanged `night-outlook/hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`, `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `night-outlook/il2cpp_plus@1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`.

GitHub compare prior independent R2 review HEAD `hybridclr_demo@a909909d724c33515eee41458311f122fc745ce4` → new R3 **code** `eeba27a51e46dd5304da108e14285a1ad5ccd10d`: six commits, **exactly three modified files**, no native/old-admission/plan/wrapper edits:

| File | Git blob at exact R3 code |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `3cf4e746bc1cd361d162ab4681af3d6d0281ae37` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `0698cff62f1e8a0437c8f2e808dfa504b36106da` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `ee768deafb7b229d7e0b9b0ef74cf9d04d710095` |

Unchanged and separately verified: `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` Git blob `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9`, `run_d5_local.py` `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39`. All 16 prior C10 link-source + 14 receipt-producer + five historical comparator Git checks remain those of the independently passed source-only RR5 R2 gate; no new actual native link is asserted.

## 2. R2-IR-01 — final receipt after-flush/`fsync` error

**Old behavior:** writing/fsyncing directly to the public `LOCAL_BATCH_RESULT.json` filename could leave a complete, matching positive file if its final `fsync` failed. **R3 correction:** a durable `INCOMPLETE.json` veto is created and directory-fsynced before any positive receipt. Preliminary receipts and manifest are fsynced, then positive bytes are written/fsynced under `LOCAL_BATCH_STAGING.json`, read back through the bound root directory descriptor and verified against expected byte content and SHA-256. After full source/remote/history/host rechecks and preclosing the parent descriptor, the writer calls same-directory `os.rename(...,src_dir_fd=root_fd,dst_dir_fd=root_fd)` to publish the final name atomically, then fsyncs the directory with the incomplete marker still present. **Only after that succeeds** is `INCOMPLETE.json` removed as the final commit step.

Unfinished/failed roots remain consumed, with the `INCOMPLETE` veto and optional `FAILURE.json`; even if the *final positive bytes* exist following a failed post-rename directory sync, structural validation rejects them. On power failure, a lost commit-unlink may restore the veto and force a false-negative reinspection rather than a false-positive acceptance. No further fallible disk write is performed after commit-unlink. An independent verifier `inspect_dry_receipt_structure()` requires exactly five sealed receipt files, checks v3 manifest's SHA-256+sizes and final NoUnity/NoPlayer fields, and rejects any veto, staging, failure or unexpected file. It does **not** establish actual source/Player/canonical Local execution authority.

## 3. R2-IR-02 — errors while closing descriptors

Removed the R2 `finally: os.close(root_fd); os.close(parent_fd)` that could override a prior outcome. The parent fd closes **before** atomic final commit; any error leaves the durable incomplete marker. Root fd cleanup after commit runs in the same root-created-aware error accounting. Post-creation errors always raise `PartialOutput` with `outputCreated=true`, never fall through to generic `outputCreated=false` handling. When the commit-unlink already occurred but a subsequent root-descriptor close fails, the result is **`IndeterminateAfterCommit`**, `commitVisible=true`, `requiresPhysicalReconciliation=true`, `retryAllowed=false`, `R03Accepted=false` with cleanup diagnostics. There is no silent green success from failed descriptor cleanup. This is deliberately a separate state from a precommit `FailedAfterPartialOutput` and is **not** accepted as Local Validation without an independent physical/command outcome review.

## 4. Exact source-host tests and CI evidence

11 new synthetic, isolated tests 66–76, 76 total. Test 66 validates positive sealed structure; 67 injects after-write/flush staging `fsync` failure; 68 fails the **post-rename** directory `fsync` while also failing `FAILURE.json` creation, proving the veto remains despite a complete-looking final file; 69 fails final atomic rename; 70 fails commit-veto unlink; 71 fails parent close before commit; 72 fails root close after commit; 73 checks truthful CLI indeterminate output; 74/75/76 reject veto-present, missing final and failure-marker-tainted physical evidence. Earlier tests 1–65 remain present, with test 35 tightened to check physical seal and test 60 changed to target staging-file writes.

**Final [GitHub Actions run 45375970635](https://github.com/night-outlook/hybridclr_demo/actions/runs/45375970635)**, push, attempt 1, **`completed/success` 1/1**, exact demo code `eeba27a51e46dd5304da108e14285a1ad5ccd10d`, job `138382258238` (Ubuntu/Python). Raw GitHub job log read back: **276 lines / 29,088 characters**, `Ran 76 tests in 0.118s`, `OK`, individual test_66…test_76 `ok`, and source-only public CLI `--mode execute` refused `NotAuthorized`, `outputCreated=false`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. No real Local executable existed, no Unity/IL2CPP/Player run was attempted. Exact tested workflow asserts 76 tests and the current null approval hard stop.

**Intermediate outcomes remain historical**, not promoted to this final source PASS: earlier `45375634381` and `45375689831` failed while the new sealer/test expectations were mid-update; `45375806304` passed the previous 65-test contract; `45375922233` and `45375960396` failed on the intermediate 76-test cardinality/import integration; only `45375970635` is the exact committed R3 implementation source CI PASS.

## 5. Mandatory Connector write smoke test

At this cycle's bootstrap, the GitHub connector read/write-smoke-tested only the participating `night-outlook/hybridclr_demo` repository on an **isolated disposable branch** `codex/smoke-d5b-r3-20261124-a909909d`, based on feature HEAD `a909909d724c33515eee41458311f122fc745ce4`. One harmless file `.connector-smoke-r3-20261124.txt` was created there and the exact remote smoke HEAD read back as `86a51ae3c95999a9afedde37d7db95fc972639d0`, matching the write commit. The connector exposed no remote branch-delete action, so the isolated smoke branch remains; it is **not** part of the feature branch or Local handoff. No other repository required an independent connector write smoke because it was read-only in this cycle.

## 6. Stop condition

**Primary assessment:** focused R2-IR-01 and R2-IR-02 now have source implementations and negative source-host test evidence. They are **not self-approved**. Publish an independent **R3** design → source → raw-CI rereview at the exact code SHA; verdict may be `PassDryAdmissionSourceOnly` or `ReturnRequired` and must not grant Local permission. No actual macOS `mkdirat`, Unity 2022.3.62f2, IL2CPP compilation, full native VM, Bee/Mach-O link, GC, PID, Player/first-error evidence or 18 D5 real Player cells were executed.

**Binding authority:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All 18 real Player cells remain `NoCoverage`. No Local preview/dry admission, D5-C/D, D6/H2/M08A/X02/SNAP-01, Human Review Gate or R03 acceptance.