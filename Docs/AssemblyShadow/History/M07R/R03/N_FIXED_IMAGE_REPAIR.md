# R03 N — authoritative fixed-image provisioning before resource compilation

Primary Implementation, 2026-10-04 UTC. **Source repair and batch-L handoff; integrated LK-001 closure remains pending. Not R03 acceptance or H2 approval.**

## Preserved empirical return

K executed demo `1704c0393dd0c7717502e336232a0d951422e767` once; Local published `4abd44f1fc6f81a75c76ae4975c28dd06a80b9f8`. Preserve **ReturnRequired: 43 Passed / 1 Failed / 46 Blocked; seal Passed**. Four focused builds, 23 Players, the early 18-method and full 754/755 zero-skip Editor runs, source-pin checks and all ten target-inventory controls Passed. The resource compiler failed before a successful snapshot; two resource builds and 36 downstream Players were Blocked. Native installation is not a fifth build. M01 source-asset/GUID coverage Passed; resource/bundle/runtime coverage remains unavailable.

The original failure is `ReflectionBindingsILPostProcessor` reading the absent `Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes`, followed by `CompileFailed`. `fixture_project.ROOTS` selected an ignored directory, but its Git-only catalog contained no files from that directory. The historical ignored owning file captured by Local is diagnostic only and is not the input used by this repair. [RETURN_TO_WEB.md](../../../Handoff/RETURN_TO_WEB.md) and [K checkpoint](local-validation-20261003-batch-k-return-required/README.md) remain unchanged. All earlier custody checks remain attributed to Local; no complete new authentication of K's archive or earlier live roots is claimed here.

## Exact implementation authority

All branches: `codex/assembly-shadow-r01b-h1`.

- Demo executable/CI anchor: `78ce9f81968a330b2801a93d4a426ffab7565b5f`.
- HybridCLR: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`.
- Managed package: `c86cbf665f5fcb2137e5adf2960541ce492467a4`.
- IL2CPP: `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

At resumption, the two implementation commits `e7a46219de7230ba5dfea065b88695d2bd5421ad` and the anchor above were already pushed. Primary read their source and Local return, reviewed the provisioning/consumer boundaries, reran local contracts, authenticated matching CI artifacts and finalized this handoff. The final documentation-only transport does not create a new runtime execution claim.

## Design: reuse existing immutable INPUT authority, never an ignored cache

The repository already contains the reviewed R02 compact fixture and origin record:

- `Tools/AssemblyShadow/R02/fixtures/m00-frozen.dll.zlib.base64.txt`, Git blob `9803eb472c0ef6eaf713a38a59d3fe07aa93830e`;
- `Tools/AssemblyShadow/R02/fixtures/m00-origin.json`, Git blob `245d7b56ffeccc16c897dfc8ef40bfb4f73fe098`.

The decoded image is exactly 4,608 bytes, SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`, provider `AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null`, MVID `e7f5b1ac-eca4-4034-8da4-69e25ca9fe3b`.

Its origin is the existing immutable H1 archive `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority925e/raw-evidence.tar.gz`, SHA-256 `2ecb3d04cdd093c469717d4c2959ec416ec8d0745c51c2a4ba37c82f9bc253e8`. The exact member is `_temp/AssemblyShadow/H1Authority925e-FailureFixtures-20260919A/CompileSnapshot/ReflectionBindings/Images/9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27.dll.bytes`. The unchanged origin record supplies archive repository commit `1d7dc134003206ada8a92b50763ca2da7dc9530d`, extraction commit `74e41cdc0173379b424014de151ae5413fd1c9a3`, extraction run `36329158287` and artifact `10935435820`.

`fixed_image_inputs.authenticate_origin` runs the existing read-only `export_m00_fixture.py --verify-committed` against that one archive and requires exact agreement with the compact fixture. This is **historical input authentication**, not a reproducible new M00 build, historical Player-result reuse, or acceptance of Local's unproven cache copy. No claim of a fresh bit-identical compilation is made.

`fixture_project` now requires both immutable Git blobs and the original six-site reflection configuration. It explicitly excludes the ignored M00 directory as a source. Before any resource-project Unity invocation, the existing `ordinary_input.prepare` writes the image under a new isolated root and emits its source-pin-bound materialization receipt. Existing wrong bytes are preserved and rejected, never overwritten; absent/changed receipt, image, origin, configuration, path or source binding fails verification. Every later resource phase rechecks the materialized input.

Both `FixedAssemblyBytes` sites are audited together: `m00-normal-hot-update-image` and `h1-count-ordinary-witness-image`. Their image path, SHA, provider and original Development/Release semantic variants remain unchanged. The six-site configuration stays byte-identical at SHA-256 `26837a5f710abae42a69a85ea2edf66939eff9afa6f6e8ce5b8e2cafc44f564a`.

## Actual consumer and negative controls

A separate supervised Unity invocation of `R03CompletionFixedImageContract.Verify` runs after the existing capability preflight and before the resource compiler. It requires the exact project/baseline/profile/Unity/target/receipt root, invokes the production `ShadowReflectionBindingEvidence.ValidateProjectImages`, executes the shared actual package guard/encoder checks, and records before/after hashes of image, configuration, source pins, project authority, materialization receipt and both frozen-source files. It cannot claim snapshot compilation or runtime acceptance.

Ten controls retain exact codes: positive image; absent image; mutated bytes; wrong provider; Development selection; Release selection; missing mode; unknown mode; omitted semantic variant; invalid image path. Controls use separate preserved files. Original live inputs cannot be edited to manufacture a negative result. The verifier checks exact operations, mutations, modes, paths, complete control membership, codes, source hashes and false authorization flags.

Development and Release controls prove selection of the two existing configured variants. They do **not** prove that a newly compiled target provider matches either variant. That remains the unchanged production snapshot/ILPP/policy contract. The exact pinned Unity Mono encoder independently identifies this frozen DLL as the existing Development variant `7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369`; the Release variant remains `e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022`. No additional hash variant is accepted.

The .NET host records its encoder observation without presenting it as pinned-Mono evidence. CI separately compiles and runs the actual guard/encoder sources using Unity 2022.3.62f2's Mono and reference profile. Unused host model boundaries are explicit and do not emulate Unity or production acquisition policy. Actual Editor preflight and successful reflection-enabled Player compilation remain Local work.

## Verification completed

Matching host workflow `37188867823` Passed on Linux and macOS: 148 completion Python contracts (41 new LK tests), 183 retained R03 contracts, ten fixed-image guard cases, 20 capability helper cases, 12 constructor cases, 32 qualification cases, both nine-case graph suites and 35 admission cases. Both hosts also reauthenticated the pinned archive/member against the compact input. All 17 owned commands per host completed without survivors.

Pinned-API workflow `37188867837` Passed: 16 resource assemblies / 654 source files, plus the separate fixed-image probe compilation and pinned Mono execution; all 18 owned commands Passed. Compiler warnings remain preserved (927 recorded), not suppressed. The pinned Mono probe Passed all ten controls and the original Development semantic comparison. No Unity Editor or Player was launched by these workflows.

Primary downloaded and authenticated all three exact-source artifacts, including unique/safe membership, every indexed size/hash, ZIP digest, source/package identities and command stream hashes. Host artifacts each contain 541 indexed files / 542 ZIP files; API artifact contains 172 / 173. Current-container reruns passed 148 completion and 183 retained tests; syntax parsing passed for 20 completion Python modules. See [N_HOST_EVIDENCE.json](N_HOST_EVIDENCE.json).

Review found no additional source defect requiring a new runtime change in this finalization. This is the Primary repair review, not the independent full R03 review. Original package/native guards, counters, producer lease, reflection sites, fixture DLL expectations, full Editor rosters and measurement protocol are unchanged. The full original archive recheck in this cycle was performed by source-bound CI; Primary authenticated its resulting evidence rather than claiming access to Local's live roots.

## Changed files since Local K

Only the demo changes: `.github/workflows/r03-completion-api.yml`; `Assets/AssemblyShadowDemo/Editor/R03FixedImageChecks.cs` and `R03CompletionFixedImageContract.cs` with their meta files; `Tools/AssemblyShadow/R03Completion/FixedImageTests/{FixedImageTests.csproj,Program.cs,MonoProbe.cs,SemanticDiagnostics.cs,EnvironmentBoundaries.cs}`; completion modules `compile_fixed_image.py`, `fixed_image_inputs.py`, `fixture_project.py`, `resource_pipeline.py`, `run_completion.py`, `run_host.py`, `test_lk_contracts.py`, `test_lk_reports.py`; this N repair/evidence/matrix record, README, CURRENT_STATUS and WEB_TO_LOCAL. The R02 frozen fixture/exporter/materializer and all three sibling repositories remain unchanged.

## Handoff, preservation and rollback

Batch L retains 90 cells, six fresh native builds, 59 fresh Players, the early 18-method Editor preflight and both 754/755 zero-skip rosters. Origin/materialization and ten actual fixed-image checks are added within existing prerequisites, not substituted for any runtime coverage. Use the new root in WEB_TO_LOCAL. Do not retry A–K, select old apps, relax hashes/modes, disable reflection ILPP or implement a non-trivial Local correction.

Connector tree/commit/non-forced-ref smoke verification passed on `codex/connector-smoke-r03-lk-20261004-0950`, commit `5b6dc6f5fd470fac13dd46c2c9d31891ac77a166`, including exact HEAD and file read-back. No delete-ref action is exposed; the branch remains disposable and non-authoritative. Four-repository read bootstrap succeeded; sibling repositories require no write.

Rollback requires a new reviewed Primary commit restoring a coherent source/profile tuple, not resetting or rewriting preserved evidence. Any failure stays Failed/Blocked with its seal result. Even a green L only returns EvidenceReadyForPrimaryReview. R03Accepted=false, H2Passed=false, qualificationApproved=false and expansion disabled remain mandatory; full-stage reconciliation and independent review remain Primary-owned.
