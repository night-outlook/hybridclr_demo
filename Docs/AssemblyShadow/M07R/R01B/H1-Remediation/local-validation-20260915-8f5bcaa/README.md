# Local Validation checkpoint — handoff 8f5bcaa

## Exit

**Local Validation → Primary Implementation**

V00 and V01 pass. V02 proves that the real Apple declared-input capture crosses the former 267,613,743-byte failure point: 448 declared paths contribute 315,422,684 nominal bytes, while the complete 451-observation store contains 318,212,421 logical unique bytes in 72,612,459 physical bytes. The retained replay completes planning, exact PCH replay, six syntax/macro probe contexts, and independent store verification.

The prioritized fresh V03 candidate ON/Debug Player also builds and passes native compiler-provenance and store verification. It then fails the required managed-source verifier with:

```text
Blocked: Missing or ambiguous managed action chain for AssemblyShadow.R01BDiagnostics
```

The managed capture retained one new native Bee graph and zero managed compilation rows. The exact Player C# actions exist only in an unchanged pre-existing `200b0aPDevDbg.dag.json`; both matching DLL outputs also existed before the build. The current capture excludes unchanged Bee graphs, while exact reuse requires an earlier direct proof for the same source-pin SHA. Resolving that conflict changes provenance semantics and is outside Local Validation's correction boundary.

The remaining five builds, V04, V05, successor packaging, and independent whole-chain M08 are `Blocked / NotRun`. `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Source identity

| Role | Exact identity | Final state |
| --- | --- | --- |
| Candidate handoff checkout | `8f5bcaa687e33e8666eacc942b5e414a83b737fc` | requested branch; checkpoint files are the only new tracked candidates |
| Candidate source/implementation anchor | `91ebef56eaa7034ed49a80bced422ea4c067d2fe` | source target and pin match |
| Candidate native | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | clean |
| Candidate package | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | clean |
| Candidate IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` | clean |
| Reproduction demo | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | unchanged and clean |
| Reproduction native | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | unchanged and clean |
| Performance reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | unchanged and clean |

Pre-existing untracked historical `v7`–`v11` evidence was preserved and excluded.

## Results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; expected checkout, source anchor, pins, and false gate flags. |
| V01 Bee Primary | `Pass` | 256/256 bounded tests. The first launcher attempt used a pre-existing output directory and is retained as an invocation failure. |
| V01 H1 Python | `Pass` | 451/451 leaf tests. |
| V01 strict provenance / normal M02 owner | `Pass` | 4/4 and 15/15. |
| V01 candidate Unity | `Pass` | Compile passed; corrected focused filters passed 4/4 and 10/10; demo Editor suite passed 351/351; package Editor suite passed 720/720. Both initial zero-test filter attempts are retained. |
| V01 reproduction Unity | `CompletedWithNonPass` | Compile and focused 4/4 + 10/10 passed. Optional full demo sweep completed 330/342 with 12 historical missing-fixture/baseline failures. |
| V02 retained Apple replay | `Pass` for diagnostics | `DiagnosticReplayVerifiedNotBuildAccepted`; 446 compile actions, 444 linked objects, 430 runtime / 2 BDWGC / 14 zlib, two PCH producers, six successful probe groups. |
| V02 store verification | `Pass` for storage integrity | `StoreVerifiedNotAcceptance`; 451 observations/content/blobs; 318,212,421 logical bytes; 72,612,459 stored bytes; 444 `zlib-v1`, 7 `raw-v1`. |
| V02 fail-closed controls | `Pass` | 6/6: old-boundary volume, compressed tamper, corrupt finalization, incompressible raw fallback, logical bound, stored bound. |
| V03 install / installed verification | `Pass` | Installer passed. Correct verifier invocation reported 955 source files, 957 installed files, demo source verified, mode `on`. The initial duplicate `verify` positional argument failure is retained. |
| V03 Player/native provenance | `Pass` before managed verification | Player build passed; native strict verifier and fresh store verifier passed; exact restoration passed. |
| V03 managed provenance | `Fail` | Zero captured managed compilation rows because required cached Bee graphs and outputs were unchanged before/after the build. |
| V03 remaining builds | `Blocked / NotRun` | A valid candidate ON/Debug smoke receipt is mandatory. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | The six-build provenance set does not exist. |
| V05 successor/M08 | `Blocked / NotRun` | Acceptance inputs are incomplete. |

## Real retention metrics

The V02 replay and V03 fresh capture have the same complete storage totals:

| Metric | Value |
| --- | ---: |
| Declared input paths | 448 |
| Declared inputs available at census | 448 |
| Declared nominal bytes | 315,422,684 |
| Retained observations | 451 |
| Unique raw contents / stored blobs | 451 / 451 |
| Logical unique bytes | 318,212,421 |
| Physical stored bytes | 72,612,459 |
| Encodings | 444 `zlib-v1`; 7 `raw-v1` |
| Per-file / logical / stored / observation limits | 64 MiB / 2 GiB / 512 MiB / 4096 |

Both `h1_verify_capture_store.py` runs exited 0 and reported `StoreVerifiedNotAcceptance`. These are integrity results, not build or H1 acceptance.

## Fresh build identity

- Build ID: `H1Count-On-Debug`
- Build GUID: `540065befa904f7f880ab13416c0f852`
- Input snapshot SHA-256: `7ddd2f21c4718469ec06998ce3f19e2ff0100cc28eda2c4b5a2431a6eab753d5`
- Fresh Bee graph SHA-256: `3115788e4cdae9f9a4021dc8f5f27f4d5efd9ac5c819bcc30fb5298072832c95`
- Native library SHA-256: `9acf78528cda4587f0cf97b4a2e565767e57962c863da19f30479276f91c4ba0`
- Build receipt SHA-256: `3043f69397cb8cc0dc4a798cbfe851f02f65031a6d8a23f2b31f09dec1ce1a92`
- Compiler provenance SHA-256: `13a2fe9f1ce20a8db3d120b38e18e93040117edf94ea8fb8127cd4acbd998109`
- Fresh retention inventory SHA-256: `089060a3ca2ea4e9eb162c4f9bf9b90a77819b455bed7faa8119ed6ab45629dc`
- Source-pin SHA-256: `3bb928c8abd8d61da9050b7766466ffd4931a516669315eeec8013e8dea47e0d`

## Failure evidence

`v03/managed-action-census.json` records all four matching managed compiler actions. The two Player actions in `200b0aPDevDbg.dag.json` reach the Player input, but the graph SHA-256 `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af` is unchanged from the pre-build capture and both output DLLs existed before the build. The fresh managed capture therefore contains zero compilation rows and cannot directly prove the current source anchor.

- `v02/retained-apple-replay.tar.gz`: complete executable replay/store, SHA-256 `a36c324c635911a4c68f814a5d17cc7819f32d57ea76f5b8c7c398aee08632d6`.
- `v03/candidate-on-debug-managed-provenance-failure.tar.gz`: smoke runner, complete fresh compiler store, managed capture, receipt, and restore evidence, SHA-256 `a82275037f61c3e42e7d298a0f10b5446b1b7fd7cea3cadef80fdef584f76658`.
- Full unpacked raw root: `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-8f5bcaa`.
- Failed preparation root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-e347902b06224cbc8af39ec58902fafa`.

The archives were listed and fully decompressed by `tar -tzf`. `evidence-manifest.json` binds every committed checkpoint file after final report generation.
