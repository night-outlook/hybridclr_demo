# R03 P1 — first-use class metadata capture, Primary published source review

**Disposition: published additive native source; host CI PASSED 3/3; official new Unity SDK, linked Player and runtime NOT RUN.** The source change is [il2cpp_plus@f598f8da5749e7c09ad5816630ce7e40b3f4ebca](https://github.com/night-outlook/il2cpp_plus/commit/f598f8da5749e7c09ad5816630ce7e40b3f4ebca). Subsequent *CI-workflow-only* terminal integration test corrections resulted in final native HEAD `1e1d152f0e05b8038427c76a9c8a9b4b60998a72`. The original first-use getter, C# emitter and Unity engine boundary remain unchanged and inactive. All prior Local cycles remain consumed.

The GitHub Connector successfully wrote disposable commits and read them back in both affected repositories. It then created all six native source/test/CI blob objects, verified five exact expected target Git blob IDs, constructed one complete source-tree commit and advanced the intended feature branch by expected-HEAD lease. No Local checkout was used to publish code.

## Scope and exact baseline

The narrow objective is to complete class-bearing rows in the existing, inactive `AssemblyShadow::TryCaptureBoundedFirstUses` source reader. It does not activate or replace either legacy diagnostic getter, integrate native/C# V2 emission, implement the engine scheduler, or complete P1.

All canonical repositories use `codex/assembly-shadow-r01b-h1`. Baselines freshly read through the GitHub Connector:

| Repository | Remote baseline commit |
| --- | --- |
| night-outlook/hybridclr_demo | eb482858203ac9322f3f08da38fab7d6877ad586 |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | f71691407bf9af5544d00dd54bff9e2e7eb77307 |

The relevant native files were transcribed from Connector reads and authenticated against the returned Git blob IDs. `SOURCE_BASELINES.json` records eleven exact complete files. The **complete original `AssemblyShadow.cpp`** was fetched from the pinned GitHub revision, its Git blob verified as `0012b9ccadcb8c0bbc2ec5411e206dc733f04eeb`, and every unified-diff hunk matched against its exact original contents. The committed new source Git blob is `b7c99eeaefb77bd7739304214277484d8b2ab261`. A six-file atomic native commit was remotely published; the earlier unpublished materializer and bundle remain historical *working* artifacts, not handoff authority.

Reviewed method SHA-256 (excluding final linefeed): `67fcd9f6660c67c8a60ed610cdc9b3c3cfc06adb01f9805a581e6dd97dd42be2`. The separately published **source commit** is `f598f8da5749e7c09ad5816630ce7e40b3f4ebca`; do not confuse a function digest with a Git revision.

## Concurrent remote dependency update reconciled

The final ref check discovered a remote advance from native `0a0b70156e75d450d75d0bcfd9132843b8abbbb0` to **`f71691407bf9af5544d00dd54bff9e2e7eb77307`** during this session. That commit was not created here. Connector compare reports seven changed metadata-gate/fixture/runner/workflow paths; the first-use source method and all six patch-base paths are unchanged. The incoming gate implementation was read and independently matched to Git blob `d2fe09dd51debbbbc71d67b21347f5d971a3cafd`.

The committed source change is built **on top of f716** and keeps the source-epoch metadata gate unchanged. Its default Reader admits only epoch 1; it deliberately does not replace absent source provenance with a current epoch. The first-use fixture now constructs an independent fresh **mock process** for each Reset after all test threads join. This placement construction is test setup only, never a production/runtime reset operation. A separate test reopens the SAME gate with the SAME retained registry and proves that the default reader refuses before any raw usage or class-name access. The earlier 0a0b gate fails that new reopening assertion, as an expected dependency-control failure.

All four final compiler/profile runs were repeated successfully with the unmodified f716 header; the eight runner tests were repeated too. Earlier host evidence remains preserved and distinguishable. The original source-body class-refusal regression was also rerun and failed at its expected assertion. The six-file candidate patch does not modify or revert any of the seven incoming files. **The prior Local 70-unit SDK PASS covered 0a0b, not f716 or this candidate.** Fresh **source-bound host CI is Passed 3/3** at native source commit f598. The *full* installed Unity SDK, linking, Player, and runtime metadata/shutdown qualification still remain NotRun.

## Confirmed source gap and preserved bytes

At the native baseline, the bounded reader stores `UseRecord::klass` as an opaque token, copies registry names, and deliberately reaches `Seal` without resolving class names. Any present class-bearing row therefore fails `UnverifiedClassMetadata`. See the pinned [source method](https://github.com/night-outlook/il2cpp_plus/blob/0a0b70156e75d450d75d0bcfd9132843b8abbbb0/libil2cpp/vm/AssemblyShadow.cpp#L1476-L1533) and [capture header](https://github.com/night-outlook/il2cpp_plus/blob/0a0b70156e75d450d75d0bcfd9132843b8abbbb0/libil2cpp/vm/AssemblyShadowBoundedFirstUseCapture.h).

The legacy general getter constructs first-use type text as `std::string(use.klass->namespaze) + "." + use.klass->name`. An empty namespace therefore gives `.Class`; it must not be normalized to `Class`. Both empty strings produce `.`. A null namespace/name is not treated as an invented empty string. The detail suffix, kind, candidate order, thread, timestamp and sequence semantics are preserved. See the [legacy first-use formatting block](https://github.com/night-outlook/il2cpp_plus/blob/0a0b70156e75d450d75d0bcfd9132843b8abbbb0/libil2cpp/vm/AssemblyShadow.cpp#L1585-L1604).

## Candidate implementation and lock order

The native method first acquires an RAII Reader from the **existing real** process-global metadata gate. Closed admission rejects with appended `OwnerUnavailable` without touching the source registry or any class. It does not create a second native gate, alter its lifecycle implementation, or enlarge either data capacity.

The sequence is:

1. Hold metadata admission across the complete source operation. Under the first short `UsageLock`, copy raw records and the protected usage generation; never dereference a class or obtain the metadata mutex there.
2. Release `UsageLock`. Copy immutable candidate names and format the exact decimal ` FirstUseSequence=` suffix into the existing arena.
3. Enter a separate `g_MetadataLock` scope. Resolve only pending identities, reading existing `Il2CppClass::namespaze` and `name` and copying the complete physical strings. There is no class materialization, type-key recursion, managed callback, file I/O or heap string formatting.
4. Release `g_MetadataLock`. Reacquire only `UsageLock` to read the generation, then reject a witnessed generation/registry change before sealing.
5. Release metadata admission after the operation. Resolve, Seal and first failure clear stored opaque tokens; complete output retains owned bytes, not an `Il2CppClass*` or ticket.

`UsageLock` and `g_MetadataLock` are never nested by this reader. This avoids introducing the inverse lock order against metadata paths that record baseline use. The capture remains single-owner; concurrent calls require independent Capture objects. The source registry is assumed to contain valid current-runtime class identities, as supplied by the original writers.

The existing [metadata lifetime gate](https://github.com/night-outlook/il2cpp_plus/blob/0a0b70156e75d450d75d0bcfd9132843b8abbbb0/libil2cpp/vm/AssemblyShadowMetadataLifetime.h) prevents its participating `Runtime::Shutdown` teardown from passing the drain while the admitted reader is active. It is **not** an engine-owner safe point, a bounded-wait guarantee, or proof that an arbitrary pointer belongs to the current runtime. Default reads now refuse after the same gate reopens, preserving f716 epoch discipline. General reload support, other reclamation paths and real shutdown lock ordering remain unqualified; this candidate must not be activated as a terminal Player source on the strength of host mocks.

## Storage and failure behavior

`ResolvePhysicalClassCString` scans namespace/name against the **same remaining 1 MiB arena**, reserving one byte for the literal separator. It does not call unbounded `strlen` to obtain lengths before checking capacity. A scan visits at most the allowed text length plus the terminator probe. Sources must be legitimate lifetime-valid C strings, or readable through the declared scan window; this is not arbitrary pointer probing or memory validation.

The capacity remains 4096 candidate slots and 1,048,576 owned text bytes. Exact fit succeeds; one byte over fails without exposing a partial row. Null strings, wrong token, duplicate resolution, out-of-phase calls, unresolved rows, changed generation/registry, aliased source bytes and exhausted capacity fail closed. The alias check is performed before each scanned read, including a source range that crosses into the Capture object. First error is retained. No transport limits, enum values already in use, JSON schema, original getter bodies or historical evidence are changed.

## Host verification actually performed

The actual candidate method **excerpt**, actual modified capture header, existing gate header and unchanged pinned writer/current V1 serializer/frozen-general builder are compiled. CandidateRegistry, Il2CppClass layout, class-name access, UsageLock, metadata mutex and lifecycle scenarios are explicit host mocks. Full `AssemblyShadow.cpp` and official Unity headers are not compiled.

| Verification | Actual result |
| --- | --- |
| Original pinned source/header/fixture baseline, Linux Clang strict | Passed, original fixture execution |
| Final candidate, Linux Clang 17, strict C++17 | Passed, 15 groups |
| Final candidate, Linux Clang 17, ASan/UBSan with leak detection | Passed, 15 groups |
| Final candidate, Linux GCC 14.2, strict C++17 | Passed, 15 groups |
| Final candidate, Linux GCC 14.2, ASan/UBSan with leak detection | Passed, 15 groups |
| Runner source/refusal/early-ledger regression tests | Passed, 8 methods |
| Original reader with new class-ownership regression | Compiled, then failed the expected completion assertion; regression reproduced |
| Earlier gate dependency with new reopened-owner regression | Compiled, then failed the expected owner-refusal assertion; incoming f716 behavior preserved |
| Six-file patch mechanics in an explicitly synthetic context tree | Passed; full pinned-checkout application NotRun |
| Materializer with an unpinned synthetic full `.cpp` | Correctly refused before any output; positive full-base materialization NotRun |
| New native CI at f598 | **Passed 3/3** (macOS Apple Clang, Linux Clang/GCC; strict and sanitizer profiles) |
| Installed Unity SDK syntax/link / Unity Editor / Player | **NotRun on this new native revision** |

The final four native profiles ran through the revised runner against an **explicitly labelled synthetic input tree containing the exact candidate excerpt**, not a fabricated full translation unit. The runner then compiled that excerpt inside the instrumented fixture. Its `compiledActualProductionMethod` field refers to the extracted method; the enclosing Primary evidence explicitly records `fullAssemblyShadowTranslationUnitCompiled=false` and `remotePublication=false`.

The 15 groups include classless ownership, prior fail-closed/capacity/token contracts, independent general parity, class-name ownership after source mutation/destruction, null/absent rows, bounded C-string budget and alias cases, closed-owner refusal, usage changes after metadata reads, shutdown drain and parallel captures. Heap-new accounting is zero in the watched, preallocated synchronous capture cases; that is not a whole-VM allocator/RSS/GC result. Instrumented class-name access requires a metadata mutex and positive admission and rejects a held UsageLock.

The 4096-class-bearing-row fixture produces **692,677 bytes** of complete general JSON. It matches the **pinned current V1 serializer** using independently constructed legacy field values and the staged frozen general output byte-for-byte. The classless fixture matches 980 bytes. Other VM domains are explicitly synthetic. Neither size is an actual SNAP-01 producer length, and neither proves complete field14+15 V2 integration.

Two development-only control failures are retained rather than hidden: the first extended fixture compile needed an explicit conversion of its instrumented name type in the independent expected-value expression; the first old-body control compile found the deliberately unused mock metadata mutex. A harmless explicit mock reference allowed the old-body negative to execute without suppressing warnings. The final compiler flags remain `-Wall -Wextra -Werror -pedantic`; no sanitizer or production assertion was disabled. Earlier evidence directories are retained under their original failed statuses.

## Runner and CI preparation

The revised native runner pins the exact reviewed method SHA-256, verifies all 15 unique group results in both strict/sanitized profiles, tracks its header inputs, and creates a factual failed RESULT/MANIFEST after an admitted output root even if a source prerequisite is missing. Eight new Python tests cover reviewed/changed/duplicate/unbalanced source, missing input/API/compiler and refusal to reuse a consumed output. Metadata-scope pass fields stay false if a prerequisite fails.

The existing first-use workflow draft includes the gate header, executes those Python tests, then the C++ matrix. The CLI and result kind remain compatible with the existing ten-component Local preflight. The changed workflow **ran and passed all 3/3 native CI jobs**. The original/current first-use class method was compiled under explicit instrumented mocks. The 3 original ZIP digests and all **57/57** manifest-declared output files were independently verified. [CI 38876310270](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876310270). The other nine components, 70-unit installed-SDK matrix, general/execution integration suite, C# API checks and original broader regressions were not rerun for this candidate.

## Publication, CI custody and remaining gates

Remote native source published as `f598f8da5749e7c09ad5816630ce7e40b3f4ebca` on `codex/assembly-shadow-r01b-h1`; later workflow-only native HEAD `1e1d152f0e05b8038427c76a9c8a9b4b60998a72`. Source pin and current native HEAD must be separately recorded at Local. The new first-use host CI [38876310270](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876310270) passed all **3 jobs**. ZIP archives: 606920/961953/1004512 bytes for macOS Clang, Linux GCC, Linux Clang; independently checked exact ZIP SHA256 and **21+18+18=57** manifest files. The exact machine evidence is in [EVIDENCE.json](EVIDENCE.json).

The broader native CI at f598 also passed general producer, execution serializer, transaction inventory/status, terminal rejection/reporting, and serializer interop scopes. Two unrelated old source gates were red: an R02 historical `finalize_sources.py --verify` whole-file fingerprint (already invalid before this increment) and the R03 terminal-policy workflow's obsolete source-shape assertions. Primary corrected **only the workflow assertions** to match the existing multi-line terminal rejection path and single diagnostic exception scope, retaining the compiled native policy test. Terminal workflow [38876957263](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876957263) was an intermediate red attempt, followed by the later exact-source workflow-only commit whose run should be read separately. No terminal product code was changed. **The old R02 whole-file historical identity failure remains FAIL**, not accepted or silently ignored.

Official Unity2022.3.62f2 installed SDK compilation and Player tests for this new native commit are **NotRun**; earlier Local PASS `20261016-0620` only exercised native `0a0b7015...`, not the new source or f716. A **separate exact-source host/SDK-only Local batch** is required under a new reviewed `WEB_TO_LOCAL.md`. Do not reuse a consumed root or run Unity/Player without later independent authorization. This native source method is still **inactive** and not integrated with the real getters.

**P1 remains incomplete:** class-pointer origin is not globally authenticated by merely holding a metadata ticket; the source owner must guarantee that any stored class pointer was registered in the initial admitted runtime lifetime. `g_MetadataLock` + first-session admission do not prove a coherent VM-wide snapshot, safe shutdown in all thread/lock states, complete metadata iterator memory/GC/RSS cost, R02 counter epoch, or bounded execution type-key formatting. P2 native/C# V2 transport/unchanged semantic verifier remains NotIntegrated; E0/E1 Unity engine-owner safe point, native maintenance, callback drain and restart remain unresolved. Neither these host tests nor 70 legacy official syntax tests meet full P3 acceptance.

The previous Local receipt successor `20261016-0620` remains PASS/PassedSourceHostAndSDKOnly; its preceding `20261016-0a0b` remains FAIL/FailedOrIncomplete. Earlier SNAP-01/N/M/K/I/E FAIL, strict original S custody Blocked and independent R03 full-stage review FAIL/re-review NotRun remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No H2/X02/M08A or automatic Human Review Gate.
