# IR-LOCAL-API-01 — current-source compiler evidence; storage remains external

Primary Implementation correction, 2026-10-09 UTC. **The C# source-coverage prerequisite has new passing evidence. Local storage has not been reclaimed, reserved or remeasured by Primary.** The successor B assignment remains conditional on fresh Local admission. This is not independent R03 review or acceptance.

## Original return preserved

Read the immutable Local return at demo `d576ae49261a35565bca9fc0701e835d8d9a87fa`, under `History/M07R/R03/local-validation-20261009-ir-r03-02-preflight-blocked/`, and the unchanged Local-owned handoff documents. Local executed source `fca2fdb035512fc739693641a5fa2126e4254258`; d576 is its evidence publication, not a new runtime execution.

Local correctly reported 64 Python tests and 69 standalone native-policy checks Passed, 15 original S fixtures authenticated, 416,161 custody files unchanged, and **zero Unity launches / 14 cells, 3 builds, 4 Players NotRun**. The previously cited API run `37874183375` compiled an earlier Player body; its current-body classification remains **NoCoverage** in that historical record. No old report or failed storage admission is rewritten by this correction.

## Change and fresh execution

Commit `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b` changes only `.github/workflows/r03-ir-player-api.yml` relative to d576. It adds missing original-Player/source-pin triggers, authenticates every declared tracked C# input plus workflow/project/pins before compilation, and verifies unchanged inputs and actual compiler output afterwards. It retains the real pinned HybridCLR package, existing Unity API stubs, target framework and language settings. **No native guard, Player assertion, fixture, runtime helper, source pin or storage threshold changed.**

[Fresh run 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633), attempt 1, job `113729828150` (`managed-api`), **Passed**. Primary read the real job log, including checkout identities, the compiler command containing `../../R03IR/PlayerProject/R03TerminalPlayer.cs`, compiler output and artifact-upload receipt.

| Binding | Actual value |
| --- | --- |
| Executing demo | `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b` |
| Package | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| Current Player Git blob | `adc798c6c299594d496393c6729c4c6087111b31` |
| Current Player SHA-256 | `22c3e0be7cebc041706b1412c5fc317c806c49a0980be143d5517dc4cc59a7bd` |
| Compiler | .NET SDK 10.0.401, net8.0 target/reference pack 8.0.31, C# 9.0 |
| Configuration | Release; UNITY_EDITOR; checked-in Unity API stubs |
| Result | 0 errors, 13 CS0649 warnings; real build elapsed 11.21 seconds |
| Captured tracked inputs | 22 entries, including 19 explicit C# compilation inputs |

The warnings concern request/native-receipt fields populated through serialization rather than direct assignments. Their runtime population is not proved by this compiler. This is a **current-body C# / real-package signature check**, not compilation against official Unity managed assemblies, not a Unity project build, not an IL2CPP Player, and not whole-program or independent acceptance. Generated SDK inputs and binary logging remain in the separate CI artifact; the tracked input inventory is not a claim of a fully hermetic toolchain.

## Durable evidence and verification

[EVIDENCE.json](EVIDENCE.json) records exact artifact/member identities and limitations. `compile-inputs.json` and `compile-result.json` are exact unmodified artifact members. `build.log.gz.b64` is a lossless encoding of the **entire** 62,753-byte artifact build log, not a selected excerpt. Decode with Python `gzip.decompress(base64.b64decode(path.read_bytes()))`; its SHA-256 must be `a2805d2bf18a7004f5cb1b2197b8fba3f9f1edb4fac6f4ec2fc0d27dc820ae72`. Do not decode over existing evidence.

Artifact `11603880990` is 557,663 bytes, 24 members, ZIP SHA-256 `de434b6e31839908cefd6653cf986e9225767ec6f2c16b694e943c63b5c0df2f`. Primary downloaded it through the Connector and independently matched the ZIP digest, both receipt hashes, the full build-log hash and `PlayerApiCompile.dll` output hash. The artifact expires **2026-10-23T08:12:55Z**. Its binaries and binlog are CI-hosted, not falsely represented as permanent Git members. The input/result receipts and full encoded text log remain in Git.

The 11 synthetic tests in `test_workflow_receipts.py` passed separately, with the exact workflow/script/log hashes in `PRIMARY_SYNTHETIC_CHECKS.json`. They exercise stale pins, dirty/missing/symlinked inputs, changed checkouts and absent outputs, using explicitly synthetic output placeholders. They are **not** C# compile or Player evidence. Reproduce from the demo root with an existing Python/PyYAML environment:

```bash
R03_API_WORKFLOW="$PWD/.github/workflows/r03-ir-player-api.yml" python3 -B \
  Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09/test_workflow_receipts.py
```

Connector bootstrap reverified all four identities/HEADs and read/write permission metadata. The demo Contents-API update smoke commit `25244adab960ff6e75f4130e7690e358443b5503` was remotely read back on `codex/connector-smoke-20261009-primary-owner-6c48`. Previous disposable branches remain in all four repositories because no Connector branch-delete action exists. They are not handoff pins or acceptance evidence.

## Storage disposition and successor boundary

The original observation was 68,289,347,584 available versus 68,719,476,736 required bytes, a 430,129,152-byte deficit. **That observation is historical, not current capacity.** Primary made no local storage change. The existing `max(64GiB, 2*Q+20GiB)` admission policy, per-location allocation/sync/readback tests and 20GiB operating floor remain intact; capacity is not reserved. Merely freeing the historical deficit is not a proof of sustained headroom.

A human/operator may provide storage headroom through separately authorized management of unrelated data. This handoff authorizes no cache/evidence deletion, snapshot or quota change, path relocation, cleanup or threshold reduction. A planning target above the measured admission requirement is prudent; it does not replace the actual admission tests. Local may perform one fresh diagnostics-only B admission under the updated procedure. Only if source, custody, host, compilation and fresh capacity prerequisites all pass may the separately admitted one-shot B focused batch execute. A blocked diagnostic is retained and returned without retries or Unity launches.

Final transport commits must be **Docs-only descendants of ba47**, whose runtime source is unchanged from the Local return. The final four-head prompt supplies transport identity; a differing Player/package/input hash blocks execution regardless of this report's success. Full R03 closure still requires the missing genuine captured-generic and initializer-failure witnesses, IR-R03-01 semantic/capture work, separate independent re-review and a separately initiated Human Review Gate.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. S/R/Q/P/O/N, staged retained R, failed warm certificates and deferred CPU/RSS risks are preserved. No H2, X02 or M08A is started.
