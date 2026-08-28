# M05 independent review record

Status: pending both independent full milestone reviews. Implementation and
required validation are complete; this record does not yet accept M05 or open
M06. The review targets are committed evidence, actual immutable artifacts and
the complete M04-to-M05 source ranges, not the summaries alone.

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
equivalence and unchanged native ABI proved separately. The evidence-only
review target will be supplied as an immutable commit in each review request
and recorded in the closeout; it is not a new executable revision.

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
The final gate must additionally inspect the completed installation separation,
evidence archive and the entire managed/package/tooling boundary.

## Required independent final gates

### Native/runtime and actual Player integration

Assigned reviewer: `m03_transaction_review_gpt56sol_high_1`.
Verdict: PENDING.

Inspect the complete native/runtime changes, TypeKey/composite construction,
resolve-before-cache ordering, active members, class-init/allocation guards,
private staging and stable exported image identities with physical ownership
unchanged. Check real P01/P03 identity/interface/member/resource evidence,
precommit-use and incompatible-layout failures, ordinary/native-OFF behavior,
source hashes and final native regression inputs.

### Managed/package/tooling/evidence

Assigned reviewer: `m02_integrity_review_gpt56sol_high_1`.
Verdict: PENDING.

Inspect public API/DTO/schema contracts, raw-query and reflection acquisition
policy, selector propagation/ownership, exact compiler/linked/resource proofs,
all strict result conditions and the independent Python specialization. Check
actual build metadata and input graphs, preserved original observations,
archive/copy consistency, frozen-v6 versus current-tooling pins, tests, restored
installation, historical preservation and source/file/API inventory.

Both reviewers are passive and read-only: source/evidence reads, Git, JSON and
hash checks are allowed. They must not execute repository code/tests/scripts,
launch or control Unity/Players/debuggers, change files, commit or tag. They
must inspect actual evidence and return PASS, FAIL or BLOCKED with concrete
findings and limits. Recorded validation is not represented as newly executed
by a reviewer. The declared two-gate requirement remains mandatory even when
the generic collaboration setting is Off.

## Continuation and residual limits

Only both full PASS verdicts permit metadata-only closeout and authorized local
tags after a final exact-delta/source/artifact audit. M06 implementation cannot
start until that accepted/tagged boundary. No push or PR is authorized here.

Acceptance is limited to pinned macOS ARM64 Unity 2022.3.62f2 IL2CPP and the
declared finite acquisitions. Unsupported runtime MVID stays unavailable;
process pointers are diagnostics, not persistent identity. Single controlled
Player/native timings are not production frame-time or managed-GC guarantees.
Native seams and unsigned locally bound receipts remain disclosed. Full M06
execution semantics and M07 asset integration are not accepted by M05.
