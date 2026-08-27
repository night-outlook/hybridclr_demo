# M00 baseline acceptance report

Status: baseline Player passed; final pinned ARM64/cache rebuild and independent
review are still pending. M01 has not started.

## Requirements and evidence

| Requirement | Current evidence |
| --- | --- |
| 00.1 current four-repository inventory and dirty-state preservation | source-pins.md; original demo unchanged; exact backup branch snapshot |
| 00.2 independent il2cpp_plus source of truth | night-outlook fork, upstream v2022-8.14.0 pin, ASSEMBLY_SHADOW_FORK.md |
| 00.3 full SHA pairing | ProjectSettings/AssemblyShadowSourcePins.json; final demo build-source pin pending |
| 00.4 installer decision | ADR-0001, opt-in pinned local source composition |
| 00.5 ordinary HybridCLR IL2CPP Player | Initial real ARM64 run Passed; M00-HOTUPDATE-OK, AOT Prefab/Scene/reflection/SO passed |
| 00.6 native observability and repeatable install | Two identical 921-source-file receipts; Debug native build; dSYM and source-line symbol lookup |
| 00.7 native feature default OFF | Header and actual compiler flag OFF; preprocessor OFF/ON accepted, value 2 rejected; Editor switch tests passed |
| 00.8 branches, commits, tags and independent review | M00 branches/implementation commits exist; final tag/review pending |

## Validation so far

- Unity 2022.3.62f2 compiled the project and opt-in package installer.
- Repeated installation produced identical receipts. Immutable source files are
  checked against committed Git blobs and installed SHA-256 hashes.
- The normal IL2CPP Player returned exit zero and result Passed. It loaded the
  ordinary non-AOT hot-update DLL, preserved AOT Assembly.Load identity,
  returned M00-AOT-OK|1234 from the serialized Prefab, loaded ScriptableObject
  value 5678, found the scene component, and found no Missing Script.
- Five Editor/tooling tests passed, including large process-output draining,
  quoting/backslash round-trip, native feature flag selection, baseline
  MonoScript.GetClass and ordinary hot-update exclusion.
- Twenty-one standalone tests passed for clean verification, tampered installed
  bytes, forged/incomplete receipts, extra/missing files, arbitrary exclusions,
  wrong pins/target/Unity, duplicate JSON/path entries, traversal, hidden source
  drift, ignored Unity code, symlinks and recoverable cache handling.
- LLDB resolved the generated ARM64 GameAssembly symbol for
  hybridclr::metadata::Assembly::LoadFromBytes to Assembly.cpp:101.

## Findings and deviations

1. The old il2cpp_plus 2022-3.x checkout was not the package's intended pairing.
   A new branch starts from exact v2022-8.14.0; the old branch remains intact.
2. A local UPM dependency requires real filesystem package paths. The opt-in
   installer and template paths now use PackageInfo resolution.
3. One upstream .meta contained only its GUID. Unity added the default
   MonoImporter block. This was inspected and committed without changing the
   GUID, rather than exempting dirty package state from the pin guard.
4. The original process-capture helper waited before reading redirected output.
   A complete native Git inventory filled the pipe and deadlocked. Concurrent
   stdout/stderr draining, quoting, a timeout, and regression tests address the
   cause. Only the task-owned stalled Git process was terminated.
5. Initial Unity macOS output was universal despite PlayerSettings.SetArchitecture.
   The build now sets OSXStandalone.UserBuildSettings.architecture explicitly;
   the final accepted build must be ARM64 and verified as such.
6. This host has Command Line Tools, not full Xcode. The real native compile and
   Player run succeeded. Windows and Android are not validated.
7. A live LLDB launch stalled while macOS SecurityAgent was active. The
   task-owned probe and debugserver were stopped; no machine authorization was
   changed. Offline symbol/source-line lookup succeeded. M01 must retain
   symbol-backed in-process native traces and report any debug-access limits.
8. Initial Player shutdown emitted Unity's allocator-after-shutdown diagnostic.
   It occurred with unmodified HybridCLR runtime and Shadow OFF; there was no
   crash or failed test. It is recorded, not suppressed or called a clean
   whole-engine shutdown.

## Gate boundary

Do not start M01 until the exact demo source is pinned, final clean-cache ARM64
Player validation is archived, and an independent M00 review accepts the code
and evidence. The M00 tag is created only for the accepted boundary.
