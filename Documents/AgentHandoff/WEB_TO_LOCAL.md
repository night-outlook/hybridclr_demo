# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the declared-input retention repair. The new candidate demo source/implementation anchor is `91ebef56eaa7034ed49a80bced422ea4c067d2fe` on `night-outlook/hybridclr_demo` branch `codex/assembly-shadow-r01b-h1`.

Local Validation commit `425186b213313eb945571c01a2b060ae701e7bd8` established that the previous source anchor passed V00 and V01, then both retained replay and a fresh candidate ON/Debug Player build stopped during `declared-input-retention` after retaining 337 observations / 267,613,743 unique bytes. The next legitimate generated source would exceed the old fixed 256 MiB aggregate bound. Planning, PCH replay and macro probes were `NotRun`; the Player itself built; exact restoration passed; no accepted provenance/build receipt exists.

This Primary successor fixes that storage design without skipping any declared source, broadening Apple Bee source/macro domains, relaxing compiler/PCH checks, changing native count behavior, or rewriting historical evidence. Run fresh V00–V05. H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-22eda8b/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/retention-store-primary-20260915/`

Git is the sole handoff authority. Preserve all prior attempts and evidence. Do not apply chat ZIPs or unpublished patches.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate demo source / implementation anchor | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `91ebef56eaa7034ed49a80bced422ea4c067d2fe` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Reproduction demo published head — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction demo code anchor | same branch | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Unfixed reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. `ProjectSettings/AssemblyShadowSourcePins.json` pins candidate demo revision `91ebef56eaa7034ed49a80bced422ea4c067d2fe`. The fetched candidate branch HEAD is a later metadata-only handoff successor; record both checkout HEAD and source anchor. New auxiliary validation checkpoints/raw evidence belong under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`, not a new `Documents/AgentHandoff/local-validation-*` directory.

## Implementation

### Root cause and retention contract

The previous capture journal used one 256 MiB ceiling for the raw unique bytes of all declared native inputs. The real 446-action Apple graph deterministically exceeded it before planning. The repair **does not simply drop sources or make the old budget unbounded**. It separates source identity from its physical evidence representation:

- raw content identity is always the original **SHA-256 + raw byte length**;
- every selected declared native source remains represented in the inventory and recoverable byte-for-byte;
- generated `.c/.cc/.cpp/.cxx/.m/.mm` source blobs use content-addressed `zlib-v1` storage only when compression is smaller; otherwise they remain `raw-v1`;
- request, selected DAG, PCH, headers, response files and plist/config semantic evidence remain raw by default;
- content de-duplicates by raw SHA while preserving every source/role observation;
- compressed rows bind raw SHA/length **and** stored SHA/length/encoding;
- decompression is output-bounded and must reproduce the exact raw length/SHA;
- a successful attempt independently re-reads and authenticates its inventory/store before finalization.

Four independent limits remain fail-closed:

| Bound | Value |
| --- | ---: |
| Per retained file | 64 MiB |
| Logical unique raw content | 2 GiB |
| Physical retained store | 512 MiB |
| Inventory observations | 4096 |

The 2 GiB logical bound is an explicit bounded envelope above the measured 267,613,743-byte partial real attempt; it is not derived dynamically from whatever graph happens to run. The physical store has its own independent 512 MiB ceiling. Exceeding **either** bound is `FailedNotAccepted`; no provenance receipt is published.

`Tools/AssemblyShadow/h1_verify_capture_store.py` independently authenticates one attempt store and reports `StoreVerifiedNotAcceptance`. It verifies reversible bytes and accounting only; it does not replace compiler/PCH provenance, a build receipt, M08, or human approval.

### Provenance semantics retained

The reviewed Apple Bee contract remains unchanged: exact source-owned `il2cpp-runtime` / `external-bdwgc` / `external-zlib` domains, exact Shadow/count definitions on every selected compile action, compiler/SDK identity, object/link coverage, fail-closed unknown external sources, PCH producer/consumer binding, byte-identical PCH replay, per-context compiler probes, and `NDEBUG` definedness semantics. No source-domain allowlist was broadened.

Historical plan-stage failure retention remains intact: the attempt root exists before planning; reached inputs/stages are preserved; unreached replay/probes stay `NotRun`; failed attempts cannot produce accepted receipts.

### Primary review and bounded tests

Primary CI workflow run **35050737320** at source anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe` authenticated the existing Apple failure graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181` and passed **256/256** tests with zero nonpasses. The suite includes the previous Apple Bee/domain/provenance regressions plus a 446-action-shaped fixture retaining more than the old 256 MiB logical limit, logical/stored-limit failures, compressed-store tamper rejection, corrupt-finalization rejection, and incompressible raw fallback.

CI artifact ID `10428726815`, ZIP SHA-256 `227effe44e29080b0191252b19ca15569b801d4e3d20ad36aca52d397c836015`. This is bounded Primary/tooling evidence, **not** macOS Unity/Apple Player/runtime or M08 acceptance.

## Local validation

Run fresh **V00–V05**. Previous successful facts remain historical evidence but do not substitute for affected validation of the new code anchor.

### V00 — authoritative preflight

1. Explicitly `git pull --ff-only origin codex/assembly-shadow-r01b-h1` in candidate.
2. Record branch, origin, checkout HEAD and dirty/untracked state without reset/clean/stash-away of unrelated evidence.
3. Confirm `source-targets.json` and source pins both identify candidate anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe` and all protected identities above.
4. Run into a new absolute path:

```sh
python3 Tools/AssemblyShadow/h1_handoff_preflight.py \
  --project /ABS/CANDIDATE/hybridclr_demo \
  --role candidate \
  --output /ABS/NEW/v00/candidate-handoff.json
```

Expected: exit 0, `SourceTargetVerifiedNotBuildAccepted`, code commit `91ebef56eaa7034ed49a80bced422ea4c067d2fe`, gate flags false. If V00 fails, stop and return evidence before V01–V05.

### V01 — affected source/tool/Unity regression

Run the full H1 Python inventory and exact Bee Primary suite, especially `test_h1_capture_attempt`, `test_h1_capture_volume`, native-capture/PCH/provenance, handoff, collector/successor, and normal M02-owner tests. Compile candidate and reproduction in Unity and rerun focused H1 Editor tests plus affected Assembly Shadow regression suites. Preserve exact IDs, Python version, logs, XML, failures and skips.

The Linux CI 256/256 result is supporting evidence only. Reproduction's previously observed optional full-sweep missing-baseline/fixture failures remain historical facts; do not relabel them.

### V02 — real Apple replay, retention volume and fail-closed controls

First use the exact retained Apple failure inputs from `local-validation-20260915-22eda8b` if those bound source locators/bytes still exist. Otherwise record them `Unavailable` and use a new fresh smoke input; do not rewrite old locators.

For an executable replay/new capture, require:

1. declared-input retention progresses past the previous 267,613,743-byte / 256 MiB boundary rather than failing there;
2. every selected declared source observation is retained or an actual missing input is explicitly recorded — no silent source omission;
3. state records `declaredInputPathCount`, nominal volume, logical unique bytes, physical stored bytes and all four limits;
4. run the independent store verifier on the completed attempt root:

```sh
python3 Tools/AssemblyShadow/h1_verify_capture_store.py \
  --attempt-root /ABS/ATTEMPT \
  --output /ABS/NEW/retention-store-verification.json
```

Expected: `StoreVerifiedNotAcceptance`; inventory/store accounting matches and all compressed/raw members recover their declared original SHA/length.

If replay reaches planning, continue to require the established real graph/domain result: 446 compile actions, 444 linked objects, 430 runtime / 2 BDWGC / 14 zlib, six probe contexts, complete selected-link coverage, and appropriate Debug/Release runtime profile. If it reaches PCH execution, require the existing exact PCH replay/probe contract; do not downgrade missing later stages to a retention PASS.

Also run the new fail-closed regression controls: logical limit, physical stored limit, compressed blob tamper, corrupt store at finalization, and incompressible raw fallback. A bound/tamper failure must remain `FailedNotAccepted` and must not publish `h1-compiler-provenance.json`.

**Do not locally raise 2 GiB / 512 MiB / 64 MiB / 4096.** If a real graph reaches any of those bounds, return the complete census, state, inventory and failing file/store metrics to Primary. Do not skip files, switch compression codecs, or externalize bytes ad hoc.

### V03 — fresh provenance-bound Player builds

Reinstall candidate from the new source pins and rerun normal installed-runtime verification with demo-source verification enabled. Execute a new candidate ON/Debug smoke first. Acceptance requires:

- Player build success;
- complete native compiler provenance;
- complete declared-input retention and independent store-verifier result;
- Apple macro-domain and compiler/PCH probes;
- managed-source provenance;
- final build receipt and strict single-build verifier PASS;
- exact generated/project restoration.

Record logical/stored retention bytes, observation/content/blob counts and retention policy for the fresh smoke. After a valid smoke, run the other candidate ON/OFF × Debug/Release builds and unfixed reproduction ON Debug/Release in fresh immutable roots. Explicit same-source smoke reuse is permitted only through the already committed supported route after revalidation; never choose a result by recency.

Any new Apple grammar/source-membership/PCH/provenance ambiguity or real retention-bound exhaustion returns to Primary; Local must not alter acceptance semantics.

### V04 — runtime/count/startup/capacity/performance chain

After the six provenance-bound build set exists, run the established current R01B chain: 132 candidate count cells; 8 unfixed reproduction cells; fresh baseline/fixtures/replay and 11 startup modes; ordinary/mixed 8192 lifetime capacity and 8193 rejection; retained failures; >=25% usable encoded-page free capacity; 32 MiB maximum DLL and 512 MiB valid input boundary; lazy/dense/generic/array/reflection/FieldRVA/old-Player and affected M03–M07 checks.

Run controlled Development performance pairs only against the separate performance-reference checkout on workloads supported by both sides. Do not infer Release/P99/device-RAM acceptance.

### V05 — successor package and independent whole-chain M08

Construct the successor evidence archive/index from explicit source/build/raw locations. Include required compiler/PCH/domain/store-verification/runtime evidence and preserve every unavailable/excluded disposition accurately. Authenticate archive/index bytes, membership and references; run the strict semantic verifiers; then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

A tooling/store/CI PASS is not M08 PASS. Only a genuine independent whole-chain M08 PASS can make the package Ready for Human Review Gate. Then stop for explicit human H1 approval.

Commit new auxiliary checkpoint/raw evidence under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`. Update/push Local-owned `LOCAL_VALIDATION.md`; place nontrivial issues in `RETURN_TO_WEB.md`.

## Failure evidence

For any failure retain the exact repository/branch/checkout HEAD/source anchor/pin bytes, command/cwd/exit/timeout/stdout/stderr, Unity log/XML, selected Bee graph, declared-input census/inventory/state, retention policy and four limits, logical/stored byte counts, failing raw/stored member identity, store-verifier output, response closure, compiler/SDK identity, original/rebuilt PCHs, module-file-info/header bytes, probe source/argv/macro output for reached contexts, native/managed artifact identities, build/preparation/restore state and attempt failure JSON.

For compressed source rows preserve both raw (`bytes`, `sha256`) and stored (`retainedBytes`, `retainedSha256`, `retainedEncoding`) identities. Do not report compression success as source equivalence unless decompression reproduces the raw SHA/length through the committed verifier.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Preserve the 22eda8b retention failures and all earlier v6–v11/c0d3070 evidence unchanged.

## Alternatives

The selected production design is reversible content-addressed compression for large generated native sources plus independent logical/physical bounds. This is a storage representation change, not a provenance-domain relaxation.

Do not substitute hash-only source records, omit generated source bytes, disable PCH/PDB, ignore compiler failures, expand source-domain allowlists, repoint reproduction to fixed native code, alter the performance reference, or raise retention limits locally. If actual Apple data shows the selected envelope or codec cannot satisfy the reviewed contract, return the complete evidence to Primary for a new design/anchor.

Diagnostic replay remains investigation-only and cannot satisfy fresh-build acceptance. Explicit same-source smoke reuse remains an optional documented optimization, not fallback acceptance.

## Risks

The real Apple generated-source corpus may be larger or less compressible in another build/configuration. That is why logical raw volume and physical stored volume are separately bounded and observable. The current local failure only measured a 267.6 MiB partial raw set; **Primary has not yet demonstrated the complete real corpus under the new 2 GiB/512 MiB envelope.** V02/V03 must establish that empirically.

Compression adds capture CPU/I/O and changes diagnostic storage format. It must not alter raw source identity; independent store verification and tamper tests guard that boundary. Semantic PCH/header/response/config evidence remains raw by default.

The candidate code anchor changed, so affected old build receipts cannot automatically be promoted to this source chain. Historical results remain evidence about previous anchors only unless explicit equivalence rules legitimately apply.

## Local correction boundary

Local Validation may correct machine-specific paths, executable permissions, invocation syntax, new output-directory choices, isolated test harness setup, and previously documented exact generated-file restoration after preserving before/after bytes.

Local Validation must not modify retention bounds/codec/storage semantics, source-domain membership, compiler/PCH provenance rules, witness allowlists, source identity exclusions, count behavior, ABI/architecture, performance methodology, or other cross-module design. These are Primary Implementation changes regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md`. Preserve/append empirical facts in Local-owned reports.

## Human review gate

Current project gate remains H1 as defined by the committed project review documents. State is `InProgress`, technically blocked pending fresh V00–V05; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Only after implementation plus actual Local Validation satisfy the gate definition and a genuine independent whole-chain M08 returns PASS may the package be marked **Ready for Human Review Gate**. Then stop for explicit human H1 approval. Neither agent grants H1. Do not begin R02 before that approval is recorded.
