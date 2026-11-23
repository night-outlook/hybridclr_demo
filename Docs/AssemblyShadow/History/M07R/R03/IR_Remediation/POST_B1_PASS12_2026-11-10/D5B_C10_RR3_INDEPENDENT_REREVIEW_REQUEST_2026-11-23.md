# R03 B2 D5-B C10 RR3 — new independent source/design/CI rereview request

**Status: PendingIndependentC10RR3Review.** Act as an independent reviewer separate from Primary Implementation and Local Validation. Read prior [RR2 independent ReturnRequired](D5B_C10_RR2_INDEPENDENT_REREVIEW_2026-11-23.md), this cycle's [Primary RR3 implementation report](D5B_C10_RR3_PRIMARY_IMPLEMENTATION_2026-11-23.md), and **actual fixed source plus raw CI**, not only the Primary narrative.

**Review scope: C10 source/test-producer preparation only.** No Unity/IL2CPP/Player execution, no Local Validation authorization, no D6/H2/M08A/X02/SNAP-01 or Human Review Gate. Branch for all four repos: `codex/assembly-shadow-r01b-h1`.

| Repo | Exact immutable tested source SHA |
| --- | --- |
| `night-outlook/hybridclr_demo` | `dbb1360c5b68dabab05755a5d39a5cea53270574` (CI source, not later docs-only HEAD) |
| `night-outlook/il2cpp_plus` | `c741fb32a2b770856f211f47305c4f86b51f54ce` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |

Compare native to `87a34bbea39930dab96cf4703756d8da79d54684` and demo to previous review `2a639128d186a1f5584c1dd4cacae817a2e0fe44`. The source/host CI only applies to the exact above tested code tuple.

## Mandatory independent checks

1. **RR2-01 actual native early terminal path:** inspect `AssemblyShadow::AssertMethodIsActive` before any physical owner metadata dereference. Does it call the exact TLS-bound `MethodResult(false)` only for the target method, keep original business policy and preserve first-error behavior? Compare to normal allowed/rejected paths; verify no inadvertent double count or constructor confusion. Host `early_terminal` only simulates the branch; actual full `AssemblyShadow.cpp` VM compilation is **NotRun**.
2. **RR2-02 real canary happens-before:** inspect `HasWorkerCompletedP5Acquire` relative to `ReleaseP5` CAS and the C# worker's try/finally placement, `canaryReady` release/acquire publication, and the collector's `before/after` read conditions for allowed, denied, raced, timed-out and not-yet-bound cases. Examine real IL2CPP GCHandle/object metadata lifetime separately; host integer synchronization is not real GC evidence. Look for C++ data races or unsupported assumptions.
3. **RR2-03 receipt durability:** inspect fresh `.pending` path validation, `O_EXCL/O_NOFOLLOW`, disk event writes, preclose file `fsync`, actual `close` check, non-clobber `link`, pending `unlink` and parent-dir `fsync`. Confirm failure after final publication cannot classify as candidate without **separate actual PID+exit**, and missing/incorrect PID or exit 2/0 are rejected. The current parser checks *caller-supplied* PID/exit only and sets `externalProcessProvenanceIndependentlyVerified=false`; independently evaluate whether this is adequate for bounded source-only preparation, and explicitly retain the requirement for a future source→binary→PID/argv process monitor.
4. **Fault injection:** verify `io_pwrite`, `io_fsync`, `io_close`, `io_dirsync` host cases test exposed final path and mock outcome correctly; do not equate simulated host errors with actual real disk faults. Check final host binary validity and expected nonzero native Player exit codes 2/20/42.
5. **Fresh exact CI:** [run 45144226643](https://github.com/night-outlook/hybridclr_demo/actions/runs/45144226643), attempt 1, 4/4 successful jobs; fetch raw job IDs `137589405848` (Ubuntu C++17), `137589406538` (macOS C++11), `137589406633` (macOS C++17), `137589406705` (Ubuntu C++11). Each has **59+27+34 Python tests**, **22+2+20 native host cases strict/sanitized**, one feature-OFF control, and 20 synthetic file-outcome checks. Keep intermediate failed `45143818536` and `45144032193` failed.
6. **Provenance and scope:** independently fetch/check **13 actual native source Git blobs and three isolated demo blobs**, five intended TUs, nine exports; confirm exactly two native and 11 demo code/workflow changed paths, and no B1, D5-B custody or Local-owned document changes. Review source-pinset blob `cfca8eecb339fdbc16777efee42465c762f0462b`, no global allocator host source in native build; fake Mach-O/nm fixtures stay `SyntheticSourceHost`.
7. **Closed gates:** all 18 D5 Player cells remain `NoCoverage`; actual full Unity and `HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1` compile, real GC, first-error and executable/PID are `NotRun`; `APPROVED_LOCAL_HANDOFF_BLOB=None` and six historical source/evidence roots not authenticated for new Local. Do not imply source/host success grants Local approval.

**Decision and publication:** choose exactly `PassD5BC10ForNextPreparation`, `ReturnRequired`, or `Blocked` for **source/test-producer preparation only**, with actual source line links, raw CI references, severities and clear untested hypotheses. Publish new independent Markdown report under the same history directory, prepend current status to canonical README and **keep** WEB_TO_LOCAL closed, commit/push/verify GitHub branch remote, then **stop**. No human or Local approval is implied even by source-only Pass.
