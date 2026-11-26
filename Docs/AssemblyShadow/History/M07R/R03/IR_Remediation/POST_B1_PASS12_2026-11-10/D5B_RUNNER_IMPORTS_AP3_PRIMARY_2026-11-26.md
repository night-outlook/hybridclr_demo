# D5-B AP3 runner import bootstrap: Primary report

- Date: 2026-11-26 (America/Los_Angeles); validation timestamps below remain UTC
- Stage: Primary source-only runner import bootstrap
- Published source T: `bcf3a9470a12758b210738476d18f80bf60d2eaf`
- Source tree: `a9c4206b4b863614142f48b9d0f9c366df5ca79e`
- Parent and preserved AP2 accepted base: `20ca45419ca797ed2bcd330a7be0698fab59819f`
- Validation: host and exact-source CI passed all 161 methods
- Independent AP3 verdict: **Pending**
- Requested separate verdict: `PassRunnerImportBootstrapSourceOnly` or `ReturnRequired`

## 1. Outcome and stage selection

The AP3 source is published at T, and both host validation and CI passed 161 methods: 94 retained R5, 22 retained AP1 R2, 25 retained AP2, and 20 new AP3. Current CI ran on the exact source commit identified above. These are Primary implementation and validation results; they do not constitute independent AP3 approval or permission for Local work.

AP2 already established the reviewed runner artifact closure and a bounded physical checkout observation. Its accepted independent Pass at `20ca45419ca797ed2bcd330a7be0698fab59819f` remains preserved. AP2 deliberately left candidate import selection unverified: ordinary wrapper loading could select an ambient project module, and the reviewed writer inserts a directory into `sys.path` before importing preflight.

AP3 addresses that next narrow dependency. Its observer consumes fresh AP2-verified immutable source bytes, privately initializes preflight, writer, and wrapper, and observes their import bindings. This stage does not require runtime configuration changes, admission, preview, execution authority, a new Local handoff, Q, or a complete executable-closure claim.

The host receipt records all eleven baseline implementation, test, and configuration files unchanged. AP3 adds its implementation, tests, and design; only the existing workflow changes for integration. Earlier source-only and historical comparator results are not promoted to Local or Player evidence.

## 2. Source and accepted review anchors

| Item | Identity or reference |
| --- | --- |
| Published AP3 source T | [`bcf3a9470a12758b210738476d18f80bf60d2eaf`](https://github.com/night-outlook/hybridclr_demo/tree/bcf3a9470a12758b210738476d18f80bf60d2eaf) |
| Published source tree | `a9c4206b4b863614142f48b9d0f9c366df5ca79e` |
| T parent and accepted AP2 base | `20ca45419ca797ed2bcd330a7be0698fab59819f` |
| Accepted AP2 independent review | [D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md](https://github.com/night-outlook/hybridclr_demo/blob/20ca45419ca797ed2bcd330a7be0698fab59819f/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md) |
| Accepted AP2 review blob | `c9ee646dc77b2775d336b5afcee517a7e0932255` |
| AP2 verifier required by AP3 | `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py`; Git blob `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| Integration workflow at T | [.github/workflows/r03-b2-d5b-local-admission-source-host.yml](https://github.com/night-outlook/hybridclr_demo/blob/bcf3a9470a12758b210738476d18f80bf60d2eaf/.github/workflows/r03-b2-d5b-local-admission-source-host.yml) |
| Current CI run | [Run 45790198813](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813); attempt 1 |
| Current CI job | [Job 139806988184](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198813/job/139806988184); `future-admission-source-host` |

The AP2 Pass is a prerequisite and retained result, not an AP3 verdict. The AP3 design is `D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md` at T, with its exact source identity recorded below.

## 3. Production observer contract

The public API is `observe_runner_imports(raw: bytes, expected_closure_blob: str) -> ImportObservation`. It requires actual process flags corresponding to `-I -S -B`: isolated operation, no site initialization, and no bytecode writes. It accepts closure bytes and their external blob pin. It accepts no caller-constructed bundle, candidate module, callback, import map, execution option, or candidate arguments. The external pin identifies bytes and grants no authority.

The adjacent AP2 verifier is authenticated against `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` before the exact checked bytes are compiled. AP2 then performs fresh closure verification. A temporary uniquely named trusted-helper `sys.modules` entry supports the authenticated AP2 helper's dataclasses and is removed afterward, including on failure. Canonical candidate names are never installed in real `sys.modules`.

Preflight, writer, and wrapper initialize in dependency order from immutable `BundleFile.raw` bytes returned by that fresh AP2 verification, under non-`__main__` names. Private per-module importers enforce exact direct allowlists. A fixed map of preloaded trusted standard-library objects supplies allowed library requests. The writer receives the private preflight object; the wrapper receives the private writer's `main` binding.

The observed direct-import trace contains 23 requests: 19 served by the preloaded standard-library map, two by the private `sys` facade, and two project bindings. The actual ordered-import and real-AP2/private-binding tests passed in both environments. This claim concerns selection during the fixed reviewed initialization.

The path-only `sys` facade owns a private `path` list. The writer's literal top-level insertion affects that list; real `sys.path` is unchanged. The facade is not a general runtime substitute for `sys`. The observer does not rewrite source, replace candidate functions, substitute approval constants, or redirect plan/profile reads.

Module `__file__` values and compilation filenames derive from the verified root/path mapping. The reviewed top-level `Path.resolve()` calls can perform filesystem metadata operations. These labels and paths are not new evidence of physical custody: AP2's snapshot observation occurs before candidate initialization, and AP3 adds no post-import checkout or custody observation.

`ImportObservation` stores immutable JSON bytes and returns a fresh decoded report on access. Its output is binding, hash, import-trace, and stage data. It exposes no candidate module, callable entry point, code object, or execution handle. The observer does not invoke candidate plan/profile content reads; AP2 still performs its established prerequisite artifact and checkout observations.

## 4. Initialization, function invocation, and rejection reporting

The successful observation has kind `R03D5BRunnerImportObservationV1` and result `RunnerImportBindingsObserved_NoExecutionAuthority`.

The **AP3 observer/import phase** invokes no candidate function or entry point. It nevertheless executes reviewed top-level candidate Python while initializing each module. Those two facts are reported separately. The AP3-level `candidateWriterImported` field is true after completed writer initialization. The nested AP2 `artifactObservation` correctly retains its earlier `candidateWriterExecutedOrImported=false`, explicitly scoped by `artifactObservationScope=AP2BeforeCandidateModuleInitializationOnly`. That earlier-stage observation is not an AP3-stage claim.

Attempted and completed initialization are tracked separately. Rejection after preflight or partial writer initialization retains that progress. It does not claim that no candidate code ran merely because the overall observer rejected. There is no fallback to ambient candidate imports or retry under broader permissions.

The broader 161-method validation pipeline has a different purpose: retained R5/AP1/AP2 synthetic suites deliberately exercise existing functions and CLI behavior, and a separate old-wrapper rejection check exercises the closed Local gate. Those operations must not be described as if no existing function or entry point ran anywhere in the pipeline. They do not constitute live Local admission or production evidence generation. The no-function-invocation claim applies to the AP3 observer/import phase only.

## 5. Host and exact-source CI validation

The committed [machine evidence](D5B_RUNNER_IMPORTS_AP3_EVIDENCE_2026-11-26.json) embeds the complete host receipt under `sourceHost` (schema `R03AP3PrimarySourceHostValidationV1`). It records validation from `2026-11-26T09:11:44.037261+00:00` to `2026-11-26T09:12:23.246698+00:00`. Every host suite returned `OK` with exit code `0`. The same committed evidence embeds the exact-source CI receipt under `githubActions` (schema `R03AP3ExactSourceCiValidationV1`), recording the same 161 methods and four `OK` footers.

| Suite | Host methods | Host unittest seconds | CI methods | CI unittest seconds | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Retained R5 | 94 | 0.160 | 94 | 0.185 | Host `OK`, exit `0`; CI `OK` |
| Retained AP1 R2 | 22 | 11.238 | 22 | 4.133 | Host `OK`, exit `0`; CI `OK` |
| Retained AP2 | 25 | 17.980 | 25 | 6.721 | Host `OK`, exit `0`; CI `OK` |
| New AP3 | 20 | 9.036 | 20 | 4.260 | Host `OK`, exit `0`; CI `OK` |

The durations are the recorded `unittest` footer seconds, not elapsed driver times. AP3's 20-method inventory matches host, CI, and source. The host receipt also records two Python AST inputs, parsed workflow YAML, five syntax-checked Bash run blocks, no trailing whitespace, and unchanged source bytes after tests.

CI run `45790198813`, attempt `1`, was a `push` run on branch `codex/assembly-shadow-r01b-h1` with `head_sha=bcf3a9470a12758b210738476d18f80bf60d2eaf`. The checked-out SHA matches that head. The run and its one job are both completed with conclusion `success`. The job returned eleven step records, all completed successfully. The run was created at `2026-11-26T09:14:57Z` and updated at `2026-11-26T09:15:29Z`.

### AP3 coverage

| AP3 methods | Exercised boundary |
| --- | --- |
| 01–02 | Real AP2 snapshot, three private bindings, and actual ordered direct imports |
| 03–06 | Ambient candidate cache, meta/path caches, source/opaque-bytecode nonselection, and unchanged real `sys.path` |
| 07–08 | No candidate function/content-reader calls during the import phase; captured bytes remain the source after later pathname changes |
| 09–13 | Invalid external pins/raw input, changed trusted helper, malformed or inconsistent snapshots, and unsupported direct imports |
| 14–17 | Immutable report copies, truthful partial initialization, compilation interruption, and temporary helper registration cleanup |
| 18–20 | Actual isolated CLI, checkout/no-output observations in those fixtures, required flags, rejected pins, and rejected execution arguments |

The AP3 outer harness uses actual `-I -S -B` flags and explicitly loads trusted fixture modules by their local test paths before invoking the public API. That is deliberate trusted test initialization. It does not establish that an arbitrary preexisting Python process is pristine or attest the standard library. The exact workflow and named test methods at T define the source-only validation procedure.

A preparatory discovery run reported 45 passing methods because a module-level TestCase alias also exposed the existing 25 AP2 methods. Removing that alias restored the intended 20-method AP3 suite; the corrected focused run passed in 8.579 seconds. Those development runs are not counted as extra qualification. The completed combined host and exact-source CI runs above are the current 161-method evidence. The machine evidence retains this preparation history.

### Toolchain identities

| Environment | Python | Fixture Git | Verifier/auditor Git |
| --- | --- | --- | --- |
| Host | `3.12.14`; `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3` | `/usr/local/bin/git`; `git version 2.56.1` | `/bin/git`; `git version 2.47.3` |
| CI | `3.11.18` | `/usr/bin/git`; `git version 2.56.1` | `/bin/git`; `git version 2.56.1` |

The host platform is `Linux-6.18.57-x86_64-with-glibc2.41`. Fixture Git and verifier/auditor Git remain distinct observations. On the host they have different recorded paths and versions. These identities characterize source-only validation, not current Mac, Unity, Xcode, IL2CPP, or Player inputs.

### Closed Local guard

Both receipts record the old wrapper's rejection outcome as `NotAuthorized`, with `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `outputCreated=false`, and `retryAllowed=false`. The host receipt records the unapproved-envelope path absent. The successful CI gate step asserts the expected exit code `2` and absence of that unapproved envelope.

This negative guard check deliberately invokes existing CLI logic in the broader validation pipeline. It grants no admission or execution authority and does not alter the narrower AP3 observer no-function-invocation claim.

## 6. Transcript identities and transport scope

| Transcript in the documentation/evidence packet | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| [Host source validation log](D5B_RUNNER_IMPORTS_AP3_SOURCE_HOST_2026-11-26.log) | 27675 | `971abdddbb5acba734c42ab2717d1b29600959aecfdbc4692558e3a42bb403d7` | `bb1d78a280c3eaa3e244ae0d7752a9c762b99e01` |
| [CI run/job log](D5B_RUNNER_IMPORTS_AP3_CI_45790198813_JOB_139806988184.log) | 54594 | `5be56b9b80fb25fc6b268281801645cfabd4d682dd175e9974d6496689307296` | `0f156bf431fb775e2df7ae8c19675e92002c51b2` |

The host transcript resides at `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_SOURCE_HOST_2026-11-26.log`. The CI transcript resides at `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_CI_45790198813_JOB_139806988184.log`.

The CI log representation is the UTF-8 re-encoding of the exact Connector-decoded text, with no newline or BOM normalization; the decoded BOM was preserved. Its byte length, SHA-256, and Git blob identify that retained representation. They are not a claim about an unexamined original archive or transport-byte encoding. The run uploaded zero workflow artifacts; this packet preserves the retrieved transcript separately.

These transcript links belong to the documentation/evidence packet, not to source T. Their exact bytes are already recorded above. The packet is prepared for a documentation/evidence-only successor whose parent is T; this report claims no not-yet-created successor SHA. The final handoff identifies the actual successor after creation and readback.

## 7. Published source and baseline preservation

The published source commit T has tree `a9c4206b4b863614142f48b9d0f9c366df5ca79e` and parent `20ca45419ca797ed2bcd330a7be0698fab59819f`. The completed host receipt records these exact tested source identities and confirms source bytes unchanged after testing:

| Tested source artifact | Git blob | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py` | `2bff794380f77b61dbbd84058fcba94d5ee4d9d2` | 19539 | `fe348335d0d72d21ee7c7d5e3aa7cb9985cc03a9e05b45b6dbbfedd8a3808cab` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py` | `86840e72285b99ea885469390b66c42d1f3d681f` | 40342 | `62c2f53f9425d7c7b2780c7e848cb4d6243b65b0bed9b6292c2cf2b0ec8c4192` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `e55b88f8e33d12077d0a0ca4105d8fe02c3e7d01` | 5992 | `e57887096456ebc6b85338a75bce10bfac57606025347126b3b0e9c66638dec2` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_IMPORTS_AP3_DESIGN_2026-11-26.md` | `af08b920ada9e628f78a73f8b26bc015cbd78364` | 18191 | `08f86835f2519b64a49a25dd440a1b8b6aed79df85185f719af4224bcd06f9b2` |

The same receipt records all eleven baseline files preserved against the accepted AP2 base:

| Preserved baseline file | Unchanged Git blob |
| --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py` | `ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976` |

The implementation source tested on the host and checked out by CI is T. A later documentation/evidence commit does not replace T as the tested source identity.

## 8. Repository transport and publication identity

All four repositories use branch `codex/assembly-shadow-r01b-h1`. GitHub Connector is the authoritative transport. Repository identity, branch existence and pull/push permissions were verified before this increment. The source review tuple is:

| Repository | Source review commit | Historical candidate path | Verification scope |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `bcf3a9470a12758b210738476d18f80bf60d2eaf` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Pull/push verified; physical Mac Unverified |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | Pull/push verified; physical Mac Unverified |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | Pull/push verified; physical Mac Unverified |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | Pull/push verified; physical Mac Unverified |

The demo source was published through Connector `create_tree → create_commit → update_ref`, with expected parent `20ca45419ca797ed2bcd330a7be0698fab59819f` and `force=false`. Remote readback matched T and the exact four source files. The compare contains exactly one commit and those four paths. No sibling feature ref was mutated. Primary used `/workspace/scratch/a6fad0908883/ap3_source`, a Connector-derived snapshot. No current physical Mac checkout, Unity package, native overlay or build input was qualified.

The documentation/evidence-only successor containing this packet uses T as parent and preserves its source. Its changes are the three canonical entry points (`README.md`, `Plan/CURRENT_STATUS.md`, `Handoff/WEB_TO_LOCAL.md`), this Primary report, the review request, machine evidence and two raw logs, all under `Docs/AssemblyShadow`. Existing canonical document history is preserved as an exact suffix. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` remain unchanged. The final handoff records the actual containing commit and fresh four-repository remote heads after publication; it does not label that documentation commit as the CI-tested source.

### Existing Connector smoke proof

The same-conversation operational smoke test used retained branch `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0`. This cycle freshly read back its exact refs and commit objects; it did not create another smoke commit.

| Repository | Original smoke base | Retained smoke commit | Current cycle observation |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` | Exact retained ref and commit object read back |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` | Exact retained ref and commit object read back |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` | Exact retained ref and commit object read back |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` | Exact retained ref and commit object read back |

Cleanup is unavailable because this session exposes no delete-ref/branch Connector operation. The disposable branches remain explicitly recorded. They are transport proof only, never product acceptance, the source review tuple, or the latest feature HEAD.

### Other workflow metadata

The focused AP3 qualification is run `45790198813` only. The remaining source-T workflows returned the following metadata; their raw logs were not used for this AP3 qualification, and no reason is inferred for cancellation.

| Run | Workflow | Reported conclusion |
| --- | --- | --- |
| [45790198964](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198964) | R03 K source-bound contracts | `cancelled` |
| [45790198793](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198793) | R03 L factory and receipt contracts | `cancelled` |
| [45790198938](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198938) | R03 independent-review terminal host contracts | `cancelled` |
| [45790198943](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198943) | R03 K terminal observation host contracts | `cancelled` |
| [45790198828](https://github.com/night-outlook/hybridclr_demo/actions/runs/45790198828) | R03 Native B1 first error source/host qualification (not Unity) | `success` |

These metadata observations add no Unity, native runtime or Player qualification. The precise AP3 claims remain those of the focused 161-method workflow and preserved host evidence.

## 9. Runtime-read and trust limits

| Boundary | Established observation or remaining limit |
| --- | --- |
| Fixed reviewed initialization import selection | AP3's bounded observed result, supported by host and exact-source CI tests |
| AP2 artifact/checkout snapshot | Retained prerequisite observation before candidate initialization |
| Candidate plan/profile content reads during AP3 initialization | Not invoked by the AP3 observer |
| Later runtime configuration reads bound to immutable snapshot bytes | Not established |
| Interpreter or standard-library provenance attestation | Not established; trusted-runtime assumption remains explicit |
| Full runtime import isolation or Python sandboxing | Not established |
| Complete executable closure | Deferred |
| Active source-data admission, current source tuples, live remote refs | Deferred |
| Current Mac, Unity, Xcode, IL2CPP, or Player inputs | Deferred |
| Post-import, exclusive, or continuous custody | Not established |
| Q and execution authorization | Not established |
| Live Local admission, preview, one-use writing, native build, Unity or Player execution | Not authorized or performed by the AP3 observer |

AP2's retained limits also include no complete Git administrative-file custody, raw index-format qualification, namespace lock or ABA exclusion. AP3 adds no process resource sandbox.

The writer's later `read_plan()` and preflight's later `inspect()` still use their existing runtime pathnames if separately invoked. Existing content checks can authenticate the bytes read then; AP3 does not call those functions or bind those future reads to the captured snapshot. The profile under the active source checkout remains a separate read and location.

Within the AP3 observer/import phase, no validator, `inspect`, either candidate `main`, `read_plan`, `approved_envelope`, `seal_oneuse_dry_admission`, or other candidate function is invoked. Standard-library objects such as `os` and `subprocess` remain capable objects. The basis is exact reviewed initialization, not an arbitrary-code sandbox.

## 10. Closed authority and requested independent verdict

The successful AP3 result explicitly states `NoExecutionAuthority`. It cannot substitute for separately reviewed executable admission or explicit user Local approval.

- `WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`.
- `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`.
- `approvedEnvelopeGitBlob` remains null as an authority field. A candidate literal or publication blob may be recorded only as artifact identity.
- The AP3 observer grants no live admission, preview, one-use writer, native build, Unity, IL2CPP link, or Player launch authority.
- Q is not approved; `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false.
- Real Player passes remain zero, with all 18 cells without coverage.

Independent AP3 review is **Pending**. The requested separate verdict is `PassRunnerImportBootstrapSourceOnly` or `ReturnRequired`, with the latter identifying concrete blockers and corrections. Neither this Primary report nor a source-only Pass authorizes Local work, Q, or an acceptance transition.
