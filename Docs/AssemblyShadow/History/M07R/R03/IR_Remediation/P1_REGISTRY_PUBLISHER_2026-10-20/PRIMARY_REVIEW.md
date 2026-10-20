# Primary source review — execution-registry publisher

## Factual starting point

Local-owned `20261020-f09e` was **PASS / PassedSourceHostAndSDKOnly**, 16/16, 75 controlled Python failure tests, five positive managed builds and exact expected-negative, 90/90 official Apple arm64 SDK C++17 syntax checks. Exact previous validated source tuple is in `LOCAL_VALIDATION.md`; the consumed raw/checkpoint/SDK and all historical SNAP-01/N/M/K/I/E/R02 FAIL, strict S custody Blocked and independent full-stage FAIL/re-review NotRun remain unchanged. The registration-witness source/host increment newer than that Local run has not been promoted to official SDK qualification.

## Independent code inspection

1. **Exact hot-path call:** `ObserveExecutionClass` retains the candidate/active membership check, precedence and original `ExecutionObservationLock`. The new helper receives the same registry, witness table, bounded count, revision, pointer and source role inside that scope. There is no new mutex, heap buffer or extra class metadata dereference.
2. **Witness publication ordering:** the helper rejects invalid input, excess capacity and saturated revision before calling the write-once `witnesses.Register`; only after successful registration does it publish the pointer, count and revision. This guarantees no new unwitnessed entry in the reviewed single-owner writer path. Existing pointer encounters bypass new registration, preserving original memo behavior.
3. **Failure behavior:** witness collision, full capacity, null or invalid source and saturated revision do not mutate the slot/count/revision. `ObserveExecutionClass` increments the existing dropped-class observation counter once on failed publisher outcomes. Saturation is an intentional safety tightening: no registration with an unadvanceable revision.
4. **Source authenticity:** `run_opaque_execution_inventory.py` checks the actual added include and one exact helper call in production CPP, restores precisely the previous inline writer and then applies the original witness/revision/opaque strips before recomputing the immutable original getter/guard Git blob. The test fixture compiles the **same exact publisher header**, not a copied algorithm. The producer's real C++ getter bodies and C# APIs are not changed.
5. **Capacity and cost:** compile-time slot alignment (2,048), existing 1,024-entry limit, one pointer hash/probe and one source registration/revision per successful insertion. The underlying write-once witness Table and revision are still process-lifetime. The helper is inline and nonallocating by construction; **no measured Player CPU/memory/GC/RSS benefit is claimed**.
6. **Limits:** registration-path role is not physical `Il2CppClass*` ownership or safe lifetime; the compiler/host fixture cannot prove real metadata teardown, full VM epoch/ABA, original class type-key reading, cross-thread process quiescence or linked Player use. The collector remains inactive. No `R03Accepted` or Human Review Gate promotion follows.

## Tests and evidence

Native source commit `699dec4698a529c66e201aca1802ee8f498d8334`: [dedicated CI 39382804881](https://github.com/night-outlook/il2cpp_plus/actions/runs/39382804881) **PASS, 3/3** Mac Clang/Linux Clang/Linux GCC jobs, each strict and sanitized with **34 distinct groups/profile** (original 25 + 9 writer source-bound cases) and compiler-version/compile/execute receipts. The unchanged historical R02 whole-file fingerprint workflow reports FAIL when the native CPP blob changes; that is not a runtime regression qualification and is not reclassified.

Demo source anchor `22c935c3a3bcebd1fe08bb75ba18727eaabbc9d7`: [integrated 75 CI 39382994571](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994571), [focused CI 39382994501](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994501) and [managed/aggregate CI 39382994639](https://github.com/night-outlook/hybridclr_demo/actions/runs/39382994639) PASS on macOS and Linux. Official installed Unity SDK execution at this **new** source tuple is **NotRun**; the old 90/90 belongs to the consumed `f09e` source.

## Disposition

Ready for only ONE fresh, source-pinned 16-component source/host/installed SDK syntax Local cycle using `WEB_TO_LOCAL.md` at the final Docs-only demo HEAD. **P1 Incomplete**, **P2 NotIntegrated**, **E0 Blocked/Unavailable**, **E1 BlockedByE0**, **full P3 Incomplete**. Original historical failures/custody and report semantics unchanged. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
