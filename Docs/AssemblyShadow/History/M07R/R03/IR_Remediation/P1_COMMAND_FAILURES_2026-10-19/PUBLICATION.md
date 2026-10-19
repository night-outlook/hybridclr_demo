# P1 command-failure Primary publication reconciliation

## GitHub Connector publication and scope

The prior `PUBLICATION_BLOCKER.json` and `REMOTE_READBACK.json` are historically accurate snapshots of an earlier **read-only Connector session**. That operational blocker was resolved in this publication session. The historical files are preserved verbatim, **not** reused as current authorization, HEAD pins or negative evidence against this publication.

The current GitHub Connector read and write path was verified with disposable branch `codex/connector-write-smoke-20261019-b61f4a` in both affected repositories. Each created one harmless commit and remote branch HEAD was read back exactly. Smoke commits:

- `night-outlook/hybridclr_demo`: `94e8d955edc2febc1c36d203aeb4996601a3b9dc`.
- `night-outlook/il2cpp_plus`: `6f65745083ea8cddcb6835492789232d5e362053`.

These disposable branches remain because branch deletion is unavailable through the exposed Connector. They are **not** feature source or handoff state.

Published and remotely verified source commits on `codex/assembly-shadow-r01b-h1`:

- Native `night-outlook/il2cpp_plus@e29a38f66331ccabe5822a9f83401cd4a2b20c5a`: three files, one native Python source runner replacement, one focused test and one CI workflow. Exact candidate blob read-back matched the original package. Parent `d8a1df3007e93aeb65dd9fe97ab96b4771de8f17` carried unrelated/new inactive owned-execution record, preserved without rewrite.
- Demo `night-outlook/hybridclr_demo@d67846e9a28add70046198da9a4fba7e27f0764b`: 20 files, including six source/test/workflow changes and 14 retained historical primary documents/evidence files. The commit preserves the original blocked-session snapshots as immutable provenance.
- Unchanged `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.

**Final authorization** is in `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, published in a separate Docs-only commit after these source commits. That final commit SHA cannot literally self-reference inside its own bytes; it is supplied as a **40-character pushed remote SHA** in the accompanying Primary handoff prompt and must match the remote branch HEAD and `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. Any later changed HEAD invalidates this authorization pending a refreshed handoff.

## Source/testing reconciliation

The unpublished candidate bundle was cryptographically checked: 26 candidate files matched declared Git blob, SHA256, byte length; seven existing source/document Git blobs matched exact remote originals, and all new paths were absent. After publication, remote commits were independently read back and original project branches preserved by a non-force, expected-parent fast-forward. The selected source changes are identical to the candidate tested via its standalone source mirror.

Host re-execution in the publication session: **53/53 unique Python tests PASS** (`PassedWithinHostScope`), zero failures/errors/skips. Includes actual controlled Python timeout children and mock compiler/Git/SDK/VM orchestration; 3 additional admission refusals and 13 static checks were previously recorded in the candidate. The [demo focused CI 39208716350](https://github.com/night-outlook/hybridclr_demo/actions/runs/39208716350) and [native focused CI 39208403729](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403729) both completed successfully on the published source SHAs. The retained native live-general source CI [39208403683](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403683) and demo managed/aggregate CI [39208716262](https://github.com/night-outlook/hybridclr_demo/actions/runs/39208716262) also completed successfully.

**Separate known failing CI:** the additional native owned-execution/R02 feature from predecessor `d8a1df3...` has [run 39208403669](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403669) **failed** on macOS Clang in its typed R02 owned-execution step; Linux Clang and GCC jobs passed. This failure is **not** silently converted to PASS or delegated for Local fixes. That distinct feature remains a Primary-owned follow-up outside the new 13-component tooling validation. No fresh installed Unity SDK, full native C++/ASan/UBSan qualification, Editor/Player, runtime or Human Review Gate is claimed by this evidence.

The next **one-time 13-component source/SDK batch** includes the original 12 and one command-failure harness, 75 unchanged native SDK syntax commands, five managed products and expected-negative compiler control. No changed C++ production runtime/getter/guard/serializer or compiler helper is part of this publication. The additional predecessor native owned-execution feature remains outside this focused source/SDK qualification.

## Immutable acceptance and ownership boundaries

The latest `20261018-5667` Local 12/12 PASS is consumed, and the original SNAP-01/N/M/K/I/E FAIL, R02 source fingerprint FAIL, strict S custody Blocked, full R03 independent FAIL/re-review NotRun and original numerical guard/transport thresholds remain unchanged. P1 product coherence/pointer/lifetime/GC/RSS still incomplete, P2 real V2 native/C# NotIntegrated, E0/E1 owner-safe lifecycle Blocked, full P3 Player acceptance Incomplete. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled.

The Local Agent must not implement repairs, edit unrelated repository source or execute more than the one documented source/SDK-only cycle. On any substantive finding preserve receipts and return to Primary.
