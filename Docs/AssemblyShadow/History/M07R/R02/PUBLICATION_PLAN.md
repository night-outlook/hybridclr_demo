# R02 Primary publication — batch-F finalization complete

Status: **Published and host-validated; final documentation transport remains metadata-only.** No publication or implementation work is assigned to Local.

## Fixed identities

- Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.
- Recovered integration repair: `d43663e9ff96a9249d5e7bbf1e02bbd7e40f552b`.
- Final executable/tool source: `1642392278a97bc9348195e35ec5d1b7fb6fa530`.
- Candidate authority: `4a6a8d604e27aa5e3175149c4df0170b8ec09b05`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Control: `codex/r02-h1-runtime-control@028ad68fa25a531be07f11f1fdcc417842f98ab4`.
- Common managed package: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Common HybridCLR: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Earlier publication tuples and test results stay in Git history and historical records; they are not silently relabeled as this source.

## Completed sequence

1. Read Local F and remote successor repair; authenticate the prior source export and rerun its 203-test Python suite. Read-only runtime/package refs matched the published repair.
2. Find and correct the Editor acceptance gap: enforce the three new schema tests plus two original probe tests. Seven host acceptance tests added; new source freeze is 1642392278a97bc9348195e35ec5d1b7fb6fa530. No runtime/package change in this finalization.
3. Pass demo-only disposable Connector write/read-back at 7664740f26680d9b89223962413cc93a2eab0aaa on codex/connector-smoke-r02-f-coverage-8d72. This is not a source/handoff commit and must not be merged.
4. Advance control without force from 95b85617c92f8ce806f4652d88077936c76c3b8a, using the frozen source tree and explicit source parent. Control 028ad68fa25a531be07f11f1fdcc417842f98ab4 differs only in the source-pin file. Both roles retain the same new managed package.
5. Publish candidate pins, source-targets and WEB_TO_LOCAL at 4a6a8d604e27aa5e3175149c4df0170b8ec09b05.
6. Verify selected CI at that authority: R02/Linux/macOS 36387357718, legacy 36387357712 and fixed-origin 36387357717 all Passed. Download/authenticate four artifacts, 3,278 source files and 137 nested bindings. Exact results are in PRIMARY_VALIDATION.md and F_COVERAGE_VALIDATION.json.
7. Publish final metadata only, then verify source-to-final delta and exact candidate/control/package/runtime refs before issuing Local's prompt.

A commit cannot name itself in its contents. The exact final transport HEAD is supplied by the verified Primary prompt, never replaced by the source/CI commit. The prompt may be rendered from independently verified Connector reads; local checkouts are not invented.

Every later executable change requires another source freeze, matched control, authority update and affected tests. Do not broaden shadow_tools.metadata_only, mix old/new source or package builds, force-push control history or weaken checks. Local fetches the complete published tuple and runs the existing 34-cell batch. H1 stays PassedWithExplicitDeferredRisk; R02 runtime/stage acceptance and R03 entry remain false.
