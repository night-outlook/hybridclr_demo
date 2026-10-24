# R03 P1 — Historical auditor admitted-helper identity correction

## 1. Authority and observed first failure

Latest Local-owned `20261023-c42a` is **overall FAIL / FailedOrIncomplete**. Its ONE isolated historical audit-only process exited 1, raising `StopIteration` at source line **1031**, before producing `EVIDENCE_AUDIT.json`. The original `b7e3` raw batch remains `PassedSourceHostAndSDKOnly` (25/25); its separate original required auditor FAILED at line 190, hence original overall Local FAIL. The c42a historical audit is a distinct later failure, not a revision of b7e3.

Local admission and two independent after-preservation processes verified 4,269 original raw files, 2,405 installed Unity 2022.3.62f2 SDK files (316,062,203 bytes), 1,925 original SDK scratch files and 104 retained original preflight files. The 23/23 source-only prerequisite, isolated staging, and single historical auditor invocation are factual. No new core/SDK compiler/Unity/Player ran; original sources and historical findings were not rewritten.

The original consumer `Tools/AssemblyShadow/R03IR/test_p1_command_failures.py` (SHA256 `637915585936544f2c001d936917959b1d53adf62a8e4f7d6b923ad316ed02de`) defines `OwnedBindingInventoryContract.verify_admitted_execution_receipt_and_negative_mutations` at line 504 and calls it exactly once from original 85-test leaf `test_all_eighteen_components_have_independent_success` at line 892. The original helper includes 17 explicit negative mutations and an uncertain-lifetime refusal. The c42a inherited auditor expected the nonexistent `verify_admitted_execution_receipt_and_fail_closed_mutations` in BOTH the AST name lookup (line 1031) and mandatory call-site assertion (line 1032). This is an auditor/receipt identity mismatch, not a demonstrated native/SDK/product defect.

## 2. Primary Implementation — minimal source correction

The complete new `audit_historical_helper_successor.py` is derived byte-for-byte from consumed c42a `audit_historical_only.py` (Git blob `c451e0cb7794e624eabb9029db0a35ba28d14592`) with **exactly two string replacements on lines 1031 and 1032**. Its new Git blob is `220aa2831458b37a81f66555f27d95349ec7013f`, its length is six bytes smaller, and every other line is unchanged. The actual source/AST method and source segment SHA, exact call-site, eight receipt inventory flags, admitted host proof, all previous original85/source/SDK/negative checks, and terminal *historical-captured Git* authority remain intact. No original consumer code, original c42a auditor or old checkpoint was edited. `PassedHistoricalEvidenceAuditOnly` retains its narrow scope; it never promotes original Local FAIL.

New immutable `stage_helper_successor.py` is derived from the earlier successful one-shot stager, solely changes the expected auditor blob/file and strengthens consumed **c42a history custody**: complete 197-entry published checkpoint Git manifest, original c42a FAIL/finding/failed-auditor receipt, preserved after-report and three source-bound files in the original c42a external stage. It continues independently binding all b7e3 raw 4,269, installed SDK 2,405, scratch 1,925 and original 104 preflight inputs before and after the one-shot. It rejects canonical/overlapping stage roots. It copies original preflight into a NEW isolated staging root; only the staged `audit.py` is replaced. It does not invoke the audit or any compiler.

New `run_helper_audit_once.py` is the old bounded one-shot runner with **only its expected auditor Git blob changed**. It creates the atomic invocation marker before process launch, captures stdout/stderr hashes and PID/exit/lifetime, fails closed on timeout/errors and refuses retry. No original raw/source/SDK input is writable by design.

## 3. Test scope

`test_historical_helper_identity.py` (17 host-only tests) pins the exact full source and prior finding, AST-verifies one existing helper definition/one correct owner/caller from original85, compares the new auditor to exactly two changed lines, executes ONLY the two isolated identity statements (never the full auditor), and rejects wrong spelling, missing/duplicate definitions or calls, wrong caller/receiver and altered negative case inventory. `test_helper_audit_staging.py` (11 host-only tests) checks old and new runner/stager source pins, exact 197-file published c42a checkpoint, synthetic immutable c42a FAIL/stage custody, tampered historical source and fake PASS rejection. The already-published 23 source-only tests and full published b7e3 checkpoint verifier are retained as additional gates. On Mac and Linux the expected complete host suite is **17+11+23=51 tests per platform**, plus full published SHA evidence check.

These tests cannot substitute for executing the new full historical auditor against the original external Local evidence. A later assertion could still fail. A complete audit-only PASS must be based on true exit 0, all original downstream assertions, a new `EVIDENCE_AUDIT.json` with the exact narrow historical result, and independent pre/post preservation.

## 4. Fresh one-shot Local Validation boundary

The previous `c42a` isolated root and checkpoint are consumed. A new independent audit-only Local cycle may be authorized with fresh identifiers after final Mac/Linux source CI PASS and exact remote source pin verification:

- Audit-only root: `/Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261024-f51d`
- New factual checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-audit-only-p1-20261024-f51d/`

Before either exists, independently verify absence, canonical identity, source boundaries, installed SDK and all retained evidence. Run only the published source-bound tests, new staging script ONCE, new bounded historical auditor ONCE and independent after-preservation. No Local source edits, retries, original root reuse, SDK compile, Unity Player/Editor, core25, original85 or later project milestones. Report any unknown-lifetime/assertion failure as a new distinct audit-only FAIL and return to Primary.

## 5. Acceptance and historical outcome discipline

Original `7896` and `7c2c` host+SDK scoped PASS, `82dd` raw aggregate FAIL, `e1e5` and `6c72` prerequisite Blocked, `b7e3` raw scoped PASS but overall Local FAIL, and `c42a` distinct isolated audit FAIL must remain intact. `P1=Incomplete`, `P2=NotIntegrated`, `E0=Blocked/Unavailable`, `E1=BlockedByE0`, `P3=Incomplete`. All `R03Accepted`, `H2Passed`, `qualificationApproved`, `ReadyForHumanReviewGate`, `runtimeAcceptance`, `fullLegacyRegressionAcceptance` remain false. PureInterpreter disabled. No H2/X02/M08A, protected SNAP-01 or Human Review Gate.
