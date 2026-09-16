# Local Validation Tasks — Editor-Compatible Reproduction Tooling

Run fresh **V00–V05** from the authoritative `Documents/AgentHandoff/WEB_TO_LOCAL.md`.

Preserve `local-validation-20260916-534b03e`, `local-validation-20260916-9568ea3`, and all earlier evidence unchanged. Their results remain historical observations under their original source identities.

## V00 — dual source/tooling authority

1. Pull candidate `codex/assembly-shadow-r01b-h1`; record final handoff HEAD, source anchor `3242b071540278510ea4ae287c70e37fc4c60340`, dirty/untracked state and all protected sibling heads.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Use a separate reproduction checkout on `codex/assembly-shadow-h1-count-repro-tooling` at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. From candidate run:

```sh
python3 Tools/AssemblyShadow/h1_reproduction_tooling.py \
  --project /ABS/REPRO_TOOLING \
  --authority-project /ABS/CANDIDATE \
  --output /ABS/NEW/v00/reproduction-tooling.json
```

Require:

- `status=BehaviorAndToolingSourcesVerifiedNotBuildAccepted`;
- behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- protected head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`;
- tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e`;
- exact eleven-file required tool map;
- exact nine-file replacement map;
- exact two-path `toolDeletions` for `H1ManagedSourceProvenanceTests.cs` and `.meta`;
- `editorSourceCompatibility.status=Compatible`;
- protected runtime/native/package/IL2CPP pins unchanged;
- gate flags false.

If either preflight fails, stop before V01–V05. Do not modify the protected or tooling checkout locally.

## V01 — regression and real Unity compile

- Run full H1 Python inventory and `h1_bee_primary_tests.py`, including the deletion and assembled Editor-source compatibility cases.
- Compile candidate in Unity 2022.3.62f2.
- Compile exact tooling successor `ba8fee33...` in Unity 2022.3.62f2. The historical CS0426 must be absent.
- Run the affected H1/Assembly Shadow Editor NUnit suites in candidate and tooling successor.
- Preserve exact logs, XML, test IDs, skips/nonpasses, preflight output and tooling checkout identity.

Any new compile error caused by the assembled tooling tree is a Primary issue unless it is purely machine invocation syntax.

## V02 — fresh candidate schema-3 normal-cache proof

Run a fresh candidate ON/Debug normal-cache proof for source anchor `3242b071...`. Preserve normal Bee cache and require the existing schema-3 action-local recursive response ownership, graph/action/dependency/output/reachability controls, exact fresh Player input binding and no `--reuse-proof` substitution.

Historical candidate V02/V03 evidence remains historical only.

## V03 — fresh six-build set

Use candidate-owned:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch_tooling.py \
  --candidate /ABS/CANDIDATE \
  --reproduction /ABS/REPRO_TOOLING \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /ABS/pwsh \
  --scope all \
  --output /ABS/NEW/v03/builds \
  --execute
```

Do not reuse old-source smoke receipts. Produce fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release.

Each reproduction build must pass current strict native and managed provenance, exact restoration, and receipt-bound tooling identity. Archive the V00 preflight beside the build bindings so the two authenticated deletions and assembled Editor compatibility are part of the evidence chain.

## V04 — runtime/count/startup/capacity/performance

After a valid six-build set, execute the established R01B chain:

- 132 candidate count cells;
- 8 unfixed reproduction cells;
- fresh baseline/fixtures/replay;
- startup11;
- 8192/8193 lifetime-capacity boundary;
- required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage;
- controlled Development performance only against preserved reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

## V05 — successor package and independent whole-chain M08

Build the successor package only from explicit fresh evidence locations. Include:

- candidate and tooling V00 authority outputs;
- exact `source-targets.json` and both source pin files;
- tooling branch/tree identity and exact replacement/deletion delta;
- `editorSourceCompatibility` result;
- each reproduction build's receipt/tooling binding and raw native/managed/PCH/store evidence;
- all current runtime/count/startup/capacity/performance evidence;
- preserved historical evidence with original source identity/disposition.

Authenticate archive/index bytes and membership and run strict semantic verifiers. Then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only genuine independent whole-chain M08 PASS may make the package Ready for Human Review Gate. Then stop for explicit human H1 approval. **Do not begin R02.**
