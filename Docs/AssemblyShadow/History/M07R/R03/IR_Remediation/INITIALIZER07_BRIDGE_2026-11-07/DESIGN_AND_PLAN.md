# R03 initializer oneuse-07 — source-derived Bi4 bridge

**Design and detailed single-use Local Validation plan**  
UTC 2026-11-07. Owner: Primary Implementation. Scope only
`IR-LOCAL-R03-INITIALIZER-06-NATIVE-BRIDGE-01` and the new isolated
initializer Player evidence. No H2/M08A/X02/SNAP-01 or Human Review
Gate action.

## 1. Frozen actual oneuse-06 evidence

One original fresh source-pinned batch at execution demo
`611ad2e45a92ebfbd07cb64238bf2f47b5aff626`; Local published
at demo `7ada3408a2a5f211a7acfdadd06c36a6c48e274c`.
Original Unity2022.3.62f2 macOS arm64 ON/Release IL2CPP BuildReport:
Passed, 0 errors/1 warning. Two actual Players:
control command0017/PID30595 and failure0018/PID30603,
both exit2, real Commit19/state9, native strict V1 raw=0 bytes,
managed verifier NotRun_CommandFailed and retained VM first
error `NotSupportManaged2NativeFunctionMethod`.
No phase299/300 native preparation callback, no field3/mask15
proof, no real original failure sentinel.

The actual `MethodBridge.cpp` was recorded in the build receipt
at SHA `65f2d1993808492e31396c554c7e3301bc338d13a7be4680b55e1745e165c47c`.
Its `g_managed2NativeFunctionPointerCallStub` was only
`{nullptr,nullptr}`. The isolated build's hot-update analyzer assembly
set was empty and the target fixture still appeared as AOT
baseline. This is consistent with the exact runtime fallback
`NotSupportManaged2NativeFunctionMethod` for signature `Bi4`.

Ten real native host components, 47 initial host tests, existing
S archived-identity audits, signed source/install/provenance and
the original product seal Passed **within their own scopes**
(451 indexed members). These do not override the failed Players.

All oneuse01–06 execution data/verdicts are immutable. The
17 user-authorized retired old runtime roots and 40 explicitly
retired duplicate paths remain
`Unavailable/PermanentlyDeleted_UserAuthorized`, not secretly
restored, rehashed as present, or regenerated. Historical strict
custody remains Blocked. All other protected inputs must still
pass exact before/after preservation. No Local retry of06.

## 2. Independently inspected source boundary

- `hybridclr_unity/Editor/Commands/MethodBridgeGeneratorCommand.cs`:
  normal generator calls `PInvokeAnalyzer` only on selected
  hot-update assembly names. The isolated builder deliberately
  provides no such names, so normal generation has no
  interpreted fixture PInvoke to analyze.
- `hybridclr_unity/Editor/MethodBridge/{PInvokeAnalyzer,Generator}.cs`:
  the `Cdecl` static no-argument `int32` return signature is
  `Bi4`; the generator's exact native ABI wrapper body is
  `typedef int32_t (CDECL *NativeMethod)();`
  and the native function-pointer table row must be
  `{"Bi4", __M2NF_Bi4}` with a null terminator.
- `hybridclr/interpreter/InterpreterModule.cpp` maps
  `g_managed2NativeFunctionPointerCallStub` keys at
  startup, otherwise raising
  `NotSupportManaged2NativeFunctionMethod`.
- Original`R03/PlayerProject/R03Build.cs` calls
  `PrebuildCommand.GenerateAll()` under a fixed empty
  hot-update list and then BuildPipeline.BuildPlayer.
  Original `SourceInstaller` and general Product/VM
  source must be retained, not changed.

Chosen fix: **initializer-only source-verified bridge augmentation
AFTER the ordinary generator** in the newly isolated project.
This does not promote Methods to a hot-update build input, does
not change non-initializer builds, does not invent a global
fallback bridge and does not modify production HybridCLR forks.

## 3. Exact source implementation

A small test-only helper
`R03IR/PlayerProject/R03InitializerBridge.cs`:
- Is copied into `Assets/Editor/R03InitializerBridge.cs`
  *only* by the fresh initializer source preparator; an exact
  SHA-bound manifest and configuration records it.
- Opens the two separately generated V2 Methods DLLs with actual
  dnlib. Verifies both existing SHA256/MVID, Methods assembly
  identity, one and only one `R03.TerminalWitness.RecordPreparedInNative`
  static PInvoke, `__InternalDynamic` import module,
  `R03_IRW_OnPrepared` exported entry, Cdecl/NoMangle,
  zero arguments and int32 return; rejects any unexpected
  extra import, duplicate/same fixture, mutated SHA/metadata.
- Requires the ordinary new build to have produced
  `hybridclr/generated/MethodBridge.cpp` with exactly one
  **null-only** managed-to-native function-pointer table and
  no Bi4 preexisting; otherwise fails without replacing
  unrelated bridge signatures.
- Inserts exactly one source-derived native wrapper
  `static void __M2NF_Bi4(...)` using
  `typedef int32_t (CDECL *NativeMethod)();`, and table
  `{"Bi4", __M2NF_Bi4}, {nullptr,nullptr}`.
  Source bytes before/after SHA256, duplicate uniqueness and
  original generator contents are checked.
- `R03Build.cs`, shared with old R03 stages, invokes this
  helper by reflection **only when** the new explicit isolated
  `R03IR.Managed2Native.Cdecl.Int32NoArgs.V1` contract exists.
  No contract means no reflection target or change to the
  historical path. The existing AOT baseline and empty
  hot-update selection are untouched. The actual build
  receipt records new signature, fixture identity and the
  generated source SHA, which is rechecked after BuildPlayer.
- The Local source-bound BuildReceipt validator checks the
  actual post-build generated bridge table, original build
  source manifest, corresponding GameAssembly.dylib bytes,
  and both native `_R03_IRW_BridgeStatus` and
  `_R03_IRW_OnPrepared` exports, without calling this an
  accepted runtime result.

**Linked runtime witness**:
`R03InitializerPreparedProbe.cpp` adds AOT export
`R03_IRW_BridgeStatus()`. The real compiled function reads
the *same linked native* managed-to-native function-pointer
array consumed by InterpreterModule; bounded scan requires
one `Bi4` entry, a nonnull call target, unique match and null
terminator. The existing managed AOT observation Player
calls this via `DllImport("__Internal")` **before Commit**,
emitting new native phase103 with result1. The strict phase
verifier requires this exact positive runtime observation,
then the original real callback299/300, field3, mask15,
one callback, control0/6 and failure19/9 with intended
postprepared sentinel. A source-only or nm-only string
cannot substitute for phase103.

All original strict first error, safe native journal,
`raw.json` and `raw.json.vm-recovery.json` transports,
canary1→1 and denial of postterminal AOT activity remain
unchanged. The new verifier never grants R03 acceptance.

## 4. Source/host tests and limitations

- Real .NET8/dnlib generator builds the exact V2 control and
  failure fixture, then a small host adapter compiles and
  invokes the *actual test-only C# bridge helper* against both
  real DLLs and the actual checked-in original
  `hybridclr/generated/MethodBridge.cpp`. It validates exact
  generated wrapper/table via C++11 clang/g++ and executes a
  native HostStub function that must return the correct int32
  through the generated managed-to-native call path.
- Host tests reject old/mismatched SHA, reused table, malformed
  source, source manifest duplicates, missing input,
  symlinks, missing Bi4 and a null-only linked mock.
  No Unity process/Player is run in CI.
- The pinned Unity Editor API compile verifies R03Build
  against real Unity2022.3.62f2 APIs; a separate legacy
  broad Player API compile may fail at an unrelated
  older R03TerminalPlayer reference to a missing
  R03EngineFrameDispatcher source input. Such a failed
  broad suite is NOT silently called a bridge PASS.
  A complete macOS Player build/link/runtime must still
  be performed by Local Validation and is the only way
  to close the live bridge observation.
- Exact source/host two-OS GitHub Actions
  `r03-ir-initializer-bridge-host.yml`,
  `r03-ir-initializer-local-contracts.yml`
  and `r03-ir-current-native-local-cycle-host.yml`
  must all pass at the **same FINAL pushed demo SHA**.
  Native observer and host writer compiles are also required
  with exact byte-identical inputs; old compiled-Player
  managed import change may require a fresh managed API
  compile, never infer byte equality when it changed.

## 5. Single-use Local Validation plan

New, never previously created root:
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261107-oneuse-07`,
and its genuinely separate `-native-host-raw` sibling.
Do NOT use consumed01–06 roots, old apps, old fixtures or
deleted historical paths.

**P0 read-only admission**:
- Read current `README.md`, the canonical
  `Handoff/WEB_TO_LOCAL.md`, this design/plan and
  `PRIMARY_SOURCE_REVIEW.md` and original oneuse06
  Local findings and raw recovery.
- Verify four exact clean Git roots/branch/upstream HEAD,
  unchanged interpreter/native/package pins and final
  demo source-pinned SHA, registered detached original-S
  `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`
  and all surviving SDK/Unity/custody evidence.
  Explicitly reconcile the 17 user-authorized retired
  raw roots: Unavailable, not a new defect, *nor*
  falsely rehashed as present. Any other missing
  protected file => STOP.
- Check actual Apple Silicon Unity2022.3.62f2 IL2CPP,
  SDK/dotnet/C++11, no competing Unity/Bee/Players,
  previously preserved older sources, both new
  product/host roots *absent*, physically canonical,
  and two genuinely fresh separated available-space
  measurements each >=25.0GiB on the same
  volume (hard20GiB/advisory40GiB unchanged, only
  conditional 25–40GiB oneuse07 exception).
  Run unchanged `current_native_environment_admission.py`
  read-only with final new demo SHA. Wrong/missing
  head, source/fixture, status, CI, capacity or
  original-S/custody gate => BLOCKED/STOP.
- The three exact-final-source two-OS CI passes,
  focused native/managed bridge compile evidence,
  and the explicit fixture pinning are mandatory;
  source-only CI is never enough to claim Local success.

**P1 one authorized run only**:
With actual independent GO, invoke precisely ONCE
`Tools/AssemblyShadow/R03IR/run_initializer_local.py`
with canonical workspace/original-S/unity, new root
and final exact demo SHA. Fixed 15 cells only,
genuine ten native host suites and source tests,
original S read-only archive/90-cell/59-join/
Mach-O audits, two deterministic V2 targets,
one real macOS ARM64 ON/Release Unity IL2CPP
build, and two separate real native Players.

**P2 linked bridge and Player evidence**:
- New BuildReceipt must confirm generated Bi4
  wrapper/table source, SHA after Prebuild and
  after actual build, and complete source/install
  provenance. Verify actual linked GameAssembly
  and the exported native bridge probe/callback.
- Each real Player must independently execute
  `R03_IRW_BridgeStatus` in actual GameAssembly:
  phase103=1. Then prove phase299/300 real native
  callback once, physical field3 and mask15,
  control Commit0/state6, failure Commit19/state9
  only AFTER authenticated prepared callback and
  expected
  `R03IR.InitializerFailure.AfterPublication.V1`
  first-failure reason. Distinct PIDs/nonces,
  fixture SHA/MVID, request, independent build
  receipt, real output raw, first recovery and
  phase journal, original terminal canary constraints.
- A failed command (exit2 or any other nonzero)
  retains `NotRun_CommandFailed`, empty raw bytes
  when present, all actual diagnostics and no
  simulated or host-only semantic PASS.
  Host custody, independent product seal and
  historical audit pass only their own scopes.

**P3 publication and STOP**:
Create a new additive checkpoint
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-07/`,
without rewriting original01–06 or owner-retired artifacts.
Record source execution SHA vs evidence publication SHA,
CI/SDK/capacity gates, exact 15-cell matrix, native
Bi4 provenance, both real Player outcomes/first
error and independent before/after source/custody.
Update Local-owned `LOCAL_VALIDATION.md` and
`RETURN_TO_WEB.md`, commit/push and independently
verify all four live remote heads, then return to
Primary. No additional build/Player replay, broad
VM refactor or advancing milestones.

## 6. Immutable acceptance boundary

Independent full R03 review FAIL and High
`IR-R03-01/IR-R03-02` remain open. Captured
generic error15, full native V2 and coherent
whole-VM epoch, original S full compiler/link/
Player evidence, managed shutdown, GC/RSS,
RC1–RC6, P1/P2/E0/E1/P3, performance and
full legacy regression acceptance remain open.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`,
`qualificationApproved=false`,
`fullLegacyRegressionAcceptance=false`,
PureInterpreter disabled. No Human Review Gate,
H2/M08A/X02/SNAP-01, or self-approval.
