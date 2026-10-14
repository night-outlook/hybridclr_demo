# HybridCLR Assembly Shadow

Plan holds normative R03 design and Human Review Gates. Handoff holds current Primary assignments and Local-owned factual returns. History preserves original source and evidence.

## Current state — SNAP-01 FAIL; native V2 codec implemented but inactive

**Current owner: Primary Implementation. No new Local runtime execution is authorized.** SNAP-01 remains FAIL/ReturnRequired and diagnostic collection EvidenceCollected:18 cells14 Passed/4 Failed,3 builds/5 Players; OFF and3 Bee observations Passed. Three ON first native failures prove slot14/finalDiagnostics exceeds the original262144-byte text capacity; recorded262145 is a scanned prefix, not an exact full length. Empty raws/exit2 remain Failed. Engine51213 uncapped reports/500ms and exit71 remains Failed. Host/compiler/custody/storage/after/seal passes do not override these results. Do not retry SNAP-01 or N.

The previously published [V2 representation design](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/LOSSLESS_DIAGNOSTICS_DESIGN.md) now has an **inactive native implementation of its framing and bounded capture-sink component** under `Tools/AssemblyShadow/R03IR/bounded_v2/`. The native header emits exact complete UTF-8 fields, incremental/context/whole hashes and the commit footer using <=65536-byte frames and the unchanged4194304-byte encoded envelope/artifact allowance. It rejects overflow instead of truncating or enlarging limits. It does not connect the actual VM serializers, publish durable files, change the existing semantic verifier or control Unity scheduling.

[CI38529319047](https://github.com/night-outlook/hybridclr_demo/actions/runs/38529319047) passed the same20 cases per strict and ASan/UBSan profile on Linux Clang, Linux GCC and Apple Clang. Three original ZIPs,2445 declared artifact files and492 compiler/process records were independently authenticated. Exact native bytes match the immutable Python V2 reference, including two complete fields individually larger than262144. Six full test logs are retained losslessly. Apple LeakSanitizer was unsupported and is explicitly Unavailable; ASan/UBSan remained enabled. No actual Unity, GC, scheduler, current live custody or corrected Player ran here.

## Read order and remaining work

1. [Current status](Plan/CURRENT_STATUS.md), [paused WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md), factual Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md), original SNAP-01 checkpoint.
2. [New Primary native-codec reconciliation](History/M07R/R03/IR_Remediation/SNAP01_NATIVE_CODEC_c2e8/PRIMARY_RECONCILIATION.md), [exact evidence](History/M07R/R03/IR_Remediation/SNAP01_NATIVE_CODEC_c2e8/EVIDENCE.json) and [native component usage](../../Tools/AssemblyShadow/R03IR/bounded_v2/README.md).
3. [Lossless design](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/LOSSLESS_DIAGNOSTICS_DESIGN.md), [engine ownership design](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/ENGINE_TERMINAL_DESIGN.md), and [implementation plan](History/M07R/R03/IR_Remediation/SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md). P1a component is complete in host scope; full P1/P2/E0/E1 remain open.
4. Original C scoped-loss policy, S seal/fixture provenance, retained R/Q, prior source/evidence outcomes and independent R03 full-stage FAIL/Human Review Gates.

The next Primary work is actual common native serialization/coherent frozen capture, secure prearmed durable sidecar/envelope and tagged V2 semantic dispatch reusing every original predicate. A wire receipt is not an fsync/close or acceptance receipt. Separately, the supported native StandaloneOSX engine-owner safe point/maintenance/restart capability must be established and implemented; the native coordinator model is not an adapter. No pointer guessing, fake acknowledgement, report caps/coalescing, sleeps, finalizer suppression, arbitrary managed allowlists or early-exit shortcut is allowed.

## Source, custody and acceptance boundaries

All canonical branches remain `codex/assembly-shadow-r01b-h1`; native `0f72078711d4786dac2666c9017d952d857dd041`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and package `948c0e3b4f8891481301770115e8ba4945eea6de` unchanged. Current component anchor `8120ca91c0c762b8b29f703f087ab1bfdaf0f532` descends from design09720df7692598561d59722753a0e58e08e276ad. The final publication SHA is for Primary review, not execution. Original current Player/native guard/runner/verifier/source-pin files and historical Local reports were not modified.

Strict historical S custody remains Blocked:416844 original,339367 survivors,77477 missing identities and4 original S installed-native roots absent. Scoped preservation is not historical provenance restoration. SNAP-01/N/M/K/I/E remain FAIL; F/H/L blocked; G/J historically scoped Passed. All acceptance flags false; independent full-stage R03 FAIL/rereviewNotRun; PureInterpreter expansion disabled. Captured-generic/initializer, IR-R03-01, normal finalizer/shutdown and broad legacy/performance remain open. No H2/X02/M08A or automatic Human Review Gate.
