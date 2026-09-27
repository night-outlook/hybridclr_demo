# R02 Primary publication protocol and current completion

Current cycle: successor to Local return `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`. Primary publication and bounded host validation are complete; real Local acceptance remains outstanding.

## Reproducible publication sequence

1. Read canonical documentation and Local return, verify four candidate refs and control ref, preserve all existing source and evidence.
2. Prove the intended Connector Git-object/ref write path on a disposable branch; never use the active feature branch for transport testing.
3. Publish executable changes as source anchor C. Do not broaden metadata-only policy to hide source changes after C.
4. Build the control tree from exact C with only its source pins selecting H1 IL2CPP. Preserve old control ancestry and add C as a parent; update control with force=false. This keeps the common source anchor an ancestor without dropping previous control history.
5. Publish candidate source pins, R02 source-targets and live WEB_TO_LOCAL naming exact C and actual returned control HEAD. No provisional commit is authority.
6. Verify fresh source/native/managed/Python and platform host CI. Reauthenticate published bytes, artifacts and source graph. Preserve failed attempts with their actual results.
7. Publish final coordination/validation records as metadata-only successors. Re-read all remote refs and verify final candidate/control non-metadata equality and source ancestry.
8. Render a short final Local prompt from the verified Connector state. It must use the latest candidate transport HEAD, not C or the earlier CI commit. The prepared prompt may not invent filesystem access to the user's Mac.

## Current completion

- Source C: `57a9470bf299af60f88112998c8326c4c013204a`.
- Candidate/control common executable source includes all seven changed workflow/tool/test files.
- Control branch: `codex/r02-h1-runtime-control`.
- Control HEAD: `a379f0b809a5d8af967df06fc83271d90fd84f4c`.
- Control tree differs from C only in `ProjectSettings/AssemblyShadowSourcePins.json`.
- Candidate authority: `96ec97221439ab1ca8964acaf5bf2b5b16e2dcda`.
- R02 workflow 36323257884: Linux primary and macOS lifecycle jobs Passed.
- Scoped legacy workflow 36323257953: Passed.
- Exact artifacts and member hashes: `D_PRIMARY_VALIDATION.json`.

Candidate runtime heads remain `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`. Control uses H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933` with the same HybridCLR/package.

Candidate local roots remain `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repository>`; control roots remain `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/<repository>`. Local must confirm actual filesystem state before execution.

The disposable `codex/connector-smoke-r02-d-20260927-a92d` passed read-back at `f89683801f8c2b9e9c74f06f237e357fab97b523`. It remains because branch deletion is not exposed; it must not be merged or used as a handoff.

## Historical boundary

Earlier R02 publications at sources `06ba01e...` and `82d64ce4...`, their CI runs, and Local A/B/C/D remain historical with their original classifications. This cycle does not retroactively approve those executions, claim to know D's unrecorded post-signal transition, approve a performance SLA, or establish Player runtime acceptance. No non-trivial implementation is delegated to Local and no R03 work is authorized.
