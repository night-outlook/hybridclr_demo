# P1 command-failure receipts and fail-stop batch design

## Status and scope

**Implemented as an unpublished candidate. Publication is blocked because this session's GitHub connector exposes read actions only.** This is a tooling increment within R03/P1, not completion of the production integration program and not a Local execution authorization.

Base branch: `codex/assembly-shadow-r01b-h1` in all four repositories.

| Repository | Documented Local checkout | Verified remote **base**, not this delivery |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `d49b85bfd633f25b9f8351e03efd406c6f1df53b` |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `5667e3712f49e4b38c7dd7359e57f81e344626da` |


Primary source mirrors used here are `/mnt/data/assembly-shadow-primary/base/<repo>` and `/mnt/data/assembly-shadow-primary/work/<repo>`. They are not Git checkouts. Exact fetched originals were authenticated by their Git blob hashes before editing. The Local paths above are recorded project paths, not paths inspected on this host.

## Evidence and defect

The native live-general runner writes command streams and receipts only after `subprocess.run` returns. A timeout raises first, so captured bytes in `TimeoutExpired` are discarded and no native command receipt is appended. The outer source/SDK wrapper likewise records only the exception and then continues executing later scheduled components. Timeout or interruption does not establish that detached descendant processes have stopped.

Primary independently reproduced both behaviors using exact, Git-blob-authenticated baseline Python source and a controlled Python child which flushes distinct stdout/stderr bytes before sleeping. The native call retained zero receipts/files even though the exception contained both prefixes. The actual outer `execute` function, extracted from its source AST, returned after the timeout and reached a subsequent-work marker. The reproduction does not claim that a live Unity/compiler descendant was observed or that a product runtime defect was reproduced.

The nonmanaged component consumer also used an ordinary JSON parse followed by a second read for hashing. It accepted duplicate keys and non-finite JSON constants and did not reject symlink-redirection paths. This increment rejects those inputs and parses/hashes one byte buffer. It is not an adversarial filesystem transaction or a replacement for each component's semantic verifier.

## Selected behavior

A normal completed child retains its actual exit status and complete captured direct-child streams. A timeout retains the exact bytes exposed by the exception as `CapturedPrefix`, including availability flags to distinguish missing capture from genuinely empty output. An interruption or unknown execution outcome records unavailable streams as unavailable, never an invented empty successful transcript. Unknown exit status is JSON null, not a fabricated signal/exit code. Diagnostic files contain exact binary bytes with SHA-256 and captured-byte counts.

A witnessed timeout, interruption, unknown execution outcome, or child-reported `commandLifetimeUnverified=true` causes the outer batch to stop launching subsequent components. Every remaining planned cell is written as `NotRun` with `commandInvoked=false`; no corresponding component root is created. Postflight Git subprocesses are not launched in this state. The aggregate remains FailedOrIncomplete, source preservation is not asserted, and the observation inventory is labeled UnsealedObservedFiles. Cancellation exits 130 after feasible receipt persistence. A completed ordinary nonzero child, failed semantic receipt, or known executable-not-found launch failure remains Failed but does not prohibit independently useful later checks.

`commandInvoked` describes an attempted wrapper invocation, not proof of a successfully spawned OS process. Absence of a witnessed lifetime failure is not a proof of descendant quiescence: `descendantQuiescenceProven=false` is explicit even on normal completion.

The native runner now retains failure receipts in `finally`, propagates failure, emits a failed RESULT for a missing compiler, and preserves RESULT even when postflight source hashing fails. `compiledExactProductionSource` and `compiledActualBoundedSourcesAndSerializer` are true only after both compile commands actually report success. Prepared source text alone is not compilation evidence. Observed source hash equality is recorded separately from source preservation.

## Alternatives and boundary

Merely adding timeout logs without stopping the batch leaves later SDK work potentially overlapping an unverified child lifetime. Converting every failure into a stop would unnecessarily sacrifice independent results from ordinary completed failures. Both alternatives are rejected.

Introducing a new outer process group does not prove control over existing SDK-owned child sessions. Replacing the established SDK command-lifetime policy or killing globally discovered compiler processes would broaden this change's ownership/risk scope. This increment deliberately leaves `command_lifetime.py`, compiler environments, native/managed compiler commands, and all timeout values unchanged. It performs no broad process cleanup or automatic retry. A separate Primary design is still required for complete nested-session supervision and bounded termination guarantees.

Filesystem capacity and write failures can prevent durable receipts; no implementation can guarantee successful writes to unavailable storage. The current capture still depends on `subprocess.run` returning/raising; this change does not fix an indefinitely held descendant pipe or establish a whole-process-tree deadline. Path validation addresses completed private component outputs, not an adversarial check/open race. These limits must not be hidden by an acceptance flag.

## Consolidated verification

The first component of the prepared Local batch is `command-failures`: the new source-bound harness runs 53 unittest methods: 5 existing CLI checks, 14 existing managed receipt/aggregate checks, 24 outer failure/strict-receipt checks, and 10 native-runner command checks. Tests use real controlled Python children where indicated; Git, Unity SDK, VM and C++ compiler operations in orchestration fixtures remain mocked. The harness binds all nine participating source/test files, unique test IDs, counts, logs, before/after digests, and scope flags. It rejects altered test counts, skips, expected failures, duplicate IDs, alternate receipt source overrides, and noncanonical/reused/source-contained output paths.

These 53 tests augment, not replace, the original 12 components. The full prepared batch is 13 components, with the native live source's existing 13 C++ case groups/profile, five managed products and exact expected-negative control, and all 75 official native SDK syntax configurations unchanged. Source and compiler policies and historical `source-pins.json` are not rewritten.

## Production/acceptance exclusions

No C++, C#, serializer, VM guard, original getter, Player API, managed/native compiler helper, transport budget, reporting threshold, or historical evidence file changes in this increment. In particular, the first-error/GC/canary/recovery predicates and the uncapped 500ms / 1–64 native report requirement stay fixed.

P1 coherent VM-wide epoch/ABA protection, class-pointer provenance, complete execution/R02 capture, original live getter integration, worst-case allocation/GC/RSS, and true lock/Shutdown safety remain incomplete. P2 authenticated native/C# V2 transport/semantic integration remains NotIntegrated. E0 supported Unity2022.3.62f2 StandaloneOSX engine-owner safe point remains Blocked/Unavailable; E1 is BlockedByE0. Full P3 linked Player/runtime acceptance remains incomplete. These are Primary-owned work, not a Local implementation assignment.

The latest `20261018-5667` Local source/host/SDK PASS is consumed. The `20261016-3dc9`, `20261016-f598`, and `20261016-0620` source/SDK PASS cycles and `20261016-0a0b` FAIL remain unchanged. SNAP-01/N/M/K/I/E FAIL, historical R02 source-fingerprint FAIL, original strict S custody Blocked, and independent full-stage R03 FAIL/re-review NotRun are not reclassified.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion remains disabled.
