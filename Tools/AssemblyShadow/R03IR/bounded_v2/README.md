# Inactive native bounded diagnostics V2 component

This C++17 Capture/Encoder is not included by the current Unity Player. It implements the exact existing V2 binary wire format over two complete frozen UTF-8 fields; it is not a VM serializer, filesystem transaction, authenticity authority or semantic verifier.

`BoundedDiagnosticsV2.h` uses no dynamic allocation. Caller prepares Capture storage and a65536-byte frame scratch while healthy. Objects are noncopyable, single-owner and not thread-safe; buffers and field data must remain valid and unmodified for the whole operation. Sink callbacks consume bytes synchronously and must not retain scratch pointers. An encoder receipt means wire completion, not durability. Trustworthy identity/inline digests and the independently authenticated descriptor are caller responsibilities.

Physical frame payload <=65536, artifact <=3932160, inline/envelope reserve262144, pooled total4194304. Original V1 text-slot262144 and runtime behavior remain unchanged. Overflow, invalid UTF-8, duplicate/order/state, reentry, source/scratch alias, incomplete sink or changed input fail closed; no truncation or larger bound.

Run only host tests with a fresh external output:

```sh
CXX=clang++ python3 -B Tools/AssemblyShadow/R03IR/bounded_v2/run_tests.py \
  --repository /absolute/path/to/hybridclr_demo --output /absolute/unused/output
```

The test runner hashes the immutable Python reference before use. It executes20 tests per strict/sanitized profile and preserves commands, streams, synthetic inputs/outputs, sources and exact inventory. Compiler/OS source matrix: Linux Clang, Linux GCC, macOS Apple Clang. ASan/UBSan enabled; LeakSanitizer explicitly unavailable on the tested Apple runner, enabled on Linux. No Unity or real GC/scheduler runs.

[Primary reconciliation and remaining integration gates](../../../../Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_NATIVE_CODEC_c2e8/PRIMARY_RECONCILIATION.md). No Local runtime authorization is implied.
