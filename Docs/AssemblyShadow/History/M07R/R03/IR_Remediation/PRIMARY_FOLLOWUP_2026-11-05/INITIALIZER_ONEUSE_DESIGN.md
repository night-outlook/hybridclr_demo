# R03 IR-R03-02 initializer one-use Local cycle — design

Date: 2026-11-05 UTC. Owner: Primary Implementation. Branch: `codex/assembly-shadow-r01b-h1`.

## Decision and scope

Create one **new**, independently admitted source-bound Local Validation cycle
`R03IR-Initializer-20261105-oneuse-01`. The prior A–K cycles and all October 8
independent findings are immutable. The user authorized preparing a new Local
Validation batch; this is not approval of R03, a Human Review Gate, another
milestone or unrestricted Unity execution.

The earlier source-only initializer producer, observer and V1 writer exist.
This cycle builds their **actual composite native overlay** into one fresh
Unity 2022.3.62f2 macOS ARM64 IL2CPP feature-ON Release Player, and runs
two distinct processes: `initializer-control` (Commit 0, state 6) and
`initializer-failure` (Commit 19, state 9). The fixture generator produces
the separately hashed Methods.dll for each process. Actual callback counts,
prepared primitive field and post-failure canary are read by the native
preopened writer, not invented by a host verifier. Each Player gets its own
request, raw file, command receipt, OS PID and log.

This is explicitly an **initializer diagnostic V1**, not native
`NativePreopenedSnapshotV2` or a complete post-terminal recovery/diagnostic
record. It can establish that the two distinct real native initializer
outcomes and a physical prepared-field invariant occurred in fresh Players,
subject to independent Local source/build/process verification. It cannot
by itself close High IR-R03-02 or change the independent R03 FAIL.

## Build and source architecture

- `run_initializer_local.py` extends `CurrentNativeBatch`, preserving the
  original K five-Player source, original S, source pins and native runtime.
- It first validates the four owning Git repositories, exact active branch
  and remote commits, the native 11-file source inventory and 45-file VM
  delta, a clean immutable original-S checkout, macOS host/Unity admission,
  and an unused external output root.
- A targeted Git HEAD byte check covers the seven new native/managed/test
  inputs; the existing source gate checks the historical eleven. The copied
  Unity project has an explicit `source-inputs.json`.
- The previously published fifteen **original S** fixture DLLs are staged
  under original publication authority; the separate opt-in generator
  produces exactly two new, deterministic native initializer target DLLs.
  Original S/K fixtures are never regenerated as authority.
- `prepare_ir` copies the existing terminal Player and frame dispatcher;
  `prepare_initializer_sources` appends the observer and writer to the
  exact original native overlay and adds one initializer Player C# source
  to the isolated project. It rejects built/reused projects and stale
  configurations. No native/product repository is edited by this overlay.
- The inherited `Batch.verify_build` rejects any overlay other than K's
  historical original. The new runner therefore supplies a dedicated
  **full** real-build verification: BuildReport Succeeded, errors zero,
  native feature ON/diagnostics 2, exact composite overlay SHA in config,
  build receipt, and installed native VM file; actual managed file digests,
  source-install provenance, Player inventory and ARM64 executable.
  Do not weaken the historical verifier to make the new build pass.
- The same fresh app hosts the two sequential distinct process requests.
  Failing an initializer process never causes an automatic retry.

## Local batch graph

Independent read-only original-S stages run in this same batch:
full nine-part archive/90-cell authentication, 59 historical source/process
identity joins, the four generated
registration-source occurrence scan, and the original two archived
GameAssembly Mach-O symbol-registration identity check. These stages
observe **historical** original S and cannot prove source-to-object/link/
executed-Player compiler closure. Their result cannot replace the new
native initializer Player evidence.

Before Unity, execute all ten **actual** existing current-native C++11
host components, plus the new C++11 initializer observer/writer suites
and source/preparation/schema/verifier negative tests. The Local process
has 15 fixed cells: entry authority, host, original archive, archived
59-process joins, two original binary/source audits, original fixtures, generator, new targets, original
IR preparation, new initializer preparation, one build, two Players and
final authority. Original-S archival failures do not suppress independent
initializer preparation; initializer build requires only passed source,
native-host and fixture prerequisites. The overall result remains
ReturnRequired if **any** required cell fails or the evidence seal fails.

The `R03IRInitializerOneUseEvidenceBatchV1` sealed summary is deliberately
non-authorizing. It records one planned fresh build/two planned Players,
actual pass counts, original-S scopes and explicit missing evidence.

## Evidence requirements and adversarial checks

Every new Player request binds runId, caseId, stimulus, fixture digest,
and preexisting compiled bundle. The native record must have exact V1 schema,
matching process PID, control/failure return and final state, **one**
native callback, direct/delegate/generic pre-positive mask 15, prepared and
final pinned field 3, post-failure attempted AOT call with no side effect,
and all acceptance flags false. Duplicate/missing/extra JSON keys, wrong
native transport, wrong PID, wrong DLL, canary advance, accidental
initializer repetition and success-mask substitution are rejected.

The original-S audit is read-only and cannot classify generated-code
compiler inputs, complete native link dependencies, full native include
closure, managed lifecycle shutdown or a coherent whole-VM epoch as Passed.

Host-only tests exercise the actual new Python runner's distinct case
selection and failure receipts, actual native C++11 observer/writer
translation units and negative variants, existing deterministic dnlib
target generation, and managed API compilation. Host tests and GitHub
Actions are NOT real Unity or Player evidence.

## Risks and admission

A real IL2CPP bridge or metadata/layout implementation mismatch, native
symbol collision, or post-Commit C# exception can fail the first new build
or Player; preserve the raw error and return to Primary rather than
making non-trivial Local edits. The fixture's prepublication callback
and postfailure pinned read are additive test-only code; incomplete or
unexpected field evidence fails closed. Finalization may include binary
app files and needs disk headroom. Fixed hard admission is 20 GiB and
ordinary advisory is 40 GiB. For this one one-build/two-Player cycle,
Primary permits a **single-use conditional advisory exception** only if
two independently timed measurements on the actual output parent are
both at least 25.0 GiB; below 25.0 GiB is NO-GO. This exception never
changes the global thresholds or authorizes a different cycle.

## Unfinished work (do not relabel)

Physical captured-generic error-15 execution is NotRun. Complete native
snapshot V2/first-failure/general diagnostic transport is not implemented
by this runner. IR-R03-01 original compiler/source/object/link/Player
chain, original generated-code capture omissions, RC1–RC6, P1/P2/E0/E1/P3,
full managed shutdown, GC/RSS, whole-VM epoch, legacy coverage and
performance qualification remain unresolved. All R03/H2/qualification
flags stay false; PureInterpreter remains disabled. Next review must
be independent and explicitly authorized.
