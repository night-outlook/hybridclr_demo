# D5-B Runner Configuration AP4 Design

Date: 2026-11-26 (America/Los_Angeles)

Status: Primary source-only design. This document is not an independent verdict, an executable admission, or a Local handoff.

Accepted AP3 publication/review: `77fe1c174eb44c2d14a26cc9b057671541efe2a3`.

Accepted AP3 implementation source: `bcf3a9470a12758b210738476d18f80bf60d2eaf`.

Requested independent verdict: `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired`.

## 1. Decision and exact claim

AP4 will extend the source-only observation by making the existing plan and profile consumers read the immutable bytes captured by a fresh AP2 verification and initialized through the reviewed AP3 import mechanism. The new public API is:

```python
observe_runner_configuration(
    raw: bytes,
    expected_closure_blob: str,
) -> ConfigurationObservation
```

Its implementation lives in `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py`. The public inputs are the closure bytes and their external expected Git blob. The API does not accept caller-supplied snapshots, contexts, modules, functions, import callbacks, adapters, or claims that a prior verification is sufficient.

A successful result establishes `fixedConfigurationConsumerReadsBound=true` for the two specified consumers in this invocation. It establishes that their configuration bytes came from the freshly verified captured records and that the existing validators accepted those bytes with their blob checks enabled. It does not establish general runtime configuration closure, executable closure, live checkout custody after capture, or Local execution authority.

The design makes one intentional change to the accepted AP3 implementation: a private initializer refactor in `d5b_runner_imports.py`. The change budget preserves the other twelve baseline implementation, test, and configuration files byte for byte. AP3's existing public API, CLI, result contract, import-only behavior, and tests remain preserved. This document specifies that preservation requirement; it does not claim a completed comparison or a test result.

## 2. Existing boundary

AP3's `observe_runner_imports(raw, expected_closure_blob)` requires the trusted interpreter flags `-I -S -B`, checks the closure bytes against the external pin, and invokes `_verified_snapshot`. That helper verifies the installed AP2 helper's exact bytes before invoking AP2 to obtain a fresh artifact observation and immutable snapshot records.

AP3's initializer validates the six-artifact roster and each captured record, compiles the three candidate source modules from those captured bytes, and initializes private preflight, writer, and wrapper modules in the reviewed order. Candidate project imports use the existing private importer. The modules are not installed under their candidate names in `sys.modules`, and ambient candidate source or bytecode lookup is not the selection mechanism.

Before returning import details, AP3 verifies the writer-to-preflight and wrapper-to-writer bindings, the original runner-relative path globals, the plan and profile blob constants, the candidate literal proposal blob, and the private `sys.path` initialization. AP3 currently discards the private module and record references when returning its report. Its public observer invokes no candidate function.

AP4 will reuse that mechanism and its validated context. It will not replace it with a second candidate loader or infer provenance from an earlier public report.

## 3. Minimal AP3 private refactor

Introduce `_InitializedSnapshot(NamedTuple)` with exactly these context fields:

| Field | Private contents |
| --- | --- |
| `files` | Validated captured records indexed by the exact artifact paths |
| `modules` | The private modules initialized from the captured candidate source bytes |
| `observation` | The existing JSON-compatible import-observation details |

Move the existing initializer body into `_initialize_snapshot_context`. Preserve its validation, compilation, initialization order, import selection, binding checks, and progress accounting. Return `_InitializedSnapshot(files, modules, observation)` after those checks succeed.

Retain `_initialize_snapshot` as the compatibility wrapper with its existing four-argument interface and dictionary result:

```python
def _initialize_snapshot(closure, records, artifact_report, progress):
    return _initialize_snapshot_context(
        closure, records, artifact_report, progress
    ).observation
```

The public AP3 observer continues through this compatibility wrapper and continues to call no candidate function. The existing AP3 tests remain applicable, including tests that instrument `_initialize_snapshot`, assert the absence of candidate function calls, and require a frozen JSON-only public result.

The refactor intentionally changes the AP3 helper's source identity. AP4 must pin the reviewed refactored helper bytes rather than silently continue to identify them as the accepted older helper. AP2's existing verifier identity and behavior remain unchanged unless a separately scoped change is authorized.

The context is private implementation state. A `NamedTuple` does not make its contained module dictionaries immutable, and private naming is not a Python sandbox or a security boundary against an arbitrary caller in a compromised process. The design retains AP3's trusted-process requirement.

## 4. Fresh verification and deliberate private-global adaptation

Each AP4 public invocation must check its own raw closure input and exact expected blob, verify the installed AP3 helper against AP4's reviewed helper pin, obtain a fresh AP2 snapshot through that helper, and initialize one private context through `_initialize_snapshot_context`.

The consumer invocation must use the records and modules from that same context. Calling the public AP3 observer and subsequently creating a second context would produce two observations and would obscure which captured records reached the consumers; it is outside the selected design.

Only after the unchanged initializer has checked the original path metadata and constants will AP4 deliberately replace two private module globals:

| Private global | Exact captured record |
| --- | --- |
| `writer.PLAN` | `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` |
| `preflight.PROFILE` | `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json` |

The replacement is a narrow captured-file view, not a live filesystem path. It stores immutable verified bytes and their exact record identity. Its supported operations are limited to the existing consumer protocol:

| Operation | Snapshot-view meaning |
| --- | --- |
| `is_file()` | The captured record represents the verified regular-file artifact |
| `is_symlink()` | The captured record is not a symlink |
| `read_bytes()` | Return the exact immutable captured bytes |

These metadata responses describe the verified captured artifact. They do not assert that its current pathname is still present, unchanged, or exclusively held. The adapter must not fall back to opening a path. It must not expose arbitrary path selection, path resolution, writable methods, or a filesystem protocol such as `__fspath__` that could permit unsupported operations to reopen the live file.

The bindings change only the private initialized modules. AP4 must not patch the global `Path` type, built-in file operations, standard-library modules, candidate functions, or ambient candidate module-cache entries to implement the adaptation. The existing `writer.source is preflight` relationship remains intact.

## 5. Exact consumer calls and transitive scope

After binding the captured-file views, AP4 makes these calls with both identity checks explicitly enabled:

```python
plan = writer.read_plan(verify_blob=True)
profile = preflight.checked_profile(
    preflight.PROFILE.read_bytes(),
    check_blob=True,
)
```

The plan path is:

1. `writer.read_plan` calls the bound `PLAN.is_file()` and `PLAN.is_symlink()` methods.
2. It obtains the bytes from the bound `PLAN.read_bytes()` method.
3. `writer.git_blob` checks them against the initialized `PLAN_BLOB`.
4. `writer.parse_json` calls `preflight.read_object`.
5. The existing JSON parser uses `preflight.strict_pairs` and `preflight.require` to reject duplicate keys and require a top-level object.
6. `writer.need` enforces the existing schema, source authority, target, custody, producer, authorization, and mode requirements.

The profile path is:

1. The bound `PROFILE.read_bytes()` returns the captured profile bytes.
2. `preflight.checked_profile` calls `preflight.git_blob` and checks the initialized `PROFILE_BLOB`.
3. `preflight.read_object`, `preflight.strict_pairs`, and `preflight.require` apply the existing strict JSON parsing and profile policy checks.

`read_plan` does not call `checked_profile`; both calls are necessary. Its references to preflight constants are not a substitute for invoking the profile validator.

The candidate function scope is limited to the two root consumers and their existing immediate helper paths: writer `read_plan`, `need`, `git_blob`, and `parse_json`; preflight `checked_profile`, `require`, `git_blob`, `read_object`, and `strict_pairs`. The existing plan comprehension for the expected D5 cell names is also part of the selected expression evaluation.

AP4 does not call either module's `inspect` or `main`, the wrapper's `main`, admission preview, envelope admission, receipt creation, machine inspection, remote/source inspection, native compilation, Unity, or Player. Parsed results remain private or are copied into JSON data; the public result contains no modules, callables, adapters, or initialization context.

## 6. Earlier-stage reporting and truthful progress

AP4 must preserve the meaning and scope of earlier AP2 and AP3 stage evidence. AP2 describes verification before candidate module initialization. The AP3 initialization evidence describes import selection before configuration-consumer invocation. A later AP4 success must not rewrite those earlier observations as if they included configuration consumption, a second checkout check, or execution authority.

The unchanged public AP3 observer continues to report `candidateFunctionsInvoked=false`, `planProfileFunctionsInvoked=false`, and `runtimeConfigurationReadsBound=false`. AP4's own reporting must state that candidate functions were invoked when its consumers run. Calling validators is Python execution even though it is source-only work and confers no Local authority.

AP4 must record attempted and completed consumer calls separately. A rejection after the plan consumer has executed cannot be presented as if no candidate function ran. A profile-read failure and a profile-validator failure must not be confused with successful completion of both consumers. Earlier completed initialization and consumption progress must remain visible in rejected reports.

`fixedConfigurationConsumerReadsBound` is true only when both designated consumer calls successfully validate the bytes supplied through the bound captured-file views. The report must associate that claim with the exact two consumer names and artifact identities. It must remain false on incomplete or rejected consumption.

Broad runtime and authority claims remain false, including:

- `runtimeConfigurationReadsBound`
- `runtimeImportIsolationVerified`
- `runnerExecutableClosureVerified`
- `standardLibraryIdentityVerified`
- `checkoutRecheckedAfterModuleInitialization`
- `exclusiveCustodyVerified`
- `liveRemoteRefsVerified`
- `sourceDataInputsVerified`
- `currentMacInputsVerified`
- `executionAuthorityVerified`

The result remains frozen JSON data with fresh presentation copies. The API and CLI provide no execution option and no externally reusable private context.

Structured rejection covers ordinary `Exception` failures. It does not guarantee a JSON report after `BaseException` (including `KeyboardInterrupt` or `SystemExit`), abrupt termination, resource exhaustion, serialization failure or failed output. Injected failure evidence below refers to ordinary exceptions. Unsupported or missing CLI arguments retain argparse's exit-2, diagnostic-stderr, empty-stdout behavior. AP3's compile-progress list still describes completion of the whole compilation batch; this private refactor does not add a per-compilation journal. Actual isolated process flags remain necessary preconditions, not an attestation of arbitrary process history or standard-library provenance.

## 7. Candidate proposal identity is not approval

The accepted AP3 initializer checks the candidate writer's `APPROVED_EXECUTION_ENVELOPE_BLOB` against the closure's proposal-envelope blob. Consequently, the initialized candidate snapshot can contain the candidate proposal literal even though the production writer source is closed with `APPROVED_EXECUTION_ENVELOPE_BLOB=None`.

AP4 must not rely on the production source's `None` value remaining true inside that candidate snapshot as its explanation for closed authority. It must preserve the initializer's existing literal-identity check and keep candidate proposal identity separate from approved execution authority.

The bounded observation remains closed because it invokes only the specified configuration paths, exposes no admission or execution API, returns no callable context, and keeps its authority report closed. The plan and profile validators independently require their existing closed authorization and unperformed Player/native evidence values. Those checks do not turn the candidate proposal literal into an approval.

The public `approvedEnvelopeGitBlob` remains null. `WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`. `D5BLocalExecution`, `D5LocalValidation`, and `explicitUserLocalApproval` remain `NotAuthorized`. `R03Accepted`, `H2Passed`, `ReadyForHumanReviewGate`, `allowNativeBuild`, and `allowPlayerLaunch` remain false. Unity/Player execution remains unperformed, with zero passed real Player cells and eighteen cells without coverage.

## 8. Why the private refactor is selected

A second candidate loader would duplicate snapshot validation, compilation order, import-routing policy, module-binding checks, and progress accounting solely to avoid changing AP3 helper bytes. That would create another implementation to review and keep aligned while providing no additional configuration-consumption assurance.

The private context refactor preserves one implementation of those operations and lets AP4 use the exact modules and records that it initialized. Keeping `_initialize_snapshot` as a compatibility wrapper preserves the existing AP3 contract and test seam. The deliberate change in AP3 helper identity is explicit and reviewable.

Reparsing the captured JSON through new validators would not establish that the actual existing consumers read the captured bytes. Adding public module injection or caller-supplied snapshot parameters would weaken the provenance boundary. Neither alternative is selected.

The private captured-file protocol is sufficient for the current consumers, so the writer, preflight, plan, and profile need no API or semantic changes for this increment. This is a design choice based on their actual call graph, not a general requirement that every historical helper remain byte-identical forever.

## 9. Narrow validation required for implementation review

This design document records no test execution or passing result. The implementation review should require the following focused evidence:

1. Preserve the existing AP3 tests and their import-only assertions, including no candidate function calls, the compatibility seam, frozen JSON-only results, rejection of execution arguments, and truthful partial initialization progress.
2. Use a real AP2-verified fixture and trace the actual existing plan and profile consumers. Establish that their globals refer to the initialized private modules, that `writer.source` is the same preflight module, and that no candidate function outside the bounded call graph runs.
3. Change or remove benign plan/profile fixture files after snapshot capture. Demonstrate that the consumers validate the original captured bytes and report their original identities. A harmless appended newline is sufficient to distinguish a live reread because the existing blob check would reject it.
4. Guard content-open and process-launch operations after fresh verification. Establish that configuration content comes from the adapters and that no content or process I/O occurs during the bounded consumer phase. Distinguish this assertion from path metadata operations during initialization.
5. Confirm that AP4 calls `read_plan(verify_blob=True)` and `checked_profile(..., check_blob=True)`. Check malformed, missing, swapped, mutable, or inconsistent private records as internal consistency failures without treating such private seams as a public source of provenance.
6. Exercise benign ordinary-exception failures before consumption, between the two consumers, and inside profile validation. Verify attempted/completed progress, closed authority, absence of output artifacts, unchanged candidate import state, and JSON-only result or rejection data.
7. Verify the declared twelve-file preservation boundary and the intentional AP3 helper identity change. Confirm that AP4's helper pin selects the reviewed refactored AP3 bytes.

These checks address the new bounded claim. They require no admission preview, native build, Unity run, or Player run.

## 10. Deferred integration and independent verdict boundary

This increment does not connect the captured-file views to a future admission, inspection, wrapper, or executable entry point. It does not bind every future configuration read. Future consumers that use unsupported adapter operations must fail visibly or receive a separately reviewed integration; they must not silently reopen the filesystem.

Fresh verification followed by captured-byte consumption is not continuous custody. Success does not show that the plan/profile pathnames still refer to the verified files after capture. The remaining runtime import behavior, standard-library identity, other source data inputs, envelope consumption, current machine and Unity inputs, live remote refs, output custody, and executable admission remain separate future work.

An independent reviewer is requested to return `PassRunnerConfigurationBindingSourceOnly` only for the bounded source implementation and its evidence, or `ReturnRequired` for defects or unsupported claims. Neither verdict is supplied by this Primary design document. Even a later `PassRunnerConfigurationBindingSourceOnly` would not authorize Local execution, native work, Unity, Player, or a human-review gate transition.
