# R02 Local Validation — successor to batch F

Protocol: `R02LocalBatch-v1`; **34 required cells**, one fresh unused execution root. Primary code, tests, source/control pairing and selected host CI are published. This task sheet does not establish runtime acceptance.

## Entry authority

Read canonical `Docs/AssemblyShadow/README.md` and `Handoff/WEB_TO_LOCAL.md`, then this directory's `F_INTEGRATION_REPAIR.md`, `PRIMARY_VALIDATION.md` and `source-targets.json`. Use the final pushed transport HEAD in Primary's prompt, not the source or CI commit.

Common source: `995dbf1003c306a69586f882ff02599db7a9780e`.
Control demo: `codex/r02-h1-runtime-control@95b85617c92f8ce806f4652d88077936c76c3b8a`.
**Both roles must use package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.** Candidate/control runtime pins, owning paths and branch identities are fixed by the handoff. The old package or previous F graphs are not valid substitutes.

Close both Unity editors; verify eight clean, correctly identified owning checkouts and common executable graph. Confirm Unity 2022.3.62f2, macOS arm64, Python 3.10+, PowerShell, a .NET SDK supporting net8.0, clang++ and at least 30 GiB free. This disk minimum is not a total archive-space guarantee. Preserve unrelated worktrees and all A/B/C/D/E/F/H1 evidence.

Set exact paths and heads from the final prompt in `CANDIDATE`, `CONTROL`, `CANDIDATE_HEAD`, `CONTROL_HEAD`; resolve absolute `UNITY`/`PWSH`, and use a new unused direct candidate `_temp/AssemblyShadow/` child as `OUTPUT`.

```sh
export TMPDIR=/private/tmp
export PYTHONDONTWRITEBYTECODE=1
python3 "$CANDIDATE/Tools/AssemblyShadow/R02/run_local.py" \
  --candidate "$CANDIDATE" --candidate-head "$CANDIDATE_HEAD" \
  --control "$CONTROL" --control-head "$CONTROL_HEAD" \
  --unity "$UNITY" --pwsh "$PWSH" --output "$OUTPUT"
```

Inspect this non-executing plan, then add `--execute` for the single new batch. Do not resume or relabel F.

## Required coverage and repair observations

| Area | Required evidence |
| --- | --- |
| Source/host | Exact four-repository authority per role, common graph, host native/managed/Python checks and actual native-writer/package-parser contract |
| E forensic retention | Exact authenticated live snapshots or original E archive member recovery, retained origin/index/archive and selected copies; no dangling original paths |
| Controlled builds | Independent fixed M00 materialization and new ON/OFF graphs for both roles, current package and installed runtime, complete build/input identities |
| Parser and functional sidecars | All eight role/mode combinations; candidate ON-P01/P03 must no longer fail on the known r02 extension; raw native JSON retained |
| Formal measurement | Four pilot plus forty formal A/B pairs, 88 fresh timing processes; balanced order and unchanged strict verification; no sidecar during formal timing |
| Editor serialization/linker tests | All three `R02TypeResolutionSchemaTests` and both existing `R02ProbeContractTests` Passed; retain complete XML and other case classifications |
| M07/startup/failure | Prepared mode-specific Control capsule root, early callback receipts and then semantic/raw M07 results; unchanged negative-case expectations |
| Counts | Parameter and nested manifests reach their respective auditors; fresh four diagnostic builds and complete 132-case launch/raw chain |
| Restoration | Diagnostic/count linker before/generated/restored bytes; exact restoration and final clean authority; unknown output returns to Primary |
| Remaining regressions | Four independent native scripts, authenticated generated-native transaction, lazy/dense and ordinary/mixed capacity |
| Sealing | Every required input/output and partial failure retained; complete content-addressed seal bound by `LOCAL_BATCH_RESULT.json` |

F's old missing early arguments are a source-level diagnosed cause, not proof that all later M07 paths are correct. Report any further refusal separately. Raw native JSON is authoritative for R02 diagnostics; the legacy serialized DTO intentionally omits its transient parsed extension.

## Failure and retention rules

Independent valid cells continue; invalid prerequisites or dirty source state block consumers. Do not automatically retry semantics, increase timeouts, change pins/hashes, relax verifiers, reduce cases or implement non-trivial fixes. No historical Player execution is promoted to current success.

The existing E archive is an exact recovery source only. Missing/corrupt required inputs remain fatal to complete sealing; no basename fallback or substitute run is allowed. Preserve F's failed-seal status and preservation inventory as such. Do not reconstruct historical paths or invent a complete F archive.

A linker expansion beyond the exact approved set returns to Primary. Preserve all source mutations and before/after receipts; do not reset unexpected changes. Build failure and restoration failure remain separate observations.

## Return and stop

Retain complete command logs, raw diagnostics, capsule files, both count audits, copied forensic inputs and origins, materialization/build/launch/raw/verifier chains, linker recovery and Unity process-completion receipts, D1/D2 analysis, seal/index/archive and generated roots outside the batch directory.

Update and push `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications, first failure, exact source/build/input bindings and preserved paths. If all evidence is eligible, obtain a genuinely independent R02 stage review using the existing reviewer definition and keep its verbatim verdict. This does not replace H2 Human Review Gate or authorize R03.

H1 remains PassedWithExplicitDeferredRisk. D1/D2 require measured allocation/reflection/closed-generic and memory disposition before H2. R02Accepted=false; mayEnterR03=false. Stop and return to Primary.
