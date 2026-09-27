# R02 Primary Validation

Primary source anchor: `06ba01e010c7eac3543dd6f23e083c2716941190`.
Candidate authority commit: `149a7f33d7bf4c431c2ed7ef3e5f393b47b71817`.
Matched H1-runtime control: `e6fdd32a6fd661a88ef108f7b055e4f7840e9e43`.

## Fresh CI

Workflow: `R02 Primary native and tooling validation`.
Run: `36289846827`.
Head: `149a7f33d7bf4c431c2ed7ef3e5f393b47b71817`.
Result: **Passed**.

Artifact: `10921843892`; 10,428,779 bytes; SHA-256 `23c40013304d56ee545941aee0a174f19f89ae4fe29020c5fc64c4b8720e5f2e`.

The artifact source inventory binds:
- hybridclr_demo `149a7f33d7bf4c431c2ed7ef3e5f393b47b71817`;
- hybridclr `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
- hybridclr_unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
- il2cpp_plus `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`;
- 3,082 inventoried source/input files.

## Results

- source verification: Passed;
- native production-header matrix: 70/70 cases Passed, 1,540 checks;
- native revision matrix: 70/70 cases Passed, 28,294 checks;
- Python R02 tests: 115/115 Passed;
- managed host Baseline: 102 assertions Passed;
- managed host P01: 111 assertions Passed;
- managed host P03: 111 assertions Passed;
- strict owned process groups: clean for all passing managed rows;
- codec storage attribution: GCC and Clang Passed, four constructor allocation requests totaling 29,884,384 bytes plus a 120-byte codec object on the CI host ABI.

The codec number excludes allocator overhead and is not Unity RSS. The component is unchanged between H1-runtime control and R02 candidate.

## Scope limit

This CI did not run Unity Player or establish runtime acceptance. Its top-level receipt has `unityPlayerRun=false` and `runtimeAcceptance=false`. Actual candidate/control Unity/IL2CPP builds, functional sidecars, the 44-pair/88-process performance series, affected regression suites, D1/D2 disposition, evidence seal, and independent R02 stage review are Local Validation responsibilities under the committed handoff.
