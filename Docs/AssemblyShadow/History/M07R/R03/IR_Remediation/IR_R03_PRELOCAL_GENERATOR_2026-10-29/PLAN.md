# R03 pre-Local generator proof — execution plan

1. **Inventory/source review:** Verify exact four remote pins, current oneuse-D handoff, original S oneuse-C result, fixture generator and existing real CI. Record that source/host checks cannot substitute for real Unity.
2. **Implement verifier:** Add a pure pinned `Methods.dll` verifier and 16 synthetic adversarial receipt tests; do not edit C#/native code, historical source manifests, fixtures, original S archive or coordinator.
3. **Strengthen actual compiler CI:** Sparse-checkout only explicit generator/package inputs; setup .NET SDK 8.0.318; use no-server flags; build `PlayerFixtures.csproj`; run original 15-file structural/path/assembly/references/size comparison (not impossible byte-equivalence), retain all SHA/MVID differences, and two separate IR generation outputs; check duplicate output rejection and pinned hash/MVID; preserve immutable S blob cross-check and raw artifacts.
4. **Fix preflight advisory:** Align code to 40 GiB advisory without changing hard 20 GiB; add 35 and 40 GiB tests.
5. **Validate:** Inspect the latest host workflow on the 29-admission-test code revision. Then require both upgraded actual generator CI OSs to pass at the final pushed demo commit, recording job conclusions, test counts, toolchain and raw output provenance. Correct any findings in Primary, then re-run CI via push; no historical/local replay.
6. **Document and publish:** Update canonical README and `WEB_TO_LOCAL.md`, commit and push through GitHub Connector, independently verify latest four repository remote HEADs and provide short source-pinned Local prompt.
7. **Local Validation (pending):** Agent performs fresh read-only no-write/CLI/capacity admission; if qualified, runs oneuse-D coordinator ONCE at a new verified-absent root. Collect all ten stage receipts and raw artifacts. Preserve prior failed roots, return factual Passed/Failed/Blocked/NotRun; stop for Primary on nontrivial findings.

**Stop condition:** No new milestone or Human Review Gate approval. Oneuse-D remains conditionally authorized only with green source-pinned prerequisites.
