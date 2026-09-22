# Primary Implementation → Local Validation

## Objective

Validate cross-remount-stable pilot seal guard v2 and collision-resistant internal pair outputs at source/tool anchor:

`27df1a3d60811dc121f296ab561ae313a382b363`

Then complete a wholly new 40-pair formal series and final strict analysis in one Local cycle if every gate passes.

Latest Local return:

`421f221156f4e9a71aab3363fd4e49a91cbaba68`

H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine authority:

`Docs/AssemblyShadow/Handoff/source-targets.json`

Candidate identities:

| Repository | Branch | Build/runtime identity |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Protected profile-1 family remains unchanged.

Environment target:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`

The branch checkout HEAD may be a later metadata-only successor. Record checkout HEAD separately from source/tool anchor.

Latest authenticated blocked checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260922-authority91ac-formal-seal-invalidated/`

Authority-updated Primary validation:

- workflow `35730535436`;
- commit `465e97be2104a963b38caab439f1fcdd49445dd4`;
- bounded Primary **368/368**;
- live handoff **11/11**;
- R01 early capsule **7/7**;
- R01 early launch **20/20**;
- R01 early results **20/20**;
- R01 failure pipeline **16/16**;
- both M07 PowerShell recovery regressions Passed;
- R01B lazy **10/10**;
- artifact `10695057616`;
- artifact SHA-256 `d30e3676419c05fcf22f728aff299823df2129a018efa24c614c539484e356fc`.

This is Primary source/tool evidence only.

## Implementation

### Returned Local finding

At source `91ac4db3...`, Local passed all previously blocked authority/admission boundaries and completed formal pairs 1–14.

Resume later failed before pair 15 because the old seal compared filesystem device identity:

`Pilot verification cache invalidated by changed file identity`

For the affected protected `GameAssembly.dylib`:

- canonical path unchanged;
- SHA-256 unchanged:
  `ae75b36f20a8adf323a821ee2f2f585ae0bfc664e8e81063f8b3cc0ec4023b8d`;
- inode unchanged;
- mode unchanged;
- size unchanged;
- mtime unchanged;
- ctime unchanged;
- only `st_dev` changed:
  `16777229 → 16777230`.

This is filesystem mount-instance drift, not artifact/content drift.

The same cycle also observed a fresh-batch project-local output-name collision with preserved historical evidence because the old internal name was derived only from the pair output leaf.

### Decision — st_dev is not acceptance-critical

Primary classifies `st_dev` as mount/filesystem topology rather than immutable file identity.

It is excluded from acceptance.

No other guard field is relaxed.

### Cross-remount seal guard v2

New seals bind:

- `guardKind=CrossRemountStableStatGuard`;
- `guardVersion=2`;
- `guardFields=[inode, mode, size, mtimeNs, ctimeNs]`.

Canonical path remains separately required.

Acceptance still fails closed on any change to:

- canonical path;
- inode;
- mode;
- size;
- mtimeNs;
- ctimeNs.

The sealed file inventory remains SHA-256-bound by strict pilot launch/input evidence.

Formal admission still re-hashes control receipts/tools and re-derives the immutable path/hash inventory.

Only `st_dev` is excluded.

### Old seals are deliberately incompatible

The 91ac device-bound seal does not satisfy guard v2.

Old seals are rejected rather than reinterpreted.

Therefore the previous 14/40 formal series remains historical only and cannot be chained into the new series.

### Collision-resistant project-local outputs

Internal per-project output naming now derives from:

- safe requested output leaf;
- 12-hex SHA-256 suffix of the **full canonical requested output path**.

A fresh batch root using the same pair ID/attempt therefore produces a different project-local `_temp/AssemblyShadow` path from preserved historical runs.

External evidence roots remain new-only and unchanged in receipts.

### Primary regression coverage

New tests prove:

- two stat records differing only in `st_dev` have identical acceptance guards;
- inode/mode/size/mtime/ctime mutations each change the guard;
- new seals record guard-v2 metadata;
- old device-bound guard schema is rejected;
- output IDs are deterministic for one full path but differ across different batch roots;
- two actual paired runs with identical pair leaf names but different batch parents preserve both project-local outputs without collision.

All existing retained-runner, graph bridge, seal, formal subprocess authority, formal batch, retry, and final-analysis regressions remain active.

## Local validation

Detailed authoritative plan:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

Run it in order.

### Fresh authority and source audits

Before bridge creation:

1. fresh V00 current/protected authority;
2. candidate installed-runtime receipt refresh if required;
3. current bounded/Python tests;
4. exact source audits;
5. retained evidence authentication.

Source deltas:

- `91ac4db3... → 27df1a3d...`: exactly **3** non-metadata paths;
- `69130bbb... → 27df1a3d...`: exactly **22** non-metadata paths.

The 3-path set is:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`.

### Unity evidence

No Unity source/resource input changed.

Historical 1076/1076 may remain only `ReusedAuditedFromD18` after the exact 3-path audit.

### New bridge and retained-pilot admission

Create a new current-source graph bridge.

Then run:

~~~text
python3 Tools/AssemblyShadow/verify-h1-retained-pilot-admission.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --pilot-index <retained-live-pilot-index.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --output <new-retained-pilot-admission.json>
~~~

Require Passed, five retained attempts, four selected pilots, exact historical runner provenance, and zero deep R00 reconstruction.

### Create a new guard-v2 seal

Run the normal strict seal using the new bridge.

Require:

- Passed strict seal;
- 8 deep side verifications;
- guard kind/version/field list exactly as above;
- no per-file `device` acceptance field;
- stable complete inventory.

The previous seal is historical only.

### Start a wholly new formal series

Use the retained pilot index, not any prior formal sample index:

~~~text
python3 Tools/AssemblyShadow/run-h1-formal-batch.py \
  --protocol <bound-protocol> \
  --schedule <bound-schedule> \
  --build-map <retained-live-frozen-build-map.json> \
  --graph-reuse-bridge <new-graph-reuse-bridge.json> \
  --pilot-verification-receipt <new-pilot-verification.json> \
  --prior-index <retained-live-pilot-index.json> \
  --output-root <new-unique-formal-batch-root> \
  --timeout 900
~~~

Do not use the 14/40 historical series as prior input.

### Output-collision acceptance

Pair 1 must run through the batch path without manual direct-pair output adjustment.

Verify project-local A/B outputs:

- include the new full-path hash suffix;
- differ from preserved historical side outputs;
- do not fail with `Per-side output must be new`.

If collision still occurs, stop and return to Primary.

### Formal/current-runner acceptance

All previous constraints remain:

- protected A has no retained authority;
- candidate B uses current runner;
- candidate B uses unique formal launch authority;
- child reaches retained graph preparation and Player launch;
- successful launch receipt echoes authority/bridge/seal/map.

Historical pilot runner provenance must not leak into formal execution.

### Complete 40 pairs

Require `PassedAllFormalPairs` and 40/40 selected formal pairs.

If only `st_dev` changes after a remount while guard-v2 fields remain unchanged, cached admission must continue.

Any accepted guard-field drift must still fail closed.

### Final strict analysis

After 40 pairs complete, run the existing strict analyzer and retain the full result regardless of direction.

Proceed to checkpoint/V05/M08 only when all mandatory V04 evidence is complete.

## Failure evidence

### Guard-v2 admission failure

Retain:

- new seal;
- exact invalidated path;
- sealed/current SHA-256;
- sealed/current inode/mode/size/mtime/ctime;
- current `st_dev` as diagnostic;
- bridge/seal/current source identities.

If only `st_dev` differs and admission still fails, return to Primary.

### Output collision failure

Retain:

- requested full output path;
- derived project-local run ID;
- collided historical path;
- pair/attempt;
- batch receipt/console.

Do not manually bypass another collision.

### Formal failure

Retain the complete whole-pair attempt, formal authority, child logs/receipts, and process cleanup evidence.

## Alternatives

Do not:

- add `st_dev` back into acceptance locally;
- remove inode/mode/size/mtime/ctime from the guard;
- reinterpret the old seal as guard v2;
- rewrite the 14/40 historical series to the new seal;
- chain old formal indexes into the new series;
- manually rename/delete preserved project-local evidence to avoid collisions;
- weaken SHA-256/path verification;
- auto-retry or side-only retry;
- edit protocol/schedule/map/statistics after timings;
- begin R02.

## Risks

- Guard v2 solves only mount-device drift; inode or other stable stat changes remain fail-closed by design.
- A new source requires a new bridge and seal, so the prior 14 passed pairs must be rerun.
- The strict seal and full 40-pair series remain expensive.
- Any further source/tool change invalidates the current bridge/seal.
- Final strict analysis remains intentionally expensive.
- Reused evidence must remain explicitly labelled reused, not fresh.

## Local correction boundary

Local may adjust only absolute paths, new evidence roots, permissions/PYTHONPATH, bounded invocation syntax, and protocol-valid whole-pair retry number.

Local must not change guard-v2 semantics, output-ID derivation, source/runtime pins, graph-reuse policy, bridge/seal/formal authority logic, pair order/retry policy, protocol/schedule/map, or final analyzer.

Any non-trivial source/tool correction returns to Primary.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Still required:

- new bridge;
- admission preflight;
- guard-v2 strict seal;
- new full 40-pair series;
- final analysis;
- checkpoint;
- V05;
- genuinely independent M08.

M08 must explicitly review the `st_dev` decision, guard-v2 schema, historical 14/40 classification, collision-safe output namespace, and the complete new formal series.

Only genuine **M08 PASS** may make H1 **Ready for Human Review Gate**.

**Do not begin R02.**
