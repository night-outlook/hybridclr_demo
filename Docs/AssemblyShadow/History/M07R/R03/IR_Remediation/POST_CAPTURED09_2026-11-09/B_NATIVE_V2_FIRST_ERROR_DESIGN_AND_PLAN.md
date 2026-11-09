# R03 B — native V2 first-error, sink and epoch integration design and staged plan

Status: **Primary source design + inactive B1 host candidate only** (2026-11-09 UTC). No approved Unity build or Player run. The genuine captured generic A2 oneuse-09 is a focused PASS, *not* V2.

## 1. Actual code boundaries and failure ownership

The pinned native VM is night-outlook/il2cpp_plus at 41764ae1eeefb33b05966e7f7676e52aae39c340. Concrete source responsibilities:

- libil2cpp/vm/AssemblyShadow.cpp: `RecordFirstGuardFailure` is first-writer process-lifetime TypeFailure storage using `new TypeFailure{error,detail}` and a CAS on s_typeFailure. It records an immutable guard error on success, and std::string detail/exception formatting currently **allocate** on error paths. It does not provide a fixed-size copy to a V2 producer.
- CommitTransaction captures interpreter initializer errors into the transaction recovery fields after publication; state becomes FailedAfterCommit. This is a different first-error origin from AssertMethodIsActive (which produces error15 for captured baseline type).
- GetRecoveryInfoJson reads a mutable transaction snapshot under its mutex, then lets durable guard/unexpected/late-use/reference facts dominate. It formats into std::ostringstream and std::string and produces V1 recovery. **Its returned JSON is not a no-allocation first-error freeze** and a preopened V2 exporter must not treat repeated calls as a coherent native-wide epoch.
- Existing R03IR/bounded_v2/{BoundedDiagnosticsV2.h,PosixDiagnosticTransaction.h} implement a host-verified binary field14/15 codec and descriptor-relative POSIX transaction, but are **inactive** and do not collect real VM data or make V2 executable authority.
- New R03IR/NativeDiagnostics/FirstFailureFreezeV2.h is a **non-integrated**, bounded allocation-free first-writer copy of explicit caller-provided error facts. It is neither an alternate VM first-error source nor a complete V2 transport.

## 2. Normative invariants for the real integrated producer

1. **One originating first error:** choose a canonical VM source at the actual failure boundary, not by postterminal polling. Classify at least Guard, InterpreterInitializer, LateBaselineUse, ReferenceViolation and UnexpectedFailure with exact code/source. A captured first guard15 cannot be overwritten by a later Runtime::Invoke denial; initializer error19 must retain its exact sentinel. A successful control has **no** first terminal failure, not a fabricated empty V2 failure.
2. **No hidden allocations after terminal publication:** all storage/descriptor identity/serialization scratch must be reserved in healthy time. A source path that still constructs std::string/ostringstream after poison must be documented as not meeting this requirement; do not relabel an allocationful getter as a safe freeze.
3. **Strict copy/visibility:** first ownership CAS (Empty→Writing→Frozen or Invalid) is one-way and immutable; readers acquire a fully published snapshot only. For concurrent attempted writers, the first actual VM event is retained (subject to actual instrumentation and scheduling), later failures cannot replace it. A malformed original first event invalidates the V2 record instead of falling back to a later convenient error.
4. **Complete bounded fields:** keep the original UTF-8 reason/code/source and indicate explicit invalid/unavailable/overflow, never silently truncate. 4,096 bytes is the current *candidate* freeze limit, not an automatically approved production universal bound. A real longer first reason must fail closed and retain its native V1 source.
5. **Descriptor-relative exclusive output:** bind source four-repo SHAs, Unity/SDK/build, actual GameAssembly/executable, request/fixture/MVID, OS PID, nonce, case, file device/inode, artifact/envelope sizes and independent cryptographic digests. Use a new absent owner-controlled output directory and O_EXCL/O_NOFOLLOW with positive identity checks, full write/readback/fsync, complete-envelope publication, no duplicate/reopen, and durable receipt only after both names are authenticated. Historical output roots are never reused.
6. **No invented coherent VM epoch:** snapshot generation, candidate/closure and first-use locks are not a single global epoch; an equality/revision fence is a *bounded observational consistency check*, not global atomicity. To claim VM-wide coherence, specify and implement an actual global capture transaction barrier across metadata/class/managed executor and shutdown/GC paths, with time bounds and concurrency tests; otherwise explicitly return NotProven.
7. **No accidental promotion:** native V1 remains distinct from V2; a successful encoder/host/CLI or a well-formed V2 payload is never a full R03/H2/production acceptance. An independent real Player source/fixture/PID/VM-first-error join and later independent human-initiated full R03 review remain mandatory.

## 3. Staged Primary implementation

### B0 — bounded first-error candidate (implemented, non-integrated)

- Add FirstFailureFreezeV2.h and first_failure_freeze_driver.cpp. C++11/C++17 macOS+Ubuntu host tests cover normal15/19, no-copy source alias, invalid-first stickiness, strict UTF-8, 4096/4097 bounds, 12 concurrent writers and zero heap allocation within freeze/read.
- CI workflow r03-ir-first-failure-freeze-host.yml passes only `PassedHostLatchOnly_NotVmOrV2Transport` with all stage flags false. **Not a real VM first-error claim.**

### B1 — native originating first-error integration (next Primary implementation)

- Source-review exact implementations and callers of RecordFirstGuardFailure, s_typeFailure, transaction.recoveryTerminalError/detail, terminal/late/reference flags, GetRecoveryInfoJson, ReportUnexpectedFailure, initializer failure and terminal Runtime::Invoke. Enumerate precise error/event ordering under UsageLock, transaction mutex and metadata publication, including concurrent candidate publication.
- Choose a single actual native first-error owner. Integrate a bounded preallocated capture at **each original event producer** without changing failure precedence, application code disposition or error codes. Do not use GetRecoveryInfoJson to invent the first event after the VM is already poisoned.
- For guard15, bind actual owner baseline image/TypeDef, method_inst context and exact reason before postterminal denial; for initializer19 retain the actual original sentinel; for other origins provide a typed unavailable code when the original detail cannot safely be copied.
- Native host regressions for two competing origins, reentrancy, early failure, invalid/overlong raw reason, postterminal repeat, wrong epoch and poison-before-freeze. Compare the legacy V1 original recovery facts before/after a failed V2 attempt. Build native code against pinned Unity SDK source in Local only when source and CI gates pass.

### B2 — integrate bounded V2 transport into isolated test-only Player

- Compose the existing verified binary codec and PosixDiagnosticTransaction into the **new** isolated R03 probe; do not activate the dormant component in normal application builds or add hard-coded binary patches.
- Prepare all scratch buffers and an exclusively-owned output descriptor before the transaction/first possible terminal event. Reject path alias/symlink, unsupported filesystem flags, insufficient capacity, partial write/readback/fsync/close, double-commit, reentrancy, malformed/nonfinite JSON, wrong identity or changed input.
- Bind the VM-native frozen first-error snapshot and field14/15 records to independently authenticated source/PID/nonce/build/fixture/MVID context; ensure the reader distinguishes a valid V2 artifact from V1. Produce positive and adversarial host/native tests on macOS and Ubuntu. No new Unity run before complete source/pin/CI review.

### B3 — VM execution epoch and complete source semantics

- Explicitly define whether an all-VM atomic barrier is implementable without interfering with Unity lifecycle. Either implement/test that barrier across metadata, class execution, transaction use and shutdown, or record V2 data as individually frozen snapshots with **wholeVmEpoch=NotProven**. Do not claim global coherence from two equal counters alone.
- Verify failure-preserving managed shutdown, GC/RSS, native execution counter provenance and direct AOT entry breadth separately; keep selected/omitted original S compiler/object/link evidence and permanently unavailable historical roots visibly scoped.

### B4 — new Local Validation and independent review

- Only after B1–B3 source code and host CI are reviewed, publish an **entirely new** one-use Local contract with fresh absent roots, latest exact four Git SHAs, fixed Unity/IL2CPP and Player scenario roster, fresh dual-OS CI admission and fresh same-volume capacity/custody/Original-S gates.
- Run exactly the enumerated batch once; preserve unmodified raw V1 and new native V2, original error-code comparisons, real PID/source/first-error ancestry, product seal and failed attempts. Never rerun consumed oneuse-09 or substitute its prior Player binary.
- Primary reconciles Local facts; a **separate human-initiated independent full-stage R03 review** is required before any Human Review Gate or later milestone.

## 4. Explicit current stop

B0 is complete **host-only**. B1–B4 remain incomplete and are assigned to Primary Implementation / later Local Validation in their specific phases. The captured A2 focused PASS and initializer earlier PASS remain historical. Full R03 independent verdict FAIL; High IR-R03-01/02 open; all runtime/qualification/H2/Human Review Gate flags false, PureInterpreter disabled.
