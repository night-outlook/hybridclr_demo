# Primary Implementation → Local Validation

## Objective

Validate the repair batch at candidate build-input source anchor:

`99ef65db13341f54cf610e18453dddf197ee86e4`

Then complete as much remaining H1 evidence as safely possible in one Local cycle:

fresh authority/builds → current M07 → startup/M07 matrix → early-owned failure/publication → current independent matrix → lazy-v2 Player → protected profile-1 M07 driven by current coordinator → old-Player → controlled A/B performance → retention → V05/M08 if eligible.

Latest Local return:

`7a627afc7d3615430772cd1f5e6978d5106f34c7`

H1 remains `InProgress`.

Historical independent M08 remains `FAIL`; it was not rerun.

`humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate:

| Repository | Branch | Identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source anchor `99ef65db13341f54cf610e18453dddf197ee86e4` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected identities remain:

- reproduction published head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`;
- reproduction tooling `ba8fee33753a5ebc215b7a98739e343d8e05572e`;
- performance reference demo HEAD `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- profile-1 reference HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- profile-1 HybridCLR Unity `b649c499385ea68490a0f652a98b732e060aeb89`;
- profile-1 IL2CPP `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Environment:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

Final checkout HEAD will be a later metadata-only handoff/status successor. Record it separately from source anchor.

## Implementation

### 1. Failure/publication transaction ownership corrected

The `4fff4df...` run proved that “early admission only → late transaction” is invalid.

After the earliest callback returned, normal host startup used candidate baseline assemblies. A later Begin/Validate therefore correctly failed `BaselineAlreadyUsed`.

The dedicated failure/publication matrix now executes the full transaction in the earliest callback.

Mapping:

| Matrix mode | Early mode | Callback |
| --- | --- | ---: |
| `R01-Failure-P03-Control` | `Control` | 0 |
| `R01-Failure-Q04-Metadata` | `MetadataFailureContinue` | 0 |
| `R01-Failure-InitializerThrow` | `InitializerFailureContinue` | 0 |

The continued modes reuse the exact existing failure transaction implementation.

Historical startup modes remain unchanged:

- `MetadataFailure` → callback 1 / terminal gateway;
- `InitializerFailure` → callback 1 / terminal gateway.

Continuation-only modes are rejected by the generic early suite and are owned by the dedicated failure/publication launcher.

### Late handoff is read-only

`R01FailureProbe` is now verification-only.

It:

- verifies the same current fixture/failure/Q04 graph;
- validates the profile-2 budget contract;
- requires early receipt file == `R01EarlyStartup.LastReceiptJson`;
- binds current PID, capsule hash, mode, baseline/runtime/patch/closure and actual staged DLL/PDB bytes;
- queries post-host diagnostics/capacity/recovery only.

It contains no calls to Configure/Begin/Reserve/Stage/Validate/Commit.

Expected post-host states:

- Control → `Committed`;
- Metadata → `Failed`;
- Initializer → `FailedAfterCommit`.

Launch/verification schema is v3; strict result records `transactionOwnership=EarliestStartup`.

The early receipt is transaction evidence. The late schema-2 handoff result is post-host persistence/provenance evidence.

### 2. Lazy deterministic-v2 command schema corrected

The producer writes four-field generation records:

`[mono, generator.exe, fixtureId, output.dll]`

The verifier now requires exactly four commands in deterministic order:

1. 1 / run1;
2. 1 / run2;
3. 2 / run1;
4. 2 / run2.

All existing v2 generator hashes, reproducibility, shape, parser, fixture confinement and sealed-v1 non-relabel requirements remain.

### 3. Protected profile-1 M07 uses current coordinator policy

The protected profile-1 installation was valid. Its historical wrapper policy was not suitable for current H1: it re-ran historical full demo-source verification after a workflow-owned mutation.

The current candidate core now always invokes the coordinator checkout's:

`Tools/AssemblyShadow/verify-installed-runtime.py`

rather than `<target-project>/Tools/.../verify-installed-runtime.py`.

The current verifier owns split dispatch under the outer `H1_M07_WORKFLOW_*` context:

- pre-mutation → full source/runtime verification;
- post-mutation → installed runtime/package/native verification plus `h1_m07_workflow_authority` against authenticated originals and the exact requested baseline.

The current outer wrapper still snapshots/restores the three tracked mutable paths byte-for-byte.

For the protected reference, Local must therefore run the **current candidate** `Invoke-M07Build.ps1` with `-ProjectPath <reference-demo>`.

Do not run the protected project's historical wrapper.

`verify-h1-protected-reference.py` now authenticates the actual reference-side Unity producers used by this coordinator, not the obsolete wrapper.

### Primary tests

Authority-consistent workflow `35411171891` passed before the final protected producer-list cleanup:

- bounded **320/320**;
- handoff **11/11**;
- early capsule **7/7**;
- early results **19/19**;
- failure pipeline **16/16**;
- lazy **9/9**.

Artifact `10573647440`, ZIP SHA-256 `6b6cc55adf33447829af1b680c738970e81d2f06db6a50ec0fd8f65540a72e11`.

A final CI run on source anchor `99ef65db...` is required and will be recorded before handoff completion.

## Local validation

Detailed executable plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Batch stop/continue policy

Hard-stop on:

- source authority mismatch;
- wrong runtime/package/native installation;
- tracked source drift not owned by the current M07 authority contract;
- invalid shared current/reference M07 graph;
- provenance corruption.

After shared foundations pass, retain isolated functional failures and continue independent cells when common authenticated inputs remain unchanged.

Never promote a failed prerequisite to acceptance.

### Priority validation

The next batch must specifically close:

1. real early-owned Control/Q04/initializer transaction execution;
2. same-PID late read-only persistence verification;
3. real lazy-v2 Player launch/execution;
4. protected profile-1 M07 through current coordinator;
5. fresh old-Player rejection;
6. protected/candidate controlled Development performance if reference M07 closes.

### Protected project invocation

Use:

~~~text
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath <reference-demo> \
  -BaselineId M07-Baseline-H1-ProtectedProfile1-<unique-id> \
  -TimeoutSec 28800 \
  -BuildTarget StandaloneOSX
~~~

The protected project's historical `Invoke-M07Build.ps1` must not be invoked for this H1 cycle.

### Retention

Authenticate a fresh checkpoint before cleanup.

Retain/hash-bind the complete current and protected graphs, including early failure transaction evidence, late handoff raw results, lazy-v2 generator/Player evidence, protected outer recovery/authority, old-Player and performance artifacts.

## Failure evidence

For failure/publication retain per process:

- failure binding;
- early transaction capsule;
- early receipt;
- late schema-2 handoff result;
- three post-host raw responses;
- exact PID/command/start time;
- Unity/console logs;
- strict schema-v3 verification.

For lazy retain:

- v2 manifest;
- all four producer commands;
- tool/generator hashes;
- parser receipt;
- lazy fixture;
- diagnostic Player build;
- launch/result/logs.

For protected M07 retain:

- protected verification;
- current coordinator command;
- outer authenticated originals;
- split-authority receipts;
- exact restoration receipt;
- workflow/fixture/ON/OFF/replay outputs;
- post-run clean source/runtime verification.

Keep `Passed`, `PassedFocused`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, `NoCoverage` and historical evidence identities distinct.

## Alternatives

Do not:

- start the failure transaction after host continuation;
- replace the new early transaction with Baseline admission-only;
- weaken terminal startup modes to callback 0;
- add a runtime exception for `BaselineAlreadyUsed`;
- weaken strict early/late process/hash binding;
- accept three-field dense-v2 commands;
- relax v2 generator/parser/historical evidence rules;
- modify the protected project to embed current coordinator policy;
- invoke the protected historical M07 wrapper and then bypass its verifier;
- hand-author old-Player/performance evidence;
- weaken `verify_demo`, `metadata_only`, performance comparability or sampling policy;
- begin R02.

## Risks

- `MetadataFailureContinue` and `InitializerFailureContinue` deliberately continue normal host startup from terminal Shadow failure states only for the dedicated diagnostic matrix. Real Player validation must prove the expected late probe can run without altering terminal state.
- The initializer case publishes a generation before module-initializer failure; post-host persistence must remain `FailedAfterCommit`.
- Protected M07 now depends on candidate coordinator tooling driving historical Unity producers; exact pre/post source verification and outer restoration are mandatory.
- Old-Player/performance remain unavailable if a fresh protected M07 graph cannot be produced.
- All Player/reference/performance outputs are cleanup-sensitive.

## Local correction boundary

Local may adjust:

- absolute worktree paths;
- fresh baseline IDs;
- executable permissions;
- invocation syntax;
- fresh evidence/output directory names;
- bounded environment setup for already pinned runtime installation.

Local must not alter:

- source anchor;
- early failure ownership/mode/callback semantics;
- late probe read-only boundary;
- dense-v2 schema;
- split M07 authority semantics;
- protected commits;
- runtime ABI/capacity/index constants;
- performance protocol/schedule/comparability policy.

Any non-trivial source/tool change returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Fresh mandatory V04 evidence and V05 successor closure are required before a genuine independent whole-chain M08 rerun.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

Human H1 approval must then be explicit.

**Do not begin R02.**
