# H1 Local Validation — MethodPtr and dense replacement

This checkpoint records Local Validation of Primary implementation anchor `8b1298d6a5979928bdfa30446e2d674d63999b76` at candidate handoff HEAD `7e91c42d7baf1d9045d3fd924b7ad2d176f599e9`.

Focused M05 tests, the retained real Unity `#-` Bootstrap pointer proof, deterministic dense-v2 generation, and the native full/dense/bounded parser suite passed. The candidate source preflight failed because the committed source anchor remains `68df00fe31a199491b313cc17f25575663b7452b`; fresh Unity and provenance-bound V04 therefore did not run. Capsule/startup11 is `Unavailable` because consolidation removed the required fixture/build/replay receipts.

`raw-evidence.tar.gz` contains both preflight results, test logs, Bootstrap permutation and method-witness proofs, dense-v2 manifest and DLLs, the initial missing-corpus parser failure, and the successful native receipt/log. The incomplete packaging attempt was retained outside the committed package.

Historical dense-v1 remains `UnavailableDoNotRelabel`. H1 remains in progress, M08 remains FAIL, and R02 remains closed.
