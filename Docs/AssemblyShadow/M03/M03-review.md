# M03 independent review record

## Final milestone verdict

PASS for M03 on 2026-08-27. Both independent reviewers returned PASS for their
complete assigned milestone boundaries, with no actionable findings. M04 entry
is approved; neither M04-M07 nor the full project is accepted by this verdict.

The reviewed immutable executable-source boundary is:

- HybridCLR: `assembly-shadow-m02-tooling` through `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9`.
- IL2CPP: `assembly-shadow-m02-tooling` through `0486098099e7e80176401267538499e611b181f2`.
- Package: `assembly-shadow-m02-tooling` through `0c9302ffa2f420b30774423d4da8305214a78784`.
- Demo: `assembly-shadow-m02-tooling` through `6369ae8e32b8458c3b7c4180c99e47d15d5a63b3`.

The complete demo evidence/metadata target was
`da22b3692a3ffb2fe0f3b69fce843c6a2e5cc3a0`. Later pin/report/evidence-only commits
do not alter the executable source. This closeout changes only review/status
documentation. The local four-repository milestone tag is
`assembly-shadow-m03-transaction`; the demo tag includes this closeout record.

### Full native/runtime review

Reviewer: `m03_transaction_review_gpt56sol_high_1`, independent and read-only.
Verdict: PASS. The review covered the complete M02-to-M03 runtime/native ranges,
not just the last OFF correction. It verified private staging and retained-byte
lifetime, terminal-state sealing, missing-closure rejection, raw-owner facade
authorization, reserved atomic publication, lock ordering, initializer timing
and FailedAfterCommit, recursive private visibility, minimum Usage Guard,
InternalCall exception/marshaling/OFF behavior, prototype retirement, and no
added fields in upstream ABI structures.

The reviewer independently reran the strict verifier against the original v4
artifacts: all 16 modes passed. It inspected randomized staging, generation-one
initializer/publication observations, exact failure/retry behavior, separate
fallback, private generic and AOT Nullable visibility, ordinary OFF evidence,
and the native ASan receipts. Receipt inspection is not a new ASan/Unity run.

### Full managed/tooling/evidence review

Reviewer: `m02_integrity_review_gpt56sol_high_1`, independent and read-only.
Verdict: PASS for the complete package/demo boundary through the metadata target
above. The reviewer independently reran all 16 strict Player cases and restored-ON
source verification, checked exact UInt64 and all 23 OFF fields, matched all 49
archive files to original bytes, and verified frozen-resource/ordinary-OFF
provenance and all seven restored files. It inspected the 493/493 Editor XML and
the archived 133/133 Python output. The requested standalone Python receipt was
added at the expanded metadata target; executable sources remained unchanged.

### Main-agent integration audit and limits

All four repository trees were clean at the reviewed boundary. Exact changed-path
inventories match Git (runtime 16, native 24, package 14, demo 77). Installed source
verification passes with 935 source/937 installed files, native ON and verified
demo source. The original checkout retains its four known dirty paths, its
pre-existing Editor PID 13313 remains running, and no shadow Editor is running.
Frozen M01 manifest/source-audit, accepted M02 native library, and fixed M00 DLL
hashes match their pre-M03 values. No push or PR is part of this acceptance.

Evidence is pinned Unity 2022.3.62f2 macOS ARM64, with bounded concurrency stress,
not exhaustive race detection. Receipts are local unsigned evidence and depend
on retained external artifact trees. Abort retains private metadata for process
lifetime. Full logical resolution, reflection, execution and Unity coverage
remain M04-M07; full memory-snapshot side-effect freedom, hostile full-IL
validation, and platform/performance matrices are not claimed.

## Bounded native correction review

Reviewer: `m03_transaction_review_gpt56sol_high_1`, independent and read-only.
The first logical-facade repair was rejected because a forwarded type could be
materialized and traced before its defining owner was authorized. The corrected
implementation checks raw defining-image ownership before materialization and
retains the approved provider list for lazy post-commit resolution.

Re-review returned PASS with no actionable findings. It covered the cold raw
name-cache path, lifetime, lock ordering, candidate precedence and native OFF.
The executable adapter regression includes an unsafe control; it is not a
claim that an adapter replaces real transaction-state evidence. The source
commits above retain this reviewed native implementation unchanged.

## Bounded compiler-proof correction review

Reviewer: `m02_integrity_review_gpt56sol_high_1`, independent and read-only.
The installed compiler-library proof, v2 stable-AOT provenance, Python binding
checks and fresh failure-diagnostic capture returned PASS. The reviewer
independently confirmed 346/346 Editor tests at that boundary and explicitly
left the real Player matrix and final milestone verdict pending.

## Bounded diagnostic-preservation review

The v2 Player processes returned zero, but the unchanged strict verifier
rejected diagnostic snapshots after Unity stripped 14 of 48 DTO fields. Native
JSON contained the data; the managed serialization contract did not retain it.
This was not resolved by defaulting missing fields or rewriting old results.

Reviewer: `m02_integrity_review_gpt56sol_high_1`, independent and read-only.
The package field/type preservation and demo linked-schema gate returned PASS
with no actionable defects. The reviewer inspected the actual code, exact
prelink/linked byte bindings, recursive schema traversal and mutation tests, and
independently confirmed 355/355 Editor tests with zero failures/skips at
`_temp/AssemblyShadow/EditorTests-081ae26a0a9f42e39e7aa08ef4c17c54/results.xml`.
Those code changes were committed unchanged as package `f3329281` and demo
`b20145a7`; the v3 scene/configuration binds the new baseline and runtime ABI.

The verdict explicitly requires fresh linked parity, all 16 runtime modes and
the unchanged strict verifier before final M03 acceptance. Ordinary HybridCLR
OFF regression, restored-ON source verification and the paired-source audit
also remain part of the final gate.

## Bounded unsigned-contract and OFF-probe review

Reviewer: `m02_integrity_review_gpt56sol_high_1`, independent and read-only.
All eleven unsigned native fields now use `ulong`; 132 exact-token cases cover
native parsing, managed serialization and reparse across numeric boundaries.
Four Bootstrap counter mirrors also retain the complete unsigned range.

The first review found a P2: JsonUtility defaults could manufacture missing
zero/false OFF fields. The repaired probe overwrites invalid sentinels and rejects
each omitted field. The independent literal-fixture test removes each of all 23
root fields, without deserializing/re-serializing its test input. Re-review
returned PASS with no remaining findings and independently confirmed 493/493
Editor tests, zero failures/skips, in
`_temp/AssemblyShadow/EditorTests-30a3fc849558489f9584272ebda8d3a3/results.xml`.

## Bounded native-OFF adapter review

Reviewer: `m03_transaction_review_gpt56sol_high_1`, independent and read-only.
The native adapter now forwards the complete native schema in both feature
modes. Mode-specific null-output errors, initialized outputs and query-only
exception handling remain intact. The actual adapter/core/serializer ASan test
passed 27 checks; only managed string allocation is substituted. Reviewed
hashes matched `/private/tmp/m03-native-disabled-api-first.json` and its 1,003
unchanged dependencies. The review returned PASS with no actionable findings.
Real managed allocation, internal-call integration and v4 Player proof remain
outside that standalone test and are still required for milestone acceptance.
