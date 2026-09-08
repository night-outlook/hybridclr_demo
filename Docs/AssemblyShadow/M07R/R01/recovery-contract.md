# R01 recovery contract — implementation draft

Status: implemented and covered by bounded native tests; R01 Player acceptance and stage review remain pending. This table does not select a startup baseline or authorize a later milestone.

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
- Capacity rejection before Stage: `MetadataCapacityExceeded`, reservation commits no prefix. Correct input or Abort remains available in a healthy private transaction. Native helper tests establish all-or-nothing cursor evaluation; real Player reservation evidence is pending.
- A DLL byte length different from its reservation: `MetadataBudgetMismatch` before owner creation. Real Player evidence is pending.
- Skeleton creation returning an error after producing an owner: enters Failed; retains owner bytes; Abort returns InvalidState; recovery requires restart.
- Runtime metadata initialization failure during Validate: enters Failed with ReferenceResolutionFailed; retained bytes and terminal error survive a rejected Abort; recovery requires restart.
- Baseline use observed before validation: BaselineAlreadyUsed rejects before metadata initialization; Abort succeeds while the use history remains recorded.
- Unexpected native failure: seals Failed and remains RestartRequired after later errors.
- Post-publication module initializer failure: the implementation enters FailedAfterCommit and cannot offer Abort or an intermediate baseline. Existing M06 initializer-failure coverage is historical; the R01 native adapter test independently checks the production post-publication failure transition and durable recovery, while a fresh actual Player initializer-failure run remains pending.

The current actual-state-machine receipt is `native-transaction-5.json`: 109 checks, fresh subprocesses, real identity parser and production transaction code with explicit synthetic skeleton ownership/backend outcomes and production Commit callbacks. It does not initialize Unity GC, execute real runtime metadata initialization or exercise real Player publication. The separate production recovery helper receipt records 498 checks, including unknown/error/publication combinations. These counts are different verification boundaries and must not be presented as full Player coverage.
