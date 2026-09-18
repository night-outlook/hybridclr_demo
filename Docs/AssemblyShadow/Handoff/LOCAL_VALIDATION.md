# Local Validation report

## Current run — 2026-09-17 MethodPtr and dense replacement validation

### Exit

**Local Validation → Primary Implementation**

Validation ran from 2026-09-18T05:44:55Z through 2026-09-18T05:54:03Z in `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`. The candidate checkout was clean at `7e91c42d7baf1d9045d3fd924b7ad2d176f599e9` on `codex/assembly-shadow-r01b-h1`; implementation anchor `8b1298d6a5979928bdfa30446e2d674d63999b76` is an ancestor. Native, package, and IL2CPP checkouts remained clean at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `6be7f38bec2fa4677d24efc1a4a1294240789933`. Protected reproduction, reproduction-tooling, and performance-reference remote heads remained exact.

The split reproduction-tooling preflight passed at `ba8fee33753a5ebc215b7a98739e343d8e05572e`. Candidate `h1_handoff_preflight.py` failed closed with `Demo HEAD contains build-input changes after the source pin`: the committed demo pin remains `68df00fe31a199491b313cc17f25575663b7452b`, while the MethodPtr and dense implementation changes are later build inputs. No fresh Unity, Player, or provenance-bound V04 work was run after this failure.

Independent focused validation remained meaningful and completed:

- focused M05 Python inventory: 113 passed, one explicitly skipped because real compiler/config paths were not supplied;
- retained Unity 2022.3.62f2 Bootstrap DLL `a937e18b...` verified as `#-`, 469 TypeDef, 1,675 MethodPtr, and 1,675 MethodDef rows;
- all 1,675 MethodPtr rows form a complete one-to-one permutation; the five raw method witnesses resolve through logical-to-physical indirection and match the configured Development hashes;
- compiled and linked raw-admission verification passed against the retained M07 baseline inputs;
- deterministic dense v2 generation passed two fresh byte-identical runs, producing two exact 1 MiB assemblies with 4,098 TypeDef rows, 4,097 MethodDef rows, and strings heaps above 64 KiB;
- the restored 8,192-file corpus matched its sealed manifest with 536,870,912 total bytes;
- native parser validation passed `raw_image_checks=8192`, dense `2/2`, all 13 bounded-reader cases, ASan/UBSan cleanliness, and source/dependency stability.

Capsule generation and startup11 are `Unavailable`, not failed: consolidation removed the required current fixture, ON/OFF build, and replay receipts. The retained Bootstrap image and baseline snapshot were sufficient for the focused verifier proof, but not for a provenance-bound Player launch. Historical sealed dense-v1 evidence remains `UnavailableDoNotRelabel`; the new dense-v2 results are a distinct evidence identity.

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| Git and remote pins | `Passed` | Four candidate repositories and protected remote refs match the handoff. |
| Candidate source preflight | `Failed` | Current build inputs differ from source pin `68df00fe...`; fresh Unity/V04 stopped. |
| Reproduction-tooling preflight | `Passed` | Exact behavior/tooling split authenticated at `ba8fee33...`. |
| Focused M05 tests | `Passed` | 113 passed; one explicit real-compiler-path test skipped. |
| Retained Bootstrap pointer proof | `PassedFocused` | Complete 1,675-row MethodPtr permutation and five real method witnesses verified. |
| Capsule/startup11 | `Unavailable` | Required fixture/build/replay receipts were removed during consolidation. |
| Dense v2 generation | `Passed` | Fresh hashes `738d20e0...` and `430d8ce0...`; historical dense-v1 not reused. |
| Native full/dense/bounds parser | `Passed` | 8,192 full corpus, dense 2/2, 13/13 bounded cases, sanitizer clean, provenance stable. |
| V04 downstream / V05 / M08 | `NotRun` | Blocked by candidate source authority and missing current launch receipts. |

Portable evidence is under [local-validation-20260917-methodptr-dense](../History/M07R/H1/local-validation-20260917-methodptr-dense/README.md). The prior M07 recovery checkpoint remains unchanged under its original identity. Actionable issues are in [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`; R02 was not started.
