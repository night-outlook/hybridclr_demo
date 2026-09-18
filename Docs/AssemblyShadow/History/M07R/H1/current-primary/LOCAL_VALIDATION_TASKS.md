# Local Validation Tasks — H1 Source Authority Advance

## V00 — authority

1. Pull the final candidate handoff HEAD and record checkout HEAD separately from candidate source anchor `8b1298d6a5979928bdfa30446e2d674d63999b76`.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Run split reproduction-tooling preflight at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. Verify protected reproduction/runtime/package/IL2CPP/performance refs remain exact.
5. Confirm source-target and ProjectSettings demo pin both identify `8b1298d...`.

Stop on any V00 failure. Do not weaken `verify_demo` or expand metadata-only paths.

## V01 — source / focused regressions

Run the complete H1 Python inventory and source-authority tests required by the current H1 matrix. The MethodPtr/dense checkpoint from `local-validation-20260917-methodptr-dense` is exact evidence for build-input anchor `8b1298d...` and may be reused for those focused claims because no build-input file changed after that anchor. It does **not** substitute for fresh source-pin/provenance, Unity, Player, capsule, startup, or V04/V05 evidence.

Real Unity 2022.3.62f2 compilation remains required where called for by the H1 matrix.

## V02 / V03 — provenance and six-build set

Regenerate fresh candidate provenance and the required candidate/reproduction build set under source anchor `8b1298d...` unless an exact current-anchor result is already produced in this same uninterrupted validation chain and satisfies the existing provenance contract.

Do not promote evidence bound to `68df00fe...` or older anchors.

## V04 — fresh M07 and downstream chain

### A. Controlled M07 authority/recovery

Run a fresh controlled M07 baseline as defined by the existing H1 contract. Require the explicit expected controlled failure only after post-validation authority succeeds, then require exact restoration and a fresh candidate preflight.

### B. Normal M07 regeneration

Use a separate fresh baseline ID and run normal `Invoke-M07Build.ps1`.

Require:

- baseline resources;
- Native-ON Player;
- Native-OFF Player;
- generated-link exact restoration;
- structural prepare/compile/restore;
- fixture finalization;
- Editor replay;
- successful normal `m07-build-workflow.json`.

Do not substitute the removed pre-consolidation receipts.

### C. Immediate capsule/startup continuation

Using the exact newly generated fixture/build/replay receipts, generate authenticated control capsules and run startup11 before any workspace cleanup.

Then continue the previously blocked V04 work: M07 Player matrix, 8192/8193 capacity, required lazy/dense/generic/array/reflection/FieldRVA/old-Player coverage, retained M03–M07 coverage, and controlled Development performance where applicable.

### D. Mandatory retention before cleanup

Before deleting, moving, consolidating, or regenerating any `_temp`, `Builds`, Player, resource, fixture, replay, or launch directories, create the new Local checkpoint and authenticate its archive/index.

The retained set must include or explicitly hash-bind at least:

- `m07-build-workflow.json`;
- `m07-fixtures.json`;
- exact Native-ON/OFF `m07-player-build.json` receipts;
- `m07-editor-replay.json`;
- failure/rejected fixture and negative-input receipts referenced by the manifest;
- control capsule files and `capsules.json`;
- startup11 launch receipt/results/logs;
- exact source pins and post-run preflight;
- exact paths/hashes for referenced Player/resource/fixture inputs.

If a required artifact cannot be retained, record `Unavailable` and stop before V05 rather than reconstructing it from summaries.

## V05 — successor + independent whole-chain M08

Build the successor package only from explicit fresh current-anchor evidence. Preserve all older evidence under its original identity.

Commission a genuine independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate. Then stop for explicit human approval.

Do not begin R02.
