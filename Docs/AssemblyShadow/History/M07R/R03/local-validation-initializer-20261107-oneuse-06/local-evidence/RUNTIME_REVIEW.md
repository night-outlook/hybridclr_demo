# Independent scoped runtime evidence review

Reviewer storage_scope_review_gpt61sol_high_1 confirmed both live recovery/request/fixture joins for PIDs 30595 and 30603, exit 2 and zero-byte strict outputs. Both lack callback phases 299 and 300. The actual build receipt binds the exact live generated MethodBridge.cpp, whose managed-to-native function-pointer table contains only the null sentinel. The required Bi4 signature is derived from pinned Cdecl and Int32 rules. TransformContext resolves the P/Invoke and checks its address before bridge lookup. The bridge fallback raises the exact observed exception.

The named-symbol path is inferred from the source and observed exception. The receipt proves installed generated source and the static export scan proves the callback symbol exists. The linked-image bridge table was not independently inspected. The runtime batch remains FAIL with 13 Passed and 2 Failed cells.
