# R01 early-observation pairing preparation

Status: InProgress / NotAccepted / H1NotReached. This is prebuild evidence, not Player acceptance.

The initial ConfigureOnly pair reproduced ASR-011 in four pre-Configure use paths. Its eight individually verified diagnostic processes and two ordinary-probe failures remain preserved. The ordinary failure was a probe bug: it compared the raw snapshot JSON SHA to its semantic snapshot hash. The corrected probe binds both independently to the selected Player inputs and consumes verified DLL bytes.

The next baseline is `M07-Baseline-R01-early-v1`, runtime ABI `33bcf290b4e70420668494d5bb7119619413df25a66ec13b6c4ad6f410cca3a7`. Native source pins: hybridclr `99ed95d58c7d976e5fd05257a4fe735ce0ee3813`, package `9f5d288e36f60c35420878f5796798b2dfa34de7`, il2cpp_plus `5e9a1a93b530888fa41603e40c29e049a3914ea6`. Demo source is frozen in the commit containing this document, then recorded in a metadata-only child commit.

## Implemented changes

- Publish immutable startup candidate identities during native metadata startup, before managed startup; retain first use across Configure and fail closed on initialization retry. The physical registration boundary remains the documented observation limit.
- Promote reproducible native startup (168 checks, 15 ASan scenarios) and actual allocator/metadata-lock contention (545 checks) harnesses. The contention oracle checks a legal serial ordering and rejects a crossed allocation; it does not claim full concurrent Assembly.Load publication coverage.
- Correct ordinary snapshot raw/semantic hash binding and add eight self-contained Editor cases.
- Add a separate three-mode failure Player harness: five-member control, genuine metadata-init failure after Stage, and published initializer failure. Its negative input is one verified signature byte changed in a sidecar, preserving assembly identities; its initializer fixture uses the production compiler/builder and replay.
- Correct the native transaction runner's default installed-header root to this project. The failed stale-path invocation is retained; the corrected default passed 109 checks.

## Verification before executable build

- Actual Unity Editor suite: 289 passed, zero skipped. `_temp/AssemblyShadow/EditorTests-10429bc77ff9447a95b1387083a2ac3d/results.xml`.
- Native source regressions: M03 identity/name/facade/facade-lookup/OFF 94707/30/25/15/33 checks; M04 53 checks, 22 syntax checks and one million allocation-free lookups; M05 616 core, 2 OFF, 35 reflection and 219 identity assertions plus 34 syntax checks; M06 824 checks and 20 syntax checks. Receipts are `m03-native-early-1.json` through `m06-native-early-1.json` under `_temp/AssemblyShadow/R01`.
- These native receipts bind exact compiler input hashes. They precede installation of the final executable pairing and cannot prove that installation or its Player behavior.
- Initial complete Python run: 397 passed, zero skipped. After the verifier fix, the complete rerun passed 398 tests in 57.397 seconds, zero skipped: `_temp/AssemblyShadow/R01/python-tests-early-identity-fixed-1.log`.

## Bounded review finding and remediation

P2: the new failure verifier accepted native baseline/patch/closure/MVID fields from an unrelated transaction if raw hashes were rebound, despite the correct outer result. Fixed with phase-aware native identity checks in every main, observer and reentrant initializer snapshot, exact closure rows/counts, and admitted staged MVIDs. Before Configure the native IDs/closure must be empty; after Begin they must match the admitted patch. The synthetic producer now represents real un-staged closure rows and distinct manifest MVIDs. Rebound-hash tampering exercises each identity in every captured location across all three modes. Focused eight-test suite passed in `_temp/AssemblyShadow/R01/failure-identity-tests-1.log`; independent re-review returned PASS, with all three positive modes accepted and 97 independent rebound-hash identity mutations rejected in memory. This is a bounded prebuild verdict only.

## Still required

Reinstall final pins, regenerate native definitions, verify exact installation, build the new immutable ON/OFF pair, run the strict ten-mode early-guard matrix and the three real failure modes, complete affected M07/R00 regressions and evidence review. The failure modes have only synthetic wire-contract and compiler evidence so far. Production sizing remains NotProvided; no R01B applicability or Q06 production acceptance is inferred from the five-member demo.
