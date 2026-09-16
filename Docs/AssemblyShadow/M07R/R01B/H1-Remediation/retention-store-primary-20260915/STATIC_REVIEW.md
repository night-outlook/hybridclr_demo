# Primary static review — declared-input retention store

Scope: candidate demo changes from Local Validation return `425186b213313eb945571c01a2b060ae701e7bd8` through code anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe`.

## Finding closure

The returned blocker is reproduced by evidence, not inferred: the old attempt held 267,613,743 unique bytes and then rejected a 1,498,382-byte generated source because the fixed aggregate ceiling was 268,435,456 bytes. The file itself was below the unchanged 64 MiB per-file bound. Both replay and fresh smoke failed at `declared-input-retention`; later provenance phases were `NotRun`.

## Design review

PASS for return to Local Validation, subject to fresh empirical validation:

- **No source omission.** All graph-selected declared native source paths remain inventory observations; generated source storage is reversible, not hash-only.
- **Identity/storage separation.** Raw SHA-256 and raw length are authoritative. Stored SHA-256, stored length and encoding separately bind the physical representation.
- **Semantic evidence remains raw by default.** Request/DAG/PCH/header/response/plist evidence was not moved behind compression merely to save space.
- **Independent limits remain.** 64 MiB/file, 2 GiB logical unique bytes, 512 MiB physical store and 4096 observations each fail closed.
- **No data-dependent auto-resize.** Limits are fixed constants. Local Validation is prohibited from increasing them when a real input hits a limit.
- **Store is self-authenticating before success.** Finalization re-reads the JSONL inventory and every referenced store blob, verifies path confinement, raw/stored hashes, reversible decompression, logical/stored accounting and bounds.
- **Tampering fails closed.** Compressed member length/hash mismatch and corrupt finalization are tested.
- **No provenance-domain relaxation.** Exact Apple Bee source ownership, compiler/SDK, feature/count definitions, linkage and PCH/probe contracts are unchanged.
- **Historical evidence is immutable.** No old attempt or archive is rewritten or relabeled.

## Bounded validation

GitHub Actions run `35050737320` passed 256/256 with zero nonpasses at `91ebef56eaa7034ed49a80bced422ea4c067d2fe`. The new volume fixture has the relevant 446 compile-action shape (444 object sources + 2 PCH producers) and retains more than 256 MiB of distinct logical source bytes while remaining within the physical store bound.

Negative coverage includes:

1. logical-volume bound exhaustion → `FailedNotAccepted`, no provenance receipt;
2. physical-store bound exhaustion → `FailedNotAccepted`, no provenance receipt;
3. compressed member tamper → verifier rejection;
4. corrupt store before finish → successful finalization refused;
5. incompressible source → raw fallback with identical source SHA/length.

## Residual risks / required Local evidence

- The complete real Apple source corpus size/compressibility is still unknown because the returned real attempts stopped at 267.6 MiB and Primary CI does not possess all generated local source bytes.
- Actual macOS Python/zlib filesystem behavior and capture cost require Local execution.
- Actual replay must demonstrate that the repaired journal advances into planning and, where inputs remain available, the established 446/444/430/2/14 domain and PCH/probe contracts.
- A new source anchor invalidates automatic promotion of previous Player receipts; V03 needs fresh provenance-bound builds or explicit supported equivalence/reuse only.
- Store integrity is supporting evidence only. It does not prove which Player executed and is not M08.

Any real hit of the 2 GiB logical, 512 MiB physical, 64 MiB per-file or 4096 observation limit is a Primary design return, not a Local tuning task.

H1 remains blocked pending fresh V00–V05. R02 is prohibited.
