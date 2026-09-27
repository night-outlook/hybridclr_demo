# R02 Local Validation task sheet — batch-D successor

Protocol: `R02LocalBatch-v1`; 33 required cells. This is the published successor to Local return `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`, not a relabeling or retry of D.

## Entry

Read the canonical README and live WEB_TO_LOCAL, then `D_COMPLETION_REPAIR.md`, `PRIMARY_VALIDATION.md` and `source-targets.json`. Candidate source anchor is `57a9470bf299af60f88112998c8326c4c013204a`; use the final Primary prompt's exact candidate transport HEAD. Control is `a379f0b809a5d8af967df06fc83271d90fd84f4c` on `codex/r02-h1-runtime-control`.

Both roles require four correctly identified clean owning checkouts at the exact paths/heads in the handoff. Candidate/control executable graphs must match. Control uses H1 IL2CPP; candidate uses R02 IL2CPP. Preserve unrelated worktrees and the separate historical R01 reference. Do not copy generated files across roles.

Confirm macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, a .NET SDK supporting net8.0 and clang++. Close Unity in both workspaces. At least 30 GiB free is required, not guaranteed sufficient for all archives. Never delete historical evidence to satisfy the check.

Set CANDIDATE and CONTROL to the exact approved demo paths; set CANDIDATE_HEAD from the final prompt, CONTROL_HEAD to `a379f0b809a5d8af967df06fc83271d90fd84f4c`, UNITY/PWSH to actual absolute executables, and OUTPUT to a new unused direct child of candidate `_temp/AssemblyShadow/`. These are explicit execution inputs, not inferred source identities.

```sh
export TMPDIR=/private/tmp
export PYTHONDONTWRITEBYTECODE=1
python3 "$CANDIDATE/Tools/AssemblyShadow/R02/run_local.py" \
  --candidate "$CANDIDATE" --candidate-head "$CANDIDATE_HEAD" \
  --control "$CONTROL" --control-head "$CONTROL_HEAD" \
  --unity "$UNITY" --pwsh "$PWSH" --output "$OUTPUT"
```

This prints the plan. After checking it against the handoff, run the identical command with `--execute` once. Use a new root, not A/B/C/D. No automatic semantic retry or increased timeout is authorized.

## Batch coverage and dependencies

| Group | Required evidence |
| --- | --- |
| Authority/host | Exact eight source/ref identities, clean inputs, common graph, source-to-transport metadata-only delta; all host Primary checks |
| Builds | Fresh candidate/control installed runtime, independent fixed M00 compilation/authentication, controlled ON/OFF graphs and source/build/restoration receipts |
| Functional | Eight role/mode combinations; physical identities, constructor markers/checksums, 1/10/10000 cases, 100/1000 types and four joined workers |
| Formal performance | Four pilot plus forty formal pairs, 88 fresh processes, 10 formal pairs per mode, balanced AB/BA, no overlap, strict R00 reconstruction and no sidecar during timing |
| Independent native | Four budget/recovery/index/type-cache scripts, still available if controlled builds fail |
| Generated native prerequisite | Depends on candidate-build; full installed-runtime verification plus exact generated UnityVersion.h, current graph DLL, source/install pins and explicit Unity baselib |
| Transaction native | Depends on generated-native prerequisite; explicit current inputs, pre/post byte rechecks, original failure and integrity-check failure retained independently |
| Other regressions | Editor, M07, startup11, failure/publication/recovery, fresh count132, diagnostic, lazy/dense, ordinary/mixed capacity |
| Retention | Final source checks, all selected input bytes and complete launch/raw chains, failed attempts and content-addressed seal |

A failed candidate-build blocks generated-native and transaction cells. A failing generated-input check records Failed with available bindings; its dependent transaction cell is Blocked. Independent valid cells may proceed. Do not synthesize a Unity header or fall back to the historical M02 DLL.

## Process-completion observations

Retain `commands/*-unity-completion.json` using policy `R02OwnedUnityRoslyn-v2`: initial identities, every post-signal census, kernel birth/PID/group/UID, lifecycle state, phase, exact expected/observed mismatch, compiler binding, actual command exit and signal actions. A same-instance exiting process is wait-only, never clean while present. Unknown/new instances and changed live commands fail. The outer no-survivor rule remains mandatory.

macOS CI used real process/zombie tests, not the user's Unity installation. Actual installer, M00 compilation and long M07 Roslyn completion are still acceptance inputs for this cycle. A remaining rejection must return its census, not merely the final error string.

## Failure, recovery and evidence

Never turn a nonzero result, cleanup failure, wrong hash or incomplete provenance into success because the command printed Passed. Preserve command stdout/stderr, completion records, build and restoration errors separately. Unexpected source changes must be retained and returned, not automatically reset. Independent cells run only with valid source/workspace authority.

M00 expected SHA-256 remains `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`; retain compiler output and preparation receipts on mismatch. Missing capacity corpus bytes are an input-availability limitation, not permission to reuse old execution PASS.

Keep `native-generated-inputs.json`, `native-transaction-integrity.json`, transaction results, ordinary-input records, controlled graphs, launch/raw/verifier chains, sidecars, paired analysis, generated-input recovery and all partial attempts. `LOCAL_BATCH_RESULT.json` binds the seal/index/archive. Retain indexed generated roots outside the batch directory as well. Preserve prior A/B/C/D and H1 evidence.

## Return and review boundary

D1/D2 require measured current H1-runtime control versus R02 CPU/RSS disposition before H2. Distinguish cold/warm, distributions/sample counts, native allocation requests, owned storage, managed memory, RSS and lifetime peak. A passing unit test or faster readiness does not close these risks.

If every required cell succeeds and complete evidence is available, commission the genuinely independent R02 stage reviewer using the fixed committed source/evidence inputs and retain its verbatim verdict. This does not approve H2 or authorize R03.

Update and push LOCAL_VALIDATION.md with actual Passed/Failed/Blocked/NotRun/Unavailable classifications. Non-trivial issues go in RETURN_TO_WEB.md with exact commands, source/build tuple, first failing input or process observation and complete retained evidence. No non-trivial source changes are assigned to Local. R02Accepted=false and mayEnterR03=false until subsequent explicit disposition.
