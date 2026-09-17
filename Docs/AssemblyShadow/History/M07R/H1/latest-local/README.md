# H1 Local Validation checkpoint — 12cf9b2

Candidate handoff `12cf9b25b71bb6fe819b09958a97ab55fb633d7a`, source anchor `f59b0d8d171340951157b01b583df17e380d6f55`, and reproduction-tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e` were validated in isolated checkouts. All protected reproduction, native, package, IL2CPP, and performance-reference pins remained unchanged.

V00–V03 pass. V01 includes real Unity 2022.3.62f2 compilation and `M07FixedByteBootstrapPolicyTests` 2/2. V02 proves fresh ON/Debug provenance and the 318,212,421-byte logical capture store. V03 produces six fresh unique Players with strict native/schema-3 managed provenance, exact fresh Player binding, tooling binding, and restoration. V04 candidate count passes 132/132; all eight unfixed reproduction observations are retained separately (six `UnexpectedAccepted`, two Debug `AssertAbort`).

The required controlled M07 path fails after real `ValidateCompilerInputs` succeeds and mutates both `M07Bootstrap.unity` and `AssemblyShadowSettings.asset`. The post-validation call to the full installed-runtime verifier rejects the intentionally mutated scene before the explicit controlled-failure throw. The outer wrapper restores all three guarded files exactly, and post-recovery authority passes. A separate normal M07 run reaches the same post-validation guard and fails before baseline resources. It also restores all three files exactly and passes post-recovery authority.

This is a Primary-owned workflow/authority issue. Local did not modify the guard, policy, allowlists, protected pins, provenance, runtime, ABI, or performance methodology. Startup11, 8192/8193, remaining coverage, performance, V05 successor, and independent M08 are `Blocked / NotRun`. Human Review Gate is not ready, `mayEnterR02=false`, and R02 was not started.

## Results

| Step | Result | Evidence |
| --- | --- | --- |
| V00 authority | `Pass` | `v00-v03/v00/` |
| V01 Unity / policy | `Pass` | External raw root recorded in Local report; 480/480, 302/302, Unity compiles, policy 2/2 |
| V02 smoke / retained store | `Pass` | Fresh receipt `d8e22387...`; 318,212,421 logical / 72,612,459 stored bytes |
| V03 six-build provenance | `Pass` | `v00-v03/v03-verification-summary.json` |
| V04 candidate count | `Pass` | `candidate-count-verifications.tar.gz`; 132/132 |
| V04 unfixed reproduction | `Pass` as reproduction evidence | `reproduction-execution.json`, `reproduction-count-raw.tar.gz`; not candidate acceptance |
| V04 controlled recovery | `Fail` | Real validation and mutation occur, exact restore passes, explicit controlled throw is not reached |
| V04 normal M07 | `Fail` | Same post-validation pin mismatch; baseline resources are not built |
| V04 downstream | `Blocked / NotRun` | No valid M07 baseline/Players/fixtures/replay |
| V05 / independent M08 | `Blocked / NotRun` | `v05/status.json` |

Machine-readable disposition is in `results-summary.json`; root-cause analysis is in `failure-analysis.json`. Raw evidence outside Git remains under `/Users/ah/GitHub/hybridclr/h1-local-validation-20260916-12cf9b2` and the two isolated checkout `_temp/AssemblyShadow/H1LocalValidation-12cf9b2` roots.
