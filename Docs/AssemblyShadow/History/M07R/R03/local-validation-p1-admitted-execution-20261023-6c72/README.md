# Local P1 admitted execution — 20261023-6c72 prerequisite Blocked

## Current run — P1 admitted execution 20261023-6c72 — PrerequisiteBlocked / batch NotRun

[Checkpoint](README.md), [Local result](LOCAL_RESULT.json), [Primary return finding](FINDING.json), [independent after-preservation](PRESERVATION_AFTER.json).

| Actual repository | Branch | Exact attempted source |
| --- | --- | --- |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | codex/assembly-shadow-r01b-h1 | 7a098e45b41b98ee024ed0205b353aa2f132aae9 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | codex/assembly-shadow-r01b-h1 | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

**BLOCKED / PrerequisiteBlocked; core batch NotRun (0/25).** Source/remote/fresh-root/SDK/retained-evidence admission completed. The required published preparer regression suite ran ONCE: **13 tests, 12 Passed, 1 ERROR, 0 assertion failures and 0 skips**. It exited1 before the preparer command. The handoff says any prerequisite failure stops the cycle. No source/test/TMPDIR/SDK/compiler change or retry was made.

**IR-LOCAL-P1-PREPARER-TEMP-01 — reproduced published test-fixture prerequisite error.** Exact command: python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py. PID 97249; exit 1; UTC 2026-10-23T08:48:29.064549+00:00 → 2026-10-23T08:48:29.154075+00:00; America/Los_Angeles 2026-10-23T01:48:29.064549-07:00 → 2026-10-23T01:48:29.154075-07:00. Full stdout SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256 22149df6b36440e8063b5bf38eeeff4c11b53dc296740e01baf037bd4ec5a663. Original command/streams are in evidence/Dispatch-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json and evidence/6c72-preparer-tests.stdout.bin / .stderr.bin. Source test blob 58e6e0b9ff870d1ada20021ab36a82882d60b837, SHA256 94ee6e8d1ec1957598445fe3ce625a4c2af896b4b7e4020ecbbd48f480d52946; preparer blob cf2fdf39fe17df076d50dcc33ed72c757eaa3b26, SHA256 ddaa342817906dec659c4be062ea052cd8e12ed1ad2b538bcb283ae12a750db8.

Failed leaf: LocalCollectorRepairTests.test_pristine_root_fail_closed at test_prepare_p1_admitted_local.py:106. It creates a TemporaryDirectory, uses parent = Path(d), then calls pristine_root(parent / 'absent') expecting acceptance. The actual unchanged inherited TMPDIR is /var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T/. macOS /var resolves to /private/var; its canonical parent is /private/var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T. The fixture supplies /var/folders/.../tmpqsr57skb/absent instead of the canonical /private/var/folders/.../tmpqsr57skb/absent. The real pristine_root guard at prepare_p1_admitted_local.py:148 correctly rejects a path different from path.resolve(). Actual error:

    ValueError: Root is non-absolute, already used, or not canonical: /var/folders/8w/lgmfhbk15gddrdq0stxvy_pm0000gn/T/tmpqsr57skb/absent

The first expected-good check raises; later existing/symlink/relative controls within this leaf are not reached. Twelve other test leaves Passed. No claim of 13/13 success or failed native/SDK compiler is made. The suite used the published source and ordinary inherited environment; no alias, timeout or fault was injected by Local.

**Root cause / boundary:** the published test-owned temporary parent lacks canonicalization; this is a fixture/host-path assumption. The production root guard is doing its intended fail-closed check. Native runtime sources, Gate, original getters, compiler procedure and SDK are not implicated by this error. Correctness of the shipped preparer itself and its generated collector is still **NotRun**, not disproved or accepted by the failed test.

**Primary direction:** canonicalize only the test-owned TemporaryDirectory parent before constructing the expected-good absent child, and add an inherited aliased-parent cohort. Keep all existing rejection controls, immutable helper/frozen source blobs and production pristine_root semantics. Do not weaken path guards, override TMPDIR or relabel this attempt. Verify the existing and alias tests on native macOS and canonical-root hosts. Publish corrected evidence plus a new exact handoff/unused roots before another cycle.

| Obligation | Actual state |
| --- | --- |
| Source/remote identities, source-anchor Docs-only delta, package/historical pins | Passed admission and independent after checks |
| Four absent canonical/disjoint candidate roots | Passed admission; remained absent through stop |
| Published preparer unit tests | Failed prerequisite: 12 Passed, 1 ERROR of 13 |
| Actual preparer / PREPARATION.json | NotRun / unavailable because no preparation |
| Generated run-once.py / audit.py / EXPECTED.json | NotRun / not created in candidate preflight |
| Original85 failure-contract tests | NotRun |
| Eight outer inventory flags and new nine strict+nine sanitized groups | NotRun |
| Five managed positives plus exact negative | NotRun |
| 100 official native SDK syntax commands | NotRun |
| 20 core Git postflight commands | NotRun |
| Raw RESULT/MANIFEST, core PID and lifetime consistency | NotRun / not constructed |
| Copied independent success auditor | NotRun |
| Primary --verify-after / BLOCKED_HISTORY_AFTER.json | NotRun / no PREPARATION receipt |
| Independent read-only after-preservation | Passed; distinct receipt, not substituted Primary verify-after |
| Unity Editor/Test Runner/Player, link, real runtime | NotRun |

| Component | Actual state |
| --- | --- |
| command-failures | NotRun |
| legacy-host | NotRun |
| metadata-gate | NotRun |
| bounded-class | NotRun |
| bounded-physical | NotRun |
| bounded-first-use | NotRun |
| owned-general | NotRun |
| live-general | NotRun |
| owned-execution | NotRun |
| empty-live | NotRun |
| opaque-inventory | NotRun |
| physical-membership | NotRun |
| owned-physical-names | NotRun |
| owned-physical-json | NotRun |
| live-owned-physical-json | NotRun |
| observed-type-shape | NotRun |
| live-type-shape-census | NotRun |
| observed-type-shape-json | NotRun |
| vm-shape-json | NotRun |
| admitted-execution | NotRun |
| bounded-status | NotRun |
| bounded-inventory | NotRun |
| frozen-v2 | NotRun |
| managed-sdk | NotRun |
| native-sdk | NotRun |

All four original candidate root names were absent when the prerequisite stopped. P=/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261023-6c72, raw=/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261023-6c72, scratch=/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261023-6c72 remain absent; only the authorized additive checkpoint was subsequently created to publish factual evidence. These identifiers are consumed; no suffix swap, preparer/core retry, audit invocation, alternate source or fabricated core receipt occurred. The one required Python test command is a prerequisite suite, not one of the original85 core tests. The dispatch assertion only records that nonzero exit and does not launch the next command.

**Preservation after failure:** independent read-only collector UTC 2026-10-23T08:51:59.282098+00:00 → 2026-10-23T08:52:22.573002+00:00 (America/Los_Angeles 2026-10-23T01:51:59.282098-07:00 → 2026-10-23T01:52:22.573002-07:00). All 2405 installed Unity2022.3.62f2 SDK inputs / 316062203 bytes and installed inventory match their admitted original hashes. All 22 consumed P1 raw/scratch/audit sets, 88 historical negative symlinks and original24 checkpoint sets are verified. Separately, the **42** e1e5 blocked checkpoint files and **48** external blocked-preflight files remain unchanged, and its old raw/scratch remain absent. Both original host-only raw manifests remain byte-bound to authenticated checkpoints and all 2549/3164 entries verify. Four independent clean current-source heads and live remotes match the exact tuple. These read-only Git checks are not the unexecuted core20 postflight.

Preserve e1e5 PrerequisiteBlocked / 0of25, 7896 PASS, 7c2c PASS, 82dd FAIL / FailedOrIncomplete and original sourcePreserved=false/fourRepositoriesAfter=[]/timeout. IR-LOCAL-P1-ADMITTED-PREFLIGHT-01 remains frozen, with no new attempt at its failed root. IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01 retains original SourceConfirmed_NotFaultInjected and its earlier corrected successor disposition. No old compiler/test result is reported as fresh.

**Evidence custody:** LOCAL_RESULT.json is an independent Local prerequisite outcome, not the core RESULT. PRESERVATION_AFTER.json explicitly describes independent after-preservation; it is not BLOCKED_HISTORY_AFTER.json from the unrun preparer. Source copies, executed command PID/times/exit, original full streams, admission bundle, after records and COPY_BINDINGS.json are authenticated by this checkpoint MANIFEST.sha256. No runtime batch seal, SDK output, PREPARATION.json or core manifest is fabricated. Python/macOS version command receipts and inherited temp identities are in the independent after-preservation record.

**Exit:** Local Validation → Primary Implementation, BLOCKED. Still required after a new handoff: preparer tests/preparation, original85, all25 components/eight inventories/nine+9, managed5+negative/100 native syntax/20 actual Git, independent auditor and required after checks. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. No canonical TypeKey, pointer lifetime/origin, coherent VM epoch, full execution V1, actual GC/RSS/Shutdown or linked Player proof. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; fullLegacyRegressionAcceptance=false. PureInterpreter disabled. No Human Review Gate, SNAP-01, H2, X02, M08A or further milestone.

Admission read-log/helper copies are losslessly encoded in evidence/admission-6c72.log.utf8.json and admission-6c72.py.utf8.json to preserve original whitespace while satisfying Git checks. COPY_BINDINGS.json records decoded hashes/byte counts; original external bytes are unchanged. Core/test outcome remains Blocked/NotRun.
