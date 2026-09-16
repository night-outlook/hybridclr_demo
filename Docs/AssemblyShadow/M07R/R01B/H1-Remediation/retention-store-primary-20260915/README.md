# H1 Primary retention-store successor

Primary Implementation successor for Local Validation return commit `425186b213313eb945571c01a2b060ae701e7bd8`.

## Code anchor

- candidate demo / implementation: `91ebef56eaa7034ed49a80bced422ea4c067d2fe`
- returned local failure: 337 observations / 267,613,743 unique raw bytes before the old 256 MiB aggregate ceiling
- previous source anchor: `b6db7c2fb2fce364d49458b7dfc78886fd430004`

## Repair

Declared native source identity remains the original raw SHA-256 and length. Large generated C/C++/ObjC source content is stored reversibly as content-addressed `zlib-v1` only when smaller; otherwise it remains `raw-v1`. Request/DAG/PCH/header/response/plist semantic evidence remains raw by default.

Independent fail-closed limits are 64 MiB/file, 2 GiB logical unique raw bytes, 512 MiB physical store, and 4096 observations. Successful attempts re-read and authenticate the store before finalization. `h1_verify_capture_store.py` provides an independent store-integrity result and is explicitly not build/M08 acceptance.

No Apple Bee macro-domain/source allowlist, compiler/PCH proof, witness rule, count behavior, native code, reproduction defect, or performance-reference profile changed.

## Primary bounded validation

GitHub Actions run `35050737320` at code anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe` authenticated the existing Apple failure graph and ran the Primary suite:

- 256 / 256 passed
- 0 nonpasses
- authenticated graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID `10428726815`
- artifact ZIP SHA-256 `227effe44e29080b0191252b19ca15569b801d4e3d20ad36aca52d397c836015`

The added volume fixture retains more than the old 256 MiB logical limit with a 446-compile-action-shaped graph and tests logical/stored limit exhaustion, compressed-store tampering, corrupt finalization, and raw fallback.

This does **not** prove the complete real Apple generated-source set fits the new envelope, nor Unity/Player/runtime/M08 acceptance. Fresh V00–V05 remain required.

## Read next

1. `STATIC_REVIEW.md`
2. `LOCAL_VALIDATION_TASKS.md`
3. `Documents/AgentHandoff/WEB_TO_LOCAL.md`

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.
