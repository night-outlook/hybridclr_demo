# Local validation checkpoint — 2026-09-14

**H1 InProgress / technical readiness Blocked. Historical M08 FAIL remains; this run's independent L02/L03 review FAIL. Human approval and R02 remain closed.**

Pulled explicit remote branches first. Candidate demo started at `61aa83854f3df8e51da0554a5362e03649d2bea7`, reproduction demo at `c8d2faffe289efff6f347ad7a571a6ce16c3a6d4`. Restricted fetch refspecs made plain pull misleading; explicit `git pull --ff-only origin <branch>` fetched the requested published heads. See `source-preflight.json` for all worktree paths and exact commits; its status snapshot was taken during validation, not before edits. The original main checkout and historical v7–v11 artifacts were excluded from staging.

## Results

- Candidate and reproduction Unity 2022.3.62f2 Editor compile: Passed, fresh logs retained.
- Witness config: ConfigurationValidatedNotCompiled; real wrapper integration: 8/8 Passed.
- Candidate H1 Python: initial 204/205, corrected 205/205 Passed. The test fixture had already populated fields it asserted were absent; the correction models legacy receipts and asserts unchanged receipt bytes. Runtime verifier behavior was not altered.
- Candidate full Python: corrected 702 identities, 697 Passed, 1 Failed, 3 Error, 1 Skipped. Initial run also retains the corrected fixture failure. Remaining failures are three missing historical M01 inputs and the original M02 parser's sixth-site rejection. Exact IDs and traces are in inventories/logs.
- Candidate Editor: 1047 identities, 1044 Passed, 3 Failed. Both new H1 test classes passed. M01 is missing its historical manifest; M05 layout/R01 initializer fixtures fail Bootstrap ILPP with `Expected a null constant`.
- Reproduction H1 Python: 56/56 Passed; focused H1EvidenceProcess Editor test result is recorded in `repro-editor-inventory.json`.
- Full installed-runtime check: Failed because current demo build inputs differ from the historical configured pin. Native-only inspection: Passed, 955 source/957 installed files, `demoSourceVerified=false`; not acceptance. The empty `installed-runtime.json` preserves an initial CLI invocation error (the script already inserts `verify`, so explicitly passing it produced `unrecognized arguments: verify`). The subsequent check used the correct invocation. `installed-runtime-check.json` contains the tool's plain-text failure, not JSON.
- Fresh Player builds, count/repro/startup11, successor package and whole-chain M08: NotRun, blocked by prerequisite compilation/integration/source-freeze work. No prior evidence is promoted.

Only narrow changes were made: correct the sidecar test fixture and document the required managed-provenance build wrapper. Larger implementation is in [REMAINING_WORK.md](REMAINING_WORK.md). Independent findings: [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md). Resume with [NEXT_AGENT_PROMPT.md](NEXT_AGENT_PROMPT.md).

## Reproduction commands

Run from the candidate demo with `PYTHONPATH=Tools/AssemblyShadow` for Python commands:

```sh
python3 Tools/AssemblyShadow/h1_witness_contract.py --project .
python3 Tools/AssemblyShadow/integration-tests/h1_m02_witness_integration.py
python3 Tools/AssemblyShadow/h1_test_inventory.py python --tests Tools/AssemblyShadow/tests --pattern 'test_h1_*' --log NEW_LOG --output NEW_JSON
python3 Tools/AssemblyShadow/h1_test_inventory.py python --tests Tools/AssemblyShadow/tests --log NEW_FULL_LOG --output NEW_FULL_JSON
pwsh -NoProfile -File .agents/skills/unity-debug/scripts/Invoke-UnityCompile.ps1 -TimeoutSec 300
```

Editor test CLI used the configured Unity executable with `-batchmode -nographics -projectPath <exact project> -runTests -testPlatform EditMode -testFilter AssemblyShadow -testResults <new XML> -logFile <new log>` (no `-quit`). Reproduction used filter `AssemblyShadowDemo.EditorTests.H1EvidenceProcessTests`. Check exact-project Editor ownership before repeating; outputs must be new. Reproduction Python used unittest discovery with `test_h1_*` from its own checkout.

The evidence manifest hashes this checkpoint's portable files. It is an integrity inventory, not the H1 successor package or M08 acceptance. Local raw compiler attempts stay preserved; their machine paths in logs are historical evidence, not portable fetch URLs.
