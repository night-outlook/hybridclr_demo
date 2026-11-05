# R03 IR-R03-02 — remaining Player-witness design

**Phase:** Primary Implementation, not runtime evidence. This design defines
the missing independent producer/observer/verifier split. It does not declare
R03 accepted or reopen K's consumed Local Validation handoff.

## Existing concrete baseline

- The original 15 S DLLs must remain copied from immutable original-S
  publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
  Never regenerate them as replacements or infer binary identity from
  recompiled host fixtures.
- `Tools/AssemblyShadow/R03/PlayerFixtures/TerminalProducerFixtures.cs`
  already emits deterministic additional `Methods.dll` files for
  `captured-generic`, `initializer-failure` and
  `initializer-control`. It is host-only. Generated `R03.Node.Keep`
  and `GenericKeep<T>` each increment private instance `stable`.
  `R03.TerminalWitness.Prepare` performs direct, delegate, generic and
  primitive-read operations, with resulting `stable=3`.
  Initializer failure also raises
  `R03IR.InitializerFailure.AfterPublication.V1` after Prepare.
- K's original Player, native overlay, batch S, and V1 verifier cover
  only `off`, `baseline-owner`, `type-resolution`, and
  `engine-unhandled`. The present V1 `verify_ir` explicitly rejects
  new producer labels. Do not weaken that rule.

## Captured-generic path — distinct fresh Player process

**Goal:** prove that an actually *inflated* generic method from a stable
non-candidate declaring assembly captures a physical `Methods/R03.Node`
baseline type argument, and that the production
`AssemblyShadow::AssertMethodIsActive` path rejects the call.

1. In a new isolated Player source, create a healthy positive control using
   the same AOT method family with a non-candidate type argument. Verify its
   body executes. Bind the positive result and any side effects while state
   is `Committed=6`.
2. After committed publication, obtain an actual closed generic
   `MethodInfo` whose **physical** declaring-method owner is not the
   baseline Methods assembly, but whose class or method generic context
   contains the **physical** candidate baseline type handle for
   `R03.Node`. A managed `Type.GetType` result is not sufficient proof
   of the physical identity after Shadow redirection.
3. Attempt the real engine method-invocation route (e.g. Runtime::Invoke
   through the normal method guard), not a direct call to the synthetic
   `R03_IR_ForceTypeFailure` test export. Require the first terminal
   error `BaselineAlreadyUsed=15`, state `FailedAfterCommit=9`,
   and actual guard detail identifying `CapturedBaselineType`,
   `CapturedArgumentAssembly=Methods` and the genuine captured
   argument context/path. A `BaselineMethodExecution=21` result from
   invoking a physical Methods method is **not** this witness; nor is
   `ReferenceResolutionFailed=13`.
4. Continue using the previously bound active-shadow and AOT positive
   method/delegate identities and native side-effect observers. Prove
   subsequent attempts are rejected without incrementing either counter.
   Preserve the first failure and complete diagnostic bytes.

The AOT closed generic body must remain an actual method in the compiled
Player, not a fabricated `MethodInfo` record or one-off guard call.
The verifier must bind the concrete physical type/owner evidence to the
fresh Player PID, build provenance, source manifests, and first failure.

## Module initializer — separate positive and negative Player processes

**Goal:** one genuine post-publication `<Module>` initializer is executed
during Commit and throws after performing positive side effects.

1. Generate `initializer-control/Methods.dll` and
   `initializer-failure/Methods.dll` in separately hashed, unused
   directories. The generator's Editor layout admission is not native
   Player acceptance.
2. In the control Player, Commit must reach `Committed=6` and return
   `Success=0`. Verify the actual module initializer ran once and
   prepared the direct/delegate/generic counters; do not merely verify
   a generated IL listing.
3. In the failure Player, the production
   `InterpreterAssembly::RunStagedModuleInitializer` is called only
   **after publication** while Commit is in progress. The initializer
   calls `Prepare`, then throws the exact fixture sentinel.
   `CommitTransaction()` must return
   `ModuleInitializerFailed=19` (unless a separately identified
   production error is demonstrated), and the state must become
   `FailedAfterCommit=9`. The native first-failure diagnostic must
   retain the initializer cause. A synthetic state change, an
   `InternalError` or `RuntimeAbiMismatch` may not pass.
4. The existing K native field binder requires `Committed=6` and a
   counter value of 2. It **cannot** observe the initializer's counter
   inside the `Committing=5` window or after failure. Add a distinct,
   test-only native observer bound by a real initializer-execution
   callback while the relevant instance and method/delegate identities
   are still valid; capture and pin the exact object/field provenance.
   Its postterminal read must be allocation-free and must not run
   metadata discovery, managed reflection, generic inflation, a
   class constructor, or managed user code.
5. Verify `stable=3` before the throw and remains 3 after terminal
   attempts. Bind the AOT canary and any prepared method/delegate in
   the same fresh process, and prove rejected postterminal execution
   with stable first recovery. A caught C# exception without an
   independently readable primitive/counter is not sufficient.

Do not reuse the old field/guard JSON slots to silently reinterpret a V1
snapshot as a V2 witness. Use a distinct, explicit wire kind and separately
tested verifier; keep the immutable K raw schema and verifier intact.

## Publication, provenance, and negative controls

For each isolated, new case: expected unused output directory; fresh Player
process/nonce; exact four-repo tuple; source/input files and SHA256; actual
target DLL SHA256/MVID; generator receipt; project source manifest; native
overlay/source SHA256; verified IL2CPP BuildReport; launched executable
identity/PID; raw native snapshot; complete diagnostics or bounded
explicit failure; first and final recovery bytes; non-acceptance status.

All negative controls are independent host inputs, not simulations
masquerading as runtime evidence. Required mutations:

- Relabel an existing type failure to either new stimulus.
- Change code 15↔21 or 15↔13 in the generic case.
- Change initializer code 19↔13 or claim success on the failure fixture.
- Omit a real module-initializer attempt or the prepared side effect.
- Change a pinned field from 3 to 2, or mark the native read unavailable.
- Mutate the postterminal AOT or active shadow side-effect counter.
- Mutate the first recovery while leaving the final state 9.
- Replace fresh run ID, PID, target DLL digest, source digest, build
  receipt, or native overlay digest.
- Clip the original complete diagnostic bytes while retaining a
  synthetic valid-looking JSON prefix.
- Reuse an occupied output root or overwrite historical S/K bytes.

The validator must fail closed on every mutation, plus missing/extra
unsupported fixture modes, and return explicit
`runtimeAcceptance=false`, `R03Accepted=false`, `H2Passed=false`.

## Execution sequence and stop rule

Primary Implementation prepares additive Player sources, native observers,
versioned host verifier, source manifests, test controls, and independent
static review first. Only then may an explicitly scoped fresh Local
Validation request be authored with an exact **new** four-repo tuple and
the actual unconsumed case list. Do not alter K or silently rerun S.
IR-R03-01 original-S source/build/runtime provenance is a separate open High
finding and remains a prerequisite for overall R03 qualification.

If any native behavior differs from the proposed generic or initializer
failure code, preserve its actual output and return to Primary for
investigation; never adjust a verifier to accept a failure merely to
obtain a Passed result.
