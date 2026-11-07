# Initializer oneuse-07 — PASS

**Focused initializer PASS.** 15 Passed across one 15-cell batch.

Unity 2022.3.62f2 macOS arm64 IL2CPP BuildPipeline reported Succeeded with 0 errors and 1 warning(s). The build receipt SHA-256 is `553af2f5cd35a08da543e2b6b2d68ac89a5a7e98d63b7fb840ce2e64dfd60a05`.

The generated Cdecl int32() wrapper and table contained exactly one `Bi4` row and a null terminator. The source hash after augmentation and after BuildPipeline was `c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da`. The helper checks its pre-augmentation source internally. The BuildReceipt records the two post-augmentation hashes. GameAssembly SHA-256 `416eedc304a5f0429bcd67710a4ed86203eadf1e2e611e37b6b197758a23dd68` binds both native exports and the linked Bi4 identity. The isolated project kept its empty hot-update assembly list.

| Player | PID | Exit | Bi4 phase 103 | Callback 299/300 | Commit / state | Field / mask |
| --- | ---: | ---: | --- | --- | --- | --- |
| initializer-control | 35820 | 0 | 1 | 1 / 1 | 0 / 6 | 3 / 15 |
| initializer-failure | 35842 | 0 | 1 | 1 / 1 | 19 / 9 | 3 / 15 |

Both distinct Players observed the real linked Bi4 entry before Commit and entered and completed the native callback exactly once. The pinned field remained 3 and the positive mask was 15. Control committed successfully at state 6 and had empty recovery reason. Commit returned 19 and entered FailedAfterCommit state 9 after the callback, with the exact post-preparation recovery sentinel `R03IR.InitializerFailure.AfterPublication.V1`. The AOT canary remained 1→1 and the failure Player recorded an attempted post-terminal AOT call that failed without changing the canary. Both strict V1 verifications passed within the initializer scope.

The native host audit covered 10 components and 56 initializer tests. Host custody recorded 3198 regular files and 4 literal symlinks. The original product seal was Passed with 456 members.

WEB_TO_LOCAL refers to a historical oneuse-06 RUNTIME_FINDINGS.json filename. Its published findings are in local-evidence/FINDING.md and BRIDGE_FINDING.json. Those files and the preserved historical raw inventory supplied the prior-cycle record.

Return to Primary Implementation with all acceptance flags false.

The execution source, command receipts, CI, original Player bytes, fixture targets and custody audits are bound in the checkpoint manifest. Concatenate the sealed archive parts in transport order and verify the original archive SHA-256. The original product and host roots retain the raw payloads identified by the complete inventories. Files ending in .utf8.json carry exact original bytes in their UTF-8 text field.

The separate publication receipt records the closing pushed commit and verified remote heads.

- [Local result](LOCAL_RESULT.json)
- [Independent audit](local-evidence/FINAL_INDEPENDENT_AUDIT.json)
