# R03 oneuse-K — Primary Implementation evidence reconciliation (2026-11-04)

**Classification:** Primary Implementation assessment after Local K. **Not** an independent re-review, full-stage acceptance, Human Review Gate, new Local validation authorization, or a rewrite of historical S/I/J verdicts. The original 2026-10-08 independent R03 review remains **FAIL**, with High IR-R03-02 and IR-R03-01. K itself is **PASS only within its focused scope**.

## 1. Frozen source and evidence authority

| Role | Repository and immutable SHA |
| --- | --- |
| K Unity/host execution | night-outlook/hybridclr_demo @ c20da0b261172cbdd188378e24dbe9343a14c6b2 |
| K Local checkpoint publication | night-outlook/hybridclr_demo @ 14f97f15af6c06afa65957a9b880ccf841069452 |
| Interpreter | night-outlook/hybridclr @ 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| Unity package | night-outlook/hybridclr_unity @ 948c0e3b4f8891481301770115e8ba4945eea6de |
| K native | night-outlook/il2cpp_plus @ 41764ae1eeefb33b05966e7f7676e52aae39c340 |
| Original S execution | demo @ 29bb3d4a39bf8a2f23be404f77535aaba3485bfc; native @ 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 |
| Original S immutable checkpoint | demo @ fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b |
| Original independent R03 source review | demo @ aee7975874a5ddf236ab9d00d5d682b470010f8f; original native @ 1cf87f8209790f9fb2ebec97487dc1990ccd56c5 |

All four active branch HEADs were read directly from the GitHub Connector after the K handoff and matched the reported Local publication tuple. The K source-to-publication comparison is one descendant commit; do not substitute the publication SHA for the actual Player execution SHA. Branch: codex/assembly-shadow-r01b-h1. Workspace paths are documented by [K checkpoint](../../local-validation-current-native-original-s-20261103-oneuse-k/README.md).

Evidence read directly at the K publication SHA: [K result](../../local-validation-current-native-original-s-20261103-oneuse-k/LOCAL_RESULT.json), [coordinator](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/RESULT.json), [child producer](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/current-native/LOCAL_BATCH_RESULT.json), [actual Player/runtime observations](../../local-validation-current-native-original-s-20261103-oneuse-k/RUNTIME_FINDINGS.json), [ten-component host gate](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/native-host-diagnostics/RESULT.json), [official installed-source parity](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/installed-native-vm-parity.json), and [independent Local preservation audit](../../local-validation-current-native-original-s-20261103-oneuse-k/local-evidence/oneuse-K-FINAL_INDEPENDENT_AUDIT.json). The original [October 8 review](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md), its [citation erratum](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md), [original S provenance correction](../ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json), [generated-source omission index](../ORIGINAL_S_CAPTURE_OMISSIONS_2026-10-08.md), and [RC1–RC6 matrix](../IR_R03_REREVIEW_PREP_2026-10-24/R03_RC1_RC6_CLOSURE_MATRIX_2026-10-26.md) were also examined.

Primary independently queried the nine real GitHub Actions push workflow runs 41630559141, 41630559134, 41630559223, 41630559149, 41630559135, 41630559129, 41630559213, 41630559137 and 41630559182, including each job endpoint: all nine were completed/success on exact K execution SHA, each with two completed/success macOS/Ubuntu jobs, 18/18 total. These are source/host/fixture CI, not Unity Players. No Unity, IL2CPP or full evidence-archive execution was performed in the web environment. Original-S/K multi-gigabyte archive hashes, live Mac filesystem custody and every byte of the original-S generated sources were **not** independently recomputed by Primary in this session; the Local receipts and Actions logs are evidence to be independently challenged.

## 2. K evidence classified by its actual scope

| Contract | Fresh K evidence | Nonclaim |
| --- | --- | --- |
| Actual host admission and ten components | Two independent read-only admissions; eight historical native host commands and two fresh current C++11 owner suites passed before Unity | Host tests are not Player acceptance |
| Source/build | Three fresh Unity 2022.3.62f2 arm64 IL2CPP C++11 builds (ON Release, ON Debug, OFF Release), BuildReport Succeeded, errors 0, warnings 1 per role | Not whole-binary generated-code linkage or all-platform coverage |
| Actual Player method entry | Five distinct PIDs and successful original verifiers; ON baseline Release/Debug and type-resolution attempted active reflection, delegate and AOT after poison; ON canary 1→1, shadow field 2→2; OFF ordinary canary 1→2 | Captured-generic failure and post-publication initializer failure are explicitly NotRun in the K child receipt; does not enumerate every virtual/interface/bridge entry |
| First failure and fixed diagnostics | ON pre-call positive 42; post-call attempt flags true; state remains FailedAfterCommit (9), original recovery failure/restart disposition stable, fixed diagnostics readable; general sidecars 540,959 / 540,382 / 540,759 bytes passed bounded length/CRC/hash/strict schema | Sidecar records explicitly say coherentVmEpochProven=false |
| Engine terminal observer | Frame-originated engine sentinel; first terminal code 13; one native quit call, one native wants response and quit notification; 11 completed real reports in 103ms, NativeAtexit, exit 0 | Native-only test response deliberately bypasses managed quit subscribers; C-runtime exit is not complete Unity-managed Shutdown or full GC/RSS acceptance |
| Full child/coordinator | 18/18 child cells, ten coordinator stages, complete typed producer consumed, fresh K seal, coordinator exit 0 and FocusedEvidenceReadyForIndependentReview | Full R03 independent assessment remains NotRun |
| Native installed-source parity | 45 changed VM Git source files × three successful build roles = 135 exact installed-source pairs, official audit PassedInstalledSourceParityOnly | The official parity receipt explicitly says fullNativeIncludeClosure=NotProven, generatedCppBinaryLinkage=NotProven |
| Original-S custody | Nine-part / 15,713-member historical S archive audited, 90 **historical** cells and 59 historical process joins, 16,978 protected files, 13 prior checkpoints and 2,405 installed SDK inputs preserved | Historical execution is not a fresh K source-equivalent Player, and source/build/Player semantic completeness is not independently approved |

K's archived native child is a bounded evidence object; retained larger raw inventory is 46,661 files / 6,414,459,908 bytes, with its exact published manifest, copy bindings and retained Mac artifacts. Do not call the archived K child's evidence archive the original historical S archive: their digests, provenance and execution tuples differ.

## 3. Original independent High findings: Primary dispositions

### IR-R03-02 — terminal method entry after poison — **SourceCorrected / ScopedRealPlayerEvidencePassed / IndependentClosurePending**

The original independent reviewer found that the then-native AssertMethodIsActive could return success for an otherwise valid method despite existing terminal state, allowing RequireActiveMethod and interpreter entry to miss the poison. The original source-derived counterexample was not a real Player reproduction. The erratum corrects a mistaken assertion that original S C04 JSON explicitly recorded post-poison attempt flags: they were **absent**, not false.

At K native 41764ae1..., direct source inspection of libil2cpp/vm/AssemblyShadow.cpp shows AssertMethodIsActive checks TerminalMethodDenied *before* method resolution (around lines 1954–1960); RequireActiveMethod rechecks terminal denial before constructing its exception (around lines 2068–2100). The current Runtime.cpp invokes RequireActiveMethod at Invoke/InvokeWithThrow boundaries (around lines 652/673), and HybridCLR Interpreter_Execute.cpp uses REQUIRE_ACTIVE_METHOD for initial, nested, delegate and numerous opcode entries. These are source observations, not a complete endpoint audit.

The K three ON post-poison cases now provide genuine pre-positive plus attempted and denied valid method entry and observable unchanged primitive state. The OFF control executes normally. Thus the original specific valid-identity-after-poison concern has both a code correction and fresh bounded runtime regression evidence. **Do not declare the High finding independently Fixed** until a separate reviewer inspects the actual source/binary/Player chain and tests the required scope. K explicitly reports capturedGenericFailure=NotRun and initializerFailure=NotRun; other applicable generic/virtual/interface/managed-AOT/old-handle entry paths remain subject to reviewer coverage. The original October 8 FAIL is immutable.

### IR-R03-01 — original S archive/source evidence contradiction — **CorrectedAuthoritativeBytes / HistoricalCustodyAudited / IndependentSemanticClosurePending**

The immutable original S authority is the **nine-part, 587,907,380-byte** evidence.tar.gz SHA-256 **23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6**, 15,713 members, with index SHA-256 0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70. The older **five-part, 283,728,477-byte** f4c2a120... family remains preserved but is **withdrawn as original S authority**, not declared transformed or matched to the original S. The independent October 8 contradiction is real historical evidence.

The Primary-authored original S correction and pinned audit identify the authoritative bytes and 90 original cell ledger joins; K independently reports the latest read-only original S archive/process preservation. This materially strengthens custody but **does not establish a separate independent semantic and executable provenance review**. In particular the four original S occurrences of Il2CppGenericMethodPointerTable.c and Il2CppInvokerTable.cpp were byte-identified but not fully semantically inspected, and the original capture omissions index was not exhaustively reconciled. K's *new* 135 source-install pairs refer to current native/build roles and cannot be substituted for original S's generated C++ build/executable identity. The withdrawn family's origin/transform remains unresolved. Leave High IR-R03-01 **open pending independent review**.

## 4. Residual RC1–RC6 and adjacent obligations

- **RC1:** D1=A conservative NativeLayoutAdmissionV1 holds; unsupported structural expansion remains deferred to separately qualified X02, never silently accepted by K.
- **RC2:** Original S resource and Unity ABI/source/serialized asset coverage requires independent source/resource/consumer pairing; original M01 NoCoverage is not retroactively Passed.
- **RC3:** K substantially improves the original active-method-after-poison evidence; captured generic, initializer, other entry paths, whole-VM coherence and legacy old-handle obligations remain to be classified by an independent reviewer.
- **RC4:** Original S P01–P05 and installed-baseline/target-graph source and cumulative role/graph acceptance must remain tied to the original historical record; K did not rerun them.
- **RC5:** D2=A remains observational. Four contaminated warm certificates remain Failed; R02 CPU and H1 RSS risks are not accepted as production performance qualification.
- **RC6:** Original S provenance remediation and K current-native receipt joins are different evidence families; complete semantic audit and an independently issued R03 full-stage verdict remain required.

Other tracked unfinished work (P1 incomplete, P2 not integrated, E0 unavailable/blocked, E1 blocked by E0, P3 incomplete) and full Unity-managed Shutdown/GC/RSS/global VM-epoch/legacy regression acceptance are unaffected by a five-Player focused result.

## 5. Next action and STOP boundary

**Next eligible action:** the user/development owner explicitly commissions a **separate independent R03 full-stage design → plan → implementation → raw-evidence review**, using [the fixed K re-review brief](INDEPENDENT_REREVIEW_BRIEF.md) and the exact execution and evidence-publication tuples above. The reviewer must return independent issue-by-issue decisions and RC1–RC6 status, not inherit Primary's labels. Additional Local source-bound tests are warranted **only** if that reviewer identifies concrete missing executable proof; Primary must first design and authorize a new distinct Local cycle, with its own admission/custody/budget and one-use authority. Do not rerun K/J/I or regenerate prior evidence.

No new product/runtime source modification is justified solely by K's PASS. This cycle publishes a documentation-only Primary reconciliation and closes the consumed K handoff. It does **not** initiate a new review, run Local Validation, enter H2/M08A/X02/SNAP-01, or declare human approval.

Current flags remain: R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; qualificationApproved=false; runtimeAcceptance=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled.
