# H1 V05 Analysis-Only Successor Evidence and Independent M08 Contract

## Status

Current source anchor:

`25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

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
