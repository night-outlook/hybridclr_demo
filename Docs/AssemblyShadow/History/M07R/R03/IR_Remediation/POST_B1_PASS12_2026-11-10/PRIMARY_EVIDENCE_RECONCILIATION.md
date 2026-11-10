# R03 B1 oneuse-12 — Primary reconciliation of published Local evidence

Date: 2026-11-10 UTC. Owner: Primary Implementation. Scope: **focused originating native first-error B1 only**. The original R03 independent full-stage verdict remains FAIL.

## 1. Authoritative source and publication

The successful **executed** source tuple on branch `codex/assembly-shadow-r01b-h1` was:

| Repository | Executed source commit |
| --- | --- |
| `night-outlook/hybridclr_demo` | `2d690bb2f7234ddcbee339f9da7125d687f5ed45` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `8aa8d09319a89b55b2496bcc2c69ccc69cb57be9` |

The **subsequent evidence publication** is `hybridclr_demo@9c210801c8da1e8371a09c25e0ef708a6d130fc3`, not an alternate execution source. Read Local-owned [LOCAL_VALIDATION](../../../../Handoff/LOCAL_VALIDATION.md) **first**, then [RETURN_TO_WEB](../../../../Handoff/RETURN_TO_WEB.md), then the immutable [oneuse-12 checkpoint](../../local-validation-native-b1-20261110-oneuse-12/README.md), its `LOCAL_RESULT.json`, `product/LOCAL_BATCH_RESULT.json` and `local-evidence/FINAL_INDEPENDENT_AUDIT.json`.

The Primary read the Git-published structured results, original Local report and independent audit and compared their shared counts, source tuple, Player PID/error fields and all-false acceptance flags. This is a **selected published-receipt semantic reconciliation**, not an independent byte-for-byte rehash of the entire retained local raw evidence tree, the 534-member product archive or the physical GameAssembly.

## 2. Reconciled observations and provenance

- Exactly **one** authorized oneuse-12 runner invocation, **19 Passed / 0 Failed**, one real Unity **2022.3.62f2** macOS ARM64 IL2CPP ON/Release build, zero errors / one warning, and three genuine Player launches with successful exits.
- Actual linked `GameAssembly.dylib` SHA-256 `b660d8ff6128ad934f7605cf25736559ab2fcf51d82bb78f322f4e56c7e7303e`; UUID `9667BE92-31EF-3C4A-B809-2ABB82B10718`. Installed native VM and compiled Bee source roster excluded the standalone test-host allocator driver; independent linked-symbol receipt found **zero** global allocator overrides. The required B1/guard exports and `Bi4` bridge were observed.
- Player `initializer-control`: PID **8760**, B1 state/code/origin **0/0/0**, null first reason and 0 reason bytes; native V1 control disposition remained healthy.
- Player `initializer-failure`: PID **8777**, B1 **2/19/2**, **114** UTF-8 reason bytes. Native B1 first reason and separately captured original V1 reason were byte-identical; postprepared initializer/bridge evidence joined to the same Player and fixture.
- Player `captured-generic`: PID **8787**, B1 **2/15/1**, **252** UTF-8 reason bytes. Real physical `Methods.R03.Node` captured baseline type produced first guard error15, with source/executable/PID and original native V1 reason equality preserved. Its postterminal AOT attempt remained denied.
- Initializer V1 `verification.json` and B1 `verification-b1.json` both existed and were independently checked; the historical oneuse-11 exclusive receipt collision was not observed.
- Actual host-only B2 descriptor/codec suites ran in strict/sanitized profiles. External B2 custody retained **2,006 regular files and two literal symlink targets**; the product archive carried verified regular-only custody metadata. The independently checked bounded product seal passed with **534 members**. Host-only B2 results do **not** mean real VM V2 transport.
- Fresh Mac capacity and SDK/admission evidence were produced; original-S/SDK/prior-checkpoint preservation was rechecked in the Local report's bounded scope. **17 retired roots and 40 duplicate paths remain Unavailable**; historical strict custody remains Blocked. Do not recreate missing data.

## 3. Findings disposition and acceptance scope

The three oneuse-11 defects (test-only allocator in production link, negative symlinks under the sealed product root, and exclusive V1/B1 verification receipt collision) are **verified corrected for this oneuse-12 source + linked Player path**. The evidence does not prove arbitrary other Unity targets, SDK versions, configurations or future refactors.

The prior oneuse-07/09 focused PASS, oneuse-10 prerequisite block and oneuse-11 failure remain separate immutable historical outcomes. **oneuse-12 is consumed**; its product/native-host/B2-host/preflight paths are retired. Do not run its canonical command again or overwrite its receipts. The former `Handoff/WEB_TO_LOCAL.md` from executed source `2d690bb2...` is retained immutably through Git history, not as fresh authority.

Mandatory flags stay **false**: `R03Accepted`, `H2Passed`, `ReadyForHumanReviewGate`, `runtimeAcceptance`, `qualificationApproved`, `fullLegacyRegressionAcceptance`, `nativeV2TransportImplemented`, `firstRecoveryAuthenticatedV2`. `wholeVmEpoch=NotProven`. PureInterpreter stays disabled. Both original High independent review findings `IR-R03-01/02` remain open; original S independent full compiler/object/link/Player provenance, B2 integrated real V2, B3 whole-VM epoch, real shutdown/GC/RSS and RC/P/E qualification remain incomplete.

## 4. Next authorized Primary scope

The earliest next **Primary-owned** implementation area is **B2 real bounded V2 transport in the isolated R03 test-only Player**, defined in [B2 implementation design/plan](B2_IMPLEMENTATION_DESIGN_AND_PLAN.md) and the original [B-stage design](../POST_CAPTURED09_2026-11-09/B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md). No Local Validation invocation is authorized until source integration, independent source review, focused host tests, exact source pins and final-source dual-OS CI are complete and a **new one-use** WEB_TO_LOCAL is published with fresh absent roots.

**Current state: B1 focused Local PASS reconciled; B2 Primary Implementation pending. No Human Review Gate or H2/M08A/X02/SNAP-01.**
