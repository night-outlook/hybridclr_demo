# Local Validation Tasks — M07 Post-Validation Authority Repair

## V00 — authority

1. Pull final candidate handoff HEAD and record checkout HEAD separately from source anchor `21d3d5763ce027185d2e7f777f71545d354d44ec`.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Run split reproduction-tooling preflight at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. Verify protected reproduction/runtime/package/IL2CPP/performance refs remain exact.

Stop on any V00 failure.

## V01 — source / Unity regressions

Run the full H1 Python inventory and exact bounded Primary suite, then real Unity 2022.3.62f2 compilation for candidate and reproduction tooling.

Require the M07 policy integration tests to pass and retain exact logs/XML. Include the new M07 workflow-authority regressions in the test inventory.

## V02 — fresh candidate provenance

Run fresh candidate ON/Debug normal-cache provenance under source anchor `21d3d576...`.

Require strict native compiler/PCH/store verification, schema-3 managed provenance, exact fresh Player binding and exact restoration. Preserve normal Bee cache; do not substitute legacy reuse proof.

## V03 — fresh six-build set

Use candidate-owned `h1_count_build_batch_tooling.py` to produce fresh:

- candidate ON/OFF × Debug/Release;
- unfixed reproduction ON Debug/Release.

Require strict current native+managed provenance, reproduction-tooling binding and exact restoration for each accepted build.

## V04 — fresh count + M07 authority + full downstream chain

Re-run candidate 132 count cells and all eight unfixed reproduction observations under the current source anchor. Older passing count evidence remains historical comparison only.

### A. Controlled post-validation authority / restoration

After fresh V03 installs the exact candidate runtime, choose a new baseline ID and invoke:

```powershell
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 `
  -ProjectPath /ABS/CANDIDATE `
  -BaselineId M07-Baseline-H1-<NEW-CONTROLLED-ID> `
  -TimeoutSec 28800 `
  -ControlledFailureAfterValidateCompilerInputs
```

Require:

1. pre-mutation full installed-runtime/demo source verification passes;
2. real Unity `M07Build.ValidateCompilerInputs` succeeds;
3. scene and `AssemblyShadowSettings.asset` actually mutate and contain the exact requested baseline ID;
4. the post-validation recheck succeeds under the new split authority; retain its `M07PostValidationAuthorityVerifiedNotBuildAccepted` output or equivalent raw stdout;
5. execution reaches the exact explicit failure text:
   `Controlled M07 failure after successful ValidateCompilerInputs for exact-byte restoration verification.`
6. `workflow-inputs-restored.json` reports exact restoration for all three paths;
7. pre-restore evidence retains the actual mutated bytes;
8. all three post-restore hashes equal their authenticated originals;
9. a fresh full candidate handoff/source preflight passes after recovery.

If post-validation authority rejects another tracked input, retain the exact path/hash/diff and return to Primary. Do not add it to the mutable set locally.

### B. Separate normal successful M07 chain

Use another fresh baseline ID and invoke normal `Invoke-M07Build.ps1` without the controlled switch.

Require it to pass the former post-`ValidateCompilerInputs` guard and proceed through:

- `BuildBaselineResources`;
- Native-ON Player;
- Native-OFF Player;
- structural resources and exact settings recovery;
- fixture finalization and Editor replay.

Retain repeated M07 authority/pin recheck outputs where available. The workflow must not depend on caller `--skip-demo-source` or a broadened source allowlist.

Then complete the required H1 downstream chain:

- startup11;
- 8192/8193 capacity boundary;
- required lazy/dense/generic/array/reflection/FieldRVA/old-Player coverage;
- required M03–M07 retained coverage;
- controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

## V05 — successor + independent whole-chain M08

Build the successor package only from explicit fresh current-anchor evidence. Include:

- both V00 authority outputs;
- V01 source/Unity/policy evidence;
- V02/V03 strict provenance and six-build receipts;
- current count/reproduction evidence;
- controlled M07 mutable-authority output, explicit controlled failure, pre-restore bytes and exact-restoration receipt;
- normal successful M07 resources/Players/fixtures/replay;
- startup/capacity/retained-coverage/performance evidence;
- historical checkpoints under their original identities and dispositions.

Authenticate archive/index bytes and semantic membership. Then commission a genuinely independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate. Then stop for explicit human approval. Do not begin R02.
