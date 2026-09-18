# Local Validation Tasks — Fresh V00 After Handoff Contract Repair

Candidate build-input source anchor:

`39c33e259d1ba893e23e3f1aa22529c87524534f`

The previous Local attempt at `f8a2766d...` is **Blocked / V00** evidence only. Do not reuse or relabel it as V00 PASS.

## V00 — mandatory fresh restart

1. Pull the final pushed `codex/assembly-shadow-r01b-h1` handoff HEAD.
2. Record checkout HEAD separately from source anchor `39c33e259d1ba893e23e3f1aa22529c87524534f`.
3. Confirm clean tracked state.
4. Run:
   `python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project <candidate-root> --role candidate --output <new-v00-candidate-output>`
5. Require:
   - `status=SourceTargetVerifiedNotBuildAccepted`;
   - `codeCommit=39c33e259d1ba893e23e3f1aa22529c87524534f`;
   - committed handoff/source-target hashes from this fresh run.
6. Run exact reproduction-tooling preflight at `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
7. Verify protected reproduction/runtime/package/IL2CPP/performance refs remain exact.

Hard-stop on any authority/source/provenance mismatch.

## V01 onward

After fresh V00 PASS, follow `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` for the complete one-batch sequence.

The intended order remains:

- V01 source tests + real Unity compilation;
- V02 fresh candidate provenance;
- V03 fresh candidate/reproduction build set;
- V04 controlled M07;
- V04 normal M07;
- startup11;
- M07 14-mode Player matrix;
- repaired three-mode failure/publication matrix;
- capacity 8192/8193 and mixed boundary;
- lazy/dense/generic/array/reflection/FieldRVA;
- old-Player rejection;
- retained M03–M07 coverage;
- controlled Development performance;
- authenticated retention checkpoint;
- V05 successor evidence and genuine independent whole-chain M08 only when mandatory prerequisites are complete.

After authority/provenance/shared-input foundations pass, preserve isolated functional failures and continue independent safe cells where the same authenticated inputs remain valid. Do not promote failed prerequisites to acceptance.

## Required V00 regression expectation

The live Primary regression now executes the preflight against the actual committed handoff. If Local still receives `Incomplete handoff sections`, preserve the exact checkout HEAD, handoff hash, source-target hash, and preflight output and return immediately.

Do not edit `WEB_TO_LOCAL.md` locally.

## Gate

H1 remains `InProgress`.

Historical M08 remains `FAIL`; no M08 rerun occurred in the blocked attempt.

`humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
