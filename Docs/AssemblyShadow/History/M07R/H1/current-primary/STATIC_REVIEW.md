# Static Review — Early Failure Ownership / Lazy Command / Protected M07 Repair

## Verdict

**PASS for Primary → Local handoff.** Reviewed source anchor:

`99ef65db13341f54cf610e18453dddf197ee86e4`

This review is source/tooling only. It does not establish real Unity/IL2CPP Player acceptance, performance acceptance, V05, M08 PASS, or human H1 approval.

## Failure/publication ownership

### Root cause

The prior design used an admission-only Baseline earliest callback, then attempted the real transaction from `R01FailureProbe` after normal host continuation.

That contradicts the first-use contract: host startup may legitimately use candidate baselines before the later MonoBehaviour probe runs.

`BaselineAlreadyUsed` was therefore correct.

### Corrected ownership

The transaction now runs entirely in `R01EarlyStartup`.

Dedicated continuation-only modes were added:

- `MetadataFailureContinue`;
- `InitializerFailureContinue`.

They reuse the exact failure transaction implementation and strict receipt schema.

Only callback termination differs:

- normal failure startup modes → callback 1 / terminal native gateway;
- continuation-only modes → callback 0 / dedicated failure-publication handoff continues.

The generic early launcher rejects continuation-only modes.

### Late probe

`R01FailureProbe` is schema-2, read-only handoff evidence.

Static inspection confirms it does not call:

- `AssemblyShadowRuntime.ConfigureCandidates`;
- `BeginTransaction`;
- `ReserveMetadataBudget`;
- `StageAssembly`;
- `ValidateTransaction`;
- `CommitTransaction`.

It still independently verifies:

- current fixture/failure/Q04 provenance;
- shared profile-2 budget contract;
- exact capsule/early receipt/current PID;
- selected patch/closure/actual DLL/PDB bytes.

It then queries post-host diagnostics/capacity/recovery and requires stable transaction state.

The Python strict gate uses the early receipt as authoritative transaction evidence and the late result only for post-host persistence/provenance.

## Lazy deterministic-v2

The producer/verifier command schema now agrees.

Exactly four generator records are required:

`[mono, generator.exe, fixtureId, output.dll]`

with deterministic IDs/output names for the two runs of fixture 1 followed by the two runs of fixture 2.

All prior v2 generator/tool/hash/shape/parser and sealed-v1 non-relabel rules remain.

## Protected reference M07

The historical protected project had a valid profile-1 source/runtime but an obsolete coordinator verifier policy.

The reusable current core now always calls the current coordinator's:

`Tools/AssemblyShadow/verify-installed-runtime.py`

via `$PSScriptRoot`, even when `-ProjectPath` is an external protected worktree.

The outer wrapper supplies authenticated originals and baseline through `H1_M07_WORKFLOW_*`.

The current Python verifier already has tested dispatch:

- no required mutation observed → full generic verifier;
- mutation observed → runtime/package/native verification plus exact `h1_m07_workflow_authority`.

This avoids modifying the protected source and avoids importing its obsolete verification policy.

`verify-h1-protected-reference.py` authenticates the reference-side Unity producers actually used by the current coordinator, not the old wrapper.

## Regression coverage

Primary regressions cover:

- continued failure capsule codec;
- continued failure receipt semantics and callback 0;
- terminal failure modes remain callback 1;
- same-process early receipt/capsule binding;
- no late transaction mutation calls;
- post-host diagnostics/capacity/recovery tamper rejection;
- early transaction identity tamper rejection;
- dense-v2 four-field generator schema;
- protected M07 core uses current coordinator verifier;
- current verifier pre/post mutation dispatch;
- protected reference identity/producer contract;
- live committed handoff/source preflight.

Most recent complete pre-cleanup run:

workflow `35411171891`:

- bounded: **320/320**;
- handoff: **11/11**;
- early capsule: **7/7**;
- early results: **19/19**;
- failure pipeline: **16/16**;
- lazy: **9/9**.

Final source-anchor workflow `35411286564` passed 320/320 bounded tests plus 11/11 handoff, 7/7 early capsule, 19/19 early results, 16/16 failure pipeline and 9/9 lazy tests. Artifact `10574492806`, ZIP SHA-256 `96e2043424077871e1af6007922aaee74b894d6ed39e7fe1319eb9ba6cf9b079`.

## Source authority

Only `hybridclr_demo` changes in this Primary cycle.

Candidate native/package/IL2CPP pins remain unchanged.

Protected profile-1 heads remain unchanged.

No metadata-only expansion, verifier weakening, runtime ABI/capacity/index relaxation, performance protocol change, or gate-state promotion was introduced.

## Residual empirical work

Local still must prove:

1. fresh current source/provenance/M07;
2. real early-owned Control/Q04/initializer transactions with callback 0 only for dedicated continuation modes;
3. same-PID late post-host persistence;
4. lazy-v2 real diagnostic Player;
5. protected project driven by current candidate M07 coordinator;
6. fresh profile-1 M07 graph;
7. old-Player rejection;
8. controlled A/B Development builds and performance;
9. checkpoint retention;
10. V05 + genuine independent M08 when eligible.

## Gate

H1 remains `InProgress`.

Historical M08 remains `FAIL`.

`humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
