# Apple Bee provenance Primary checkpoint — 2026-09-15

This directory records the Primary Implementation correction returned after Local Validation commit `33543dd39efec42a9480ea976ae3a3684dcd5ffd`.

Candidate executable/tooling code anchor: `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` on `codex/assembly-shadow-r01b-h1`. Following commits update only source pins, agent handoff files and documentation.

The correction replaces one global Apple native assertion/debug predicate with reviewed source-owned domains while preserving complete provenance. The authenticated graph classifies 430 IL2CPP/runtime/PCH actions, two exact BDWGC sources and fourteen exact zlib sources. All actions remain linked/accounted, use one compiler/SDK, require requested Shadow/count defines and are independently checked under the domain contract. The runtime domain still owns requested C++ Debug/Release evidence. Unknown external membership fails closed.

Fresh capture and explicit diagnostic replay now retain their tool-owned attempt inputs/status before planning, so plan-stage failures do not disappear and cannot be mistaken for failed compiler probes or accepted receipts.

Primary bounded regression: GitHub read-only workflow run `34967358028`, exact anchor above, authenticated Bee graph `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`, **250/250 tests passed**. This is not Unity/Apple Player or M08 acceptance.

Read:
1. `Documents/AgentHandoff/WEB_TO_LOCAL.md` — authoritative Local Validation handoff.
2. `STATIC_REVIEW.md` — bounded Primary review.
3. `LOCAL_VALIDATION_TASKS.md` — V01–V05 checklist.

H1 remains InProgress; independent whole-chain M08 has not passed; humanGatePassed=false; mayEnterR02=false.
