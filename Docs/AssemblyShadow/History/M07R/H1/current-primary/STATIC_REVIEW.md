# Static Review — Cross-Remount Seal Guard v2

## Verdict

**PASS for Primary → Local Validation handoff**, subject to a real guard-v2 seal and fresh formal series.

Reviewed source/tool anchor:

`27df1a3d60811dc121f296ab561ae313a382b363`

## Returned finding

The old seal identity guard included `st_dev`.

Local observed an actual remount where:

- canonical path unchanged;
- SHA-256 unchanged;
- inode unchanged;
- mode unchanged;
- size unchanged;
- mtime unchanged;
- ctime unchanged;
- only `st_dev` changed.

Therefore `st_dev` was measuring filesystem/mount topology rather than immutable artifact identity.

## Review of semantic change

The change removes **only** `st_dev`.

It does not add a hash fallback, stat tolerance, automatic reseal, or cache-miss retry.

The new acceptance guard is:

- inode;
- mode;
- size;
- mtimeNs;
- ctimeNs.

Canonical path remains independently required.

Any mismatch in those fields remains fail-closed.

Immutable content remains SHA-256-bound through the strict pilot evidence and current immutable inventory.

## Explicit schema boundary

New seals carry guard kind/version/field metadata.

Old seals lack guard v2 and are rejected before cached admission.

This prevents reinterpretation of an existing 14-pair series under changed verifier semantics.

## Output collision review

Previous internal project-output identity used only the requested output leaf.

Separate batch roots can legitimately reuse the same pair/attempt leaf, causing a collision with preserved project-local evidence.

The new ID includes SHA-256(full canonical output path), so two external roots map to distinct internal directories.

The external evidence path remains unchanged and new-only.

## Regression review

New tests cover:

- same stat identity with different device;
- every remaining field mutation;
- guard-v2 receipt metadata;
- old schema rejection;
- deterministic full-path output ID;
- actual two-run preserved-project-output coexistence.

Existing formal/pilot/bridge authority suites remain active.

## Scope

`91ac4db3... → 27df1a3d...`: exactly 3 non-metadata paths.

`69130bbb... → 27df1a3d...`: exactly 22 non-metadata paths.

No Player/runtime/native/measurement/Unity build input changed.

## Primary validation

Exact live handoff workflow `35731096138` at `7093ea03...` passed bounded **368/368**, live handoff **11/11**, R01 early capsule **7/7**, early launch **20/20**, early results **20/20**, failure pipeline **16/16**, both M07 recovery regressions, and lazy **10/10**.

Artifact `10695328184` has SHA-256 `e939d91da81895d9dfb5d8d19aa3fc48ff6bc1189ef3bc4528cc00218689f513`.

## Residual empirical requirements

Local must:

- refresh current authority;
- verify exact 3/22 path sets;
- reauthenticate retained evidence;
- create a new bridge;
- run retained-pilot admission preflight;
- create a new guard-v2 strict seal;
- start a new 40-pair formal series;
- prove preserved historical outputs no longer collide;
- complete final strict analysis;
- checkpoint / V05 / independent M08.

H1 remains `InProgress`. Do not begin R02.
