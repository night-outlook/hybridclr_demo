# R03 host-only return: stale execution source binding corrected

**Primary reconciliation — 2026-10-15.** Disposition: corrected for pinned host verification only. This is not a corrected Unity Player, R03 acceptance, or a Human Review Gate.

## 1. Local evidence and root cause

The factual [LOCAL_VALIDATION](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](../../../../Handoff/RETURN_TO_WEB.md) record IR-LOCAL-HOST-EXECUTION-BINDING-01. The original consumed host batch ended FailedOrIncomplete: eight outer command receipts, seven Passed, one Failed. Both 25-case general-stream profiles were NotRun. Their component result/manifest were Unavailable because the harness failed before compilation. Other individual host components passed within their limited scopes. The immutable checkpoint is Docs/AssemblyShadow/History/M07R/R03/local-validation-host-only-20261015-fc0d3565/.

Original four execution-source pins: demo 19f7c8768c2596c876609da30d673afe7e30f3f3, HybridCLR 4b2774b066cfc6afd77a8c8aded6bda7ea574f55, Unity package 948c0e3b4f8891481301770115e8ba4945eea6de, native fc0d3565ecc5c9d1a31520a26ff3f9fda25bc98f. Canonical branch codex/assembly-shadow-r01b-h1. **New reviewed native source pin: 74dbdbea80d83923863303bd2b2c0a87f36541b1**. The final demo commit is verified from the remote and the separate Local handoff prompt.

Root cause: tools/r03/diagnostic_stream/run_tests.py had required the current AssemblyShadow::GetExecutionDiagnosticsJson C++ function to be textually identical to the immutable historical N_SNAPSHOT_PUBLICATION_91b7 source extract. The real function intentionally changed to use AssemblyShadowExecutionSerializer.h while preserving its JSON schema. The exact-source gate was obsolete; it had never reached a data parity check, so the failure did not establish a runtime defect.

Frozen original function SHA-256: 051497faf816e4094b8f4e8f194c5b877812cee034c6901c755e8b6efdff9c40. Reviewed current function SHA-256: 4829a3ae7b9b0df57d054738f99d940b4ad7644a364df0502c9976469819d372. Neither frozen function nor historical test script was modified.

## 2. Implemented correction and unchanged contracts

Primary changes in il2cpp_plus:

- tools/r03/diagnostic_stream/current_execution_producer.py pins source Git blobs of the entire current AssemblyShadow.cpp, new serializer header, writer header, and three immutable original N fixture/script files. It extracts real old/current C++ function bodies and compiles both against the SAME original synthetic VM mock.
- It compares all output bytes, not merely schema or hash, in three cases per strict/sanitized profile: original 1024-class 331078-byte specimen, empty inventory, and deterministic IL2CPP_DEBUG/class flags/static-storage/baseline-owner scenario. It requires six exact parity cases and 24 compile/process receipts; source mismatch, missing bytes, or incomplete coverage fails closed.
- tools/r03/diagnostic_stream/run_tests.py now requires separately pinned reviewed current and immutable historical function hashes, runs the unchanged original golden producer and this independent parity harness, THEN executes all retained 25 general-stream cases per strict and sanitized profile. On preflight source or compiler failures it preserves factual RESULT.json, MANIFEST.json and firstFailure instead of leaving the component status unavailable.
- .github/workflows/r03-general-current-producer.yml tests all cases on Apple Clang/macOS, Linux Clang and Linux GCC. It also deliberately modifies an isolated TEST COPY of the frozen fixture to prove the original source gate still fails closed with complete failed-component receipts.

Primary changes in hybridclr_demo: Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py includes current runner/fixture/producer and test source hashes before/after, and independently rejects incomplete or absent 25-case and six-parity receipts after a successful component exit. The multi-repository CI sparse checkout includes the original N fixture paths. Source pins match the new native publication.

**No product runtime, new formatter production source, managed Player, original verifier/guards, historical extracts, Local-owned report, or consumed evidence was changed by this correction.** Test attribution is confined to host-only code.

## 3. Verification

[CI 38689771914](https://github.com/night-outlook/il2cpp_plus/actions/runs/38689771914) finished **SUCCESS**, pinned to native source 74dbdbea80d83923863303bd2b2c0a87f36541b1. All three platform/compiler jobs passed the full general 25 tests in each profile, six exact old/current execution producer cases, and the deliberate frozen-source mutation rejection with an explicit FailedOrIncomplete component receipt. Earlier qualifying host CI 38689525864 also passed before addition of the negative fixture test; final CI is the authoritative result for this source pin.

The historic 331078-byte specimen is SYNTHETIC, not SNAP-01 actual producer size. The checked executable bodies use mock VM enumeration, not live Unity metadata. Bounded output tests do not bound VM acquisition, GC, allocator RSS, native engine scheduling, restart, or durability under power loss. CI does not replace the installed official Unity2022.3.62f2 managed/55-native compiler matrix or Player execution. Mac LeakSanitizer remains unavailable.

## 4. New Local Validation: host-only, then STOP

Read the updated Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md and exact four-commit handoff prompt. Run one NEW read-only batch from clean source checkouts into a never-before-used external host-only directory; do not retry or modify the consumed Local root. The batch jointly exercises current/frozen producer parity, original 25-case general suite per profile, codec 20/profile, POSIX transaction 27/profile, earlier sink 32 total, execution-formatter strict/sanitized compile/execute, and preservation checks. Collect exact source pins, commands, raw stderr/stdout hashes and complete manifests. Local may make only bounded environment adjustments and append factual Local-owned reports; nontrivial failures return to Primary.

No Unity Editor/Player, integrated SDK compilation, seven new Player roots, H2/X02/M08A, PureInterpreter expansion or Human Review Gate follows from host-only testing. Primary P1 coherent general/execution capture; P2 authenticated native/C# V2 transport and unchanged semantic verifier; E0/E1 supported Unity engine-owner safe point, callback drain/GC/finalizer maintenance and restart; and P3 source-bound integrated SDK/Player review remain open.

Preserve the original SNAP-01 14Passed/4Failed with three ON V1 slot14 scanned prefix262145 (full length Unavailable), 51213 uncapped engine reports/500ms/exit71, R03 full-stage FAIL/re-review NotRun, strict S historical custody Blocked (416844 originals,339367 survivors,77477 missing identities), and all acceptance flags false.
