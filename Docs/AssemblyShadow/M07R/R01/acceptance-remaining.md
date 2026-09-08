# R01 Remaining Acceptance

Status: **Active / Unaccepted**. This is the current v6 checklist for R01. It supplements the normative plan and validation matrix; it cannot advance H1 or authorize R02.

## Current source and evidence boundary

The v6 executable pairing is:

```text
hybridclr       b22fa3d92223645c32663e4a2157eaadf8ea495e
hybridclr_unity b649c499385ea68490a0f652a98b732e060aeb89
il2cpp_plus     7967b8c7043904fcae130b294defd5ce7aa897c4
hybridclr_demo  cc7b17683c2e68a162914c347bb81d765dbc26c0
runtime ABI     46814a65339ab321eb2c35ac2b8edd9ff180ce60039a13d650d4bf3f4f3bcc00
```

The v5 installation verification is retained historical evidence. The v6 baseline is `M07-Baseline-R01-early-v6`; fresh installation/build pairing is pending in `_temp/AssemblyShadow/R01/early-v6-build-driver-1.log` and `_temp/AssemblyShadow/R01/early-v6-build-1.log`. The cumulative v6 source index is [source-change-index-v6.json](source-change-index-v6.json:1); the v5 source-change index remains retained historical evidence ([source-change-index-v5.json](source-change-index-v5.json:1)).

The v5 native correction and nine native suites are retained historical evidence for unchanged native pins. They remain bounded native/adapter results and do not establish v6 Player acceptance ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)). The v6 verifier correction changes only the early verifier and its tests, with no native or managed runtime source change. Its review passed with no findings, and the full Python suite passed 443 tests with zero skips in 63.044 seconds ([early-v6-verifier-correction-review.json](early-v6-verifier-correction-review.json:1), [early-v6-python-validation.json](early-v6-python-validation.json:1)).

The supplemental v5 P01 process (PID 47561) passed its native/managed raw checks and exited 0, but its original strict producer failed on a globally empty candidate first-use-history assertion. The selected `Internal` use and unchanged `Extensibility` sequence 1 / `Contracts` sequence 2 are legitimate nonclosure AOT dependency uses, as documented by the M07 boundary ([early-v5-p01-diagnostic.json](early-v5-p01-diagnostic.json:35), [M07-report.md](../../M07/M07-report.md:78)). The v6 closure-aware verifier correction does not retroactively accept that failed receipt. First-use history is not continuous user-code exclusion evidence; native guard tests and staging policy establish that separate boundary.

The retained v5 native scope is recorded as `PassedNativeScope`: nine hash-bound suites covering M03 (94,707 identity, 30 name, 25 facade, 15 lookup, 33 OFF), M04 (53 total, 15 reference identity, 22 syntax, one million lookups, zero allocations, 373,503 microseconds), M05 (616 core, 35 reflection, 219 identity, 34 syntax), M06 (824 and 20 syntax), startup 168, contention 545, transaction 131, budget 2,684, and recovery 498. The retained gateway has all nine inputs matching and remains retained execution. The helper compiler binder preserves the original missing-compiler-hash and direct-backend-SDK failed attempts. Native scope passes within its explicit adapter limits; it does not prove Player metadata initialization or publication ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)).

## Required completion

- **Fresh v6 Player pairing and strict matrices — Pending.** The v5 ON/OFF pair, fixture lifetime, deterministic replay, and 11-mode result are retained historical evidence. Its strict verdict is `PassedBoundedProfile`, with independent early-runtime review passed; it is diagnostic-only and does not bind v6 or accept R01 ([early-v5-strict-matrix.json](early-v5-strict-matrix.json:1), [early-v5-stage-source-review.json](early-v5-stage-source-review.json:1)). Fresh v6 installation/build pairing and all v6 runtime claims remain pending; the strict 11-mode verdict and 14-mode M07 aggregate are required.
- **Q04/S03 failure recovery — Fresh v6 evidence pending.** The v5 PID 47041 and PID 47045 receipts are historical evidence of the required Validate 13 and Commit 19 dispositions. Capture and bind fresh v6 failure receipts; the v5 native correction remains supporting evidence.
- **NativeScript witness — Fresh v6 trace pending.** The retained v5 bounded trace passed with PID 47101/TID 15077444, seven events, expected UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B`, non-null class return before Configure, and natural exit 1 ([early-v5-native-script-trace.json](early-v5-native-script-trace.json:1)). Capture and bind the fresh v6 trace to the current executable, UUID, capsule, PID/TID, non-null class return, ordering, and exit; it is not whole R01 acceptance.
- **Native regression scope — Completed bounded historical scope.** The nine retained v5 native suites pass with exact metrics in [early-v5-native-regressions.json](early-v5-native-regressions.json:1). Q05’s production allocator/`g_MetadataLock` contention evidence remains native-only and is not concurrent Player Configure coverage. The retained gateway and helper compiler failed attempts remain explicitly labeled.
- **Installed/generated provenance — Fresh v6 audit pending.** The v5 post-build audit is historical. Verify fresh v6 immutable ON/OFF copies and generated bindings after the v6 build; do not carry v5 generated hashes into current acceptance.
- **Final evidence package — Pending.** Bind every result to TestId, four-repository pins, ABI/encoding/capability identity, target/compiler, input/resource hashes, native library, process or device, raw log, and assertions. Preserve all historical receipts and label their pins.
- **Independent R01 code review — Source scope passed; evidence acceptance pending.** The independent v5 stage source review passed with no findings and explicitly remains source-scope evidence, not milestone acceptance ([early-v5-stage-source-review.json](early-v5-stage-source-review.json:1)). The human H1 review is required only after R01B and cannot be replaced by agent review ([HUMAN_REVIEW_GATES.md](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md:12)).

## S02 scope clarification

Normative S02 is “Stage input correctable rejection”: correct state/error followed by legal Abort and permitted recovery ([validation-matrix.md](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md:71)). The v4 R01 Mismatch mode is historical evidence for this boundary. Its one-byte Stage mismatch, unchanged cursor, expected error, and Abort must be bound in the final strict v6 early aggregate.

The exact-set admission checks in `R01EarlyStartup.ValidateCapsule` and `M07R01Probe.RequireSet` are pre-Configure validation. Existing M03 Player probes cover duplicate Stage, malformed-input rejection followed by valid retry, invalid Configure arguments/state, and bounded concurrent ordinary reads (`M03TransactionProbe.cs:158-180,190-198,280-302,680-741`). Those retained M03 cases are historical unless the affected M03-M07 regression gate requires fresh v6 Player receipts. No separate concurrent Configure test is required by S02, and Q05 native contention must not be relabeled as one.

## Capacity and target boundary

The v5 Editor evidence is historical: it includes a positive five-member closure, fixture/replay and lifetime preservation with 379 sealed files unchanged, and an exactly 64 MiB padded assembly rejected before publication with `MetadataCapacityExceeded` ([early-v5-editor-validation.json](early-v5-editor-validation.json:1)). Fresh v6 Editor fixture/replay/lifetime/capacity evidence is required and does not prove the user target of 65,536 assemblies. The approved target makes R01B mandatory; allocation domain, DLL size distribution, and headroom remain to be declared and measured. Suggested 100/300/1000 pressure tiers are diagnostic observations, not product closure criteria.

## Gate disposition

R01 remains unaccepted. After R01 evidence and review, execute required R01B for the 65,536 target, then stop at H1. Do not enter R02. `H1Passed=false` and `mayEnterR02=false` remain the current status ([current-status.json](../current-status.json:14)).

This checklist is complete only when fresh v6 installation/build provenance, strict 11-mode verdict, 14-mode M07 aggregate, Editor fixture/replay/lifetime/capacity evidence, NativeScript trace, unchanged-native-input audit, final hash-bound evidence package/review, and R01 evidence decision are recorded. v5 evidence is preserved as historical with explicit limits. The human H1 review follows required R01B completion. No historical evidence is deleted or overwritten.
