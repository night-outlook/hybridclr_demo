# R02 — allocation admission caching and observation policy

Status: Primary Implementation in progress; no R02 Player acceptance claimed.

## Authority and scope

H1 was explicitly closed as `PassedWithExplicitDeferredRisk` after user choices D1=A and D2=A. The next user instruction explicitly starts Primary Implementation. This work implements the existing `Plan/stages/R02-allocation-cache-and-guards.md`; it does not start R03 or approve H2.

Starting four-repository branch: `codex/assembly-shadow-r01b-h1`.

| Repository | Starting pushed HEAD |
| --- | --- |
| night-outlook/hybridclr_demo | a8d2c02c636ee9276d6cf12a54ee3e0626a5c49e |
| night-outlook/hybridclr | 1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad |
| night-outlook/hybridclr_unity | 0ea633a2c5b936b5af69d944593c55bd2783fca9 |
| night-outlook/il2cpp_plus | 6be7f38bec2fa4677d24efc1a4a1294240789933 |

The H1 source anchor and its immutable performance/Local evidence remain historical identities. New native code requires new installed-source verification, builds, and affected Player regressions. It is not a metadata-only H1 successor.

## Allocation certificate

The key is `(active generation, complete physical input Il2CppClass pointer, context, domain)`. An allocation value records the exact selected target class and baseline contributors checked by the existing V1 layout proof. Input and target identities are never interchangeable. Different constructed classes, arrays, generations, and domains do not share certificates merely because their names or generic definitions match.

The immutable table only publishes completed values. Readers acquire a bucket head, traverse immutable nodes, and neither acquire a cache mutex nor allocate. Entries have process lifetime. A cold builder acquires the existing metadata lock, checks the table again, and performs the existing resolver/layout proof without holding the resolver-map mutex across metadata calls. Publication uses release/acquire ordering. No cache reset, image-ID reuse, unload, or new successful transaction is introduced.

Optional baseline counterpart lookup has its own physical-definition/image/generation key. A published null value means the immutable image has no counterpart; it is different from a cache miss. That absence can be cached. Failed or incomplete allocation proofs are never published as permission.

When physical size metadata is not ready, the original bounded admission path may complete without creating a cache entry. This remains an unready admission, not proof of a complete layout. Diagnostics distinguish these attempts. The one-proof/warm-hit assertion is made after the tested physical class reaches layout readiness, not by pretending a structural generic-definition comparison proves an unmaterialized constructed layout.

## Checks that remain outside the cache

Every supported allocation checks the private/physical-metadata execution boundary before lookup. Cached admissions recheck failure state and the baseline initialization contributors recorded by the proof. The existing outer allocation boundary continues to record actual type use on every call. Existing old-object clone/boxing, method-owner, generic-context, baseline-use, and publication guards are not converted into cached permissions. Unaffected framework exception allocation must remain possible when reporting a failure; a process-wide prohibition on all framework allocation would recursively break exception reporting.

The active publication may be in `Committing` while legitimate module initializers execute. R02 must not reject that state merely because it is not yet `Committed`. Failed and FailedAfterCommit admissions are not accepted. Unexpected native allocation failures must preserve the failure boundary rather than publish partial entries.

## Observation policy

`HYBRIDCLR_ASSEMBLY_SHADOW_DIAGNOSTICS_LEVEL` has three build-time values:

- 0: correctness-only; observation counters and class inventory are unavailable, not successful zero-valued evidence.
- 1: bounded counters; no detailed class inventory.
- 2: bounded counters plus detailed class observations; compatibility default for existing H1/M07 diagnostic fixtures.

The macro never removes correctness guards, candidate registration, baseline-use records, generic-context traversal, failure sealing, or publication synchronization. Build provenance must record the effective value. Performance comparisons use matching levels; functional tests that inspect legacy class observations use level 2.

Counters use 128 process-lifetime single-writer thread shards with atomic snapshot reads. Retired-thread counts are retained. Thread slots are not recycled. Overflow is explicitly reported as truncated coverage; level 0 reports disabled coverage. Saturation does not wrap. Ordinary updates do not contend on a shared read/modify/write cache line or allocate. Registration has a bounded one-time shared operation per thread.

Detailed class observation may memoize only already-registered physical class identities. The global inventory remains bounded at 1024 classes, and dropped observations remain visible. An unregistered or overflow class is never memoized as successfully observed.

## Measurement semantics

Definition searches, inspected metadata rows, proof attempts/entries/hits/rejections/unready attempts, baseline checks, field/interface workspace constructions, guard/context checks, observation contention, counter storage, and owned cache-capacity bytes are separate metrics. Workspace construction counts are not a global malloc count. Owned cache bytes exclude allocator overhead and are not process RSS. Counter snapshots are live observations, not a global atomic transaction.

D1 requires controlled R02-versus-H1-candidate measurements of allocation, reflection, and closed generics, with cold and warm phases, cross-type load, and multithreading. Keep the older R01 reference separate; do not move the comparison baseline. D2 requires native owned storage, native allocation profiling where available, managed bytes, point-in-time RSS, and lifetime peak with their distinct meanings. Faster readiness does not cancel slower warm calls. A no-SLA result does not automatically close D1/D2.

## Validation and stopping boundary

Primary supplies native concurrency/failure/allocation-free tests, diagnostic-policy tests, source/integration checks, workload verification and batch support. Local performs real Unity/IL2CPP compilation, fresh source-bound builds, allocation/guard tests, affected M07/startup/failure/count/capacity regressions, and controlled performance/memory measurement. Testable independent cells should continue within one batch; dependent Player cells must stop on invalid source/build provenance or semantic failure.

Keep raw results, launch receipts, build/input identities, logs, before/after hashes, failed attempts, and archive inventories. No report-only package may replace launch/raw evidence. Historical H1 acceptance stays intact and is not promoted to R02 execution evidence.

R02 remains unaccepted until the required fresh Local evidence and independent stage review are complete. Remaining D1/D2 costs must be disposed before H2. No R03 or later milestone starts automatically.
