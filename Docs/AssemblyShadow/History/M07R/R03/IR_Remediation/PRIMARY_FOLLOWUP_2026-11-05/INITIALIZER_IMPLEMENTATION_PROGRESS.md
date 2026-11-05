# R03 Primary Implementation — initializer diagnostic source checkpoint

Date: 2026-11-05 UTC. Scope: IR-R03-02 initializer-control and initializer-failure. This is source/host preparation only, not Unity or runtime acceptance.

## Source tuple

Branch: codex/assembly-shadow-r01b-h1.
Source implementation began at demo ccbbf1858dab82bcb054cc2a124227ebd8f3665b. Latest source/CI commit before this document: 18374896b69d623e884e87361cf44c1404d4df7a.

Other repositories remain unchanged:
- night-outlook/hybridclr 4b2774b066cfc6afd77a8c8aded6bda7ea574f55
- night-outlook/hybridclr_unity 948c0e3b4f8891481301770115e8ba4945eea6de
- night-outlook/il2cpp_plus 41764ae1eeefb33b05966e7f7676e52aae39c340

## Implemented source

The existing separate InitializerNativeTargetFixtures.cs produces two deterministic Methods.dll variants. Their IL calls R03_IRW_OnPrepared after actual direct/delegate/generic increments and PreField=3. The control initializer returns and the failure initializer throws R03IR.InitializerFailure.AfterPublication.V1.

| Case | Exact DLL SHA-256 | MVID |
| --- | --- | --- |
| initializer-control | f909d3a4dd2ae3e561f1c0a2e25b50009203e440ce35a743afae937073e294a8 | c8dff3d3-01e2-4b9f-0969-87c69d2b9e73 |
| initializer-failure | 1cf13922d9f5798873a2581867f4dc0ea7415bd5ceee815e1b9489d99ce4937d | 3ec341b2-04be-2d14-1904-fac3f8a6a6c4 |

Each is 2,560 bytes. These are new host-generated targets, NOT replacements for original S.

R03InitializerPreparedProbe.cpp is the previously added native observer: it only binds while Committing=5, pins the actual shadow object after verifying stable=3 and positive return counters, then permits a primitive postterminal field read without new managed reflection.

The following new source files are published in Tools/AssemblyShadow/R03IR:
- PlayerProject/R03InitializerObservationPlayer.cs: separate request arguments and real CommitTransaction path, expecting 0/Committed=6 for control or 19/FailedAfterCommit=9 for failure, plus AOT canary attempt.
- PlayerProject/R03InitializerObservationWriter.cpp: exclusive preopened native diagnostic receipt; requires stable field 3, positive mask 15, one callback, unchanged AOT canary, exact state.
- prepare_initializer_sources.py: composes original diagnostic overlay plus new observer and writer in a freshly isolated UNBUILT ON-only project, preserving the original overlay prefix and updating source hashes. Rejects source tampering, prior builds, disabled profiles and reused roots.
- verify_initializer_observation.py: strict typed non-authorizing consumer for this distinct diagnostic record.
- NativeDiagnostics host drivers/tests and corresponding CI workflows: exact source compilation and negative controls on two OSes.

The diagnostic output kind is R03IRInitializerCommitObservationV1 with NativePreopenedInitializerObservationV1 transport, NOT the final NativePreopenedSnapshotV2. Its fields explicitly set firstRecoveryAuthenticated=false, completeDiagnosticsAuthenticated=false, nativeV2TransportImplemented=false, runtimeAcceptance=false, R03Accepted=false and H2Passed=false. The existing V1/K result and V2 verifier are unchanged.

The compile-only Player API harness now includes R03EngineFrameDispatcher.cs and the new initializer Player, and has the necessary GameObject/MonoBehaviour/DoNotDestroyOnLoad stubs. Its source checkout is narrowed without dropping file-identity checks.

## Actual host/CI evidence

| Source-only verification | Actions run | Evidence |
| --- | --- | --- |
| Deterministic native initializer fixture generation | [41995263499](https://github.com/night-outlook/hybridclr_demo/actions/runs/41995263499) | Ubuntu and macOS PASS |
| Native diagnostic writer with real C++11 compilation and host fakes | [41996267139](https://github.com/night-outlook/hybridclr_demo/actions/runs/41996267139) | Ubuntu and macOS PASS |
| Source project/composite-overlay preparation after prebuild admission hardening | [41997475267](https://github.com/night-outlook/hybridclr_demo/actions/runs/41997475267) | Ubuntu and macOS PASS |
| Exact native prepared-field observer compiled against C++11 host models | [41997019776](https://github.com/night-outlook/hybridclr_demo/actions/runs/41997019776) | Ubuntu and macOS PASS |
| Managed Player API compilation against pinned package | [41997200242](https://github.com/night-outlook/hybridclr_demo/actions/runs/41997200242) | Ubuntu PASS |
| Typed diagnostic-schema negative tests (NOT V2) | [41997699439](https://github.com/night-outlook/hybridclr_demo/actions/runs/41997699439) | Ubuntu and macOS PASS |

None of these source-only checks compiles Unity IL2CPP generated C++, links the new native observer into a real GameAssembly, or executes a Player. No native device, real GC relocation, Unity callback, or first-failure evidence is claimed.

## Remaining implementation and acceptance boundaries

1. A distinct source-bound initializer coordinator/build verifier must consume the composite overlay and actual generated target receipts. The existing K source-bound verifier must not be relaxed or reused as fresh evidence.
2. Test actual IL2CPP native compilation, __Internal int(void) P/Invoke bridge, real postpublication initializer callback, native field read, output sealing, BuildReport and new Player PID under a future explicitly admitted Local cycle.
3. Implement complete native V2 snapshot, full first/final recovery and initializer sentinel detail, bounded complete general diagnostics, original source/build/launch/overlay bindings and postterminal active-shadow method/delegate rejection with independently observed field invariants. The current diagnostic record is NOT V2 acceptance.
4. The genuine physical captured-generic error-15 Player witness is still absent.
5. IR-R03-01 full original S compiler/source-to-object/link/process chain and other R03 RC requirements remain open.

Canonical Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md remains CLOSED (K consumed). No new Local execution has been authorized, and no historical raw or product VM source was changed. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false, fullLegacyRegressionAcceptance=false, PureInterpreter disabled. Do not begin H2, M08A, X02 or SNAP-01.
