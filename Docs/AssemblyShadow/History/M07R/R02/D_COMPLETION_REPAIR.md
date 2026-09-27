# R02 batch-D completion and native prerequisites

Input authority: `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`, branch `codex/assembly-shadow-r01b-h1`.

## Evidence and limits

Local batch D returned 8 Passed, 3 Failed, 20 Blocked. Both Unity installers exited zero but owned Roslyn completion rejected an identity change after SIGTERM. The old receipts did not retain the rejecting census, so the precise historical change cannot be established. The transaction native probe separately ran before valid generated inputs existed. Preserve D and A/B/C, their complete seals, H1 evidence and the older R01 performance reference. No historical failure is relabeled.

The retained Primary CI source artifact `10931711251` was reauthenticated: ZIP SHA-256 `b94c9346e03f5c7e6122a51207b85b4852313e8823462928ea82f021b0061f67`; 3,103 source files match size, SHA-256 and Git blob identities. Connector comparison from its `fd59bad0...` source to the Local return contains only documentation/evidence changes.

## D-01: stable kernel identity and complete observations

The previous implementation used `ps lstart` and live command text as identity. Apple ps may render `(name)` when process arguments are unavailable and `<defunct>` for zombies. Its E flag represents process exit in progress. These are presentation/lifecycle changes, not sufficient evidence of a new process; neither are they permission to ignore a live identity mismatch.

`process_identity.py` reads Darwin `PROC_PIDTBSDINFO` with argument 1 (include zombies), validates the 136-byte ABI result, and identifies an instance by PID, process group, UID and kernel start seconds/microseconds. Linux host tests use `/proc/<pid>/stat` birth ticks. Permission failures, truncated records, inconsistent groups and unsupported hosts fail closed; no production fallback to ps start text exists.

The v2 supervisor first requires the exact owned Unity Roslyn command. Before each signal it reauthenticates every present owned instance. A previously authorized instance with matching kernel birth may be waited for while the kernel marks it exiting/zombie even if displayed argv changes; it is never called clean until absent and is not signalled in that state. New PIDs, changed birth/group/user, or changed live command text fail. Existing outer command/process-group cleanup and command timeouts remain unchanged. Formal Player timing is not wrapped.

Every census is retained before policy evaluation, including the failing post-signal census, phase, expected/observed identity, and kernel state. Native attachment errors retain the raw owned rows. Census/retention budgets fail explicitly. Compiler file hash, actual command exit, signals, and final absence are still required.

This repairs a concrete portability weakness and the diagnostic gap; it does not prove that a particular unrecorded argv/birth transition caused historical batch D.

Primary references inspected for this bounded repair:
- Apple ps presentation: https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c (getproclline, state, lstarted).
- Darwin ABI and exit flag: https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/proc_info.h (proc_bsdinfo, PROC_FLAG_INEXIT, PROC_PIDTBSDINFO).
- Kernel birth and zombie lookup: https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/proc_info.c (proc_pidbsdinfo and proc_pidinfo argument handling).

## D-02: explicit generated-native dependency

The batch now has 33 required cells. `native-regressions` retains the four independent budget/recovery/index/type-cache scripts. `native-generated-inputs` depends on the current successful candidate build; `native-transaction` depends on that authenticated prerequisite. Missing build prerequisites block the dependent probe without suppressing the independent tests.

The prerequisite runs the existing full installed-runtime verifier, binds the current controlled graph, exact source pins/install receipt, generated UnityVersion.h, current graph's AssemblyA.Contracts.dll, and baselib from the supplied Unity installation. It requires the exact generated macro profile for Unity 2022.3.62f2. The transaction command receives explicit runtime/installed/pins/DLL/baselib paths, not its historical M02 DLL default. All bound files are rechecked before and after; command and integrity failures have separate retained fields through the existing with_recovery helper. No generated header is fabricated or copied from another checkout.

## Validation plan and ownership

Primary local Python tests: 165/165 Passed after the repair (145 existing plus 20 added). Tests cover live kernel identity, real unreaped zombies, Darwin API size/error behavior, display changes during exit, changed live identities/new children, complete failing observations, generated header/profile errors, stale install pins, altered current fixtures, and dependency blocking. The existing real-process cleanup tests still run, including an unrelated session remaining untouched.

The R02 workflow adds a macOS host job for the 32 focused lifecycle/prerequisite tests. It does not install Unity or establish Player correctness. Final CI run identities and results are recorded separately after execution; no pending run is claimed as passed here.

Next Local cycle: use a newly published matched candidate/control pair and a new unused batch root. Independently prepare M00 input in both workspaces with the unchanged frozen hash, build fresh controlled graphs, run eight functional sidecars and four pilot plus forty formal A/B pairs (88 timing processes), all affected regressions, final authorities and complete seals. The kernel adapter must be verified with the user's real Unity compiler; M00 byte equality and the generated transaction native path still require Local execution.

All non-trivial code and diagnostic changes are Primary-owned. Local may resolve tools, run the supplied batch and bounded environment fixes, and return evidence; it must not edit identity policy, source pins, generated header expectations or verifier case sets. H1 remains PassedWithExplicitDeferredRisk. D1/D2 remain open for R02 measurement before H2. R02Accepted=false; mayEnterR03=false.

## Connector prerequisite

Disposable branch `codex/connector-smoke-r02-d-20260927-a92d`, based on this Local return, passed Git-object commit/ref/read-back at `f89683801f8c2b9e9c74f06f237e357fab97b523`. It is transport evidence only and must not be merged. No branch-deletion operation is exposed. The other three repositories are read-only in this repair.
