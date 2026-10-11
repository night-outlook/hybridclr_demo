# IR-LOCAL-CUSTODY-01 — bounded Primary custody disposition (2026-10-09)

**Owner: Primary Implementation. Decision: a scoped historical-custody *loss exception* for one new, isolated IR-R03-02 focused validation, conditional on complete read-only authentication. This is NOT recovery and NOT a finding closure for original S live source/build-process custody.** No Local or product runtime was executed by Primary. Original independent R03 review: **FAIL**; re-review NotRun.

## Exact C evidence and investigation

C source execution demo: `e6f918bf6c756251982eef47f255eaa71b11e1d4`. C Local publication: `36b9828d62bb81d98e81d055871a9540fe116276`, all on `codex/assembly-shadow-r01b-h1`. Authoritative checkpoint: [C custody-blocked evidence](../../local-validation-20261009-ir-r03-02-c-custody-blocked/README.md), especially `preflight/CUSTODY_FAILURE_ANALYSIS.json`, raw BEFORE/AFTER and `preflight/NATIVE_LIVE_CUSTODY_LIMIT.json`.

- Both full strict C audits: 416,844 expected; 339,367 still present and verified; **77,477 Missing**; 0 changed. The missing **path + expected SHA-256 + ENOENT error** rows match exactly before/after, unique count 77,477. The previous map SHA-256 is `133cba8a9b54b74a9909c6da6948838f8f604afea47bc61bdee88f45c22df0e8` (127,296,143 bytes, four Git parts).
- All missing files are in **12** retained S `projects/<role>/Library` and `projects/<role>/HybridCLRData` subtrees. No S sealed-index/archive member overlaps them. These are **not merely empty caches**: absent files include Unity build reports, stripped native source, generated IL2CPP and four installed-native roots.
- The exact original S sealed artifact SHA-256 is `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, 587,907,380 bytes, 15,712 indexed files / 15,713 archive members. C verified the five top-level artifacts and all indexed members. None of the missing 77,477 files can be restored from that archive.
- Four *historical S* schema-2 native build receipts still exist; each `installedNativeRoot` is missing: candidate-debug, candidate-off, candidate-release, reference-release. Historical S used `il2cpp_plus@1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, **not** the new candidate `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`. Do not fabricate a historical root by installing the present source or regenerating caches.
- Actor, deletion command, deletion date/time within the B→C interval, a byte-identical surviving external copy, and complete original S live-installed-native recovery are **Unavailable/NotProven**. Primary has not touched the user's macOS evidence roots or reclaimed data.
- C storage *separately* Admitted: 83,657,576,448 bytes versus 68,719,476,736 required; eleven allocation/sync/readback probes Passed, but this historical space is **not** a reservation or future admission. C remained `CustodyBlocked`, 0 Unity launches, 14 cells/3 builds/4 Players NotRun.

**Historical findings remain unchanged**: C and full strict S retention are `CustodyBlocked`; original S local result remains 90 Passed / EvidenceReadyForPrimaryReview with weakened ability to reauthenticate live native provenance, not current evidence custody `Passed`. Original independent full-stage R03 remains FAIL. R remains staged and its restore Failed. Q/P/O/N, all A/B/C local returns, failed performance/warm certificates, original C missing rows and previous provenance withdrawals remain intact. No historical result or protected map has been rewritten, rebaselined or declared Passed.

## Exact scope of exceptional admission

One fresh **D** Local attempt may treat **the unchanged, fully pinned C missing set as an explicitly acknowledged historical custody loss** solely for a **new independent** 14-cell / three IL2CPP-build / four-Player IR-R03-02 observation, provided every other prerequisite passes. This is a Primary engineering exception to *historical cache availability*, **not** to the source/CI/fixture/S sealed-evidence/read-only custody verification or 64 GiB/20 GiB storage policies.

Strict historical custody is **still Blocked**. The only permitted successor evidence result is **ScopedHistoricalLossStable** and must always include `originalStrictCustody=Blocked`, `strictFullHistoricalCustodyAccepted=false`, and `sourceBuildProcessProvenanceRestored=false`. This exception cannot be reused for original S full-stage reacceptance, release qualification, historic SDK/native identity, P05 acceptance, H2, generic/initializer witness coverage, previous missing file restoration claims, performance SLA or the independent Human Review Gate.

**The new D build MUST use new directories and pinned current IL2CPP+ sources, not existing S Library/HybridCLRData or historical S native installation.** Native and test artifact origins remain separately proven. If the target runner or Unity build would consume any missing S caches/native roots, abort rather than proceed under this exception.

## Fail-closed verification contract

The checked-in [verify_scoped_custody.py](verify_scoped_custody.py), with [negative tests](test_scoped_custody.py), is **Primary-owned, Docs-only supplemental code**. It does not change the frozen Player or product sources. With the immutable C checkpoint it authenticates:

1. Raw C BEFORE/AFTER reports against exact SHA-256, all 77,477 exact missing path/hash/error rows and their 12-group census; C `CUSTODY_FAILURE_ANALYSIS` and four native receipt limits.
2. Four exact ordered 127 MB C map parts against their individual byte lengths/hashes and whole-map SHA-256; exactly 416,844 original frozen expected path/hash entries; no new or weakened map.
3. Every still-present protected file independently by SHA-256 and regular-file/no-symlink ancestry, and **every frozen missing path still absent**. Any newly missing file, mismatched byte, unexpected restoration, symlink, count/map discrepancy, invalid original receipt, error, or interrupted/partial scan => **Blocked**. It does not claim the absent historical content is recovered.
4. A unique read-only *before* receipt and a second full *after* audit in the fresh external D preflight directory. The second audit must pass even if runtime fails, to the extent possible; preserve original runtime outcome and classify post-run custody defects independently.

Synthetic negative controls (changed file, new missing file, restored formerly missing file, symlink, parent symlink, malformed/duplicate errors, and positive stable-loss) are in the adjoining tests. Primary's isolated environment executed ten synthetic tests; **full 416,844-file/macOS validation remains Local-owned NotRun**. Do not treat host unit tests as a real D custody scan.

The verifier returns `ScopedHistoricalLossStable`/exit 0 only for **339,367 byte-verified still-present files and exactly 77,477 unchanged missing identities**. It leaves the historical strict result `Blocked` in the output. Any alternative count or missing-set difference returns Blocked/exit 2 and requires Primary disposition; **do not automatically expand the exception or silently accept partial restoration**.

## Fresh D handoff and limits

Follow [D focused procedure](D_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md), and use the separately committed `Handoff/WEB_TO_LOCAL.md` and final Primary four-SHA prompt. D uses fully unused external roots ending `20261009D-custody-scoped`; C/A/B paths and source/fixture evidence remain read-only. The core test harness and all current runtime code remain unchanged. The current managed API compile evidence is [CI 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633), 0 errors / 13 warnings, **Unity API stubs only**.

Local must stop unless source/remote, API, original 15 S Git fixtures, retained Q/R and original S seal, ten supplemental tests, 64 host Python tests, 69 native policy checks, exact pre-custody verifier, and **fresh storage admission** all qualify; then exactly one D execution, no retries, with post-custody audit. This is NOT blanket authorization to bypass any new failure. Report all 14 cell statuses and three builds/four Players factually, never synthetic Passed cells.

**No stage advancement:** R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter expansion disabled. Preserve the independent FAIL and require a distinct independent re-review/explicit human gate. Original S native-root loss is an explicit **unaccepted risk** for full-stage provenance review, regardless of any future focused D Player success.
