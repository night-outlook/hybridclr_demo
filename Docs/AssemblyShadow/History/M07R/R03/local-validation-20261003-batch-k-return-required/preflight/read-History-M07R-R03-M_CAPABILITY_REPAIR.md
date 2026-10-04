# R03 M — resource dependency and actual target-capability contract

Primary Implementation, 2026-10-03 UTC. Source repair and batch-K preparation, not integrated runtime acceptance or a Human Review Gate.

## Preserved empirical return

J executed demo `cebed900e6456433ac65db531262b60fd26766ee` once; Local published `71bddefd86a3b718d9d36b3edc2d88cd21db1e92`. Its result remains **ReturnRequired: 43 Passed / 1 Failed / 46 Blocked; seal Passed**. Four focused builds, 23 focused Players, the 18-method preflight, 754/755 full Editor rosters, ten source-pin checks and native installation Passed. LI-001/LI-002 have fresh passing regressions. The M01 source-asset/GUID Editor contract Passed; resource/bundle/Player coverage remains unavailable, not inferred from that Editor pass.

The actual resource compiler failed `UnknownPrecompiledCapability: Unity.Collections.LowLevel.ILSupport` before its target snapshot. Two resource builds and 36 downstream Players were Blocked. Antlr3 was a source-supported additional mismatch, not a separately observed J exception. A full serialized target inventory was Unavailable in J; its ScriptAssemblies listing is not substituted. Local reports, every earlier checkpoint, failed unisolated producer certificates and the P05 cleanup-only NotApplicable result remain unchanged.

## Design choice: complete explicit resource scope

The narrowed copied resource project did not include Collections or VisualScripting, while M02 configuration inherited five declarations. Importing unrelated full-demo packages would expand the resource validation domain and require a Collections version/provider not established by J. Instead, the completion adapter has a named, complete `R03ResourceCapabilitiesV1` profile, bound to the copied project's authority marker and exact resolved package set.

All five inherited declarations are reviewed together:

| Declaration | Resource-only disposition |
| --- | --- |
| Newtonsoft.Json | Required precompiled Runtime, explicitly non-shadow and non-bootstrap |
| Unity.Burst.Unsafe | Required precompiled Runtime, explicitly non-shadow and non-bootstrap |
| nunit.framework | Required precompiled Runtime as determined by actual Player references; its name is not a classification exemption |
| Unity.Collections.LowLevel.ILSupport | Excluded from this resource scope; its appearance in actual inventory is an error |
| Unity.VisualScripting.Antlr3.Runtime | Excluded from this resource scope; its appearance in actual inventory is an error |

This is not an inventory-driven filter. `Select` requires the entire unchanged five-declaration input and rejects duplicates, missing/extra names, changed classifications and capability flags. The original M02/M07 five-declaration behavior remains unchanged outside the synchronous adapter scope. Owner-thread/nesting checks and disposal bound the override to the explicit operation. No package production guard was changed.

The 11 non-module package versions come from J's published resolved lock and are promoted to explicit roots: Burst1.8.21, Mathematics1.2.6, ext.nunit1.0.6, Newtonsoft3.2.1, Core/URP/ShaderGraph14.0.12, universal-config14.0.10, Searcher4.9.2, TestFramework1.1.33 and UGUI1.0.0. The pinned local HybridCLR package and original built-in modules remain explicit. No Collections version is invented and no unused VisualScripting package is imported. Manifest and resolved lock must have identical membership and exact versions; unrelated resolver additions are not optional.

### Additional issue found before handoff

The already-pushed candidate `eb9f38097e8b76f95aef8b8aad144bbd7e713327` omitted `com.unity.modules.subsystems` while requiring exact manifest/lock membership. J's actual lock contains this XR transitive module at version1.0.0/depth1. Primary reproduced the old mismatch with an explicitly synthetic lock shape based on J and fixed the producer to pin that reviewed module as a root. Six independent regressions cover the 32 observed built-in module names, missing-from-both documents, version conflicts and unreviewed additions. This correction does not loosen membership checks or retrospectively claim a new J failure.

Source for that observation: `local-validation-20261003-batch-j-return-required/preflight/issue-resource-snapshot/Packages/packages-lock.json`, Git blob `61f02845b988206b6ffc75e4d380e9b9a95fc42f` at Local publication `71bddef...`.

## Actual Unity policy/inventory preflight

Before the resource compiler snapshot, a separate supervised Unity invocation runs `R03CompletionInventoryContract.Verify`. It validates package resolution, explicitly calls M07 Configure, and then captures both actual `CompilationPipeline` arrays: Player and PlayerWithoutTestAssemblies. Configuration is a permitted mutation, not disguised as read-only observation.

The receipt records source paths, references, flags, compiler outputs, hashes/sizes of all compiled-reference DLLs, all derived capability rows, all five declaration dispositions, configured policy JSON, consumer-source hashes and configured-input before/after hashes. Positive validation invokes the actual production `BuildCompilerInventory`, `CreatePolicyConfiguration` and policy validator. Python independently reconstructs the entire derived inventory from the captured arrays. No hand-authored inventory substitutes for the positive case.

Ten named positive/negative controls call the exact production `BuildCapabilities` core on copied settings/inventories: scoped success; original five declarations; both excluded names individually; an unknown plugin; source and framework assemblies falsely declared as plugins; a non-runtime plugin; ordinary fixed plugin success; and ordinary shadow-plugin rejection. Controls preserve their exact expected codes and cannot mutate the configured inputs. `UnknownPrecompiledCapability`, classification, ordinary-hot-update, source binding, closure, resource and ownership guards remain intact. Missing required plugins or unexpected excluded providers fail rather than receiving a fallback.

The preflight lives inside the existing resource-compiler cell. It does not replace target compilation, resource native builds, Editor tests or Players. Failures preserve logs/available Failed receipts and block dependent work. Independent focused and Editor checks retain their existing dependency rules.

## Review and verification boundaries

The candidate profile, all five declarations, package closure, production call signatures, scoped configuration, restoration and failure paths were reviewed. Primary found and repaired the transitive module omission before issuing K. The package/native implementation and original runtime verifiers are unchanged. This is a Primary repair review, not the independent full R03 review or H2 approval.

Executable/CI anchor: `f00626dca8591496f2676b629104fd688bf06dce`. Matching host/compiler outcomes, artifact identities, authentication counts and limitations are in `M_HOST_EVIDENCE.json`. The current-container completion suite passed 107 tests; the prior candidate suite passed 101 but did not cover the subsequently found transitive closure defect. Host policy-profile tests execute the actual scope helper, not Unity's live compiler inventory. Pinned API compilation includes the new observer, but does not launch Unity. Actual package resolution, all ten inventory controls and the previously blocked resource paths remain Local K work.

## Changed files since Local J

Only the demo repository changes:
- `.github/workflows/r03-completion-api.yml`;
- `Assets/AssemblyShadowDemo/Editor/M02Build.cs` and `R03CompletionBuild.cs`;
- `R03ResourceCapabilityProfile.cs`, `R03CompletionInventoryContract.cs` and their meta files in that Editor directory;
- `Tools/AssemblyShadow/R03Completion/CapabilityProfileTests/{CapabilityProfileTests.csproj,Program.cs}`;
- `Tools/AssemblyShadow/R03Completion/{fixture_project.py,resource_capabilities.py,resource_pipeline.py,run_completion.py,run_host.py,test_lj_contracts.py,test_lj_module_closure.py}`;
- this M repair/evidence/matrix record, README, CURRENT_STATUS and WEB_TO_LOCAL.

All three non-demo heads stay unchanged. Local-owned reports and historical checkpoints are not modified. Existing resource assets/GUIDs, source-pin and constructor preflights, runtime counters/leases, rejection expectations, full Editor rosters and observation protocol are retained.

## Transport, next run and rollback

The Connector Git-tree/commit/non-forced-ref write path was tested on disposable branch `codex/connector-smoke-r03-lj-20261003-1730`: commit `d03d365da89d4d4ffaaa89579a01f0e483269c98` was read back exactly. Delete-ref is unavailable; the branch remains disposable and non-authoritative. The other repositories need no write in this cycle.

Batch K uses a new root and retains 90 cells, six fresh native builds and 59 fresh Players, plus all existing preflights/full Editor runs and the new inventory consumer. See `M_VALIDATION_MATRIX.md` and `Handoff/WEB_TO_LOCAL.md`. No non-trivial changes are delegated to Local. Do not retry J or reuse any earlier app/root.

Rollback requires a new reviewed Primary commit restoring a coherent resource adapter/profile tuple, not removal of a production check or reset of evidence. Any fresh failure returns to Primary with exact diagnostics. Even a green K does not authorize expansion, full R03 acceptance, H2 or a production performance SLA.
