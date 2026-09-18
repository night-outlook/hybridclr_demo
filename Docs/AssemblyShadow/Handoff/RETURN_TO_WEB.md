# Local Validation → Primary Implementation

## Blocker: committed handoff fails its own required-section contract

### Symptom

At clean candidate checkout `bd6abcd32880066cc7cb71b2fad349b6a56bd4ca`, the mandatory command:

```text
python3 Tools/AssemblyShadow/h1_handoff_preflight.py \
  --project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --role candidate \
  --output /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/local-validation-20260918-authority50c/v00-candidate
```

exits 1 with:

```text
Blocked: Incomplete handoff sections
```

### Root cause

`h1_handoff_preflight.py` requires exact substring matches for:

```text
## Implementation
## Risks
## Local correction boundary
## Human review gate
```

The committed `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` uses `## Primary implementation`, has no exact `## Risks` or `## Local correction boundary` heading, and uses `## Human Review Gate` with different case. This mismatch was not caught by the bounded Primary tests because the unit fixture covers a synthetically complete handoff rather than executing the preflight against the committed live handoff document.

### Evidence

- Candidate failure receipt: `_temp/local-validation-20260918-authority50c/v00-candidate-failure.json`, SHA-256 `2bab589ce7cfeb71b6bc30251acf36f2166f19311f9327bc04272d3d8bbd7e1f`.
- Committed `WEB_TO_LOCAL.md` SHA-256: `878bec2c1b08277c7e12919d4d32df3e0de680213d68786fa6c534c8345ae98c`.
- `source-targets.json` SHA-256: `c99776dbb09d35db619603af67841ffc6aeabe4b1d322b830a648c3dc45a07eb`.
- Source-pins SHA-256: `5fcf6226b9050232850c03d09d36ffa9a2f69bce9f3113c5087e19e9eec42167`.
- Reproduction-tooling preflight and live protected-ref checks passed independently and are retained in the same evidence root.

### Recommended implementation direction

Make the committed handoff and verifier contract agree without weakening source authority. The smallest repair is to restore the exact required headings in `WEB_TO_LOCAL.md` while preserving the current content. Add a Primary regression that runs `h1_handoff_preflight.py` against the actual committed candidate handoff/source-target files, not only synthetic fixtures.

Do not loosen or bypass the preflight, broaden metadata-only rules, move the source anchor, or ask Local to rewrite the authoritative Primary handoff.

### Validation still required

After the repaired handoff is committed and pushed, Local must restart at fresh V00 under source anchor `50c79913096961636a776ee8254b6631002cdfe5`. None of V01–V05, M08, or R02 ran in this attempt.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
