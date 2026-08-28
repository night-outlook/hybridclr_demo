# M05 independent review record

Status: PASS. Both independent full milestone reviews accepted M05 with no
actionable findings or missing acceptance evidence. The local milestone tag is
`assembly-shadow-m05-types`, applied after this documentation-only closeout.
M06 may start after the main tag/source/artifact audit. M06/M07 and the overall
M02-M07 goal are not accepted here.

## Immutable source boundaries

| Repository | Accepted M04 base | Frozen v6 executable source |
| --- | --- | --- |
| hybridclr | `39eca7a2cc9c8e414f29701629da268e4e213e09` | `7f0da36e1a978abfd22c2c195ecb2741588a5d69` |
| il2cpp_plus | `229f9450c0ebe2293da2bffbfc35f160f18c69de` | `50194392f08815354b6f230f6d0ddd3ec5f9b0f3` |
| hybridclr_unity | `deee300670730fbc4d864e82fa70e7b022581afe` | `b132981fa72f8259efde8e8319029b8812858bcf` |
| demo | `3abeb0bd10c26b24a536fd18a25a79d4f97eb30b` | `09a15e686a4e7581e362175f4aa99d6bde80de55` |

The later offline-only verifier correction is demo
`6f0123839ba1fe01e18c29858b15fefc1cc7b12c`, based on
`fab982fea73dabc5cc54cfd573e38accc064f542`. It changes four Python source/test
files and adds contract/report documentation. The separate metadata pin is
`f880c33f89050f2396e55a9ce8d4d838d3eb6091`. Full frozen and supplemental file
inventories are in [M05-source-inventory.json](M05-source-inventory.json).

The v6 receipts keep their original demo executable pin. Live tooling and the
repeated installation receipt use the newer verifier pin, with the exact source
equivalence and unchanged native ABI proved separately. Both reviewers accepted
evidence commit `7136ed91be8b95a0c43ba597e97547f9a2bfaf22` against the complete
M04 bases and the pairing above. This closeout changes only this review, report
status and contract status; it is not a new executable or verifier revision.

## Completed validation supplied to both gates

- Fresh v6 ON/OFF Unity/IL2CPP builds with actual GUID/native/metadata/linked
  receipts; complete normal and rejected fixture policy plus Editor replay.
- 667/667 full Unity Editor tests with no failed, skipped or inconclusive
  cases. The actual XML and log are retained.
- 267/267 Python tests with no skips, including the preserved real compiler
  inventory. The corrective command/output/source-hash receipt is retained.
- All 19 actual fresh-process Player cases and the complete corrected strict
  CLI pass. The strict receipt has `diagnosticOnly=false`, no missing modes and
  binds the unchanged v6 originals; the driver itself is not the strict gate.
- Final M03, M04, visibility and M05 native suites pass with unchanged recorded
  transitive inputs; every command and the disclosed adapter boundaries remain
  in the receipts. The initial generated-header failure is retained separately.
- Native ON restored and strict current-source installation verification
  passed after narrow definition generation; frozen/current install receipts
  remain distinct.
- All 76 Player files are losslessly archived and 63 supporting artifacts are
  byte-identical copies. [artifact-index-v6.json](Evidence/artifact-index-v6.json)
  maps every copy to its original and hash; the archive has a per-member index.
- Final source-equivalence audit checks 1,158 unchanged non-metadata source
  files plus the exact four-file offline delta, 48 frozen input/result hashes,
  clean paired source heads and original checkout/Editor preservation.
- Independent historical preservation audit passes 13/13 artifacts. No M00-M04
  evidence or frozen M01 bundle was rewritten.

## Bounded corrective-source readiness

The earlier source-readiness reviews and their corrective findings are retained
in the chronological [report](M05-report.md) and `Evidence/source-reviews`.
They explicitly did not accept runtime behavior.

The independent integrity reviewer also returned PASS for immutable demo
`fab982f..6f01238`: exact first-use site plus separate typed/load witnesses,
canonical explicit zero array bounds, and root-only field annotations bound to
actual active DLL field flags/full signatures and matching operations. It
verified the four source hashes, recorded 267-test success, strict receipt and
affected original Player results. This was corrective-source readiness only.
The later full final gate additionally accepted the completed installation
separation, evidence archive and entire managed/package/tooling boundary.

## Completed independent final gates

### Native/runtime and actual Player integration

Reviewer: `m03_transaction_review_gpt56sol_high_1`, independent and read-only.
Verdict: PASS, full assigned M05 native/runtime and Player-integration gate.

The reviewer inspected stable keys/composites, resolution before reflection
cache access, active members, layout/allocation and baseline-use guards,
first-failure sealing, stable exported image identity and macro-OFF behavior.
No actionable defect remained in the complete native/runtime source range.

All 19 original Player results and distinct process records matched. Actual
P03 prefab/scene-first/reload restored the nested shadow value with correct
serialized values and reference identity. T05-04 retained separate first-use
and typed/load witnesses, rejected Commit with 15 and aborted successfully.
T05-09 used the byte-bound rejected DLL, threw during allocation, returned no
object and sealed FailedAfterCommit with 16. Actual OFF ordinary loading,
placeholder, supplementary metadata and duplicate behavior remained supported.

The passive audit matched 126 copied/original artifact hashes, all 76 original
archive members and archive payload, 48 frozen inputs/results, 4,160 native
dependency entries and both actual ON/OFF native libraries/metadata. Source
inventories matched Git. Only the documented four Python paths differ after
the frozen executable source; installation receipts differ only in demo pin,
with all 940 native source hashes identical. The reviewer inspected the actual
strict 19-case, Editor 667/667, recorded Python 267/267 and native receipts.

### Managed/package/tooling/evidence

Reviewer: `m02_integrity_review_gpt56sol_high_1`, independent and read-only.
Verdict: PASS, full assigned M05 managed/package/tooling/evidence gate.

The reviewer accepted the exact ten-API/18-field diagnostic contract, preserved
earlier schemas, finite acquisitions, raw-query proofs, selector propagation
and corrected mutable-output/publication boundaries. Exact file/line inventories
matched Git; 1,158 non-tooling sources were unchanged and the only postbuild
source delta was the documented four Python paths.

All 69 final evidence blobs matched Git; all 63 copies matched originals and
all 76 archive members matched index/original bytes. The reviewer independently
rehashed 1,896 compiler/reference/filtered/linked DLL/PDB receipt entries, 48
frozen input/result files and 13 historical artifacts. Actual Editor XML had
667 passed cases and no other outcomes; recorded Python reported 267 passing
tests without skips. All 19 launch modes/PIDs/hashes matched strict results
with zero exits, including both negatives, P01/P03 resource unload/reload,
native-OFF APIs and ordinary HybridCLR behavior.

The frozen/live installation receipts differed only in demo pin; their 940
source hashes matched, and current installed receipt `d943c205...` matched the
recorded strict ON verification without a demo-source bypass. The postcommit
strict replay retained the exact original `7aca87b2...` receipt hash.

Both gates were passive: source/evidence reads, Git, JSON and hash checks only.
Neither reviewer executed repository code/tests/scripts, launched or controlled
Unity/Players/debuggers, changed files, committed or tagged. Recorded main-agent
validation is not represented as newly executed by a reviewer. Both declared
gates passed even though the generic collaboration setting returned Off.

## Continuation and residual limits

Both reviewers explicitly permit docs/status-only closeout and authorized local
annotated tags after the main exact-delta/source/artifact audit, with unchanged
reviewed sources and artifacts and no new executable review. The only closeout
paths are M05-review.md, M05-report.md and M05-type-contract.md. M06 implementation
starts only after that accepted/tagged boundary. No push or PR is authorized.

The main postcommit audit already proved all 69 evidence-commit Git blobs match
indexed/current bytes, including the ten deliberately retained logs. The strict
19-case replay was byte-identical and installed ON verification passed again.
Tag audit must still confirm those exact three documentation-only changes,
unchanged paired heads, all indexed artifacts and local annotated tag targets.

Acceptance is limited to pinned macOS ARM64 Unity 2022.3.62f2 IL2CPP and the
declared finite acquisitions. Unsupported runtime MVID stays unavailable;
process pointers are diagnostics, not persistent identity. Single controlled
Player/native timings are not production frame-time or managed-GC guarantees.
Resolver-delegate overloads, portable/authenticated deployment evidence and
general whole-program Type-flow safety are not established. Native adapters
remain narrower than the real VM; not every concurrency/platform path is proved.
Native seams and unsigned locally bound receipts remain disclosed. Full M06
execution semantics and M07 asset integration are not accepted by M05.
