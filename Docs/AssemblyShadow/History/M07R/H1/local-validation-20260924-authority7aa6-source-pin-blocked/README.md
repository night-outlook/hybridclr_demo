# Analysis-source preflight blocked at pushed HEAD

This Local Validation attempt used `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` on `codex/assembly-shadow-r01b-h1`, starting at pushed HEAD `d7854b16c09b02d4494d28c2b0ea015ba83f58a3`. The declared analysis anchor was `7aa6f61994da354b04464e38ddfc8552cc5c3055`.

`V00/preflight.json` records the actual command, UTC timing, exit code 1, and source-tree rejection. `V00/repository-preflight.json` records all four repository paths, branches, commits, remote heads, worktree registrations, source pins, package manifest, submodule inventories, and tool versions.

`V01A/source-audits.json` contains the complete Git name/status deltas and SHA-256 hashes for changed non-metadata files. The fixed historical 27df→7aa five-file delta and retained-graph 6913→7aa 24-file delta match their code allowlists. The actual 7aa→HEAD delta has nine unexpected non-metadata agent files.

`V02/historical-checkpoint-manifest.log` verifies all 92 entries of the earlier immutable [source-27df execution checkpoint](../local-validation-20260923-authority27df-formal-analysis-blocked/README.md). `V02/historical-live-four-hashes.json` verifies the four fixed live bridge/seal/batch/final-sample hashes at their original paths. These are historical integrity checks, not current-source compatibility or complete live-graph authentication.

No bounded test suite, Unity, Player, pilot, formal pair, historical compatibility preflight, corrected analysis, V05, or M08 was run after source preflight failed. No historical receipt was edited. The source-27df execution checkpoint remains the authority for its 40/40 historical formal series.

`MANIFEST.sha256` authenticates only this new checkpoint. The current conclusion and Primary action are in `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` at the same published commit.
