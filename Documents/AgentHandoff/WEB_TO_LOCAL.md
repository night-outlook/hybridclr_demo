# Primary Implementation → Local Validation

## Objective

Continue HybridCLR Assembly Shadow R01B remediation from the committed source targets below. Resolve the remaining PCH compiler-provenance blocker, execute fresh provenance-bound builds and the project acceptance chain, and return empirical results. **This handoff is ready for local validation, not Ready for Human Review Gate. H1 remains InProgress / technically Blocked; the last independent whole-chain M08 is FAIL; humanGatePassed=false; mayEnterR02=false.**

Git is the sole authority. Do not apply earlier chat ZIPs, recover old speculative D01 patches, or advance from a summary PASS. Primary owns this document and implementation; Local Validation owns `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`. Those two existing files and `preflight.json` are preserved, not overwritten by this delivery.

The preflight returned in demo commit `2802b23291ddcf16de6650a90c39fc44f81dd67f` ran no Unity validation because this file was missing. The substantive prior local checkpoint is `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/d01-d02-local-validation-20260914/`: read `README.md`, `REMAINING_WORK.md`, `PCH_PROVENANCE_BLOCKER.json`, and `source-heads.json` on the candidate branch. It already records D01 route A selected, D02 normal-owner integration, 1067/1067 Editor tests, 758 Python passes plus one declared skip, and restoration/authentication of 93 M01 files. Do not rediscover or reimplement those reliable facts. This new source still needs affected regression testing.

## Source targets

Machine-readable authority: [source-targets.json](source-targets.json). All repositories belong to `night-outlook` on GitHub.

| Role | Repository / branch | Exact source commit |
|---|---|---|
| Candidate demo | hybridclr_demo / codex/assembly-shadow-r01b-h1 | `54259ef467e3937fe1879161aa552e42eb7e5854` |
| Reproduction demo | hybridclr_demo / codex/assembly-shadow-h1-count-repro | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Candidate native | hybridclr / codex/assembly-shadow-r01b-h1 | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Unfixed reproduction native | hybridclr / codex/assembly-shadow-h1-count-repro | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Shared Unity package | hybridclr_unity / codex/assembly-shadow-r01b-h1 | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | il2cpp_plus / codex/assembly-shadow-r01b-h1 | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Performance reference demo | hybridclr_demo / codex/assembly-shadow-h1-performance-reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

The demo commits above are **code anchors**. A following commit on each branch publishes this document, source-targets and pins without changing executable inputs. `ProjectSettings/AssemblyShadowSourcePins.json` must pin the corresponding code anchor. Record both the fetched checkout HEAD and code anchor in local evidence. Resolve the actual handoff revision with `git log -1 --format=%H -- Documents/AgentHandoff/WEB_TO_LOCAL.md`; do not demand a document embed its own circular commit hash. Any later build-input change requires a new reviewed code anchor and fresh affected evidence.

Unity/target: **2022.3.62f2, StandaloneOSX, arm64**. Maintain separate candidate/reproduction checkouts. Pin localPath values remain relative to each project. Do not repoint either to the other native implementation. The performance reference must keep its own older-profile pins, not the shared candidate runtime listed above.

## Implementation

The current change is demo tooling, capture adapters, tests and handoff governance only. It does not alter native count algorithms, the selected D01 serializer/reference route, the package, IL2CPP, historical evidence, or the reproduction defect.

`h1_pch_provenance.py` binds the exact producer and consumer graph dependency, source/output paths, recursive response bytes and every distinct flag/language/PCH context. It permits only the evidenced `-Xclang -fno-pch-timestamp`/single `-include-pch` path, not arbitrary forced includes or compiler escapes. It retains original PCH/header bytes and raw module-file-info output, replays the producer to a new output and requires identical PCH bytes, then runs actual compiler syntax assertions and macro dumps after loading the PCH plus the pinned IL2CPP configuration. NDEBUG is checked by definedness, not its numeric value. Unknown grammar or changed inputs fail with retained diagnostics.

The normal native capture, normal strict verifier, C# receipt fields, evidence collector and successor archive owner now consume this proof. A previous PASS summary is insufficient. PCH data and header/probe text are mandatory archive members; they cannot disappear behind an external-binary exclusion. Non-PCH input retains the existing strict path. `h1_pch_diagnose.py` can replay an explicitly selected old failed attempt without generating a build receipt; its extra diagnostic binding is rejected by fresh-build verification.

`h1_count_build_batch.py` orchestrates a fresh candidate ON/Debug smoke and then all six builds, with explicit ownership checks and separate prepare/build/restore Unity processes. It requires full installed-source verification, saves generated before/after bytes, and restores only the four validated diagnostic-scene fields or the known empty-Standalone serialization change. Unexpected changes stop without being overwritten. `h1_handoff_preflight.py` rejects missing/uncommitted handoff files, wrong branch/origin, mismatched pins or changed executable inputs. Only five exact handoff metadata filenames are excluded from demo-code identity; arbitrary files under Documents are not exempt.

Primary validation: **160 selected portable tests passed (83 new + 77 existing), no failures/errors/skips**. Tiny real Linux Clang PCH fixtures exercise C/C++ × ON/OFF × Debug/Release; synthetic native markers are not Player binaries. Four new NUnit cases are written but NotRun. Apple Clang, the actual 1121-node Bee graph, Unity compilation, real Player builds and M08 have not been executed here. Read the committed `pch-primary-20260914/STATIC_REVIEW.md`, `portable-validation.json`, and `portable-tests.log` under the same remediation directory.

## Local validation

Execute in dependency order; batch independent checks within each step. Preserve unrelated modifications and all previous attempts. First read the local-owned handoff reports, then this file; this file supersedes earlier chat/ZIP instructions for the primary changes, not historical evidence.

**V00 — fetch and authoritative preflight.** In each corresponding checkout, explicitly run `git pull --ff-only origin codex/assembly-shadow-r01b-h1` or `git pull --ff-only origin codex/assembly-shadow-h1-count-repro`. Inspect origin, branch, actual HEAD and worktree diff before any write. Do not reset/clean/stash-away unrelated changes. Run from each demo:

```sh
python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project /ABS/DEMO --role candidate --output /ABS/NEW/candidate-handoff.json
# In the separate reproduction checkout use --role reproduction and a different output.
```

Expected: SourceTargetVerifiedNotBuildAccepted, correct anchors/runtime pins, no unpinned code. This is not an installation check. Retain existing generated dirty inputs before any independently verified recovery; the new batch does not repair arbitrary pre-existing dirt.

**V01 — compile and focused tests.** Use Python >=3.11 and the local selected clang for portable tests. Run each new Python module (test_h1_pch_provenance, test_h1_pch_integration, test_h1_count_build_batch, test_h1_handoff_preflight) via ordinary unittest discovery; run the compiler/native-capture/collector/successor/witness regressions and existing normal M02-owner tests. In reproduction, run only the shared modules present there. Record exact IDs, failures and skips, not a requested count. Compile candidate and reproduction in Unity, then run `AssemblyShadowDemo.EditorTests.H1PchEvidenceProcessTests` (four cases) and affected existing H1 evidence-process tests. Use the existing exact-project ownership helpers. NUnit `-runTests` commands must not include `-quit`. Expected: compile success, all required focused cases pass, raw XML/logs retained.

**V02 — cheap PCH diagnosis before broad builds.** Use the actual old request/DAG/PCH paths in the committed PCH_PROVENANCE_BLOCKER and logs only when those exact bytes still exist. Example from the candidate tools:

```sh
python3 Tools/AssemblyShadow/h1_pch_diagnose.py --request /ABS/OLD_CAPTURE_REQUEST.json --graph /ABS/OLD_BEE.dag.json --output /ABS/NEW/PCH_DIAGNOSTIC
```

This gathers producer replay, header inventory and every context's compiler assertions/dump in one pass. Expected status is DiagnosticReplayVerifiedNotBuildAccepted; this never closes a fresh build requirement. If old bytes are unavailable, record Unavailable rather than Failed and obtain the same diagnostics from a fresh smoke. Do not rewrite old source locators or complete old receipts. Unknown flags, an absent dependency, PCH replay byte differences or macro mismatch must return to Primary with the complete evidence described below; do not broaden an allowlist merely to pass.

**V03 — fresh install, smoke, six-build batch.** Reinstall from the newly committed pins with `HybridCLR.Editor.Installer.PinnedSourceInstaller.Install` in each demo, after ownership checks and retaining the prior installation receipt. This is needed even though native/package algorithms are unchanged: the receipt's demo source pin has changed. Run normal `verify-installed-runtime.py` with its documented CLI (it already inserts the verify operation), with demo checking enabled. No native-only inspection substitute. Then dry-run and execute the batch from the candidate checkout:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py --candidate /ABS/CANDIDATE --reproduction /ABS/REPRO --unity /ABS/Unity --pwsh /ABS/pwsh --scope all --output /ABS/NEW/BATCH
# Review the dry plan, then repeat with --execute and a new output directory.
```

Use `--scope smoke` first when diagnosing Apple compatibility. After its successful complete receipt, `--scope all --reuse-smoke /ABS/EXACT/build-receipt.json` revalidates that one same-source ON/Debug build before continuing the other five; no automatic latest-file choice. Without this option all six are fresh executions. Each Player uses the managed-provenance wrapper, new output/preparation directories, clean-build options and direct managed/native verification. Expected four candidate modes (ON/OFF × Debug/Release) and two unfixed ON modes, complete source-bound receipts, all PCH contexts proved, exact restoration. A single-mode PASS is not four-mode coverage. At least 10 GiB free is checked before each build; do not delete evidence to satisfy it.

**V04 — execute the remaining project chain.** Follow `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/d01-d02-local-validation-20260914/REMAINING_WORK.md` and `continuation-20260914/LOCAL_VALIDATION_TASKS.md` on candidate for the actual existing entrypoints and fixtures. Complete fresh eight unfixed reproduction cells and 132 candidate count cells; fresh baseline/fixtures/replay and all eleven startup modes; affected M03–M07, ON/OFF, ordinary/mixed capacity including 8193 rejection, lazy/dense/generic/array/reflection/FieldRVA and old-Player checks. Reuse only with explicit source/dependency/binary equivalence evidence; do not call it fresh execution. Expected safety-rejection or assertion cells retain their intentional nonzero exits/crashes, not a fabricated zero exit. Preserve 8192 charged lifetime identities, 32 MiB maximum DLL, 512 MiB valid input, retained failures and at least 25% free usable encoded capacity. Run the controlled Development performance pairs on common supported workloads against the separate reference profile; neither Release/P99 nor device RAM fitness is inferred.

**V05 — successor and review.** Collect the new source pins, installed/generated provenance, selected builds, test inventories, all raw results, PCH proofs and dependencies through the committed successor collector. Explicit paths/index mappings resolve capture locators. Authenticate archive/index digests and members, perform the existing strict semantic verifiers, and then commission genuine independent whole-chain design→source→build→raw-evidence M08 review. Tool integrity PASS or this bounded static review is not M08 PASS. Record every exclusion/unavailable artifact and its acceptance effect. Append new evidence; never replace historical v6–v11 archives or failed receipts.

## Failure evidence

For each failed phase record exact repo/branch/checkout HEAD/code anchor/source-pin bytes, command, working directory, exit code/timeout, stdout/stderr, Unity log and NUnit XML. For PCH include the raw selected DAG, recursive response bytes, original and replayed PCH, raw module-file-info, all referenced header/config bytes, SDK settings, compiler/libtool identity and hashes, exact probe source/argv/macro output for every context, failed-attempt JSON and before/after hashes. For build/restore include preparation state, generated scene/meta/settings before/after bytes, restoration checks, managed DLL/snapshot capture and selected native-library identities. Keep failed raw artifacts immutable; absolute paths are locators, not portable proof. Do not select only successful contexts or retrospectively bind a new source tree to old DLLs.

Update and push Local Validation's `Documents/AgentHandoff/LOCAL_VALIDATION.md` with facts, exact test IDs and authoritative evidence locations. Put any nontrivial implementation issue in `RETURN_TO_WEB.md` with a minimal reproducer and the full failing input set. A missing file is Unavailable; a checked mismatch is InvalidEvidence; an executed failure is Failed. Do not merge these categories.

## Alternatives

The production candidate keeps the already selected D01 route A; its existing B route remains diagnostic, not an automatic fallback. For this PCH delivery, the normal route is fresh strict capture. The old-attempt diagnostic replay is a separate explicitly marked investigation route, not weaker acceptance. The explicit same-source smoke receipt reuse avoids one redundant build while rechecking provenance. No no-PCH/PDB-dropping workaround, ignored compiler error, permanent experimental macro or source-authorization relaxation is introduced. Unsupported Apple behavior or non-identical PCH replay requires Primary to design a justified alternative before changing the evidence contract.

## Risks

Actual Apple Clang/Bee compatibility is not proved by Linux fixtures. Conservative grammar may reject legitimate new flags or header-inventory formats; exact replay may expose toolchain nondeterminism. Such results are actionable diagnostics, not reasons to bypass validation. Macro scope is after forced PCH plus the pinned config, before the translation-unit body; it does not prove arbitrary later source cannot redefine macros. PCH probes add build-time I/O/storage; capture has bounded subprocess/overall timeouts and does not modify runtime performance code. Independent build/launch provenance is still required: a self-consistent graph/probe bundle alone does not prove which Player ran. Published source changes invalidate affected older build claims unless equivalence is actually established.

## Local correction boundary

Local may correct explicit machine paths, executable permissions, invocation arguments and isolated test setup, or perform the documented exact generated-file recovery after preserving before/after bytes. A truly independent, locally closed correction may be committed with its test and impact analysis; any executable change invalidates the frozen anchor and must be reported for a reviewed successor source freeze. Do not modify parser/provenance acceptance rules, witness allowlists, count behavior, source-identity exclusions, PCH replay requirements, public ABI, cross-module design or performance methodology locally. Those are Primary responsibilities, irrespective of line count. Do not edit another owner's handoff document or quietly skip a mandatory test.

## Human review gate

Project gate definition: `Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md` and the current R01B remediation plan on candidate. Only implementation plus actual local validation satisfying that definition and a genuine independent whole-chain **M08 PASS** permit **Ready for Human Review Gate**. Then stop for explicit human H1 approval. Neither agent grants human approval. R02 remains prohibited until that approval is recorded.
