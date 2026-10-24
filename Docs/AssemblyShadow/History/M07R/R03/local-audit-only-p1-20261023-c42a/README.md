# c42a historical b7e3 audit-only — FAIL, originals preserved

## Current run — c42a isolated b7e3 historical audit-only — FAIL

[Checkpoint](README.md), [new Local outcome](LOCAL_RESULT.json), [Primary finding](FINDING.json), [one-shot run receipt](stage/AUDIT_ONLY_RUN_RECEIPT.json), [original preservation](stage/AUDIT_ONLY_AFTER.json).

| Actual current audit-source repository | Branch | Exact source HEAD |
| --- | --- | --- |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | codex/assembly-shadow-r01b-h1 | 26a4ea22aa0a11f1e86c8d2ac2aa4bd55a308a05 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | codex/assembly-shadow-r01b-h1 | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

**FAIL / FailedOrIncomplete for the ONE new isolated historical audit-only invocation.** Source-only prerequisite **23/23 Passed**, isolated staging Passed, historical auditor exited1 with StopIteration at line1031; both the supplied and separate independent after-preservation Passed. No audit retry, original core25/original85/SDK100/compiler/Unity/Player/product-link execution or source modification. EVIDENCE_AUDIT.json is **Unavailable_NotProduced**; complete historical audit-only acceptance is not established.

**Source and CI gate:** independently queried GitHub run40072179278 jobs and full Mac/Linux logs. Both completed success at source63943cc914c19917ff356bab7303495ff09c8331, 23 source-only tests/host and limited published snapshot. All five published audit/stage/test/runner/verification source Git blobs and workflow bytes match the successful CI source at current checkout26a4ea22aa0a11f1e86c8d2ac2aa4bd55a308a05. CI remains PassedPublishedSnapshotScope_ExternalInputsUnavailable; its2396/4269 published raw files and1873 unavailable external records are not mistaken for a full Local check. This Local admission/stage actually verified **all4269** original raw files, including those1873, all2405 installed SDK inputs (316062203 bytes), all1925 original SDK scratch inputs and historical source bindings. Nothing was rebuilt.

**Historical executed tuple (not current live authority):**

| Repository | Original b7e3 execution SHA |
| --- | --- |
| hybridclr_demo | 49c6b62d38d7668be10004ac1e5a030d74894f09 |
| hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| il2cpp_plus | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

Original b7e3 remains overall Local **FAIL**, raw PassedSourceHostAndSDKOnly25/25, original required auditor exit1/line190. Current demo26a4ea22 is a distinct Docs/CI descendant of the executed source; it was verified as current clean/live authority before this new audit-only run. No original historical SHA was changed to match today's branch. Old 20 event-time Git receipts were re-read; no original Git20, SDK or test batch was executed again. Final historical GIT_BEFORE authority join after the failed lookup is **NotRun**, and no live-remote-equivalence-to-old49c6 claim is made.

**Actual source-only prerequisite:** one python3 -B invocation of test_audit_only_source.py ran all23 leaves, exit0 and no skips/errors/failures. Two tiny test-owned Python auditor stubs exercised the tool's pass/fail/no-retry paths; these are synthetic tool tests, not the real historical auditor or core. Full command argv, inherited TMPDIR/CXX, PID, UTC start/end, exit and stdout/stderr hashes are local-evidence/c42a-DISPATCH.json and the original streams. The environment was inherited unchanged.

**One isolated stage:** stage_local_audit_only.py ran once and produced AUDIT_ONLY_STAGE.json status StagedNotExecuted. It authenticated the original preflight/raw/source/SDK/scratch before copying into /Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a. The manifest binds95 pre-publication original preflight files; the **full live retained preflight contains104** with later publication/helper receipts, and all104 are bound by the stage and after snapshots. The extra records are preserved, not removed or misreported as95. Original failed auditor remains byte-identical, staged separately as ORIGINAL_B7E3_FAILED_AUDITOR.py; the new staged audit.py has Git blob c451e0cb7794e624eabb9029db0a35ba28d14592. The new historical source retains all inherited checks before the final authority block; only the final time-varying Git authority/result scope differs from the reviewed fixed-roster successor. No source assertion was weakened by Local.

**One bounded audit invocation:** argv /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B /Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a/audit.py; cwd=/Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a; PID=43142; exit=1; UTC 2026-10-24T07:37:49.370106+00:00 → 2026-10-24T07:38:12.396850+00:00; America/Los_Angeles 2026-10-24T00:37:49.370106-07:00 → 2026-10-24T00:38:12.396850-07:00; elapsed=23.02670000004582 seconds. Atomic AUDIT_ONLY_INVOCATION.json preceded launch and was never reused. No timeout or unknown command lifetime; originalConsumedCoreRetried=false. Stdout 0 bytes/SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr 427 bytes/SHA256 dd72629059b0b01e1e87bd7252c15f69926e4cc7aca028ace096ea1be7255080. The exact original stderr contains:

    consumer_node=next(n for n in ast.walk(ast.parse(consumer_fixture)) if isinstance(n,ast.FunctionDef) and n.name=='verify_admitted_execution_receipt_and_fail_closed_mutations')
    StopIteration

**IR-LOCAL-P1-HISTORICAL-AUDIT-HELPER-01 — concrete first failure:** the exact bound test source Tools/AssemblyShadow/R03IR/test_p1_command_failures.py defines **verify_admitted_execution_receipt_and_negative_mutations**, at line504, and calls it from the existing original85 success leaf. It contains no method named verify_admitted_execution_receipt_and_fail_closed_mutations. The current test file is byte-identical to original b7e3 execution49c6b62d; SHA256 637915585936544f2c001d936917959b1d53adf62a8e4f7d6b923ad316ed02de. The historical auditor's AST lookup therefore exhausts its iterator, raises StopIteration, and cannot capture the helper source. Its following line1032 call-site assertion also uses the wrong spelling and was not reached.

**Affected scope / Primary direction:** this is an inherited source-identity lookup defect in the independent auditor, not evidence of a native wrapper, SDK compiler, data-custody or product runtime failure. Correct BOTH the successor lookup and following required-call assertion to the exact existing negative_mutations helper. Add a source-bound regression resolving exactly one actual definition and the original call, with explicit missing/duplicate/wrong-identity refusal. Do not rename original tests to fit the auditor, remove consumer negatives, weaken identity checks, edit historical bytes or rerun consumed c42a. The remaining statements after1031, new ADMITTED_EXECUTION_VERIFICATION.json, final captured GIT_BEFORE authority and final EVIDENCE_AUDIT.json are NotRun/unavailable. Later assertions may still fail. A new explicit source-pinned audit-only handoff is needed before any further attempt; no core/SDK rerun is implied.

**Partial vs completed evidence states:**

| Stage | State |
| --- | --- |
| Four current clean exact Git heads, CI/source and fresh-root admission | Passed |
| Source-only tests | Passed23/23 once |
| Isolated staging and original input snapshot | StagedNotExecuted / Passed |
| New historical auditor | FailedOrIncomplete, exit1, StopIteration1031 |
| Assertions/partial outputs before first failure | Retained as partial audit evidence |
| Final admitted helper identity/output and historical-authority/report checks | NotRun |
| EVIDENCE_AUDIT.json | Unavailable_NotProduced |
| Supplied verify-after | Preserved |
| Separate source/SDK/prior-history verification | Preserved |
| Original b7e3 Local/raw result | FAIL / PassedSourceHostAndSDKOnly, unchanged |
| Core/SDK compiler/Unity/Player rerun | NotRun |

**After-preservation:** the shipped verify-after ran ONCE, exit0; AUDIT_ONLY_AFTER.json verifies original preflight104, raw4269, installedSDK2405, scratch1925 and source bindings unchanged, originalLocalFAIL not promoted. Independent after verification also rehashed the entire b7e3 checkpoint2506 files, original104 preflight files, full raw/scratch/SDK, original22 consumed P1 raw/scratch/audit sets, original24 checkpoint sets,88 prior negative symlinks and both e1e5/6c72 histories. Current clean/live source tuple was reverified separately before publication. Staged auditor remains its published blob and original preflight/audit.py remains old failed SHA2b43453f...; original raw manifest and result hashes match before. Exact raw result f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6; raw manifest 4b286c29a7ef36ec4377642b6009804ad532b0ae3166c186866fe74f4246130e.

**Provenance:** all writes/derived audit receipts are isolated in /Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a; original raw /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261023-b7e3, scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261023-b7e3, preflight /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3 and SDK remain read-only. STAGE_FILE_PROVENANCE.json distinguishes unchanged original input copies from new/overwritten isolated outputs. In particular copied stage/GIT_AFTER.json and stage/LOCAL_RESULT.json are historical inputs, not new current authority or this cycle's verdict. Current outcome is stage/C42A_LOCAL_RESULT.json and root LOCAL_RESULT.json; original copied FINDING.json is old b7e3 finding, while current finding is C42A_FINDING/root FINDING. COPY_BINDINGS.json records exact copies and lossless UTF8 encodings used solely for whitespace-safe new checkpoint publication; all raw bytes are unchanged. No missing full audit report, compiler outcome, PID or runtime proof was fabricated.

**Exit: Local Validation → Primary Implementation, FAIL.** Original b7e3 FAIL, original raw scoped PASS and auditline190FAIL remain immutable. E1e5/6c72 Blocked,7896/7c2c scopedPASS,82dd rawFAIL and original findings remain distinct. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; fullP3 Incomplete. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled. No canonical execution TypeKey, physical pointer lifetime, coherent VM epoch, genuine runtime GC/RSS/Shutdown, Player, R03 or Human Review acceptance. No H2/X02/M08A, protected SNAP-01 or further milestone. Stop after this one audit-only result.
