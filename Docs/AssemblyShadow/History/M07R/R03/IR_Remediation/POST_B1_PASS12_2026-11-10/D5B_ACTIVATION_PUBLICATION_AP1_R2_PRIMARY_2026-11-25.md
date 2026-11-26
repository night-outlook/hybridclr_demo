# R03 D5-B AP1 R2 — Primary parser remediation and source-only evidence

**Client date:** 2026-11-25 America/Los_Angeles. Preserve actual UTC execution timestamps in the attached evidence.

**Role:** Primary Implementation. This report does not assign an independent verdict. `D5BActivationPublicationAP1IndependentReview=ReturnRequired` remains the applicable AP1 independent status until separate rereview. R5's `PassDryAdmissionSourceOnly` is retained.

## 1. Focused correction

The [independent AP1 review][prior-review], published at demo `6d0a5d1613c483119b41d774765ef9752adb7732` with report blob `9065580fc26868b1c76b773348657564150c6741`, returned **D5B-AP1-IR-01** against source `25551bca385c5af20c417110ad1ee27593a3eefc`. The old parser counted parent-named lines anywhere in the commit header block. A real stored late-parent object could therefore be reported as A's sole-parent relationship to H even though Git recognized no such edge. Successful strict object checking did not settle that semantic difference.

Primary has replaced that full-header scan with the shared strict-prefix parser and bounded native-parent consistency check described in the [R2 design addendum][design]. The change applies to both source and runner commit parsing. The proposed H/E/A/Q publication separation remains as previously assessed; R2 introduces no source-runner activation mechanism or new authority.

## 2. Exact source and publication identities

| Repository | R2 source tuple |
|---|---|
| `night-outlook/hybridclr_demo` | `2a0053bbe350bc52b189ca4201542b2c93b5eca7` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

The canonical source branch remains `codex/assembly-shadow-r01b-h1`. The new exact source is the identity to use for the [auditor][auditor], [tests][tests] and [workflow][workflow]. Later evidence/status publication commits must be recorded separately; they must not be presented as the CI-tested source.

The focused implementation surface is the AP1 commit parser, appended AP1 regressions, supporting workflow count/version recording, and R2 design. The remote source comparison contains exactly these four paths and one new commit; all four files were read back with exact content and Git blob identity. The source commit has parent `6d0a5d1613c483119b41d774765ef9752adb7732` and tree `a2b1a7ea55a2b20a7e80312b0300eb6bf6b955b9`. This table does not attest to current Mac checkouts or grant source/runner execution permission.

## 3. Parser and Git-view contract

`_Git.commit` retains object-type, exact-byte hash and complete header/message-separator checks. It now requires the initial tree line, followed only by the immediately contiguous parent prefix. Parent order and cardinality are preserved; there is no sorting or deduplication. Once metadata starts, a later top-level tree or parent header is rejected. Metadata has a supported ASCII field name and opaque value bytes; a leading-space continuation requires prior metadata. Continuations and the message cannot introduce topology. No full-header UTF-8 decoding, signature authentication or new author semantics are introduced.

The same parser accepts supported root, linear and merge source topology. Runner A must still have exactly one parsed parent equal to source H. Duplicate genuine parent entries remain visible in the tuple and cannot satisfy that runner rule.

After parsing each source or runner commit, the existing sanitized Git command path performs `rev-list --no-walk --parents <oid> --`. Exactly one row must equal `[oid, *parsedParents]`. An inconsistent effective local view, including a shallow/graft view that changes parentage, rejects. This is a bounded current observation, not a history walk, remote check, namespace lock or authority validation.

Canonical source-ref binding, direct distinct local refs, ref rechecks, the exact closed proposal schema, reviewed R5 writer blob, literal envelope-blob substitution and two-path tree delta remain unchanged. Successful audit still means `ProposalPublicationStructureVerified_NoExecutionAuthority`.

## 4. Regression scope and preservation

The source inventory contains **94 retained R5 methods and 22 AP1 R2 methods**, with **four additions** to the prior 18-method AP1 suite. Primary's preservation record reports all **18 old AP1 method bodies and 13 old helpers byte-identical**. The four new methods use actual temporary Git objects and refs; the candidate writer remains inert object bytes.

| Added method | Concrete coverage |
|---|---|
| `test_19_standard_commit_prefixes_match_git_topology` | Root, linear, merge and duplicate-parent prefixes for both roles; ordered parser/native agreement; only the direct single-parent runner qualifies. A real temporary shallow-file control changes Git's effective parent view and must reject. |
| `test_20_metadata_continuations_and_messages_do_not_add_topology` | Ordinary metadata, signature-like continuations and tree/parent-looking message text preserve the original topology for source and runner. Signature-like text is not authenticated. |
| `test_21_ordinary_stored_late_parents_reject_source_and_runner` | Late-only and split-parent-block layouts are stored through ordinary `hash-object`. Git's observed parents are recorded; the late-only object passes the exercised strict check, yet the shared parser and complete publication audit must reject. Runner tree, proposal and writer bytes stay fixed. |
| `test_22_late_duplicate_and_misordered_topology_headers_are_rejected` | Late/duplicate/misordered/missing tree headers, orphan continuation and tab-separated parent cases. Ordinary-storable cases and literal-only rejection fixtures are distinguished. Full audits run when Git permits ref installation; other malformed objects reach the shared parser directly without mocked refs. |

The R2 topology helper compares fixture Git's `show` and `rev-list` observations with the auditor's sanitized Git observation. Tests do not assume those executable selections resolve to the same Git version.

### Preserved R5 files

| Repository-relative file | Exact retained Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |

Complete-file identity preserves the R5 test bodies/helpers and prior source-only review boundary. It does not establish fresh physical custody or runtime coverage.

### Transcript-only old-auditor negative control

The tool transcript reports **17 failed subcase assertions across methods 19, 21 and 22, with 0 errors**, when exercising the old auditor. **No raw log of that negative-control execution was retained.** This is a supplementary transcript observation, not archived evidence or an independently audited run. The number 17 counts failed subcase assertions, not test methods; it is not included in the R2 suite totals or positive results. Do not manufacture a raw-log path, digest, timing or fuller execution roster for this observation.

## 5. Completed source-host and Actions evidence

The retained host output and freshly fetched Actions metadata/raw log both confirm the 94 and 22 method inventories. Counts below come from actual unittest footers, with complete method rosters and successful `OK` outcomes in the archived logs.

| Suite | Source method inventory | Observed host count | Host unittest footer seconds | CI unittest footer seconds |
|---|---:|---:|---:|---:|
| Retained R5 | 94 | `94` | `0.242` | `0.191` |
| AP1 R2 | 22 | `22` | `11.797` | `4.230` |

The host suites each exited 0; hashes of all four source files were identical before and after validation. Static checks parsed both Python files and the workflow YAML, checked all three workflow shell blocks with `bash -n`, and found no trailing whitespace in the four source files.

| Actions provenance field | Required observed value |
|---|---|
| Exact run/job/checkout source | `2a0053bbe350bc52b189ca4201542b2c93b5eca7` |
| Run | `45751527263` |
| Job | `139680200608` |
| Python | `3.11.18` |
| Fixture Git version | `git version 2.56.1` |
| Sanitized auditor Git version | `git version 2.56.1` |
| Exact decoded raw CI log bytes / SHA-256 | `40426` / `689a9416b5e9839973b400c86aa5e3a77e9146a164654dc1b481f6b053c9ce9d` |
| Retained Primary host log bytes / SHA-256 | `19186` / `27544339c8929e3b460538eaa398c0ca2d35cf396b06e02f6a1e96b5a2b04eb1` |

Fixture commands resolve Git through their test environment; the auditor resolves system Git through `os.defpath` and uses the sanitized environment. The selections are recorded separately below; no version is borrowed from an earlier run.

Actions attempt **1**, event **push**, branch **codex/assembly-shadow-r01b-h1**, run and job **completed/success**: **1/1 focused job and 9/9 returned steps successful**. The run/checkout SHA is the exact source above. No workflow artifacts were returned; the decoded job log is archived directly, including its UTF-8 BOM. The standalone production-gate check retained exit **2**, `NotAuthorized`, `outputCreated=false`, CLOSED authority and absence of its supplied unapproved-envelope path. The machine evidence includes the actual host response; successful CI shell assertions and the response are in its raw log.

### Retained execution provenance

| Environment | Python / platform | Fixture Git | Sanitized auditor Git |
|---|---|---|---|
| Primary host | 3.12.14; Linux-6.18.57-x86_64-with-glibc2.41 | `/usr/local/bin/git` — git version 2.56.1 | `/bin/git` — git version 2.47.3 |
| Actions | 3.11.18; Ubuntu 24.04.5 | `/usr/bin/git` — git version 2.56.1 | `/bin/git` — git version 2.56.1 |

Host start/end UTC: `2026-11-26T03:50:40.194030+00:00` / `2026-11-26T03:50:52.776933+00:00`. Actions created/updated UTC: `2026-11-26T03:51:16Z` / `2026-11-26T03:51:40Z`. These UTC execution times correspond to the 2026-11-25 client date.

- [Machine evidence](D5B_ACTIVATION_PUBLICATION_AP1_R2_EVIDENCE_2026-11-25.json)
- [Retained Primary host log](D5B_ACTIVATION_PUBLICATION_AP1_R2_SOURCE_HOST_2026-11-25.log)
- [Retained decoded CI job log](D5B_ACTIVATION_PUBLICATION_AP1_R2_CI_JOB_139680200608_2026-11-25.log)
- [Actions run](https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263) and [job](https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263/job/139680200608)
- [Exact four-path source comparison](https://github.com/night-outlook/hybridclr_demo/compare/6d0a5d1613c483119b41d774765ef9752adb7732...2a0053bbe350bc52b189ca4201542b2c93b5eca7)

All five R5 file blobs were freshly read back at the new source. The old-auditor transcript observation used exact auditor blob `e4508a201081dfb87fc77a0b097fd92ce143beb6`; it remains supplemental and has no invented archive.

| Changed source path | Read-back Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `f9782fa9f78f65c9ac6a3fac81f2bde2c0d30bb0` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_DESIGN_2026-11-25.md` | `3c0f077c1b6e08ef91841fd4e22b3f38b1532c0e` |

The Native B1 workflow `45751527251` returned success; four unrelated L/K/terminal workflows (`45751527225`, `45751527339`, `45751527384`, `45751527220`) returned cancelled. These are observed metadata only and are not counted as AP1 evidence or runtime acceptance.

### Transport, ownership and Primary peer check

All four canonical repository identities, feature refs and Connector pull/push permissions were verified. Existing smoke proof from this same conversation was freshly read back on **`codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0`**:

| Repository | Original smoke base | Verified smoke commit |
|---|---|---|
| night-outlook/hybridclr_demo | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` |
| night-outlook/il2cpp_plus | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` |

These disposable refs remain because Connector branch deletion is unavailable. They are transport evidence only. The new source was published through Git tree/commit creation and a non-forced expected-head ref update, then read back remotely.

The internal read-only Primary peer check found no concrete inconsistency in the parser, appended tests, workflow counts or design. It did not rerun tests or assign the pending independent decision. Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, prior independent reports and sibling repositories are outside this cycle's write scope. The machine evidence records preserved Local-owned blobs.

For supporting Git semantics, the fetched [Git commit parser](https://github.com/git/git/blob/v2.51.0/commit.c), blob `d1e1061214b9ab410f0619d3d4f92ccc6cb98b58`, uses the initial tree and contiguous parent prefix. The fetched [no-walk documentation](https://github.com/git/git/blob/v2.51.0/Documentation/rev-list-options.adoc), blob `d9665d82c8dfbe051fc0c22ff816b272e45e73bd`, supports the bounded one-commit observation. The correction deliberately accepts a strict subset rather than promising every storable Git layout.

## 6. Independent return and hard stop

The next gate is [separate independent AP1 R2 rereview][request] of D5B-AP1-IR-01 against these exact source and evidence identities. Primary implementation or a passing suite cannot self-clear `ReturnRequired`.

Fifth-runner identity/custody, executable/import/configuration closure, a reviewed plan-version or adapter, Q approval validation, live remote qualification and physical admission remain deferred Primary work. H/E/A/Q constructibility and the prior R5 pass retain their bounded meaning. R5's no-adoption proof remains limited to unresolved creation. The normal successful mkdir-to-open name replacement gap and later namespace mutation remain outside that guarantee; future controlled parent custody is still required.

```text
D5BActivationPublicationAP1IndependentReview=ReturnRequired
D5BActivationPublicationAP1R2IndependentReview=Pending
D5BDryAdmissionR5IndependentReview=PassDryAdmissionSourceOnly
APPROVED_EXECUTION_ENVELOPE_BLOB=None
APPROVED_LOCAL_HANDOFF_BLOB=None
WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION
D5BLocalExecution=NotAuthorized
D5LocalValidation=NotAuthorized
R03Accepted=false
H2Passed=false
ReadyForHumanReviewGate=false
```

All 18 real D5 Player cases remain `NoCoverage`; candidate Local/macOS, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain `NotRun`. No activation branch, approved executable envelope, Local preview/dry admission, D5-C/D, D6, H2, M08A, X02, SNAP-01 or Human Review Gate is authorized by this report.

[prior-review]: https://github.com/night-outlook/hybridclr_demo/blob/6d0a5d1613c483119b41d774765ef9752adb7732/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_2026-11-25.md
[design]: D5B_ACTIVATION_PUBLICATION_AP1_R2_DESIGN_2026-11-25.md
[request]: D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md
[auditor]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[tests]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py
[workflow]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
