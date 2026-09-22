# Local Validation checkpoint — authority `91ac4db3`

This checkpoint preserves the 2026-09-22 Local Validation cycle at candidate checkout `bb2bf106c172c985e9330de9cc0e2f58b24f096b` and source/tool anchor `91ac4db31cec704551c7db05bd918c8d5695ce83`.

V00, current Python validation, exact 9/22 source audits, retained evidence reauthentication, the new graph bridge, retained-pilot admission, and the new strict 8-side pilot seal passed. Fourteen of forty formal pairs then passed. Resume failed closed before pair 15 because the sealed protected OFF `GameAssembly.dylib` device identity changed from `16777229` to `16777230`; its SHA-256 and every other sealed stat field remained unchanged.

Contents:

- `V00/`, `V01/`, `V01A/`, and `V02/`: current authority, tests, source audits, and retained-evidence audit;
- `V04/`: bridge, admission preflight, 8-side seal, cumulative sample indexes through formal pair 14, interruption classification, and seal-invalidation receipt;
- `formal-side-evidence.tar.gz`: all 14 pairs' A/B output roots, driver consoles, and candidate formal-authority receipts;
- `raw-evidence.tar.gz`: complete Local evidence root before cleanup;
- `prior-checkpoints/`: exact manifest snapshots for all earlier Local checkpoints;
- `handoff/`: the Local result and Primary return as committed with this checkpoint;
- `results-summary.json`: machine-readable disposition;
- `MANIFEST.sha256`: hashes for every checkpoint file except the manifest itself.

No failed or partial attempt was overwritten. Pair 15 did not create a protocol output root or sample index, so it remains unattempted. Final analysis, V05, independent M08, and R02 were not run.
