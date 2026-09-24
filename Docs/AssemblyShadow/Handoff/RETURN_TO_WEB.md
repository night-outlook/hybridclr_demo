# Local Validation → Primary Implementation

## Blocker: V04.AF reads current analysis source pins from the historical bridge checkout

### Symptom and reproduction

The pushed validation checkout at `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` HEAD `aedf3c58c3e3f8ab612552563a29c8906b82bea1` passes V00, bounded Primary 377/377, and complete Python discovery with zero failures/errors. The source-27df checkpoint manifest, four fixed original live inputs, 33,792 sealed files, and additional direct live bindings authenticate read-only. Both exact source deltas pass: seven v2 historical analysis/test paths and 25 v2 retained-graph paths.

From that validation checkout, run the exact command in `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/V04/historical-compatibility-command.json`. It invokes `Tools/AssemblyShadow/h1_historical_reanalysis.py` with the original live source-27df final sample index, pilot seal, graph bridge, and formal batch, plus `--preflight-only`. The command exits 1 and writes:

```text
kind=H1HistoricalPerformanceReanalysisFailure
result=Failed
Historical analysis successor delta differs from the exact policy:
missing=[Tools/AssemblyShadow/h1_bee_primary_tests.py,
         Tools/AssemblyShadow/tests/test_h1_paired_performance.py]
extra=[]
```

V04.AG strict analysis, V05, and independent M08 are blocked. No Player was launched. The failed preflight output is not a `H1HistoricalAnalysisCompatibility` receipt and cannot be used as one.

### Root cause and affected scope

`Tools/AssemblyShadow/h1_historical_reanalysis.py::authenticate_compatibility` reads the immutable historical bridge's `projectRoot`, then calls `_current_source_pins(project)` and `authenticate_analysis_delta(project, current_revision)` through that same path. The bridge points to the ordinary owner checkout `/Users/ah/GitHub/hybridclr/hybridclr_demo`, detached at `d7854b16c09b02d4494d28c2b0ea015ba83f58a3`. Its demo source pin remains `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The designated v2 validation checkout pins `d239d9d00784ea2df22133cb8c938ec25035f5a0`. The tool therefore compares source-27df with the older five-path v1 authority and reports exactly the two v2 test paths missing. `V04/project-selection-diagnosis.json` records both checkout identities and the call chain.

The design conflates the immutable historical evidence root with the current analysis-source checkout. Changing the owner checkout or rewriting original bridge/receipts would conceal that distinction and violate the historical evidence boundary. This defect affects the v2 compatibility proof and all dependent analysis/acceptance gates; read-only live evidence hashes and current-source test results remain valid within their stated scope.

### Evidence

Authenticated return checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`.

- `V00/source-authority.json` and `handoff-preflight.json`: four correct pushed checkouts, pins, zero anchor-to-HEAD non-metadata delta, exact seven/25-path audits, `SourceTargetVerifiedNotBuildAccepted`.
- `V01/bounded-primary/` and `python-inventory.json`/`python-tests.log`: 377/377 bounded; 1,033 Passed / 28 explicit Skipped / zero Failed/Error across 1,061 Python leaves; corrected positive leaf Passed.
- `V02/live-evidence-reauthentication.json` and `historical-checkpoint-manifest.log`: original four live hashes, 33,792 sealed files, 92/92 checkpoint manifest. `direct-binding-audit.json` and `direct-binding-semantics-audit.json` preserve the generic false mismatches and their Git-pinned resolution.
- `V04/historical-compatibility-command.json`, `historical-compatibility-v2.json`, and `project-selection-diagnosis.json`: exact failure, original live paths, checkout-source divergence, and no Player invocation.
- `MANIFEST.sha256`: return checkpoint authentication.

### Required Primary action and remaining uncertainty

Separate the historical evidence project root from the current analysis-source authority in the compatibility tool. Authenticate the current source using the explicitly designated validation checkout or an independently verified source identity, while continuing to authenticate the original bridge, seal, batch, sample, and formal authority through their immutable live paths. Keep the exact v2 seven-path and 25-path allowlists and fail-closed production analyzer checks. Add a process-level regression with historical bridge and current source in different checkouts, plus negative tests for wrong current pin and changed historical evidence. Do not rerun Players or rewrite historical receipts.

The v2 semantic bridge/seal/formal-authority proof and corrected historical strict analysis have not run because this first prerequisite failed. Once Primary publishes a pushed repair, Local must rerun V00/V01, complete live reauthentication, V04.AF, V04.AG, analysis-only checkpoint authentication, V05, and genuinely independent M08 if eligible. H1 remains `InProgress`; historical M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`; R02 is closed.
