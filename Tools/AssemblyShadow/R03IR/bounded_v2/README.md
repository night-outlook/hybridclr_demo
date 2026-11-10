# Inactive native bounded diagnostics V2 component

This C++11/C++17 host-tested Capture/Encoder is **not** included by the current Unity Player. It implements the exact existing V2 binary wire format over two complete frozen UTF-8 fields; it is not a VM serializer, filesystem transaction, authenticity authority or semantic verifier.

`BoundedDiagnosticsV2.h` uses no dynamic allocation. Caller prepares Capture storage and a65536-byte frame scratch while healthy. Objects are noncopyable, single-owner and not thread-safe; buffers and field data must remain valid and unmodified for the whole operation. Sink callbacks consume bytes synchronously and must not retain scratch pointers. An encoder receipt means wire completion, not durability. Trustworthy identity/inline digests and the independently authenticated descriptor are caller responsibilities.

Physical frame payload <=65536, artifact <=3932160, inline/envelope reserve262144, pooled total4194304. Original V1 text-slot262144 and runtime behavior remain unchanged. Overflow, invalid UTF-8, duplicate/order/state, reentry, source/scratch alias, incomplete sink or changed input fail closed; no truncation or larger bound.

Run only host tests with fresh, distinct external output roots. C++17 is the original default; opt in to C++11 explicitly:

```sh
CXX=clang++ python3 -B Tools/AssemblyShadow/R03IR/bounded_v2/run_tests.py \
  --repository /absolute/path/to/hybridclr_demo \
  --output /absolute/unused/codec-cpp11 --cxx-standard c++11
CXX=clang++ python3 -B Tools/AssemblyShadow/R03IR/bounded_v2/run_transaction_tests.py \
  --repository /absolute/path/to/hybridclr_demo \
  --output /absolute/unused/posix-cpp11 --cxx-standard c++11
```

The test runner hashes the immutable Python reference before use. It executes20 tests per strict/sanitized profile and preserves commands, streams, synthetic inputs/outputs, sources and exact inventory. Compiler/OS source matrix: Linux Clang, Linux GCC, macOS Apple Clang. ASan/UBSan enabled; LeakSanitizer explicitly unavailable on the tested Apple runner, enabled on Linux. [C++11/17 compiler CI](../../../../.github/workflows/r03-ir-b2-compiler-compat-source.yml) and [full dual-OS host CI](../../../../.github/workflows/r03-ir-b2-host-cxx11-cxx17.yml) verify the source under both language modes: the latter ran 376 real host tests successfully on macOS and Ubuntu (20+20 codec and 27+27 POSIX tests per OS/standard). [RED→GREEN scope and remaining B2 source blockers](../../../../Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_CPP11_COMPATIBILITY_REMEDIATION.md). These are **host-only**; no Unity/official SDK V2 integration, real GC/scheduler or whole-VM epoch was tested.

[Primary reconciliation and remaining integration gates](../../../../Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/SNAP01_NATIVE_CODEC_c2e8/PRIMARY_RECONCILIATION.md). No Local runtime authorization is implied.
