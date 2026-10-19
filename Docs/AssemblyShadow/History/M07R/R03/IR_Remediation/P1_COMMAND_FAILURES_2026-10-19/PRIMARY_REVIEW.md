# Primary source review and Local reconciliation

**Disposition: local source/test increment passes its host-only checks; publication blocked; not handoff-ready.** This is Primary self-review, not an independent full-stage reviewer or a Human Review Gate approval.

## Reconciliation of Local return

At published demo `d49b85bfd633f25b9f8351e03efd406c6f1df53b`, Local reports `20261018-5667` PASS / PassedSourceHostAndSDKOnly: 12/12 outer cells and 75/75 official native SDK syntax configurations; no new substantive Local defect. Actual execution used demo `25d5986c5919ab70119364ce36e8b670329ad5b0`, not the later report publication commit. The other three execution pins match the base table in DESIGN.md.

The run's UTC timestamps in Local evidence are 2026-10-19T02:35:13.828215+00:00 through 2026-10-19T02:37:49.485117+00:00. These are retained reported timestamps, not fresh execution here. The original batch RESULT SHA-256 is `ca50378cb0bb6fc414d274255cad925606673c9c7dc275a4e0fb19c545d384cc`; original MANIFEST SHA-256 is `3673391f85aa6318a03129e2d459e2aebde33dd05fb0bd84dfb93e9957ee1af9`. The complete 3,759-file external inventory and Unity vendor bytes were not independently reacquired/rehashed in this cycle. This reconciliation consumes the accurately scoped Local report; it is not another SDK run or expanded acceptance.

Canonical sources: `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and `History/M07R/R03/local-validation-p1-live-general-20261018-5667/` at the fixed demo base. Local-owned reports and checkpoint files remain unmodified.

## Findings addressed

| Finding | Evidence and correction | Disposition |
| --- | --- | --- |
| P1-CMD-01 | Native timeout discarded available streams and command receipt; actual Python child reproduction. Finally-persisted exact streams, partial/unavailable markers, unknown exit, propagated failure. | Corrected in candidate; real subprocess regression passed |
| P1-CMD-02 | Outer timeout returned and permitted later work. Explicit fail-stop, NotRun receipts, no postflight subprocesses after unknown lifetime; failure aggregate and cancellation code retained. | Corrected in candidate; actual main/control tests passed |
| P1-CMD-03 | Nonmanaged result parse/hash used separate reads and lenient JSON. Strict canonical regular-file read, same bytes parsed/hashed, duplicate/nonfinite/redirected records refused. | Corrected within completed-private-output scope |
| P1-CMD-04 | Missing compiler/source loss could prevent RESULT; compiled-source flags were unconditional. Failure summaries and observed source state retained, compilation claims conditional. | Corrected in candidate; controlled native main tests passed |

## Fresh checks actually performed

The integrated candidate harness ran **53/53 unique unittest methods**, 0 failures, 0 errors, 0 skips, with all nine bound source files unchanged. Its result, full verbose test IDs/log and manifest are retained in `evidence/final-contracts/`. Three additional harness admission controls reject a reused output, a source override, and an output under source. All Python files and both added workflow embedded Python scripts parse. Patch/delivery integrity checks are recorded separately in STATIC_REVIEW.json.

The baseline execution script is retained verbatim as `evidence/executed_reproducer.py.txt`; it documents the original source-mirror layout and is not a Local validation entrypoint. The controlled timeout tests launch Python children, not Unity or native runtime test binaries. Existing managed producer receipt expressions are exercised from the actual unchanged `build_api.py` AST, with compilation mocked. The original native C++ live-general fixture was not newly compiled or run here. Native C++/ASan/UBSan, macOS host execution, installed Unity SDK compilation, GitHub CI, Player/link/runtime validation, and Human Review remain **NotRun in this cycle**.

## Source review boundaries and residual risks

The real VM .inl and its associated production headers remain untouched. The exact native source method identity retained by Local (`232bd739bc6a54e8047118fbba8eb301a58f67e869ca8ce974902c8c382244a8`) therefore belongs to the unchanged runtime source, not proof of a fresh compiler run. All original native case names, compile flags, sanitizer environment and source-provenance checks in the runner remain unchanged. Managed compiler helper, native SDK compiler helper and managed receipt validation body remain unchanged. The first added batch component uses the new tests; old components are retained in order.

No quiescence or fully bounded nested-process teardown is claimed. `subprocess.run`/OS interactions can still outlive the requested timeout when unrelated child sessions or inherited pipes are involved; witness-free completion does not establish a process-tree proof. Receipt writes may fail if storage fails. Only this focused candidate is completed; the overall P1 product work is not declared complete.

P1 coherent VM-wide epoch/ABA protection, class-pointer provenance, complete execution/R02 capture, original live getter integration, worst-case allocation/GC/RSS, and true lock/Shutdown safety remain incomplete. P2 authenticated native/C# V2 transport/semantic integration remains NotIntegrated. E0 supported Unity2022.3.62f2 StandaloneOSX engine-owner safe point remains Blocked/Unavailable; E1 is BlockedByE0. Full P3 linked Player/runtime acceptance remains incomplete. These are Primary-owned work, not a Local implementation assignment.

The latest `20261018-5667` Local source/host/SDK PASS is consumed. The `20261016-3dc9`, `20261016-f598`, and `20261016-0620` source/SDK PASS cycles and `20261016-0a0b` FAIL remain unchanged. SNAP-01/N/M/K/I/E FAIL, historical R02 source-fingerprint FAIL, original strict S custody Blocked, and independent full-stage R03 FAIL/re-review NotRun are not reclassified.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion remains disabled.

## Publication blocker and next Primary action

Current connector discovery returned no create/update/commit/ref mutation functions. The GitHub plugin is already enabled/installed; this is unavailable write functionality in the exposed session, not a demonstrated repository-permission denial. Earlier disposable-branch smoke tests are historical and are not reused as current write readiness.

All new files and modifications are uncommitted/unpushed. Restore a session exposing GitHub connector mutation actions, revalidate the remote base and intended changes, perform the required disposable write/read-back test through that transport, publish source/tests/workflows/evidence, and verify their exact remote commits. Then Primary must publish a final executable handoff with exact new source/transport pins and fresh evidence roots. Local must not be asked to apply these patches, repair the implementation, or infer a new source pin from old evidence.
