# R03 B2 D5-B C10 — independent rereview request after RR2 Primary correction

**Status: PendingIndependentC10RR2Review.** Independent reviewer must inspect actual source and **raw GitHub Actions job logs**, not merely endorse [Primary implementation report](D5B_C10_RR2_PRIMARY_IMPLEMENTATION_2026-11-23.md) or the preceding [independent `ReturnRequired`](D5B_C10_PRIMARY_REMEDIATION_INDEPENDENT_REREVIEW_2026-11-23.md). **Scope: C10 source/host test-producer preparation only.** Do not start Unity/IL2CPP/Player, Local Validation, D5 completion, D6, H2, M08A/X02/SNAP-01 or Human Review Gate.

**Fixed source tuple, branch `codex/assembly-shadow-r01b-h1`:**

| Repo | Immutable source SHA |
|---|---|
| `night-outlook/hybridclr_demo` | `38b166eea238ff7e734178175bfeaa33889a022d` (CI-tested implementation; later documentation-only HEAD is not tested) |
| `night-outlook/il2cpp_plus` | `87a34bbea39930dab96cf4703756d8da79d54684` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |

Compare demo code against prior independent review `d0b381809a5273c3dc82a0885c2e4277b6b330bb` and native `il2cpp_plus` against `84f9435628b8ff4cc675409f6b4d76dd2753d8a8`.

## Independent checklist

1. **RR-01 native auto writer:** confirm `ReceiptOpen` preopens exclusively while healthy, creates a native collector outside publication locks, and never requires managed `Join/GetState/ReceiptSeal/JsonUtility` after `CommitTransaction`. Inspect the exact `NativeCollector` loop, 60s pre-arm/8s post-arm bounds, pwrite/fsync/close, first-error B1 frozen-source reads, pinned object field snapshot and **nonzero test-only `_exit(20/42/2)`**. Identify races, data-race/UAF/GC risks, file descriptor lifecycle and test-only process exit effects. Native production VM branch is NotRun; do not promote host mocks to real VM.
2. **RR-02 exact worker identity:** inspect `WindowProbe::ArmTargetForCurrentThread`, `MatchesTargetOnCurrentThread`, `MethodResult` token consumption and actual `AssemblyShadow::AssertMethodIsActive` guarded call. Confirm one source-bound `MethodInfo*` and worker thread, not just `Methods/R03.Node.Keep` names or process-wide counters. Check `Class::GetMethodFromName` vs actual interpreted `MethodInfo` pointer equivalence as an untested real-VM hypothesis. Examine pinned `GCHandle` and precommit metadata/GC timing.
3. **RR-03 slot 5:** verify native collector writes slot-5 exact target guard result, not a fabricated managed method-return result. Review Python parser's ten required event slots, token/counter/outcome/first-error/field joins, missing-slot5 and competing-worker negatives, admitted and unsafe body effects; confirm **all outcomes remain source-material, not Player acceptance**.
4. **Actual CI:** [final run 45132702353](https://github.com/night-outlook/hybridclr_demo/actions/runs/45132702353) at exact tested SHA, completed/success 4/4. Fetch all four raw job logs IDs `137551628821`, `137551629012`, `137551629033`, `137551629043` and independently confirm **50+27+28 Python tests per job**, **18 window, 2 manual writer, 12 autonomous writer strict/sanitized native cases per job**, one OFF control/job, **12 synthetic auto-receipt parse checks per job**. No real Unity, C# compilation, Bee/link or Player. Keep intermediate CI failures failed.
5. **Source fidelity:** verify exactly 2 changed native files, 14 demo C10 paths, all 13 native Git blob pins, 3 isolated source blobs, 5 intended native TUs, 9 exports, ON/OFF compiler macro distinctions, synthetic Mach-O/nm/test allocation exclusion. No global allocator host source in production compile roster.
6. **Acceptance gate:** `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `APPROVED_LOCAL_HANDOFF_BLOB=None`, all six historical roots not independently bound for future Local, all **18 Player cases NoCoverage**. Actual native VM/GC/first-error/32-bit ABI/linked GameAssembly/PID are NotRun.

## Required outcome

Choose exactly one: `PassD5BC10ForNextPreparation`, `ReturnRequired`, or `Blocked`. Publish an independent Markdown rereview with line-specific source evidence and raw CI IDs in this directory, update README + the **closed** WEB_TO_LOCAL document, commit/push and verify remote HEAD; **do not approve Local** or enter unrelated milestones. Even `PassD5BC10ForNextPreparation` only approves a bounded source/test-producer preparation checkpoint; it is **not** product acceptance, evidence that `Keep` ran or was denied in a real Player, or permission to run Unity. Stop after the independent review.
