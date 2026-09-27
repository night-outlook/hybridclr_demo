# Historical H1 positive fixtures after R02 source evolution

The first build-repair candidate `6b2bcedfedee17fcbf9db126a6d89ceee61071cb` passed R02 CI run `36305925182`, but the separate old H1 CI run `36305925190` failed with 381 Passed and six Errors. These results remain unchanged; it would be incorrect to describe that candidate as all-CI-green.

Five positive graph/reanalysis tests read current HEAD or current native pins and assume the live repository is still the exact H1 analysis-only successor. The sixth positive test assumes WEB_TO_LOCAL is still the H1 handoff schema. R02 intentionally changes native source and executable demo files and publishes a different handoff. The production H1 verifiers correctly reject those inputs. Broadening old allowlists, rewriting historic pins, treating errors as passes, or deleting all legacy tests would be wrong.

`Tools/AssemblyShadow/R02/legacy_scope.py` separates the original 387 case IDs without omissions or overlap. The 381 reusable contracts execute against current source. The six listed positive tests execute in a disposable Git fixture at accepted H1 checkpoint `2cbf68658a5b73189930fcdfe250835b72639515`. Twelve direct test/policy inputs must match exact committed current and fixture bytes; drift fails before fixture use. No old Player evidence is reused and no real handoff is accepted through the fixture.

Three additional current-source negative tests require R02 rejection by the unchanged H1 analysis-only transition, retained-graph transition, and handoff-schema contracts. Thus expected scopes are 384 current tests (381 existing plus three new negatives) and six separately labelled fixed-H1 positives. Inventory changes, missing/duplicate case IDs, unknown scope, missing fixture history or policy-byte differences fail; no generic skip or optional fallback exists.

The old original test files, H1 production verifiers, historical evidence, native pins, and R02 functional/performance runners remain unchanged. Only the CI scope adapter, its tests, and legacy workflow change. The remaining current R01 early/failure, M07 PowerShell recovery and lazy tests continue to run. This is a test-fixture migration, not an H1 reapproval or R02 runtime acceptance. The prior failed job/artifact must remain visible in the validation record.

## Follow-up fixture checkout repair

CI run `36306463415` proved the current scope separately (`384/384 Passed`) but the fixed-H1 positive phase did not execute: the disposable `git clone --no-checkout` already created local branch `codex/assembly-shadow-r01b-h1`, so `git checkout -b` exited 128 because that local branch already existed. The workflow now uses `git checkout -B codex/assembly-shadow-r01b-h1 2cbf68658a5b73189930fcdfe250835b72639515` inside that disposable clone. This changes fixture construction only; the six pinned positive IDs, fixed checkpoint, H1 verifiers, Player source, and runtime pins remain unchanged.
