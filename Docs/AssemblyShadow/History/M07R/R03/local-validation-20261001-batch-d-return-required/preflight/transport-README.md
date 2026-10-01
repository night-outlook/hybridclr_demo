# HybridCLR Assembly Shadow

This is the canonical documentation root.

- `Plan/`: design, roadmap, stages and normative review gates.
- `Handoff/`: live Primary Implementation / Local Validation coordination.
- `Architecture/`: durable decisions.
- `History/`: immutable evidence, implementation and review records.
- `Evidence/`: protected fixture and artifact catalogs.

**R02 remains accepted as PassedWithExplicitDeferredRisk. R03 is in progress; R03Accepted=false and H2Passed=false. PureInterpreter structural expansion is disabled.**

Latest Local return: **C, ReturnRequired — 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. C verified the fixture references and supervised compiler lifecycle, but all four native-role build invocations and EditMode compilation stopped at R03Build.cs's int-to-uint count assignments. Native builds, Editor assertions and nineteen Players did not run. Its reports/checkpoint and all earlier evidence remain preserved.

Primary now matches both count fields to Unity's int getters and adds complete build-helper compilation against the actual pinned Unity compiler/APIs and real package dependencies. The original complete C source is retained as a precise two-CS0266 negative control. **A fresh batch D is requested**, not a retry or acceptance of C.

Read:
1. `Plan/CURRENT_STATUS.md`.
2. `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for preserved C facts.
3. `History/M07R/R03/E_BUILD_API_REPAIR.md`, `E_HOST_EVIDENCE.json`, and `E_VALIDATION_MATRIX.md`.
4. `Handoff/WEB_TO_LOCAL.md` for the only current execution command.
5. `History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md` and `Plan/stages/R03-evolution-semantics.md` for unchanged product scope and full-stage exits.

New tested demo source anchor: **`5931ada3c70958a7c6132219e059a42ee3cecbd0`**. The API workflow extracts the exact official Unity 2022.3.62f2 ARM64 package without installing or launching the Editor. Actual helper/package compilation and its old-source negative control passed; the Linux/macOS host regression suites also passed. E_HOST_EVIDENCE.json binds exact CI sources, results, command/output hashes and authenticated artifacts. This is compile-only evidence, not native/Editor pipeline acceptance.

All four repositories use `codex/assembly-shadow-r01b-h1`. Unchanged external pins:
- HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`
- package `120bb01be680cec0375002a0823552d66d34b84c`
- IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`

Execute only the final pushed docs-only transport SHA identified in Primary's prompt and by the latest commit touching WEB_TO_LOCAL.md; local/remote HEAD must match. Earlier handoffs/anchors are historical. Preserve all 36 cells, four native build roles and nineteen fresh-process Player cases; the fixture cell now includes the complete-helper compile prerequisite.

Use only the new unused D root in WEB_TO_LOCAL.md. Never retry A/B/C or modify preserved evidence. R02 deferred CPU and original H1 RSS risks stay visible through H2. Full R03 regression, measurements, PureInterpreter qualification and independent stage review remain Primary-owned. No focused batch grants R03, H2 or release approval.
