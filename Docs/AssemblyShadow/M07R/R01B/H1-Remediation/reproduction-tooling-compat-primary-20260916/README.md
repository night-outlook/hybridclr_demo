# R01B H1 — Reproduction Tooling Editor Compatibility Repair

## Status

Primary Implementation completed for the Local Validation blocker returned at `cef1ec761e268ebbb699cc16b6ab037d7bc5a482`.

Authoritative candidate source / implementation anchor:

`3242b071540278510ea4ae287c70e37fc4c60340`

Reviewed reproduction tooling successor:

`codex/assembly-shadow-h1-count-repro-tooling` @ `ba8fee33753a5ebc215b7a98739e343d8e05572e`

Protected behavior/runtime identities remain unchanged:

- protected reproduction head: `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`
- unfixed reproduction behavior source: `4e3d2035991ab5629265ac663e61bcb2ca62828b`
- reproduction native: `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`
- shared package: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- shared IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`
- performance reference: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`

## Local finding

The first authenticated tooling successor `0c9c2508d94a097dff50028212a01695c8e29c60` combined the current schema-3 `H1ManagedSourceProvenance.cs` bridge with the protected historical test `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs`.

That test referenced the removed nested `H1ManagedSourceProvenance.Capture` API and caused Unity compilation to fail with CS0426 before any reproduction Player build. Local correctly stopped instead of expanding the tooling allowlist.

## Selected repair

Delete the obsolete historical test and its `.meta` in the **tooling-only successor**, matching their absence from the reviewed candidate source anchor. No replacement test is introduced into the reproduction project because the candidate source no longer carries that historical test surface.

The exact new tooling changes relative to protected head are therefore:

- prior nine validation blob replacements remain unchanged;
- delete `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs`;
- delete `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs.meta`.

The complete tooling successor delta is 11 validation-only paths. No runtime/gameplay/native product source or protected pin changes.

## Authority changes

`Tools/AssemblyShadow/h1_reproduction_tooling.py` now supports explicit authenticated `deletions` in addition to blob `overrides`.

V00 requires:

1. exact protected behavior → protected head → tooling successor ancestry;
2. exact nine replacement + two deletion build-input delta;
3. every deletion existed in the protected head and is absent in the tooling successor;
4. every deletion is also absent from the exact candidate source anchor;
5. all eleven required native+managed validation dependency blobs still equal candidate source blobs;
6. all current working build-input bytes match Git and no untracked Unity code input exists;
7. the exact assembled tracked `Assets/AssemblyShadowDemo/Editor/**/*.cs` and `Tests/Editor/**/*.cs` set contains no consumer of the removed historical managed-source API.

The preflight report now includes `toolDeletions` and `editorSourceCompatibility`.

## Regression coverage

The real disposable-Git regression constructs the failure topology explicitly:

- candidate source has the reviewed tool and no historical managed-source test;
- protected reproduction contains unfixed runtime plus the stale `H1ManagedSourceProvenance.Capture` consumer;
- tooling successor replaces the reviewed tool and deletes the stale `.cs` and `.meta`;
- source-target authority declares both replacements and deletions;
- full split-identity verification must report `editorSourceCompatibility.status=Compatible`.

Additional negatives reject undeclared deletions, stale legacy API consumers, deletion paths still present in the candidate source anchor, dirty tool bytes, wrong tool blobs, and non-validation deltas.

## Primary validation

Workflow `35093281267` at source anchor `3242b071540278510ea4ae287c70e37fc4c60340` passed **298/298**, zero nonpasses.

- authenticated Apple Bee fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10444094920`
- artifact ZIP SHA-256: `336777f8cec845bc2a9557f3a6312d472229cb62e3eed31ec17dde97dd5f4045`

This is bounded Primary/tool evidence. It does not claim Unity compilation of the new successor, fresh Player provenance, runtime/count acceptance, independent M08 PASS, or Human Review Gate approval.

## Evidence preservation

`local-validation-20260916-534b03e`, `local-validation-20260916-9568ea3`, and all earlier evidence remain historical and unchanged. Prior candidate V02/V03 evidence is not relabeled for the new source anchor.

H1 remains `InProgress / BlockedPendingFreshV00ToV05`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
