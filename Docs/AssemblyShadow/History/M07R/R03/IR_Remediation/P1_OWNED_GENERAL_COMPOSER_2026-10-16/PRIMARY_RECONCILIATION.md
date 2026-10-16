# R03 P1 — Owned bounded general JSON composer

**Disposition: implementation and host source checks Passed. Official Unity SDK validation for the new native revision NotRun. Runtime acceptance false.**

## Source design

Previous P1 increments individually owned transaction inventory, bounded first-use records, physical assembly enumeration, ordinary classes and a frozen general JSON serializer. The new **AssemblyShadowBoundedGeneralComposer.h** composes only already-completed owned captures into a complete frozen general V1 JSON document. It does not acquire a VM/metadata/transaction mutex, look up Il2CppClass pointers, call managed code, or touch files.

The stage order matches the original AssemblyShadowDiagnostics::Serialize(ShadowDiagnosticSnapshot): startup names, closure load order, stable AOT names, commit names, assembly flags, events, baseline uses, ordinary assemblies and ordinary classes. Startup names are borrowed only during composition; all other input text was previously copied into fixed-size source arenas. Present first-use rows must equal the source PresentCount. ActiveGeneration values from physical/class capture must match; a mismatch rejects the complete result. Matching values do **not** establish a global VM epoch or eliminate ABA observations.

Input/output source objects must be preallocated while healthy. All five owned structures have compile-time combined object bounds at most 16 MiB, but this is not measured process RSS or GC. The frozen general JSON field retains its 3,932,160-byte bound, separate from the total authenticated V2 wire/transport budget and the unchanged V1 per-slot bound. Failure never returns partial success: a new additive FrozenGeneralCapture.RejectInvalidSource permanently invalidates any partially populated output. The composer receipt always reports coherentVmEpochProven=false and runtimeAcceptance=false, even on a host success.

**No live getter was replaced. The new composer and first-use reader remain inactive and have no Player entrypoint.** This is progress in P1 source composition, not completed P1 VM acquisition, authenticated P2 transport or engine E0/E1 integration.

## Code and regression scope

Native changes:
- New libil2cpp/vm/AssemblyShadowBoundedGeneralComposer.h, using actual production Capture APIs.
- Add one fail-closed method to AssemblyShadowFrozenGeneralCapture.h.
- Add tools/r03/diagnostic_stream/bounded_general_composer_fixture.cpp and run_bounded_general_composer.py.
- Add .github/workflows/r03-p1-bounded-general-composer.yml.

The fixture constructs the **actual production bounded captures**, independently constructs the existing ShadowDiagnosticSnapshot and compares the original V1 serializer output byte-for-byte (including embedded NUL). It covers copied text ownership, no new C++ allocations during composition after prewarm, absent/incomplete sources, generation mismatch, startup bounds, invalid borrowed strings, total output overflow, invalid UTF-8, single-use output, and explicit absence of global-epoch/runtime claims. It records 11 unique groups per strict and sanitized profile.

[Native CI run 38885246083](https://github.com/night-outlook/il2cpp_plus/actions/runs/38885246083) **Passed 3/3 jobs**: macOS 15 Apple Clang, Ubuntu 24.04 Clang, Ubuntu 24.04 GCC. All profiles had 11/11 case groups, four successful compile/run receipts per job, and 0 allocations after prewarm. The three original artifact digests and all **51/51 manifest-declared files** were independently SHA-256/size verified (macOS19, Linux GCC16, Linux Clang16). These are real product headers and original serializer compiled against owned host captures, but **not** Unity SDK or Player execution. See [machine evidence](EVIDENCE.json).

Demo tooling now aggregates **11** separately receipted source and SDK components, adding the owned-general test. The candidate official Unity2022.3.62f2 arm64 syntax matrix includes a new standalone composer compilation probe, expanding 14 x five =70 to **15 x five =75**; historical non-candidate 12 x five =60 remains unchanged. Updated the CLI/managed receipt regressions for the 11/75 scope. Old Local evidence remains pinned to its original 10/70-source versions. The new 75 matrix is assigned to Local only after complete publication and verified handoff.

## Remaining P1/P2/E0/E1 gates

P1 is **Incomplete**: independently sealed source captures are not necessarily one coherent live VM snapshot, the original GetDiagnosticsJson/GetExecutionDiagnosticsJson still allocate, and type-key enumeration, R02 counters, class pointer provenance, GC/RSS peak, metadata shutdown, lock ordering and safe native terminal scheduling are not qualified. A matching physical/class generation alone is not a whole-VM epoch proof.

P2 native/C# authenticated V2 artifact + unchanged semantic verifier remains **NotIntegrated**. E0 Unity2022.3.62f2 StandaloneOSX engine owner capability is **Blocked/Unavailable**; E1 scheduling, GC/finalizer maintenance, callback draining and restart remains **BlockedByE0**. A 75-unit SDK syntax PASS would not prove linking or Player behavior.

Immutable historical records: 20261016-f598 PASS (10/10), 20261016-0620 PASS (10/10), 20261016-0a0b FAIL (9/10) with its original false SDK aggregate; SNAP-01 FAIL (14/18), original slot14 exceeded 262144 bytes and engine had 51213 uncapped reports in 500ms with exit71. Historical R02 whole-file identity FAIL, other N/M/K/I/E FAIL, strict original S custody Blocked and full-stage independent R03 review FAIL/re-review NotRun remain unchanged.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled. No Unity Player or Human Review Gate authorized.
