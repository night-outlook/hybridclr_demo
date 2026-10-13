# Primary reconciliation — snapshot diagnostics after N

Owner: Primary Implementation. Date: 2026-10-13 UTC. **Decision: one explicitly diagnostic-only SNAP-01 cycle may be admitted under a separate exact-source handoff. Neither oversized diagnostic representation nor terminal engine containment is repaired.** This is not a repaired-runtime acceptance claim.

## Preserved empirical result

N publication `3138ce154b8ad1cbe7fc925522bdfec82a386dd5` remains **FAIL: 18 cells, 14 Passed / 4 Failed**. Three fresh builds, OFF and three Bee observations Passed. Three ON Players exited2 with zero-byte raw after phase220/910; complete semantic proof remains Unavailable. Engine completed **51,283 uncapped reports in500ms**, exit71. Its multiple Runtime::Invoke samples do not establish dominant-method frequencies. All host/compiler/storage/custody/seal successes retain their original bounded classifications. Nothing in this publication modifies LOCAL_VALIDATION.md, RETURN_TO_WEB.md or N's checkpoint.

The earlier downloadable candidate report incorrectly said 15 Passed/4 Failed. That sum was a transcription error; the authoritative original N ledger/report is **14/4 of18**. No historical outcome is corrected or promoted by editing this Primary description.

## Reconciled implementation already published

The canonical source had advanced concurrently to **c5b69990d650293ff2faa6ef7ba712ba2a5147a1** before this continuation. I retained and independently checked that publication rather than overlaying another candidate. It changes the test-only native snapshot writer and supplementary C# emitter, plus host checks/CI. Native IL2CPP+ remains **0f72078711d4786dac2666c9017d952d857dd041**. The later managed round-trip test and documentation do not change these compiled executable bytes.

* The native writer records only its immutable first failure: operation, slot, prior state, bounded scanned length, errno, completed integer/text masks and actual PID. It preserves the strict once-only slot8 contract, all25 integers/16 texts, original262144-byte per-text limit, complete schema, exclusive output and independent I/O checks. Its `[R03SnapshotFailure]` line is diagnostic evidence, not a substitute raw record.
* The actual C# emitter now always attempts strict Seal, even when a preceding store failed. It returns success only when all original stores and Seal succeeded. No missing field or partial snapshot can become Passed.
* No engine scheduling, Runtime::Invoke acceptance, first-cause recovery, reporting CompletedCounter,500ms/1..64 requirement, finalizer policy or business method/class/allocation guard changes are included.

The new read-only classifier `N_SNAPSHOT_PUBLICATION_91b7/checks/classify_snapshot_failure.py` authenticates an original log SHA256 and expected positive PID. It validates the source-defined field/reason/state/masks and retains `runtimeAcceptance=false`. Absence of a line is not proof of a complete raw file; a scanned262145 prefix does not give a full producer length.

## Additional coverage implemented in this continuation

The prior integration mechanically transcribed the C# emitter into C++. The new **test_managed_emitter.py** extracts the exact current Report declaration, four PInvoke declarations and complete EmitNativeReport method and compiles them as actual C#. The exact native writer is compiled into a host shared library. .NET8 executes the unchanged emitter through its real PInvoke marshaller, then compares every declared Report field to the persisted JSON. Test Report values and baseline slot8 seed are explicitly synthetic. This is **not IL2CPP marshalling, Unity execution, real shadow-object GC or terminal-state behavior**.

Thirteen scenarios include type/baseline/OFF shapes, null/text/unicode round-trip, a synthetic Failed result which stays Failed, exact262144-byte UTF8 and over-limit UTF8, duplicate/missing baseline slot8, duplicate integer, repeated Seal, occupied-output preservation and the actual synthetic diagnostic producer's331078-byte JSON. Each platform ran17 compiler/process commands including tool-version records. No C# source transformation into C++ is used by this new test.

[Current CI38406447101](https://github.com/night-outlook/hybridclr_demo/actions/runs/38406447101) at **126626c71f1571ae9a0de9f95a56b485ae9a5267** Passed both macOS14 and Ubuntu24.04: all original18 source/classifier contracts,26 native integration scenarios per strict/sanitized profile, real serializer/coupled controls, and13 actual managed-emitter scenarios. Downloaded artifacts were verified against exact ZIP SHA256 and all **289 declared members /290 total files** on each platform, including each17 command receipt's stdout/stderr hashes and current source blobs. The first new CI run38405747965 passed tests but its upload omitted one hidden generated assembly-attribute source; a new workflow commit includes only the known isolated output's hidden files and the final artifacts are complete. The original incomplete artifact is not relabeled complete.

## Confirmed incompatibility, historical cause still unknown

The actual native GetExecutionDiagnosticsJson body, supplied with explicitly synthetic1024-class metadata, emits **331078 bytes**. This exceeds the unchanged per-text limit **262144 by68934 bytes**. Both the original C++ coupling and new real C#→native round-trip produce precise **slot15 / reason9 / TextExceedsOriginalLimit**, first scanned prefix262145, raw0. That proves a producer–writer capacity incompatibility under a valid-sized synthetic census; it does **not** prove that N's actual failed text was331078 bytes or that slot15 caused its historical failure. N recorded neither.

There is no lossless way to preserve an arbitrarily larger single string inside the unchanged single-slot limit. Increasing the number, silently truncating classes, replacing a full diagnostic with a prefix/hash, or accepting missing execution diagnostics is not authorized. The next design must choose a versioned, fully authenticated representation (for example bounded chunks or a separate complete diagnostic artifact with an exact content binding) rather than disguise omitted information. Such a change must preserve the semantic verifier and explicit total-resource limits and be reviewed by Primary. **It is not delegated to Local or implemented in this diagnostic cycle.** First identify the real store/size/I/O failure without guessing from synthetic data.

## Independent official compiler evidence

[Official SDK CI38400656965](https://github.com/night-outlook/hybridclr_demo/actions/runs/38400656965), sourcec5b/native0f, was re-audited: exact artifact ZIP, all209 manifest files, all56 native command receipts and both streams, **55 successful syntax configurations** (11 units×five profiles), all five managed products and one expected-negative control. The current snapshot overlay hash was matched in each of its five profile records; current Player hash matched its compiler input. **616 repeated vendor Baselib warnings remain retained**, not suppressed or called harmless. Unexported vendor reference bytes remain inventory-bound. Syntax compilation is not native linking, GC behavior or a Player run.

The separate old independent-review host run38400656947 is not globally green: Ubuntu Passed; macOS failed at checkout and its test steps were Skipped. This is not a newly reproduced source defect and is not rewritten as a passing macOS result. New source-bound checks and fresh Local prerequisite suites remain mandatory.

## Why the next handoff is diagnostic-only

N's first failing store/I/O is missing. The now-source-tested native first-error record can close that gap with one fresh controlled real-IL2CPP attempt. [SNAP-01 procedure](SNAP01_PROCEDURE.md) retains the original18-cell/three-build/five-Player core, guards, raw verifier and report-count bound. Any empty raw, semantic failure or >64 engine count remains Failed. A separate diagnostic collection outcome may be EvidenceCollected, but must never override the original cell or batch verdict. No counters are capped, no callbacks are delayed or silently admitted, no finalizers disabled, no early exit substitutes for500ms, and no sixth Player is introduced.

The engine problem remains an architectural integration issue: ordinary engine scheduling continues to invoke terminally denied methods. A safe native terminal/restart boundary must authenticate scheduler ownership and account for required maintenance, not infer that an arbitrary method-name family is safe to bypass. No validated native loop-containment integration exists in the current source. SNAP-01 records unchanged bounds, preserves evidence and returns to Primary; it does not ask Local to design or patch that boundary.

## Publication and acceptance

[Machine-readable audit](EVIDENCE.json) records source hashes, CI artifact identities, coverage and limits. Complete original CI artifacts remain retention-limited; this repository stores exact audit identities, source tests and selected unmodified diagnostics, not copies of vendor/compiler binaries. Connector smoke commit **67cbe3eda8c296a3e65456466544ae86877b0d8d** on `codex/connector-smoke-snapshot-resume-20261013-82bd` was remotely read back. The branch remains because branch deletion is not exposed; it is not an execution source.

N/M/K/I/E remain FAIL; F/H/L prerequisite-blocked; G/J historical scope Passed. Strict S custody remains Blocked (416844 original identities,339367 survivors,77477 missing/four original native roots). Independent R03 full-stage review FAIL/rereviewNotRun; all acceptance flagsfalse; PureInterpreter disabled. Captured-generic/initializer, IR-R03-01, normal finalizer/shutdown and broad legacy/performance remain open. No H2/X02/M08A or automatic Human Review Gate.
