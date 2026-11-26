# D5-B AP3 runner import bootstrap: independent review request

- Date: 2026-11-26 (America/Los_Angeles); validation timestamps below remain UTC
- Requested published source T: `bcf3a9470a12758b210738476d18f80bf60d2eaf`
- Source tree: `a9c4206b4b863614142f48b9d0f9c366df5ca79e`
- Parent and preserved AP2 accepted base: `20ca45419ca797ed2bcd330a7be0698fab59819f`
- Host and exact-source CI validation: all 161 methods passed
- Independent AP3 verdict: **Pending**
- Requested verdict: `PassRunnerImportBootstrapSourceOnly` or `ReturnRequired`

## 1. Review question and stage selection

Does AP3 at T establish the bounded claim that the three fixed reviewed candidate modules initialize from fresh AP2-verified immutable source bytes, with their direct imports selected privately, without the AP3 observer calling any candidate function or granting execution authority?

AP2's accepted independent Pass at `20ca45419ca797ed2bcd330a7be0698fab59819f` remains preserved. It established runner artifact closure and a bounded checkout observation while deliberately leaving candidate import selection unverified. The next narrow gap is the wrapper's ambient project import and the writer's top-level `sys.path` insertion before importing preflight. AP3 addresses those import bindings while leaving runtime configuration, full executable closure, custody, Q, and Local authorization for separate work.

The host receipt records all eleven baseline implementation, test, and configuration files unchanged from the AP2 base. AP3 adds its module, tests, and design; only the existing workflow changes for integration. Independently check the exact baseline table and source identities in the Primary report rather than treating those Primary assertions as the verdict requested here.

## 2. Exact source and evidence packet

| Material | Identity or reference |
| --- | --- |
| Published AP3 source T | [`bcf3a9470a12758b210738476d18f80bf60d2eaf`](https://github.com/night-outlook/hybridclr_demo/tree/bcf3a9470a12758b210738476d18f80bf60d2eaf) |
| Source tree and parent | Tree `a9c4206b4b863614142f48b9d0f9c366df5ca79e`; parent `20ca45419ca797ed2bcd330a7be0698fab59819f` |
| New implementation | `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py`; blob `2bff794380f77b61dbbd84058fcba94d5ee4d9d2` |
| AP3 tests | `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py`; blob `86840e72285b99ea885469390b66c42d1f3d681f` |
| Integration workflow | [.github/workflows/r03-b2-d5b-local-admission-source-host.yml](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/.github/workflows/r03-b2-d5b-local-admission-source-host.yml); blob `e55b88f8e33d12077d0a0ca4105d8fe02c3e7d01` |
| Design | `D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md`; blob `af08b920ada9e628f78a73f8b26bc015cbd78364` |
| Primary report | [D5B_RUNNER_IMPORTS_AP3_PRIMARY_2026-11-26.md](D5B_RUNNER_IMPORTS_AP3_PRIMARY_2026-11-26.md) |
| Accepted AP2 independent review | [D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md](https://github.com/night-outlook/hybridclr_demo/blob/20ca45419ca797ed2bcd330a7be0698fab59819f/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md); blob `c9ee646dc77b2775d336b5afcee517a7e0932255` |
| Authenticated AP2 verifier pin | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| Current CI run | [Run 45790198813](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813); attempt 1 |
| Current CI job | [Job 139806988184](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813/job/139806988184); `future-admission-source-host` |

The Primary report gives all four tested source blobs, byte lengths and SHA-256 values, and all eleven preserved baseline blobs. The committed [machine evidence](D5B_RUNNER_IMPORTS_AP3_EVIDENCE_2026-11-26.json) embeds complete host and CI receipts under `sourceHost` and `githubActions`, respectively. It also records the four repository identities, prior review, transport proof, preparation history and closed authority. Raw retained transcripts are identified below.

This packet is prepared for a documentation/evidence-only successor whose parent is T. Its transcript/report links target that packet, not source T. No not-yet-created successor commit identity is asserted here; the final handoff supplies its actual SHA after creation and readback. T remains the source tested on the host and checked out by CI.

## 3. Import and process boundary to review

The public API is `observe_runner_imports(raw: bytes, expected_closure_blob: str) -> ImportObservation`. Actual `-I -S -B` flags are required at the API boundary. Its caller cannot supply a verified bundle, module object, import callback/map, execution option, or candidate arguments.

The adjacent AP2 verifier must match Git blob `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` before its checked bytes are compiled, and it must perform fresh AP2 closure verification. A uniquely named temporary real-`sys.modules` entry is allowed only for the authenticated trusted AP2 helper's dataclass mechanism and must be removed on success and failure. Canonical candidate names are never installed in real `sys.modules`.

Candidate preflight, writer, and wrapper initialize in dependency order from immutable AP2 bundle bytes. They use non-`__main__` names, private per-module exact direct import allowlists, and fixed preloaded trusted standard-library references. The writer's project import binds to the private preflight; the wrapper's `main` binds to the private writer's `main` without being called.

The observed trace contains 23 direct requests: 19 preloaded standard-library selections, two private-`sys` selections, and two project bindings. Host and CI passed the actual ordered-trace, private-binding, unsupported-import, and ambient-nonselection checks. Independently confirm the source and evidence supporting those claims.

The private path-only `sys` facade confines the writer's literal insertion to its own list and does not delegate unknown attributes to real `sys`. Real `sys.path` stays unchanged. The observer performs no source rewriting, function replacement, approval-constant substitution, plan/profile redirection, or candidate configuration-content read.

`__file__` and compilation filenames derive from the verified runner root and fixed relative paths. Candidate top-level `Path.resolve()` may perform metadata reads. AP2's physical snapshot observation precedes candidate initialization; AP3 does not establish a new post-import checkout observation or continuous custody.

The result stores immutable JSON bytes and returns fresh report copies. It exposes no candidate module, callable, code object, or execution handle. The successful kind/result are `R03D5BRunnerImportObservationV1` and `RunnerImportBindingsObserved_NoExecutionAuthority`.

## 4. Truthful initialization and failure reporting

During the **AP3 observer/import phase**, candidate top-level code executes, but no candidate function or entry point is invoked. The current AP3-level `candidateWriterImported` field must acknowledge completed writer initialization. The nested AP2 `artifactObservation` correctly retains its earlier `candidateWriterExecutedOrImported=false` under `artifactObservationScope=AP2BeforeCandidateModuleInitializationOnly`; that earlier-stage value must not be interpreted as a current AP3-stage claim. Review attempted and completed initialization separately: a rejection after partial progress must preserve what was attempted or completed and must not falsely claim that candidate code did not run.

Check temporary trusted-helper registration cleanup, denied-import behavior, and the absence of fallback to ambient imports or retries under broader permissions. The private importer establishes selection during fixed reviewed initialization; it is not a general Python sandbox, pristine-interpreter or standard-library attestation, full runtime isolation, runtime configuration closure, executable closure, or authorization.

The no-function-invocation claim is intentionally scoped. Retained R5/AP1/AP2 synthetic tests exercise existing functions and CLI behavior, and the separate old-wrapper rejection gate invokes existing CLI logic. The complete 161-method pipeline must not be characterized as invoking no existing functions anywhere. Those source-only tests are distinct from live Local admission and from the production AP3 observer's contract.

## 5. Completed validation evidence

Both environments passed 161 methods: 94 R5, 22 AP1 R2, 25 AP2, and 20 AP3. Host suites each returned `OK` and exit `0`; CI records four `OK` footers and a successful run/job. AP3's 20-method inventory matches host, CI, and source.

| Suite | Host methods | Host unittest seconds | CI methods | CI unittest seconds | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Retained R5 | 94 | 0.160 | 94 | 0.185 | Host `OK`, exit `0`; CI `OK` |
| Retained AP1 R2 | 22 | 11.238 | 22 | 4.133 | Host `OK`, exit `0`; CI `OK` |
| Retained AP2 | 25 | 17.980 | 25 | 6.721 | Host `OK`, exit `0`; CI `OK` |
| New AP3 | 20 | 9.036 | 20 | 4.260 | Host `OK`, exit `0`; CI `OK` |

Durations are recorded `unittest` footer seconds. Host validation ran from `2026-11-26T09:11:44.037261+00:00` to `2026-11-26T09:12:23.246698+00:00`. The host receipt also records two Python AST inputs, parsed workflow YAML, five syntax-checked Bash run blocks, no trailing whitespace, source bytes unchanged after testing, and eleven preserved baseline files.

CI run `45790198813`, attempt `1`, checked out `bcf3a9470a12758b210738476d18f80bf60d2eaf` and confirms that checkout matches `head_sha`. It is a completed successful `push` run on `codex/assembly-shadow-r01b-h1`. Its one job returned eleven successful step records. The run was created at `2026-11-26T09:14:57Z` and updated at `2026-11-26T09:15:29Z`.

### Environment and transcript identities

| Environment | Python | Fixture Git | Verifier/auditor Git |
| --- | --- | --- | --- |
| Host | `3.12.14`; `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3` | `/usr/local/bin/git`; `git version 2.56.1` | `/bin/git`; `git version 2.47.3` |
| CI | `3.11.18` | `/usr/bin/git`; `git version 2.56.1` | `/bin/git`; `git version 2.56.1` |

The host platform is `Linux-6.18.57-x86_64-with-glibc2.41`. Keep fixture Git separate from verifier/auditor Git; the host records different paths and versions for those roles.

| Transcript in the documentation/evidence packet | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| [Host source validation log](D5B_RUNNER_IMPORTS_AP3_SOURCE_HOST_2026-11-26.log) | 27675 | `971abdddbb5acba734c42ab2717d1b29600959aecfdbc4692558e3a42bb403d7` | `bb1d78a280c3eaa3e244ae0d7752a9c762b99e01` |
| [CI run/job log](D5B_RUNNER_IMPORTS_AP3_CI_45790198813_JOB_139806988184.log) | 54594 | `5be56b9b80fb25fc6b268281801645cfabd4d682dd175e9974d6496689307296` | `0f156bf431fb775e2df7ae8c19675e92002c51b2` |

The full repository paths are `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_SOURCE_HOST_2026-11-26.log` and `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_CI_45790198813_JOB_139806988184.log`. The CI transcript is the UTF-8 re-encoding of exact Connector-decoded text, with no newline or BOM normalization and with the decoded BOM preserved. Its recorded hashes identify that retained representation, not an unexamined original transport archive. The run uploaded zero workflow artifacts; the retrieved log is preserved in this separate packet.

### Coverage and harness assumptions

| AP3 methods | Exercised boundary |
| --- | --- |
| 01–02 | Real AP2 snapshot, three private bindings, and actual ordered direct imports |
| 03–06 | Ambient candidate cache, meta/path caches, source/opaque-bytecode nonselection, and unchanged real `sys.path` |
| 07–08 | No candidate function/content-reader calls during the import phase; captured bytes remain the source after later pathname changes |
| 09–13 | Invalid external pins/raw input, changed trusted helper, malformed or inconsistent snapshots, and unsupported direct imports |
| 14–17 | Immutable report copies, truthful partial initialization, compilation interruption, and temporary helper registration cleanup |
| 18–20 | Actual isolated CLI, checkout/no-output observations in those fixtures, required flags, rejected pins, and rejected execution arguments |

The AP3 outer harness runs with actual `-I -S -B` flags and explicitly loads trusted fixture modules by local test path before calling the public API. That deliberate trusted initialization does not prove that an arbitrary existing process or the standard library is pristine. Independently examine the exact workflow/test source, named methods, and retained transcripts rather than treating a method count as sufficient proof.

Both host and CI receipts also record the unchanged Local gate returning `NotAuthorized`, `outputCreated=false`, and `retryAllowed=false`. The host records the unapproved-envelope path absent; the successful CI gate step asserts absence and expected exit `2`. This separate old-wrapper rejection check is part of the broader validation pipeline, not a candidate function invoked by the AP3 observer and not a Local permission.

## 6. Explicit limits and closed authority

The AP3 observer does not invoke candidate plan/profile reads. Later writer `read_plan()` and preflight `inspect()` still use their existing runtime pathnames if separately called. AP3 neither binds those future reads to the captured bytes nor authorizes their invocation. AP2's established artifact and checkout reads remain prerequisite observations; the packet does not claim that the entire verification pipeline makes no filesystem or configuration reads.

Runtime configuration-read closure, interpreter/standard-library attestation, full runtime import isolation, complete executable closure, active source-data admission, current source tuples and live remote refs, current Mac/Unity/Xcode/IL2CPP inputs, post-import or continuous custody, Q, and Local authorization remain deferred or unestablished.

The production AP3 observer/import phase calls no candidate function, validator, admission routine, preview, writer, Unity/native build, or Player entry point and creates no candidate evidence output. Source-only fixtures and the separately exercised closed gate retain their distinct scope.

`WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`. `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`; independently reviewed executable admission and explicit user Local approval have not been granted. `approvedEnvelopeGitBlob` remains null as an authority claim. Candidate literal/publication blobs identify artifacts and do not create an approved envelope. Q is not approved. `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false. Real Player passes remain zero, with all 18 cells without coverage.

## 7. Required independent response

Independent AP3 review is **Pending**. Return exactly one substantive verdict:

- `PassRunnerImportBootstrapSourceOnly`, supported by the exact reviewed source, evidence, preserved baseline, and bounded limitations; or
- `ReturnRequired`, identifying concrete blockers, affected source or claims, and corrections required before re-review.

Identify the exact source and evidence reviewed, distinguish independently checked facts from Primary assertions, and retain the stated non-claims. A development peer reread and successful Primary/CI tests do not replace this separate verdict.

Do not invoke live candidate admission, preview, one-use writing, native builds, Unity, or a Player to produce the source-only verdict. No verdict requested here grants Q, Local execution, or acceptance authority.
