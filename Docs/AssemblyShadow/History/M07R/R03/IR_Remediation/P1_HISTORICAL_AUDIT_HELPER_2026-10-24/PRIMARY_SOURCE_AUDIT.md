# Primary independent source audit — c42a helper-identity failure

## 1. Authoritative evidence read

- Current Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` at publication demo `3f25f4370733f4ca64b6ef5938e319c1bcb05589`, plus the immutable c42a checkpoint (`README.md`, `FINDING.json`, `LOCAL_RESULT.json`, `stage/AUDIT_ONLY_RUN_RECEIPT.json`, `stage/AUDIT_ONLY_AFTER.json`, `MANIFEST.sha256`).
- The actual source of c42a's failed invocation was `audit_historical_only.py` Git blob `c451e0cb7794e624eabb9029db0a35ba28d14592`; the published staged auditor is the same Git blob. It failed with `StopIteration`, exit1, at line 1031, after 23.03 seconds, without `EVIDENCE_AUDIT.json`. Source/SDK/raw/scratch and historical after-preservation passed; no compiler, Unity or core rerun.
- The original consumer `Tools/AssemblyShadow/R03IR/test_p1_command_failures.py` at historical b7e3 tested demo source and current repo has unchanged SHA256 `637915585936544f2c001d936917959b1d53adf62a8e4f7d6b923ad316ed02de`. At source line 504 the real helper definition is `verify_admitted_execution_receipt_and_negative_mutations`; line 892 calls exactly that helper inside the original 85-test success leaf. The actual method includes 17 negative case labels, explicit uncertain-lifetime refusal and error result checks.
- Both c42a source line1031 AST lookup and line1032 required-call assertion incorrectly name the nonexistent `verify_admitted_execution_receipt_and_fail_closed_mutations` method. No native runtime, package or SDK input defect is supported by this failure.

## 2. Exact correction and provenance

New `audit_historical_helper_successor.py`: Git blob `220aa2831458b37a81f66555f27d95349ec7013f`, exactly **two altered lines (1031,1032)** replacing only the two incorrect helper-name occurrences. Bytes change from 177962 to **177956** (-6), with no line insertion/deletion. The predecessor is still present and unmodified; 25 ordered component assertion, all previous historical/native/SDK tests, 17 negative mutations, source SHA extraction `consumerMutationHelperSha256`, all after-1032 original checks and final captured Git authority remain intact.

New `stage_helper_successor.py` is derived from the prior `stage_local_audit_only.py`. It binds the corrected successor Git blob, all b7e3 pre-existing raw/SDK/scratch/source/preflight hashes, and independently verifies the complete **197-file** immutable published c42a checkpoint plus c42a FAIL/finding/audit-exit/after-verification and three consumed original stage source files before and after. It reserves a new absent stage root and copies only historical preflight; the original c42a and b7e3 roots are never used as output. New `run_helper_audit_once.py` is the previous bounded one-shot runner except for the expected source Git blob. Original core/SDK/Unity and original Local auditors are never invoked by Primary.

GitHub Connector actual-readback Git blobs for added source (tests and CI to be verified at final revision) are recorded in this folder's `EVIDENCE.json`; historical c42a failed `stage/audit.py`, original `MANIFEST.sha256` and `LOCAL_RESULT.json` retain their original Git blob identities. The original c42a manifest blob is `091d57e6234331ee1f5a8e1e3d5f1d9d229cf60b`.

## 3. Source-only regression coverage and limitations

`test_historical_helper_identity.py` contains **17** source-bound checks, including actual consumer AST lookup/invocation, exact two-line diff, source SHA, original 85 unique IDs, all 17 negative receipt mutations and synthetic absent/duplicate/wrong method and caller failures. It executes ONLY two isolated source-identity lines, never the actual 1000+-line auditor.

`test_helper_audit_staging.py` contains **11** read-only and synthetic custody regressions: both full source pins, complete 197-file published c42a SHA manifest, c42a immutable FAIL records, synthetic c42a history/copy corruption and forged success refusal, and one-shot marker/source scope. Prior **23** historical staging/run-with-tiny-Python-host tests and the published b7e3 raw-manifest/2506-file SHA verifier remain separate CI steps. Host tests do not execute Unity, official SDK C++/managed compiler, original Core25, original85, real historical auditor or retained original Local inputs.

The first Mac/Linux CI attempt exposed one **test-only literal comparison error**: the expected Git blob assignment was formatted using Python `repr()` (single quotes), but the real source used double quotes. The staging and auditor source pins themselves were correct; the comparison in the synthetic test was amended without modifying the production/staging/auditor checks. The initial failing CI outcome remains a real historical host-test failure, and final CI evidence must cite the post-fix run only.

## 4. Unverified inherited assertions and next Local scope

All old historical auditor code after **line 1032** is still **NotRun** in the last completed c42a Local cycle, including `ADMITTED_EXECUTION_VERIFICATION.json`, final historical Git `GIT_HISTORICAL_AUTHORITY_AFTER.json` and final `EVIDENCE_AUDIT.json`. A new error might be revealed. The complete audit-only result is unavailable until a new independently admitted Local `f51d` one-shot cycle executes the new source against fully retained external files. Any `Stopped/FAIL` outcome must be preserved without retry; Local must not patch substantive code or fabricate status.

Acceptance boundaries: b7e3 overall Local FAIL with separate raw `PassedSourceHostAndSDKOnly` 25/25; c42a overall Local FAIL; P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, P3 Incomplete; all R03/H2/qualification/Human Review/runtime flags false and PureInterpreter disabled. A future isolated historical audit-only PASS would not rewrite either old FAIL or establish full product/runtime/Player/GC/RSS/Shutdown/pointer/epoch safety.
