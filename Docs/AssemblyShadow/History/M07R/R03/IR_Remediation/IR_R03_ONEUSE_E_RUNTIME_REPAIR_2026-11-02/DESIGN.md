# R03 oneuse-E runtime failure remediation — bounded candidate

## Empirical inputs

One E cycle only: 3 successful Unity2022.3.62f2 C++11 IL2CPP builds; 5 launched Players; OFF PASS; 3 ON empty raw.json / exit2 after a text-field-14 length lower-bound 262145 exceeded the unchanged 262144 bound; one engine case exited71 with an actual 51211 completed reports within500ms against max64. Official parity stage Blocked; independently compared 129 source-installed pairs matched. Evidence and source heads are in immutable oneuse-E checkpoint and RETURN_TO_WEB.

## Transport design

Retain original 262144 native report text-field limit and 3932160 maximum full-general field. For a fully materialized >262144 general diagnostic, write the complete **owned** field14 bytes into a distinct, preopened, exact-capacity sidecar before the report's end seal; record a bounded descriptor instead of truncated JSON. Verify canonical adjacent sidecar, exact byte length, CRC/hash, valid complete JSON, all required array fields and generation indicators on the host. Any missing, malformed, too-long, duplicate, aliasing, or corrupted byte path fails, never promotes Player output. Transport completeness is **not** coherent cross-VM epoch proof or runtime acceptance. Preserve field15 and all established post-poison semantics.

## Engine containment

For the actual native engine unhandled sentinel, attempt exactly one native Unity owner quit request through the runtime's internal call, not a managed callback. Record original native completed-report count honestly (max64 over500ms) and verify a matched sentinel/log witness and exact once flag; never cap, sleep, suppress, or relax terminal guards. Host contract mocks are not Player/Shutdown evidence. If owner exit is delayed or request unavailable, fail the real Player verifier and return evidence to Primary.

## Scope and checks

Current candidate is `il2cpp_plus@ecb9f010f84915b6fa0924dfd66174f812c52fc0` and the GitHub source gate declares 45 changed VM files (135 physical role pairs). Historical candidate pins and source archives remain immutable. Bounded host suites check actual C++11 native writer/one-shot owner callback, full general verifier and negative cases, original fresh Python runner and command-failure receipts. Local must still perform fresh official Unity three-build/five-Player evidence in a NEW oneuse-F root; do not reuse E or infer acceptance from CI. No new milestone or independent review acceptance.
