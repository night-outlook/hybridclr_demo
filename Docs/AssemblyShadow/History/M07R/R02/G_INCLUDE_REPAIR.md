# R02 batch-G host contract include repair

## Source authority and observed failure

Input Local return: `4c4f50adfd3a44073d14b107227f399c53ea605c`. Read its immutable `local-validation-20260928-batch-g-return-required/` checkpoint and Local-owned handoff reports. G remains ReturnRequired: 9 Passed, 1 Failed, 24 Blocked, with a complete independently audited seal. No Unity builds or producer/parser semantic assertions ran after the host compile failure. This repair does not relabel G or replace its archive.

The retained `compile-0` stderr follows macOS libc++ headers into `libil2cpp/vm/string.h`, then fails to locate `il2cpp-config.h`. The contract runner passed `-I <native>/libil2cpp/vm`, which made that project directory eligible for standard angle-bracket lookup. The missing config file was a consequence of selecting the wrong string header, not a reason to broaden the native include tree.

HybridCLR remains `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`; package remains `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` in both roles. Candidate/control IL2CPP remain `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`. Only demo host tooling, tests, CI and coordination change. No native writer, parser, schema, fixture expectation, timeout, runtime guard, Player code or formal timing code changes.

## G-01: quoted project include isolation

`type_resolution_contract.writer_command` constructs all three diagnostics-level compiler commands using `-iquote <native>/libil2cpp/vm`. Quoted project headers and their quoted siblings remain available; standard angle-bracket includes no longer select that directory. The directory is not changed to `-isystem`, and no broad additional `-I` root or copied native header is introduced. Invalid diagnostics levels fail rather than being coerced.

Official compiler background, separate from project evidence: GCC documents that `-iquote` applies only to quoted includes, whereas `-I` participates in both quoted and angle-bracket lookup (https://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html). Clang documents `-iquote` as its QUOTE search-path option (https://clang.llvm.org/docs/ClangCommandLineReference.html). These references explain the chosen flag; the retained G error and new compiler tests establish project-specific behavior.

The contract receipt additionally records the include-policy identifier `R02QuotedProjectHeaders-v1`, host system/architecture, compiler path/version command receipt, and all thirteen emitted fixture bindings. All existing strict command completion, twelve native extensions plus one legacy fixture, schema/UInt64/coverage/malformed-input/serialization assertions and failure propagation remain mandatory. New receipt fields are diagnostics, not acceptance waivers.

## G-02: regression coverage and actual macOS execution

Eight new host tests cover command construction for levels 0/1/2, invalid levels, real header collision, quote-sibling resolution, actual execute orchestration, failed compilation, missing compiler, failed managed execution and incomplete fixture/assertion results. The real compiler test places a sentinel `string.h` beside quoted project headers, includes `<cstring>`, and requires the old `-I` command to fail at the sentinel before the corrected command compiles and runs. Paths contain spaces. Both available host compiler drivers are exercised. Mocked orchestration results remain explicitly synthetic and are not producer/parser evidence.

A dedicated `r02-contract-macos.yml` workflow now checks out the exact candidate runtime and package pins and executes the real native header writer and real package parser at levels 0/1/2 on macOS. It also runs the eight new regressions, records compiler/.NET/OS identities, retains all native fixtures and command logs, and rejects changed source worktrees. This is additional to the existing macOS lifecycle subset. A Linux pass or synthetic test pass cannot stand in for this new actual macOS contract job.

The local Primary Python suite passes 218/218 after the change. Actual selected CI results and source/artifact bindings are recorded separately in `PRIMARY_VALIDATION.md` and `G_PRIMARY_VALIDATION.json` after publication. No current-environment .NET or Unity execution is implied by local Python tests; the actual managed execution belongs to the reported CI jobs.

## Review, next batch and stopping boundary

Focused self-review confirms the existing 33-field producer/parser semantics and all five machine-enforced Editor cases are unchanged. The eight new tests retain negative controls and do not weaken existing assertions. This is not the independent R02 stage review.

Publish a new common source anchor, a matched H1-runtime control with explicit ancestry, and metadata-only final candidate transport. Both workspaces use the same unchanged managed package. Then run one new unused 34-cell R02LocalBatch-v1, retaining full source/host checks, E forensics, both fixed M00 inputs and new controlled graphs, eight sidecars, four pilot plus forty formal A/B pairs, five Editor contracts, generated/native/M07/startup/count/diagnostic/capacity regressions and complete sealing. No changes are delegated to Local beyond tool-path/worktree setup, execution and evidence collection.

Preserve A/B/C/D/E/F/G, all raw inputs and H1 history. G's successful forensic archive recovery and seal are empirical successes of that execution, not current-build acceptance. D1/D2 remain development-stage deferred risks requiring measured disposition before H2. R02Accepted=false; mayEnterR03=false.

Rollback requires a newly reviewed complete source/package/control handoff, never a mixed tuple or deletion of evidence.

## Connector transport

Demo-only disposable branch `codex/connector-smoke-r02-g-20260928-6b93` passed Git-object write/read-back at `20cc7ea959df3c3e78bb6982ddec301ddd3f9993`, based on the Local return above. It remains because no branch-deletion action is exposed. It is not a handoff or validation commit and must not be merged. All three runtime/package repositories are read-only in this cycle.
