# Local Validation Tasks — V04 Controlled Workflow Repair

Candidate build-input source anchor:

`4d6bc15d97b0b7b9bdadff81419abeab76262d50`

Latest Local return:

`8788d123ca7769396cf14c707f8df13ac764223b`

H1 remains `InProgress`. Do not begin R02.

## Goal

Validate both returned V04 boundary repairs and, if they pass, continue the remaining performance chain in one Local batch without stopping between independent checks.

## V00 — fresh authority

1. Pull the final pushed `codex/assembly-shadow-r01b-h1` checkout and require clean tracked state.
2. Record checkout HEAD separately from source anchor `4d6bc15d97b0b7b9bdadff81419abeab76262d50`.
3. Run candidate handoff/source preflight; require `SourceTargetVerifiedNotBuildAccepted` at the exact source anchor.
4. Authenticate reproduction tooling and protected profile-1 pins.
5. Verify candidate and protected installed runtimes before any controlled build.

Hard-stop on authority, pin, runtime, or protected-reference mismatch.

## V01 — Primary regressions and Unity sanity

Run the complete current Python inventory, bounded Primary suite, live handoff preflight, R01 suites, lazy suite, and:

~~~text
pwsh -NoProfile -File Tools/AssemblyShadow/tests/test_m07_generated_input_recovery_labels.ps1
pwsh -NoProfile -File Tools/AssemblyShadow/tests/test_m07_player_input_recovery.ps1
~~~

Require both PowerShell tests to pass with `unityInvoked=false`.

Run broad Unity EditMode once. In particular, `M07BuildTests` must compile and pass the new workflow source assertions.

## V01A — source-scope audit

Audit from the prior candidate source anchor:

`316894a83873c46ffd3eefa57222311ae03da214`

to:

`4d6bc15d97b0b7b9bdadff81419abeab76262d50`

Expected functional changes:

- `Tools/AssemblyShadow/Invoke-M07Build.Core.ps1`;
- `Assets/AssemblyShadowDemo/Editor/H1BuildInputProvenance.cs`.

Expected support changes:

- `Tools/AssemblyShadow/tests/test_m07_player_input_recovery.ps1`;
- `Tools/AssemblyShadow/tests/test_h1_m07_workflow_authority.py`;
- `Assets/AssemblyShadowDemo/Tests/Editor/M07BuildTests.cs`;
- `.github/workflows/h1-bee-primary.yml`.

Metadata/history/handoff commits after the source anchor are not executable build-input changes.

If any unexpected runtime/native/performance-protocol input changed, stop audited reuse and widen validation.

## V02/V03 — provenance

Freshly verify candidate/protected source pins, installed runtime, M07 coordinator authority, and controlled-build provenance tooling.

The current nested native provenance evidence must show:

`verificationEnvironmentScope=NativeOnlyWithoutOuterM07WorkflowAuthority`

The top-level verifier must still reject direct caller `--skip-demo-source` while M07 workflow authority is active.

## V04.A — protected profile-1 controlled workflow

Run:

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <reference-demo> \
  -BaselineId M07-Baseline-H1-Perf-Reference-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX \
  -ControlledPerformanceBuilds
~~~

Require Native ON and Native OFF to complete.

For **each** `native-on-controlled` and `native-off-controlled`, retain and verify:

- `<label>-link-xml.original`;
- `<label>-link-xml.generated`;
- `<label>-link-xml-restored.json`;
- `<label>-project-settings.original`;
- `<label>-project-settings.generated`;
- `<label>-project-settings-restored.json`.

Both receipts must report `ExactBytesRestored` and `originalSha256 == restoredSha256`.

After Native ON, the immediate next pinned-input guard must pass; this directly closes returned blocker 1.

Require complete workflow receipt, controlled ON/OFF Player receipts/evidence, fixture manifest, Editor replay, and outer restoration. Reverify protected installed runtime afterward.

## V04.B — candidate profile-2 controlled workflow

Run the same command against the candidate project with a fresh Current baseline ID.

Require the same two-input restoration evidence for both labels.

Additionally require Native ON provenance capture to succeed. Its evidence must contain the native-only child scope marker and no `M07 workflow authority cannot be invoked with --skip-demo-source` failure. The post-Player outer pinned-input guard must still run and pass. This directly closes returned blocker 2.

Reverify candidate installed runtime afterward.

## V04.C onward — continue only after both graphs pass

If V04.A and V04.B both produce complete self-consistent graphs:

1. run current-anchor old-Player rejection;
2. freeze the strict A/B build map and require `ComparabilityPassed`;
3. bind preregistration without changing protocol/schedule semantics;
4. run every preregistered pilot pair;
5. if pilots pass, run every formal pair;
6. run final paired analysis;
7. retain every failed/retried attempt;
8. authenticate a new checkpoint before cleanup;
9. proceed to V05 and a genuinely independent M08 only if mandatory V04 is complete.

Do not edit build receipts, map bindings, protocol, schedule, thresholds, or samples after observing timings.

## Evidence to retain on any failure

Capture:

- exact stage/label;
- command and complete coordinator/Unity logs;
- original/generated/restored hashes for both mutable Player inputs;
- both restoration receipts if helper-body entry occurred;
- controlled-build evidence;
- native provenance capture and verifier stdout/stderr;
- source/runtime verification before and after;
- exact tracked-state diff;
- workflow outer-restoration receipt.

Preserve failed bytes before manual recovery when the workflow itself did not restore them.

## Reuse boundary

Historical `925e84d7...` runtime evidence may be cataloged only as `ReusedAuditedFrom925e` if the source-scope audit proves its domain unaffected. Never relabel it as fresh current-anchor PASS.

## Exit

If either repaired boundary fails, update `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` and return to Primary.

If the complete chain passes, record all evidence and commission independent M08. Only a genuine M08 PASS may make H1 ready for explicit Human Review Gate approval.

Do not begin R02.
