# Primary Implementation → Local Validation — ONE new P1 source/official-SDK preflight authorized

**Scope: R03 P1 METADATA-LIFETIME SOURCE PREFLIGHT ONLY.** The previous one-shot host cycle is consumed. This is a **new, narrowly authorized** one-shot Local Validation cycle for the published native gate, bounded source readers, retained host/V2 tests and official installed SDK **syntax compilation**. It is **NOT** permission for Unity Editor, Test Runner, any actual Player/build launch, SNAP-01/N retry, V2 semantic acceptance, a new seven-root runtime batch, new stages, or Human Review Gate.

Current owner after this publication: **Local Validation for this fixed one-shot preflight only**. After recording factual evidence, return to Primary for nontrivial source/architecture corrections. Local must not modify native production, C# implementation, integration policy, engine adapter or original test predicates.

## 1. Mandatory read order and exact four GitHub repositories

1. `Docs/AssemblyShadow/README.md` and `Plan/CURRENT_STATUS.md`.
2. This current `Handoff/WEB_TO_LOCAL.md`.
3. Factual `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`; read only until publishing the new factual return.
4. [Primary source/lifetime review](../History/M07R/R03/IR_Remediation/P1_METADATA_LIFETIME_2026-10-16/PRIMARY_RECONCILIATION.md), and historical Local host PASS [checkpoint](../History/M07R/R03/local-validation-host-only-20261015-74dbdbea-a1/README.md). Preserve all original FAIL/Blocked verdicts.
5. Existing [Primary P1/P2/E0/E1/P3 plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md) and [E0 blocked evidence](../History/M07R/R03/IR_Remediation/SNAP01_EXECUTION_FORMATTER_2026-10-15/ENGINE_OWNER_CAPABILITY_ASSESSMENT.md).

All repositories: `codex/assembly-shadow-r01b-h1` from canonical `night-outlook/<repo>` GitHub remotes.

| Repository | Exact Local checkout path | This preflight source pin |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Latest pushed remote branch HEAD from the final Primary handoff message** (the DEMO source anchor preceding Docs is `1a861c3c777e25d422248f1621f610b30669f2cc`) |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `0a0b70156e75d450d75d0bcfd9132843b8abbbb0` |

**Do not use historical `source-pins.json` as the current candidate native SHA.** That file deliberately remains bound to the last actually executed earlier Local source and is not rewritten. Candidate SDK syntax uses an explicit `--candidate-native-sha` opt-in. The DEMO source anchor listed here is NOT the latest Docs handoff commit: use the final verified remote HEAD from the Primary handoff prompt. The single command refuses mismatch in ANY one of the four repos, dirty trees or unexpected Git remotes. Safely fetch/fast-forward only clean ancestor histories before running. Never reset, clean, force-update or overwrite unrelated worktrees.

## 2. Exact authorization and unused output roots

Official installed Editor SDK path (read-only): `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity` (macOS Apple Silicon). The Editor executable is used only as the anchor for installed SDK files. The preflight must not launch Unity.

New candidate output roots, subject to Local **existence/canonical/root separation** verification before starting:
- Batch evidence: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-METADATA-SOURCE-20261016-0a0b`
- Official SDK isolated scratch copy: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-METADATA-20261016-0a0b`

Both names must be absent, disjoint, on approved external storage and outside all source/Editor/previous evidence roots; never reuse if they already exist. No source checkout or installed SDK tree may be modified. Do not create or consume new Player/custody roots. Do not invoke any historical SNAP-01 or N runtime command.

## 3. One source-bound command (exact current demo SHA supplied in the Primary handoff)

Set the exact `DEMO_SHA` to the latest pushed 40-character SHA shown in the final Primary handoff (it cannot be self-referentially written into its own Git-tracked document). Fixed native SHA below. Run **only once**, after checkout/remotes/environment/output verification:

```bash
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
DEMO_SHA=REPLACE_WITH_LATEST_PUSHED_PRIMARY_DEMO_HEAD
NATIVE_SHA=0a0b70156e75d450d75d0bcfd9132843b8abbbb0
B=/Users/ah/GitHub/hybridclr/r03-local-validation
python3 -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE_SHA" \
  --output "$B/R03-P1-METADATA-SOURCE-20261016-0a0b" \
  --sdk-scratch "$B/Scratch-R03-P1-METADATA-20261016-0a0b"
```

This newly authored wrapper performs **TEN separately receipted tests in ONE overall cycle**:
1. Retained current/frozen native general/execution legacy byte parity, V2 codec/file transaction/legacy sink and original 25-case profile matrix through `run_primary_host_preflight.py`. No previously consumed external run is reused.
2. New metadata gate lifecycle concurrency, shutdown-order source audit, closed/open/restart rejection under strict and ASan/UBSan.
3. Complete owned ordinary-class source, original/current/frozen V1 8192-row parity; closed owner denial.
4. Complete bounded physical assembly source, original/current/frozen V1 4096-row parity; closed owner denial.
5–7. Bounded first-use, transaction status and transaction inventory source host suites.
8. Frozen V2 execution source/codec host suite.
9. Official installed Unity managed compiler/API targets + unchanged expected-negative old source.
10. Official installed Unity native syntax **14 translation units x 5 profiles = 70** using an isolated SDK copy (legacy 60 plus actual `Assembly.cpp` and `AssemblyShadowVisibility.cpp`), with candidate native SHA opt-in.

Each case records its raw stdout/stderr/hash, exact command/exit and nested result. All result statuses remain scoped to **host or SDK syntax**. The aggregate `RESULT.json` is `PassedSourceHostAndSDKOnly` only if all ten inner components pass and exact source/repository preservation holds. On any failure, preserve the output and stop after the one batch; **no rerun, in-place repair or fresh Player attempt**.

## 4. Expected receipts, failures and preflight exit

Required external evidence:
- `<BATCH>/RESULT.json`, `MANIFEST.json`, `commands/*.json`, raw `stdout.bin` and `stderr.bin`, ten nested results/manifests and complete compiler/process command receipts.
- Actual **70 syntax configurations** and five managed targets/one expected-negative; exact SDK version paths, source binary hashes, CXX/Apple Clang toolchain version, original source hashes before/after, feature-on/off and DEBUG profiles.
- Native gate, class/physical source-bound CI links and matching source commits. Preserve all notices and warnings (including Baselib warnings), sanitized failures, missing-data statuses, and exact first error. Do not reinterpret host mocks as Player evidence.
- Factual Local `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` (for any nontrivial blockers) and one additive bounded checkpoint under `Docs/AssemblyShadow/History/M07R/R03/`; commit/push only factual reports/evidence using canonical Git. Do not commit SDK/vendor binaries or copy enormous external evidence into Git. Bind retained external original file inventory/hashes.

**Allowed Local changes:** factual evidence and handoff report publication, and narrowly scoped environment-only diagnostics. **Forbidden:** editing primary design, production C++/C#, native gating, test harness, V2 codec/transport/predicates, source-pins.json, historical evidence, interpreter controls, engine scheduler, or tuning performance/limits. Report any SDK syntax failure and precise file/line to Primary. No nontrivial code fix by Local.

If the installed SDK, clean repository state, storage root or permission is unavailable, mark `Blocked`, record exact missing input and stop. If compilation fails, `Failed`; not "Passed after mock". Each case retains `Passed`, `Failed`, `NotRun`, `Unavailable` or `Blocked` precisely. Do not promote earlier history.

## 5. Open gates, immutable acceptance and stopping rule

**P1 still INCOMPLETE**: admitted bounded class/assembly readers are inactive; the original live general/execution getters still allocate and dereference pointers across independent lifetimes. The gate does not prove global source epoch, lock-wait bound, actual peak VM RSS/GC or recursive class iterator safety. Official 70-unit **syntax** can expose integration defects; a Pass would not prove linked native Player or runtime teardown.

**P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; P3 official SDK source preflight now delegated only for this candidate**, not full acceptance. The Unity2022.3.62f2 StandaloneOSX native engine-owner scheduling/queue-drain/finalizer/restart interface has not been proven; a modeled coordinator is not an adapter. Historical SNAP-01 remains FAIL (14/18 cells, three ON writer failures after field14 bound262144; engine 51213 uncapped reports/500ms exit71). Original strict S custody remains Blocked; R03 full independent review FAIL/re-review NotRun. No cap/coalescing, sleep, fake successful emission, weakened original semantic verifier or finalizer suppression.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter disabled.

**Stop after this one host/SDK-only Local cycle; return factual evidence and blockers to Primary.** No R03 Player execution, seven runtime roots, H2/X02/M08A, unrelated refactoring or Human Review Gate is authorized by this document.
