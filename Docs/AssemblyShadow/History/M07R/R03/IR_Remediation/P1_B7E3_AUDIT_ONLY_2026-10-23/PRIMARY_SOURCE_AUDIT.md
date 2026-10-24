# Primary source and evidence audit — b7e3 isolated historical re-review

## Exact source history and independent scope

Canonical branch: `codex/assembly-shadow-r01b-h1`. Original b7e3 executed source:
`hybridclr_demo@49c6b62d38d7668be10004ac1e5a030d74894f09`,
`hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`,
`hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`,
`il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. The user authorized continuation into a narrowly scoped audit-only follow-up. This is **not** authority to repeat the consumed core25/SDK100/Unity Player or to change the original failed Local result. The canonical current docs/CI remote HEAD is distinct from the original b7e3 source SHA.

The original b7e3 Local-owned result is **FAIL**, despite raw `PassedSourceHostAndSDKOnly` 25/25; the original required auditor failed at line190, and all later assertions were NotRun. The original auditor Git blob `0813c686df363a2f209d73c784c6fb0fac57b221` and one-line successor `908358c1b302d31e3be434e36988c43e65b976cf` are untouched. New distinct historical-audit-only source `audit_historical_only.py` has blob `c451e0cb7794e624eabb9029db0a35ba28d14592` and is **NotRun** against consumed Local external files in the current Primary environment.

## Source review and time-varying Git authority

The original full successor contains a source-authority block at its end which independently calls **live** Git `branch`, `rev-parse HEAD`, `ls-remote origin` and requires current remote HEADs equal the **past** b7e3 source pins. This can no longer hold for the demo because the remote branch advanced through Docs-only commits. Rewinding the branch, changing the recorded old pin or fabricating the current Git output would be inaccurate.

The new historical-only variant preserves all source assertions before `def authority(n)` byte-identically, including the 25 ordered names, original85, SDK/managed/native/physical/shape/metadata-Gate verification and the **full original 20 direct Git postflight START/RESULT/stream checks**. Only the obsolete final current-time Git authority is replaced with a strict historical `GIT_BEFORE.json` reference binding:
- Exact eight original commands/argv per repository, all known exit0, original path/branch/head/clean/remote/snapshot assertions, including 20 subsequent capture-time direct Git proofs earlier in the source.
- Original `fourRepositoriesAfter` exact source tuple preserved; current remote head equivalence explicitly **NotRun**.
- Output is `GIT_HISTORICAL_AUTHORITY_AFTER.json`, never a fabricated fresh `GIT_AFTER.json`.
- Final result is explicitly `PassedHistoricalEvidenceAuditOnly` with `originalB7E3LocalResult='FAIL'`, `liveRemoteHeadCheck='NotRun_TimeVariant'` and `productAcceptance=False`. It is not the original auditor's result, not full R03 acceptance and not runtime proof.

No source changes to the original `run_p1_metadata_local_preflight.py`, native production code, Unity SDK, original 85 tests, old checkpoints or Local reports were made.

## Executed GitHub published snapshot audit (Mac/Linux)

The new `verify_published_checkpoint.py` completed successfully under [GitHub Actions 40053309333](https://github.com/night-outlook/hybridclr_demo/actions/runs/40053309333) on **macos-15 and ubuntu-24.04**. Both jobs independently hashed all **2506 published checkpoint file entries** against the immutable checkpoint manifest, and verified available raw-manifest records; the original raw manifest declares **4269**, of which **2396 are available in the published GitHub copy and 1873 remain absent**. It validated the raw25 status and ordered names, original85 test IDs, admitted9+9, six managed compiler commands (five positives plus one exact expected negative), 101 native direct command receipts (one version +100 syntax), original final20 Git START/RESULT/stdout/stderr and historic FAIL. It wrote a fresh result artifact within each GitHub CI runner, **outside repository source**. The output is `PassedPublishedSnapshotScope_ExternalInputsUnavailable`, specifically **not** an independent full Local PASS.

CI did **not** install/recompile Unity, run the original 1052-line auditor, alter any original file, validate all 2405 vendor SDK bytes or all 1873 missing external raw files. The 2405 / 316062203 SDK report and 22 prior P1 raw/scratch/audit sets, 24 original checkpoints and 88 symlinks are retained Local-owned claims, pending fresh externally independent checks, not Primary live SDK observations.

## Staging/one-shot tool review boundaries

`stage_local_audit_only.py` enforces a fresh canonical absent output root; pins original execution tuple, the current historical auditor Git blob, the complete original 4269-member external manifest, all original 2405 installed SDK files, **all 1925 separately retained SDK scratch files** bound by the immutable `native-sdk/native-sdk-inputs.json` (including duplicate/alias/symlink refusal), and original source bindings. It authenticates the special lossless UTF-8 wrapper of original `preflight/run-once.log` against both the Git checkpoint and original source bytes. It copies only preflight evidence to an isolated new audit workspace, preserving the failed original auditor as a separate file. The staged `audit.py` alone is replaced by the source-pinned historical audit-only variant; the preparer does not invoke it.

`run_local_audit_once.py` refuses any previous marker, records an atomic one-shot invocation before launch and captures original PID, stdout/stderr SHA256, exit and lifetime in the **new isolated root**. It launches only this staged audit Python source, never the original host/core/SDK compiler/Unity application. It fails closed on unknown lifetime and never automatically retries. After its run, the stager's `--verify-after` independently rechecks every external original raw manifest file, the installed SDK, **all 1925 copied SDK scratch files**, original source bindings, and all original preflight files, comparing to the before snapshot. A success outcome may be called **historical audit-only**, never rewritten b7e3 Local PASS.

Potential blockers still require actual Local evidence: historical source versus the current machine source bytes, stored Git blobs, prior batches/negative/symlink checks and every original post-line190 assertion. A new check could legitimately fail. **No assertion may be silently weakened by Local.** Report first failure and evidence to Primary; one attempt consumes new audit-only roots even on failure.

## Acceptance and protected scope

The old b7e3 overall Local FAIL is not reclassified; full P1, R03, runtime and Human Review acceptance remain incomplete or false, PureInterpreter disabled. P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, P3 Incomplete. Original `7896` and `7c2c` scope PASS, `82dd` raw FAIL, `e1e5` and `6c72` PrerequisiteBlocked, b7e3 raw scoped PASS plus original independent auditor FAIL all remain immutable. No protected SNAP-01/H2/X02/M08A or Human Review Gate; no Unity Editor/Player, product native link, actual GC/RSS/Shutdown, canonical TypeKey or pointer-lifetime safety claim.
