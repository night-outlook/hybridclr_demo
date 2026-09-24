# Local Validation Tasks — V05 + Independent M08 Closure

Current analysis/test/V05 source anchor:

`25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

Latest Local return:

`5f8db436e31df017dbff396b375547394c396ad5`

Completed formal execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Previous validated source:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`

Previous V04 closure checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd61-split-analysis/`

V05/M08 contract:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/V05_M08_CONTRACT.md`

H1 remains `InProgress`. Do not begin R02.

## Goal

In one Local cycle:

fresh current-source validation → complete live historical reauthentication → V04 revalidation → authenticated pre-V05 checkpoint → V05 analysis-only successor evidence → genuinely independent M08 → stop for human H1 review if and only if M08 PASSes.

Do not rerun Players.

## V00 — source authority

1. Pull final pushed `codex/assembly-shadow-r01b-h1`.
2. Use the exact final pushed HEAD from the handoff prompt.
3. Require clean tracked state before creating evidence.
4. Record all four repository paths, branches, commits, remote heads, remotes, worktrees, pins and package reference.
5. Require demo source pin:
   `25cd25f675c0caaf5009fd1aa3136aa0d98302d8`.
6. Require source anchor → final handoff HEAD has zero non-metadata paths.
7. Run committed handoff/source preflight.
8. Require `SourceTargetVerifiedNotBuildAccepted`.

Do not classify this as Player/build acceptance.

## V01 — bounded regression

Run:

`Tools/AssemblyShadow/h1_bee_primary_tests.py`

Require:

- `testCount=385`;
- 385 Passed;
- zero Skipped/Failed/Error.

Explicitly require the four new V05 tests:

- `test_v05_checkpoint_manifest_detects_member_tamper`;
- `test_v05_analysis_only_successor_binds_without_fresh_player_claim`;
- `test_v05_rejects_nonpassing_historical_analysis`;
- `test_v05_rejects_invalid_no_player_evidence`.

Also retain all prior split-checkout and paired-performance positive regression results.

## V01B — complete Python discovery

Run complete `test*.py` discovery through `h1_test_inventory.py`.

Expected current inventory:

- 1,069 leaves;
- if environment skips are unchanged:
  - 1,041 Passed;
  - 28 explicit Skipped;
  - 0 Failed;
  - 0 Error.

Requirements:

- discovered count equals executed count;
- zero Failed/Error;
- every skip is explicit and retained.

Treat expected skip/pass counts as an expectation, not as permission to alter results.

## V01A — source audits

### Historical execution → current source

Require:

`27df1a3d60811dc121f296ab561ae313a382b363 → 25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

to equal exactly the existing seven-path `H1HistoricalPerformanceReanalysis-v2` set:

1. `Tools/AssemblyShadow/README.md`
2. `Tools/AssemblyShadow/h1_bee_primary_tests.py`
3. `Tools/AssemblyShadow/h1_graph_reuse.py`
4. `Tools/AssemblyShadow/h1_historical_reanalysis.py`
5. `Tools/AssemblyShadow/h1_paired_performance.py`
6. `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`
7. `Tools/AssemblyShadow/tests/test_h1_paired_performance.py`

### Retained graph → current source

Require retained graph `69130bbb...` → current source to equal the existing exact 25-path `H1V04RetainedGraphToolOnlySuccessor-v2` set.

### Previous source → current source

Require:

`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece → 25cd25f675c0caaf5009fd1aa3136aa0d98302d8`

to contain exactly:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

Any additional non-metadata path fails.

## V02 — complete historical live reauthentication

Repeat the same complete read-only source-27df authentication used in the previous successful Local cycle.

Require:

- source-27df checkpoint manifest: 92/92;
- graph bridge exact SHA;
- pilot seal exact SHA;
- formal batch exact SHA;
- final sample exact SHA;
- 33,792/33,792 sealed files;
- 1,606,993,133 verified bytes;
- zero missing/content/stable-stat mismatches;
- direct binding semantics: zero unresolved mismatch.

Fixed hashes:

- bridge `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`;
- seal `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`;
- batch `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

Do not rewrite or relocate historical evidence.

## V04.AF — compatibility revalidation

Because `h1_historical_reanalysis.py` changed at the new source anchor, rerun V04.AF.

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --sample-index <original-live-final-sample-index> \
  --pilot-verification-receipt <original-live-pilot-seal> \
  --graph-reuse-bridge <original-live-graph-bridge> \
  --formal-batch <original-live-formal-batch> \
  --output <new-v04af-output> \
  --preflight-only
~~~

Require:

- `AuthenticatedAnalysisOnlySuccessor`;
- policy `H1HistoricalPerformanceReanalysis-v2`;
- current source `25cd25f...`;
- exact 7-path delta;
- original historical bridge/seal/formal-authority identities;
- exact four historical input hashes;
- 45 attempts / 40 formal;
- no Player launch.

## V04.AG — strict historical analysis revalidation

Only after V04.AF passes, rerun without `--preflight-only`.

Require the same closure conditions previously demonstrated:

- `Passed / ComparabilityPassed`;
- 45 retained attempts;
- 44 valid/analyzable;
- exactly one preserved invalid historical ON-NoPatch pilot attempt;
- all 40 formal attempts valid;
- 10 formal pairs/mode;
- one valid selected pilot/mode;
- 10 startup observations/mode;
- complete chronology and non-overlap.

Retain the full performance JSON unchanged, including unfavorable results.

`ComparabilityPassed` is not performance acceptance.

## V04.AH — create pre-V05 closure checkpoint

Create a new authenticated checkpoint for this source cycle containing at minimum:

- V00 source authority + committed preflight;
- V01 bounded results + full Python inventory/log;
- V01A exact source audits;
- V02 complete live authentication and binding-semantics audit;
- V04.AF compatibility;
- V04.AG full performance analysis;
- strict-analysis validation receipt;
- scoped no-Player receipt;
- references to prior blocked/closed checkpoints.

Create and verify `MANIFEST.sha256`.

Do **not** include the future V05 output in this pre-V05 manifest.

## V05 — analysis-only successor evidence

Run:

~~~text
python3 Tools/AssemblyShadow/h1_historical_reanalysis.py \
  --analysis-project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --v05-package \
  --current-checkpoint <new-authenticated-pre-v05-v04-closure-checkpoint> \
  --historical-checkpoint /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked \
  --output <new-v05-successor-evidence.json>
~~~

Require:

- exit 0;
- `kind=H1AnalysisOnlySuccessorEvidence`;
- `status=SuccessorEvidenceBoundForIndependentM08`;
- `policyId=H1AnalysisOnlySuccessorEvidence-v1`;
- `v05Complete=true`;
- `independentM08Eligible=true`;
- `M08Passed=false`;
- `humanGatePassed=false`;
- `mayEnterR02=false`.

Require exact classifications:

- current source regression = `FreshCurrentSourceValidation`;
- historical execution = `ReusedAuthenticatedFromSource27df`;
- historical performance = `ReanalyzedImmutableHistoricalExecution`;
- fresh current-source Player execution = false;
- Player rerun for V05 = false.

Require:

`performanceAcceptance=NotClaimedNoSLA`.

Retain the full bound performance analysis for M08.

If V05 fails, stop and return to Primary with the failure output. Do not attempt independent M08.

## Independent M08 — mandatory whole-chain review

Prerequisite: V05 success only.

Use a genuinely independent read-only context with:

`.codex/agents/code-gate-reviewer.toml`

Gate:

`MILESTONE`

Read first:

1. `Docs/AssemblyShadow/README.md`
2. `Docs/AssemblyShadow/Plan/HUMAN_REVIEW_GATES.md`
3. `Docs/AssemblyShadow/Plan/EVIDENCE_CONTRACT.md`
4. `Docs/AssemblyShadow/Plan/VALIDATION_MATRIX.md`
5. `Docs/AssemblyShadow/Plan/PERFORMANCE_PROTOCOL.md`
6. `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`
7. `Docs/AssemblyShadow/History/M07R/H1/current-primary/V05_M08_CONTRACT.md`
8. the new V05 JSON;
9. the new pre-V05 closure checkpoint;
10. the immutable source-27df execution checkpoint;
11. current source diff / relevant seven source files;
12. prior H1 findings relevant to current scope.

The reviewer must explicitly inspect the complete V04 performance JSON. It must not treat `ComparabilityPassed` as performance acceptance.

Allowed verdicts:

- PASS;
- FAIL;
- BLOCKED.

Retain the independent review verbatim.

Create a machine-readable review receipt binding:

- reviewer config SHA;
- current source anchor;
- V05 evidence SHA;
- current closure manifest SHA;
- historical checkpoint manifest SHA;
- verdict;
- findings count;
- start/end time;
- read-only/no-mutation assertion.

Do not edit an independent FAIL/BLOCKED result.

## Result handling

### M08 PASS

Mark only:

`ReadyForHumanReviewGate`

Keep:

- `humanGatePassed=false`;
- `mayEnterR02=false`.

Stop for explicit human H1 approval.

### M08 FAIL

Return the findings to Primary.

H1 remains `InProgress`.

### M08 BLOCKED

Return the missing evidence/access reason to Primary.

H1 remains `InProgress`.

## Final checkpoint

After V05 and M08 outcome, create a new checkpoint that includes:

- all current V00–V05 evidence;
- V05 successor evidence;
- independent M08 output/receipt when run;
- final Local handoff snapshots;
- authenticated manifest.

Do not overwrite historical checkpoints.

## Local correction boundary

Local may adjust only:

- canonical existing evidence path arguments;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded invocation syntax.

Local must not modify:

- source;
- source pins;
- 7/25-path policies;
- V05 classifications;
- historical receipts/evidence;
- performance statistics;
- independent-review verdict;
- M08 independence rules.

Any non-trivial issue returns to Primary.

**Do not rerun Players. Do not begin R02.**
