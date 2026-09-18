# Local Validation report

## Current run — 2026-09-18 authority `50c79913`

### Exit

**Local Validation → Primary Implementation: BLOCKED at V00**

The clean candidate checkout was fast-forwarded to the exact requested handoff commit `bd6abcd32880066cc7cb71b2fad349b6a56bd4ca` on `codex/assembly-shadow-r01b-h1`. The declared build-input source anchor is `50c79913096961636a776ee8254b6631002cdfe5`, and it is an ancestor of the checkout.

The mandatory candidate preflight failed before Unity, IL2CPP, compilation, or Player execution:

```text
Blocked: Incomplete handoff sections
```

`Tools/AssemblyShadow/h1_handoff_preflight.py` requires these exact committed headings:

| Required heading | Present |
| --- | --- |
| `## Objective` | Yes |
| `## Source targets` | Yes |
| `## Implementation` | **No** |
| `## Local validation` | Yes |
| `## Failure evidence` | Yes |
| `## Alternatives` | Yes, as a longer heading containing this text |
| `## Risks` | **No** |
| `## Local correction boundary` | **No** |
| `## Human review gate` | **No**; committed heading uses different case |

The committed handoff instead uses `## Primary implementation`, `## Local validation — detailed order`, `## Alternatives / forbidden changes`, and `## Human Review Gate`, and has no exact `## Risks` section. The handoff explicitly prohibits Local from rewriting `WEB_TO_LOCAL.md`, so no bounded correction was made.

### Independent V00 checks

| Check | Result | Evidence |
| --- | --- | --- |
| Candidate source preflight | `Blocked` | `_temp/local-validation-20260918-authority50c/v00-candidate-failure.json`, SHA-256 `2bab589ce7cfeb71b6bc30251acf36f2166f19311f9327bc04272d3d8bbd7e1f` |
| Reproduction-tooling preflight | `Passed` | `BehaviorAndToolingSourcesVerifiedNotBuildAccepted` at `ba8fee33753a5ebc215b7a98739e343d8e05572e`; receipt SHA-256 `c3d9f7a9253d1093bd1ff3b8582bd4f5e01ad5ea8676a9d9ab5ca3fa2051fcc5` |
| Protected refs | `Passed` | Live `git ls-remote`: reproduction `352d7474...`, tooling `ba8fee33...`, performance `88508b59...`; receipt SHA-256 `70cc9c527eceb940f275c3d37cad097aa756a956a140c3d064ec0409247f734a` |
| Runtime checkout commits | `Passed` | HybridCLR `1d2df7c...`, package `0ea633a...`, IL2CPP `6be7f38...` |
| Tracked working state | `Passed` | All listed checkouts remained clean. |

A stale local `origin/codex/assembly-shadow-h1-count-repro` tracking ref pointed at `426f00f...`; it was not treated as authority. The live remote check returned the required protected head `352d747...`.

### Not run

V01–V05 and M08 are `NotRun` because the V00 candidate authority gate is a mandatory hard stop. No prior `8b129d...` receipt was relabelled. No Unity, build, runtime, performance, cleanup, or R02 action occurred.

Evidence is authenticated under [local-validation-20260918-authority50c-v00-blocked](../History/M07R/H1/local-validation-20260918-authority50c-v00-blocked/README.md). The actionable correction is recorded in [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
