# D5-B AP5 Primary Implementation Report

Date: 2026-11-26 America/Los_Angeles

**D5BFiveIdentityAP5Primary=SourceOnlyCIComplete_PendingIndependentReview.** The four-path implementation increment, combined source-host checks, exact-source CI, and source readback are complete. Independent AP5 review remains Pending. This is a source-only review checkpoint.

## 1. Exact candidate and evidence

| Item | Record |
| --- | --- |
| Accepted baseline | `hybridclr_demo@911d8f96f44430124c487698dde53183d7a75dd2` |
| Source branch | `codex/assembly-shadow-r01b-h1` |
| Exact CI-tested implementation | `0dff80b0fffb37d8c13ff08ad955454a60dde5d6` |
| Source tree | `d43a6ca553ad009b656b7691df89cf34f0508280` |
| Primary publication | The containing documentation/evidence-only child of `0dff80b0fffb37d8c13ff08ad955454a60dde5d6`; identify its exact SHA through the feature ref and record it separately from the tested implementation |
| Combined host and CI | 210/210 methods in each: 94 R5 + 22 AP1 R2 + 25 AP2 + 20 AP3 + 18 AP4 + 31 AP5 |
| Focused CI | [Run 45929766326 / job 140279429052](https://github.com/night-outlook/hybridclr_demo/actions/runs/45929766326/job/140279429052), attempt 1, 1 successful job, 13 successful returned steps |
| Accepted source preservation | All 15 accepted Python/configuration blobs exact; no AP1–AP4 refactor or approval repinning |
| Machine evidence | [D5B_FIVE_IDENTITY_AP5_EVIDENCE_2026-11-26.json](D5B_FIVE_IDENTITY_AP5_EVIDENCE_2026-11-26.json) |
| Raw transcripts | [Host](D5B_FIVE_IDENTITY_AP5_SOURCE_HOST_2026-11-26.log) and [CI](D5B_FIVE_IDENTITY_AP5_CI_45929766326_JOB_140279429052.log) |
| Independent decision | Pending; request `PassFiveIdentityObservationSourceOnly` or `ReturnRequired` |

AP4 is accepted as `PassRunnerConfigurationBindingSourceOnly` for exact source `000e72941f74e52aa18bcd17553e8929acc69167`, including the changed AP3 helper `22ad93598131a59b2d5c46174a45187aede848a6`, with independent publication `911d8f96f44430124c487698dde53183d7a75dd2`. AP3 `PassRunnerImportBootstrapSourceOnly`, AP2 `PassRunnerArtifactClosureSourceOnly`, AP1 R2 `PassActivationPublicationProposalOnly`, `D5B-AP1-IR-01=ClosedInCorrectedSource`, and R5 `PassDryAdmissionSourceOnly` remain preserved in their accepted scopes. Retained earlier AP4-pending labels are historical and do not override the independent AP4 decision.

The source-host directory `/workspace/scratch/a6fad0908883/ap5_source` was assembled from Connector-fetched baseline bytes. It is not a Git checkout. Host tests ran before publication; their four changed file hashes were then matched to exact remote source blobs. This is documentary source association, not attestation of a former physical host state. CI checked out the exact implementation commit above. The later documentation/evidence publication does not receive a separate implementation-test claim.

### Exact source delta

| Path | Git blob | Bytes |
| --- | --- | ---: |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py` | `ab4e9cbf796d4ab91602a14a9294d3773e75879c` | 25854 |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py` | `28945bc7bd29ac5404996f2c40cf81e2600917f4` | 54685 |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `fa80fefd95f7c4b99d180a2e6584e71abe118469` | 8552 |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_FIVE_IDENTITY_AP5_DESIGN_2026-11-26.md` | `bb72ff55828a7881b314cbd870bd46ef229883c4` | 23226 |

The baseline-to-source comparison is one commit and exactly these four paths. Sibling repositories, accepted source files, approval constants, Local-owned records, and prior evidence are preserved.

## 2. Implemented scope

The new observer is `Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py`. Its public API is `observe_five_identities(raw, expected_proposal_blob) -> FiveIdentityObservation`; its CLI accepts only `--proposal` and `--expected-proposal-blob`. The API requires a trusted POSIX Python process invoked with `-I -S -B`.

The externally blob-pinned strict JSON proposal has kind `R03D5BFiveIdentityProposalV1`, fixed source ref `refs/heads/codex/assembly-shadow-r01b-h1`, four exact dynamic `sourcePins`, a distinct demo runner commit/ref, AP2-shaped locations, exact AP1 `CLOSED_AUTHORITY`, and scope `CheckoutAndLiveRefObservationOnly_NoExecutionAuthority`. Runner refs must use the implementation's restricted `refs/heads/codex/` spelling, be at most 240 characters, and differ from the source ref. Repository roles and remote URLs are derived, not supplied by the caller.

The observer checks canonical separated checkout roots, ordinary Git administrative directories with all 15 observed `.git`/`objects`/`refs` root identities pairwise distinct, exact HEAD/attached-branch/local-ref identities, supported local Git configuration, logical index/tree equality, and complete worktree contents using the accepted AP2 raw-byte scanner. It also checks that the runner commit has the proposed demo source as its sole parent. The production report field for this narrow topology fact is `runnerSoleParentObserved`; it does not establish AP1's two-path publication relation.

The order is fixed: locations before, five local observations before, five exact remote observations before, five exact remote observations after, five local observations after, and locations after. Corresponding observations must be equal. Fresh local Git readers perform the second pass.

Runtime result names are `FiveIdentitiesObserved_NoExecutionAuthority` and `FiveIdentitiesRejected_NoExecutionAuthority`. They are implementation result categories, not review verdicts. The immutable stored report returns decoded copies and retains actual attempted/completed phases on rejection. `runnerSoleParentObserved` is a progress fact from two completed local passes and can remain true if a later requirement rejects the overall observation.

## 3. Reuse, preservation, and authority

AP5 authenticates AP2 before helper execution; AP2 separately authenticates AP1. The pinned helpers are:

| Helper | Git blob |
| --- | --- |
| `d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |

The preservation target is all 15 accepted Python/configuration files identified in the baseline ledger. AP5 adds its own role-aware checks and reuses pinned leaf helpers; it does not need an AP1–AP4 refactor or candidate-module import. The host ledger, remote readback and exact four-path comparison confirm all 15 preserved blobs.

Dynamic proposal pins identify the tuple to observe. Their external blob pin is byte identity, not AP1 approval. `sourcePinsMatchAcceptedAP1SiblingPins` reports only whether the three non-demo pins equal AP1's existing sibling constants. Even when that metadata is true, `acceptedAP1SourceTupleVerified`, `runnerPublicationRelationVerified`, `AP2ArtifactCompatibilityVerified`, `AP4ConfigurationCompatibilityVerified`, `AP4CompositionVerified`, `sourceSemanticPreflightVerified`, and `sourceDataInputsVerified` remain false.

Admission, captured-configuration consumers, semantic source preflight, candidate entry points, Unity, and Player execution are outside this observer. Execution and Q authorization remain false; the approved envelope remains null; Local execution/validation remain `NotAuthorized`; `WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`; R03/H2/human-review-gate flags remain false. Real build status remains `NotRun`, Player passes remain zero, and 18 cells retain no coverage.

## 4. Remote transport and fixture evidence

Production uses fixed canonical GitHub HTTPS URLs with `git ls-remote --exit-code --refs`, an explicit null Git directory, `cwd=/`, a constructed environment, disabled inherited/system/global configuration and prompts, cleared credential helpers, proxy configuration and extra headers, HTTPS-only protocol selection, enabled TLS verification, and disabled redirects. It creates no observer scratch directory. Each query has a 30-second timeout and validates stdout and stderr at no more than 65,536 bytes each after capture. The parser requires one row naming the exact requested ref and expected SHA; it rejects failure and ambiguity without fallback.

The required fixture strategy uses actual temporary working checkouts and actual temporary bare refs. Only the private test transport reroutes the remote invocation to those fixture repositories; the public API accepts no callback, alternate endpoint, or offline-success mode. A separate focused test verifies the unmodified production arguments/environment and isolation from benign local URL rewrites and inherited configuration sentinels. The 31 AP5 methods pass in the combined host and exact-source CI evidence below.

Local fixture transport does not establish actual production HTTPS reachability, TLS success against GitHub, or current production ref values. Those claims remain unqualified. On rejection, the conservative fields `remoteProcessLaunchMayHaveBeenAttempted` and `networkMayHaveBeenUsed` preserve the possibility of network activity after an attempted remote phase.

## 5. Limits and review request

The repeated observations are sequential, not atomic. They do not freeze refs, establish simultaneous five-repository state, detect every change-and-return, or protect future reads. Exclusive/continuous custody, runtime import isolation, executable closure, standard-library identity, raw Git index-byte verification, complete administrative custody, and current physical Mac inputs remain unverified.

Retained AP2 limits are 1 MiB proposal/helper reads, 256 MiB per tracked file, 4 GiB per checkout scan, 100,000 entries, and depth 64. Ten full scans can hash up to 40 GiB. Local Git captures/caches complete metadata and objects; remote size checks occur after capture. Neither this validation nor subprocess timeouts establish hard process-memory, network-byte, or filesystem wall-clock bounds.

Review must use the exact completed candidate and evidence, including preservation and CI records. The requested independent verdict is exactly **`PassFiveIdentityObservationSourceOnly`** or **`ReturnRequired`**. Any pass must remain confined to this physical-checkout/exact-ref mechanism and cannot authorize admission, Local execution, evidence promotion, R03/H2 acceptance, or the human-review gate.

## 6. Completed validation and provenance

| Suite | Actual test methods | Host footer | CI footer | Host / CI |
| --- | ---: | ---: | ---: | --- |
| R5 | 94 | 0.114s | 0.190s | OK / OK |
| AP1R2 | 22 | 6.855s | 4.238s | OK / OK |
| AP2 | 25 | 10.662s | 6.871s | OK / OK |
| AP3 | 20 | 6.533s | 4.391s | OK / OK |
| AP4 | 18 | 6.476s | 4.325s | OK / OK |
| AP5 | 31 | 13.848s | 10.146s | OK / OK |

The exact commands and AP5 method identities are recorded in the machine evidence and raw transcripts. AP3, AP4 and AP5 use actual `-I -S -B`. The host checked two new Python ASTs, workflow YAML, seven Bash run blocks, trailing whitespace, the AP2 helper pin, all 15 preserved blobs, and unchanged source bytes after tests. Both approval constants were parsed as null from the actual source.

Both environments retain the old-wrapper denial: exit 2, `NotAuthorized`, `outputCreated=false`, closed WEB-to-Local state, and no unapproved-envelope file. CI reports 6 actual OK footers; AP5's executed method identities match the host source inventory. The workflow's successful exit-code and absent-file shell assertions establish the CI denial details. There were 0 uploaded artifacts in the Connector's returned first page; the committed transcripts supply the retained raw evidence.

Host Python is 3.12.14; CI Python is 3.11.18. Retained-suite fixture Git is recorded separately from system-path Git. AP5 selects system-path Git for both its fixtures and observer, with their actual paths and versions recorded explicitly. The CI archive is the exact UTF-8 encoding of Connector-decoded log text, including its BOM if present; no original archive-byte attestation is claimed. Other workflows triggered by the source publication are not AP5 qualification evidence.

Internal static review covered AP5 and its direct AP2/AP1 helper paths. It identified one narrow contract gap: only five `.git` identities had been compared for uniqueness. The correction compares all 15 recorded `.git`, `objects`, and `refs` roots and explicitly excludes recursive storage custody; a follow-up read verified that correction. `plannedReadOrder` also clarifies intended versus completed phases on rejection. Internal review and tests do not substitute for the separate AP5 decision.

The all-15 negative fixture injects duplicate observed identity tuples after real checkout scans; it is not an actual mounted-alias integration test. CLI argument errors retain argparse stderr, while ordinary observation exceptions produce structured rejection. No unconditional JSON-delivery guarantee covers termination, `BaseException`, resource exhaustion, serialization failure or unavailable output.

## 7. Four-repository tuple and transport proof

| Repository | Branch | Exact source commit for review | Historical candidate path — physical state Unverified |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `0dff80b0fffb37d8c13ff08ad955454a60dde5d6` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

All four canonical identities, feature refs and Connector pull/push permissions were read at bootstrap. The demo source row identifies the implementation. The containing publication is its documentation/evidence-only child; final ref readback must record that latest demo publication separately. No physical Mac path was inspected, and no package, overlay, native binary or build pin was regenerated or qualified.

Same-conversation Connector write smoke proof was reused and freshly read back as four exact branch refs plus four commit objects. The branch is `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0`. This is operational transport proof only.

| Repository | Original smoke base / sole parent | Read-back smoke commit |
| --- | --- | --- |
| `hybridclr_demo` | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` |
| `hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` |
| `hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` |
| `il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` |

The disposable branches remain because the Connector offers no delete-ref capability in this session. This AP5 cycle made no new smoke mutation and created no production runner or approval ref.

## 8. Next owner and closed gates

Production `APPROVED_EXECUTION_ENVELOPE_BLOB=None` and `APPROVED_LOCAL_HANDOFF_BLOB=None` remain unchanged. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`; `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false. Q, explicit user Local approval, native/Player permission and production activation remain unauthorized. Current real Unity/native/Player work remains `NotRun`; all 18 real Player cells remain `NoCoverage`, with zero passed. Historical Mac paths are physically `Unverified`. The candidate proposal literal is not an approval and is not assumed null.

Next read order: `Docs/AssemblyShadow/README.md`, `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, AP5 design, this report, the independent review request and machine evidence, exact implementation/test/workflow files, and both raw logs. The independent reviewer should identify concrete code/evidence/scope defects if any and return the requested source-only verdict. Preserve Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`; their latest historical Native B1 oneuse-12 result is not AP5 qualification.

Stop after Primary publication and four-ref readback. Local commands, candidate integration, approval repinning, Q execution, Unity/native/Player work, evidence promotion and later milestones remain closed. Bounded Local fixes are not in scope for this review checkpoint; source corrections return to Primary implementation.
