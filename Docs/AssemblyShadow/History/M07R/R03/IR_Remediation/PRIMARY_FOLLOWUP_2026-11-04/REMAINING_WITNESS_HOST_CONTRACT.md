# R03 Primary Implementation — remaining witness host-contract publication (2026-11-04)

**Status:** Published source-only preparation. This is **not** new Unity, IL2CPP, native Player, Local Validation, independent R03 full-stage approval, or acceptance evidence. The canonical Local handoff remains CLOSED and consumed K is immutable.

## Source authority

- Working branch, all repositories: `codex/assembly-shadow-r01b-h1`
- Demo feature-branch HEAD before these additions: `715ab80283a4df8961ef88aa3f08ef765bc38d7a`
- Interpreter: `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`
- Unity package: `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`
- Native VM: `night-outlook/il2cpp_plus@41764ae1eeefb33b05966e7f7676e52aae39c340`

The existing primary verifier V1 fix, host fixture generator, existing Player runner and all historical S/K raw evidence are unchanged.

## Additive files

- `Tools/AssemblyShadow/R03IR/remaining_witness_contracts.py` — standalone fail-closed schema/semantic consumer for only `captured-generic`, `initializer-failure`, and `initializer-control`. It expects the distinct `R03IRRemainingTerminalWitnessV1` envelope and `NativePreopenedSnapshotV2` transport **that are not yet implemented by a real Player**. It returns only `SchemaSemanticsOnly` with all acceptance flags false. It does not validate raw-snapshot authenticity or complete diagnostics on its own.
- `Tools/AssemblyShadow/R03IR/test_remaining_witness_contracts.py` — synthetic host-only tests for three positive schemas, strict error-code separation, invalid/forged authority fields, original V1 relabelling, PID and physical-image-index cases, and multiple negative mutations.

The exact prepared source Git blob identities were verified after Connector publication:

| File | Git blob SHA |
| --- | --- |
| `remaining_witness_contracts.py` | `de1531c09049d0a331ed57dcc4e688b4efd9ffaf` |
| `test_remaining_witness_contracts.py` | `e40cdbe49c2144c2dcc43692c3c76a75a0058efe` |

## Host verification

Executed in the source-preparation environment:

`cd Tools/AssemblyShadow/R03IR && python3 -m unittest -v test_remaining_witness_contracts.py`

Result: **8/8 test methods passed**, including more than 55 independently rejected synthetic negative cases. Both files also passed `python3 -m py_compile`. These checks do **not** use authentic Unity/IL2CPP output. The prepared source package SHA-256 was `07b47a5beebdcb515a7925488afedc92f503a7ff5326b67ae30b54c2a615d748`.

## Remaining implementation, review, and stop boundary

1. Primary must implement actual distinct Unity Player producers and test-only native field/physical identity observers for the three new cases. The present V1 Player may not be relabelled as V2.
2. A separate coordinator must independently authenticate the exact four Git commits, fixture/MVID, Unity build and source-manifest hashes, native overlay, executable/PID/launch, truly preopened native raw snapshot, and full diagnostics. Never derive the expected identity record from raw Player fields.
3. The real captured-generic witness must capture a physical baseline Methods type argument in a noncandidate owner and prove first failure code 15; the initializer-failure witness must execute the actual postpublication module initializer, preserve first failure 19 and a native-observed side-effect field 3; initializer-control must really commit and run once with side-effect field 3. The previous [TERMINAL_PRODUCER_WITNESS_DESIGN.md](TERMINAL_PRODUCER_WITNESS_DESIGN.md) remains authoritative for the detailed requirements.
4. Complete new source review and source-pinned CI before proposing any fresh Local Validation cycle. No Local run is authorized by publishing these tests; no replay of K/I/J or original S.

Independent High IR-R03-01 and IR-R03-02 remain open. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false, fullLegacyRegressionAcceptance=false, and PureInterpreter disabled.

## Connector write-path evidence

The GitHub Connector successfully created and read back a new commit `809e57a01624a38ff8cb0ee7cc1b6c2b60ebb6a6` on the disposable branch `codex/r03-smoke-20261104-retry-f4e2`, based on the demo feature HEAD `715ab80283a4df8961ef88aa3f08ef765bc38d7a`. The disposable branch remains because branch deletion is not available through the current Connector. It is unrelated to the feature branch and not evidence of runtime acceptance.
