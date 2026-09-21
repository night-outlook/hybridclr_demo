# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `fa23a0ddcf45eabc870e7e7742d2d18a78a52d49`.

Candidate build-input source anchor: `01cdd033665400eba9fa0533fe17c12f9da92746`.

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Local result received

The latest Local cycle successfully completed both controlled Native ON/OFF graphs, exact stage restoration, nested native provenance, old-Player rejection, strict A/B map freeze, unchanged preregistration, and all four pilots.

Formal sampling was operationally blocked before formal pair 1 launched because every driver invocation reconstructed and re-hashed all eight pilot side graphs. One such precondition remained active for 47:39.

## Primary implementation

The formal admission path now has an explicit two-stage contract.

### 1. Strict pilot seal

`Tools/AssemblyShadow/seal-h1-pilot-verification.py` accepts the bound protocol/schedule/map and the completed pilot index.

It:

1. selects the latest retained successful attempt for each of the four pilot modes;
2. derives every launch receipt's complete immutable `inputHashesBefore == inputHashesAfter` inventory plus result/early evidence;
3. snapshots filesystem identity for the union of those files;
4. runs the unchanged deep `r00_results.verify_suite` reconstruction for all eight pilot side launches;
5. requires filesystem identity to be identical after verification;
6. binds all verifier/tool implementations and control artifacts;
7. writes `H1PilotVerificationReceipt`.

### 2. Formal admission

Every formal invocation now requires `--pilot-verification-receipt`.

It verifies:

- exact protocol/schedule/build-map hashes;
- exact pilot-attempt subset and selected launch-receipt bindings;
- current verifier/tool hashes;
- current launch-derived immutable path/hash inventory;
- canonical file identity guard: device, inode, mode, size, mtimeNs, ctimeNs.

A mismatch fails closed. Formal admission does not silently deep-rescan or regenerate the seal.

The produced formal sample index carries the same pilot-verification binding so the cumulative chain cannot switch seals.

## Regression coverage

`test_h1_paired_driver.py` now verifies that:

- seal creation executes exactly eight deep launch reconstructions;
- forty formal admissions reuse the seal with zero calls to the deep R00 verifier;
- pilot launch-receipt mutation is rejected;
- bound graph-file mutation is rejected;
- protocol mutation is rejected;
- schedule mutation is rejected;
- build-map mutation is rejected;
- verifier implementation mutation is rejected.

The paired-driver tests are now part of the bounded Primary suite.

## Scope

Executable/tool changes relative to `69130bbb...` are limited to:

- `Tools/AssemblyShadow/run-h1-paired-performance.py`;
- `Tools/AssemblyShadow/seal-h1-pilot-verification.py`;
- `Tools/AssemblyShadow/tests/test_h1_paired_driver.py`;
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`;
- `.github/workflows/h1-bee-primary.yml`.

No Player source, HybridCLR native, HybridCLR Unity, IL2CPP, `run-r00-players.py`, `r00_results.py`, performance protocol JSON, schedule JSON, map freezer, preregistration binder, timing/statistics, or final analyzer changed.

Therefore the retained controlled graphs/map/preregistration/pilots are eligible for audited reuse only after Local independently proves that exact scope and re-verifies their bound hashes.

## Gate

Mandatory formal samples and final analysis remain absent. V05/M08 remain ineligible until those close and the generated-prerequisite inventory nonpasses are resolved/re-executed.

Do not begin R02.
