# Primary reconciliation — R03 initializer oneuse-07 focused PASS

Date: 2026-11-07 UTC. Owner: Primary Implementation. This is a source/receipt reconciliation, not new runtime validation, independent full-stage R03 review, or Human Review Gate approval.

## Authority

- Execution demo source: `6e1dc7b4349a386dc35c5ed46fca4225db273b18`.
- Local evidence publication: `66a0218ffb17e363531b7f7bc0f4114787ae0b76`.
- Other exact source pins: hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`; il2cpp_plus `41764ae1eeefb33b05966e7f7676e52aae39c340`.
- Read `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md` and `Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-07/`: `README.md`, `LOCAL_RESULT.json`, `local-evidence/RUNTIME_FINDINGS.json`, `local-evidence/RUNTIME_REVIEW.md`, `local-evidence/FINAL_INDEPENDENT_AUDIT.json`, both original Player raw/recovery/phase journals and requests, commands 0017–0019, and the build receipt. The Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` remains an empty file in the published repository; do not invent its contents. `RETURN_TO_WEB.md` and the committed checkpoint are the factual Local record.

## What the published record supports

- Exactly one executed run: 15/15 distinct cells Passed. One genuine Unity 2022.3.62f2 macOS ARM64 IL2CPP ON/diagnostics2/Release build succeeded, zero errors and one BuildReport warning. BuildReceipt SHA256 `553af2f5cd35a08da543e2b6b2d68ac89a5a7e98d63b7fb840ce2e64dfd60a05`.
- The initializer-only Cdecl int32() `Bi4` managed-to-native source digest matches the after-augmentation and post-BuildPipeline values `c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da`. GameAssembly SHA256 is recorded as `416eedc304a5f0429bcd67710a4ed86203eadf1e2e611e37b6b197758a23dd68`. The original isolated hot-update analyzer list stayed empty.
- Control Player PID 35820 and failure Player PID 35842 both exited 0. Each reported the actual linked `Bi4` phase103 result1 before Commit, exactly one native callback299/300, pinned field3 and pre-positive mask15. Control Commit0/state6 with empty first recovery. Failure Commit19/state9 after native callback with first recovery ending `R03IR.InitializerFailure.AfterPublication.V1`.
- The failure Player attempted a post-terminal AOT method invocation; its success marker remained false and the AOT canary stayed1→1. This does **not** prove which guard denied the invocation or certify all direct AOT business entries.
- Ten native-host components, 56 initializer tests, source/SDK/custody preservation, original-S archival audits, 3198 regular host files, four literal symlinks, independent 456-member product seal and distinct process/source joins passed in their reported scopes.

## Added reproducible source-level check

`Tools/AssemblyShadow/R03IR/initializer07_publication_audit.py` reads the *Git-published* raw records, independently rehashes the actual published BuildReceipt (SHA256 above), V1 raw, native phase journal, native recovery and request bytes, joins the per-Player original PID/nonce and external fixture identity, and requires the exact 15-cell record and false acceptance flags. It returns `PassedPublishedRecordCrossCheck_NotRuntimeOrV2Acceptance`. `initializer07_publication_contracts.py` has 22 real-checkpoint/negative mutations; `.github/workflows/r03-ir-initializer07-publication.yml` runs them on macOS15 and Ubuntu24.04. Prior failed test runs are not relabeled; they exposed a manually transcribed wrong SHA and a test schema assumption, repaired without altering original evidence.

This cross-check does **not** independently rehash the original physical macOS executable/GameAssembly or the complete 41-part product archive. It does not independently re-run Unity, inspect lost retired data or prove native V2 first failure or full R03 source-to-object/link/Player authority.

## Historical and independent review boundaries

The oneuse-07 bridge issue is resolved **for the initializer-only V2-target fixture path validated by the two Players**, not the entire HybridCLR runtime. All oneuse01–06 verdicts remain historical. The 17 explicitly owner-retired roots and 40 duplicate paths remain `Unavailable/PermanentlyDeleted`; historical strict custody is `Blocked`.

The October 8 independent R03 overall verdict remains `FAIL`; High `IR-R03-01` (original S authoritative provenance, complete compiler/link/Player and capture omissions) and High `IR-R03-02` (broader terminal-entry coverage, captured-generic error15, native V2 and whole-VM diagnostic consequences) remain unclosed. No independent R03 re-review has declared PASS.

`R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`; `qualificationApproved=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

The single-use oneuse-07 WEB_TO_LOCAL authorization is **consumed**. Do not rerun its executable, reuse its output roots, or continue into H2/M08A/X02/SNAP-01.