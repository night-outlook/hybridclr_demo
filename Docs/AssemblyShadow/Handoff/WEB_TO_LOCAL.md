# Primary Implementation → Local Validation — ONE inactive execution metadata-admission SDK cycle

**Authorizes exactly ONE fresh R03 P1 25-component SOURCE/HOST + official installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation batch.** The new native method is **INACTIVE** and only wraps the UNCHANGED original V1 execution diagnostic getter in an initial-runtime MetadataLifetime Reader. This is NOT pointer allocator/lifetime proof, complete generic-aware TypeKey, a VM coherent epoch, original getter activation, V1/V2 transaction qualification, Unity Player or R03 acceptance. **Never start** Unity Editor/Test Runner/Player, link product native binaries, enable/distribute the new wrapper or original getters, attempt actual Shutdown/GC/RSS/latency/profiling, protected SNAP-01, H2/X02/M08A, Human Review Gate or another milestone.

## 1. Read first and source/old-evidence admission

1. Read `Docs/AssemblyShadow/README.md` then `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`.
2. Read **Local-owned** `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` FIRST, then `Handoff/RETURN_TO_WEB.md`; authenticate newest consumed [`20261021-7896` checkpoint](../History/M07R/R03/local-validation-p1-git-lifetime-20261021-7896/README.md), [independent audit](../History/M07R/R03/local-validation-p1-git-lifetime-20261021-7896/preflight/EVIDENCE_AUDIT.json), source/SDK/raw/scratch/audit data, and all preceding consumed P1 runs/negative symlinks, especially `20261021-82dd` raw aggregate FAIL and `7c2c` PASS.
3. Read [Design](../History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/DESIGN.md), [one-cycle Plan](../History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/PLAN.md), [Primary audit](../History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/PRIMARY_SOURCE_AUDIT.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/EVIDENCE.json) and relevant earlier metadata gate/physical membership/VM shape census requirements. Read this entire handoff and original stage exit criteria.
4. **BEFORE any new root is created**, independently authenticate all four canonical clean Git repos, submodules/worktrees/packages, installed SDK and Apple toolchain/vendor hashes, old raw/SDK/historical checkpoint/symlink custody, available disk, and **all four exact new roots ABSENT, canonical, disjoint from each other, each repo/SDK and all consumed evidence**. Any failure ⇒ Blocked/STOP, no root reuse, no changed suffix/alternative execution or silent evidence substitution.

**Latest factual Local `20261021-7896`**: `PASS / PassedSourceHostAndSDKOnly` on demo `a5c0a4272efc4eee000220f40b7ca769be277917`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`. One 24/24 source/host/installed SDK syntax batch, 85 original tests, seven source groups, five actual managed positives plus exact original compiler-negative, **100/100** native official Apple arm64 C++17 `-fsyntax-only` commands, **20/20** original final Git commands and four clean source-head comparisons, independent audit Passed. No retries, Unity Editor/Player or product link. The `7896` raw/scratch/audit/checkpoint roots are **CONSUMED** and not reusable.

**Historical `7c2c` PASS / `82dd` FAIL preserved.** The `82dd` raw aggregate remained FailedOrIncomplete after 120-second `hybridclr ls-remote` timeout even though 24 child results Passed. Do not relabel any old run or rebaseline old original source fingerprints. The prior Git manifest-lifetime finding retains original `SourceConfirmed_NotFaultInjected` and successor `CorrectedAndRegressionValidatedWithinHostScope_NoRealTimeoutInjected`.

## 2. Exact GitHub repos, branch, source pins and package

Four independent nested Git repos under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` (parent is **not** a repo). Branch for **every** repo `codex/assembly-shadow-r01b-h1`, canonical HTTPS as listed; equivalent SSH only if independently proven same identity. Verify origin, current local HEAD, exact branch, clean `git status --porcelain`, live `git ls-remote` remote HEAD, worktrees/submodules, package and source/SDK before starting. **No reset-hard/clean/force push/unrelated merges**; only safe clean fast-forward. Any branch head advanced after final handoff requires fresh Primary source review/pin.

| Canonical repo / HTTPS identity | Existing Local checkout | Required final pushed source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` / `https://github.com/night-outlook/hybridclr_demo.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **FINAL Docs-only handoff-containing remote SHA** supplied as full 40 hex in Primary's short accompanying prompt; verify equals local HEAD, current remote HEAD and `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. Tested demo code source anchor `117cc6b1c2be8050cd2f433ef17db8b3c5138f93`; all later commits must be Docs-only. |
| `night-outlook/hybridclr` / `https://github.com/night-outlook/hybridclr.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` / `https://github.com/night-outlook/hybridclr_unity.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` / `https://github.com/night-outlook/il2cpp_plus.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` |

Historical `Tools/AssemblyShadow/R03/source-pins.json` (older original native `74dbdbea80d83923863303bd2b2c0a87f36541b1`) stays **byte-identical**, no accidental replacement by current candidate. Native is supplied separately via `--expected-native` and propagated to `--candidate-native-sha`. Unity package `file:../../hybridclr_unity` must resolve to pinned sibling.

## 3. Exact new native/demo implementation and evidence boundaries

**Native `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`:** new `libil2cpp/vm/AssemblyShadowAdmittedExecutionDiagnosticsSource.inl`, one `AssemblyShadow.h` static method declaration and a single include **after** the unchanged original `GetExecutionDiagnosticsJson` in `AssemblyShadow.cpp`. Method `TryGetExecutionDiagnosticsWithMetadataAdmission(std::string&)` clears prior JSON; creates original initial-source-epoch `assembly_shadow_metadata_lifetime::Gate::Reader(g_MetadataLifetimeGate)`; on unavailable/closed gate returns `AssemblyShadowError::InvalidState` **without** invoking the old getter; when admitted calls original getter exactly once with Reader held for whole synchronous invocation/exception unwinding. No changes to normal getters, V1 fields, V2 publication, caller policy, metadata lock order, managed API, Unity Player or ability to call the original getter unguarded through its preexisting path. **No physical class pointer-origin/validity, complete TypeKey, VM-wide epoch, real Shutdown/GC/RSS/latency or runtime proof.** This one method is inactive.

- `admitted_execution_diagnostics_fixture.cpp` compiles **actual .inl and actual Gate implementation** against explicitly mocked old getter, not its actual full source body. Nine ordered groups **per strict+sanitized**: closed admission no delegation/stale output, open epoch1, Reader visible throughout, caller-owned output, original error propagation, exceptional exit releases Reader, concurrent Shutdown waits for Reader, closed gate refusal, re-opened epoch2 fails default source epoch. Source runner `run_admitted_execution_diagnostics.py` verifies exact method CPP/API source, original getter immutable fingerprint, strict source call order, no new VM reads in wrapper, exact nine groups/profile, real five host compiler commands and before/after source/stream SHA/size/children lifetime.
- Original `run_owned_physical_names.py`, `run_physical_membership.py` and `run_opaque_execution_inventory.py` only strip the **byte-exact** new header/CPP declarations/includes before checking frozen original getter source SHA; historical R02 fingerprint expected failure not rebaselined. Focused [native final CI 39735806552](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735806552) **PASS 3/3** Mac Clang/Linux Clang/GCC strict and ASan/UBSan. First [CI 39735204197](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735204197) and [CI 39735624217](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735624217) **FAIL** on source-verifier newline and multiline signature matcher, not product compiler. These historical initial results remain failures. Old source-gate [39735624233](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735624233), [39735624262](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735624262), [39735624261](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735624261) PASS 3/3 each.

**Demo exact code source anchor `117cc6b1c2be8050cd2f433ef17db8b3c5138f93`:** a **25th independently receipted** `admitted-execution` host child with typed `R03P1InactiveExecutionMetadataAdmissionActualSourceHost` / integer schema1 / `PassedWithinInactiveMetadataAdmittedExecutionHostScope`, previous original getter/API immutable fingerprint, exact real Gate/source signature and nine ordered source-host groups per BOTH strict/sanitized. Add **eighth** independently verified `admittedExecutionMetadataCaseInventoryVerified=true` while preserving seven previous inventory flags, previous 24 components, original **85=5+14+44+10+12** Python test discovery IDs, existing five managed-positive + exact compiler-negative, and original **100** official native syntax calls. Controlled malformed/unknown lifetime/NotRun/source/gate/unsupported runtime claims still fail closed. Existing `PlayerProject/AssemblyShadowOwnedPhysicalNamesSyntax.cpp` merely acquires a type-safe function pointer of the native new method, **no new TU**. Normal gameplay/Editor/Player does not call it.

Demo first [integrated 39736625885](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736625885) / [focused 39736625864](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736625864) CI **FAILED** due to one new total count in a **known failed synthetic child** test, not actual SDK. Corrected [integrated 85 CI 39736751961](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736751961) and [focused 39736752238](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736752238) **PASS 2/2** Mac/Linux. Earlier unchanged managed mock [39736625771](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736625771) PASS 2/2. Host/mocked CI **NOT** new official installed SDK validation. Native latest candidate full official SDK syntax **NotRun** until Local.

## 4. Four fresh, absent roots (pre-admit before creation)

Local must independently verify **all** four roots below ABSENT (not symlinks), canonical, pairwise disjoint, outside four repos/submodules/worktrees, vendor SDK and **every** consumed P1 raw/scratch/audit/checkpoint. Never reuse `7896`, `7c2c`, `82dd` or any earlier used root; if admission is incomplete ⇒ Blocked/STOP, not permission to rename or retry.

- Fresh raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261022-e1e5`
- Fresh SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261022-e1e5`
- Fresh independent Local audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261022-e1e5`
- New additive demo checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261022-e1e5/`

Official original installed Unity2022.3.62f2 binary READ-ONLY location, **NEVER LAUNCH**:
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
Preserve inherited approved TMPDIR/CXX, per-process lifetime/SDK inputs and vendor source hashes. No compiler/SDK/Git/SSH timeout/auth configuration changes.

## 5. ONE exact core batch command — ONLY after independent admission

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=117cc6b1c2be8050cd2f433ef17db8b3c5138f93
NATIVE=e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-ADMITTED-EXECUTION-20261022-e1e5" \
  --sdk-scratch "$B/Scratch-R03-P1-ADMITTED-EXECUTION-20261022-e1e5"
```

Only **ONE core attempt**. Four roots consumed on PASS/FAIL/Blocked/timeout/interrupt. No retry/resume/re-execution with a new suffix or modified Git/SDK/compiler/source, no new stage. Unknown subprocess/descendant lifetime fails stop and marks remaining scheduled cells NotRun **without creating roots**; records partial direct streams/null exits and skips unsafe postflight. Known completed nonzero remains Failed and follows the established independent scheduling rule; no false quiescence claims.

## 6. Required independent actual validation / PASS boundary

- Existing **24** original child identities/results remain and add **25th `admitted-execution`** with nine exact ordered strict +nine ASan/UBSan source-host groups, verified byte/source/Gate contract and original getter frozen source proof. All **EIGHT** outer case-inventory flags true: original seven plus `admittedExecutionMetadataCaseInventoryVerified`. Original 85 unique Python tests from original 5+14+44+10+12 modules, zero errors/failures/skips/expected/unexpected successes.
- All retained original legacy, metadata, bounded class/physical/first-use, owned/live general/execution/opaque/membership/physical names/physical JSON/shape/shape JSON/frozen/current V1 parity and negative tests. Original preceding case inventories **28/21/12/15/16/16/16** strict/sanitized; new admitted nine/profile do not replace any previous case.
- `managed-sdk`: actual original five positive official Unity managed compiler products from 428 source inputs plus **separate** `OriginalUnsignedCounts` exact expected compiler negative exit1, **two CS0266 and no DLL**; canonical nested result path/sha/returned-output binding, not root decoy.
- `native-sdk`: actual **100/100** official Unity2022.3.62f2 Apple arm64 C++17 `-fsyntax-only` commands = 20 unchanged TUs × five profiles. Must compile complete genuine original `AssemblyShadow.cpp` now including inactive admitted wrapper and existing probe signature; original no native product linking.
- **20** real Git source-authority postflight direct commands with 120-second limit and full START/RESULT/sha/stream bindings (five per four repos), all known exit0/no timeout, four complete cleaned expected remote heads, original vendor/source/SDK/history preserved. On successful whole batch require `RESULT.commandLifetimeUnverified=false` and `MANIFEST.commandLifetimeUnverified=false`, `MANIFEST.inventoryScope=CompletedBatchFiles`, `sourcePreserved=true`, `postflightError=null`, `stoppedAfter=null`, zero unknown lifetime. Independent Local audit must join the exact raw process argv/PID/times/direct streams, C++ source/vendor inputs, original consumed negative controls, and final manifest SHA/size.

**Only PASS / PassedSourceHostAndSDKOnly** for the described **source/host/official installed SDK SYNTAX** evidence and factual final authority; **not** original execution getter runtime safe, P1, R03, H2, Player or full V1 identity. If real Git/SSH times out, preserve raw FAIL and aggregate/manifest lifetime true/unsealed, partial sources/streams, no retry, no later audit promotion. No real metadata Shutdown/Reader concurrency experiment in Unity.

## 7. Local ownership / return / STOP

Local may edit/push **ONLY** factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md`, and one new additive `local-validation-p1-admitted-execution-20261022-e1e5/` checkpoint. Nontrivial native/source/compiler problems return as evidence to Primary, not Local refactors or hidden retries. Verify all four latest remote heads after factual commit, then **STOP regardless of outcome**.

Preserve `7896` PASS, `7c2c` PASS, `82dd` FAIL, all old M/N/S/R02 source fingerprint/strict S/full independent stage verdicts and all acceptance booleans false. **P1 Incomplete** (canonical generic TypeKeys, physical allocator pointer provenance/lifetime, coherent VM epoch, full execution V1, original getter integration, process GC/RSS/Shutdown); **P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete**. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No protected SNAP-01, Human Review Gate, H2/X02/M08A.
