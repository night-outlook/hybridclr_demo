# Primary Implementation → Local Validation — HOST-ONLY HANDOFF; RUNTIME PAUSED

**Primary Implementation authorizes one READ-ONLY source-bound host diagnostic preflight only. No Unity Editor/Player, IL2CPP SDK integrated compile, engine sentinel runtime run, historic evidence re-run, or new seven-root Player execution is authorized.** This limited host assignment does not change the historical SNAP-01 FAIL/ReturnRequired or remove the Primary responsibility for P1/P2/E0/E1/P3.

## Mandatory read order and authority

1. Docs/AssemblyShadow/README.md, Plan/CURRENT_STATUS.md and this WEB_TO_LOCAL.md.
2. Local-owned Handoff/LOCAL_VALIDATION.md and Handoff/RETURN_TO_WEB.md, plus immutable local SNAP-01 checkpoint and original evidence.
3. History/M07R/R03/IR_Remediation/SNAP01_EXECUTION_FORMATTER_2026-10-15/PRIMARY_RECONCILIATION.md and ENGINE_OWNER_CAPABILITY_ASSESSMENT.md.
4. History/M07R/R03/IR_Remediation/SNAP01_FILE_TRANSACTION_PROMOTION_2026-10-14/PRIMARY_RECONCILIATION.md and EVIDENCE.json.
5. Historical native V2, original bounded design/Primary plan, all prior R03 full-stage FAIL and Human Review Gates.

The final README and this file are published on canonical branch codex/assembly-shadow-r01b-h1. **The latest pushed demo commit is supplied as an exact 40-character SHA in the accompanying Primary→Local prompt and must equal the remote HEAD before any host test.** This document cannot reliably hardcode its own final containing commit SHA. Do not infer demo SHA from any older execution or source anchor.

| Canonical GitHub repository | Local exact owned path | Branch | Required pushed SHA |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | codex/assembly-shadow-r01b-h1 | Final Primary-published branch HEAD, exactly as in handoff prompt |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | codex/assembly-shadow-r01b-h1 | fc0d3565ecc5c9d1a31520a26ff3f9fda25bc98f |

Source/ABI package: Unity2022.3.62f2 StandaloneOSX arm64 is a future integrated compilation/Player target, NOT exercised by this host batch. Tools/AssemblyShadow/R03/source-pins.json pins the three non-demo SHAs above. Exact README source history is not an execution tuple. Historical SNAP-01 original four-source execution SHAs and real output roots remain immutable. Never use obsolete Player overlays or old build roots as new runtime evidence.

## Work completed by Primary (bounded scope)

- New native VM-independent typed execution JSON formatter in il2cpp_plus/libil2cpp/vm/AssemblyShadowExecutionSerializer.h. The REAL enabled GetExecutionDiagnosticsJson now uses its shared Header/ClassRow/Begin/AppendClass/EndClasses for its existing legacy string output; original VM metadata acquisition remains unchanged/unbounded.
- Focused strict/sanitized golden-byte, max integer, escape/NUL, exact-capacity and rejected-sink tests in il2cpp_plus/tools/r03/diagnostic_stream/execution_serializer_tests.cpp.
- Native CI 38675806461 **Passed** across macOS Apple Clang, Linux Clang and Linux GCC after correcting a host include-path-only failure. No official Unity/Player acceptance is claimed.
- Demo Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py and .github/workflows/r03-primary-host-preflight.yml provide a read-only, branch/remote/clean-worktree-verified multi-suite host batch. It records each command, source-before/after hashes, stdout/stderr SHA-256 and final external artifacts.

The pre-existing general bounded serializer, native V2 codec and POSIX file transaction are unchanged/inactive components and remain host-testable. New source does not connect those components to a Player or repair the original failure.

## ONE host-only Local Validation command

First independently verify clean four-repo worktrees on the exact remote branch/commits above. Confirm the requested output directory does not exist and resides on an external test volume/root separate from all four repositories and protected historical evidence. For example, using an existing writable parent directory /Users/ah/GitHub/hybridclr/r03-local-validation:

    python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py \
      --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r \
      --expected-demo [40-character commit from final Primary handoff prompt] \
      --expected-native fc0d3565ecc5c9d1a31520a26ff3f9fda25bc98f \
      --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03-PRIMARY-HOST-ONLY-20261015-fc0d3565

The demo SHA shown as square-bracket notation above is an explanatory parameter, NOT an authorized literal shell argument. Replace it only with the exact verified commit in the final handoff message. The output path is a suggested fresh **host-only** location, not one of the seven future runtime candidate roots. The preflight fails closed if the output exists, the parent is absent, paths alias a repository, any repo is dirty, branch/HEAD/remote differs or local commands fail. Do not delete or overwrite any existing path to satisfy it; choose a different unused host-only output name instead.

Expected suites, all under the one batch (distinct failures preserved):
1. il2cpp_plus/tools/r03/diagnostic_stream/run_tests.py: original general stream/legacy byte parity and bounded V2 interop, strict/sanitized.
2. demo/Tools/AssemblyShadow/R03IR/bounded_v2/run_tests.py: fixed-storage native V2 codec/invalid input/identity and resource limits, strict/sanitized.
3. demo/Tools/AssemblyShadow/R03IR/bounded_v2/run_transaction_tests.py: descriptor-bound POSIX file transaction, durability requests, faults and strict read-only decoder, strict/sanitized.
4. demo/Tools/AssemblyShadow/R03IR/NativeDiagnostics/test_native_v2.py: existing native sink/codec contract negatives, strict/sanitized.
5. New execution_serializer_tests.cpp: strict and sanitized source-bound native host compile/execute using local CXX and quote-only include paths.

Required evidence: chosen external root RESULT.json (result PassedHostOnly or FailedOrIncomplete), MANIFEST.json and all files/symlinks inventoried; per-component evidence subdirectories, stdout.bin/stderr.bin SHA-256, command.json, original strict/sanitized logs and compiler receipts. Preserve the actual compiler, runtime OS and inability to execute any component. Verify original-source hashes before/after and record source/runner paths, exact SHAs, any warning, uncovered platform/sanitizer property and full failures. Do not label a host result as integrated SDK compile, Player PASS, SNAP-01 repair, R03 acceptance or a completed Human Review Gate.

## Local ownership, allowed operations and stop

Allowed: read-only repo/source inspection, clean fast-forward to the exact published remote SHAs **only if clean and safe**, running the above host-only command once, collecting receipt/CI/source facts, recording a new factual section in Handoff/LOCAL_VALIDATION.md, recording nontrivial problems in Handoff/RETURN_TO_WEB.md when present, and committing/pushing only the Local-owned factual documentation. Any discovered source mismatch, credential/provenance error, test failure or unavailable compiler stops host promotion; report the failure without retrying consumed Player attempts or mutating tests/source. Compiler tool selection (clang++/g++ and safe ASan/UBSan environment) and fresh output-directory selection are bounded environment actions, **not** architectural fixes.

Forbidden: any modifications to Primary-owned product/VM/native/managed code, serializer/reader/validator, tests or workflow; no unapproved local bug workaround; no changes to original semantic predicates, 1–64 uncapped reports, 500ms window, current V1 per-text262144, V2 frame65536, artifact3932160/envelope262144/combined4194304; no caps/coalescing/no-op dispatch/early exit, finalizer suppression, native scheduler ABI guesses, stage migration, history rewrites or starting H2/M08A/X02. Do not use uncommitted local results as authoritative handoff. A failure of a host test must be returned to Primary before changing substantive code.

## Remaining Primary prerequisites: no runtime assignment

P1 **Not completed**: allocation- and lifetime-reviewed coherent general+execution VM capture, full lossless actual diagnostics, bounded peak memory/freeze and no terminal managed bulk strings.
P2 **Not completed**: actual native/C# V2 emitter/wire, independently authenticated health-time file identity and transaction, complete readback into **every unchanged original V1 semantic predicate** with tagged V2, full failures.
E0/E1 **Blocked**: supported Unity2022.3.62f2 StandaloneOSX engine-owner safe point, queued/in-flight callback drain, native GC/finalizer/service maintenance, restart lifecycle. A modeled coordinator and Unity public PlayerLoop/plugin callbacks are not evidence of these capabilities.
P3 **NotRun**: four-source integrated official Unity managed/55-native compile, independent terminal path review and fresh authorized 3-build/5-Player Local runtime successor.

Immutable outcomes: SNAP-01 18 cells 14Passed/4Failed, 3 ON zero-byte/exit2 with authentic slot14 prefix262145, engine51213 reports/500ms/exit71; N/M/K/I/E FAIL, S custody Blocked (416844 original,339367 survivors,77477 missing, four original native roots Missing), independent full-stage R03 FAIL / re-review NotRun.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled. **A successful host-only batch returns factual host evidence to Primary, not authorization to continue the Player/engine phase.**
