# Local Validation checkpoint — authority `27df1a3d`

This checkpoint preserves the 2026-09-23 Local Validation batch for candidate checkout `f5e34235641c212c715aef3405925ddd4cf28ee6` and source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`.

Current/protected authority, current Python validation, exact source-delta audits, retained evidence reauthentication, the new graph bridge, retained-pilot admission, and the guard-v2 strict seal all passed. A wholly new formal series then completed all 40 pairs on attempt 1 with no retries.

The final strict analyzer returned `Incomplete` / `ComparabilityIncomplete`. Forty-four otherwise analyzable raw R00 nested `playerBuildReceipt` objects omit `baselineBuildId` and `runtimeAbiHash`, while the analyzer requires both nested fields. The forty-fifth cumulative item is a preserved historical pilot process-cleanup failure. Correct top-level values and all immutable evidence are retained. The receipt issue is a source/tool schema disagreement that must return to Primary; it was not repaired or reinterpreted locally.

## Contents

- `V00/`: candidate, reproduction-tooling, protected-reference, and installed-runtime authority receipts.
- `V01/`: current test results and the audited Unity reuse classification.
- `V01A/`: exact 3-path and 22-path source-delta audit.
- `V02/`: retained-evidence reauthentication receipt.
- `V04/performance/`: bridge, admission, guard-v2 seal, all 40 sample indexes, batch receipt, final analyzer output/log, and failure diagnosis.
- `raw-evidence.tar.gz`: complete working evidence selected for the checkpoint.
- `formal-side-evidence.tar.gz.part-00` and `formal-side-evidence.tar.gz.part-01`: ordered parts of the complete referenced formal-side evidence archive.
- `prior-checkpoints/`: immutable prior checkpoint manifests.
- `handoff/`: final Local Validation and Return-to-Web snapshots.
- `results-summary.json`: machine-readable outcome summary.
- `prior-checkpoints.json`: names and authenticated hashes of prior manifests.
- `MANIFEST.sha256`: checkpoint file authentication.

Reconstruct the split archive by concatenating the parts in lexical order. The reconstructed archive SHA-256 must be `fda8226ee124ecc7d6687e2bbbab30d2166c838fd5fc7225b9972d949982f75f`.

No cleanup of the working evidence was performed. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
