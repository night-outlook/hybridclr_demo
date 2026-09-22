# Static Review — Formal Side-B Subprocess Authority

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real formal candidate subprocess execution.

Reviewed source/tool anchor: `f1266a4d7f39a49523186b3dc63f9add9cc0e64c`

## Finding

The prior bridge/seal/admission path was correct, but formal execution crossed a process boundary.

`run-h1-paired-performance.py` validated the bridge and seal in the parent process. It then launched public `run-r00-players.py` with only project/graph input arguments.

The child therefore used its default current-pairing verifier and rejected the retained candidate graph before Player launch.

The two identical Local whole-pair failures prove this is the missing boundary.

## Review of correction

### No generic historical override

The child runner still has no raw revision/source-pin option.

Its retained path accepts only an `H1FormalSideLaunchAuthority` receipt.

That receipt can only authenticate the fixed H1 retained graph through the existing graph bridge policy.

### Exact formal binding

The authority binds:

- side B;
- pairId and attempt;
- mode and AB/BA order;
- exact candidate project;
- exact runner output root;
- protocol and schedule;
- frozen build map;
- bridge and pilot seal;
- exact fixture, ON/OFF receipts, replay;
- current formal-authority/parent-runner/R00/early verifier hashes.

Build-map side B and schedule row are independently rechecked when the authority is created and when the child consumes it.

### Child reauthentication

Before graph preparation, the child:

- validates the authority receipt;
- validates bridge/seal/map/input/tool bindings;
- obtains pairing authority from the same compact bridge verification;
- calls `verify_inputs_with_reuse`.

For ON modes, the exact same authority reaches nested Baseline/Control early preparation.

Without the authority receipt, the original current-pairing path remains unchanged.

### Side isolation

Protected side A is authority-free.

Only formal retained side B receives an authority receipt.

### Parent fail-closed behavior

A real runner launch can pass only if its launch receipt echoes the exact parent-issued authority.

If the child exits before writing an R00 receipt, the parent preserves the original failure and the authority evidence but cannot mark that side Passed.

### Retry / final analysis

Prior formal indexes hash-bind side-B authorities.

A bridge-bound resumed chain requires authority evidence for every non-skipped candidate formal attempt.

Final analysis revalidates every authority with pair/attempt/output/input/bridge/seal/tool identity and requires side A to have none.

Failed pre-launch attempts are representable without fake launch receipts.

## Regression review

The most important new regression crosses the exact returned boundary:

1. paired driver constructs the actual child command;
2. that argv is passed to actual `run-r00-players.main`;
3. formal authority verification returns the bridge-authenticated pairing;
4. default `verify_inputs` is forced to throw if touched;
5. `verify_inputs_with_reuse` must receive the authority;
6. only the actual Player process is mocked.

Separate receipt tests reject mode, input-hash, and tool-hash tampering.

Analyzer tests cover successful and failed-pre-launch formal authority evidence.

## Scope

`a964f79d... → f1266a4d...`: exactly 11 non-metadata paths.

`69130bbb... → f1266a4d...`: exactly 20 non-metadata paths.

The new retained paths are the formal authority module, public R00 runner modification, and formal authority regression.

No runtime/Player/measurement/Unity asset/native code changed.

## Residual empirical requirements

Local must:

- refresh current installed-runtime source authority;
- verify exact 11/20 path sets;
- reauthenticate retained graph/pilot evidence;
- create a new bridge;
- create a new strict 8-side seal;
- start a new formal series from the retained pilot index;
- prove pair 1 candidate side B creates and consumes the authority, then actually launches a Player;
- complete 40 formal pairs;
- run final strict analysis;
- checkpoint / V05 / independent M08.

The previous a964 attempts remain historical and are not part of the new source series.

H1 remains `InProgress`. Do not begin R02.
