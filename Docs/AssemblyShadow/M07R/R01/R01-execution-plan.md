# R01 execution boundary

Status: in progress; not accepted. R00 independent acceptance is recorded at demo `8b2e0d60a36268c9066c2a68bd69460a6d597534`. All four R01 sibling worktrees branch from that accepted pairing under `/Users/ah/GitHub/hybridclr/assembly_shadow_r01`; R00 worktrees and raw artifacts remain unchanged.

The normative R01 plan and revised design govern this implementation. No R02/R03 work is authorized before human H1.

## Integration plan

1. Extract one standalone native budget helper used by actual ordinary allocation, Shadow allocation, dry-run and batch reservation. Keep existing metadata encoding. Test exact threshold edges, fresh homogeneous capacities, mixed/order effects, ordinary-first consumption, retained failed allocations and integer overflow rejection with native compilation.
2. Add an explicitly versioned budget capability. Preserve legacy API and enum values. New budgeted activation reserves the complete ordered closure under transaction then metadata lock before any Stage. Actual cursor advancement is all-or-nothing for reservation; reserved indices are process-lifetime and never returned by Abort/failure. Ordinary load continues through the same global allocator after reservations and cannot consume reserved indices.
3. Add baseline encoding/ordinary-input evidence and patch capacity reports using exact verified DLL bytes. Reject over-budget input before creating the publication directory. A new report must require the runtime budget capability; legacy evidence cannot be relabeled as budget-admitted.
4. Add state-based recovery reporting using publication, poison and native state, not the mutable last-error slot. Preserve current Failed/Abort rejection. Unknown native failure requires restart; only verified private prepublication states can advertise an Abort path.
5. Investigate pre-Configure use with real Type/object/cctor/native script-resolution experiments before treating ASR-011 as a reproduced native defect. Embed candidate identities independently from ordinary hot-update placeholders. A possible early registration point follows physical metadata table initialization; it must retain first-use observations across Configure and preserve owner/state semantics. Run an untouched activation control before deciding how early tracking affects real Unity startup. Do not whitelist observed startup use merely to make Commit pass.
6. Synchronize native registration, managed wrappers/DTO preservation, Editor schema and verifiers, explicit old-capability rejection and feature OFF. Pin real source commits, reinstall and regenerate definitions before new native ON/OFF builds. Freeze every failed and successful attempt separately.
7. Complete meaningful native/Editor/Python checks and real Player capacity/reservation/recovery/startup evidence, affected M03-M07 regression and R00 performance comparison, then independent stage review. Stop at H1 after R01 and any required R01B.

## Current scope inputs and uncertainties

Fresh R00 snapshot has five candidates, maximum observed closure five, and one configured ordinary hot-update assembly. Actual ordinary runtime image consumption was not measured by the snapshot. Production upper bounds have been requested but not provided. Planned 100/300/1000-assembly stress requirements remain requirements, not support promises. R01 must report actual shared-budget behavior. If the declared supported target exceeds available capacity, R01B is required; an admission rejection alone cannot close that target requirement.

The earliest-safe registration point and native startup trust window are hypotheses pending Player experiments. Existing guard observations begin after Configure. R01 will not label source-only risks as reproduced failures or broaden the historical M00-M07 scope.

## Ownership

Root: architecture, runtime allocator/reservation integration, four-repository pins, Unity/install/build, evidence and final review. Budget worker: new pure native helper and native tests/runner only. Read-only supporting agents: Editor/managed extension points; failure-state and early-startup callchain. Further write ownership will be assigned explicitly once contracts are fixed.
