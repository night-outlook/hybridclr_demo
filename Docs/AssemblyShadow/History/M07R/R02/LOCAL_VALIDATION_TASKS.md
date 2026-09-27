# R02 Local Validation task sheet — after verified publication

Protocol: `R02LocalBatch-v1`. The repaired package is published and Primary-validated. Execute only from the exact final handoff tuple and the source/control authority in `source-targets.json`; prior A/B/C attempts remain historical failed evidence.

## Entry

Use the final Primary prompt and source-targets file, not chat history. Candidate and matched control must each have four correctly identified owning checkouts. Their managed executable source graphs must match; the control uses the accepted H1 runtime, the candidate uses R02. The historical R01 reference is separate and must remain untouched.

Confirm Unity `2022.3.62f2`, macOS arm64, PowerShell, Python 3.10+, a .NET SDK supporting net8.0, and a host C++ compiler. Close Unity for both workspaces. Resolve tool locations without changing source. Use an unused direct child of candidate `_temp/AssemblyShadow/` as the batch output. At least 30 GiB free is required; preserve historical evidence rather than deleting it to satisfy this check.

Record the exact final prompt heads in shell variables `CANDIDATE_HEAD` and `CONTROL_HEAD`; do not infer them from whichever branch happens to be checked out. Set `CANDIDATE`, `CONTROL`, `UNITY`, `PWSH`, and `OUTPUT` to the exact approved absolute paths. These variables are execution inputs, not unspecified source identities.

```sh
python3 "$CANDIDATE/Tools/AssemblyShadow/R02/run_local.py" \
  --candidate "$CANDIDATE" --candidate-head "$CANDIDATE_HEAD" \
  --control "$CONTROL" --control-head "$CONTROL_HEAD" \
  --unity "$UNITY" --pwsh "$PWSH" --output "$OUTPUT"
```

The command above prints the frozen plan without execution. After checking it against the handoff, run the same command with `--execute`.

## Batch acceptance cells

| Group | Required observations |
| --- | --- |
| Authority | Four exact source/ref identities per role, clean inputs, common managed graph, source-to-metadata-head equivalence |
| Host | Read-only source reconstruction; native kernels/revisions; Python verifiers; separate managed build/exec; codec owned-storage measurement |
| Builds | Fresh installed runtime and two controlled ON/OFF graphs, independent candidate/control provenance, restoration checked |
| Functional | Eight role/mode combinations; correct execution markers and physical identities; 1/10/10000 construction checks; 100/1000 distinct complete types; four joined worker threads |
| Cache oracle | Warm single-class candidate P01/P03 has no metadata scan or repeated layout-proof work, sufficient admission hits, no positive-path rejection; unavailable counters never treated as zero |
| Formal performance | Four pilot pairs followed by forty formal pairs, 88 unique sample nonces, 10 formal pairs per mode, balanced AB/BA, no overlapping processes, strict R00 reconstruction |
| Regressions | Candidate Editor and native checks, M07, startup11, failure/publication/recovery, fresh count132, lazy/dense, ordinary/mixed capacity |
| Retention | Logs, build identities, all selected input bytes, complete launch/raw chains and partial failures sealed and available |

Functional sidecar timings are diagnostics, not substitutes for the controlled R00 formal series. Formal processes explicitly clear the three R02 sidecar environment variables. D1/D2 are not closed by a PASS label or an exit code: report measured effects and their limitations.

## Failure rules

Do not retry a semantic failure automatically. Independent cells with valid workspaces may continue. Dependencies and workspace source-state failures block consumers. Never disable an assertion or relax ownership/cleanup because the host program printed Passed.

Build and recovery failures have separate records. The recovery helper captures every original/generated file before considering writes, accepts only the predeclared changes, checks again for concurrent edits, and does not overwrite unexpected mutations. If recovery fails, preserve the workspace and receipts for Primary.

Missing retained capacity input bytes are an input-availability limitation, not permission to reuse the old capacity PASS. Record their exact missing location/hash. No basename fallback, fabricated old path, or fresh execution claim for historical results is permitted.

## Evidence locations and return

The batch writes `commands/`, per-cell JSON, graphs, sidecar/verifier/sample records, build map, frozen schedule, paired index/analysis, generated-input recovery receipts, and `seal/seal-index.json` plus content-addressed archive. `LOCAL_BATCH_RESULT.json` binds the seal. Preserve the generated roots outside the batch directory as well. No cleanup through independent review.

If all required cells succeed, obtain a genuinely independent R02 stage review using `.codex/agents/code-gate-reviewer.toml` and exact committed source/evidence. Preserve its verbatim report. This does not approve H2 or authorize R03.

Update and push `LOCAL_VALIDATION.md` with precise scope, versions and Passed/Failed/Blocked/NotRun/Unavailable classifications. For non-trivial issues, update `RETURN_TO_WEB.md` with the exact failing command, source/build/input identities, first observed failure, partial results and restoration state. Do not implement non-trivial fixes locally.
