# R03 post-review Primary preparation — 2026-11-04

Status: implementation preparation, not finding closure or Local execution authority.

## Basis and immutable boundaries

The user requested Primary continuation after the [November 4 re-review](../../S_Reconciliation/R03_RE_REVIEW_2026-11-04/REPORT.md). Entry tuple: demo b17c73372e3d735d47b52aa85adb548b0e8a2a37; hybridclr 4b2774b066cfc6afd77a8c8aded6bda7ea574f55; hybridclr_unity 948c0e3b4f8891481301770115e8ba4945eea6de; il2cpp_plus 41764ae1eeefb33b05966e7f7676e52aae39c340. All use codex/assembly-shadow-r01b-h1.

IR-R03-01 and IR-R03-02 remain High/NeedsEvidence. K's focused PASS is historical evidence for its executed tuple, not coverage for new fixtures. D1=A/D2=A remain unchanged. Original S, K, failed attempts and prior reviews are read-only. No H2, X02, M08A, production shutdown or global-epoch claim is added.

## A. Actual terminal-producer fixtures

Extend the existing R03 PlayerFixtures generator additively; preserve its original --output and --ir-target behavior and deterministic IR byte identity. New fixtures must be distinct, generated in unused output directories, and explicitly marked host/source preparation rather than Player validation.

Captured-generic preparation must expose a real generic method whose body mutates the existing primitive instance field. The eventual native witness must obtain an actual runtime-owned constructed MethodInfo with a physical baseline type argument; a copied/fabricated MethodInfo, ordinary old owner rejection, or direct write to a terminal state is not the intended producer. A healthy corresponding call must execute before the invalid captured argument is attempted. The actual production CapturedArgumentVisitor and first-failure record must be observed.

The post-publication initializer witness must use an actual module initializer reached by the production Commit path. Prewarming active Shadow objects before publication would violate the design. Instead, the initializer must execute the positive side-effecting method while publication is already visible, make the observation available to a test-only native adapter, then throw an exact sentinel. A paired otherwise-identical initializer must return normally. The adapter must pin real objects and capture exact method/field identity before the throw; it cannot manufacture a successful observation. After Commit returns failed, the same supported cached entry paths must be attempted, with no additional body side effects and no replacement of transaction.recoveryTerminalError.

The fixture generator can prove emitted IL, stable bytes, metadata shape, and conservative V1 metadata admission. It cannot prove native construction, Commit behavior, actual bridge dispatch, or rejection. Those remain NotRun until the adapters, verifier, source freeze and a separately authorized Local run exist.

## B. Original-S material generated-source audit

Reuse the existing fixed-fc55 original-S source workflow and provenance utilities. Authenticate the original index and the four occurrences of two unique generated tables; export the exact unique bytes in a bounded compressed artifact so reviewers can inspect them without the oversized full audit ZIP. Export is a representation of original bytes, never a new compiler output.

Inspect the actual generated syntax before defining a bounded parser. Validate material table declarations, initializer membership/counts, declared function targets and index bounds where the captured tables provide them. Retain exact source and line/hash anchors and negative parser tests. Unsupported syntax must fail explicitly rather than be silently ignored.

A table consistency result is not proof that these sources were compiled or linked into an original Player. The final source-to-build-to-executable audit still needs compiler/link receipts and the exact source/resource/launch joins, with unavailable inputs explicitly classified. Do not rerun Unity merely to replace a historical documentation or transport gap.

## Execution sequence and stop

1. Publish this bounded design and the read-only generated-byte export through the Connector.
2. Inspect exported exact source and implement/test a bounded structural auditor.
3. Add the missing terminal-producer fixture preparation to the existing generator; compile and verify actual host outputs where available, including the old IR target byte regression.
4. Review the changes and record exact checks, failures, repairs, commits and unresolved integration requirements.
5. Keep the canonical WEB_TO_LOCAL.md CLOSED. Do not allocate a new Local cycle, root, retry or runnable Unity command in this preparation slice.

Source-only GitHub Actions and isolated host unit/compiler checks may execute. Their results must never be described as a Unity Player run or independent stage approval. There is no local Unity installation in this Primary environment.

## Connector bootstrap

All four repository identities, feature refs and write permissions were verified. The demo write/read-back smoke passed at 977cd3832e95c6ad3f310ae467231b009ef8f77b on disposable branch codex/assembly-shadow-smoke-20261104-primary-rereview-7d32, based on b17c73372e3d735d47b52aa85adb548b0e8a2a37. The branch is not merged and remains separate. Only demo changes are planned in this slice.

R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; qualificationApproved=false; runtimeAcceptance=false; fullLegacyRegressionAcceptance=false. PureInterpreter expansion remains disabled.
