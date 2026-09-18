# Local Validation → Primary Implementation

## Blocker 1: candidate build inputs are outside the committed source anchor

### Symptom

At clean candidate HEAD `7e91c42d7baf1d9045d3fd924b7ad2d176f599e9`, implementation anchor `8b1298d6a5979928bdfa30446e2d674d63999b76` is present and the four repository pins match the handoff. The authoritative candidate preflight nevertheless fails before Unity:

```text
Blocked: Demo HEAD contains build-input changes after the source pin
```

`ProjectSettings/AssemblyShadowSourcePins.json` and `source-targets.json` still identify `68df00fe31a199491b313cc17f25575663b7452b`, while the repaired `m05_types.py`, dense generator, native dense harness, parser launcher, and focused tests are later build inputs.

### Root cause and impact

Primary published a new implementation anchor but did not advance the candidate source-authority contract. The generic source verifier is correctly fail-closed. Fresh Unity, capsule/Player, V04 downstream, successor packaging, and M08 cannot form a provenance-bound chain from the current handoff.

### Recommended implementation direction

Primary should bind the reviewed candidate source target and demo source pin to the intended MethodPtr/dense implementation anchor (or a reviewed successor), update all source-authority hashes consistently, and run the strict preflight before returning the branch. Do not relax `verify_demo`, add a path exception, or classify these code files as metadata-only.

### Validation still required

After the authority repair, rerun candidate preflight, regenerate current M07 fixture/build/replay receipts, and resume the blocked capsule/startup11 and V04 downstream chain. Focused results from this cycle remain evidence for the exact retained inputs only.

## Blocker 2: current capsule/startup receipts were not retained

### Symptom

The retained fresh Bootstrap DLL and full PlayerInputs snapshot are present and pass the repaired compiled+linked raw-admission verifier. The exact `m07-fixtures.json`, Native ON/OFF `m07-player-build.json`, and `m07-editor-replay.json` paths recorded by the prior workflow were removed during workspace consolidation. Capsule generation and startup11 therefore cannot be invoked without fabricating or relabelling inputs.

### Root cause and impact

Consolidation retained the baseline assemblies and summarized workflow evidence but not the complete authenticated launch contract. This independently prevents the requested capsule/startup11 proof even though the MethodPtr verifier now accepts the real 1,675-row permutation.

### Recommended implementation direction

After repairing candidate source authority, regenerate a fresh normal M07 chain and retain its fixture, ON/OFF build, replay, failure-fixture, and negative-input receipts as one provenance-bound set. Do not reconstruct acceptance receipts from summaries or historical paths.

## Closed focused findings

- MethodPtr verifier: `PassedFocused`; malformed zero, duplicate, out-of-range, count-mismatch, truncated, and mixed pointer-table cases remain fail-closed in the 113-test M05 run.
- Real Bootstrap raw lookup: `PassedFocused`; all five method witnesses resolve through pointer indirection and match configured hashes.
- Dense replacement: `Passed`; fresh deterministic v2 fixtures and native parser/sanitizer validation pass. Historical sealed-v1 evidence remains `UnavailableDoNotRelabel`.

## Current gate state

H1 is `InProgress`. Whole-chain M08 is still `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Return the authority and receipt-retention issues to Primary. Do not begin R02.
