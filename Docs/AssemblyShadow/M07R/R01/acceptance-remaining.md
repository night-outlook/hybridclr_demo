# R01 Remaining Acceptance

Status: **Active / Unaccepted**. This is the current v5 checklist for R01. It supplements the normative plan and validation matrix; it cannot advance H1 or authorize R02.

## Current source and evidence boundary

The v5 executable pairing is:

```text
hybridclr       b22fa3d92223645c32663e4a2157eaadf8ea495e
hybridclr_unity b649c499385ea68490a0f652a98b732e060aeb89
il2cpp_plus     7967b8c7043904fcae130b294defd5ce7aa897c4
hybridclr_demo  c2c908c5a11ce65aabb0da75b512923f709277c1
runtime ABI     46814a65339ab321eb2c35ac2b8edd9ff180ce60039a13d650d4bf3f4f3bcc00
```

The v5 installation verification is repeatable at 945 source files and 947 installed files, with the demo source verified and receipt SHA-256 `32d9d71093c2aeef028bd9fd48088c2bf9b837493eb07453d2d989a5488ee045` (`_temp/AssemblyShadow/R01/early-v5-installed-verification-1.json`). The v5 source-change index is [source-change-index-v5.json](source-change-index-v5.json:1).

The v5 native correction review passed 131 checks, including 22 new checks, with 1,069 unchanged source inputs. Three native files were corrected; the receipt covers the actual staging error carrier and exception formatter. It does not cover metadata initialization, publication, or the Player boundary ([early-v5-source-correction-review.json](early-v5-source-correction-review.json:48)).

The authoritative v5 native scope is now `PassedNativeScope`: nine fresh hash-bound suites covering M03 (94,707 identity, 30 name, 25 facade, 15 lookup, 33 OFF), M04 (53 total, 15 reference identity, 22 syntax, one million lookups, zero allocations, 373,503 microseconds), M05 (616 core, 35 reflection, 219 identity, 34 syntax), M06 (824 and 20 syntax), startup 168, contention 545, transaction 131, budget 2,684, and recovery 498. The retained gateway has all nine inputs matching and remains retained execution. The helper compiler binder preserves the original missing-compiler-hash and direct-backend-SDK failed attempts. Native scope passes within its explicit adapter limits; it does not prove Player metadata initialization or publication ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)).

## Required completion

- **Fresh Player pairing and strict matrices — Pending.** The v5 ON/OFF pair, fixture lifetime, and deterministic replay now pass ([early-v5-player-build-pair-checkpoint.json](early-v5-player-build-pair-checkpoint.json:1)). Complete the current-pair strict 11 early modes plus 13 M07 ON resource modes and OFF. The v4 matrix remains diagnostic history: 9/11 strict-passed, while MetadataFailure and InitializerFailure failed strict verification ([early-v4-matrix-diagnostic.json](early-v4-matrix-diagnostic.json:220)).
- **Q04/S03 failure recovery — Pending.** Re-run the corrected Player failure paths and record the real staged failure state, retained budget, no publication, legal/illegal Abort behavior, and restart disposition. The 131-check native correction is supporting evidence only.
- **NativeScript witness — Pending actual v5 trace.** The v4 bounded LLDB run captured five public IL2CPP API events, a non-null class return, and return-before-Configure ordering. A fresh v5 ON debug capture is prepared with build GUID `a5b484a6772e4c90a24dd29216022630` and native UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B` (`_temp/AssemblyShadow/R01/early-v5-on-native-wrappers/native-debug-artifacts.json`); capture and bind the actual v5 trace before treating the witness as current ([early-v4-native-script-trace.json](early-v4-native-script-trace.json:1)).
- **Native regression scope — Completed bounded scope.** The nine fresh v5 native suites pass with exact metrics in [early-v5-native-regressions.json](early-v5-native-regressions.json:1). Q05’s production allocator/`g_MetadataLock` contention evidence remains native-only and is not concurrent Player Configure coverage. The retained gateway and helper compiler failed attempts remain explicitly labeled.
- **Installed/generated provenance — Completed for v5 installation; final package binding pending.** The repeatable v5 check records 945 source files, 947 installed files, and `demoSourceVerified=true`; the pair checkpoint records workflow and replay Passed. Complete the final generated-artifact binding after Player evidence without treating mutable build artifacts as source evidence.
- **Final evidence package — Pending.** Bind every result to TestId, four-repository pins, ABI/encoding/capability identity, target/compiler, input/resource hashes, native library, process or device, raw log, and assertions. Preserve all historical receipts and label their pins.
- **Independent R01 code review — Required.** An independent agent code review may inspect the design, plan, four repositories, tests, Player/negative evidence, regressions, limitations, performance, and release risk for the R01 stage. This is separate from the human H1 review; the H1 human review is required only after R01B and cannot be replaced by agent review ([HUMAN_REVIEW_GATES.md](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md:12)).

## S02 scope clarification

Normative S02 is “Stage input correctable rejection”: correct state/error followed by legal Abort and permitted recovery ([validation-matrix.md](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md:71)). The v4 R01 Mismatch mode is the Player witness for this boundary. Its one-byte Stage mismatch, unchanged cursor, expected error, and Abort belong in the final strict v5 early aggregate after current-pair binding.

The exact-set admission checks in `R01EarlyStartup.ValidateCapsule` and `M07R01Probe.RequireSet` are pre-Configure validation. Existing M03 Player probes cover duplicate Stage, malformed-input rejection followed by valid retry, invalid Configure arguments/state, and bounded concurrent ordinary reads (`M03TransactionProbe.cs:158-180,190-198,280-302,680-741`). Those retained M03 cases are historical unless the affected M03-M07 regression gate requires fresh v5 Player receipts. No separate concurrent Configure test is required by S02, and Q05 native contention must not be relabeled as one.

## Capacity and target boundary

The v5 Editor evidence includes a positive five-member closure, fixture/replay and lifetime preservation with 379 sealed files unchanged, and an exactly 64 MiB padded assembly rejected before publication with `MetadataCapacityExceeded` ([early-v5-editor-validation.json](early-v5-editor-validation.json:1)). This does not prove the user target of 65,536 assemblies. The approved target makes R01B mandatory; allocation domain, DLL size distribution, and headroom remain to be declared and measured. Suggested 100/300/1000 pressure tiers are diagnostic observations, not product closure criteria.

## Gate disposition

R01 remains unaccepted. After R01 evidence and review, execute required R01B for the 65,536 target, then stop at H1. Do not enter R02. `H1Passed=false` and `mayEnterR02=false` remain the current status ([current-status.json](../current-status.json:14)).

This checklist is complete only when the current v5 Player matrices, corrected failure recovery, actual v5 NativeScript trace, final hash-bound package, and independent R01 code-review decision are recorded. The v5 native scope and installation provenance are complete within their explicit limits. The human H1 review follows required R01B completion. No historical evidence is deleted or overwritten.
