# Plan Changelog

## 2026-10-15 — P1 owned frozen execution capture component (inactive; no new Local task)

- Primary added a bounded 1024-row / 2MiB owned text frozen execution snapshot under native il2cpp_plus@096ad96168e025a43a8581b3f15b704a66731f29. It is a source-lifetime isolation step only; actual GetDiagnosticsJson / GetExecutionDiagnosticsJson are unchanged and still allocate during VM acquisition.
- [Native CI38698299448](https://github.com/night-outlook/il2cpp_plus/actions/runs/38698299448) Passed strict/sanitized host tests on macOS Apple Clang, Linux Clang and GCC; real V2 memory codec matches unchanged reference wire bytes and failed semantic status remains Failed. Audited original ZIP manifests: 150 verified V2 files, zero mismatches.
- Published independent source/lifetime, lock-boundary, memory-budget audit and Primary reconciliation under History/M07R/R03/IR_Remediation/P1_FROZEN_CAPTURE_2026-10-15. The old Local host PASS and even older FAIL/SNAP-01 failed evidence remain immutable. No official Unity SDK compilation, Player or real engine-owner interface is claimed.
- WEB_TO_LOCAL stays explicitly PAUSED, P1 remains Incomplete, E0 blocked, all R03/H2/readiness/qualification gates false; no next milestone.

## 2026-10-08/09 — Primary IR-R03-02 source candidate and separate focused evidence (gate still FAIL)

- GitHub Connector write verified on disposable demo/native branches, no smoke merge; authoring on feature branch preserved S/R/Q/P/O/N evidence.
- Native `il2cpp_plus@9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`: explicit process-wide terminal business-entry predicate before and after valid MethodInfo guard, narrowly allowed fixed corlib exception constructors, preserved first diagnostic, ABI-bound pure policy tests. Header/source CI [37872834945](https://github.com/night-outlook/il2cpp_plus/actions/runs/37872834945) passed Linux and macOS; **not** full IL2CPP compile/Player acceptance.
- Added parallel `Tools/AssemblyShadow/R03IR` Player source, actual old-baseline and type-resolution stimuli, strict four-Player/three-build runner, synthetic negative verifier tests and package API compile workflows. Historical C04 and 90-cell S tests remain unchanged; debug/release ON and OFF source controls are pending fresh Mac Player execution.
- Recorded that genuine captured-generic and initializer-failure post-poison cases, and active shadow method's own side-effect counter, remain outside the initial four-Player evidence envelope. A source-only positive/rejection contract is not a standalone Human Review Gate.
- IR-R03-01 retains exact original-nine-part byte-authentication and an explicit withdrawal of the false five-part attribution; original-to-capture complete semantic and source-omission joins remain not independently closed.
- Independent original review **FAIL**, separate re-review **NotRun**; R03/H2/qualification/readiness/expansion flags remain false. No new Local assignment before final pinned source/build/CI/impact checks.

## 2026-10-08 — Owner D1=A / D2=A: bounded R03 and observational measurements

- Recorded owner decisions in a new affirmative disposition; preserved the original alternatives, S, and prior evidence.
- Limited supported R03 structural-layout scope to existing NativeLayoutAdmissionV1; explicitly deferred unproved private-reference add/remove and other V1-external expansion to independently gated X02, without enabling it.
- Limited S performance/memory claims to unfenced development observations; retained deferred R02 CPU/H1 RSS risks and Failed contaminated warm certificates.
- Amended R03 stage, remaining-completion, DESIGN, roadmap, ADR-0002, status, review scope, and read-only handoff. No runtime source or Local acceptance result changed.
- Separate independent full-stage review remains NotRun; R03/H2/readiness/qualification/expansion remain false, and no later milestone is authorized.

## 2026-09-17 — Canonical package

- Consolidated the original design/plan, M07 source-review amendments, and durable H1 contracts.
- Established `Docs/AssemblyShadow/Plan/` as the sole active plan package.
- Preserved historical plan/evidence identities through commit `7cb710fa38464b1977a69619fea2b5fc93f79966` and evidence catalogs.
- Kept H1 closed and R02 prohibited pending fresh validation and human approval.
