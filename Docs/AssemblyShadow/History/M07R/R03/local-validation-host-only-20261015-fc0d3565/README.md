# Local host-only validation — 2026-10-15 fc0d3565

Result: **FAIL / FailedOrIncomplete**. One source-pinned host batch, exit1, 2026-10-15T03:39:13.437543+00:00 → 2026-10-15T03:39:53.667789+00:00. No retry or source/test changes. Return to Primary Implementation.

Read [Local report](../../../../Handoff/LOCAL_VALIDATION.md), [finding](FINDING.json), [batch result](host/RESULT.json), [inventory](host/MANIFEST.json), [independent audit](preflight/EVIDENCE_AUDIT.json), [invocation](preflight/RECEIPT.json) and [copy bindings](COPY_BINDINGS.json). Full live evidence stays at `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-PRIMARY-HOST-ONLY-20261015-fc0d3565`; external authority/audit/publication receipts at `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-PRIMARY-HOST-ONLY-20261015-fc0d3565`. All original test data/binaries and four deliberate negative-control symlinks remain external. Published files are factual text evidence only.

The complete original batch inventory verifies **2549 entries**; source-before/after and all four post-batch clean remote identities match. RESULT SHA256 `5cbc46d691064e45bc897b4d6c80930e8713fb891c0411bbcb42edcda61fc704`; MANIFEST SHA256 `294bba26b5f05521496a85d26030ef07b96a46be80a8f41a50da4fba9b1f574e`. Eight outer command receipts: seven Passed, one Failed. All470 nested command stream hash bindings were independently verified. No `warning:` marker in retained stderr streams; this is not a warning-free official SDK compilation claim.

| Component | Factual fresh result |
| --- | --- |
| General stream / immutable producer binding | Failed before compile; strict/sanitized25-method profiles NotRun; component result/manifest Unavailable |
| Native V2 codec | 20 tests/profile, strict+ASan/UBSan Passed, zero failures/errors/skips;164 command receipts |
| POSIX V2 transaction | 27 tests/profile, strict+ASan/UBSan Passed, zero failures/errors/skips;184 command receipts |
| Earlier native V2 sink | 32 tests Passed; strict/sanitized tools,122 command receipts |
| Execution formatter | Separate strict/sanitized compile+run all Passed (four outer commands) |

Apple clang21.0.0, macOS26.5.2 arm64, Python3.14.6. Inherited TMPDIR unchanged. Apple LeakSanitizer unavailable/disabled by component runners; other OS/compilers NotRun. Host filesystem/sanitizer tests do not prove hardware power-loss durability, coherent live VM capture or engine lifecycle. No Unity, Test Runner, Player, integrated SDK compile or historical evidence re-run. All historical outcomes and acceptance flags stay unchanged/false. Historical S strict custody remains Blocked; SNAP-01/N/M/K/I/E remain FAIL. R03/engine-owner/runtime coverage stays open.
