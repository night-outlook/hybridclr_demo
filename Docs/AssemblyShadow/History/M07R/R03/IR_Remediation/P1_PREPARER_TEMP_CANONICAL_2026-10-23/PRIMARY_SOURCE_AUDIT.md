# Primary source and host audit — IR-LOCAL-P1-PREPARER-TEMP-01

## Reviewed authoritative sources

- Local-owned: `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` at remote demo 79532a96873889f1e1fc0307cdd513000ab037d2.
- Immutable 6c72 checkpoint `FINDING.json`, `LOCAL_RESULT.json`, `README.md`, after-preservation and original test stderr receipt. The actual previously executed source was demo 7a098e45b41b98ee024ed0205b353aa2f132aae9; Local 13 discovered tests/12 Passed/1 ERROR, no core invocation.
- Corrected file: `Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py`, Git blob **d8838bf0788d41a306f900f70d8052cb2d409803**, SHA256 **74ee21349d0bc8f8723d7528c89d83f0b1250e27c4f0dc0692087f0a1102ce01**.
- Original unchanged production/source-admission tool: `Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py`, Git blob **cf2fdf39fe17df076d50dcc33ed72c757eaa3b26**, SHA256 **ddaa342817906dec659c4be062ea052cd8e12ed1ad2b538bcb283ae12a750db8**.
- Native source pins unchanged at `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. The old 82dd predecessor and source-frozen e1e5 evidence remain untouched.

## Changes and independently executed host results

Precisely one preexisting test line was changed: `Path(d)` -> `Path(d).resolve(strict=True)`. Two additional test leaves exercise (a) actual inherited tmp path vs canonical, (b) test-owned aliased symlink parent and absent child. The production root guard and its required absolute, unused, nonsymlink and exact-canonical validation are unchanged; other existing test leaves and their expected-failure contracts are unchanged.

**Actual Primary execution environment: Linux x86_64, Python 3.13.5 (not native macOS).** The complete 15-test suite ran under the canonical host and independently under an in-process synthetic `/var -> /private/var` temp parent. Both runs **15/15 Passed, zero errors/failures/skips**. Literal source bytes were reconstructed locally and compared by `git hash-object` with the GitHub Connector fetched blobs above, and Python AST parsing passed. No Unity, compiler or network was used by these tests.

Evidence payload `EVIDENCE.json` records actual Python/platform, source and raw stdout/stderr SHA256/byte counts and commands. These are **Primary host-only** proofs, not macOS installed Unity SDK evidence. The prior Local 6c72 blocked result remains unchanged.

## Remaining required gates

The original 25-component runtime-source-host/installed official SDK syntax-only batch has not been launched at the current source tuple. Actual Mac prerequisite test, independent source provenance, compiled native SDK, 85 old tests, 8 inventories, 5 managed positives + exact negative, 100 native syntax, 20 Git postflight and historical preservation are pending. Human Review Gate is not authorized; all runtime/product acceptance flags remain false.
