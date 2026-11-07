# Primary source review — initializer oneuse-07 Bi4 bridge correction

Date: 2026-11-07 UTC. Review role: Primary Implementation,
not an independent R03 full-stage review, actual Local Unity
Player validation, or Human Review Gate.

## 1. Raw evidence and independent code trace

Read:
- `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md` and actual
  `History/M07R/R03/local-validation-initializer-20261107-oneuse-06/`
  Local receipt, finding, original commands, generated
  MethodBridge source inventory, both raw/recovery traces
  and original product seal.
- Exact native fork sources for
  `hybridclr/interpreter/InterpreterModule.cpp`
  and `hybridclr_unity/Editor/MethodBridge/{PInvokeAnalyzer,Generator}.cs`,
  plus build command `MethodBridgeGeneratorCommand.cs`
  and `R03/PlayerProject/R03Build.cs`.

Conclusions supported by the real oneuse06 evidence:
  source demo `611ad2e45a92ebfbd07cb64238bf2f47b5aff626`
  later Local publication `7ada3408a2a5f211a7acfdadd06c36a6c48e274c`;
  one actual successful macOS ON/Release IL2CPP build,
  both distinct Players exits2/PIDs30595,30603,
  Commit19/state9, no native callback, empty strict V1.
  Both original VM recovery reasons are precisely
  `NotSupportManaged2NativeFunctionMethod`.
  The original installed generated bridge source was
  a null-only managed-to-native pointer table,
  SHA256 `65f2d1993808492e31396c554c7e3301bc338d13a7be4680b55e1745e165c47c`.
  Source metadata derives `Bi4`; old isolated
  normal hot-update generator had an empty analyzed
  hot-update assembly list. This directly explains
  the missing bridge fallback, while the **exact
  linked table was not independently inspected**
  by that consumed runtime batch.

## 2. Implementation findings and corrections

Narrow patch to test-only R03 isolated build:
- Preserved exact `PrebuildCommand.GenerateAll`,
  empty analyzer hot-update list and existing
  AOT physical fixture roles. Never turn Methods
  into a hot-update build assembly to force a wrapper.
- `R03InitializerBridge.cs`, copied solely to
  the *fresh* isolated initializer project's
  `Assets/Editor`, opens and checks actual
  pre-generated DLL bytes/MVID + Cdecl int32()
  PInvoke metadata with dnlib and source SHA pins.
  It strictly requires one untouched generated
  null-sentinel table, then adds the original
  Generator-equivalent `__M2NF_Bi4` native wrapper,
  exactly one `{"Bi4", __M2NF_Bi4}` and keeps the
  null sentinel. Whole source SHA is checked
  immediately and after actual BuildPipeline.
- Shared `R03Build.cs` remains compilable for
  older standalone builds through optional
  reflection only on the new explicit
  `initializerBridgeContract`; missing contract
  causes no new import or generated file change.
  Source Installer and native product forks
  stay unmodified.
- `prepare_initializer_sources.py` copies and
  source-authenticates the new helper, the V2
  target paths, SHA and MVIDs into the isolated
  build config. The main runner requires its
  specific BuildReceipt/hash/source identities
  and separately checks actual built
  GameAssembly native exports.
- Actual linked native probe
  `R03_IRW_BridgeStatus` checks the compiled
  managed-to-native function-pointer table
  *at runtime*, bounded to 64 entries, with
  one and only one non-null `Bi4` target
  before any transaction Commit. AOT managed
  Player records probe result in phase103;
  complete phase verifier now requires
  phase103=1 and original callback299/300,
  fields/mask/Commit/canary predicates.
- No old acceptance predicates or older
  source/fixtures/evidence were relaxed.

## 3. Source-side validation

The new CI workflow
`r03-ir-initializer-bridge-host.yml` compiles
the actual new C# bridge helper using .NET8
and dnlib, parses the real current V2 control/
failure DLL files, modifies an original normal
generated bridge .cpp and compiles/calls that
exact generated wrapper as C++11 on both
macOS and Ubuntu against a self-contained
host ABI shim. This covers byte/metadata
mismatch, duplicate generation and the
Cdecl int32 function pointer invocation,
not actual Unity linking.

Additional host tests exercise the
source preparator, strict record joins,
real C++11 native observer with positive
and null-only negative linked table,
native writer and strict native phase
diagnostics. Earlier CI attempts found
small **host test harness** issues:
synthetic trace ordering after phase103,
new appended Editor manifest item,
macOS temporary canonical paths,
static assertion comments and the
writer-only synthetic phase103.
Primary corrected these; no runtime
evidence or guard was relabeled.
All earlier failed/cancelled CI remains
historical and is NOT source acceptance.

The official pinned Unity2022.3.62f2
build-helper API workflow on the
first code source commit compiled the
real `R03Build.cs` to a successful
`R03Build.dll` (verified independently
from the raw GitHub Actions ZIP).
Its broader subsequent
`R03TerminalPlayerApi` compilation
failed on pre-existing missing
`R03EngineFrameDispatcher` in that
separate response-file input set.
That workflow was **not** a successful
end-to-end official API run; no claim
of complete Unity compilation is made
for the new helper. The separate
BridgeHost compiled the new helper.
The next actual Unity Editor/IL2CPP
compile and linked Player remain
mandatory Local Validation.

**Final source-commit gate:** require
completed/success macOS15 + Ubuntu24.04
jobs at the exact FINAL pushed demo
SHA for each of:
1. `r03-ir-initializer-bridge-host.yml`.
2. `r03-ir-initializer-local-contracts.yml`.
3. `r03-ir-current-native-local-cycle-host.yml`.

Previously green code-side CI is insufficient
for a newer documentation commit. The
native observer/managed AOT Player exact
unchanged-source-blob build checks are
supplementary; cancelled unrelated
macos14 jobs cannot be relabeled Passed.
Every source CI is host-only, not a new
actual Unity Player.

## 4. Risk assessment / unresolved proof

Source helper may still fail when the
actual Unity installed native tree contains
unexpected bridges or when BuildPipeline
regenerates/overwrites the managed-to-native
table. These will produce explicit failed
BuildReceipt and preserve original editor
errors. A linked GameAssembly may differ
from the source-only table; the new
`R03_IRW_BridgeStatus` real in-process
probe must be observed before any
callback/positive field can pass.
The interpreter may subsequently find a
different execution error or runtime
validation defect even with Bi4 available.
No actual new Unity Player is available
to Primary: no prototype or host synthetic
record can assert the VM failure has been
fully fixed.

oneuse01–06 immutable, 17 retired old
roots and 40 duplicates
`Unavailable/PermanentlyDeleted`,
strict historical custody Blocked.
Original High R03 IR-R03-01/02, native V2
complete diagnostics/first recovery,
captured generic failure15, whole VM
epoch, managed shutdown/GC/RSS,
original-S full compiler/object/link/Player
join, RC/P/E/qualification remain open.
`R03Accepted=false`,
`H2Passed=false`,
`ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`,
`qualificationApproved=false`,
`fullLegacyRegressionAcceptance=false`,
PureInterpreter disabled.
