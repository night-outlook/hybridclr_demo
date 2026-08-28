# M04 active Assembly and AssemblyRef resolution

Status: all ten initial v1 IL2CPP Player modes passed, but the strict offline
gate exposed a native-generated assembly evidence gap. The evidence-model
correction and a fresh v2 validation are in progress; M04 is not accepted.
M03 is accepted and locally tagged. No M04 tag or M05 entry is claimed here.

The [acceptance contract](M04-assembly-contract.md) records the immutable M03
bases, required behavior, validation matrix, source/artifact boundaries and known
integration risks before implementation. The governing plan is
`Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-04-assembly-reference-resolution.md`.

Final delivery will record exact executable source pins, changed files and APIs,
native/Editor/tooling and actual Player results, raw benchmark data, ordinary OFF
regression/restoration, deviations, independent review and the M05 entry decision.

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
and found no actionable issue. This PASS is bounded source readiness only;
actual ON/OFF Player identity, enumeration, regression and benchmark evidence
remains required before M04 acceptance or M05 entry.

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
Actual emitted v2 receipts and fresh v2 Player observations are still required.

Guarded Configure generated the distinct `M04-Baseline-v2` scene/settings in
`_temp/UnityExec_20260827_211440.log`; it reuses the unchanged runtime ABI and
does not modify frozen M00/M01 artifacts.

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
- The pinned managed name-load wrapper throws on a native miss without
  dispatching `AssemblyResolve`. Native missing-name checks and pinned wrapper
  IL will document this boundary. A known-name callback-noninvocation Player
  probe is not a direct managed missing-name observation or fallback proof;
  no unknown-alias policy waiver is introduced.
- Executing-assembly witnesses are patch-only methods on existing, finite
  baseline-known types. Five existing class declarations gain only `partial`;
  baseline DLL semantic equality and frozen resource bytes must still pass.
- Logical enumeration evidence retains the actual returned order and duplicates.
  It must not be grouped or sorted before correctness checks. M03 native
  diagnostics intentionally remain a separate physical view.
