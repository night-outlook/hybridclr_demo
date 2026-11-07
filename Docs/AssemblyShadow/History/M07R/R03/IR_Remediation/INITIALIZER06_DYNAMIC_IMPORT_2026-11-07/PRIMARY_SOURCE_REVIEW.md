# Primary source review — R03 initializer interpreted import v2

Date 2026-11-07 UTC. Owner: Primary Implementation; NOT independent full-stage
review or Human Review Gate.

## Evidence and comparison

Original once-executed oneuse-05 demo
`db232418adf2fc35c54ed72a8933a174f8218126`,
published at `eeeec3ba574047c06b5b853e58a5b594e80c37ae`,
reported two separate real Players (PID23120/23133)
both exit2, strict output empty, no native callback,
and exact native VM recovery
`Unable to load DLL '__Internal'` with
`dlopen(__Internal,0x0005)`. Both control and failure
returned code19/state9; their source-bound native
journal/custody seals passed separately but did NOT
establish initializer behavior. The preceding 05
capacity readiness issues, owner-authorized retirement
of 17 old raw roots/40 duplicate paths, and
historical strict custody Blocked remain separate
factual records. The deleted roots remain Unavailable.

Source independently read:
`InitializerNativeTargetFixtures.cs`
emitted `ModuleRefUser(module,"__Internal")`;
`hybridclr/transform/TransformContext.cpp`
resolves interpreted `PInvoke` via
`il2cpp::vm::PlatformInvoke::Resolve`;
`il2cpp_plus/libil2cpp/vm/PlatformInvoke.cpp`
special-cases exact `__InternalDynamic` to
`LibraryLoader::LoadDynamicLibrary(Empty())`
and treats ordinary `__Internal` as a library
name; `os/LibraryLoader.cpp` maps empty
name to `OpenProgramHandle`. This proves
the producer/resolver contract mismatch
for the named library failure reported by
the actual Player. It does NOT prove
new current-process symbol visibility
or bridge availability in the Player.

## Scoped modification

Only the **opt-in initializer test fixture**
import is changed to the existing, exact
`__InternalDynamic` dynamic-import token.
Native entry `R03_IRW_OnPrepared`,
PInvoke no-arg/int32, NoMangle/Cdecl and
fail-closed Ready->callback->initializer
IL are unchanged. An in-memory negative
mutation from the valid fixture to the
retired `__Internal` ModuleRef must fail
the **specific** generator verifier message.
No global PlatformInvoke VM rewrite,
new native call ABI, existing historical
fixture rewrite or deterministic original
S/K data change.

Producer now declares
`R03IR.InterpreterCurrentProcessImport.V2`
in its receipt, emits newly generated
identities and new MVID v2 namespace.
The Local runner and read-only Mac
admission pin the entire new producer
source blob, exact current target
SHA256 and MVID per mode, and reject
unreviewed module metadata and past
v1 target hashes. Original control0/6,
failure19/9 only after authentic
prepared callback and sentinel,
field3/positiveMask15/callback1,
AOT canary1→1 and native strict V1
remain unchanged.

## Real host evidence, not Unity

At initial source commit
`7e53f193cf7453e92856ca307e628ba93a35ab03`,
an actual .NET8/dnlib generator
ran twice on macOS and twice on
Ubuntu with the same pinned package
and native-resolver source. Both
platforms independently attested:

| Mode | SHA256 | MVID | Bytes |
|---|---|---|---:|
| initializer-control | `d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e` | `5bb6e17a-09b9-5b29-dac2-41d3519f76f4` | 2560 |
| initializer-failure | `6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370` | `f61d7325-6d38-4640-5873-37371f587b16` | 2560 |

The **first attestation CI intentionally failed**
because the runner still had V1 pins,
after printing the actual new identities.
Primary then updated the strict runner
to those actual values, added negative
legacy-identity/source controls, and
recompiled the mutated-import verifier.
Exact-code SHA after this pinning:
`51d484b5827a4c0bb2d8529bd37244444cb791a1`.
Real source host run
[42329883018](https://github.com/night-outlook/hybridclr_demo/actions/runs/42329883018)
completed PASS on macOS15/Ubuntu24.04
with genuine repeat generation and
all new runner identities. [Initializer
host 42329882908](https://github.com/night-outlook/hybridclr_demo/actions/runs/42329882908)
also passed both OS. Current-native full
host evidence is a **distinct** workflow.

The final **documentation SHA** must
again complete the three exact-source
two-OS workflows before Local dispatch.
No code-side or previous CI is allowed to
override an unsuccessful final SHA.
GitHub host work cannot compile the
actual Unity Player here.

## Tradeoffs and remaining risk

**Chosen narrow option:** use the existing
interpreter current-process import token
in one controlled test DLL. Source/host
evidence justifies it; Mac OS actual
`GameAssembly.dylib` symbol lookup
must be tested by a real fresh Player.
Possible next failure: missing managed-
to-native bridge, hidden export,
different initializer exception, or
unexpected side effect. All remain
unknown until genuine Local execution.

**Rejected general rewrite:** map every
runtime `__Internal` in PlatformInvoke
to the process handle. That changes
PInvoke behavior for every interpreted
assembly and potentially unsupported
platforms, beyond the R03 finding;
there is no evidence authorizing it.
HybridCLR's public PInvoke guidance
lists macOS support but not iOS or
WebGL for this runtime lookup mechanism.

Original05 remains FAIL/ReturnRequired,
and all earlier PASS/FAIL/Blocked/
NotRun/Unavailable conclusions retain
their historical scopes. Original
independent High `IR-R03-01/02`
remain open; native V2, captured generic,
whole VM epoch, original-S compile/link
chain, managed shutdown, GC/RSS,
RC/P/E and performance are unproven.
`R03Accepted=false; H2Passed=false;
ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`;
PureInterpreter disabled.
