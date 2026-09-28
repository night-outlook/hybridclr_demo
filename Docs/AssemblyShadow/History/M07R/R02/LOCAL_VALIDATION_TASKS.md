# R02 Local Validation — final successor to batch F

Protocol: `R02LocalBatch-v1`; **34 required cells**, one fresh unused execution root. Primary code, tests, source/control pairing and selected host CI are published. This task sheet does not establish runtime acceptance.

## Entry authority

Read canonical `Docs/AssemblyShadow/README.md` and `Handoff/WEB_TO_LOCAL.md`, then this directory's `F_INTEGRATION_REPAIR.md`, `F_EDITOR_COVERAGE_FINALIZATION.md`, `PRIMARY_VALIDATION.md` and `source-targets.json`. Use the final pushed transport HEAD in Primary's prompt, not the source or CI commit.

Common source: `1642392278a97bc9348195e35ec5d1b7fb6fa530`.
Control demo: `codex/r02-h1-runtime-control@028ad68fa25a531be07f11f1fdcc417842f98ab4`.
**Both roles must use package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.** Candidate/control runtime pins, owning paths and branch identities are fixed by the handoff. Old package or prior F graphs are not valid substitutes.

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

Inspect the non-executing plan, then add `--execute` for the single new batch. Do not resume or relabel F.

## Required coverage and repair observations

| Area | Required evidence |
| --- | --- |
| Source/host | Exact four-repository authority per role, common graph, host native/managed/Python checks and actual native-writer/package-parser contract |
| E forensic retention | Authenticated live snapshots or original E archive member recovery, retained origin/index/archive and selected copies; no dangling original paths |
| Controlled builds | Independent fixed M00 materialization and new ON/OFF graphs for both roles, current package and installed runtime, complete build/input identities |
| Parser and sidecars | All eight role/mode combinations; candidate ON modes must accept the known r02 extension; retain original native JSON |
| Formal measurement | Four pilot plus forty formal A/B pairs, 88 fresh timing processes; balanced order, unchanged strict verification and no formal sidecar |
| Editor | All three R02TypeResolutionSchemaTests and both R02ProbeContractTests Passed exactly once by full name; a Passed overall test-run; editor-tests.json requiredCases and complete XML |
| M07/startup/failure | Prepared mode-specific Control capsule root, early callback receipts, then semantic/raw M07 results; unchanged negative expectations |
| Counts | Parameter/nested manifests reach respective auditors; fresh four diagnostic builds and complete 132-case launch/raw chain |
| Restoration | Diagnostic/count linker before/generated/restored bytes, exact restoration and clean final authority; unknown output returns to Primary |
| Other regressions | Four independent native scripts, authenticated generated-native transaction, lazy/dense and ordinary/mixed capacity |
| Sealing | Every required input/output and partial failure retained; full content-addressed seal bound by LOCAL_BATCH_RESULT.json |

The final runner now machine-enforces all five Editor full names listed in `F_EDITOR_COVERAGE_FINALIZATION.md`. Missing, skipped, duplicated or misnamed required cases reject the cell. Report any unrelated skipped cases separately; they do not supply required coverage. Host synthetic XML tests do not replace these real Editor executions.

F's missing early arguments are a source-level diagnosed cause, not proof of all later M07 paths. Report any subsequent refusal separately. Raw native JSON is authoritative for R02 diagnostics; the legacy serialized DTO intentionally omits its transient extension.

## Failure, evidence and return

Independent valid cells continue; invalid prerequisites or dirty source block consumers. No automatic semantic retries, increased timeouts, changed pins/hashes, relaxed verifiers, reduced cases or non-trivial local fixes. Do not promote historical Player execution.

The exact E archive is the only missing-live-input recovery source. Missing/corrupt required inputs remain fatal to complete sealing; no basename fallback or substitute run. Preserve F's failed-seal status and partial inventory. Do not reconstruct old paths or invent a complete F archive. Linker expansion beyond the exact approved set returns to Primary with before/after evidence; build and restoration failures stay separate.

Retain all command logs, raw diagnostics, capsules, count audits, forensic copies and origins, materialization/build/launch/raw/verifier chains, Editor XML/requiredCases, linker recovery, Unity completion, D1/D2 analysis and seal/index/archive, including generated roots outside the batch directory. Do not delete history to satisfy free-space checks.

Update and push `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with precise classifications, first failure, exact source/build/input identities and preserved paths. Obtain a genuinely independent R02 stage review only when complete evidence is eligible; retain its verbatim verdict. This is not H2 Human Review Gate and does not authorize R03.

H1 remains PassedWithExplicitDeferredRisk. D1/D2 require measured allocation/reflection/closed-generic and memory disposition before H2. R02Accepted=false; mayEnterR03=false. Stop and return to Primary.
