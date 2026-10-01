# R03 D — fixture-reference and Unity compiler-lifetime repairs

Primary Implementation self-review and source-bound host evidence. CI evidence was produced on 2026-10-01 UTC. **Not Local acceptance, independent stage review, or a Human Review Gate.**

## Received authority and preserved facts

Local return: `ec463b6dfbd91603ec0c539378af6dbbe6b9e651`.
Executed B demo: `a261bdf0db3f1432226a6b6b69f6f56fbbc47d34`.
Read `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and `History/M07R/R03/local-validation-20260930-batch-b-return-required/` under `Docs/AssemblyShadow`.

B remains **ReturnRequired: 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. Direct managed lifetime, both 9-case graph suites, 35 admission cases and generation of fifteen DLLs passed. Four build invocations and the independent EditMode invocation failed at C# compilation. Editor assertions, IL2CPP/native builds and nineteen Players did not run. Local authenticated 407 indexed files and 408 archive members. Primary does not claim access to the retained macOS live root and has not rewritten either Local-owned report or any A/B checkpoint.

B result/index/archive SHA-256 values remain:
- `3c8646fa68556b987469467c473e7bff6b529abbd8df3b1693a0a49a20738870`
- `ec1feae707274098acfbce3f83696a0ce1d2aa734318254bb84d54878cb63887`
- `a09d5480508a6d40bf619f925b76144693faf5ed637dbf7ac1c7fed5cec86ebd`

The earlier A failure remains historical. The successful direct managed path in B closes the demonstrated A-path symptom only; it did not prove Unity compiler ownership.

## R03-LB-001: exact unsigned AssemblyRef construction

The shared `EvolutionFixtureCorpus.Build` used dnlib's two-argument `AssemblyRefUser(name, version)` constructor. B's metadata diagnostics observed the resulting provider reference with PublicKey bit set and zero key bytes, while its provider AssemblyDef was unsigned. The Unity logs report CS0009 Invalid public key. The constructor overload's default full PublicKey is consistent with that observation; this is not a native layout failure.

The generator now explicitly supplies `new PublicKeyToken()` and `HasPublicKey=false`. It preserves provider names, versions, graph directions, class/method definitions and static graph witnesses. Existing sealed DLLs are never edited. New source builds produce new exact input hashes.

`FixtureAudit` independently reopens all **15 Player DLLs plus 18 shared-corpus DLLs**. It verifies unsigned definitions, full-key flag clear, empty local-provider tokens, eight-byte corlib tokens, provider identity/actual peer binding, the declared graph edges and static Player provider fields. The audit also creates a separate deliberately malformed A.dll copy to reproduce the original empty-full-key defect. That copy is not part of the fifteen accepted Player inputs.

Compiler-consumption tests then compile actual consumer DLLs against each of the 33 inputs, using explicit aliases for duplicate logical type names. Consumers reference the type and emit a call to its retained Keep method using its declared instance/static calling shape. A separate negative consumer must exit 1 with both CS0009 and Invalid public key, emit no consumer DLL, and leave no owned processes. Arbitrary errors are not accepted as this negative proof.

The host toolchain is .NET SDK 8.0.318. Local uses the actual pinned Unity 2022.3.62f2 `NetCoreRuntime/dotnet`, `DotNetSdkRoslyn/csc.dll`, and the NetStandard reference paths recorded in B's Editor.log. The exact compiler/runtime/reference files are hashed before and after consumption. The host compiler is not represented as the Unity compiler.

## R03-LB-002: explicit Unity command completion

The direct .NET build-server opt-outs remain unchanged. B's Unity Bee command explicitly used `/shared`, which is a separate lifecycle boundary; the captured comm field proves an owned dotnet process but does not establish its exact executable arguments or identity as a specific server. That uncertainty remains attached to B.

R03 now reuses the existing, unchanged **R02OwnedUnityRoslyn-v2** supervisor and its kernel birth-identity implementation. `unity_command.py` places that supervisor inside the fresh process group created by the unchanged R03 `run_owned_command`. The actual Unity command runs inside the supervised group. Before the supervisor returns, it requires completion of only the exact compiler descendants belonging to that invocation, anchored to the selected Unity installation's VBCSCompiler.dll and authenticated by PID, PGID, UID, kernel birth identity and command shape. Unknown, new or changed descendants fail closed. Bounded termination and census observations are retained in `unity-completion.json`.

This is an explicit supervised lifecycle, not a dotnet-name whitelist, global server shutdown, or a reinterpretation of an already-failed outer command. The outer **R03OwnedCommandV1** no-survivor check and its raw pre/post-cleanup observations are unchanged. A compiler that remains after the supervisor returns still causes failure. The supervisor preserves the original inner command exit code; normal Unity builds and EditMode still require exit 0. The outer command PID now identifies the supervisor, not the inner Unity executable; native Player cases remain direct fresh-process launches with their original PID binding.

The three reused source files are unchanged and hashed around each invocation:
- `Tools/AssemblyShadow/R02/unity_session.py`
- `Tools/AssemblyShadow/R02/process_identity.py`
- `Tools/AssemblyShadow/R02/evidence.py`

The adapter verifies the outer receipt, supervisor policy, exact command, original exit code, clean completion, compiler file binding and unchanged support sources. Only batch-owned isolated projects can use its Unity entrypoint. A separate explicitly named negative compiler probe is allowed to expect original exit 1; it must also prove the intended CS0009 diagnostic and no execute-method marker. It never changes a failed product build into success.

Selection rationale: direct build-server opt-outs demonstrably fixed the direct managed path but do not remove Unity's recorded `/shared` argument. The existing birth-authenticated supervisor provides a source-reviewable scoped lifecycle without patching the installed Unity SDK or guessing an unsupported Unity switch. No alternate fallback silently accepts unknown descendants.

## Additional Local subchecks; original scope retained

The existing `player-fixtures` cell now includes metadata auditing, **33 pinned-Unity compiler consumers plus one deliberate invalid-key control**, and two additional isolated Editor projects: a valid compile/execute-method marker probe and an invalid-key compile-failure probe. Both Editor probes use the same supervisor adapter as the four normal builds and EditMode. Their source, copied DLLs, logs, command receipts and completion receipts remain in the new batch root.

The top-level ledger remains **36 cells**, with the same four native build roles and **nineteen fresh-process Player cases**. No Player expectation, runtime admission rule, native/package pin, original command deadline or product source was changed. The existing Python verifier cell now runs 57 tests (43 retained plus 14 new policy/input tests). Failure of a new prerequisite blocks dependent work rather than bypassing it.

## Primary verification and limitation

The 57 Python tests passed in the current Linux container. Real .NET execution used the committed GitHub Actions workflow, not an installed local Unity engine.

Final tested source: **`5c2932d5340728b16302b7cea8f20b64fcc9e7ce`**.
Implementation commit: `c72893c0df9452aa46a45a1f723b71f62512a0e6`.
Final CI run: **36805988857**.

| Check | Linux x86_64 | macOS 15.7.9 arm64 |
| --- | --- | --- |
| SDK | 8.0.318 | 8.0.318 |
| Python contracts | 57/57 | 57/57 |
| Reference/candidate graph suites | 9/9 each | 9/9 each |
| Admission/method suite | 35/35 | 35/35 |
| Player fixture inventory | 15 DLLs | 15 DLLs |
| Fixture metadata and real consumer compilation | 33/33 each | 33/33 each |
| Invalid-key control | exact CS0009, exit 1 | exact CS0009, exit 1 |
| Actual Runtime API compile | Passed | Passed |
| Real SDK `/shared` compiler success/failure supervision | both verified | both verified |
| Positive/expected-negative command receipts | 49 / 2, all process-clean | 49 / 2, all process-clean |
| Artifact indexed files / ZIP files | 620 / 621 | 620 / 621 |

The shared-compiler regression copies the actual SDK compiler to a unique **explicitly host-only** toolchain directory, observes a real compiler child in both success and failure cases, and verifies scoped retirement plus an unrelated live sentinel. Its `.app/Contents/MacOS/Unity` file is only a path anchor for testing the existing supervisor, clearly marked as not an engine executable; no Unity Editor is invoked or simulated as empirical engine evidence. Actual pinned Unity compiler/Editor probes remain **NotRun in Primary**, implemented for Local C. The successful host evidence does not prove behavior on Local's macOS 26.5 or the full Unity/IL2CPP build graph.

Primary downloaded both final artifacts and verified ZIP digests, exact membership, all 620 indexed sizes/hashes, command stream hashes, source provenance, original negative exits and supervisor completion records. `D_HOST_EVIDENCE.json` records job/artifact IDs, result hashes and command-inventory bindings. Raw inputs/consumers and process completion receipts are retained in the artifacts. GitHub retention ends 2026-10-15; retain downloaded originals for long-term review.

Linux artifact **11137537132**, SHA-256 `99e7fa543915d3ce5292e3ff530c5cc74d1974cc867eae29e0e7c8db11f1e3b0`.
macOS artifact **11137658546**, SHA-256 `a2a1e99d4d30854f5b513a912a6f6c7014d2b41f0cf6765b6639fdc22aef8c3a`.

An initial CI run at c72893c failed because the new consumer incorrectly assumed instance Keep for the existing value fixture, whose method is static. Commit 5c2932d corrects the consumer calling shape. The fixture/native expectation was not changed and CS0176 was not relabeled as an expected failure. Initial run 36805795209 remains a failed Primary test attempt, not final evidence.

## Self-review disposition and changed files

R03-LB-001: **fixed in generator and host compiler-validated; pinned Unity revalidation required**.
R03-LB-002: **supervised lifecycle integrated and real shared-compiler host-validated; actual Unity revalidation required**.
No new runtime semantic acceptance or independent stage review is claimed.

Changed implementation/tooling paths are the common fixture generator; new `FixtureAudit/FixtureAudit.csproj` and `Program.cs`; `input_validation.py`, `unity_command.py`, `test_input_validation.py`, `run_host_inputs.py`; the existing `run_local.py`/`run_host_lifetime.py`; and `.github/workflows/r03-primary.yml`. Later transport changes are only this D record, D evidence/matrix, canonical README/status and WEB_TO_LOCAL. The outer lifetime helper, reused R02 supervisor, native/package sources, Player fixtures' runtime expectations and all Local-owned evidence remain unchanged.

## Source authority, smoke and next cycle

All four repositories remain on `codex/assembly-shadow-r01b-h1`.
- HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`.
- Package `120bb01be680cec0375002a0823552d66d34b84c`.
- IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`.
- Demo tested anchor `5c2932d5340728b16302b7cea8f20b64fcc9e7ce`; final docs-only transport identified by the live handoff and final Primary prompt.

Connector Git-tree/commit/ref smoke passed on disposable `codex/connector-smoke-r03-inputs-20260930`, smoke commit `57f56e91888f4567bc4fb8413b2d045e0cbd1399`, with exact ref read-back. Delete-ref is not exposed (current discovery returned file deletion only); the branch remains non-authoritative. No external repository write is needed; their previously recorded transport smokes and current read-back source pins remain intact.

Local C uses only the new root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`. Its actual existence must be checked locally; do not delete or reuse it if present. Do not retry A or B. Any new non-trivial issue returns to Primary with immutable diagnostics. Rollback requires a new coherent Primary-controlled handoff/rebuild, not patching sealed DLLs or reusing failed output roots.

R03Accepted=false; H2Passed=false; PureInterpreter expansion remains disabled. R02 deferred CPU and original H1 RSS risks, full legacy/resource regressions, broader method/generic coverage, startup/capacity/performance/memory and remaining R03/gate work remain Primary-owned.
