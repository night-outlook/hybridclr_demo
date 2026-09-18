# R01B H1 — Current Primary Implementation

## Status

Latest Local return:

`f8e66d092b275173a415776f845182171c4dbc31`

Current reviewed candidate build-input source anchor:

`36173a5b12c74fbc9e5fc56b8d5246b187bce65a`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local findings at `af56b841...`

The previous Local batch successfully established a fresh current-source chain through:

- authority/source preflight;
- Unity compilation;
- candidate/reproduction provenance and build set;
- controlled M07 restoration;
- normal M07 fixture/ON/OFF/replay graph;
- startup11;
- M07 Player 14/14;
- 8192/8193 capacity;
- 512 MiB mixed boundary;
- parser/FieldRVA/dense-v2;
- generic/index/cache/capability;
- retained M03-M06/R01 native coverage.

It then exposed two source/tool defects and two missing reference-artifact families.

### Finding A — failure/publication late probe still profile 1

Earliest Baseline admission succeeded for all three processes and bound the correct PIDs/capsules. The late `R01FailureProbe` then rejected every patch because it required:

`patch.nativeBudgetCapabilityVersion == 1`

The authenticated current M07 patch contract is profile 2.

### Finding B — lazy Player runner accepted only sealed-v1 dense input

The deterministic dense-v2 generator and native parser evidence passed, but `run-r01b-lazy-player.py` required the unavailable historical schema-1 sealed-v1 manifest. The lazy Player never launched.

### Finding C — old-Player evidence unavailable

No immutable profile-1 fixture + Native ON/OFF + replay + Player graph was present in the active workspace.

### Finding D — controlled performance reference build map unavailable

The protected performance-reference commit was exact, but no fresh reference Development Players/controlled build evidence existed to construct the A/B frozen build map.

V05 and M08 therefore remained `NotRun`.

## Repair A — shared profile-2 failure admission

The late failure probe no longer owns a separate metadata-profile policy.

It calls:

`ShadowPatchMetadataReservation.ValidateIfDeclared`

with the exact selected patch:

- native capability version;
- dormant legacy profile/report;
- profile-2 profile/report;
- load order;
- closure names and declared DLL sizes;
- independently confined/hash-verified DLL bytes.

The helper must return a declared profile whose version equals `M07Probe.RuntimeAbiVersion`, and every load-order member must have a verified byte-size entry.

Only then does the late probe call:

`AssemblyShadowRuntime.ReserveMetadataBudget(sizes, budgetProfileVersion)`

The Control/Q04/initializer transaction oracle, earliest Baseline admission, process binding, raw diagnostics/recovery checks, and strict Python verifier are unchanged.

This avoids both the stale profile-1 equality and an ad-hoc `== 2` replacement.

## Repair B — explicit sealed-v1 / deterministic-v2 lazy contract

The Python lazy runner now has two independent admission paths.

### Historical sealed-v1

Accepted only as:

- schema 1;
- kind `R01BWorkloadV3DenseMetadataAdjunct`;
- status `VerifiedSealedV1FixturesOutsideV2Envelope`;
- authenticated source corpus/parser/fixture envelope.

No historical v1 evidence is synthesized or relabelled.

### Deterministic-v2

Accepted only as:

- schema 2;
- kind `R01BDenseAdjunctManifest`;
- status `GeneratedDeterministicDenseV2`;
- evidence identity `replacement-fixtures-require-fresh-native-and-player-evidence`;
- `historicalEvidenceReused=false`;
- exact old-v1 hashes retained as `UnavailableDoNotRelabel`;
- exact generator/source/Mono/mcs/Cecil hashes;
- two-run reproducibility contract;
- two exact 1 MiB fixtures;
- exact 4098 TypeDef / 4097 MethodDef shape;
- >64 KiB strings heap and 4-byte metadata table widths;
- current parser-revalidated identity, MVID, inventory and confinement.

The runtime C# diagnostic probe independently checks the v1/v2 header, rejects v2 historical relabelling, requires exactly fixture IDs `{1,2}`, and applies the v2 boundary envelope before `Assembly.Load`.

The runtime lazy semantics themselves are unchanged.

## Protected profile-1 reference coordination

The protected performance reference is usable as a fresh profile-1 evidence producer.

Reference identities:

- demo HEAD: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- demo build-input source anchor: `f1c923cbaa814e1b63f3c5b9f8303c90616de726`;
- HybridCLR: `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity: `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP: `7967b8c7043904fcae130b294defd5ce7aa897c4`.

The reference still contains:

- profile-1 `ShadowPatchMetadataReservation`;
- the M07 build workflow;
- `R00ControlledBuild`;
- the same performance probe, process-memory implementation and witness bytes as the candidate.

Primary added:

### `verify-h1-protected-reference.py`

Read-only verifier for an isolated reference family. It requires:

- exact four Git heads/origins;
- clean tracked state;
- exact reference source pins;
- profile-1 reservation source contract;
- required M07/performance producers;
- byte-identical measurement sources between reference and candidate.

Result is `ProtectedReferenceInputsVerifiedNotBuilt`; it does not claim installation/build/runtime acceptance.

### `freeze-h1-performance-build-map.py`

Takes actual A/B controlled ON/OFF build receipts and `R00ControlledBuildEvidence`, plus each side's fixture/replay receipts.

It authenticates them using the existing strict `h1_paired_performance` analyzer, derives comparability facts from the verified artifacts, requires `ComparabilityPassed`, and only then emits `H1ControlledBuildMap`.

Local no longer needs to hand-author comparability claims.

## Primary executable validation

GitHub Actions workflow `35355439098` at source anchor `36173a5...` / authority successor `e8241a62...` passed:

- bounded Primary suite: **316/316**;
- committed live-handoff suite: **11/11**;
- R01 early-capsule suite: **7/7**;
- R01 early-results suite: **19/19**;
- R01 failure-pipeline suite: **17/17**;
- R01B lazy-contract suite: **8/8**.

Artifact:

- ID: `10551697107`
- ZIP SHA-256: `2fed1be31722ab8b67435f264d293cf56fe62f68af0ce28f7a5feb4dd437ba0a`

This is source/tool evidence only. Real Unity/IL2CPP validation remains Local work.

## Evidence preservation

The Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authorityaf56/`

remains immutable historical evidence for source anchor `af56b841...`.

Its Passed cells remain valid as historical observations, but they are not current-anchor `36173a5...` acceptance.

The failed failure/publication late-probe evidence and lazy `NoCoverage` evidence must remain under their original status.

The old-Player/performance `Unavailable / NotRun` states must not be replaced by summaries. Only fresh regenerated reference artifacts may close them.

## Next Local cycle

Local restarts from fresh V00 under source anchor `36173a5...`.

The desired one-batch order is:

1. current candidate V00-V03 authority/provenance/builds;
2. current controlled + normal M07;
3. startup11 + M07 14/14;
4. repaired failure/publication matrix;
5. capacity/mixed/parser/dense/current retained cells;
6. fresh deterministic dense-v2 + current diagnostic Player + repaired lazy Player;
7. isolated protected profile-1 reference family authentication;
8. fresh reference M07 graph;
9. old-Player rejection using current profile-2 inputs and fresh reference profile-1 Player graph;
10. fresh controlled Development ON/OFF builds for reference and candidate;
11. freeze/authenticate A/B build map;
12. preregistered paired performance pilot/formal execution if comparability passes;
13. checkpoint retention;
14. V05/M08 only if mandatory evidence is complete.

Authority/provenance/common-input corruption remains a hard stop. After foundations pass, isolated fresh-process functional failures should be preserved while independent cells continue when the authenticated common inputs remain valid.

Do not begin R02.
