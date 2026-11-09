# Captured-generic oneuse-09 — PASS

**Focused captured-generic PASS.** One invocation produced 19 Passed across the fixed 19-cell roster. There were 1 Unity build commands and 3 actual Player launches.

Unity 2022.3.62f2 macOS arm64 IL2CPP ON/diagnostics2/Release BuildPipeline reported Succeeded with 0 errors and 1 BuildReport warning(s). Build receipt SHA-256 is `671644a8b110684389fe07c00e6052559b5151d2ed876364824d1bb66ac3b345`.

The generated Cdecl int32() wrapper and table contained exactly one `Bi4` row and its null terminator. The generated source hashes after augmentation and after BuildPipeline matched `c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da`. The actual GameAssembly SHA-256 `1a7b6a25125c79478b6019a859498fbed6d412cd8d05bc03aed4d081e77882c4` binds the Bi4 identity and all six initializer and captured-generic exports.

Two fresh same-host fixture generations matched for captured Methods.dll at SHA-256 `c7e4ddd3da14207ad680e9c0f60458f967661202a9cbf6a383ba06289ec11aab`, MVID `d8f7bafb-421a-2979-4e5a-1b290117a32a`, 2560 bytes.

| Player | Cell | PID | Exit | Strict raw bytes |
| --- | --- | ---: | ---: | ---: |
| initializer-control | Passed | 52095 | 0 | 752 |
| initializer-failure | Passed | 52113 | 0 | 752 |
| captured-generic | Passed | 52122 | 0 | 1273 |

Both fresh initializer traces record linked Bi4 phase 103 result 1 before Commit and one native callback at phases 299/300. The physical field was 3 and mask 15. Control returned Commit/state 0/6 with an empty reason. The failure returned 19/9 after the callback and retained the exact R03IR.InitializerFailure.AfterPublication.V1 sentinel. The post-terminal AOT attempt did not succeed and the canary remained 1→1.

The captured-generic Player joined the physical original Methods.R03.Node type handle to its inflated Assembly-CSharp AOT method owner. It recorded state 6 after inflation and a native guard denial that produced FailedAfterCommit state 9 and first error 15. Its exact native reason was `ShadowCapturedBaselineType Assembly=Assembly-CSharp Type=AssemblyShadow.R03.IR.R03CapturedGenericAotOwner Method=Touch Site=R03IR:PhysicalCapturedAotOwner CapturedArgumentAssembly=Methods Context=method_inst TypePath=/arg[0] Reason=CapturedBaselineType`. The actual post-terminal Runtime::Invoke reported an exception and the native counter remained 1→1.

The host audit recorded 10 native host components. Host custody recorded 3198 regular files and 4 literal symlinks. The product seal was Passed with 509 members.

Return to Primary Implementation with all acceptance flags false. The old oneuse-08 prerequisite result remains PrerequisiteBlocked/NotRun.

The execution source, command receipts, CI, original Player bytes, fixture targets and custody audits are bound in the checkpoint manifest. Concatenate the sealed archive parts in transport order and verify the original archive SHA-256. The original product and host roots retain the raw payloads identified by the complete inventories. Files ending in .utf8.json carry exact original bytes in their UTF-8 text field.

The separate publication receipt records the closing pushed commit and verified remote heads.

- [Local result](LOCAL_RESULT.json)
- [Independent audit](local-evidence/FINAL_INDEPENDENT_AUDIT.json)
