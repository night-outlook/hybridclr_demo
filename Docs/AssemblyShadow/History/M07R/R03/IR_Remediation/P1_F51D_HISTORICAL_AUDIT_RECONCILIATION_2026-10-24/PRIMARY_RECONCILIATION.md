# Primary Implementation reconciliation — f51d historical audit-only result

**Disposition: CONFIRMED PASS, historical-evidence-audit scope ONLY. No R03/P1/runtime acceptance.**

## 1. Authority, source tuple and reviewed evidence

The authoritative latest Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` published at `hybridclr_demo@ac32d96939147f0309ddd8679e2d0fe8c9986592` document ONE completed `20261024-f51d` isolated historical audit. They do not authorize a repeat. Original audit execution used demo source `ea530e59eef38175738e517110c698ebd31bb07f`, plus `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. Original `b7e3` EXECUTED demo source `49c6b62d38d7668be10004ac1e5a030d74894f09` and original `c42a` audit EXECUTED demo source `26a4ea22aa0a11f1e86c8d2ac2aa4bd55a308a05` are distinct; never substitute today's branch HEAD for those captured pins.

Original Local evidence: [f51d README](../../local-audit-only-p1-20261024-f51d/README.md), [factual Local result](../../local-audit-only-p1-20261024-f51d/LOCAL_RESULT.json), [raw f51d evidence report](../../local-audit-only-p1-20261024-f51d/stage/EVIDENCE_AUDIT.json), [one-shot invocation receipt](../../local-audit-only-p1-20261024-f51d/stage/AUDIT_ONLY_RUN_RECEIPT.json), [admitted execution verification](../../local-audit-only-p1-20261024-f51d/stage/ADMITTED_EXECUTION_VERIFICATION.json), [historical Git authority](../../local-audit-only-p1-20261024-f51d/stage/GIT_HISTORICAL_AUTHORITY_AFTER.json), [supplied after receipt](../../local-audit-only-p1-20261024-f51d/stage/AUDIT_ONLY_AFTER.json), [independent preservation](../../local-audit-only-p1-20261024-f51d/stage/F51D_INDEPENDENT_AFTER.json), [f51d immutable manifest](../../local-audit-only-p1-20261024-f51d/MANIFEST.sha256).

## 2. Verified historical-audit outcome

| Requirement | Observed factual evidence |
| --- | --- |
| Source-only prerequisites | 17 + 11 + 23 = **51/51 passed**; existing Mac/Linux source-only CI run `40076790889` also passed on both systems |
| Isolated staged auditor | Exactly one historical audit invocation, PID `47743`, **exit 0**, `timedOut=false`, `unknownCommandLifetime=false`, 25.0492 elapsed seconds |
| Run result | `PassedHistoricalAuditOnly_UnchangedLocalFail` in the invocation receipt |
| Complete new report | `EVIDENCE_AUDIT.json`: `PassedHistoricalEvidenceAuditOnly`, mode `ReadOnlyIsolatedB7E3History`, `originalB7E3LocalResult=FAIL`, `productAcceptance=false` |
| Historical outer components | Original `PassedSourceHostAndSDKOnly`: **25/25 passed** (not newly executed) |
| Historical source/host test evidence | Original **85** test identities and eight inventories; admitted execution **nine strict + nine sanitized** groups; original negative helper/17 mutation cases source-bound |
| Captured compiler/command evidence | Five original managed positives + original expected compiler-negative (two CS0266), original **100** native syntax commands, **515** localized command-stream receipts |
| Captured Git authority | `PassedCapturedB7E3HistoricalSourceAuthorityOnly`: four historical repo pins, previous twenty direct Git postflight receipts; **NO claim** that current live remote HEAD equals historical `b7e3` SHA |
| Source/SDK/history custody | Supplied and independent after-preservation **Preserved**; **4,269** raw, **2,405** installed SDK, **1,925** SDK scratch, **104** original preflight, **2,506** b7e3 checkpoint entries, **197** c42a checkpoint entries, 165 c42a external files, previous 22 consumed P1 sets/24 checkpoints/88 symlinks |
| New errors or code edits | New nontrivial findings `[]`; no product/native code changed; no Unity/SDK compiler/Player or original core rerun |

The previously unreached admitted-execution helper source check and the final historical Git evidence assertion both completed in **f51d**. The earlier `c42a` failure was a *source-identity lookup error*, corrected in a separate new auditor; no old source was rewritten.

## 3. Independent Primary publication/source checks and limitation

Using the GitHub Connector against the exact Local-published commit, Primary verified all four repository/branch HEADs, the original `b7e3` and `c42a` actual saved FAIL receipts, and the new `f51d` JSON result, completed auditor report, source-bounded Git report, run receipt and independent preservation report. The `f51d` manifest has **206 unique paths**. Primary independently recomputed **seven SHA-256 hashes directly from fetched UTF-8 GitHub file bytes**—Local result, reconciliation, completed audit, invocation, supplied after, independent after and captured historical Git report—and confirmed all **7/7** equal the immutable `MANIFEST.sha256` entries; SHA-256 computation was self-tested against known reference digests.

GitHub comparison of audited-source demo `ea530e59eef38175738e517110c698ebd31bb07f` to Local publication `ac32d96939147f0309ddd8679e2d0fe8c9986592` shows **one Docs-only commit**, adding this distinct f51d checkpoint and updating Local-owned reports; no source/product changes. Comparison from code anchor `117cc6b1c2be8050cd2f433ef17db8b3c5138f93` likewise shows no non-Docs/CI paths changed (GitHub compare may cap file listings; the direct source/publication comparison is authoritative for this cycle). Original b7e3/c42a Local outcome JSON and original auditor data remain their historical Git blobs.

**Independence limit:** Primary directly verified these seven published file digests and selected structured receipts, **not every one of the 206 f51d checkpoint files** and not the complete external original `/Users/ah` raw/SDK/scratch/historical trees. The 4,269/2,405/1,925/full history before/after checks were performed and reported by Local, with both after-verification receipts published in GitHub. Thus the supported statement is **historical-evidence-audit-only PASS with validated published evidence**, not new independent runtime/product/SDK compilation acceptance.

## 4. Historical outcomes MUST remain distinct

| Historical cycle | Immutable outcome |
| --- | --- |
| `7896` and `7c2c` | `PassedSourceHostAndSDKOnly` (prior source/SDK host scope) |
| `82dd` | `FailedOrIncomplete` raw aggregate |
| `e1e5`, `6c72` | `PrerequisiteBlocked`; core not run for those cycles |
| `b7e3` | Raw **`PassedSourceHostAndSDKOnly` 25/25**, but original required independent auditor failed at line 190; overall Local **FAIL** |
| `c42a` | Separate isolated audit-only **FAIL**, `StopIteration` at line 1031; old Local report/evidence unchanged |
| `f51d` | New **`PassedHistoricalAuditOnly_UnchangedLocalFail`**, no reclassification of b7e3/c42a |

No report is retroactively changed from FAIL or Blocked to PASS. Original independent full-stage R03 review/gates and protected SNAP-01 restrictions are not dismissed by this audit-only result.

## 5. Remaining engineering/acceptance gates and authoritative next state

- **P1 Incomplete**: complete canonical execution TypeKeys, physical `Il2CppClass*` origin/lifetime, coherent whole-VM epoch, safe full execution V1/original getter integration, actual runtime initialization/shutdown and GC/RSS/Player validation remain unproven.
- **P2 NotIntegrated. E0 Blocked/Unavailable. E1 BlockedByE0. Full P3 Incomplete.** Product/Player runtime path and the broader independent stage-acceptance evidence remain outstanding.
- `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; **PureInterpreter disabled**.
- The completed source/host/SDK evidence should remain available as a bounded basis for future planning, not a substitute for a fresh formally authorized implementation/integration and Human Review Gate. **No further Local audit-only or SDK/core rerun is authorized by the consumed f51d handoff. Do not begin H2/X02/M08A or protected SNAP-01.**

**Primary disposition:** CLOSE the audit-only evidentiary reconciliation as **completed within its stated scope**; leave substantive runtime/integration/qualification work OPEN, with any next Local work gated on a new explicit Primary plan and authorization.
