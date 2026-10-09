# IR-R03-01 — original S capture omission identity crosswalk

**Status: Source-file identity recovered; semantic inspection of oversized generated code remains NotReviewed.** This is an additive read-only Primary observation. It does not alter S, its Local verdict, prior capture metadata or the independent review's FAIL decision.

Original committed checkpoint: `night-outlook/hybridclr_demo@fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, directory `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready`, Git tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`. This tree was read **recursively via the GitHub Connector** and was not truncated: 18,437 nodes. The earlier read-only capture script omitted files larger than 8 MiB or path components under `.parts/`. Its declared code paths were `Tools/`, `Assets/`, `Packages/`, `ProjectSettings/`, `.agents/`, `.codex/`, `.github/`, active Plan/Architecture/Handoff and the exact original S checkpoint. The old capture's `capture-index.json` itself was not successfully unpacked in the chat host; the exact *identity list below is derived from the original pinned Git tree*, not claimed as an independently recomputed row-by-row comparison to that historical omissions list.

## Two unique oversized generated source blobs

Each file occurs in two source-output paths under the same `batch/projects/resource-complete/Builds/AssemblyShadow/M07/` prefix. These are real generated IL2CPP text sources, not the Native VM hand-written patch and not the original S archive ZIP.

| Basename | Bytes | Original Git blob | Recorded occurrences |
|---|---:|---|---:|
| `Il2CppGenericMethodPointerTable.c` | **11,350,766** | `bf86c8ee7dffe81a23c0b21ccbdc37e7374d414c` | Two: NativeOff and NativeOn backup `il2cppOutput` |
| `Il2CppInvokerTable.cpp` | **8,465,159** | `c5a9c6bb34b7a48c000e7c2f16f1b5d4844a4f86` | Two: NativeOff and NativeOn backup `il2cppOutput` |

The exact four checkpoint-relative paths (all appended to the prefix above):

- `M07-Baseline-R03Completion-29bb3d4a39bf-NativeOff_BackUpThisFolder_ButDontShipItWithYourGame/il2cppOutput/Il2CppGenericMethodPointerTable.c`
- `M07-Baseline-R03Completion-29bb3d4a39bf-NativeOff_BackUpThisFolder_ButDontShipItWithYourGame/il2cppOutput/Il2CppInvokerTable.cpp`
- `M07-Baseline-R03Completion-29bb3d4a39bf_BackUpThisFolder_ButDontShipItWithYourGame/il2cppOutput/Il2CppGenericMethodPointerTable.c`
- `M07-Baseline-R03Completion-29bb3d4a39bf_BackUpThisFolder_ButDontShipItWithYourGame/il2cppOutput/Il2CppInvokerTable.cpp`

**Scope limit:** Other checkpoint entries greater than 8 MiB include native binaries, large JSON, checkpoint transport parts and source metadata; the two names above are two *unique generated C/C++ source blob identities*, not a claim that the historical capture omitted only two files total. The original recursive checkpoint tree contains 34 large blobs, 15 under `.parts/`, and 19 non-part entries. The additional non-part files are not silently categorized as handwritten runtime source.

## Authentication / verification boundaries

The separate committed original-S [provenance auditor](../../../../../Tools/AssemblyShadow/R03IR/audit_s_provenance.py) reassembled the original nine archive parts, authenticated every index entry/member, and compared all 90 original cells to the original execution ledger, including archive members that coincide with generated source files. The successful original-S audit run is [37845000985](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985). It establishes **archive byte identity**, not authorial or codegen semantics.

The GitHub Connector returned exact Git blob identities for both oversized files but **empty decoded content** when asked to read their first lines. No direct line-by-line C/C++ semantic review was performed. The independent reviewer must inspect the materiality and, if necessary, the full source content via a source-bound checkout or a dedicated hash-and-structure scan. Do not convert these blob identities into an invented assertion about every generated method, runtime call edge, or the exact old capture omissions manifest. Reconcile these paths against the actual historical `capture-index.json` before claiming that specific index fully accounted for.

No repo revisions, S/R/Q/P/O/N outcomes, original receipts, readiness gates or Local instructions are modified by this addendum. `IR-R03-01` remains partially remediated and awaits independent re-review; `IR-R03-02` still requires actual Player validation. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`; X02 expansion disabled.
