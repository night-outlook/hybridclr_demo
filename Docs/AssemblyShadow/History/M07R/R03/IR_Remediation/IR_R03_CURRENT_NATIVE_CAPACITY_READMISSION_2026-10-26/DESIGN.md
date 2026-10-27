# R03 oneuse-A storage BLOCKED — Primary remediation design (2026-10-26)

**Scope:** Primary response to IR-LOCAL-CURRENT-NATIVE-ORIGINAL-S-CAPACITY-01 only. R03, not H2/M08A/X02. The Local 20261026 oneuse-A attempt remains **BLOCKED / CapacityBlocked_CoordinatorNotRun**. No coordinator, Unity, SDK compiler, original-S archive audit, Player or 126-file parity check ran. Do not turn a pre-execution environment failure into a native-code finding or promote historical evidence.

## 1. Source and factual root-cause boundary

Authoritative Local checkpoint: Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261026-oneuse-a (FINDING.json, LOCAL_RESULT.json, STAGE_STATES.json, raw capacity/worktree/toolchain/preservation receipts). Exact current branch after Local publication before Primary: hybridclr_demo@542078a801463b29d234d4221800e6ec7fab27d4, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb.

Pre-worktree available 55,757,221,888 bytes (51.93 GiB). The separately mandated fc55 worktree creation succeeded once and reduced observed free space to 21,074,190,336 bytes (19.63 GiB), below the **existing immutable 20-GiB / 21,474,836,480-byte admission floor**. Later passive sample 21,783,199,744 bytes (20.29 GiB) is a separate observation, not retroactive eligibility or verified sustained capacity. Exclusive attribution of the observed change is unproven. **All ten stages NotRun**. The original S worktree remains clean and registered at /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse, commit fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b. Original coordinator output root oneuse-A was never created, but its authority/name is consumed.

A second pre-execution gap is explicitly recorded: PATH lookup for dotnet --list-sdks failed FileNotFoundError. Actual R03 PlayerFixtures.csproj source Git blob 6bd02a765a53d9fc1830d1026f2b02710172a092 targets net8.0. The previous Unity executable 2022.3.62f2 arm64 and Apple clang were observed, but .NET CLI/sdk/runtime availability was **not established**.

The capacity finding does not justify reducing the 20-GiB floor, deleting protected historical data, silently recreating fc55 or consuming oneuse-A a second time.

## 2. Primary decisions

1. **Reuse, not regenerate, original S fc55 worktree:** explicitly authorize read-only use of the retained fc55 path *only after a new independent admission* verifies it is still singly registered to the owning demo Git, detached exact fc55, clean (tracked and untracked), correctly rooted and has its canonical remote. Never force-add/remove/prune/repack/reset/check out/modify it during this cycle. Its original full evidence will still be read by the unchanged audit_s_provenance.py.
2. **Choose a fresh disjoint output root for oneuse-B**, never oneuse-A. Prefer a separately mounted, physically canonical macOS volume with **comfortable free capacity (30 GiB+ as advisory, not a proved lower bound)**. If using the original volume, new independent admission must pass the existing 20 GiB threshold immediately before launch; a marginal transient 20.29 GiB sample is not proof of run durability. Avoid cleaning historical roots, Unity or Git caches automatically. Capacity is checked on the actual output parent by the unchanged coordinator too.
3. **Read-only toolchain gate:** before launching the expensive combined 10-stage coordinator, check PATH-visible executable dotnet, a compatible SDK >=8, actual Microsoft.NETCore.App 8.x runtime needed to execute net8.0 fixtures, clang++ and lipo, and the exact committed R03 PlayerFixtures.csproj Git blob. The Local owner may activate an **already installed** .NET 8-capable arm64 toolchain via process-scoped PATH; no automatic system installer, PATH persistence or source modifications. If no usable SDK/runtime is available, return a distinct PrerequisiteBlocked with the observed command/paths; do not begin coordinator.
4. **Add source-bound no-write admission tool**, current_native_environment_admission.py, reusing existing exact four-repo remote/source, original fc55 and Unity 20-GiB admission functions. It creates **no** batch root or worktree and records the nuance between minimum disk test, advisory headroom and actual future Unity disk usage. Positive readmission is prerequisites only, not a new product test or permission to reuse the stopped run.
5. **One new precisely scoped WEB_TO_LOCAL** authorizes oneuse-B only after independent new read-only prerequisites pass. All ten original composite stages, 3 builds, 5 Players, 126 source-installed matches and original S archive/59 historical process crosswalk retain their existing assertions and historical outcome boundaries. Other product/native/managed source and previous evidence remain unchanged.

## 3. Alternatives and rejected shortcuts

| Choice | Decision | Reason |
| --- | --- | --- |
| Retain original S fc55, use a fresh larger output volume | **Preferred** | Avoids a second 30+ GiB materialization; isolates generated build/cache evidence from original checkout, preserves oneuse-A |
| Retain original S fc55, use same filesystem with newly admitted >=20 GiB | Conditionally allowed; risk of exhaustion | Existing hard floor stays intact; 20.29 GiB history is not stable assurance. Prefer comfortable capacity and collect both fresh samples and mount identity |
| Recreate worktree and delete retained one | **Prohibited this cycle** | Destroys/collapses original custody and may reintroduce the same capacity blocker |
| Lower disk floor to 19 GiB / force previous oneuse-A | **Prohibited** | Defeats previously required fail-closed admission and consumed-root discipline |
| Move/delete historical evidence or automate aggressive cleanup | **Prohibited** | Preserves b7e3/c42a/f51d/original S and previous root identities |
| Run original S audit or build/Player stages separately before admission | **Prohibited by this one-use contract** | Creates incomparable fragmentary data outside the source-pinned coordinator |

## 4. Validation and unknowns

Primary CI is **host-only**. It tests read-only SDK parsing, retained worktree registration, 20-GiB threshold refusal, marginal-capacity distinction, source pin preservation, no-root positive path and missing toolchain refusal. Neither CI nor this document asserts actual .NET SDK availability on the Mac, a mounted alternate volume, sufficient sustainable Unity build space or successful Player runtime.

The separate 2026-10-08 independent R03 full-stage FAIL (High IR-R03-01/02) remains. D1=A NativeLayoutAdmissionV1 conservative / X02 deferred; D2=A performance observational only; four contaminated Failed certificates unchanged. b7e3/c42a overall Local FAIL and f51d historical-only PASS are immutable; original S historical 90/90 does not close R03. P1 incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 incomplete, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false and PureInterpreter disabled.

**Next gate:** oneuse-B independent preflight, then exactly one coordinator invocation in fresh root if all prerequisites pass. Failure before output -> PrerequisiteBlocked, not a partial product result. Local publishes factual results and returns to Primary; no autonomous subsequent milestone or independent reviewer/H2.
