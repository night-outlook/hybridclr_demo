# Primary Implementation → Local Validation

## Objective

Validate the V04 repair batch at candidate build-input source anchor:

`f15b339610c42f340c181bdfffef29bdc4a99ed3`

Then complete as much remaining H1 evidence as safely possible in one Local cycle:

authority/provenance → current M07 → startup/M07 matrix → repaired failure/publication → current capacity/parser/index coverage → deterministic-v2 lazy Player → protected profile-1 reference rebuild → old-Player rejection → controlled A/B Development builds → frozen performance map → preregistered paired performance → retention → V05/M08 only if eligible.

Latest Local return:

`f8e66d092b275173a415776f845182171c4dbc31`

H1 remains `InProgress`.

Historical independent M08 remains `FAIL`; it was not rerun.

`humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine-readable authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Source/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | build-input anchor `f15b339610c42f340c181bdfffef29bdc4a99ed3` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected H1 identities remain:

- reproduction published head: `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`;
- reproduction behavior source: `4e3d2035991ab5629265ac663e61bcb2ca62828b`;
- reproduction tooling: `ba8fee33753a5ebc215b7a98739e343d8e05572e`;
- performance reference demo HEAD: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.

Protected profile-1 reference runtime family:

- demo build-input source anchor: `f1c923cbaa814e1b63f3c5b9f8303c90616de726`;
- HybridCLR: `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity: `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP: `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Environment:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

`ProjectSettings/AssemblyShadowSourcePins.json` and candidate `source-targets.json` both identify source anchor `f15b339...`.

The final checkout HEAD is expected to be a later metadata-only handoff/documentation successor. Record checkout HEAD and source anchor separately.

## Implementation

### Local result being addressed

The fresh `af56b841...` Local batch passed:

- V00-V03 authority/provenance/builds;
- controlled M07;
- normal M07;
- startup11;
- M07 Player 14/14;
- 8192/8193 capacity;
- 512 MiB mixed boundary;
- parser / FieldRVA / deterministic dense-v2;
- generic/index/cache/capability;
- retained M03-M06/R01 native coverage.

It exposed:

1. failure/publication late probe rejected profile-2 patches because of a stale profile-1 equality;
2. lazy Player had `NoCoverage` because its runner only admitted unavailable sealed-v1 dense manifests;
3. old-Player rejection was `Unavailable / NotRun` because no fresh protected profile-1 M07/Player graph existed;
4. controlled performance was `Unavailable / NotRun` because no fresh protected-reference controlled build map existed.

V05/M08 were `NotRun`.

The checkpoint remains:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authorityaf56/`

Do not relabel its statuses.

### Repair 1 — failure/publication profile contract

`R01FailureProbe` no longer contains a separate profile-1 admission rule.

It delegates to the existing fail-closed:

`ShadowPatchMetadataReservation.ValidateIfDeclared`

using the selected patch's complete profile/report/closure and hash-verified DLL bytes.

The validator must return `profileVersion == M07Probe.RuntimeAbiVersion`.

Late reservation uses that validated version.

The early Baseline admission, Control/Q04/initializer transaction semantics, native runtime, recovery semantics, process binding and strict Python oracle are unchanged.

### Repair 2 — deterministic dense-v2 lazy admission

`run-r01b-lazy-player.py` now has explicit independent admission for:

- historical sealed-v1 under its original schema/kind/status only;
- deterministic-v2 under its schema-2 generator/tool/shape/parser contract only.

For v2 it requires, among other invariants:

- `historicalEvidenceReused=false`;
- old v1 hashes remain `UnavailableDoNotRelabel`;
- exact generator/source/Mono/mcs/Cecil hashes;
- two-run reproducibility contract;
- exactly two 1 MiB fixtures;
- exact 4098 TypeDef / 4097 MethodDef rows;
- >64 KiB strings heap;
- expected 4-byte metadata row widths;
- current parser-revalidated identity/MVID/inventory;
- generated fixture-root confinement.

`R01BLazyProbe` independently recognizes v1/v2, rejects v2 historical relabelling, requires exactly IDs 1/2, and enforces the v2 runtime boundary envelope before loading the assemblies.

No lazy allocation/reservation acceptance rule was weakened.

### Protected profile-1 reference preparation

Primary added:

`Tools/AssemblyShadow/verify-h1-protected-reference.py`

It authenticates an isolated reference family against the exact protected four Git commits, source pins, profile-1 source contract, required producers, clean tracked state, and byte-identical performance measurement sources.

It reports only:

`ProtectedReferenceInputsVerifiedNotBuilt`

It does not install/build or claim acceptance.

### Controlled performance build-map preparation

Primary added:

`Tools/AssemblyShadow/freeze-h1-performance-build-map.py`

It accepts actual controlled ON/OFF receipts/evidence from:

- side A = protected profile-1 reference;
- side B = current candidate.

It uses the existing strict `h1_paired_performance` analyzer to authenticate build configuration, source/provenance snapshots, executables, native library/metadata, measurement source snapshots and source pins.

Comparability is **derived from authenticated facts**, not supplied by Local.

The build map is emitted only after `ComparabilityPassed`.

### Primary executable validation

Workflow:

`35355439098`

at source anchor `f15b339...` / authority successor `e8241a621cc0310385bb3f8f2a3b3b7532203908` passed:

- bounded Primary: **316/316**;
- committed handoff: **11/11**;
- R01 early capsule: **7/7**;
- R01 early results: **19/19**;
- R01 failure pipeline: **17/17**;
- R01B lazy contract: **8/8**.

Artifact:

- ID `10551697107`;
- ZIP SHA-256 `2fed1be31722ab8b67435f264d293cf56fe62f68af0ce28f7a5feb4dd437ba0a`.

This is source/tool evidence only.

## Local validation

Detailed executable sequence:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Batch policy

**Hard stop** on:

- candidate source-authority failure;
- reproduction/protected-ref mismatch;
- wrong runtime installation;
- tracked source drift;
- invalid common M07/reference input graph;
- provenance failure that invalidates downstream artifact identity.

After those foundations pass, an isolated fresh-process functional failure does not automatically terminate the batch.

Preserve it, then continue other independent cells when they still use authenticated unchanged common inputs.

A failed prerequisite must never be promoted to acceptance.

### Required current-candidate sequence

At minimum:

1. fresh V00;
2. V01 Unity/tests;
3. V02/V03 current candidate/reproduction provenance/builds;
4. controlled + normal current M07;
5. startup11;
6. M07 14/14;
7. repaired failure/publication matrix;
8. current capacity/mixed/parser/index/retained coverage;
9. fresh deterministic dense-v2;
10. fresh lazy fixture;
11. fresh R01B diagnostic Player;
12. repaired lazy Player.

### Required protected-reference sequence

If reference setup is possible in the real environment:

1. create an isolated reference worktree family at the exact protected commits;
2. run `verify-h1-protected-reference.py`;
3. install the reference's own profile-1 runtime only into the reference project;
4. require the reference project's own `verify-installed-runtime.py`;
5. run its own M07 workflow and retain fresh profile-1 fixture/ON/OFF/replay evidence;
6. run current `run-r01b-old-player-rejection.py` using fresh current profile-2 + fresh reference profile-1 graphs;
7. produce fresh controlled Development ON/OFF builds on both reference and candidate through each project's own `R00ControlledBuild`;
8. freeze the map using `freeze-h1-performance-build-map.py`;
9. require `ComparabilityPassed`;
10. bind the preregistered protocol/schedule into a fresh evidence root with `bind-h1-performance-preregistration.py` and require its integrity receipt;
11. run the bound preregistered performance pilot/formal protocol and retain all attempts.

Do not reconstruct old Player or performance receipts from historical summaries.

### Retention

Before any cleanup, authenticate a new Local checkpoint containing or hash-binding all fresh candidate and reference artifacts described by the detailed task file.

Only then consider V05.

## Failure evidence

For failure/publication retain, per mode:

- early binding/capsule/result;
- late result and raw responses;
- exact patch profile/report/manifest;
- exact command/PID/start;
- console/Unity logs;
- strict verifier output.

For lazy retain:

- deterministic-v2 manifest;
- generator/tool hashes;
- both fixture hashes;
- parser/native dense receipt;
- lazy fixture receipt;
- diagnostic Player build receipt;
- lazy launch/result/logs;
- strict result verification.

For protected reference retain:

- exact four Git HEADs;
- source pins;
- protected-reference verification output;
- installed-runtime receipt/inventory;
- reference M07 workflow/fixture/ON/OFF/replay;
- old-Player launch/result/logs.

For performance retain:

- both sides' controlled ON/OFF build receipts/evidence;
- frozen build map + freeze receipt;
- protocol/schedule hashes;
- every pilot/formal attempt;
- final analysis.

Keep `Passed`, `PassedFocused`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, `NoCoverage`, and historical/reused evidence distinct.

## Alternatives

Do not:

- replace the shared profile validator with a hard-coded profile-2 acceptance;
- bypass earliest-startup admission;
- weaken the failure/publication strict verifier;
- relabel sealed-v1 dense evidence;
- accept arbitrary schema-2 dense JSON without generator/parser bindings;
- hand-author performance comparability claims or sampling schedules;
- reuse normal M07 Players as controlled Development performance Players;
- reconstruct historical old-Player or performance receipts;
- move protected branches/commits;
- broaden `metadata_only`;
- weaken `verify_demo`;
- begin R02.

If protected reference installation/build cannot be completed, retain `Unavailable` with the exact blocker and continue other independent current-candidate cells.

## Risks

- The repaired failure probe has Primary source/contract coverage but still requires real IL2CPP execution of all three late oracles.
- The lazy v2 path has Primary manifest/runtime-contract coverage but still requires a fresh diagnostic Player and real dense assembly execution.
- Reference runtime installation is intentionally not automated by a new Primary installer; it must use the already-established project-local HybridCLR installation flow and then pass the protected project's own runtime verifier.
- Controlled performance requires four fresh Development C++ Release Players. Normal M07 production Players are not substitutes.
- The performance formal phase can be lengthy; all invalid/retry attempts must be retained under the preregistered policy.
- Candidate and reference artifacts are cleanup-sensitive. Checkpoint them before deleting or regenerating working directories.

## Local correction boundary

Local may correct:

- machine-specific absolute paths;
- worktree locations;
- executable permissions;
- invocation syntax;
- fresh output/evidence directory names;
- bounded environment setup needed to install an already pinned runtime into its isolated project.

Local must not change:

- source anchor;
- required handoff headings;
- source/verifier policy;
- profile admission semantics;
- dense v1/v2 evidence identities;
- failure/runtime transaction semantics;
- capacity/index constants;
- protected commits;
- performance protocol, schedule, comparability rules or outlier policy.

Any non-trivial source/tool fix returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Mandatory fresh current/reference V04 evidence and V05 successor closure are required before a genuine independent whole-chain M08 rerun.

Only genuine whole-chain **M08 PASS** may make H1 **Ready for Human Review Gate**.

Human H1 approval must then be explicit.

**Do not begin R02.**
