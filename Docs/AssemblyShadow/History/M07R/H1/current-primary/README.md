# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `421f221156f4e9a71aab3363fd4e49a91cbaba68`

Candidate source/tool anchor: `27df1a3d60811dc121f296ab561ae313a382b363`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned blocker

The previous cycle reached 14/40 formal pairs and proved the entire retained-pilot → seal → current formal subprocess chain.

Resume then failed because one sealed file's `st_dev` changed across a remount while SHA-256, canonical path, inode, mode, size, mtime and ctime remained unchanged.

That behavior was fail-closed but made long-running formal series mount-instance-dependent.

A separate first-batch launch also encountered a deterministic internal project-output name already preserved from historical evidence.

## Primary decision

Filesystem device identity is not immutable artifact identity.

`st_dev` is removed from acceptance while all stable stat fields remain strict.

The change is versioned as seal guard v2 so no old seal is silently reinterpreted.

## Guard v2

New acceptance guard:

- inode;
- mode;
- size;
- mtimeNs;
- ctimeNs.

Canonical path remains separately required.

New seals bind:

- `guardKind=CrossRemountStableStatGuard`;
- `guardVersion=2`;
- exact guard field list;
- explicit device-ID exclusion policy.

Old device-bound seals fail the new contract and require resealing.

## Output collision repair

The project-local run ID now combines:

- safe leaf name;
- first 12 hex chars of SHA-256(full canonical requested output path).

A new batch root therefore produces a new project-local side output even when pair ID and attempt are the same as preserved historical evidence.

## Regression coverage

Tests prove:

- `st_dev` drift alone is accepted;
- every remaining stat field remains acceptance-critical;
- old guard schema is rejected;
- same pair leaf under two batch roots persists in distinct project-local directories;
- existing bridge/pilot/formal authority contracts remain unchanged.

## Source scope

Previous Primary delta: exactly 3 non-metadata paths.

Full retained-graph delta remains exactly 22 paths.

## Primary validation

Workflow `35730535436` passed bounded **368/368** plus all live handoff/R01/M07 recovery/lazy suites.

## Next Local cycle

1. fresh authority / current Python;
2. exact 3/22 source audits;
3. retained evidence audit;
4. new graph bridge;
5. retained-pilot admission preflight;
6. new guard-v2 8-side seal;
7. new 40-pair formal series from retained pilot index;
8. final strict analysis;
9. checkpoint / V05 / independent M08 if eligible.

The old 14/40 series remains historical and must not be mixed into the new series.

Do not begin R02.
