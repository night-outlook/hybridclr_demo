# Local Validation Tasks — Split Reproduction Tooling

Run fresh **V00–V05** from the authoritative `WEB_TO_LOCAL.md`. Preserve `local-validation-20260916-9568ea3` unchanged; its candidate V02/V03 results remain historical evidence, not current-source acceptance.

## V00 — source/tooling authority

1. Candidate checkout: pull `codex/assembly-shadow-r01b-h1`, record checkout HEAD and source anchor.
2. Run candidate handoff preflight into a new absolute output path; require `SourceTargetVerifiedNotBuildAccepted`.
3. Use a separate reproduction checkout on branch `codex/assembly-shadow-h1-count-repro-tooling` at exact revision `0c9c2508d94a097dff50028212a01695c8e29c60`.
4. From candidate run:

```sh
python3 Tools/AssemblyShadow/h1_reproduction_tooling.py \
  --project /ABS/REPRO_TOOLING \
  --authority-project /ABS/CANDIDATE \
  --output /ABS/NEW/v00/reproduction-tooling.json
```

Require `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`, behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`, protected head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`, tooling revision `0c9c2508d94a097dff50028212a01695c8e29c60`, exact 11-file tool map / 9-file override map, protected runtime pins unchanged and gate flags false.

If either preflight fails, stop before V01–V05. Do not modify the protected reproduction branch locally.

## V01 — affected regression and Unity compile

- Run full H1 Python inventory and `h1_bee_primary_tests.py`, including split-tooling and receipt-binding tests.
- Compile candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` in Unity 2022.3.62f2.
- Compile exact reproduction-tooling revision `0c9c250...`; verify both native provenance and managed schema-3 capture bridge compile while protected behavior/runtime pins remain unchanged.
- Run focused H1/Assembly Shadow Editor tests on both checkouts.
- Preserve exact IDs, logs/XML, skips/nonpasses and both V00 preflights.

## V02 — fresh candidate schema-3 normal-cache proof

Re-run candidate ON/Debug normal-cache proof using the new candidate source anchor. Preserve normal Bee cache. Require schema-3 action-local recursive response ownership, complete graph/action/dependency/output/reachability checks, exact fresh Player binding and no `--reuse-proof` substitution.

The prior candidate V02/V03 evidence in `local-validation-20260916-9568ea3` remains preserved for history/comparison but is not relabeled as this source anchor's fresh acceptance.

## V03 — fresh six-build set with split reproduction tooling

Use candidate-owned wrapper only:

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

Do not reuse an old-source smoke receipt. Build fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release.

Every accepted reproduction build must pass current native **and managed** provenance and exact restoration, and must contain `validation-tooling-binding.json` with:

- `role=reproduction`;
- `behaviorSourceCommit=4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- `validationCheckoutCommit=validationToolingCommit=0c9c2508d94a097dff50028212a01695c8e29c60`;
- exact protected source-pin SHA;
- exact strictly verified build-receipt SHA;
- exact current candidate `source-targets.json` SHA;
- exact complete 11-file tool identity map;
- gate flags false.

If any additional tooling dependency, protected pin change or unsupported real graph is encountered, stop and return evidence to Primary. Do not expand the tooling allowlist locally.

## V04 — runtime/count/startup/capacity/performance

After a valid six-build set, run the current R01B chain: 132 candidate count cells; 8 unfixed reproduction cells; fresh baseline/fixtures/replay and startup11; 8192/8193 lifetime-capacity boundary; required boundary/lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage; controlled Development performance only against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

Preserve raw failures/classifications; do not infer unsupported Release/P99/device-RAM acceptance.

## V05 — successor and independent M08

Package explicit fresh evidence including V00 split-tooling preflight, exact source-target/pin bytes, tooling branch tree/delta, every reproduction `validation-tooling-binding.json`, each bound receipt, raw reproduction native+managed/PCH/store evidence, and preserved historical candidate V02/V03 evidence with original source identity/disposition.

Authenticate archive/index bytes and semantic membership, then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only genuine independent whole-chain M08 PASS can make the package Ready for Human Review Gate. Then stop for explicit human H1 approval. Do not begin R02.
