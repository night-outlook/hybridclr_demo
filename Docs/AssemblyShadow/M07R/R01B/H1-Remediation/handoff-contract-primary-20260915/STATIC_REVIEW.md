# Static review — authoritative handoff contract repair

## Scope

Reviewed against Local Validation return commit `b6db7c2fb2fce364d49458b7dfc78886fd430004`, especially `RETURN_TO_WEB.md`, `local-validation-20260915-c0d3070/README.md`, `handoff-section-census.json`, `source-state.json`, `h1_handoff_preflight.py`, and `shadow_tools.py`.

## Findings and closure

### F1 — handoff section contract mismatch — Closed

The c0d3070 handoff omitted four literal headings required by the unchanged preflight: `## Implementation`, `## Alternatives`, `## Risks`, and `## Human review gate`. The successor `WEB_TO_LOCAL.md` restores all nine required headings while retaining the current R01B instructions.

### F2 — next-stage demo-source identity would otherwise drift — Closed for this successor

The returned Local Validation checkpoint added tracked files under `Documents/AgentHandoff/local-validation-20260915-c0d3070/`. Under the current `shadow_tools.metadata_only()` contract those files are demo source inputs, so merely fixing headings while leaving the old `463ec3f…` source pin would allow the preflight to advance to a later `Demo HEAD contains build-input changes after the source pin` failure.

The repair therefore promotes `b6db7c2…` as the candidate demo source anchor and updates both machine-readable source targets and `AssemblyShadowSourcePins.json` to that exact SHA. The executable/tooling implementation itself remains `463ec3f…`; no preflight/source-verifier executable was relaxed.

Future auxiliary Local Validation checkpoints are directed to the existing `Docs/AssemblyShadow/...` metadata-only namespace. The three owner protocol files continue under `Documents/AgentHandoff/`.

### F3 — provenance / gate weakening — Not introduced

No Apple Bee domain, PCH, compiler, source-linkage, witness, count, runtime, performance, or human-gate acceptance rule is weakened. Historical failed preflight and earlier evidence remain immutable.

## Static acceptance

The final successor must satisfy all of the following before handoff:

1. branch remains a fast-forward descendant of `b6db7c2…`;
2. the final diff from `b6db7c2…` contains only `WEB_TO_LOCAL.md`, `source-targets.json`, `AssemblyShadowSourcePins.json`, and `Docs/AssemblyShadow/...` documentation;
3. all nine `h1_handoff_preflight.REQUIRED_SECTIONS` literal headings occur in `WEB_TO_LOCAL.md`;
4. candidate source target and demo source pin both equal `b6db7c2fb2fce364d49458b7dfc78886fd430004`;
5. runtime pins remain candidate native `1d2df7c…`, package `0ea633a…`, IL2CPP `6be7f38…`;
6. reproduction demo/native remain `352d747…` / `99cdb1b…` and performance reference remains `88508b5…`;
7. H1 remains not passed and R02 remains prohibited.

Direct execution of the real local preflight still belongs to V00 because this environment has no working GitHub DNS/local Unity checkout. The unchanged preflight has existing disposable-repository regression coverage; the document/source identities above are verified through committed Git state and final compare.
