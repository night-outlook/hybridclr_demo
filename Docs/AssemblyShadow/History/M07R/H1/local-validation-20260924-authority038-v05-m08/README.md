# Local Validation checkpoint — source 038, V05, independent M08

This checkpoint records Local Validation of pushed demo handoff
`4b8e8617deee75dbc10241e120ec2e8a3b3cd366` and source anchor
`0388479f7073289e3505b992956a7cbe78c302ce` on 2026-09-24/25.
The other three source pins and clean remote heads are in
`V00/source-authority.json`. Source-27df execution remained immutable and
historical. No Player or formal runner was invoked.

| Cell | Result | Evidence |
| --- | --- | --- |
| V00 | Passed four-repository authority and committed preflight | `V00/` |
| V01 | Bounded Primary 387/387 Passed; Python 1,071 leaves, 1,043 Passed, 28 environment Skipped, zero Failed/Error | `V01/` |
| V01A | Exact seven-path historical analysis, 25-path retained-graph, three-path split-checkout audits; zero nonmetadata source-anchor-to-HEAD delta | `V01A/source-audits.json`, `V00/source-authority.json` |
| V02 | 92/92 historical manifest, four fixed live hashes, 33,792/33,792 sealed files and 1,606,993,133 bytes authenticated; zero unresolved direct bindings | `V02/` |
| V04.AF | `AuthenticatedAnalysisOnlySuccessor` | `V04/historical-compatibility.json` |
| V04.AG | `Passed` / `ComparabilityPassed`; 45 attempts, 44 valid, one preserved failed pilot, 40/40 formal valid | `V04/historical-performance-analysis.json`, `V04/analysis-validation.json` |
| Pre-V05 V04 closure | Separate 22-entry manifest verified, SHA-256 `bd8a7e575503623a0c8bf98739a1a8da3c0cc3bebc44dbdd94075c74e7f92c28` | `../local-validation-20260924-authority038-pre-v05-v04/` |
| V05 | `SuccessorEvidenceBoundForIndependentM08`; classifications and full analysis SHA bound; no performance acceptance claimed | `V05/` |
| Independent M08 | **BLOCKED**, three evidence blockers | `M08/independent-review.md`, `M08/independent-review-receipt.json` |

The first V05 command failed before analysis because the new output directory
did not exist. Its command receipt is preserved. After creating that empty
directory, the identical V05 package command succeeded; the retry receipt and
output are preserved. No evidence input was changed for the retry.

The independent reviewer verified the V05 and V04 bindings but could not
authenticate closure of prior H1 M08 findings from the designated local
record, found two older whole-H1 checkpoint manifests incomplete at their
listed paths, and found no selected suite-by-suite reuse bridge for older
capacity, failure, recovery, count, and startup claims. The full finding text
is retained verbatim in `M08/independent-review.md`. These older manifest
issues do not by themselves show corruption of the current source-27df
40/40 formal series.

`ComparabilityPassed` establishes analyzable paired measurements, not
performance acceptance. The full statistics, including P01/P03 slowdowns and
increased RSS, remain in `V04/historical-performance-analysis.json`.
H1 remains `InProgress`; `M08Passed=false`; `humanGatePassed=false`;
`mayEnterR02=false`.
