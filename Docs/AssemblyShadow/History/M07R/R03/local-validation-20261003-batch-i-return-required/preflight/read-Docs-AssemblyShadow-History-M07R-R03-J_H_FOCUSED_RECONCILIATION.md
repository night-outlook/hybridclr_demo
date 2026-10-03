# R03 J — batch H focused evidence reconciliation

Primary Implementation disposition, 2026-10-02 UTC. **Focused evidence reconciliation, not independent full-stage review, R03 acceptance, or Human Review Gate approval.**

## 1. Disposition

**H is reconciled as a Passed, source-bound focused validation result.** The immutable Local result remains `EvidenceReadyForPrimaryReview`, 37 Passed / 0 Failed / 0 Blocked, seal Passed. No new focused defect was reproduced or found by the checks described here. This disposition closes the current rejection-observation repair loop in its tested scope; it does not close all R03 requirements.

Read the original [Local report](../../../Handoff/LOCAL_VALIDATION.md), [return](../../../Handoff/RETURN_TO_WEB.md), and [H checkpoint](local-validation-20261002-batch-h-evidence-ready/README.md). Those files and all A–G checkpoints remain unchanged by this reconciliation. G's five Failed rejection cases, missing probe observations and code-16-to-15 transition remain historical failures. Four H natural controls retain **Failed unisolated warm certificates**, although their diagnostic contracts Passed.

Current owner is **Primary Implementation**. There is no active Local execution assignment. The completed H command is retired from the live handoff; no H rerun, new runtime root, new Player execution or later milestone is authorized by this record. The next work is [remaining R03 completion](../../../Plan/stages/R03-remaining-completion.md).

## 2. Three different source identities

All four branches are `codex/assembly-shadow-r01b-h1`. Owning checkouts are beneath `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, with directory names matching the repositories.

| Identity | Exact revision |
| --- | --- |
| Demo actually executed by H | `2007c5dbd3dcf535706688e6595700e3ba26a11e` |
| Local publication containing H evidence | `3a9d51a9bb42b12bf29dfd6e0d7d12956ae04a68` |
| Primary read-only auditor tested in this cycle | `3139b08f71dab8f4138b4127d6b0eb7a2fd0e4e1` |
| HybridCLR executed and unchanged | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| Managed package executed and unchanged | `120bb01be680cec0375002a0823552d66d34b84c` |
| IL2CPP executed and unchanged | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

H's product/tool CI anchor was `9d70494c97e4efc9597a3e071f63c1489c6ac396`. The executed demo, Local publication and subsequent reconciliation revisions are not interchangeable execution claims. No product, original runner/verifier, fixture, package or native source changed in this reconciliation cycle. Its only executable additions are a separate read-only auditor and CI workflow.

The auditor verified that the original `Tools/AssemblyShadow/R03` tree is identical at the executed revision and Local publication: Git tree `e386116ca6b95694303275f53e0b6ef1c0598464`. It imported those original verifier bytes, not the current reconciliation code as a substitute acceptance policy.

## 3. What H actually establishes

H ran exactly once, PID 60711, UTC `2026-10-02T15:42:35.301026+00:00` through `2026-10-02T15:48:47.419720+00:00`. The recorded platform is Unity 2022.3.62f2, StandaloneOSX/arm64, macOS 26.5, SDK 8.0.318. No broader platform support is inferred.

| Focused requirement | Reconciled H result and boundary |
| --- | --- |
| Exact-source execution and native provenance | Four fresh build roles Passed, with schema-2 installed-root bindings and complete app inventories. This is not a new production deployment capability. |
| Editor contracts | All 754 explicitly selected identities Passed with zero skips, including all 35 R03 admission/method contracts and the true-cycle regression. The excluded frozen M01 asset contract remains NoCoverage. |
| Runtime contracts | All 19 main Player cases and four separate natural-control contracts Passed. Expected rejections remain successful negative contracts, not successful patch publications. |
| R03-LG-001 | All five negative cases retain Validate16/state8/unpublished through a capacity -2 result, two complete reads and final diagnostics. Captured identities and retained rows are complete/equal; terminal transaction and entire recovery are unchanged. **Verified repaired in this focused H scope.** |
| Warm certificate and producer attribution | All six isolated main witnesses retain zero all-thread repeated exact-loop proof/layout/workspace work and at least 10,000 hits/baseline checks. All four natural controls identify the ArrayPool Gen2 finalizer path and retain Failed unisolated warm certificates. |
| Primitive append | Full C07 and its paired control establish the positive 24-to-32-byte layout witness, retained offset16 and private eight-byte tail at offset24, without baseline business initialization. This is not arbitrary reference-field or Unity resource compatibility. |
| Method identity and guards | Moved-slot reflection/delegate mapping and old-AOT rejection controls Passed. This does not cover every generic/modifier/interface/stack-trace or old-handle path. |
| Graph semantics | Direction reversal and genuine target-cycle controls Passed. Host G03–G06 also cover cumulative installation-baseline/deleted-edge/ordinary-role cases. Full production-entry and multi-version Player coverage is not inferred from those host contracts. |

The finite producer lease is test-only scheduling isolation. Its drained/finite witness does not prove that an unisolated production process has no unrelated cold work. It can indirectly delay queued finalizers and is not a production GC policy, performance acceptance technique or SLA. Later measurements must distinguish this diagnostic profile from the production profile.

The original G/H ArrayPool identity is empirical in those runs. No H identity is assigned retrospectively to E/F. A retained negative layout row is not necessarily the first failing type; the original `failingRowIdentified=false` remains unchanged.

## 4. Read-only Primary authentication and replay

New files are `Tools/AssemblyShadow/Reconciliation/reconcile_r03_h.py` and `.github/workflows/r03-h-reconciliation.yml`. Final auditor source `3139b08f...` passed workflow **37077636830**. It checks an exact, clean checkout of the H publication and writes only to an unused external directory. It neither launches Unity/Players nor executes commands embedded in evidence.

Completed checks:

- 13 auditor path/JSON/inventory self-checks.
- Exact checkpoint membership and SHA-256 authentication of **2,007 manifest-listed publication files**, plus the manifest itself. This count includes publication support files and is distinct from the original seal's indexed-file count.
- Authentication of all **1,901 originally indexed files** and reconstruction of all three exact archive parts into a separate temporary file. The full 164,177,597-byte archive hash and all **1,902 regular archive members** match the original seal. Only the auditor's own temporary reconstruction was removed afterward.
- Equality of all 37 cell files, result and execution-ledger records; preserved false stage/gate/expansion flags; exact four-repository entry/final source tuples.
- Original 83 command receipts' schema, lifetime flags, named negative exits and retained stdout/stderr hashes: 80 exit0; only 0048/0050/0055 are the expected exit1 compiler controls. This re-audits receipts, not the inaccessible original macOS processes.
- Replay of the **original** `verify_raw` over every original request/raw/launch pairing. All **23 recomputed verdict objects exactly match** the stored source-bound verification receipts. All PID/run nonces remain unique. Five rejection subchecks, six strict isolated warm subchecks and four Failed unisolated control certificates retain their original classifications.
- Replay of the original Editor verifier over the real H XML and source-bound scope: all 754 exact identities Passed; no missing/extra/skipped case.
- Published checkout remained clean and the checkpoint manifest unchanged after auditing.

The first audit passed before its command-lifetime projection was tightened to the actual named fields. The final run above additionally requires `R03OwnedCommandV1`, schema2, no timeout, no pre/post-cleanup process group, no launch error/interruption/cleanup error and matching stream hashes. No original H expectation or record was changed to obtain that result.

Primary downloaded and independently authenticated the final audit artifact: **90 indexed output files / 91 ZIP files**, every size/hash and exact nonduplicate safe membership. Artifact ID **11257725069**, size **583479**, SHA-256 `0a181c4a1cb3161d9eb650081e5b0223b20379ceaf1cac84fe14c591137abc85`. The structured result is bound by audit.json SHA-256 `b535bb0892856cfe7e27ef8cda4ea1caca8349e6b43eb5fad4fb9f684cc3dce6`; provenance.json SHA-256 `cc41063fcbd767f02b5402fc268124eda7106d4103a0223f6e26ece918aa8423`. See [J_H_EVIDENCE_AUDIT.json](J_H_EVIDENCE_AUDIT.json).

**Classification: ReusedAuditedEvidence. New Editor runs: 0. New Player runs: 0.** This audit checks custody, source binding, declared semantics and consistency; it is not an independent review of the entire design or proof that all original verifiers are complete. Local's 9,000 earlier custody bindings remain attributed to Local; Primary did not access or re-audit those prior macOS live roots.

## 5. Immutable H evidence anchors

| Original H artifact | SHA-256 |
| --- | --- |
| LOCAL_BATCH_RESULT.json | `fe3eb7e1e767f54d58b0702d03890c2b5d46aff55be8adb67af1f749d06895a8` |
| BATCH_EXECUTION.json | `81dabf1052f63da49ff8c017757e90b08e5504f445c60e1f553111a848b5fe80` |
| evidence-index.json | `ef0e33ef8efa345bca758539646a8d81aefd2d16b5a1e0b139f78234332d1a28` |
| evidence.tar.gz | `dd7adb4de12aa7203c69f993e57ebbde49e4f223edfd1179a2945e3d55f6e5cd` |
| seal-receipt.json | `b47641a234507290872ca04c5bd07973bd017d2a60f9173aea394566b4cded43` |
| Checkpoint MANIFEST.sha256 | `c1f499235432aba0093b5d21e3aae4df7a0f38288b34d9d7b7aa73d98436bb06` |

H's retained live root remains `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002H-rejection`. Its publication preserves original archive parts; it must not be rerun, recompressed or rewritten.

## 6. Reconciliation against the normative R03 plan

This table distinguishes evidence already present from remaining obligations in [R03-evolution-semantics.md](../../../Plan/stages/R03-evolution-semantics.md). It does not replace that file's exit conditions.

| Plan section | Existing evidence | Remaining obligation |
| --- | --- | --- |
| Step1: three real counterexamples | Independent DLL bytes, reference/candidate graph checks, reference late-layout/slot behavior and candidate Player controls | Preserve the exact pairings for full-stage review; do not repeat already reliable reproduction merely to produce another label. |
| Step2: NativeLayoutAdmissionV1 | Conservative byte-level screen, prepublication rejection and positive primitive layout; safe rejection observation now verified | Review supported-shape coverage and resource/domain limits on the full required fixture; do not generalize one private primitive witness. |
| Step3: PureInterpreter eligibility/extension Gate | Expansion remains disabled; focused safety baseline now predictable | **Earliest unfinished numbered implementation step.** Establish auditable eligibility and the qualification decision before any structural expansion experiment. No blanket exemption or silent omission. |
| Step4: logical member identity vs compatibility | Moved-slot mapping, real reflection/delegate and old-AOT guards; 35-case host/Editor corpus | Broader real runtime generic/constraint/byref/modifier/interface/delegate/stack-trace paths and supported old-handle rejection boundaries. |
| Step5: safety and load graphs | Reversal/true-cycle witnesses, existing shared target-load algorithm checks | Bind existing generation-plan/manifest call chains and complete target inputs to the wider integration evidence; no reinvention of working algorithms. |
| Step6: cumulative closure and roles | Host G03 installation-baseline/v1/v2/rollback, G04 deleted edge, G05/G06 ordinary-role cases Passed | Complete source-bound production-entry/multi-version runtime pairing and role boundaries; never use the previous patch as installation baseline. |
| Step7: regressions | Focused 754 Editor, 23 Player contracts and host checks | M01 plus impact-selected P01–P05/old-resource, broader runtime, startup/capacity and applicable measurements; preserve every NotRun/NoCoverage distinction. |
| Independent review/delivery | Primary repair self-reviews and this read-only audit | Independent design→plan→implementation→evidence stage review, finding closure, then human-initiated H2. This record performs neither review. |

## 7. Resource scope correction and next ownership

M01 is **NoCoverage in H's isolated fixture**, not proof that the source assets are missing from the repository. At the Local publication, `Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab`, `VersionedData.asset`, and `Scenes/Business.unity` and their .meta files exist. Their presence alone does not establish frozen-resource compatibility. Primary must authenticate the original resource/dependency/GUID/bundle lineage and provision a resource-complete isolated regression project before changing the Editor selection. Do not invent GUIDs or flip H's excluded case to Passed.

The next Primary work packages and evidence requirements are defined in [R03-remaining-completion.md](../../../Plan/stages/R03-remaining-completion.md). No source change is being delegated to Local. A new exact-source Local command will be issued only after the next implementation/test fixture is prepared and checked; this completed batch is not a reason to repeat H without new coverage.

R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Full R03 is **not ready for Human Review Gate**. M08A and later formal milestones remain blocked by H2. R02's explicit deferred CPU risk and original H1 RSS risk remain visible; this diagnostic pass does not waive them.

## 8. Publication and rollback

All four feature heads were read through the Connector. Only demo audit tooling and coordination documents change in this cycle. Demo write/read-back smoke Passed on disposable `codex/connector-smoke-r03-h-reconcile-20261002`, commit `a780b9f067a93bddc44c441baab0844af76f1226`; that branch is retained and non-authoritative. Unchanged external repositories are not represented as new writes or new runtime validation.

The final documentation commit updates README, CURRENT_STATUS, the R03 stage header, this reconciliation/evidence record, the remaining-work plan and WEB_TO_LOCAL. It must not change the normative R03 body, Local reports or historical checkpoints. Any rollback is a new coherent coordination revision; it does not change H's original source tuple, raw evidence or empirical result.
