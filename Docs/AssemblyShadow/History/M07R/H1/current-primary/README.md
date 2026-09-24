# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`5f8db436e31df017dbff396b375547394c396ad5`

Current analysis/test/V05 source anchor:

`25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Latest Local V04 closure:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd61-split-analysis/`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local result received

The d61 split-checkout repair closed V04 successfully.

Local passed:

- source authority;
- 381/381 bounded Primary;
- full Python with zero failures/errors;
- exact v2 source audits;
- complete source-27df live evidence reauthentication;
- V04.AF split-checkout compatibility;
- V04.AG strict historical analysis;
- V04.AH authenticated closure checkpoint.

No Player was rerun.

V04.AG returned:

- `result=Passed`;
- `status=ComparabilityPassed`;
- 45 attempts;
- 44 valid/analyzable;
- one preserved invalid historical pilot;
- 40/40 valid formal attempts;
- ten formal pairs/mode;
- one valid pilot/mode;
- complete startup/chronology/non-overlap.

## Returned blocker resolved

Local correctly marked V05 `NotEligibleUnderCurrentHandoff` because the previous handoff did not define an analysis-only successor-evidence contract.

Primary now defines:

`H1AnalysisOnlySuccessorEvidence-v1`

implemented by:

`Tools/AssemblyShadow/h1_historical_reanalysis.py --v05-package`

See:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/V05_M08_CONTRACT.md`

## V05 semantics

V05 verifies and binds:

- the authenticated current V04 closure checkpoint;
- the immutable source-27df execution checkpoint;
- current source authority/tests;
- complete V02 live reauthentication;
- V04 compatibility and full strict performance analysis;
- scoped no-Player evidence;
- canonical H1 gate/evidence/performance documents;
- the independent reviewer configuration.

It does not run Players or convert historical execution into current-source Fresh evidence.

Required classifications:

- `FreshCurrentSourceValidation`;
- `ReusedAuthenticatedFromSource27df`;
- `ReanalyzedImmutableHistoricalExecution`.

Success means only:

`SuccessorEvidenceBoundForIndependentM08`

## Performance

The performance protocol has no approved H1 SLA.

`ComparabilityPassed` is not performance acceptance.

The full measured analysis, including observed slowdowns and increased memory, is bound into V05 and must be examined by independent M08.

## Independent M08

Use:

`.codex/agents/code-gate-reviewer.toml`

in a genuinely independent, read-only context.

The independent review must return PASS / FAIL / BLOCKED and inspect the full chain, not summaries only.

A PASS yields only:

`ReadyForHumanReviewGate`

Human H1 approval remains explicit and separate.

## Source scope

New source anchor:

`25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

The exact seven-path historical analysis policy and 25-path retained-graph policy remain unchanged.

Relative to d61, only these already-authorized paths changed:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

## New regression coverage

Four V05 leaves cover:

- checkpoint manifest tamper;
- positive V05 analysis-only evidence binding and classifications;
- nonpassing V04 analysis rejection;
- invalid no-Player evidence rejection.

Expected next counts:

- bounded: 385;
- full Python: 1,069;
- expected with unchanged environment skips: 1,041 Passed / 28 Skipped / 0 Failed/Error.

Fresh Local execution remains required.

## Next Local cycle

Run one complete batch:

1. V00 source authority.
2. V01 bounded/full Python.
3. exact source audits.
4. complete V02 live reauthentication.
5. rerun V04.AF/V04.AG.
6. authenticate pre-V05 V04 closure.
7. run V05.
8. if eligible, run genuine independent M08.
9. PASS → stop at ReadyForHumanReviewGate.
10. FAIL/BLOCKED → return findings to Primary.

Do not rerun Players.

Do not begin R02.
