# Bounded primary static review — PCH provenance and formal handoff

This is an implementation self-review, not an independent M08 review. H1 remains blocked pending local validation.

## Basis and preserved facts

Start from candidate 2802b23291ddcf16de6650a90c39fc44f81dd67f and reproduction 426f00fda92a97dd1ed3eb261169e9c0c2203400. The committed local D01/D02 checkpoint already selected explicit-reference route A, passed 1067 Editor cases, recorded 758 Python passes and one skip, and authenticated restored M01 inputs. The later local preflight did not run validation because WEB_TO_LOCAL.md was absent. No historical source, receipt or local-owned handoff report is overwritten.

## Review trace

| Requirement | Implementation and check | Remaining real validation |
|---|---|---|
| PCH not admitted as unexplained forced input | Exact producer/output and file/node dependency; recursive response closure; conservative flag grammar; all contexts enumerated | Actual Apple/Bee DAG grammar |
| PCH bytes bind producer | Original bytes, header inventory, compiler/toolchain hashes, identical redirected producer replay | Actual Apple deterministic replay |
| Macros include prefix state | Compile assertions plus raw macro dump after PCH/config; NDEBUG definedness; C/C++ × ON/OFF × Debug/Release tests | Unity-selected compiler, SDK and PCH |
| No fake old-to-new proof | Build/source/native/graph identity; diagnostic-only replay has incompatible binding | Six fresh source-bound builds |
| Normal entrypoints enforce proof | C# DTO and capture → strict verifier → successor owner; archive reader checks mandatory raw members | Unity serialization/build integration |
| Safe local batching | Smoke dependency, explicit receipt reuse, ownership checks, full pin verification and narrow recorded recovery | Six-build actual Unity workflow |
| Formal handoff cannot be omitted | Committed-document bytes, exact branch/origin/source targets and five-file metadata whitelist | Full real checkout preflight |

## Findings handled during implementation

Preserved `.pch` extensions because the selected Clang module-info command can ignore an unrecognized binary suffix. Added producer replay instead of trusting only a file hash plus declared graph. The SDK `dummy` dependency is treated only as a bound Bee SDK marker; compiler/libtool remain explicit toolchain identities. Empty optional Path/Sha256 pairs are absent, while half-empty pairs still fail. Added source-target preflight and limited metadata exclusions rather than exempting the whole Documents directory. Added all-context diagnostics and explicit old-attempt replay so Apple issues can be collected before repeated Unity builds.

## Executed validation and limits

160 selected portable cases passed, 83 new and 77 existing; no skips/failures/errors. See portable-validation.json and unchanged portable-tests.log (module byte ranges are indexed). These use a verified source slice, not a complete local Unity checkout. Tiny actual Linux Clang PCH fixtures and synthetic DAG/native markers are explicitly not Player evidence. Four new NUnit cases, Unity compile, actual Apple PCH graph, Player builds and independent M08 are NotRun. Two earlier combined test commands exceeded this host's execution window; completed per-module runs are the indexed result, not an inferred success from interrupted output.

The published strict-verifier file differs from its initial local representation only by the final newline. AST equality and the actual normal-entry integration test were rechecked; strict-published-byte-recheck.log is retained. No executable semantic change was accepted without testing.

## Residual constraints

Unknown PCH compiler options, module/VFS chains, missing producer edges, changed headers or non-identical replay are hard failures requiring Primary analysis. No disabling of PDBs, default-false macro inference, unrestricted -Xclang route or automatic no-PCH fallback. Raw graph/probe consistency is necessary but not sufficient for build/launch authenticity. Performance and gate claims remain subject to the existing project requirements.
