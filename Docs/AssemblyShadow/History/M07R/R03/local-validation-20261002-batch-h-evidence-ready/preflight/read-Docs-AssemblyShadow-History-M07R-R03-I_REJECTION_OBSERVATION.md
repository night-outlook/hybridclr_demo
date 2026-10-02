# R03 I — owned staged identities and non-mutating rejection observation

Primary Implementation design, source review and validation record, 2026-10-02 UTC. **Not independent stage review, integrated runtime acceptance, or Human Review Gate approval.**

## 1. Received authority and preserved batch G

Local publication `0d8a19830ce454d22335c854978816a830997187` records exactly one batch G executed from demo `78767ea4d7ea064115daffcdbb2ce9435569814c`. Read the unchanged `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md` and `History/M07R/R03/local-validation-20261002-batch-g-return-required/` under `Docs/AssemblyShadow`.

G remains **ReturnRequired: 37 cells, 32 Passed / 5 Failed / 0 Blocked**, focused seal Passed. Four fresh builds and all 754 selected Editor cases with zero skips passed. All 23 Players ran. The six strict isolated warm witnesses and the full positive C07 case passed. All four natural producer controls identified the actual ArrayPool Gen2-finalizer callback; their diagnostic results passed while their contaminated unisolated warm certificates remained Failed. Those distinctions are preserved, not collapsed into a generic Player pass.

The five failed main cases are C02/C08/C09/C10/D01. They reached Validate error 16/state 8, but late probe retrieval returned -3 and terminal diagnostics became error 15. The unavailable frozen M01 resource case remains NoCoverage. No prior failed cell, raw observation or acceptance state is rewritten.

Local authenticated 1,901 indexed files and 1,902 archive members, with 6,989 earlier custody bindings unchanged. Primary read the published records and sources, not the retained macOS live root. G's result/index/archive hashes remain:
- `65ee4842a81e7ec9e7d14546dd95d40d995e807a528e4b89c56918860100f5f1`
- `24c18f78be4ed43d8f8600e2f114d2b5c717180cf171ab4e1cd11eb807e8aa25`
- `2a3e90a49eb9b13d035a3749b8012f1e96d4410343d76b7f11a00617d17aaf23`

## 2. R03-LG-001: do not resolve a private type while reporting its rejection

The batch-G renderer retained physical layout class pointers and later passed them to `ProbeType`. Its full-key path called `AssemblyShadowTypeKey::Format(&klass->byval_arg)`, which uses `RawDefinition` and a metadata-handle lookup for class/value definitions. That lookup was attempted after private staging ownership ended. The metadata-only guard remained active, so an attempted managed failure allocation could itself trigger `ShadowAllocationDuringMetadataResolution Object::NewAllocSpecific` and replace the original observable terminal error.

The source establishes the unsafe late-resolution path and G records the -3/error-15 sequence. G does not provide an inner native stack or prove the first failing row, freed memory, or a unique initial decoder exception. The repair removes the path rather than inventing that missing attribution.

Chosen design: **capture owned identity bytes while the staged caller still has valid ownership, then serialize those bytes without decoding the rejected target again**. Do not widen private-image visibility, initialize old classes, bypass ownership guards, omit retained rows, downgrade full type keys, catch-and-restore terminal error 16, or accept error 15 as an equivalent rejection.

## 3. Implementation and boundaries

New `AssemblyShadowProbeTypeSnapshot.h` owns the assembly, namespace, name and complete declaration key in fixed buffers, plus an opaque physical identity. `Capture` is bounded and nonthrowing; missing inputs, oversized strings and capture failure have explicit statuses. A partial/truncated identity is not a valid snapshot. `WriteJson` prints only owned bytes and the numeric pointer value; it never dereferences that pointer. JSON escaping and the caller's numeric formatting state are preserved.

`RuntimeProbe::RecordLayout` now has a VM adapter in `AssemblyShadowRuntimeProbe.cpp`. The existing staged caller invokes it under its metadata lock/owner scope. It builds the key with `AssemblyShadowTypeKey::Make(klass).ToString()` from the already materialized definition/declaration chain, not a `Format(byval_arg)` round-trip through private type resolution. Identity capture precedes the probe mutex; only the completed row copy is placed in the bounded report. Capture failure marks diagnostic overflow/incompleteness, never a successful witness or a new transaction error.

The late layout renderer uses the captured baseline/target identity and status. Published warm targets and producer events retain their existing full-key formatter; a new native guard refuses a non-null live identity when no generation is published before entering that formatter. Raw AOT baseline initialization flags are still read for the existing positive C07 invariant. No claim is made that all fields of every published probe are now immutable byte snapshots.

Bounds are 512 bytes each for assembly/namespace/name and 4,096 bytes for the key, including terminators, with the existing 32 layout rows. The extra fixed report storage exists only in the enabled diagnostic profile. Ordinary probe-off builds exclude these identity buffers and the VM capture implementation. The repair does not change allocation caches, counters, physical admission, producer recognition/lease duration, staging ownership, terminal-state setters, deployment manifests or runtime APIs.

Fresh available runtimeProbe records use **schema 3**, adding each layout row's `identityPolicy=R03OwnedLayoutIdentityV1` and baseline/target capture statuses. Fresh overall Player raw observations also use schema 3 and add `rejectionProbe`, a JSON string with schema 1 / `R03RejectedProbeNonMutationV1`. Reference/off unavailability remains explicit; old schema-2 evidence is not upgraded.

## 4. Observe negative paths without mutating or restoring their failure

For the five existing Validate-16 rejection cases, the managed harness captures terminal diagnostics/recovery before retrieval, after a deliberate 16-byte buffer read expected to return -2, after a full read, and after a second full read. The first full receipt remains raw.runtimeProbe; the second and all return codes/captures remain in rejectionProbe. The final ordinary raw diagnostic capture is also checked. These are bounded observations after one transaction, not transaction retries.

The strict verifier retains the original Validate phase/code/state, no-publication/no-business-work and no-exception requirements. It additionally checks complete return lengths, both full probes, every retained layout identity/status and identical layout rows across reads. It compares the complete recovery document and an explicit immutable transaction projection across all observations: state/error/detail, baseline/patch identity, generation/counts/bytes, closure/stable/commit orders, assembly states, events and baseline uses.

Complete diagnostic documents remain retained. Their independent ordinary-class enumeration is not asserted to be an immutable transaction snapshot, and unrelated finalizer counters can progress between probe reads. Neither distinction permits a terminal error, reason, assembly state or layout identity to change. A probe exception, missing/oversized identity, error 15, skipped row, changed transaction event or restored failure is rejected. Prior observed rows may precede the failing type; the new evidence explicitly does not claim to identify the failing row.

All original positive checks remain: six strict all-thread warm witnesses, the finite drained producer lease, exact counter/event reconciliation, four unisolated attribution controls, positive C07 physical geometry, real MethodInfo/old-AOT guard, graph controls and scoped Editor coverage. No thresholds, warm-up, iteration counts, case identities, input DLLs or Local command deadlines changed.

## 5. Source inventory and tests

Final tested demo anchor: **`9d70494c97e4efc9597a3e071f63c1489c6ac396`**.
Native implementation: **`1cf87f8209790f9fb2ebec97487dc1990ccd56c5`** in il2cpp_plus.
Unchanged HybridCLR/package: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` / `120bb01be680cec0375002a0823552d66d34b84c`.
All branches remain `codex/assembly-shadow-r01b-h1`.

IL2CPP changes are `libil2cpp/vm/AssemblyShadowRuntimeProbe.h`, new `AssemblyShadowRuntimeProbe.cpp`, new `AssemblyShadowProbeTypeSnapshot.h`, and new `tools/r03/probe_identity_tests.cpp`. No allocation, finalizer, type resolver or ownership implementation is modified in this cycle.

Demo changes under `Tools/AssemblyShadow/R03/` are `PlayerProject/AssemblyShadowR03Probe.cpp`, `PlayerProject/R03Player.cs`, `batch_contract.py`, `runtime_contract.py`, new `rejection_contract.py`, `native_validation.py`, `run_host_lifetime.py`, `source-pins.json`, `test_batch_contract.py`, `test_runtime_contract.py`, and new `test_rejection_contract.py`. The top-level runner, Player case matrix and workflows remain unchanged.

Twenty new Python tests exercise terminal mutation at each boundary, capacity failure versus probe failure, missing/changed rows, explicit incomplete identity, read-byte binding, no publication/initializer mutation, old-schema rejection, preserved ordinary enumeration and the actual renderer's lack of private-handle formatting. Eleven native serializer modes run in three profiles (C++11 -O0, C++17 -O1, ASan/UBSan): source-buffer lifetime, copy lifetime, nested/generic key bytes, missing input, size bounds, escaping, numeric stream state, repeated reads/counters, failed recapture and stream failure. These are production-header/synthetic contracts, not new integrated Player evidence.

## 6. Completed validation

Host workflow **37014409670** passed on Linux x86_64 and macOS 15.7.9 arm64 at the exact source anchor. Each passed **183 Python tests**, both 9-case graph suites, 35 admission contracts, fifteen fixture DLLs, 33 audits/consumers, actual managed Runtime API compilation, previous provenance/scope and compiler-lifetime checks, **90 native header-test processes**, and unchanged R02 suites with **60 + 60 passed processes**. Each archive binds 159 fully owned command receipts: 157 exit 0 and two named expected-negative exit-1 controls; all completed without survivors/timeouts/cleanup errors. Another 148 legacy receipts have authenticated streams, not equivalent lifetime coverage.

Pinned-Unity workflow **37014409955** passed the complete build helper and three actual package dependencies (202 C# source files), plus **35 native translation-unit/profile syntax checks**: seven units across candidate, Debug, probe-off, diagnostics-off and feature-off. The helper emitted no diagnostics; the 61 existing package CS0649 warnings remain visible. The unchanged C helper still produces exactly its two expected CS0266 errors. These compiler checks are not integrated linking or Player execution.

| Final archive | Artifact | SHA-256 | Membership |
| --- | --- | --- | --- |
| Linux host | 11230060365 | `85425e1c2085157c0253d49cd28fc296f0a9fabf5495f4ed7152876a66f8cd87` | 1,446 indexed / 1,447 files |
| macOS host | 11228938971 | `fd0f42ebdcb1dc8e4b7413cc94b6c2c58e30ff2b9580371f592797dfbe3b02b7` | 1,563 indexed / 1,564 files |
| Pinned Unity API/native syntax | 11228879256 | `424926af51ead93b579637273eb73d4719c3b137fd0111dc9ae490242e40e219` | 139 indexed / 140 files |

Primary downloaded all three archives and authenticated exact safe/nonduplicate membership, every indexed size/hash, source tuples, edited source copies, results and command streams. I_HOST_EVIDENCE.json records the audit, individual result bindings and its limits. The archives expire on 2026-10-16. The current container separately reran all 183 Python tests successfully; .NET and pinned Unity/SDK compiler execution occurred in CI. No new Unity Editor or IL2CPP Player was launched by Primary.

## 7. Disposition and next validation

**R03-LG-001: source repair and host/compiler validation complete; integrated rejected-stage observation remains pending.** This is Primary self-review, not independent stage review. No G failure is retrospectively closed or promoted. Batch H must establish that all five negative cases retain error 16 through the capacity control and repeated complete reads, while all positive, warm, producer and physical checks remain intact.

Connector bootstrap read all four feature refs. Demo and IL2CPP writes each passed a disposable commit/read-back smoke on `codex/connector-smoke-r03-lg-20261002`: demo `36a3f130876a48c90ab784456bb6147f5b2bede6`, IL2CPP `806257b64a5633facca4dc242609bab1efc7988d`. Delete-ref is unavailable in the exposed actions; both branches remain disposable and non-authoritative. Unchanged HybridCLR/package reads are not represented as new writes.

The next unused root is `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002H-rejection`. Local receives a completed implementation and one prepared 37-cell batch, not a source-repair assignment. It must use the final exact pushed tuple in WEB_TO_LOCAL.md/the outgoing prompt, preserve raw before/after failure states, publish Local-owned reports/evidence and stop. Rollback requires a new coherent Primary source/handoff tuple, never mixed native versions, app reuse or historical result mutation.

R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. Full legacy/resource/P01–P05 and M01 coverage, broader generic/interface/delegate/stack-trace work, startup/capacity/performance/memory, gated qualification and independent stage review remain open. R02 deferred CPU and original H1 RSS risks are not waived.
