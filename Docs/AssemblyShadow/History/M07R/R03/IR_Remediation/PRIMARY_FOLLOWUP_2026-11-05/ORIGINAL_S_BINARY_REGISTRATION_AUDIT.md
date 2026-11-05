# R03 Primary continuation — original S code-registration and Mach-O symbol audit

Date: 2026-11-05 UTC. Scope: IR-R03-01 source/build/evidence provenance only. No fresh Player/Unity execution.

## Frozen authority

Original S publication: night-outlook/hybridclr_demo@fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b.
Original execution demo: 29bb3d4a39bf8a2f23be404f77535aaba3485bfc; original native: 1cf87f8209790f9fb2ebec97487dc1990ccd56c5. These are not the current native 41764ae1eeefb33b05966e7f7676e52aae39c340.
Original S evidence-index SHA-256: 0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70 (15,712 indexed members). Canonical nine-part archive SHA-256 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6. The older five-part family remains withdrawn.

## Newly implemented source-only audit

The new files are Tools/AssemblyShadow/R03IR/audit_s_binary_linkage.py, Tools/AssemblyShadow/R03IR/test_s_binary_linkage.py, and .github/workflows/r03-original-s-binary-linkage.yml.

The audit uses the exact clean original S checkout and original archive index, authenticates both on/off generated source files, parses the actual Il2CppCodeRegistration.cpp initializer rather than loose keyword occurrences, checks both archived GameAssembly.dylib file bytes/Git blobs and executable Git mode 100755, and examines actual Mach-O symbols using nm -m. It fails if either required generated-table symbol is undefined, duplicated or only similarly named.

The generated registration contains 48,232 g_Il2CppGenericMethodPointers and 10,198 g_Il2CppInvokerPointers, matching the previously audited initializer row counts. The original on/off code-registration fields and external references match.

| Original role | Archived GameAssembly SHA-256 | Generic symbol address | Invoker symbol address |
| --- | --- | --- | --- |
| NativeOn | e9d926f18d8cc8632070b78e61ecebd1e2f67e47568977ad62f587f0326c3839 | 0x2b9dee8 | 0x2b4c328 |
| NativeOff | 7212782000fe67cc5917da333a362af9b3d6c73b94fb6cb97332ed079b229fe8 | 0x2b0dea8 | 0x2abc2e8 |

Both symbols in both original binaries were reported as defined, non-external symbols in the __DATA_CONST,__const Mach-O section. This establishes real archived binary symbol presence, but does not independently prove exact original C++ source bytes compiled into each object, complete compiler/link input closure, or a particular Player process execution.

## Executed verification and correction

- Initial read-only macOS run 41964893231 FAILED because the audit assumed Git mode 100644 for GameAssembly.dylib. Immutable Git tree independently confirms mode 100755. This was an audit implementation error, not a detected archive discrepancy.
- Corrected run 41964999042 PASSED, 11/11 host tests, plus both actual original archived Mach-O inspections.
- Strict final source revision f15eb260b51117da0da37a567876eab2cd1ed331: [Actions run 41965330265](https://github.com/night-outlook/hybridclr_demo/actions/runs/41965330265), 14/14 host tests PASS and actual original-S audit PASS. Tests reject undefined, lookalike and duplicate symbol records.
- Final [Actions artifact 13386923737](https://github.com/night-outlook/hybridclr_demo/actions/runs/41965330265/artifacts/13386923737) ZIP SHA-256 abecea0443f9fda805bdbcb33fc0459aa082e599e45e3f76acae6fd19566c8eb; contained JSON SHA-256 2715ec502e3d2f27584dfea0a84173fdf2d6698d10f6e3b78a9859adb6775e5b. The ZIP was independently opened and its ON/OFF symbols, addresses and SHA-256 identities inspected.

## Explicit remaining boundaries

IR-R03-01 stays High / NeedsEvidence. Source-to-compiled-object hash/commands, linker input closure, full original capture-omissions reconciliation and exact archived executable-to-original-Player-process joins are still not authenticated.

IR-R03-02 stays High / NeedsEvidence. Captured-generic and postpublication initializer Player producers and real V2 native snapshot remain unimplemented. The initializer Prepare executes during Committing=5; K's old binder requires Committed=6 and field value 2. A separate before-terminal native observation of the actual prepared field value 3 is required. The old V1 cannot be relabelled.

No Local Validation, Unity, IL2CPP native build, original S replay or new Player was executed by this audit. WEB_TO_LOCAL.md remains CLOSED (K consumed). R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false. PureInterpreter disabled; H2, M08A, X02 and SNAP-01 remain closed.
