# R03 independent review — evidence citation erratum and readback verification

Date: 2026-10-08  
Status: **Supplement to the existing independent FAIL review; not a replacement or a new stage approval.**

## Scope and immutable authority

This record supplements [INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md](INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md), published in demo commit `0320495a6262f634fe0f69b628b143d5d1c1581b`. The original review baseline is unchanged:

- `hybridclr_demo@aee7975874a5ddf236ab9d00d5d682b470010f8f`
- `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`
- `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`
- `il2cpp_plus@1cf87f8209790f9fb2ebec97487dc1990ccd56c5`

The feature branch advanced from the fixed demo baseline by one documentation-only commit adding the original review. The existing disposable smoke branch `codex/review-smoke-r03-20261008-8ac7d921` was independently read back at `191b2a5d3a97cb4ddff093775069e18cbfd27b2e`. Its branch remains; no new smoke branch or product modification is necessary for this documentation-only supplement.

## ERR-R03-01 — Correct C04 verification-file assertion in the original report

The original review, Section 7 IR-R03-02, states that the C04 old-AOT guard `verification.json` **explicitly records** `newMethodInvocationAttempted=false` and `newMethodInvocationSucceeded=false`. This is **not accurate for the cited file**.

A fresh GitHub Connector retrieval at the fixed demo SHA found that:

- [C04 verification.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/players/C04-old-AOT-guard/verification.json) (blob `6185b3a2f573e74560a7ac7759f02dec4f4898db`) records `result=Passed`, `state=9`, `value=42`, receipt binding and `warmWindow`. **Neither claimed `newMethodInvocation*` field is present**.
- [C04 raw.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/players/C04-old-AOT-guard/raw.json) (blob `acbefc151c46dde4e2c92e5dc4e10d546f56e019`) likewise does not contain those field names. Its top-level record does include `finalState=9`, `invocationResult=42` and `delegateResult=42`; these values alone do not establish an attempted **post-poison** valid active-method call.

**Corrected interpretation:** C04 documents a terminal guard outcome within its recorded test semantics. Neither cited JSON file explicitly records the asserted attempt/success flags. The absence of fields **must not be described as observed `false` values**. There remains no affirmative evidence in these two files for the precise post-poison execution counterexample. This is a citation/evidence-precision correction, not a declaration that such a test failed.

## Blocking findings rechecked against source and committed records

**IR-R03-02 remains a source-derived, not Player-reproduced, concern.** Directly reading [native `AssemblyShadow.cpp` lines 1572–1746](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/AssemblyShadow.cpp#L1572-L1746) shows `AssertMethodIsActive` returns true for current-method identity success without consulting already-stored `Failed`/`FailedAfterCommit` state; `RequireActiveMethod` consults `s_typeFailure` only when that assertion returns false; `RequireUserCodeAllowed` enforces private/staging execution restrictions but does not test terminal state. The inspected [`Runtime::Invoke` / `InvokeWithThrow`](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/Runtime.cpp#L580-L655) and [HybridCLR `Interpreter::Execute`](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/Interpreter_Execute.cpp#L1650-L1715) use those guards. A fresh, specific post-poison regression remains required before claiming the business-entry property proven.

**IR-R03-01 remains a directly observed evidence-identity contradiction.** [Primary EVIDENCE.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/EVIDENCE.json) names `evidence.tar.gz=f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7`, 283,728,477 bytes, five parts and 18,160 members. Directly fetched [committed S FILE_TRANSPORT.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/FILE_TRANSPORT.json) instead records `evidence.tar.gz=23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, 587,907,380 bytes and nine parts; its [seal-receipt.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/seal-receipt.json) agrees with the latter hash and records 15,713 members. No authenticated transformation/join was established in this supplemental read.

This supplement does not assert the historical S runtime failed, does not replace Local's 90/90 outcome, does not perform new Unity/Player validation, and does not claim exhaustive S archive reauthentication. **Existing independent verdict remains FAIL** pending Primary-owned remediation and separately triggered independent re-review. D1=A/D2=A, all stage/qualification/H2 readiness flags and historical Failed certificates are unchanged. No H2, X02, M08A or product action is authorized.
