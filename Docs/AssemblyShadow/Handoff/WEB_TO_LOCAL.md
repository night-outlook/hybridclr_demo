# Primary Implementation → Local Validation

## Objective

Close the only remaining H1 M08 evidence blocker by executing a fresh source-038 132-cell count matrix with complete Launch/Raw retention, then rerun genuinely independent M08.

Source anchor remains:

`0388479f7073289e3505b992956a7cbe78c302ce`

Latest Local return:

`482d9d5cfe703310e8ea6d980677c73817bad774`

Do not begin R02.

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate runtime identities remain:

- hybridclr: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- hybridclr_unity: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- il2cpp_plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`

Protected reproduction behavior/tooling authority is exactly the `demoTargets.reproduction` contract in machine authority.

The final demo checkout may be later than source 038 only by metadata-classified paths. Require the exact final pushed HEAD from the handoff prompt.

Existing source-038 V05 evidence remains authoritative if source authority passes.

## Implementation

### Returned blocker

Latest Local independently closed:

- prior M08/finding provenance;
- 925e manifest successor authentication;
- 6913 explicit 29+1 historical disposition;
- startup11 reuse;
- failure/publication/recovery reuse;
- ordinary capacity reuse;
- mixed capacity reuse;
- M07/native reuse.

The only blocked suite is count-chain.

The historical 12cf count archive has:

- 132 verifier reports;
- one result index;
- 132 references to launch receipts;
- zero retained launch receipt bytes;
- 132 references to raw results;
- zero retained raw result bytes.

The independent reviewer correctly rejected promotion of that 132/132 summary because the canonical Launch and Raw evidence layers cannot be independently inspected.

### Primary decision

Do not reconstruct nonexistent bytes.

Do not swap current source pins to reuse historical build receipts.

Run a fresh count-only closure at source 038.

Protocol:

`H1CountMatrixClosureSource038-v1`

Authoritative contract:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/COUNT_MATRIX_CLOSURE_CONTRACT.md`

Detailed Local tasks:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

### Player authorization

This handoff newly authorizes only:

**count diagnostic Players required by `H1CountMatrixClosureSource038-v1`.**

Still forbidden as workaround:

- performance/formal Player reruns;
- V04 performance rerun;
- unrelated M07 runtime rerun;
- V05 rerun;
- replaying the five already accepted reused suites.

### Fresh count evidence

Frozen inputs:

- source 038;
- Unity 2022.3.62f2;
- StandaloneOSX / arm64;
- fixture seed 20260925;
- canonical case set `all`;
- 132 cells;
- 120-second per-cell timeout;
- existing strict count build/matrix/verifier tooling.

Build phase uses:

`Tools/AssemblyShadow/h1_count_build_batch_tooling.py --scope all --execute`

It must produce six fresh provenance-bound builds.

The 132 count matrix uses only the four exact candidate tuples:

- candidate/on/Debug;
- candidate/on/Release;
- candidate/off/Debug;
- candidate/off/Release.

The reproduction Debug/Release builds are retained diagnostic provenance only.

### Required Launch/Raw closure

Fresh matrix acceptance requires exactly:

- 132 canonical cells;
- 132 verification reports;
- 132 `H1CountPlayerLaunchReceipt` files;
- 132 semantic raw outcomes;
- 132 unique run IDs;
- zero missing launch/raw files;
- zero duplicate cell IDs;
- zero unexpected build GUIDs;
- all inputs unchanged;
- strict aggregate `H1CountMatrixVerification / Passed / 132`.

The historical 12cf count evidence remains historical and blocked; do not rewrite it.

### Evidence retention

The previous failure was packaging, so complete retention is mandatory.

Seal:

- complete parameter fixture root;
- complete nested fixture root;
- complete build batch output;
- complete matrix output;
- all four selected candidate build roots, including Player/input/provenance bytes;
- aggregate verification.

Create regular-file SHA inventories before archiving.

Use `COPYFILE_DISABLE=1` for macOS tar creation and reject `._` AppleDouble members.

Do not clean live roots before independent M08.

### Fresh closure receipts

Create:

`H1FreshCountMatrixClosureReceipt`

required status:

`PassedFreshSource038CountMatrix`

Then create:

`H1WholeChainSuiteClosureV2`

with:

- count-chain = `FreshCurrentSourceExecution`;
- startup11 = `AcceptedReusedAudited`;
- failure-publication-recovery = `AcceptedReusedAudited`;
- ordinary-capacity = `AcceptedReusedAudited`;
- mixed-capacity = `AcceptedReusedAudited`;
- m07-and-native-regression = `AcceptedReusedAudited`.

Zero required suites may be Blocked/Rejected.

## Local validation

### C00 — authority

Require:

- exact final pushed demo HEAD;
- source pin = 038;
- source 038 → final HEAD has zero non-metadata paths;
- four candidate repository identities exact;
- protected reproduction behavior/tooling identity exact;
- committed preflight = `SourceTargetVerifiedNotBuildAccepted`.

Do not rerun prior suites at C00.

### C01 — fixtures

Generate fresh parameter and nested fixtures with seed **20260925**.

Run their independent audits.

No historical fixture reuse.

### C02 — builds

Run exact `h1_count_build_batch_tooling.py --scope all --execute` command from the detailed task sheet.

Require six fresh builds and strict native/managed provenance.

### C03/C04 — matrix + aggregate

Select the four candidate build receipts by tuple, never list position.

Run fresh 132-cell matrix.

Immediately run `verify-h1-count-matrix.py`.

Any semantic failure returns to Primary.

### C05/C06 — Launch/Raw and sealing

Audit every cell's launch/raw/verifier chain.

Create complete inventories/archives for the matrix, fixtures and four selected candidate build roots.

No cleanup before M08.

### C07 — closure receipts

Require:

- `H1FreshCountMatrixClosureReceipt / PassedFreshSource038CountMatrix`;
- `H1WholeChainSuiteClosureV2`;
- count Fresh;
- five prior suites ReusedAudited;
- zero Blocked/Rejected.

### C08 — independent M08

Only after count closure passes.

Use:

`.codex/agents/code-gate-reviewer.toml`

Gate:

`MILESTONE`

Provide:

- latest BLOCKED independent review;
- fresh count closure;
- strict 132 aggregate;
- complete Launch/Raw audit;
- archive/seal receipts;
- whole-H1 closure V2;
- previous E01–E04 closure receipts;
- source-038 V05 evidence;
- full performance analysis.

Reviewer must explicitly revisit the count Launch/Raw blocker.

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

For fixture/build failure retain exact command, source authority, stdout/stderr, partial outputs and restoration state.

For count-cell failure retain:

- cell ID;
- attempt directory;
- launch receipt if created;
- raw/early result if created;
- verification output;
- build tuple/GUID;
- input before/after state;
- logs.

For aggregate or retention failure retain first missing/mismatched path/hash and complete prior successful cell evidence.

For M08 FAIL/BLOCKED retain independent review verbatim and machine receipt.

## Alternatives

Do not:

- synthesize historical 12cf launch/raw files;
- relabel 12cf count Fresh;
- temporarily replace source-pin bytes to admit historical builds;
- alter count source/tooling;
- rerun unrelated suites;
- suppress failed count attempts;
- package only verifier reports;
- clean live build/matrix roots before M08;
- self-approve independent M08;
- begin R02.

## Risks

- Fresh count closure is a real multi-Player execution and may expose a new semantic defect; such a defect returns to Primary.
- Complete Launch/Raw/build retention can be large; keep large archives outside Git if needed, but commit exact hashes/sizes/inventories and keep bytes available through M08.
- Reproduction builds are diagnostic provenance only and must not be substituted for candidate count acceptance.
- Performance slowdowns and higher RSS remain separate H1 human-review inputs.

## Local correction boundary

Local may:

- choose a new unused run-root suffix;
- resolve the registered reproduction checkout;
- resolve absolute Unity/pwsh paths;
- execute the exact pre-registered tools;
- select candidate build tuples by exact fields;
- create hashes/inventories/archives/receipts;
- use `--resume` only after a documented infrastructure interruption with no semantic count failure;
- run independent M08.

Local must not modify source, source pins, count tools, generated fixture bytes after creation, historical evidence, V05/performance evidence, or reviewer verdict.

## Human review gate

H1 remains `InProgress`.

Only a genuine independent M08 PASS may move to:

`ReadyForHumanReviewGate`

Human approval remains separate.

Until explicit human approval:

- `humanGatePassed=false`
- `mayEnterR02=false`

**Do not begin R02.**
