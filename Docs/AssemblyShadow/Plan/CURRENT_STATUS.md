# Current Status

- Candidate build-input source anchor: `2d44ee4eef735cf9dc5c2295fb8c0df71834743f`.
- Latest Local return: `8788d123ca7769396cf14c707f8df13ac764223b`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/`.
- Gate: `H1 / InProgress / AwaitingFreshControlledWorkflowClosure`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

The prior controlled-label binder defect is closed in real Unity. Profile-1 reached and completed `native-on-controlled`.

Two new V04 blockers were returned:

1. Unity's semantic restoration changed tracked `ProjectSettings/ProjectSettings.asset` bytes, so the next exact source guard failed before profile-1 Native OFF.
2. Candidate profile-2 nested native provenance passed `--skip-demo-source` while inheriting outer M07 authority variables, which the verifier correctly rejected before the controlled Player completed.

Both projects were manually restored to exact pinned tracked bytes and their installed runtimes reverified.

## Current Primary repair

Source anchor `2d44ee4eef735cf9dc5c2295fb8c0df71834743f` contains:

- controlled Player exact-byte transaction extended from `link.xml` to both:
  - `Assets/HybridCLRGenerate/link.xml`;
  - `ProjectSettings/ProjectSettings.asset`;
- post-build bytes retained for both inputs;
- exact restoration attempted for both on success and failure;
- per-input restoration receipts;
- nested `H1BuildInputProvenance` verifier child removes only `H1_M07_WORKFLOW_AUTHORITY_ROOT` and `H1_M07_WORKFLOW_BASELINE_ID`;
- outer coordinator authority and `verify-installed-runtime.py` fail-closed behavior unchanged;
- direct PowerShell recovery regression for success/failure;
- bounded/static and Unity source-contract coverage;
- CI execution of both PowerShell recovery tests.

The HybridCLR, HybridCLR Unity, and IL2CPP source pins are unchanged.

## Required next action

Local Validation must restart fresh V00 and rerun both complete controlled-performance workflows.

For each Native ON/OFF controlled stage, require exact restoration receipts for both `link.xml` and `ProjectSettings.asset`.

Candidate profile-2 must additionally prove the nested native provenance capture succeeds under the explicit child-only environment scope while the subsequent outer source-authority check still executes and passes.

Only after both complete graphs exist may Local continue old-Player rejection, strict build-map freeze, preregistration, pilots, formal samples, analysis, V05, and independent M08.

Historical or reused evidence must retain its original classification; `ReusedAuditedFrom925e` is not fresh current-anchor `Passed`.

Do not begin R02.
