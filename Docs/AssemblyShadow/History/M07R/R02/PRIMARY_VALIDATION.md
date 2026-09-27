# R02 Primary Validation — successor to batch D

Result: **Passed for the bounded Primary host/source scope. Awaiting real Local Validation.**

## Exact authority and publication

- Input Local return: `39dd8213f0a93a2ebde4bdbe982ead4214e9b2eb`.
- Executable/tool source anchor: `57a9470bf299af60f88112998c8326c4c013204a`.
- CI-tested candidate authority commit: `96ec97221439ab1ca8964acaf5bf2b5b16e2dcda`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@a379f0b809a5d8af967df06fc83271d90fd84f4c`.
- Candidate HybridCLR/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP remains `6be7f38bec2fa4677d24efc1a4a1294240789933`; the other two runtime/package pins match the candidate.

Control includes the source anchor as explicit Git ancestry and differs from its tree only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate transport changes after the source anchor are documentation and the source-pin file only. No source-policy allowlist was broadened. The final handoff prompt must use the latest pushed documentation transport HEAD, not the earlier source or CI commit.

## Review of the returned problems

Read `D_COMPLETION_REPAIR.md` for design, official platform references and test mapping.

| Finding | Primary disposition | Remaining verification |
| --- | --- | --- |
| Process identity based on ps display fields | Replaced with kernel birth/PID/group/UID identity; known exiting instances may be waited for without trusting changing displayed argv | Actual user Unity Roslyn lifetime and long M07 commands |
| Rejecting post-signal census omitted | All observations retained before assertions, including phase and exact expected/observed mismatch; native census errors preserve owned raw rows | Any remaining real rejection must retain its complete snapshot |
| Transaction native probe scheduled without generated inputs | Four independent scripts retained; new generated-input prerequisite depends on candidate build and gates transaction probe | Current Unity-generated header and native compile/link execution |
| Transaction probe's historical DLL default | Explicit current controlled graph fixture, installed root, source pins and supplied Unity baselib; pre/post bindings checked | Fresh actual candidate graph with no historical output substitution |

This is a focused Primary implementation self-review, not a new independent R02 stage review. The old D receipts lack the rejecting census; the exact historical process transition remains unproven. The repair closes concrete portability/diagnostic and ordering defects without relabeling D as successful.

The M00 preparation from the earlier cycle is unchanged and still requires actual Unity verification. The frozen ordinary DLL hash was not modified. R02 production runtime code, formal timing code and correctness guards are unchanged in this cycle.

## Actual validation performed

R02 workflow run **36323257884**, at `96ec97221439ab1ca8964acaf5bf2b5b16e2dcda`, completed successfully in both jobs:

| Check | Actual result and boundary |
| --- | --- |
| R02 Python in current environment | 165/165 Passed, zero failures/skips |
| R02 Python in Linux CI | 165/165 Passed, zero failures/skips |
| macOS 14.8.9 arm64 focused tests | 32/32 Passed: real kernel birth/zombie checks, real owned-process retirement and unrelated-session isolation, policy and native-prerequisite tests. This is a repeated subset of the 165 tests, not 32 additional unique cases. |
| Native production-header matrix | 70/70 process cases, 1,540 checks; synthetic physical classes, not IL2CPP VM integration |
| Native revision matrix | 70/70 process cases, 28,294 checks |
| Managed host Baseline/P01/P03 | 102 / 111 / 111 assertions, strict clean process groups; not Unity execution |
| Codec storage attribution | Two compiler runs Passed; four requests totaling 29,884,384 bytes plus 120-byte object on the CI ABI. Not RSS or new R02 bytes. |
| Published source authentication | All 3,119 inventoried source/input files match size, SHA-256 and Git blob; all seven changed executable blobs match the tested artifact |
| Artifact bindings | ZIP digest/CRC checks passed; 48 unique nested exported bindings authenticated with no missing member |

Scoped legacy-H1 workflow **36323257953**, at the same candidate authority commit, also completed successfully: 384/384 current reusable/rejection cases, 6/6 fixed-H1 positive cases, plus the remaining R01 early/failure, M07 PowerShell recovery and R01B lazy workflow steps. The fixed-H1 positives executed at `2cbf68658a5b73189930fcdfe250835b72639515`; no historical Player execution is promoted to R02 acceptance.

## Retained CI evidence

All artifacts below were downloaded through the Connector and digest-verified. `D_PRIMARY_VALIDATION.json` records individual member hashes and exact results.

| Artifact | ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Primary source/native/managed/Python | 10933361330 | 10,629,330 | `7cea9daadfefb74ba38c65855d089a09189b2e8de937c3e91f9fa493dd98f8c5` |
| Darwin focused tests | 10933026186 | 1,113 | `ebd482561604e90ad5176365ca2a77e35f5dad72340c582243b000479f5cb6fe` |
| Scoped legacy tests | 10932818367 | 12,979,985 | `bcb8434f14bcd78ea7e7f53032081fe40985c4114651ef97cbc83150d388fd6f` |

The earlier source-only run 36322916359 also passed. The authority runs above are the selected final Primary evidence. Initial historical CI and Local attempts keep their original classifications. The previous build-repair Primary records at source `82d64ce4...` and runs 36318653155/36318659885 remain in Git history; they do not validate this new source.

## Remaining Local work and stopping point

Primary did not access the user's Mac workspace, run Unity, build Players or rerun D. Actual Roslyn retirement, M00 fixed-byte generation, generated-native prerequisite/transaction execution, controlled functional/performance results, affected regressions and complete Local seals remain required.

Run the 33-cell successor batch once in a new unused root; preserve A/B/C/D and H1 evidence. Local returns actual classifications, first failures and complete snapshots. A genuinely independent R02 stage review is required only after the full evidence is eligible. D1/D2 remain development-stage deferred risks requiring measured disposition before H2. R02Accepted=false; mayEnterR03=false.
