# Primary reconciliation of G-COMP — publication 4808743f

Owner: **Primary Implementation**. This is a scoped source/evidence reconciliation, not the independent full-stage review or a Human Review Gate. Authority is the immutable G publication `4808743fcbbc2075b9be305140bdf5ffa8583b0f`, with actual compiler execution at demo `d7f46bfd090313b41b38175ce1196f14484a3d1e`.

## Disposition

**G-COMP Passed is supported within its compile-only scope. The official managed/native compilation prerequisite is closed for the exact compiled source tuple.** A separately published H runtime assignment may use the unchanged executable sources after fresh source, historical-evidence preservation and storage admission. No runtime result or full-stage acceptance follows from this disposition.

No production source, Player, fixture, compiler script, runtime runner, source pin, guard or test expectation is changed in this reconciliation cycle. Feature-branch changes are exclusively current Primary documentation and new review evidence under Docs/AssemblyShadow. Local-owned reports and all previous checkpoint bytes remain unchanged. Two isolated CI workflows on the disposable smoke/audit branch inspect the immutable G evidence and existing host tests; they are not runtime source or Local handoff revisions.

## Exact compiled/source tuple

All repositories use `codex/assembly-shadow-r01b-h1` at their owning checkouts beneath `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`.

| Repository | G actual compilation source |
| --- | --- |
| night-outlook/hybridclr_demo | d7f46bfd090313b41b38175ce1196f14484a3d1e |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | c386cdd1e8942561f1d1e1fada52d21ca524f174 |

The subsequent G publication and this review's final documentation publication are distinct transport revisions. Do not execute from a smoke/audit commit. The final short Primary handoff identifies the exact latest demo transport HEAD. Executable equivalence must be proved against the above compiled source, not inferred from ancestry alone. All four commit values must be full 40-character hexadecimal strings. G's source-authority receipt preserves the earlier prompt typo and explicit owner correction; use the published full HybridCLR pin above, never the truncated text.

## Independent checks performed

[Raw audit workflow](https://github.com/night-outlook/hybridclr_demo/blob/77b206da4e66677b3c7ef29174586e0887e41b3d/.github/workflows/gcomp-reconcile-7d42.yml), [run 38193946749](https://github.com/night-outlook/hybridclr_demo/actions/runs/38193946749), job 114632427362: **Passed**. This separately checks the raw files rather than relying solely on Local's FINAL_EVIDENCE_AUDIT report.

- Original MANIFEST.sha256 authenticates as Git blob `4dc786b14983cc099e87cbd58189c9816f890de9`, SHA-256 `eda067e3a425fab00a1754d1f8dfbc3b444b409e70c7832940bec2609cd37fec`. All **544 listed files**, exact inventory/uniqueness and their full SHA-256 hashes verified. The manifest itself is additional to those 544 files.
- All **77 raw command receipts** bind their actual stdout/stderr streams. The only nonzero command is the intentionally negative original unsigned-count managed compile. Command lifetime records contain no timeout/interruption, startup error, cleanup error or surviving process group.
- All **55 native configurations** independently match the complete 11-unit × 5-profile set, actual command/source/receipt hashes, C++17, arm64, syntax-only mode and candidate/debug/probe-off/diagnostics-off/feature-off defines. The 11 distinct unit bytes match current pinned repository objects. This is not native linking or Player construction.
- The five successful managed targets are HybridCLR.Runtime, Unity.HybridCLR.AssemblyShadow.CodeGen, HybridCLR.Editor, R03Build and R03TerminalPlayerApi. Actual commands, response files and input digests match. The complete current R03TerminalPlayer.cs is in the real compiler input; official Unity managed references are present. **213 owned managed input bindings** match the pinned repository bytes and lengths. The remaining official/tool inputs retain Local's recorded identity, not a new Primary installed-SDK scan.
- OriginalUnsignedCounts is a separate **Passed expected-negative control**: exit 1, exactly two CS0266 diagnostics; it is not a sixth successful product target.
- Published before/after custody receipts each retain 416,844 expected, 339,367 verified survivors, 77,477 same historical missing identities, complete scan and zero problems. `originalStrictCustody=Blocked` and `sourceBuildProcessProvenanceRestored=false` remain unchanged. Primary authenticated these existing records; it did not execute another Local live scan.

[PRIMARY_G_AUDIT.json](PRIMARY_G_AUDIT.json) is the exact downloaded audit result (SHA-256 `37c3cbf8b275d217ad5297c59dc1e79e9ef6d7f4e30a3a659f0191035f288b69`). [AUDIT_PROVENANCE.json](AUDIT_PROVENANCE.json) records run/job/workflow/artifact bindings and limitations. Original audit artifact 11723055507 was downloaded through the Connector and its archive SHA-256 verified as `fa9c0483f5d673682b023ec88a9596f190248443b934e417127b521046043ffb`.

[Existing-host-suite run 38194176062](https://github.com/night-outlook/hybridclr_demo/actions/runs/38194176062), workflow source `7383ea2be2633190f295419546a6edec86273b7a`, checks out exact G publication 4808743f and independently runs **65 R03IR tests, 20 scratch tests and nine retained-E tests**: all Passed, no skipped tests. The retained-E suite includes real original-E Git inventory authentication and synthetic preservation negatives, not a new live E scan. Its downloaded archive is hash-bound in AUDIT_PROVENANCE.json. The current R03IR count is **65**, not the historical pre-reporting count of 64. These host results do not replace fresh Local prerequisites.

## Warnings retained; not dismissed as harmless

The raw streams contain **74 managed CS0649 warnings** (61 HybridCLR.Editor, 13 R03TerminalPlayerApi) and **616 native warning occurrences** of `failure memory order argument to atomic operation is invalid [-Watomic-memory-ordering]`. The native warnings are repeated across translation units/profiles, not 616 independently identified defects. Local's COMPILER_WARNING_AUDIT.json binds the originating Baselib header to unchanged installed official SDK bytes. The audit independently recounts the warning text; Primary did not possess or rescan the installed vendor SDK.

No warning suppression, vendor modification, expectation change or claim of atomic runtime correctness is made. These existing warnings do not prevent a bounded diagnostic run intended to measure the candidate; their runtime/performance significance is **not** accepted for shipping or full-stage approval. Retain complete fresh build warnings and any changed diagnostic category. A new compiler/link failure remains a failure, not an excuse to disable a warning or alter a guard.

## Runtime scope assessment and sequencing

The actual unchanged `Tools/AssemblyShadow/R03IR/run_terminal_local.py` schedules **14 cells, three new build roles and four new Players**. G compiled its Player/probe inputs but did not execute these runtime assertions.

| Required fact | G-COMP status | H runtime assignment / later requirement |
| --- | --- | --- |
| Official managed API and 55 native syntax profiles | Passed, reconciled | Reuse only with exact input equivalence; fresh builds still required |
| Current corrected source builds and links into Unity Player | NotRun | Three fresh ON Release/ON Debug/OFF builds |
| Same active MethodInfo/delegate really return 42/42 and increment private stable field 0→2 | Unavailable in E; NotRun in G | Mandatory ON raw evidence; no inferred PASS from phase logs |
| Post-poison reflection/delegate/reflected AOT calls rejected, field readable at 2, recovery immutable | Unavailable in E; NotRun in G | Mandatory ON raw/verifier assertions |
| Exact native reporting substitution and continued guard denial | Host/probe compile only | ON `terminalReportingProbeMask=15`, OFF zero; direct native probe only |
| Engine itself invokes reporting after an uncaught managed exception; custom logger body never runs | NotRun in actual Unity | Still open after H; requires a separately source-bound engine-originated experiment, not a fabricated direct-probe equivalence |
| Original E first triggering failure | Unknown | Collect fixed native first-failure and ordered phase records on any recurrence; a new healthy run cannot reconstruct an absent historical first-error record |
| Captured-generic / initializer terminal witnesses and IR-R03-01 closure | Outstanding | Separate Primary scope, not silently added to this run |
| Full legacy regression, performance qualification, independent full-stage review and Human Review Gate | Not accepted / FAIL / NotRun | Unchanged normative gates |

**Chosen sequence:** first test the already compiled, unchanged correction with the existing narrowly bounded runtime batch. Changing the Player now to add a new unhandled-engine experiment would invalidate G's exact compilation coverage and combine unresolved behaviors. H therefore isolates corrected build/link, caught terminal behavior and direct fixed reporting. After its factual return, Primary must separately implement/validate the genuine engine-originated experiment and the other outstanding witnesses before attempting broader closure. This is sequencing, not a waiver or a claim that the native observer's host mock proves engine behavior.

The optional native observer source compiled in G is not wired into the four-current-Player runner as a genuine engine-originated case. Local may not invent a fifth Player, call an unprescribed export, throw an extra unhandled exception, or modify the source to create such a case under H.

## Authorized next boundary and unchanged history

[H_RUNTIME_PROCEDURE.md](H_RUNTIME_PROCEDURE.md) and the current canonical WEB_TO_LOCAL.md authorize **one new H attempt**, after the final exact transport SHA is supplied and all preflight gates pass. H is only an attempt identifier, not H1/H2 or a Human Review Gate. New roots use `H-post-GCOMP-7d42`, not any previously designated F/G path. Original source/evidence, full C-frozen scoped custody and retained E preservation, G compilation-input equivalence and fresh storage admission are mandatory. No automatic retry, changed threshold, alternate TMPDIR, protected cleanup or reuse of old Player/SDK output.

G remains Passed within compile-only scope. F-COMP remains PrerequisiteBlocked with before-admission/compilers NotRun; E remains FAIL (11 Passed/3 Failed, three ON SIGSEGV, OFF Passed); earlier S/R/Q/P/O/N/A/B/C/D states are unchanged. Strict historical S custody remains Blocked and four native roots Missing. New preservation checks never reclassify those facts.

Independent R03 full-stage review remains FAIL; independent re-review NotRun. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2/X02/M08A or automatic human approval.
