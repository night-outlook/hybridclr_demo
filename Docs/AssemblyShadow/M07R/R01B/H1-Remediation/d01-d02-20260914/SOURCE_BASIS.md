# Source basis, inference and evidence limits

## Project sources read

- Demo branch `codex/assembly-shadow-r01b-h1`, commit `4ef5f674522f03c11dbcf22128071c745778b0e5`: `local-validation-20260914/NEXT_AGENT_PROMPT.md`, `REMAINING_WORK.md`, the prior transfer/context, M02 verifier and current witness helper/probe.
- Package branch `codex/assembly-shadow-r01b-h1`, commit `c7ed6d244a2c3a8e948f062d5431c289e1369650`: transformer, ILPP, configuration/checking interfaces and existing CodeGen test conventions.
- Transformer base blob `a89968130730c5d7386852916edb1564172329c2` and ILPP base blob `783dec8a752d54f3f2bbf1c57cb62fafe2365161` were reconstructed and their complete Git blob hashes verified locally. Reversing only the intended edits reproduces those exact bases.
- Demo modified-base blobs are recorded in `demo-edits.json`. Existing files are changed only after exact blob and unique-anchor checks; original method fingerprints are not automatically regenerated or admitted.

## D01 inference, not a local root-cause verdict

The current transformer loads PE/PDB without a supplied compiler-reference context. dnlib's Portable-PDB constant reader may obtain a ClassSig when an external enum cannot be resolved; its writer rejects a non-null primitive value under that class signature. This is a strong candidate explanation for the local error, not proof that this is the offending constant in the unavailable failed Bootstrap artifact.

Primary upstream context:

- https://github.com/0xd4d/dnlib/issues/550
- https://github.com/0xd4d/dnlib/issues/550#issuecomment-2026687699
- https://github.com/0xd4d/dnlib/blob/9ab9b58ab31b99b3f6cdef36efec613fc11ddbe2/src/DotNet/Pdb/Portable/LocalConstantSigBlobReader.cs
- https://github.com/0xd4d/dnlib/blob/9ab9b58ab31b99b3f6cdef36efec613fc11ddbe2/src/DotNet/Pdb/Portable/LocalConstantSigBlobWriter.cs
- https://github.com/dotnet/runtime/blob/main/docs/design/specs/PortablePdb-Metadata.md

The upstream issue reports this error with external-enum local constants and discusses the need to resolve the enum's actual assembly/references. Its reporter also describes an initial resolver that did not solve the issue. Therefore merely creating a resolver is not proof of correction: the prepared resolver supplies only the actual compiler references; real failure replay, explicit normalization checks and independent symbol auditing remain mandatory. No dnlib binary upgrade is included.

## This environment

GitHub reads worked. Direct `git ls-remote` failed DNS resolution. A GitHub blob write was separately blocked by the tool safety check; it was not retried through a different write interface. No target branch, source pin or historical evidence was modified.

The earlier interrupted attempt's claimed D01/D02 source files and 49-test log were not present in the retained workspace. This delivery does not reuse those claims. Its own final raw logs identify 50 fresh portable tests. Full repository M02 integration, Unity/C# compilation, Player builds, raw local failure replay, runtime acceptance, archive authentication and independent M08 are not claimed as executed.
