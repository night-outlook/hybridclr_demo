# R03 P1 — bounded Git source-authority postflight receipts

## Authority and finding (immutable)

The latest Local-owned `20261021-82dd`, [LOCAL_VALIDATION](../../../../../Handoff/LOCAL_VALIDATION.md) then [RETURN_TO_WEB](../../../../../Handoff/RETURN_TO_WEB.md), and `local-validation-p1-vm-shape-json-20261021-82dd/` checkpoint are the **sole factual authority** for this repair. Actual executed tuple: demo `bf4ebab005d008e7d936e4c9b17f62d06afcd37c`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`.

Finding **`IR-LOCAL-P1-VM-SHAPE-JSON-POSTFLIGHT-01`**: one core invocation; all **24/24** children actually Passed, original 85 failure tests, seven group inventories, five genuinely compiled managed positives plus the exact `OriginalUnsignedCounts` expected-negative and **100/100** native Apple arm64 C++17 installed SDK syntax commands Passed. The original aggregate is nonetheless **`FailedOrIncomplete`**, exit 1, `sourcePreserved=false`, `fourRepositoriesAfter=[]`, because final `git -C .../hybridclr ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1` exceeded the **unchanged 120-second timeout**. The former runner discarded the successful pre-timeout postflight repo receipts and did not retain per-postflight Git argv/start/end/streams/PID/exit/timeout. Actual source mutation and transport cause are **Unavailable**, not disproven or proved by the subsequent independent audit.

The independent factual preservation audit passed for installed SDK, source bytes and history, and subsequent read-only Git checks passed, but **cannot promote or rewrite the original raw aggregate**. The entire `82dd` raw/scratch/audit/checkpoint set is consumed and must never be retried, relabeled, or modified. Original R02 fingerprint FAIL, strict S custody Blocked, independent R03 full-stage FAIL/re-review NotRun and all acceptance booleans false remain unchanged.

## Narrow change and runtime model

Scope is **ONLY** the Primary-owned Python preflight `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py` and direct 85-leaf host test contracts. **No production native, HybridCLR, Unity SDK, managed API, V1/V2 wire format, Player or original source pin change**.

Introduce `GitPostflightProbe` for the **final** existing four-repo `verify_repo` loop only. Initial admission remains the original unmodified `verify_repo(base,name,sha)`. Optional explicit `git_probe=...` wraps the original per-checkout `git remote get-url origin`, `git branch --show-current`, `git rev-parse HEAD`, `git status --porcelain`, and `git ls-remote origin refs/heads/<branch>`. Preserve identical process argv, source/remote identity, branch/clean/HEAD validations, execution order, existing inherited environment, authentication transport, and **120-second timeout**. **No retries**, credentials overrides, Git SSH configuration, alternate GitHub API fallback, timeout increase, source authority relaxation, or returning cached `git ls-remote` success.

For each actually invoked final Git direct child, create one unique run-local directory `postflight-git/<repository>/<ordinal>-<operation>/` with:
- `START.json` before invocation: exact argv, repo, ordinal, 120-second limit, start Unix time, schema/type and `descendantQuiescenceProven=false`.
- `RESULT.json` after completion/error: actual exit (nullable), status `Completed`, `CompletedNonzero`, `TimedOut`, `Interrupted`, `LaunchFailed` or `UnknownExecutionError`, start/end/monotonic duration, typed exception if available, unknown-lifetime flag, and stream completeness.
- `stdout.bin` and `stderr.bin` retaining **up to the first 65,536 bytes each** of captured direct-child output; explicit available/missing, actual captured byte counts, stored-prefix counts, total captured SHA-256, stored-prefix SHA-256 and truncation flags. No invented full streams, child PID or descendants/SSH sessions. Recorded files are enumerated by the existing aggregate manifest.

A `subprocess.TimeoutExpired` retains available direct stdout/stderr prefixes, `exit=null`, `commandLifetimeUnverified=true`, and `descendantQuiescenceProven=false`. A completed nonzero exit remains distinct with known direct child lifetime; a launch `OSError` remains distinct from a process that may have started. Even if the Python parent directly killed/reaped `git`, inherited SSH descendants are **not independently shown quiescent**. When no command executed due to prior child unknown lifetime, no postflight directory is fabricated.

The authoritative four-repo postflight still verifies **all four** before `sourcePreserved` is true. Instead of a destructive list comprehension that discarded partial earlier results on a later error, an explicit loop appends only each fully verified repository to `fourRepositoriesAfter`. This is **partial information only**: a list shorter than four always keeps `sourcePreserved=false`, `postflightError` non-null, aggregate `FailedOrIncomplete`. On a timed-out Git authority process, aggregate `commandLifetimeUnverified=true` and manifest `inventoryScope=UnsealedObservedFiles`, while all 24 original child states and their actual SDK compiler evidence are still retained. The new top-level `postflightGitDiagnostics` summarizes command count, completed-repository names/count, timeout and completed-nonzero count, 120-second contract, fixed stream-prefix cap, whether direct Git receipts are present, no-retry, transport-cause-unknown, and no descendant-quiescence proof.

No detached-process kill/wait policy is changed and no additional postflight Git command or retry is scheduled. A complete known nonzero command keeps overall `FAIL` even when no process lifetime uncertainty exists. `KeyboardInterrupt` after the last child still produces an interrupted/FAIL aggregate and exit 130 rather than manufacturing a PASS.

## Regression evidence / strict result contract

Keep all **85** original test IDs and module counts **5+14+44+10+12**. Inside existing Python discovery leaves, source-bound controlled mocks verify:
- Exact five genuine `verify_repo` operation paths feed bounded direct `GitPostflightProbe` receipts with an expected clean HEAD, byte/hash consistency, 120-second timeout and no fake SSH/Player execution;
- A mocked timed-out `ls-remote` returns complete available prefixes with null exit, `TimedOut`, unknown lifetime, no extra Git retry, no descendant quiescence and accurate SHA-256;
- A completed nonzero command is not mislabeled a timeout or success;
- The full 24/24 Passed mocked-component batch with a timed-out *second* postflight repository remains aggregate `FailedOrIncomplete` and retains **only one** fully verified earlier repo, partial timed-out Git streams, `sourcePreserved=false`, `postflightError` and unsealed manifest; no acceptance booleans flip;
- The old known postflight failure, normal 24/24 mock success, earliest child fail-stop/NotRun/unknown-lifetime and every managed/SDK mock receipt contract continue. Mocked Git results explicitly yield **zero** real Git direct receipts; they do not masquerade as live Git/SSH evidence.
- macOS temporary-dir canonicalization uses `Path(td).resolve()` because `/var` may resolve under `/private/var`; Linux and macOS use the exact same strict original `verify_repo` guard.

CI: source-bound integrated 85-test, focused controlled failure, and managed aggregate on macOS/Linux. Initial corrected-source macOS failure in the new fixture was a **test path canonicalization issue**, and its failed CI remains factual. Only subsequent fixed test CI may be reported Passed.

## Local run, rollback and excluded acceptance

After Primary commits/tests/docs exact four GitHub pins and a fresh handoff, the Local agent may perform **ONE** new 24-component source/host/**official installed Unity2022.3.62f2 SDK syntax-only** batch under four **fresh absent/canonical/disjoint** raw/scratch/audit/checkpoint roots. Before creating roots, independently authenticate all consumed evidence including `82dd`, original SDK, original source pins and negative symlinks. A transport timeout may still occur: that new aggregate must remain `FAIL`, but now with bound per-command evidence; do not retry or raise timeout.

Rollback is a reviewed new commit reversing only the Python postflight recorder and its direct tests/docs. Do not rewrite `82dd` evidence. No Editor/Test Runner/Player, product-native link, process GC/RSS/metadata Shutdown, canonical execution TypeKey or original getter activation is permitted.

**P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete.** Original strict S custody Blocked, SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, independent full-stage R03 FAIL/re-review NotRun, and `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false` persist. PureInterpreter disabled.
