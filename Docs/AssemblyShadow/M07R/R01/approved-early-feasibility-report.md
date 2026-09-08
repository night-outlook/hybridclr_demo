# Approved early-activation feasibility

The user-authorized experiment passed its bounded native feasibility check. R01 is still active and unaccepted. This report appends to the preserved early-v1 startup-blocker evidence; it does not replace or reinterpret that failed late-startup run.

The owned Player process 87891 was paused immediately after successful `Runtime::Init`, at `il2cpp_init+0x28`, outside the initialization lock. A compiled bridge using exact installed native headers invoked the actual Configure, Begin, Reserve, five Stage calls, Validate and Commit APIs. All returned Success. The resulting world was Committed at generation 1 with no baseline uses.

Unity startup then resumed. All 22 candidate lookups in the serialized MonoScript catalog returned active Shadow classes, in the previously captured catalog order. At the stable M07 runner Awake boundary the world remained Committed, generation 1, with no baseline uses. The root deliberately killed this owned diagnostic process there, before the older runner could issue a second Configure. This was not a full resource run or natural successful Player exit.

The exact Player is `M07-Baseline-R01-early-v1`, GameAssembly UUID `F23C9CDA-E8BB-46A3-B10B-C9BA7F996593`, SHA-256 `c6c3640a43d66d62c21e1f4e5fb00d81c2152b1dbcaced57e961c88edacdc361`. The retained-input audit binds 16,840 immutable artifacts. Current-source acceptance preflight correctly rejected pending source changes; no skip override was used.

`approved-early-feasibility-evidence.json` records 49 debugger events, 14 bridge events, exact member hashes and a verified 19-member archive. Independent bounded source/evidence review passed this feasibility claim only. Executable-specific offsets, debugger invocation, implicit LLDB restoration during lookup queries, and the deliberate stop limit its scope.

## Source integration and remaining work

The resulting implementation is a generated opt-in native startup entry after full runtime readiness. The entry must preserve exact physical bootstrap identity, once-only semantics, sticky reentry/concurrent failure and explicit callback refusal. A pure-BCL managed capsule reader performs the hash-bound transaction before Unity catalog admission. An M07 handoff imports actual early observations and then executes the existing resource checks.

Fresh Editor/native tests, source review corrections, coherent four-repository pins and installation, a new ON/OFF Player pair, successful resource matrices, ordinary-loader contention, actual metadata/initializer failures and remaining R01 acceptance evidence are required. The new source gateway is not accepted merely because the debugger bridge worked.

The user requirement of up to 64k assemblies is conservatively recorded as 65,536. It makes R01B mandatory after R01. H1 remains unpassed; stop for human review after R01/R01B and do not enter R02 automatically.
