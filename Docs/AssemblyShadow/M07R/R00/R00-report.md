# R00 baseline execution

Status: **Not accepted — baseline execution found an intermittent Player shutdown failure.** R01 has not started. H1–H5 have not been reached; M12 still requires an explicit human start.

This is an execution record, not a revision of the accepted M00–M07 history. The original review and every historical receipt remain unchanged.

## Scope and changes

- Created four sibling integration worktrees under `/Users/ah/GitHub/hybridclr/assembly_shadow_r00`, all on `codex/assembly-shadow-r00`.
- Retained the original M07 branch/checkouts, their outputs, and their unrelated `.DS_Store` files. The original `main` demo and its local changes were not used as build inputs.
- Changed only the integration demo source pin to the actual reviewed commit `73161474f5b681b46c25424f4e72b4b757c51e66`. The three native/package revisions are unchanged. The complete old-source-to-review delta is recorded separately; it contains documentation and pin metadata only.
- Added repository/Unity inventory, ASR-001–013 confirmation tasks, snapshot sizing, execution evidence, and this status report. No runtime, Editor package, test implementation, or historical evidence was changed.
- Installed the real pinned runtime twice in the isolated project. Restored only settings/scene changes made by this run's `M07Build.Configure`, after its Editor exited. Those transient bytes and their restoration hashes are retained.

## Source and evidence boundaries

`baseline-inventory.json` distinguishes review HEAD, declared closeout executable source, captured Player source pins, pin-only commit, current integration source pin, and original working-copy state. `historical-to-review-source-delta.json` records the actual Git delta.

Current native/package pairing:

| Repository | Revision |
| --- | --- |
| hybridclr | `a19db144751f4f016769b90e61a80b8c27578678` |
| hybridclr_unity | `2180b99daf39095cd76301da2bdf34ac945ee8b4` |
| il2cpp_plus | `666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8` |

The fresh M07 replay executes the existing `M07-Baseline-v6` Players. It is not a rebuilt R00 Player. Their captured fixture provenance names package `8c94f178646e71c9020dc8b66cf3c38632e9cc6d` and demo `9f322a948981341321f0eeb40cc5aa006a094bae`; the later M07 report lists package `2180b99…` and demo `3aab779…`. The captured RuntimeAbiHash is `a41a8261e5fdbade351943b118d153c6f75e39595709b281c11c230427305015`; recomputing the current source-pin contract yields `6f27487799c4e398e6e60dceae734ccf59c4dc871bbd55754c2034d2037ae8de`. These identities are preserved and must not be relabelled as identical. `provenance-reconciliation.json` records R00-OBS-002: the captured-to-declared delta includes 43 demo files and two package files. The final gate constants and later pin-only commit do not prove the earlier captured working-tree bytes equal the declared source commits. A fresh current-pairing baseline is required.

## Fresh validation

| Check | Result and boundary |
| --- | --- |
| Python suite | 356 passed, zero skips, with preserved real compiler DLLs and the actual raw-admission configuration. |
| Unity Editor suite | 912 passed, zero failures/skips, Unity 2022.3.62f2, StandaloneOSX ARM64. |
| Pinned installation | Two identical installs, 942 files; complete installed-source verification passed with Shadow ON and demo source verification enabled. |
| Native targeted suites | All five passed. M03: 92,659 identity checks plus name/facade/OFF checks; visibility: 18,674; M04: 53 checks; M05: 870 checks; M06: 824 checks. Detailed syntax counts and adapter limits are in `validation-summary.json`. |
| Source algorithms | Capacity buckets and the cross-version graph pseudo-cycle recomputed. This is source-derived calculation, not native capacity/Player validation. |
| M07 initial fresh matrix | Modes 1–12 passed. Mode 13 wrote all 21 successful checks, then exited with SIGSEGV. Runner stopped before mode 14. **Failed.** |
| M07 strict verifier | Rejected incomplete initial process coverage. No incomplete/skip override was used. |
| Additional diagnosis | Four owned P05 LLDB replays exited zero; three used normal ASLR. Separately launched NativeOff mode 14 passed. These do not erase the failed matrix. |
| Artifact integrity | All 16,792 recorded M07 input hashes match the accepted launch and remain unchanged across the failed and diagnostic runs. |

The first isolated Python/Editor runs lacked frozen historical inputs and the ARM64 Editor configuration. Their failures are retained. Provisioning real frozen inputs, using the correct raw-admission path, and running the existing configuration entry point resolved those setup failures; assertions and expected results were not changed. The M04 native runner similarly required an explicit real DLL fixture in this clean checkout.

## New observed failure

`R00-OBS-001`: process 442, `T07-13-P05-Rebuilt`, produced `result=Passed`, all 21 checks, and zero selected-closure baseline uses, then crashed during process shutdown. The exit code is `-11`; acceptance still fails.

The OS crash report places the failing GC finalizer in:

```text
PhysicsModule::GetDefaultPhysicsSceneHandle
  -> UnityScene::~UnityScene
  -> LoadSceneOperation::~LoadSceneOperation
  -> AsyncOperationBindings::InternalDestroy
  -> UnityEngine.AsyncOperation.Finalize
```

At the same time, the main thread was executing `DoQuit -> PlayerCleanup -> CleanupEngine -> CleanupAllObjects -> AudioManager/FMOD shutdown`. The GC implementation and `Runtime::Shutdown` match the installed Unity upstream source. An engine cleanup/finalizer lifetime race is the leading explanation; exact destruction ordering and Assembly Shadow's necessity as a trigger remain unproven. No ASR pending risk has been reclassified as a confirmed cause.

A pre-quit GC drain is only a mitigation hypothesis. It was not applied. A durable correction needs evidence from a minimal stock-IL2CPP async-scene shutdown reproduction and a demonstrated lifetime/ordering contract. Never suppress the process-exit requirement or accept the Passed JSON alone.

## Capacity and support scope

The observed demo has five candidates. P01/P04/P05 replace one assembly, P02 replaces three, and P03 replaces five. Captured patch DLLs are 24,064–36,352 bytes. Captured first staged snapshots show zero visible ordinary Interpreter assemblies; this is not a remaining allocator-budget query and does not prove absence of retained hidden allocations.

Production snapshots and maximum cumulative closure were not supplied. The 100/300/1000 small-assembly tiers are test requirements, not support declarations. The 1000 tier exceeds the existing source-derived fresh small-image upper bound of 338; R01 must resolve the target profile and trigger R01B when required. AddManaged/AddUnityTypes/Remove remain undecided product scope and independently gated X01 capabilities. Windows/Android remain NotRun, scheduled for M10.

## Remaining R00 acceptance work

1. Resolve the observed shutdown failure or establish an explicitly reviewed support disposition, then rerun a complete matrix with zero unexpected process exits and strict verification.
2. Build a new current-pairing Player following the completed provenance reconciliation; the captured contract differs. Do not rewrite old receipts to match new pins.
3. Add and execute the requested unmodified-runtime performance observation harness: ON/no patch, P01/P03, first-call versus warm allocation/Invoke/generic timings, business readiness, and at least 10,000 successful repeated allocations. Existing M05 tests measure type lookup; M06 measures a small number of calls. Neither satisfies this requirement. Native diagnostics lack proof-build/row-scan/allocation counters; unavailable measurements must remain explicit.
4. Replay relevant M05/M06 Player allocation, reflection, Runtime::Invoke and generic cases against the required executable boundary. Historical results remain retained, not counted as fresh R00 passes.
5. Complete the stage's independent review and resolve its acceptance findings before R01.

## Gate and rollback

R00 is **not complete**, R01 is **not allowed**, and no human gate has passed. The user's H1–H5/+1 rules remain unchanged. Stage-level agent review cannot authorize passage through any human gate.

Rollback is to stop using the isolated integration worktrees and retain this failed-run evidence. No cleanup of original repositories, baseline resources, Players, or M00–M07 evidence is needed or authorized by this record.

## Independent checkpoint review

The first read-only review of `7316147..c1d1f1b` rejected checkpoint integrity for two P2 documentation errors: the inventory implied that the historical Player was bound to the later declared demo commit, and the report understated M05 native checks. Both were corrected: the inventory now separates captured and declared source identities, and M05 is recorded as 616 core + 35 reflection + 219 image-identity = 870 checks, plus 34 syntax checks. A focused re-review is recorded in `code-review.json`. This does not close the separate R00 acceptance gaps or authorize R01.
