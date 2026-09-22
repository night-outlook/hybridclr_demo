# Local Validation → Primary Implementation

## Current blocker: strict seal rejects the authenticated retained pilot runner before bridge use

Fresh Local Validation at checkout `0733534d8112a7a0b1e05bb5d904e945b6ed24cc`, source/tool anchor `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`, passed current/protected authority, current Python validation, exact 11-path and 20-path source audits, and complete retained artifact reauthentication.

The new side-B `H1GraphReuseBridge` passed and binds the current formal-authority and R00 runner implementations. Its SHA-256 is `3962cdd9fbd2d81de2d1f2918bc802c9e6e10151f8ae41ec01d40d388ae76004`.

The mandatory production seal failed immediately:

`Prior A diagnostic runner binding mismatch`

The retained pilot index correctly binds the runner that created it, SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c`; this is exactly the `run-r00-players.py` blob at `69130bbb...` and `a964f79d...`. The current repair changed that runner to `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

### Direct cause

`seal-h1-pilot-verification.py` loads the retained pilot index through `run-h1-paired-performance.py::_load_prior` before it authenticates the supplied bridge. `_load_prior` unconditionally compares every historical pilot diagnostic runner to the current `runner_binding()`. The exact retained pilot provenance is therefore rejected before bridge-aware reconstruction; no strict receipt exists and zero deep sides ran.

This is not retained artifact drift:

- retained V04 manifest: passed;
- Player-artifact manifest: passed;
- latest a964 checkpoint manifest: passed;
- exact live protocol/schedule/map/pilot hashes: unchanged;
- selected launch receipts: 8/8 bound;
- complete file rehash: 33,792 files / 1,606,993,133 bytes / zero mismatches;
- source audits: exact 11-path and 20-path sets;
- new current bridge: passed.

### Required correction

Add a narrowly scoped bridge-aware retained-pilot loader for seal creation. Authenticate the recorded historical runner as the exact retained-anchor runner and authenticate the reviewed bridge transition to the current runner, while preserving:

- current runner binding for every new formal attempt;
- protected side A and direct R00 current-pairing behavior;
- no generic historical runner or pairing override;
- exact bridge/map/protocol/schedule identities;
- tamper rejection for any non-anchor historical hash;
- current final-analysis authority checks.

Add an end-to-end regression through the actual seal entrypoint using a retained-style pilot index whose runner hash is the retained-anchor hash. The positive test must reach eight deep verifications; negative tests must reject missing bridge, wrong anchor hash, wrong path, or bridge switching.

## Independent closure completed

- V00 candidate, reproduction, protected family, and both installed runtimes passed after the sanctioned candidate receipt refresh.
- Bounded Primary passed 359/359; all focused repaired-boundary suites passed.
- Full Python inventory recorded 1,016 passed and 28 explicit environment skips with no failures/errors.
- Prior Unity 1,076/1,076 and retained-ON 3/3 are classified only `ReusedAuditedFromD18` after the exact audit.
- Retained manifests, controls, eight selected launches, and 33,792 bound files reauthenticated.
- A new current-source graph bridge passed.
- No a964 bridge, seal, or failed formal index was reused.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority24a0-pilot-seal-blocked/`.

The new formal series, final analysis, V05, and independent M08 were not run. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
