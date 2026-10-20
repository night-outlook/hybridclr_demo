# Primary Implementation → Local Validation — ONE registry-bound owned physical-name source/SDK cycle

**Authorization:** exactly **one new** source-pinned **18-component SOURCE/HOST plus official installed Unity2022.3.62f2 SDK SYNTAX-ONLY** batch after independent Local preflight, under the four exact latest pushed source heads below. New P1 objective: validate bounded `registrySlot` / Candidate-or-ActiveShadow witness binding for the previously owned physical display-name rows; verify typed invalid/duplicate/refused first-match registrations and failure scrub. This is NOT a Unity Editor/Test Runner/Player launch, linked runtime, native owner-safe-point experiment, protected historical SNAP-01, Human Review Gate, H2/X02/M08A, or another milestone. Local owns factual validation, not implementation.

## 1. Mandatory read order and consumed authority

1. Current `Docs/AssemblyShadow/README.md` then `Plan/CURRENT_STATUS.md`, at the **final exact pushed demo HEAD** from Primary's accompanying prompt.
2. **First** Local-owned `Handoff/LOCAL_VALIDATION.md`, **then** Local-owned `Handoff/RETURN_TO_WEB.md`, and the entire immutable last Local [P1 owned-name checkpoint](../History/M07R/R03/local-validation-p1-owned-physical-names-20261020-e6a3/README.md).
3. New [design](../History/M07R/R03/IR_Remediation/P1_BOUND_REGISTRY_ROWS_2026-10-20/DESIGN.md), [plan](../History/M07R/R03/IR_Remediation/P1_BOUND_REGISTRY_ROWS_2026-10-20/PLAN.md), [Primary audit](../History/M07R/R03/IR_Remediation/P1_BOUND_REGISTRY_ROWS_2026-10-20/PRIMARY_SOURCE_AUDIT.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_BOUND_REGISTRY_ROWS_2026-10-20/EVIDENCE.json), previous owned physical-names design and full P1/P2/E0/E1/P3 remaining acceptance plan; then read this entire handoff.
4. Mandatory independent Local admission: all four Git working trees and remotes, prior consumed evidence/SDK inventories, new root absence, source fingerprints, repository source-pin ancestry and available space BEFORE any new audit/root creation.

**Last consumed Local cycle** `20261020-e6a3` = **PASS / PassedSourceHostAndSDKOnly**: 18/18 children, 85 Python failure cases, 20 owned physical name groups/profile, 21 physical membership groups/profile, five actual managed positives plus exact negative, **100/100** Apple arm64 native SDK syntax commands. It has already executed **once** and is immutable; do not rerun its root, reclassify any old result or interpret it as linked Player/runtime evidence. Its source tuple was demo `63c812228c749bb44129ee141ab32895cfdc62e1`, native `e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5`, other two as below.

## 2. Four authoritative repositories and exact test-source pins

Branch for **every** independent repository: `codex/assembly-shadow-r01b-h1`. Canonical remotes are the four `https://github.com/night-outlook/<repo>.git` equivalents (or SSH resolving to the same repositories). Parent `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` is NOT a repository. Local must inspect each nested repository, branch, `git status --porcelain`, submodule identity, local HEAD and live `git ls-remote` and fast-forward **only clean ancestor checkouts**; no reset/clean/force/merge, no unrelated modifications.

| Repository | Exact existing Local checkout | Required latest pushed HEAD |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final Docs-only handoff-containing commit** from Primary's final Local prompt; must equal current `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` and live remote HEAD. Tested demo source anchor **`b2d6345f66fdf76456b5fab943f0737da4c62974`**; all later commits must modify **Docs/** only. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | **`bc3b7df43c5009fa4bc7f6d94e414ad9cd135f62`** |

Do NOT update or rebaseline historical `Tools/AssemblyShadow/R03/source-pins.json` (native historical pin `74dbdbea80d83923863303bd2b2c0a87f36541b1`). Pass the current candidate native pin through the existing explicit `--candidate-native-sha` path. Honor original package `file:../../hybridclr_unity` source origin, installed Unity SDK fingerprints and all old four-repo committed provenance.

## 3. Production changes already completed by Primary — Local tests only

**Native:** five files in `il2cpp_plus`:
- `libil2cpp/vm/AssemblyShadowPhysicalMembership.h`: new `TryObservedRegistrationBinding` reads only the already matched opaque slot/witness/seen-bit table; before first callback match, unrelated pointer or scrubbed scratch returns no binding. Original `ObserveEnumeratedOwned`/void `ObserveEnumerated` and registry insertion/hash are unchanged.
- `libil2cpp/vm/AssemblyShadowOwnedPhysicalNames.h`: bounded row stores copied assembly/namespace/simple-name spans, `registrationSlot`, `registrationSource` and no raw class/image/assembly pointer; reject absent/bad role/out-of-range/duplicate slot; hard object limit <=512 KiB, <=1,024 rows, <=256 KiB text, <=4,096 bytes/field. Internal Add failures and caller-level `Revoke` clear text, rows and slot tracking. Receipt adds `boundRegistrationRows` and `allRowsBoundToObservedRegistry`; first owned error remains typed.
- `libil2cpp/vm/AssemblyShadowOwnedPhysicalNamesSource.inl`: source binding only **after exact FirstMatch**, synchronous iterator within existing `g_MetadataLock`; initial-session Reader and separate observation-lock before/after registry fence unchanged. No lock nesting. Remains **INACTIVE** and uncalled by original getters/Player/managed APIs. No new canonical `TypeKey` or general VM epoch claim.
- `tools/r03/diagnostic_stream/owned_physical_names_fixture.cpp` and `run_owned_physical_names.py`: actual production method/header and previous physical member source compiled under explicit mocks, **28 ordered host groups per strict/sanitized profile** (old 20 plus eight new binding/order/collision/bad-source cases). Five direct compiler-version/compile/run receipts; original CPP/API and pre-addition physical-header byte reconstructions source-gated.

**Demo source/tests:** `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py`, `test_p1_command_failures.py`, `test_p1_managed_receipt.py`. A successful owned-name producer must have the exact `R03P1InactiveOwnedObservedPhysicalNamesSourceHost` result/schema, two **ordered 28/28** strict/sanitized group arrays, actual compiled/preserved production source and explicit false runtime/provenance/TypeKey flags; the outer child receipt now carries `ownedBindingCaseInventoryVerified=true`. An incomplete/duplicated/malformed positive inventory fails closed. A child with known completed failure remains Failed without fictitious detached descendants; an unknown lifetime marks remaining commands NotRun, no unsafe postflight, no fabricated SDK result. A boolean schema version is refused. The adversarial positive/negative consumer tests are executed inside the existing 85 frozen distinct test leaves.

**CI evidence only, not Local SDK:** Native owned source suite Linux GCC+Clang passed at [run 39452191805](https://github.com/night-outlook/il2cpp_plus/actions/runs/39452191805); macOS job status must be independently checked (was queued when first inspected). The first prior candidate run [39452019927](https://github.com/night-outlook/il2cpp_plus/actions/runs/39452019927) FAIL at precompile inventory/fixture and remains historical. Demo preceding [integrated run 39453680455](https://github.com/night-outlook/hybridclr_demo/actions/runs/39453680455) PASS Mac+Linux, after correcting a separate old 85-test inventory precompile FAIL [39452772587](https://github.com/night-outlook/hybridclr_demo/actions/runs/39452772587). Full final demo code source `b2d6345f...` also needs its own CI admission or Local evidence; do not claim an older code commit is the final source.

## 4. ONE fresh root set — never precreate, reuse or retry

All FOUR paths below must independently be absent, canonical, pairwise disjoint, outside the four Git checkouts, Unity Editor/SDK and all previous raw, scratch, audit or symlink negative-control roots. Preserve inherited TMPDIR/CXX, compiler-private temporary policy and existing installed SDK. Local first authenticates the consumed historical manifests and expected preexisting sources without creating new audit files. Local creates audit and the additive checkpoint **only after** preflight admission; the attempt consumes all four root names on PASS/FAIL/timeout/interrupt/Blocked.

- **Raw:** `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-BOUND-REGISTRY-20261020-bc3b`
- **Official SDK scratch:** `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-BOUND-REGISTRY-20261020-bc3b`
- **Independent Local audit:** `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-BOUND-REGISTRY-20261020-bc3b`
- **Additive source-tracked checkpoint:** `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-bound-registry-20261020-bc3b/`

Read-only installed official SDK anchor: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. **Do not launch Unity**. This is an SDK header/compiler input anchor only. Local must verify installed SDK hash/layout, original negative symlinks, all previously consumed 13 P1 raw/scratch/audit states (including latest e6a3), available external storage and clean four-repo provenance before root creation.

## 5. Exactly ONE command after independent Local admission

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=b2d6345f66fdf76456b5fab943f0737da4c62974
NATIVE=bc3b7df43c5009fa4bc7f6d94e414ad9cd135f62
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-BOUND-REGISTRY-20261020-bc3b" \
  --sdk-scratch "$B/Scratch-R03-P1-BOUND-REGISTRY-20261020-bc3b"
```

This is the sole run. No Local child resume, second attempt, renamed suffix root, parallel SDK run, compiler overrides, threshold relaxation, source fixes or fabricated postflight. An unknown command/descendant lifetime must STOP later subprocesses and mark scheduled children NotRun without creating their component roots or unsafe source/Git postflight; keep actual streams (complete/prefix/unavailable), nullable exits and unsealed inventory factual. Do not independently assert global descendant quiescence after a completed child.

## 6. Required single-batch test matrix and empirical return

Verify all 18 separate children in order:

1. `command-failures` — **85 original unique tests = 5+14+44+10+12** and no failures/errors/skips.
2. `legacy-host`; 3. `metadata-gate`; 4. `bounded-class`; 5. `bounded-physical`; 6. `bounded-first-use`.
7. `owned-general`; 8. `live-general`; 9. `owned-execution`; 10. `empty-live`; 11. `opaque-inventory`.
12. `physical-membership` — retained **21 distinct groups/profile**.
13. `owned-physical-names` — **28 distinct groups strict and 28 sanitized**, `PassedWithinInactiveOwnedPhysicalNamesHostScope`, five actual native version/compile/run receipts, exact raw/stream hashes, typed fail-stop, **producer** and **outer** case inventory identity; `ownedBindingCaseInventoryVerified=true`.
14. `bounded-status`; 15. `bounded-inventory`; 16. `frozen-v2`.
17. `managed-sdk` — five **real** official compiled products and independent `OriginalUnsignedCounts` expected-negative (compiler exit1, exactly two original CS0266, no DLL), canonical nested return/path/SHA join with no root fallback.
18. `native-sdk` — **100/100** actual Apple arm64 C++17 `-fsyntax-only` commands, 20 unique translation units x five candidate/debug/probe-off/diagnostics-off/feature-off profiles including full production `AssemblyShadow.cpp` and owned/membership syntax probes, no synthetic compile flags; actual warnings retained as observations.

Other retained strict/sanitized groups and exact original V1 byte parity, R02, publisher (34/profile), owned execution (6x35), empty-live (20/profile), general and frozen tests must retain unchanged semantic scope and source bindings. New eight owned-binding groups demonstrate **reversed order**, **same display names remain distinct**, **open-address hash collisions**, pre-first-match rejection, unrelated-metadata rejection, bad slot/bad witness role rejection and duplicate binding scrubbing. Confirm actual row slot/source joins and owned text independence after original source name mutation; host assertions are not separately recorded raw per-row JSON unless actually emitted.

To claim `PASS / PassedSourceHostAndSDKOnly`: 18/18 outer Passed with corresponding actual inner Passed, 85 Python cases, 28+28 owned binding groups, outer bound inventory true, 100/100 official syntax compiles, five real managed positives+negative, `sourcePreserved=true`, `postflightError=null`, `stoppedAfter=null`, `commandLifetimeUnverified=false`, official SDK attempted/passed flags actually true, four unchanged clean local/remote heads, original installed SDK and every consumed source/history hash unchanged. Logs/receipts must bind exact argv, streams, PID/time, SDK/source hashes, individual cells and final manifest. Keep `descendantQuiescenceProven=false` absent independent positive proof.

Factual `Passed` in this one batch proves **source/host/installed SDK syntax only**. The newly bound slot/source is snapshot-local and cannot certify stable class pointer ownership, generic-aware `TypeKey`, VM epoch/ABA, safe shutdown, GC/RSS/latency, full execution JSON or Player acceptance. Preserve all historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, independent full-stage R03 FAIL/re-review NotRun and unused superseded roots. Never promote old failures or reused-audited evidence into new full-stage R03 acceptance.

## 7. Local modification ownership and return

Local may modify **only** factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md` and one new additive `local-validation-p1-bound-registry-20261020-bc3b/` checkpoint; environment-only bounded diagnosis is allowed. Do not alter source/native/compiler/test code, README, Plan, Primary review, `WEB_TO_LOCAL.md`, original historical metadata/pins, evidence or SDK. A substantive finding is returned to Primary with raw provenance, not locally fixed. Commit and push factual Local files; verify exact remote HEADs for all four repositories. **STOP after this one cycle** regardless of outcome and return to Primary Implementation.

## 8. Open risks, next gate

P1 **Incomplete**: physical class allocation origin/lifetime, canonical generic-aware execution TypeKeys, full nonempty execution row/JSON, VM-global coherent epoch/ABA, original getter integration, allocation/GC/RSS/latency, MetadataLock/Shutdown. P2 **NotIntegrated** real native/C# V2 transaction. E0 **Blocked/Unavailable** vendor-supported StandaloneOSX owner safe point. E1 **BlockedByE0** drain/restart. Full P3 **Incomplete** linked Player runtime. Strict S custody remains Blocked; original reporting/logger/GC/500ms/1..64 uncapped/recovery/canary, original R02 regression/performance and all historical negative contracts remain pending or factual. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

This handoff authorizes one narrow Local source/SDK syntax batch and nothing else. Local may not begin H2/X02/M08A or any subsequent milestone. Primary must reconcile returned results before preparing another source change or review gate.
