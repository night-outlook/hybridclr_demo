# H1 V05 Analysis-Only Successor Evidence and Independent M08 Contract

## Status

Current source anchor:

`0388479f7073289e3505b992956a7cbe78c302ce`

V05 policy:

`H1AnalysisOnlySuccessorEvidence-v1`

Historical analysis policy remains:

`H1HistoricalPerformanceReanalysis-v2`

Retained graph policy remains:

`H1V04RetainedGraphToolOnlySuccessor-v2`

This contract does not authorize Player reruns, does not relabel source-27df execution as fresh current-source execution, and does not approve H1 or R02.

## Why V05 is analysis-only

The canonical evidence contract permits reviewed reuse when the relevant executable/runtime inputs are unchanged, but forbids relabelling historical evidence as fresh.

The current source successor changes only the exact seven analysis/test paths already authenticated by `H1HistoricalPerformanceReanalysis-v2`. V04 reauthenticates the original source-27df execution graph and reanalyzes its immutable raw bytes under the current analyzer.

Therefore V05 is an evidence-binding stage:

- current V00/V01 source/test validation is Fresh current-source evidence;
- source-27df Player/runtime execution remains historical and reused-authenticated;
- V04 performance is a current reanalysis of historical execution;
- no new Player execution is implied or required.

## Exact source-specific cardinalities

For source anchor `0388479f7073289e3505b992956a7cbe78c302ce`, V05 fails closed unless the bound evidence contains:

- bounded Primary: 387/387 Passed;
- full Python discovery: exactly 1,071 leaves with zero Failed/Error;
- immutable source-27df checkpoint manifest: exactly 92 members;
- sealed-live authentication: exactly 33,792 files and 1,606,993,133 bytes with zero missing/content/stable-stat mismatch.

These are source-specific evidence identities, not adjustable thresholds.

## Required pre-V05 closure checkpoint

Before V05, Local creates and authenticates a V04 closure checkpoint containing at least:

- V00 source authority;
- committed handoff preflight;
- bounded Primary results;
- complete Python inventory;
- V02 complete live reauthentication;
- V02 direct-binding semantics audit;
- V04.AF compatibility receipt;
- V04.AG full performance analysis;
- V04 strict-analysis validation receipt;
- V04 scoped no-Player receipt;
- `MANIFEST.sha256`.

The checkpoint must not claim V05 or M08 completion.

## V05 command

Run from the designated validation checkout:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --v05-package \
  --current-checkpoint <authenticated-current-v04-closure-checkpoint> \
  --historical-checkpoint <authenticated-source-27df-execution-checkpoint> \
  --output <new-v05-successor-evidence.json>
~~~

Require exit code 0 and:

- `kind=H1AnalysisOnlySuccessorEvidence`;
- `status=SuccessorEvidenceBoundForIndependentM08`;
- `policyId=H1AnalysisOnlySuccessorEvidence-v1`;
- `v05Complete=true`;
- `independentM08Eligible=true`;
- `M08Passed=false`;
- `humanGatePassed=false`;
- `mayEnterR02=false`.

## Required evidence classifications

The V05 output must state exactly:

- current source regression: `FreshCurrentSourceValidation`;
- historical execution: `ReusedAuthenticatedFromSource27df`;
- historical performance: `ReanalyzedImmutableHistoricalExecution`;
- fresh current-source Player execution: `false`;
- V05 Player rerun: `false`.

Any output that calls the source-27df Player series Fresh is invalid.

## Performance handling

V05 must bind the complete V04 performance-analysis JSON by SHA-256.

It must state:

`performanceAcceptance=NotClaimedNoSLA`

`ComparabilityPassed` means the paired measurements are valid for analysis. It does not mean the observed performance is acceptable.

Independent M08 must inspect the complete timing, startup and memory statistics. Stable slowdowns, increased RSS/managed memory and variance remain visible review inputs.

## Historical evidence

The source-27df checkpoint remains immutable.

V05 must authenticate its manifest and the fixed hashes:

- graph bridge: `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- pilot seal: `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- formal batch: `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample index: `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

## Independent M08 mechanism

Use the established read-only agent:

`.codex/agents/code-gate-reviewer.toml`

M08 must run in a genuinely independent context. The implementing/validating agent must not self-review and label its own result independent.

Gate type:

`MILESTONE`

The review input must include:

1. `Docs/AssemblyShadow/README.md`;
2. `Docs/AssemblyShadow/Plan/HUMAN_REVIEW_GATES.md`;
3. `Docs/AssemblyShadow/Plan/EVIDENCE_CONTRACT.md`;
4. `Docs/AssemblyShadow/Plan/VALIDATION_MATRIX.md`;
5. `Docs/AssemblyShadow/Plan/PERFORMANCE_PROTOCOL.md`;
6. `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`;
7. the V05 successor-evidence JSON;
8. the current V04 closure checkpoint and manifest;
9. the immutable source-27df execution checkpoint and manifest;
10. current source diff from source-27df to the current source anchor;
11. relevant implementation files in the seven-path analysis/test successor;
12. all prior H1 findings that remain relevant.

## M08 required review questions

The reviewer must determine, independently:

- whether current source/test validation is complete and correctly paired;
- whether source-27df historical execution is reused within the canonical evidence rules;
- whether V04 historical compatibility/reanalysis is fail-closed and source-correct;
- whether the preserved failed pilot is handled honestly;
- whether all 40 formal attempts remain valid and unchanged;
- whether V05 classifications are truthful;
- whether any evidence was silently promoted from Historical/Reused/NotRun to Fresh/Passed;
- whether unfavorable performance/memory results create an actionable H1 defect or residual risk;
- whether the H1 capacity/failure/recovery acceptance criteria are sufficiently evidenced;
- whether any current source defect, missing validation, provenance gap or scope drift remains.

## M08 verdict semantics

Allowed verdicts:

- `PASS`;
- `FAIL`;
- `BLOCKED`.

On FAIL, Local returns the findings to Primary. H1 remains InProgress.

On BLOCKED, Local returns the missing evidence/access. H1 remains InProgress.

On PASS, Local may mark only:

`ReadyForHumanReviewGate`

It must still retain:

- `humanGatePassed=false`;
- `mayEnterR02=false`.

Only explicit human H1 approval can change those fields.

## M08 output

Retain the independent review verbatim under the new Local checkpoint, plus a machine-readable receipt containing:

- reviewer mechanism/config binding;
- source anchor;
- V05 evidence SHA-256;
- current closure manifest SHA-256;
- historical checkpoint manifest SHA-256;
- verdict;
- findings count;
- review start/end;
- read-only/no-mutation assertion.

Do not edit the independent review result to make it PASS.

## M08 BLOCKED re-review addendum — 2026-09-25

The first source-038 independent M08 run completed read-only and returned `BLOCKED` on evidence-package completeness. V05 itself remains valid and does not need to be rerun if source authority remains metadata-only.

Primary closure package:

`m08-evidence-closure-20260925/`

The re-review has two additional mandatory prerequisite receipts:

1. `H1HistoricalCheckpointSuccessorAuthentication`
2. `H1WholeChainSuiteReuseAuthentication`

The independent reviewer must also receive the recovered original M08/finding records and `prior-finding-successor-map.json`.

### Historical manifest semantics

The 925e manifest may be successor-authenticated 293/293 only by substituting the exact recovered historical Handoff bytes for its external relative Handoff member. The original manifest is not edited.

The 6913 manifest must remain historically 29 available + 1 unavailable. The unavailable formal-prelaunch blocker log is excluded only because:

- it is absent from the checkpoint creation Git tree;
- it was a prelaunch operational diagnostic;
- it is not selected for any current claim;
- later source-27df 40/40 formal evidence supersedes the blocked attempt.

Do not call the original 6913 manifest 30/30.

### Whole-H1 reuse semantics

Reused suite evidence is acceptable for re-review only when Local independently authenticates the per-suite bridge.

Required classification is per suite, never blanket:

- `AcceptedReusedAudited`
- `Rejected`
- `Blocked`

Any required Rejected/Blocked suite prevents M08 rerun and returns to Primary.

No reused suite may be relabelled Fresh at source 038.

### Re-review verdict

A new independent M08 is a new review; it must not inherit PASS/FAIL/BLOCKED mechanically from the earlier result.

It must explicitly revisit the prior three BLOCKED findings against E01–E04 receipts.

PASS still means only `ReadyForHumanReviewGate`; human approval remains separate.

## Fresh count closure addendum — 2026-09-25

The second independent source-038 M08 re-review returned `BLOCKED` only because the historical 12cf count suite lacks its underlying 132 launch receipts and raw semantic results.

The prior evidence-closure work remains valid for:

- prior M08/finding provenance;
- 925e effective 293/293 successor authentication;
- 6913 29+1 explicit historical disposition;
- startup11;
- failure/publication/recovery;
- ordinary capacity;
- mixed capacity;
- M07/native regression.

Do not rerun those suites.

Primary authorizes one replacement suite only:

`H1CountMatrixClosureSource038-v1`

See:

`COUNT_MATRIX_CLOSURE_CONTRACT.md`

### Required replacement semantics

The new count suite must be fresh source-038 execution and must retain all evidence layers missing from 12cf:

- 132 canonical cells;
- 132 fresh process/run IDs;
- 132 launch receipts;
- 132 semantic raw outcomes;
- 132 per-cell verification reports;
- strict aggregate `H1CountMatrixVerification / Passed / 132`;
- fresh fixture/audit bindings;
- fresh candidate build/provenance bindings;
- complete matrix/build evidence sealing.

The historical 12cf count evidence remains historical failed-closure evidence and must not be upgraded.

### Whole-H1 successor

After count closure, create:

`H1WholeChainSuiteClosureV2`

with:

- count-chain = `FreshCurrentSourceExecution`;
- the five previously accepted suites = `AcceptedReusedAudited`.

This successor does not change V05 source/performance classifications.

### Independent re-review

A third independent M08 review is eligible only after the fresh count closure and whole-H1 closure V2 both pass.

The reviewer must explicitly revisit the former count Launch/Raw blocker and inspect the complete retained count evidence.

PASS still means only `ReadyForHumanReviewGate`. Human approval remains separate.
