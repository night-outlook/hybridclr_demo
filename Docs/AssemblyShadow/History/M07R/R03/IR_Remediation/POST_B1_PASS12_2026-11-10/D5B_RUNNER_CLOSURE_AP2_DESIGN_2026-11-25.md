# D5-B runner artifact closure — AP2 design

Client date: **2026-11-25, America/Los_Angeles**. Existing UTC evidence labels remain unchanged.

Status: **Primary source-only design; separate AP2 independent review required**. R5 `PassDryAdmissionSourceOnly` and the [AP1 R2 independent `PassActivationPublicationProposalOnly`][ap1-review] remain preserved. This document grants no Local, plan, envelope or Q authority.

## 1. Bounded purpose

Add `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py` as a companion verifier. Preserve the reviewed R5 writer, wrapper, plan, preflight and tests, and the reviewed AP1 R2 auditor and tests. AP2 partially implements the fifth-runner identity and executable-closure requirements in [AP1 design §4][ap1-design]: it authenticates declared repository artifacts and observes a supplied checkout. Runtime import isolation and the complete activation contract remain future work.

The verifier reads Git objects and filesystem bytes without importing or executing candidate runner code. Its two distinct conclusions are: the candidate artifact closure matches a constrained expected record; and the supplied runner checkout matches that closure during bounded observations. Neither conclusion establishes execution permission, a live remote ref or continuing custody.

## 2. External manifest and hash ordering

Retain AP1's frozen source H, closed proposal envelope E(H), and direct-child runner A. Introduce an external manifest C **after A exists**. C binds exact H/A/E identities, the runner artifact roster, canonical repository identity, declared runner ref and locations. It does not bind a literal origin URL; the verifier accepts the fixed canonical URL spellings and records the observed URL. C is not inserted into H, E or A. A later, separately reviewed authority/delivery record Q may bind C's immutable identity together with the required source and runner identities. C and Q never embed their own hashes; those identities are resolved externally after publication.

Thus neither A nor E must predict C, and publication does not recreate the original hash cycle. Today's C is a caller-proposed expected-input record with a closed schema and closed authority fields. It is not an independent trust root, an approved execution envelope or a substitute for Q. The trusted verifier constrains its artifact policy with reviewed pins; a caller cannot replace that policy by supplying a different roster or different expected helper bytes.

## 3. Direct closure and source-inspection inputs

The direct runner-owned closure contains five existing files plus E. Names below are relative to `Tools/AssemblyShadow/R03IR/`.

| Artifact | Required identity or rule |
|---|---|
| `D5Local/run_d5_local.py` | Git blob `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `D5Local/d5b_local_admission.py` | Reviewed base blob `99746fe64976da313cbd0e1625f0fcc5a67bca62`, with only AP1's exact `None`-to-E-blob literal substitution in A |
| `D5Admission/d5b_rr5_source_preflight.py` | Git blob `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `D5Local/d5b_local_admission_plan_v1.json` | Git blob `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `D5Admission/d5b_rr5_source_preflight_v1.json` | Git blob `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `D5Local/d5b_activation_publication_proposal_v1.json` | Exact E blob, strict AP1 proposal kind and closed contents |

This follows the [wrapper][wrapper] → [writer][writer] → [preflight][preflight] dependency chain. The plan and preflight profile are read relative to their runner modules, so both belong to A's closure. The preflight profile is easy to omit when considering only Python imports.

The C10 source pinset, source review, native sources, evidence-producer sources and historical comparator objects inspected through the four-source workspace are a separate source-inspection input set. Reading a `.py` or native source file as evidence does not import or execute it. AP2 does not replace the existing source-admission checks or turn those data reads into native/Player coverage. Identical paths under H and A retain distinct ownership; a source-workspace copy cannot satisfy a runner-owned file check.

## 4. Verification boundary

Load the [AP1 R2 helper][ap1-code] only from bytes verified against blob `ecf36a7a51f1750c6e8425ee79e9ac8938102b54`, never from the candidate import path. Retain its actual-object, strict commit-topology, native-topology agreement, canonical source-ref, sole-parent and exact two-path-delta checks. Add C schema validation and closure comparisons against actual A Git objects and the supplied checkout.

The runner must be its own ordinary `.git` checkout at a canonical absolute root, on the declared runner branch, with exact HEAD/ref A and canonical origin. Require exact committed-tree/index equality and a verifier-owned raw-byte worktree inventory. No Git `status`, `diff`, `hash-object` or worktree-conversion operation is used. Missing, untracked or ignored entries, including extra empty directories, reject; so do skip-worktree/assume-unchanged index flags, submodules and filters. Canonical containment and identity checks keep the runner disjoint from the workspace, its four source children, all six historical roots and evidence parent. Historical roots need not be mutually disjoint.

Use bounded descriptor-based reads for the six regular artifacts, comparing actual bytes and supported modes with both Git objects and C. Reobserve root/file identities, HEAD, ref and cleanliness before returning. Verified immutable bytes may be returned as data; AP2 does not execute them or create an evidence output directory. Unsupported layouts and ambiguous observations reject.

The six artifacts have Git mode `100644`, no filesystem execute bits, one hard link and at most 1 MiB each. Their reads reject symlink leaves/ancestors and compare descriptor/entry fingerprints. The wider tracked inventory supports UTF-8 paths, single-link regular/symlink leaves and owner-execute-bit equality for regular files. Tracked symlinks outside the six artifacts are compared as literal link bytes without following their targets. Each scan is limited to 256 MiB per regular leaf, 4 GiB total leaf bytes, 100,000 entries and depth 64. These are per-scan bounds, not cumulative I/O, memory or elapsed-time guarantees. Raw Git bytes are required; converted/LFS/smudge/line-ending materialization is not qualified.

Checkout checks reject detached HEAD, shared administrative directories, shallow/graft/alternate stores and unsupported config/index states. Canonical origin spelling is not network authentication. Protected source directories are observed for separation only, without qualifying their Git contents or historical evidence.

The API constructs C with `make_closure_proposal` and verifies externally pinned C bytes with `verify_runner_closure`. Its success is `RunnerArtifactClosureObserved_NoExecutionAuthority`; returned `VerifiedBundle` members are immutable byte records and its report is a fresh presentation copy. The CLI requires the trusted interpreter's `-I -S -B` mode and exposes only closure input and expected-blob arguments. Those startup flags isolate this verifier's invocation; they do not implement a candidate runner loader or qualify the interpreter itself.

## 5. Trust and authority limits

The verifier's installation, the externally established verifier/helper pins, Python interpreter/standard library, selected Git executable and host OS are trusted infrastructure. C cannot authenticate the code that first interprets C. The reviewed AP1 helper's constrained Git execution remains part of that boundary.

Artifact equality does not prove which modules a later Python process will load. The existing bare wrapper import and writer `sys.path` insertion require a future reviewed bootstrap/import-isolation design covering ambient paths, preloaded modules, bytecode, extension modules and configuration. AP2 must not claim that work is complete.

A successful result must identify its bounded artifact/checkout observations while explicitly leaving runtime import isolation, live remote refs, target-Mac prerequisites, Q/user authority and execution authority unverified. All Local gates remain CLOSED; Unity/native execution remains `NotRun`, with 18 Player cells `NoCoverage`. The production writer remains `None`-gated in H; A's proposal kind remains deliberately rejected, and the versioned plan remains source-only.

Reobservations are snapshots, not a namespace lock. Replacement, movement or ABA changes between observations and after return remain possible. AP2 establishes neither continuous custody nor the controlled evidence-parent namespace required by R5 review §8.2.

## 6. Source-only validation and next boundary

Use real temporary Git repositories and synthetic roots for focused tests covering:

- Exact closure acceptance; modified helpers already present in H that AP1's H→A delta alone cannot detect; wrong profile ownership, pins, modes and derived writer.
- Closed manifest/schema rejection, missing or extra roles, identity substitutions and attempted authority escalation.
- Wrong HEAD/ref/origin, dirty and ignored content, hidden index flags, unsupported layouts, overlap/aliasing and changes detected during descriptor/ref reobservation.
- Candidate import sentinels remaining inert, closed results on success/failure, and no launch, output creation or remote-validation claim.

An internal Primary peer review identified that the earlier Git-status approach could invoke mutable configuration-selected filters. The correction removes that mechanism entirely and owns the byte comparison in the verifier. Test 17 retains its actual ancestor-replacement/rejection scenario; its diagnostic regex also accepts the new inventory scan's earlier `Tracked directory changed during scan` rejection. This correction is not independent project approval.

The outer unittest harness uses Python `-B`, as do the retained R5/AP1 suites. AP2 tests 19/20 launch the actual verifier CLI with `-I -S -B` and check each missing flag. CLI isolation is not attributed to the outer harness.

Preserve existing suites; publish new exact-source host/CI evidence separately. Stop at independent AP2 review before integration. Future work still includes full four-source admission and live refs, runtime loader isolation, a separately reviewed plan version/adapter, Q authority and revocation semantics, controlled physical custody, fresh stable identities and explicit user approval. No approval is supplied by this design.

[ap1-design]: D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md
[ap1-review]: https://github.com/night-outlook/hybridclr_demo/blob/653930479b37230d757ed8a089e320b0ac53998b/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_R2_INDEPENDENT_REVIEW_2026-11-25.md
[ap1-code]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[wrapper]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py
[writer]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py
[preflight]: ../../../../../../../Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py
