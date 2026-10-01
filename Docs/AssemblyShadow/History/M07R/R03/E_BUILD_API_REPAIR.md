# R03 E — build-summary count types and complete helper compilation

Primary Implementation self-review. This record is not independent stage review, Local acceptance, or a Human Review Gate.

## Received and preserved evidence

Local return `ed9afef29d17c64f15b281ea8b2176cb17d637b3` records exactly one C invocation from demo `fdefb4f7133812f3b0593ae2257057c1bc57195e`: **ReturnRequired, 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. The original 677 indexed files / 678 archive members remain the Local custody claim; Primary has not accessed the retained macOS live root or modified the Local-owned reports/checkpoint.

C confirmed the fixture reference and supervised compiler-lifetime repairs in their focused scope: 33 pinned-Unity consumers, the invalid-key control, two real Editor probes, and clean completion of all 55 command groups. It did not complete four native builds, Editor assertions, or any of the nineteen Players. Original A/B classifications and uncertainty about B's survivor identity remain historical.

C result/index/archive SHA-256:
- `f1dae2e7925f155dcb3eb4d6eff51705846c68366560e89506d6cbde631f5c6d`
- `477ad959a85db392a11fb0569fa313ee67ee4ad3e835a31821d37ebe2b790dec`
- `65537c0270229671214ae6c36633533d5f864484c00a2f6aa745e65399c20fe3`

## R03-LC-001 and selected correction

The common `R03Build.cs` receipt declared `errors` and `warnings` as uint, while the pinned BuildSummary getters return System.Int32. All four build-role invocations and EditMode failed at the direct assignments on line 109 before the build method/Test Runner could run. Local's metadata inspection bound UnityEditor.CoreModule.dll to `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`.

The product-code change is exactly two declarations: both receipt count fields now use int. There is no cast, narrowing, unchecked wraparound, change to the numeric JSON fields, or change to the requirement for a successful report and zero totalErrors. A checked unsigned conversion is unnecessary when the receipt can represent the API directly. No native source, managed package, fixture, runtime expectation, timeout, lifetime cleanup policy, or top-level cell dependency changed.

## New complete-source compile check

`build_api.py` compiles the actual asmdef-owned HybridCLR runtime, CodeGen, and Editor dependencies, then the complete current `PlayerProject/R03Build.cs`. It uses the pinned Unity installation's NetCoreRuntime/dotnet, DotNetSdkRoslyn/csc.dll and real API/reference DLLs. The macOS defines/reference profile comes from C's actual compiler log; the CodeGen compilation pipeline dependency is explicitly included. This is a compile-only check, not a simulation of Unity's import/ILPostProcessor/build pipeline.

The decisive UnityEditor.CoreModule bytes must equal the SHA-256 observed in Local C. Source, asmdef, plugin, compiler, runtime, and API/reference files are hashed before and after compilation. Source selection follows nested asmdef ownership and dependency order. No handwritten Unity API stubs or replacement HybridCLR implementation is used. All responses, command receipts, emitted assemblies and input inventories are retained.

The preserved complete C helper is a separate negative control. Its Git blob must be `7b54381bc96b4be133ebed5f7b7173fcc0a57849`; it is read, never changed or executed. Compilation must return exit 1 with exactly the two CS0266 count-conversion errors, no extra compiler error and no output DLL. A timeout, survivor, missing reference, different diagnostic or successful original compilation cannot satisfy this control. The repaired complete helper must compile and emit a DLL with clean command completion.

The Local `player-fixtures` cell performs this same check after the existing fixture consumers and Editor lifecycle probes and before any native-role preparation/build. The 36-cell ledger and nineteen Player cases are unchanged. A failed API check records its own `build-api/results.json` and blocks dependent work; no batch retry or evidence rewrite is introduced.

## Source, validation and evidence

Implementation commit: `24a5a25972afc2a91afb26e68f97984c6dd8af2b`.
Final tested source anchor: `5931ada3c70958a7c6132219e059a42ee3cecbd0`.

Final pinned-API workflow **36834916602**, job **110279907209**, passed on source `5931ada3c70958a7c6132219e059a42ee3cecbd0`. The three actual package dependencies compiled from **15 Runtime + 14 CodeGen + 173 Editor C# files**, followed by the complete repaired helper with **zero compiler errors or warnings**. The package Editor sources reported 61 existing CS0649 warnings; those logs are retained, not suppressed or treated as helper errors.

The original full helper separately produced exactly two CS0266 errors at (109,34)/(109,81), exit 1, and no DLL. The four positive and one expected-negative compiler command all completed with no survivors, timeout or cleanup errors. The critical CoreModule hash equals C's `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. The current helper source SHA-256 is `d058bed910f81341c6a615abe2479167d7ebe0537913a205573d0c59f0f182b5`; emitted helper DLL SHA-256 is `80c702a3b60e9f1ff4afdb6abc64b82fa0baef675ae7e0a8d72e63284fffb71c` (13,312 bytes). The check binds 425 input files and 115 captured defines.

Pinned-API artifact **11147819952**: SHA-256 `a6546e0780bbf6bf28ec5a652b37821ef236eee2451656e641478b3e243990a0`; 461,940 bytes, **28 indexed files / 29 ZIP files**. Result SHA-256 `61f563d4ef42eac2a2c77697e2bb7640d21d448c470c4f60ab7763e01ba4a368`.

Final host workflow **36834916578** passed both Linux x86_64 and macOS 15.7.9 arm64 jobs on the same source. Each passed **67 Python contracts**, reference/candidate graph **9/9 each**, admission/method **35/35**, fifteen generated fixtures, **33 metadata audits and 33 actual SDK compiler consumers**, Runtime API compilation and success/failure shared-compiler supervision. Each has **49 positive and two expected-negative command completions, all clean**. The container's 67 Python contracts also passed; actual .NET/Unity compiler execution was performed in CI, not simulated in this container.

| Host | Job / artifact | ZIP SHA-256 | Authenticated membership |
| --- | --- | --- | --- |
| Linux x86_64 | 110279907359 / 11148846697 | `e29f6c71e8f1b93f8a6a89ec3d69297c0849c218f289d153aeb4862917c0c8e0` | 622 indexed / 623 ZIP files |
| macOS arm64 | 110279907270 / 11148348847 | `73928fae7335ba832b82d93a3b40875b533440cbb4d0c3b109921c3aa2d427d2` | 622 indexed / 623 ZIP files |

Primary downloaded all three final archives and authenticated each ZIP digest, exact safe/nonduplicate membership, every indexed size/SHA-256, result/source identity and command stdout/stderr binding. E_HOST_EVIDENCE.json records these checks, individual pinned-compiler PIDs/receipt hashes, input/output hashes and host results. Raw compiler responses/results/streams remain in the archives; archive retention ends 2026-10-15. This is not the Local focused seal or access to C's retained macOS live root.

R03-LC-001 disposition: **fixed and verified by actual pinned compiler; integrated Local revalidation required**. No independent stage review or new Unity Editor/IL2CPP execution is claimed.

The build-API workflow downloads the exact official Unity 2022.3.62f2 ARM64 installer, changeset 7670c08855a9, and extracts it without installation, Editor launch, or license operations. Its package digest and extracted API/compiler hashes are evidence; no Unity binaries are uploaded in the result archive. Compiler execution is not Unity Editor or native Player execution.

Official distribution source: https://download.unity3d.com/download_unity/7670c08855a9/MacEditorInstallerArm64/Unity-2022.3.62f2.pkg . Release identity: https://unity.com/releases/editor/whats-new/2022.3.62f2 . These external sources locate the original toolchain; project requirements and C's diagnostics remain the authority for the repair.

## Primary compiler-option correction

The first source-24a compile passed the actual helper and reproduced the two original errors, but archive inspection found CS2023: Roslyn ignored `/noconfig` inside its response file. Primary corrected the invocation before handoff: `/noconfig` now stays on the actual command line and remaining arguments are in the retained response file. Source `5931ada3c70958a7c6132219e059a42ee3cecbd0` is the new test anchor; first-run artifacts remain historical, not the final strict-profile evidence. Existing package source warnings are recorded, not suppressed; they do not represent errors in the repaired helper.

## Changed files and self-review

Product helper: `Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs` (two field types only).

Tooling: `Tools/AssemblyShadow/R03/build_api.py`, `test_build_api.py`, `input_validation.py`, `run_host_lifetime.py`, and `.github/workflows/r03-build-api.yml`. The existing host workflow discovers the additional ten tests; its expected total advances from 57 to 67 without removing a prior test.

Documentation: new E repair/evidence/matrix records plus canonical README/status/WEB_TO_LOCAL. No Local-owned report or previous history file is overwritten.

Self-review verifies: exact two-field product delta; unchanged zero-error/build-success guard; actual entire helper as compiler input; actual package dependencies and Unity references; strict positive/negative outcomes; bounded owned-command enforcement; unused output roots; immutable prior source and diagnostics; unchanged original validation scope.

## Bootstrap, handoff, limits and rollback

Four feature refs were read through the GitHub Connector and matched the Local return. A demo disposable smoke on `codex/connector-smoke-r03-build-api-20261001` used base `ed9afef29d17c64f15b281ea8b2176cb17d637b3` and exact read-back commit `15d3069ccd4ebdd79cd9851581a857e2176a1349`. Only demo is modified; unchanged external repositories retain their prior write-smoke record and fresh read verification. No delete-ref action is exposed; the disposable branch remains non-authoritative.

Next root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`. The Local agent receives completed source and executable checks, not an implementation task. It must use the new exact transport tuple and current WEB_TO_LOCAL.md. Native/package sources remain `041c0cbb42d3e64e54fe605673d99799b5d63893` / `120bb01be680cec0375002a0823552d66d34b84c` / `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`.

No new integrated Local batch was run by Primary. Installer/generation/IL2CPP/native/runtime behavior remains unvalidated; subsequent failures may surface after this compiler prerequisite. Full R03 legacy/resource/generic/stack-trace/startup/capacity/performance/memory, PureInterpreter qualification and independent stage review remain Primary-owned. R03Accepted=false; H2Passed=false; expansion disabled. R02 deferred CPU and original H1 RSS risks remain visible.

Rollback is a new Primary-controlled coherent source/handoff revision or a separate read-only comparison with the pre-repair source. Never retry C, overwrite retained Players/logs/archives, or mix unrelated source tuples.
