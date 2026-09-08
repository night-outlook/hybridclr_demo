# R00 continuation

Status: implementation under validation; R00 is not accepted and R01 remains closed. This record supplements the immutable initial checkpoint at `08cd976` and does not replace the failed historical Player run.

## Changes under validation

- Added a separate `M07R-R00` Player result boundary for native ON/no patch, P01, P03, and native OFF/no patch. It reuses the existing M07 byte-bound inputs and transactions while retaining the normal fourteen-mode M07 contract.
- Added pure managed allocation, reflection invocation, and closed generic witnesses. Each operation records its first invocation, 100 warmup iterations, 10 repeated iterations, and 10,000 repeated iterations. Allocation rows independently compare constructor increments and checksums. The fresh-return witness runs after measured allocation to preserve the first-allocation boundary.
- Added an explicit preserved `ClosedGeneric<int>` call site to make the native baseline's generic instantiation a build input. This reference is not executed before the measured call; generated native coverage still requires inspection.
- Added two executions each of the existing M06 `new`, `dispatch`, and `generics` witnesses after timing. These are affected-path regressions in the new M07 Player, not a claim that the complete historical M05/M06 milestone matrices were rerun. The M07 fixtures retain the M06 baseline constants; physical type diagnostics distinguish AOT and shadow execution.
- Added R00 process launching and strict result verification. The verifier reopens the M07 input graph, compares captured baseline/Player/Editor pins to all four current source pins (including demo), verifies the installed source, checks native ON/OFF distinctions, and binds results to process exits, PID, build GUID, exact arguments and Player paths.
- Corrected test harness ownership at shutdown: detach and dispose the completed probe, yield another frame to clear `Current`, then perform two bounded collection/wait cycles before quit. Native runtime source is unchanged.

## Shutdown investigation boundary

Historical generated C++ proves `Start.work -> M07Probe.resource -> M07ResourceProbe.work -> RunCore` retained seven AsyncOperation fields until quit. `RunCore.Dispose` was empty. Native disassembly establishes that the original failing instruction dereferenced the null result of `GetPhysicsManager`. The narrow ownership correction received an independent read-only PASS; it does not yet prove prevention of the native shutdown race. Fresh ordinary P05/OFF repetitions, the complete matrix, and debugger ordering evidence remain required. The original SIGSEGV is retained.

## Validation so far

- First Unity compilation exposed an inaccessible private nested transaction field in the new probe. Changed it to an internal, explicitly nonserialized implementation field; the next Configure execution passed.
- Full Python suite: 365 passed, zero skips (`_temp/AssemblyShadow/R00-python-continuation-v1.log`). Subsequent focused verifier checks: nine passed.
- First full Editor suite: 919 of 920 passed. The single failure was an old source-text test requiring the removed `failed.Dispose` alias. Updated that check; actual ownership behavior is exercised by new detach-before-dispose, throwing-dispose, and repeated-cleanup tests.
- Focused M07 Editor suite: 28 passed, zero skips, including the new readiness timestamp test (`EditorTests-c18703ba45b04889ae656404ae421ab8`). Final full rerun: **921 passed, zero failures/skips** (`EditorTests-57b05fb296ee4e4c93c2cfe44cc1b5f8`).
- Independent prebuild review first found P2: readiness capture overwrote the original invocation UTC timestamp. Fixed by capturing it once and testing both observations. Re-review returned PASS. Actual Player behavior and generated code remain unverified.

## Remaining execution

1. Commit the validated demo code/configuration and update its source pin in a separate metadata-only commit.
2. Reinstall the pinned pairing, build a fresh immutable M07 native ON/OFF pair, fixtures and Editor replay, then verify generated generic coverage and source receipts.
3. Execute the four R00 observations, affected execution paths, full M07 matrix, and shutdown repetitions/order diagnosis; run strict verifiers with no skip/incomplete overrides.
4. Append exact hashes, raw evidence, final changed-file inventory and independent R00 acceptance review. Only an accepted R00 permits R01; H1 remains mandatory after R01/R01B.

Performance timing includes reflection call overhead and managed argument boxing where applicable. Allocation batch timing includes one reflection entry into the batch. Readiness means the configured active witness can execute its marker, before resource/scene load. Parent launch-to-readiness timing is separately computed when the Player process-start API is unavailable. Native proof-build, metadata-row-scan and allocation counters remain explicitly unavailable in this unchanged runtime.
