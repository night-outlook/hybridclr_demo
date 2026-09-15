# Primary Implementation → Local Validation

## Objective

Resume R01B H1 local validation from the reviewed Apple Bee provenance correction. The new candidate code anchor is `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` on `night-outlook/hybridclr_demo` branch `codex/assembly-shadow-r01b-h1`. **Run V01–V05 again from this anchor and its metadata-only handoff successor. H1 remains InProgress / technically Blocked; the last independent whole-chain M08 is FAIL; humanGatePassed=false; mayEnterR02=false. Do not begin R02.**

Git is the sole authority. Do not apply earlier chat ZIPs or unpublished patches. Primary owns this file and nontrivial implementation. Local Validation owns `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`; preserve their existing empirical records and append/supersede only with fresh facts.

The authoritative return input is candidate commit `33543dd39efec42a9480ea976ae3a3684dcd5ffd`: read `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, and `local-validation-20260914-bec2bd1/README.md`. V00/V01 there are reliable historical facts for the prior anchor; the fresh ON/Debug Player build succeeded but provenance failed before a receipt because the old implementation incorrectly required one global IL2CPP debug/assertion state across all 446 Apple Bee compile actions. V02/V03 failure evidence remains historical and must not be relabeled as acceptance.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact source identity |
| --- | --- | --- |
| Candidate demo code anchor | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Reproduction demo published head — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction demo code anchor | same branch | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Unfixed reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. `ProjectSettings/AssemblyShadowSourcePins.json` on candidate pins the code anchor, not this metadata-only handoff commit. Resolve the actual handoff commit from the fetched branch and record both checkout HEAD and code anchor. Any later executable/build-input change requires a new Primary-reviewed anchor.

## Primary correction

### Apple Bee macro domains

The authenticated failure fixture proves the 16/430 split was real and source-owned, not a reason to weaken provenance:

- `external-bdwgc`: exactly 2 reviewed direct-C sources: `external/bdwgc/extra/gc.c` and `extra/krait_signal_handler.c`;
- `external-zlib`: exactly 14 reviewed zlib C sources: `adler32`, `crc32`, `deflate`, `gzclose`, `gzlib`, `gzread`, `gzwrite`, `infback`, `inffast`, `inflate`, `inftrees`, `trees`, `uncompr`, `zutil`;
- `il2cpp-runtime`: every other selected native compile action, including both PCH producers, brotli C and generated C/C++.

Domain selection is based on exact canonical source ownership. **Observed macro values, action counts, node indices, display names and “is C” are not selectors.** An unknown external source, external PCH use, compiler/SDK drift, nonempty compiler environment, unlinked object, missing link input/argv object, or ambiguous output fails closed.

Every selected compile action still requires the exact requested `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW` and `HYBRIDCLR_H1_COUNT_DIAGNOSTICS` definitions and must be accounted into the selected GameAssembly link. The runtime domain owns `IL2CPP_DEBUG`, `IL2CPP_DEVELOPMENT` and the requested C++ Debug/Release assertion profile and is probed with the pinned IL2CPP configuration. BDWGC/zlib do not inherit that runtime configuration; each external domain is internally consistent and gets a real headerless compiler syntax/macro probe. `NDEBUG` uses definedness. PCH producer/consumer dependency, retained header bytes, exact producer replay and forced-input restrictions remain unchanged.

The normal strict verifier independently re-derives the domain ledger from the raw graph; it does not trust a PASS summary. Synthetic graphs may contain only the runtime domain, but the authenticated Apple fixture requires the exact 430 runtime / 2 BDWGC / 14 zlib inventory.

### Plan-stage failure retention

Fresh capture and explicit diagnostic replay now create a bounded tool-owned attempt root before graph interpretation/planning. They retain the original request/graph/configuration and declared-input/response inventory as stages are reached. A plan-stage failure records the stage and exception while PCH replay/macro probes remain `NotRun` unless child artifacts actually exist. No plan-stage failure creates a successful provenance receipt. Existing output directories are never reused.

## Primary review and bounded tests

Read `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/bee-domain-primary-20260915/` for the static review and local-validation checklist.

GitHub read-only CI run **34967358028** authenticated the committed fresh failure fixture and graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`, then ran the exact Primary regression suite at code anchor `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9`: **250/250 passed, 0 nonpasses**. The fixture tests assert 446 compile actions, 444 linked objects, exact 430/2/14 domains, six macro-probe groups and actual post-link file edges. This is bounded planning/tool validation on Ubuntu plus synthetic host compiler probes; it is **not** Unity, Apple Clang Player, runtime or M08 acceptance.

## Local validation

Perform an authoritative preflight first, then fresh **V01–V05**. Batch independent checks to minimize environment switching. Preserve unrelated files and every historical failed attempt.

### Preflight / V00 prerequisite

Explicitly fetch/pull candidate `codex/assembly-shadow-r01b-h1` and verify:

1. fetched checkout HEAD contains this handoff;
2. candidate code anchor in `source-targets.json` and `AssemblyShadowSourcePins.json` is exactly `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9`;
3. runtime pins match the table above;
4. reproduction branch is still exactly `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` and is not modified by this correction;
5. performance reference remains exactly `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` with its own historical profile.

Run the committed handoff/source preflight with a new output. Expected: source target verified, not build accepted. No ZIP/manual patch is authoritative.

### V01 — source/tool regression

On candidate, run the full H1 Python inventory plus the exact Bee Primary regression suite. Compile Unity and run focused H1 Editor tests, including `H1PchEvidenceProcessTests` and `H1EvidenceProcessTests`, then affected existing Assembly Shadow Editor regressions. Re-run the appropriate reproduction regressions without changing its frozen defect source. Record exact test IDs/results, Unity logs and NUnit XML.

Expected: no source/test regression. The committed CI 250/250 result is useful Primary evidence but does not replace macOS/Unity execution.

### V02 — Apple graph / failure-retention verification

Use the retained fresh V03 failure fixture or an explicitly selected fresh smoke input to verify planning now classifies the actual graph as:

- total compiler actions: 446;
- linked object actions: 444;
- `il2cpp-runtime`: 430;
- `external-bdwgc`: 2;
- `external-zlib`: 14;
- runtime Debug profile `IL2CPP_DEBUG=1`, `NDEBUG` undefined, `IL2CPP_DEVELOPMENT=0` for ON/Debug;
- all selected actions still carry feature/count definitions and are linked/accounted.

Then execute a bounded negative planning fixture and verify the tool-owned failure root exists before planning fails, with retained original inputs/stage/failure record and PCH replay/probe status accurately `NotRun` when they were not reached. Do not manufacture old DAG bytes marked Unavailable.

### V03 — fresh provenance-bound builds

Reinstall candidate from the new source pins and run the normal installed-runtime verifier with demo source verification enabled. Run a **fresh candidate ON/Debug smoke first**. Acceptance requires:

- Unity Player build success;
- complete compiler provenance root;
- successful exact domain ledger and compiler probes;
- PCH producer byte-identical replay and proof;
- managed-source provenance;
- final build receipt;
- strict single-build verifier PASS;
- exact restoration after build.

If smoke passes, execute candidate ON/OFF × Debug/Release and unfixed reproduction ON Debug/Release using fresh immutable roots. An explicitly supplied same-source smoke receipt may be revalidated/reused only through the committed supported route; never auto-select “latest”. Preserve all failed attempts.

Unknown external source membership, changed Apple Bee grammar/flags, PCH nondeterminism, unsupported macro state or provenance semantic ambiguity is **Primary Implementation work**: return it in `RETURN_TO_WEB.md`; do not expand allowlists locally.

### V04 — runtime/count/startup/performance evidence

After all six provenance-bound builds exist, complete the current R01B remediation matrix using existing documented entrypoints:

- 132 candidate count cells;
- 8 unfixed reproduction cells with their expected old failure/acceptance classifications;
- fresh baseline/fixtures/replay and all 11 startup modes;
- ordinary/mixed 8192 lifetime capacity and 8193 rejection;
- retained failed reservations, at least 25% usable encoded-page free capacity, 32 MiB per-DLL max and 512 MiB valid input boundary;
- lazy/dense, generics, arrays, reflection, FieldRVA, old Player and affected M03–M07/M06 regressions;
- controlled Development performance pairs against the separate performance-reference checkout on workloads supported by both sides.

Keep `Passed`, `Failed`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Do not infer Release/P99/device-RAM acceptance from the Development comparison.

### V05 — successor package and independent whole-chain review

Build the successor evidence selection/archive/index using explicit paths and the new source/build identities. Include raw compiler/PCH/domain proof inputs; do not substitute summary PASS artifacts. Authenticate archive/index hashes, membership and raw references, then run the existing strict semantic verifiers and commission a **genuine independent whole-chain M08 review** over design → source → builds → raw runtime evidence.

Only independent M08 PASS can make the package **Ready for Human Review Gate**. At that point stop for explicit human H1 approval. Neither agent may self-grant the gate. R02 remains prohibited.

## Failure evidence to return

For any failure, preserve and identify: repo/branch/checkout HEAD/code anchor/pin bytes, exact command/cwd/exit/timeout/stdout/stderr, Unity log/XML, raw selected Bee DAG, macro-domain census, recursive response files, compiler/SDK identity, original/rebuilt PCHs, module-file-info/header bytes, exact probe source/argv/macro output for every reached domain/context, native binary identity, managed capture, build/preparation/restore state, attempt-stage/failure JSON and before/after restoration hashes.

Do not delete failed evidence to make space. Absolute local paths are locators, not portable proof. Missing bytes are `Unavailable`; executed mismatches are `Failed`/`InvalidEvidence` as appropriate.

## Local correction boundary

Local Validation may correct explicit machine paths, executable permissions, invocation syntax, output-directory selection and isolated test setup, and may perform already-documented exact generated-file restoration after preserving before/after bytes. Do **not** locally change macro-domain membership, provenance acceptance semantics, PCH requirements, witness allowlists, count behavior, source-identity exclusions, architecture, ABI or performance methodology. Those are nontrivial Primary changes even if the diff would be small.

## Gate state

Current state remains: H1 `InProgress`, technically blocked pending V01–V05; last independent whole-chain M08 `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
