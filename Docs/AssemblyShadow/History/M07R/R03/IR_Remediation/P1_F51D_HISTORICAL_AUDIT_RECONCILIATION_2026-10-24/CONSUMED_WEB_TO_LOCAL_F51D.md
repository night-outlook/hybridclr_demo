# Primary Implementation → Local Validation — ONE new f51d isolated historical audit-only cycle

**NEW and EXCLUSIVE authority:** The prior `20261023-c42a` one-shot historical auditor was consumed and **FAILED**, StopIteration at line 1031, with no complete audit report. Original `20261023-b7e3` Local result also remains FAIL despite separate raw `PassedSourceHostAndSDKOnly` 25/25. This handoff supersedes the previous executable c42a handoff. It authorizes exactly **ONE** fresh, source-pinned **historical AUDIT-ONLY** `20261024-f51d` cycle after independent admission. It does **NOT** authorize a retry of c42a, another b7e3 core/test/SDK compiler/Unity/Player run, any production/source adaptation by Local, or any new project milestone.

## 1. Mandatory authoritative read order

1. `night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md`.
2. Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` FIRST, followed by `Handoff/RETURN_TO_WEB.md`; latest Local must still say **c42a FAIL**.
3. Immutable **c42a** checkpoint `History/M07R/R03/local-audit-only-p1-20261023-c42a/README.md`, `FINDING.json`, `LOCAL_RESULT.json`, `MANIFEST.sha256`, `stage/AUDIT_ONLY_RUN_RECEIPT.json`, `stage/AUDIT_ONLY_AFTER.json`, old `stage/audit.py` and retained logs, plus original **b7e3** raw/checkpoint/historical source receipts.
4. Current source-bound [Design](../History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/DESIGN.md), [Plan](../History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/PLAN.md), [Primary Source Audit](../History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/PRIMARY_SOURCE_AUDIT.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/EVIDENCE.json) and **all five** new scripts; read the ENTIRETY of this handoff.

**Do not execute old c42a, b7e3, e1e5, 6c72 or any superseded Local script from a consumed root.** Never treat earlier historical prompts or current source-only CI as an accepted full independent audit.

## 2. Canonical repositories, source revisions and source-only CI

All four independent repositories use branch `codex/assembly-shadow-r01b-h1` and origin `night-outlook/<repo>`. The Local actual working copies are under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/{hybridclr_demo,hybridclr,hybridclr_unity,il2cpp_plus}`; parent workspace is NOT a repository. Require exact clean local HEADs and current remote HEAD equality before creating any new root.

| Repository | REQUIRED current pushed HEAD |
| --- | --- |
| `night-outlook/hybridclr_demo` | **Full 40-character latest remote HEAD from the accompanying Primary short prompt**, independently checked. This handoff MUST be contained in that HEAD and be the latest demo file-changing commit. No non-Docs/CI changes from tested-code anchor `117cc6b1c2be8050cd2f433ef17db8b3c5138f93`. |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` |

**Three different demo pins must never be conflated:** original b7e3 EXECUTED source = `49c6b62d38d7668be10004ac1e5a030d74894f09`; original c42a audit EXECUTED source = `26a4ea22aa0a11f1e86c8d2ac2aa4bd55a308a05`; latest Primary DOCS/CI code source = complete current remote HEAD from the short handoff prompt. Original b7e3 `EXPECTED.json` retains historical source, and the new historical auditor preserves **captured event-time Git receipts**, not false live-remote equality with old commits.

**All new exact published Git source blobs:**

| File, relative to `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/` | Required Git blob |
| --- | --- |
| `audit_historical_helper_successor.py` | `220aa2831458b37a81f66555f27d95349ec7013f` |
| `stage_helper_successor.py` | `f0eabc9458de33c8da8b6b0434cc97753689fa92` |
| `run_helper_audit_once.py` | `a4de8e6298c487bfa121242a6df7b80a62276dc3` |
| `test_historical_helper_identity.py` | `25bc8e474d63714ec1182d48463f3d6923dfd892` |
| `test_helper_audit_staging.py` | `2421ff68a62f7db816a8f95c150a7eebd3bc3757` |

**Real source-only CI gate:** [GitHub Actions 40076790889](https://github.com/night-outlook/hybridclr_demo/actions/runs/40076790889), source commit `1fbdb008c82f262c8b4aa56cc33a9d8b54994a92`, **Completed SUCCESS on ubuntu-24.04 and macos-15**, each **17/17 + 11/11 + 23/23 = 51/51** host-only tests. Also both passed the published checkpoint verifier: 2,506 published b7e3 checkpoint files hashed, 2,396/4,269 raw files published, 1,873 original external files unavailable on GitHub, 20 captured Git receipts. The earlier CI 40076486968 was a real test-only FAIL corrected by Primary; do not erase it. The successful CI was **not** a real historical auditor, original SDK compile or Local run.

## 3. Original immutable evidence and fresh SINGLE-USE f51d roots

All these paths are READ-ONLY original inputs, never output:

- `W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` (four separate repos).
- `P=/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3` (original source-bound preflight, 104 retained files).
- `O=/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261023-b7e3` (raw 4,269-file manifest, 25 components).
- `S=/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261023-b7e3` (original 1,925 copied official native SDK inputs).
- Original installed Unity2022.3.62f2 at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` (read-only; DO NOT start).
- Consumed c42a external original stage: `/Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261023-c42a` (failed one-shot, never retry/change).
- Original 22 consumed P1 raw/scratch/audit sets, 24 original checkpoints, 88 prior negative symlinks and all b7e3/c42a/e1e5/6c72/82dd/7896/7c2c history remain immutable.

**NEW SINGLE-USE audit output root only:** `/Users/ah/GitHub/hybridclr/r03-local-validation/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261024-f51d`

**NEW SINGLE-USE additive Git checkpoint:** `Docs/AssemblyShadow/History/M07R/R03/local-audit-only-p1-20261024-f51d/`

Independently confirm BOTH are ABSENT, canonical/nonsymlink, disjoint from each other/all original roots/SDK/four repos, and have never been used, before any creation. GitHub did not contain the f51d checkpoint at Primary preparation; **Local filesystem existence remains unverified until independent admission**. If either is present, changed, or cannot be established unused, **BLOCKED/STOP**, no alternative suffix or silent retry.

## 4. One complete audit-only Local cycle — exact scripts, no Local code changes

Independently validate four current exact repos/branch/origin/clean HEADs, source pins, successful CI, raw/SDK/scratch/104-preflight evidence and the **entire 197-file original c42a checkpoint** before staging. Local may perform read-only hashing/admission. No other major implementation work is delegated to Local.

After independent admission, execute the following source-only prerequisites and stager ONCE. The actual demo SHA MUST equal the explicit accompanying Primary short handoff SHA, not merely the then-live mutable branch. Run commands from a real Mac terminal, without rewriting `TMPDIR`, SDK/SSH settings, source files, manifests or histories:

~~~bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
T="$D/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24"
P="$B/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3"
O="$B/R03-P1-ADMITTED-EXECUTION-20261023-b7e3"
A="$B/AuditOnly-R03-P1-ADMITTED-EXECUTION-20261024-f51d"
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
git -C "$D" diff --exit-code 117cc6b1c2be8050cd2f433ef17db8b3c5138f93 "$DEMO_SHA" -- . ':(exclude)Docs/**' ':(exclude).github/workflows/**'
python3 -B "$T/test_historical_helper_identity.py"
python3 -B "$T/test_helper_audit_staging.py"
python3 -B "$D/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/test_audit_only_source.py"
python3 -B "$T/stage_helper_successor.py" \
  --workspace "$W" --preflight "$P" --raw "$O" --stage "$A"
~~~

Require host source-only tests **17/17**, **11/11**, **23/23** separately, true unmodified source Git blobs, all original source/raw/SDK/scratch preadmission hashes, c42a checkpoint **197** files, and `AUDIT_ONLY_STAGE.json.status=StagedNotExecuted`, with `initialSnapshot.consumedC42A.publishedFilesVerified=197`, raw4269, sdk2405, scratch1925 and preserved original Local FAIL. The stager produces only A, retains original failed b7e3 `audit.py` as a separate staged input, installs the two-line-corrected auditor into A, and **does not run it**. Any error STOP without alternative suffix.

Only after complete success of all prior gates, execute this **ONE** isolated audit invocation, retaining actual PID/exit and complete stdout/stderr. The invocation marker is written in A before execution:

~~~bash
python3 -B "$T/run_helper_audit_once.py" --stage "$A" --timeout-seconds 1800
~~~

**On zero OR nonzero exit once staged**, independently perform this non-auditor original-evidence preservation check ONCE (do not let a previous `set -e` skip it silently after a known failure):

~~~bash
python3 -B "$T/stage_helper_successor.py" \
  --verify-after --workspace "$W" --preflight "$P" --raw "$O" --stage "$A"
~~~

This must independently verify the original 4,269 raw, 2,405 installed official SDK, 1,925 SDK scratch, 104 preflight, 197 published c42a checkpoint files and the three c42a original external stage evidence identities. If stage never created A, after-check is NotRun; report factual preadmission/blocked state and independently preserve existing source/SDK/history, not fictional after evidence.

## 5. Factual result, permitted publication and STOP

A *new* scoped `PassedHistoricalAuditOnly_UnchangedLocalFail` is allowed **ONLY** if the actual bounded new runner exited0, generated new `EVIDENCE_AUDIT.json` with `PassedHistoricalEvidenceAuditOnly` and `auditMode='ReadOnlyIsolatedB7E3History'`, retained the original `originalB7E3LocalResult='FAIL'` and `liveRemoteHeadCheck='NotRun_TimeVariant'`, produced original required `ADMITTED_EXECUTION_VERIFICATION.json`, `GIT_HISTORICAL_AUTHORITY_AFTER.json` and all inherited source/negative/SDK/Git joins, and new independent before/after original evidence preservation Passed. It is **never** a reclassification of historical b7e3/c42a FAIL, never genuine Unity/Player runtime acceptance, and never an R03/Human Review PASS.

On any error/timeout/unknown-lifetime/new source assertion fail, retain exactly the real stderr/partial files/PIDs/exit, mark new audit-only FAIL/Blocked and return to Primary without retry, alternate root, source edit or further project stage.

Local Git publication is limited to append-only/factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md` and ONE new `Docs/AssemblyShadow/History/M07R/R03/local-audit-only-p1-20261024-f51d/` checkpoint. Preserve **every old Local report/findings/raw/checkpoint** byte-identically. Include exact current four 40-char source HEADs, historic b7e3/c42a pins, all source/CI checks, stage/audit/after receipts and logs, source/SDK/raw/scratch/full history custody, expected negatives, and original FAIL statuses. Commit, push, independently verify remote HEAD and **STOP regardless of result**.

**Never** rerun original 25-component core, original 85 tests, original native100/managed SDK compiler operations, Unity Editor/TestRunner/Player, old c42a/b7e3 auditors, modify SDK, branch/commit history or original consumer source, change assertions, retry a failed audit, create new roots silently, begin H2/X02/M08A/protected SNAP-01 or Human Review Gate.

**Acceptance remains closed:** P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, P3 Incomplete. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
