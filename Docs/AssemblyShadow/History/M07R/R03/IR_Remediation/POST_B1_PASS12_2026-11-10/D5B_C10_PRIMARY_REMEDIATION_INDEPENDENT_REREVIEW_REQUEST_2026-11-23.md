# R03 B2 D5-B C10 — independent rereview request after Primary remediation

**Status: PendingIndependentRereview.** Independent reviewer must read the [original C10 ReturnRequired](D5B_C10_PRODUCER_INDEPENDENT_REVIEW_2026-11-22.md) and the [new Primary remediation report](D5B_C10_RETURN_REQUIRED_PRIMARY_REMEDIATION_2026-11-23.md), then independently inspect the actual source and raw CI. Do not treat the Primary report as approval. Review **C10 producer preparation only**, not Local Unity/IL2CPP, D5 completion, D6/H2/M08A/X02/SNAP-01 or a Human Review Gate.

**Exact branch:** `codex/assembly-shadow-r01b-h1` on all four repos. **Actual tested source tuple:**
- `night-outlook/hybridclr_demo@063de11e2459fa6530dee0bd0da9176f14b15c7f` (compare to `acd6bc55b9e5e48edf52c61083a291c42239a8fa`; later documentation-only HEAD is not the CI-tested SHA).
- `night-outlook/il2cpp_plus@84f9435628b8ff4cc675409f6b4d76dd2753d8a8` (compare to `8eeb3cc53a451a6925b490d623c81753822cb1d4`).
- Unchanged `night-outlook/hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a` and `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.

**Required independent checks:**

1. Exact physical `Methods/R03.Node.Keep` guard matching in the actual native `AssertMethodIsActive`, C# constructor/prebinding order, target `keepAttempted` and synthetic constructor-denial negative. Confirm feature-OFF code cannot change.
2. Validate native pinned `GCHandle`/`Il2CppObject`/`FieldInfo`/`stable` observer against the real VM definitions, not merely host C++ stubs. Validate correct pre/post body canary and fail-closed `AllowedGuard`, `DeniedGuard`, `RacedP6`, `BodyExecuted` and `Unknown` classification. Full Unity C#/native compile is **NotRun**.
3. Verify the eight native exports, exclusive preopen `O_EXCL/O_NOFOLLOW`, one-write-per-slot events, 212+320+4120-byte binary contract, authenticated first-error source and no postterminal managed JSON/FileStream. **Explicitly decide whether the remaining managed-to-native ReceiptSeal invocation after possible terminal poisoning requires further source correction before even bounded preparation approval.** A partial receipt must remain `NoCoverage`.
4. Independently inspect **all four raw logs** from [CI run 45122592338](https://github.com/night-outlook/hybridclr_demo/actions/runs/45122592338), job IDs `137519551034`, `137519551260`, `137519551297`, `137519551470`. Verify 39+27+20 Python tests/job, 12 window and 2 native writer strict/sanitized host cases/job plus one OFF control; preserve earlier failures.
5. Verify new native diff is two files and demo diff 13 C10 files only; authenticate all 13 native Git blobs and 5 intended TUs/8 exports, updated manifest/compiler flags, exclusion of any host global allocator, and that fake Mach-O/nm/compile materials are never presented as real execution.
6. Preserve `APPROVED_LOCAL_HANDOFF_BLOB=None`, six historical root roles, real native source→Bee→object→binary→PID as future required evidence, and **18/18 D5 Player NoCoverage**. No existing B1 oneuse-12 result substitutes for D5.

**Decision:** exactly one of `PassD5BC10ForNextPreparation`, `ReturnRequired`, `Blocked`. Publish a new independent Markdown report under this same history directory; document source lines, exact CI job evidence and unverified cases. Even Pass is **source/test-producer preparation only**, never Local execution or project acceptance. Update canonical README and closed WEB_TO_LOCAL, commit/push, verify remote HEAD, then stop.
