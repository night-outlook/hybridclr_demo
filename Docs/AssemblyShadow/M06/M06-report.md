# M06 execution semantics evidence report

Status: the final v8 Development/Release artifacts, 28 fresh Player cases,
strict runtime verifier, and post-Player closeout are complete. Five lossless
archives and 53 selected copies are sealed in `Evidence/artifact-index-v8.json`.
The two deterministic commit gates and local tag audit remain before final M06
acceptance; M07 integration remains closed until those gates pass.

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
| il2cpp_plus | `5b12ee96e574999d0eb82a6200d95a5b63c7fcfc` |
| hybridclr_unity | `8d2e811fb37f4427ea15321369c883a61975a57d` |
| demo | `e1ab1ca512dfd12642c333094d884808ff757fc9` |

Demo metadata commit `1311e7c5fb9da4769260529bb561661aa335b198`
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
- Reflected `MethodInfo` objects could still carry a baseline declaring-class
  method after the logical type had been remapped. The final native correction
  canonicalizes reflected methods through the active shadow type before invoke,
  and the demo regression sources exercise the same-name method path.

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

- path: `_temp/AssemblyShadow/M06Generation-121a2a74c5f844b2b09b0f3e49e24eef/m06-generation.json`
- SHA-256: `1227c19d072c959f8d29d30922348668ffcbe7bc596f444595e4f20224fddefb`
- baseline: `M06-Baseline-v8`
- mode: Development
- selected plan: P03
- ordinary baseline compile snapshot:
  `3d2f3441d18a80bda68d2ea54813058364b04ad04ff0aee8e280da2dfefd8548`

Release generation proof:

- path: `_temp/AssemblyShadow/M06Generation-b451aea0e0934b46b0fab0ecfb54b889/m06-generation.json`
- SHA-256: `21baab4511c50e2b3b5b4de8a909e49eab15b182acf6ce7992d989d0d703a95d`
- baseline: `M06-Baseline-Release-v8`
- mode: Release
- selected plan: P03
- ordinary baseline compile snapshot:
  `01247b20ca55c3ab85eba7dc673e33e0b0c6bbc18132c15ddf26ec1ef43630fa`

The retained generation archives include all plan/output receipts and generated
Link/bridge/AOT-generic bytes. They intentionally exclude the reproducible
multi-gigabyte compile/IL2CPP work directories; all excluded DLL/PDB/source
graphs stay at immutable local paths and remain covered by receipt hashes.

## Development Player pair

The genuine native-ON Development Player is
`Builds/AssemblyShadow/M06/M06-Baseline-v8.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-c93706fc8db048a3b593539ea4c68477`.

- input snapshot hash:
  `4b53c4bd41b7187761cb0d08cee6ea5223778efb151d0dc5818a78f66e815560`
- GameAssembly SHA-256:
  `ee0c3686ff10dec63ed6d596597adc00127181f92fd28570af9f99b31290909c`
- type-proof SHA-256:
  `bbf7c3e44c0f08fcfa005875c11628a38c73efe923bac105c7c47d473d91c951`
- execution-proof SHA-256:
  `465b6de5f5ac2f6e05a4ef4b241a49b08fd8732302272dc694da82034ecac451`
- Player-receipt SHA-256:
  `4c129fefa5fc6a3238b2c0b7fe4d40c8a4f485abff18d91e24da831cb0964904`
- baseline-manifest SHA-256:
  `5397351f29c3144f063427bbb543bdc5e92652296d743fe6f9de1477ed6c013a`
- runtime ABI:
  `efa86c4633e2d2f08c1effad4de334076d821c6ca653b7732bd605449f66c3f8`
- resource ABI:
  `sha256:255458bf49ed437c208aa8acf2b139825ff0cbb11d70e4a45d1d1459cd7d7973`

The genuine native-OFF Development Player is
`Builds/AssemblyShadow/M06/M06-Baseline-v8-NativeOff.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-96867fc6d6374461ab31e7ab837cbfba`.

- input snapshot hash:
  `5ba489b37f34039276b22f792cfbf089ae25008740b88ca2251f8e3f8e4e37fd`
- GameAssembly SHA-256:
  `cb7fa21b45690f5e1dee8c38239e6812f8f4e152fcc12cac3d4990585998cc33`
- type-proof SHA-256:
  `0fb842c723e6e5535bd6e19878993926739b6070b48df5f262dc7546bf1cfa81`
- execution-proof SHA-256:
  `f3001bfa6fb5ff901cb04fbf6decb7467574f8c452c1837a01440e84c0337600`
- Player-receipt SHA-256:
  `ae8decb53f92ae119319d792a803fd647bf1f1cb746dc29dfb65b03be3b3ab36`
- build GUID: `361d20d31a4f406aa5234fd3b0acc620`

The ON and OFF builds have distinct GUIDs, executables, native libraries,
metadata/snapshot graphs and native identities. Their managed assembly
projections are exactly equal; native identities are deliberately distinct.
This prevents a feature-flag build from being accepted merely because the same
managed names appeared in both snapshots.

## Development fixtures and replay

The Development fixture root is
`_temp/AssemblyShadow/M06Fixtures-d2d7a7fee8464070a71b94ee1c6ae362`.

- fixture-manifest SHA-256:
  `21a9d2aa2f4b9caef4f9df9d426ee41fd351de430ecad8e1ac6fbead34151a4b`
- independent replay SHA-256:
  `8cf77178cd4e79ac03ddbfa20c283dfb390a5013449f55ed4d71fa987f57da84`
- patch file counts: P01 11, P02 15, P03 19, InitializerFailure 11

The replay uses a separate scratch root, recompiles and compares every fixture
artifact, and checks compiler mode, closure/order, resource ABI, raw type
admissions, reflection binding, warmup and generation plan identity. It is not
the same call stack that publishes the fixture manifest.

## Release Player and no-PDB provenance

The genuine Release Player is
`Builds/AssemblyShadow/M06/M06-Baseline-Release-v8.app`. Its input snapshot is
`_temp/AssemblyShadow/M06PlayerInputs-3b218ff927b74a278ebf59f4d0ddcdc9`.

- input snapshot hash:
  `a1714c13b15e6475da46dd9e0b40fe4fab80d37df4a716e38b74ab10aa8ea16f`
- GameAssembly SHA-256:
  `4265ffc3125554aaaeb230fd062ae91741a143ddbf65fbb7edc6191adf1f1fcf`
- build GUID: `164cc1a5274940babe2de8dbbbe1b070`
- type-proof SHA-256:
  `6fb35b8d3df398ad06e641dc94d3c5ba89dfb63fbb809e7d1a97f6ffee3cb000`
- execution-proof SHA-256:
  `e38ecf7a3c96d77a3d847ae2d060ed6a222c6f07820d9c51b2811e1a5e6d53fa`
- Player-receipt SHA-256:
  `54b7c46a19f7446a4289f408d02dc50bf9096ebcd66e3fb242695bb8423a5738`
- baseline-manifest SHA-256:
  `142982be322ae093326e72018c07b1aa32f0cb8db5c10633ab7f314fc6129884`

The Release generation/Player is not a relabeled Development build. Its fixture
root is `_temp/AssemblyShadow/M06Fixtures-0a71fdad264946c7a4d65a7f07ee2a0f`:
fixture-manifest SHA-256
`21d1b632199c25cfa71a22e1aa11251584367a7c82ac0a92e757a24883d3769c`
and independent replay SHA-256
`fb0a87cd48bc2fa2306b841ab48b81ee26d24bda835ac92a07619c29806db357`.
The Release fixture contains no PDBs (P01/P02/P03/InitializerFailure file counts
10/12/14/10). T06-13 binds this exact no-PDB graph and correlates byte-level
type/method token evidence without claiming runtime ModuleVersionId support.

## Final runtime, Editor, Python and native evidence

The final launch receipt at
`_temp/AssemblyShadow/M06Results-final-v8/player-launches.json` has SHA-256
`abc4b5811143e11d2141b9dee2fbdff31d6b7dea392730559b75352488f94c21`.
It records all 28 requested modes, 28 distinct operating-system process IDs,
zero timeouts/failures and unchanged input hashes. The separate strict receipt
`_temp/AssemblyShadow/m06-final-verification-v8.json` has SHA-256
`6997b9bc33e279aee4df19b3c7a1db7587807c476716686e2a70bb561c4e09e6`
and `result=Passed`, `caseCount=28`.

The final combined Unity Editor suite passed 874/874 with no failed, skipped or
inconclusive cases. The preserved XML is
`_temp/AssemblyShadow/EditorTests-a05e5bf965204111b2a000f765b7c27d/results.xml`
(SHA-256 `503cfe5c6fdff0e01abe8f4affedc0b1a0274ffd90a844f28e4e049d2c938e7a`).

The full Python suite passed 337 tests with the preserved 36-DLL M05 compiler
root and exact raw-admission configuration; there were no skips. Fresh native
receipts passed for M03 parser/runtime, visibility, M04, M05 and M06. The M06
receipt records 824 checks, 20 translation-unit syntax checks and 1,080
dependencies; M05 records 34 syntax checks.

Pinned installation repeatability passed. The final install receipt SHA-256 is
`f1b96d9bf841102cc97a91b263389a680e14551ddf712d4eda85a8318639d874`;
the repeatability receipt SHA-256 is
`6f9727b2d6bc10afec53c749fb60756d2c3322247f5bf5c7ed78b26a88ea9597`.
Installed-source verification passed before and after the Editor suite for 940
pinned native source files and 942 installed files with native mode ON. Demo
identity is instead enforced by the frozen executable revision, exact source
inventory and exact dirty-path gate because Unity intentionally regenerated
five tracked build outputs after the Player builds.

The closeout receipt is `_temp/AssemblyShadow/m06-closeout-validation-v8.json`,
SHA-256 `068253e762f558666259316968a78ad574690cf1eef924557423eb45197ff91e`.
The previously observed original-checkout Editor PID 13313 was absent by final
closeout; it was never adopted, stopped or replaced by this workflow, and the
original checkout's exact working status remains preserved.

Two post-execution verifier corrections were required by real IL2CPP evidence:
compiler `netstandard` primitive signatures retarget to the exact linked
`mscorlib` identity at runtime, and module warmup returns its exact closed
generic type rather than only `generic.value=4`. These changes affect only
`m06_results.py` and its tests, are explicitly classified as post-execution
verification tooling, and are not represented as Player-producing source.

## Retained evidence and remaining gate boundary

`Evidence/artifact-index-v8.json` has SHA-256
`df3b6971385cece762dd54d589d70c2748e54916d539357ef420fe817a7651ff`.
It seals five deterministic archives containing 549 files and 53 byte-identical
selected copies. The archives cover all 28 Player results/logs, both fixture and
replay trees, both five-plan generation proofs, all three Player input proofs,
and the complete resumed closeout logs/receipts.

Runtime and closeout acceptance inputs are now complete. Remaining work is
limited to committing the retained evidence, Gate A current-checkout replay,
Gate B clean detached-commit replay, retaining both gate receipts, and the exact
post-closeout/local four-repository tag audit.

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
