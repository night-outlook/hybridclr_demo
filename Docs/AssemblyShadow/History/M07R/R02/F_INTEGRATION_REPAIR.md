# R02 batch-F integration repair

## Authority and preserved evidence

Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`. The fixed checkpoint is `local-validation-20260927-batch-f-return-required/` in this directory. F recorded 22 Passed, 8 Failed and 4 Blocked cells, followed by a failed complete seal. Its 1,984-file preservation inventory is not a complete seal, and no `LOCAL_BATCH_RESULT.json` was produced. No historical report or execution is changed by this repair.

The successful F controlled builds and generated-native transaction checks establish progress, not R02 acceptance. The next batch remains fresh: changed managed package code requires newly source-bound builds for candidate and control. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false.

## F-01: strict producer/parser integration

The unchanged R02 native `AssemblyShadowR02Diagnostics.h::AppendDiagnostics` writes a nested `r02` extension with its own schemaVersion 1 and 33 mandatory fields. The prior managed `AssemblyShadowTypeResolutionInfo.Reader` accepted only the 18 legacy outer fields. This directly explains the retained `Unknown type-resolution field: r02` exceptions in candidate ON sidecars and startup positives.

The package parser now supports exactly the legacy 18-field outer schema or that schema plus the explicitly known R02 object. Absence is represented by null and means unavailable legacy diagnostics, not measured zero. A present null object, missing fields, duplicates, unknown fields, wrong token types, unsupported versions, overflow and invalid coverage are rejected. No generic unknown-field skip exists. All counters preserve UInt64 values without floating-point conversion.

The nested model exposes all 33 fields with preservation attributes. It checks the fixed schema version, diagnostics levels 0/1/2, counter capacity 128 and accounting scope `R02StructuresExcludingAllocatorOverhead`. Coverage is limited to Disabled/Truncated/Saturated/BoundedComplete and must respect immutable profile availability. It does not impose cross-counter equalities on a live non-atomic snapshot. Neither disabled counters nor absent legacy data constitute acceptance evidence.

Package commit `809a67f1f14c3626bd3c7b21721a53c1c61b1849` is used in BOTH candidate and H1-runtime control. Their package and demo code therefore stay common; only IL2CPP runtime pins differ. The native producer, allocation cache, correctness guards and timing workloads are unchanged.

A new Primary interoperability test compiles the actual native header writer at each diagnostics level and links the actual package parser into a .NET host. Twelve native extension fixtures cover normal high counters, saturation, exhausted thread slots and dropped classes; one legacy fixture covers absence. Tests inspect every emitted field, each missing/duplicate/null nested field, UInt64 precision and malformed tokens, unknown schemas/fields, invalid coverage and field ordering. The outer legacy object is explicitly a host fixture, not an IL2CPP VM execution claim. Unity's Preserve attribute alone is stubbed. This test is required in the Primary/Local host cell; missing SDK is Unavailable, never Passed.

## F-02: M07 early-startup capsule preparation

The preserved F command `batch/commands/0031/command.json` invokes `run-m07-players.py` without `--early-capsule-root`. The launcher only inserts the three early-startup arguments when that root is supplied. The native-ON startup callback's `R01EarlyStartup.Run` calls `Arguments.Read` before it can acquire a result path; those arguments are mandatory. This is a source-level sufficient cause of the observed early refusal and missing managed result, distinct from the later type-resolution parser failure. The sparse historical Unity log cannot rule out additional causes.

The R02 M07 cell now invokes the existing `prepare-h1-m07-control-capsules.py` using the exact new fixture, ON/OFF receipts and replay receipt, then passes its retained new root to the launcher. Existing per-mode patch selection, input hashing and rejection behavior remain. Capsule preparation failure prevents launching; no automatic retry or manual startup bypass is introduced. Local must preserve capsule manifests, per-mode early receipts and Player raw results and report any further refusal separately.

## F-03: count-family dispatch

`counts` selects the existing parameter auditor only for `parameters` and the existing nested auditor only for `nested`. Unknown families fail. Both generated families and audits feed the unchanged 132-cell matrix. Tests exercise the actual batch dispatch and ensure both audit paths/arguments are present; neither auditor, fixture schema nor expected case count is relaxed. Actual Unity/Mono fixture generation and Player execution remain Local work.

## F-04: scoped linker restoration

The diagnostic transaction now captures `Assets/HybridCLRGenerate/link.xml` together with its existing scene input. The count-build transaction captures it too, because that path also invokes GenerateAll. Each transaction retains complete original/generated bytes before considering restoration and restores the originals exactly, including BOM and line endings.

Permission is deliberately narrow: unchanged bytes, or the observed empty linker expanding to one netstandard assembly with exactly the 14 preserve-all types in F's committed `generated-link-after-diagnostic.xml`. Extra assemblies/types/attributes, duplicates, non-whitespace content, declarations, links or concurrent edits fail rather than granting arbitrary XML overwrite permission. Other source mutations still fail normal authority checks. Tests cover exact restoration and adversarial changes. A different generated type set needs Primary review; Local must not extend this permission.

## F-05: stable forensic retention and exact archive recovery

F successfully analyzed E's raw DLLs while they existed, but retained only their historical paths; those paths were unavailable at final sealing. An analysis receipt cannot substitute for its raw inputs.

The forensic cell now snapshots and hash-checks each exact live DLL and original Git preparation receipt into its own new output before any build. Snapshots remain the retained inputs even if old paths later disappear. A missing live DLL may be recovered only through E's exact Git-bound `LIVE_EVIDENCE_BINDINGS.json` (blob `7d2a0cf83d0550b875f8c1c078daeec3bc1832b5` at commit `1d7dc134003206ada8a92b50763ca2da7dc9530d`), its exact index/archive hashes, the full existing member audit and the exact original locator/member/size/hash. The index, archive and origin record are also snapshotted and retained. No basename search, alternate run, synthesized DLL or reconstruction at the old path occurs. Existing corrupt live bytes do not fall back to a good archive.

The archive-backed copies are historical inputs, never reused Player execution or replacement evidence for F. Missing/incomplete forensic acquisition remains a fatal complete-seal failure. Other independently valid cells may run and report errors, but neither a partial forensic report nor an inventory-only return is promoted to a complete batch seal. Tests delete old live files after snapshotting, recover from a real test archive, seal retained copies, and reject altered archives/indexes/locators/live bytes.

## Execution sequence and review boundary

Primary completes code, negative tests, the Linux producer/parser integration, macOS focused tests and source/control publication. The final handoff pins the new common source and package. Runtime pins remain HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, candidate IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` and control IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Local runs one new 34-cell R02LocalBatch-v1: source/common graph and expanded host checks, retained forensics, independent fixed M00 materialization and fresh controlled builds, eight functional sidecars, four pilot plus forty formal A/B pairs, Editor/native/transaction/M07/startup/failure/count132/diagnostic/lazy-dense/capacity, final authority and complete sealing. Existing dependency barriers remain. No non-trivial implementation, pin change, weakened check or source-policy expansion is assigned to Local.

This document is a Primary implementation self-review. A genuinely independent R02 stage review remains required after eligible Local evidence. D1/D2 require measured disposition before H2. Previous A/B/C/D/E/F failures retain their original statuses. Rollback requires a new explicit handoff of a previously published complete tuple; never mix new parser/source receipts with historical build claims or reset retained evidence.

## Connector transport

Disposable branch `codex/connector-smoke-r02-f-20260927-3a8c` passed write/read-back in demo at `d6eb60b84af2f16c4914c7418ab528d214ee91b9` and package at `09c87163cb767453b71f2a7e49b7d015e89abd8a`. These branches are not source or handoff commits and must not be merged. They remain because the available Connector exposes no branch-deletion operation.
