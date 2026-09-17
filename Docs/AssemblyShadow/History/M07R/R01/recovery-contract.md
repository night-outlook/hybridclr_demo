# R01 recovery contract — implementation draft

Status: implemented and covered by fresh v6 bounded Player/native evidence; the strict14 aggregate has passed, while final packaging has passed; independent stage review remains pending. R01 is unaccepted. This table does not select a startup baseline or authorize a later milestone.

Recovery is computed from native state, actual publication, durable terminal failure/poison and recorded baseline-use rejection. The mutable last error is supplementary. A later rejected Abort or query cannot erase a terminal failure.

| Native condition | Disposition | Abort permitted | Baseline startup validation required |
| --- | --- | --- | --- |
| Healthy Disabled or CandidatesRegistered | BaselineUnselected | No | Yes |
| Private Staging, Staged or Validated with success or a known correctable input rejection | CorrectInputOrAbort | Yes | Yes |
| Private state with recorded BaselineAlreadyUsed rejection | AbortRequired | Yes | Yes |
| Healthy Aborted, including an earlier prepublication baseline-use rejection | BaselineEligibleAfterAbort | No second Abort | Yes |
| Healthy Committed with a published active snapshot | ActiveShadow | No | No |
| Failed, FailedAfterCommit, Committing, unknown state/error, InternalError, durable poison or inconsistent publication/state | RestartRequired | No | Yes |

`CorrectInputOrAbort` describes available caller actions; it does not promise that every individual error can be corrected by replaying the same operation. A clean Abort retains private metadata and reserved image indices for process lifetime and forbids a second transaction. `BaselineEligibleAfterAbort` is not proof that resources, prior native effects or application startup are compatible; the coordinator must make that decision in its later authorized milestone.

## Error-to-state evidence

- Malformed identity before owner creation: `BadImage`, remains Staging; Abort succeeds and recovery becomes BaselineEligibleAfterAbort.
- Capacity rejection before Stage: `MetadataCapacityExceeded`, reservation commits no prefix. Correct input or Abort remains available in a healthy private transaction. Native helper tests establish all-or-nothing cursor evaluation, and the fresh v6 strict Oversize receipt binds the prepublication Player rejection and successful Abort; strict14 aggregation has passed.
- A DLL byte length different from its reservation: `MetadataBudgetMismatch` before owner creation. The fresh v6 strict Mismatch receipt binds the Player rejection, unchanged reservation state and successful Abort; strict14 aggregation has passed.
- Skeleton creation returning an error after producing an owner: enters Failed; retains owner bytes; Abort returns InvalidState; recovery requires restart.
- Runtime metadata initialization failure during Validate: enters Failed with ReferenceResolutionFailed; retained bytes and terminal error survive a rejected Abort; recovery requires restart.
- Baseline use observed before validation: BaselineAlreadyUsed rejects before metadata initialization; Abort succeeds while the use history remains recorded.
- Unexpected native failure: seals Failed and remains RestartRequired after later errors.
- Post-publication module initializer failure: the implementation enters FailedAfterCommit and cannot offer Abort or an intermediate baseline. Existing M06 initializer-failure coverage is historical; the R01 native adapter test independently checks the production post-publication failure transition and durable recovery, while the fresh v6 strict InitializerFailure receipt binds the actual Player transition and inner reason.

The earlier actual-state-machine receipt `native-transaction-5.json` (109 checks) is retained historical evidence. Current v6 native evidence is indexed by [early-v6-native-regressions.json](early-v6-native-regressions.json:1): `native-transaction-v6-1.json` records 131 transaction checks and `native-recovery-v6-1.json` records 498 recovery checks. These are fresh production-header/native boundaries and do not initialize Unity GC, execute full managed metadata initialization or establish full Player publication; they must not be presented as full R01 Player coverage.

The fresh v6 strict early receipts bind the required terminal states: Q04 `Validate` returns code 13 (`ReferenceResolutionFailed`) unpublished in `Failed`, retains its budget, rejects `Abort`, and reports `RestartRequired`; initializer `Commit` returns code 19 (`ModuleInitializerFailed`) in published `FailedAfterCommit`, retains its inner reason, and rejects `Abort`. `Oversize` rejects at `Reserve` with code 23 (`MetadataCapacityExceeded`) and then completes `Abort`; `Mismatch` rejects at `Stage` with code 24 (`MetadataBudgetMismatch`) and then completes `Abort`. These facts are indexed in [early-v6-strict-matrix.json](early-v6-strict-matrix.json:1) and remain bounded evidence bound with the passed strict14 aggregate; final stage review remains pending.

Strict14 completion and original raw hashes are recorded in [early-v6-m07-aggregate.json](early-v6-m07-aggregate.json). The stopped ordering-failure attempt remains preserved; all 140 restart-sealed raw Player files are unchanged.
