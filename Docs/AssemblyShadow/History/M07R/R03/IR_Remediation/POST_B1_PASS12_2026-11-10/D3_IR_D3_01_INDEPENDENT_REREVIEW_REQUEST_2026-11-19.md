# D3 independent re-review disposition — PassD3ForD4 (2026-11-19 UTC)

**Independent D3 re-review COMPLETED: `PassD3ForD4` (D3 checkpoint only).** See [D3_INDEPENDENT_REREVIEW_2026-11-19.md](D3_INDEPENDENT_REREVIEW_2026-11-19.md). The earlier independent `ReturnRequired` and this request's `ReadyForIndependentReview` status below are **historical pre-decision states**. IR-D3-01 is **closed at exact source-host scope** after independently verifying one-file native repair, all four CI job logs at test commit `b2e39532718d8bb80ce3089b7374015befbdab37`, 76 passing Python source tests, 64 host scenario receipts / 1,688 assertions and four expected-failing broken-order negative controls. **D4 Primary Implementation alone is now eligible to begin in a separately assigned task**; its ActiveSnapshot lifetime defect remains critical/open. No Local Validation/Unity Player/R03/H2/Human Review authorization. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. The original re-review request is retained below unchanged for provenance.

---

# R03 B2 D3 — IR-D3-01 independent re-review request (CI complete; review pending)

**State:** `ReadyForIndependentReview` (CI host gate complete, NOT independent acceptance). The prior [independent D3 review](D3_INDEPENDENT_REVIEW_2026-11-19.md) remains **ReturnRequired** until a new independent reviewer evaluates the **corrected exact production tuple and completed evidence**, not the Primary self-review. **D4 not authorized.**

## Exact source tuple

All repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Review source SHA | Changed vs rejected D3 |
| --- | --- | --- |
| `night-outlook/il2cpp_plus` | `40d9a16a6e357f0b3ad1cc93362a93cc41768258` | `libil2cpp/vm/AssemblyShadow.cpp` only, blob `5e5fb4b094ae8111e5f674dfc534d411bf597690` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | No new change |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | No new change |
| `night-outlook/hybridclr_demo` | `b2e39532718d8bb80ce3089b7374015befbdab37` | New focused source-exact regression and corrected workflow; later documentation HEAD to be verified separately |

Read first [Primary IR-D3-01 remediation](D3_IR_D3_01_PRIMARY_REMEDIATION_2026-11-19.md), the independent [ReturnRequired analysis](D3_INDEPENDENT_REVIEW_2026-11-19.md), [D2 independent pass](D2_INDEPENDENT_REVIEW_2026-11-18.md) and Approach A.

## New exact source / test evidence

[GitHub Actions run 44496297788](https://github.com/night-outlook/hybridclr_demo/actions/runs/44496297788) is the **fixed workflow-expression** run at exact test source `b2e39532718d8bb80ce3089b7374015befbdab37`. Its matrix is Ubuntu 24.04 + macOS 15 × C++11/C++17. **Final independent evidence readback (2026-11-19 UTC): all four jobs completed/success**, including macOS C++17. Each job produced 19 passing Python source/mutation tests, 16 passing exact-source host receipts / 422 assertions, and one expected-failing old-behavior negative-control execution. Total: **76 source tests, 64 passing host receipts, 1,688 assertions, and four expected-failing negative controls**; 40 host receipts specifically exercised the deterministic two-thread barrier. All four raw logs were read; no host assertions or ASan/UBSan diagnostics failed. The prior **3/4** status was an intermediate observation, superseded by this completed CI run. Earlier workflow variants with escaped YAML expressions or different test SHAs are not acceptance evidence.

The new test source lives in `hybridclr_demo/Tools/AssemblyShadow/R03IR/TypeDefCensus/`:
- `extract_d3_usage_gate.py` — authenticates exactly pinned native, Runtime, Codec, D2 vector scopes, phase receipt and FirstError headers, compiles 21 literal bodies with a host adapter.
- `test_extract_d3_usage_gate.py` — 19 source/mutation regressions fail closed if the seal is removed/reordered, an origin/terminal signal is altered, the safe P0 or success path changes, D2 rollback is removed, or the Codec/group phase boundary changes.
- `D3UsageGateRaceHost.cpp` — actual Runtime/Codec, exact D2 physical/CLI scope bodies, real native `dynamic_array.h` template, D3 phase/lease callbacks, actual `FirstErrorV2` and `TerminalMethodDenied` with host-owned locks and VM objects. A scheduler barrier pauses the publisher after lease release but before outer `CommitTransaction` classification, while the contender acquires UsageLock and checks terminal admission. Normal P0 and success, normal failures before/inside/after Codec, exception before/after Codec group and first-error preservation are distinct process scenarios.
- `.github/workflows/r03-b2-d3-usage-gate-race.yml` — strict/ASan+UBSan matrix, source-pin/source-hash checks, expected-failing **test-only** control that avoids early terminal sealing while retaining the exact callable body.

**Evidence limit:** The host compiles literal native *function bodies* and real Runtime.cpp/Codec.h plus test-owned OS mutex/VM/allocator substitutes, not complete native Unity production translation units. No real Player, native atomic lock-free ABI, class/GC/whole-VM epoch, V1 fields14/15, native V2 readback/first recovery or process restart occurred.

## Independent reviewer questions (after all CI jobs complete)

1. Does `ReleasePublicationUsage` now seal `FirstErrorV2`, D1 phase, `s_unexpectedFailure` and terminal state **while still owning UsageLock**, before `usageHeld=false` and `UnlockUsage()`, including the C++ exceptional abandonment callback? Is that monotonic and nonallocating under actual source constraints?
2. Is `UsedBeforeAppend` marked only on the exact witnessed used-closure P0 denial, and `ActivePublished` only after actual `s_active` release-store? Can any misclassified normal false escape terminal classification? Does the D2 rollback retain its prior destructor and mutex order?
3. Under the concurrent T1/T2 interleaving from the original IR-D3-01 report, does the contender's acquire of UsageLock necessarily synchronize with a prior terminal release-store, and does the actual `TerminalMethodDenied` reject it? Check both the initial method check and final recheck in the full method-entry implementation.
4. Confirm the old unlock-before-terminal **negative control fails for the intended race**, and the corrected source passes all real Codec validation, real group-published, unexpected-exit, safe P0 and normal success cases without enabling runtime fallback.
5. Check first-error origin/first-reason preservation, target-specific atomic C++11/no-throw assumptions, an allocation/lock inversion under nested native scopes, ABI preservation, and absent any post-Codec rollback fiction.
6. Authenticate new pinned blobs, full raw completed job logs, sanitizer results, source mutation outputs, negative control, and total receipt counts before evaluating closure; preserve historical failed/queued test attempts as such.
7. Keep **D4 ActiveSnapshot lifetime and P5/P6** explicitly open, with no H2/M08A/X02/SNAP-01, Local Validation or Human Review Gate assertion.

**Requested decision (only after CI is complete and independently assessed):** `PassD3ForD4`, `ReturnRequired` or `Blocked`. A pass would permit D4 Primary Implementation **only**. It must not be interpreted as D4 implementation, Unity/IL2CPP/Player acceptance, Local Validation authorization, R03 acceptance, or project Human Review Gate approval.

**Current authority:** `D3IndependentReview=ReturnRequired` (existing decision pending re-review), `D3Remediation=PrimaryHostValidationComplete`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `D4=NotStarted`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
