# Local continuation after D01/D02 source preparation

## 1. Review and integrate the source changes

Use the existing candidate demo/package worktrees on `codex/assembly-shadow-r01b-h1`. Inspect unrelated changes first. When fetching published prerequisites, name the branch explicitly; the prior workspaces used restricted fetch refspecs. The basis for this delivery is demo `4ef5f674522f03c11dbcf22128071c745778b0e5` and package `c7ed6d244a2c3a8e948f062d5431c289e1369650`.

The delivery has not been applied to the remote branches. From the delivery directory, the following command only reads the worktrees and renders patches/expanded source into a new output directory:

```sh
python3 render_changes.py --demo /ABS/candidate/hybridclr_demo \
  --package /ABS/candidate/hybridclr_unity --output /ABS/new-d01-d02-render
```

The render output must be outside both source worktrees. The renderer verifies every supplied payload SHA-256 before use. Review the two patches, changed-file inventory and expanded sources before integrating them through the normal local review workflow. A blob/anchor conflict is not permission to disable the check: compare that specific file against the recorded basis. The renderer never changes a checkout, modifies pins, creates a branch or pushes. Historical evidence must not be changed to agree with new code.

No native runtime source is changed by this delivery. Keep reproduction native on `codex/assembly-shadow-h1-count-repro`, with the count defects intact. Candidate/reproduction demos must use intentionally selected package worktrees; do not unintentionally replace the performance reference runtime/profile with the candidate.

## 2. Run the diagnostic batch

After local source integration and inspection, fill `variables.example.json` with the actual candidate, package, reproduction, Unity, Python and PowerShell paths. Use Python >= 3.11 and Unity 2022.3.62f2. Place the filled variables file outside historical evidence. The directory passed as `--output` must not exist, including when first previewing it.

Run from the candidate demo:

```sh
python3 Tools/AssemblyShadow/h1_local_batch.py \
  --plan Docs/AssemblyShadow/M07R/R01B/H1-Remediation/d01-d02-20260914/diagnostics-plan.json \
  --variables /ABS/diagnostic-variables.json --output /ABS/new-diagnostic-run
```

Review the resolved arguments, then repeat the same command with `--execute`. Preview does not create the run directory. The batch serializes Unity processes, calls the project's existing exact-project Editor detection helper before every Unity launch, checks executed test counts and NUnit cases, and writes fresh command logs and task results. It never terminates an existing user Editor. Close or manage that Editor through the existing ownership-aware workflow first.

The plan runs the normal M02 owner/CLI tests, new CodeGen PDB tests, both formerly failing Player-script fixtures, full Python tests, and the full Editor suite after focused prerequisites pass. Independent diagnostic tasks can still run after another diagnostic fails; expensive dependent stages do not receive a false PASS. The known M01 absence can still make full suites nonpassing. Do not rewrite test expectations or archived evidence to hide it.

## 3. Collect and evaluate every D01 failure in the same local session

Unity jobs receive `ASSEMBLY_SHADOW_ILPP_FAILURE_ROOT` pointing into their fresh task directory. On an ILPP failure, the package retains original PE/PDB bytes, the configuration, compiler-reference copies, exact tool binaries when exposed by Unity, and the complete exception. These are capture-time replay inputs, not a substitute for build provenance.

If new failures occur, generate a replay plan for the explicit diagnostic run root:

```sh
python3 Tools/AssemblyShadow/h1_replay_batch.py plan \
  --capture-root /ABS/new-diagnostic-run --output /ABS/new-replay-plan.json
python3 Tools/AssemblyShadow/h1_local_batch.py \
  --plan /ABS/new-replay-plan.json --variables /ABS/diagnostic-variables.json \
  --output /ABS/new-replay-run --execute
```

Every captured failure is included; the tool does not pick a "latest successful" sample. Each replay runs the unresolved control and both prepared routes in one Unity process, then independently compares raw Portable-PDB LocalConstant signature bytes and owning scope coordinates. All failures remain recorded. The audit does not claim all PDB custom-debug records or native execution are verified.

Route A is the default: resolve only assemblies present in the compiler reference list, by complete assembly identity. Route B is explicit: `ASSEMBLY_SHADOW_PDB_RESOLVED_ENUMS` in the compiled assembly defines enables normalization of ClassSig constants only when the type resolves to an enum and its underlying primitive type matches the value exactly. There is no automatic retry/downgrade inside the transformer. Record the selected route and evidence. If B is selected, stage and restore the define using the established fresh-process settings workflow, include it in subsequent source/build receipts, and rerun the focused compiler tests. A replay success alone does not qualify a Player build.

If both routes fail, the batch has already retained the exact failing data and full traces for further local diagnosis. Do not remove `const`, discard PDBs, approve newly discovered method hashes, suppress writer errors, or use an unrestricted assembly search as a shortcut. A raw signature/token/scope mismatch is a review item, not an equality to normalize away. Non-Portable-PDB input is outside the independent Python auditor's format support and must remain explicitly unverified.

## 4. Continue the original acceptance chain

After D01/D02 close in the real environment, complete `LOCAL_VALIDATION_TASKS.md`. Import-generated `.meta` changes, selected emission defines and configuration changes must be reviewed before the new source freeze. Old pins deliberately describe old code; do not edit old receipts to make them current. Six new candidate/reproduction builds must use their documented managed-provenance wrappers and fresh prepare/build/restore processes. Verify the actual provenance, not only successful build exit codes.

Proceed through the existing count/reproduction, fresh baseline/startup11, capacity/lazy/dense/FieldRVA, controlled performance and successor-package requirements. Obtain an independent whole-chain M08 PASS for the actual final sources and evidence. Only then stop for the user's explicit H1 approval. This delivery is not that approval; R02 remains prohibited.
