# R02 publication record — batch-H successor

## Completed source publication

The Connector published native commit `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` on `night-outlook/il2cpp_plus:codex/assembly-shadow-r01b-h1`, followed by demo source `a81bb0d7b886fe941ba4b132296a30dcf4a319cc` on `night-outlook/hybridclr_demo:codex/assembly-shadow-r01b-h1`. The source incorporates input Local return `d33792957303488e03529c945ac01ce0eedd660b` without editing its evidence.

The matched H1-runtime control `21c689732cd8087f8ee8fdce4e52a8f2a655f722` on `codex/r02-h1-runtime-control` includes `a81bb0d7b886fe941ba4b132296a30dcf4a319cc` as an explicit additional parent and uses that exact tree with only `ProjectSettings/AssemblyShadowSourcePins.json` changed. Control native remains `6be7f38bec2fa4677d24efc1a4a1294240789933`; HybridCLR/package match the candidate.

Candidate metadata authority `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d` binds the new source and control. It changes only the pin file, source-target metadata and WEB_TO_LOCAL. All four selected workflows at that authority passed: 36431496003 (R02), 36431496157 (actual macOS contract), 36431495940 (legacy), 36431495954 (M00 origin). Their downloaded artifacts, source inventory and raw bindings are recorded in `H_PRIMARY_VALIDATION.json`.

## Final transport contract

The final documentation commit records validation/task/status completion. Its delta from the source anchor must contain only permitted metadata under unchanged `shadow_tools.metadata_only`; no executable source may change after the selected validation without a new freeze/control/validation cycle.

The final response must read back all four candidate remote refs and the control refs after the last write, then supply that exact candidate transport HEAD in the Local prompt. Do not reuse source/CI HEADs or an earlier chat tuple as transport authority. Stop on later remote movement rather than weakening the exact-ref preflight.

## Boundary

Primary publication and host CI do not accept R02 or approve R03. The next Local cycle is one fresh 34-cell batch with new-native candidate builds and source-matched H1 control, full regressions and sealing. H1 remains PassedWithExplicitDeferredRisk; D1/D2 require measured disposition before H2. Preserve all historical results, raw inputs and failed attempts. Rollback requires an explicit complete new tuple, never mixed pins or destructive reset.
