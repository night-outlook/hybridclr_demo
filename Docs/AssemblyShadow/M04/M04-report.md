# M04 active Assembly and AssemblyRef resolution

Status: implementation, managed/evidence integration and bounded source-readiness
reviews complete; fresh IL2CPP Player validation and milestone acceptance pending.
M03 is accepted and locally tagged. No M04 runtime result, tag or M05 entry is
claimed here.

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

The integrated Unity Editor suite passed 532/532 tests with zero failures or
skips, including 39 M04-named cases. Raw XML and the fresh Editor log are in
`_temp/AssemblyShadow/EditorTests-e1ad91c6364447baa21a040f911c6b59`.
The main agent also ran all 152 Python tests successfully (27.405 seconds).
The separate managed/tooling source-readiness reviewer inspected the probes,
build/replay/schema helpers, shared M03 extractions, policy and Python evidence
contracts, independently checked the Editor XML and literal-load policy groups,
and found no actionable issue. This PASS is bounded source readiness only;
actual ON/OFF Player identity, enumeration, regression and benchmark evidence
remains required before M04 acceptance or M05 entry.

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
