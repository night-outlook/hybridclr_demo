# R03 current-native one-use Local cycle — Primary source and test review (2026-10-26)

**Status:** Primary implementation source/host-only preparation complete; **actual Local execution NotRun**. This is NOT a separate independent R03 full-stage reviewer verdict. The original independent review remains FAIL (IR-R03-01/IR-R03-02 High). Source-only approval does not change R03Accepted=false.

## 1. Immutable pins, scope, ownership

Working branch: codex/assembly-shadow-r01b-h1. Primary implementation source commit before handoff-document-only successors: 9d5d2b4a885e0109388554ad07271ede2d829534 (demo). External runtime source pins: hybridclr 4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity 948c0e3b4f8891481301770115e8ba4945eea6de, il2cpp_plus e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb. Historical original-S read-only worktree pin fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b. Historical old R03 runner uses native 74dbdbea80d83923863303bd2b2c0a87f36541b1, unchanged.

All changes are additive only to night-outlook/hybridclr_demo, under Tools/AssemblyShadow/R03IR, Docs/AssemblyShadow, and one workflow. No native/interpreter/package/Unity Player fixture was edited. No consumed archive/runner/result was rewritten.

## 2. Actual production test path reviewed

- Existing run_terminal_current.py validates candidate ten-source Git blobs and exact three external HEADs before creating a fresh batch, overlays the current native e1e5 pin in memory, then delegates to unchanged run_terminal_local.py.
- The unchanged focused runner defines three candidate native role builds (release/debug/OFF), five fresh Player cases (release/debug baseline owner, release type failure, OFF, engine unhandled), original-S exact fifteen fixture copies, deterministic separately generated side-effect Methods.dll and strict native build-v2 source installation checks.
- Existing verify_ir/verify_engine test oracle checks actual post-poison reflection/delegate/AOT attempts, stable terminal reason, unchanged body field and AOT canary, pre-poison success, request/process nonce/role identity and native engine terminal sentinel. Existing 27 host adversarial tests execute these verifier functions against synthetic receipts, not a new Player.
- Existing 42-file native VM manifest checks exact current Git blobs across 8 modified and 34 added VM paths. Source-only bytes alone do not prove installed or linked source.
- New current_native_install_audit.py independently compares exactly those 42 VM current source bytes against installed source tree in each of the three build roles, checking before/after installed file inventories, build-v2 receipt and exact role/project/pins. It records 126 required source-installed pairs without claiming native transitive include closure, generated C++ coverage or compiled/linker identity.
- New run_current_native_validation_cycle.py requires zero-write preflight, complete host suites, original S byte/90-cell/59-process read-only reauthentication, independent source-host native diagnostics, the fresh three-build/five-Player run, installed source parity and postflight Git authority before declaring the limited focused evidence ready for independent review. A failure in any required stage is ReturnRequired, not an accepted stage. Original-S archival failure does not erase independently completed fresh Player results; source/oracle failures prevent a fresh Player launch.
- Every stage uses a once-only invocation marker, separately owned process group, captured stdout/stderr SHA256, start/end/exit and cleanup observations. A zero-exit group leader with surviving child fails; the group is signalled and the failure remains recorded. Existing future scripts are not rerun in a historical consumed root.

## 3. CI: verified source-only results

- First code commit 718b635fb4060d59f5a73639a4c82d84a5e4556b triggered CI 40314633425: Ubuntu passed, macOS failed two test-fixture path checks because macOS /var is a symlink to /private/var. This was a real host test failure and remains retained, not rewritten.
- Corrected mock fixture in commit 2515c101745af6b123b5bb2ced81aa4cfabfd834 to use physically resolved temp base; CI 40314856281 passed macOS/Linux.
- Expanded installed-source parity source and 15 adversarial tests in a1fcdc3a0e406ec18dd7ec492ef89c2f033ee349; CI 40316044735 passed macOS/Linux.
- Latest child-process no-survivor correction commit 9d5d2b4a885e0109388554ad07271ede2d829534: GitHub Actions CI https://github.com/night-outlook/hybridclr_demo/actions/runs/40317130046, completed SUCCESS, both macos-15 (job 121552429124) and ubuntu-24.04 (job 121552428648). Raw job logs separately inspected. Each host ran **20 + 15 + 20 + 27 + 12 + 30 = 124** host-only tests with no failures/errors. Counts are respectively coordinator, installed-VM synthetic, source candidate, actual verifier synthetic, changed VM source and original-S audit host contracts.
- GitHub's CI source checkouts used current e1e5 native, interpreter 4b27, package 948c; the demo CI commit is code 544f. Test receipt not from a real four-clean-checkout Local execution, not official installed SDK, original S full archive reconstruction, real Player or independent reviewer.

## 4. Reviewed change boundaries and limitations

Primary inspected canonical R03/IR runners and related native source/authentication utilities. Source review identified original runner's source-to-installed gap; it is addressed with 126 explicit physical byte comparisons but not falsely promoted into a compiled/linked C++ proof. No modification to authoritative historical source-pins, five-case C# fixture or recovery/guard predicates was required in this bounded Primary cycle. The current native e1e5 runtime entry guard is still NOT empirically proven by this CI.

Material unresolved items:
1. IR-R03-02: exact e1e5 installed native and actual Unity 2022.3.62f2 arm64 Player execution with authentic method-entry attempt after terminal poison remains NotRun until Local. The original five cases do not cover captured generic, initializer, all virtual/interface/AOT crossings. Physical source parity is not a generated C++/linker dependency closure.
2. IR-R03-01: original S archive provenance/90 cells and historical process joins need actual full read-only Local archive access and then a separate independent semantic reviewer. The original nine parts, generated oversized method-pointer/invoker C++ material, original source/build/Player executable pairing, resource ABI and M01 NoCoverage must be independently examined. No omitted historical raw has been fabricated.
3. P1 incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Original b7e3/c42a overall FAIL, f51d historical-only PASS, original S 90/90, D1=A V1-only, D2=A observational performance and prior four contaminated Failed certificates remain unchanged.
4. No Unity installation, IL2CPP build, source-produced real C++ compile/link, Player execution, Unity Test Runner, original S archive full reproduction or live source receipt is possible to claim from this web environment.

## 5. Next handoff and independent assessment

The authorized one-use next cycle is documented in canonical Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md, which requires a final full pushed demo transport SHA from the short Local prompt, not the earlier code-only source anchor above. Exact CLI and one-use root are specified there. Local owns factual empirical run/receipt collection and bounded setup issues, not nontrivial design/source changes. It must publish LOCAL_VALIDATION.md and RETURN_TO_WEB.md and preserve failures.

After Local returns, Primary reconciles exact source/process/install/Player pairs and fixes nontrivial issues. A separately human-initiated independent R03 full-stage review is required for IR-R03-01 and IR-R03-02 dispositions and RC1–RC6; H2 is user-triggered only if full R03 acceptance predicates truly hold. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled.
