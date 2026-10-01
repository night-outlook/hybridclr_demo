# R03 D — batch-C validation matrix

Status: **implemented and host-tested; actual Local C NotRun**. The authoritative next invocation is in `Handoff/WEB_TO_LOCAL.md`. This file supplements the original `A_VALIDATION_MATRIX.md`; it does not weaken R03 stage exits or replace historical A/B results.

## Bound source and target

All four repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact source |
| --- | --- |
| hybridclr_demo | tested source `5c2932d5340728b16302b7cea8f20b64fcc9e7ce`; execute its final docs-only transport identified by the current handoff and Primary prompt |
| hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` |
| il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Unity 2022.3.62f2 / StandaloneOSX / arm64. Direct managed SDK 8.0.318. Reference package/native source pins are unchanged from the original R03 matrix. Host CI results at the tested source are in `D_HOST_EVIDENCE.json`; they are not Local/Unity evidence.

## Existing 36-cell ledger

All original cells remain: entry/final source authority; verifier contracts; detached reference sources; baseline and candidate graph host suites; admission/method host suite; player-fixtures; four prepare/build pairs; actual EditMode tests with mandatory IDs; and the nineteen Player cases in `Tools/AssemblyShadow/R03/player-cases.json`.

The four build roles remain candidate Release, reference Release, candidate Debug and candidate feature-OFF. Player IDs remain C01–C10, R01–R05, D01–D03 and O01. Baseline, moved-slot mapping, old-AOT guard, warm certificate, direction reversal, real target cycle, primitive append, interface/kind/removal rejection and reference observations keep their original expected results. No native expectation or timeout changed.

## Added required subchecks

| Parent cell/path | Additional requirement | Required evidence |
| --- | --- | --- |
| verifier-contracts | all 57 Python tests, including the retained 43 | exact command receipt and unittest output; no skipped required case |
| player-fixtures / metadata | audit 15 Player plus 18 shared DLLs; valid unsigned provider identity and unchanged graph/static witnesses | `fixture-audit/results.json`, consumer sources, all input/peer hashes and separate malformed control |
| player-fixtures / pinned compiler | actual Unity csc compiles all 33 consumers, including baseline, reversal and true-cycle inputs | `consumer-unity-2022.3.62f2/results.json`, emitted consumer DLLs, compiler/runtime/profile hashes, raw commands |
| player-fixtures / compiler negative | separate malformed-key DLL rejected with original exit 1, CS0009 and Invalid public key, no emitted DLL and no surviving group | negative command receipt and stdout/stderr; arbitrary diagnostics do not pass |
| player-fixtures / valid Editor probe | actual isolated Unity compiles and invokes the marker method, exit 0, clean supervised completion | `unity-lifecycle/valid.log`, `.marker`, completion/outer receipts, copied valid A/B hashes |
| player-fixtures / invalid Editor probe | actual separate isolated Unity fails compilation with exact invalid-key diagnostic, original exit 1, no marker and clean supervised completion | `unity-lifecycle/invalid-key.log`, no marker, completion/outer receipts and malformed A hash |
| four builds + EditMode | the same exact-source supervisor adapter completes Unity-owned compiler lifecycle before the outer no-survivor check | each `commands/*/unity-completion.json`, original inner command exit, compiler binding, kernel birth/PGID census and outer schema-v2 receipt |

The two Editor probes are additional compiler/lifecycle observations, not substitutes for any of the four complete native builds or the actual EditMode assertions. The malformed control is a newly generated test-only copy; it is never substituted into a normal candidate/reference build or used to alter A/B evidence.

## Acceptance boundaries

Normal builds, compiler consumers and Editor assertions require exit 0 and their original semantic evidence. The only deliberate exit-1 controls are the separately named invalid-key consumer and Editor probe. Each must prove the specific diagnostic and clean command completion. Their original failed command statuses remain visible inside a passed negative-test assertion.

Unknown, changed or lingering owned compiler processes must fail closed. Do not whitelist dotnet, issue global server shutdowns, relax cleanup or census checks, or reinterpret post-failure cleanup as a passed production command. The outer command PID identifies the supervisor for Unity invocations; Player launches retain direct PID/run-ID binding.

Any failure remains evidence. Independent cells already scheduled by the runner continue; dependent cells are Blocked. Do not invoke blocked cells manually or retry the same root. All 36 cells and the focused seal must pass for `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired`.

## Custody and return

New prescribed root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`. It must be unused. Preserve A, B, R02/H1 and all original execution flags.

Retain `BATCH_EXECUTION.json`, `LOCAL_BATCH_RESULT.json`, `evidence-index.json`, `evidence.tar.gz`, `seal-receipt.json`, all cells/commands/host/builds/players/Editor evidence and the new audit/consumer/lifecycle outputs. Retain excluded live worktrees/SDK/cache roots according to the unchanged seal policy. The focused archive is not the full historical R02 seal.

Local writes factual `LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md`, adds an immutable C checkpoint, commits/pushes Local-owned demo evidence/docs, then stops. Any required non-trivial correction returns to Primary.

`R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false`, and `fullLegacyRegressionAcceptance=false` remain mandatory. Full R03 legacy/resource, broader generic/interface/delegate/stack-trace, capacity/startup/performance/memory, PureInterpreter qualification and independent stage review remain outside this focused repair.
