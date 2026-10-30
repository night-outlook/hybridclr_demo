# Primary source-only correction review — oneuse-D return (2026-10-30)

## Empirical inputs retained

Local oneuse-D source demo `b6076f8d85ba1ac56bfe15656842eb37115d1475` and final evidence publication `e171676ac039a7b0ce5206279d1ca3719997d4ad` are separate authorities. The current repair does not rewrite them. Oneuse-D actual 3/3 Unity build failures occurred during C++11 compilation. No current Player launched, and no actual installed 126-pair audit ran. Eight scoped coordinator tests were Passed, but the overall result was FAIL. An original archival source audit is not a new independent R03 full-stage PASS.

## Source findings and corrections

- **F1/High — Unity language standard:** Fixed incompatible C++17 pointer declaration and C++14 NSDMI brace expressions in six production-facing files, without changing execution algorithms or feature switches. New genuine host compiler matrix validates current production headers under C++11 + C++17 for ON/OFF; the original core `AssemblyShadow.cpp` still requires actual Unity SDK compile and three Players.
- **F2/Medium — build error precedence:** BuildReport unsuccessful status must be handled before `.app` inventory, preventing absent output from supplanting original native compiler evidence; new receipt fields and eight source contract tests. No compiled Unity Editor C# validation has yet happened.
- **F3/Medium — JSON artifact:** Replaced literal trailing backslash-n with actual newline; now strict round-trip reads persisted bytes.
- **F4/High — new source inventory:** Affected `AssemblyShadowDiagnosticWriter.h` was NOT among original 42 files. The latest native compared with historical 74db contains 43 VM files (9 modified, 34 added). New source manifest includes this exact blob and expands installed-source parity from 126 to 129. Historical 42/126 failure records remain immutable.

## Review limitations and gate

This Primary source audit is not an independent R03 full-stage re-review. Host C++11 test uses a minimal config stub, not actual Unity2022.3 installed toolchain or Player linker. All current native builds, five genuine Player evidence cases and all physical installed pairs remain **NotRun** for the corrected source. Keep independent IR-R03-01/02 open, prior failed runtime evidence Failed, D consumed, R03Accepted=false, ReadyForHumanReviewGate=false and PureInterpreter disabled.

Independent Local reproduction is necessary before oneuse-E can claim at most FocusedEvidenceReadyForIndependentReview, never acceptance or Human Review Gate approval.
