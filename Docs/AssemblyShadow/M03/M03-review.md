# M03 independent review record

## Final milestone verdict

Pending. No final M03 PASS or permission to enter M04 is recorded yet. The
reviewed source corrections below do not replace real Player acceptance.

The immutable executable-source boundary for the next review is:

- HybridCLR: `assembly-shadow-m02-tooling` through `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9`.
- IL2CPP: `assembly-shadow-m02-tooling` through `0486098099e7e80176401267538499e611b181f2`.
- Package: `assembly-shadow-m02-tooling` through `0c9302ffa2f420b30774423d4da8305214a78784`.
- Demo: `assembly-shadow-m02-tooling` through `6369ae8e32b8458c3b7c4180c99e47d15d5a63b3`.

Later pin/report/evidence-only commits do not alter that executable source.

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
