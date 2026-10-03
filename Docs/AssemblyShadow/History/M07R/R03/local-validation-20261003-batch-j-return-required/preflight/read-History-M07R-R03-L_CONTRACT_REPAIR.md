# R03 L — batch-I constructor and source-pin contract repair

Primary Implementation, 2026-10-03. **Source repair and preflight preparation; not integrated Unity/Player acceptance, R03 acceptance or H2 approval.**

## Preserved return and source authority

Batch I remains `ReturnRequired`: 90 cells, **40 Passed / 2 Failed / 48 Blocked**, seal Passed. Four focused builds and all 23 executed focused Player contracts Passed. Its focused Editor result remains **736 Passed / 18 Failed / zero skips**. Both resource builds, resource Editor and 36 additional Players were Blocked. Static qualification Passed without authorization. The P05 cleanup's NotApplicable coverage is not successful structural compilation/restoration evidence.

I executed demo `c579e75eadef58ca484b35ffee03e435a925d781`; Local published the reports/checkpoint at `c16f39ec204876e3fd569f75c7b2e7dabc8c3913`. Its archive remains SHA-256 `fe2f9d40b84e4a2d7dd3929b6399601ad3f9e4da29eb088e2a4371d49223c718`. See the unchanged [Local return](../../../Handoff/RETURN_TO_WEB.md) and [I checkpoint](local-validation-20261003-batch-i-return-required/README.md). Earlier A–H states, H's M01 NoCoverage and failed unisolated control certificates remain unchanged.

All branches: `codex/assembly-shadow-r01b-h1`. Repair/compiler source anchor: demo `8d5297c375201687d17b91843ea0250ed90c0095`. Package: `c86cbf665f5fcb2137e5adf2960541ce492467a4`. Native pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and IL2CPP `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. A later documentation-only transport is not a new executed runtime source.

At resumption the package repair and demo source-capture workflow were already pushed. Primary inspected those exact commits and completed their missing integration, regression tests, preflight and handoff; it did not replace them based on chat recollection.

## LI-001 — exact constructor boundary, no synthetic qualification

The two policy-test fixtures reflected an internal constructor with four arguments. `CompiledAssemblySet` now requires five, the last being `IEnumerable<CompiledAssemblySource>`. Reflection compiles even when its invocation's arity is obsolete, so helper/API compilation did not detect the defect. In I, 17 acquisition-policy tests and one reference-module test failed before their policy assertions.

The shared `SyntheticCompiledAssemblySet.Create` helper in package commit `c86cbf...` resolves the exact five-type signature and passes an explicitly empty source-binding collection. The fixtures remain synthetic policy inputs, not byte-authenticated qualification evidence. No compatibility overload or production constructor relaxation was added; real loading and qualification still require actual source bindings.

Twelve host contracts link the actual helper and actual package metadata implementation. They test the exact signature, modules without snapshot descriptors, empty synthetic source authority, rejection by qualification analysis, disposal/null/deferred-reference boundaries and the original four-argument `TargetParameterCountException` control. These host checks **do not execute the 18 acquisition-policy assertions in Unity**.

The new early Editor preflight runs those exact 18 named methods in an unused isolated project before native builds. Its roster is checked against the immutable I failure identities only as a name catalog; I's results are never reclassified. Every selected method must Pass with zero skips and exact aggregate/identity matching. The later original 754-case and resource-complete 755-case runs are still required; the small preflight replaces neither.

## LI-002 — complete producer schema and actual consumer preflight

`fixture_project.source_pins` omitted `architecture`. The production `ShadowSourcePins.Read` correctly rejected the document. The former Python copy test even asserted that architecture was absent; it is corrected to require the complete independent field set and `arm64`, not deleted or bypassed.

The producer now writes exact schema1, Unity2022.3.62f2, StandaloneOSX and arm64 with all four URL/revision/relative-owner bindings. A separate Python schema screen rejects missing/extra platform fields, wrong values, revision/owner substitutions and malformed repository rows before writing the document. Production `ShadowSourcePins.Read`, `RequireCompatible` and `RequireSameBuildSources` are unchanged.

Before Configure/Install, a separate supervised Unity invocation runs `R03CompletionSourcePinContract.Verify`. It passes the actual generated file to the actual `UnityEngine.JsonUtility` / `ShadowSourcePins.Read` implementation. It records the derived runtime ABI hash and before/after hashes of source pins, Shadow settings, Player settings and the isolated authority marker. Separate new control files exercise:

| Contract | Exact expected outcome |
| --- | --- |
| Generated document; JsonUtility roundtrip | Success; same build sources |
| Missing architecture; wrong architecture; wrong target; wrong Unity | SourcePinTarget |
| Wrong schema | SourcePinSchema |
| Invalid revision; missing repository | InvalidSourcePin |
| Different demo build source with compatible runtime tuple | BuildSourceProvenanceMismatch |

There are **10 consumer cases**. The script does not alter the generated pins/settings, invoke installation, execute business code, stage an assembly or invent success JSON. The Python verifier binds actual files, exact outcome codes, source/platform identity and unchanged inputs. Only after this receipt verifies does the original native installation command run. Failed controls remain evidence; no second attempt or global cleanup is performed.

The new Unity consumer method is fully compiled against pinned APIs in Primary CI; **actual JsonUtility execution and the early 18-method Editor run remain Local work**, not host-test claims.

## Verification and review boundary

See [L_HOST_EVIDENCE.json](L_HOST_EVIDENCE.json) for exact CI source/run/artifact identities and independently authenticated counts/digests. Primary's local completion-tool suite passed 73 tests (49 retained plus 24 LI tests); the actual constructor/helper host suite passed 12. A new test's initial disposed-object assertion targeted an unguarded dictionary accessor; it was corrected to the existing guarded GetModule contract, without changing production code. The deliberate old-arity exception remains a passing negative contract.

The new Python tests also reject changed consumer bytes/settings, fake consumer identities, unauthorized flags, wrong negative codes and outside/symlink paths. They retain original I output as a rejected historical input and require the same 18 names. Existing 183 R03 verifier, 32 qualification, 9+9 graph and 35 admission cases remain scheduled in matching CI. Source upload is checked against the local source hashes using the final compiler artifact, with retained metadata/workflow hashes checked through Connector read-back.

Primary reviewed design, code, independent negative controls, process-lifetime integration, ownership, evidence selection and failure dependencies. This is the Primary repair review, **not the independent full R03 stage review or a Human Review Gate**. No package production implementation, native code, counter, producer lease, source-ownership guard, admission rule, timing protocol, Player case or full Editor roster is weakened. Missing broader RC1–RC6 obligations remain open.

## Changed files since Local I

Package (already-pushed c86 fixture repair):
- `Tests/Editor/AssemblyShadow/SyntheticCompiledAssemblySet.cs` and `.meta`;
- `Tests/Editor/AssemblyShadow/ManagedAcquisitionPolicyTests.cs`;
- `Tests/Editor/AssemblyShadow/PolicyTests.cs`.

Demo:
- `.github/workflows/r03-li-source.yml` (already-pushed immutable input capture);
- `.github/workflows/r03-completion.yml`, `r03-completion-api.yml`;
- `Assets/AssemblyShadowDemo/Editor/R03CompletionSourcePinContract.cs` and `.meta`;
- `Tools/AssemblyShadow/R03Completion/FixtureContractTests/{FixtureContractTests.csproj,Program.cs}`;
- `Tools/AssemblyShadow/R03Completion/{editor_contract.py,fixture-constructor-cases.json,fixture_contracts.py,fixture_project.py,resource_pipeline.py,run_completion.py,run_host.py,source-pins.json,source_pin_contract.py,test_completion_contracts.py,test_li_contracts.py}`;
- this L repair/evidence/matrix record, canonical README, CURRENT_STATUS and WEB_TO_LOCAL.

No original R03 runner/verifier/native probe, old checkpoint or Local-owned report is modified. Native feature branch heads are unchanged.

## Transport, next execution and rollback

Connector write/read-back succeeded on disposable branch `codex/connector-smoke-r03-li-20261003-1010`: demo `31ae8ab0252d0c6d6274ec48fcf877eed25652aa`, package `6dbbf01c18fd1f58c66b21134275fc5a2ab8351a`. No delete-ref action is exposed, so these two branches remain explicitly disposable/non-authoritative. Earlier native transport checks are retained; no native write is needed for this repair.

Batch J retains **90 cells / six fresh builds / 59 fresh Players**, with the extra 18-test Editor preflight and ten real consumer checks inside existing prerequisite cells. [L_VALIDATION_MATRIX.md](L_VALIDATION_MATRIX.md) and the live [WEB_TO_LOCAL.md](../../../Handoff/WEB_TO_LOCAL.md) bind the fresh execution. Do not retry I or reuse its apps/root. Local must not repair source/expectations or manipulate preservation rules; any non-trivial defect returns to Primary with all evidence.

Rollback is a new reviewed Primary commit restoring a coherent demo/package tuple. Do not reset the owning checkouts, overwrite old evidence, or treat a previously built app as fresh. Any failure in J stays Failed/Blocked with its seal result. On success return EvidenceReadyForPrimaryReview, still R03Accepted=false, H2Passed=false, qualificationApproved=false and expansion disabled. Full-stage reconciliation and independent review remain Primary-owned.
