# R03 B2 — Observed class root TypeDef/byval source fence: design, implementation and review

**Stage:** Primary Implementation, R03 B2 ONLY. **Date:** 2026-11-12 UTC. **Branch:** codex/assembly-shadow-r01b-h1 on all four canonical forks. **Native candidate:** night-outlook/il2cpp_plus@c37adc9f7cb610b524ae32b176cbc3e3f67cd35b; hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de unchanged. Demo source-admission anchor: hybridclr_demo@f952caacf72c686be87f0b37e0a1fc58f51930ac; read the newest pushed demo HEAD after this documentation update.

## Original source and defect

Original enabled V1 GetExecutionDiagnosticsJson (the pinned, unchanged 5,222-byte reference body) builds per-class rows from the registered Il2CppClass, obtains physical ownership through klass->image->assembly and formats the canonical TypeKey using klass->byval_arg. The inactive B2 collector previously checked exact class cctor/initialization-exception/static-storage primitives on three physically matched callbacks, and separately checked original V1 physical image identity/order/typeCount/tokens. **It did not compare the class's root image, definition handle, byval type tag/payload and generic-class pointer across those callbacks.** A registered class could retain the same address and cctor/static values but have a changed root after its owned TypeKey row was produced, without necessarily changing the registry revision, image token/count or R02 counters.

This is an *observational source consistency* concern. It is not evidence that the live Unity runtime permits arbitrary concurrent mutation of those fields, nor proof of their allocation provenance or lifetime.

## Bounded implementation and scope

The existing inactive ClassFacts snapshot now owns exact primitive copies of these fields per physically authenticated class registration slot: static-fields address, cctor started/finished/exception bits, root klass->image, klass->typeMetadataHandle, klass->byval_arg.type, its active union pointer when CLASS/VALUETYPE or GENERICINST, and klass->generic_class. It only reads a byval union member appropriate to the observed tag. Every sample occurs **inside the original g_MetadataLock and initial metadata-lifetime Reader**, after the callback matches the opaque registered identity and source witness. No new Class::Init, reflection, dynamic allocation, original getter invocation, reader session or Player entrypoint was added.

The source compares **SameRoot** before comparing **SameClassState** at the second physical callback, after per-row TypeKey formatting, and in the existing third end-of-collection physical traversal. Observed mismatches return the new typed error ObservedClassRootChanged, distinct from the existing ObservedClassFactsChanged for cctor/static facts. Positive receipt observedClassRootFactsThreePassStable is published only if all existing original V1 image, source, registration/R02, native B1 first-error and frozen-record fences succeed. Reject clears the new matched count and stable flag and revokes all owned rows and frozen record.

**Resource change:** ClassFacts grows from at most 16 to at most 48 bytes/slot. At 2,048 slots the reviewed maximum buffer is **98,304 B = 96 KiB on a 64-bit host**, an increase of **65,536 B = 64 KiB**; the separate 12-KiB original physical image-facts buffer is unchanged. This is unvalidated in real Unity worker thread stacks. An actual Unity IL2CPP/Player compile, stack measurement and profiler/Gc/RSS run is mandatory before any terminal B2 enablement. No global no-allocation claim is made because the existing VM iterator may allocate.

## Raw test evidence and source gate

The actual inactive production source .inl is compiled by NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp against a **synthetic VM**, not official Unity. [Native CI 43218731616](https://github.com/night-outlook/il2cpp_plus/actions/runs/43218731616), at native@c37adc9f7cb610b524ae32b176cbc3e3f67cd35b: **Ubuntu-24.04 C++11 and C++17 host jobs Passed**, Release and Debug, strict and ASan/UBSan profiles. Each host execution emitted **106 source cases and 3,194 assertions**, including seven new negatives:

1. definition handle changes before second matched class callback;
2. root image pointer changes during end pass;
3. root definition handle changes during end pass;
4. byval type code changes during end pass;
5. byval TypeDef handle/payload changes during end pass;
6. constructed-generic pointer changes during end pass;
7. an earlier class's definition handle changes while a later row's TypeKey is being formatted.

All negative paths reject partial data and clear source receipts. Existing cctor/static drift cases retain their separate typed error and previous AOT/interpreter bounded owner tests continue to pass. **macOS native C++11/17 jobs were queued at review time** and should not be represented as PASS until a completed run is independently verified. The exact four-fork Git blob source-admission CI must be checked at the final *demo* commit; a prior CI verdict does not transfer automatically.

In demo, the exact 63-native/eight-demo manifest pins the four changed native Git blobs and retains false flags for actual Unity source/GC/VM-epoch/field15/V2 acceptance. The admission gate verifies the new source read members, tags, root and class-state compare points, source receipts, unchanged original getter, typed error and explicit mock mode coverage. Negative unittest mutations reject false overclaims and source-schema drift. The permanent no-execution handoff is unchanged.

## Source-review findings and remaining blockers

- **ROOT-01 / scoped PASS:** The checked-in inactive native source now detects observed changes to class root identity/type source at the identified sample points, including earlier-row change during later-row TypeKey, without changing the original enabled getter.
- **ROOT-02 / provenance and semantic limits OPEN:** Copying pointer values does **not** prove the underlying metadata contents, name bytes, nested declaration chain, interpreter generic argument storage, object lifetime or pointer reuse (ABA). Not every original V1 row type is supported; open VAR/MVAR and other unsupported interpreter/generic shapes still fail closed. The root snapshot is not an atomic VM epoch.
- **ROOT-03 / latency/stack OPEN:** Additional 64 KiB on the native call stack increases unmeasured risk. Real Unity 2022.3 native full translation units, GameAssembly, Player/GC/RSS, profiler and platform worker-thread stack are **NotRun** for these SHAs.
- **ROOT-04 / full terminal field14 and field15 BLOCKED:** A complete original general finalDiagnostics field14 and full execution finalExecutionDiagnostics field15 need defensible preterminal coherent source/lifetime and immutable owned snapshots. One-owner descriptor-relative native V2 binary artifact/envelope, independent identity-bound external receipt/readback and authenticated first recovery are still unimplemented. Historical B1 oneuse-12 focused real Player 19/19 PASS is consumed and does not establish B2. Prior independent R03 full-stage FAIL/High findings remain open.

**Next Primary-owned step:** establish a complete original execution-class shape/source inventory and defensible metadata/class/GC lifetime epoch before terminal full-field V2 publication; resolve the 96KiB class buffer worker-stack requirement before a future Local run. Do not begin H2/M08A/X02/SNAP-01, self-approve Human Review Gate, or reuse consumed evidence.

**State:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled; WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION.
