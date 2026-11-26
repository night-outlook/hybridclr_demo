# D5-B AP1 — proposed activation publication without a hash cycle

**Client date:** 2026-11-25 America/Los_Angeles. Older records retain their original UTC/timezone labels.
**Status:** Primary source-only protocol proposal. No activation branch, approved envelope, user approval or executable Local handoff is created here.

## 1. Baseline and scope

The [published R5 independent review][r5-review] remains `PassDryAdmissionSourceOnly` for implementation `eaca19c08f41245c46dfacbf605cd80480bc3a92`, published in demo revision `e63732d755c0ed283138e72d3e612609ea73a565`. AP1 does not reopen its closed findings or extend that verdict to activation. The [current README][readme] retains CLOSED Local authority.

The recorded four-head baseline for this proposal is:

| Repository | Commit |
|---|---|
| `hybridclr_demo` | `e63732d755c0ed283138e72d3e612609ea73a565` |
| `hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

AP1 preserves the R5 writer, versioned plan, 94-test suite, imported preflight and public wrapper byte-for-byte. Their reviewed Git blobs are respectively `99746fe64976da313cbd0e1625f0fcc5a67bca62`, `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9`, `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c`, `81e7c3a2eaccb77bff2515c91b173558e4eeba2f`, and `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39`. These identities are recorded in R5 review §2.2; they are not new Local observations.

## 2. Selected protocol: separate immutable runner identity (Design B)

Putting an envelope's blob pin into the same source revision named by that envelope makes publication circular: changing the pin changes the source commit, which changes envelope bytes and therefore its blob. Design B separates those identities while retaining exact four-source live-ref checks and the literal immutable-envelope pin. It introduces no signing-key infrastructure.

| Identity | Proposed publication relationship |
|---|---|
| **H** | Final demo source revision, with the other three exact source commits. Freeze the four source feature refs after implementation stabilizes. The baseline above is not automatically the eventual authorized tuple. |
| **E(H)** | Immutable envelope bytes naming that frozen four-source tuple. E contains neither the future runner identity nor the approval-publication identity. Draft bytes alone confer no authority. |
| **A** | Separate runner revision whose source contains the literal Git blob of E. Freeze its distinct runner ref after publication. The runner is a fifth executable identity, separate from the four source checkouts. |
| **Q** | Later independent review, explicit user decision and canonical handoff publication on a separately designated documentation/approval ref. Q binds the exact four-source tuple, runner A, E blob and reviewed executable/import closure. |

All subsequent review and handoff publication belongs on Q's designated ref; neither source H nor runner A advances for that publication. Canonical `WEB_TO_LOCAL` at Q can therefore name all five exact executable/source identities without changing any of them. Q's own commit hash is resolved and communicated externally after publication, never embedded into its own hashed contents. E does not acquire A or Q fields later.

The source, runner and approval refs must be distinct. Their exact names, creation, custody and authority remain subject to project review and explicit approval. None is created by AP1. A future authorized envelope requires a stable final source tuple, independent activation review and explicit user approval; the present proposal supplies none of those activation permissions.

## 3. What the AP1 auditor establishes

The proposed module `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` checks **local Git proposal topology only**. Its envelope kind is deliberately non-executable: `R03D5BActivationPublicationProposalV1`. Its success label is `ProposalPublicationStructureVerified_NoExecutionAuthority`, with all authority flags closed.

The bounded model checks actual local source/runner Git objects, binds the source ref to `refs/heads/codex/assembly-shadow-r01b-h1`, and requires a distinct supplied runner ref; A has H as its sole parent. The H-to-A tree delta is exactly two paths: the reviewed R5 writer with only its `None` approval literal replaced by the proposal-envelope blob, and the added proposal envelope. Other tree changes are rejected. The existing R5 executable envelope parser rejects this proposal kind, even in the synthetic pinned tree.

`test_d5b_activation_publication.py` uses real temporary Git objects to check constructibility and invalid topology. These are synthetic source-host fixtures, not created production activation branches or approved execution envelopes. AP1 hard-pins the reviewed R5 writer; its result does not validate a future runner implementation, imported-module custody, Q authority, live remote heads, physical paths, host prerequisites or execution permission. Test execution and exact-source CI evidence belong in a separate Primary record.

## 4. Concrete Primary work remaining after protocol review

The protocol proposal must receive separate review before further activation implementation. Primary would then need to:

1. **Implement the fifth-identity contract.** Validate runner A against its immutable pin and exact live runner ref; require a clean canonical checkout disjoint from all four source repositories, historical roots and output locations. Retain exact clean-head/live-ref checks for every source repository. AP1's local Git-object checks do not implement these requirements.
2. **Bind the executable closure.** Authenticate the runner entry point, every imported module, plan, wrapper and configuration against independently reviewed blobs. Prevent ambient import paths or another checkout from supplying unpinned code. Specify what the final handoff records and how runtime identity is rechecked.
3. **Resolve plan authorization explicitly.** R5's versioned plan encodes closed authorization and source-only semantics. A literal envelope pin cannot silently turn that plan into an executable authority. Implement a separately reviewed new plan version or explicit adapter with defined authority semantics, tests and immutable closure. Any resulting runner/source changes require a successor reviewed activation contract; AP1's two-path topology prototype is not approval of those changes.
4. **Implement Q validation and custody.** Define the separate approval ref, committed independent review and user-decision evidence, exact five-identity handoff, external Q pin, revocation/drift handling and reconciliation requirements. The auditor does not currently validate Q or the truth of a user-approval assertion.
5. **Complete fresh qualification before authorization.** Obtain exact-source tests/CI and independent activation review of the implemented runner, plan/adapter, closure and publication process. Stabilize the final source tuple before preparing the new envelope and final approval record. Present those exact bytes and identities for explicit user approval before any Local action.

No part of this list is delegated to Local as missing architecture or implementation. A source-only pass or a constructible Git history cannot substitute for its completion.

### Namespace prerequisite retained from R5 §8.2

R5's proved no-adoption behavior covers **unresolved creation**. After recorded mkdir, a concurrent replacement before the initial pathname-based root open can be the directory acquired; the checks have no independently retained child inode from mkdir. Moves after the last identity observation also remain possible. Future activation must establish a controlled evidence-parent namespace and independent physical custody. AP1 supplies neither, and must not be described as providing atomic namespace protection or resolving arbitrary crash/response ambiguity. [R5 review §8.2][r5-review]

## 5. Bounded historical input inventory

The following literals were recovered through the GitHub Connector at demo `e63732d755c0ed283138e72d3e612609ea73a565`, starting with its README and the bounded oneuse-12 publication. **Every present-day physical fact is Unverified**: existence, canonical identity, contents, cleanliness, capacity and Unity hash. No current output location is inferred.

| Input | Historical candidate | Provenance |
|---|---|---|
| Four-repository workspace | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` | CMD's explicit workspace argument; ADM records children `hybridclr_demo`, `hybridclr`, `hybridclr_unity`, `il2cpp_plus`. |
| Original S | `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse` | ADM's retained-worktree authority, commit `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; CMD corroborates. |
| `b1EvidenceBase` candidate | `/Users/ah/GitHub/hybridclr/r03-local-validation` | ADM's historical `capacity.outputParent` and CMD's `cwd`. Mapping to this D5-B role is an **inference**, not a historical field with that name. |
| `b1Oneuse12` | `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-NativeB1-20261110-oneuse-12` | RES's `productRoot`; B1 and CMD corroborate. |
| `b1NativeHostRaw` | `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-NativeB1-20261110-oneuse-12-native-host-raw` | RES's `nativeHostRawRoot`; B1 corroborates. |
| `b1B2HostRaw` | `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-NativeB1-20261110-oneuse-12-b2-host-raw` | RES's `b2HostRawRoot`; B1 corroborates. |
| `b1Preflight` | `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-NativeB1-12` | RES's `localPreflightRoot`; MAP maps the published receipts. |
| Unity executable | `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` | ADM's `machine.unityExecutable`; CMD corroborates. |
| Historical Unity SHA-256 | `35721b35221875b2d170160f7fdd661afff7458b3386f029124f30e1ba2b862c` | ADM's `machine.unityExecutableSha256`; recorded only, not recomputed. |

These are comparator/proposal inputs, not reusable execution authority. The future output parent must be separately selected and reviewed, canonical and disjoint from the source workspace, runner checkout and **every historical base/root**. In particular, the historical `r03-local-validation` base cannot be reused as the prospective output parent. No new parent or one-use name is selected here.

### Published provenance

Historical paths below are relative to `Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/` at the pinned demo revision. IDs are connector-returned **Git blobs**, not executable SHA-256 values.

| Key | Published file | Git blob |
|---|---|---|
| B1 | [README.md][b1-readme] | `0f8db81bb16490094d039ce4aed53469ac26ed56` |
| RES | [LOCAL_RESULT.json][local-result] | `83d155301a83b98306048bb62b83eab17b6771fd` |
| MAP | [PUBLISHED_RAW_MAP.json][raw-map] | `083e9348e1dd3e947b2ea4e62a42a117c7f8b7cb` |
| ADM | [local-evidence/ADMISSION.json][admission] | `e7954bf837429cacc71bf82565071c0693580e22` |
| CMD | [local-evidence/runner-COMMAND.json][command] | `a6f599e2e71bcb56a0dabc5570c4f99c745183a2` |

The starting `Docs/AssemblyShadow/README.md` blob is `c4a83d30cebf96828c63983e5612bd523ce1879e`. The published R5 independent report blob is `ba52c572f3761a687ee99dcec0bf187a99398157`. Reading those Git records establishes their published contents, not present Mac filesystem state.

## 6. Authority and stop

```text
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

All 18 real D5 Player cases remain **NoCoverage**. Candidate macOS Local admission, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain **NotRun**. AP1 authorizes no Local preview/dry admission, D5-C/D, D6, H2, M08A, X02, SNAP-01 or Human Review Gate. Stop at the Primary source-only protocol/auditor publication and separate protocol review; no executable handoff follows from this document.

[readme]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/README.md
[r5-review]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md
[b1-readme]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/README.md
[local-result]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/LOCAL_RESULT.json
[raw-map]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/PUBLISHED_RAW_MAP.json
[admission]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/local-evidence/ADMISSION.json
[command]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/local-evidence/runner-COMMAND.json
