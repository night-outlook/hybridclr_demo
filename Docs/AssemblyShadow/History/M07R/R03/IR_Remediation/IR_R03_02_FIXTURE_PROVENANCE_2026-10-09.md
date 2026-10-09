# R03 IR fixture custody and distinct deterministic target — 2026-10-09 UTC

**Primary Implementation evidence and amended IR-input policy; not Local Player acceptance, not independent review closure.** The original independent full-stage R03 verdict is still **FAIL**. No historical S/R/Q/P/O/N evidence, status or byte is rewritten.

## Reconciliation of the failed regeneration contract

The older supplemental [side-effect fixture CI run 37882275356](https://github.com/night-outlook/hybridclr_demo/actions/runs/37882275356) is preserved **Failed**, because its generator's current `--output` emitted fifteen DLL SHA-256 values different from the immutable S inventory (several MVIDs differed). The independent [same-source diagnostic 37891116173](https://github.com/night-outlook/hybridclr_demo/actions/runs/37891116173) showed `NotIdentical` generation of all 15 on Linux and five on macOS. This does **not** demonstrate S's original stored DLLs changed. The original compilation's PE timestamp is an input to byte identity; dnlib's default writer creates a timestamp when not explicitly fixed. Some legacy fixtures also have different MVIDs. Do not assert a single unproved cause for all differences.

It was incorrect to make *regenerating* old DLLs bit-identically an admission prerequisite for a **new** IR-only Player when the original S byte objects are still tracked. The corrected control is stronger at the actual provenance boundary: **authenticate and copy the exact original S Git objects**, reject any byte mismatch, and never run the legacy `--output` generator to supply this batch's baseline inputs. This does not mark the historical regeneration tests Passed, or relax the original S archive seal/manifest or any NativeLayoutAdmissionV1 safeguard. The failed regenerability observations remain archived.

## Immutable historical inputs for the new focused IR batch

- S publication: `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
- Original 15-fixture directory: `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/host/player-fixtures`.
- Original inventory Git blob: `0688bd2dad054bd59fcdd1564a050a398cfa14e7`.
- All fifteen original DLLs are individually committed there, in addition to their placement in the independently authenticated S evidence archive.
- `Tools/AssemblyShadow/R03IR/ir_original_fixtures.py` verifies S is an ancestor of the current demo, checks the original and current exact Git object for each file, checks the working tree's object and each inventoried SHA-256, size, identity fields and path safety, then copies only authenticated bytes to a fresh external directory and emits an exclusive `ir-original-s-fixture-authority.json`. A modified or missing historical byte is **Blocked/Failed before any Player**. No S regeneration, Git clean/reset, or archive reseal is performed.
- `run_terminal_local.py` now calls this admission in place of `Batch.fixtures()` and independently builds the generator **for the new `--ir-target` mode only**. The original immutable 15 inputs are not substituted by new baseline binaries.

This directly replaces the supplemental workflow's logically impossible requirement to equate two separately generated PE files with a previously sealed historical S file. The prior historical FAIL reports remain sources for the *regeneration* behavior, not for the correctness of the new original-S byte staging.

## Deterministic separately identified IR target

The new IR Methods DLL, whose existing private primitive `R03.Node.stable` is incremented by the virtual `Keep` method, is **not an S artifact**. Its writer uses a fixed MVID and zero PE timestamp in its separate `--ir-target` branch; the original `--output` path has not been edited to manipulate historical output.

At identical test-only generator source, two independent writes on **Linux and macOS** produced the same exact hash and MVID:

| Property | Authenticated distinct IR target |
| --- | --- |
| Bytes | **2048** |
| SHA-256 | `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd` |
| MVID | `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff` |
| PE timestamp | `0` |
| Source mode | `SupplementaryIR` |
| Editor layout admission | `Passed` |
| Real Player execution | `NotRun` |

The runner additionally requires this **exact test-only SHA-256/MVID**; the new DLL is forbidden from masquerading as `virtual-slot/Methods.dll` from S.

## Actual CI and limitations

[Run 37894240648](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894240648) **Passed on Linux and macOS** at source `156e1c889d0cefe8162b3ecf8c1e97e8e253efe2`: eight mutation/rejection host tests per OS; verification of fifteen copied S identities and Git bindings; independent deterministic IR writes; clean original and working checkouts. The later [run 37894308627](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894308627) also Passed after pinning the deterministic IR digest in the focused runner. These runs include **zero** Unity Editor/Player executions and do not approve production regression or structural expansion. Historical failed experiments remain Failed with their raw logs.

The bounded independent-stage provenance finding **IR-R03-01** is not fully closed by this input admission: the original S archived result/index/ledger crosswalk passed separately but broad role-specific build/process joins and material capture omissions still require explicit treatment and independent re-review. The native **IR-R03-02** source is committed, but its actual terminal behavior must be measured in a new Mac IL2CPP Player, including the first-caught failure, reflection/delegate/active-field and AOT side-effect controls. Genuine captured-generic and module-initializer cases remain to be covered separately. The independent original FAIL verdict and D1=A/D2=A owner bounds stand.

## Stop and next gate

The correct next decision is whether the source-bound CI/impact review is sufficient to issue a **single new, separately named focused Local Validation batch** using these exact copied S files and this distinct IR target. The authority test and native compile checks do **not** make the Player result Passed, grant H2, or permit a rerun of S.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. Retained R stays staged and untouched; four contaminated warm certificates remain Failed; R02 CPU/H1 RSS risks remain deferred.
