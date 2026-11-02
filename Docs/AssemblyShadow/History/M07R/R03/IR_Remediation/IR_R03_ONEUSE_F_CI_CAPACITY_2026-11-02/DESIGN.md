# R03 oneuse-F CI prerequisite block → oneuse-G

## Observed evidence and root cause

F is **BLOCKED / PrerequisiteBlocked**, not a new runtime failure: exact demo execution source `9db3927a9cc899fbe73948e0ff9c586f96efde6d` had both-OS combined host CI `41433978929` PASS, but eight other required exact-commit workflow runs were unavailable. F invoked no Local Mac admission, coordinator, Unity or Player, and its reserved root stayed absent. This did not change the consumed E FAIL, its three passed Unity builds, OFF Player PASS, three ON snapshot failures, or the 51,211 native report count.

GitHub Actions `on.push.paths` was the cause: four of nine workflows already watched canonical `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`; the other five did not. A final documentation-only handoff therefore did not run every required workflow at its governing commit.

## Source-bounded repair

Extend the five missing workflow path filters with the **exact canonical WEB_TO_LOCAL.md** while retaining existing source filters, branch, SDK/matrix, and checks. The final G handoff commit must update that document, causing **all nine workflow runs at the same final head SHA**. Add a Python source-only regression `current_native_handoff_ci_contracts.py` validating all nine actual files and refusing missing, misplaced, duplicate, wrong-branch and non-push triggers. The combined host workflow must run that regression from a sparse checkout that actually includes the workflows. It is still essential to inspect actual GitHub job results: a source-only trigger-contract PASS does not mean a workflow has run.

No product C++/C#, native runtime, 45-file manifest or 135-pair acceptance logic is modified. No ancestor success is silently accepted as exact-commit CI. Source-equivalence exceptions are intentionally **not** used.

## Capacity decision

F's preliminary sample: **42,437,967,872 bytes / 39.5234375 GiB**, below the 40-GiB advisory but above the unchanged 20-GiB hard floor. E's completed 3-build/5-Player cycle observed free space changing from 46,004,543,488 to 42,819,563,520 bytes (~2.966 GiB reduction). This provides a bounded planning observation, **not** a G capacity guarantee. Primary grants a one-time documented GO for G **only when** fresh read-only admission and an independent immediately pre-coordinator disk sample both measure **≥39.0 GiB on the actual G output parent** with all other gates green. Below 39.0 GiB: NO-GO/return to Primary, even when above20. Keep the fixed 20-GiB minimum and 40-GiB advisory unchanged, with no cleanup/relocation/SDK changes.

## Acceptance limits

Use a distinct unused oneuse-G root. F's blocked checkpoint and reserved uncreated root remain unchanged. Original S, all A–F outcomes and E runtime artifacts remain immutable. Only a new actual G batch may observe real diagnostics sidecars, owner-quit containment, five Players and installed 135 native VM source bytes. R03Accepted=false; no H2/M08A/X02/Human Review Gate advancement.
