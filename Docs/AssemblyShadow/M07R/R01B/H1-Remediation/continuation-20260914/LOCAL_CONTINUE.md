# Local continuation instructions

## Branches

- Candidate: `hybridclr_demo`, `hybridclr`, `hybridclr_unity`, `il2cpp_plus` on `codex/assembly-shadow-r01b-h1`.
- Unfixed reproduction: demo/native on `codex/assembly-shadow-h1-count-repro`.
- Performance reference demo: `codex/assembly-shadow-h1-performance-reference`.

Before running Unity, read `transfer/README.md`, `transfer/h1-transfer-manifest.json`, its committed coordination snapshots, `../../H1-handoff.md`, this directory's README, and `LOCAL_VALIDATION_TASKS.md`. Planning files remain normative, but live execution status comes from the transfer/continuation ledger.

Do not modify historical receipts to point at new commits, do not rewrite failed attempts, and do not begin R02.

## First local task

Start with `H1R-M05-POLICY-REFREEZE` integration/compile validation. From candidate demo:

```bash
export PYTHONPATH="$PWD/Tools/AssemblyShadow${PYTHONPATH:+:$PYTHONPATH}"
python3 Tools/AssemblyShadow/h1_witness_contract.py --project "$PWD"
python3 Tools/AssemblyShadow/integration-tests/h1_m02_witness_integration.py
python3 -m unittest discover -s Tools/AssemblyShadow/tests -p 'test_h1_*' -v
```

Use Python >= 3.11. Unity can receive `-shadowH1Python /ABS/python3` when `python3` is not the intended interpreter. Record interpreter/tool hashes with fresh evidence.

## Count builds and provenance

Build candidate `On/Debug`, `On/Release`, `Off/Debug`, `Off/Release`; build reproduction `On/Debug`, `On/Release`. Each build uses a new preparation/output/evidence directory and separate Unity processes for prepare/build/restore. Use the managed-provenance wrapper for the build phase; prepare and restore keep their existing entry points:

```text
AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.PrepareDiagnosticBuild
AssemblyShadowDemo.Editor.H1CountDiagnosticBuildWithManagedProvenance.BuildDiagnosticPlayer
AssemblyShadowDemo.Editor.H1CountDiagnosticBuild.RestoreDiagnosticBuild
```

Pass explicit absolute `-shadowH1BuildReceipt` and `-shadowH1PreparationRoot` arguments to the wrapper. Calling the unwrapped build method omits managed source capture.

After each build, verify the generated managed and native provenance rather than inferring it from settings/logs. Candidate compiler verification consumes four build receipts; reproduction compiler verification consumes two. Managed proof route A is fresh graph verification. Route B is allowed only with an explicit prior direct proof whose source/configuration/defines and actual Player DLL bytes are reverified equal; no automatic fallback is permitted.

## Completion

Complete every applicable item in `LOCAL_VALIDATION_TASKS.md`, update append-only coordination status, seal a new successor archive/index, and obtain an independent whole-chain M08 review. Only after an independent M08 PASS should work stop for the user's explicit H1 decision. `humanGatePassed` and `mayEnterR02` must remain false until that human decision.
