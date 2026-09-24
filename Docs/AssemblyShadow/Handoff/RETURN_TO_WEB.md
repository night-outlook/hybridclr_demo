# Local Validation → Primary Implementation

## Blocker: pushed checkout no longer matches its analysis source pin

### Symptom and exact reproduction

At the pushed demo HEAD `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` on `codex/assembly-shadow-r01b-h1`, the current `WEB_TO_LOCAL.md` and `ProjectSettings/AssemblyShadowSourcePins.json` declare analysis source/tool anchor `7aa6f61994da354b04464e38ddfc8552cc5c3055`.

From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, run:

```text
python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo --role candidate --output /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/LocalValidation-20260923-authority7aa6-reanalysis-a/V00/handoff-preflight.json
```

It exits 1 before writing the requested output:

```text
Blocked: Demo HEAD contains build-input changes after the source pin
```

`git diff --name-status 7aa6f61994da354b04464e38ddfc8552cc5c3055 d7854b16c09b02d4494d28c2b0ea015ba83f58a3` identifies nine non-metadata changes, all in the later `d7854b1` agent migration:

```text
.agents/skills/agent-collaboration/SKILL.md
.agents/skills/agent-collaboration/scripts/Get-GateReviewMode.ps1
.agents/skills/agent-collaboration/tests/Test-AgentCollaborationGatePolicy.Tests.ps1
.codex/agents/code-debugger.toml
.codex/agents/code-explorer.toml
.codex/agents/code-gate-reviewer.toml
.codex/agents/code-general.toml
.codex/agents/code-reviewer.toml
.codex/agents/code-worker.toml
```

### Root cause and affected scope

`shadow_tools.verify_demo` requires the complete non-metadata Git tree at HEAD to match the pinned source tree. The project metadata-only policy does not classify `.agents/` or `.codex/` as metadata. Primary's agent migration was pushed after the final source-target commit without a corresponding source-authority handoff revision. This invalidates the current candidate checkout before bounded tests or historical compatibility may run. The exact five-path 27df→7aa analysis delta and exact 24-path 6913→7aa retained-graph delta still pass as anchor comparisons, but neither authorizes the later HEAD.

### Evidence

Authenticated return checkpoint: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-source-pin-blocked/`.

- `V00/preflight.json`: exact command, UTC timing, exit 1, and failure text.
- `V00/repository-preflight.json`: four clean handoff-branch worktrees, source/native/package pins, remotes, and tool versions.
- `V01A/source-audits.json`: complete name/status deltas and hashes of non-metadata files.
- `V02/historical-checkpoint-manifest.log`: 92/92 historical checkpoint manifest entries pass.
- `V02/historical-live-four-hashes.json`: the original live bridge, seal, formal batch, and final sample match all four fixed SHA-256s.

No Player, Unity, pilot, formal pair, historical compatibility preflight, or corrected analysis ran in this cycle. The source-27df 40/40 formal series remains immutable historical evidence; it has not been relabelled or reanalyzed.

### Required Primary action and remaining uncertainty

Publish a coherent source-authority successor that explicitly accounts for the agent migration and preserves the verifier's fail-closed behavior and the fixed historical-analysis compatibility boundary. Evaluate whether these nine files should be treated as repository metadata under the existing source policy or whether a new source anchor and reviewed compatibility contract is required. Do not silently broaden the five-file 27df→7aa historical compatibility allowlist or alter the completed formal evidence. Include fail-closed coverage for the chosen classification and update `WEB_TO_LOCAL.md`, source targets, and the detailed Local task plan together.

After the corrected handoff is pushed, Local must rerun V00, current Python/bounded regression, exact source audits, live historical compatibility, corrected analysis, checkpoint authentication, V05, and a genuinely independent M08 review. Historical M08 remains `FAIL`; H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
