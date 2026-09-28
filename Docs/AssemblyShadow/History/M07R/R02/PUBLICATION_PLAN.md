# R02 Primary publication — batch-F repair completion

Status: **Published and host-validated; final documentation transport remains metadata-only.** No publication or implementation work is assigned to Local.

## Fixed publication identities

- Local return base: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.
- Final executable/tool source: `995dbf1003c306a69586f882ff02599db7a9780e`.
- Candidate authority commit: `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Control: `codex/r02-h1-runtime-control@95b85617c92f8ce806f4652d88077936c76c3b8a`.
- Common managed package: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Common HybridCLR: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Earlier E/D and initial R02 publication tuples remain in Git history and historical evidence. They are not current authority and are not silently rewritten as executions of the new package.

## Completed sequence

1. Read the exact Local return and current refs; perform disposable Connector write/read-back tests in changed demo/package repositories.
2. Publish strict native-extension parsing in the package, then its serialization-compatible transient view at final package `b936a495...`.
3. Publish demo integration repairs, producer/parser tests, schema proof and Editor tests. Final source freeze is `995dbf1003c306a69586f882ff02599db7a9780e`.
4. Advance the control without force using a tree based on the complete frozen source and explicit source ancestry. Its tree differs from the source only in `ProjectSettings/AssemblyShadowSourcePins.json`; both roles use the same new managed package.
5. Generate/publish candidate pins, exact R02 source-targets and `WEB_TO_LOCAL.md` at `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`.
6. Verify selected CI at that exact authority: R02/Linux/macOS 36372371088, legacy 36372371077 and fixed-origin 36372371129 all Passed. Download and authenticate four artifacts and their source/raw bindings. Detailed identities and counts are in `PRIMARY_VALIDATION.md` and `F_PRIMARY_VALIDATION.json`.
7. Publish the final validation/status/task/design documentation without executable changes. Verify the source-to-final and CI-to-final deltas, final candidate/control/package/runtime refs, and remote read-back before issuing Local's prompt.

The final commit cannot name itself in its own content. The exact final transport HEAD is supplied by the verified Primary prompt; never substitute the source or CI commit for it. `prepare_metadata.py prompt` may be used with actual source-bound checkouts, or Primary may render the same contract from independently verified Connector refs.

## Continuing publication rules

Every later executable change requires a new source freeze, common control pairing, candidate authority and affected tests. Do not broaden `shadow_tools.metadata_only`, mix old/new package builds, force-push control history, or weaken source checks. Local only fetches the published tuple and executes the supplied batch; it does not invent missing pins or publish Primary fixes.

The final handoff is for one fresh 34-cell batch. H1 remains PassedWithExplicitDeferredRisk; this publication is not Unity Player acceptance, independent stage approval, performance/RAM approval or permission to enter R03.
