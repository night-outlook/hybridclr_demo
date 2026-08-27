# M01 feasibility acceptance report

Status: implementation and validation complete; independent acceptance pending.
Proposed Gate 1: **CONDITIONAL-GO** for the exact macOS ARM64 P01 fixture.

The first-build prefab and scene bundles create physical same-name interpreter
components and execute `BASELINE-EXT|PATCH-P01-INTERNAL|1234`. Scene unload/reload,
both tested GetComponent overloads, serialized values, ScriptableObject and AOT
external consumer checks pass. This is not approval of a production Shadow
system or of activating after business use.

## Requirements and evidence

| Requirement | Evidence |
| --- | --- |
| 01.1 isolated business assembly graph and Bootstrap | Assets/AssemblyShadowDemo; Bootstrap references HybridCLR.Runtime only; five actual Editor checks pass |
| 01.2 marker-only P01 | CompilePlayerScripts extra define; same simple name/types/fields/base/interfaces/method signatures; normalized IL permits only the marker change |
| 01.3 immutable original assets/bundles | baseline-manifest.json records GUIDs, hashes, compiler DLL/PDB/MVID snapshots; first bytes remain read-only and unchanged |
| 01.4 baseline AOT Player | m01-baseline-final.json, exit 0; three business assemblies captured from actual post-strip inputs |
| 01.5 same-name patch | patch-manifest.json; distinct baseline/P01 MVIDs and SHA-256; Internal remains in the Player's AOT input |
| 01.6 Stage | physical baseline/shadow pointers, no module initializer; immediate registration is explicitly PoC-only |
| 01.7-01.8 name resolution and reflection | final native trace and reflection object header; new body, Type.Assembly identity, FullName, IsDynamic and duplicate count recorded |
| 01.9-01.10 native paths and minimal mappings | completed investigation; name-only failure, image-map failure, operand trace, final query-target mapping; symbol-backed stacks and ARM64 disassembly |
| 01.11 old prefab | final result and native Object::New input; no Missing Script, retained 1234/base 7/reference, both GetComponent paths |
| 01.12 old scene | first asynchronous load plus unload/reload pass with physical shadow objects and AOT external consumer |
| 01.13 negative timing | four complete separate-process observations; pre-created AOT objects stay AOT, not silently replaced |
| 01.14 honest gate | CONDITIONAL-GO in the final result; restrictions and M03-M07 backlog in investigation; independent approval required |
| Native OFF preserves ordinary behavior | final native commit built OFF; ordinary M00 hot-update/AOT Player regression passes |

Native findings, actual pointer/event tables, engine cache details, deviations,
and the concrete production backlog are in
[the investigation](../Investigations/unity-2022-prefab-script-resolution.md).
The scope is M00 and M01 only. M02-M12 are not implemented or claimed complete.

## Source boundary

All repositories use local branch `codex/assembly-shadow-m01`:

| Repository | Exact runtime source revision |
| --- | --- |
| hybridclr | 1bc69c3acc2434804e71560418df8c728a63360e |
| hybridclr_unity | a1d2697dfa3b1c510d5bfe5cf5e513886a3af78a |
| il2cpp_plus | 03a450c73b5c5db2ed6f87dc4f194788fd204567 |

Demo build-source pin and strict install closeout: pending final source commit.
The accepted final Player was built from the source bytes being committed;
later pin/review metadata must not alter executable source. No commit or tag is
pushed by this task. The prior `assembly-shadow-m00-baseline` tags remain intact.

Changed source scope relative to M00:

- demo: Assets/AssemblyShadowDemo and its meta; two build settings files and
  source pins; Tools/AssemblyShadow M01 verifier/tests/readme; M01 evidence/docs.
- package: Runtime/RuntimeApi.cs experimental API declarations only.
- hybridclr: metadata/Assembly and RuntimeApi prototype creation/diagnostics.
- il2cpp_plus: the new vm/AssemblyShadowPrototype pair, macro-guarded name/image
  resolution and observed query comparison, and bounded diagnostic call sites
  in existing metadata/reflection/object/class paths.

The exact file list is the Git diff from each M00 tag to the reviewed M01 target.
Original demo dirty state and the pre-existing Unity Editor are preserved.

## New APIs and build commands

`HybridCLR.RuntimeApi` adds feasibility-only LoadAssemblyShadowPrototype,
ActivateAssemblyShadowPrototype, GetAssemblyShadowPrototypeDiagnostics,
InspectAssemblyShadowPrototypeObject, InspectAssemblyShadowPrototypeAssembly,
and SetAssemblyShadowPrototypePhase. They do not promise production transaction,
unload, usage guard, or rollback behavior. Native Assembly::CreateShadowPrototype
creates the same-name interpreter assembly without a module initializer.

Editor entrypoints are BuildBaselineBundles.Build, CompilePatchDlls.Build,
BuildBaselinePlayer.Build, M01EditorValidation.Validate under
AssemblyShadowDemo.Editor. M01PlayerBuildEvidence.CaptureExisting captures an
existing build only; it does not build bundles or a Player.

Follow [the reproduction guide](../../../Tools/AssemblyShadow/README.md) from
the isolated project. Unity invocations use the shared guarded PowerShell skill
scripts, never a second Editor for the same project. Run modes in order:
Baseline, PreUseType, PreUseReflection, PreUsePrefab, PreUseScene, P01. Each run
gets a distinct result/log path; P01 last leaves the accepted positive result at
PersistentDataPath/AssemblyShadowTests/m01-result.json.

## Validation record

- Final native-ON build: `_temp/UnityExec_20260827_054717.log`, BuildReport
  Succeeded, zero reported build errors/warnings; BuildPlayer phase 30.12 s.
- Final native-OFF build: `_temp/UnityExec_20260827_054452.log`, Succeeded;
  separate NativeOffRegression.app preserves the M00 accepted app; 28.04 s.
- Real final Player exits: Baseline 0, PreUseType 0, PreUseReflection 0,
  PreUsePrefab 1, PreUseScene 1, P01 0. Exit-one cases are complete intentional
  negative observations, not successful positive tests or ignored harness errors.
- `verify-m01-results.py` passes actual artifacts, all six results, native
  trace hashes/allocation stacks, the P01 DLL, three linked AOT input snapshots,
  unchanged bundles and all four negative witnesses; gate CONDITIONAL-GO.
- Five actual Editor validation cases pass in
  `_temp/UnityExec_20260827_055024.log`. The NUnit wrapper compiled but was not
  separately run through Unity Test Runner; no Test Runner result is claimed.
- `python3 -m unittest discover -s Tools/AssemblyShadow/tests -v`: 34 passed
  (21 M00 source/cache safety tests, 13 M01 evidence/false-positive tests).
- ON/OFF C++ syntax checks, business baseline/P01 and Editor C# compilation,
  and asmdef JSON parsing passed. Staged code/docs/JSON whitespace checks pass.
  The unrestricted staged diff flags Unity-generated empty-value trailing spaces
  in serialized assets and metas; those bytes are deliberately retained so the
  original business source/asset snapshot remains exact, not reformatted.
- Final GameAssembly and dSYM UUID match:
  `37AA5842-07E5-4517-BE9C-1C42C5A065FE`; offline LLDB resolves final trace PCs
  to the actual native source. Live debugging was not authorized by this host.

BuildReport warning counts do not erase native clang warnings or headless
shader/shutdown diagnostics in full logs. These timings are build-phase
observations, not production runtime performance measurements.

## Evidence and review

[Evidence/README.md](Evidence/README.md) indexes raw results, causal experiments,
the artifact/hash inventory, and the run ledger. DLLs, apps, logs and dSYMs stay
in ignored local artifact directories; their paths/hashes are recorded.
Post-strip MVID/SHA differences are reported honestly, with a separate bounded
dnlib semantic comparison against the frozen compiler snapshots. Runtime
Assembly.ManifestModule is unsupported and is not used to fabricate MVIDs.

Independent review record and local `assembly-shadow-m01-poc` tags are pending.
The tag, if approved, identifies a conditional PoC milestone, not release-ready
Shadow behavior. M02 entry may proceed only subject to the documented conditions
and a separate request; this task does not implement M02.
