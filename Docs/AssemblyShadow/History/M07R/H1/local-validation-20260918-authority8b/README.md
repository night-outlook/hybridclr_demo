# H1 Local Validation — authority `8b1298d` fresh M07 checkpoint

This checkpoint preserves the fresh local chain produced from clean candidate checkout `dc64f250c1c47f260625fe60bac80fd26f0c7cdc` and candidate source authority `8b1298d6a5979928bdfa30446e2d674d63999b76` on macOS 26.5.2 / Unity 2022.3.62f2 / StandaloneOSX arm64.

V00–V03 passed: both source-authority preflights passed, protected refs remained exact, Unity compilation and the fixed-byte policy tests passed, and six fresh candidate/reproduction Players were provenance-verified. The controlled M07 run reached its expected explicit post-validation failure and restored all three guarded inputs exactly. A separate normal M07 run passed and produced baseline `M07-Baseline-H1-Authority8b-Normal-20260918A`.

The complete current launch contract was retained before cleanup. The normal workflow, fixture manifest, ON/OFF receipts, Editor replay, failure fixtures, Q04 negative input, all 13 control capsules, startup11 receipts/results/logs, and the 14-mode M07 Player receipts/results/logs are present in `raw-evidence.tar.gz`. Large Player, resource, and captured-input trees remain in the validation workspace and are explicitly hash-bound by the archived ON/OFF receipts, launch receipts, and their complete input-hash maps.

Startup11 passed its independent strict gate as `PassedBoundedProfile`. The 14-mode M07 Player matrix passed Gate 3B with no missing modes.

The next failure/publication prerequisite is blocked. All three launches were attempted, but the current `run-r01-failure-players.py` / `r01_failure_results.py` command contract omits an authenticated early capsule. The advanced Player therefore refused startup before host continuation; the strict result is `Failed` with `R01-Failure-P03-Control.exitCode: expected 0, got 1`. The verifier module also lacks a `__main__` entrypoint; Local invoked its existing `main()` directly without changing source.

Capacity 8192/8193, lazy/dense/generic/array/reflection/FieldRVA/old-Player, retained M03–M07, controlled Development performance, V05, and M08 were not run after this prerequisite failure. H1 remains `InProgress`; the prior M08 state remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Key receipt hashes:

- `m07-build-workflow.json`: `1b3301d22a2d30109f6ba1f57e00b53284873b71620bb80f2f43ce9b43282b8b`
- `m07-fixtures.json`: `0e4036bc803504e9452dbb1881b7390df09f5e8bc7e8fef4db8d5c728ec465fd`
- Native-ON `m07-player-build.json`: `b5afad2b527d594f4e81ecda85fc673e0a0a888000673b54c14d58d9689dfc5f`
- Native-OFF `m07-player-build.json`: `e60aaf47a83fd5c8d85d7abf688234c98a27e1b92e3286b55970d27614fd271c`
- `m07-editor-replay.json`: `f258aa16b83fe9b57f50b961c73feb268ab27eacb1393f8b9fefd5b4b26665ec`
- `capsules.json`: `17625693999627566962258a26c50797712aac9ab7a9527edcbc7b952e9d114e`
- startup11 strict result: `cd322f083c4f50f98af2cdcb0a2937f3e8965435992e54de43236c9f4106902e`
- M07 Gate 3B result: `ccf24653f696f7d1ef52b6dc1e0d576c8b669cab112e35d42c466f0d45b9d87d`
- failure-matrix strict result: `ebeb4def22376d037d39b28fe7fe79bb4c964b211ff5341bad65810387e2d8a2`

`MANIFEST.sha256` authenticates this README, `results-summary.json`, and `raw-evidence.tar.gz`.
