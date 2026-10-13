# Primary implementation plan after SNAP-01

Current status: architecture and executable reference contracts published; production integration and real engine-owner binding **NotRun/unimplemented**. This is a continuation plan, not permission to run SNAP-01 again or a new Local runtime batch. All nontrivial changes below remain Primary-owned.

## P0 — evidence and executable design contracts (completed within scope)

Read exact SNAP-01 Local reports and first-error records at demo64da7e51d740d4816907a63864b9c006a9db4b85. Preserve collectionResult=EvidenceCollected and semanticBatchResult=ReturnRequired, all18 original cell outcomes, true slot14 reason9, prefix262145 only, actual engine51213/500ms and all old historical outcomes. Publish lossless wire/consumer reference, native coordinator model, negative controls and source-bound CI. No production code changed. This completion does not certify native scheduler capability or Player repair.

## P1 — native complete diagnostics and bounded capture (Primary)

Targets after separate source audit: native general/execution serializer bodies, test-only R03 probe and their direct tests. Add an output-sink serializer without changing JSON fields/values/ordering/escaping. Reuse the same emission logic for legacy and V2. Design the frozen native capture so no managed callback or filesystem I/O occurs under metadata/transaction locks. Prepare all buffers/descriptors while healthy, measure peak allocation/capture usage, and enforce the pooled4MiB transport budget plus separately reviewed process-memory/capture limits. Exact length must be reported only when genuinely counted to completion; overflow preserves partial measurement as a lower bound.

Exit: whole legacy-vs-stream byte equality for actual serializer outputs; complete slot14+15 paths; oversized aggregate fails; no terminal marshalling allocation; original side-effect/recovery guards unchanged. Add strict/sanitized native writer, UTF-8/control-character, hash-vector, missing/duplicate/order/length, early/partial-I/O and resource-bound tests. Preserve original failure records and negative test logs.

## P2 — filesystem transaction and semantic verifier integration (Primary)

Preopen exactly one same-run artifact with canonical no-follow directory descriptors; bind file identity and exact raw/request/PID/build/four-source hash context. Incremental hashes and complete footer, then fsync/close both artifact and envelope; partial outputs are retained but never accepted. V2 resolver must reject mismatched/forged/trailing/partial content before returning data, preserve tagged transport identity and call unchanged original semantic predicates. V1 historical verification remains unmodified. Do not synthesize fake V1 raw or turn a failed report into a pass.

Exit: actual C# native declarations/emitter and native producer/sink/verifier integration, not mechanically transcribed pseudo-emission alone. Five existing Player case schemas and all original source/ABI/file bounds are covered in host tests; file-race and corruption controls fail closed. The original report counters and500ms/1..64 bound are untouched.

## E0 — native engine-owner capability gate (Primary dependency)

Identify a legitimate source/vendor-supported scheduling safe point and native lifecycle interface for **Unity2022.3.62f2 StandaloneOSX**. Required input: actual declarations/implementation or documented registration contract, exact engine/module source/build identities, owner thread and lock context, managed callback queues, in-flight cancellation/drain behavior, GC/finalizer/service maintenance and shutdown/restart semantics. A symbol name, nonzero pointer, PlayerLoopSystem native pointer or managed quit method does not establish these capabilities.

This dependency is currently unresolved. Do not delegate reverse-engineering, ABI guessing or scheduler design to Local, and do not register the reference Coordinator as if it controlled Unity. If the platform cannot supply the required interface, return a precise unsupported-integration/design decision; no test-bound relaxation or early-exit acceptance.

## E1 — scheduler adapter and native supervisor (Primary)

Implement authenticated healthy-time registration, single first-cause request, prearmed native wakeup, actual owner safe-point acknowledgement, closure of new managed admission, truthful queue drain and native-maintenance receipts. Do not alter Runtime::Invoke to return default results. Retain original class/method/finalizer guards and uncapped reporting. Typed ownership ticket includes run/generation/source/process identity; unsupported, stale or mismatched adapters reject registration.

Maintain the original full500ms observation starting with the true trigger, not acknowledgement. Collect report delta and maintenance liveness through exact original code. Require actual1..64 reports and unchanged logger/GC/canary/recovery assertions; late managed dispatch, missing maintenance, excessive reports and native-fatal remain failures. Supervisor restart uses separately authenticated new process/run identity after complete evidence and reviewed native lifecycle disposition. Do not equate an internal ReadyForRestart bit to proven teardown or clean finalization.

Exit: coordinator-to-actual-adapter source coverage, no arbitrary pointer/interface assumption, lock/thread ordering review, original policy/header equivalence except explicit approved integration, rollback and unavailable-capability behavior. Contract tests include the unchanged51213 failure. Normal shutdown/resource cleanup remains separately unqualified until tested.

## P3 — consolidated source-bound preparation (Primary)

Combine reviewed P1/P2 and E1 in one coherent four-repository tuple. Update the demo native pin only after native commit publication, and compile against the complete official managed/55-native SDK matrix. Run all original host suites, current snapshot/C# marshalling tests and new transport/coordinator/adapter tests on Linux and macOS. Perform independent code review of terminal paths, durability and engine ownership. Preserve warnings and original failed statuses. Update source/ABI schema manifests, build packaging, sidecar capture/index/seal, exact metadata inventory and the Local batch plan. No nontrivial Local repair.

## V1 — next Local cycle (inactive)

Only after P1/P2/E0/E1/P3 pass and a **separate exact-four-SHA WEB_TO_LOCAL** is published, designate seven unused roots for a fresh successor (no root names are authorized by this plan). Local reauthenticates all historical source/fixtures/custody, current host/compiler results and SDK before state; full original-C416844/339367/77477 scoped before/after remains required, strict custody still Blocked. Both fresh source-bound compiler gates and independent diagnostic/execution storage admissions must pass.

One original three-build/five-Player runtime attempt can then check the complete slot14/15 byte/hashes, native snapshot durability and unchanged three ON/OFF semantic proofs, actual scheduler ack and native maintenance, original engine sentinel/logger1→1/GC31/recovery/1..64 uncapped reports over500ms, actual Bee processor/factory restoration, and a separately identified restart receipt. Do not add an unreviewed sixth Player or weaken existing exit/raw checks. Any failure preserves the original verdict; collect source-bound diagnostics and stop. A focused pass is not full R03 acceptance or Human Review Gate approval.

## Definition of present delivery

Completed: two design documents, executable host reference codec/consumer, native lifecycle contract,36 Python controls and21 native scenarios per strict/sanitized profile, cross-platform CI, audited test artifact inventory, paused canonical handoff and this Primary plan.

Not completed: native serializer/sink integration, new disk transaction in Player, semantic verifier transport dispatch, authenticated StandaloneOSX scheduler adapter, real GC/finalizer maintenance, actual lifecycle/restart, new official product compilation or corrected Player execution. Local has no runtime assignment from this delivery. Current owner remains Primary Implementation.

All acceptance flags false; independent full-stage R03 FAIL/re-review NotRun, original strict historical S custody Blocked. No H2/X02/M08A/PureInterpreter expansion or automatic Human Review Gate.
