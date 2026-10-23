# P1 admitted execution Local 20261023-b7e3 — raw PASS, required audit FAIL

## Current run — P1 admitted execution 20261023-b7e3 — Local FAIL; raw scoped PASS; required audit Failed

[Checkpoint](README.md), [Local outcome](LOCAL_RESULT.json), [Primary return finding](FINDING.json), [raw core result](batch/RESULT.json), [failed audit receipt](preflight/AUDITOR_COMMAND.json), [separate preservation](preflight/INDEPENDENT_PRESERVATION_AFTER.json).

| Actual repository | Branch | Exact execution commit |
| --- | --- | --- |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | codex/assembly-shadow-r01b-h1 | 49c6b62d38d7668be10004ac1e5a030d74894f09 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | codex/assembly-shadow-r01b-h1 | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

**Local result FAIL: required independent audit incomplete. Original raw aggregate remains PassedSourceHostAndSDKOnly with 25/25 Passed.** This cycle performed one actual 15-test prerequisite, one unchanged preparation, ONE core batch and ONE unchanged auditor invocation. No source/tool/SDK/compiler/TMPDIR/timeout modification, retry, Unity Editor/Test Runner/Player/product linking or milestone advancement.

**Fresh prerequisite and preparation:** actual macOS suite Passed 15/15, zero failures/errors/skips, with inherited TMPDIR /var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T/ resolving to /private/var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T; real inherited alias present=True. Both new alias leaves ran alongside the original13. PREPARATION.result=PreparedNotExecuted correctly describes preparation only; its coreInvoked/sdkCompiled flags were not rewritten after later core execution. It created exactly four initial preflight files; collector SHA256 06c76817c9bb200bec9ea94a6664a2944daa538279b7fa6614fa4b12f0738dc6, unchanged copied auditor SHA256 2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0. E1e5 original helper SHA256 remains 73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd. The generated collector changes only its two missing early opaque admitted literal removals, retains the later correct reconstruction and original Git blobs. Actual prerequisite/preparer argv/PID/times/exits/full streams are PREPARER_COMMANDS.json and the associated preflight records. No TMPDIR override.

**Actual core:** PID 99511, exit 0; UTC 2026-10-23T09:30:09.614474+00:00 → 2026-10-23T09:33:36.036076+00:00; America/Los_Angeles 2026-10-23T02:30:09.614474-07:00 → 2026-10-23T02:33:36.036076-07:00. Exact argv: python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --expected-demo 49c6b62d38d7668be10004ac1e5a030d74894f09 --expected-native e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261023-b7e3 --sdk-scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261023-b7e3. Unity2022.3.62f2 is a read-only SDK anchor, never launched. Environment/version receipts: preflight/python.json, os.json, kernel.json, clang.json, sdkpath.json. All original direct raw outputs and warnings remain unchanged.

| Core component | Raw state | Raw inner verdict |
| --- | --- | --- |
| command-failures | Passed | PassedWithinHostScope |
| legacy-host | Passed | PassedHostOnly |
| metadata-gate | Passed | PassedWithinHostScope |
| bounded-class | Passed | PassedWithinHostScope |
| bounded-physical | Passed | PassedWithinHostScope |
| bounded-first-use | Passed | PassedWithinHostScope |
| owned-general | Passed | PassedWithinOwnedHostScope |
| live-general | Passed | PassedWithinInactiveSourceHostScope |
| owned-execution | Passed | PassedWithinOwnedExecutionHostScope |
| empty-live | Passed | PassedWithinInactiveZeroClassHostScope |
| opaque-inventory | Passed | PassedWithinInactiveOpaqueHostScope |
| physical-membership | Passed | PassedWithinInactivePhysicalEnumerationHostScope |
| owned-physical-names | Passed | PassedWithinInactiveOwnedPhysicalNamesHostScope |
| owned-physical-json | Passed | PassedWithinOwnedPhysicalNamesJsonHostScope |
| live-owned-physical-json | Passed | PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope |
| observed-type-shape | Passed | PassedWithinObservedTypeShapeSourceHostScope |
| live-type-shape-census | Passed | PassedWithinInactiveLiveTypeShapeCensusHostScope |
| observed-type-shape-json | Passed | PassedWithinOwnedTypeShapeJsonSourceHostScope |
| vm-shape-json | Passed | PassedWithinInactiveVmShapeJsonHostScope |
| admitted-execution | Passed | PassedWithinInactiveMetadataAdmittedExecutionHostScope |
| bounded-status | Passed | PassedWithinHostScope |
| bounded-inventory | Passed | PassedWithinHostScope |
| frozen-v2 | Passed | PassedWithinInactiveHostScope |
| managed-sdk | Passed | Passed |
| native-sdk | Passed | Passed |

**Observed core obligations:** original85 distinct failure-contract tests Passed in modules 5+14+44+10+12; all eight independent outer inventory flags are true in their actual command receipts. Original strict/sanitized case inventories 28/21/12/15/16/16/16 remain. New admitted-execution ran all **nine strict+nine ASan/UBSan** cases and five actual version/compile/run commands. The actual production wrapper .inl and actual MetadataLifetime Gate compiled under host fixtures with an explicitly mocked legacy getter. This is host Gate/RAII/error/initial-epoch/drain behavior, **not genuine original getter, process Shutdown, pointer allocator/lifetime, coherent VM epoch or full V1 proof**. The original production getter was not enabled through normal paths.

Managed compilation produced five real positive products from original428 inputs, with canonical nested managed-sdk/build-api/results.json/returned path/hash/outer binding. The distinct original OriginalUnsignedCounts control returned expected exit1 with exactly two CS0266 and no DLL; it is not a positive build. Native compilation recorded **100/100** actual Apple arm64 C++17 -fsyntax-only commands, original20 translation units×five modes, including actual complete AssemblyShadow.cpp and typed admitted method probe; no native product link. Managed warning occurrences=0; native=742. Full streams and product/source/SDK hashes are retained externally and copied/bound as text receipts.

Final core Git authority: **20/20** actual direct commands, five per four repos, all Completed/exit0, unchanged120-second limit, no timeout/nonzero/unknown lifetime or retry. Full START/RESULT/stdout/stderr receipt files are retained. Raw sourcePreserved=true, complete fourRepositoriesAfter, postflightError=null, stoppedAfter=null. RESULT and MANIFEST commandLifetimeUnverified are both false; inventoryScope=CompletedBatchFiles. Git direct PIDs are Unavailable_NotEmitted; core/collector/auditor process PIDs and times are recorded. descendantQuiescenceProven=false remains a nonclaim. Separate raw-receipt observations verify source/hash joins without pretending the failed full auditor Passed.

**IR-LOCAL-P1-ADMITTED-AUDIT-ROSTER-01 — reproduced required-auditor failure.** Exact command python3 -B /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/audit.py; PID 1519, exit1; UTC 2026-10-23T09:33:48.468705+00:00 → 2026-10-23T09:33:52.778244+00:00; America/Los_Angeles 2026-10-23T02:33:48.468705-07:00 → 2026-10-23T02:33:52.778244-07:00. The auditor is byte-identical to PREPARATION.independentAuditSha256=2b43453f00fd74c1692d55d3c10b7351df45a0a82d08cf551deb0282862848a0. Its line189 requires componentCount=attemptedComponentCount=25, but line190 compares actual names to a literal **24-name** list omitting admitted-execution. Actual25 order is exactly that list plus admitted-execution between vm-shape-json and bounded-status. The one-time auditor therefore asserts before its later checks. Raw audit.log SHA256 73f06a599b259796677b4a6761618cb2ed4f72b319654bfbf6cf9a4692d064cb. See FINDING.json for exact expected/actual ordered lists, source assertion, reproduction argv and relevant hashes.

The first failure is an **auditor roster contract defect**, not an extra/unexpected core component or demonstrated product/native/SDK failure. The source-bound preparer copies the archived independent auditor unchanged by design. All later auditor statements after line190 are **NotRun** in this execution. Partial receipts emitted before the assertion remain factual partial evidence. No EVIDENCE_AUDIT.json or whole-audit PASS was fabricated; no code was fixed or re-executed.

**Primary direction:** derive a successor auditor whose exact ordered identity assertion includes admitted-execution in its real slot and still requires all25 components. Preserve exact identity/order checks, all original contracts and archived bytes. Add regression coverage for the actual25 roster and refusal of missing/extra/reordered identities; do not drop the assertion or relabel raw evidence. Full independent source/inventory/managed/native/Git evidence validation remains required after the fix under a new explicit handoff. Later auditor defects are possible because those statements were not reached. This consumed core and failed audit are not retried by Local. No native product change is justified by this failure.

**Required after checks completed:** preparer --verify-after exited0 and BLOCKED_HISTORY_AFTER.json=Preserved for e1e5's42 files and unchanged generated scripts. A separate independent full before/after collector verified all 2405 SDK files / 316062203 bytes and exact inventory, current source bindings, **22 consumed P1 raw/scratch/audit sets, original24 checkpoint sets and88 historical negative symlinks**. Separately e1e5 blocked checkpoint/external collector and 6c72 blocked checkpoint/full retained test-error/dispatch/publication evidence match their own before hashes. E1e5 raw/scratch remain absent and its historical preflight exists unchanged; 6c72 preflight/raw/scratch remain absent. All four exact clean source heads/live remotes matched after checks. These independent preservation receipts do not repair the required auditor's failure.

Preserve e1e5 PrerequisiteBlocked0/25; 6c72 PrerequisiteBlocked12Passed/1ERRORof13 and0/25; 7896 PASS; 7c2c PASS; 82dd FAIL/FailedOrIncomplete with original timeout, sourcePreserved=false and fourRepositoriesAfter=[]. Preserve original findings and manifest-lifetime correction dispositions. This new Local outcome is **FAIL with raw PassedSourceHostAndSDKOnly**, not another Blocked/NotRun batch and not a full accepted Local PASS.

**Custody:** raw RESULT SHA256 f762d292d9601e620a83ecd79cc5e3c5ab85b0ea0a3813fbf472bd716eb1c7e6; raw MANIFEST SHA256 4b286c29a7ef36ec4377642b6009804ad532b0ae3166c186866fe74f4246130e. Complete raw /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261023-b7e3; SDK scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261023-b7e3; independent evidence /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3. COPY_BINDINGS.json authenticates copied bytes and lossless UTF8 JSON encodings used only for Git whitespace-safe new checkpoint copies; all external raw bytes unchanged. SDK/vendor/DLL/executable binaries and deliberate historical negative symlinks stay external. Checkpoint MANIFEST.sha256 binds Local documents/copies, not product acceptance.

**Exit:** Local Validation → Primary Implementation, FAIL. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Canonical generic TypeKeys, pointer provenance/lifetime, coherent VM epoch, full execution V1, original getter integration, real GC/RSS/Shutdown and Player remain unproved. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. No H2/X02/M08A, Human Review Gate or further milestone.
