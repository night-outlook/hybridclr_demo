# Static Review — V04 Controlled Workflow Boundary Repairs

## Verdict

**PASS for Primary → Local Validation handoff**, subject to real Unity/IL2CPP controlled-workflow execution.

Reviewed build-input source anchor: `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.

This review does not establish performance acceptance, V05 completion, independent M08 PASS, or Human Review Gate approval.

## Finding 1 — ProjectSettings exact-byte drift

The Local evidence shows the controlled Native ON build itself succeeded, then the next source guard rejected `ProjectSettings/ProjectSettings.asset` because Unity's semantic restore changed its serialization.

The repair is correctly placed in the outer Player-stage transaction rather than weakening the guard or relying on `R00ControlledBuild.RestoreSettings`. This is required because the same current coordinator must operate against the protected historical reference project.

The helper now snapshots/restores both tracked inputs and attempts recovery for each even if another recovery item fails. Post-build bytes are retained before overwrite. Exact SHA equality is required before return.

## Finding 2 — nested native verifier inherited outer authority

The native provenance subprocess deliberately passes `--skip-demo-source`; the top-level M07 verifier deliberately rejects that option when outer workflow authority is active. Both behaviors are individually correct.

The repair scopes only the nested child process by removing the two M07 authority variables from that child's environment. It does not mutate the parent environment and does not alter `verify-installed-runtime.py`. Therefore the outer coordinator's source/workflow authority remains fail-closed.

## Regression review

Coverage now exercises:

- PowerShell parameter binding for all four labels;
- real production helper restoration of `link.xml` and `ProjectSettings.asset` without Unity;
- success and failing-stage recovery paths;
- per-input receipts and original failure preservation;
- source contract for child-only environment scoping;
- retained verifier rejection of caller demo-source skipping under M07 context;
- Unity Editor source-contract assertions.

## Scope

Functional changes are limited to:

- `Tools/AssemblyShadow/Invoke-M07Build.Core.ps1`;
- `Assets/AssemblyShadowDemo/Editor/H1BuildInputProvenance.cs`.

Other changes are tests/CI/authority metadata. The three runtime repositories remain pinned unchanged.

## Required empirical closure

Local must freshly prove:

1. V00 candidate/reproduction/protected authority;
2. current source/tool regressions and broad EditMode;
3. protected profile-1 controlled Native ON + Native OFF with two-input exact restoration each;
4. candidate profile-2 controlled Native ON + Native OFF with nested provenance succeeding;
5. post-workflow runtime/source verification;
6. current-anchor old-Player rejection;
7. strict build-map freeze and `ComparabilityPassed`;
8. preregistration, all pilots, all formal samples, analysis;
9. authenticated checkpoint;
10. V05 and genuinely independent M08 only if V04 closes.

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.
