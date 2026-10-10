# IR-LOCAL-CUSTODY-02 — Primary correction after D preflight BLOCKED (2026-10-10 UTC)

**Owner: Primary Implementation. Result: Source/host regression repaired; fresh E Local Validation conditional.** This checkpoint records a narrowly scoped correction to the Docs-only original-C custody verifier. It does NOT alter C or D Local evidence, historical strict custody, runtime sources, source pins, admission thresholds, or acceptance flags. No Unity, native Player build, or Player process was executed by Primary.

## Verified defect and correction

D validation source `hybridclr_demo@7313c768a2658ae77357e3fb1a83e9542585c99c` ran ten synthetic verifier tests successfully but returned `ScopedCustodyPreflightBlocked` for both before/after verifier invocations. The first failure was immutable original-C `NATIVE_LIVE_CUSTODY_LIMIT.json` receipt authentication. The published literal was only 53 characters: `5cf6365c3e84e5390868984b52b40534de0fa53b92499d0359f9d`. The original immutable C SHA-256 is **`5cf6365c3e84e5390868984b52a2f11cc8f52b40534de0fa53b92499d0359f9d`** (64 chars); original Git blob `cca29fae8e0bbe7431d44b1f3f0eff96727c5756`. The original C publication was `36b9828d62bb81d98e81d055871a9540fe116276`. D publication `4d728038f562ddbf7e35564409e9d3b436c6772c` and its failed receipts are immutable facts.

Changed only `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py` and `test_scoped_custody.py`:

- Correct the native-limit SHA-256 to the original source bytes; preserve all four map-part SHA-256 and 416,844-entry frozen roster pins.
- Fail closed on malformed SHA-256/Git-blob/map-part constants **before** consuming C evidence.
- Authenticate all five genuine C JSON receipts using independently pinned original Git blob IDs in addition to their SHA-256 values.
- Extend 10 synthetic tests with five real-source tests, including all-five receipt authentication, malformed SHA rejection, wrong Git-blob rejection, and parsing of the **complete immutable original C roster** without inspecting or altering historical live S files.

### Independent source-bound CI evidence

A separate CI-only branch `codex/r03-ir-custody-02-sourcecheck-20261009` was forked from the corrected active feature source `81502a93b472e52f189969fb74bdf358b352cb07`; its only extra file is its own CI workflow. Active feature branches are unaffected by the CI workflow and retain a Docs-only delta after C# compilation source anchor `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`.

- [GitHub Actions run 38031146338](https://github.com/night-outlook/hybridclr_demo/actions/runs/38031146338), job 114152170509: completed **success**, exact executing `675930d9125b7ca11f183d857210e2934ae72ff7`.
- Python AST syntax: Passed. **15/15** custody tests Passed, no failed/error/skipped test; complete genuine C map parsed successfully.
- The CI job independently computed native-limit SHA-256 `5cf6365c3e84e5390868984b52a2f11cc8f52b40534de0fa53b92499d0359f9d`, consistent with original C bytes and code pin.
- Artifact 11661479189, SHA-256 `966724f5418f2be067807772e5894c9f997979e3a13c163c108a5d9567da3f93`, retains the CI test output/source identity; it is retention-limited, not an original S artifact.
- See [EVIDENCE.json](EVIDENCE.json) for exact source, executions, scopes, outcomes and non-acceptance classification.

**Limit:** CI operates on repository C bytes and synthetic temporary files. It did **not** hash the current macOS 339,367 historical surviving files, verify that all 77,477 original missing paths still have the same status, reserve 64 GiB headroom, or compile/run Unity. The real full live census remains a new E Local prerequisite.

## E authorization boundary

Use the new [E procedure](E_FOCUSED_LOCAL_PROCEDURE_2026-10-10.md), current `Handoff/WEB_TO_LOCAL.md` and **final pushed four-SHA Primary handoff**. No local E work may infer the final commit from this document or reuse A/B/C/D external roots.

The original C custody map (416,844 entries) and D `CustodyBlocked`/scope-failure reports remain fixed. A new E `ScopedHistoricalLossStable` result is allowed only if all 339,367 expected surviving bytes match and exactly the same 77,477 original C path+hash identities remain missing, before and after; any new loss, restored item, changed byte, symlink, incomplete scan or altered C manifest is Blocked. Historical full custody remains `CustodyBlocked`, and four historical installed native roots remain Missing/NotReauthenticated. Original sealed S 90 Passed is not full-stage R03 acceptance.

Fresh E must separately pass source/remote CI-equivalence, 15 original S fixture Git objects, 15 custody tests, 64 host Python tests, 69 native policy checks, retained Q/R/S authentication, and new 64 GiB/20 GiB storage admission. At most one `--execute` invocation of the unchanged 14-cell/3-build/4-Player runner may occur after all gates pass. Preserve any negative result; no retry or recovery of D. No S/R/Q/P/O/N rerun or protected cleanup.

**Current acceptance boundaries:** independent R03 full-stage review FAIL, independent re-review NotRun; `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter structural expansion disabled. IR-R03-01 capture/semantic closure and genuine captured-generic/initializer terminal-witness coverage remain unresolved.
