# M06 execution semantics evidence report

Status: pending the final Release fixtures, 28 fresh Player cases, post-Player
closeout validation, two deterministic full gates and local tag audit. The
source/build facts below are frozen evidence, but they do not yet accept M06.
M07 implementation remains closed.

## Scope and source identity

M06 implements executable constructor/static/module-initializer behavior,
inheritance and virtual/interface dispatch, delegates/events, generic and struct
bridges, exceptions, async/iterator/coroutine state machines, explicit generator
inputs, first-use warmup and a physical baseline-method execution guard. It does
not implement the M07 Unity serialized-resource boundary.

The immutable executable revisions are:

| Repository | Revision |
| --- | --- |
| hybridclr | `a19db144751f4f016769b90e61a80b8c27578678` |
| il2cpp_plus | `6613a02feaf7774b14fb1b57d20a72812bde0434` |
| hybridclr_unity | `8d2e811fb37f4427ea15321369c883a61975a57d` |
| demo | `88b4f9145430f9993eb49c1e6854e377ce7ea345` |

Demo metadata commit `9cac0c9d8ba03e30cf2b084278c0c2c1b1676f54`
pins those exact revisions and changes no executable input. The complete M05-tag
delta is recorded in [M06-source-inventory.json](M06-source-inventory.json); the
human-readable boundary is [M06-file-and-api-inventory.md](M06-file-and-api-inventory.md).

All work occurred in `/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow`. The
original `/Users/ah/GitHub/hybridclr/hybridclr_demo` checkout and its pre-existing
Unity Editor PID 13313 were never adopted or controlled.

## Execution guard and diagnostics

The native boundary uses physical published baseline identity rather than
assembly name or token alone. `AssertMethodIsActive` fails closed before the
supported Runtime::Invoke, interpreter, nested opcode, delegate, generated
virtual/interface and generated reverse-PInvoke paths can execute a baseline
candidate method. It preserves the first failure as code 21,
`BaselineMethodExecution`. Ordinary direct nonvirtual AOT calls remain excluded
by the reverse closure/fixed-AOT policy; M06 does not add per-AOT dispatch stubs.

The eleventh public API, `GetExecutionDiagnosticsJson(out string)`, returns a
separate strict schema-1 document. It does not mutate transaction state or
manufacture classes/static storage. Development may expose pointer details;
Release reports those fields unavailable. Method/class-initializer/transformation
counters are actual native observations, not inferred from elapsed time.

The final native correction had two direct causes:

- The M05 layout predicate compared `native_size` for reference types, so a
  legitimate delegate with matching managed shape could be rejected. M06 now
  keeps exact native-size comparison for value types and the serialized/layout
  field boundary for reference types.
- `GlobalMetadata::FromTypeDefinition` could materialize a staged/active type
  outside the Shadow metadata scope. The corrected function opens an
  `AssemblyShadowTypeMetadataScope`, retaining the active physical image through
  class creation. A native regression test exercises this path.

Both changes are inside the exact pinned native revision above.

## Byte-bound generation plans

Development and Release each have five generation-only plans: `Ordinary`,
`P01`, `P02`, `P03`, and `InitializerFailure`. Every plan binds target,
architecture, source revisions, compile snapshot and policy hashes; provider-
first closure/load order; explicit ordinary and selected DLL/PDB identities;
the stripped-AOT input inventory; Link, MethodBridge/reverse-PInvoke and
AOT-generic outputs; startup/execution policy; and generated output hashes.

The P03 Player output was selected only after P01, P02 and P03 coverage
comparison. Candidate names were not globally added to the Player hot-update
filter. The installed P03 outputs were checked before and after IL2CPP, so a
Player-side generator overwrite cannot be mistaken for the recorded inputs.

Development generation proof:

- path: `_temp/AssemblyShadow/M06Generation-6376dac0b694491d909315b135b8c3a9/m06-generation.json`
- SHA-256: `92d41e395f77eeb7c38b62545dc8d0cf945d69ffa66303f04106925f00a28f84`
- baseline: `M06-Baseline-v7`
- mode: Development
- selected plan: P03
- ordinary baseline compile snapshot:
  `de0ac176d6f3174cba110afabfed707d3cd645696935002bbead47240d9d6db1`

Release generation proof:

- path: `_temp/AssemblyShadow/M06Generation-ade540d4ee4e4d9d9bd3c85073830d17/m06-generation.json`
- SHA-256: `f8aef74cc15320c64924b6639d47774e5bb244e50f20957d2c4f14a48af6eddb`
- baseline: `M06-Baseline-Release-v7`
- mode: Release
- selected plan: P03

The retained generation archives include all plan/output receipts and generated
Link/bridge/AOT-generic bytes. They intentionally exclude the reproducible
multi-gigabyte compile/IL2CPP work directories; all excluded DLL/PDB/source
graphs stay at immutable local paths and remain covered by receipt hashes.

## Development Player pair

The genuine native-ON Development Player is
`Builds/AssemblyShadow/M06/M06-Baseline-v7.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-d0443d0087b846a18b4cbf525887e6c9`.

- input snapshot hash:
  `f776efd7981d46facd2a294dd079c5a4e3ea3ea0fe371d0c29df19c6899c6b69`
- GameAssembly SHA-256:
  `989884edb0cedc3d1158cffdafe0c658800b7af7994f95b433020f1e5b2de0fd`
- type-proof SHA-256:
  `0400f57d99788be1022a313e7621078b1861a3300f599494fe0f463a08b259bf`
- execution-proof SHA-256:
  `94c44e69db6558775af2b3a089fc41e7639dcd4f0e581126dd5c8ea4bb84651e`
- Player-receipt SHA-256:
  `55a11ef3bf2b8709f48646f3a31b645ae8937fc404f8f1c2610f34e4a695fda9`
- baseline-manifest SHA-256:
  `9e02097d14d6b2b5c71d2517feafd6b277081329352d3654a3c998752c00fe72`
- runtime ABI:
  `82e67fdd1134e105c4e4da4012cc9405ef7b4a561dab10260b400b0a25ab8ef2`
- resource ABI:
  `sha256:255458bf49ed437c208aa8acf2b139825ff0cbb11d70e4a45d1d1459cd7d7973`

The genuine native-OFF Development Player is
`Builds/AssemblyShadow/M06/M06-Baseline-v7-NativeOff.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-b0ac61d48df24880a94434c49f71c985`.

- input snapshot hash:
  `70e0f79840d0b646decc09c6cc1d8a21325858a0299f6cb9c1ea36b0e7eb50b0`
- GameAssembly SHA-256:
  `607178772810e0838cac98d411118cc097fd6b339e961d3fe91675c1de417a40`
- type-proof SHA-256:
  `8265030c34f700adc0da62a80fe9cc1f126d75fd259f3d09bd69587d5e14a03f`
- execution-proof SHA-256:
  `cbf4ebfe5a9c7bb6e1783dc5003badf65bc56dc360545e507be5a288e6ad9f6f`
- Player-receipt SHA-256:
  `58748960e9aac53c33cac7567b0f9eb9de7473da590829ba228de91250f5afa1`
- build GUID: `2bcfbe459176400fb67f9188f58cc887`

The ON and OFF builds have distinct GUIDs, executables, native libraries,
metadata/snapshot graphs and native identities. Their managed assembly
projections are exactly equal; native identities are deliberately distinct.
This prevents a feature-flag build from being accepted merely because the same
managed names appeared in both snapshots.

## Development fixtures and replay

The Development fixture root is
`_temp/AssemblyShadow/M06Fixtures-88145bf85f4a4de887232554027d108a`.

- fixture-manifest SHA-256:
  `f222d5c4c2d0aa1f3ad48547270465f46ead58aecd9d706d1bdfe136430aa685`
- independent replay SHA-256:
  `6e2eaaaa1e05e63a16d13e0db5f19846f3061da9e47f5ebbeb1767ea6a04191b`
- patch file counts: P01 11, P02 15, P03 19, InitializerFailure 11

The replay uses a separate scratch root, recompiles and compares every fixture
artifact, and checks compiler mode, closure/order, resource ABI, raw type
admissions, reflection binding, warmup and generation plan identity. It is not
the same call stack that publishes the fixture manifest.

## Release Player and no-PDB provenance

The genuine Release Player is
`Builds/AssemblyShadow/M06/M06-Baseline-Release-v7.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-4c2ea626ceba4ee2866a2d0bb9748ecf`.

- input snapshot hash:
  `4afb7d3fb57d5c5eedaabb94aab37843fa7b68d99f2ca352cc5464f2a1558752`
- GameAssembly SHA-256:
  `cb6a1d8bc50cf4ec4de709b02a1860a0338ed0dd5e9701a48fe7b856512a8811`
- build GUID: `5ec3affbf8c44efe8a13d489a27c41d7`
- type-proof SHA-256:
  `02a651ad46bdeb5df853c0b519d373e3c5c2a93f83915304a094501fbf0275a8`
- execution-proof SHA-256:
  `edfa47a1f72eee38606353903222df15c9904b101b02b3b126b4583a7728e71c`
- Player-receipt SHA-256:
  `ba0b76e26bd1765776e6bfc9caa5a73c4bf08845bfa4acdef2228f67f22c3397`
- baseline-manifest SHA-256:
  `ef364faba2dc012c481d8784cf5e3792245cef46747145dba633543c071a3e7b`

The Release generation/Player is not a relabeled Development build. Its fixture
and independent replay remain pending at the time of this draft. The final
T06-13 process must bind this exact no-PDB graph and correlate type/method token
evidence without claiming runtime ModuleVersionId support.

## Static, Editor, Python and native evidence before final closeout

The combined Unity Editor suite passed 874/874 with no failed, skipped or
inconclusive cases. The preserved XML is
`_temp/AssemblyShadow/EditorTests-1bcd5d94bc974a4bb5d5c66b8a8ab34b/results.xml`.

The full Python suite passed 335 tests with one intentional skip when the real
M05 compiler environment was not supplied. Final closeout is configured with
the preserved 36-DLL compiler root and exact raw-admission configuration; it
must rerun without skips before acceptance.

The corrected M06 native runner passed 824 checks, including 20 translation-
unit syntax checks and 1,080 recorded dependencies. Its receipt is
`_temp/AssemblyShadow/m06-native-featureoff-fix-20260904020543.json`. The
corrected M05 native layout runner also passed with 34 syntax checks at
`_temp/AssemblyShadow/m05-native-layout-fix-20260904020658.json`.

Pinned installation repeatability passed, with install receipt SHA-256
`03f5e092f8eaca77124c68fc0319d5e116af51da81e88d9b6c12207bd28ec7ff`.
A clean detached source verification checked 940 source files and 942 installed
files, current demo-source identity and native mode ON. Final closeout will
repeat installation, all M03/visibility/M04/M05/M06 native suites, the full
Editor suite, full unskipped Python suite and installed-source verification.

## Final runtime and gate boundary

Pending. Acceptance requires all of the following from the frozen artifacts:

- a genuine Release fixture manifest and independent replay;
- 28 complete actual Player modes, 28 distinct operating-system process IDs,
  zero timeouts/exits, unchanged input hashes and every raw diagnostic/log;
- a separate strict verifier receipt with `result=Passed`, `caseCount=28`;
- fresh unskipped full Python, full Editor, five native suites, repeat install
  and installed-source verification with native ON restored;
- deterministic lossless evidence archives and byte-identical selected copies;
- committed evidence, Gate A current-checkout PASS and Gate B clean detached-
  commit PASS;
- exact post-closeout audit and matching local annotated four-repository tag.

The two gates are independent deterministic implementations/processes, not
independent human or LLM reviewers. Gate A reruns the strict and installed-source
verifiers over the current immutable roots. Gate B runs from a clean detached
evidence commit, reruns the full Python and strict verifiers, and independently
reads every archive member, copied artifact, original hash and Git blob.

## Limits

Acceptance, once complete, is bounded to macOS ARM64 and Unity 2022.3.62f2
IL2CPP. Receipts are unsigned and locally bound. Runtime ModuleVersionId remains
unsupported; offline byte MVID/token/PDB evidence is not a runtime identity.
The finite acquisition/policy scanners and native adapter suites do not prove
arbitrary whole-program reflection or every platform/concurrency path. Single-
machine timings demonstrate ordering and transformation deltas, not production
frame-time or managed-allocation guarantees. M07 serialized Unity resources,
asset lifecycle and resource-catalog authorization are not accepted by M06.
