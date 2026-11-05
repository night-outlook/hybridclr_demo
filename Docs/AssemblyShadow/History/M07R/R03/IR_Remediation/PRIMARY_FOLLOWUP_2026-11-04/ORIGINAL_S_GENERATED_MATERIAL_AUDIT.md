# R03 Primary Implementation — original-S generated table audit and V2 host CI (2026-11-04)

**Classification:** Primary source-only verification. Not a new Local Validation run, Unity build, independent review, compiler/link qualification, R03 acceptance, Human Review Gate, or authorization to rerun consumed K.

## Frozen original material and exact source

- Original S source publication: demo `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
- Original executed demo: `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`; executed native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.
- Original S evidence index SHA-256: `0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70`; 15,712 indexed files.
- Working branch: `codex/assembly-shadow-r01b-h1`. First complete new scan source/test input demo `e32be835148715db838014c06a645d72b0772614`. Current interpreter/package/native remain respectively `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` / `948c0e3b4f8891481301770115e8ba4945eea6de` / `41764ae1eeefb33b05966e7f7676e52aae39c340`. Later documentation/CI commits are not a second original S execution.

## Executed read-only source audit

New additive files:

- `Tools/AssemblyShadow/R03IR/audit_s_generated_material.py`
- `Tools/AssemblyShadow/R03IR/test_s_generated_material_audit.py`
- `.github/workflows/r03-ir-generated-material-scan.yml`

[Exact-source successful Actions run 41962491415](https://github.com/night-outlook/hybridclr_demo/actions/runs/41962491415), job 127031856975, executed against demo `e32be835148715db838014c06a645d72b0772614`. **15/15 host tests Passed** and the real historical sparse checkout scanner returned `PassedIdentityAndLexicalScanOnly`, without modifying the original S checkout. The four specific original generated-file occurrences each matched pinned Git blob, SHA-256, size, line count and the original S archive index. Both original NativeOn and NativeOff copies matched byte-for-byte.

| Source file | Unique Git blob | SHA-256 | Lines | Original initializer rows |
| --- | --- | --- | ---: | ---: |
| Il2CppGenericMethodPointerTable.c | `bf86c8ee7dffe81a23c0b21ccbdc37e7374d414c` | `197debac4e5ea493126785b48703f19d0b842caa1bab0ed83d19196d73ac59b6` | 96,487 | **48,232 / 48,232 declared** |
| Il2CppInvokerTable.cpp | `c5a9c6bb34b7a48c000e7c2f16f1b5d4844a4f86` | `fc7a707baf8be8f23061b5362f29f6c2c3e0e52d607add49de1833c1f21c8c03` | 91,940 | **10,198 / 10,198 declared** |

The bounded scanner found 48,232 unique generic table initializer lines and 10,198 unique invoker initializer lines. Initializer-text fingerprints are identical between the original ON and OFF files. It reports line-marker fingerprints, bounded samples, and exact cardinalities; it does **not** purport to parse full C++ ASTs, resolve symbol definitions into linked machine code, or prove every entry safe.

The retained workflow artifact is `r03-s-generated-material-readonly`, ID `13385833136` from run 41962491415. Artifact ZIP SHA-256 `f7f3ee300559aa5388540f4aa50675fdb2a47254e1c0bca93bf5c93139c8562a`; contained JSON SHA-256 `4fa3ac1e5f451f37f8046bad5cc27601c3fb6d7fc9c5a682e72fa661c47c93e0`. SHA-256 values were independently computed from the downloaded artifact in Primary's analysis environment. This is distinct from original S's nine-part evidence archive and from the 2026-10-08 withdrawn five-part family.

At that exact demo SHA, four other source/host workflows also concluded success: K source-bound contracts 41962491407, K terminal observation 41962491512, terminal IR host 41962491425 and L factory/receipt contracts 41962491433. They are not new Unity runs or evidence at a later documentation-only SHA.

## Remaining High finding boundaries

**IR-R03-01 — NeedsEvidence.** This improves the earlier original source *identity-only* crosswalk with actual table-header/initializer cardinality checks and immutable byte fingerprints. It does **not** establish the C++ compiler-object commands, source-to-object linkage, linked Player executable inclusion, or every original capture omission. A future reviewer must still bind these material generated tables to the original executed build/link receipts, map the relevant semantic entries, and reconcile the original capture omissions list. Historical S's 90 cells and 59 process joins remain unchanged and must not be promoted by this host audit alone.

**IR-R03-02 — NeedsEvidence.** The separate `R03IRRemainingTerminalWitnessV1` host consumer and tests exist, but **no genuine captured-generic / initializer-failure / initializer-control Unity Player producers, native V2 preopened reporter, real postpublication initializer field observer, or independently bound source/build/Player receipts are present**. The new cross-platform host workflow `.github/workflows/r03-ir-remaining-witness-host.yml` checks only the existing synthetic verifier; it cannot supply those Player witnesses.

## Next Primary actions and stop

1. For IR-R03-01, implement/verify original compile/link input graph and full original capture-index reconciliation using only authenticated historical sources, without replacing or regenerating old outputs.
2. For IR-R03-02, implement actual physical captured-generic and initializer callbacks/probes with real native V2 snapshot, independently source-bound runners, and strict non-authorizing verifier integration; perform genuine source/host review before any Local handoff.
3. Any future Local Validation requires a fresh explicitly scoped one-use cycle and a separate source-pinned handoff; do not rerun S or K and do not edit existing raw evidence.

The existing `WEB_TO_LOCAL.md` is **CLOSED**. All flags remain `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `qualificationApproved=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter disabled. H2/M08A/X02/SNAP-01 do not begin.
