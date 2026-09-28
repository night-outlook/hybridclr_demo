# R02 batch-F integration repair

## Authority and preserved evidence

Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`. Its immutable checkpoint is `local-validation-20260927-batch-f-return-required/` in this directory. F recorded 22 Passed, 8 Failed and 4 Blocked cells, followed by a failed complete seal. Its 1,984-file preservation inventory is not a complete seal, and no complete `LOCAL_BATCH_RESULT.json` was produced. None of these historical executions or reports is rewritten.

Final executable/tool source: `995dbf1003c306a69586f882ff02599db7a9780e`. Final package: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`, used in both roles. Matched H1-runtime control: `95b85617c92f8ce806f4652d88077936c76c3b8a` on `codex/r02-h1-runtime-control`. The candidate authority tested by final CI is `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`; the final prompt must use the subsequent documentation transport HEAD.

HybridCLR remains `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`. Candidate IL2CPP remains `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`; control IL2CPP remains `6be7f38bec2fa4677d24efc1a4a1294240789933`. No allocation-cache, native writer, correctness-guard or formal-timing change is introduced. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false.

## F-01 — strict native/managed diagnostics integration

The unchanged native `AssemblyShadowR02Diagnostics.h::AppendDiagnostics` writes a nested `r02` extension with its own schemaVersion 1 and 33 mandatory fields. The earlier managed parser accepted only the eighteen legacy outer fields. This directly explains F's `Unknown type-resolution field: r02` exceptions in candidate ON sidecars and startup positives.

The parser now admits exactly the legacy outer schema or that schema plus the known R02 object. Missing, duplicate, unknown and mistyped fields fail, including omitted false/zero values. A present null extension is invalid; true absence represents unavailable legacy diagnostics. Unsigned counters are parsed directly into UInt64 without signed or floating-point intermediates. The extension enforces schema 1, diagnostics levels 0/1/2, fixed counter capacity 128, known coverage values and accounting scope `R02StructuresExcludingAllocatorOverhead`. It checks immutable profile availability, not cross-counter equalities on a non-atomic live snapshot. Unknown schemas and generic extra objects are not silently skipped.

### Serialization and stripping follow-up

Adding a public serialized extension field would change existing DTO round trips and the exact eighteen-field build proof. The final package instead exposes a preserved `r02` property backed by a private `[NonSerialized, Preserve]` field. The eighteen public serialized fields remain unchanged. The extension is a transient parsed view; persistence of R02 diagnostics must retain the original native JSON. Serializing the legacy DTO intentionally does not persist that view or manufacture an absent/default R02 object.

The actual M05 pre/post-link verifier retains its exact legacy field check and explicitly roots the nested R02 schema separately. `R02TypeResolutionSchema.Fields()` is an independent inventory of all 33 typed fields. A matching but narrowed pre/post schema cannot redefine the wire contract. M06/M07 already use this verifier. The new model and fields carry preservation attributes; real stripping and Unity serialization still require Local execution.

Official background, distinct from project evidence: Unity 2022.3 documents field-based serialization and inline custom-class null limitations at https://docs.unity3d.com/2022.3/Documentation/Manual/script-Serialization.html . This motivates keeping the optional parsed view outside legacy serialization; the project behavior is checked by the tests described below.

### Tests and comparison boundary

A required Primary host test compiles the actual native header writer at all three diagnostics levels and links the actual package parser and independent schema inventory. Twelve native extension fixtures cover high counters, saturation, exhausted thread slots and dropped classes; one legacy fixture covers absence. It checks every emitted field, missing/duplicate/null/unknown fields, numeric precision/overflow/coercion, versions, coverage and field ordering. Real BCL JSON round trips check the legacy eighteen-field shape. The outer legacy JSON is a labelled host fixture and the Unity Preserve attribute is stubbed; no IL2CPP VM execution is claimed.

Three new Editor tests exercise actual dnlib/Unity surfaces: each missing linked extension field, equally narrowed pre/post fields, and Unity serialization of the non-serialized view. They are authored, not executed in Primary. Local must run all three and retain their results. The existing eighteen-field tests are not relaxed.

Both candidate and control use the new package so this parser change does not create a package mismatch in their controlled runtime comparison. Fresh builds are mandatory; an old F build is not a new-package artifact.

## F-02 — M07 early-startup capsules

F's preserved `batch/commands/0031/command.json` invokes `run-m07-players.py` without `--early-capsule-root`. The launcher inserts the required early-startup arguments only when supplied. The native-ON callback reads those arguments before obtaining a result path. This is a sufficient source-level cause of the observed early refusal and missing managed result, separate from later parser errors. The sparse historical log cannot exclude additional causes.

The R02 M07 cell now invokes existing `prepare-h1-m07-control-capsules.py` with the exact new fixture, ON/OFF and replay receipts, then supplies its retained root to the launcher. Existing mode-specific selection, input hashing and rejection logic remain. Failed preparation prevents launch. Tests verify actual command ordering and arguments, and failure prevents any Player call. Local must retain capsule files, per-mode early receipts and semantic results and report any subsequent refusal separately.

## F-03 — count-family auditor dispatch

The batch dispatches `parameters` only to `audit-h1-count-fixtures.py` and `nested` only to `audit-h1-nested-fixtures.py`. Unknown families fail. Both generated families and their independent audits feed the unchanged 132-cell matrix. Tests exercise the actual batch dispatch; no auditor, fixture schema or expected case count is weakened. Real generation and Player execution remain Local work.

## F-04 — bounded linker restoration

Diagnostic and count build transactions now capture `Assets/HybridCLRGenerate/link.xml` alongside existing restorable inputs. The count path also invokes generation and therefore needs the same protection. Original/generated files are retained before any restoration and originals are restored byte-for-byte, including BOM and line endings.

Permission is deliberately narrow: unchanged bytes, or the observed empty linker expanding to one netstandard assembly containing exactly the fourteen preserve-all types recorded in F's `generated-link-after-diagnostic.xml`. Extra assemblies, types, attributes, duplicate types, non-whitespace content, declarations, links and concurrent edits fail. Well-formed arbitrary XML is not overwrite authorization. Unknown future generated output requires Primary review; Local must not expand this permission. Tests cover exact restoration, BOM/newlines and adversarial mutations. Normal source-authority checks continue to reject other unexpected changes.

## F-05 — stable forensic evidence retention

F analyzed E's original DLLs while they existed but retained only the old live paths. Those paths were unavailable at final sealing. An analysis receipt cannot substitute for its raw inputs.

The forensic cell now snapshots and reauthenticates exact live DLL bytes and original Git receipts into its new output before builds. Those copies, not the old paths, are retained for sealing. If a live DLL is absent, recovery is limited to E's exact Git-bound `LIVE_EVIDENCE_BINDINGS.json`, blob `7d2a0cf83d0550b875f8c1c078daeec3bc1832b5` at `1d7dc134003206ada8a92b50763ca2da7dc9530d`, its exact index/archive digests, the full existing archive audit and the exact original locator/member/size/hash. Origin, index, archive and selected copies are also retained. Existing corrupt live bytes do not fall back to a good archive.

There is no basename search, newer-run fallback, synthesized DLL or recreation of an old path. Archive-backed data is historical input, not historical Player execution promoted to current acceptance. Missing/incomplete forensic acquisition remains fatal to a complete seal. Independently valid cells may continue, but a partial forensic report or inventory-only return never becomes a full seal. Tests remove original paths after copying, recover from an actual test archive, seal copies and reject corrupt archives, indexes, locators and live data.

## Validation and next cycle

Final-authority R02 workflow 36372371088 passed Linux and macOS jobs; scoped legacy workflow 36372371077 and fixed-origin workflow 36372371129 also passed. Selected results: 203/203 Python tests in Primary and Linux CI; 72/72 repeated-subset macOS tests; 1,310 cross-language/schema/serialization checks; both 70/70 native matrices; managed 102/111/111 assertions; legacy 384/384 current and 6/6 historical positives. `PRIMARY_VALIDATION.md` and `F_PRIMARY_VALIDATION.json` retain full identities, artifact hashes, source authentication and limits.

The next Local cycle is one fresh 34-cell R02LocalBatch-v1 with both updated package checkouts and new controlled graphs. It preserves eight functional sidecars, four pilot plus forty formal A/B pairs, Editor/native/generated-transaction/M07/startup/failure/count/diagnostic/lazy-dense/capacity coverage, final source checks and complete sealing. All three new Editor tests and existing two R02 probe contract tests must pass. No non-trivial implementation, source-pin change, weaker check or case reduction is assigned to Local.

This is a focused Primary self-review, not the independent R02 stage review. Actual Unity compilation, linked proof, callbacks, sidecars, measurements and complete sealing remain unrun here. D1/D2 need measured disposition before H2. R02 and R03 remain unapproved. A rollback requires a new complete, explicit handoff tuple, never mixed package/source/build identities or deletion of retained evidence.

## Connector transport

Disposable branch `codex/connector-smoke-r02-f-20260927-3a8c` passed write/read-back in demo at `d6eb60b84af2f16c4914c7418ab528d214ee91b9` and package at `09c87163cb767453b71f2a7e49b7d015e89abd8a`. They are transport artifacts, not source/handoff commits, and must not be merged. They remain because the available Connector exposes no branch-deletion operation.
