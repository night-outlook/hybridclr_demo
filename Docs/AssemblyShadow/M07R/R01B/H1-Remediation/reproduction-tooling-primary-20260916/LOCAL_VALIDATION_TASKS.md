# Local Validation Tasks — Split Reproduction Tooling

Run fresh **V00–V05** from the authoritative `WEB_TO_LOCAL.md`. Preserve `local-validation-20260916-9568ea3` unchanged; its candidate V02/V03 results remain historical evidence, not current-source acceptance.

## V00 — source/tooling authority

1. Candidate checkout: pull `codex/assembly-shadow-r01b-h1`, record checkout HEAD and source anchor.
2. Run candidate handoff preflight into a new absolute output path; require `SourceTargetVerifiedNotBuildAccepted`.
3. Use a separate reproduction checkout on branch `codex/assembly-shadow-h1-count-repro-tooling` at exact revision `482a615bb662666f16f861c560f15c6607b82224`.
4. From the candidate checkout run:

```sh
python3 Tools/AssemblyShadow/h1_reproduction_tooling.py \
  --project /ABS/REPRO_TOOLING \
  --authority-project /ABS/CANDIDATE \
  --output /ABS/NEW/v00/reproduction-tooling.json
```

Require:

- `status=BehaviorAndToolingSourcesVerifiedNotBuildAccepted`;
- `behaviorSourceCommit=4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- `protectedPublishedHead=352d7474dd7c2ffd9b9501d8fa42334a3b236e05`;
- `validationToolingCommit=482a615bb662666f16f861c560f15c6607b82224`;
- exact declared tool file/override maps;
- protected runtime/native/package/IL2CPP pins unchanged;
- gate flags false.

If either V00 preflight fails, stop before V01–V05 and return evidence. Do not repair the protected reproduction branch locally.

## V01 — affected regression and Unity compile

- Run the full H1 Python inventory and `h1_bee_primary_tests.py`; include `test_h1_reproduction_tooling` and `test_h1_reproduction_tooling_binding`.
- Compile candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` in Unity 2022.3.62f2.
- Compile the exact reproduction-tooling checkout in Unity; confirm the protected behavior/runtime pins still identify the unfixed reproduction chain.
- Run focused H1/Assembly Shadow Editor tests on candidate and reproduction-tooling checkout.
- Preserve exact test IDs, logs/XML, skips/nonpasses, branch/HEAD and source/tooling preflight outputs.

## V02 — fresh candidate schema-3 normal-cache proof

Re-run the affected candidate ON/Debug normal-cache proof using the new candidate source anchor. Preserve normal Bee cache. Require schema-3 action-local recursive response ownership, complete graph/action/dependency/output/reachability checks, exact fresh Player binding, and no `--reuse-proof` substitution.

The prior candidate V02/V03 evidence in `local-validation-20260916-9568ea3` remains preserved and may be referenced for history/comparison, but must not be relabeled as this source anchor's fresh acceptance.

## V03 — fresh six-build set with split reproduction tooling

Use the candidate-owned wrapper, not the old batch entry point:

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

Do **not** reuse an old-source smoke receipt. Build fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release.

For every accepted build require the established strict native/managed provenance and exact restoration. For each reproduction build additionally require `validation-tooling-binding.json` and verify:

- `role=reproduction`;
- `behaviorSourceCommit=4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- `validationCheckoutCommit=validationToolingCommit=482a615bb662666f16f861c560f15c6607b82224`;
- `sourcePinSha256` equals the protected reproduction pin file used by the build;
- `buildReceiptSha256` equals the strictly verified receipt bytes;
- `authoritySourceTargetSha256` equals the current committed candidate `source-targets.json` bytes;
- the exact complete tool file map is present;
- gate flags remain false.

If the tooling checkout needs any additional non-metadata path, any protected pin changes, or the current policy cannot consume the real graph, stop and return complete evidence to Primary. Do not expand the tooling allowlist locally.

## V04 — runtime/count/startup/capacity/performance

After a valid six-build set exists, run the current R01B chain:

- 132 candidate count cells;
- 8 unfixed reproduction cells;
- fresh baseline/fixtures/replay and 11 startup modes;
- ordinary/mixed 8192 lifetime capacity and 8193 rejection;
- boundary/lazy/dense/generic/array/reflection/FieldRVA/old-Player and affected M03–M07 coverage;
- controlled Development performance only against protected performance reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

Preserve all raw failures and classifications; do not infer unsupported Release/P99/device-RAM acceptance.

## V05 — successor and independent M08

Create the successor evidence package from explicit fresh locations. In addition to existing candidate/native/managed/runtime evidence include:

- V00 `ReproductionValidationToolingPreflight`;
- exact `source-targets.json` and protected reproduction pins;
- tooling-branch tree/delta identity;
- each reproduction build's `validation-tooling-binding.json`;
- the build receipt each sidecar hashes;
- raw reproduction compiler/PCH/domain/store evidence;
- preserved historical candidate V02/V03 evidence with its original source identity/disposition.

Authenticate archive/index bytes and membership and run strict semantic verifiers. Then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only a genuine independent whole-chain M08 PASS can make the package Ready for Human Review Gate. Then stop for explicit human H1 approval. Do not begin R02.
