# D5-B AP3 — independent fixed runner import bootstrap review

**Verdict: `D5BRunnerImportsAP3IndependentReview=PassRunnerImportBootstrapSourceOnly`.**  
**Exact implementation reviewed and checked out by CI:** `night-outlook/hybridclr_demo@bcf3a9470a12758b210738476d18f80bf60d2eaf`.  
**Primary documentation/evidence HEAD examined:** `246aedcd9e3aa9d09dd1bad2aba1a00864c94416`.  
**Review date:** 2026-11-26 America/Los_Angeles. Execution timestamps below remain UTC.

## 1. Decision, independence and scope

AP3 establishes its declared bounded observation: the fixed preflight, writer and wrapper modules initialize from fresh AP2-verified immutable source bytes; their direct imports select private project bindings, a private path-only sys facade, and fixed trusted standard-library references. The observer checks the resulting bindings without calling candidate functions. It records attempted and completed initialization separately and returns serialized observations with closed authority. **No material in-scope defect or unsupported successful-observation claim was established.** [Exact source][source] · [Design][design] · [Companion independent evidence][evidence]

This accepts only `PassRunnerImportBootstrapSourceOnly`. Runtime configuration binding, full runtime import isolation, complete executable closure, source/live-ref admission, post-import or continuous custody, Q and Local authorization remain unestablished. Importing these modules executes their reviewed top-level Python; this decision does not describe the imported candidate as inert. The accepted R5, AP1 R2 and AP2 decisions remain preserved within their original scopes. [Closed report fields][closed-source] · [Accepted AP2 decision][ap2-review]

The reviewer acted independently of Primary Implementation and Local Validation. Work began with the committed README, closed WEB_TO_LOCAL and AP3 request, followed by the accepted AP2 report, AP3 design, Primary report/evidence, exact source, tests, workflow and raw logs. Source, reporting/test reach, and CI/preservation were separately examined. Final adjudication includes direct source inspection and a fresh exact-source AP3 rerun. Primary statements were checked against source, remote objects and transcripts; missing state was not inferred from chat. [Request][request] · [Primary report][primary] · [Closed handoff][handoff]

The independent rerun executed only the 20 AP3 methods in temporary Git repositories and synthetic Linux locations. The observer initialized the reviewed candidate modules in those fixtures. It did not invoke live candidate admission, preview, one-use writing, Unity/native work or Player execution. The 141 retained methods and old-wrapper denial gate were checked in existing host/CI evidence, not rerun by this reviewer. Static additional considerations below are identified as reasoning rather than newly executed fixtures.

## 2. Exact revisions and remote identities

All four feature branches are `codex/assembly-shadow-r01b-h1`. Fresh Connector reads matched the supplied heads:

| Repository | Exact AP3 source tuple | Remote HEAD examined before independent publication |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `bcf3a9470a12758b210738476d18f80bf60d2eaf` | `246aedcd9e3aa9d09dd1bad2aba1a00864c94416` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Same |

Source T has tree `a9c4206b4b863614142f48b9d0f9c366df5ca79e` and sole parent `20ca45419ca797ed2bcd330a7be0698fab59819f`, the accepted AP2 independent publication. Its one-commit increment has exactly four paths: new observer, tests and design, plus 13 added workflow lines. Documentation HEAD D has tree `6fa992c06c6c89d1fc2685c4321a80d1abfd9297`, sole parent T, and exactly eight changed paths under `Docs/AssemblyShadow`. All four source-increment files are identical in D. This independent report is another documentation publication, distinct from both T and D. [Source commit][source-commit] · [Packet commit][docs-commit] · [Machine comparison records][evidence]

| Source-increment artifact | Verified Git blob | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [d5b_runner_imports.py](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py) | `2bff794380f77b61dbbd84058fcba94d5ee4d9d2` | 19,539 | `fe348335d0d72d21ee7c7d5e3aa7cb9985cc03a9e05b45b6dbbfedd8a3808cab` |
| [test_d5b_runner_imports.py](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py) | `86840e72285b99ea885469390b66c42d1f3d681f` | 40,342 | `62c2f53f9425d7c7b2780c7e848cb4d6243b65b0bed9b6292c2cf2b0ec8c4192` |
| [r03-b2-d5b-local-admission-source-host.yml](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/.github/workflows/r03-b2-d5b-local-admission-source-host.yml) | `e55b88f8e33d12077d0a0ca4105d8fe02c3e7d01` | 5,992 | `e57887096456ebc6b85338a75bce10bfac57606025347126b3b0e9c66638dec2` |
| [D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md) | `af08b920ada9e628f78a73f8b26bc015cbd78364` | 18,191 | `08f86835f2519b64a49a25dd440a1b8b6aed79df85185f719af4224bcd06f9b2` |

The review verified downloaded bytes against Connector Git blobs before execution and again afterward. Remote identity is an observation of repository objects and refs. It grants no runtime source/live-ref admission, attests no physical Mac checkout and does not make the historical paths current. All four `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repository>` paths remain physically **Unverified**. [Input identities and remote records][evidence]

## 3. Authentication and captured-byte selection

### 3.1 The public boundary obtains fresh evidence

The public API accepts exactly `raw: bytes` and `expected_closure_blob: str`. It exposes no bundle, module, importer map, callback, candidate argument or execution option. At source lines 354–363 it requires isolated/no-site/disabled-bytecode process conditions, exact lowercase 40-character SHA spelling, exact immutable bytes, a 1 MiB limit, and equality to the external closure blob before obtaining a snapshot. The pin identifies bytes; it is not approval. Tests 09, 14 and 19/20 substantiate these boundaries. [API][api-source] · [Tests][tests]

The adjacent AP2 helper is read into bytes and checked against `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` before compilation. The bounded reader requires a canonical absolute parent, no-follow directory and leaf opens, a regular single-link non-executable leaf, exact bounded read length, matching before/after descriptor and named-entry fingerprints, and parent identity rechecks. These checks concern that read; they do not establish continuous installation custody. [Reader and helper loading, lines 104–174][helper-source]

The same authenticated `helper_raw` bytes are compiled and executed. No second source read or ambient module-name lookup selects the helper. A unique real-`sys.modules` name is checked absent before temporary registration for AP2's dataclass initialization; its identity is checked and its own entry deleted in `finally`. AP2 then performs a fresh `verify_runner_closure(raw, expected_blob)`. Candidate canonical names are unrelated to this temporary registration. [Helper loading][helper-source]

The accepted AP2 helper, in turn, authenticates the reviewed AP1 helper before loading it and performs the existing artifact, proposal, checkout and location observations. AP3 transfers the resulting immutable file bytes into its own snapshot tuples. It rechecks exactly six records, exact roster, no duplicate paths, bounded immutable bytes, mode `100644`, matching blob/content identities, and the required closed AP2 result. AP3's later ordinary `json.loads(raw)` reparses the same immutable bytes after AP2's strict validation; it is not an alternate unverified closure path. [Snapshot validation][snapshot-source] · [AP2 verifier][ap2-source]

### 3.2 Candidate code comes from the authenticated captures

All three candidate modules are compiled from `SnapshotFile.raw` before any candidate initialization. The compiler receives `dont_inherit=True`, `optimize=0`, and filenames derived from the verified runner root and fixed relative paths. Candidate source paths are not reopened for compilation, and source loaders, bytecode caches and canonical candidate cache entries do not select those bytes. Test 08 changes the writer pathname after real AP2 capture and observes that the compiler still receives the prior captured bytes. [Initialization, lines 226–282][initialize-source] · [Test 08][test-capture]

AP1 constrains the writer to the reviewed base plus its sole exact envelope-blob literal substitution. The derived literal is a checked hexadecimal identity, not arbitrary replacement source. AP3 does not perform a new substitution or repin the repository. It checks the resulting writer literal against the closed proposal while reporting `approvedEnvelopeGitBlob=null` as authority. [AP1 publication policy][ap1-source] · [Initialization constants][initialize-source]

Plan, profile and proposal bytes remain data. AP3 does not compile them, call their candidate validators, redirect configuration paths, or claim that future runtime reads consume the captures. Writer `read_plan()` and preflight `inspect()` retain their existing pathname reads if separately called; this observer does not call them. [Writer][writer] · [Preflight][preflight] · [Design, runtime configuration boundary][design]

## 4. Fixed import graph and process state

### 4.1 Exact private routing

Initialization order is preflight → writer → wrapper. Each candidate receives a fresh private module object, a non-`__main__` name, fixed runner-relative `__file__`, and a separate builtins dictionary whose import function is replaced only in that private dictionary. Loader/spec/cache metadata are empty. The existing main guards remain inactive. [Initialization][initialize-source]

AST inspection independently confirms all direct import forms and finds no nested/function-local imports or calls in function-definition defaults. The actual ordered trace in test 02 contains:

| Candidate module | Direct requests | Trusted standard-library selections | Private sys selections | Private project selections |
| --- | ---: | ---: | ---: | ---: |
| `d5b_rr5_source_preflight` | 8 | 7 | 1 | 0 |
| `d5b_local_admission` | 14 | 12 | 1 | 1 |
| `run_d5_local` | 1 | 0 | 0 | 1 |
| **Total** | **23** | **19** | **2** | **2** |

The per-module importer checks exact module spelling, exact permitted from-list and absolute level zero. Unknown names, dotted extensions, star/extra/incorrect from-lists, relative levels, boolean levels and unavailable project dependencies fail without ambient fallback. Standard-library selections come from the fixed preloaded map; project requests come from already initialized private modules. [Allowlists, lines 47–67][imports-source] · [Importer, lines 205–223][importer-source] · [Tests 02/13][tests]

After initialization, the observer checks actual identities: `writer.source is preflight`, `wrapper.main is writer.main`, and the writer main function's globals are its initialized module dictionary. It also checks runner-relative path metadata, plan/profile blob constants, the closed proposal literal and the private path list. None of those identity comparisons calls a candidate function. Test 01 captures the actual namespaces and confirms these identities. [Binding checks][initialize-source] · [Test 01][tests]

### 4.2 Real path and candidate-cache preservation

Both `sys` requests receive one shared private `ModuleType("sys")` with its own initially empty path list. The reviewed writer's top-level insertion changes only that list. The facade delegates no unknown attributes to real sys. It deliberately supports this fixed initialization, not later runtime functions requiring other sys attributes. Source checks the one resulting directory string. [Private sys construction and checks][initialize-source]

The observer captures the real `sys.path` object and tuple contents plus identity/absence of the three canonical candidate names in real `sys.modules`. It compares those observations after initialization and on ordinary failure. Candidate module objects stay in the private table; the observer does not temporarily alter and restore real `sys.path`. Tests 03–06 additionally check inert ambient entries, candidate-aware meta/path-cache observers, untouched inert source/opaque-bytecode files and line-by-line preservation during writer initialization. [API process-state observations][api-source] · [Tests][tests]

This does not freeze every process cache, finder, standard-library global or thread. The three canonical candidate slots are the reported cache boundary. Trusted helper/library initialization may use normal Python machinery. The interpreter, preloaded standard library, observer/helper installation, selected Git and OS remain trusted infrastructure; isolated flags do not attest arbitrary process history.

Candidate top-level `Path(__file__).resolve()` calls can read filesystem metadata after AP2. The remaining reviewed initialization binds imports/constants, compiles regular expressions and defines classes/functions. Test 07 permits the known module and class-body frames while checking that no candidate function, content reader or process operation is invoked during the initialization seam. Those statements do execute Python. The earlier AP2 snapshot provides no post-import or continuous custody guarantee. [Candidate sources][writer] · [Preflight][preflight] · [Test 07][tests]

## 5. Truthful progress, immutable observations and limits

Attempted initialization is recorded immediately before each candidate `exec`; completion is recorded after it returns. A failure inside preflight, writer or wrapper retains the attempted prefix and previously recorded completions. `candidateTopLevelCodeMayHaveRun` derives from attempts, while `candidateWriterImported` derives from recorded writer completion. In particular, a wrapper failure after writer initialization keeps writer import positive. Test 15 exercises those three ordinary-error stages. [Progress and report fields][closed-source] · [Rejection conversion][api-source] · [Tests 15–17][test-progress]

The nested AP2 `artifactObservation.candidateWriterExecutedOrImported=false` describes the earlier artifact-only stage. AP3 labels it `AP2BeforeCandidateModuleInitializationOnly` and reports its own later writer initialization positively. This is a coherent stage distinction, not a statement that successful AP3 left candidate code inert. [API report assembly][api-source]

Success stores one immutable JSON-bytes field in a frozen `ImportObservation`. Each report access produces fresh nested JSON containers. Ordinary `Rejected.report` copies also decode retained JSON bytes. The successful returned object exposes no candidate module, callable, code object or importer handle. Test 14 checks the exact field inventory, ordinary frozen assignment, JSON-only values, fresh copies and two-argument signature. This representation is not a hostile same-process isolation boundary; normal Python reflection and exception tracebacks remain possible. [Observation types, lines 325–343][result-source]

The review retains these reporting qualifications:

- `compiledModuleNames` is assigned after all three compilations succeed. It records completion of that batch, not a per-compilation journal. A later compilation failure could leave the list empty after an earlier compile succeeded. All compilation precedes initialization; this does not erase an attempted candidate initialization. Test 16 interrupts only the first candidate compile.
- Ordinary `Exception` paths become closed reports. A serialized report is not guaranteed after `BaseException`, abrupt termination, resource failure, serialization failure or failed output. No successful observation follows those uncompleted paths.
- Helper cleanup tests cover success, helper-compilation `RuntimeError` and AP2 rejection. Arbitrary registry replacement is outside the trusted-process boundary; a changed entry is rejected rather than deleting an unrelated replacement.
- Unsupported/missing CLI arguments follow argparse: exit 2, empty stdout and diagnostic stderr. They are not JSON rejections. Wrong pins and handled observation failures produce closed JSON.
- Source `independentlyReviewedImportBootstrap="Pending"` remains unchanged. This external independent verdict accepts the exact source without repinning that constant, granting executable admission or changing approval state.

These are explicit limits on evidence and interpretation. No correction to implementation is required to accept the requested fixed-initialization claim. [Exact source][source] · [Tests][tests]

## 6. Test reach and additional considerations

The AP3 fixture adapter reuses AP2's construction helpers without inheriting its 25 test methods. AST analysis finds exactly **20 AP3 methods**. The outer suite requires actual `-I -S -B` and explicitly imports reviewed fixture helpers from its local test directory. That trusted harness setup is distinct from the candidate import mechanism. The companion evidence lists every qualified method in all four suites and its source range. [AP3 tests][tests] · [Method inventory][evidence]

| AP3 method | Independently inspected reach and limit |
| --- | --- |
| 01 | Fresh real AP2 snapshot, actual private object/function identities, source identities, non-main names and recorded progress. |
| 02 | Full actual ordered 23-request direct-import trace and provider classification. |
| 03 | Inert canonical ambient module objects remain unchanged and are not selected for private bindings. |
| 04 | Candidate-aware meta finder and path-importer cache are not consulted for candidate names. |
| 05 | Inert source and opaque non-executable bytecode remain unread/unchanged during guarded initialization; no alternate candidate program executes. |
| 06 | Line tracing observes real path identity/content and the writer's private list insertion throughout the fixture. |
| 07 | Candidate frame profiling and content/process API guards during initialization; protected synthetic roots remain empty. |
| 08 | Real post-capture writer pathname change does not replace compiled snapshot bytes; no post-import custody is asserted. |
| 09 | Invalid/mismatched pin, changed/text/mutable/oversized raw input rejected before helper acquisition. |
| 10 | Helper read seam appends harmless bytes; mismatch rejects before compilation. This is not a physical helper-file replacement fixture. |
| 11 | Private snapshot seam rejects malformed, missing, duplicate, mutable, mismatched or oversized records before compile. |
| 12 | Private consistency seam rejects roster/mode/blob discrepancies and selected unclosed AP2 report fields. Full schema provenance still comes from fresh AP2. |
| 13 | Unsupported importer forms and unavailable ordered dependencies rejected by direct importer calls; no alternative candidate source executes. |
| 14 | One immutable JSON field, frozen assignment, fresh report copies and restricted API signature. |
| 15 | Ordinary import-stage interruptions retain attempted/completed prefixes and writer-import status, with closed reports. |
| 16 | First candidate compile interruption records no candidate initialization; later-compile and forced-termination accounting are not covered. |
| 17 | Temporary authenticated-helper registration removed on success, compile interruption and AP2 rejection. |
| 18 | Actual isolated CLI amid inert CWD/PYTHONPATH fixtures; refs/index/tracked bytes/status and protected-output observations remain unchanged. |
| 19 | Three CLI cases each omit one required isolation/no-site/no-bytecode condition and reject. |
| 20 | Wrong supplied pin, five execution-option forms and missing required arguments reject; argparse cases intentionally emit no JSON. |

Additional static considerations were adjudicated separately from those completed tests:

| Consideration | Disposition for this exact source |
| --- | --- |
| Caller supplies a fabricated successful bundle or importer | No public parameter accepts it; the observer obtains fresh authenticated AP2 evidence. Private test seams are not public provenance. |
| Ambient AP2/candidate cache entries satisfy dependencies | AP2 selection uses authenticated bytes; candidate selection uses private objects. No such ambient fallback exists. |
| Helper or candidate pathname changes after capture | The checked captured bytes remain the compilation input. Later path metadata and runtime reads do not acquire custody from that fact. |
| Ordinary JSON reparsing loses prior strictness | The same immutable raw closure has already passed AP2's strict validation and exact proposal comparison. |
| Candidate proposal literal becomes execution approval | It remains artifact identity; the authority field stays null and the production defining constants remain None. |
| Private builtins, capable standard-library objects or immutable JSON imply a sandbox | Explicitly excluded. The fixed reviewed initialization and trusted process are essential. |
| Partial compilation or external termination is treated as complete initialization evidence | Batch compilation and ordinary-error reporting have the narrower limits stated in section 5; no positive import verdict is produced after uncompleted initialization. |
| Earlier AP2 checkout is interpreted as post-import custody | Explicit scope label and false post-import/custody fields prohibit that interpretation. |

No additional dynamic reviewer fixtures beyond the exact 20-method AP3 rerun are claimed. These considerations are source reasoning, not extra test counts. No material in-scope counterexample was established.

## 7. Raw CI, retained host and independent rerun

### 7.1 Fresh CI and archived Primary evidence

Fresh run **45790198813**, attempt **1**, is a successful completed push run on the specified branch at T. Its single job **139806988184** has matching source/attempt and **11 successful returned step records**, numbered 1–8 and 15–17. The raw checkout prints T. Creation/update are `2026-11-26T09:14:57Z` and `09:15:29Z`. Step numbers do not imply seventeen returned steps. [Run][run] · [Job][job] · [Raw CI archive][ci-log]

The newly retrieved decoded job log matches the committed archive exactly, including leading BOM. Digests below describe UTF-8 re-encoding of the exact Connector-decoded representation, without newline/BOM normalization; they do not attest an unexamined transport archive. The Actions artifact endpoint returns **zero** artifacts. The committed log is the retained evidence copy. [Raw transcript identities][evidence]

| Suite | Methods | Primary host footer seconds | CI footer seconds | Independent reviewer rerun |
| --- | ---: | ---: | ---: | --- |
| R5 | 94 | 0.160 | 0.185 | Retained evidence inspected; not rerun |
| AP1 R2 | 22 | 11.238 | 4.133 | Retained evidence inspected; not rerun |
| AP2 | 25 | 17.980 | 6.721 | Retained evidence inspected; not rerun |
| AP3 | 20 | 9.036 | 4.260 | **20 passed / 9.301s / exit 0** |
| **Total host/CI methods** | **161** | **Four OK footers** | **Four OK footers** | **20 methods independently rerun** |

All 161 qualified source methods appear exactly once and in source order in both retained logs, with actual successful results. R5 methods 36/37 print JSON before next-line `ok`; the inventory check accounts for that. Counts come from executed method records and actual unittest footers, not echoed schema counters. Host records exit 0 after each suite. CI has the corresponding successful pipefail steps. Preparatory 45-method discovery and corrected development runs are not additional qualification. [Host log][host-log] · [CI log][ci-log] · [Full source inventories][evidence]

The source workflow has five Bash run blocks and uses `python3 -I -S -B` for AP3. Primary's prior AST/YAML/Bash/whitespace and historical before/after host-stability checks remain receipt assertions; this review independently recomputed source identities, AST inventories, raw-log correspondence and its own before/after snapshot hashes. It does not retroactively attest Primary's physical host. [Workflow][workflow] · [Primary evidence][primary-evidence]

### 7.2 Independent execution and exact transcript identities

The independent rerun used the downloaded exact source hierarchy and the actual command `python3 -I -S -B .../test_d5b_runner_imports.py -v`. It ran from `2026-11-26T09:47:18.764666+00:00` to `09:47:28.269362+00:00`. The actual unittest footer is **20 tests in 9.301s**; driver elapsed time is **9.504679204s**. All 20 method names match the exact test AST. Fourteen downloaded source/test/configuration/workflow files retained their exact Git blobs before and after execution. The entire 3,619-byte reviewer log is embedded in the companion JSON. [Independent rerun receipt and raw log][evidence]

| Transcript | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| Fresh CI and committed CI archive | 54,594 | `5be56b9b80fb25fc6b268281801645cfabd4d682dd175e9974d6496689307296` | `0f156bf431fb775e2df7ae8c19675e92002c51b2` |
| Committed Primary host | 27,675 | `971abdddbb5acba734c42ab2717d1b29600959aecfdbc4692558e3a42bb403d7` | `bb1d78a280c3eaa3e244ae0d7752a9c762b99e01` |
| Independent AP3 rerun, embedded verbatim in JSON | 3,619 | `f64233e27ce99d796d627ab943b0f7ae10a59cc88c6b27cdf6627de69a700fd3` | `4a980c30a91abcaf7ad3f6ed451039f0f4626262` |

| Environment | Python | Fixture Git | Verifier/auditor Git |
| --- | --- | --- | --- |
| Primary host | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 |
| Focused CI | 3.11.18 | `/usr/bin/git`, 2.56.1 | `/bin/git`, 2.56.1 |
| Independent AP3 rerun | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 |

Both host records describe Linux 6.18.57 x86_64 with glibc 2.41; reviewer Python is `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`. Fixture Git and verifier/auditor Git are different roles and, on these hosts, different versions. These are source-host observations, not Mac/Unity qualification.

The separate retained wrapper-denial gate emits `NotAuthorized`, `outputCreated=false` and `retryAllowed=false`. Host prints exit 2 and the absent-envelope check. CI prints the exit-2 and absence assertions and completes their step successfully; it does not print a separate numeric exit result. This gate and retained suites deliberately invoke existing function/CLI logic. The no-candidate-function claim is limited to the AP3 observer/import phase. [Workflow][workflow] · [Gate records][evidence]

## 8. Preservation and closed authority

Full contents and blobs of all eleven baseline files match at accepted AP2 publication B, exact AP3 source T and documentation HEAD D. Paths below are relative to `Tools/AssemblyShadow/R03IR`:

| Preserved file | Exact unchanged Git blob |
| --- | --- |
| `D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `D5Local/d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `D5Local/test_d5b_runner_closure.py` | `ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976` |

The defining writer constant remains `APPROVED_EXECUTION_ENVELOPE_BLOB=None` at line 47; custody remains `APPROVED_LOCAL_HANDOFF_BLOB=None` at line 25. The preserved plan retains 18 D5-C01–D5-C18 Player cells, zero passed, 18 NoCoverage, null approval authority and closed execution/build/launch gates. The proposal-derived writer inside synthetic AP1/AP2 fixtures does not alter these production source constants. [Writer][writer] · [Custody][custody] · [Plan][plan] · [Preservation evidence][evidence]

Local-owned `Handoff/LOCAL_VALIDATION.md` remains blob `cbc4141a1f79c16c920d1723a81c5507b87b7e5f`; `Handoff/RETURN_TO_WEB.md` remains `411948c65d0ab04a36ed0f43a8944b6c8291ed30`. Their identities were compared without rewriting or interpreting missing Local state. The current closed WEB_TO_LOCAL input is blob `a27cec05efe47af5281706a54d49a1aa3f166881` and is preserved. Earlier AP3-pending labels in that unmodified checkpoint are historical after this external verdict; they do not grant execution or override the new independent decision. [Handoff][handoff] · [Protected records][evidence]

Accepted predecessor decisions remain: R5 `PassDryAdmissionSourceOnly`; AP1 R2 `PassActivationPublicationProposalOnly` with `D5B-AP1-IR-01=ClosedInCorrectedSource`; AP2 `PassRunnerArtifactClosureSourceOnly`. Their original limitations and historical return records remain intact. [R5 review][r5-review] · [AP1 R2 review][ap1-review] · [AP2 review][ap2-review]

All gates remain closed: **`WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `allowNativeBuild=false`; `allowPlayerLaunch=false`.** All 18 real Player cells remain **NoCoverage / 0 passed**. For AP3, real Unity/native/Player validation remains **NotRun**. This review performs no Mac, IL2CPP, Bee, full VM, Mach-O, GC or PID qualification; historical Mac paths remain physically **Unverified**. No Q, production activation, Local integration, approval repinning or Human Review Gate is authorized.

## 9. Publication and stop boundary

This decision is published as a separate independent report and companion evidence beside the Primary packet, with current verdict links prepended to README and CURRENT_STATUS. Their prior contents are retained as exact suffixes. The publication is limited to those four documentation paths and uses documentation HEAD D as its expected parent. Implementation, tests, workflow, design, WEB_TO_LOCAL, Local-owned records, accepted prior reviews and sibling repositories are preserved.

The containing Git commit supplies this publication's actual identity; the report does not fabricate a self-referential commit SHA or substitute its publication for the CI source. Publication completion requires a non-forced expected-head update and remote readback of the four files, changed-path comparison, protected identities and all four feature refs. The final handoff records the resulting commit and readback outcome.

**Final source-only decision: `PassRunnerImportBootstrapSourceOnly`. Stop after independent publication and remote readback.** No subsequent milestone or execution is part of this review.

[source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py
[design]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md
[evidence]: D5B_RUNNER_IMPORTS_AP3_INDEPENDENT_EVIDENCE_2026-11-26.json
[request]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_INDEPENDENT_REVIEW_REQUEST_2026-11-26.md
[primary]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_PRIMARY_2026-11-26.md
[primary-evidence]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_EVIDENCE_2026-11-26.json
[handoff]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md
[source-commit]: https://github.com/night-outlook/hybridclr_demo/commit/bcf3a9470a12758b210738476d18f80bf60d2eaf
[docs-commit]: https://github.com/night-outlook/hybridclr_demo/commit/246aedcd9e3aa9d09dd1bad2aba1a00864c94416
[api-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L346-L386
[helper-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L104-L174
[snapshot-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L177-L202
[imports-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L47-L67
[importer-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L205-L223
[initialize-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L226-L282
[closed-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L285-L322
[result-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L325-L343
[tests]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py
[test-capture]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py#L432-L459
[test-progress]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py#L604-L694
[workflow]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
[ap2-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py
[ap1-source]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[writer]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py
[preflight]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py
[custody]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py
[plan]: https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json
[ap2-review]: https://github.com/night-outlook/hybridclr_demo/blob/20ca45419ca797ed2bcd330a7be0698fab59819f/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md
[ap1-review]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_2026-11-25.md
[r5-review]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md
[run]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813
[job]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813/job/139806988184
[ci-log]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_CI_45790198813_JOB_139806988184.log
[host-log]: https://github.com/night-outlook/hybridclr_demo/blob/246aedcd9e3aa9d09dd1bad2aba1a00864c94416/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_SOURCE_HOST_2026-11-26.log
