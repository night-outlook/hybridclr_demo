# R01B H1 — Current Primary Implementation

## Status

Latest Local return: `d18a1fb15c43f918c9d3bba1ed641e87a58b32b0`

Candidate source/tool anchor: `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

## Returned blocker

The prior nested early-authority repair is empirically closed.

Local created a valid bridge, passed all three retained-ON early modes, and passed the full 8-side strict seal.

The first formal pair then exposed a separate subprocess authority boundary.

The parent formal driver had bridge/seal authority, but child `run-r00-players.py` started as a fresh process with only graph input paths. It called default current-pairing `verify_inputs`, so candidate side B failed before Player launch.

The entire pair was explicitly retried per protocol and reproduced exactly.

## Primary design

### Pair-specific subprocess authority

New `h1_formal_launch_authority.py` defines `H1FormalSideLaunchAuthority`.

The paired driver creates it only for retained candidate side B in formal phase.

The receipt binds pair identity, attempt number, mode/order, project, exact runner output root, protocol/schedule/map, bridge, seal, fixture/on/off/replay inputs, and current tool hashes.

It is not a general historical-pairing token.

### Public runner contract

`run-r00-players.py` remains current-pairing-only by default.

The only retained path is the H1-specific `--h1-formal-launch-authority` receipt.

The child validates the receipt and reconstructs authority from the same graph bridge. It never accepts a raw revision or caller-supplied source-pin DTO.

The retained path uses `verify_inputs_with_reuse`; ON modes pass the same authority through nested Baseline/Control early preparation.

### Protected side

Side A never receives a retained authority.

Parent diagnostics and final analysis reject any retained authority on protected side A.

### Evidence chain

For candidate side B:

- parent attempt records the authority binding;
- child R00 launch receipt must echo it;
- parent requires the echo before Passed;
- retries retain separate authority receipts;
- failed pre-launch attempts preserve authority evidence without fabricating an R00 launch;
- final analyzer revalidates pair/attempt/output/input/bridge/seal/tool bindings.

### Replay protection

Each authority binds the exact R00 output root.

The child validates it before output creation; final analysis validates the same path after it exists.

## Regression coverage

Primary includes:

- authority receipt binding and tamper rejection;
- exact parent `build_command → run-r00-players.main → verify_inputs_with_reuse` boundary regression;
- default `verify_inputs` is forbidden in the authorized candidate-side test;
- direct runner without authority remains current-pairing-only;
- parent runner-receipt authority echo requirement;
- resumed formal side-B authority binding;
- final-analysis authority verification;
- failed pre-launch authority evidence without an R00 receipt;
- all previous bridge/preflight/seal/cache/formal-batch regressions.

## Scope

Previous source delta: exactly 11 non-metadata paths.

Full retained graph delta: exactly 20 non-metadata paths.

No Player/runtime/native/Unity asset/measurement/protocol/schedule/graph-production source changed.

## Primary validation

Authority-updated workflow `35673645036` passed **358/358** bounded Primary tests plus all existing live handoff/R01/M07 recovery/lazy suites. Artifact `10672720137`, SHA-256 `3d2c82e8972776945efe92dbee5efb70e451088ee37bbe11cfa087221d690a8f`.

## Next Local cycle

Fresh source/runtime authority and Python tooling checks occur before bridge creation.

Unity 1076/1076 from d18 may be classified `ReusedAuditedFromD18` after the exact 11-path audit because no Unity C#/asmdef/resource input changed; a fresh run remains optional before bridge creation.

Then:

1. new graph bridge;
2. new 8-side strict seal;
3. new formal series from retained pilot index;
4. inspect pair 1 side-B formal authority and real Player launch;
5. continue all 40 pairs if successful;
6. final bridge-aware analysis;
7. checkpoint / V05 / independent M08 if eligible.

The old a964 bridge, seal, preflight, and two failed formal attempts remain historical evidence.

Do not begin R02.
