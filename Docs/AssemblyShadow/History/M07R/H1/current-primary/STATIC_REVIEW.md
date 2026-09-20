# Static Review — Controlled Performance Recovery-Label Repair

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real controlled-performance execution.

Reviewed source anchor:

`316894a83873c46ffd3eefa57222311ae03da214`

This review does not establish performance acceptance, V05 completion, independent M08 PASS, or Human Review Gate approval.

## Returned Local finding

The `925e84d7...` Local cycle passed all requested runtime work through:

- failure/publication;
- dense-v2 real Player boundary;
- ordinary/mixed capacity;
- protected-reference authentication.

Both graph-bound performance workflows then failed at the same boundary before their first controlled Player build.

The failing production call labels were:

- `native-on-controlled`;
- `native-off-controlled`.

The helper accepted only:

- `native-on`;
- `native-off`.

PowerShell `ValidateSet` rejected the controlled label before the helper body.

## Repair review

The accepted vocabulary is now exactly:

`native-on / native-off / native-on-controlled / native-off-controlled`.

No new branch was introduced into recovery behavior.

The label is used only to distinguish evidence filenames and stage names. All four cases retain the same:

- pre-Unity link.xml snapshot;
- SHA-256 binding;
- immutable backup;
- generated-byte capture;
- finally-path exact restore;
- restored SHA-256 validation;
- restoration receipt schema.

Unknown labels still fail closed.

## Executable binder regression

A source-text assertion alone would repeat the gap that caused the Local failure.

The new PowerShell regression instead parses the real core script AST and loads the actual production helper definition.

For each valid label, it supplies all real parameters and replaces the first Unity-dependent call with a sentinel. Reaching the sentinel proves parameter binding succeeded and helper-body execution began.

For an invalid label, the test requires a PowerShell parameter-validation error and proves the sentinel was not reached.

The test does not depend on Unity installation and is executed directly in GitHub Actions using `pwsh`.

## Primary evidence

Workflow:

`35492692165`

passed:

- bounded Primary: **324/324**;
- committed handoff: **11/11**;
- R01 early capsule: **7/7**;
- R01 early launch: **20/20**;
- R01 early results: **20/20**;
- R01 failure pipeline: **16/16**;
- direct PowerShell binder regression: **Passed**;
- R01B lazy contract: **10/10**.

Artifact:

- `10599209690`;
- ZIP SHA-256 `7e4fd0b9ae99c1c929966364ec15a98403953e6b629e09ef07f81b2b03e50a40`.

## Scope / regression analysis

The functional product delta relative to broad-runtime source anchor `925e84d7...` is confined to the M07 PowerShell coordinator's accepted stage labels.

There are no changes to:

- managed runtime or Bootstrap behavior;
- native runtime;
- package/IL2CPP source;
- transaction/recovery semantics;
- metadata capacity/indexing;
- dense metadata behavior;
- R00 benchmark operations;
- build-map comparability;
- preregistered schedule/statistics.

The historical `925e84d7...` runtime PASS evidence is therefore relevant comparison evidence, but normative H1 version-binding means it is not automatically current-anchor PASS evidence.

Local may record those cells as `ReusedAuditedFrom925e` only after independently proving the exact source-scope delta. A source-scope mismatch requires fresh validation of the affected domain.

## Residual empirical requirements

Local must still execute:

1. fresh source authority and test admission;
2. the repaired profile-1 controlled-performance workflow;
3. the repaired profile-2 controlled-performance workflow;
4. current-anchor old-Player rejection from fresh graphs;
5. strict build-map freeze;
6. preregistration;
7. complete pilot sampling;
8. complete formal sampling and analysis if pilots pass;
9. authenticated checkpoint retention;
10. V05 + genuinely independent M08 if mandatory V04 closes.

## Gate

H1 remains `InProgress`.

Historical M08 remains `FAIL`.

`humanGatePassed=false`.

`mayEnterR02=false`.

Do not begin R02.

## Final committed handoff verification

The exact live handoff commit `16755d156ccf00c1fa9f2b0168c63f42a06cb01e` passed workflow `35492912802` with 324/324 bounded tests, 11/11 handoff, 7/7 early-capsule, 20/20 early-launch, 20/20 early-results, 16/16 failure-pipeline, the direct PowerShell recovery-label binder, and 10/10 lazy-contract tests. Artifact `10599344201`; ZIP SHA-256 `de83de6ede1d6d277c96e667eeb14c2cc292891ef4e394793ee02abd56011e9d`.
