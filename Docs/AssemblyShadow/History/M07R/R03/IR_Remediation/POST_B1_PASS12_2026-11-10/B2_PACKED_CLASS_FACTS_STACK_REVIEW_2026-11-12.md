# R03 B2 — Packed class-fact scratch: design, implementation, test, source review

Date: 2026-11-12 UTC. Stage: Primary Implementation, R03 B2 only. Branch: codex/assembly-shadow-r01b-h1 on all four repos. Native source: night-outlook/il2cpp_plus@39ac1a66b906da12825e095de010cae7cf5a8161. Unchanged: hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Demo code/test source anchor: 7a38e9d28eb580d463f1334df7e169c1978cb4d1; final demo commit is the latest pushed HEAD after this documentation change.

## Problem and choice

The inactive B2 producer expanded ClassFacts from 16 to 48 bytes to record class root/type identity together with cctor/static state. It allocated 2048 facts, one per sparse execution-registry hash slot, for a maximum of 98304 bytes (96 KiB) of stack. Yet PhysicalMembership caps admitted physically observed classes at 1024, so at least half the entries could never be used by an accepted capture. Official Unity worker-thread stack capacity has not been measured.

Use an exact dense primitive class-fact store, not a shortened fingerprint. New pure C++11 source libil2cpp/vm/AssemblyShadowPackedClassFacts.h implements Scratch<Fact,Slots,Capacity> with at most 1024 trivially-copyable facts and a 2048-element uint16 one-based slot-to-dense-index map. Zero means unregistered. Insert rejects duplicate slots, invalid slots and overflow. Find and Update reject missing or out-of-range slots. Scrub clears all copied values and mappings, and the destructor calls Scrub for early return/rejection paths. No heap allocation or class pointer is retained.

## Implemented native changes

The actual inactive VM implementation now creates PackedFacts under initial metadata Reader and g_MetadataLock. Pass one inserts the copied ClassFacts under the authenticated original registry slot. Pass two retrieves and compares exact previously owned class root/cctor/static bits and updates that slot only after successfully copying its owned row. Pass three retrieves the final fact by original slot and uses the unchanged SameRoot and SameClassState comparisons; source mismatch still revokes rows/record/receipts. Original V1 physical image first-owner, image count/token checks, R02/registry and B1 first-error fences are unchanged. AssemblyShadow.cpp includes the new helper before the inactive source. Enabled V1 5222-byte getter, B1 and runtime resolver paths are unchanged.

## Bounded memory and test evidence

ClassFacts <=48 bytes; dense capacity 1024 gives <=49152 bytes, and the 2048 uint16 map adds 4096 bytes plus size_t/alignment. The checked-in static_assert caps the packed object at 53264 bytes, versus the old 98304 bytes. The class-fact scratch bound therefore saves >=45040 bytes (~44 KiB). The separate 12288-byte original V1 image-facts array and 2048-byte end-pass visited array remain. This is not a complete stack-frame or performance measurement.

[Exact native source-host CI 43346655116](https://github.com/night-outlook/il2cpp_plus/actions/runs/43346655116) at native@39ac1a66b906da12825e095de010cae7cf5a8161: 4/4 Passed, macOS-15 and Ubuntu-24.04 C++11/C++17, Release/Debug strict and ASan-UBSan host profiles. Each process reports 111 cases and 4237 assertions. Five new pure packed-scratch scenarios cover empty/out-of-range, sparse high slot 2047 and duplicate rejection, Update, complete 1024-row capacity/overflow, and Scrub/reuse. The previous 106 source scenarios remain. This executes the checked-in inactive .inl against a SYNTHETIC VM; no real Unity native translation unit, Player, GC, or worker-stack measurement ran.

[Exact demo source CI 43347245365](https://github.com/night-outlook/hybridclr_demo/actions/runs/43347245365) at demo source anchor 7a38e9d28eb580d463f1334df7e169c1978cb4d1: 2/2 Passed (macOS/Ubuntu) for 64-native/eight-demo source files. Checks include original V1 getter byte fidelity, pure packed header/VM include, no standalone allocation/main in runtime files, exact changed native blobs and unchanged full-field/product rejection flags. The final documentation commit may trigger another source-audit run; verify its exact HEAD separately.

## Independent Primary source-review findings

PACK-01 / scoped PASS: exact sparse registry-slot bindings survive packing, including duplicates, end-of-capacity, updates and scrubbing. No hash collision or approximate fingerprint is used. All existing sampled root/ctor checks and typed error revocation are retained.

PACK-02 / OPEN: observations under g_MetadataLock are not a coherent VM/GC/class epoch or allocation provenance. TypeDef handles/name bytes can change between samples; interpreter nested/constructed/generic and VAR/MVAR shapes remain unsupported. No original complete field15 parity from actual Unity metadata has been demonstrated.

PACK-03 / OPEN: the reduced <=53264-byte scratch still contributes to native stack usage alongside other bounded buffers. Official Unity 2022.3 full native translation-unit compilation, GameAssembly, macOS/Windows/Android worker-thread stack profiling, Player/GC/RSS are NotRun. No source mock can qualify that runtime capacity.

PACK-04 / BLOCKED: terminal-safe complete original field14/finalDiagnostics and field15/finalExecutionDiagnostics, one-owner descriptor-relative native V2 artifact/envelope, independent identity-bound external receipt/readback and authenticated first recovery remain unimplemented. Independent R03 full-stage FAIL/High findings remain; historical B1 oneuse-12 focused Player 19/19 PASS is consumed and not B2 acceptance.

Next Primary: complete original execution-registry/class TypeKey source inventory and metadata/GC lifetime/epoch, then terminal-safe immutable field14/15 and authenticated native V2. Do not start H2/M08A/X02/SNAP-01 or self-approve Human Review Gate.

Flags: readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. WEB_TO_LOCAL remains CLOSED / NO EXECUTION.
