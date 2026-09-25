# Local Validation report

## Current run — 2026-09-25, M08 evidence closure re-review

### Exit

**Local Validation → Primary Implementation: the evidence-closure package authenticates its recovered origins and historical manifest successor claims, but the required count-chain suite is BLOCKED. The independent M08 re-review returned BLOCKED with one high-priority finding.** H1 remains `InProgress`; `M08Passed=false`, `humanGatePassed=false`, and `mayEnterR02=false`. R02 remains closed. No Player or formal runner was rerun.

The clean validation worktree `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` was fast-forwarded to pushed handoff `384662d08482f804bfa9772c4acf38b834c57db1` on `codex/assembly-shadow-r01b-h1`. The source anchor remains `0388479f7073289e3505b992956a7cbe78c302ce`; its delta to the handoff HEAD has 79 metadata paths and zero non-metadata paths under the unchanged `shadow_tools.metadata_only` policy. The other three worktrees were clean and matched their pushed heads: `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `il2cpp_plus=6be7f38bec2fa4677d24efc1a4a1294240789933`. Committed handoff preflight returned `SourceTargetVerifiedNotBuildAccepted`. The existing source-038 V05 SHA-256 `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f` and prior Local checkpoint manifest SHA-256 `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10` were unchanged. In accordance with this metadata-only handoff, V01, V02, V04, and V05 were not rerun.

The new authenticated Local checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260925-authority038-m08-re-review/`. It contains E00–E05 receipts, the initial and corrected E04 dispositions, the independent review verbatim, a machine receipt, and snapshots of this report and the Primary return. The Primary closure bundle remains at `Docs/AssemblyShadow/History/M07R/H1/current-primary/m08-evidence-closure-20260925/`; historical checkpoints and recovered JSON were not modified.

| Cell | Result | Evidence and limit |
| --- | --- | --- |
| E00 source/handoff authority | `Passed` | Exact four pushed heads, zero source-038→HEAD non-metadata paths, committed preflight, existing V05/checkpoint hashes unchanged |
| E01 recovered origins | `Authenticated` | All 11 prior-review/12cf copies byte-equal their immutable Git origins; reconstructed 925e Handoff bytes equal commit `075f8a25...` and expected SHA-256 `cb8f06d7...52a3d54` |
| E02 historical checkpoint successor | `AuthenticatedWithExplicitHistoricalExclusion` | 925e effective 293/293 using the recovered external Handoff member; 6913 has 29 verified plus one unavailable/excluded prelaunch log absent at creation commit; original 6913 manifest is **not** claimed 30/30; source-27df superseding checkpoint 92/92, formal 40/40 |
| E03 prior P1 successor mapping | Authenticated facts for re-review, not acceptance | COUNT 12cf summary says 132/132 and six provenance builds; startup11 has 11 distinct historical PIDs and `ReusedAuditedFrom925e` classification; eight UNFIXED-REPRO cells retain 6 `UnexpectedAccepted`, 2 Debug `AssertAbort`, and `candidateAcceptance=false` |
| E04 whole-chain source/index audit | `Passed` within its measured scope | 925e→038 exact 70 Bootstrap, 16 Runtime, 42 H1 count, three failure-tool and three capacity-tool blobs unchanged; native/package/IL2CPP pins unchanged; all 884 indexed 925e artifacts plus raw archive and 3168 reuse bindings authenticate |
| E04 per-suite disposition | **Five `AcceptedReusedAudited`, one `Blocked`** | Startup11, failure/publication/recovery, ordinary capacity, mixed capacity, and M07/native accepted as reused. Count-chain blocked because the selected 12cf 132/132 reports lack their launch/raw layer. |
| E05 independent `MILESTONE` re-review | **`BLOCKED`**, one high-priority finding | Read-only `code-gate-reviewer` independently confirmed the count evidence gap and revisited all three previous BLOCKED findings. Review retained verbatim. |

The initial E04 suite receipt recorded six accepted suites after checking the 12cf summary, six-build provenance record, and archive Git blob identity. It did **not** inspect the archive member set or resolve the per-cell launch/raw references before accepting count-chain. The initial receipt and its nine-entry pre-review manifest are retained as failed-attempt evidence. The subsequent `E04/count-chain-raw-availability.json` examines all 132 verifier reports in the immutable Git archive: its 133 business members are 132 `verification.json` files plus `result-index.json`; none of the referenced 132 launch receipts or 132 raw results is present in the archive or designated checkout. The archive also contains 133 AppleDouble metadata entries. The corrected E04 receipt classifies count-chain `Blocked`, leaves five suites `AcceptedReusedAudited`, and makes independent M08 eligibility false. E03 remains an authentication of historical summary/provenance facts; it does not promote the count Player execution to an accepted raw-evidence chain.

The independent reviewer ran read-only from `2026-09-25T08:44:08Z` to `08:58:55Z` and returned `BLOCKED`. It confirmed the recovered prior-review provenance, the 925e effective 293/293 and 6913 29+1 dispositions, and the supportable reuse of five suites. It found that the 12cf candidate count archive cannot establish the canonical Launch and Raw semantics layers for the selected 132/132 claim; the later 925e six-build GUIDs differ and cannot replace the missing 12cf launch provenance. Its full reasoning and unfavorable performance observations remain verbatim in `E05/independent-review.md`. The independent review was commissioned from the initial E04 receipt; its finding prompted the corrected Local classification. This re-review does not confer `ReadyForHumanReviewGate`.

Primary must recover and index the exact 132 historical count launch receipts and raw results, together with their referenced build/input bytes and per-cell semantic checks, or arrange a separately authorized new controlled count matrix with a frozen source/build. The current Local handoff does not authorize a Player rerun. After count-chain can genuinely be `AcceptedReusedAudited`, a new independent M08 review is required. `ComparabilityPassed` in the reused source-27df performance analysis remains measurement validity only; P01/P03 slowdowns and higher RSS remain human-review inputs, not accepted performance.

## Historical run — 2026-09-24/25, source 038 V05 and independent M08

### Exit

**Local Validation → Primary Implementation: V00–V05 passed within the analysis-only handoff; genuinely independent M08 returned BLOCKED with three evidence gaps.** The 40/40 formal Player series was not rerun. H1 remains `InProgress`, `M08Passed=false`, `humanGatePassed=false`, and `mayEnterR02=false`; R02 remains closed.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, at pushed handoff HEAD `4b8e8617deee75dbc10241e120ec2e8a3b3cd366` before this metadata-only checkpoint/report commit, with source anchor `0388479f7073289e3505b992956a7cbe78c302ce`. The other clean, remotely verified worktrees matched `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `il2cpp_plus=6be7f38bec2fa4677d24efc1a4a1294240789933`. `V00/source-authority.json` records exact paths, heads, remote refs, source/package pins, and worktree registrations. The original execution source remains `27df1a3d60811dc121f296ab561ae313a382b363`.

The pre-V05 V04 closure checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-pre-v05-v04/`: all 22 manifest members verify; its manifest SHA-256 is `bd8a7e575503623a0c8bf98739a1a8da3c0cc3bebc44dbdd94075c74e7f92c28`. The final Local checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-v05-m08/`: all 28 manifest members verify; its manifest SHA-256 is `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10`. The final checkpoint retains the independent review verbatim and a SHA-bound receipt. Command receipts retain the exact commands, cwd, UTC intervals, outputs, and exit codes.

| Cell | Result | Evidence and limit |
| --- | --- | --- |
| V00 source authority and committed preflight | `Passed` | Exact four-repository pins and remote heads; source-anchor→handoff HEAD zero nonmetadata paths; preflight `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | 387/387 Passed, zero Failed/Error/Skipped; six V05 leaves included |
| V01 complete Python discovery | Required zero Failed/Error met; 28 environment skips | 1,071 leaves: 1,043 Passed, 28 Skipped; inventory CLI exit 2 reflects skip policy; full inventory/log and explicit skip reasons retained |
| V01A source audits | `Passed` | Source-27df→038 exact seven analysis/test paths; retained-6913→038 exact 25 paths; d61→038 exact three paths |
| V02 immutable historical reauthentication | `PassedHistoricalIntegrityOnly` | 92/92 source-27df manifest, four fixed live hashes, 33,792/33,792 sealed files totaling 1,606,993,133 bytes; zero missing/content/stable-stat mismatches; 33,981 direct bindings with zero unresolved semantic mismatches |
| V04.AF split-checkout compatibility | `AuthenticatedAnalysisOnlySuccessor` | Current analysis checkout and original historical evidence root remain distinct; exact v2 source policy and live historical authority pass |
| V04.AG strict historical analysis | `Passed` / `ComparabilityPassed` | Fresh analysis of immutable original bytes: 45 attempts, 44 valid, one preserved invalid ON-NoPatch pilot, 40/40 valid formal, ten formal pairs/startup observations per mode, chronology and non-overlap pass |
| V04 closure | `Passed` | 22-entry pre-V05 manifest; full performance JSON, exact assertion receipt, and scoped no-Player command proof |
| V05 successor binding | `SuccessorEvidenceBoundForIndependentM08` | `H1AnalysisOnlySuccessorEvidence-v1`; current tests Fresh, historical execution Reused, historical performance Reanalyzed; complete performance JSON SHA bound; no Player; performance acceptance `NotClaimedNoSLA`; M08/human/R02 flags false |
| Independent M08 `MILESTONE` | **`BLOCKED`**, three findings | Read-only `code-gate-reviewer` examined the complete V05 package and H1 gate; review and machine receipt in `M08/` |

V04.AG ran once and exited 0 after full strict verification. The full paired analysis SHA-256 is `c02c4ffd0ad93759ef4f2ffb3a7482b3c9d5ed96cf4c9a122f35135478323053`. The original failed `R00-ON-NoPatch-pilot-01` still records process-group cleanup failure and skipped B side. In the warm repeat-10,000 phase, median paired B/A ratios for allocation, reflection invoke, and closed generic are 1.133/1.266/1.204 for ON-P01 and 1.150/1.276/1.221 for ON-P03. B median RSS is higher than protected A in every mode at both snapshots; P01/P03 managed-memory medians move downward. `ComparabilityPassed` is measurement validity, not performance acceptance. The full timing, startup, memory, and variance statistics remain visible to M08.

The first V05 invocation failed before analysis because its new output directory had not been created. Its failure receipt is preserved. After creating that empty directory, the identical package command exited 0 and produced V05 SHA-256 `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f`; no input or Player evidence changed for the retry. The final checkpoint retains both command receipts and all 15 Local V05 assertions.

The independent M08 review ran read-only from `2026-09-25T06:35:25Z` to `06:48:23Z` and returned **BLOCKED**, not PASS. Its three findings are: (1) the original M08 review/finding-closure records referenced by `History/M07R/R01B/H1-handoff.md` are not available in the designated local paths for finding-by-finding closure; (2) older whole-H1 manifests verify only 292/293 and 29/30 members at their listed paths, respectively, although the reviewer did not infer corruption of the current 40/40 formal raw evidence; and (3) V05 does not provide the required selected suite-by-suite equivalence bridge for older capacity, failure, recovery, count, and startup claims. The complete reviewer wording, evidence paths, performance observations, and closure requests are preserved verbatim in `M08/independent-review.md`. These gaps require Primary evidence disposition and a new independent M08 review. Human H1 approval is still separate even if a future M08 returns PASS.

No Unity Editor, native build, IL2CPP build, Player, profiler, or formal runner was invoked in this analysis-only cycle. `V04/no-player-proof.json` records Local command issuance with its stated scope limit. Historical Unity EditMode and runtime results remain historical/reused where separately supported; this run does not promote them to fresh current-source execution.

## Historical run — 2026-09-24, split-checkout historical analysis

### Exit

**Local Validation → Primary Implementation: V04 closed; V05 is not eligible under the current handoff, so independent M08 was not run.** V04.AF authenticated the separate current analysis checkout and historical evidence root. V04.AG then returned `Passed` / `ComparabilityPassed` for the immutable source-27df 40/40 series. No Player was rerun.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, pushed handoff HEAD `0bed47e981e5b3b4ac8b9ed2b4c423e11aa88b31` before this metadata-only report/checkpoint commit, and source/tool anchor `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`. The other clean, remotely verified worktrees remained `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. The source pins, package reference, remote heads, worktree registrations, and host versions are recorded in `V00/source-authority.json`.

The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd61-split-analysis/`. Its `MANIFEST.sha256` covers 24 evidence/README files, SHA-256 `04ca3e24a1f16f21cbbde7e62493070529ffce4720beebac2c1f1615ab3b3553`; all 24 verified independently. Command receipts retain exact commands, UTC start/end, cwd, exit codes, stdout/stderr and paths. V04.AG ran once from `2026-09-24T06:57:24Z` to `17:08:44Z` and exited 0. Python was 3.14.6 on macOS arm64. Unity 2022.3.62f2 / StandaloneOSX / arm64 is the pinned target, but Unity and Players were not invoked in this analysis-only cycle.

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 four-repository authority and committed preflight | `Passed` | `V00/`; all four pushed worktrees clean at entry; `d61→0bed` zero non-metadata paths; preflight `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | `V01/bounded-primary/`: 381/381 Passed, zero skips/failures/errors; four split-checkout regressions included |
| V01 complete Python discovery | `CompletedWithNonPass` from explicit environment skips; required zero failures/errors met | `V01/python-inventory.json` and full log: 1,065 leaves, 1,037 Passed, 28 Skipped, zero Failed/Error; the inventory CLI exit 2 reflects its skip policy |
| V01 exact source audits | `Passed` | `V00/source-authority.json`: source-27df→d61 exact v2 seven paths; retained-6913→d61 exact v2 25 paths; d239→d61 exact three paths |
| V02 source-27df checkpoint and complete live reauthentication | `PassedHistoricalIntegrityOnly` | `V02/`: 92/92 prior checkpoint manifest; four fixed live hashes; 33,792/33,792 sealed files, 1,606,993,133 bytes, zero missing/content/stable-stat mismatches; 184 additional current-live bindings match and five historical Git-source/tool identities match pinned Git blobs, zero unresolved |
| V04.AF split-checkout compatibility | `Passed` | `V04/historical-compatibility.json`: `AuthenticatedAnalysisOnlySuccessor`, analysis root is the designated worktree, historical root is the unchanged ordinary owner, exact v2 policy and source-27df bridge/seal/formal authority |
| V04.AG strict historical analysis | `Passed` / `ComparabilityPassed` | `V04/historical-performance-analysis.json` and `analysis-validation.json`: 45 retained attempts, 44 valid, exactly one preserved invalid ON-NoPatch pilot, 40/40 valid formal, ten formal pairs and startup observations per mode, one valid pilot per mode, complete chronology and non-overlap |
| V04.AH analysis-only closure | `Passed` | New 24-entry SHA-256 checkpoint manifest verified; full measured statistics, including unfavorable values, retained unchanged in analysis JSON |
| V05 successor | `NotEligible / NotRun` | `V05/eligibility.json`: current handoff names V05 but provides no runnable analysis-only successor criteria; the historical series cannot be relabelled fresh current-source execution and Player reruns are forbidden in this handoff |
| Genuinely independent M08 | `NotEligible / NotRun` | `M08/eligibility.json`; no successor package eligible for a whole-chain review, so historical independent M08 `FAIL` remains the only M08 result |

The original failed `R00-ON-NoPatch-pilot-01` retains its process-group cleanup error and skipped B side. The 40 formal attempts were not replayed. V04.AG authenticated and reanalyzed existing bytes; it did not create current-source Player evidence or change the original live source-27df paths. `V04/no-player-proof.json` records Local command issuance and its scope limit. Earlier runtime evidence remains `ReusedAuditedFromFF3D`, and Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`; neither is fresh current-source execution.

`ComparabilityPassed` establishes that the paired measurements can be analyzed, not that they meet a performance target. In the `repeat10000` phase, the median paired B/A ratios for allocation, reflection invoke, and closed generic are respectively 1.133/1.266/1.204 for ON-P01 and 1.150/1.276/1.221 for ON-P03. The candidate B median current RSS exceeds protected A in every mode at both memory snapshots. The analysis JSON retains every measured value and statistic for independent review.

Primary must state an exact V05 successor-evidence contract that is compatible with this analysis-only, no-Player boundary, or explicitly defer V05 to a separately authorized fresh-execution program. Only after an eligible V05 package should a genuinely independent M08 review be commissioned. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 remains closed.

## Historical run — 2026-09-24, v2 historical compatibility preflight

### Exit

**Local Validation → Primary Implementation: FAIL at V04.AF historical compatibility preflight.** The fail-closed preflight rejected the checkout selected for current analysis authority. Corrected historical analysis, V05, and independent M08 were not run. No Players were rerun.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, pushed HEAD `aedf3c58c3e3f8ab612552563a29c8906b82bea1` before this metadata-only report commit, with demo source/tool pin `d239d9d00784ea2df22133cb8c938ec25035f5a0`. The other clean, remotely verified validation worktrees were `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. Native/package/IL2CPP source pins and the Unity package file reference resolve to these worktrees. `V00/source-authority.json` records exact paths, branches, commits, remote heads, worktree registrations, pins, and host versions before report edits.

The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`. Its `MANIFEST.sha256` covers 17 evidence and README files; verification passes. Command receipts contain exact commands, UTC start/end, cwd, exit codes, and output paths. The run used Python 3.14.6 on macOS arm64. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity and Players were not invoked. No local source or test fix was made.

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 four-repository source/native/package authority | `Passed` | `V00/source-authority.json`; all four initial worktrees clean and at pushed commits; anchor `d239d9d0` → handoff HEAD has zero non-metadata paths |
| V00 committed handoff preflight | `Passed` | `V00/handoff-preflight.json`: `SourceTargetVerifiedNotBuildAccepted`, not a build acceptance result |
| V01 bounded Primary | `Passed` | `V01/bounded-primary/results.json` and `tests.log`: 377/377 Passed, zero skips/failures/errors |
| V01 complete Python discovery | `CompletedWithNonPass` from explicit skips; handoff requirements met | `V01/python-inventory.json` and `python-tests.log`: 1,061 leaves, 1,033 Passed, 28 environment Skipped, zero Failed/Error; corrected positive paired-performance leaf Passed. Inventory CLI exit 2 reflects skip policy, not a test failure; 27 skips lack the canonical H1R coordination directory and one lacks real compiler/config paths. |
| V01A exact source audits | `Passed` | `V00/source-authority.json`: `27df1a3d` → `d239d9d0` exact seven-path `H1HistoricalPerformanceReanalysis-v2`; `69130bbb` → `d239d9d0` exact 25-path `H1V04RetainedGraphToolOnlySuccessor-v2`; `27df` → handoff HEAD remains exact seven paths |
| V02 source-27df checkpoint manifest and fixed live inputs | `PassedHistoricalIntegrityOnly` | `V02/historical-checkpoint-manifest.log`: 92/92; `V02/live-evidence-reauthentication.json`: original live bridge `c03665db...`, seal `bdc4062a...`, formal batch `97ddb6c8...`, final sample `a8e519c3...` all SHA-256 exact |
| V02 complete live sealed graph | `PassedReadOnlyReauthentication` | 33,792/33,792 files, 1,606,993,133 bytes, zero missing/content/stable-stat mismatches. 184 additional current-live direct bindings match. The initial generic binding audit marked five historical Git-source/tool identities as live mismatches; `V02/direct-binding-semantics-audit.json` verifies their pinned Git blobs and reports zero unresolved mismatches. Both audit receipts are retained. This does not replace the V04 semantic proof. |
| V04.AF v2 historical compatibility | `Failed` | `V04/historical-compatibility-v2.json`, command receipt and checkout-selection diagnosis: exact v2 policy says the two new test paths are missing from the source delta selected by the tool |
| V04.AG corrected historical strict analysis | `Blocked / NotRun` | Requires V04.AF `AuthenticatedAnalysisOnlySuccessor` |
| V04.AH analysis-only closure, V05, independent M08 | `Blocked / NotRun` | No authenticated compatibility/analysis result; historical M08 `FAIL` is unchanged |
| Current Unity/native/IL2CPP builds, Players, profiler | `NotRun` | Analysis-only handoff; original source-27df 40/40 execution remains historical and unchanged |

The preflight uses the original live source-27df bridge, seal, batch, and final sample paths as required. It checks `bridge.projectRoot` (`/Users/ah/GitHub/hybridclr/hybridclr_demo`) for **current** source pins. That ordinary owner checkout is detached at `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` and pins demo source `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The designated validation checkout pins `d239d9d0`; the audited v2 seven-path delta is there. Thus the preflight returns `H1HistoricalPerformanceReanalysisFailure` with `missing=[Tools/AssemblyShadow/h1_bee_primary_tests.py, Tools/AssemblyShadow/tests/test_h1_paired_performance.py]`. This is a checkout-selection defect in the compatibility tool, not a live evidence hash failure. `RETURN_TO_WEB.md` contains the exact reproduction and Primary implementation direction.

The immutable source-27df execution checkpoint and 40/40 formal series remain historical. Earlier runtime evidence remains `ReusedAuditedFromFF3D`; Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`. Neither is fresh current-source execution. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. After Primary publishes a source-authority-safe repair, Local must restart V00, V01, live reauthentication, V04.AF, V04.AG, checkpoint authentication, V05, and genuinely independent M08 in order. R02 remains closed.

## Historical run — 2026-09-23/24, repaired analysis-source handoff

### Exit

**Local Validation → Primary Implementation: FAIL at complete Python discovery.**

The final pushed Primary handoff was checked out cleanly at `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, HEAD `dd3c8988e9136e0c3a8ca965f82067d6b7c83acd`. Its build-input/tool anchor remains `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The other validation worktrees and matching pushed commits are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. All use the expected branch. Native/package/IL2CPP pins and the Unity package file reference resolve to this validation workspace. Exact repository inventories are in the new checkpoint's `V00/v00r-source-authority.json`.

V00.R passed: all nine restored `.agents`/`.codex` files are byte-identical to their `7aa6f619` Git blobs; the complete 7aa→HEAD non-metadata delta is empty. The 27df→HEAD non-metadata delta is exactly the fixed five analysis-only paths, and the retained 6913→7aa delta is exactly the 24-path allowlist. The committed V00 preflight returned `SourceTargetVerifiedNotBuildAccepted`. This authenticates source identity, not a new Player build or acceptance gate.

Bounded Primary regression passed 376/376. Complete Python discovery then executed 1,061 leaves: 1,032 `Passed`, 28 explicit `Skipped`, and one `Failed`. The failure is `test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`. Its synthetic `raw()` fixture stores build GUID, baseline ID, and runtime ABI only inside `playerBuildReceipt`; the corrected analyzer requires those three values at raw-result top level and rejects all 44 synthetic pilot/formal attempts with `R00 raw top-level build field differs: buildGuid`. The focused committed test reproduced this. Adding those top-level fields from the expected receipt **in memory only** made the focused test return `ComparabilityPassed`; no repository test or production source was edited. The bounded suite does not contain this failing positive test.

Changing the test file in this checkout would create a sixth non-metadata path after the fixed `7aa6f619` anchor and invalidate both current source preflight and the exact five-path historical compatibility rule. This is therefore a Primary source-authority decision, even though the test fixture defect itself is narrow. `RETURN_TO_WEB.md` gives the reproduction and corrective direction.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| Four-repository Git/native/package preflight | `Passed` | `V00/v00r-source-authority.json`; exact pushed commits and clean checkouts before report edits |
| V00.R repaired source-authority audit | `Passed` | Nine restored bytes exact; 7aa→HEAD zero non-metadata; 27df→HEAD exact five; 6913→7aa exact 24 |
| V00 committed handoff/source preflight | `Passed` | `V00/handoff-preflight.json`; `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | 376/376, full inventory and log in `V01/bounded-primary/` |
| V01 complete Python discovery | `Failed` | 1,032 Passed / 28 Skipped / 1 Failed; `V01/python-inventory.json` and `python-tests.log` |
| V01 focused fixture diagnosis | `FailedAsCommitted`; `PassedWithInMemoryDiagnosticCorrection` | 44 invalid synthetic attempts as committed; no file edit or authoritative PASS claim |
| V02 historical checkpoint and four fixed live hashes | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries and four SHA-256 matches; full live graph not reauthenticated this cycle |
| V04 historical compatibility preflight and corrected analysis | `Blocked / NotRun` | Complete Python prerequisite has one failure |
| Analysis-only closure checkpoint / V05 / independent M08 | `Blocked / NotRun` | V04 remains incomplete |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff is analysis-only; no new build GUID or execution evidence |

The run used Python 3.14.6 on macOS arm64; command receipts in the checkpoint record UTC start/end, exact commands, logs, paths, and exit codes. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`, containing all fresh V00/V01 and independent integrity evidence plus `MANIFEST.sha256`. The immutable source-27df execution checkpoint and 40/40 formal series remain historical; no Player was rerun and no historical receipt was changed. Earlier runtime evidence remains `ReusedAuditedFromFF3D`, earlier Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`, and source-27df formal execution remains historical. None is relabelled as fresh current-source execution.

Primary must publish a coherent test-fixture correction and source/compatibility handoff. After it is pushed, Local must restart V00.R/V00, rerun the full Python suite, then perform complete live historical reauthentication, historical compatibility preflight, corrected analysis, checkpoint authentication, V05, and genuinely independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23/24, source-pin mismatch

### Exit

**Local Validation → Primary Implementation: FAIL at V00 source authority.**

The latest pushed handoff was read at demo checkout HEAD `d7854b16c09b02d4494d28c2b0ea015ba83f58a3`, branch `codex/assembly-shadow-r01b-h1`, path `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`. Its declared analysis source/tool anchor is `7aa6f61994da354b04464e38ddfc8552cc5c3055`. All four validation worktrees are on the handoff branch, clean, and match the pushed remote heads. Their exact paths, commits, remotes, worktree registrations, package references, source pins, submodule inventories, and host versions are in the new checkpoint's `V00/repository-preflight.json`.

| Repository | Validation checkout | Pushed commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` before this report commit |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Native, package, and IL2CPP pins equal those three repository commits. `Packages/manifest.json` resolves the HybridCLR Unity package to this validation workspace. No new build GUID or Player artifact was generated. The completed formal evidence remains bound to execution source `27df1a3d60811dc121f296ab561ae313a382b363` and retained graph source `69130bbb3a6df516916dddb5ad263799a7c6e5e3`; its four fixed live evidence hashes are recorded in `V02/historical-live-four-hashes.json`.

The current `h1_handoff_preflight.py --project <candidate> --role candidate --output <new V00 output>` returned exit 1: `Blocked: Demo HEAD contains build-input changes after the source pin`. The exact nine non-metadata changes from `7aa6f619` to `d7854b1` are the three `.agents/skills/agent-collaboration` files and six `.codex/agents` profiles. The source verifier compares the complete non-metadata Git tree at the pin to HEAD, so the migration commit `d7854b1` invalidated the pinned checkout. The source-to-source five-path analysis delta and 24-path retained-graph delta remain exact, but they do not authenticate this later HEAD.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 repository/branch/remote/native/package pins | `Passed` | `V00/repository-preflight.json`; clean worktrees and exact remote heads before report commit |
| V00 current committed handoff/source preflight | `Failed` | `V00/preflight.json`; source pin rejected before output receipt |
| V01 exact source-to-source audits | `PassedForAnchorsOnly` | `V01A/source-audits.json`: 27df→7aa exact five; 6913→7aa exact 24; 7aa→HEAD has nine non-metadata files |
| V02 historical checkpoint manifest | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries verified in `V02/historical-checkpoint-manifest.log` |
| V02 four fixed live evidence hashes | `PassedHistoricalIntegrityOnly` | Bridge, seal, batch, and final sample hash-identical at original live paths; no full live graph reauthentication this cycle |
| V00 bounded Primary / complete Python discovery | `Blocked / NotRun` | Source preflight prerequisite failed |
| V04 historical compatibility and corrected analysis | `Blocked / NotRun` | Source-authority prerequisite failed; no analysis result claimed |
| V04 new checkpoint / V05 / independent M08 | `Blocked / NotRun` | No authenticated current analysis checkout |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff specifies analysis-only validation; no new execution evidence |

The fresh run used Python 3.14.6, PowerShell 7.6.3, and Git 2.50.1 on macOS arm64. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The preflight command, UTC start/end, exit code, stdout/stderr, Git inventories, full path lists, hashes, and manifest log are in `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-source-pin-blocked/`. That checkpoint is the evidence for this return and references the immutable 27df execution checkpoint. Historical runtime, EditMode, pilot, and formal results remain historical and are not promoted to current-source PASS.

Primary must restore a coherent pushed handoff source identity while preserving the completed 40/40 formal series and the source verifier's fail-closed guarantee. `RETURN_TO_WEB.md` gives the reproduction and implementation boundary. After a new pushed handoff, Local must restart V00 and run V01, historical compatibility, corrected analysis, checkpoint, V05, and independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23 authority `27df1a3d`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after 40/40 formal pairs**

Fresh V00 authenticated candidate checkout `f5e34235641c212c715aef3405925ddd4cf28ee6` and exact source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed through the sanctioned `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` path, then passed strict verification.

Fresh bounded Primary validation passed 368/368. The focused suite passed 126/126, both requested PowerShell recovery suites passed, and full Python discovery completed 1,053 leaves: 1,025 Passed, 28 explicit environment-bound Skipped, zero failures, and zero errors. The exact source audits passed: `91ac4db3... → 27df1a3d...` contains the required 3 non-metadata paths and `69130bbb... → 27df1a3d...` contains the required 22 paths, with no forbidden runtime or producer delta. Historical Unity 1,076/1,076 remains only `ReusedAuditedFromD18`, not fresh current-source execution.

The retained V04 manifests, build map, protocol, schedule, pilot index, five pilot attempts, four selected pilots, and eight selected launch receipts reauthenticated. Independent hashing verified 33,792 bound files totaling 1,606,993,133 bytes with zero content mismatches.

A new `H1GraphReuseBridge` passed as `AuthenticatedToolOnlySuccessor` with SHA-256 `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`. It binds the exact retained runner SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c` and current runner SHA-256 `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

The retained-pilot admission preflight passed with five retained attempts, four selected pilots, exact historical runner bindings, and no deep reconstruction. Its SHA-256 is `cbfc6faf8512a214ff97fa939bc6335b05a36362d66b539ff22e954c61529ed1`.

The new guard-v2 strict seal passed with `guardKind=CrossRemountStableStatGuard`, `guardVersion=2`, guard fields exactly `[inode, mode, size, mtimeNs, ctimeNs]`, no device field, `deepLaunchVerificationCount=8`, and 33,792 sealed files. Its SHA-256 is `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`.

A wholly new formal series started from the retained pilot index, without chaining either historical failed series. The batch runner automatically used path-hash namespace suffix `7cafb9c53434`, so pair 1 did not collide with preserved project-local outputs. Pair 1 proved protected A had no formal launch authority, while candidate B received and consumed a valid current `H1FormalSideLaunchAuthority`, passed retained graph preparation, launched the Player, and emitted an R00 receipt echoing the same authority, bridge, seal, and build map.

All 40 formal pairs passed on their first protocol attempt: 10/10 OFF-NoPatch, 10/10 ON-NoPatch, 10/10 ON-P01, and 10/10 ON-P03. No whole-pair retry was required. The batch receipt is `PassedAllFormalPairs`, SHA-256 `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`; the final cumulative index SHA-256 is `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

The bridge-aware strict analyzer completed after reconstructing the cumulative chain, but returned `Incomplete` / `ComparabilityIncomplete`. Build-map comparability and chronology passed. Of 45 cumulative attempts, 44 were rejected by the same receipt-shape check:

`R00 raw build field differs: baselineBuildId`

The raw R00 top-level `baselineBuildId` and `runtimeAbiHash` are correct and match the frozen build. The nested raw `playerBuildReceipt` correctly binds its path, SHA-256, and build GUID, but omits `baselineBuildId` and `runtimeAbiHash`. The final analyzer requires those fields inside the nested receipt. The omission is identical across protected/candidate and the 44 otherwise analyzable pilot/formal attempts. The remaining cumulative attempt is the already-preserved historical `R00-ON-NoPatch-pilot-01` failure: its A-side runner process group could not be proven gone, so B was skipped. Local reproduced the receipt-shape failure through the analyzer's isolated build-binding check and retained a machine-readable diagnosis. This is a source/tool contract failure, not a formal pair failure; retrying current formal pairs would reproduce the same immutable receipt shape.

Local did not modify the producer, analyzer, `WEB_TO_LOCAL.md`, or any source/tool contract; did not relabel the formal evidence; did not enter V05/M08; and did not begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `f5e34235...`; exact `SourceTargetVerifiedNotBuildAccepted` for `27df1a3d...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling on its actual branch worktree; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt SHA `4d8afaea...`; protected receipt SHA `54bfe84c...` |
| V01 bounded Primary | `Passed` | 368/368 |
| V01 focused validation | `Passed` | 126/126 plus both PowerShell recovery suites |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,053 total; 1,025 Passed; 28 environment Skipped; 0 failures/errors |
| V01 Unity EditMode | `ReusedAuditedFromD18` | Historical 1,076/1,076 only after exact source audit; not fresh execution |
| V01A source audits | `PassedExactSets` | Exact 3-path and 22-path non-metadata sets |
| V02 retained evidence | `PassedRetainedEvidenceReauthentication` | 33,792 files / 1,606,993,133 bytes / zero mismatches |
| V04 graph bridge | `Passed` | New bridge SHA `c03665db...`; retained runner SHA `afc0b649...` exact |
| V04 retained-pilot admission | `Passed` | 5 attempts; 4 selected; exact historical runner; no deep reconstruction |
| V04 guard-v2 pilot seal | `Passed` | Stable stat guard exact; no device; 8/8 deep sides; SHA `bdc4062a...` |
| V04 formal pair 1 authority | `Passed` | A has no authority; current B authority consumed; real Player launch; receipt echo exact |
| V04 formal series | `PassedAllFormalPairs` | 40/40 first-attempt passes; 10 per mode; zero retries |
| V04 final analysis | `Incomplete` | `ComparabilityIncomplete`; 0 valid / 45 invalid: 44 nested-receipt schema mismatches plus 1 preserved historical pilot process-cleanup failure |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory V04 final analysis did not pass |

### Root cause and required Primary correction

The Player-side R00 producer and strict final analyzer disagree about the nested raw build-receipt schema. The producer places `baselineBuildId` and `runtimeAbiHash` at R00 top level but not inside `playerBuildReceipt`; the analyzer requires the same values inside `playerBuildReceipt`. The design allowed the mismatch because launch-time and cached-admission verification authenticated path/hash/build-GUID and top-level authority, while the final analyzer applied a stricter nested-field contract only after the complete series.

Primary must reconcile this contract and add fail-closed coverage. The durable choices are to make the producer echo both fields into the nested receipt, or to deliberately revise the analyzer to bind the authenticated top-level fields instead. Primary must also decide, based on the corrected contract and immutability rules, whether these 40/40 raw attempts may be reanalyzed or whether a new formal series is required. Local must not make that semantic decision.

### Retention checkpoint

The authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`. It contains current authority/tests/audits, retained evidence authentication, the new bridge/admission/guard-v2 seal, all 40 cumulative sample indexes, the batch receipt, strict analyzer output and logs, the contract-failure diagnosis, prior checkpoint manifest links, handoff snapshots, raw evidence, all referenced formal side evidence, and a SHA-256 manifest. The large side-evidence archive is split into ordered parts for Git transport; concatenating the parts reconstructs aggregate SHA-256 `fda8226ee124ecc7d6687e2bbbab30d2166c838fd5fc7225b9972d949982f75f`.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
