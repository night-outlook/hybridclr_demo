# D5-B AP1 R2 — independent source review

**Decision: PassActivationPublicationProposalOnly.**  
**Finding: D5B-AP1-IR-01 — closed for corrected source `2a0053bbe350bc52b189ca4201542b2c93b5eca7`.**  
**Review date:** 2026-11-25 America/Los_Angeles. Recorded execution timestamps retain their actual UTC dates.

This independent review accepts the focused R2 topology correction within AP1's closed activation-publication proposal scope. The shared parser now interprets the initial tree and contiguous parent prefix, rejects misplaced structural headers, and requires agreement with Git's bounded native parent observation. Both source H and runner A pass through that parser; A must still have exactly H as its sole parent. Source inspection, actual stored-object regressions, preservation checks, independently retrieved CI evidence and an independent 22-method AP1 rerun support this decision. No new in-scope blocking finding was established. [Auditor][auditor] · [Tests][tests] · [Independent machine evidence][independent-evidence]

The prior `ReturnRequired` remains the correct historical verdict for implementation `25551bca385c5af20c417110ad1ee27593a3eefc`. This successor decision closes its D5B-AP1-IR-01 return for R2 only. R5's separate `PassDryAdmissionSourceOnly` remains preserved with its existing limits. Neither verdict authorizes Local execution, an executable activation, a Human Review Gate or a later milestone. [Prior independent AP1 report][prior-review] · [R5 independent rereview][r5-review]

## 1. Independence, inputs and method

The reviewer acted separately from Primary Implementation and Local Validation. The review began with committed README, the closed WEB_TO_LOCAL handoff and the R2 independent request, then read the design, prior finding, actual implementation, test modules, workflow, production gates, plan and raw evidence through GitHub Connector. Claims were reconstructed from those current committed inputs and freshly returned GitHub metadata; missing state was not inferred from chat history. Independent supporting reviews covered parser semantics, preservation/regression reach, and CI provenance, with final adjudication by this reviewer. [Request][request] · [Closed handoff at review input][handoff]

The review used static source and byte comparisons, source AST method inventories, actual GitHub run/job metadata, decoded job-log bytes, and the retained Primary host log. It also ran the exact 22-method AP1 suite in an isolated Linux source-host workspace using downloaded, Git-blob-verified source snapshots. This was a temporary-object source test, not target Local admission. The reviewer did not rerun the R5 suite, invoke the Local wrapper, inspect the historical Mac directories, launch Unity/Player, alter implementation or create a production activation ref. The AP1 tests import reviewed production helper code; the substituted candidate writer bytes remain inert and are never imported or executed as a runner. [Tests][tests] · [Independent machine evidence][independent-evidence]

## 2. Exact source, documentation and repository identity

All branch references are `codex/assembly-shadow-r01b-h1`. The following were independently read through the Connector before publication.

| Role | Repository | Commit |
|---|---|---|
| Exact implementation and CI checkout under review | `night-outlook/hybridclr_demo` | `2a0053bbe350bc52b189ca4201542b2c93b5eca7` |
| Subsequent documentation/evidence HEAD; publication base | `night-outlook/hybridclr_demo` | `0332fb12e12df134049eaefade6a6dbf99ca0967` |
| Preserved sibling source pin and remote branch head | `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| Preserved sibling source pin and remote branch head | `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| Preserved sibling source pin and remote branch head | `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

The source commit has sole parent `6d0a5d1613c483119b41d774765ef9752adb7732`, the prior independent review publication. Its four changed paths are the auditor, AP1 tests, source-host workflow and R2 design. The subsequent `0332fb12…` commit has sole parent `2a0053bb…` and changes eight paths, all under `Docs/AssemblyShadow`. It does not change source, tests or workflow. The independent publication containing this report is another documentation revision; it is not the CI checkout. [Source commit][source-commit] · [Documentation commit][docs-commit]

| Exact-source input | Verified Git blob |
|---|---|
| `D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `f9782fa9f78f65c9ac6a3fac81f2bde2c0d30bb0` |
| R2 design | `3c0f077c1b6e08ef91841fd4e22b3f38b1532c0e` |
| Prior independent AP1 report, preserved | `9065580fc26868b1c76b773348657564150c6741` |

The first two paths are relative to `Tools/AssemblyShadow/R03IR`. The companion evidence records complete paths, byte identities, repository observations and comparisons. Remote commit identity does not establish the physical state of any Mac checkout. [Independent machine evidence][independent-evidence]

## 3. D5B-AP1-IR-01 adjudication

### 3.1 Failure contract and correction

The prior auditor collected top-level `parent ` lines throughout a commit's header block. Git obtains parents from the contiguous prefix immediately after the initial tree. Consequently, a later parent-named header could make AP1 claim that A's sole parent was H while Git saw A as a root. Ordinary object storage and a successful strict integrity check did not remove that interpretation discrepancy. The prior return correctly required a shared source/runner correction and stored-object evidence. [Prior independent AP1 report][prior-review]

R2 replaces that scan with a strict supported grammar in `_Git.commit`, lines 261–310. It retains raw-object type, length and Git-object-hash verification before interpreting topology. The initial line must be a tree header with an exact lowercase 40-hex ID. Immediately contiguous parent lines supply ordered parent IDs. The first metadata header closes the parent region permanently; a later parent or another top-level tree rejects. Parent order and multiplicity are retained rather than sorted or deduplicated. [Auditor, lines 235–310][auditor-parser]

| Reviewed requirement | Source behavior | Disposition |
|---|---|---|
| Exact initial tree | Lines 269–278 require the header/message boundary and initial tree; structural ID validation is shared with `_sha` | Satisfied |
| Contiguous parent prefix | Lines 279–284 accept parents only before metadata starts | Satisfied |
| Late/resumed parents | Lines 281–282 reject a parent after metadata | Historical failure closed |
| Duplicate or late tree | Lines 289–295 reject structural field names outside their prefix position | Satisfied |
| Ordered parent tuple | Parsed order and duplicate entries survive through line 310 | Satisfied |
| Shared H/A interpretation | Lines 417–418 call the same parser for both commits | Satisfied |
| Actual runner sole parent | Lines 419–420 require `runner_parents == (source,)` | Satisfied |

Git's own `commit.c` at the separately inspected v2.51.0 source, lines 487–539, corroborates initial-tree/contiguous-parent semantics and the locations where shallow/graft state affects native parentage. That reference is explanatory source evidence; it is not represented as the exact binary source version of either test environment. Actual observed binary versions are recorded in section 6. [Official Git parser][git-parser]

### 3.2 Accepted metadata and messages

A metadata header has a supported printable ASCII field name, a space separator and opaque value bytes. A leading-space continuation is permitted only after metadata has begun. A continuation containing tree- or parent-looking text is content, and it cannot reopen the parent prefix. Everything after the first blank-line boundary is message content. The implementation decodes structural object IDs and the native observation, not the complete metadata/value/message block. [Auditor, lines 269–310][auditor-parser]

This correctly supports the ordinary metadata, synthetic signature-continuation and message controls in method 20. It does not authenticate signatures, assign new author/committer semantics or promise acceptance of every Git-storable header format. The new positive fixtures use ASCII values; non-UTF-8 opaque-value handling is supported by static inspection, not claimed as a separately executed positive fixture. Unsupported structural formatting fails closed. [Method 20][test-new]

### 3.3 Bounded native agreement

For each H and A, lines 301–309 invoke `rev-list --no-walk --parents <oid> --` through the same sanitized read-only Git path. Exactly one ASCII output row is required, and its token sequence must equal `[oid, *parsedParents]`. Command failure, wrong commit identity, absent or extra parents, changed order/cardinality or additional rows cannot satisfy this comparison. The invocation supplies one validated object ID, no revision range, and `--`; the documented no-walk form does not traverse ancestors. [Auditor][auditor-parser] · [Official no-walk documentation][git-nowalk]

The check detects an effective local shallow/graft view that changes the parent tuple. It does not categorically reject the presence of shallow/graft state when the observed tuple remains identical. The real regression uses a temporary shallow file, not a separate graft fixture. Agreement is a point-in-time local observation: it supplies no namespace lock, live-remote guarantee, complete ancestry validation, signature verification or physical custody proof. Those limits do not recreate the late-header false parent claim. [Method 19][test-new] · [R2 design][design]

**Finding disposition:** D5B-AP1-IR-01 is closed for the exact corrected source. Both grammar enforcement and native agreement protect the source and runner paths; the closure is supported without relying on an unarchived old-auditor negative control.

## 4. Real stored-object regressions and counterexamples

Methods 19–22 are four appended unittest methods with multiple subcases. The evidence does not count their subcases as separate methods. They use actual temporary Git repositories and stored commit bytes, preserve direct ref checks, and exercise native topology with fixture Git and the auditor's separately selected Git. The helpers verify retained raw bytes; ordinary stored-object cases and accepted controls also compare fixture and auditor native observations before the relevant parser/audit result. [Tests, lines 558–762][test-new]

| Method | Objects and roles | Observed reach and result |
|---|---|---|
| 19 — standard prefixes and local mismatch | Ordinary root, single-parent, merge and duplicate-parent prefixes, for source and runner roles | Parser/native order and cardinality agree. H accepts these supported shapes; A accepts only a single H parent. An actual shallow-file view removes native parents and causes both direct parser and full audit rejection in both roles. |
| 20 — metadata, continuations and messages | Ordinary metadata; synthetic `gpgsig` with leading-space structural-looking continuations; structural-looking message lines; both roles | Direct parser and full audit retain the actual single parent and accept. Signature text is explicitly synthetic/unverified. |
| 21 — ordinarily stored late parents | Late-only parent after identities and parent block interrupted by identities; both roles | Git reports no parents for late-only, and only the initial other parent for the split block. Direct parser and full audit reject both. Strict `fsck` success is asserted for late-only in both roles; it is not claimed for the split block. Runner variants also retain the valid runner's writer/envelope bytes. |
| 22 — late/duplicate/misordered structure | Ordinary late tree; literal-only duplicate initial tree; five further literal-only malformed layouts; both selected roles | All reject. Late tree and duplicate initial tree reach full audit as well as the shared parser. The five remaining layouts have direct-parser coverage only. |

The five direct-only layouts in method 22 are parent before tree, metadata before tree, missing tree, continuation before metadata and tab-separated parent. Some malformed objects cannot be installed as refs by Git, so the tests deliberately do not mock ref acceptance to manufacture full-audit coverage. Their role labels select source/runner tree contents; they do not establish separate end-to-end audit executions for those five layouts. The ordinary late-tree case and literal duplicate-tree case are distinguished in both the report and machine evidence. [Method 22][test-new]

The central regression therefore reaches the finding at the necessary boundary: an ordinarily stored commit, a native parent observation, direct exact refs where applicable, and a closed full-audit result. It goes beyond conventional `commit-tree` parent variants. The interrupted-prefix, duplicate-parent, shallow-view and metadata/message controls address adjacent counterexamples without conflating integrity checking with topology interpretation. [Methods 19–22][test-new]

Remaining coverage limits are explicit: there is no new separate non-UTF-8 metadata fixture, no independent graft-file fixture, and no enumeration of every malformed ID length/hex-byte variant. The unchanged `_sha` validation applies to each structural ID. Static inspection and the executed regression classes did not identify a concrete remaining discrepancy requiring a further fixture to adjudicate this return. These are coverage boundaries, not newly demonstrated implementation failures.

## 5. Preservation and unchanged proposal boundaries

Independent byte comparison against AP1 implementation `25551bca…` verified that the complete original **27,318-byte AP1 module prefix**, including all **18 methods, 13 helpers, imports and assertions**, is unchanged. Its original main-guard suffix is also unchanged. Four methods and six supporting helpers were appended. The auditor differs only in `_Git.commit`; every byte outside that method matches the original source. Source AST inventories and raw output independently establish the new 22-method count. [Tests][tests] · [Source commit][source-commit] · [Independent machine evidence][independent-evidence]

The five retained R5 files were compared to exact R5 source `eaca19c08f41245c46dfacbf605cd80480bc3a92`. Their raw contents and Git blobs match:

| Retained file, relative to `Tools/AssemblyShadow/R03IR` | R5 and R2 Git blob |
|---|---|
| `D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |

The retained AP1 controls still cover canonical source/direct distinct refs, stale/missing/symbolic refs, object kinds, exact E pinning, the reviewed R5 writer, one literal substitution, mode/type restrictions, new proposal-path absence in H, strict JSON/schema/type checks, all four source pins, all eleven closed authority fields, normal wrong/multiple/indirect parent cases, proposal rejection by the executable writer, closed CLI output and absence of execution-override arguments. Both raw CI and the independent rerun include those original 18 methods. [Tests, original methods][tests]

The unchanged auditor still checks the closed proposal envelope against H and the sibling pins, exact writer bytes, a two-path H-to-A tree delta and final ref reobservation. The proposal kind remains `R03D5BActivationPublicationProposalV1`, with success limited to `ProposalPublicationStructureVerified_NoExecutionAuthority`. Retained method 16 verifies rejection by R5's executable envelope parser even when a test patches the expected blob to match proposal bytes. The production parser expects a different executable kind. [Auditor, lines 396–459][auditor-audit] · [Writer][writer] · [Tests][tests]

H/E/A/Q constructibility remains the accepted AP1 design: E binds frozen H without embedding the not-yet-known A/Q hashes; A carries the exact writer binding and proposal; later Q would separately publish approval/handoff authority. This focused correction neither implements Q nor resolves runner import/executable closure, a production plan/adapter, live qualification or fifth-runner custody. Those remain deferred Primary requirements, not authority implied by this pass. [R2 design][design] · [Prior AP1 review][prior-review]

## 6. Raw CI, retained host evidence and independent rerun

### 6.1 GitHub Actions provenance and actual result

Fresh GitHub metadata identifies run **45751527263**, attempt **1**, event **push**, branch `codex/assembly-shadow-r01b-h1` and head SHA **2a0053bbe350bc52b189ca4201542b2c93b5eca7**. Job **139680200608**, `future-admission-source-host`, belongs to that run/attempt and head. The raw checkout fetch and subsequent `git log` output name the same source SHA. The run completed successfully with **one returned job and nine returned steps**, all successful; the returned step numbers are 1–6 and 11–13, not thirteen returned steps. [Actions run][run] · [Job][job] · [Decoded raw CI log][ci-log]

The actual raw footers are **94 tests in 0.191s, OK** and **22 tests in 4.230s, OK**. The individual qualified method rosters match the source AST inventories in order, with no missing, extra or duplicate method names and all 116 methods passing. Expected diagnostic JSON interleaved in R5 output is not mistaken for failed or absent tests. The successful step labels or workflow summary alone were not used to infer these counts. The artifact API returns **zero artifacts**; the evidence is the decoded raw job log and its committed byte-identical archive. [Decoded raw CI log][ci-log] · [Workflow][workflow] · [Independent machine evidence][independent-evidence]

| Evidence | UTF-8 bytes | SHA-256 |
|---|---:|---|
| Fresh Connector-decoded CI log and identical retained archive | 40,426 | `689a9416b5e9839973b400c86aa5e3a77e9146a164654dc1b481f6b053c9ce9d` |
| Retained Primary source-host log | 19,186 | `27544339c8929e3b460538eaa398c0ca2d35cf396b06e02f6a1e96b5a2b04eb1` |
| Independent AP1 rerun log, embedded in companion evidence | 3,793 | `7ad32dc05fb53034a95a44a1963dfee367fde75e5dd23ab24597abbb1d8b1992` |

The CI byte identity includes its UTF-8 BOM. Its Git blob is `d17a51962bdf7de1e1cf3d506d0bca0b11bb6ea2`; the Primary host archive blob is `28b62010f925964214fae60c5c504dcda2590925`. The independently fetched CI bytes match the committed archive exactly. The host archive was independently inspected, but its original Primary execution is not relabeled as a reviewer execution. [CI archive][ci-log] · [Host archive][host-log]

### 6.2 Environment and execution separation

| Evidence environment | Python | Fixture Git | Sanitized auditor Git | Actual suite footers |
|---|---|---|---|---|
| CI, Ubuntu 24.04.5 | 3.11.18 | `/usr/bin/git`, 2.56.1 | `/bin/git`, 2.56.1 | R5 94 / 0.191s; AP1 22 / 4.230s |
| Retained Primary Linux host | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 | R5 94 / 0.242s; AP1 22 / 11.797s |
| Independent Linux source-host rerun | 3.12.14 | `/usr/local/bin/git`, 2.56.1 | `/bin/git`, 2.47.3 | AP1 22 / 9.102s |

The fixture and auditor selectors are separate observations; a shell's Git version is not assumed to be the auditor's version. The host and independent platforms report Linux 6.18.57 x86_64 with glibc 2.41. These observations provide no macOS/APFS qualification. [CI log][ci-log] · [Host log][host-log] · [Independent machine evidence][independent-evidence]

The independent run began `2026-11-26T06:13:27.302274+00:00` and completed `2026-11-26T06:13:36.605827+00:00`, with exit **0**, exactly **22 methods**, one `OK` footer and no source-snapshot byte changes. Its complete raw output, command, environment and source identities are embedded in the companion JSON. The AP1 fixtures create disposable Git objects/refs only; they grant no production activation or Local authority. No extra reviewer R5 run is claimed. [Independent machine evidence][independent-evidence]

### 6.3 Closed production refusal and negative-control limits

The CI workflow's separate null-approval check produces `NotAuthorized`, `outputCreated=false`, closed handoff/admission fields and a false same-envelope retry field. The successful shell step explicitly asserts exit code **2** and that the supplied unapproved-envelope path does not exist. The numeric exit code is established by the successful shell assertion, not a separately printed numeric line. The Primary host archive explicitly prints `EXIT 2`, but has no separately printed path-absence assertion; that absence claim is grounded in CI's successful assertion. The reviewer did not invoke this Local wrapper. [Workflow][workflow] · [CI log][ci-log] · [Host log][host-log]

Primary's old-auditor control is classified **ToolTranscriptObservation_NoRetainedRawLog**: four new methods run against the old parser, 17 failed subcase assertions across methods 19/21/22, zero errors, with method 20 positive. There is no retained raw log. This review verified the published classification and count meaning, not that execution independently. The 17 are neither seventeen tests nor current R2 failures, and are excluded from all passing totals. Closure rests on the reviewed correction and retained exact-source evidence. [Request][request] · [Primary report][primary] · [Primary machine record][primary-evidence]

## 7. Authority, physical state and residual boundaries

The actual production constants were inspected in their defining modules, not inferred only from report fields. The writer at line 47 retains `APPROVED_EXECUTION_ENVELOPE_BLOB = None`. The custody module at line 25 retains `APPROVED_LOCAL_HANDOFF_BLOB = None`, blob `185c1bd6603a8c43e4222d30ed8bb057ab94824a`. The plan remains closed and neither review pass substitutes for its still-pending executable-admission review or explicit Local approval. [Writer][writer] · [Custody authority][custody] · [Plan][plan]

| State | Independent disposition after this review |
|---|---|
| `D5BActivationPublicationAP1R2IndependentReview` | `PassActivationPublicationProposalOnly` |
| `D5B-AP1-IR-01` | `ClosedInCorrectedSource` at `2a0053bb…` |
| Original AP1 independent verdict | Historical `ReturnRequired` for `25551bca…`, preserved |
| `D5BDryAdmissionR5IndependentReview` | `PassDryAdmissionSourceOnly`, preserved |
| Both production approval constants | `None` |
| `WEB_TO_LOCAL` | `CLOSED_NO_LOCAL_EXECUTION` |
| `D5BLocalExecution` / `D5LocalValidation` | `NotAuthorized` / `NotAuthorized` |
| `R03Accepted` / `H2Passed` / `ReadyForHumanReviewGate` | `false` / `false` / `false` |
| `allowNativeBuild` / `allowPlayerLaunch` | `false` / `false` |
| Real D5 Player cases D5-C01 through D5-C18 | All `NoCoverage`; 0 passed |
| Candidate Local/macOS, Unity, IL2CPP, Bee, full VM, Mach-O, GC, PID and Player work | `NotRun` |

All four supplied paths under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/` remain historical candidates with physical state **Unverified**. No filesystem inspection, Mac commands or custody observation is implied by remote repository verification. The exact paths are retained in the machine evidence with that classification. [Request][request] · [Closed handoff][handoff] · [Independent machine evidence][independent-evidence]

The accepted R5 namespace/custody limitation remains: unresolved-creation no-adoption behavior does not close every replacement window after a recorded mkdir or after the last identity observation. This R2 review does not promote source-host observations into APFS, hard-kill, crash-durability, execution-custody or real Player evidence. It also supplies no Q approval validation, executable/import closure, production runner authorization or plan adapter. These already disclosed limits remain outside this focused return. [R5 rereview][r5-review] · [R2 design][design]

## 8. Publication and stopping point

This independent publication is limited to this new report, its companion machine evidence, and a current-decision prepend with links in README and `Plan/CURRENT_STATUS.md`. Earlier Primary pending sections and the prior AP1 return remain historical records beneath the current decision. In particular, unchanged pending labels in the closed WEB_TO_LOCAL checkpoint do not reopen the adjudicated source finding or grant execution authority.

Implementation, tests, workflow, both constants, WEB_TO_LOCAL, Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, prior reports and sibling repositories are preserved. The publication is based on `0332fb12…` and uses a non-forced branch update with that expected head; the containing Git commit supplies its publication identity without a self-referential hash in this file. Final completion records the remote readback of the four publication files and preserved boundaries.

**Final decision: PassActivationPublicationProposalOnly. D5B-AP1-IR-01 is closed for AP1 R2 source only. Local execution stays CLOSED. Stop after independent publication and remote readback.**

[independent-evidence]: D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_EVIDENCE_2026-11-25.json
[auditor]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[auditor-parser]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L235-L310
[auditor-audit]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L396-L459
[tests]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py
[test-new]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py#L558-L762
[workflow]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
[writer]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py
[custody]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py#L25
[plan]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json
[design]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_DESIGN_2026-11-25.md
[request]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md
[handoff]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md
[prior-review]: https://github.com/night-outlook/hybridclr_demo/blob/6d0a5d1613c483119b41d774765ef9752adb7732/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_2026-11-25.md
[r5-review]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md
[primary]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_PRIMARY_2026-11-25.md
[primary-evidence]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_EVIDENCE_2026-11-25.json
[ci-log]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_CI_JOB_139680200608_2026-11-25.log
[host-log]: https://github.com/night-outlook/hybridclr_demo/blob/0332fb12e12df134049eaefade6a6dbf99ca0967/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_SOURCE_HOST_2026-11-25.log
[source-commit]: https://github.com/night-outlook/hybridclr_demo/commit/2a0053bbe350bc52b189ca4201542b2c93b5eca7
[docs-commit]: https://github.com/night-outlook/hybridclr_demo/commit/0332fb12e12df134049eaefade6a6dbf99ca0967
[run]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263
[job]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263/job/139680200608
[git-parser]: https://github.com/git/git/blob/v2.51.0/commit.c#L487-L539
[git-nowalk]: https://github.com/git/git/blob/v2.51.0/Documentation/rev-list-options.adoc
