# Local validation checkpoint — handoff e96bc07

## Disposition

**Local Validation → Primary Implementation**

Candidate handoff `e96bc073e66c1ecdf1f461f9286422a7c9d26f82`, source anchor `3242b071540278510ea4ae287c70e37fc4c60340`, and reproduction-tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e` were validated in isolated checkouts. Protected reproduction `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`, reproduction native `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`, and performance reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` were not moved or modified.

V00–V03 pass. V04 proves 132/132 candidate count cells and captures all eight unfixed reproduction cells, but the fresh M07 baseline stops in real Unity policy validation. `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness` is rejected as an unapproved bootstrap reflection entrypoint even though `ProjectSettings/AssemblyShadowReflectionBindings.json` contains its exact fixed-image acquisition contract. Local Validation did not add an allowlist or change policy semantics.

The baseline workflow changed `M07Bootstrap.unity` and `AssemblyShadowSettings.asset` before failing. Their diffs and before/after blob identities are retained, and both files were restored to exact handoff blobs. Post-restoration candidate and tooling preflights both pass.

V04 startup11, 8192/8193, remaining required coverage, and controlled performance are `Blocked / NotRun`. V05 successor packaging and independent M08 are `Blocked / NotRun`; last independent M08 remains `FAIL`. `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Results

| Stage | Result | Evidence |
| --- | --- | --- |
| V00 candidate authority | `Pass` | `SourceTargetVerifiedNotBuildAccepted` at exact handoff/source anchor. |
| V00 tooling authority | `Pass` | Exact 11-path delta: 9 replacements, 2 authenticated deletions; `editorSourceCompatibility.status=Compatible`. |
| V01 Python / Primary | `Pass` | H1 476/476; Bee Primary 298/298. |
| V01 Unity / NUnit | `Pass` | Candidate and tooling compile with zero errors; prior CS0426 is absent; each checkout passes 4/4 plus 10/10 focused NUnit. |
| V02 candidate ON/Debug | `Pass` | Fresh receipt `d46ee5f8...`; strict native, schema-3 managed, exact Player binding, restoration, and retained-store verification pass. |
| V03 six builds | `Pass` | Four candidate and two unfixed reproduction Players have strict provenance, exact restoration, and tooling bindings. |
| V04 count matrix | `Pass` | Candidate 132/132. Fresh unfixed reproduction: 6 `UnexpectedAccepted`, 2 Debug `AssertAbort`; all eight inputs unchanged. |
| V04 fresh M07 baseline | `Fail` | `BootstrapReflection` at `M07Build.ValidateCompilerInputs`. |
| V04 downstream | `Blocked / NotRun` | No valid fresh M07 baseline/fixtures/replay inputs. |
| V05 / M08 | `Blocked / NotRun` | Explicit fresh evidence chain is incomplete. |

## Evidence map

- `source-state.json`: exact repository identities, working-tree classification, and restoration blobs.
- `results-summary.json`: machine-readable V00–V05 disposition and all six build receipt identities.
- `failure-analysis.json`: direct issue, likely root cause, design gap, impact, and recommended Primary direction.
- `v00/`: both raw authority preflights.
- `v01/`: complete Python/Primary outputs, Unity compile outputs, NUnit XML, inventories, and Unity logs.
- `v02/raw-results.tar.gz`: complete V02 attempts, accepted smoke metadata, provenance verification, and store verification.
- `v03/raw-results.tar.gz`: both six-build attempts, the isolated generated-fixture seed record, install attempts, receipts, provenance, bindings, logs, and restoration evidence.
- `v04/candidate-count-verifications.tar.gz`: 132-cell result index and all 132 verification receipts.
- `v04/reproduction-count-raw.tar.gz`: all eight raw unfixed reproduction launch/result/Unity logs.
- `v04/reproduction-execution.json`: classified eight-cell reproduction summary bound to exact build receipts and fixture audits.
- `v04/control-and-fixture-metadata.tar.gz`: invocation failures, fixture manifests/audits, accepted count commands, post-failure/preflight results, and M07 failure records; generated fixture DLL bytes are represented by the authenticated manifests and audits.
- `v04/m07-baseline/`: directly readable policy failure, gzip-preserved raw task-created diffs, exit code, and exact restoration proof.
- `v05/status.json`: blocked successor/M08 status and closed gates.
- `evidence-manifest.json`: SHA-256 and byte size for every committed checkpoint file except itself.

The external raw workspace remains `/Users/ah/GitHub/hybridclr/h1-local-validation-20260916-e96bc07`; this committed checkpoint is the portable handoff authority.
