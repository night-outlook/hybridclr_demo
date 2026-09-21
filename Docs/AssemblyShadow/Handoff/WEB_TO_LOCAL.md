# Primary Implementation → Local Validation

## Objective

Validate the two V04 controlled-workflow boundary repairs at candidate build-input source anchor:

`2d44ee4eef735cf9dc5c2295fb8c0df71834743f`

in one Local batch:

fresh authority/tests → protected profile-1 controlled Native ON/OFF → candidate profile-2 controlled Native ON/OFF → old-Player check → strict A/B map → preregistration → pilots → formal analysis → retention → V05/M08 if eligible.

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source anchor `2d44ee4eef735cf9dc5c2295fb8c0df71834743f` |
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

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from the source anchor.

## Implementation

Latest Local return:

`8788d123ca7769396cf14c707f8df13ac764223b`

The prior label repair is proven in real Unity. Two later blockers were returned.

### Repair 1 — exact controlled Player settings restoration

The controlled Native ON build changed:

`ProjectSettings/ProjectSettings.asset`

from its pinned empty `il2cppCodeGeneration` map to an explicit `Standalone: 0` representation after semantic restore. The next exact source guard correctly stopped.

`Invoke-M07PlayerMethodWithGeneratedInputRecovery` now owns an exact-byte transaction for **both**:

- `Assets/HybridCLRGenerate/link.xml`;
- `ProjectSettings/ProjectSettings.asset`.

For every `native-on`, `native-off`, `native-on-controlled`, and `native-off-controlled` stage it:

1. captures original bytes/hash before Unity;
2. creates immutable per-input backups;
3. invokes the Player build;
4. preserves post-build bytes;
5. restores both originals in the finally path;
6. verifies exact SHA equality;
7. emits per-input receipts;
8. returns only after restoration, so the existing source guard sees pinned bytes.

Recovery attempts both inputs even when another recovery operation fails. If recovery succeeds and the build failed, the original build failure is rethrown.

Receipt kinds:

- link.xml: `M07GeneratedPlayerInputRestoration`;
- ProjectSettings.asset: `M07ControlledPlayerSettingsRestoration`.

### Repair 2 — nested native provenance execution scope

`H1BuildInputProvenance.CaptureAfterGenerate` performs a native-only installed-runtime verification with `--skip-demo-source`.

The nested child process now removes only:

- `H1_M07_WORKFLOW_AUTHORITY_ROOT`;
- `H1_M07_WORKFLOW_BASELINE_ID`;

from its own `ProcessStartInfo.EnvironmentVariables`.

The parent Unity/coordinator environment is unchanged. The outer M07 pinned-input guard therefore retains the complete workflow/demo-source authority immediately after each Player stage. `verify-installed-runtime.py` itself was not weakened and still rejects a caller that supplies `--skip-demo-source` while M07 authority is active.

Provenance evidence records:

`verificationEnvironmentScope=NativeOnlyWithoutOuterM07WorkflowAuthority`

### Primary regression support

Added/updated:

- `Tools/AssemblyShadow/tests/test_m07_player_input_recovery.ps1`;
- `Tools/AssemblyShadow/tests/test_m07_generated_input_recovery_labels.ps1`;
- `Tools/AssemblyShadow/tests/test_h1_m07_workflow_authority.py`;
- `Assets/AssemblyShadowDemo/Tests/Editor/M07BuildTests.cs`;
- `.github/workflows/h1-bee-primary.yml`.

The direct recovery test extracts the actual production helper, mutates both files, and proves exact restoration on success and simulated stage failure without launching Unity.

No HybridCLR native, HybridCLR Unity, IL2CPP, performance protocol/schedule/analyzer, capacity/index, dense metadata, or runtime transaction semantics changed.

## Local validation

Detailed executable plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Fresh mandatory admission

1. Fresh V00 candidate/reproduction/protected authority.
2. Candidate and protected installed-runtime verification.
3. Complete current Python/bounded regressions.
4. Both direct PowerShell recovery tests.
5. Broad Unity EditMode sanity.
6. Source-scope audit from `316894a8...` to `2d44ee4e...`.

### Profile-1 controlled workflow

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <reference-demo> \
  -BaselineId M07-Baseline-H1-Perf-Reference-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX \
  -ControlledPerformanceBuilds
~~~

Native ON and Native OFF must both complete.

For each controlled label verify both:

- `<label>-link-xml-restored.json`;
- `<label>-project-settings-restored.json`;

with `status=ExactBytesRestored` and `originalSha256 == restoredSha256`.

The exact pinned-input guard immediately following Native ON must pass.

### Profile-2 controlled workflow

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <candidate> \
  -BaselineId M07-Baseline-H1-Perf-Current-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX \
  -ControlledPerformanceBuilds
~~~

Require the same two-input restoration for Native ON/OFF.

Candidate controlled evidence must show successful native provenance with `verificationEnvironmentScope=NativeOnlyWithoutOuterM07WorkflowAuthority`. No nested `M07 workflow authority cannot be invoked with --skip-demo-source` failure is acceptable.

The subsequent outer source-authority guard must still run and pass.

### Continue the performance chain

Only after both complete graphs pass:

1. current-anchor old-Player rejection;
2. strict A/B build-map freeze with `ComparabilityPassed`;
3. preregistration binding;
4. every pilot pair;
5. every formal pair when pilots pass;
6. final paired analysis;
7. authenticated checkpoint;
8. V05 and genuinely independent M08 only when mandatory V04 is complete.

Historical runtime evidence may be referenced only under its original hashes/classification, e.g. `ReusedAuditedFrom925e` when the source-scope audit justifies reuse. Do not relabel it fresh current-anchor PASS.

## Failure evidence

If either repaired boundary fails, retain before cleanup/manual recovery:

- exact command, stage, and label;
- complete coordinator and Unity logs;
- tracked-state diff;
- original/generated/restored hashes for both mutable Player inputs;
- both restoration receipts when helper-body entry occurred;
- controlled Player receipt/evidence if produced;
- native provenance capture including verifier argv/stdout/stderr/environment-scope field;
- source/runtime verification before and after;
- outer workflow restoration receipt;
- failed bytes for any path the workflow itself did not restore.

Return non-trivial failures to Primary via `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`.

## Alternatives

Do not:

- weaken or bypass the exact source guard;
- add `ProjectSettings.asset` to the outer three-path M07 mutable-authority exception;
- rely on semantic Unity setters as exact-byte recovery;
- remove `--skip-demo-source` from the nested native-only proof and thereby broaden it into a conflicting full-source check;
- alter `verify-installed-runtime.py` to allow caller demo-source skipping under M07 authority;
- clear M07 authority variables from the parent coordinator/Unity process;
- hand-edit controlled receipts/build maps;
- change preregistered performance protocol, schedule, thresholds, or samples;
- begin R02.

## Risks

- The new PowerShell test proves real transaction behavior without Unity, but real Unity serialization/build behavior remains Local evidence.
- Exact-byte recovery assumes the owned Unity process has exited; the helper retains this guard.
- The nested scope change is intentionally child-only; Local must prove the outer authority recheck still executes afterward.
- Controlled workflows perform expensive IL2CPP builds and produce cleanup-sensitive evidence.
- Historical audited reuse remains review input, not fresh current-anchor acceptance.

## Local correction boundary

Local may adjust only:

- absolute local paths;
- fresh baseline IDs;
- fresh evidence/output roots;
- executable permissions;
- bounded machine-specific invocation syntax.

Local must not alter:

- the two controlled mutable-input transaction paths;
- restoration semantics or receipt requirements;
- nested verifier child environment scope;
- outer source/verifier policy;
- source anchor or protected pins;
- controlled-performance graph binding;
- protocol/schedule/statistics.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Mandatory V04 performance evidence must close before V05 and a genuinely independent whole-chain M08 review.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**. Human approval must then be explicit.

**Do not begin R02.**
