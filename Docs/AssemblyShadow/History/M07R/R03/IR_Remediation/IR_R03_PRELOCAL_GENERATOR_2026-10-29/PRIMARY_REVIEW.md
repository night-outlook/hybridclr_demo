# Primary source-only review — 2026-10-29

## Starting authority

Feature branch `codex/assembly-shadow-r01b-h1`, starting demo `b3f94fbbe1fa9ad949ea00d0f285e6c4533ad857`; unchanged sibling source pins: `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`.

Latest authoritative Local oneuse-C = FAIL / ReturnRequired at standalone CLI import before Player startup, eight scoped Passes, one Failed, one Blocked; 0/3 current builds, 0/5 real Players, 0/126 installed changed VM pairs. Prior original S historical archive, b7e3/c42a failures and f51d historical-only PASS remain unchanged.

## Findings and corrections

- **False historical byte-equivalence invariant (confirmed in actual new CI):** Fresh generation of all 15 original-mode DLLs on both Linux and macOS produced differing SHA/MVID values relative to immutable original S. The legacy fixture workflow incorrectly asserted bitwise equality. Corrected to enforce independent historical inventory blob integrity, 15 exact paths, assembly identities, references and sizes; record all divergences without reclassifying original S or adopting regenerated DLLs. Authentic original-S bytes remain supplied only by `ir_original_fixtures.stage_immutable_original_s` and the retained fc55 checkpoint.
- **Pre-Local host evidence gap:** The original real net8 generator workflow ran only on generator Program/Corpus edits, not active current-native dispatch/handoff changes; its test asserted self-reported hash/MVID rather than independent fixed expected values and repeat generation. New source verifier, actual repeat/duplicate-root controls and CI trigger address this.
- **Mac CI disk risk:** The original full repo/package checkouts unnecessarily materialize large history. Sparse checkouts are limited to project and pinned compiler inputs; actual `csproj` input paths are not changed.
- **Admission document/code mismatch:** Code advised 30 GiB while active WEB_TO_LOCAL prefers 40 GiB. Changed advisory only; no min-floor weakening.

## Review exclusions and deferred proof

Unit test positives with synthetic bytes do not prove that the real .NET generator compiles or produces the pinned binary. The updated CI must prove this on both OSs, and Local oneuse-D must separately prove official Unity2022.3 native/Player execution. The original archive's independent semantic provenance, IR-R03-01/02 and full acceptance remain open; this is a Primary source-level audit, not an independent full-stage review.

Retain separate Passed, Failed, Blocked, NotRun and Unavailable observations. No claim that the 10-stage current coordinator is complete, or that the simulator tests prove post-poison execution.
