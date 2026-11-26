# D5-B AP2 — independent runner artifact closure review

**Verdict: `D5BRunnerClosureAP2IndependentReview=PassRunnerArtifactClosureSourceOnly`.**  
**Exact implementation:** `night-outlook/hybridclr_demo@8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`.  
**Documentation/evidence HEAD examined:** `b762c12be15e3d0d1c32658b194f541c945fa7be`.  
**Review date:** 2026-11-26 America/Los_Angeles. Primary filenames/date labels and actual UTC execution timestamps retain their original meaning.

## 1. Decision and scope

AP2 satisfies its declared source-only contract for authenticating six runner-owned artifacts and making bounded checkout observations. It constrains the caller's closure proposal with reviewed pins, authenticates the AP1 helper before loading it, leaves candidate modules inert, compares committed-tree/index metadata with a verifier-owned raw-byte worktree inventory, and returns immutable byte snapshots with closed authority fields. **No material in-scope defect or unsupported successful-verification claim was established.** [Exact verifier][verifier] · [Design][design] · [Independent machine evidence][evidence]

This verdict does not establish a runnable activation, future runtime imports, full executable closure, four-source admission, live remote refs, Q authority/revocation, exclusive custody, physical Mac qualification or explicit user approval. Those remain false or deferred in the implemented report. R5 `PassDryAdmissionSourceOnly` and AP1 R2 `PassActivationPublicationProposalOnly` remain preserved within their accepted scopes; D5B-AP1-IR-01 remains closed for its corrected source. [R5 review][r5-review] · [AP1 R2 review][ap1-review] · [Verifier report fields][report-source]

The reviewer acted separately from Primary Implementation and Local Validation. The review began with current committed README, closed WEB_TO_LOCAL and the AP2 request, then inspected the design, exact code, tests, workflow, accepted decisions, production gates and raw evidence through GitHub Connector. Missing state was not inferred from chat. Supporting independent analyses covered artifact/schema/helper boundaries, checkout observations and CI/preservation. Final adjudication integrates those analyses with direct source inspection and one independent exact-source AP2 rerun. [Request][request] · [Closed handoff][handoff]

The permitted rerun used temporary Git repositories and synthetic locations on Linux. It did not run Local admission, Unity, a native build or Player, or import/execute candidate wrapper/writer/preflight modules. R5 and AP1 suites were not independently rerun. No implementation, approval pin or production activation was changed. The companion JSON retains the entire reviewer log and distinguishes it from archived Primary execution.

## 2. Exact revisions and provenance

All four feature branches are `codex/assembly-shadow-r01b-h1`. Fresh remote reads matched the supplied heads:

| Repository | Exact AP2 source pin | Remote head before independent publication |
|---|---|---|
| `night-outlook/hybridclr_demo` | `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a` | `b762c12be15e3d0d1c32658b194f541c945fa7be` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Same |

The tested source has sole parent `653930479b37230d757ed8a089e320b0ac53998b`, the AP1 R2 independent publication, and tree `f523f6d509b3409de09bc8bf5f67d872fad9de3e`. Its one-commit increment changes four paths: new AP2 verifier, new AP2 tests, AP2 design and focused workflow. The later `b762c12b…` commit has sole parent `8a856ab6…` and changes eight paths, all under `Docs/AssemblyShadow`. All four source-increment files are byte-identical in that successor. The independent publication containing this report is another documentation revision, not the CI checkout. [Source commit][source-commit] · [Documentation commit][docs-commit]

| Source-increment file | Verified Git blob | Bytes |
|---|---|---:|
| `D5Local/d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` | 30,031 |
| `D5Local/test_d5b_runner_closure.py` | `ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976` | 42,800 |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `2aff9a399708f90f58fe312f8c03a90b101ae16a` | 5,013 |
| AP2 design | `742f385b15335c8ecf842283d6470bfb49b5f8fd` | 11,291 |

The first two paths are relative to `Tools/AssemblyShadow/R03IR`. Downloaded execution snapshots were independently hashed against their Connector Git blobs before and after the reviewer run. Complete input identities, comparisons and inventories are in the companion evidence. Remote repository identity does not qualify physical checkout state. [Independent machine evidence][evidence]

## 3. Closure policy, ownership and trust

### 3.1 The six artifacts form the declared direct dependency set

The existing wrapper imports the writer. The writer imports its sibling preflight module and reads its runner-relative plan. The preflight reads its runner-relative profile. Static inspection of this chain found no further repository-local imports. AP2's catalog contains those five runner-owned files plus E:

| Artifact, relative to `Tools/AssemblyShadow/R03IR` | Required identity |
|---|---|
| `D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `D5Local/d5b_local_admission.py` | Base `99746fe64976da313cbd0e1625f0fcc5a67bca62` with only AP1's exact literal substitution to E's blob |
| `D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `D5Local/d5b_activation_publication_proposal_v1.json` | Exact E blob with closed AP1 proposal contents |

The wrapper import is at line 9; writer ownership is at lines 24–31 and plan reading at 120–126; preflight profile ownership is at lines 18–21 and its read at 289. The profile belongs to A's closure even though the preflight separately examines a same-path source-workspace profile as data. Pinsets, native/overlay files, evidence-producer sources and historical comparators inspected under H are a separate source-input set. AP2 retains `sourceDataInputsVerified=false`. [Wrapper][wrapper] · [Writer][writer] · [Preflight][preflight]

An unchanged helper already altered in H also appears unchanged in A, so AP1's two-path delta alone cannot authenticate it. AP2's four fixed catalog pins reject that situation; AP1 separately pins the writer base and exact derived writer. Method 05 first establishes a valid AP1 publication for each changed fixed dependency and then observes AP2 catalog rejection during proposal construction. The same catalog is reconstructed during verification. This test is not described as reaching full verification after its constructor has already rejected. [Verifier, lines 232–283][catalog] · [Tests, lines 306–335][tests]

### 3.2 External C does not become authority

C follows the already-known A and is not inserted into A's tree. It binds H/A/E, canonical repository identity/ref, declared location literals and the exact artifact/import roster. A future Q would bind C externally; neither record embeds its own hash. This avoids making A or E predict C. The constructor validates real proposal objects and location spelling, writes nothing and makes no protected-root custody claim. [Design][design] · [Catalog/proposal source][catalog]

Verification first requires exact bytes, the 1 MiB input bound and an external lowercase Git-blob pin. It reconstructs expected policy from the authenticated AP1 audit and fixed catalog. The helper's parser rejects duplicate keys at every depth, invalid UTF-8, nonobjects, named non-finite constants and excessive JSON nesting. Its recursive comparison requires exact types, key sets and values, including boolean/integer distinctions. Caller-controlled roles, file pins, repository identity, scope or authority cannot replace that policy. [Verifier, lines 506–523][verify-source] · [AP1 helper, lines 88–145][ap1-policy]

The C pin is byte identity only. Origin is checked against six accepted canonical spellings and the observed spelling is recorded; C does not pin one literal URL, and local origin configuration is not remote authentication. Methods 03/04 and 11 address the external-pin, schema, authority, identity and origin boundaries. [Tests][tests] · [Checkout source][checkout-source]

### 3.3 Reviewed helper loading and candidate inertness

AP2 reads the installed AP1 helper through bounded no-follow reads, checks blob `ecf36a7a51f1750c6e8425ee79e9ac8938102b54`, and only then compiles/executes those same immutable bytes into a new module. It does not choose the helper through a candidate module name or load its pathname again after authentication. Candidate artifacts are data. Method 02 guards candidate import names and candidate frame filenames during verification. [Verifier, lines 206–229][helper-source] · [Tests, lines 227–248][tests]

The preserved helper retains actual-object/hash checks, corrected H/A topology interpretation, canonical/direct refs, sole-parent relationship, exact E contents, literal writer substitution and the two-path delta. E remains `R03D5BActivationPublicationProposalV1`. The preserved executable writer requires a distinct approved-envelope kind and independent/user/open-handoff conditions. Binding the derived writer literal to E therefore does not make E an execution approval. [AP1 helper][ap1-helper] · [Writer, lines 454–476][writer]

Verifier installation, Python/stdlib, selected Git and OS remain trusted infrastructure. The API assumes a trusted process. The CLI requires `-I -S -B` for this verifier invocation; it does not implement a future runner loader. Ambient imports, bytecode, extension loading and runtime bootstrap remain deferred, with `runtimeImportIsolationVerified=false` and `runnerExecutableClosureVerified=false`.

## 4. Checkout observations and bounded reads

### 4.1 Git metadata and index equality

The verifier requires canonical ordinary directory-based runner/`.git`/objects/refs locations, a non-bare repository, equal absolute Git/common-directory identity, no observed shallow/graft/alternate-store markers, one supported origin, and exact HEAD/checked-out branch/direct ref A. The trusted helper sanitizes Git execution, disables replacements, hooks, fsmonitor, lazy fetch and protocol use, rejects includes/extensions/partial-clone settings, and requires SHA-1 objects. AP2 additionally rejects configured filters, URL rewrites and specified worktree/hidden-status/sparse/split-index/external-diff settings. [Checkout source][checkout-source] · [AP1 helper, lines 163–224][ap1-helper]

Index checks require accepted `ls-files -v` flags, unique stage-zero entries and full path/mode/blob equality with every non-directory committed-tree entry. Submodules and unmerged entries reject. This is semantic equality of Git-reported entries, not a fingerprint of every raw index byte or a complete index-format classifier. Rejecting `core.splitindex` configuration is not claimed to classify every physical index representation. [Verifier, lines 444–462][checkout-source]

The implementation also does not provide descriptor-based private custody of every administrative child inside `.git`. The worktree inventory intentionally excludes that top-level directory. Explicit layout checks and Git-reported configuration/ref/index observations define this boundary; no full `.git` fingerprint or exclusive-custody assertion is returned. These possible scope edges were considered without finding a contradiction with the declared comparison.

### 4.2 Verifier-owned worktree equality

The tree inventory uses authenticated raw Git metadata, explicit supported modes, UTF-8 paths and entry/depth limits. At every worktree directory it compares the exact actual name set against the expected committed entries. Regular bytes are streamed through its own Git-blob hash; tracked symlinks are compared as literal link bytes without target traversal. Ignored, untracked or missing entries and extra empty directories reject. [Verifier, lines 286–409][inventory-source]

No Git `status`, `diff`, `hash-object`, filter or worktree-conversion operation supplies the verification comparison. Method 21 checks the actual verifier command set. Methods 07/08/09 include conditions where ordinary Git status can appear clean but AP2 rejects. Fixture setup uses normal Git creation/mutation commands; those commands are not confused with verifier operations. [Tests][tests]

General tracked regular leaves require one hard link, owner-execute-bit agreement with Git mode, exact raw bytes and descriptor/named-entry fingerprint consistency. Exact equality of every permission bit is not claimed. General tracked symlinks are intentionally allowed as literal data, including a positive dangling-target control. The strict six-artifact set remains regular-only. Converted line endings, smudge/LFS materialization and future execution are not qualified. [Inventory source][inventory-source] · [Tests, lines 753–805][tests]

### 4.3 Stricter artifact reads and limited resources

Each artifact must have Git mode `100644` and correct object identity. Descriptor-relative reads reject symlink ancestors/leaves and require regular single-link files, no filesystem execute bits and at most 1 MiB. They compare descriptor/named-entry fingerprints, length and ancestor identity. Verification retains immutable bytes, rereads them and their fingerprints, repeats publication checks, repeats the complete checkout observation and reobserves protected roots. [Verifier, lines 158–203][artifact-read] · [Verification sequence][verify-source]

Wider per-scan limits are **256 MiB per regular leaf, 4 GiB total leaf bytes, 100,000 entries and directory depth 64**. These do not establish a cumulative I/O, process-memory or elapsed-time sandbox. Methods 24/25 use reduced constants and modest fixtures to exercise rejection boundaries and relevant positive controls; they are not 4 GiB load testing or exhaustive platform/resource qualification. [Design][design] · [Tests, lines 807–837][tests]

### 4.4 Separation and rechecks

Protected roles include the workspace, four source children, six historical roots and evidence parent. Path spelling, canonical resolution, directory identities and ancestor identities enforce runner separation. The evidence parent is also separated from workspace/history. Historical roots may nest as designed. Their contents are not admitted as source or evidence by these observations. [Verifier, lines 85–150][locations-source]

`sameSnapshotAtRecheck=true` means equality of recorded observations. It is not one simultaneous global filesystem snapshot, continuous ownership, a namespace lock, or exclusion of intervening/ABA/post-return replacement. Methods 15–18 inject real byte, inode, ancestor, ref/config and protected-directory changes at controlled boundaries. Method 17 may reject during the earlier inventory scan; its diagnostic does not prove that rejection occurred exclusively in the later artifact reader. The retained R5 namespace/custody limits remain relevant to future admission. [Tests][tests] · [Design][design] · [R5 review][r5-review]

## 5. Regression reach and preservation

The AP2 inventory has **25 unittest methods**, with multiple subcases. Counts are method counts. Tests use actual temporary Git objects and synthetic roots; selected patches control observation timing or lower resource constants. They do not qualify a production checkout. [Exact tests][tests]

| Methods | Coverage established |
|---|---|
| 01 | Six immutable records, ordinary mutation rejection, fresh report copies, retained snapshot after later file changes |
| 02 | Candidate import/execution guards during verification |
| 03–04 | External pin before helper loading; JSON/type/schema/authority/import-map/roster rejection |
| 05–06 | Changed fixed dependencies in otherwise-valid AP1 objects; unsupported artifact Git modes/types; catalog rejection during construction |
| 07–10 | Tracked/staged/untracked/ignored changes, hidden index flags, artifact links/execute bits and directory aliases |
| 11–14 | HEAD/branch/ref/origin, specified config and administration rejection, canonical disjoint location roles |
| 15–18 | Real byte/inode, ref/config, ancestor and protected-directory changes detected at controlled observation boundaries |
| 19–20 | Actual isolated CLI; missing isolation flags and wrong-pin rejection; no execution override; refs/index/artifacts unchanged and synthetic evidence/source directories empty |
| 21 | Object/metadata Git operations only, without conversion |
| 22 | Positive general tracked executable and literal symlink outside the six artifacts |
| 23 | Unrelated tracked changes and extra empty directories |
| 24–25 | Scaled per-file/aggregate byte thresholds and entry/depth bounds |

Unknown CLI switches deliberately produce argparse exit 2, empty stdout and an argument diagnostic. Expected verification failures produce closed rejection JSON. No claim is made that every process termination, arbitrary resource failure or argument-parse error yields an observation object. The outer suite uses `-B`; isolated `-I -S -B` behavior belongs to its actual child CLI tests. [Tests, lines 676–730][tests] · [CLI source][cli-source]

Nine baseline files were freshly compared at accepted AP1 R2 source `2a0053bbe350bc52b189ca4201542b2c93b5eca7`, accepted review/base `653930479b37230d757ed8a089e320b0ac53998b`, AP2 source and its documentation successor. Raw contents and independently computed Git blobs match across all four refs:

| Preserved path, relative to `Tools/AssemblyShadow/R03IR` | Git blob |
|---|---|
| `D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |

This includes the complete retained 94/22 suites and accepted AP1 R2 correction. The companion record contains full 94/22/25 method inventories and agreement with actual CI/host rosters. Preservation comes from fresh repository bytes and comparisons, not inherited chat descriptions. [Independent machine evidence][evidence]

## 6. Raw execution evidence

### 6.1 Actions provenance and actual results

Fresh metadata and raw logs identify **run 45774292828 / job 139754092541 / attempt 1**, event `push`, the required branch, workflow ID `428785163` and exact source/checkout `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`. The run is completed/success with **1 successful returned job and 10 successful returned steps**. Step numbers are **1–7 and 13–15**, not fifteen returned steps. Run creation/update timestamps are `2026-11-26T07:18:06Z` and `2026-11-26T07:18:31Z`. [Run][run] · [Job][job] · [Raw CI archive][ci-log]

Actual qualified method rosters match source AST inventories exactly on CI and the retained host log, without missing, extra or duplicate names. Three actual unittest footers and `OK` results establish **141 passing methods**. Workflow echo receipts and grep command text are not substitutes for those results. The workflow uses pipefail and explicit count/OK checks. Actions reports **zero uploaded artifacts**; freshly fetched decoded raw bytes and the committed identical archive are the CI evidence. [Workflow][workflow] · [CI log][ci-log] · [Independent evidence][evidence]

| Evidence | UTF-8 bytes | SHA-256 |
|---|---:|---|
| Fresh decoded CI log and identical archive, BOM preserved | 47,973 | `f86025615a33de28d13ab585230dd5b6a238039d66afff0db6187253ecfdf105` |
| Retained Primary host log | 23,828 | `11651964c906570888ca035e1d5aa6e5db7f63fcb7be5801d2060f75f2f6c3d2` |
| Independent AP2 rerun, raw log embedded in companion JSON | 4,373 | `3a1557c756917d843fe4aff1151accd00ff22f6b3d963d85cb2d5cbcf03f17c2` |

The CI archive blob is `1fd5fc887ee35653b070d1e1d2952a42a364c968`; the host archive blob is `6d10cc5d23679700c4086a27fe199b07125caa2c`. The retained host execution remains Primary-origin evidence independently inspected here, not a new reviewer execution. [CI archive][ci-log] · [Host archive][host-log]

### 6.2 Environments and independent rerun

| Evidence environment | Python | Fixture Git | Auditor Git | Actual footers, all OK |
|---|---|---|---|---|
| GitHub CI | 3.11.18 | `/usr/bin/git`, 2.56.1 | `/bin/git`, 2.56.1 | R5 94 / 0.188s; AP1 22 / 4.220s; AP2 25 / 6.797s |
| Retained Primary Linux host | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 | R5 94 / 0.189s; AP1 22 / 11.934s; AP2 25 / 19.305s |
| Independent Linux rerun | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 | AP2 25 / 15.418s |

Fixture and auditor selections are separate observations. The independent platform was Linux 6.18.57 x86_64 with glibc 2.41. Its run began `2026-11-26T08:22:17.452860+00:00` and completed `2026-11-26T08:22:33.053654+00:00`, exited **0**, contained one actual 25-method footer and one `OK`, and left all downloaded execution-source bytes unchanged. Its command, identities, environment and entire raw output are retained in the companion JSON. No reviewer R5/AP1 rerun or target-Mac qualification is claimed. [Independent evidence][evidence]

Primary's earlier 25-method/20.623s preparatory run and internal peer correction remain development history, not extra passing methods or independent approval. The final archived host/CI evidence and separate reviewer rerun are the execution records used here. Final source and method 21 substantiate removal of conversion operations without relying on a preparatory transcript. [Primary report][primary] · [Tests][tests]

### 6.3 Closed production gate

CI actually emits `NotAuthorized`, `outputCreated=false`, `retryAllowed=false` and closed admission/handoff fields. The successful shell assertions require exit **2** and absence of the unapproved-envelope path. The numeric code is established by the assertion, not a separate printed exit line. The host archive separately prints **EXIT 2** and **CHECK unapprovedEnvelopePathAbsent=true**. Both were checked; the independent reviewer did not invoke this Local wrapper. [Workflow][workflow] · [CI log][ci-log] · [Host log][host-log]

## 7. Authority, physical state and publication

The production writer defining assignment remains `APPROVED_EXECUTION_ENVELOPE_BLOB = None` at line 47; the custody module's defining assignment remains `APPROVED_LOCAL_HANDOFF_BLOB = None` at line 25. Both were read in their modules rather than inferred from report fields. The closed plan is unchanged. [Writer][writer] · [Custody module][custody] · [Plan][plan]

| State | Independent disposition |
|---|---|
| `D5BRunnerClosureAP2IndependentReview` | `PassRunnerArtifactClosureSourceOnly` |
| R5 / AP1 R2 decisions | Preserved within their original scopes |
| D5B-AP1-IR-01 | Remains `ClosedInCorrectedSource` |
| Both production approval constants | `None` |
| `WEB_TO_LOCAL` | `CLOSED_NO_LOCAL_EXECUTION` |
| `D5BLocalExecution` / `D5LocalValidation` | `NotAuthorized` / `NotAuthorized` |
| `R03Accepted` / `H2Passed` / `ReadyForHumanReviewGate` | `false` / `false` / `false` |
| Native build / Player launch authorization | `false` / `false` |
| Real D5-C01 through D5-C18 | All `NoCoverage`; 0 passed |
| Candidate Local/macOS, Unity, IL2CPP, Bee, full VM, Mach-O, GC, PID and Player work | `NotRun` |

All four supplied Mac paths under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/` remain historical candidates with physical state **Unverified**. Remote reads and Linux fixtures provide no physical admission, APFS/crash qualification or Local evidence. Runner loading, full source admission/live refs, a production plan/adapter, Q approval/revocation, controlled custody and explicit user approval remain future work. [Closed handoff][handoff] · [Request][request]

Publication is limited to this independent report and companion evidence, plus current-verdict prepends/links in README and `Plan/CURRENT_STATUS.md`. Earlier records remain intact. Implementation, tests, workflow, approval pins, WEB_TO_LOCAL, Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, and sibling repositories are preserved. Earlier AP2-pending checkpoint labels remain historical beneath the current decision and grant no execution authority.

Publication uses `b762c12b…` as expected parent/head for a non-forced update. The containing commit supplies its publication identity; this report does not embed a self-referential hash. Completion records remote readback of the four exact publication files, protected identities and branch heads.

**Final decision: PassRunnerArtifactClosureSourceOnly. No material AP2 return finding established. All Local gates remain CLOSED. Stop after independent publication and remote readback.**

[evidence]: D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_EVIDENCE_2026-11-26.json
[verifier]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py
[helper-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L206-L229
[catalog]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L232-L283
[locations-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L85-L150
[artifact-read]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L158-L203
[inventory-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L286-L409
[checkout-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L412-L468
[verify-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L506-L563
[report-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L471-L563
[cli-source]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L578-L600
[tests]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py
[ap1-helper]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[ap1-policy]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L88-L145
[wrapper]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py
[writer]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py
[preflight]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py
[custody]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py
[plan]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json
[workflow]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
[design]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_DESIGN_2026-11-25.md
[primary]: https://github.com/night-outlook/hybridclr_demo/blob/b762c12be15e3d0d1c32658b194f541c945fa7be/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_PRIMARY_2026-11-25.md
[request]: https://github.com/night-outlook/hybridclr_demo/blob/b762c12be15e3d0d1c32658b194f541c945fa7be/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md
[handoff]: https://github.com/night-outlook/hybridclr_demo/blob/b762c12be15e3d0d1c32658b194f541c945fa7be/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md
[ap1-review]: https://github.com/night-outlook/hybridclr_demo/blob/653930479b37230d757ed8a089e320b0ac53998b/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_2026-11-25.md
[r5-review]: https://github.com/night-outlook/hybridclr_demo/blob/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md
[ci-log]: https://github.com/night-outlook/hybridclr_demo/blob/b762c12be15e3d0d1c32658b194f541c945fa7be/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_CI_45774292828_JOB_139754092541.log
[host-log]: https://github.com/night-outlook/hybridclr_demo/blob/b762c12be15e3d0d1c32658b194f541c945fa7be/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_SOURCE_HOST_2026-11-25.log
[source-commit]: https://github.com/night-outlook/hybridclr_demo/commit/8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a
[docs-commit]: https://github.com/night-outlook/hybridclr_demo/commit/b762c12be15e3d0d1c32658b194f541c945fa7be
[run]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45774292828
[job]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45774292828/job/139754092541
