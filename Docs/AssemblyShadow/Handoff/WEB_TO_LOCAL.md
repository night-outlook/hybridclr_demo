# Primary Implementation → Local Validation — ONE P1 registry revision source/SDK cycle

**Exactly ONE NEW source-pinned, source/host + installed Unity2022.3.62f2 SDK SYNTAX-ONLY cycle is authorized**, subject to all admission gates below. The newly inactive registry revision is not an all-VM epoch, valid metadata class dereference, complete execution JSON, or Player/runtime acceptance. No Unity Editor, Test Runner, Player, native linking, seven-root runtime/SNAP-01, scheduler/engine-owner experiment, Human Review Gate, H2/X02/M08A or other milestone is permitted. Local must not change substantive implementation, test or compiler code.

## Factual history and mandatory reading

**Last consumed Local run**: `20261019-d548` **PASS / PassedSourceHostAndSDKOnly**, 16/16 independently receipted components, 75 command-failure tests, five positive managed compilation products plus the exact original expected-negative case, 90/90 native SDK C++17 arm64 syntax checks, all source/SDK/historical hashes preserved. Its original raw/scratch/audit/checkpoint are consumed and must not be rerun, renamed, overwritten or reclassified. All earlier P1 PASS/FAIL, historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, and independent R03 full-stage FAIL/re-review NotRun remain unchanged.

Read, in order: `Docs/AssemblyShadow/README.md`; `Plan/CURRENT_STATUS.md`; Local-owned `Handoff/LOCAL_VALIDATION.md` **before** `Handoff/RETURN_TO_WEB.md`; [design](../History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/DESIGN.md); [Primary review](../History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/PRIMARY_REVIEW.md); [source/CI evidence](../History/M07R/R03/IR_Remediation/P1_REGISTRY_REVISION_2026-10-20/EVIDENCE.json); this entire handoff; [remaining implementation plan](../History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md). Do not infer source or test state from older chat.

## Four source repositories and strict pins

Branch for **all** is `codex/assembly-shadow-r01b-h1`. Each checkout is a **separate** Git working tree with canonical `night-outlook/<repo>` origin, clean status and matching local and live remote exact HEAD. Workspace parent `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` is not itself a repository. Fast-forward only clean ancestors; never reset, clean, overwrite unrelated changes or force-push.

| Repository | Local checkout | Required full SHA |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **The final published, verified Docs-only HEAD containing this exact WEB_TO_LOCAL.md**. It MUST equal the explicit full 40-hex SHA in the accompanying Primary handoff prompt, `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` and live branch tip. The SOURCE/CI anchor is `05077e54a4b350c7cce7c3efce5161a975c7719d`; every commit after this anchor must touch only `Docs/**`. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `f09edc0499fa8baf964b80256a71ce9f4d2bd522` |

The historical `Tools/AssemblyShadow/R03/source-pins.json` records earlier source evidence and MUST remain unchanged. The candidate source is selected only by the outer script's `--candidate-native-sha`. A later source or even Docs-only branch commit invalidates this authorization until Primary publishes a fresh reviewed handoff. Isolated Connector smoke branches are not project feature branches and must never be substituted for this source tuple.

## Primary implementation already delivered — Local verifies only

- Native `AssemblyShadowExecutionRegistryRevision.h`: saturating fixed-size revision; `Advance()` only after a **successful new registry insertion** while the existing `ExecutionObservationLock` is held. No new lock, heap buffer, managed call or pointer dereference.
- `AssemblyShadowOpaqueExecutionInventory.h` and `.inl`: bind revision to each opaque 2,048-slot/1,024-count snapshot; require exact slot, count **and version** equality; refuse saturated/invalid version, duplicate identity, changed state, closed admission, scratch reuse. Expose numeric `registryRevisionBefore/After` and boolean `registryRevisionFenceStable` on success, scrub all retained opaque values. No pointer origin/lifetime or VM-wide coherence is proven.
- Native actual production host fixture and runner now require **21 distinct cases each strict and ASan/UBSan**, including the formerly 18 source-bound cases plus same-slot/different-revision rejection, stable nonzero revision, saturated-version refusal. The exact prior `AssemblyShadow.cpp` getter/guard blob is still proven unchanged after removing only approved additive snippets. No active getter, C# API or V2 transport was changed.
- Demo existing aggregate has **16 independently receipted cells**, retains **75 unique command-failure tests (5+14+34+10+12)** including fail-stop/NotRun, and now hashes the new native revision header. The existing native SDK syntax probe additionally compiles the actual revision type and fixed-size/fail-closed type contract.
- Official installed native candidate matrix remains **90 actual Apple arm64 C++17 syntax commands = 18 translation units × five original candidate/debug/probe-off/diagnostics-off/feature-off profiles**. The full real `AssemblyShadow.cpp` compiles the new instrumentation, alongside `AssemblyShadowOpaqueInventorySyntax.cpp`; unchanged managed SDK still builds five positive products and distinct `OriginalUnsignedCounts` exit1/exact two CS0266/no DLL negative.
- [Native CI 39360310335](https://github.com/night-outlook/il2cpp_plus/actions/runs/39360310335) PASS 3/3 Mac/Linux native host jobs, 21 × 2 source tests per job; [integrated demo CI 39360193616](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193616), [focused failure CI 39360193811](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193811), [managed/aggregate CI 39360193768](https://github.com/night-outlook/hybridclr_demo/actions/runs/39360193768) PASS within controlled host/mock scope. These do NOT replace official installed Unity SDK syntax or Player runtime evidence.

## ONE unused evidence/audit/checkpoint set

All FOUR paths must be **absent**, canonical, mutually disjoint, outside SDK, checkouts and every consumed external source/scratch/audit before the run. Independently verify sufficient approved external disk space and unchanged source/SDK/prior manifests before creating new evidence. The Local audit/checkpoint may be created ONLY after admission; Primary's outer script must not precreate them.

- New raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-REGISTRY-REVISION-20261020-f09e`
- New SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-REGISTRY-REVISION-20261020-f09e`
- New independent audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-REGISTRY-REVISION-20261020-f09e`
- New additive committed checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-registry-revision-20261020-f09e/`

Installed read-only Unity SDK executable path (**do not launch**): `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Keep inherited TMPDIR, original Apple SDK compiler procedure, private/temp owner policy; do not commit Unity/vendor SDK binaries or use previous scratch outputs as fresh results.

## Exactly ONE executable invocation after all preflight checks

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=05077e54a4b350c7cce7c3efce5161a975c7719d
NATIVE=f09edc0499fa8baf964b80256a71ce9f4d2bd522
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-REGISTRY-REVISION-20261020-f09e" \
  --sdk-scratch "$B/Scratch-R03-P1-REGISTRY-REVISION-20261020-f09e"
```

The one-shot attempt is consumed on PASS/FAIL/Blocked/timeout/interruption. **Never retry, resume a child, reuse/rename any previous root, adjust thresholds, or substitute old SDK outcomes.** An unknown command/descendant lifetime stops all later subprocess cells and postflight Git/source checks; later planned cells become factual `NotRun` without component roots, with preserved partial streams/unsealed evidence. A known completed nonzero child remains failed, without being fabricated as an unsafe survivor. No Local source or compiler procedure fixes.

## Required independent verification and return

Inspect all **16** outer cells and their actual nested/source-bound receipts: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, `empty-live`, `opaque-inventory`, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`.

To report `PASS / PassedSourceHostAndSDKOnly`: 16/16 exact `Passed` outer results, inner verdicts matched, no unverified lifetime, original source+SDK fingerprints unchanged before/after, exact four local/remote source pins, `sourcePreserved=true`, `postflightError=null`, `stoppedAfter=null`, correct actual SDK attempted/passed flags and no historical evidence/status reclassification.

- `opaque-inventory`: **21 named groups per strict/ASan+UBSan host profile**, both profiles green, five actual version/compile/run command receipts exit0 and stream SHA joins. Verify `registryRevisionBefore==registryRevisionAfter` and `registryRevisionFenceStable=true` on the successful fixture; same slots with a changed revision and saturated MAX must be explicit fail-closed cases. Its numeric revision is **registry-only**; original `physicalClassPointerOriginProven=false`, `coherentVmEpochProven=false`, `completeExecutionSource=false`, `officialUnitySdkCompiled=false`, `UnityPlayerExecuted=false`, `runtimeAcceptance=false` stay false. No class pointer dereference/return or original getter call is permitted.
- Keep all 75 source-bound controlled failure tests (5+14+34+10+12), zero failures/skips. Retain prior source-host `live-general` 13/profile, `owned-general` 11/profile, first-use 15/profile, `owned-execution` 6×35, `empty-live` 2×20, and original legacy/frozen-V2 negative and serializer byte-parity controls.
- Five managed SDK products and original distinct compiler-negative (exit1, exactly two CS0266, no DLL) require actual fresh compiler receipts and exact nested producer path/hash joins. All 90 native C++17 Apple arm64 official SDK syntax commands (18 units × five original profiles) must compile the actual production `AssemblyShadow.cpp` with the **new revision header** and existing opaque signature probe, not a mocked-only proxy. Preserve diagnostics/warnings truthfully; do not require copied historical warning counts.
- Preserve installed Unity SDK files and all consumed P1 raw/manifest/audit/scratch inventories, native old generator-source pins, deliberate symlink negative controls, and historical SNAP-01/N/M/K/I/E/R02 FAIL and strict S custody Blocked, with digest checks and signed/hashed results before/after. Keep descendantQuiescenceProven=false and process GC/RSS/Shutdown/Player acceptance flags false.

Local owns only factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, one additive versioned checkpoint, and bounded environment diagnosis. Publish these by committed/pushed GitHub source tuple, with independent raw/audit receipt hashes and exact new local/remote SHAs. Preserve all history byte-for-byte and stop after the ONE batch.

## Acceptance and stop boundary

**STOP** and return to Primary Implementation; no automatic new Local cycle, R03 acceptance, Human Review Gate, H2 or other milestone. P1 remains Incomplete for class metadata origin/lifetime, nonempty class JSON/type keys, global VM epoch/ABA, getter integration, process allocation/GC/RSS and Shutdown. P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Original reporting/500ms/1–64 uncapped/GC/logger/recovery/canary predicates and V1/V2 budgets remain fixed. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
