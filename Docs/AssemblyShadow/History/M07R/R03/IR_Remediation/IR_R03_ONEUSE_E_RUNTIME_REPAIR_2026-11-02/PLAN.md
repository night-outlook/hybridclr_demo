# R03 oneuse-E remediation plan (current bounded cycle)

1. Preserve oneuse-E source, log, raw and seal evidence exactly; confirm E failed after 3 build PASS, 1/5 Player PASS and official parity Blocked. No E rerun.
2. Isolate field14 size failure from field15 semantics; implement complete bounded preopened sidecar and verify strict raw/sidecar identity, byte length/CRC, schema and negative conditions without truncation or raising size limits.
3. Implement one-shot native engine-owner quit request and strict result/log once evidence, retaining original 500ms/64 bound and full counter.
4. Exercise actual production native C++11 writer and engine callback through host mocks, run transport/verifier/negative tests, and run source/VM/parity/CLI and generator CI on both host OSs.
5. Independently inspect changed source/pins, repair failing host-positive fixtures without relaxing runtime validators, and update canonical README and WEB_TO_LOCAL. Commit/push and verify four latest remote HEADs.
6. Conditional Local cycle F: source-gated 45 VM files/135 pairs, no-write environment admission, exactly one ten-stage coordinator at an unused F root; 3 real builds, 5 Players, complete diagnostic sidecars, actual engine containment, original archive/process joins, sealed evidence and return to Primary.

Stop on any CI/host gate failure before allocating F. Any Player or source/semantic failure returns to Primary, not to self-approved runtime acceptance. R03Accepted=false and no H2/M08A/X02/Human Review Gate.
