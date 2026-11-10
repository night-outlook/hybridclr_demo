# R03 B2 — exact-source full-field readiness gate (Primary B2-0)

Date: 2026-11-10 UTC. Owner: Primary Implementation. **This is a source-admission tool plus tests, not an implemented native V2 diagnostic producer.**

## 1. Scope, sources and provenance

The prior [oneuse-12 Local result](../../local-validation-native-b1-20261110-oneuse-12/README.md) remains a **focused 19/19 B1 PASS** at execution source `hybridclr_demo@2d690bb2f7234ddcbee339f9da7125d687f5ed45`, native `il2cpp_plus@8aa8d09319a89b55b2496bcc2c69ccc69cb57be9`. Its later evidence publication `9c210801c8da1e8371a09c25e0ef708a6d130fc3` is not a new execution source. Product and earlier evidence are immutable.

The authoritative R03BoundedDiagnosticsV2 reference at Git blob `0866b07f758a20284d2a5d5d933b2be577b20b50` maps slot **14** to `finalDiagnostics` and slot **15** to `finalExecutionDiagnostics`; these are complete legacy-compatible source fields, not the bounded `FirstErrorV2` B1 code/reason.

Primary inspected and pinned exactly **eight current native fork source blobs** at `il2cpp_plus@8aa8d09319a89b55b2496bcc2c69ccc69cb57be9`: `AssemblyShadow.cpp/.h`, `AssemblyShadowBoundedGeneralLiveSource.inl`, `AssemblyShadowBoundedExecutionEmptyLiveSource.inl`, `AssemblyShadowTypeKey.cpp`, `AssemblyShadowMetadataLifetime.h`, `AssemblyShadowFrozenExecutionRecord.h` and `AssemblyShadowOwnedPhysicalNamesSource.inl`. Their reviewed Git blobs are in `Tools/AssemblyShadow/R03IR/bounded_v2/b2_source_readiness.py`; that file also authenticates the original reference blob.

## 2. What the source actually establishes

| Source domain | Existing native producer | Proven limited behavior | Missing acceptance requirement |
| --- | --- | --- | --- |
| B1 first native event | `FirstFailureV2Status` / `TryReadFirstFailureV2` | Immutable Empty/Frozen/Invalid first-error facts; actual macOS Player B1 evidence exists | Does **not** contain full general/execution field14/15 |
| General final diagnostics | `TryCaptureBoundedGeneralLive` | Owned bounded component sources, initial-session metadata Reader, three fence samples, source failure invalidates output | No accepted terminal-phase/teardown/whole-VM atomicity guarantee; source-integration and exact independent legacy parity remain unproven |
| Execution final diagnostics | `TryCaptureBoundedEmptyExecutionLive` | Real R02 counters and zero-class output under initial-session Reader; fails closed when `before.count!=0` | Nonempty observed classes, canonical execution TypeKeys, physical class provenance, complete per-class state rows and postterminal semantic parity |
| Legacy execution path | `GetExecutionDiagnosticsJson` | Existing complete legacy formatting from a class inventory | Allocating `std::ostringstream` / `FormatMetadataOnly` / `std::string`, metadata pointer dereferences after the original observation lock; cannot silently use as no-allocation terminal V2 producer |
| Owned physical names | `TryCaptureOwnedObservedPhysicalNames` | Matched physical enumerator callback and owned display bytes / shape bits | Display names are explicitly **not** canonical execution TypeKeys |
| Metadata lifetime | `assembly_shadow_metadata_lifetime::Gate::Reader` | Admission for the initial source epoch and teardown reader drain | Stored physical class pointer origin and coordinated full shutdown/GC epoch remain unproved |

The B2 full field completeness question is **separate** from the already resolved C++11 host-compiler incompatibility. [B2 C++11 remediation](B2_CPP11_COMPATIBILITY_REMEDIATION.md) verifies 376 source-bound codec/POSIX host tests, not real final field capture.

## 3. Primary-owned source-admission code and tests

New source:
- `Tools/AssemblyShadow/R03IR/bounded_v2/b2_source_readiness.py` checks exact `HEAD` for demo and native, clean tracked worktrees, original blob for each of the eight native source files and the reference, and source-bound assertions (fenced general, nonempty execution hard rejection, metadata lifetime Reader, legacy allocator path, physical display-name warning).
- It emits a deterministic `R03B2ExactVMSourceReadinessAudit` JSON receipt with `sourceAudit=PassedPinnedStructuralInspection` **but** `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, and every runtime/R03/H2/Human Gate flag false. A source drift, wrong branch source blob, changed field schema, unexpected admission method or missing file returns code 2. The script **does not** declare that live field14/15 producers exist.
- `test_b2_source_readiness.py` implements **12** source/negative tests: canonical field order, expected blocked classification, B1 cannot promote full fields, wrong/missing schema, absent file, original allocating getter drift, nonempty class rejection removed, metadata Reader removed, physical display name promoted to TypeKey, deleted source-fence marker, Git blob drift and symlink/missing tree.
- `.github/workflows/r03-ir-b2-exact-full-field-source-readiness.yml` performs sparse GitHub checkouts of **two** exact repositories and tests on macOS-15 and Ubuntu-24.04, checks 12/12 tests, confirms `verifiedNativeFiles=8`, and **requires** that readiness remain false. It is NOT a full four-repository product admission or a Unity Player test.

First full-source + negative-test CI: [run 42793524378](https://github.com/night-outlook/hybridclr_demo/actions/runs/42793524378) at `hybridclr_demo@353c6f0f2705f1fd0b677fb6404da697bdf6b628`. **2/2 source-audit jobs Passed**, each with 12 unit tests and a real native-fork checkout inspection. The report explicitly contained `handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. This is a **correct, independently evidenced BLOCK**, not a producer-readiness success.

## 4. Selected implementation path and stop condition

**Preserve the original full-field schema.** Do not replace slot14/15 with B1-only text, zero-class-only data or a fabricated null, and do not weaken the file/receipt or pure-host tests.

Next **Primary Implementation** source tasks, in order:

1. Complete bounded live execution **nonempty class** producer with class-pointer source-epoch provenance and canonical, physically owned execution TypeKey bytes; preserve original V1 execution class ordering, counters, flags and pointer-detail schema. Do not dereference borrowed class pointers after metadata Reader or original matching locks exit.
2. Prove the full general bounded capture matches the original `GetDiagnosticsJson` across baseline/no-candidate/active/error19/guard15 and actual multi-assembly diagnostics scenarios, including source-fence rejection under concurrency and terminal readability. Do not interpret equal counters as a VM-wide epoch.
3. Cross-check **both complete fields** as immutable byte slices, with original JSON semantic parity and effective 4 MiB aggregate/frame budgeting. Bind real source/output lifetime to the existing V2 encoder/PosixTransaction, not a fresh getter after terminal.
4. Independently review exact implementation and adversarial tests. Only after B2 source and CI completion, prepare a NEW one-use Local Validation handoff with four pushed source pins, all original-S/SDK/capacity/custody/CI prerequisites, fresh absent roots and one real Unity build/Player suite.

The current code cannot satisfy item 1. Therefore **B2-0 is not closed as a source-completeness milestone; implementation stops before B2-1 runtime activation**. Human Review Gate remains closed. Original R03 independent full-stage review FAIL, High IR-R03-01/02 and all broader acceptance booleans remain unchanged. PureInterpreter disabled. [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) must remain **CLOSED / NO EXECUTION**.
