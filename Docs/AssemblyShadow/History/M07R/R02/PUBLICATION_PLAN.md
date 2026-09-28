# R02 publication record — batch-G include repair

This cycle is completed by Primary, not work assigned to Local. Canonical GitHub Connector writes are authoritative; no local-only commit or working copy is a handoff.

## Bound inputs and published source

- Local return/base: `4c4f50adfd3a44073d14b107227f399c53ea605c` on `codex/assembly-shadow-r01b-h1`.
- Source/tool repair: `af9ba49127a7e852fed504a55c733c5f6ec5e54e`.
- Matched control: `codex/r02-h1-runtime-control@2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`.
- CI-tested candidate authority: `5c7b9babca7257edb61976f50e3b8a51fc18abd6`.
- Final documentation transport is the later exact remote HEAD in Primary's prompt. It must be metadata-only relative to the source above.

Only three executable paths changed: the host contract runner, its new regression module and the dedicated actual-macOS contract workflow. Native, package, fixtures, schema, Player code and timing remain unchanged. The new design is `G_INCLUDE_REPAIR.md`.

The control merge uses its prior tip plus the new source as parents, retaining the new source tree except for the source-pin file selecting H1 IL2CPP. No branch was force-updated or reset. Candidate metadata includes exact pins, the control tip and updated WEB_TO_LOCAL. `prepare_metadata.pins/targets` generated the JSON values; the live handoff was explicitly authored for batch G rather than using the older batch-F prose template.

## Final verification

Selected authority workflows all passed: R02/Linux/macOS lifecycle 36393519340; actual macOS writer/parser contract 36393519338; scoped legacy 36393519418; immutable M00 origin 36393519352. `PRIMARY_VALIDATION.md` and `G_PRIMARY_VALIDATION.json` record exact artifact sizes/digests, raw member bindings, 3,336 verified source/input files and actual scope.

The final docs commit updates the validation record, current status, task sheet, root README and this publication record only. It does not create a new executable or CI identity. Read back final candidate/control refs and all unchanged runtime/package refs after the last write, verify post-source metadata-only deltas, then issue exactly that tuple. Perform no additional candidate/control write after issuing the prompt during this cycle.

## Local identities and preservation

Candidate workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.
Control workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control`.
Each contains its own demo, HybridCLR, package and IL2CPP owning checkout. Control native/package siblings may remain detached at exact source-target commits. Preserve unrelated worktrees.

Previous publications and A/B/C/D/E/F/G results remain in Git history and retained evidence. No old G build existed to reuse. Run one new 34-cell batch after the exact remote checks, without source edits or weakened prerequisites. Publication is not Player acceptance. R02Accepted=false; mayEnterR03=false.
