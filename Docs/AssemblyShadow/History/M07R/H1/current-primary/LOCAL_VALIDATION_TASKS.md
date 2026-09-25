# Local Validation Tasks — M08 Evidence Closure Re-Review

## Authority

Source anchor remains:

`0388479f7073289e3505b992956a7cbe78c302ce`

Latest Local return:

`7be042c6a6b1a73e907a53bcea10a4d1a3b50c03`

Latest V05/M08 checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-v05-m08/`

Primary evidence closure:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/m08-evidence-closure-20260925/`

H1 remains `InProgress`. Do not begin R02.

## Goal

Authenticate the three M08 evidence closures and rerun genuinely independent M08 in one cycle.

If source anchor → final handoff HEAD contains **zero non-metadata paths**, do not rerun V01, V02, V04, V05, Unity, or Players. Reuse the already authenticated source-038 V05 package and validate only the new metadata/evidence closure.

If any non-metadata drift exists, stop and return to Primary instead of silently widening this task.

## E00 — source/handoff preflight

1. Pull exact final pushed handoff HEAD.
2. Verify branch and four remote heads.
3. Require demo source pin remains `0388479f7073289e3505b992956a7cbe78c302ce`.
4. Require `0388479f... → checkout HEAD` has zero non-metadata paths under unchanged `shadow_tools.metadata_only`.
5. Run committed handoff preflight and require `SourceTargetVerifiedNotBuildAccepted`.
6. Confirm existing source-038 V05 evidence/checkpoint SHAs remain unchanged:
   - V05 SHA `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f`;
   - prior final Local checkpoint manifest SHA `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10`.

## E01 — authenticate recovered prior-review history

Read:

`m08-evidence-closure-20260925/origin-index.json`

For every listed row:

1. compare current copy bytes to:
   `git show 7cb710fa38464b1977a69619fea2b5fc93f79966:<originPath>`;
2. require exact byte equality;
3. require current Git blob equals the listed `originGitBlob`;
4. record path, origin path, origin commit, blob and byte-equality result.

Special historical Handoff reconstruction:

- current copy:
  `manifest-reconstruction/authority925e-LOCAL_VALIDATION.md`;
- origin:
  commit `075f8a25f44b7fe5fef397be566b8a5f4f7e447f`,
  path `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`;
- require exact byte equality;
- require SHA-256:
  `cb8f06d757962ddd366878543b2bb75aade49f8b27b165cf7d9eb984652a3d54`.

Create:

`E01/recovered-origin-authentication.json`

No original historical record may be edited.

## E02 — historical checkpoint successor authentication

Read:

`m08-evidence-closure-20260925/historical-manifest-successor-index.json`

### 925e

Authenticate:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority925e/MANIFEST.sha256`

Use normal current checkpoint paths for 292 members and substitute only the reconstructed historical Handoff bytes for the external relative Handoff member.

Require:

- all 292 retained members exact;
- reconstructed Handoff exact expected SHA;
- effective successor authentication = 293/293;
- original manifest itself remains unchanged.

### 6913

Authenticate all 29 available entries in:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/MANIFEST.sha256`

For missing:

`V04/performance/formal-01-prelaunch-operational-blocker.log`

require:

- expected manifest SHA =
  `8d899ad7f910dbf6c2eef903f735fb343e67c5124e45b22796f43d41f0aec0ae`;
- file absent from current checkpoint;
- file absent from Git tree at checkpoint creation commit
  `fa23a0ddcf45eabc870e7e7742d2d18a78a52d49`;
- classification =
  `ExcludedUnavailableSupersededDiagnostic`;
- it is not used by a selected current H1 claim.

Then reauthenticate superseding source-27df formal evidence:

- source-27df checkpoint 92/92;
- formal batch SHA `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`;
- final sample SHA `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`;
- formal pairs 40/40;
- current source-038 V04 reanalysis remains `Passed / ComparabilityPassed`.

Create:

`E02/historical-checkpoint-successor-authentication.json`

Required kind/status:

- `kind=H1HistoricalCheckpointSuccessorAuthentication`;
- `status=AuthenticatedWithExplicitHistoricalExclusion`.

Do not claim the original 6913 manifest itself passed 30/30.

## E03 — prior M08 finding successor audit

Read:

- recovered original M08 review;
- recovered original finding closure;
- `prior-finding-successor-map.json`;
- recovered 12cf successor records.

Verify independently:

### COUNT

- 12cf results record candidate count 132/132;
- V03 provenance summary has exactly six fresh provenance-bound builds:
  four candidate + two reproduction;
- every build has native Passed, managed SourceGraphBound and tooling binding.

### FRESH-STARTUP

- 925e checkpoint records fresh startup11 / 11 fresh PIDs;
- key startup launch/result hashes match the bridge/index;
- later 3168 reuse catalog identifies startup11 as `ReusedAuditedFrom925e`, not Fresh at the successor.

### UNFIXED-REPRO

- eight cells present;
- 6 `UnexpectedAccepted`;
- 2 Debug `AssertAbort`;
- every cell `inputsUnchanged=true`;
- Debug cells use receipt SHA
  `505249186b7aab356e25b11b95750e3122350afd687d45fa82bc72ac3451a9d0`;
- Release cells use receipt SHA
  `f6bc036b3bd4ed1c6c236cbee3b76c4c225ddabc273d792d977d0382203487ea`;
- those hashes exactly equal reproduction build hashes in recovered V03 provenance;
- `candidateAcceptance=false`.

Create:

`E03/prior-finding-successor-authentication.json`

Do not change the original M08 FAIL; this receipt only supplies evidence for re-review.

## E04 — whole-H1 suite reuse authentication

Read:

`whole-h1-suite-reuse-bridge.json`

Independently recompute Git-tree comparisons.

Require 925e → source 038:

- Bootstrap: 70 blobs, 0 changed;
- R01B diagnostics Runtime: 16 blobs, 0 changed;
- H1 count-related files: 42, 0 changed;
- selected failure runner/verifier files: 3, 0 changed;
- selected capacity runner/verifier files: 3, 0 changed;
- only changed Assets files are Editor provenance/test files;
- only changed ProjectSettings file is source-pin authority;
- hybridclr / hybridclr_unity / il2cpp_plus pins exactly unchanged.

Review the post-925e build-side commits listed by the bridge. Confirm their scope is orchestration/restoration/provenance verification or Editor test code, not Player-managed runtime source/compiler-feature policy.

Authenticate the prior 3168:

- `reused-audit-catalog.json`;
- `V01A/source-scope-audit.json`;

and require `ReusedAuditedFrom925e` semantics are preserved.

For every suite in the bridge:

- authenticate listed checkpoint/index/key hashes;
- classify independently as:
  - `AcceptedReusedAudited`,
  - `Rejected`, or
  - `Blocked`;
- retain reason and exact evidence bindings.

Required suites:

- count-chain;
- startup11;
- failure-publication-recovery;
- ordinary-capacity;
- mixed-capacity;
- m07-and-native-regression.

Create:

`E04/whole-h1-suite-reuse-authentication.json`

with:

`kind=H1WholeChainSuiteReuseAuthentication`

Do not return a single blanket PASS. Every suite needs its own disposition.

If any required suite is Rejected/Blocked, stop and return to Primary before M08.

## E05 — independent M08 re-review

Prerequisites:

- E01 PASS;
- E02 authenticated successor result;
- E03 authenticated successor evidence;
- all E04 required suites = `AcceptedReusedAudited`.

Use established read-only reviewer:

`.codex/agents/code-gate-reviewer.toml`

Gate:

`MILESTONE`

The review package must include:

1. canonical H1 gate/evidence/validation/performance docs;
2. source-038 V05 evidence and pre-V05 closure;
3. latest BLOCKED independent M08 review verbatim;
4. complete `m08-evidence-closure-20260925/` bundle;
5. E01–E04 Local authentication receipts;
6. source-27df execution checkpoint;
7. current source diff / source authority;
8. full V04 performance analysis, including unfavorable measurements.

Reviewer must explicitly revisit the three previous BLOCKED findings.

Allowed verdicts:

- PASS;
- FAIL;
- BLOCKED.

Retain review verbatim and create a machine receipt binding reviewer config, source, V05 SHA, closure package/receipts and verdict.

### PASS

Mark only:

`ReadyForHumanReviewGate`

Keep:

- `humanGatePassed=false`;
- `mayEnterR02=false`.

Stop for explicit human H1 approval.

### FAIL / BLOCKED

Return exact independent findings to Primary.

## Final checkpoint

Create a new immutable Local checkpoint containing:

- E00–E05 evidence;
- prior V05 reference;
- closure bundle reference;
- final Local handoff snapshots;
- manifest.

Do not modify historical checkpoints.

## Local correction boundary

Local may create receipts, temporary Git-materializations, SHA inventories and review outputs.

Local must not modify:

- source;
- source pins;
- recovered historical evidence;
- original historical manifests;
- V05 evidence;
- performance values;
- independent reviewer verdict.

**Do not rerun Players. Do not begin R02.**
