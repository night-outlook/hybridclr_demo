# Primary Implementation -> Local Validation — ACTIVE ONE-USE R03 CURRENT-NATIVE + ORIGINAL S

**Current execution authority: ONE new Local cycle only, R03 IR-R03-01/02 evidence, not human approval.** Replaces the previous CLOSED handoff (f51d was completed/consumed and remains read-only). Authorization is limited to one unused physical output root, one corresponding source-pinned launch of run_current_native_validation_cycle.py, and one original-S historical audit within that fresh root. If admission fails, stop before creating output; report Blocked. If execution starts and fails, preserve the original root and return; never reuse a failed/partial root or rerun a consumed cycle. No H2, M08A, X02, SNAP-01, production deployment or R03 acceptance may be inferred.

## 1. Exact repositories and source authority

All repositories on branch codex/assembly-shadow-r01b-h1, canonical GitHub HTTPS night-outlook/<repo>.git. **The final latest-pushed demo HEAD is supplied as the full 40-character demo commit in the final Primary-to-Local copyable prompt for this handoff and MUST match live GitHub remote HEAD; it is the operative fourth source pin.** Git cannot embed its own final commit SHA inside the contents of that same commit. The following demo code anchor is a fixed ancestor, **not** the transport HEAD to pass as --demo-commit.

| Repo | Exact latest source requirement | Expected local path |
| --- | --- | --- |
| night-outlook/hybridclr_demo | code source anchor 9d5d2b4a885e0109388554ad07271ede2d829534; actual final pushed transport HEAD = explicit demo 40-SHA in final short handoff prompt | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity |
| night-outlook/il2cpp_plus | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus |

Path values describe the prior actual Local checkout layout, not an assertion that the web agent inspected today's Mac filesystem. Local must verify actual exact paths and each remote identity/HEAD, clean status, branch and original submodule/package source resolution before operating. The code-source commit 544f introduced the final coordinator and stricter no-survivor checks; any future documentation-only descendant must preserve exact corresponding implementation Git blobs and old historical source contract. Do not pick an arbitrary moving HEAD or reset unrelated local changes to match.

Separate **historical** source, NOT the fourth current code pin: a new clean, exact hybridclr_demo worktree at fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b, containing complete original S committed nine-part transport and checkout evidence. Original S actual executed demo was 29bb3d4a39bf8a2f23be404f77535aaba3485bfc and native 1cf87f8209790f9fb2ebec97487dc1990ccd56c5. It is read-only source for audit only. The separate historical R03 focused runner native 74dbdbea80d83923863303bd2b2c0a87f36541b1 remains unchanged in original source-pins.json; the new candidate switches to e1e5 **only in memory**. Never change either historical native identity to manufacture a match.

## 2. Read order and explicit scope decision

Read first:
1. Docs/AssemblyShadow/README.md.
2. This canonical Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md.
3. Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/DESIGN.md and PLAN.md and PRIMARY_SOURCE_REVIEW.md and EVIDENCE.json.
4. Docs/AssemblyShadow/Plan/stages/R03-evolution-semantics.md, Plan/HUMAN_REVIEW_GATES.md and Plan/CURRENT_STATUS.md.
5. The October 8 immutable independent full-stage FAIL at History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md and erratum, October 26 RC1–RC6 matrix, D1=A/D2=A owner disposition.
6. Read latest Local-owned LOCAL_VALIDATION.md and RETURN_TO_WEB.md, f51d checkpoint and Primary reconciliation, **without** re-running f51d/b7e3/c42a/e1e5/6c72 or older S outputs.

Scope is exactly a new R03 current-native terminal post-poison five-case witness **plus** full immutable original S provenance/process crosswalk **plus** current-native diagnostics and installed-source parity. This is a focused empirical input for a separately initiated independent R03 re-review. It is not an independent reviewer verdict, all R03 RC1–RC6 support, original S semantic acceptance, Phase P1, H2 Human Review Gate, or any next milestone.

Owner decisions remain D1=A (conservative NativeLayoutAdmissionV1 only; structural extension X02 deferred) and D2=A (performance observational only, contaminated warm certificates Failed). PureInterpreter remains disabled. The historical 90/90 S remains scoped history, b7e3/c42a overall Local FAIL remain immutable, and f51d remains historical audit-only PASS.

## 3. One-use Local resources, preparations and hard stops

Use an isolated macOS Apple Silicon environment with a genuine, matching Unity **2022.3.62f2** executable; independently locate the installed Unity app (do not assume a path). Before any new root:
- All four exact full Git SHAs from the final handoff prompt must match local HEAD and live GitHub origin refs/heads/codex/assembly-shadow-r01b-h1. Confirm clean tracked AND untracked status, correct owning checkout, branch and remote; preserve unrelated working trees, never reset/clean them.
- Source git objects for existing ten-file current candidate manifest and 42 current native VM changed files must match the code, and no pinned external code has changed.
- Confirm original S source worktree destination and batch destination are nonexistent, physically canonical, non-symlink, disjoint from all four sources, each other, all old consumed Local roots and outputs, and disk free >=20 GiB. Do not delete/prune/reuse originals. If original S worktree already exists at the proposed destination, use a new explicitly documented unique name (not an existing root); do not reuse arbitrary untrusted history.
- Confirm no Unity/IL2CPP/App/Player processes from another run are active in the same isolated fixture workspace. Avoid interfering with other developers' processes. Do not rerun on failure.
- Canonical proposed workspace is /Users/ah/GitHub/hybridclr/assembly_shadow_h1r, original S destination /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse, and new output /Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261026-oneuse-A. Use them ONLY if absent and independently verified; if different, record the exact canonical replacements before launch. The web agent has not created or inspected these on the Mac.

Create a **new** original S worktree once from the demo repository:
    git -C "$WORKSPACE/hybridclr_demo" worktree add --detach "$ORIGINAL_S" fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b

Do not force it and do not mutate its files. Verify HEAD fc55, clean status and canonical remote. Because this worktree contains original S archive, its storage may be substantial. If full original checkpoint is missing or cannot be materialized, declare original S audit Blocked and return to Primary rather than silently skipping its required evidence.

## 4. Authoritative **single** execution command

After exact source and environment admission, choose absolute values for:
- WORKSPACE: the canonical four-repo parent.
- ORIGINAL_S: new exact fc55 historical worktree.
- UNITY_EXE: real Unity 2022.3.62f2 executable.
- RUN_ROOT: ONE previously nonexistent, isolated output root.
- DEMO_COMMIT: **the final full 40-char pushed demo branch HEAD from the closing Primary handoff prompt**, not code anchor 544f and not old S commit.

Invoke exactly once:

    PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"

The coordinator checks real repo/remote/Git/source/disk/arm64 authority **before creating RUN_ROOT**; reject an existing root. Do not run individual old historical S, b7e3, c42a, f51d, R03 legacy native runners, ordinary M07 or R02 project commands as a substitute. The output root is owned by this single new invocation. No agent may automatically retry it, change source pins to bypass a failure, or invoke a new sibling root without fresh Primary authorization.

## 5. Ten required stages / empirical contracts

Stages collected in the single coordinator's RESULT.json:
1. source-contracts: original 20 current-native source/adversarial tests.
2. oracle-contracts: original 27 synthetic tests invoking the real Player verifier; not Player evidence.
3. vm-delta-contracts: original 12 actual 42-VM-file Git blob tests.
4. original-s-host-contracts: original 30 host-only provenance contracts.
5. installed-source-host-contracts: 15 synthetic physical installed VM parity negative/positive tests.
6. original-s-audit: existing audit_s_provenance.py; reauthenticate all nine original S parts (aggregate 587907380 bytes, SHA256 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6), original index 15713 archive members, exact original S 90/90 ledger, receipt/hash/seal; **no historical Player re-execution**. Do not confuse withdrawn five-part archive f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7 with original S.
7. original-s-process-joins: existing audit_s_process_joins.py crosswalks 59 ORIGINAL archived Player process/request/raw/build roles (after six full original audit prerequisites). Not a new process launch, independent reviewer verdict or complete original source/build/Player semantic inspection.
8. native-host-diagnostics: existing run_primary_host_preflight.py bounded native diagnostic stream, codec, transaction and legacy sink host tests plus strict/sanitized C++ checks if compiler available, with independent raw result and no Unity acceptance.
9. current-native-players: existing run_terminal_current.py, exactly three fresh native Builds (feature-ON Release, feature-ON Debug, feature-OFF Release), five fresh real OSX arm64 Unity Players:
    IR-R03-02-release-baseline,
    IR-R03-02-debug-baseline,
    IR-R03-02-release-type,
    IR-R03-02-off,
    IR-R03-02-release-engine.
    Enforce correct current e1e5 source installation/build-v2 before/after native inventory and copied current/older fixture authority, installed Unity binary architecture and source manifest, original typed first failure, genuine valid post-poison reflection/delegate/AOT canary attempted after catch, no method body side effect, stable first recovery, native engine unhandled-sentinel path, OFF healthy negative, process/nonce/build source joins, actual Player log/raw positive and rejection evidence. A good synthetic verifier test cannot substitute for actual Player raw.
10. native-installed-source-audit: new current_native_install_audit.py compares each of the 42 changed VM files' exact current native Git blob bytes to physically installed source in all three actual built role trees, including actual build receipt-v2 before/after inventories, Release/Debug/OFF config and four source pins. Require 3 x 42 = 126 matching source-install file pairs. This source parity **does not** establish complete transitive C++ include closure, generated C++ compiler inputs, object/linker identity or final binary execution semantics; retain those as explicit independent review targets.

If a source/oracle/VM host check fails, no new current-native Player may launch. Original S and native-host diagnostics may still collect independent evidence, but the composite result is ReturnRequired. If original S or native host fails, the current Player may independently finish its fixed valid scope after source gates; overall still ReturnRequired. After a real Player succeeds, the physical VM parity audit must succeed too for the composite focused result. No successful component can erase another Failed/Blocked/NotRun.

## 6. Required evidence and failure return

Retain the fresh root exactly as produced:
- ADMISSION.json, RESULT.json, COORDINATOR_MANIFEST.json (coordinator receipts only; NOT a substitute for child source/Player/archive sealing).
- steps/<stage>/{INVOCATION.json,RESULT.json,stdout.log,stderr.log}, recorded PID/group ownership, exit/timeout/command/environment and SHA256. Ensure no surviving owned subprocess; do not declare PASS if any remain. If an independent child detaches outside the process group, record uncertainty, stop and report.
- original-s-audit/audit.json, checkpoint-git-crosswalk.json, original-archive-members.json, ninety-cell-crosswalk.json, original reconstructed file hashes and original-s-process-joins/process-joins.json.
- native-host-diagnostics/RESULT.json and original per-test native receipts (actual strict/sanitized results; Unavailable is not Passed).
- current-native/LOCAL_BATCH_RESULT.json, BATCH_EXECUTION.json, seal-receipt.json, source authority, original-S fixture authority, all 3 builds' build-receipt.json/source-inputs.json/source pins, before/after native inventory, installed native actual source, generated method-pointer/invoker material where present, lipo arm64 verification, all 5 Player requests/launches/raw/logs/verification; include negative/rejection/canary values and original first failure code. Preserve untouched original S history and earlier failed Local roots.
- installed-native-vm-parity.json with 126 expected source-installed bytes and exact three roles, noting its nonproof of binary linkage.
- Actual before/after clean Git status, origin, branch, live remote HEAD SHA across all four; original fc55 worktree clean after; exact Unity 2022.3.62f2 host info and disk capacity; retain failed/blocked/NotRun results with causal receipts. Do not omit negative test failures or full stdout/stderr.
- A new additive, provenance-bound Local checkpoint under Docs/AssemblyShadow/History/M07R/R03 (no rewrite), SHA manifest, local evidence root reference and Source/Evidence provenance. Update **Local-owned** Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md (when findings exist), commit/push all factual new records, verify remote after push.

The Local Agent may perform bounded environment preparation, diagnostics, build re-execution within the one originally authorized one-shot coordinator only, and minor local changes only when independently closed-loop safe and expressly permitted. **Nontrivial source/design changes, architecture, native semantics, new regression/fixture design, identity rule changes, reinterpretation of source/Player evidence or additional root retry belong to Primary.** Return full errors and preserved evidence to Primary, do not force tests green or change expectations.

## 7. Pass ceiling, known blockers and next agent

A completely green ten-stage fresh Local cycle can report only FocusedEvidenceReadyForIndependentReview. It is NOT a fully independent R03 semantic review, IR-R03-01 closure, IR-R03-02 universal-path closure, R03 acceptance, H2 pass, runtime/production qualification, P1/P2/E0/E1/full P3 close, structural PureInterpreter admission or performance SLA. The initial independent R03 verdict remains **FAIL** until a separately human-initiated full-stage re-review returns a new evidence-based verdict.

Remaining limitations: IR-R03-02 current-native five-case execution not yet performed as of Primary handoff; captured generic and initializer terminal variants, alternate virtual/interface/AOT entry paths and true source inclusion/linker/Player binary closure remain outside this bounded witness. IR-R03-01 original S generated oversized method-pointer/invoker materials, full original source/build/Player/process semantic authenticity, resource ABI, M01 NoCoverage and RC1–RC6 still need independent review. D1=A/D2=A and contaminated Failed performance certificates unchanged. Original b7e3/c42a FAIL and f51d limited historical audit PASS untouched. No H2/M08A/X02 or Human Review Gate without separate human initiation.

**One-use transition:** Primary Implementation -> Local Validation for empirical evidence; stop immediately after factual validation/checkpoint publication and return to Primary. No autonomous next milestone.
