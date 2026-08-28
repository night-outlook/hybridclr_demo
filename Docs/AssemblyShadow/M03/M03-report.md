# M03 native transaction and staging

Status: v4 diagnostic-contract corrections are committed and independently
reviewed. The paired installation, native-ON baseline and native regressions pass;
fresh fixtures/replay and the complete 16-mode Player matrix also pass.
V3's 16 processes exited zero, but strict evidence checks exposed unsigned
diagnostic overflow and an incomplete native-OFF adapter response; v3 is not
accepted. Ordinary HybridCLR OFF regression and exact restoration also pass;
the final independent milestone review remains pending.
Earlier integration failures are retained below as diagnostic evidence.
No M03 milestone tag or permission to enter M04 is claimed here.

## V4 executable source and correction validation

| Repository | Exact source commit |
| --- | --- |
| hybridclr | `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9` |
| il2cpp_plus | `0486098099e7e80176401267538499e611b181f2` |
| hybridclr_unity | `0c9302ffa2f420b30774423d4da8305214a78784` |
| demo | `6369ae8e32b8458c3b7c4180c99e47d15d5a63b3` |

Baseline ID is `M03-Baseline-v4`; runtime ABI is
`3ba82486b7cd561eadb4fe2dfc34690019d1402fe77a5d33d174b5a377a42be3`.
The pin-only follow-up commit changes no executable sources. The
[inventory](M03-file-and-api-inventory.md) records the four exact diffs.

Fresh pinned Editor tests passed 493/493 with no skipped tests, including
132 full-range native unsigned-token roundtrips, all 23 individual OFF-schema
field-removal negatives and four Bootstrap counter mirrors. The archived
[test XML](Evidence/editor-tests-6369ae8.xml) hashes to
`5ec842a7ed77d71d93631bbe4902eac4956f3240b4322416343a965b660049e0`.
The unchanged strict Python suite passed 133/133. The native OFF adapter/core/
serializer test passed 27 checks, in addition to existing ASan coverage.
The [bounded reviews](M03-review.md) returned PASS after closing the missing-field
defaulting P2; neither review substitutes for fresh v4 Player acceptance.

## V4 baseline and native regressions

Repeatable installation (`_temp/UnityExec_20260827_184537.log`) and strict source
verification passed with 935 source and 937 installed files. The receipt SHA is
`55e8d113da62872a83580d5e427228afb863c8a143c5deb209019498098efffb`.
The native-ON baseline completed in `_temp/UnityExec_20260827_184658.log`, including
linked diagnostic-schema parity, frozen M01 business semantics and resource reuse.

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v4.app`.
- Build GUID: `e32dce5cae124b7991d05a21d4a162b1`.
- Native SHA: `20ffcc8ed4b8c03d76becf67112b82e4df0721cf8390ff866ffb59583d632781`.
- Snapshot: `_temp/AssemblyShadow/M03PlayerInputs-15f548502b9a4c599180d587bea03e50`.
- Snapshot hash: `bd5697b7c5e3e6a4576fcd73edf8fd5e4dc2a51c5c5373f7417b146e85328bd1`.
- Baseline manifest: `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M03-Baseline-v4/baseline-manifest.json`.
- Manifest SHA: `c3b05cba7e31abb5898b4420b3bb79170508b4e8f062f8a71282653a06844eed`.
- Bootstrap ABI: `e77f77688f6dd6806d931d34b1005266d317343a69eed8c6b6a90c4ecb8f128d`.
- Resource ABI: `sha256:255458bf49ed437c208aa8acf2b139825ff0cbb11d70e4a45d1d1459cd7d7973`.

The [native regression receipt](Evidence/native-regression-6369ae8.json) passes
23,027 identity, 30 name, 25 facade-policy, 13 actual-lookup and 27 disabled-API
checks. The [visibility receipt](Evidence/visibility-regression-6369ae8.json)
passes 18,674 checks (6,262 abort and 12,412 commit). Both use ASan and confirm
unchanged transitive inputs (1,003 and 985 files). These tests ran after normal
prebuild generation, with no installed-header copy or source-verification waiver.
The [native-ON build receipt](Evidence/native-on-build-6369ae8.json) is retained
separately from this focused native evidence.

## V4 fresh native-ON observations

All fifteen native-ON processes under
`_temp/AssemblyShadow/M03PlayerResults-6369ae8-VciYIs` exited zero and passed
strict per-case verification. The fresh fixture manifest is
`_temp/AssemblyShadow/M03Fixtures-4d6223afaa79405a8f32b28552215355/m03-fixtures.json`
(SHA `31b0c2c99bc919295aadf3e56bbec8a8b34f98af7b68276ea961703971fcd85c`).
The complete suite subsequently passed with the finished Editor replay and
distinct native-OFF build bound to the observations, as recorded below.

T03-10 and T03-11 both preserve the actual native thread hash
`18199233411598851025` exactly in their typed snapshots, directly closing the
v3 UInt64 defect. T03-12 records eight before-publication and six after-publication
samples, fourteen iterations total, with no stress errors. Initializer failure
seals FailedAfterCommit, and the separate fallback process executes baseline.
Native retained-byte counts are 24,380 for one image and 105,736 for five, including
after Abort. These are DLL/PDB ownership counts, not total metadata/process memory
or a performance-budget claim.

## V4 complete transaction acceptance evidence

The actual-byte Editor replay completed in `_temp/UnityExec_20260827_185047.log`.
Its [archived receipt](Evidence/editor-replay-6369ae8.json) hashes to
`de283a596eb197c472f8948cb784c8e74891d6f484a46f9263048d71db472219`.
Stable-AOT provenance hashes to
`719f09e016f9776a108c76dfe19420360cfc26e423830e2f589d772d66d02af8`.

The separate native-OFF build completed in `_temp/UnityExec_20260827_190057.log`:

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v4-NativeOff.app`.
- Build GUID: `1e26f7dc7131412086808a96cea0838b`.
- Native SHA: `92f8e22cdcd5ce4b2da5aedfc639d07d52c35f9f167bff9d705d40f303597b97`.
- Snapshot: `_temp/AssemblyShadow/M03PlayerInputs-dc64d15ef66b4ebfbf761be802ad3140`.
- Snapshot hash: `96a9565316bf72db6310ea2582ba5eba440d9a5b80ce9060d86aef2510141247`.

T03-09 exited zero in process 6145. Every API reports FeatureDisabled, the out
values are Disabled/AotBaseline, and the complete native schema is present with
zero counters and empty transaction arrays. Its captured disabled snapshot no
longer invents missing fields.

`verify-m03-results.py` passed all sixteen required modes, bound to the exact
ON/OFF build GUIDs, native libraries, immutable input snapshots, patch bytes,
baseline and Editor replay. The [verification receipt](Evidence/verification-6369ae8.json)
is a complete transaction-matrix result, not yet the whole milestone verdict:
ordinary HybridCLR OFF regression and restored-source audit subsequently passed,
while final independent review is pending. No verifier expectation was weakened.

## Ordinary HybridCLR OFF regression and restoration

The unmodified M00 build entrypoint produced a separate
`Builds/AssemblyShadow/M03/M03-OrdinaryOff-6369ae8.app` in
`_temp/UnityExec_20260827_190411.log`. The native compiler flag was zero; the build
reported no errors/warnings and 33.471 seconds of BuildPipeline time. Native SHA:
`d099023186ea46f83fa93d2dafa553a4048f15f886b20d1c1ba30c2cc3d27572`.
The parent-owned process 8130 exited zero. The [runtime result](Evidence/ordinary-off-result-6369ae8.json)
confirms normal hot-update loading and assembly identity, prefab marker/value,
ScriptableObject value 5678, a scene component, no missing script, and interpreter
stack size 131072. The [verification record](Evidence/ordinary-off-verification-6369ae8.json)
binds the actual native library, build/result hashes, launch observation and
unchanged staged/compiler/Player hot-update DLL bytes.

Before the regression, seven exact files were backed up under
`_temp/AssemblyShadow/M03OrdinaryOffRestore-EsBwrJ`. M03 Configure restored all
four settings files byte-for-byte in `_temp/UnityExec_20260827_190814.log`.
The fixed M00 DLL and meta never changed content; their hashes still match the
backup. The previous stable M00 build receipt was restored after archiving the
new regression receipt separately. All seven hashes match their pre-test bytes.
Strict installed-runtime/source verification then passed with native ON,
935 source files, 937 installed files and unchanged receipt SHA
`55e8d113da62872a83580d5e427228afb863c8a143c5deb209019498098efffb`.
The [restored-runtime receipt](Evidence/installed-runtime-verification-6369ae8.json)
retains the exact successful command output.
The complete sixteen-mode verifier was rerun after this ordinary regression and
produced the same receipt SHA
`db60a3231a08b8635cc0f7c056179f0684b6943e1b26b60a3472274d32369492`.

The [lossless Player archive](Evidence/player-results-6369ae8.tar.gz) retains all
49 original observation JSON, native JSON, logs and fallback-marker files.
Its [index](Evidence/player-results-6369ae8.index.json) verifies every name and
byte hash against the original run directory. Archive SHA:
`2adcde9a708eeb4c5905600641e39b3c1481b9a5356a4ea450c03163e1e75dc8`.
The archive excludes macOS auxiliary metadata, not observation data. Raw JSON
retains its original absolute artifact paths; this is not a portable copy of
the complete Player/compiler/bundle trees or a signed attestation.

## V3 source pairing and repair validation

The v3 baseline uses runtime `fd60cb21a4d0d4c204848c3477d2a30ffd155710`,
native `0486098099e7e80176401267538499e611b181f2`,
package `f3329281f75e4eefdabdfad137bd9e3dacd996c7`, and
demo `b20145a7bf6b8a8cde714e2bbd8712d89f440fea`.
The pin-only follow-up commit does not change these executable sources.
Baseline ID is `M03-Baseline-v3`, runtime ABI
`5e4bfd6f45b5cfdd8a8fd3eb1a4be140476551d6413f06a551fbfc5adae26bfe`.
The [file and API inventory](M03-file-and-api-inventory.md) records the later v4
pairing. This v3 pairing and the v2 evidence below remain historical, not
substituted for v4 acceptance.

Repeatable installation completed in `_temp/UnityExec_20260827_181403.log`
with identical receipt SHA
`7f4a3151873b88b20e35f98f266ced6c7be07fa2332aba1792853f864fb8f979`.
355/355 Editor tests and 133/133 tooling tests passed before these commits;
the independent preservation/schema-gate review found no actionable defects.

The complete v3 baseline finished in `_temp/UnityExec_20260827_181509.log`,
including the exact prelink/linked diagnostic-schema comparison, frozen M01
business semantics and unchanged resources.

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v3.app`.
- Build GUID: `caf7bed5e5df4e60a3e2e938d2116ea4`.
- Native SHA: `a2386b15e77ab274a82554ad8b258dcda9f1941f50f0b9ea19530b7a4a834656`.
- Snapshot: `_temp/AssemblyShadow/M03PlayerInputs-46ca80b014224dac8bb6a04289d6f568`.
- Snapshot hash: `230637b2a5782f0705975e7b53465ef5d323347d49e95e110758eee0228bd4c0`.
- Baseline manifest: `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M03-Baseline-v3/baseline-manifest.json`.
- Manifest SHA: `ce96caf4ec5186e5bbe2f3ae08eb04309a148ac282a336d211b4b06d2b331068`.
- Resource ABI: `sha256:255458bf49ed437c208aa8acf2b139825ff0cbb11d70e4a45d1d1459cd7d7973`.

Fresh ASan receipts `m03-native-regression-b20145a.json` and
`m03-visibility-regression-b20145a.json` under `_temp/AssemblyShadow` both passed
and verified unchanged inputs. They cover 23,027 identity, 30 name, 25 facade
policy, 13 actual lookup and 18,674 private-visibility checks. The dependency
inventories contain 995 and 985 files respectively. These remain native helper
checks, not a substitute for the actual Player matrix.

## V3 live evidence and remaining contract defects

Fixture compilation and actual-byte Editor replay completed in
`_temp/UnityExec_20260827_181940.log`. The fixture root is
`_temp/AssemblyShadow/M03Fixtures-108a81e4656646769930d5078fb46c35`, with
manifest SHA `84110ba227a6174a9e98ec5def117377baa84414cddf551e09241680dde63b35`
and replay SHA `4444de2128430f23337ef65ecede57f1de241838e017c9f54696491e951702fe`.
Replay policy remains `compiler-linked-policy-graph-resource-abi:2`.

All 15 native-ON processes under
`_temp/AssemblyShadow/M03PlayerResults-b20145a-sAQhAN` exited zero. Per-case
strict verification passed 13 modes but rejected T03-10 and T03-11 because
their captured managed snapshots differ from the exact native JSON. T03-10's
native thread hash is `18199233411598851025`; the signed managed `long` field
serialized as `4294967295`. All 48 linked fields are present, so preservation
worked; the numeric contract was wrong. All native `uint64_t` and ARM64 `size_t`
diagnostic scalars must use managed `ulong`, with full-range exact-token tests.

The separate native-OFF build completed in `_temp/UnityExec_20260827_182915.log`:

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v3-NativeOff.app`.
- Build GUID: `a5610b846f654a39a68398cb17cada68`.
- Native SHA: `4bcb2f94aeeb8cf1bae0a846f1ce655e785c6914171c30a7304bb51f14563e73`.
- Snapshot: `_temp/AssemblyShadow/M03PlayerInputs-c4091e3b6b7646cea46d8a6882d47056`.
- Snapshot hash: `014e18cd9119159079f6348c872f9c04eb323fc503df4ca4e3f2b35998d15380`.

T03-09 exited zero in process 98780, but the complete strict suite rejected its
raw `{"enabled":false}` response. The native core already serializes the full
disabled schema; the managed-call adapter replaced it with a legacy stub.
The adapter must forward the native response unchanged, and the Player probe
must validate the complete disabled schema before declaring its case passed.
No v3 acceptance receipt was created. Neither historical results nor strict
verifier expectations are changed to hide these defects.

## V2 build-source pairing

| Repository | Exact source commit |
| --- | --- |
| hybridclr | `fd60cb21a4d0d4c204848c3477d2a30ffd155710` |
| il2cpp_plus | `0486098099e7e80176401267538499e611b181f2` |
| hybridclr_unity | `460eb5d65923e092d3c8acc7eb912c2942aea645` |
| demo | `ea49e1d11e30c65417dadc0f903ef7606b63776e` |

Baseline ID: `M03-Baseline-v2`. Runtime ABI hash:
`c9236ac7b6d2a1b32551ca60266199df3acaf11265b488cb2d7a609f6a2f6bfb`.
This is the retained v2 source pairing. Build completion is not transaction
acceptance.

## V2 baseline and native regression evidence

Repeatable pinned installation and strict source verification passed with 935
source files, 937 installed files, and receipt SHA
`6aee283d5c032c5fa321ab3979137461807f822634e73e60d713588b01a37c1b`.
The complete Unity build exited successfully in
`_temp/UnityExec_20260827_174753.log`, including frozen M01 business-semantic
equality and bundle reuse.

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v2.app`.
- Build GUID: `a79df871a6ea4ec598062c9404d445e1`.
- Native SHA: `3a5774d647a40fdb78341cd4980b017cf40b0db7456e53d7a31ffd55b3cba73e`.
- Input snapshot: `_temp/AssemblyShadow/M03PlayerInputs-c932c309a5b1400fa0f0fa5f83d7b736`.
- Snapshot hash: `a95be5d2d1038ea0849cf0cd6abd44f73d244b05aadd24ec5d70ff02a93dbf59`.
- Baseline manifest: `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M03-Baseline-v2/baseline-manifest.json`.
- Manifest SHA: `8de24e0e3e9ddbc285ab37308d29574f36d56c1e0b1ec7f651ae9db2afd189eb`.
- Resource ABI remains `sha256:255458bf49ed437c208aa8acf2b139825ff0cbb11d70e4a45d1d1459cd7d7973`.

Fresh ASan receipts are
`_temp/AssemblyShadow/m03-native-regression-ea49e1d-after-build.json`
(23,027 identity, 30 name, 25 facade-policy and 13 actual-lookup checks; 995
dependencies) and
`_temp/AssemblyShadow/m03-visibility-regression-ea49e1d-after-build.json`
(18,674 visibility assertions; 985 dependencies). Both verified unchanged inputs.
The earlier native-harness attempt immediately after installation refused the
placeholder Unity version header; the successful run followed normal build-time
header regeneration, without a header-copy workaround or validation waiver.

## V2 live probes and diagnostic preservation

The three patch fixtures and actual-byte Editor replay completed in
`_temp/UnityExec_20260827_175300.log`. Fixture root:
`_temp/AssemblyShadow/M03Fixtures-aedc145436b041779d1b351729acb07b`.
The fixture-manifest SHA is
`98d45bc928392893a302a34c1b700cdf1550d108e639a6116d176158da6c6553`;
replay SHA is
`d6be68d6d8e1f6273adb85102a6b3b0746fd259c2761dba4582acdd1ac0f04d5`.
Replay policy is `compiler-linked-policy-graph-resource-abi:2`.

All 15 native-ON modes ran in separate processes under
`_temp/AssemblyShadow/M03PlayerResults-ea49e1d-xSsPwa` and exited zero. Successful
commit cases returned `PATCH-P01-INTERNAL`; the initializer-failure process
sealed `FailedAfterCommit`, and its separate fallback process returned
`BASELINE-INTERNAL`. T03-12 observed eight pre-publication and six
post-publication coherent snapshots with no reported stress errors.

T03-09 also exited zero from the distinct
`Builds/AssemblyShadow/M03/M03-Baseline-v2-NativeOff.app`, built in
`_temp/UnityExec_20260827_180326.log`. Its GUID is
`5fba662ee4dc49659de25b9936d51df0`, native SHA
`786e96f691ea1040596ef87085d6f9081fafdb38c10b9855150e57ee1f87cdbc`,
and snapshot `_temp/AssemblyShadow/M03PlayerInputs-816d5047706c42f69face0176c6e9de4`
hashes to `376558d1cbd1725b1a38e493d3306efc74c485980409a9bae7779a96dfaac596`.
The complete 16-mode verifier reached the diagnostic-schema rejection after
binding both actual Players and the Editor replay; no acceptance output was
created.

The independent Python verifier nevertheless rejected T03-01's first snapshot:
`diagnostic closureLoadOrder must be an array`. Native JSON retained that field
and the other diagnostic data, while managed snapshots omitted fields unused
by the probe's C# assertions. This is a managed-linker preservation defect, not
permission to default missing data or reconstruct historical snapshots from
the final native JSON. A corrected, pinned Player and fresh observations are
required before acceptance.

Immutable prelink/linked metadata confirmed six DTO types with 48 source fields
but only 34 linked fields. Package commit
`f3329281f75e4eefdabdfad137bd9e3dacd996c7` preserves every schema field and all six
DTO constructors. A recursive coverage test and non-default roundtrip test cover
future reachable fields. The new M03 build/replay gate compares the exact captured
prelink and linked field names, types and serialization flags before issuing a
successful build receipt. It does not weaken the existing Python checks.
Fresh Editor tests passed 355/355, zero skipped, at
`_temp/AssemblyShadow/EditorTests-081ae26a0a9f42e39e7aa08ef4c17c54/results.xml`;
the unchanged Python suite passed 133/133. The independent bounded correction
review returned PASS, explicitly pending real v3 serialization and runtime proof.

The raw final native diagnostics report 24,380 retained bytes for one image and
105,736 for five images, including after Abort. These are retained DLL/PDB byte
counts, not total native metadata or process memory. The retained-private-image
policy remains explicit; no leak-free Abort or performance-budget claim is made.

## First diagnostic build source checkpoints

| Repository | M03 source checkpoint |
| --- | --- |
| hybridclr | `69168bb1f192ef16261a7822de82d52150fb691a` |
| il2cpp_plus | `740912bbfcf3e26155f157e7ba0f36d660546ef3` |
| hybridclr_unity | `460eb5d65923e092d3c8acc7eb912c2942aea645` |
| demo | `a71ce08c561a86781ed4f90b2b7281bc2653a1e8` |

The [transaction contract](M03-transaction-contract.md) describes the API, states,
locking, lifetime, publication, diagnostic schema, build identity and deviations.
The original checkout is not modified by this work. The accepted M01 resources
and M02 Player/evidence remain separate and immutable.

## Implementation and API boundary

The native core replaces the hard-coded `AssemblyShadowPrototype` files with
`AssemblyShadow`, explicit state/error definitions, diagnostics, a canonical-name
index, and private metadata visibility. The removed prototype remains recoverable
from the accepted M01/M02 tags. The runtime adds owned staged images, a private
thread-local metadata/reference resolver, and managed InternalCall adapters.

The nine public managed operations are ConfigureCandidates, BeginTransaction,
StageAssembly, ValidateTransaction, CommitTransaction, AbortTransaction, GetState,
GetAssemblyExecutionMode and GetDiagnosticsJson. Every operation returns an
explicit error code; queries use initialized out values. Native OFF returns
FeatureDisabled before interpreting arguments; Editor/Mono throws NotSupported.

New demo entrypoints are M03Build.Configure, ValidateCompilerInputs,
BuildPlayerBaseline, BuildFixtures, BuildFeatureDisabledPlayer, and
M03EditorValidation.Validate. Compiler-only preflight is not runtime-policy proof.
BuildFixtures must finish a separate actual-byte Editor replay before writing its
immutable validation receipt. `Tools/AssemblyShadow/README.md` records commands.

## Required real Player cases

| Case | Required observation |
| --- | --- |
| T03-01 | P01 commits once and invokes the patched Internal method |
| T03-02 | Randomized five-image staging, full skeletons before metadata |
| T03-03 | Three expected members, two staged, exact missing-closure error |
| T03-04 | Extra candidate refused without retaining an image |
| T03-05 | Duplicate refused without additional retained bytes/images |
| T03-06 | Wrong baseline refused before any image exists |
| T03-07 | Real initializers run once, after publication, in manifest order |
| T03-08 | Throwing initializer seals FailedAfterCommit; business never starts |
| T03-08-Fallback | Separate process invokes baseline with the bound failure marker |
| T03-09 | Separate native-OFF binary returns FeatureDisabled for all nine APIs |
| T03-10 | Acquiring baseline Internal prevents activation |
| T03-11 | Managed enumeration hides private images and records baseline use |
| T03-12 | Concurrent ordinary loads/queries span coherent publication |
| T03-13 | Malformed PDB rejected before allocation; real PDB retry succeeds |
| T03-14 | Invalid states/arguments/ABI remain exact and retry-safe |
| T03-15 | Real private generic metadata remains invisible after Abort |

The verifier must require all modes, bind results to actual Player build GUIDs,
native SHA, fixture/baseline/patch snapshots and Editor replay, and reject
tampering. Passing synthetic verifier tests cannot establish runtime acceptance.
Ordinary HybridCLR OFF regression, restored-ON installation verification and the
paired-source audit have passed for v4 as recorded above. The independent
milestone review remains the final required acceptance step.

## V1 pre-build evidence (historical)

- Unity Editor tests: 338/338 passed, none skipped, at
  `_temp/AssemblyShadow/EditorTests-dd3563551b47463db93bb0193856ce20/results.xml`.
- Python tooling: 122/122 passed, including 29 focused M03 tests. Every
  adversarial case starts with a passing complete synthetic 16-mode suite and
  checks the intended rejection reason; CLI testing includes real sidecar names,
  shuffled staging, and case-varied physical assembly names.
- Twenty modified native translation units passed syntax-only checks with the
  feature ON and OFF. This does not establish Unity's full native build/link ABI.
- Final pinned ASan checks passed 23,027 parser assertions and 30 actual VM
  name-folding checks, plus 18,674 private-visibility assertions and five cached
  class-enumeration structural checks. Receipts are
  `_temp/AssemblyShadow/m03-native-regression-a71ce08.json` (974 dependencies) and
  `_temp/AssemblyShadow/m03-visibility-regression-a71ce08.json` (985 dependencies).
- The M01 manifest still hashes to
  `e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d`;
  accepted M02 native SHA remains
  `0ac827495f6371c81cfc7d5bce7bf6d84c4cbf2968ca7682c9388c764002375c`.

## V1 native-ON baseline build (historical)

The two pinned installations produced identical receipt SHA
`d1622f5d82e3d22c18dcd258cfeee510264147afe401792c4469266a60bc0469`.
Strict installed-runtime verification passed with 935 source and 937 installed
files, including the complete pinned demo build source. The real Unity method
then completed successfully in `_temp/UnityExec_20260827_170727.log`, including
the fresh baseline manifest, frozen M01 business semantics and resource reuse.

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v1.app`.
- Build GUID: `e454ba32269e424bbf25bc254b06968d`.
- Native SHA: `64759be6983519da9fbda314484b9e592b845b6d508e2ede9f9bd07bc3506204`.
- Input snapshot: `_temp/AssemblyShadow/M03PlayerInputs-ba6d2672d8ec4704b3a206b058431597`.
- Snapshot hash: `e7d450626c1e5bfe50eefe99eb05a194e485de36dbe8dfabfdd6576f6b82b32b`.
- Baseline manifest: `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M03-Baseline-v1/baseline-manifest.json`.
- Manifest SHA: `341e29a964f4d5a68bfa09fc0d9b8c7232222b05a99a29153f94bb9a06b22237`.

An independent bounded source/integrity review of demo `a71ce08c` returned PASS
after inspecting the compiler/replay/build bindings and adversarial tests. This
is not the final M03 milestone review; no runtime cases are accepted by that
source-only verdict.

## V1 live transaction and integration repair (historical)

The three v1 patch fixtures and independent Editor replay completed successfully
in `_temp/UnityExec_20260827_171123.log`. The fixture root is
`_temp/AssemblyShadow/M03Fixtures-00bbe514eecb43f1b5821e55df7805c8`;
its replay receipt SHA is
`eb528fc89f693125667e82084aab39200f1a34ded874ad1c01769dcac9ca03cf`.
The actual native-ON Player then failed T03-01 at Validate with
`ReferenceResolutionFailed`, after successful Configure/Begin/Stage. The result
is `_temp/AssemblyShadow/M03PlayerResults-a71ce08-Nc8p4u/m03-T03-01.json`
(SHA `e1cc81fbb0b2aa6fbb94b7db78c5ff917e6e9f7a6af84958f97dc5ee057ace85`).
This failed run is retained, not counted as an accepted runtime case.

The source assumed every AssemblyRef required a physical assembly, while Unity's
compiled patch references the absent logical `netstandard` facade. The stable
allowlist also omitted linked `UnityEngine.CoreModule` because framework proof
deliberately covers only installed system-reference directories. The repair
retains that framework boundary, adds separately byte/identity-bound installed
compiler-library proof, and provides a constrained private facade resolver.
It also captures native diagnostics after a failed assertion instead of leaving
the prior successful Stage snapshot as the apparent final state.

The v2 verifier has 40 passing focused tests and 133 passing tooling tests,
including eight new proof-format/binding regressions. Native facade checks pass
25 policy/TLS assertions and 13 actual-lookup checks in addition to 23,027 parser
and 30 name checks under ASan. Fresh real Player acceptance and the final
independent gate remain pending.

Fresh Editor verification passed 346/346 tests with zero skips at
`_temp/AssemblyShadow/EditorTests-c28758696cc54f9cbdb60362441dad2b/results.xml`,
including eight executable compiler-library provenance tests. The independent
demo source re-review passed this corrected diff; the first compile's dnlib/
System.IO `FileAttributes` ambiguity was corrected before that test run. Native
re-review identified a preauthorization lookup side effect. It was corrected by
checking raw defining-image ownership before materialization/tracing, and the
independent native re-review then passed. The executable lookup regression
includes an unsafe control, zero candidate hooks on the corrected path, and a
later approved provider outside staging TLS. It uses documented metadata/counter
adapters, not a simulated claim of transaction-state correctness.

The corrected native source commits are `fd60cb21a4d0d4c204848c3477d2a30ffd155710`
(HybridCLR) and `0486098099e7e80176401267538499e611b181f2` (IL2CPP). The managed
package remains `460eb5d65923e092d3c8acc7eb912c2942aea645`. These bounded source
reviews permit a fresh v2 build, not milestone acceptance.

## Limits and next gate

Only the transaction foundation is in scope. Full logical assembly enumeration,
all type/reflection/cache routes, execution semantics and Unity resources are
M04-M07. Abort retains private metadata for process lifetime and permanently seals
the transaction. Full memory snapshots are not claimed to be side-effect-free.
The parser is not a complete hostile metadata/IL verifier, and runtime PDB/DLL
debug-identity matching is not established by the envelope tests. Signing and
production next-launch rollback remain M09; current receipts are local integrity
evidence. No Windows or Android result is inferred from macOS ARM64.

The v4 real Player matrix, native/Editor/tooling tests and ordinary OFF regression
pass. The retained-byte observations above are not total-memory or runtime
performance-budget measurements; those broader benchmarks remain M11 scope.
An independent full M03 verdict is still pending, so M04 entry is not yet approved.
