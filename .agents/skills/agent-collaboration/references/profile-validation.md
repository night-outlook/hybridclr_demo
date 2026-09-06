# Profile validation and reasoning trial

Run from the repository root with Python 3.11+; no third-party modules are required:

```sh
python3 -B .agents/skills/agent-collaboration/scripts/check_agent_profiles.py
python3 -B -m unittest discover -s .agents/skills/agent-collaboration/tests -p 'test_*.py'
pwsh -NoProfile -File .agents/skills/agent-collaboration/tests/Test-GateReviewRouting.ps1
```

The PowerShell matrix checks eligibility, gate setting precedence, the legacy option alias, and Sol/Astra reviewer selection without Pester. Python routing integration tests require `pwsh` and report a skip when unavailable.

The checker validates TOML, unique names matching filenames, explicit model/effort,
read-only roles, Sol/Astra pair parity (all fields except name, description, model), retired unsuffixed roles, route coverage, and fixed/fallback model, effort, and access agreement.
It does not prove prompt behavior or enforce sandbox permissions beyond the host.

To check model support, supply `--host-models /absolute/path/current-host-models.json`.
The JSON object maps exact model IDs to arrays of supported reasoning efforts.
Populate it from the current host's authoritative tool metadata; do not infer it from
these profiles. Keep snapshots outside the repository to avoid maintaining a stale
model catalog. Without a snapshot the checker explicitly reports availability as
NOT CHECKED. A supplied snapshot is caller-provided evidence, not a live network query.

## Reasoning trial

`code-general` uses Luna/high provisionally. Compare high against max with identical
read-only profile instructions, task inputs, model, and context-fork settings. Use
built-in default agents with explicit model/effort to vary effort without overriding
fixed custom profiles. Do not permit writes or further delegation in either trial.

Use representative planning questions with a known acceptance rubric, including
configuration migration, call-chain analysis, and cross-module ownership boundaries.
Keep each pair on the same source snapshot. Record dispatch-to-completion elapsed
time only when host timestamps are available; otherwise mark timing unavailable.
Record rework, missed requirements, unsupported claims, and scope violations.

Accept high provisionally only when it produces a usable bounded plan; any material
regression should trigger another paired case or restoration of max in both profile
and routing table. One case cannot establish speed, cost, or general quality gains.
Do not escalate every task automatically. Retain evidence from actual subsequent
work before making a broader performance claim.

### Initial paired trial: 2026-09-06

Both agents used `gpt-5.6-luna`, `fork_turns=none`, the revised general profile,
and the same request: plan configurable gate eligibility while preserving the
current Astra default. Inputs were the gate script, gate tests, repository config,
and general profile. No implementation of that hypothetical migration was requested
or performed. Run identities: `planning_trial_gpt56luna_high_1` and
`planning_trial_gpt56luna_max_1`.

| Criterion | High | Max |
|---|---|---|
| Preserve current default and Fight precedence | Covered | Covered |
| Alternatives, migration, implementation boundaries | Covered | Covered |
| Invalid config, model identity, alias validation | Covered; error wording partly ambiguous | Covered; missing-list wording partly ambiguous |
| Evidence boundary | Cited SKILL.md outside supplied evidence list | Cited SKILL.md outside supplied evidence list |
| Rework | Clarify empty-list/error semantics before implementation | Clarify missing-list/conflict semantics before implementation |
| Comparable elapsed time / token cost | Unavailable | Unavailable |

Both plans were usable with clarification. Neither plan was implemented or tested,
so there is no measured implementation rework or missed-defect rate. The shared
citation issue prompted an explicit evidence-scope sentence in the profile; this
small follow-up has not had another paired behavioral trial. Keep high provisional;
this single sample establishes neither a speed improvement nor quality superiority.
