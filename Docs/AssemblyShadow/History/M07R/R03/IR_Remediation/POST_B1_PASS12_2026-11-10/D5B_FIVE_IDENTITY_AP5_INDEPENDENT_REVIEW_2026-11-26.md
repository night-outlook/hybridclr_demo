# D5-B AP5 Independent Source Review

Date: 2026-11-26 (America/Los_Angeles)

**Verdict: PassFiveIdentityObservationSourceOnly**

**Exact implementation reviewed: hybridclr_demo@0dff80b0fffb37d8c13ff08ad955454a60dde5d6.**  
**Primary documentation/evidence packet reviewed: hybridclr_demo@02eb120f68d9ecee436c6269220d5d974a2bc769.**  
**Role: independent source reviewer, separate from Primary Implementation and Local Validation.**

Companion: [independent machine evidence, complete method inventories and raw reviewer fixture log](D5B_FIVE_IDENTITY_AP5_INDEPENDENT_EVIDENCE_2026-11-26.json).

## 1. Decision and scope

The exact AP5 source satisfies the declared bounded five-checkout/exact-ref observation contract. It authenticates externally pinned proposal bytes and the fixed AP2/AP1 helpers; checks five ordinary physical checkouts, all fifteen observed administrative-directory root identities, exact branch/commit and logical index/tree identities, and complete raw worktree contents; requires the runner's sole parent to be the proposed demo source; and compares repeated local, remote and location observations with truthful partial progress.

**No material in-scope source, evidence, preservation or reporting blocker was established. Blocking findings: none. ReturnRequired is not assigned.** The independent review accepts the mechanism and its supplied source-only qualification evidence. It does not qualify production HTTPS reachability, an actual production five-checkout state, the historical Mac paths, atomicity, continuous or exclusive custody, source admission, executable closure, approval, Q, or later execution.

The distinction between identity and authority is preserved throughout. Dynamic proposal pins specify what AP5 observes. The external proposal blob establishes bytes, not approval. The runner's sole-parent edge does not establish AP1's two-path publication delta. AP5 does not compose AP2 closure or AP4 configuration consumption, invoke semantic source preflight, import candidate writer/preflight modules, or promote evidence.

The prior accepted decisions remain intact: R5 **PassDryAdmissionSourceOnly**; AP1 R2 **PassActivationPublicationProposalOnly** and **D5B-AP1-IR-01=ClosedInCorrectedSource**; AP2 **PassRunnerArtifactClosureSourceOnly**; AP3 **PassRunnerImportBootstrapSourceOnly**; and AP4 **PassRunnerConfigurationBindingSourceOnly**. The [accepted AP4 independent report](D5B_RUNNER_CONFIGURATION_AP4_INDEPENDENT_REVIEW_2026-11-26.md) and current committed checkpoints supplied that scope; no missing project state was inferred from chat.

## 2. Review basis and exact publication identities

README and the closed WEB_TO_LOCAL checkpoint were read first, followed by the [AP5 request](D5B_FIVE_IDENTITY_AP5_INDEPENDENT_REVIEW_REQUEST_2026-11-26.md), [design](D5B_FIVE_IDENTITY_AP5_DESIGN_2026-11-26.md), [Primary report](D5B_FIVE_IDENTITY_AP5_PRIMARY_2026-11-26.md), [Primary evidence](D5B_FIVE_IDENTITY_AP5_EVIDENCE_2026-11-26.json), exact source/test/workflow files, direct AP2/AP1 helper paths, preserved configuration, raw transcripts and fresh GitHub Actions records. Repository access and publication use the GitHub Connector.

The review combined direct source inspection, independent static checkout/helper and transport/reporting subreviews, inert AST and hash analysis, independent raw-CI/preservation reconciliation, and a separate run of the existing 31-method AP5 synthetic fixture suite. No implementation, test, workflow, handoff or Local-owned record was edited.

| Role | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Accepted AP4 publication baseline | 911d8f96f44430124c487698dde53183d7a75dd2 | e66674ca6e37a01291350a41a8fbd202dafb9ef8 | e76d8a6ea83ce71b83b4a4263f6054b037088fbb |
| Exact AP5 CI-tested source | 0dff80b0fffb37d8c13ff08ad955454a60dde5d6 | d43a6ca553ad009b656b7691df89cf34f0508280 | 911d8f96f44430124c487698dde53183d7a75dd2 |
| Later Primary documentation/evidence packet | 02eb120f68d9ecee436c6269220d5d974a2bc769 | bc72d32944b408f0b190599e04cfa2f07c28dd3a | 0dff80b0fffb37d8c13ff08ad955454a60dde5d6 |
| This independent publication | Git commit containing this report and companion evidence | Its enclosing Git tree | 02eb120f68d9ecee436c6269220d5d974a2bc769 |

Fresh comparisons establish one source increment containing exactly **four paths**, followed by one **eight-path documentation/evidence-only** child. Root tree hashes were independently recomputed from the returned Git entries and agree with the commit records. The later documentation HEAD and this independent publication are distinct from the CI-tested code.

| Source increment | Exact Git blob | Bytes |
| --- | --- | ---: |
| [d5b_five_identity.py](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py) | ab4e9cbf796d4ab91602a14a9294d3773e75879c | 25,854 |
| [test_d5b_five_identity.py](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py) | 28945bc7bd29ac5404996f2c40cf81e2600917f4 | 54,685 |
| [r03-b2-d5b-local-admission-source-host.yml](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/.github/workflows/r03-b2-d5b-local-admission-source-host.yml) | fa80fefd95f7c4b99d180a2e6584e71abe118469 | 8,552 |
| [D5B_FIVE_IDENTITY_AP5_DESIGN_2026-11-26.md](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_FIVE_IDENTITY_AP5_DESIGN_2026-11-26.md) | bb72ff55828a7881b314cbd870bd46ef229883c4 | 23,226 |

The code commit identifies the observer and tests under review. The successful test proposals contain generated temporary-fixture commits; they are not observations of the four production source heads plus a production runner. The machine evidence retains this distinction and the separate source/documentation ancestry.

## 3. Proposal and helper authentication

The public interface takes exactly proposal bytes and an expected proposal blob. It requires POSIX and actual Python **-I -S -B** flags, an exact lowercase 40-character blob identity, immutable bytes, and the 1 MiB input bound. It checks the actual blob before using the proposal or loading its helper. The CLI input reader additionally requires a canonical parent and a bounded, non-executable, single-link regular file, with no-follow reads and before/after identity checks. [Input and helper loading](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L40-L137).

The schema is closed through AP1's strict JSON and exact-type comparison: duplicate keys, non-finite numbers, missing/extra fields, wrong types, arbitrary endpoint/transport fields and unsupported runner-ref spellings reject. Schema version true or 1.0 does not substitute for integer 1. Four repository roles and the source feature ref are fixed. The runner must belong to the demo repository, have a distinct commit, and use a restricted full codex branch ref different from the source ref. The local ref reader also invokes Git's ref-format check and rejects symbolic branch refs. [Proposal construction](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L140-L179); [strict JSON/type helpers](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L88-L122).

AP5 authenticates AP2 blob **2535bc14c31f1ff2d73fdb8c7be1d7dab605d990** before compiling its captured bytes. AP2 separately authenticates AP1 blob **ecf36a7a51f1750c6e8425ee79e9ac8938102b54** before compiling those bytes. Both helpers were freshly compared with the accepted baseline and remain exact. The AP2 helper temporarily occupies a private module slot and removes its owned registration through finally; AP1's helper module is not installed in the canonical candidate cache. This is reviewed verifier execution, with no candidate writer/preflight import. [AP2's AP1 authentication](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L220-L229).

The three sibling pins may match AP1's constants or differ as synthetic identities. The sourcePinsMatchAcceptedAP1SiblingPins field is metadata only. The focused true-metadata case proceeds through schema validation and subsequently rejects against the fixture heads; it is not a positive accepted-AP1-tuple demonstration. acceptedAP1SourceTupleVerified remains false in every outcome. A caller-created report or a correct proposal hash cannot replace the fresh observer path or confer authority.

## 4. Five checkouts, fifteen administrative roots and sole parent

The four source roots are derived as siblings under the declared workspace; the runner is a separate root. AP2's location checks and AP5's additional checks establish canonical directory spellings, physical separation of the five checkout roots, runner separation from protected locations, evidence-parent separation, workspace/history separation and distinct historical-root identities. Historical locations remain path observations, not authenticated historical datasets. No evidence output directory is created. [Location checks](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L182-L194).

Each role uses a new isolated AP1 Git reader. AP5 requires an ordinary non-bare checkout with real canonical .git, objects and refs directories; absolute Git directory and common directory must equal that checkout's own .git. Shallow/grafted/alternate stores, gitfiles, symlinked administrative directories, includes, unsupported extensions, partial-clone state, filters, URL rewriting, sparse/hidden-status configuration and other excluded forms reject. Exactly one origin must match a canonical spelling for the role. The remote-query endpoint is derived separately and does not use that origin string as a transport instruction. [Role-aware checkout front end](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L205-L266); [isolated local Git reader](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L163-L233).

The HEAD object, attached branch and exact local branch ref must equal the proposal. AP1 authenticates commit and raw tree objects and reconciles parsed parent topology with its native Git view. AP5 rejects unsupported index flags, nonzero stages, submodules and duplicate paths, then compares all logical stage-zero entries with the authenticated tree. It reuses AP2's no-follow complete worktree scan to check actual entries, raw bytes, Git executable-mode semantics, single-link constraints, sizes and read-time identities. Missing, untracked and ignored entries reject. Tracked symlinks are checked as literal link text without following the target. [Raw scanner](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py#L286-L409).

After all five checkout observations return, the local pass requires the **fifteen device/inode pairs** for their .git, objects and refs roots to be pairwise distinct. The comparison combines all three categories across every checkout, so it does not merely compare five .git roots or three separate five-item groups. The guard checks these directory roots; it does not recursively establish unique ownership of descendant files, packs, administrative leaves or backing storage. [All-fifteen guard](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L334-L347).

The runner's authenticated parent list must equal exactly the one-element list containing the proposed demo source commit. Zero-parent, wrong-parent and merge-parent runner cases use actual stored Git commits in the tests and reject before remote queries. AP5 deliberately does not check the AP1 writer substitution, envelope contents, two-path delta or artifact catalog; runnerPublicationRelationVerified remains false.

Configuration/index digests describe the selected Git command outputs and logical entries. They are not hashes of every byte in the raw administrative files. Complete raw worktree scanning excludes the root .git directory, whose supported administration is checked separately. This interpretation matches rawGitIndexBytesVerified=false and completeGitAdministrativeCustodyVerified=false.

## 5. Production transport and real fixture evidence

The production query derives the canonical HTTPS GitHub URL from the fixed repository role, selects system-path Git, and invokes a fixed argument list without a shell. It uses an explicit null Git directory and cwd=/, a newly constructed environment, disabled system/global/inherited Git configuration, cleared credential helpers, disabled prompting, cleared proxy/extra-header configuration, HTTPS-only protocol selection, TLS verification and disabled redirects. It creates no observer scratch directory and exposes no public alternate endpoint or transport callback. [Production invocation](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L269-L300).

Each query must return successfully with byte-valued stdout/stderr no larger than 65,536 bytes each after capture. Stdout must contain one row with the exact requested full ref and expected lowercase object ID. Missing, duplicate, additional, malformed, wrong-ref or wrong-SHA responses reject, as do command failure and timeout. There is no fallback to another endpoint, protocol, tracking ref, saved report or caller-supplied response. [Response processing](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L303-L331).

The repeated remote observation includes identity fields and a **stdout** byte count/SHA-256. Stderr is checked for type and size but does not enter the repeated-response digest. The parser can accept LF or CRLF framing as one exact row; a framing change between passes still changes the stdout digest and rejects. The review therefore accepts stdout-response equality, without claiming identity of both captured streams.

The positive fixture creates four actual ordinary source checkouts, four temporary bare repositories and a separately cloned demo runner. It makes real commits, trees, index entries and branch refs. The runner is a distinct direct child of the demo source and is pushed to its own temporary branch ref. Only the private remote subprocess seam changes URL/protocol selection to the corresponding local bare repository; it calls the original subprocess runner. Positive observations therefore use real checkout scans and real Git ref output, rather than a fabricated success dictionary. [Fixture creation and routing](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L95-L209).

Separate tests inspect the unchanged production argv/environment under inherited sentinel settings and verify actual system Git's null-Git-directory behavior. That behavior test uses a **file-only gate**, so HTTPS cannot occur; its actual invocation deliberately uses a checkout cwd to exercise the null-directory barrier, while cwd=/ is separately checked in the production subprocess-call assertion. These tests do not establish production TLS negotiation, HTTPS reachability or real production refs. Fresh Connector ref reads used in this review are separate bookkeeping observations and are not an AP5 production-transport run. [Transport tests](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L654-L716).

The per-query timeout is 30 seconds. Capture precedes output-size validation, so the limit does not cap process memory or transferred network bytes. The selected system Git versions are qualified only by the recorded fixtures; no broader platform or historical Mac qualification is inferred.

## 6. Repeated readers, progress and report truthfulness

The implemented order is locations before; five local observations before; five remote observations before; five remote observations after; remote equality; five local observations after; local equality; locations after; location equality. Fresh AP1 Git readers, including fresh object/tree caches, serve each checkout call. The order test retains all ten reader instances and checks distinct identities and actual event ordering. [Control flow](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L443-L486); [fresh-reader regression](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L718-L742).

Attempt arrays are updated before calls. An observation map entry appears only after a call returns successfully. Pass completion is recorded after all its requirements; the local pass also requires all fifteen administrative identities and the sole-parent rule before completion. Rejected reports retain completed observations and earlier progress without setting overall success flags.

| Failure stage | Progress that can remain | Overall success |
| --- | --- | --- |
| Input pin, isolation or early helper rejection | No remote attempt; helper flags reflect actual registration | false |
| Checkout scan, all-fifteen guard or sole-parent rejection | Earlier checkout entries and current attempt; no completed local pass until pass guards succeed | false |
| First remote pass partway through | Completed local-before pass, earlier remote entries and attempted failing role | false |
| Second remote response/equality failure | Earlier remote completion; local-after may be absent | false |
| Second local observation/equality failure | Both remote passes can be complete; completed local passes depend on where failure occurred | false |
| Final location equality failure | Both local passes and both remote passes can be complete, with both location maps retained | false |

runnerSoleParentObserved is a progress fact derived from two completed local passes. It may remain true after a later checkout/location equality rejection, while the overall result is rejected and AP1 publication verification remains false. plannedReadOrder names the intended sequence, including on early failure; actual progress is supplied by arrays and maps rather than that plan.

remoteProcessLaunchMayHaveBeenAttempted and networkMayHaveBeenUsed are conservative possibility flags derived from an attempted remote role call. They can be true when process launch fails, or when a fixture uses file transport. They do not assert actual network use, and they remain false for pre-remote rejection. [Progress/report construction](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py#L334-L421).

Success objects store canonical JSON bytes in a frozen dataclass; report access returns a fresh decoded dictionary. Rejections also store serialized report bytes and return copied presentations. No reader, helper module or admission handle is deliberately carried in the report. Private Python state is not an adversarial sandbox. Real sys.path identity/contents and the three candidate cache slots are rechecked; failures cause rejection, without promising restoration of arbitrary external mutations.

Structured reporting covers ordinary Exception. BaseException, abrupt termination, exhaustion, serialization failure and unavailable output are outside an unconditional JSON-delivery guarantee. Argparse retains exit-2 stderr behavior for missing/unsupported options. The CLI catches its specified output failures and returns 2, which cannot guarantee delivery of a JSON body. Cleanup tests cover selected paths; the inspected finally structure supplies the remaining ordinary-path reasoning.

## 7. All 31 focused methods and their actual reach

AST inspection found exactly **31 direct methods** in D5BFiveIdentityFocused, with no inherited earlier AP1–AP4 test class. Subtests are not counted as additional methods. The table identifies the actual source methods and the scope of their bodies; the companion evidence retains exact names, line boundaries, all 210 combined-suite identities and raw status parsing.

| No. | Exact method | Actual evidence and limit |
| --- | --- | --- |
| 01 | [test_01_real_five_checkouts_and_ten_remote_reads_remain_closed](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L254-L288) | Calls the unmodified observer local path and private file-only transport on five actual checkouts and ten real bare-ref reads; verifies heads, common/Git dirs, both pass completions, attempts, intended order, false sibling-pin metadata, helper pins/isolation flags, closed fields and unchanged fixture filesystem inventory. |
| 02 | [test_02_pin_and_immutable_byte_type_reject_before_helper_or_transport](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L290-L301) | Eight raw/pin cases: mismatched/uppercase/non-string/short pin, bytearray, memoryview, str and oversized bytes. Guards helper loading; requires no helper registration, no schema success and no remote attempt. |
| 03 | [test_03_closed_schema_types_roles_authority_and_endpoint_controls](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L303-L355) | Mutates schema/type/role/scope/authority/location/ref/commit fields; removes required fields and adds endpoint/mode/report fields; requires pre-remote rejection. A proposal carrying AP1 sibling pins reports matching metadata true but fails against synthetic checkouts and never claims accepted AP1 tuple. |
| 04 | [test_04_strict_json_rejects_duplicates_nonfinite_invalid_and_nonobject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L357-L365) | Rejects top-level list/null/bool, invalid UTF-8, NaN/Infinity/-Infinity, excessive nesting, and duplicate top-level/nested keys before remote work. |
| 05 | [test_05_exact_runner_ref_spelling_rejects_patterns_and_aliases](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L367-L375) | Rejects short names, wrong namespace, empty suffix, dot-dot, .lock/trailing-dot, wildcard, space, reflog syntax, backslash, hidden segment and overlong spelling before remote work. |
| 06 | [test_06_missing_untracked_ignored_and_raw_modified_files_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L377-L399) | Creates unstaged CRLF byte drift, missing tracked file, untracked file, ignored file and empty extra directory in hybridclr; requires rejection at that role before remotes and restores each case. |
| 07 | [test_07_staged_assumed_skipped_and_submodule_index_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L401-L423) | Creates staged bytes, assume-unchanged, skip-worktree, gitlink/submodule and unmerged stage-1 state in hybridclr_unity; requires pre-remote rejection, then restores. |
| 08 | [test_08_modes_hardlinks_symlink_replacement_and_special_files_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L425-L450) | Changes tracked-file executable mode, adds external hard link, replaces tracked regular file with symlink/FIFO/directory; requires pre-remote rejection. |
| 09 | [test_09_tracked_symlink_literal_is_observed_without_target_read](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L452-L469) | Commits a literal symlink in hybridclr, pushes the new commit to its bare ref, deletes the external target, then observes success with target absent and link intact. Does not instrument every filesystem read, but source uses readlink/no-follow. |
| 10 | [test_10_origins_and_unsupported_local_configuration_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L471-L491) | Rejects wrong or duplicate origin, filter/url rewrite/worktree/ignorestat/sparse/splitindex/diff configuration, include path, promisor/partial-clone settings and worktreeConfig extension. |
| 11 | [test_11_shallow_grafted_alternate_gitfiles_and_bare_layout_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L493-L513) | Creates shallow/grafts/alternates marker files; replaces .git with a gitdir file and with a symlink; sets core.bare=true. These are direct shape tests, not a git worktree add integration. |
| 12 | [test_12_detached_wrong_branch_symbolic_ref_and_wrong_head_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L515-L530) | Detaches HEAD, attaches wrong branch, converts requested branch to a symbolic alias, then advances HEAD; rejects each before remote work. |
| 13 | [test_13_locations_reject_aliases_overlap_missing_and_duplicate_history](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L532-L555) | Checks symlink/noncanonical/relative/missing location values, evidence/runner overlap, workspace-history overlap, duplicate historical role, and a source-root symlink to another checkout. |
| 14 | [test_14_all_fifteen_administrative_roots_must_have_unique_identities](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L557-L571) | For four pairs (.git/.git, objects/objects, refs/refs, objects/refs), runs real checkout observation then substitutes the runner tuple with the demo tuple. Requires five stored observations but no completed local pass. Not a mounted-alias fixture. |
| 15 | [test_15_runner_requires_the_demo_source_as_its_only_parent](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L573-L591) | Creates zero-parent, wrong-parent and two-parent runner commits with commit-tree, changes the runner ref/worktree and proposal pin, then requires sole-parent rejection after five local observations and before any remote call. |
| 16 | [test_16_exact_remote_parser_rejects_ambiguous_malformed_and_changed_rows](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L593-L605) | Accepts one exact stdout row; rejects empty, duplicate/extra blank row, wrong separator/name/SHA, uppercase, non-ASCII, extra tab, oversized data and non-bytes. Does not launch Git. |
| 17 | [test_17_real_bare_remote_missing_and_drifted_refs_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L607-L626) | Deletes hybridclr source ref to observe failure after one completed remote; restores it and changes the demo source bare ref before the sixth query. Verifies partial attempts/maps, possible network and absent second local pass. |
| 18 | [test_18_remote_subprocess_errors_bounds_and_no_fallback_keep_progress](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L628-L652) | Injects OSError, TimeoutExpired, nonzero result, duplicate row, oversized stderr/stdout and str outputs. Requires exactly one transport call, completed first local pass, no completed remote pass and preserved first remote attempt/possible launch. These are controlled seam failures, not real waiting or huge subprocess-output tests. |
| 19 | [test_19_production_remote_arguments_and_environment_are_fixed](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L654-L685) | Supplies inherited Git/config/askpass/SSH/proxy/TLS/PATH sentinels; asserts selected system Git, no -C, null gitdir, exact endpoint/ref tail, controls and exact constructed environment. Mocks subprocess.run only to verify input/capture/cwd=/, env, timeout and check=False. |
| 20 | [test_20_null_gitdir_blocks_benign_cwd_rewrite_without_any_network](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L687-L716) | Adds a benign local HTTPS-to-file rewrite, then runs production-derived argv from the checkout with file-only GIT_ALLOW_PROTOCOL. With null gitdir, HTTPS is rejected before network; without that option, the local rewrite resolves real bare refs. Separately confirms inherited sentinels do not change command/env. Does not run actual production HTTPS. |
| 21 | [test_21_second_pass_uses_ten_fresh_local_readers_and_order](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L718-L742) | Wraps real checkout and location observers plus real file transport; retains ten AP1 reader objects, checks ten unique identities and the exact locations/local/remote/remote/local/locations event order. |
| 22 | [test_22_second_pass_rejects_changed_config_index_worktree_and_local_ref](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L744-L771) | Changes allowed config, sets index assume-unchanged, changes tracked bytes or advances local ref. Requires two completed remote passes and attempted second local pass; final locations absent. It does not assert every individual completed local-pass value in this test. |
| 23 | [test_23_second_pass_rejects_changed_checkout_and_admin_directory_identity](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L773-L792) | After tenth remote, renames and copies the hybridclr checkout or .git directory. Requires both local passes complete followed by checkout-state equality rejection. Tests .git replacement; separate objects/refs changes are covered by compared identity fields and collision logic, not standalone runtime fixtures here. |
| 24 | [test_24_final_location_recheck_rejects_changed_historical_identity](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L794-L809) | After tenth remote, renames and recreates originalS directory. Requires both local passes complete, both location observations recorded, and final location equality rejection. |
| 25 | [test_25_response_bytes_are_rechecked_even_when_parsed_head_is_unchanged](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L811-L823) | At sixth query, changes actual bare-ref stdout LF to CRLF without changing parsed SHA/ref. Requires two completed remote passes, only first local pass completed, and response-equality rejection. |
| 26 | [test_26_helper_pins_authenticate_original_bytes_and_cleanup_all_outcomes](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L825-L859) | Verifies source helper pins; injects inert AP2 and AP1 byte drift, observes success and invalid-schema failure, and compares private AP2 module registry entries. AP2 mismatch rejects before registration; AP1 failure, success and schema rejection remove registration. Name says all outcomes; concrete cases are these, with other ordinary exceptions covered by source finally structure. |
| 27 | [test_27_candidate_modules_remain_inert_and_process_and_files_unchanged](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L861-L878) | Preloads candidate-named module sentinels and guards builtins.__import__ for those names during real fixture observation. Verifies same module objects, sys.path identity/content, unchanged fixture inventory, empty evidence dir, no __pycache__ and closed report fields. |
| 28 | [test_28_public_api_and_report_are_narrow_and_frozen](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L880-L903) | Checks two-argument API signature; changes nested returned success dict without affecting stored bytes or subsequent decoded values; rejects field assignment on frozen dataclass and unsupported kwargs. Changes rejected report dict and checks fresh report retains false authority. |
| 29 | [test_29_real_cli_requires_all_isolation_flags_before_transport](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L905-L915) | Launches separate CLI processes with each of -I/-S/-B missing; requires exit 2, empty stderr, structured flag reason, no remote attempt/helper registration and closed fields. |
| 30 | [test_30_real_cli_argument_and_pretransport_rejections](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L917-L944) | Launches CLI missing required arguments and with seven forbidden options; checks argparse exit 2/stderr/no stdout. Checks mismatched pin, invalid object/array, missing/relative input path yield pre-remote structured failures. |
| 31 | [test_31_real_cli_input_symlinks_hardlinks_and_executable_files_reject](https://github.com/night-outlook/hybridclr_demo/blob/0dff80b0fffb37d8c13ff08ad955454a60dde5d6/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_five_identity.py#L946-L963) | Launches CLI with proposal symlink, hard-linked proposal and executable proposal; requires exit 2 and no remote attempt. |

Several distinctions affect interpretation of this coverage. The all-fifteen negative injects duplicate identity tuples after real scans; it is not a mounted-alias integration test. Timeout, OSError, oversized-output and wrong-type results are injected at the private subprocess seam, so they do not measure real timeout duration or hard resource bounds. The gitfile test creates the disallowed representation directly rather than running git worktree add. Cleanup's “all outcomes” title covers its explicitly enumerated cases, not every possible exception. CLI tests cover argument, isolation and pre-transport file rejection, not successful production HTTPS execution.

Additional static considerations were evaluated without constructing new exploit or integration fixtures. Matching a dynamic proposal or sibling-pin metadata cannot imply approval. Equal repeated values cannot detect every change-and-return or prevent changes after the final read. Administrative-root uniqueness cannot imply recursive storage exclusivity. Logical Git configuration/index output equality cannot imply unchanged raw administrative bytes. A historical location identity cannot authenticate its contents. A completed sole-parent observation cannot rescue a later overall rejection. The implementation's closed fields and documented limits accommodate these cases; no additional source correction was established.

## 8. Exact CI, archived host evidence and independent rerun

Fresh Connector records for [run 45929766326](https://github.com/night-outlook/hybridclr_demo/actions/runs/45929766326), **attempt 1**, and [job 140279429052](https://github.com/night-outlook/hybridclr_demo/actions/runs/45929766326/job/140279429052) report completed/success for **0dff80b0fffb37d8c13ff08ad955454a60dde5d6**. The attempt jobs endpoint returns one job and **13 successful returned steps**, numbered 1–10, 19, 20 and 21. The raw checkout output names the exact source. Ordinary and attempt-specific run records agree: created 2026-11-27T02:40:59Z, updated 2026-11-27T02:41:49Z.

All **210 distinct ordered class.method identities** match exact-source AST, the archived host transcript, fresh and archived CI transcripts, and the Primary method inventory. Every method has a terminal ok status. Both transcripts contain six actual Ran footers and six actual OK footers. The R5 methods that interleave JSON and a separate terminal ok were parsed as such rather than counted from banner text.

| Suite | Methods | Host footer | CI footer | Independent reviewer |
| --- | ---: | --- | --- | --- |
| R5 | 94 | OK; 0.114s | OK; 0.190s | Source/inventory/raw evidence reviewed; not rerun |
| AP1 R2 | 22 | OK; 6.855s | OK; 4.238s | Source/inventory/raw evidence reviewed; not rerun |
| AP2 | 25 | OK; 10.662s | OK; 6.871s | Source/inventory/raw evidence reviewed; not rerun |
| AP3 | 20 | OK; 6.533s | OK; 4.391s | Preservation/inventory/raw evidence reviewed; not rerun |
| AP4 | 18 | OK; 6.476s | OK; 4.325s | Preservation/inventory/raw evidence reviewed; not rerun |
| AP5 | 31 | OK; 13.848s | OK; 10.146s | **OK; 13.940s; exit 0** |
| Total | 210 | Six successful suites | Six successful suites | 31 methods independently rerun |

Durations are unittest footers, not workflow wall times. Host records six numeric exit-0 suite results. CI suite success is supported by successful set-e/pipefail pipeline steps and actual statuses/footers; six separately printed numeric CI exit codes are not claimed.

The host interval is 2026-11-27T02:39:33.829320+00:00 through 02:40:19.152097+00:00. It used a Connector-derived prepublication byte snapshot, not a Git checkout. Recorded changed-file hashes match the exact source, and independent reads establish preservation across commits. The historical transcript does not independently attest its former process/worktree or any physical Mac machine.

| Raw record | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| [Archived Primary host transcript](D5B_FIVE_IDENTITY_AP5_SOURCE_HOST_2026-11-26.log) | 38,286 | 35d27b0435b1325a23a977b24e37a74cc9eba2e399060515da880d9c5ba866ed | 4245b4d4483ef6d4df93a579cc8e4b8365d4f559 |
| [Archived CI and fresh decoded job text](D5B_FIVE_IDENTITY_AP5_CI_45929766326_JOB_140279429052.log) | 70,827 | f88155ca5691591130aca71cddfb561d8dfc43575579669ba6434d1563c44f54 | d6b3dbb245974018cb6d32a16f45a692036ff7b3 |
| Independent AP5 fixture log, embedded in companion evidence | 5,435 | 94a09a7e58fb3a37ba3837a320ee393a9f99c682f9c77ec74a968fde8948644f | f4455b309a116aac3c2e21f5e859afea3ae9b012 |

Fresh decoded CI text equals the committed archive byte for byte when UTF-8 encoded, including the leading BOM. This does not attest original download ZIP/archive bytes. The fresh artifacts endpoint reports total_count=0 and an empty artifacts array. Other workflows are not AP5 qualification.

| Environment | Python | Retained-suite fixture Git | AP5 fixture and observer Git |
| --- | --- | --- | --- |
| Primary host | 3.12.14 | /usr/local/bin/git 2.56.1 | /bin/git 2.47.3 |
| Focused CI | 3.11.18 | /usr/bin/git 2.56.1 | /bin/git 2.56.1 |
| Independent AP5 rerun | 3.12.14 | Not used to select AP5 Git | /bin/git 2.47.3 |

AP5 selects Git through os.defpath for both its fixture and observer. The ambient PATH Git version must therefore not be substituted for the actual AP5 tool. The independent environment was Linux-6.18.57-x86_64-with-glibc2.41. Its exact-source copy included all fifteen protected files plus the four increment files, with all **19** Git blob identities checked before and after. The existing AP5 suite ran under actual **-I -S -B** from 2026-11-27T03:45:12.861114+00:00 through 03:45:26.951037+00:00. All nineteen files remained unchanged. The complete command, environment, methods, raw output and hashes are embedded in the independent evidence.

The historical host and CI wrapper controls agree on **NotAuthorized**, **outputCreated=false**, **retryAllowed=false**, the closed WEB-to-Local state and false R03 acceptance. Host explicitly records exit 2 and absent unapproved envelope. CI establishes those details through the successful final run step's explicit status-2/absent-file assertions and actual denial JSON. The independent reviewer did not rerun that wrapper control or perform Local admission.

## 9. Fifteen-file and protected-record preservation

Each of the fifteen accepted Python/configuration files was downloaded independently at the baseline, tested source and Primary packet: **45 exact-ref file reads**. Decoded bytes are equal across all three; independently recomputed Git blobs and SHA-256 values match the Connector identities and recorded ledger. All four AP5 increment files also retain their source identities in the later packet. CI checked out the exact source; its transcript is not presented as a separate fifteen-file hash audit.

Paths below are relative to Tools/AssemblyShadow/R03IR/.

| Preserved file | Exact Git blob |
| --- | --- |
| D5Local/run_d5_local.py | 519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39 |
| D5Local/d5b_local_admission.py | 99746fe64976da313cbd0e1625f0fcc5a67bca62 |
| D5Local/test_d5b_local_admission.py | 06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c |
| D5Local/d5b_local_admission_plan_v1.json | 5c0ab7a6d788ebd5adf57f1fddc567ba700632e9 |
| D5Admission/d5b_rr5_source_preflight.py | 81e7c3a2eaccb77bff2515c91b173558e4eeba2f |
| D5Admission/d5b_rr5_source_preflight_v1.json | 9956ea49656dc8337f9ab177c40faf29ea20c397 |
| D5Admission/d5b_custody_authority.py | 185c1bd6603a8c43e4222d30ed8bb057ab94824a |
| D5Local/d5b_activation_publication.py | ecf36a7a51f1750c6e8425ee79e9ac8938102b54 |
| D5Local/test_d5b_activation_publication.py | ef0b562951afd5deb49528e5b8acf013a015eadb |
| D5Local/d5b_runner_closure.py | 2535bc14c31f1ff2d73fdb8c7be1d7dab605d990 |
| D5Local/test_d5b_runner_closure.py | ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976 |
| D5Local/d5b_runner_imports.py | 22ad93598131a59b2d5c46174a45187aede848a6 |
| D5Local/test_d5b_runner_imports.py | 86840e72285b99ea885469390b66c42d1f3d681f |
| D5Local/d5b_runner_configuration.py | 5263742017950a28bd9750eeeaefe50df4f4fa49 |
| D5Local/test_d5b_runner_configuration.py | 595ba10093825d4d1c3940587ede8aa66bc6ac83 |

Both Local-owned records retain their exact identities at baseline, source and packet. Complete blob bytes were separately fetched and hashed, including the large validation record; an empty/truncated contents response was not treated as file bytes.

| Local-owned record | Bytes | Git blob |
| --- | ---: | --- |
| Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md | 1,265,383 | cbc4141a1f79c16c920d1723a81c5507b87b7e5f |
| Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md | 696,171 | 411948c65d0ab04a36ed0f43a8944b6c8291ed30 |

Primary-owned WEB_TO_LOCAL.md, blob **62f13e81db74436c9f1601884d864c9def1bd72b**, is preserved by this independent publication. The prior AP4 independent report/evidence retain blobs **4c51ddd9087d7adb65857812721bbb385af94da4** and **7f149c380f4aadf90f997f1576e37d15441efca3**. No historical Native B1 oneuse-12 result is promoted into AP5 qualification.

## 10. Resource limits, current refs and closed authority

The reviewed bounds remain explicit:

| Resource | Bound and interpretation |
| --- | --- |
| Proposal or installed helper | 1 MiB |
| Tracked regular file | 256 MiB |
| One complete checkout scan | 4 GiB and 100,000 entries |
| Tree/filesystem depth | 64 |
| Remote query | 30-second subprocess timeout |
| Captured stdout/stderr | 65,536 bytes per stream, checked after capture |

Ten full scans can hash up to 40 GiB. Git output/object capture and caches prevent a hard process-memory claim; remote capture limits do not cap transferred network bytes; blocking filesystem reads have no global wall-clock guarantee. The observer depends on trusted Python, system Git, standard library and OS. It does not supply a sandbox, atomic snapshot, frozen refs, continuous custody or future-read binding.

Fresh Connector feature-ref reads at **2026-11-27 03:48:49 UTC** returned the following input heads. All rows use branch codex/assembly-shadow-r01b-h1. Only the demo branch receives the independent documentation publication; final identity and remote readback are reported on delivery.

| Repository | Observed input HEAD | Historical candidate path | Physical state |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | 02eb120f68d9ecee436c6269220d5d974a2bc769 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Unverified |
| night-outlook/hybridclr | c3c232023724cbad565b85e9b2c3beea8ce2789a | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | Unverified |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | Unverified |
| night-outlook/il2cpp_plus | 1268dd417ffe9090fcd9ea2d49542c97ed3cccb3 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | Unverified |

These four Connector ref reads are review/publication bookkeeping. They do not qualify the AP5 production transport or establish a fifth production runner checkout/ref.

| Authority or acceptance boundary | Preserved state |
| --- | --- |
| Production APPROVED_EXECUTION_ENVELOPE_BLOB | None |
| Production APPROVED_LOCAL_HANDOFF_BLOB | None |
| Candidate proposal literal | Not approval; not assumed null; unchanged |
| Approved envelope / executionAuthorityVerified | null / false |
| WEB_TO_LOCAL | CLOSED_NO_LOCAL_EXECUTION |
| Local execution, Local validation, explicit user Local approval | NotAuthorized |
| acceptedAP1SourceTupleVerified / runnerPublicationRelationVerified | false / false |
| AP2ArtifactCompatibilityVerified / AP4ConfigurationCompatibilityVerified / AP4CompositionVerified | false / false / false |
| sourceSemanticPreflightVerified / sourceDataInputsVerified | false / false |
| R03Accepted / H2Passed / ReadyForHumanReviewGate | false / false / false |
| Native/Player permissions and Q authorization | false |
| Current real Unity/native/Player work | NotRun |
| Real Player coverage | 18 NoCoverage; 0 passed |
| Evidence promotion, approval repinning, production activation and later milestones | Not authorized |

The production None assignments were checked in actual preserved source. The implementation's Pending independent-review field remains unchanged: it does not self-approve. The separate external source verdict and new canonical status entries supersede the older AP5-pending review checkpoint without altering any execution boundary.

## 11. Publication disposition and stop

**PassFiveIdentityObservationSourceOnly** is assigned to exact source **0dff80b0fffb37d8c13ff08ad955454a60dde5d6** with the qualification limits above. No implementation correction is required for this bounded decision.

The publication consists only of this independent report, its companion machine evidence, and new current-verdict sections in README and Plan/CURRENT_STATUS. Their existing history is retained byte for byte beneath those additions. Implementation, tests, workflow, Primary packet, WEB_TO_LOCAL, Local-owned records and sibling repositories are preserved.

Publication uses the observed documentation HEAD as parent and a non-forced expected-head ref update. Completion requires remote readback of all four published files, protected identities and four feature heads, then stopping. No Local execution/integration, approval repinning, Q, Unity/native/Player work, evidence promotion, Human Review Gate approval or later milestone follows from this source-only verdict.
