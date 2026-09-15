# Local Validation report

## Exit

**Local Validation → Primary Implementation**

Preflight is `Blocked`. No Unity, IL2CPP, native, Player, runtime, performance, or acceptance validation was started because the required authoritative handoff file is absent.

## Actual checkout inspected

- Repository: `git@github.com:night-outlook/hybridclr_demo.git`
- Working copy: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`
- Local branch: `codex/assembly-shadow-r01b-h1`
- Local commit: `6f1e766c8169cb0fdb24277bbbef6f25b4d74c0f`
- Fetched remote commit: `refs/remotes/origin/codex/assembly-shadow-r01b-h1` at `6f1e766c8169cb0fdb24277bbbef6f25b4d74c0f`
- Existing excluded state: untracked historical `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/v7` through `v11`; preserved and not staged

The original checkout `/Users/ah/GitHub/hybridclr/hybridclr_demo` is on dirty `main` at `73d95b4064ee23143e0722f6eae127fe61df6c9d`; it was rejected as a validation base and left untouched.

## Environment observed

- macOS `26.5.2` (`25F84`)
- Git `2.50.1 (Apple Git-155)`
- Python `3.14.6`
- Unity and platform-tool versions: `Blocked` before tool invocation because the handoff target was not established

## Preflight operations

| Operation | Result | Evidence |
| --- | --- | --- |
| Inspect initial checkout branch, commit, remote, and status | `Pass` | Dirty unrelated `main` checkout identified and excluded |
| Fetch every published `hybridclr_demo` branch into remote-tracking refs | `Pass` | Seven remote refs recorded in `preflight.json` |
| Locate `Documents/AgentHandoff/WEB_TO_LOCAL.md` in local HybridCLR worktrees | `Fail` | No file found |
| Inspect the same path in every fetched remote ref | `Fail` | `handoffRefs` is empty in `preflight.json` |
| Confirm handoff repo/branch/commit/goal/validation list/selection criteria/risks | `Blocked` | Authoritative input file unavailable |

## Validation status

| Scope | Result | Reason |
| --- | --- | --- |
| Unity compile and EditMode/PlayMode tests | `Blocked` | Target commit and required test list not established |
| IL2CPP conversion and native compile | `Blocked` | Target commit and candidate criteria not established |
| Player build and runtime tests | `Blocked` | Target commit and required modes not established |
| Platform, profiler, performance, and memory checks | `Blocked` | Required configurations and thresholds not established |
| Integration and Human Review Gate assessment | `Blocked` | No authoritative handoff and no fresh validation chain |

No bounded local fix was made. No previous diagnostic, build, or M08 evidence was promoted. Human Review Gate is not ready, and R02 was not started.

The actionable return is in [RETURN_TO_WEB.md](RETURN_TO_WEB.md). Re-run preflight only after the primary implementation Agent commits and pushes `WEB_TO_LOCAL.md` to the designated target branch.
