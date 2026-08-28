# Actual v3 linked diagnostic schema

Independent read-only inspection by
`m03_probe_hardening_gpt56sol_high_1` used installed Mono.Cecil against the
immutable Player input snapshot:

`_temp/AssemblyShadow/M03PlayerInputs-46ca80b014224dac8bb6a04289d6f568`.

| DTO | Prelink fields | Linked fields |
| --- | ---: | ---: |
| AssemblyShadowDiagnostics | 23 | 23 |
| AssemblyShadowOrdinaryAssembly | 2 | 2 |
| AssemblyShadowOrdinaryClass | 5 | 5 |
| AssemblyShadowDiagnosticAssembly | 7 | 7 |
| AssemblyShadowDiagnosticEvent | 5 | 5 |
| AssemblyShadowBaselineUse | 6 | 6 |

All 48 field names, types and order match. All 14 fields lost in the v2 Player
are present. SHA-256 of the compared HybridCLR.Runtime DLLs:

- Prelink: `29fc0bbd45517f8d3339cd062c17ae20073b79455c38d65379328b8d9b756785`.
- Linked: `7d312c5f9c948e80d9ddd67f1a231dfa232a2713e2b867fe067398838e583d69`.

The normal v3 build also passed the snapshot-bound production schema gate.
This metadata evidence does not by itself establish runtime transaction or
serialization acceptance; those require the actual Player matrix.
