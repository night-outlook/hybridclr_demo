# M04 active Assembly and AssemblyRef resolution

Status: M04 accepted. The corrected v2 ten-process IL2CPP matrix, complete strict
verifier, Editor/Python/native checks and restoration audit pass. Both independent
final milestone reviews returned PASS at evidence commit
`1e6eeeba2adec5685ad3216343a7bdce9d82fd65`.
The local four-repository closeout tag is `assembly-shadow-m04-resolution`.
M05 may begin after the final metadata/tag audit; M05-M07 are not yet accepted.

The [acceptance contract](M04-assembly-contract.md) records the immutable M03
bases, required behavior, validation matrix, source/artifact boundaries and known
integration risks before implementation. The governing plan is
`Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-04-assembly-reference-resolution.md`.

This record binds executable source pins, changed files and APIs, actual Player
and tooling evidence, benchmarks, ordinary OFF regression/restoration and limits.
The [review record](M04-review.md) records both final verdicts and the M05 entry
decision. This closeout changes documentation only, not reviewed source or
artifact bytes.

## Source-readiness boundary (not milestone acceptance)

The native slice is committed at runtime `39eca7a2cc9c8e414f29701629da268e4e213e09`
and il2cpp_plus `229f9450c0ebe2293da2bffbfc35f160f18c69de`. Its independent
bounded review found no actionable defect and rehashed all recorded native
harness inputs. Evidence reports 53 resolver checks, 24 declared-reference
identity checks, 22 ON/OFF syntax checks, and one million active lookups with
zero allocations under ASan. The actual-helper harness still uses disclosed
physical-table/exception adapters; this is not managed Player or performance
acceptance. Preserved M03 native/visibility suites also passed.

The package name-policy slice is committed at
`deee300670730fbc4d864e82fa70e7b022581afe`. A separate bounded review found no
actionable defect in its fresh literal AssemblyName constructor proof and local
ASCII path-name handling. The author ran 71 focused checks and a pinned
netstandard compiler-profile loader proof; the reviewer inspected that evidence
without rerunning the file-writing harness.

The integrated Unity Editor suite passed 533/533 tests with zero failures or
skips, including 40 M04-named cases. Raw XML and the fresh Editor log are in
`_temp/AssemblyShadow/EditorTests-5d34445f94154db0a882dc53daa0b707`.
The main agent also reran all 152 Python tests successfully (28.052 seconds).
The separate managed/tooling source-readiness reviewer inspected the probes,
build/replay/schema helpers, shared M03 extractions, policy and Python evidence
contracts, independently checked the Editor XML and literal-load policy groups,
and found no actionable issue. That PASS was bounded source readiness only;
actual ON/OFF Player identity, enumeration, regression and benchmark evidence
remained required at that point, before M04 acceptance or M05 entry.

The first fresh compiler preflight rejected a duplicate Bootstrap-to-ordinary
runtime dependency before any Player build. Runtime dependencies are unique
consumer/provider graph edges; exact Bootstrap call-site approvals are a
separate table. The redundant M04 edge was removed while retaining the existing
M02 edge and all exact M02/M04 entrypoint approvals. A new Editor test validates
the actual project precompile policy and those approvals; the 533-test rerun
above includes it. The failing log is `_temp/UnityExec_20260827_203301.log`.

## Initial v1 Player run: diagnostic, not accepted

The initial executable demo pin was
`9ff427c51741e11f51baf07758b52f1236aafe8e`, paired with the runtime, native and
package commits above. Baseline `M04-Baseline-v1` uses runtime ABI
`12f9d7bb4b846f5438ab8fed37a93d92c45d42b945e16a208a4a27277cadd00d`.
Fresh install, compiler preflight, ON/OFF builds and P01/P03 Editor replay all
passed. The build logs are `_temp/UnityExec_20260827_203734.log` (ON),
`_temp/UnityExec_20260827_204158.log` (fixtures), and
`_temp/UnityExec_20260827_204916.log` (OFF).

All ten processes under `_temp/AssemblyShadow/M04Results-NOxFjf83` exited zero
and emitted Passed. These include the ordinary OFF loading, placeholder,
supplementary-metadata and duplicate-load checks. The isolated million-lookup
measurements were 43,562,635 ticks ON and 949,578,504 ticks OFF, both at
10,000,000 ticks/second. These raw v1 observations are retained as diagnostic
history, not substituted for the corrected source's acceptance or a production
performance claim.

The [lossless v1 archive](Evidence/player-results-v1-9ff427c.tar.gz) retains all
29 raw result, native diagnostic and log files. Its
[index](Evidence/player-results-v1-9ff427c.index.json) verifies every archived
byte against the original run directory. Archive SHA:
`5e46a231aeb470cb736fe7e939646fc3d4646fea0865cca992668f2189321cf6`.

The strict first-case offline check rejected `observed unbound assembly
'__Generated'`. The linked input snapshot contains 60 DLLs, while the actual
Player's native metadata and raw AppDomain observations contain 61 assemblies.
Pinned IL2CPP creates the extra assembly natively; it has no linked DLL. The
verifier incorrectly required every logical assembly to have a linked file.
This is an evidence-domain error, not evidence of a resolver fallback failure.

The correction captures and independently replays the actual Player
`global-metadata.dat` assembly/image tables. The pinned format is version 31,
not an assumed format based on the Editor's release name. Native identity rows
retain physical table indexes and tokens; generated names are derived from the
native-minus-linked inventory, not from a name whitelist. The runtime binds the
metadata path/hash to its own Player data directory before any Shadow API call.
C# and Python independently validate table bounds, strings, identity formatting
and exact inventory equality. Unknown or unbound names remain errors. Native
metadata contains no module MVID, so none is invented in this new evidence
domain. Existing v1 manifests, build receipts and observations are not rewritten.

## V2 corrective source validation

Fresh integrated Editor tests passed 542/542 with zero failures or skips,
including 49 M04-named cases, under
`_temp/AssemblyShadow/EditorTests-4784124d255640a2a806e1048ed5c5fd`.
The results XML SHA is
`939f256ced131890a7691102aefcafff4be94b9ea32c0acfca2ea99ccd175257`.
The main agent's full Python rerun passed 160/160 in 27.861 seconds. These checks
include malformed table/range/string/index and identity mutations, bounded
unsigned tokens, duplicate/alias metadata paths, unbound names, and distinct
physical placeholder versus logical enumeration ordering.

Both independent parsers read the existing v1 ON/OFF native metadata as version
31 with 61 assemblies; all 60 linked identities agree. The single native-only
assembly is derived at table/image index 60 with token 536870912. An in-memory
projection of only the five new receipt fields allows all ten unchanged v1
observations to pass the corrected verifier. This is diagnostic logic validation
only: old receipts remain unchanged and correctly fail the new exact schema.
At that source-readiness point, actual emitted v2 receipts and fresh v2 Player
observations were still required; the following sections record that later run.

Guarded Configure generated the distinct `M04-Baseline-v2` scene/settings in
`_temp/UnityExec_20260827_211440.log`; it reuses the unchanged runtime ABI and
does not modify frozen M00/M01 artifacts.

The corrected executable demo pin is
`3118db3f406bdbeeacaf75737d26a89414029007`; metadata-only commit
`e1a0d48af6a2be136e6ff777e3628b91b1715d26` records it. Runtime, native and
package pins remain the source-readiness pairing above. The
[file/API inventory](M04-file-and-api-inventory.md) records all four exact
source ranges. An independent bounded review inspected this correction,
rechecked the actual metadata, old-schema rejection and Editor XML, and returned
PASS for source readiness only.

## V2 native-ON build and focused regressions

Repeatable installation passed in `_temp/UnityExec_20260827_211754.log`.
Strict installed/source verification confirms 936 source files, 938 installed
files, the demo build-source pin and configured native ON. Installation receipt
SHA: `981d412763130de2b80caaed44bd141b10068455de20308e4cf90e94b4c31955`.
Fresh compiler preflight passed in `_temp/UnityExec_20260827_211913.log`, under
`_temp/AssemblyShadow/M04CompilerPreflight-bb39d0bc378f469390b087befd29119d/Snapshot`.

The ON Player build passed in `_temp/UnityExec_20260827_212039.log`, including
unchanged frozen M01 business semantics and bundles:

- Player: `Builds/AssemblyShadow/M04/M04-Baseline-v2.app`.
- Build GUID: `e613f9d84abb417aa01bb4f4a5268624`.
- Native SHA: `723490e3b2acf6de5999efd4c72f9aaff6aa8490f77605f7b10e458e5309d0e7`.
- Input snapshot: `_temp/AssemblyShadow/M04PlayerInputs-b7510196acb241f2ab40a72906a34c7c`.
- Snapshot hash: `e42a91c890ee1a2f0638d1b213c8aa3880d2024e37abba708f7a13f04740d098`.
- Player receipt SHA: `42c7d6b3047fa3ba4820bba30a48aff729100ab496bb0fedb32a86a468eb80c6`.
- Baseline manifest SHA: `351cc29070cd81bc341432dd88d6ad687ff260952c5625aaf49d1e9cdfe3b6d5`.
- Actual metadata SHA: `4b5ff9b113b0fac45fb6f58c24df3f8a8d0af3821861a477b8ce1ae74e3b65d3`.

The emitted receipt contains all five new fields and 61 native identities,
including the derived native-only assembly; all 60 linked DLL identities agree.
This inventory does not authorize additional stable-AOT providers for patches.

Fresh [M04 native checks](Evidence/native-regression-3118db3.json) passed 53
resolver, 24 declared-reference identity and 22 ON/OFF syntax checks, plus one
million active lookups with zero allocations (369,289 microseconds under ASan).
The preserved [M03 native suite](Evidence/preserved-m03-native-regression-3118db3.json)
passed 23,027 identity, 30 name, 25 facade, 13 lookup and 27 disabled-API checks.
The [visibility suite](Evidence/preserved-m03-visibility-3118db3.json) passed
18,674 checks. All three receipts confirm unchanged transitive input hashes.
These are focused native checks with the disclosed adapters, not a substitute
for the v2 managed Player matrix or its ON/OFF performance measurements.

The actual v2 linked `mscorlib.dll` wrapper
[capture](Evidence/linked-managed-wrappers-3118db3.json) binds 16 methods and
269 IL instructions to SHA
`5656c3f3da4c976c31604a19795409b4ea5b26a86f191449303cfa06ce53dfb2`,
MVID `53a1b952-b096-47be-9876-e55ed2a0d85e`, and the ON Player receipt.
Those instruction streams are unchanged from the inspected v1 wrappers even
though the linked DLL bytes differ. The exact read-only
[capture command](Evidence/capture-linked-managed-wrappers-3118db3.ps1) is retained.

## V2 complete Player matrix and OFF regression

Fixture compilation and independent Editor replay passed in
`_temp/UnityExec_20260827_212527.log`. The fixture root is
`_temp/AssemblyShadow/M04Fixtures-0ba4a1a6c6744698831b60465f409b3e`.
The archived [fixture manifest](Evidence/fixture-manifest-3118db3.json) hashes to
`423be48408cae6249dedb43c0c60d243a29063f2efee39f1fc73a8f4e2001ef3`;
the [Editor replay](Evidence/editor-replay-3118db3.json) hashes to
`9b5783634713e31db3a717eeda96bfa9fcde1d05c9446edfeea0152863505f38`.
Stable-AOT provenance hash:
`1c97eda55d5ecc53ed2f3fca4494cb52024d565a37ce49e936252e69904d4d36`.

The separate OFF Player completed in `_temp/UnityExec_20260827_213326.log`:

- Player: `Builds/AssemblyShadow/M04/M04-Baseline-v2-NativeOff.app`.
- Build GUID: `84d73ef888ed4f84b114c1e317a059f1`.
- Native SHA: `85e32caaa29a4f799ebbcd873b7aa97f59d838f5c151ba3287b9d687bd50c62b`.
- Snapshot: `_temp/AssemblyShadow/M04PlayerInputs-d148e78a25924dc1a62ccf791c03b4f4`.
- Snapshot hash: `efbbb35eeb4a93406c130056bf0a72f921a6b8c11c388b9b94c6ffff53ae2e7f`.
- [OFF receipt](Evidence/native-off-build-3118db3.json) SHA: `73d60147e3ee67c45763af412e6bb6925e09a133e6dfa6c475efc2a6ef1b8248`.

ON and OFF metadata bytes have the same verified SHA recorded above; their
native libraries, build GUIDs, output directories and input snapshots are
distinct. The build helper restored native ON after producing the OFF binary.

All ten fresh processes under
`_temp/AssemblyShadow/M04Results-3118db3-j7q6Mw66` exited zero and emitted Passed.
The [launch record](Evidence/player-launches-3118db3.json) retains the exact
fail-fast commands. The [complete verifier](Evidence/verification-3118db3.json)
passes all ten modes against actual emitted receipts, native metadata, linked
DLLs, baseline, patch bytes and Editor replay; its
[command/output](Evidence/verification-command-3118db3.json) is retained.
No in-memory receipt augmentation or expectation waiver is used for v2.

P01 exposes only Internal as interpreter; P03 resolves all five closure members
consistently through name variants, Type-to-Assembly identity, raw logical
enumeration and executing-assembly witnesses. Staged ordinary queries remain
baseline and prevent a later commit; missing closure and external-consumer
violations reject without baseline fallback. Declared reference versions/tokens
match patch compiler bytes, including the nonphysical netstandard facade.

T04-08 verifies all nine APIs return FeatureDisabled in the OFF binary. Its
ordinary loader fills the pre-existing placeholder, keeps its object identity,
exposes exactly one dynamic assembly and changes logical count from 61 to 62.
The fixed M00 marker is `M00-HOTUPDATE-OK`; null/tampered input is rejected and
caller bytes remain unchanged. Duplicate loading raises
`System.ExecutionEngineException` with `reloading placeholder assembly is not supported!`.
Known-name resolve callback count is zero with the same returned Assembly;
supplementary metadata returns 0 initially, 5 on repeat and 6 for invalid mode.
These are actual observations, not inferred from the native-OFF API stubs.

The million-lookup measurements use 1,000 warmups and a 10,000,000 Hz stopwatch:

| Process | Elapsed ticks | Seconds |
| --- | ---: | ---: |
| T04-09 committed ON | 42,434,048 | 4.2434048 |
| T04-10 isolated OFF, no Shadow API calls | 944,263,226 | 94.4263226 |
| T04-08 OFF after ordinary compatibility checks | 959,584,846 | 95.9584846 |

Each checksum is 1,000,000 and final Assembly identity is unchanged. Builds,
Editor/Python tests and native harnesses had finished before these measurements;
the original user Editor remained open. These single controlled name-load runs
are not game-frame or production performance claims, and the native resolver's
zero-allocation result is not a managed Player GC-allocation measurement.

## Final validation, archive and scope

After both builds, fresh Editor tests again passed 542/542 (49 M04 cases, no
failures/skips). The [archived XML](Evidence/editor-tests-3118db3.xml) SHA is
`774967405d527b360af3476c3c27410f64a99528a3d44be7c6c3c17805082751`;
its original root is `_temp/AssemblyShadow/EditorTests-b6385d3280994c9982f033dab7db29f0`.
The final [Python rerun](Evidence/python-tests-3118db3.json) passed 160/160 in
30.021 seconds. [Restored installation verification](Evidence/installed-runtime-verification-3118db3.json)
passed with native ON and unchanged install receipt SHA `981d412763130de2b80caaed44bd141b10068455de20308e4cf90e94b4c31955`.

The [lossless v2 archive](Evidence/player-results-3118db3.tar.gz) contains all
29 original result, raw-native and log files. Its
[index](Evidence/player-results-3118db3.index.json) verifies every byte against
the original run directory. Archive SHA:
`d9f104b41486c3a7012aea15602dcc217f1b53d4251be4b4f7072f50752755ca`.
The six copied build/baseline/fixture/replay/XML artifacts match their original
bytes exactly. Original absolute artifact paths are retained; this is not a
portable copy of the complete Player/compiler/bundle trees or a signed attestation.
The [artifact/scope audit](Evidence/artifact-and-scope-audit-3118db3.json) records
those comparisons, four frozen hashes and the retained repository boundaries.

The frozen M01 baseline manifest remains SHA
`e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d`,
and its original source-asset audit receipt remains SHA
`4fe92ddfb66134efbef3f34fbd695abe262611c326196627c8b743b32f4785cc`.
Fixed M00 staged DLL bytes remain SHA
`9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`.
The ON build separately verified frozen M01 DLL semantics and reused bundles.
The native/runtime/package worktrees are clean. Demo changes after the source
pin are confined to this M04 documentation/evidence directory.

The original demo checkout retains only its four pre-existing dirty paths:
`Assets/Settings/Renderer2D.asset`, `.DS_Store`, `Assets/Editor.meta`, and
`Documents/HybridCLR_AssemblyShadow_Design_and_Plans/.DS_Store`.
Its existing Unity Editor PID 13313 is still running; it was not adopted or stopped.

## Explicit evidence boundaries

- `RuntimeAssembly.GetManifestModuleInternal` is unsupported in the pinned
  IL2CPP, and `RuntimeModule.GetGuidInternal` intentionally does not return a
  module GUID. M04 does not add a new module API for its probes. Runtime GUID
  fields must be empty with availability false, not populated from expected
  artifacts. Prelink/linked/patch MVIDs are independently bound to DLL bytes;
  staged shadow MVIDs also come from actual native diagnostics. Runtime
  assembly names, execution modes and reference equality remain observed.
- Patch `baselineMvid` belongs to the frozen **prelink** baseline descriptor.
  Linked Player identities are a separate domain and may have different MVIDs.
  Cross-build GUID equality is not a semantic-equivalence requirement.
- The pinned managed name-load wrapper IL throws on a native miss without a
  managed `AssemblyResolve` dispatch. Native missing-name checks and the linked
  wrapper capture record the separate native boundary; bodyless icalls do not
  prove native callback behavior by themselves. A known-name callback-noninvocation Player
  probe is not a direct managed missing-name observation or fallback proof;
  no unknown-alias policy waiver is introduced.
- Executing-assembly witnesses are patch-only methods on existing, finite
  baseline-known types. Five existing class declarations gain only `partial`;
  baseline DLL semantic equality and frozen resource bytes must still pass.
- Logical enumeration evidence retains the actual returned order and duplicates.
  It must not be grouped or sorted before correctness checks. M03 native
  diagnostics intentionally remain a separate physical view.
