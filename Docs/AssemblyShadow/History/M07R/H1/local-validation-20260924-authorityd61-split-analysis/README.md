# Local Validation checkpoint — split-checkout historical analysis

This checkpoint records the 2026-09-24 Local Validation run against the pushed
`0bed47e981e5b3b4ac8b9ed2b4c423e11aa88b31` demo handoff and its
`d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece` analysis source anchor.
The other three worktrees remained at the pinned pushed commits recorded in
`V00/source-authority.json`. The immutable historical execution source is
`27df1a3d60811dc121f296ab561ae313a382b363`.

| Cell | Result | Evidence |
| --- | --- | --- |
| V00 source authority | Passed | `V00/` — exact four-repository heads, remote refs, pins, zero anchor-to-HEAD non-metadata changes, exact seven/25/three-path audits, committed preflight |
| V01 bounded Primary | Passed 381/381 | `V01/bounded-primary/` and command receipt |
| V01 complete Python discovery | 1,065 leaves; 1,037 Passed, 28 environment Skipped, zero Failed/Error | `V01/python-inventory.json`, full log and command receipt |
| V02 historical live authentication | 33,792/33,792 sealed files, 1,606,993,133 bytes; zero missing/content/guard mismatches | `V02/` — 92/92 historical checkpoint manifest, four fixed hashes, direct binding audits |
| V04.AF split-checkout compatibility | `AuthenticatedAnalysisOnlySuccessor` | `V04/historical-compatibility.json` and command receipt |
| V04.AG strict historical analysis | `Passed` / `ComparabilityPassed` | `V04/historical-performance-analysis.json`, command receipt, and exact assertion receipt |
| V04.AH analysis-only checkpoint | Manifest authenticated | `MANIFEST.sha256` covers this checkpoint's evidence and README |
| V05 | Not eligible under the current handoff | `V05/eligibility.json` |
| Independent M08 | Not eligible / NotRun | `M08/eligibility.json` |

V04.AG reanalyzes all 45 original retained attempts. Forty-four are valid,
including all 40 formal attempts and one selected valid pilot per mode. The
original failed `R00-ON-NoPatch-pilot-01` attempt remains invalid with its
runner process-group cleanup failure. Every mode has ten formal pairs and ten
startup observations; chronology and global non-overlap pass. The full
measured statistics, including unfavorable values, remain in the analysis
JSON. This is historical analysis, not new Player execution.

The current handoff names V05 but does not supply a runnable analysis-only
successor contract or acceptance criteria. The original execution series
cannot be relabelled as fresh current-source evidence, and the handoff bars a
Player rerun. `V05/eligibility.json` records the resulting gate decision.
Independent M08 was not commissioned because V05 is not eligible. The earlier
independent M08 `FAIL` remains the historical result. H1 remains
`InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.

No Player was rerun. `V04/no-player-proof.json` records Local command issuance
and its scope limit. All original source-27df live evidence paths were read
without rewriting them. The original historical checkpoint remains at
`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`.
