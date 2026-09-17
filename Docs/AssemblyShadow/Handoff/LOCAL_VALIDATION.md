# Local Validation report

## Current run — 2026-09-17 handoff 12cf9b2

### Exit

**Local Validation → Primary Implementation**

The candidate branch was explicitly fast-forwarded to handoff `12cf9b25b71bb6fe819b09958a97ab55fb633d7a`; source anchor `f59b0d8d171340951157b01b583df17e380d6f55`, reproduction tooling `ba8fee33753a5ebc215b7a98739e343d8e05572e`, and all protected pins match the handoff. Pre-existing untracked historical `v7`–`v11` evidence was preserved unchanged.

V00–V03 pass. Candidate and reproduction-tooling preflights pass with exact split authority. V01 passes the required H1 Python inventory 480/480, bounded Primary suite 302/302, both real Unity 2022.3.62f2 compiles, and `M07FixedByteBootstrapPolicyTests` 2/2. V02 fresh ON/Debug passes strict native/schema-3 managed provenance; both required managed assemblies are uniquely `BeeCacheHitBoundToFreshPlayerInput`, with exact fresh Player binding and retained-store verification at 318,212,421 logical bytes and 72,612,459 stored bytes. V03 produces six fresh unique Players; all native, managed, tooling-binding, and restoration gates pass.

V04 fresh fixtures independently audit successfully. Candidate count passes 132/132. All eight fresh unfixed reproduction observations are retained with unchanged inputs: six `UnexpectedAccepted` and two Debug nested `AssertAbort`; these are reproduction evidence, not candidate acceptance.

The required controlled M07 path invokes real Unity `ValidateCompilerInputs` successfully and proves actual mutation of `M07Bootstrap.unity` and `AssemblyShadowSettings.asset`. It then fails before the explicit controlled throw because `Assert-M07ControlledPinnedInputs` reruns the full installed-runtime verifier, which rejects the intentionally mutated scene as differing from its pinned Git blob. The outer wrapper restores all three guarded files exactly, and post-recovery candidate authority passes.

A separate normal M07 run reaches the same incompatible post-validation check in `Invoke-M07Build.Core.ps1` line 181. It fails before baseline resources/Players, restores all three guarded files exactly, and passes post-recovery authority. Local did not change the guard because its authority semantics are explicitly outside the Local correction boundary.

Startup11, 8192/8193 capacity, remaining required coverage, controlled performance, V05 successor packaging, and independent whole-chain M08 are `Blocked / NotRun`. Last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`; R02 was not started.

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 dual preflight | `Pass` | Candidate `SourceTargetVerifiedNotBuildAccepted`; tooling `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; exact 9 replacements + 2 deletions; Editor compatibility `Compatible`. |
| V01 Python / Primary | `Pass` | Required H1 inventory 480/480; bounded Primary 302/302. An initial overbroad `test_*.py` inventory is retained separately as a non-acceptance attempt. |
| V01 Unity / NUnit | `Pass` | Both checkouts compile with zero errors; candidate policy tests 2/2. |
| V02 fresh ON/Debug | `Pass` | Receipt `d8e22387...`, GUID `d639b0c9...`; strict native, schema-3 managed, exact fresh binding, normal Bee cache. |
| V02 retention store | `Pass` for integrity | 451 observations/unique/stored; 318,212,421 logical and 72,612,459 stored bytes; `StoreVerifiedNotAcceptance`. |
| V03 six-build set | `Pass` | Six unique receipts/GUIDs; candidate four-mode and reproduction two-mode compiler verifiers pass. |
| V04 candidate count | `Pass` | 132/132 fresh cells. |
| V04 unfixed reproduction | `Pass` as reproduction evidence | 8/8 classified: 6 `UnexpectedAccepted`, 2 Debug `AssertAbort`; not candidate acceptance. |
| V04 controlled recovery | `Fail` | Real validation and required mutation occur; exact three-file restore and post-recovery authority pass; explicit controlled failure is not reached. |
| V04 normal M07 | `Fail` | Same post-validation pinned-scene mismatch at core line 181; no baseline resources or Players. |
| V04 downstream | `Blocked / NotRun` | Startup11, capacity, remaining coverage, and performance lack valid fresh M07 inputs. |
| V05 successor / M08 | `Blocked / NotRun` | Explicit fresh chain incomplete; independent M08 not commissioned. |

Portable evidence is under [local-validation-20260917-12cf9b2](../History/M07R/H1/latest-local/README.md). Complete local raw evidence remains under `/Users/ah/GitHub/hybridclr/_archives/assembly-shadow/cleanup-20260917/evidence/legacy-roots/h1-local-validation-20260916-12cf9b2`. The actionable Primary-owned issue is at the top of [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

Historical Local Validation runs are indexed by `../Evidence/evidence-catalog.json` at predecessor commit `7cb710fa38464b1977a69619fea2b5fc93f79966`.
