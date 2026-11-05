# R03 initializer one-use — Primary source review and evidence boundary

Date: 2026-11-05 UTC. Review role: Primary Implementation (NOT independent
Human Review Gate or Local empirical acceptance). Scope: new test-only
runner + host tests + conditional handoff. Do not alter original S/K/I/J
results or run H2/M08A/X02.

## Actual inspected code and invariants

1. The existing deterministic `InitializerNativeTargetFixtures.cs` emits
   two separate Methods DLLs; control returns from its module initializer,
   failure throws the exact sentinel after the actual native callback. They
   are not old S or K DLLs. The two expected full SHA-256/MVID pairs are
   checked as external constants again immediately before launching.
2. `R03InitializerPreparedProbe.cpp` binds only during state 5, pins an
   actual interpreter object, checks pre-return counters/mask and uses
   prevalidated offsets for read-only field observation after commit.
   `R03InitializerObservationWriter.cpp` performs exclusive open, bounded
   exact native schema, full write/fsync/close; it cannot grant R03 approval.
3. `run_initializer_local.py` gates source, host, original S and machine
   admissions; it reuses all ten native owner host suites and then new
   observer/writer host compiles, deterministic source preparation and
   synthetic negative contracts. The old five-Player runner, native VM,
   HybridCLR interpreter and package sources are not edited.
4. The new override for `verify_build` is necessary: the inherited method
   pins only the *old* R03 native overlay. The override checks the whole
   existing BuildReport/source/install/executable chain against the new
   composite SHA rather than weakening the historical owner check.
5. Both new initializer cases require separate real Player command
   ownership, request/fixture/launch PID matching, exact native V1 raw
   field/canary/cardinality checks and no runtime acceptance flags.
   One failure retains request/raw/log/command evidence rather than a
   fabricated success or retry.
6. Original nine-part S archive, 90-cell ledger, 59 historical process joins,
   generated C++ table
   sources and archived NativeOn/NativeOff Mach-O defined-symbol checks
   are independent read-only evidence stages. They **cannot** establish
   original compiler source-to-object or executable process closure.

## Observed host-only testing

Source implementation first pushed at demo
`81597899d1ba0f8d00e3fd5dfd8531f8fab40fe9`.
GitHub Actions
`https://github.com/night-outlook/hybridclr_demo/actions/runs/42002234697`
completed **success** on macOS 14 and Ubuntu 24.04. Both jobs passed:
Python source compilation, actual new runner's synthetic positive/negative
host contracts, source preparation/schema tests, and C++11 compilation and
native host fakes for the real initializer observer and writer.
The subsequent ten-host integration revision and final documentation
need their own fresh exact-HEAD CI success before any Local invocation.
Earlier six initializer generation/writer/observer/managed API/source
workflows are complementary source evidence, not real Unity Player runs.

## Non-tested/non-promotable evidence

Neither this Primary session nor its Actions jobs executed Unity,
a native IL2CPP full build, the composite overlay in an actual
GameAssembly, a new real initializer control/failure Player, or the
captured-baseline generic guard error 15. The full native
NativePreopenedSnapshotV2 and genuine first-failure/general diagnostic
producer remain absent. Original-S compiler/object/link/Player closure,
unreconciled capture omissions, managed shutdown, whole-VM epoch,
GC/RSS, full regression/performance and RC/P/E obligations remain open.
The independent October 8 R03 FAIL and both High findings remain open.

## Local decision

Run only the distinct single-use conditional initializer batch from
`Handoff/WEB_TO_LOCAL.md` after explicit exact-source dual-OS CI,
Git/SDK/original-S preservation and two >=25.0 GiB capacity samples.
Any first real build or process discrepancy requires returned empirical
raw evidence and a new Primary design/code correction; Local must not
undertake cross-module source changes or independently approve R03.
Classification before that run: **source/host prepared; real Local NotRun**.
`R03Accepted=false`; `H2Passed=false`;
`ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`.
