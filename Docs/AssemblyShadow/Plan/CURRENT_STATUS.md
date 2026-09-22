# Current Status

- Candidate build-input/tool source anchor: `27df1a3d60811dc121f296ab561ae313a382b363`.
- Latest Local return: `421f221156f4e9a71aab3363fd4e49a91cbaba68`.
- Latest authenticated Local checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260922-authority91ac-formal-seal-invalidated/`.
- Reusable retained graph/pilot checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`.
- Gate: `H1 / InProgress / AwaitingGuardV2FormalRestart`.
- Last independent M08: `FAIL` (historical; not rerun).
- Human gate passed: `false`.
- May enter R02: `false`.

## Latest Local result

At source `91ac4db3...`, Local fully closed all earlier authority/admission defects and reached 14/40 passed formal pairs.

Passed in that cycle:

- current/protected authority and installed runtimes;
- bounded Primary 364/364;
- Python inventory 1021 Passed / 28 explicit environment skips / 0 failures-errors;
- exact 9-path and 22-path source audits;
- retained evidence / 33,792-file reauthentication;
- new retained-runner-aware bridge;
- retained-pilot admission preflight;
- strict 8-side pilot seal;
- formal pair 1 current-runner/current-authority gate;
- formal pairs 1–14.

The formal series then became non-resumable under the old seal contract because only filesystem device identity changed for a sealed protected `GameAssembly.dylib`:

- SHA-256 unchanged: `ae75b36f20a8adf323a821ee2f2f585ae0bfc664e8e81063f8b3cc0ec4023b8d`;
- size/inode/mode/mtime/ctime unchanged;
- `st_dev`: `16777229 → 16777230`.

This is a remount/topology change, not content or stable-file mutation.

Local correctly failed closed and did not rewrite/reseal/relabel the partial series.

The same cycle also exposed a pre-launch output-name collision when a fresh batch reused a pair leaf name already preserved in project-local evidence.

## Primary decision

`st_dev` is **not acceptance-critical**.

It identifies the mounted filesystem instance rather than immutable file identity and can change across remounts without changing canonical path, bytes, inode, permissions, size, mtime, or ctime.

Primary keeps all other identity fields fail-closed.

## Current Primary repair

### Cross-remount-stable seal guard v2

New seal metadata:

- `guardKind=CrossRemountStableStatGuard`;
- `guardVersion=2`;
- `guardFields=[inode, mode, size, mtimeNs, ctimeNs]`.

Acceptance identity now consists of:

- canonical path;
- inode;
- mode;
- size;
- mtimeNs;
- ctimeNs.

`st_dev` is excluded from acceptance.

Any accepted field drift still invalidates the seal.

Old device-bound seals do not satisfy guard v2 and are explicitly rejected. Therefore the 14/40 source-91ac series remains historical only.

### Content integrity remains unchanged

The immutable file inventory remains bound to the SHA-256 values captured by the strict pilot launch/input evidence.

Formal admission still:

- re-hashes protocol/schedule/map/launch/tool controls;
- re-derives immutable path/hash inventory;
- checks guard-v2 identity on every sealed file.

No content-hash or graph verification rule was weakened.

### Collision-resistant project output namespace

Internal per-project pair output names now include a 12-hex SHA-256 suffix of the **full canonical requested output path**.

Two new batch roots may therefore contain the same pair ID/attempt leaf while producing different project-local `_temp/AssemblyShadow` side directories.

External evidence roots remain new-only and unchanged.

## Regression coverage

Primary tests prove:

- changing only `st_dev` yields the same acceptance guard;
- inode/mode/size/mtime/ctime mutations each change it;
- guard v2 is recorded in new seals;
- old device-bound guard schema is rejected;
- same pair/attempt leaf under different batch roots gets distinct project-local output paths;
- both preserved outputs can coexist;
- all previous retained-runner/bridge/seal/formal-subprocess/batch/final-analysis regressions remain active.

## Source scope

`91ac4db3... → 27df1a3d...`: exactly **3 non-metadata paths**:

- `Tools/AssemblyShadow/README.md`;
- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`.

`69130bbb... → 27df1a3d...`: still exactly **22 non-metadata paths**.

No Player/runtime/native/Unity asset/measurement/protocol/schedule/graph-production source changed.

## Primary validation

Workflow `35730535436` at `465e97be...` passed:

- bounded Primary: **368/368**;
- live handoff: **11/11**;
- R01 early capsule: **7/7**;
- R01 early launch: **20/20**;
- R01 early results: **20/20**;
- failure pipeline: **16/16**;
- both M07 PowerShell recovery regressions: Passed;
- R01B lazy: **10/10**.

Artifact `10695057616`, SHA-256 `d30e3676419c05fcf22f728aff299823df2129a018efa24c614c539484e356fc`.

## Required next action

Local must create a new current bridge and a new guard-v2 strict seal, then start a **wholly new** formal series from the retained pilot index.

The prior 14 passed formal pairs remain historical evidence and are not chained into the new series because they bind the old seal/source.

Run the retained-pilot admission preflight before the expensive seal.

Then run the normal formal batch. The output-path hash should eliminate the previous preserved-output collision without manual direct-pair workaround.

H1 remains `InProgress`. Do not begin R02.
