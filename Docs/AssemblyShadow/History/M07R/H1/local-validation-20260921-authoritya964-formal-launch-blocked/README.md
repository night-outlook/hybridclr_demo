# H1 Local Validation checkpoint — authority `a964f79d`

This is the authenticated pre-cleanup checkpoint for the 2026-09-21 retained-graph nested-authority closure and formal launch batch.

- Candidate checkout: `7ff70be81c7b1a1dd73b3a02b79494acf5035d19`
- Candidate source/tool anchor: `a964f79d6ceba866c5956741a4a32e38ff8a6b5f`
- Native/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Outcome: `AuthorityTestsReuseBridgePreflightSealPassed;FormalFreshCandidateLaunchAuthorityBlocked`

Fresh V00/V01 passed, including 353/353 bounded Primary tests, 1,010 Python passes plus 28 explicit environment skips and no failures/errors, and 1,076/1,076 broad Unity EditMode tests. Exact 9-path and 17-path source audits passed. Retained checkpoint/Player manifests and 33,792 bound files totaling 1,606,993,133 bytes reauthenticated.

The new side-B `H1GraphReuseBridge` passed with SHA-256 `b6e97f573938757d712c632a765fb58b8cb82ff9e360733158de998f980a25e0`. The three-mode retained-ON preflight passed in 1763.650 seconds. The strict pilot seal passed all eight deep side verifications and stable file guards; its SHA-256 is `5dc313824e9b034475a4d6f105b5d29801ef796f1553881d8b3b3699f9f65935`.

Formal cached admission reached first side launch in approximately 14.746 seconds. `R00-OFF-NoPatch-formal-01` attempt 1 then retained a passing protected side A and a candidate side B that failed before Player launch with `R00 baseline: source pins differ from baseline provenance`. Explicit whole-pair attempt 2 reproduced the same outcome and byte-identical side-B failure evidence. No timeout, cleanup failure, or residual process occurred.

The fresh formal subprocess drops retained authority: `run-h1-paired-performance.py::build_command()` launches the public current-pairing-only `run-r00-players.py`, which calls default `verify_inputs()` before launch. This is a Primary source/tool boundary defect, not bridge, seal, graph, or Player corruption.

`raw-evidence.tar.gz` contains the complete bounded Local evidence root. The readable V04 tree contains bridge, preflight, seal, stopped batch, and both attempts with side logs/receipts. `MANIFEST.sha256` authenticates this checkpoint. No cleanup was performed.

Formal acceptance is 0/40, final analysis was not run, and V05/M08 remain ineligible. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
