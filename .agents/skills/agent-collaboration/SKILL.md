---
name: agent-collaboration
description: Use when a repository task is non-trivial, may involve subagents or parallel work, or needs coordinated ownership across agents.
---

# Agent Collaboration

Apply this versioned team contract subject to higher-priority user, host, and live tool-schema instructions. Keep host-version mechanics out of this skill.

## Safety And Scope

- Preserve existing local changes. Do not revert, overwrite, delete, clean, or broadly format other users' or agents' work unless explicitly authorized.
- Limit mutations to the user's requested scope. Narrow read-only inspection of relevant source, assets, logs, generated outputs, caches, and version-control metadata is allowed when needed for analysis or diagnosis.
- Read each target file's current state immediately before editing. If ownership is unclear and safe merging is not possible, stop and report the ambiguity.

## Delegation Decision

- Delegate only a concrete, bounded subtask that can proceed independently while the main agent continues useful non-overlapping work, and that materially improves speed, isolation, or confidence. Otherwise execute directly.
- Prefer subagents for parallel read-heavy exploration, tests, triage, summarization, independent validation, and disjoint implementation slices.
- Keep serial, tightly coupled, shared-state, or overlapping-write work with the main agent. Do not delegate solely because work is multi-file, involves a build, edits a tool or skill, or prepares a Git change.
- The main agent owns requirements, decomposition, integration, conflict review, final verification, and the user-facing result.
- Only the main agent delegates. A subagent completes its assigned task and returns evidence; it does not spawn or orchestrate other agents.
- If delegation is unavailable or forbidden, continue directly with narrow scope; mention the constraint only when it materially affects confidence or delivery.

## Identity And Routing

- Use the host `task_name` as the canonical identity. Keep the semantic prefix stable and format the full name as `<domain>_<responsibility>_<model>_<effort>_<index>` using only lowercase letters, digits, and underscores, for example `git_audit_gpt56terra_low_1`.
- Normalize the effective model slug by removing punctuation (`gpt-5.6-terra` -> `gpt56terra`) and use the exact reasoning tag (`none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, or `ultra`). If exact inherited values are not observable, use `inherit` rather than inventing metadata.
- The name's model and effort tags must match the effective spawn configuration or fixed custom-agent profile. Host-generated nicknames are presentation-only and never replace the canonical task name.
- Choose the project-scoped custom agent from the routing table. Use built-in `default`, `explorer`, or `worker` only when the matching custom profile is unavailable.
- Custom profiles pin their own model and reasoning; do not duplicate those settings as spawn overrides.
- For a built-in fallback, always pass the table's explicit fallback `model` and `reasoning_effort`; omitted inheritance is noncompliant.
- Use the smallest sufficient context and follow the live host's context-fork, lifecycle, waiting, and concurrency rules.

| Work | Preferred custom agent | Fixed routing / access | Built-in fallback |
|---|---|---|---|
| Search, cataloging, log triage, simple code inspection, symbol lookup, implementation explanation, dependency tracing | `code-explorer` | `gpt-5.6-luna` / `medium` / read-only | `explorer`, `gpt-5.6-luna` / `medium` |
| Routine implementation | `code-worker` | `gpt-5.6-luna` / `high` / inherited permissions | `worker`, `gpt-5.6-luna` / `high` |
| Bounded general analysis, planning, coordination support, or scoped architecture investigation | `code-general` | `gpt-5.6-luna` / `max` / inherited permissions | `default`, `gpt-5.6-luna` / `max` |
| Cross-system or high-risk debugging | `code-debugger` | `gpt-5.6-sol` / `high` / inherited permissions | `default`, `gpt-5.6-sol` / `high` |
| Explicit high-stakes security, regression, release, or final correctness gate | `code-reviewer` | `gpt-5.6-sol` / `high` / read-only | `default`, `gpt-5.6-sol` / `high` |
| Configured independent milestone and final acceptance gate for a large, long-running, or complex task | `code-gate-reviewer` | `gpt-5.6-sol` / `max` / read-only | `default`, `gpt-5.6-sol` / `max` |

The live host schema is authoritative. For an ordinary route, execute directly when neither the custom profile nor its built-in fallback is exposed instead of silently selecting a mismatched agent. A mandatory `code-gate-reviewer` gate is different: if no independent custom or built-in agent can be spawned, the verdict is `BLOCKED`; the main agent cannot replace the independent reviewer or claim `PASS`.

Route by purpose and risk, not by verbs in the request. A request to "review," "look at," or explain code remains `code-explorer` when it only needs read-only inspection. Use `code-reviewer` when a bounded independent high-stakes verdict is itself the deliverable. Use `code-gate-reviewer` only for the configured milestone and final workflow gates below. When uncertain outside that workflow, start with `code-explorer`; escalate only if evidence reveals material correctness, security, data-loss, concurrency, or release risk.

## Gate Review Configuration

At task classification, read the current main agent's exact effective model once from authoritative live host metadata and reuse it unless the host reports a model switch. If the host exposes only a family name, use that; never infer the value from task names, repository config, environment variables, or agent profiles, and never pass `inherit` or a guess. Run `scripts/Get-GateReviewMode.ps1` at classification and before each gate with that cached value as `-EffectiveMainAgentModel`; `-MainAgentModel` remains a compatibility alias. Matching is case-insensitive, full identifiers are allowed, and the value must resolve to exactly one `Luna`, `Terra`, or `Sol` family.

The helper normally returns exactly `Off`, `Final`, `FinalAndMilestones`, or `RequiredFinalAndMilestones`; generic invocation failure or any other returned value means `Off`. `InvalidMainAgentModel` instead means re-read the authoritative host value and retry once. If that retry repeats the error, stop and report unresolved model identity; never guess or reinterpret it as `Off`.

When Boolean `require_sol_main_agent_for_gate_review` is `true`, `Luna` or `Terra` returns `Off` before every gate setting, while `Sol` continues. Pass `-FightHeroSkillDevelopment` only when authorized implementation using `fight-dev-ability`, `fight-dev-breakthrough-passive`, or `fight-dev-new-hero` changes Fight hero combat behavior or its production inputs/outputs. Boolean `require_fight_hero_skill_development_full_gate_review` is only for Fight hero skill development, never other tasks, and has higher priority than both `enable_gate_reviewer` and `review_committed_major_milestones`; when enabled, return `RequiredFinalAndMilestones`. Otherwise, only Boolean `enable_gate_reviewer = true` enables an ordinary gate, and Boolean `review_committed_major_milestones = true` adds milestone gates.

For `Final` or `FinalAndMilestones`, classify a task as gate-qualified when the user calls it large, long-running, or complex, or when it has multiple implementation or commit phases, crosses multiple modules or systems, is expected to span sessions or context windows, or carries material integration or correctness risk. Record that classification before implementation. For a stepwise-commit task, declare the major milestones and their acceptance criteria before their commits; ordinary work, cleanup, and corrective commits are not separate milestones.

## Delegation Contract

Before spawning, verify that the canonical name matches the selected role, effective model, and reasoning. The task message states: objective; already-known facts and relevant files, paths, or symbols; role and access mode; exact read scope or write ownership; supplied inputs; forbidden areas; relevant validation command when known; expected output or acceptance evidence; and known uncertainty. Pass known facts forward instead of making the child rediscover them.

For code-changing workers, explicitly state: **You are not alone in the codebase. Do not revert others' edits; inspect current files and adapt your implementation to concurrent changes.** Require a verification command only when a command is the appropriate evidence.

Ask subagents to return concise conclusions, changed files or file/line evidence, verification results, residual risks, uncertainty, and the smallest next step when incomplete—not raw transcripts. Do not duplicate delegated work merely to confirm it; spot-check the evidence needed for integration.

## Parallel Work And Search

- Never assign multiple agents to the same file, generated-output area, or tightly coupled business logic. Main-agent integration follows all parallel writes.
- Start with the smallest task-relevant source of truth. Exclude broad cache/build/version-control searches by default, but inspect a targeted excluded area when it is the relevant evidence.
- For Unity asset, serialization, reference, Timeline, Animator, or missing-meta questions, inspect the targeted asset files directly. Use `unity-asset-safety` for deep inspection or mutation.

## Independent Gate Review

- For any gate-qualified task whose mode is not `Off`, invoke `code-gate-reviewer` after implementation and required validation, and after the final intended commit when the task includes commits. This independent FINAL gate is the mandatory Final review. Do not report completion or mark the task complete until it returns `PASS`.
- For `FinalAndMilestones` in an ordinary stepwise-commit gate-qualified task, also invoke `code-gate-reviewer` after every declared major milestone is validated and committed. Pause later task steps until that milestone gate returns `PASS`.
- `RequiredFinalAndMilestones` requires at least one meaningful Fight implementation milestone to be declared before production changes. Review every declared milestone after validation; when the task includes commits, review after its intended milestone commit, otherwise review the exact local diff. Pause later task steps until each milestone gate returns `PASS`; the final gate remains mandatory.
- A final milestone review may also satisfy the final gate only when the invocation explicitly covers both the milestone and the full-task acceptance criteria, the reviewed repository state is identical, and nothing changes afterward.
- Every gate task supplies: gate kind; requirements and acceptance criteria; declared milestone or full-task scope; immutable Git base and target commits for committed work or the exact local diff scope otherwise; relevant files and integration boundaries; validation commands/results; prior findings for a re-review; and a strict no-mutation instruction. The reviewer must inspect actual evidence rather than summaries alone.
- The reviewer returns `PASS`, `FAIL`, or `BLOCKED` and never implements fixes. `PASS` accepts that boundary. `FAIL` means an actionable defect or unmet criterion exists. `BLOCKED` means required evidence, access, scope, or validation is unavailable.
- On `FAIL`, the main agent automatically owns and fixes every in-scope finding, directly or through a non-reviewer worker, runs focused regression validation, and requests another independent gate review. Do not ask merely for permission to fix work already authorized by the task.
- On `BLOCKED`, the main agent automatically gathers missing evidence or resolves the blocker when that is safe and within scope, then requests another independent gate review. If resolution requires new authority, a material scope expansion, user choice, or external-state change, remain blocked and ask for that input.
- When any gate reviews committed state, remediation for a `FAIL` or resolvable `BLOCKED` that changes versioned content must be validated and committed before re-review whenever the surrounding workflow already authorizes commits; re-review the expanded immutable Git commit range. This applies to milestone and final gates. An already commit-authorized task includes narrowly scoped corrective commits required to close its gate findings. The gate settings do not grant commit authority to a task that otherwise lacks it or authorize unrelated changes.
- Repeat remediation and independent re-review until `PASS`; never advance a failed milestone or finalize a failed task. Do not launch an identical re-review without materially changed code, evidence, validation, or access.
- Independently confirm delegated scope, conflicts, risks, and verification before finalizing, even when the configured gate is off.
- Assess whether a recurring, material issue warrants a reusable harness improvement. Propose one only when its expected benefit exceeds its maintenance cost, and ask before implementing it.
