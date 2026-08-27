# M02 acceptance evidence

Actual local execution: Unity 2022.3.62f2, macOS ARM64, 2026-08-27.
Final milestone acceptance is recorded separately in the M02 review record.
The [run ledger](run-ledger.json) records commands, process exit codes and the
intentional OFF-configuration source-check refusal followed by ON restoration.

## Results

- [Editor integration](editor-validation.json): all 13 cases passed.
- [NUnit XML](editor-tests.xml): 319 passed, none failed or skipped.
- [Python regressions](python-tests.log): 93 passed.
- [Full artifact verification](verification.json): all four patches, actual Player
  inputs, linked reflection proof, frozen resource provenance and original bundles.
- [Reflection Player probe](m02-reflection.json): 26 allowed names, eight denied
  inputs, 17 finite discovery types, fixed-image execution and rejection checks.
- [Old-bundle baseline](m02-old-bundles-baseline.json) and
  [old-bundle P01](m02-old-bundles-p01.json): both exit zero. P01 retains the M01
  conditional feasibility result; it is not a production Shadow acceptance.
- [Native-OFF build](native-off-build.json) and
  [ordinary regression](native-off-result.json): build/Player exit zero.
- [Restored installed-source verification](installed-source-verification.json):
  strict ON check passes after the temporary OFF configuration is restored.

| Patch | Changed root | Closure size | Publication classification |
| --- | --- | ---: | --- |
| [P01](patch-p01.json) | Internal | 1 | DLL-only |
| [P02](patch-p02.json) | Extensibility | 3 | DLL-only |
| [P03](patch-p03.json) | Contracts | 5 | DLL-only |
| [P05](patch-p05-requires-bundles.json) | Internal | 1 | prefab and business-scene bundle rebuild required |

## Provenance

[artifact-inventory.json](artifact-inventory.json) records 23 byte-identical
archive copies and 22 separately hashed artifacts, including the actual ON/OFF
native binaries, raw Unity/Player logs and the unchanged M01 bundle bytes.
Original generated filenames are recorded as `sourceAtCapture`; archived paths
are the immutable Git evidence when a generated filename is later reused.

The pinned source boundary is in [source-pins.json](source-pins.json). The final
baseline is [baseline-manifest.json](baseline-manifest.json), build ID
`M02-Baseline-96de80420a47cfe2`.
Its [Player input receipt](player-input-receipt.json),
[linked receipt](linked-player-receipt.json),
[linked reflection proof](linked-reflection-evidence.json) and
[resource-build receipt](resource-build-receipt.json) are archived unchanged.
DLLs, apps and complete compiler/reference snapshots remain in ignored local
artifact directories; they are not embedded in this Git directory.

The current successful T02 run is:
`_temp/AssemblyShadow/M02Validation-374b53367f134d229d8ccb1abb3071eb`.
The actual Player input root is:
`_temp/AssemblyShadow/M02PlayerInputs-376a558c6dba461bae6a73bd6b40a686`.

[P05 state](p05-define-state.json), [Unity restoration](p05-restored.json),
[exact-byte restoration](p05-settings-restored.json), and
[P05 compiler snapshot](p05-compile-snapshot.json) bind the structural compile
to its run, baseline, source pins and original settings. The original settings
snapshot remains in that unique run directory.

[native-off-settings.diff](native-off-settings.diff) records the only tracked
OFF-build overrides: the M00 scene and native feature flag. Strict source
verification correctly refused the scene override while OFF. After restoration,
the default ON verifier passed; no source-check bypass was used.

## Read-only replay

From the isolated `hybridclr_demo_shadow` project, with the captured artifact
directories and matching pinned Unity installation still available:

```sh
python3 Tools/AssemblyShadow/verify-m02-results.py \
  --editor-result Docs/AssemblyShadow/M02/Evidence/editor-validation.json \
  --nunit-results Docs/AssemblyShadow/M02/Evidence/editor-tests.xml \
  --m01-baseline-root BaselineArtifacts/StandaloneOSX/M01-Baseline-v1 \
  --reflection-result Docs/AssemblyShadow/M02/Evidence/m02-reflection.json
python3 Tools/AssemblyShadow/verify-installed-runtime.py --expect-shadow on --json
```

The first command replays the frozen M02 artifacts. The second checks the current
installed/source state and therefore must be rerun at the matching M02 checkout,
not assumed to stay green after later milestone development.

See [the M02 report](../M02-report.md) for reproduction entrypoints, known limits,
source/API inventory, design extensions and the next-milestone gate.
