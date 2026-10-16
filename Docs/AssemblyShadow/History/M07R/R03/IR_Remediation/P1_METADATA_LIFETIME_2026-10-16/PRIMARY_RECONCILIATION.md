# R03 P1 — Native metadata lifetime admission, source-bound host evidence, and one-shot Local SDK preflight

**Owner:** Primary Implementation. **Branch:** `codex/assembly-shadow-r01b-h1`. This document is a new Primary source increment, not a replacement for historical failures, evidence, Local reports or Human Review Gate findings.

## Source and problem

At native source base `il2cpp_plus@2db707eb3021516c2cef962b3d294b4d047e4ef9`, the bounded ordinary-class and physical-assembly readers copied complete V1 names/flags into owned preallocated buffers under `g_MetadataLock`/`s_assemblyLock`. Those locks alone did **not** guarantee that `Runtime::Shutdown` could not reach `MetadataAllocCleanup`. The old general/execution getters retain separate pointer/metadata/heap lifetime problems and remain unchanged in this increment.

Primary authored a **new, initially closed, shared process-level metadata read gate** and integrated it with the real native Runtime lifecycle:
- `libil2cpp/vm/AssemblyShadowMetadataLifetime.h`: 31-bit fixed active-reader count plus a closed bit in an atomic word, CAS admission, RAII release, close-before-drain, reopen only with no active readers. No per-ticket allocation. The shutdown drain uses `std::this_thread::yield()` and **has no bounded latency or proven deadlock freedom**.
- `libil2cpp/vm/Runtime.cpp`: exactly one `g_MetadataLifetimeGate`; opens after the complete initialized runtime tail and before `AssemblyShadowStartup::MarkCoreReady`; final `Shutdown` closes and waits for readers **after `FireProcessExitEvent` but before `Thread::AbortAllThreads`, `MetadataCache::Clear`, and `MetadataAllocCleanup`**. The code is conditional on `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW`.
- `libil2cpp/vm/AssemblyShadowVisibility.cpp`, `Assembly.cpp`: both additive bounded readers acquire a read ticket **before** their respective metadata/assembly mutexes. Rejected callers record the new `OwnerUnavailable` error and cannot seal partial data. Original `CollectOrdinaryClasses`, `CaptureShadowEnumeration`, `GetDiagnosticsJson`, and `GetExecutionDiagnosticsJson` retain historical behavior.
- Both bounded result headers, source-bound fixtures and runners were updated; a concurrency/restart native test, exact source-order checker, and three-platform CI workflow were added.

**Native source anchor:** `il2cpp_plus@0a0b70156e75d450d75d0bcfd9132843b8abbbb0`.

## Evidence and what it actually proves

- [Metadata admission host CI 38847888461](https://github.com/night-outlook/il2cpp_plus/actions/runs/38847888461): 3/3 jobs Passed across macOS Apple Clang, Linux Clang and GCC, strict C++17 and ASan/UBSan profiles. The actual production header was compiled; the real Runtime method bodies were checked for source ordering but **not compiled with installed Unity SDK**.
- [Bounded class host CI 38847710731](https://github.com/night-outlook/il2cpp_plus/actions/runs/38847710731): 3/3 source-bound actual callback/method fixture jobs Passed with explicit metadata mocks and immutable original/current/staged JSON parity. The new closed-gate refusal is exercised. No real class-iterator allocation timing or real Unity metadata lifetime is proven.
- [Physical assembly host CI 38847715239](https://github.com/night-outlook/il2cpp_plus/actions/runs/38847715239): 3/3 source-bound actual native assembly method jobs Passed with registry mocks and original/current/staged V1 parity. The new closed-gate refusal is exercised. No global VM epoch is proven.
- Earlier candidate runs that failed due source-gate/test-harness mistakes remain FAILED. These three success runs verify their respective **later exact source** only. The existing serializer, frozen V2, native file transport and Local historical host evidence retain their original scope and verdicts.
- The Demo adds `Tools/AssemblyShadow/R03/native_validation.py --candidate-native-sha <full SHA>`, extending official installed Unity syntax-only validation from historical `12 x 5 = 60` to `14 x 5 = 70` units by including `Assembly.cpp` and `AssemblyShadowVisibility.cpp`. This explicit opt-in mode checks the native candidate checkout SHA and records it, **without modifying** `Tools/AssemblyShadow/R03/source-pins.json` (still the last actually executed Local host tuple).
- `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py` is a **single one-shot aggregate** for ten host/SDK components, source preservation and exact four-repo commits. Its own Mac/Linux read-only CLI/negative tests are covered by `r03-p1-metadata-preflight-contract.yml`. No newly generated official Unity SDK compile result or Player evidence is claimed here.

## Why P1 is still incomplete

The gate is a **conditional metadata-lifetime admission mechanism**, not a globally coherent snapshot or a Unity engine scheduler boundary. Specifically:
1. Native `Runtime::Shutdown` can wait indefinitely for a reader; a reader re-entering shutdown or an incompatible lock order may deadlock. The gate has no scheduler-owned handshake, source proved thread quiescence or worst-case wait bound.
2. The original general/execution getters still perform heap allocation, hold pointers outside an admitted ticket and may format type keys through unbounded recursive metadata acquisition; no single frozen field14+15/R02 VM epoch or demonstrated peak RSS/GC bound exists. Source-level fixed 8192/4096 capacities are not a proof of complete real capture.
3. The supplied host fixtures compile extracted native readers against explicit mocks, not the complete native `Runtime.cpp`/Unity headers. The 70-unit official syntax gate, Editor, Player, and actual shutdown/GC/finalizer scheduling are **NotRun** pending Local. A passing 70-unit syntax gate would still not prove full link/runtime or deadlock freedom.
4. P2 real native/C# authenticated V2 artifact/envelope emission and original semantic verifier integration remains **NotIntegrated**. E0 Unity2022.3.62f2 StandaloneOSX source/vendor engine-owner safe point and E1 authentic maintenance/drain/restart remain **Blocked**. No invented native PlayerLoop owner pointer, reporting cap, finalizer suppression, early exit or altered historical semantic predicates is allowed.
5. No historical SNAP-01/N/M/K/I/E, original strict S custody, or independent R03 review outcome can be promoted by these tests.

## Review risks and next Primary work

- Audit admission acquisition on every eventual metadata/class pointer reader, with explicit thread lock order `s_InitLock` / `g_MetadataLock` / `s_assemblyLock` / transaction / usage / GC, and prove no closing thread needs a held reader. If official 70-unit syntax fails, fix **in Primary** after Local factual report; do not ask Local to design a workaround.
- Move actual general and execution VM capture to an admitted, fully bounded source owner with separately reviewed full type-key formatting, R02 generation cohesion, source mutation refusal, memory budget and failure precedence; independently close source completeness and allocation. Do not use the new gate to justify the old getters.
- Integrate P2 authenticated complete V2 native/C# emission and original semantic verifier without weakening the original V1 path. Obtain vendor/source E0 capability before native Unity engine disposition and E1.
- Only after all P1/P2/E0/E1/P3 conditions can a new Player batch be authorized. A source/official-SDK-only Local preflight is separately and narrowly authorized in `WEB_TO_LOCAL.md`; **no Unity Editor/Player runtime action is included**.

## Preserved decisions and numerical bounds

Historical SNAP-01 `FAIL/ReturnRequired`: 18 cells, 14 Passed/4 Failed; three ON files zero bytes, original text slot14 exceeded its unchanged 262144 bound (first scanned prefix262145; exact real full length Unavailable); engine 51,213 uncapped reports/500ms, exit71. Original strict S custody Blocked. V2 frames <=65536, diagnostic artifact <=3932160, envelope <=262144, combined encoded <=4194304; no truncation or partial success.

**R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled.** Local's earlier host-only execution verdicts are untouched. No H2/X02/M08A or Human Review Gate.
