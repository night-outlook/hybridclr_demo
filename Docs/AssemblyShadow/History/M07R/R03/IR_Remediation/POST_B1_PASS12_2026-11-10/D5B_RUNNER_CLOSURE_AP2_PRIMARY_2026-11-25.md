# D5-B runner artifact closure — AP2 Primary report

Client date: **2026-11-25, America/Los_Angeles**. Earlier UTC labels retain their original meaning.

**AP2 independent review: Pending. All Local and approval gates remain CLOSED.** This report records source-only verification of `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`; it is not an independent verdict or a Local handoff.

## 1. Purpose and retained review state

AP1 established constructibility of H → E(H) → A without authorizing the proposed runner. Its two-path H→A delta did not authenticate unchanged helper/configuration bytes already present in H, or observe a runner checkout. AP2 adds a separate [artifact-closure verifier][module], [focused source-host suite][tests] and [design][design] for those bounded observations.

The [AP1 R2 independent review][ap1-review], published at `653930479b37230d757ed8a089e320b0ac53998b`, remains `PassActivationPublicationProposalOnly` and closes `D5B-AP1-IR-01`. R5 retains `PassDryAdmissionSourceOnly`. Neither result is promoted to activation approval by AP2.

The nine preserved baseline files are the original five R5 files—writer, writer tests, plan, wrapper and source preflight—plus the preflight profile, custody-authority module, AP1 R2 auditor and AP1 tests. Their bytes remain exact; the existing 94 R5 and 22 AP1 test methods remain intact.

| Repository | Source identity for this review |
|---|---|
| `hybridclr_demo` | `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a` |
| `hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

These are review-source identities, not an approved production H/A tuple. The sibling identities are unchanged.

## 2. Closure and publication ordering

The direct runner closure consists of **five existing runner-owned files plus E**:

| Artifact | Constraint |
|---|---|
| `run_d5_local.py` | Exact reviewed wrapper blob |
| `d5b_local_admission.py` | Reviewed R5 bytes with only AP1's exact `None`-to-E-blob substitution |
| `d5b_rr5_source_preflight.py` | Exact reviewed imported-module blob |
| `d5b_local_admission_plan_v1.json` | Exact closed plan blob |
| `d5b_rr5_source_preflight_v1.json` | Exact runner-relative profile blob |
| `d5b_activation_publication_proposal_v1.json` | Exact E blob and closed AP1 proposal schema |

The profile belongs to the runner because the imported preflight resolves it beside its own module. The C10 pinset, source review, native/evidence-producer source rosters and historical comparator objects inspected under H remain a separate source-data input set. AP2 does not qualify those contents, their four checkouts or their live remote refs.

C, kind `R03D5BRunnerClosureProposalV1`, is external and follows A. It binds H/A/E, the six-file roster, canonical repository identity/ref and declared locations, not a literal origin URL. C is not written into A, and neither E nor A needs to predict C. A future Q may bind C's externally resolved immutable identity; C and Q do not self-embed their hashes. No production A, E, C or Q was created by this unit.

## 3. Verification and trust boundary

The verifier authenticates AP1 helper bytes against Git blob `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` before compiling/loading that reviewed helper. Candidate wrapper, writer and preflight remain inert bytes. AP1's actual-object checks, R2 strict commit-prefix/native-topology agreement, canonical source ref, sole-parent rule and exact two-path delta remain unchanged.

AP2 requires exact C bytes under an external blob pin and exact schema/policy equality. It checks a canonical ordinary checkout with its own `.git`, declared branch/HEAD/ref A and one accepted canonical repository origin spelling, recording the observed URL. That observation is local configuration, not network authentication. Unsupported administrative layouts, shallow/graft/alternate stores, filters, hidden index states and submodules reject.

The verifier checks exact full committed-tree/index equality and owns the raw-byte worktree inventory. It uses no Git `status`, `diff`, `hash-object` or worktree-conversion calls. Missing, ignored or untracked entries, including extra empty directories, reject. General tracked paths must be supported UTF-8; regular/symlink leaves must have one link. Regular-file owner-execute bits must agree with Git mode. Symlink text outside the strict six artifacts is compared literally without following targets. Raw committed bytes are required; converted/LFS/smudge/line-ending materialization is not qualified.

Canonical path and directory-identity observations separate the runner from the workspace, four source children, six historical roots and evidence parent; the evidence parent must also remain separate from source/history locations. Protected directories are observed for separation, not admitted as evidence.

The six artifacts retain stricter descriptor reads: regular, non-executable, single-link, Git mode `100644`, at most 1 MiB, and no symlink traversal. Wider scans permit at most 256 MiB per regular leaf, 4 GiB total leaf bytes, 100,000 entries and depth 64 per scan. These limits do not bound cumulative I/O, memory or elapsed time. Rechecks cover bytes/fingerprints, roots, refs, HEAD, index, configuration and the inventory. They provide no namespace lock or continuous custody; intervening/after-return replacement and ABA remain limitations.

The verifier installation, its externally established identity, Python/standard library, selected Git executable and OS remain trusted infrastructure. C's pin establishes byte identity, not approval or trust in the process interpreting it. Artifact equality does not isolate a future candidate's imports.

## 4. API, CLI and result

The complete proposal/verification interface is:

- `make_closure_proposal(repo, source_commit, runner_commit, runner_ref, locations) -> dict`: constructs C from local Git objects and location spellings; it writes nothing and makes no custody claim.
- `canonical_bytes(value) -> bytes` and `git_blob(raw) -> str`: serialize the proposal and calculate its external Git-blob identity.
- `verify_runner_closure(raw, expected_blob) -> VerifiedBundle`: verifies C and returns immutable `BundleFile(path, git_blob, raw)` records. Accessing `report` returns a fresh presentation dictionary.
- `main(argv=None) -> int`: exposes only `--closure` and `--expected-closure-blob`; its trusted interpreter must use **`-I -S -B`**. The programmatic API assumes a trusted process.

The report kind is `R03D5BRunnerClosureObservationV1`. Success is `RunnerArtifactClosureObserved_NoExecutionAuthority`; rejection is `RunnerArtifactClosureRejected_NoExecutionAuthority`. Only artifact-closure and checkout-observation verification become true. Runtime import isolation, complete executable closure, exclusive custody, source-data admission, live remote refs, current Mac inputs and execution authority remain false.

## 5. Exact-source host and CI evidence

Internal Primary peer review identified that Git status could invoke mutable configuration-selected filters. The corrected verifier removes that mechanism entirely. Test 17 preserves its actual ancestor-replacement scenario and required rejection; its diagnostic regex additionally accepts the inventory scan's earlier `Tracked directory changed during scan` error. This is an internal correction, not independent approval.

Primary observed a focused post-correction run of 25 methods passing in 20.623 seconds. That checkpoint is separate from the final combined host/CI evidence bound below; final evidence identities take precedence. The outer unittest harness uses Python `-B` for R5, AP1 and AP2. AP2 tests 19/20 directly launch the verifier CLI with `-I -S -B` and test each missing flag; the outer harness does not claim isolated mode.

[CI run 45774292828, job 139754092541][ci] verifies the same source `8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`. Counts below are test methods, not inferred subcase counts. The test source and accompanying provenance provide the case inventory.

| Suite | Methods | Host result / seconds | CI result / seconds |
|---|---:|---|---|
| R5 | 94 | PASS / `0.189` | PASS / `0.188` |
| AP1 R2 | 22 | PASS / `11.934` | PASS / `4.220` |
| AP2 | `25` | PASS / `19.305` | PASS / `6.797` |

| Environment | Python | Fixture Git | Auditor Git |
|---|---|---|---|
| Source host | `3.12.14` | `/usr/local/bin/git — git version 2.56.1` | `/bin/git — git version 2.47.3` |
| CI | `3.11.18` | `/usr/bin/git — git version 2.56.1` | `/bin/git — git version 2.56.1` |

Fixture and auditor Git identities are recorded separately because fixture creation and sanitized auditor execution can select different executables. Retained host log: `23828` bytes, SHA-256 `11651964c906570888ca035e1d5aa6e5db7f63fcb7be5801d2060f75f2f6c3d2`. Retained CI log: `47973` bytes, SHA-256 `f86025615a33de28d13ab585230dd5b6a238039d66afff0db6187253ecfdf105`.

## 6. Decision boundary

AP2 requests a new source-only independent review. Full source admission/live refs, runtime loader isolation, a separately reviewed plan version or adapter, Q authority/revocation, controlled physical custody and explicit user approval remain future work. The production R5 approval constant remains `None`, its plan remains closed, and the proposal envelope remains rejected for execution. `WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`; Unity/native execution remains `NotRun`, with 18 Player cells `NoCoverage` and zero passed. R03/H2/ReadyForHumanReview gates remain false.

[module]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py
[tests]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py
[design]: D5B_RUNNER_CLOSURE_AP2_DESIGN_2026-11-25.md
[ap1-review]: https://github.com/night-outlook/hybridclr_demo/blob/653930479b37230d757ed8a089e320b0ac53998b/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_2026-11-25.md
[ci]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45774292828/job/139754092541

## 7. Published source, retained evidence and scope

The source commit is **`8a856ab6b50fd29ece0b17c86cd3fd359fc9ba3a`**, tree `f523f6d509b3409de09bc8bf5f67d872fad9de3e`, sole parent `653930479b37230d757ed8a089e320b0ac53998b`. Connector readback matched all four intended file contents and Git blobs; the compare shows exactly one source commit and these four paths:

| Source path | Git blob | Bytes |
|---|---|---:|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` | 30031 |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py` | `ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976` | 42800 |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `2aff9a399708f90f58fe312f8c03a90b101ae16a` | 5013 |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_DESIGN_2026-11-25.md` | `742f385b15335c8ecf842283d6470bfb49b5f8fd` | 11291 |

The subsequent publication containing this report changes only documentation/evidence. Its latest pushed HEAD is resolved from the feature ref and recorded in the final review handoff; it is not relabeled as this CI-tested source. The source commit's AP2 implementation, tests, workflow and design remain unchanged in that successor. Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` are preserved. No production activation/ref or approved envelope is published.

Focused Actions attempt **1** used `.github/workflows/r03-b2-d5b-local-admission-source-host.yml`, event **push**, on the exact source and checkout. It completed with **1/1 job and 10/10 returned steps successful**; step numbers are not treated as the number of returned steps. UTC run start: **2026-11-26T07:18:06Z**; last completed metadata update: **2026-11-26T07:18:31Z**. The actual raw-log footers and full AP2 method names match the host inventory. The public wrapper gate's successful CI step asserts exit **2**, `NotAuthorized`, `outputCreated=false`, and absence of the unapproved-envelope path. These are source-host observations only.

The [machine evidence](D5B_RUNNER_CLOSURE_AP2_EVIDENCE_2026-11-25.json) includes exact source hashes, full method inventory, retained baseline identities, environment versions, observed job/step statuses and internal correction history. The [raw CI log](D5B_RUNNER_CLOSURE_AP2_CI_45774292828_JOB_139754092541.log) retains its UTF-8 BOM and exact decoded bytes without normalization (Git blob `1fd5fc887ee35653b070d1e1d2952a42a364c968`). The [raw Primary host log](D5B_RUNNER_CLOSURE_AP2_SOURCE_HOST_2026-11-25.log) is Git blob `6d10cc5d23679700c4086a27fe199b07125caa2c`. GitHub returned **0 uploaded Actions artifacts**; these committed raw logs are the retained evidence. Other automatically triggered workflows are recorded only as metadata observations and supply no AP2 or Local qualification.

Host static checks parsed both new Python files and the YAML workflow, checked all **4** Bash run blocks, found no trailing whitespace in the four changed paths, and verified source bytes unchanged across the tests. A separate literal-count check requires **25 unique AP2 methods** and actual retained footer counts **94/22/25**; the host harness now enforces the same fixed AP2 count. The outer tests use `-B`; production CLI isolation is exercised by AP2 tests 19/20.

### Preserved reviewed baseline

| Preserved path | Exact baseline and current Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |

### Connector bootstrap and retained smoke proof

All four canonical repository identities, feature refs, and Connector pull/push permissions were verified before implementation. The source update used create-tree → create-commit → expected-head, non-forced ref update. The source remote HEAD and all changed files were read back. The same procedure is used for the documentation/evidence successor.

The disposable branch `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0` remains in each repository. Its existing same-conversation proof was read back again for this cycle. No delete-ref capability is available through the Connector. These commits demonstrate transport only; none is product acceptance or a current feature HEAD.

| Repository | Smoke base | Verified retained smoke commit |
|---|---|---|
| `night-outlook/hybridclr_demo` | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` |

### Historical physical paths and recovery

The historical Mac root is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, with one child per canonical repository. Their current physical state is **Unverified**; this cycle used a source snapshot at `/workspace/scratch/a6fad0908883/ap2_source` and the authoritative GitHub Connector. Package, overlay, native and build pins remain those recorded by the preserved source/review inputs; no Unity/package/native/build state was regenerated or requalified.

AP2 remains an unintegrated companion. Returning its source paths/workflow to the recorded baseline through a separately reviewed forward revert would remove this increment without activating the preserved writer. Do not reset or clean Local repositories, modify Local-owned evidence, repin approvals or use this record as permission to run a candidate. Next action: independent AP2 source review; stop before Local integration or execution.
