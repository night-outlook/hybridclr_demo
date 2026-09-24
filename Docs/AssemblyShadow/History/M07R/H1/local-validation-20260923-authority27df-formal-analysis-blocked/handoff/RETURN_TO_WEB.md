# Local Validation → Primary Implementation

## Current blocker: final analyzer rejects the complete 40/40 series because the nested R00 build receipt omits two required fields

Fresh Local Validation at checkout `f5e34235641c212c715aef3405925ddd4cf28ee6`, source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`, passed current/protected authority, current Python validation, exact 3-path and 22-path source audits, complete retained artifact reauthentication, a new graph bridge, retained-pilot admission, and a new guard-v2 8/8 strict pilot seal.

The bridge SHA-256 is `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`. The admission SHA-256 is `cbfc6faf8512a214ff97fa939bc6335b05a36362d66b539ff22e954c61529ed1`. The seal SHA-256 is `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`; it records `guardKind=CrossRemountStableStatGuard`, `guardVersion=2`, exact fields `[inode, mode, size, mtimeNs, ctimeNs]`, no device field, and `deepLaunchVerificationCount=8`.

A wholly new formal series started only from the retained pilot index. Pair 1 used automatic path-hash namespace `7cafb9c53434` without colliding with preserved outputs. Protected A had no formal launch authority; candidate B consumed a valid current `H1FormalSideLaunchAuthority`, launched the Player, and emitted an R00 receipt echoing the same authority, bridge, seal, and build map.

All 40 formal pairs passed on attempt 1: 10 OFF-NoPatch, 10 ON-NoPatch, 10 ON-P01, and 10 ON-P03. No whole-pair retry was required. The formal batch receipt SHA-256 is `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667` and the final sample-index SHA-256 is `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

The bridge-aware final strict analyzer completed but returned `Incomplete` / `ComparabilityIncomplete`: 44 of 45 cumulative pilot/formal attempts were invalidated with `R00 raw build field differs: baselineBuildId`. The remaining item is the already-preserved historical `R00-ON-NoPatch-pilot-01` failure where the A runner process group could not be proven gone and B was skipped.

The raw R00 top-level `baselineBuildId` and `runtimeAbiHash` are correct. Its nested `playerBuildReceipt` has the correct path, hash, and build GUID, but omits `baselineBuildId` and `runtimeAbiHash`; the analyzer requires both fields there. This identical producer/analyzer contract mismatch affects protected and candidate, pilots and formals. It is not a pair-level runtime failure, so protocol retries would not correct it.

## Required Primary correction

Reconcile the R00 producer and final-analyzer schema, with fail-closed tests:

1. Have the producer include `baselineBuildId` and `runtimeAbiHash` in the nested `playerBuildReceipt`; or
2. Deliberately revise the analyzer to bind the authenticated top-level fields instead.

Primary must then decide whether the immutable 40/40 raw series may be reanalyzed under the corrected contract or whether acceptance requires a fresh series. Local did not make that semantic change, modify `WEB_TO_LOCAL.md`, or relabel evidence.

Evidence is retained and authenticated at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`. The checkpoint includes all 40 sample indexes and referenced side evidence, the analyzer output/log, and a machine-readable failure diagnosis.

V05 and independent M08 are ineligible. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
