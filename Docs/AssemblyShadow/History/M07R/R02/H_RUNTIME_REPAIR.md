# R02 batch-H runtime and verifier repair

## Authority and historical result

Input Local return: `d33792957303488e03529c945ac01ce0eedd660b`. The immutable checkpoint is `local-validation-20260928-batch-h-return-required/` in this directory. H recorded 25 Passed, 5 Failed and 4 Blocked cells with a complete independently audited seal. Its 132 count cases and 1,119 Editor cases passed, but candidate P01/P03 warm admission, M07 aggregate verification, startup aggregate verification and diagnostic provenance failed. Performance and D1/D2 remained blocked. Historical reports, raw results and seals are not rewritten.

This is a bounded R02 correction. HybridCLR and the managed package remain at their existing pins; candidate IL2CPP changes. Control keeps the H1 runtime, not the earlier R02 candidate. Final exact source, control and runtime identities are in `source-targets.json` and the live handoff. No R03 entry or performance acceptance is granted.

## H-01: completed layout is not baseline initialization

H's two 10,000-allocation rows recorded 10,000 admission misses, proof attempts and unready decisions. The source marks a trace incomplete when either checked class lacks `size_inited`. The raw counter evidence does not identify the exact source/target class. The correction follows the actual metadata construction invariant rather than forcing the old baseline to initialize.

At the reviewed native input, `libil2cpp/vm/GlobalMetadata.cpp::FromTypeDefinition` copies concrete AOT definition sizes from `s_Il2CppMetadataRegistration->typeDefinitionsSizes`; `GlobalMetadata::GetFieldOffset` reads compiled field offsets for AOT classes. `Class::SetupFields` later handles lazy field/static setup and sets `size_inited`. Requiring that later flag for an intentionally untouched AOT baseline can prevent a valid, already completed comparison from ever becoming a certificate. Calling SetupFields or initializing the baseline is not an acceptable repair.

`AssemblyShadowLayoutReadiness.h` recognizes only a concrete, non-generic, non-array, non-interpreter AOT definition with an image, metadata handle, managed class/value-type kind, non-pending size setup and a compiled size at least the object header. An already size-initialized baseline keeps its previous readiness. Constructed generics, arrays, generic definitions and interpreter layouts do not gain this alternative. The active target still requires `size_inited` for publication.

`CheckLayout` continues to prove declaration/kind, size, packing, offsets, fields, interfaces and parent compatibility. Only trace completeness uses the stronger distinction. Failed or partial proofs do not publish. Structural generic-definition comparison is not relabeled as a physical constructed layout. The existing composite unready rejection remains unchanged. Full physical class keys, metadata lock ordering, publication ordering, per-hit baseline/cctor/vtable checks, generation/private-context checks and poison rejection are unchanged. No baseline field or static storage is touched to create readiness.

A bounded level-2 diagnostic emits at most sixteen `[R02LayoutReadiness]` records per process for cold source/target decisions. Records contain pointers, tokens, image identity, readiness/pending flags, shape, sizes and site. They do not call managed logging, initialize classes, allocate cache permissions or change JSON schemas. Levels 0/1 omit them. These observations are diagnostic, not a claim that the specific H class has been identified. Preserve stderr/Player logs in the next run. Cold logging overhead remains part of the measured candidate behavior; it is not subtracted or attributed to control.

The deterministic source recipe includes the bounded correction in `tools/r02/h_layout_repair.py`; `finalize_sources.py --verify` still authenticates immutable H1 inputs and all protected guard bodies. Local must never run its preparation mode to make an invalid checkout pass.

The actual production proof-cache header regression now tests a cold fixed AOT definition, an initially unready active target, later single publication, 10,000 warm allocations without further proof construction/allocation, and subsequent baseline-use and poison rejection. Negative shapes, missing metadata, pending and undersized layouts are covered. These synthetic physical-class tests are not IL2CPP VM execution. Existing real P01/P03 warm assertions remain unchanged and mandatory.

## H-02/H-03: strict current M07 and startup schema

The historical M05/M07 type-info verifier expects eighteen fields; R02's known native extension adds exactly thirty-three fields under `r02`. The managed package already understands it. The current batch now enters `R02/verify_regressions.py`, with exact candidate source authority checked before and after validation. Historical verifier modules are not edited.

The adapter validates every known extension field, exact UInt64 values, booleans, schema version, level, capacity, coverage and accounting scope before an in-memory projection delegates the eighteen-field and semantic checks to the original M07 validator. Raw files, original JSON strings, process receipts and hashes are never rewritten. Unknown/missing/duplicate fields fail; zero/false fields are mandatory. Current M07 positive observations require default level 2. Feature-OFF validation remains unchanged. No cross-counter equalities are imposed on the non-atomic native snapshot. The actual writer/parser host contract at all three levels also exercises this Python extension validator.

The scope restores the original function even after failure. It is used only in the single-threaded synchronous current verifier process, not as a permanent generic unknown-field permission. The wrapper refuses incomplete matrices and writes a separate source-bound `.r02-schema.json` receipt as well as the original strict output.

Startup dispatch now invokes the existing `r01_early_results.main` through that wrapper, not the nonexistent `verify-r01-early-results.py`. All eleven default modes and each complete early profile are required. Its original capsule, inputs, logs, PID and positive/negative checks remain. M07 still requires its full fourteen modes; failure/recovery retains its separate existing verifier. No historical H Player execution is promoted to new-source evidence.

## H-04: diagnostic artifacts honor existing provenance

The diagnostic Player is now built into a new canonical `Builds/AssemblyShadow/R01B/<unique-R02-id>-diagnostic/Player.app`, separate from the current controlled Player. The temporary receipt, planned output and recovery evidence stay under the batch-scoped `_temp` root. Existing output roots and linked parents are rejected before Unity runs. The returned receipt must identify the planned Player exactly before the unchanged strict diagnostic verifier accepts it. The entire Player root is retained for sealing. Linker/scene restoration and strict dirty-source rejection are unchanged.

This fixes the producer path rather than broadening `r01b_diagnostic_inputs.py`, copying a previous Player, relabeling a `_temp` binary, or skipping its distinct-build proof. Lazy/dense and ordinary/mixed-capacity still require a valid fresh diagnostic receipt.

## Tests, review and Local boundary

Eighteen new `test_h_regressions` tests exercise strict extension fields and values, original-verifier rejection/restoration, unchanged raw strings and legacy semantics, existing startup dispatch, complete matrix requirements, authority failure, distinct verifier routes and diagnostic output/retention/recovery. Synthetic module/Unity mocks are explicitly labeled. The two existing batch/contract test modules were updated for the new entry point and valid synthetic wire data, not to waive assertions. The focused macOS job also runs H tests.

Primary local results and final CI identities are recorded in `PRIMARY_VALIDATION.md` and the new structured validation record. This document is a focused Primary self-review, not the independent R02 stage review. Real native VM compilation, warm certificate behavior, M07/startup raw verification and distinct diagnostic artifacts remain Local requirements.

Run one fresh 34-cell batch with the newly frozen candidate and matched control. Preserve all A/B/C/D/E/F/G/H and H1 evidence. All eight sidecars must pass before the unchanged four pilot plus forty formal A/B pairs. Require five exact Editor contracts, native/generated-transaction, M07/startup/failure, fresh count132, diagnostic/lazy/dense/capacity, final authority and complete sealing. Never reduce cases or change warm expected values to obtain a pass. D1/D2 require measured disposition before H2. R02Accepted=false; mayEnterR03=false.

Rollback requires an explicit newly published complete source/control/native tuple. Do not reset branches, mix old builds with new pins or delete failed evidence.

## Connector transport

Disposable branch `codex/connector-smoke-r02-h-20260928-b71c` passed exact write/read-back in demo at `3ac88bad4b635b9cb56d853b354f3497b525d85b` and IL2CPP at `fe0d49580d4aa9df099edaf99629c79259ca5f5a`. These remain transport artifacts because no branch-deletion operation is exposed. They must not be merged or treated as implementation/evidence commits.
