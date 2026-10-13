# SNAP-01 follow-up: lossless authenticated bounded diagnostics

Status: proposed versioned representation with executable host reference. **Not installed in the Player and not approved as a runtime repair.** Owner: Primary Implementation. Baseline: demo `64da7e51d740d4816907a63864b9c006a9db4b85`, native `0f72078711d4786dac2666c9017d952d857dd041`, branch `codex/assembly-shadow-r01b-h1`. Historical evidence and original runtime acceptance remain unchanged.

## 1. Confirmed failure, not an inferred length

SNAP-01's actual release baseline PID67344, debug baseline PID67364 and type PID67373 each recorded their first failure at **text slot14 / finalDiagnostics**, reason9, previous writer state1, prefix262145, original limit262144, errno0, integer mask01ffffff and text mask00003fff. Complete ON raw files stayed empty, processes exited2, semantic verifiers were Unavailable. The failure is now a confirmed incompatibility between the general diagnostics producer and its single inline slot. The following execution-diagnostics slot15 has the same representational risk, but was **not** the first failed slot in these runs. Exact full actual lengths/content are Unavailable. The earlier synthetic331078-byte execution JSON must not be substituted.

Authority: immutable `../../local-validation-snap01-82bd/preflight/DIAGNOSTIC_COLLECTION.json`, its three writer classifications, original command/PID/log hashes, and Local-owned `Handoff/LOCAL_VALIDATION.md`/`RETURN_TO_WEB.md`. The release original log Git blob is `4aee9d33f2fbb3a2605bb4ae15fc8dadd7aaf63c`; it independently shows the slot14 record. This design does not rewrite SNAP-01 or N.

## 2. Decision and non-negotiable invariants

Use an explicit **NativeBoundedSnapshotV2** envelope plus one complete **R03BoundedDiagnosticsV2** artifact containing logical slots14 and15. All other original report fields remain semantically unchanged. Do not enlarge the original262144-byte inline text capacity, truncate diagnostics, omit classes/fields, replace content by a hash alone, compress unbounded input or silently accept partial output.

The representation pools the original sixteen physical text slots' existing payload allowance rather than giving either diagnostic a larger inline slot. Physical diagnostic frames are **65536 bytes or less**. The entire envelope-plus-diagnostic-artifact byte allowance is **4194304 bytes**, no greater than the original16×262144 payload allocation (the old buffers additionally had16 terminator bytes). This is a versioned representation change, not an acceptance-predicate change; it must be reviewed before integration.

Losslessness is guaranteed **inside the admitted envelope**. It cannot guarantee arbitrary-size content within a finite budget. A producer that exceeds the total remains a deterministic `ResourceLimitExceeded` failure with no complete semantic result. Actual SNAP-01 full sizes are unknown; this plan does not promise they fit. Resource failures must not result in automatically raised limits or a partial substitute.

The current executable reference resides under `reference/diagnostic_stream.py`. It is a host specification and strict consumer, not a native production writer. Its `encode` intentionally materializes host test data; that implementation must not be copied into the terminal runtime path.

## 3. Concrete budget and wire contract

Fixed budget:

| Resource | Maximum |
| --- | ---: |
| Original inline physical text capacity | 262144 bytes, unchanged |
| Binary diagnostic frame payload | 65536 bytes |
| Envelope, inline controls and descriptor reserve | 262144 bytes |
| Canonical inline portion within that reserve | 258048 bytes;4096 reserved for descriptor/wrapper |
| Diagnostic artifact including headers/checksums/footer | 3932160 bytes |
| Envelope reserve + artifact maximum | 4194304 bytes |
| Diagnostic sections | Exactly two, slot14 then slot15 |
| Declared chunks per section | At most64, also constrained by aggregate bound |
| Additional runtime output files | One diagnostic artifact; no arbitrary path map |

These are stricter pooled limits, not an increase. In particular, an unusually large control/guard receipt in slots0..13 may fail the pooled inline allowance even though the old layout had separate buffers. Such failure must be explicit, not a lost control. The reference checks the inline JSON's encoded size before admitting data. Filesystem block overhead, file descriptors, parser memory, capture buffers and allocation overhead require separately measured implementation budgets; the4194304 figure is **not a claim that the Python object graph or all process memory fits4MiB**.

Wire byte order: network/big-endian. Header is72 bytes: `R03DIA2\0` (8), identity binding digest (32), exact canonical inline-envelope digest (32). Each40-byte section header contains slot(u8), null/text tag(u8), exact total UTF-8 bytes(u32), chunk count(u16), full raw field SHA-256(32). Each38-byte frame header contains index(u32), payload-length-minus-one(u16), context-bound digest(32), then1..65536 payload bytes. All non-last chunks have65536 bytes; last length is exact remainder. Empty text is distinguishable from null and has no chunks. Null must have zero bytes/count and the SHA-256 of empty bytes.

The40-byte final commit footer contains `R03END2\0` and SHA-256 of every preceding artifact byte. No trailing bytes are allowed. The envelope descriptor carries the explicit version, exact artifact size, full artifact SHA-256, identity digest and inline digest. It does not carry a path supplied by diagnostic content. Decoder requires the entire authenticated stream, both sections, every chunk, full field hashes, footer and exact EOF **before returning any field**.

No Unicode normalization, JSON pretty-printing or parse/re-serialize step changes original producer bytes. UTF-8 may cross physical chunk boundaries; decode only after complete authenticated field assembly. Embedded NUL is a byte, not a C-string terminator in this format. Invalid UTF-8 fails. Diagnostic JSON with duplicate keys or nonfinite numbers fails the semantic-input parsing step rather than normalizing into a potentially passing object.

## 4. Authentication and trust roots

Identity binds exact runId, caseId, actual PID, request SHA-256, built binary/build-manifest SHA-256, and all four40-character source commits. Header binding is SHA256(`R03-IDENTITY-V2\0` + canonical identity). Frame digest is SHA256(`R03-FRAME-V2\0` + identity digest + slot/index/length + exact payload). Separate field, inline and whole-artifact digests detect substitution, truncation, misordering and cross-run replay.

**Hashes are not signatures and do not authenticate an untrusted producer by themselves.** The expected descriptor and identity must originate from the source/PID/request/build-bound sealed raw record and independently preserved command/evidence manifest. A self-consistent adversary able to rewrite the raw, descriptor and all hashes is outside this hash-only trust boundary. Preserve current Git source provenance, app/Mach-O joins, executable identity, sealed evidence and external publication receipts. Do not use the artifact's own untrusted header as the expected identity.

The reference decoder accepts an already-open `BinaryIO`. It does not claim to implement secure filesystem path admission. The native integration must walk approved parent directories with no-follow semantics, retain directory/file descriptors, verify original owner/device/inode/mode, create exactly once with exclusive/no-follow flags and keep original output-root gates. A path canonicalization check followed by a fresh path open is not sufficient against ancestor replacement. Host collection must verify the same bound inode and exact byte length; unexpected file/link replacement fails.

## 5. Producer integration: complete bytes without managed terminal formatting

Required Primary implementation, not Local work:

1. Prearm raw-envelope and deterministic sidecar descriptors while healthy. Preallocate the bounded capture/sink state and pin only the existing precise runtime objects. Bind run/case/PID/request/build/source identities before poison. No path allocation or arbitrary filename is taken from diagnostic text after failure.
2. Refactor native general/execution JSON generation around one shared serializer/sink interface. Preserve original property names, ordering, escaping, numeric values and complete assembly/class/member census. Do not produce an independently rewritten approximate schema. The legacy string API and new stream API must use the same serialization operations and compare byte-identically in tests.
3. Capture the complete final diagnostic state under the existing metadata/transaction rules. Do not hold a transaction or GC/metadata lock across filesystem I/O or call managed code. A preallocated native capture with explicit capacity is required; if a stable complete capture cannot be made within budget, fail with a precise receipt. Specify synchronization/lifetime for class/assembly names and counter values. Mixed before/after snapshots are not accepted as one atomic observation.
4. Stream from that frozen capture through bounded buffers into the sidecar, with counted exact bytes and incremental hashes. Do **not** route a large managed string through UTF-8 P/Invoke marshalling and then claim bounded allocation. Do not concatenate chunks into a large terminal heap string. An emitter that hits capacity reports the scanned prefix/count actually known, not an invented full length.
5. Preserve original25 integer slots and14 small logical text slots. Slot8's native caught-guard JSON remains once-only and must contain every original predicate input. Slots14/15 become exactly-once complete sidecar sections, not nullable fallback references after a failure. Null is retained only when it is the original report value and still fails any required semantic predicate.
6. After successful producer completion, finish sidecar hashes/footer and durable fsync/close, then write and durably seal the small envelope referencing exact sidecar bytes. Two files cannot be made atomically committed by pretending one fsync covers both: a complete envelope plus matching durable sidecar and external seal are all mandatory. Any write/flush/fsync/close error leaves retained failed/partial artifacts and a first-error receipt; never delete them to retry or accept partial raw.

Peak native capture, ring/sink buffers, encoder/hash state and metadata reservations must be measured and admitted before runtime use. Replace/repartition existing storage rather than keeping the old4MiB arrays plus another full diagnostic copy. The reference's budget constrains encoded transport, **not proof of implementation memory allocation or GC behavior**.

## 6. Consumer integration and unchanged semantics

Keep the original V1 verifier path intact for old evidence. Add strict transport dispatch for the explicit V2 schema; it validates the raw descriptor and artifact first, then constructs a *tagged semantic view* containing every original logical field. No rewriting a V2 artifact into fake `NativePreopenedSnapshotV1` output. The verification receipt records original envelope/artifact hashes, authenticated descriptor and exact transport version.

Extract/reuse the existing semantic predicate implementation with byte-identity/source-bound tests. Both versions must call the same predicates for42/42, stable0→2/readable2, first causes21/13, reflection/delegate/AOT rejection/no side effects, canary/recovery/fixed diagnostics, healthyGC31, mask15/OFF0 and all required baseline native guard fields. A `Failed` source report remains Failed. A missing section, invalid structure/hash, resource overflow, early seal, empty raw or nonzero required exit remains Failed/Unavailable. Complete transport is necessary, never sufficient for semantic acceptance.

Host memory/JSON recursion must be bounded separately before loading a hostile artifact; the reference caps byte consumption and rejects obvious invalid JSON but does not claim a hard process-RSS bound for Python's parsed object graph. Production collection should use a constrained verifier subprocess with explicit memory/time budget and report admission failures rather than skip fields.

## 7. Verification and integration stages

Stage A, completed here: executable Python wire/decoder/hydration reference and36 controls; native coordinator contract separately tested. The large-data test covers two complete JSON documents each above262144 bytes. Other tests cover UTF-8 spanning frames, embedded NUL, null/empty, aggregate overflow, wrong PID/request/source context, changed chunks/field digest/footer, wrong slot/index/count/size, missing/trailing bytes, duplicate JSON keys and preserved Failed verdicts.

Stage B, Primary pending: native sink/shared producer implementation, actual bounded capture, safe file transaction, native hash implementation against independent vectors, unchanged semantic predicate dispatch and integration into current native/C# bridge. Exercise exact producer output against the native writer and unchanged verifier, not a small stub. Preserve and extend the current source-bound C# P/Invoke tests. Fault injection includes each file operation and resource boundary; verify that all budgets remain unchanged or stricter.

Stage C, Primary pending: review safe native engine ownership described in ENGINE_TERMINAL_DESIGN.md. Diagnostics may be integrated first, but no full repaired-runtime handoff may imply engine quiescence is solved.

Stage D, separately authorized Local only after B/C gates: fresh exact-source managed/55-native compilation, host suites, original custody/SDK/fixture preservation, storage admission and original five-case runtime. Require complete actual diagnostics and exact ON semantics; report exact successful lengths/hashes. Keep original500ms/1..64 uncapped engine acceptance unchanged. No SNAP-01/N retry or new acceptance from this reference package.

Rollback: because only Docs/reference code is presently added, existing Player behavior is unchanged. Future V2 runtime enablement must be isolated by a versioned test-only transport selection; V1 remains available for historical verification. Removing V2 must not mutate old evidence, change original failed verdicts or restore missing historical files.
