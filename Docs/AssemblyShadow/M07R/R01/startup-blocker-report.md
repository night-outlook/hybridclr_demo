# R01 continuation checkpoint — 2026-09-08

R01 is **not accepted**. R00 remains the earliest accepted repair milestone. H1 has **not been reached**, R01B has not been selected, and R02 or later milestones are not authorized by this checkpoint.

This is a development checkpoint, not a milestone completion or human review result. Historical M00–M07 and earlier R01 evidence remain unchanged. The new ordinary-image correction remains an uncommitted source change; it is not present in the diagnostic Player.

## Changes and validation

The ordinary-load probe selected a filtered compiler DLL while the preserved M00 guard requires its approved fixed image. Both files are 4,608 bytes but have different identities: fixed `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`, filtered `cb39730f6e1d610c9e4412db5bd195766bfe5ed61ade82f473d9975539492f55`.

The correction follows the captured reflection control define to its hashed configuration, selects the exact M00 fixed-image site and image blob, and retains separate filtered-provider verification. Python verification reuses the established linked reflection-evidence chain. The original generated M00 guard, fixed blob, configuration, package and native sources are unchanged by this correction.

Modified source files:

- `Assets/AssemblyShadowDemo/Bootstrap/M07R01OrdinarySnapshotBinding.cs`
- `Assets/AssemblyShadowDemo/Bootstrap/M07R01Probe.cs`
- `Assets/AssemblyShadowDemo/Tests/Editor/M07R01OrdinarySnapshotBindingTests.cs`
- `Tools/AssemblyShadow/r01_results.py`
- `Tools/AssemblyShadow/tests/test_r01_launch_pipeline.py`
- `Tools/AssemblyShadow/tests/test_r01_pipeline.py`
- `Tools/AssemblyShadow/tests/test_r01_results.py`

Fresh validation: **400 Python tests passed**, 57.472 seconds, zero skips; **292 Unity Editor tests passed**, zero failures or skips; `git diff --check` passed. Independent source review closed the fixed-image correction. Two test-fixture defects were found and fixed: dereferencing `snapshot` before construction and a static constant shadowed by the nested fixture's instance path. The first Unity compiler failure is retained alongside the successful retry.

The corrected ordinary-load Player paths remain **NotRun**. Editor/Python success does not establish Player acceptance.

## Confirmed startup blocker

A fresh debugger run of the immutable early-guard ON Player completed naturally: PID 85569, exit 1, `Validate` returned `BaselineAlreadyUsed`. No commit occurred; final state was `Staged`, active generation 0, empty commit order.

The bounded capture contains 266 contiguous events: 220 candidate-use observations, 22 input lookups, 22 non-null returns, capture setup and final Configure entry. All 22 lookup identities and their serialized order match candidate MonoScript objects in the built `globalgamemanagers.assets` (1,670 MonoScripts total). Every input stack contains `PlayerLoadGlobalManagers`.

The observed native path is:

`PlayerLoadGlobalManagers → PersistentManager object activation → MonoScript::RebuildFromAwake → MonoManager::GetScriptingClass → il2cpp_class_from_name`.

Subsequent `MonoScript::Renew → FindOrCreateMonoScriptCache → BuildScriptClassId` calls retain and inspect the physical classes. `IVersionTextProvider` also reaches `Class::InitLocked` and vtable setup during subclass/interface inspection. This happens before managed Configure, independently of the stable bootstrap scene and empty preloaded-assets list.

This confirms early physical candidate metadata/native cache use. It does **not** prove mixed-world execution: publication was rejected. The prior review's “not yet demonstrated” startup risk now has concrete evidence for this new early-guard executable. It does not retroactively invalidate or rewrite the historical M07 acceptance record.

Removing the input hook would leave successful output and class-use observations. Whitelisting Unity callers, clearing history, or forcing lookups to fail would conceal retained identities. No such change was made.

The source investigation found no established supported packaging hook that removes or defers only the global candidate MonoScripts while preserving physical AOT registration, Unity image aliases and M07 post-commit resource restoration. The existing assembly filter removes required AOT assemblies. A raw serialized-file rewrite has not been justified by a complete reference schema or resource compatibility proof.

## Executable and source boundaries

The captured executable is `M07-Baseline-R01-early-v1`, GUID `dedb05933b3443f68ad412c5e522de9c`, native SHA `c6c3640a43d66d62c21e1f4e5fb00d81c2152b1dbcaced57e961c88edacdc361`, ABI `33bcf290b4e70420668494d5bb7119619413df25a66ec13b6c4ad6f410cca3a7`.

Its recorded source pins are:

| Repository | Executed source |
|---|---|
| hybridclr_demo | `94457105b6f37b9e180e9cc16b73e526e999ea34` |
| hybridclr | `99ed95d58c7d976e5fd05257a4fe735ce0ee3813` |
| hybridclr_unity | `9f5d288e36f60c35420878f5796798b2dfa34de7` |
| il2cpp_plus | `5e9a1a93b530888fa41603e40c29e049a3914ea6` |

Demo HEAD `d72726063e459e22a4b742c329570975b31fde05` is the pin metadata child. The seven pending corrected source hashes, repository states, receipt hashes, test logs, debugger attempts and successful catalog correlation are recorded in [startup-blocker-evidence.json](startup-blocker-evidence.json). The retained 44-member archive is `_temp/AssemblyShadow/R01/startup-blocker-evidence-v1.tar.gz`, SHA `39fcae9fdc66fbebc944897795f639b03a90e7cd00f0ba6efaffa1635f56a0b7`.

Debugger proof uses actual symbols, machine-code offsets and saved registers. Stale DWARF from the later OFF build was not used. Debugger timing is not performance evidence. The object-table parser is restricted to this captured Unity v22 format; MonoManager reference edges were not decoded. Earlier failed/interrupted captures are retained as failed/interrupted diagnostics.

## Proposed decision to unblock R01

The existing startup invariant and the current managed activation point cannot both pass on this catalog. A behavioral repair needs an explicit architecture choice. The recommended bounded amendment is to investigate and prove **activation before Unity's global script catalog initializes**, as a prerequisite experiment inside R01. This would move a small activation-timing investigation ahead of the production coordinator work currently assigned to M09; it would not start M09's signing, downloading, LKG, health or deployment implementation.

Before implementation, the experiment must identify an actual supported entry point, define which runtime/native/managed services are ready there, and reject startup if activation fails. Its acceptance must include an untouched successful control, intended early-use negatives without pre-existing-use confounding, ordinary/Shadow shared-budget behavior, Q04 and initializer terminal failures, and the affected M00–M07 resource/execution regressions on a fresh pinned ON/OFF pair. No guard exception, counter reset or acceptance waiver is proposed. If no safe entry point exists, return that evidence for a further contract decision.

The alternative is a separately justified native-cache/packaging contract that explicitly supports these pre-activation identities. That is a broader design change requiring retained-handle, layout and Unity resource proofs; it cannot be inferred from historical Configure-only success.

A second required input remains outstanding: the production maximum cumulative shadow closure, ordinary interpreter image count and DLL size distribution. The current five-shadow/one-ordinary demo is measured evidence, not an approved product target. Without that input, Q06 and the R01B trigger remain unresolved.

## Gate and remaining acceptance

H1 is **NotReached**. R01 acceptance, the R01B decision and later milestones remain blocked. The current early pair fails the untouched control; its seven producer `Passed` rows do not establish seven strict acceptance passes because startup-negative causality is confounded. The corrected paired Player, Q04/initializer matrix and affected Player regressions must follow the startup repair. Retained native helper proofs do not substitute for those runs.

The user's ordered plan and [human gate rules](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md) prohibit silently entering later stages. This checkpoint requests a decision on the bounded R01 amendment and the actual capacity target; it does not request or imply H1 approval.
