# R03 K — remaining-completion implementation and batch-I preparation

Primary Implementation record, 2026-10-03. Status: **implementation prepared and host/compiler checked; awaiting one fresh Local batch I. Not R03 acceptance or H2 approval.**

## Implemented scope

### RC1 — qualification input

The managed package adds `R03PureInterpreterEligibilityV1` and exact byte/metadata binding support. The analysis joins installation-baseline/target DLLs, loaded reference graphs, resource types, changed roots, closure/load order and concrete type/domain exclusions. It is deliberately non-authorizing: runtime proof, qualification approval and structural expansion remain false.

`ADR-0002-pure-interpreter-qualification-boundary.md` records the durable boundary. The shipping/default profile remains `NativeLayoutAdmissionV1`; private-reference expansion is still disabled.

### RC2 — original-resource fixture

The demo completion runner provisions a new project from exact tracked source bytes. It preserves original M01 prefab/data/scene and meta/GUID blobs, selected baseline/H1/R01B dependencies, source pins and project settings. The existing production M07 build/resource/P05 entry points remain authoritative. Fresh receipts are selected by explicit output identity; old apps are never promoted to fresh evidence.

The full Editor scope is 755 exact package tests and includes the M01 resource test previously excluded from H. H's NoCoverage remains historical.

### RC3 — available broader runtime witnesses

Fresh R00 processes run a supplement using the existing M06 static/delegate/exception rules against the actually selected physical DLL/PDB after original measurement collection. This does not claim the full generic/interface/delegate/old-handle matrix; missing support/coverage must stay explicit in the later R03 exit matrix.

### RC4 — production graph/generation integration

The adapter invokes existing P01–P05 compilation/generation/manifest paths and compares their changed roots, conservative closure and target load order against the static eligibility analysis. A return-to-installation-baseline source target must produce zero changed roots/closure. No multi-commit-in-one-process or M09 recovery claim is made.

### RC5 — observation protocol

Batch I schedules four original R00 modes × three fresh processes and retains original timing/memory observations under `K_MEASUREMENT_PROTOCOL.md`. It deliberately makes no new threshold/SLA claim and does not hide the previously deferred R02 CPU or H1 RSS risks.

## Verification performed before Local

- local completion orchestration/security/fixture tests: **49/49 Passed**;
- Python compile/static policy scan: Passed;
- qualification real-DLL host contracts: 32 cases in the final prepared source;
- retained original verifier/graph/admission host suites remain part of matching CI;
- complete original-resource build helper and dependencies are compiled against pinned Unity 2022.3.62f2 APIs in matching CI;
- no Unity Editor or Player execution is claimed by these Primary host/compiler checks.

Exact final CI run IDs, artifact IDs and digests are recorded in `K_HOST_EVIDENCE.json` after completion.

## Local batch design

`Tools/AssemblyShadow/R03Completion/run_completion.py` predetermines 90 cells. Resource preparation is intentionally independent of static qualification so a qualification defect cannot unnecessarily block original-resource/runtime evidence. P05 restoration is scheduled independently from P05 compile success whenever mutation authority was recorded.

The batch runs six fresh builds, both 754- and 755-case Editor rosters, and 59 fresh Player processes. Evidence is sealed by the existing R03 evidence mechanism. Success means `EvidenceReadyForPrimaryReview`, not stage/gate approval.

## Remaining after batch I

Primary must reconcile the empirical result into the R03 exit matrix. Any uncovered generic/interface/delegate/stack/old-handle item, production-profile risk or unsupported scope remains explicit. Then conduct the independent R03 design→plan→implementation→evidence review and close findings. Only after documented R03 exit conditions are satisfied may the project stop as Ready for user-initiated H2. Do not enter M08A automatically.
