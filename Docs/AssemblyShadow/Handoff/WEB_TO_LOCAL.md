# Primary Implementation → Local Validation

## Objective

Validate the V05 analysis-only successor-evidence implementation at source anchor:

`27e67920c6d8445895c1b9db647d733371a067c0`

Then reclose V04, bind V05, and immediately run a genuinely independent H1 M08 review if V05 succeeds.

Do not rerun Players.

Latest Local return:

`5f8db436e31df017dbff396b375547394c396ad5`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Required identities:

| Repository | Branch | Required source/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | analysis/test/V05 source anchor `27e67920c6d8445895c1b9db647d733371a067c0` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

The final pushed demo checkout HEAD may be later than `27e67920...` only by paths classified as metadata by the unchanged `shadow_tools.metadata_only` policy.

Historical execution source:

`27df1a3d60811dc121f296ab561ae313a382b363`

Retained graph source:

`69130bbb3a6df516916dddb5ad263799a7c6e5e3`

Latest successfully closed V04 checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd61-split-analysis/`

Immutable source-27df execution checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`

## Implementation

### Local result received

At source d61 Local completed:

- V00 source authority;
- 381/381 bounded Primary;
- 1,065 full Python leaves with 1,037 Passed / 28 explicit environment Skipped / 0 Failed/Error;
- exact seven-path / 25-path / d239→d61 three-path source audits;
- source-27df manifest 92/92;
- 33,792/33,792 sealed live files and 1,606,993,133 bytes;
- V04.AF `AuthenticatedAnalysisOnlySuccessor`;
- V04.AG `Passed / ComparabilityPassed`;
- V04.AH authenticated closure checkpoint.

No Player was rerun.

V05 was correctly left `NotEligibleUnderCurrentHandoff` because no runnable analysis-only V05 contract existed.

### V05 contract now implemented

Policy:

`H1AnalysisOnlySuccessorEvidence-v1`

Tool:

`Tools/AssemblyShadow/h1_historical_reanalysis.py --v05-package`

V05 authenticates:

- the complete current V04 closure checkpoint manifest and required V00/V01/V02/V04 members;
- the complete source-27df execution checkpoint manifest;
- current source authority and runtime repository pins;
- current bounded/full-Python evidence;
- complete live historical reauthentication;
- zero unresolved direct-binding semantic mismatch;
- V04.AF compatibility at the same current source;
- V04.AG `Passed / ComparabilityPassed`;
- strict-analysis receipt bound to the full performance JSON;
- scoped no-Player evidence;
- canonical H1 gate/evidence/performance documents;
- the read-only independent-reviewer configuration.

### V05 classifications

A valid result must preserve:

- current source regression:
  `FreshCurrentSourceValidation`;
- source-27df execution:
  `ReusedAuthenticatedFromSource27df`;
- historical performance:
  `ReanalyzedImmutableHistoricalExecution`;
- fresh current-source Player execution:
  `false`;
- Player rerun for V05:
  `false`.

V05 success status:

`SuccessorEvidenceBoundForIndependentM08`

V05 always retains:

- `M08Passed=false`;
- `humanGatePassed=false`;
- `mayEnterR02=false`.

### Performance disposition

The V05 result binds the complete V04 performance-analysis JSON.

It must state:

`performanceAcceptance=NotClaimedNoSLA`

The H1 performance protocol has no approved performance SLA. `ComparabilityPassed` proves measurement comparability; it does not make observed slowdowns, RSS increases, managed-memory differences or variance acceptable automatically.

Independent M08 must review those measurements explicitly.

### Independent M08

Established mechanism:

`.codex/agents/code-gate-reviewer.toml`

Run it in a genuinely independent read-only context with Gate type:

`MILESTONE`

It must review the whole H1 chain, not the V05 summary alone.

Allowed verdicts:

- PASS;
- FAIL;
- BLOCKED.

M08 PASS means only:

`ReadyForHumanReviewGate`

It does not constitute human H1 approval.

Detailed V05/M08 contract:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/V05_M08_CONTRACT.md`

### Source/policy scope

New source anchor:

`27e67920c6d8445895c1b9db647d733371a067c0`

Source-27df → current remains exactly the existing seven-path `H1HistoricalPerformanceReanalysis-v2` set.

Retained 69130 → current remains exactly the existing 25-path `H1V04RetainedGraphToolOnlySuccessor-v2` set.

d61 → current contains exactly:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/h1_historical_reanalysis.py`;
- `Tools/AssemblyShadow/tests/test_h1_graph_reuse.py`.

No shared runtime/input verifier, Player runner, measurement, protocol, schedule, graph producer, native source or runtime source changed.

### New regression coverage

Six V05 fail-closed tests were added inside the already-bounded graph-reuse test module:

1. checkpoint manifest tamper detection;
2. positive V05 evidence binding with exact Fresh/Reused classifications and no approval flags;
3. rejection of non-Passed/non-ComparabilityPassed V04 analysis;
4. rejection of invalid no-Player evidence containing a Player/formal runner command;\n5. rejection of incomplete current-source test cardinality;\n6. rejection of truncated sealed-live file/byte cardinality.

Expected current counts:

- bounded Primary: **387**;
- full Python discovery: **1,071** leaves;
- expected if the prior environment skip set remains:
  **1,043 Passed / 28 Skipped / 0 Failed / 0 Error**.

Fresh Local evidence is required.

## Local validation

Authoritative detailed task plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

V05/M08 contract:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/V05_M08_CONTRACT.md`

Run the following in order.

### V00

Require:

- final pushed HEAD from the handoff prompt;
- clean tracked state before evidence creation;
- source pin = `27e67920...`;
- source anchor → final HEAD zero non-metadata delta;
- all four repository/pin identities exact;
- committed preflight = `SourceTargetVerifiedNotBuildAccepted`.

### V01

Bounded Primary:

- 387 tests;
- 385 Passed;
- zero nonpass.

Complete Python discovery:

- expected 1,071 leaves;
- zero Failed/Error;
- every skip explicit;
- expected 1,043 Passed / 28 Skipped only if the environment skip set is unchanged.

### V01A

Require:

- source-27df → current = exact seven-path v2 set;
- retained 69130 → current = exact 25-path v2 set;
- d61 → current = exactly README + historical reanalysis tool + graph-reuse tests.

### V02

Repeat complete source-27df live evidence authentication:

- checkpoint 92/92;
- four exact fixed hashes;
- 33,792/33,792 sealed files;
- 1,606,993,133 bytes;
- zero unresolved mismatch.

### V04.AF / V04.AG

Because the analysis/V05 tool changed, rerun V04 compatibility and strict analysis at source `27e67920...`.

Use the same explicit `--analysis-project` split-checkout contract.

Require V04.AF `AuthenticatedAnalysisOnlySuccessor` and V04.AG `Passed / ComparabilityPassed`.

Retain the complete performance JSON without suppressing unfavorable values.

### V04.AH — pre-V05 closure checkpoint

Create a new checkpoint containing current V00/V01/V02/V04 evidence and authenticate its `MANIFEST.sha256`.

It must include at least:

- `V00/source-authority.json`;
- `V00/handoff-preflight.json`;
- `V01/bounded-primary/results.json`;
- `V01/python-inventory.json`;
- `V02/live-evidence-reauthentication.json`;
- `V02/direct-binding-semantics-audit.json`;
- `V04/historical-compatibility.json`;
- `V04/historical-performance-analysis.json`;
- `V04/analysis-validation.json`;
- `V04/no-player-proof.json`.

Do not include the future V05 result in this pre-V05 manifest.

### V05

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

- `H1AnalysisOnlySuccessorEvidence`;
- `SuccessorEvidenceBoundForIndependentM08`;
- policy `H1AnalysisOnlySuccessorEvidence-v1`;
- exact Fresh/Reused classifications above;
- `performanceAcceptance=NotClaimedNoSLA`;
- `v05Complete=true`;
- `independentM08Eligible=true`;
- M08/human/R02 flags false.

If V05 fails, stop and return to Primary.

### Independent M08

Only after V05 succeeds, invoke the established `code-gate-reviewer` in an independent read-only context.

The reviewer must read the canonical H1 gate/evidence/validation/performance documents, the current source diff, V05 output, current closure checkpoint, immutable source-27df checkpoint, full V04 performance analysis and relevant prior H1 findings.

Retain the independent response verbatim and create the review receipt specified in `V05_M08_CONTRACT.md`.

Result handling:

- PASS → mark only `ReadyForHumanReviewGate`; stop for explicit human H1 approval.
- FAIL → return findings to Primary.
- BLOCKED → return missing evidence/access to Primary.

Never set `humanGatePassed=true` or `mayEnterR02=true` without explicit human approval.

## Failure evidence

On V00/V01/source failure retain exact repos, revisions, pins, source deltas, inventory/log and first failure.

On V02 failure retain first mismatching live item and prior checkpoint provenance.

On V04 failure retain complete compatibility/analysis output, first semantic failure and no-Player proof.

On V05 failure retain:

- V05 failure JSON;
- both checkpoint manifest SHA-256s;
- first failed member/classification;
- current source authority;
- V04 analysis SHA;
- no-Player evidence.

On M08 FAIL/BLOCKED retain the independent review verbatim and machine receipt. Do not rewrite it.

## Alternatives

Do not:

- rerun Players to satisfy V05;
- use the old fresh-execution `h1_successor_evidence.py` package as a substitute for this V05 contract;
- call source-27df execution Fresh current-source evidence;
- treat `ComparabilityPassed` as performance acceptance;
- hide or remove unfavorable performance/memory measurements;
- alter the preserved invalid pilot;
- weaken the exact seven-path or 25-path policies;
- self-approve independent M08;
- begin R02.

## Risks

- Historical absolute live paths must remain present and hash-identical.
- V05 depends on both checkpoint manifests remaining intact.
- The historical performance series is valid/comparable but includes unfavorable measurements; H1 review must assess them without a predeclared SLA.
- Independent M08 may legitimately FAIL or BLOCK even after V05 binds successfully.
- Human H1 approval remains mandatory after M08 PASS.

## Local correction boundary

Local may adjust only:

- canonical existing evidence-path arguments;
- new output/checkpoint roots;
- permissions/PYTHONPATH;
- bounded command syntax;
- review-receipt timestamps/paths that truthfully record the independent run.

Local must not modify source, pins, policies, evidence classifications, historical receipts, performance statistics, reviewer verdict, or independence rules.

Any non-trivial issue returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress** until a genuine independent M08 PASS.

M08 PASS changes the state only to:

`ReadyForHumanReviewGate`

Human approval is then explicit and separate.

Until that approval:

- `humanGatePassed=false`;
- `mayEnterR02=false`.

**Do not begin R02.**
