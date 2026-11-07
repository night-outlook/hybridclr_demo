# R03 initializer oneuse-06 — interpreted current-process import correction

**Primary Implementation design and one-use Local Validation plan**  
UTC 2026-11-07. Scope: `IR-LOCAL-R03-INITIALIZER-05-INTERNAL-IMPORT-01` only.
No work on H2/M08A/X02/SNAP-01, no new product VM feature and no Human
Review Gate approval.

## 1. Empirical finding and original custody

The actual once-executed initializer oneuse-05 used demo
`db232418adf2fc35c54ed72a8933a174f8218126`; Local published
its evidence at demo `eeeec3ba574047c06b5b853e58a5b594e80c37ae`
and stopped. The original two Player commands 0017/0018 (PIDs23120/23133)
both exited 2 with empty strict V1 raw, actual bounded trace/recovery and
native Seal reason1. Both actual captured initializer first-failure reasons
reported `Methods: <Module> TypeInitializationException ---> Unable to load
DLL '__Internal'` and `dlopen(__Internal,...)` on macOS. No callback
entry phase299/return300; pinned state0; even the healthy control
reported Commit19/state9. This proves a library-resolution failure
before callback entry, **not** the intended postprepared failure sentinel.

The one actual ON/Release Unity2022.3.62f2 macOS arm64 IL2CPP build,
ten current native host components, 46 host tests, historical S scoped
audits, live host evidence custody and product evidence seal separately
Passed. Strict original historical custody still Blocked; 17
owner-authorized retired runtime roots and 40 named duplicate paths are
Unavailable/PermanentlyDeleted, *not* implicitly restored, rehashed or
reclassified. The published oneuse05 full batch and earlier
oneuse01–04 records remain immutable, regardless of their verdict.
No current source edit is permission to replay 05.

## 2. Independent source trace and decision

The opt-in original fixture emitter
`Tools/AssemblyShadow/R03/PlayerFixtures/InitializerNativeTargetFixtures.cs`
used `new ModuleRefUser(module, "__Internal")` for its interpreted
`R03.TerminalWitness.RecordPreparedInNative` PInvoke.
`hybridclr/transform/TransformContext.cpp` resolves interpreted
PInvoke using `PlatformInvoke::Resolve`; pinned
`il2cpp_plus/libil2cpp/vm/PlatformInvoke.cpp` special-cases **only**
`__InternalDynamic` to call
`LibraryLoader::LoadDynamicLibrary(Empty())`. In
`libil2cpp/os/LibraryLoader.cpp`, an empty name opens the
current-process program handle; other names are passed to a
library-name loader. The recorded `dlopen(__Internal)` is exactly
consistent with this difference. Unity's conventional AOT
`DllImport("__Internal")` is link-time, not the same runtime
interpreter import contract.

Chosen **candidate A, limited fixture correction**:
- Emit precisely `ModuleRef "__InternalDynamic"` in the opt-in
  **interpreted** initializer target only. Retain exactly
  entry `R03_IRW_OnPrepared`, no-arg → int32, Cdecl and NoMangle,
  IL callback after ordered Ready store, its throw-on-failure,
  original direct/delegate/generic/store semantics, and
  initializer-control return versus initializer-failure sentinel.
- The original compiled AOT managed Player's `DllImport("__Internal")`
  remains unchanged. No global aliasing/rewriting of `__Internal`
  in the product native resolver is authorized: that would change
  third-party PInvoke semantics and cross-platform behavior.
- Emit a new deterministic V2 MVID namespace for both changed
  target images, explicitly pin new actual DLL SHA256/MVID/size.
  The 15 historical original S inputs, CLR-only terminal fixtures,
  K/older target DLLs and all consumed oneuse05 proof are untouched.
- The editor/native metadata admission remains strictly source-
  pinned and requires exactly the new emitter Git blob.
  The real target generator receipt includes source-bound
  `expectsNativeModule=__InternalDynamic` and
  `interpreterImportContract=R03IR.InterpreterCurrentProcessImport.V2`,
  and both target rows repeat those exact facts.
- Add an in-memory **negative generator mutation** for
  legacy `__Internal` which must fail the same existing emitted-IL
  verification predicate. Do not weaken the exact source/dll
  hashes, callback count, physical field3/mask15, canary,
  control0/state6 and failure19/state9-after-authenticated-
  preparation contracts.

**Rejected candidate B**, global VM resolver reinterpretation of
all `__Internal` imports: broader behavior change across hot-update
assemblies, different AOT semantics and unreviewed iOS/WebGL/Windows
portability. The current PInvoke API is documented by HybridCLR
as runtime symbol lookup with macOS support but iOS/WebGL
limitations. This correction is **macOS evidence only**.

## 3. Real generator and source verification

A new pinned four-repo GitHub Actions
`r03-ir-initializer-dynamic-targets.yml` job builds the exact
dnlib fixture generator on Ubuntu24.04 and macOS15 with .NET8
from unchanged HybridCLR Unity provider SHA
`948c0e3b4f8891481301770115e8ba4945eea6de`.
Each OS generates both new targets twice independently,
authenticates real written DLL byte hashes, lengths and MVIDs,
matches both generated reports and explicit import contract,
then compares the actual outputs to the committed Local
`MODE_SHA` pins. It independently fetches the exact native
`PlatformInvoke.cpp`/`LibraryLoader.cpp`/interpreter transform
sources at fixed SHAs and verifies the narrow current-program
lookup branch exists (source-only; not an actual macOS Player).

The first source commit intentionally left the retired V1
target pins in the runner, so the workflow emitted true new
target identities then failed closed. That **preliminary**
failure was expected and is not a Local GO. The second
implementation pins actual emitted identities, tests old
identities rejected and reexecutes the full workflow.
A source-bound generator PASS means deterministic correct
metadata for the **new test input**, not actual dynamic
symbol availability in Unity's loaded GameAssembly.

## 4. One-use-06 Local Validation plan

Conditional fresh root (new name after consumed 05):
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261107-oneuse-06`,
with distinct `-native-host-raw` sibling. Both must be absent,
canonical, on the actual output volume; no alias/relocation
or restoration of owner-retired paths.

Before any runner:
1. Verify four clean canonical Git roots/remote branch heads at
   the **final published 40-character SHAs**, Original-S fc55
   clean registered worktree, surviving source/SDK/custody
   inventories and the recorded *exact authorized retirement
   disposition*. Missing owner-retired raw is Unavailable, not
   silently ignored or counted as Passed; any additional missing
   protected source is a STOP.
2. Require completed/success macOS15+Ubuntu24.04 at the
   same **final demo SHA** for
   `r03-ir-initializer-dynamic-targets.yml`,
   `r03-ir-initializer-local-contracts.yml` and
   `r03-ir-current-native-local-cycle-host.yml`.
   The dedicated source-pinned native writer/managed API
   compilation remains required but unchanged source blobs
   may be accepted only with explicit SHA equality.
3. Independently check installed Unity2022.3.62f2
   macOS arm64 IL2CPP/SDK/dotnet, no competing Unity/Bee/
   Players, the old two original-S archival restrictions,
   current output parent/device, and two **fresh**
   available-byte samples each >=25.0GiB,
   same actual volume, separately timed. Hard20GiB
   and advisory40GiB remain unchanged; no inherited
   permission to lower the floor or purge data. Run
   existing read-only `current_native_environment_admission.py`
   and check both new output roots absent.
4. Execute exactly ONCE the unchanged 15-cell Python coordinator
   `Tools/AssemblyShadow/R03IR/run_initializer_local.py` with
   new `--demo-commit` and root; one real ON/Release
   macOS arm64 Unity IL2CPP build; two separate Players
   (`initializer-control` and `initializer-failure`), each
   with newly attested V2 target and distinct PID.
   Do not retry after error or substitute a consumed DLL/app.
5. Preserve exact signed/source/PID/fixture/hash/MVID/build
   joins, all original native `raw.json` and
   `raw.json.native-trace.jsonl`, native VM
   `raw.json.vm-recovery.json`, phase299/300 entry/read
   and original `Player.log`/exit receipts; untouched
   host negative symlinks and bound archive/strict
   product seal. Original-S historical audits are scoped
   archived-identity only. A passing product seal or
   successful source CI never upgrades failed Players.
6. Publish one NEW additive Local checkpoint
   `Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-06/`,
   update Local-owned `LOCAL_VALIDATION.md` and
   `RETURN_TO_WEB.md`, commit/push evidence, independently
   verify all four live remote heads, and STOP. Any further
   native bridge/PInvoke/metadata failure is a new Primary
   implementation finding. Local does no broad code change.

Expected focused predicates: control Commit0/state6, actual
native OnPrepared callback exactly once, prepared field3
and positiveMask15; failure Commit19/state9 only AFTER the
same authenticated callback and the original precise
`R03IR.InitializerFailure.AfterPublication.V1` VM-recovery
reason. AOT canary before/after1→1 with denied terminal
post-call. A fresh failure to find a native symbol, missing
PInvoke bridge or different exception is FAIL and must
retain first original evidence; not guess or falsely pass.

## 5. Acceptance boundary

Original independent R03 full-stage FAIL, High
`IR-R03-01` and `IR-R03-02`, full native V2/
first-failure/general diagnostics, captured-generic error15,
original-S complete compiler/object/link/Player provenance,
whole-VM epoch, managed shutdown, GC/RSS and RC/P/E
obligations remain open. Even two focused successful
new Players would be evidence for independent review,
**not** full R03 acceptance.
`R03Accepted=false; H2Passed=false;
ReadyForHumanReviewGate=false; runtimeAcceptance=false;
qualificationApproved=false; fullLegacyRegressionAcceptance=false`.
PureInterpreter disabled. No Human Review Gate self-approval,
H2/M08A/X02/SNAP-01, historical rewrite, or
restoration of approved deleted data.
