# M00 baseline acceptance report

Status: M00 accepted. Final exact-source, clean-cache ARM64 Player passed;
independent review returned PASS. Local baseline tags identify this closeout
and the exact paired runtime/package/native revisions. M01 starts only after
the four tag targets are audited.

## Requirements and evidence

| Requirement | Current evidence |
| --- | --- |
| 00.1 current four-repository inventory and dirty-state preservation | source-pins.md; original demo unchanged; exact backup branch snapshot |
| 00.2 independent il2cpp_plus source of truth | night-outlook fork, upstream v2022-8.14.0 pin, ASSEMBLY_SHADOW_FORK.md |
| 00.3 full SHA pairing | ProjectSettings/AssemblyShadowSourcePins.json; demo build source 2c886877c9e19bbb8f10aa8efeb0786903d73193 |
| 00.4 installer decision | ADR-0001, opt-in pinned local source composition |
| 00.5 ordinary HybridCLR IL2CPP Player | Final clean-cache ARM64 run Passed; M00-HOTUPDATE-OK, AOT Prefab/Scene/reflection/SO passed |
| 00.6 native observability and repeatable install | Two identical 921-source-file receipts; Debug native build; dSYM and source-line symbol lookup |
| 00.7 native feature default OFF | Header and actual compiler flag OFF; preprocessor OFF/ON accepted, value 2 rejected; Editor switch tests passed |
| 00.8 branches, commits, tags and independent review | Independent PASS in M00-review.md; local assembly-shadow-m00-baseline tags |

## Validation

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
- The final installer receipt has SHA-256
  6fc57ec95603270398878d1958ad7e06740ebcd3cc558af33d94e64828d0138b.
  The strict verifier passed before and after the final build, including demo
  source verification (no development skip).
- Library/Bee was moved to the recorded recoverable cache backup before the
  final build; Library/Il2cppBuildCache did not exist. The new build completed,
  and `file` confirmed GameAssembly.dylib is ARM64-only, not universal.
- Final build and Player processes exited zero. Unity's BuildReport reported
  zero errors/warnings; native clang warnings and headless shader diagnostics
  remain in the full local logs and are not hidden by that summary count.

The accepted machine-generated evidence is under `Evidence/`: installation
receipt and repeatability, Editor tests, cache manifest, final build and Player
results, and native symbol lookup. `m00-verification.json` is a manually recorded
summary of commands actually run, not an additional test execution.

Raw local logs are retained at `_temp/UnityExec_20260827_040634.log` and
`_temp/AssemblyShadow/m00-player.log`; their hashes are recorded in the evidence.
The native artifact is
`Builds/AssemblyShadow/M00/Baseline.app/Contents/Frameworks/GameAssembly.dylib`.
Its symbols are `_temp/AssemblyShadow/M00-clean-arm64-GameAssembly.dylib.dSYM`.
Native intermediate objects are under Library/Bee/artifacts/MacStandalonePlayerBuildProgram.

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
   the final accepted build is verified ARM64-only.
6. This host has Command Line Tools, not full Xcode. The real native compile and
   Player run succeeded. Windows and Android are not validated.
7. A live LLDB launch stalled while macOS SecurityAgent was active. The
   task-owned probe and debugserver were stopped; no machine authorization was
   changed. Offline symbol/source-line lookup succeeded. M01 must retain
   symbol-backed in-process native traces and report any debug-access limits.
8. Initial and final Player shutdown emitted Unity's allocator-after-shutdown diagnostic.
   It occurred with unmodified HybridCLR runtime and Shadow OFF; there was no
   crash or failed test. It is recorded, not suppressed or called a clean
   whole-engine shutdown.
9. Headless runs use the Null graphics device, which reports unsupported URP
   shaders. Rendering is outside this runtime baseline; no visual validation is
   claimed. Unity serialized new defaults into UniversalRP.asset during the
   isolated worktree build. That baseline migration is committed; the original
   demo's dirty Renderer2D.asset was not touched.

## Reproduction

Follow Tools/AssemblyShadow/README.md. The final Player invocation was:

```sh
/usr/bin/arch -arm64 Builds/AssemblyShadow/M00/Baseline.app/Contents/MacOS/AssemblyShadowBaseline \
  -batchmode -nographics \
  -logFile /Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/_temp/AssemblyShadow/m00-player.log \
  -shadowResultPath /Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/_temp/AssemblyShadow/m00-player.json
```

The clean rebuild includes Generate/All and a native Debug build. Its final
BuildPlayer phase took 35.21 seconds; this is not the whole Editor startup and
Generate/All duration or a production performance measurement.

## Gate boundary

The exact demo source is pinned, final clean-cache ARM64 Player validation is
archived, and independent review accepted the code/evidence at demo commit
738fdf0cbaeb1c0f75ae7b55c5ef82c77b42b1ec. This closeout changes only review
metadata. The M00 tag is created only for the accepted boundary.
