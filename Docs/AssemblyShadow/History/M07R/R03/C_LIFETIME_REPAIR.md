# R03 C — managed build lifetime repair and batch-B preparation

Date: 2026-09-30. Primary Implementation self-review; **not independent stage review, Local acceptance, or a Human Review Gate**.

## Received evidence and finding

Authoritative Local return: `2a9fdec813592fd79db511d5db96a6dcf1dea620`. Read `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and `History/M07R/R03/local-validation-20260930-batch-a-return-required/` under `Docs/AssemblyShadow`.

R03 A remains `ReturnRequired`: **4 Passed, 3 Failed, 29 Blocked**. The source-bound build receipts 0005–0007 record exit 0, no timeout and a surviving process group. The host programs were not executed; Unity, EditMode and all nineteen Player cases were Blocked/NotRun. The seal passed; Local authenticated 58 indexed files and 59 archive members. Primary has not relabeled those cells or claimed access to the retained macOS live root.

Original A result SHA-256: `a03a2b2cc2f493ca92f782eed0a2b03d040c45a826333581818c96200c4a9173`.
Original A index: `a14717414c030ac734fc2e9543118b507df4465b55cbbeb4a9af0bf5a0756181`.
Original A archive: `13cf7407447d7952aae6429bbf8e5aae3fc11a030ae139651a09142324450c6c`.

**R03-LA-001:** the production managed build helper used default persistent-worker settings while its command boundary required immediate process-group completion. The old CI directly invoked dotnet and did not test that boundary. Persistent Roslyn/MSBuild workers are a supported explanation, not a directly observed identity: A captured no child roster. That uncertainty is retained.

## Design and implementation

The correction prevents persistent build workers at invocation rather than accepting survivors or stopping unrelated servers.

- Managed build arguments now end with `--disable-build-servers`, `-p:UseSharedCompilation=false`, and `-nodeReuse:false`.
- Child environments explicitly set `DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER=1`, `DOTNET_CLI_USE_MSBUILD_SERVER=0`, `MSBUILDUSESERVER=0`, and `MSBUILDDISABLENODEREUSE=1`. They do not mutate the parent environment. This follows the existing R02 child-policy direction while explicitly overriding inherited server selection.
- The existing Mac TMPDIR contract remains `/private/tmp`; host-only Linux commands use the platform temporary directory.
- `Batch.command` delegates to `run_owned_command`. All original command deadlines and the 36-cell scheduling/dependency rules remain unchanged.
- An observed nonempty process group remains failure even if it subsequently vanishes or cleanup succeeds. There is no grace period leading to PASS, compiler-name exception, semantic retry, global `dotnet build-server shutdown`, `pkill`, or shared-server termination.
- Failure diagnostics capture at most 64 matching PID/PPID/PGID/state/executable rows, retaining at most 512 executable characters per row, with a three-second ps timeout. Other process arguments and environments are not retained. Diagnostics are advisory and cannot override the independent group-presence check.
- The pre-cleanup snapshot is written before signaling the owned group. Unavailable diagnostics do not prevent cleanup. Launch, timeout and cleanup errors produce a receipt before failure is returned. The original `remainingProcessGroup` observation is separate from `postCleanupGroupExists`.
- The fresh command receipt is version 2, `lifetimePolicy=R03OwnedCommandV1`. This is tooling evidence only, not a change to native manifests or Player result schemas.

The group contract remains a POSIX process-group contract; this patch does not claim a new proof about arbitrary descendants that deliberately detach into other sessions. Server prevention is scoped to these invocations. No native, managed-package, fixture, Player expectation or runtime admission rule changed.

External reference, not empirical evidence: Microsoft's `dotnet build` documentation describes `--disable-build-servers` as available since .NET 7: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build . The current source/command results below are the actual evidence for this repair.

## Changed files and commits

Implementation commit: `94f2612a6c64c341ac38efcaf01952cb594f47d8`.
Evidence packaging correction / final tested source anchor: `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`.

- `Tools/AssemblyShadow/R03/run_local.py`: command delegation and explicit managed build policy.
- `Tools/AssemblyShadow/R03/command_lifetime.py`: owned lifetime, prevention, diagnostics and receipts.
- `Tools/AssemblyShadow/R03/test_command_lifetime.py`: fourteen additional policy/real-process regressions.
- `Tools/AssemblyShadow/R03/run_host_lifetime.py`: executes the actual production `Batch.command`, `Batch.managed`, fixture checks and assertions in a host-only receiver. It cannot emit Local-batch acceptance and does not bypass the real Local entrypoint.
- `.github/workflows/r03-primary.yml`: Linux/macOS matrix, .NET SDK 8.0.318, exact candidate/reference packages, same-wrapper checks, source integrity and full artifact retention.

The later transport commit adds this record, `C_HOST_EVIDENCE.json`, `C_VALIDATION_MATRIX.md`, and updates canonical README/status/WEB_TO_LOCAL. Local-owned reports, A's checkpoint and historical evidence are unchanged.

## Primary execution evidence

The 14 new tests passed in the current Linux container. The complete downloaded-source Python suite also passed **43/43** (the original 29 plus 14); no .NET SDK or Unity was installed in this container. Real .NET execution was performed through committed GitHub Actions source, not simulated locally.

Final workflow run **36739214352**, source `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`, passed both jobs:

| Observation | Linux x86_64 | macOS 15.7.9 arm64 |
| --- | --- | --- |
| SDK | 8.0.318 | 8.0.318 |
| Python contracts | 43/43 | 43/43 |
| Reference graph assertions | 9/9 | 9/9 |
| Candidate graph assertions | 9/9 | 9/9 |
| Admission/method assertions | 35/35 | 35/35 |
| Native-input DLL generation/authentication | 15 | 15 |
| Actual managed builds, including Runtime API compilation | 5 | 5 |
| Positive command receipts | 12, all exit 0/no survivors | 12, all exit 0/no survivors |
| Exact indexed artifact files | 308/308 | 308/308 |
| ZIP file membership | 309/309 | 309/309 |

Job IDs: Linux `109968830606`; macOS `109968830280`.
Artifact IDs: Linux `11109447043`; macOS `11109422025`.
ZIP hashes: Linux `dafa35ee4ce89481549612924eafa18393b829153f4be6da02fe6c3de5299eab`; macOS `41b37bde8cf30c3e9cef1363ae754ae2382a610d5d7542103a076f8c7548d1c6`.

Primary downloaded both final archives and authenticated their ZIP digests, exact membership, all indexed sizes/SHA-256 values, result provenance and command stream hashes. No duplicate or unsafe members were accepted. `C_HOST_EVIDENCE.json` records each positive command PID and receipt hash, platform, source anchor and archive/result/index bindings. Raw host receipts are in each artifact's `lifetime/execution/commands/`; managed assertions and fixtures are under `lifetime/execution/host/`. These host archives are not the full Local evidence seal. Their GitHub retention ends on 2026-10-14; retain downloaded originals for later review.

**Packaging finding discovered and fixed in Primary:** first run `36738866381` passed the host checks, but Linux artifact `11108835773` omitted five indexed `.NETCoreApp,Version=v8.0.AssemblyAttributes.cs` files because upload-artifact excluded hidden files. Its ZIP digest was `62edd6c1d8c1148aec15795d26fc89d2f0d3dd4ec2eabb980479ad47dcae869a`. That archive is explicitly incomplete and is not final custody evidence. Commit `7e2852...` enables hidden-file inclusion for this generated, source-only host evidence root; the fresh final run above satisfies exact membership. Expectations and hash checks were not relaxed.

## Self-review disposition

R03-LA-001: **fixed in source and host-validated; Local revalidation required**. Clean real builds and subsequent assertions are proven on Linux and macOS arm64 with SDK 8.0.318. This is not a retrospective identity claim about A's surviving child, nor proof of behavior on Local's macOS 26.5 environment or of any Unity/native execution.

No-survivor enforcement: retained and regression-tested with a real exit-0 parent leaving a child, timeout, nonzero exit, startup failure, unavailable diagnostics, disappearing-group race, immutable output roots, and an unrelated live sentinel. Cleanup never changes failure into success.

Artifact completeness: corrected in Primary and independently reauthenticated for the two final downloads. Product semantic scope: unchanged. Independent full R03 review: NotRun/NotEligible.

## Bootstrap, pins and transport

All four feature refs were read through the Connector at entry and matched the Local return. Branch: `codex/assembly-shadow-r01b-h1`.

- HybridCLR: `041c0cbb42d3e64e54fe605673d99799b5d63893` (unchanged).
- Package: `120bb01be680cec0375002a0823552d66d34b84c` (unchanged).
- IL2CPP: `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` (unchanged).
- Demo: new tested source anchor `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`; final documentation transport is its source-identical descendant identified by the final Primary prompt and live handoff.

A new demo Connector Git-tree/commit/ref smoke succeeded on disposable branch `codex/connector-smoke-r03-lifetime-20260930`, base `2a9fdec813592fd79db511d5db96a6dcf1dea620`, smoke commit `ad4f308648241e624117a57da2f668dd603c0cc8`, with exact ref read-back. No external repository write is needed in this repair; their earlier four-repository smoke records remain in `B_PRIMARY_HANDOFF.md`. Delete-ref is unavailable; the new disposable branch remains non-authoritative.

## Next Local cycle and rollback

`WEB_TO_LOCAL.md` authorizes one new B root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`. A remains untouched. The original **36 cells / four Unity builds / nineteen Player cases** remain required; the existing verifier cell now includes the added fourteen tests. No non-trivial work is assigned to Local. Any further source/lifetime/semantic issue returns to Primary with immutable receipts.

Rollback must be a new coherent Primary-controlled source/handoff revision, preserving A/B and host evidence. Do not reuse old binaries, repair failed evidence in place, or run the old A output root. Source-before-repair remains available at `2a9fdec...` with the unchanged external tuple for read-only comparison.

R03Accepted=false; H2Passed=false; PureInterpreter structural expansion remains disabled. R02 deferred CPU and original H1 RSS risks remain visible. Full R03 regression, broader method/generic coverage, startup/capacity/performance/memory, gated PureInterpreter work and stage review remain outside this focused repair and Primary-owned.
