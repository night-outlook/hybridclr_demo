# Static Review — R00 Final Analysis Contract + Historical 40/40 Reanalysis

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real compatibility preflight and reanalysis of the immutable 27df series.

Reviewed source/tool anchor:

`7aa6f61994da354b04464e38ddfc8552cc5c3055`

## Latest source-authority review

**PASS for repair strategy; empirical V00 rerun remains required.**

The post-anchor agent migration made the checkout fail the unchanged complete non-metadata-tree check. Treating all `.agents/` or `.codex/` files as metadata would widen the verifier around files that can influence validation behavior, while advancing the source anchor would break the fixed five-file historical-analysis compatibility contract.

Primary therefore restored only the nine drifted agent-configuration files to their exact source-anchor blobs. A remote comparison from `7aa6f619...` to the repaired branch now contains only paths already classified as metadata by the existing verifier. A remote comparison from source-27df to the repaired branch retains exactly the original five non-metadata analysis paths.

No historical receipt, runtime tool, analyzer source, verifier source, protocol, schedule, graph, Player, or native source was changed by this repair.

## Returned finding

The 40/40 formal series passed execution.

The final analyzer then rejected 44 analyzable attempts because it expected:

- `playerBuildReceipt.baselineBuildId`;
- `playerBuildReceipt.runtimeAbiHash`.

The real R00 producer does not require those nested duplicates.

It emits and verifies those identities at raw top level.

## Analyzer correction review

The corrected analyzer now requires top-level:

- build GUID;
- baseline build ID;
- runtime ABI hash.

It still requires nested:

- receipt path;
- receipt hash;
- build GUID.

Optional nested baseline/runtime values, when present, must agree.

This is stricter than simply deleting checks: the intended build identity remains mandatory and is now checked at the producer-defined location.

## Historical-series reuse decision

The 40/40 series may be reused because:

- all 40 formal pairs passed runtime execution;
- no formal retry was needed;
- build-map comparability passed;
- chronology passed;
- raw evidence is immutable and checkpointed;
- the defect exists only in final analyzer interpretation;
- current source changes no execution or measurement component.

Normal current-source bridge verification is **not** relaxed to make this work.

Instead, a separate analysis-only compatibility policy authenticates historical receipts against historical Git.

## Compatibility proof review

The fixed policy validates:

1. exact bridge SHA;
2. exact guard-v2 seal SHA;
3. exact formal-batch SHA and 40/40 status;
4. exact final sample-index SHA;
5. historical source/check-out pins;
6. graph bridge 69130→27df transition;
7. exact historical bridge verifier inventory;
8. exact historical seal verifier inventory;
9. retained pilot historical runner provenance;
10. all 40 formal current-runner/formal-authority bindings;
11. protected A has no retained authority;
12. candidate B successful launch echoes authority/bridge/seal/map;
13. exact five-file 27df→current analysis-only Git delta.

Any execution/runtime/measurement/protocol/schedule/graph/native delta rejects compatibility.

## Evidence selection

The historical index contains 45 attempts:

- 5 pilot attempts, including one preserved failed attempt and its later successful retry;
- 40 passed formal attempts.

Existing analyzer selection semantics retain the failed pilot evidence but select the later valid pilot for that pair.

Expected selected evidence after the build-binding fix:

- 4 valid pilot pairs;
- 40 valid formal pairs.

No evidence is deleted or relabelled.

## Regression review

Primary tests cover:

- real Local contract diagnosis;
- correct real-producer build binding;
- top-level tampering/missing-field rejection;
- optional nested conflict rejection;
- real exact five-file Git delta;
- historical bridge and seal Git authentication;
- exact checkpoint hash constants;
- formal-batch 40/40 contract;
- synthetic complete formal authority chain and runner-provenance isolation.

## Source scope

`27df1a3d... → 7aa6f619...` is exactly five non-metadata analysis paths.

`69130bbb... → 7aa6f619...` is the closed 24-path retained-graph tooling allowlist.

No Player/runtime/measurement/native/protocol/schedule/graph-production source changed.

## Primary validation

Workflow `35942350651` at `4c368bdb...` passed bounded **376/376**, live handoff **11/11**, R01 early capsule **7/7**, early launch **20/20**, early results **20/20**, failure pipeline **16/16**, both M07 recovery regressions, and lazy **10/10**.

Artifact `10784819521` has SHA-256 `9df947a5443d24f8f4d1a8cc71b1f440f3894f357a84824aa47ea65023c7f51b`.

## Residual empirical requirements

Local must run the compatibility proof and corrected analysis against the real live 27df evidence.

If it passes, no Player rerun is required and V04 may close.

Then authenticate an analysis-only checkpoint and proceed to V05 / genuinely independent M08.

If compatibility fails for a non-analysis reason, return to Primary rather than widening the policy.

H1 remains `InProgress`. Do not begin R02.
