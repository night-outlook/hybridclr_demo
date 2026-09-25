# Primary Implementation → Local Validation

## Objective

Authenticate the Primary M08 evidence-closure package and rerun genuinely independent H1 M08.

Source anchor remains:

`0388479f7073289e3505b992956a7cbe78c302ce`

Latest Local return:

`7be042c6a6b1a73e907a53bcea10a4d1a3b50c03`

Do not rerun Players. Do not begin R02.

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Required runtime/package/native identities remain:

- hybridclr: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- hybridclr_unity: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- il2cpp_plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`

The final demo HEAD may be later than source 038 only by paths classified as metadata under unchanged `shadow_tools.metadata_only`.

Existing source-038 V05 evidence remains authoritative if that condition holds:

- V05 SHA-256: `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f`
- latest prior Local checkpoint manifest SHA-256:
  `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10`

## Implementation

Latest independent M08 returned `BLOCKED`, not FAIL/PASS, on three evidence-package gaps.

Primary addressed all three without executable source changes.

Closure root:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/m08-evidence-closure-20260925/`

### 1. Prior independent-review provenance

Recovered from immutable commit:

`7cb710fa38464b1977a69619fea2b5fc93f79966`

The closure includes the original:

- M08 whole-chain FAIL;
- finding-closure ledger;
- reproduction follow-up review;
- review-gates/findings/status records;
- startup attempt/root cause;
- later 12cf finding-closure evidence.

`origin-index.json` records origin path and Git blob for every copy.

Primary checked all 12 recovered files: every current Git blob ID exactly equals its historical origin blob ID.

The historical verdicts are unchanged.

### 2. Prior M08 P1 successor evidence

`prior-finding-successor-map.json` binds:

- `M08-P1-COUNT-CHAIN` → later 12cf six-build provenance + candidate count 132/132;
- `M08-P1-FRESH-STARTUP` → 925e fresh startup11 / 11 fresh PIDs;
- `M08-P1-UNFIXED-REPRO` → later 12cf eight-cell execution directly bound to provenance-verified reproduction Debug/Release receipts.

Reproduction remains historical defect evidence:

- 6 `UnexpectedAccepted`;
- 2 Debug `AssertAbort`;
- `candidateAcceptance=false`.

### 3. Historical manifest successor index

`historical-manifest-successor-index.json` preserves both historical discrepancies.

925e:

- original manifest = 293 entries;
- 292 current checkpoint members remain directly verifiable;
- historical Handoff external binding was recovered from commit
  `075f8a25f44b7fe5fef397be566b8a5f4f7e447f`;
- expected recovered Handoff SHA-256 =
  `cb8f06d757962ddd366878543b2bb75aade49f8b27b165cf7d9eb984652a3d54`;
- target successor authentication = 293/293.

6913:

- original manifest = 30 entries;
- 29 remain available;
- missing
  `V04/performance/formal-01-prelaunch-operational-blocker.log`
  is absent even from creation commit
  `fa23a0ddcf45eabc870e7e7742d2d18a78a52d49`;
- it is classified
  `ExcludedUnavailableSupersededDiagnostic`;
- do not claim original manifest 30/30;
- later source-27df 40/40 formal evidence is the selected superseding execution evidence.

### 4. Whole-H1 suite reuse bridge

`whole-h1-suite-reuse-bridge.json` provides suite-specific source/input/provenance equivalence to source 038.

Exact 925e → 038 Git-tree results:

- Bootstrap runtime: 70 blobs, 0 changed;
- R01B diagnostics Runtime: 16 blobs, 0 changed;
- H1 count-related files: 42, 0 changed;
- selected failure runner/verifier: 3, 0 changed;
- selected capacity runner/verifier: 3, 0 changed;
- hybridclr / hybridclr_unity / il2cpp_plus pins unchanged.

Only changed `Assets/**` paths are Editor-only provenance/test files.

Post-925e M07 build-side changes were reviewed and are limited to:

- controlled-stage recovery labels;
- exact mutable-input backup/restoration;
- nested native-verifier environment scoping;
- Editor test assertions.

Startup verifier changes only add/constrain retained-performance pairing; direct ordinary startup verification remains current-pairing-only.

Selected older suites remain `ReusedAudited`, never Fresh.

## Local validation

Detailed instructions:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

### E00 — source/handoff preflight

Require:

- exact final pushed branch/HEAD;
- source pin remains `0388479f...`;
- source 038 → final HEAD has zero non-metadata paths;
- committed preflight = `SourceTargetVerifiedNotBuildAccepted`;
- existing V05/checkpoint hashes above unchanged.

If non-metadata drift exists, stop and return to Primary.

Do not rerun V01/V02/V04/V05 merely because handoff metadata changed.

### E01 — recovered origin authentication

Authenticate every row in:

`m08-evidence-closure-20260925/origin-index.json`

against `git show` at origin commit/path.

Also require reconstructed 925e Handoff:

- byte-equal to origin commit `075f8a25...`;
- SHA-256 = `cb8f06d757...`.

Create:

`H1RecoveredIndependentReviewAuthentication`

### E02 — historical manifest successor authentication

925e:

- verify 292 retained members;
- verify reconstructed historical Handoff;
- effective successor result 293/293;
- do not edit original manifest.

6913:

- verify 29 available members;
- prove missing log absent at creation commit;
- retain 1 unavailable/excluded member;
- authenticate source-27df 40/40 superseding formal evidence.

Create:

`H1HistoricalCheckpointSuccessorAuthentication`

with status:

`AuthenticatedWithExplicitHistoricalExclusion`.

### E03 — prior finding successor audit

Independently verify the COUNT, FRESH-STARTUP and UNFIXED-REPRO mappings in:

`prior-finding-successor-map.json`

Create:

`H1PriorFindingSuccessorAuthentication`

This does not alter the historical M08 FAIL.

### E04 — whole-H1 suite reuse authentication

Independently recompute source/tool equality and authenticate key evidence for each required suite:

- count-chain;
- startup11;
- failure-publication-recovery;
- ordinary-capacity;
- mixed-capacity;
- m07-and-native-regression.

Every suite must receive one explicit disposition:

- `AcceptedReusedAudited`
- `Rejected`
- `Blocked`

Create:

`H1WholeChainSuiteReuseAuthentication`

Do not emit a blanket PASS.

If any required suite is Rejected/Blocked, stop before M08 and return to Primary.

### E05 — independent M08 re-review

Only after E01–E04 close successfully.

Use:

`.codex/agents/code-gate-reviewer.toml`

in a genuinely independent read-only context.

Gate:

`MILESTONE`

Provide:

- canonical H1 gate/evidence/validation/performance documents;
- source-038 V05 evidence and closure checkpoint;
- previous BLOCKED M08 review verbatim;
- complete M08 evidence-closure package;
- E01–E04 authentication receipts;
- source-27df execution checkpoint;
- full V04 performance analysis.

The reviewer must explicitly revisit all three prior BLOCKED findings.

Allowed verdicts:

- PASS
- FAIL
- BLOCKED

PASS means only:

`ReadyForHumanReviewGate`

Keep:

- `humanGatePassed=false`
- `mayEnterR02=false`

Stop for explicit human H1 approval.

## Failure evidence

If E00 fails, retain exact source delta/preflight and stop.

If E01/E02 fails, retain first mismatching path/blob/hash or unavailable evidence classification.

If E03 fails, retain the finding ID and exact successor binding that failed.

If E04 rejects/blocks a suite, retain that suite's complete source/input/provenance comparison and reason.

If M08 FAIL/BLOCKED, retain the independent review verbatim and machine receipt.

## Alternatives

Do not:

- modify recovered historical JSON;
- rewrite old manifests;
- fabricate the unavailable 6913 log;
- call the 6913 original manifest 30/30;
- relabel reused suites Fresh;
- rerun Players as a shortcut;
- rerun V04/V05 when source is metadata-only;
- self-approve independent M08;
- begin R02.

## Risks

- Some old raw artifacts are live/external rather than Git-packaged; Local must preserve Available/Unavailable distinctions.
- Count finding closure is historical successor evidence, not a fresh source-038 count Player run.
- Reuse bridge acceptance remains an independent-review question even after Local authenticates its facts.
- Performance regressions and higher memory remain visible H1 review inputs.

## Local correction boundary

Local may create authentication receipts, temporary `git show` materializations, hash inventories, successor-index receipts and independent review output.

Local must not modify source, source pins, recovered history, original manifests, V05 evidence, measured performance, or reviewer verdict.

## Human review gate

H1 remains `InProgress`.

Only a new genuine independent M08 PASS may move to:

`ReadyForHumanReviewGate`

Human approval is separate.

Until then:

- `humanGatePassed=false`
- `mayEnterR02=false`

**Do not begin R02.**
