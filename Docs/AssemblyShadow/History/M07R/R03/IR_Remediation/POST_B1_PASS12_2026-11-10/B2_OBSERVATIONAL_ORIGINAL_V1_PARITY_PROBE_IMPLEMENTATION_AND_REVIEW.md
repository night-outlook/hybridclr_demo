# R03 B2 — inactive original V1 execution field15 observational byte-parity probe

Date: 2026-11-12 UTC. Owner: Primary Implementation. Stage: **source-complete bounded observational probe, not complete original V1 field15 parity, terminal native V2, or executable Local Validation**.

## 1. Exact sources and unchanged historical boundary

All repositories use branch `codex/assembly-shadow-r01b-h1`.

| Source repository | Current reviewed commit |
| --- | --- |
| night-outlook/il2cpp_plus | `2670b6cfc7006c9483c4c9322808c152efa16772` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/hybridclr_demo | Read exact current GitHub branch HEAD (this document/WEB_TO_LOCAL advance it) |

The [machine source candidate](../../../../../../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins **53 native ABI/implementation/reference/test/CI Git blobs plus six demo pure/reference source blobs**, including an independent, **exact 5,222-byte** copy of the ORIGINAL `GetExecutionDiagnosticsJson` function body from `il2cpp_plus@68530d7ecb86c9122d9ae5eb20366ccb0ea086b6`. The source gate compares every byte of that original function against the current native implementation. Both feature-on and feature-disabled getter definitions are separately accounted for. The original getter itself is **unchanged**; its historical body and original image map semantics are not replaced with the new probe.

The B1 oneuse-12 real Unity macOS ARM64 IL2CPP Player evidence remains historical **focused 19/19 PASS** at executed demo `2d690bb2f7234ddcbee339f9da7125d687f5ed45` and native `8aa8d09319a89b55b2496bcc2c69ccc69cb57be9`. That batch, all raw roots and source pins are consumed and cannot serve as current B2 parity/transport/Player acceptance.

## 2. Primary design and implementation

**Problem:** The original V1 `AssemblyShadow::GetExecutionDiagnosticsJson` produces the full `finalExecutionDiagnostics`-equivalent JSON by copying the execution registration inventory, building a `MetadataTypeImages` map from `Assembly::CaptureShadowEnumeration` (logical assembly enumeration), formatting each TypeKey using `AssemblyShadowTypeKey::FormatMetadataOnly`, collecting class cctor/static-field facts and appending the original R02 suffix. The new bounded physical AOT source independently authenticates physical TypeDef handles using the **raw originally registered** AOT assembly table. These are not automatically the same set, so successful restricted AOT TypeKey formatting does **not** establish original getter equivalence.

The new, **inactive** source `AssemblyShadow::TryProbeBoundedExecutionV1ByteParity` is declared in `AssemblyShadow.h`, included once by the same `AssemblyShadow.cpp` after the preexisting P1 admitted getter, and implemented in `AssemblyShadowExecutionV1ByteParitySource.inl`. The caller exclusively owns and preconstructs a physical membership Scratch, owned class Rows, the bounded frozen Record, a fresh `Probe` and a `std::string` originalV1 output.

Its read-and-compare algorithm:
1. Clear any old reference output and reset receipt; fail immediately if the parity probe has been consumed.
2. Acquire **one outer initial-session metadata lifetime Reader** covering both getter invocations and comparison. This prevents normal native Runtime metadata teardown during the active read, but is not a class pointer provenance/whole-VM epoch guarantee.
3. Invoke the **unchanged** P1 `TryGetExecutionDiagnosticsWithMetadataAdmission`, which delegates to original `GetExecutionDiagnosticsJson`. It may allocate, query logical assembly visibility, format original types or throw. A failure/exception, empty output or over-budget original string fails closed with scrubbed returned output.
4. Invoke the existing restricted physically matched AOT `TryCaptureBoundedDefinitionExecutionLive`. It validates class registry witnesses, original physical assembly registration, TypeDef ownership, native source/initial metadata session, Unicode/composite/limited primitive keys, B1 first error and R02/registry revisions. No class pointer survives in owned class rows.
5. Require the bounded source receipt's physical membership/restricted TypeDef/fence claims and complete immutable Record, then run the new allocation-free `assembly_shadow_execution_v1_parity::Probe::Compare` with the exact two JSON byte spans (each limited to **3,932,160 bytes**). On a difference, store original/bounded lengths and exact first byte offset in the typed comparison receipt; invalidate the bounded source and frozen result and clear originalV1. No silent fallback to the original getter bytes is allowed.
6. On exact equality, report only `exactBytesObserved=true` and `twoIndependentObservationsOnly=true`. Explicit negative fields remain `coherentVmEpochProven=false`, `fullCanonicalTypeKeysProven=false`, `terminalSafeFinalExecutionDiagnostics=false`, `nativeV2TransportImplemented=false`, `runtimeAcceptance=false`, `R03Accepted=false`, `H2Passed=false`. Equality across two separately timed observations cannot authenticate a globally atomic source.

The pure `AssemblyShadowExecutionV1ByteParity.h` contains a C++11 one-shot, noncopyable `Probe` and typed outcomes: Reused, MissingInput, OutsideBudget, DifferentLength, DifferentByte, UnavailableLegacy, UnavailableBounded, or exact observed equality. It retains no reference bytes, metadata pointers, heap allocations or mutable global state. It never parses or fabricates JSON, so it cannot claim correctness for incorrect-but-identical source rows.

**New implementation/test files in `il2cpp_plus`:**
- `libil2cpp/vm/AssemblyShadowExecutionV1ByteParity.h` — original/owned byte comparator.
- `libil2cpp/vm/AssemblyShadowExecutionV1ByteParitySource.inl` — inactive healthy-time original getter + bounded physical source adapter.
- `libil2cpp/vm/AssemblyShadow.h` and `libil2cpp/vm/AssemblyShadow.cpp` — declaration/include with original getters untouched.
- `NativeHostTests/AssemblyShadowExecutionV1ByteParityHost.cpp` and `.github/workflows/r03-native-b2-v1-parity-host.yml` — independent pure comparison host/CI.
- `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp` and existing `.github/workflows/r03-native-b2-definition-live-source-host.yml` — compile **both actual new native .inls**, exercise equal/mismatch/legacy-unavailable/reused adapter under a deliberately **fake original V1 reference** and preserve the existing AOT/Unicode/primitive negative cases.
- `NativeHostTests/README.md` — precise distinctions, test-only allocator exclusion and no-runtime-authority statement.

**Demo/source admission:**
- `BoundedObservedExecutionV1ByteParity.h` is a byte-identical independent pure header mirror.
- `OriginalV1ExecutionGetter_2026-11-12.txt` freezes the exact legacy getter source body without compiling the snippet or adding a separate implementation to GameAssembly.
- `b2_definition_source_gate.py` checks exact original getter bytes, two conditional getter definitions, actual parity adapter source, original admitted getter Reader, original ExecutionSerializer/R02, frozen Record, metadata lifetime and diagnostics writer sources, negative flags and all 53/6 Git blobs.
- `test_b2_definition_source_gate.py` exercises acceptance-promoting and getter-source mutation/alias negative tests.

## 3. Exact evidence and what it does NOT prove

| Test | Observed source/host result | Explicit limitation |
| --- | --- | --- |
| [Native source-mock CI 43146273936](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146273936) | **4/4 completed/success**, macOS/Ubuntu × C++11/17; Release/Debug strict/ASan-UBSan; 16 processes each covering **67 physical-source cases, three parity-adapter cases, 1,258 assertions and 20 direct primitive defaults** | Reference “legacy” getter is synthetic and rebuilt from the same bounded source; successful fake comparison is **not** real V1 getter/Unity evidence |
| [Pure comparator CI 43146317881](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146317881) | **4/4 completed/success**, Mac/Linux C++11/17; ten comparator cases, 42 assertions per process, strict/sanitized Release/Debug | No real VM metadata/original getter, class provenance or V2 |
| [Exact cross-fork source CI 43147578102](https://github.com/night-outlook/hybridclr_demo/actions/runs/43147578102) | **2/2 completed/success**; includes 53 original native/pure/ABI/CI blobs, six demo pure/reference sources, preserved legacy getter body and negative acceptance | Source integrity only, not original runtime byte equality or official Unity TU/Player |

Earlier source-audit REDs resulted from an outdated demo source count and an incorrect assumption that `AssemblyShadow.cpp` contains only one getter definition. It actually contains two **mutually exclusive** definitions: enabled original V1 and disabled FeatureDisabled stub. Both were independently inspected, and the final exact source byte gate accounts for them. The native C++11 mock initially failed to initialize a View with aggregate braces; an explicit C++11 constructor fixed it. Those REDs remain in CI history.

**No Unity 2022.3 SDK `AssemblyShadow.cpp`/Class.cpp full native TU build, linked GameAssembly, real V1 nonempty execution data, authentic primitive/Unicode classes, Player, GC/metadata teardown, original field14 or terminal field15/V2 artifact/recovery was run for this source.**

## 4. Independent findings and acceptance decisions

- **B2-PARITY-01 — original source identity:** the entire enabled getter body is captured verbatim in an independent demo fixture and checked against current native source, with the separate disabled fallback recognized. The original getter is not changed. **PassedSourceIdentityOnly.**
- **B2-PARITY-02 — observable equality:** the pure comparator is one-shot and bounded; actual wrapper uses metadata lifetime admission, validates source receipts and revokes on mismatch, exception or unavailable input. The synthetic host exercises real wrapper failure mechanics. **PassedHostBehaviorOnly.**
- **B2-PARITY-03 — source-map differences:** original logical Assembly::CaptureShadowEnumeration image ownership may not equal raw registered physical AOT image ownership used for the bounded source. Complete original FormatMetadataOnly can reject or format types differently. A real byte-identical comparison has **NotRun**; no assertion of complete class/field15 parity.
- **B2-PARITY-04 — temporal sampling:** the original getter performs multiple independently timed class/counter reads; the new physical-source capture re-reads metadata, state and R02. Even observed byte equality is **not** a whole-VM linearization, class cctor/static freeze, GC/teardown/ABA proof or consistent terminal snapshot. **Primary-owned open.**
- **B2-PARITY-05 — disabled/malformed source and resource limits:** original getter may allocate/throw, and original output could exceed the bounded field budget. The probe is deliberately *healthy-time only*, catches exceptions, rejects an oversized reference and offers no terminal I/O. Fake source tests cannot establish real Unity exception/noalloc behavior. **Open for runtime Local only after full B2 source implementation.**
- **B2-PARITY-06 — full V2 schema:** original V2 field14 `finalDiagnostics` and field15 `finalExecutionDiagnostics` demand complete terminal-safe original semantics, not B1 reason, a partial physical TypeDef subset or a successful dual-read probe. There is still no complete authenticated native writer, envelope or receipt. **NotImplemented; remains Primary-owned.**
- **B2-PARITY-07 — host isolation:** the fake legacy reference and any test allocator overrides remain solely under NativeHostTests, never linked into libil2cpp. CI compiles actual native parity .inl but does not compile the official native VM TU. **Source isolation only, future Unity symbol-roster verification required.**

The original independent R03 full-stage review remains **FAIL**, with both High `IR-R03-01/IR-R03-02` unresolved. H2, M08A, X02, SNAP-01 and a Human Review Gate are not entered. PureInterpreter stays disabled. The completed prior B1 oneuse-12 is not evidence for this probe.

## 5. Remaining Primary and conditional one-batch Local plan

Primary must next close **actual original V1 parity and source coherence**: prove the logical-assembly/physical-owner join and class/TypeKey/flag/r02 equivalence with valid original live metadata; implement full authenticated source copies for terminal-safe field14 and field15 with correct lifetime, or formally review a separately versioned schema if full original fields are infeasible. Then integrate the existing bounded binary codec and descriptor-relative exclusive artifact/envelope transaction with independent external identity-bound receipt and readback, harden torn-write/duplicate/replay/symlink and first-error race tests, and perform independent end-to-end source/host review before issuing a **new executable WEB_TO_LOCAL**.

A subsequent authorized Local Validation should use one **exact four SHA** tuple, fresh never-used owner-only absent roots, preserved Original-S archive and official Unity2022.3.62f2 macOS ARM64 IL2CPP build. In one batch it should check C++11 native TU/Bee and no host allocators in GameAssembly; original/frozen complete field14/15 exact bytes including 3 separated Empty, initializer error19 and captured generic guard15 Players; real Unicode/primitive/nested types; original/physical owner map differences; full V2 binary/envelope/recovery receipt identity; GC/RSS/first-call cost; negative metadata/terminal races; and independent raw/product evidence custody. **None of this is executable now.**

**Current source/product flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`.
