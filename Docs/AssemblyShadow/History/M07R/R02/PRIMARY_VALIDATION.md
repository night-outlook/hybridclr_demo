# R02 Primary Validation — repaired build boundary

Status: **Passed for Primary host/source scope; Unity/Player runtime acceptance remains Local Validation.**

## Authority

- Local return input: `621216751ade64aa39f28ed44a5acdc15c38c6cc`.
- Repaired executable/tool source anchor: `82d64ce415c062729f0082e81c1808eaac9602e4`.
- Candidate runtime pins:
  - hybridclr `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
  - hybridclr_unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
  - il2cpp_plus `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@6c950eaa98f995084750fe1ea8f80cfe4c59c61b`, using H1 il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Candidate/control comparison from source anchor to control head differs only in `ProjectSettings/AssemblyShadowSourcePins.json`; the control head has the repaired source anchor as an explicit merge parent.
- Candidate post-anchor transport delta is limited to `Docs/AssemblyShadow/**` and `ProjectSettings/AssemblyShadowSourcePins.json`, which are metadata-only under the existing source authority policy.

## Repaired boundaries

The Local A/B/C evidence exposed two build-boundary defects. Primary implemented both:

1. **Owned Unity/Roslyn completion.** Long Unity/PowerShell build commands run under `unity_session.py`, which retains the real command exit, identifies only the exact command-owned Unity `VBCSCompiler.dll`, reauthenticates PID/group/start identity before signaling, performs bounded TERM/KILL retirement, and still requires the unchanged outer no-survivor check. Unknown descendants or changed identities fail closed.
2. **Workspace-local M00 ordinary input.** Candidate and control independently compile and authenticate the frozen M00 ordinary DLL in their own workspaces before M07. The frozen SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27` is unchanged; no candidate-to-control copy, hash rewrite, M00 Configure, or fallback is allowed.

The legacy H1 workflow was also corrected after R02 source evolution. The original 387 H1 tests are partitioned without omission: 381 reusable current contracts plus three explicit R02 rejection tests run against current source, while six fixed-H1 positive tests run against an authenticated disposable checkout at H1 checkpoint `2cbf68658a5b73189930fcdfe250835b72639515`. The fixed fixture checkout uses deterministic `git checkout -B`; it does not alter H1 verifiers or historical evidence.

## Final R02 Primary CI

Workflow: `R02 Primary native and tooling validation`.

- Run: `36318653155`.
- Head: `fd59bad0a470b8f70a409fae8ccead9e4046518f`.
- Result: **Passed**.
- Artifact: `10931711251`.
- Artifact bytes: `10,553,690`.
- Artifact SHA-256: `b94c9346e03f5c7e6122a51207b85b4852313e8823462928ea82f021b0061f67`.
- Source inventory: 3,103 exact source/input files.
- Bound repository heads in artifact:
  - hybridclr_demo `fd59bad0a470b8f70a409fae8ccead9e4046518f`;
  - hybridclr `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
  - hybridclr_unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
  - il2cpp_plus `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.

Results:

- source verification: Passed;
- native production-header matrix: **70/70** process cases, **1,540** checks;
- native revision matrix: **70/70** process cases, **28,294** checks;
- Python R02 suite: **145/145 Passed**;
- managed host Baseline: **102** assertions Passed;
- managed host P01: **111** assertions Passed;
- managed host P03: **111** assertions Passed;
- managed process groups: clean for all passing rows;
- codec storage attribution: GCC and Clang both measured four allocation requests totaling **29,884,384 bytes**, plus a 120-byte codec object on the CI host ABI.

The codec number is constructor allocation-request attribution for the unchanged profile-2 storage. It excludes allocator overhead and is not Unity RSS, Player memory, or proof of the complete H1 D2 delta.

## Final legacy-H1 CI

Workflow: `H1 Bee primary fixture and tools`.

- Run: `36318659885`.
- Head: `727b8c39c5f6329d3c94e9a0cf339b8d214e2134`.
- Result: **Passed**.
- Artifact: `10931995719`.
- Artifact bytes: `12,971,530`.
- Artifact SHA-256: `a92ed53afeb9becfb25a08f971cfbe505bb66ff6310365aeb79b72e66ff1cc8e`.

Scoped results:

- current reusable contracts + explicit R02 rejection tests: **384/384 Passed**;
- fixed-H1 positive fixture tests: **6/6 Passed**;
- remaining R01 early/failure, M07 PowerShell recovery, and R01B lazy workflow steps: Passed.

The earlier failed legacy runs remain historical evidence. Their failure was not relabeled.

## Scope limit and next validation

No Primary CI above launched a Unity Player or established R02 runtime acceptance. The R02 receipt keeps `unityPlayerRun=false` and `runtimeAcceptance=false`.

Local Validation must now execute a new unused `R02LocalBatch-v1` root from the final handoff. It must independently generate candidate/control M00 inputs, produce fresh controlled graphs, run functional sidecars, the 44-pair/88-process formal comparison, affected Editor/native/M07/startup/failure/count/lazy/dense/capacity regressions, D1/D2 measurement/disposition, complete sealing, and independent R02 stage review if eligible.

R02 remains unaccepted; `mayEnterR03=false`.
