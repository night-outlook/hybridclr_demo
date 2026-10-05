# R03 P — authenticated linked/compiler nominal type identity

Primary Implementation, 2026-10-05 UTC. **LM-001 source repair and batch-N preparation. Integrated P05/runtime closure, full R03 acceptance and H2 approval remain pending.**

## Preserved empirical return

M executed demo `301493290706e81437db1ac6a31977e9930d9fc6`; Local published `d6d3a3c05ef45890fb25fca3b762289450c69c5f`. Preserve **ReturnRequired: 90 cells, 48 Passed / 1 Failed / 41 Blocked; seal Passed**. Six builds, 23 focused Players, early 18-method and full 754/755 zero-skip Editor rosters, current 25-site compiler proof/16 controls and both linked proofs Passed. P05 public compilation emitted artifacts, but atomic fixture construction Failed NativeLayoutIncompatible. The 36 downstream Players did not execute. Exact scoped settings restoration Passed. No historical result or Local-owned report is rewritten.

LM-001 crosses a linked-baseline versus compiler-reference domain: M observed 43 same-named parent references and 18 field-scope differences involving mscorlib/netstandard. Those observations did not themselves authorize equivalence. This cycle uses the retained bytes as authenticated read-only test inputs; M remains Failed and no historical runtime result is reused.

## Exact implementation authority

All repositories use `codex/assembly-shadow-r01b-h1`.

- Demo executable/CI anchor: `7e1060ff5723efe365c60bc052bbbcb117d62dfa`.
- HybridCLR: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`.
- Managed package: `ef6c70f30248c4b7c41e9e85d81e08f5709dc4ba`.
- IL2CPP: `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

At resumption the candidate implementation and matching CI runs were already pushed. Primary reread M, reviewed the current candidate and its provenance/negative boundaries, authenticated the three artifacts, reran bounded local source-slice tests, and finalized this handoff. The pre-finalization demo head `e6f88b070384349709ee670dd3eb87d8ee75eb10` differs from the anchor only in the P artifact-audit request. The final documentation-only transport must match Primary's exact prompt and Local/remote HEAD.

## Design and implementation

`NativeLayoutIdentityContext` is a closed-world, metadata-only resolver over privately cloned captured images. Its low-level API is not a provenance certificate: the production factory supplies independently authenticated inventories. Full assembly identity, namespace and nested declaration identity remain in the canonical key. Explicit exported-type forwarders are followed with bounded depth; missing providers/types, cycles, ambiguous images/definitions/exports, malformed forwarders, foreign owners and disposed contexts fail closed. There is no ambient dnlib resolver, GAC lookup, Assembly.Load, business initialization or blanket framework-name alias.

A compiler reference definition in the exact netstandard 2.1 identity is mapped only through the actual captured runtime forwarding facade. The context requires exact facade hashes/identity and forwarding-only shape, resolves its explicit destination in the linked inventory and checks destination kind/arity. It does not simply erase mscorlib/netstandard qualifiers. Unrelated assemblies declaring the same qualified names remain different identities.

`NativeLayoutAdmissionSnapshot` rereads and verifies the complete baseline and target receipts, source domains, Unity version, target and architecture. It rederives target-framework provenance, rechecks the existing linked retargeting proof and its build GUID, captures all linked/compiler image bytes, and requires the compiler netstandard reference to be in the verified target-framework inventory. It rechecks input files, proof and facade before returning. No caller-supplied inventory or claimed hash alone replaces those checks.

`EvolutionSignature` now accepts a scoped named-type identity resolver for this comparison. Parent, interface, field, generic argument, constraint and custom-modifier shapes retain their structural encoding. The default, unbound signature path remains unchanged. `NativeLayoutAdmissionValidator` retains conservative parent/interface/field/layout/generic/primitive-append decisions; the captured-context path additionally requires full compared assembly identity agreement.

The output `native-layout-admission-v1.json` keeps its established filename but uses **schema 2** for the captured-context report. It records both image inventories (identity/hash/MVID), declaration-to-definition paths, both facade hashes, framework provenance and the linked proof hash. `nativeProofExecuted=false`, `runtimeMustRevalidate=true`, `allocationProofStillRequired=true` and expansion disabled remain mandatory. Historical schema-1 reports are neither upgraded nor accepted as fresh schema-2 proof. Nominal identity equivalence is not an offset, allocation, resource-ABI or native-execution certificate.

The completion runner adds 33 actual metadata identity contracts inside the existing completion-tool prerequisite. After current fixture finalization, `layout_evidence.verify_graph` verifies all P01–P05 sidecars inside the existing resource-input-binding cell, including exact source/load order, inventories, captured forwarder paths and actual P05 mapping coverage. It does not replace the production resolver with a Python alias map. No cell or runtime coverage is removed.

## Verification and negative boundaries

Host workflow `37272466923` Passed on Linux and macOS at the anchor. Each host passed 229 completion Python contracts, 183 retained R03 contracts, 33 layout-identity cases, 12 constructor cases, 20 capability cases, 10 fixed-image cases, 32 qualification cases, 9+9 graph cases and 35 admission cases. All 19 owned commands per host completed without survivors.

Pinned-Unity workflow `37272466984` Passed: 16 resource assemblies / 657 source files, 22 clean owned commands, existing fixed-image and 25-site/16-control policy replay, and the same 33 layout-identity cases using pinned Unity Mono. Compiler warnings are retained (951 warning occurrences in the authenticated API command streams), not suppressed. No Unity Editor or Player was launched by these checks.

The actual M replay authenticates 56 linked images and 214 compiler images plus the captured runtime facade. The original unbound comparison still reproduces exactly 43 ParentChanged rows. The new comparison maps 18 declarations through the actual facade and produces **53 NeedsNativeProof rows, zero Rejected rows**. It does not authorize native allocation or mutate the preserved inputs. A changed real parent remains rejected. Synthetic real-DLL controls cover real parent/interface/field/generic/constraint/modifier/offset changes, unrelated same-named types, missing providers/destinations, two-hop forwarding, cycles, duplicate images/definitions/exports, version changes, context ownership/disposal, defensive copies and invalid facade bytes/shape.

Primary downloaded all three exact-source artifacts and authenticated ZIP digests, safe/unique membership, every indexed size/hash, source/package identities, command exits/lifetime/stream hashes, test counts and result consistency. Host artifacts each contain 585 indexed / 586 ZIP files; API has 240 / 241. The ten fixed-image cases were additionally checked in their actual nested observation schema. The current-container source-slice runs passed 52 LM verifier/auditor tests and 183 retained tests; they are not owning Local checkout, managed replay or Unity execution. The full 229-case suite and managed replay results above are attributed to CI.

The read-only artifact audit workflow `37273508600` also Passed. Its preceding request incorrectly treated fixed-image cases as a top-level collection; the committed correction follows the actual nested schema without changing a producer, artifact or test. All final fixed-image cases remain Passed. Earlier failed candidate/audit runs are not relabeled or substituted for the exact-source final evidence. Details and hashes are in P_HOST_EVIDENCE.json.

## Changed files and review scope

Managed package: `Editor/AssemblyShadow/Build/NativeLayoutAdmissionSnapshot.cs`; `Metadata/EvolutionSignature.cs`, `NativeLayoutAdmissionValidator.cs`, `NativeLayoutIdentityContext.cs` and its meta file.

Demo: completion `LayoutIdentityTests/{LayoutIdentityTests.csproj,Program.cs}`, `layout_identity.py`, `layout_evidence.py`, `compile_layout_checks.py`, `ci_artifact_audit.py`, `test_lm_identity.py`, `test_lm_artifact_audit.py`, `test_lm_workflow_pins.py`, `run_completion.py`, `run_host.py`, `source-pins.json`; R03 `AdmissionTests/AdmissionTests.csproj`, `PlayerFixtures/PlayerFixtures.csproj`, `source-pins.json`; workflows `r03-build-api.yml`, `r03-completion-api.yml`, `r03-lm-source.yml`, `r03-lm-artifact-audit.yml`; P evidence/repair/matrix records and canonical README/CURRENT_STATUS/WEB_TO_LOCAL.

Explicit project source lists include the new context, and the pinned build-helper workflow consumes the declared current package/native pins rather than an older hardcoded package. Both R03 pin documents agree. Native repositories, runtime guards/counters/producer lease, fixture DLL expectations, full Editor rosters, resource assets/GUIDs, compiler-policy declarations and measurement protocol are unchanged. The review found no additional source defect requiring a change during finalization. This is Primary's repair review, not independent full-stage review.

## Handoff, preservation and rollback

Batch N uses the new root in WEB_TO_LOCAL and retains 90 cells, six fresh builds, 59 fresh Players, early 18-method and full 754/755 zero-skip Editor runs. Require fresh P05 construction/finalization, exact settings recovery, all five schema-2 sidecars, linked/native proof and all existing runtime/measurement contracts. Do not retry M, reuse old apps, broaden forwarding mappings or delegate non-trivial repair to Local.

The current Connector tree/commit/non-forced-ref smoke test Passed on `codex/connector-smoke-r03-lm-20261005-final`, commit `45d4f3041bc0f2bf8ab82bb97f5f27d73f9b3483`, with exact HEAD/file read-back. Delete-ref is not exposed; the branch remains disposable and non-authoritative. All four source heads were read through the Connector; this finalization writes only demo documentation.

Rollback requires a reviewed commit restoring a coherent package/demo-pin tuple, not qualifier stripping, guard bypasses, source resets or evidence rewriting. Any fresh failure remains Failed/Blocked with its seal state and returns to Primary. Even a green N returns EvidenceReadyForPrimaryReview only: R03Accepted=false, H2Passed=false, qualificationApproved=false and structural expansion disabled. Full-stage reconciliation and independent review remain Primary-owned.
