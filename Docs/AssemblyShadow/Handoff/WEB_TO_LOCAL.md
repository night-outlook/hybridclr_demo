# Primary Implementation → Local Validation

## Objective

Validate the formal-admission pilot verification seal at candidate build-input/tool source anchor:

`01cdd033665400eba9fa0533fe17c12f9da92746`

Then, if the retained V04 graph/map/preregistration/pilot evidence remains hash-identical and the source-scope audit confirms no affected Player/runtime input, complete in one Local cycle:

fresh authority/tool tests → retained V04 reuse audit → one strict pilot seal → all 40 formal pairs → final analysis → Python/EditMode prerequisite closure → authenticated checkpoint → V05/M08 if eligible.

Latest Local return:

`fa23a0ddcf45eabc870e7e7742d2d18a78a52d49`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source anchor `01cdd033665400eba9fa0533fe17c12f9da92746` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected profile-1 family remains unchanged:

- demo HEAD `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- demo source anchor `f1c923cbaa814e1b63f3c5b9f8303c90616de726`;
- HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Environment target:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from source anchor.

Retained V04 evidence root:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`

## Implementation

### Local result being addressed

The latest Local cycle closed both previous controlled-workflow blockers in real Unity/IL2CPP and completed:

- protected profile-1 controlled Native ON/OFF;
- candidate profile-2 controlled Native ON/OFF;
- exact `link.xml` + `ProjectSettings.asset` restoration;
- nested native-only provenance scoping plus outer authority checks;
- old-Player rejection;
- strict A/B map freeze with `ComparabilityPassed`;
- unchanged preregistration;
- all four pilot pairs.

Formal pair 1 did not launch. Every formal driver invocation re-entered `_successful_pilots`, which called `r00_results.verify_suite` on A/B for all four pilots. The observed pre-launch verification remained active for 47 minutes 39 seconds while hashing/reconstructing eight already-passed pilot graphs.

This is an admission-orchestration scalability defect, not a failed performance sample.

### Strict pilot verification seal

Primary added:

`Tools/AssemblyShadow/seal-h1-pilot-verification.py`

After all pilots pass, the sealer:

1. selects the latest retained successful attempt for every pilot mode;
2. derives each launch receipt's complete `inputHashesBefore == inputHashesAfter` inventory plus result/early evidence;
3. snapshots canonical filesystem identity for the union of those files;
4. executes the unchanged deep `r00_results.verify_suite` reconstruction for all eight A/B pilot launches exactly once;
5. requires the complete identity inventory to remain unchanged after deep verification;
6. binds:
   - protocol;
   - schedule;
   - frozen build map;
   - full retained pilot-attempt history;
   - selected pilot launch receipts;
   - formal/seal verifier/tool implementations;
7. writes `H1PilotVerificationReceipt`.

The filesystem guard records canonical path plus device, inode, mode, size, mtimeNs, and ctimeNs.

### Cached formal admission

`run-h1-paired-performance.py` formal phase now requires:

`--pilot-verification-receipt <sealed-receipt>`

For every formal pair it:

- re-hashes compact protocol/schedule/map/launch/tool controls;
- requires the retained pilot-attempt digest and selected launch bindings to be unchanged;
- re-derives the current immutable path/hash set from current pilot launch receipts;
- requires every sealed filesystem identity guard to match;
- fails closed on any mismatch;
- never silently deep-rescans or rebuilds the seal.

The cumulative formal `sample-index.json` carries the same `pilotVerification` path/hash. A later formal invocation cannot switch to another seal.

### What is deliberately unchanged

This repair does not change:

- any Player/runtime/Bootstrap C#;
- HybridCLR native;
- HybridCLR Unity;
- IL2CPP;
- `run-r00-players.py`;
- `r00_results.py`;
- `r00_player_inputs.py`;
- frozen graph/build-map semantics;
- performance protocol JSON;
- bound schedule JSON;
- preregistration;
- pair order;
- whole-pair retry;
- timing/statistics;
- final paired analyzer.

Final analysis remains fully strict and uncached.

### Primary regression coverage

`Tools/AssemblyShadow/tests/test_h1_paired_driver.py` now proves:

- strict sealing performs exactly **8** deep pilot-side verifications;
- **40** formal admissions perform **0** deep pilot rescans;
- changed pilot receipt fails;
- changed bound graph artifact fails;
- changed protocol fails;
- changed schedule fails;
- changed build map fails;
- changed verifier implementation fails.

The paired-driver module is now part of the bounded Primary regression suite.

## Local validation

Detailed executable plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Fresh admission

1. Fresh V00 candidate/reproduction/protected authority.
2. Candidate/protected installed-runtime verification.
3. Bounded Primary and live-handoff tests.
4. Direct paired-driver regression.
5. Source-scope audit from `69130bbb...` to `01cdd033...`.

### Required reuse audit

Expected executable/tool/test/CI delta is exactly:

- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/seal-h1-pilot-verification.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`;
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `.github/workflows/h1-bee-primary.yml`.

If any Player/runtime/runner/protocol/schedule/map/preregistration/analyzer input changed, do not reuse the retained V04 artifacts.

If scope matches, authenticate the prior V04 checkpoint and all live bound graph/map/protocol/schedule/pilot hashes before reuse.

### Seal pilots once

~~~text
python3 Tools/AssemblyShadow/seal-h1-pilot-verification.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <frozen-build-map> \
  --pilot-index <retained-pilot-sample-index> \
  --output <new-pilot-verification.json>
~~~

Require:

- `kind=H1PilotVerificationReceipt`;
- `status=PassedStrictReconstructionAndStatGuardSealed`;
- `deepLaunchVerificationCount=8`;
- all four pilot modes selected;
- verifier/control bindings exact;
- no pre/post file-identity change.

Record seal duration and receipt `fileCount/totalBytes`.

### Run all formal pairs with the same seal

First formal pair:

~~~text
python3 Tools/AssemblyShadow/run-h1-paired-performance.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <frozen-build-map> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-pilot-sample-index> \
  --output-root <new-formal-pair-root> \
  --phase formal \
  --attempt 1
~~~

Chain each produced `sample-index.json` into the next pair's `--prior-index`.

For a legitimate retry, retain the failed attempt and rerun the same pair with explicit `--pair-id` and incremented `--attempt`. Never rerun only one side.

All formal sample indexes must carry the same pilot-verification path/hash.

For formal pair 1, record pre-launch admission duration and prove the old 47:39 repeated pilot reconstruction does not recur.

### Final analysis and inventory closure

After all forty formal pair IDs complete:

~~~text
python3 Tools/AssemblyShadow/analyze-h1-paired-performance.py \
  --sample-index <final-sample-index.json> \
  --output <new-performance-analysis.json>
~~~

Do not use the pilot seal as a substitute for this analyzer.

Before V05 eligibility, freshly rerun:

- complete Python inventory after the policy-pinned M00 fixed prerequisite is present;
- broad Unity EditMode after required generated M00/M01/M05 prerequisites are present.

Prior generated-prerequisite failures are not Passed evidence.

## Failure evidence

If sealing or formal admission fails, retain:

- exact command and phase;
- source/checkout identity;
- pilot verification receipt or sealing failure output;
- protocol/schedule/map hashes;
- pilot attempt digest;
- selected launch receipt bindings;
- first invalidated file path and cached/current guard;
- verifier binding mismatch when applicable;
- cumulative prior sample index;
- any formal side output/launch receipt if launch already began;
- owned-process cleanup evidence.

If a formal pair fails after launch, retain the complete failed whole-pair attempt and follow the preregistered retry policy.

Do not clean the retained V04 live graph/pilot artifacts until the new checkpoint is authenticated.

## Alternatives

Do not:

- remove strict pilot verification;
- trust only the pilot index status without reconstructing the pilot graphs once;
- cache solely on path or size;
- auto-reseal after a guard mismatch;
- silently fall back to repeated deep scans inside formal admission;
- change `r00_results.py` semantics to make admission faster;
- weaken final analyzer verification;
- alter protocol/schedule/map/preregistration after observed timings;
- delete failed/retried samples;
- rebuild already-passed controlled graphs unless the source/hash reuse audit requires it;
- begin R02.

## Risks

- Initial strict sealing still performs the expensive eight-side reconstruction once; this is intentional evidence creation.
- Filesystem identity guards are valid only while the retained live artifacts remain untouched; cleanup/copy/rewrite requires resealing after strict verification.
- Forty formal pairs remain intrinsically long because each pair executes two real Players.
- Final analysis remains intentionally expensive because it independently verifies selected evidence.
- Complete Python/EditMode acceptance still requires generated prerequisites that were absent during the previous early V01 run.

## Local correction boundary

Local may adjust only:

- absolute local paths;
- new output/evidence roots;
- executable permissions;
- bounded invocation syntax;
- pair retry attempt numbers when the preregistered whole-pair policy permits retry.

Local must not alter:

- seal schema/guard semantics;
- selected pilot semantics;
- verifier bindings;
- source anchor/protected pins;
- retained graph/map/protocol/schedule identities;
- pair ordering/retry policy;
- statistics/analyzer;
- source/verifier authority.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Formal performance, final analysis, complete inventory closure, V05, and a genuinely independent M08 remain required.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
