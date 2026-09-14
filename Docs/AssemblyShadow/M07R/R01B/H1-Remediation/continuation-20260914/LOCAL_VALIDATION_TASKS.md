# Remaining local validation tasks

These tasks are intentionally committed with the source continuation. Unity/IL2CPP compilation and Player execution were unavailable in the preparation environment; they remain `NotRun`, not failed. Missing external bytes are `Unavailable`, not a runtime failure. The existing M08 FAIL remains authoritative until a new independent review passes.

| ID | Task | Exit condition |
|---|---|---|
| L00 | Verify all target branches/working trees, preserve unrelated changes, record the actual new demo commit and actual installed native/package/IL2CPP identities. | No historical receipt/pin is rewritten to impersonate the new build. |
| L01 | Run new Python tests, real `integration-tests/h1_m02_witness_integration.py`, and the existing full Python suite. | Six-site current config passes, historical five-site input remains readable, exact test IDs are inventoried, regressions explained. |
| L02 | Unity Editor compile, existing M02 validation/ILPP/linked-input checks, all related Editor tests plus `H1EvidenceProcessTests` and `H1WitnessRuntimeEvidenceTests`. | Both declared method variants and generated guard identities match the exact contract; no broad authorization is added to resolve a mismatch. |
| L03 | Fresh candidate four count builds + reproduction two count builds with native and managed source capture. | Each build binds source, response/config/compiler/SDK, actual Player DLL and native artifact. Route A/B is explicit; missing graph stays Blocked. |
| L04 | Fresh eight unfixed reproduction cells: P03-a/b and N02-a/b × Debug/Release. | Preserve 6 `UnexpectedAccepted` + 2 `AssertAbort` if reproduced, including fresh process/build/provenance and assertion logs. Do not relabel fixed-candidate oracle failures as PASS. |
| L05 | Fresh candidate 22 cases × 3 paths × 2 CPP = 132 cells. | Raw result schema 2, exact cell membership/run IDs, correct feature/CPP build, witness/state/reservation/mapping checks through existing strict verifier. |
| L06 | Freeze a compatible current candidate baseline ON/OFF, fixtures, replay, failure/Q04 inputs; run all 11 R01 startup modes. | Fresh `R01EarlyLaunches`; strict `R01EarlyVerification=PassedBoundedProfile`; every mode has complete diagnostics. Positive modes exit 0 and hand to M07; rejection/failure modes exit 1 and do not. |
| L07 | Update M06 impact and rerun affected ordinary/mixed capacity, lazy/dense/FieldRVA, M03–M07, ON/OFF and old-Player boundaries. | Ordinary 8192/512 MiB, mixed 8184+5+3 with 512 MiB valid inputs + 12 failed bytes, max 32 MiB, 8193 rejection and >=25% usable encoded capacity remain demonstrated. Confirm dense adjunct actually ran. |
| L08 | Re-establish controlled candidate/reference Development performance comparability after source freeze; rerun unless source/build equivalence is proved. | Four modes × >=10 fresh-process pairs under the common supported workload; no Release/P99/RAM SLA claim. Preserve observed P01/P03/RSS risks. |
| L09 | Generate fresh NUnit/Python leaf inventories, source-equivalence/scope dispositions and successor selection/archive/index. | New schema-2 count chain, fresh startup11, fresh eight-cell repro and raw compiler/managed provenance are mandatory members. Archive/index member hashes independently rechecked. |
| L10 | Independent reviewer executes design→plan→four-repo source→build/runtime→raw-evidence M08 review. | Findings closed; only actual independent review may return M08 PASS. |
| L11 | Stop and hand to user. | Human explicitly chooses H1 PASS or PASS WITH EXPLICIT DEFERRED RISKS. Until then `humanGatePassed=false`, `mayEnterR02=false`. |

Startup11 is exactly: `Control, OrdinaryFirst, OrdinaryAfterReserve, Oversize, Mismatch, Type, Object, Cctor, NativeScript, MetadataFailure, InitializerFailure`. `Baseline` is separate and cannot fill a missing one of those eleven modes.

Use the existing launchers/verifiers and inspect their `--help` rather than selecting a directory named "latest". Generate test inventories with `h1_test_inventory.py`; compare exact IDs with historical claims rather than accepting aggregate 1021/492 values as proof.
