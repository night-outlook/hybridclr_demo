# Current Status — R02 batch-D repair awaiting Local Validation

Input Local return: `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`.

- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain open for measured R02 disposition before H2.
- New executable/tool source anchor: `57a9470bf299af60f88112998c8326c4c013204a`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- CI-tested authority commit: `96ec97221439ab1ca8964acaf5bf2b5b16e2dcda`.
- Matched control: `codex/r02-h1-runtime-control@a379f0b809a5d8af967df06fc83271d90fd84f4c`.
- Candidate runtime pins: HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Primary R02 CI run 36323257884: Passed, including Linux and macOS jobs.
- Scoped legacy-H1 CI run 36323257953: Passed.
- R02Accepted=false; mayEnterR03=false.

## Returned evidence and repair

Batch D remains ReturnRequired with 8 Passed, 3 Failed and 20 Blocked. Both installers exited zero but completion rejected post-signal process identity; the old receipts omitted the rejecting census. The separate transaction native test lacked its generated-input prerequisite. No new controlled Player or D1/D2 measurement was accepted.

Primary now uses kernel birth identity and retains every cleanup observation before policy assertions. Unknown/new instances and changed live commands still fail; known exiting instances are waited for until absent, not treated as clean prematurely. The outer process-group rule and formal timing path are unchanged.

The native transaction probe now depends on a successful candidate build plus authenticated generated header, installed runtime/pins, current graph DLL and supplied Unity baselib. Four independent native tests remain independent. The batch contains 33 required cells and retains all previous coverage.

## Verified Primary scope

Local and CI Python: 165/165. macOS focused subset: 32/32. Native matrices: 70/70 each, with 1,540 and 28,294 checks. Managed host assertions: 102/111/111. Current legacy cases: 384/384; fixed-H1 positives: 6/6. Source inventory: 3,119 files authenticated; seven changed executable blobs match tested bytes. See `History/M07R/R02/PRIMARY_VALIDATION.md` and `D_PRIMARY_VALIDATION.json` for exact artifact bindings and scope limits.

These are host/source results, not actual user Unity/Player acceptance. The exact unrecorded historical D transition remains unknown. Ordinary M00 fixed-byte generation was not reached in D and still needs Local validation.

## Next action

Use the final pushed candidate transport HEAD from the Primary prompt and the exact control above. Run one new unused 33-cell R02LocalBatch-v1: current authority, two controlled build graphs and M00 preparation, eight sidecars, four pilot plus forty formal pairs (88 timing processes), Editor/native/M07/startup/failure/count132/lazy/dense/ordinary/mixed capacity, final authority, complete sealing, then independent R02 stage review if eligible.

Preserve all failed A/B/C/D roots, historical H1 evidence and the older R01 reference. Local must not implement non-trivial fixes, relax identity/hash/source checks, or begin R03.
