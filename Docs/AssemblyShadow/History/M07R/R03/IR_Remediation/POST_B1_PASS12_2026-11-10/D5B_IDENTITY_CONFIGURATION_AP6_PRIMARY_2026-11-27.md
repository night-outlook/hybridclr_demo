# D5-B AP6 Primary Implementation Report

Date: 2026-11-27 America/Los_Angeles

**D5BIdentityConfigurationAP6Primary=SourceOnlyCIComplete_PendingIndependentReview.** The five-path source increment, source-host checks, exact-source CI including required integration, and implementation source readback are complete. Independent AP6 review remains **Pending**. The containing documentation publication and final remote readback are subsequent operations; this self-record does not claim those operations are already complete.

## 1. Exact candidate and evidence

| Item | Record |
| --- | --- |
| Accepted baseline | `hybridclr_demo@943040c310808065751a26caf00c80e43d87f388` |
| Source branch | `codex/assembly-shadow-r01b-h1` |
| Exact CI-tested source T | `c4abb8ec7ab32ba0579c8a3686fa33b4487a37cb` |
| Source tree | `a45681435483e4561917547f18f957e557002a9c` |
| Documentation publication M | The containing documentation/evidence-only child of T; resolve its exact remote SHA separately |
| Source delta | One commit; exactly five paths: three new Python files, workflow, design |
| Preserved accepted source | All 17 accepted Python/configuration blobs exact |
| Host | 230 actual methods in 7 suites; required integration not run |
| CI | 231 actual methods in 8 suites; required integration passed |
| Focused workflow | [Run 45984884119, job 140457825344](https://github.com/night-outlook/hybridclr_demo/actions/runs/45984884119/job/140457825344); attempt 1; 1 successful job; 21 successful returned steps |
| Machine evidence | [D5B_IDENTITY_CONFIGURATION_AP6_EVIDENCE_2026-11-27.json](D5B_IDENTITY_CONFIGURATION_AP6_EVIDENCE_2026-11-27.json) |
| Raw transcripts | [Host](D5B_IDENTITY_CONFIGURATION_AP6_SOURCE_HOST_2026-11-27.log); [CI](D5B_IDENTITY_CONFIGURATION_AP6_CI_45984884119_JOB_140457825344.log) |
| Requested independent verdict | `PassIdentityConfigurationCompositionSourceOnly` or `ReturnRequired` |

AP5 is accepted as `PassFiveIdentityObservationSourceOnly` for exact source `0dff80b0fffb37d8c13ff08ad955454a60dde5d6`, with independent publication `943040c310808065751a26caf00c80e43d87f388`. AP4 `PassRunnerConfigurationBindingSourceOnly`, AP3 `PassRunnerImportBootstrapSourceOnly`, AP2 `PassRunnerArtifactClosureSourceOnly`, AP1 R2 `PassActivationPublicationProposalOnly`, `D5B-AP1-IR-01=ClosedInCorrectedSource`, and R5 `PassDryAdmissionSourceOnly` remain preserved in their accepted scopes. Earlier pending labels in retained history do not supersede these decisions.

The source-host directory `/workspace/scratch/a6fad0908883/ap6_source` was assembled from Connector-fetched baseline bytes and the five-path increment. It is not a Git checkout. Its prepublication file hashes were matched to the exact remote source blobs. That is documentary association of tested bytes with T, not attestation of a historical physical host. CI checked out T and records that identity in its actual job log. The later documentation-only M receives no additional implementation-test execution claim; its own commit identity is deliberately unembedded.

### Exact source delta

| Path | Git blob | Bytes |
| --- | --- | ---: |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_identity_configuration.py` | `94f1e30a51c1165b54b0392801853bcb7b9e3557` | 18633 |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_identity_configuration.py` | `fdb81d073c9da09e7313568e32833102e09b7a8a` | 32373 |
| `Tools/AssemblyShadow/R03IR/D5Local/integration_d5b_identity_configuration.py` | `0119bb0bd4d471f456fd400a3f46abdf78d69810` | 11500 |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `63ac6dcbe2881429ebf2177104c9ad4f15ef5f5e` | 11467 |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_IDENTITY_CONFIGURATION_AP6_DESIGN_2026-11-27.md` | `6de97f0da257cd7433eb550221137037e1b83513` | 25710 |

The host preservation ledger, exact remote source readback and five-path baseline comparison support preservation of all 17 accepted blobs. Assembly also checks those local bytes. No separate seventeen-file hash audit inside the CI job is claimed. Accepted AP1–AP5 implementations, prior evidence, Local-owned records and sibling feature refs are preserved.

## 2. Implemented relation and sequence

The four-input API `observe_identity_configuration(closure_raw, expected_closure_blob, identity_raw, expected_identity_blob)` accepts two immutable byte strings and exact external Git blob pins. Both pins and the existing 1 MiB bound are checked before interpretation. Trusted POSIX Python `-I -S -B` is enforced. Installed AP5 and AP4 helper bytes are authenticated before private initialization; their accepted AP2/AP1 chain remains pinned.

Before either observation stage, AP6 parses strict JSON, validates identity proposal I through accepted AP5 parsing, and compares exactly `sourcePins`, `sourceRef`, `runner`, `locations` and `authorization` with exact JSON types. It requires the fixed three AP1 sibling pins and then retains a detached `matchedProposalProjection`. The location declaration includes runner root, workspace, evidence parent and all six historical roles. Two proposals with equally unsupported sibling pins cannot pass that gate.

The early gate parses C as a strict JSON object and checks that shared projection. **Full C schema, artifact catalog and publication validation occur later inside AP4's AP2 chain.** The early gate does not validate every closure-specific field before AP5 begins. AP5's nested approval, publication and compatibility fields retain their original meanings.

The fixed sequence is proposal relation → one `observe_five_identities` call → one `observe_runner_configuration` call → comparison of prior observations. AP5 rejection prevents AP4. AP4 owns its fresh AP2 snapshot, private AP3 initialization and the actual captured-byte calls `d5b_local_admission.read_plan(verify_blob=True)` and `d5b_rr5_source_preflight.checked_profile(..., check_blob=True)`. AP6 accepts no caller-supplied observation, bundle, module context, transport, callback, helper pin, alternate source policy or execution mode. It supplies no earlier AP2 snapshot as a substitute for AP4's own observation.

## 3. Exact comparison and partial progress

**Comparison scope: `AP5AfterObservation_VersusAP2BeforeCandidateInitializationOnly`.** AP6 compares AP5's final runner observation, projected to exactly 12 common fields, and its complete final location map with AP2 observations captured before AP4 candidate module initialization. AP4 returns those frozen observations after its actual configuration consumers. There is no post-consumer checkout recheck and no second AP5 call. A final comparison can reject after actual consumers have completed; the nested reports and attempted/completed progress remain retained.

The exact runner projection is `head`, `branch`, `origin`, `gitDir`, `commonDir`, `configSha256`, `indexFlagsSha256`, `indexStagesSha256`, `worktreeInventorySha256`, `worktreeFiles`, `worktreeEntries`, `worktreeBytes`. AP6 compares the complete expected key roster and exact value types with AP4's nested AP2 `observedCheckout`, not a silent key intersection. The full location observation map includes recorded path/device/inode values for the runner, workspace, evidence parent, six historical roles and four derived source roots. AP5's additional checkout and administrative-root fields remain nested AP5 observations; they are not fields newly rechecked by AP4.

Reports retain frozen JSON bytes and return fresh detached values. `stageCallsAttempted`, `stageCallsReturned` and `stageCallsCompleted` distinguish stage progress; `comparisonCallsAttempted` and `comparisonCallsCompleted` separately record runner and location comparison entry/completion. AP4 partial failures retain their actual child report. A late comparison rejection retains already completed real consumers. An attempted child with no report is conservatively treated as potentially having used its network or candidate-code capability. Temporary helper registrations are removed; the actual `sys.path` identity/content and ambient candidate module slots are checked.

## 4. Verification and coverage

The source host passed 230 methods in 7 suites: 210 retained methods plus 20 AP6 unit methods. Those AP6 positives explicitly double AP5 while using real AP2 observations and unchanged real AP4 consumers. Required integration was not run on that host. Exact-source CI passed 231 methods in 8 suites: the same 230 shared methods plus 1 required integration method. The integration uses actual fixed AP1 sibling sources, real AP5/AP4 public observers, real checkout scans and ten real temporary bare-ref reads. Its sole behavioral adaptation is test-private routing of AP5's remote subprocess transport to file remotes. It does not qualify production HTTPS or production live-ref state.

| Suite | Host methods | Host footer | CI methods | CI footer | Result |
| --- | ---: | --- | ---: | --- | --- |
| R5 | 94 | 0.122s | 94 | 0.191s | OK / OK |
| AP1R2 | 22 | 6.387s | 22 | 4.238s | OK / OK |
| AP2 | 25 | 10.775s | 25 | 6.816s | OK / OK |
| AP3 | 20 | 6.799s | 20 | 4.342s | OK / OK |
| AP4 | 18 | 6.201s | 18 | 4.323s | OK / OK |
| AP5 | 31 | 14.311s | 31 | 10.211s | OK / OK |
| AP6Unit | 20 | 14.223s | 20 | 9.463s | OK / OK |
| AP6Integration | Not run | Required pinned inputs unavailable | 1 | 2.593s | Not run / OK; required |

The actual common-suite method identities agree between host and CI. Counts above are derived from each evidence dictionary; CI reports 8 actual OK footers and a separate integration inventory. Missing or skipped required integration cannot satisfy the packet gate. Host static checks parsed 3 new Python ASTs, the workflow YAML and 9 Bash run blocks, checked whitespace/helper pins/production constants, and confirmed unchanged source bytes after tests.

The required integration checks out the three actual fixed sibling repositories with full object stores. It clones them into temporary ordinary checkouts without alternate stores, constructs compatible synthetic demo-source H and sole-child runner A from accepted candidate bytes, and creates real temporary bare refs. Fixture H/A are distinct from reviewed source T and documentation M. The integration uses the real AP6 API, unchanged real AP5/AP4 observers, actual AP2 closure validation, AP3 initialization and both actual configuration consumers. Only AP5's private subprocess transport is routed after checking original production HTTPS arguments, fixed endpoints, exact refs and isolated environment. The retained receipt records actual sibling pins, ten queries, completed consumers, selected system Git and closed authority. It qualifies actual pinned source trees with temporary file refs, not production HTTPS reachability.

The 20 unit methods cover byte pins and immutable inputs; strict JSON/type equality; each shared proposal field and declared location role; fixed sibling policy; helper drift and isolation; stage order/rejection; real AP4 partial progress; every common runner field; location observation drift and boolean/integer aliases; frozen comparison timing; detached reports; import-state cleanup; CLI pre-stage denial; a real runner-directory change between stages; and a real configuration-path change after AP2 capture while AP4 consumes captured bytes. The location-observation tests establish the recorded drift/type cases, not an exhaustive per-field location-map negative matrix. Their AP5 double is explicit. Exact method identities are in the machine record and transcripts; the separate required method is `test_real_pinned_sources_and_unchanged_helpers_compose`.

Both environments retain the old-wrapper denial: exit 2, `NotAuthorized`, `outputCreated=false`, closed WEB-to-Local state and no unapproved-envelope file. CI exit/path details are backed by successful shell assertions. Both production approval constants were parsed as `None` from unchanged source. An allowed child-fixture proposal literal is a test publication artifact, not approval.

## 5. Internal review, tools and custody limits

Internal review was static/read-only over AP6, direct AP5/AP4 and bounded AP2/AP1 paths plus the design. It did not run tests, fully review AP3 internals, qualify integration/CI, or perform the seventeen-file preservation audit. It supplies no independent AP6 verdict.

| Finding | Observed gap | Included correction | Bounded readback |
| --- | --- | --- | --- |
| `AP6-PRIMARY-01` | Separate runner/location comparison attempt and completion progress missing | comparisonCallsAttempted and comparisonCallsCompleted record each operation before entry and after exact equality | `ClosedByBoundedReadback` |
| `AP6-PRIMARY-02` | Exact five-field matched proposal projection omitted from report | matchedProposalProjection stored as detached JSON after relation and fixed sibling pins pass | `ClosedByBoundedReadback` |

Both corrections are included in T. The peer record reports no remaining material finding within its assigned scope. Internal review and passing fixtures do not replace independent review.

| Environment | Tool scope | Recorded executable / version |
| --- | --- | --- |
| Host | Python | `3.12.14` |
| Host | fixtureGit | `/usr/local/bin/git` — `git version 2.56.1` |
| Host | auditorGit | `/bin/git` — `git version 2.47.3` |
| Host | AP5FixtureGit | `/bin/git` — `git version 2.47.3` |
| Host | AP5ObserverGit | `/bin/git` — `git version 2.47.3` |
| Host | AP6UnitInitialFixtureGit | `/usr/local/bin/git` — `git version 2.56.1` |
| Host | AP6IntegrationInitialFixtureGit | `/usr/local/bin/git` — `git version 2.56.1` |
| Host | AP6IntegrationCloneAndRefGit | `/bin/git` — `git version 2.47.3` |
| Host | AP6ObserverGit | `/bin/git` — `git version 2.47.3` |
| CI | Python | `3.11.18` |
| CI | auditorGit | `/bin/git` — `git version 2.56.1` |
| CI | fixtureGit | `/usr/bin/git` — `git version 2.56.1` |
| CI | AP5FixtureGit | `/bin/git` — `git version 2.56.1` |
| CI | AP5ObserverGit | `/bin/git` — `git version 2.56.1` |
| CI | AP6UnitInitialFixtureGit | `/usr/bin/git` — `git version 2.56.1` |
| CI | AP6IntegrationInitialFixtureGit | `/usr/bin/git` — `git version 2.56.1` |
| CI | AP6IntegrationCloneAndRefGit | `/bin/git` — `git version 2.56.1` |
| CI | AP6ObserverGit | `/bin/git` — `git version 2.56.1` |

The full environment records preserve the scope of each selection. Retained fixtures and AP6 initial fixture setup use ambient-path Git; AP5 fixtures, accepted observers, and AP6 integration clone/ref operations select system-path Git. Host integration tool entries describe source selection only because integration was not executed there. Do not infer an observer version from a different fixture executable. Trusted Python, standard library, Git and OS remain assumptions; isolation is not a sandbox or standard-library identity proof.

The CI archive is the exact retained UTF-8 encoding of Connector-decoded job-log text, including any BOM. Both logs are copied byte-for-byte with byte count/SHA-256/Git blob checks; no original ZIP/archive-byte attestation is claimed. Artifact metadata and other workflow states retain their stated retrieval limits; other workflows are not AP6 qualification.

There is no simultaneous snapshot, frozen ref, continuous/exclusive custody, recursive administrative-storage custody, raw Git index-byte proof, semantic source preflight, source-data admission, executable closure, general runtime import isolation or future runtime configuration binding. Matching sequential observations does not exclude change-and-restoration between them. AP6 does not recheck AP5 administrative roots through AP4 or inspect current checkout state after consumers. Production physical checkouts, HTTPS and historical Mac inputs remain unqualified. AP5 output bounds apply after subprocess capture; hard process-memory/network-byte/global filesystem-time bounds are not claimed.

Ordinary failures preserve closed structured progress. CLI argument errors may be argparse stderr; termination, `BaseException`, resource exhaustion, serialization failure or unavailable output are not covered by an unconditional JSON guarantee. The observer does not invoke candidate entry points, admission preview, source-inspection entry points, Unity/native builds or Player launch.

## 6. Four repositories and operational smoke readback

| Repository | Branch | Exact source identity for review | Historical candidate path | Physical state |
| --- | --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `c4abb8ec7ab32ba0579c8a3686fa33b4487a37cb` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Unverified |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | Unverified |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | Unverified |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | Unverified |

The demo row names T; final branch HEAD after documentation publication is M and must be recorded separately. All four canonical identities, feature refs and Connector pull/push permissions were read at bootstrap. No Mac path was inspected; package, overlay, native-output and build pins were not regenerated or qualified.

Same-conversation smoke proof was reused and freshly read as four exact branch refs plus four commit objects. Branch: `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0`. All eight GETs matched expected commit identities and sole parents. This is operational transport proof only.

| Repository | Original smoke base / sole parent | Smoke commit | Ref / parent readback |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` | Matched / matched |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` | Matched / matched |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` | Matched / matched |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` | Matched / matched |

This AP6 cycle made no new smoke mutation. Disposable refs remain because the Connector exposes no delete-ref capability in the session; they are not production runner or approval refs.

## 7. Publication gate, next owner and closed authority

M is planned as a documentation/evidence-only sole child of T. Assembly writes five history files plus local prefix/hash manifests; it does not rewrite canonical documents or publish. The publication owner must prepend each supplied readme/status/handoff prefix to the complete accepted baseline bytes. Every historical suffix and Local-owned `LOCAL_VALIDATION.md`/`RETURN_TO_WEB.md` identity must remain intact.

**Final documentation readback is a later required gate, not a completed fact in this self-record.** After publication, record M, verify sole parent T and documentation-only delta, re-read exact packet/canonical blobs, verify source/preserved/Local-owned identities and read all four feature refs. Stop after Primary publication and that readback. Presence of this packet in a working directory or commit does not establish gate completion.

Next read order: README, WEB_TO_LOCAL, AP6 design, this report, independent request, evidence JSON, exact AP6 observer/unit/integration/workflow files, direct accepted helper boundaries and both raw logs. The reviewer must distinguish T/M and fixture H/A, inspect required integration and scope, and return `PassIdentityConfigurationCompositionSourceOnly` or `ReturnRequired`.

Production `APPROVED_EXECUTION_ENVELOPE_BLOB=None` and `APPROVED_LOCAL_HANDOFF_BLOB=None` remain unchanged. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`. Q, explicit user Local approval, production activation, native build, Unity and Player execution remain closed. `R03Accepted`, `H2Passed` and `ReadyForHumanReviewGate` remain false. Current real Unity/native/Player work is `NotRun`; zero real Player cells have passed and all 18 remain `NoCoverage`. Historical Mac paths remain physically `Unverified`. A non-null child-fixture proposal pin is a test publication artifact, not an approval, and is distinct from the unchanged production constants.

The latest Local-owned Native B1 oneuse-12 focused PASS is historical and not AP6 qualification. Source corrections return to Primary. Local commands, production candidate integration, approval repinning, Q execution, evidence promotion and later milestones remain closed.
