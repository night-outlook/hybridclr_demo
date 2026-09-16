# R01B H1 Local Validation — handoff 534b03e

## Exit

**Local Validation → Primary Implementation**

Candidate handoff `534b03eb49140eb7f9d9fbdb64217e113a317626` and source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` passed the candidate V00 preflight. The separate reproduction-tooling checkout `0c9c2508d94a097dff50028212a01695c8e29c60` passed split behavior/tooling authority with status `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`, exact eleven-file tool identity, exact nine-file override identity, protected behavior/source pins, and false gate flags.

V01 candidate checks pass: H1 Python 472/472, bounded Bee Primary 294/294, Unity 2022.3.62f2 compilation with zero compiler errors, and focused NUnit 4/4 plus 10/10. The exact reproduction-tooling checkout fails its first Unity compile:

```text
Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs(13,43): error CS0426: The type name 'Capture' does not exist in the type 'H1ManagedSourceProvenance'
```

The tooling successor overlays current schema-3 `H1ManagedSourceProvenance.cs` blob `2fdddcde4e9f1c62b93cd5f162aa922c67697628`, but it retains the protected historical test blob `635847f71c72fa0f3b191ff53746d6cfe1efc7d1`, which references the removed nested `Capture` type. The candidate source anchor has no `H1ManagedSourceProvenanceTests.cs` path. Removing or replacing that protected test is an additional tooling delta and allowlist change, so Local did not modify it.

The post-failure split-tooling preflight still passes, proving that the failure occurred inside the declared authenticated source state rather than through local source drift. Per the handoff's additional-tooling-dependency fail-closed rule, tooling NUnit and V02–V05 are `Blocked / NotRun`. No Player build, runtime/count/startup/capacity/performance run, successor package, or independent M08 review was performed. Last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 was not started.

## Source identities

| Role | Identity | Result |
| --- | --- | --- |
| Candidate handoff | `534b03eb49140eb7f9d9fbdb64217e113a317626` | exact |
| Candidate source anchor | `1b1cc9fe192b88be2a20fad31ea030b1e30be669` | exact |
| Candidate native | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | exact, clean |
| Shared package | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | exact, clean |
| Shared IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` | exact, clean |
| Protected reproduction demo | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | unchanged, clean |
| Protected behavior source | `4e3d2035991ab5629265ac663e61bcb2ca62828b` | unchanged |
| Reproduction tooling checkout | `0c9c2508d94a097dff50028212a01695c8e29c60` | exact |
| Reproduction native | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | unchanged, clean |
| Performance reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | unchanged, clean |

Pre-existing untracked historical `v7`–`v11` evidence remains unchanged and excluded from this checkpoint. Historical `local-validation-20260916-9568ea3` candidate V02/V03 evidence was not edited, copied into current acceptance, or relabeled.

## Results

| Step | Result | Evidence |
| --- | --- | --- |
| V00 candidate preflight | `Pass` | `v00/candidate-handoff.json`; `SourceTargetVerifiedNotBuildAccepted` |
| V00 tooling authority | `Pass` | `v00/reproduction-tooling.json`; exact split-tooling authority |
| V01 H1 Python | `Pass` | 472/472 in `v01/h1-python-inventory.json` |
| V01 Bee Primary | `Pass` | 294/294 in `v01/bee-primary/results.json` |
| V01 candidate Unity | `Pass` | zero compiler errors; focused NUnit 14/14 |
| V01 tooling Unity | `Fail` | CS0426 in historical managed-source test; full raw Unity log preserved |
| V01 tooling NUnit | `Blocked / NotRun` | project cannot compile |
| V02–V05 | `Blocked / NotRun` | handoff forbids expanding tooling allowlist locally |

## Root cause and Primary action

The V00 model authenticates the declared validation bridge/tool files and exact nine-path delta, but it does not close over protected tracked Editor tests that compile against those overlaid types. The tooling successor therefore combines the current bridge with a historical test API consumer that candidate source removed.

Primary should publish a reviewed tooling-only successor that removes or updates `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs`, add that exact change to the authenticated tooling delta, and extend the split-tooling regression to audit/compile protected tracked Editor test dependencies. Fresh V00–V05 remain required after the successor is published.

## Evidence map

- `source-state.json`: all checkout, pin, branch, and dirty-state observations.
- `results-summary.json`: Pass/Fail/Blocked/NotRun dispositions.
- `failure-analysis.json`: direct issue, root cause, design gap, and allowed disposition.
- `v00/`: candidate and tooling preflight output, stdout/stderr, exit records, including the preserved wrapper-recording mistake.
- `v01/reproduction-tooling-unity-compile.unity.log`: complete Unity compile failure.
- `v01/reproduction-tooling-compile-blob-identity.txt`: bridge/test blob identities.
- `v01/reproduction-tooling-vs-candidate-test.diff`: candidate anchor path deletion comparison.
- `v01/reproduction-tooling-postcompile.json`: source authority still exact after the failed Unity invocation.
- `v01/h1-python-inventory.json` and `v01/bee-primary/results.json`: exact Python test identities.
- `v01/candidate-*`: candidate compilation, focused NUnit XML, inventories, and logs.
