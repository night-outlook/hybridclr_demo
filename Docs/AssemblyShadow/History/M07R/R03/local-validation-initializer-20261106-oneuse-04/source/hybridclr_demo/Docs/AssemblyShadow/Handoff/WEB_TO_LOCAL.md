# Primary Implementation -> Local Validation — CONDITIONAL initializer oneuse-04 (2026-11-06 UTC)

**New single-use authority only.** Original initializer oneuse-01 is BLOCKED,
oneuse-02 is FAIL (including its original failed product seal), and oneuse-03 is
FAIL (13/15 cells Passed, two failed Players, original product seal PASSED).
All three original executions, their native raw evidence and every earlier S/K
checkpoint are immutable. **Do not retry, repair, rename or reseal them.**

This successor addresses `IR-LOCAL-R03-INITIALIZER-03-PRECALLBACK-01`: control
and failure both observed real Commit19/state9, with no `R03_IRW_OnPrepared`
entry, native prepared-state0, ReadPrepared -1 and strict Seal reason1.
The cause of the pre-callback failure is NOT yet known. The VM already retains
the caught initializer exception detail; new test-only code reads that existing
detail into an independent native preopened recovery file. It does **not**
assert a fix to an unobserved IL/metadata/PInvoke defect.

## 1. Authoritative source pins and read order

All four canonical Git roots are under
`/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`, one repository per
directory. The branch for all is `codex/assembly-shadow-r01b-h1`.

| Repository | Required source HEAD |
| --- | --- |
| `night-outlook/hybridclr_demo` | **Exact latest full pushed demo SHA in the closing Primary handoff prompt.** Read it there, then verify local clean HEAD AND live remote. A committed handoff cannot contain its own future Git SHA. Never substitute a prior code-side or Local execution SHA. |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Read in this order:
1. `Docs/AssemblyShadow/README.md` and THIS live `Handoff/WEB_TO_LOCAL.md`.
2. `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/INITIALIZER04_PRECALLBACK_2026-11-06/{DESIGN.md,PLAN.md,PRIMARY_SOURCE_REVIEW.md}`.
3. `Tools/AssemblyShadow/R03IR/run_initializer_local.py`,
   `verify_initializer_trace.py`, `verify_initializer_recovery.py`,
   `PlayerProject/R03InitializerObservation{Player.cs,Writer.cpp}`,
   `PlayerProject/R03InitializerPreparedProbe.cpp`,
   and `NativeDiagnostics/test_initializer_writer_host.py`.
4. Historical Local-owned `Handoff/RETURN_TO_WEB.md` and
   `Handoff/LOCAL_VALIDATION.md`, then
   `History/M07R/R03/local-validation-initializer-20261106-oneuse-03/`
   actual raw, trace, result and original independent seal audit.
   The consumed oneuse-03 handoff is preserved under the new remediation
   document directory; it is NOT the current authority.

The historical original-S checkout must remain separately registered,
detached, clean and unmodified at
`/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`,
commit `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.

## 2. Mandatory exact-source CI (all BEFORE Local execution)

At the **same exact final pushed demo SHA**, require BOTH GitHub Actions
workflows below to have completed successfully, with one macOS15 and one
Ubuntu24.04 job each:

- `.github/workflows/r03-ir-initializer-local-contracts.yml`: real C++11
  observer/writer compilation with test-only VM recovery getter stub;
  strict source, native recovery schema, fixture/PID/phase, project and
  ten-host custody synthetic positive/negative contracts.
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml`: exact
  four-repo source checkout, real complete native 8+2 host CLI and original
  host negative symlinks, full regular bytes and literal link-target custody,
  and strict generic product evidence seal.

Additionally require successful
`.github/workflows/r03-ir-initializer-writer-host.yml` (macOS and Ubuntu,
exact current writer/driver/stub bytes) and
`.github/workflows/r03-ir-player-api.yml` (actual .NET compiled
`R03InitializerObservationPlayer.cs` with current unchanged source blob).
These latter outcomes may be from an earlier exact-source commit ONLY when
all relevant compile inputs/byte identities are explicitly proven unchanged.
Failed/cancelled/skipped/wrong-SHA/wrong-OS mandatory checks are NO-GO.
Host CI is **NOT Unity/IL2CPP/Player evidence**.

## 3. Read-only Local GO/NO-GO

The exact new paths, both REQUIRED absent and physically canonical:

~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261106-oneuse-04
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT=<EXACT final pushed 40-character demo SHA from Primary message>
~~~

Require all four clean owning Git roots, canonical origin and live remote HEAD,
correct macOS Apple Silicon architecture, exact installed Unity2022.3.62f2
IL2CPP/SDK/C++11/.NET toolchain, no conflicting Unity/Bee/Player process,
preservation of all earlier checkpoints and original S, and both distinct
new roots absent/disjoint from old source/evidence. Take **two genuinely new,
separately timed free-space samples** of the actual shared output parent:
BOTH must be >=25.0GiB. Hard20GiB/advisory40GiB remain otherwise fixed;
the below40 but >=25GiB conditional advisory exception applies to THIS
oneuse-04 only. Prior oneuse01/02/03 samples are not transferable.
No cleanup, TMPDIR workaround, symlink volume alias, reused root or retry.

Run the existing actual read-only machine admission before any output write:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" \
 --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Independently confirm HOST_RAW is absent. Any failed/unknown admission,
CI, capacity, source or preservation gate -> **BLOCKED/STOP**, no runner.

## 4. ONE execution of unchanged 15-cell suite after GO

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" \
 --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Only one real ON/Release Unity2022.3.62f2 macOS ARM64 IL2CPP build and
two distinct fresh Player processes (initializer-control and
initializer-failure) are authorized, alongside ten current-native host
components, source/schema host tests, and independent read-only
original-S nine-part/90-cell/59-process/generated-source/Mach-O audits.
Keep the original deterministic Methods DLL hashes/MVIDs, native strict
V1 callback and pinned field/canary predicates, full source/install/build
provenance and host-custody/product-seal logic unchanged.

For EACH Player preserve unmodified:
- request/runId, case, stimulus, exact target SHA/MVID; owned process
  PID/group/exit/argv/timeout and full Player.log, stdout/stderr hashes;
- strict `raw.json` **even when zero bytes**, complete
  `raw.json.native-trace.jsonl` native phase/callback/read/seal
  evidence, and new `raw.json.vm-recovery.json` with the actual
  `nativeRecovery.reason` (or exact missing/rejection);
- native phases 190/191/201/205 (real Commit, state and decision),
  230/231 (real VM recovery getter), 299/300 (native OnPrepared
  callback), 400/401 (pre-pinned field read), 600–620 (Seal reason)
  and 900 (last managed caught stage);
- typed separate recovery/trace parser verdict, independent
  request/fixture/PID/BuildReceipt/executable/source digest joins.

On nonzero exit, semantic verification remains
`NotRun_CommandFailed` even if a native recovery reason is valid.
A diagnostic reason is **NOT** strict V1, native V2 or a Player PASS.
Do not infer that failure19/state9 is the intended module initializer
sentinel without the authenticated actual
`R03IR.InitializerFailure.AfterPublication.V1` reason and true
callback entry/pinned field3/mask15/one callback/unchanged canary.
Healthy control must reach0/state6 with no terminal recovery reason.

Preserve all four intentional host negative symlinks under HOST_RAW,
bind exact literal targets and all regular bytes to the sibling-host
custody manifest/archive inside RUN_ROOT, and independently validate
the unchanged strict product `evidence.tar.gz`, evidence index and
seal receipt (or retain unmodified `SEAL_FAILED.json`).
A product seal PASS does not make failed Players successful.

## 5. Local evidence publication and stop

Publish a NEW additive checkpoint
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-04/`
with current source execution vs evidence-publication SHAs, exact 15-cell
results/first failing reason, authentic full raw/trace/VM recovery, source
and process proofs, host custody, original-S audit, seal, capacity/SDK
admissions and independent before/after custody. Preserve all prior
oneuse-01/02/03 evidence and raw host siblings verbatim. Update Local-owned
`Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`. Commit/push
evidence, verify all four live remote HEADs, and return findings to Primary.
Local may make only immediately verifiable trivial unblockers; no non-trivial
VM/fixture/refactor implementation, no retries or broader milestones.

Both independent High `IR-R03-01/02` remain open, as do captured-generic15,
full native V2/first-failure/general diagnostics, original S complete
compiler/object/link/Player chain, managed shutdown, whole-VM epoch, GC/RSS,
RC1–RC6, P1/P2/E0/E1/P3, performance and full legacy regression.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`, PureInterpreter disabled.
No Human Review Gate self-approval, H2, M08A, X02 or SNAP-01.
