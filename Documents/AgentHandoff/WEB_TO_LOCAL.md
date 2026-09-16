# Primary Implementation → Local Validation

## Objective

Resume R01B H1 local validation from the repaired authoritative handoff contract. The candidate demo **source anchor** for fresh V00–V05 is `b6db7c2fb2fce364d49458b7dfc78886fd430004` on `night-outlook/hybridclr_demo` branch `codex/assembly-shadow-r01b-h1`. The last executable/tooling implementation anchor remains `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9`.

The previous Local Validation return at `b6db7c2…` established that handoff HEAD `c0d3070…` failed before source validation with `Blocked: Incomplete handoff sections`; V01–V05 were therefore `Blocked / NotRun`. This successor repairs that document/preflight contract without weakening the preflight executable, Apple Bee provenance rules, historical evidence, runtime pins, reproduction defect, or performance reference.

Git is the only authoritative handoff state. Read `Documents/AgentHandoff/LOCAL_VALIDATION.md`, `Documents/AgentHandoff/RETURN_TO_WEB.md`, and `Documents/AgentHandoff/local-validation-20260915-c0d3070/README.md` before starting. Preserve those records. Do not apply chat ZIPs or unpublished patches.

H1 remains `InProgress`, technically blocked pending fresh V00–V05; last independent whole-chain M08 is `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate demo source anchor | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `b6db7c2fb2fce364d49458b7dfc78886fd430004` |
| Candidate executable/tooling implementation anchor | same branch | `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Reproduction demo published head — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction demo code anchor | same branch | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Unfixed reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. `ProjectSettings/AssemblyShadowSourcePins.json` must pin candidate demo revision `b6db7c2fb2fce364d49458b7dfc78886fd430004`; runtime pins must match the table. The fetched branch HEAD will be a later metadata-only handoff successor. Record both checkout HEAD and source anchor in fresh evidence.

The `b6db7c2…` source anchor intentionally captures the committed `local-validation-20260915-c0d3070` checkpoint so the unchanged source verifier has a complete frozen baseline. **Do not add future auxiliary checkpoint directories under `Documents/AgentHandoff/`.** Put new raw/checkpoint evidence under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`, which is the existing metadata-only evidence namespace. Continue to update only the protocol-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` under `Documents/AgentHandoff/`.

## Implementation

### Handoff/preflight contract repair

`Tools/AssemblyShadow/h1_handoff_preflight.py` is unchanged. Its authoritative document contract requires these nine literal section headings, all of which are present in this file:

- `## Objective`
- `## Source targets`
- `## Implementation`
- `## Local validation`
- `## Failure evidence`
- `## Alternatives`
- `## Risks`
- `## Local correction boundary`
- `## Human review gate`

The repair changes handoff/source identity metadata only. The preflight must still prove committed handoff bytes, candidate branch/origin, source-target schema, source-pin equality, runtime pins, and demo-source identity. No bypass or relaxed heading check is introduced.

### Apple Bee provenance implementation retained

The executable implementation remains the Primary-reviewed `463ec3f…` anchor. It classifies the authenticated Unity Apple Bee graph by exact canonical source ownership:

- `il2cpp-runtime`: 430 compile actions, including both PCH producers, generated C/C++, brotli and other runtime-owned sources;
- `external-bdwgc`: exactly 2 reviewed direct-C sources;
- `external-zlib`: exactly 14 reviewed direct-C sources.

All selected compile actions still require exact requested Shadow/count definitions, selected compiler/SDK identity, and complete object/link accounting. Runtime owns the requested `IL2CPP_DEBUG`/`IL2CPP_DEVELOPMENT` and Debug/Release assertion profile. BDWGC/zlib do not inherit the IL2CPP configuration header; each external domain must be internally consistent and receives real headerless syntax/macro probes. Unknown external sources, external PCH use, mixed domain state, compiler/SDK/environment drift, missing link inputs or ambiguous outputs fail closed. `NDEBUG` uses definedness.

Fresh capture and diagnostic replay create bounded failure roots before planning so plan-stage errors retain request/DAG/config/input inventory, stage and exception; unreached PCH replay/probes remain `NotRun`. No failed attempt becomes a successful receipt.

Primary CI workflow run `34967358028` authenticated Bee graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181` and passed **250/250** bounded Bee/tool tests at implementation anchor `463ec3f…`. That is not Unity/Apple Player/runtime/M08 acceptance.

## Local validation

Run **fresh V00–V05** from the repaired handoff. V00 is mandatory; do not reuse the failed c0d3070 preflight as a pass.

### V00 — authoritative preflight

1. Explicitly `git pull --ff-only origin codex/assembly-shadow-r01b-h1` in candidate demo.
2. Verify branch/origin/HEAD and preserve unrelated working changes. Do not reset, clean, or hide historical untracked evidence.
3. Confirm candidate source target and source pin both identify `b6db7c2fb2fce364d49458b7dfc78886fd430004`.
4. Confirm runtime pins, reproduction head/native, and performance reference exactly match the Source targets table.
5. Run with a **new absolute output path**:

```sh
python3 Tools/AssemblyShadow/h1_handoff_preflight.py \
  --project /ABS/CANDIDATE/hybridclr_demo \
  --role candidate \
  --output /ABS/NEW/v00/candidate-handoff.json
```

Expected: exit `0`, `status=SourceTargetVerifiedNotBuildAccepted`, `codeCommit=b6db7c2fb2fce364d49458b7dfc78886fd430004`, current checkout HEAD recorded separately, `humanGatePassed=false`, `mayEnterR02=false`.

If V00 does not pass, stop V01–V05 and return exact evidence to Primary. Do not edit `WEB_TO_LOCAL.md` locally.

### V01 — source/tool/Unity regression

Run the full affected H1 Python inventory, the exact Bee Primary suite, normal strict compiler-provenance tests and existing normal M02-owner tests. Compile candidate and reproduction in Unity and run focused H1 Editor tests including `H1PchEvidenceProcessTests`, `H1EvidenceProcessTests`, and affected Assembly Shadow regressions. Preserve exact test IDs, logs, NUnit XML and skips.

Expected: no regression. Primary CI is supporting evidence only and does not replace macOS/Unity execution.

### V02 — Apple-domain and failure-retention verification

Against an authenticated retained/fresh Apple Bee input, verify the real domain inventory remains 446 compiler actions / 444 linked object actions / 430 runtime / 2 BDWGC / 14 zlib and six probe contexts, with complete selected-link coverage. Verify ON/Debug runtime profile is `IL2CPP_DEBUG=1`, `NDEBUG` undefined, `IL2CPP_DEVELOPMENT=0` while external library state is independently proved rather than used as runtime assertion evidence.

Execute a bounded negative planning case and confirm the failure root exists before planning fails, retains reached raw inputs/stages, and marks unreached PCH replay/macro probes `NotRun` rather than fabricating failure evidence.

### V03 — fresh provenance-bound builds

Reinstall candidate from the new source pins and run normal installed-runtime verification with demo-source checking enabled. Execute a fresh candidate ON/Debug smoke first. Acceptance requires Player success plus complete compiler/PCH/domain provenance, managed-source provenance, final receipt, strict single-build verifier PASS and exact restoration.

After a valid smoke, complete candidate ON/OFF × Debug/Release and unfixed reproduction ON Debug/Release in fresh immutable roots. Use explicit same-source smoke reuse only through the committed supported option; never auto-select a latest result. Preserve every failed attempt.

Unknown Apple Bee grammar, source membership, compiler flags, macro semantics, PCH nondeterminism or provenance ambiguity is Primary work. Return it; do not broaden allowlists locally.

### V04 — runtime/count/startup/performance chain

Using the established project entrypoints and current R01B plan, complete fresh required count/reproduction/startup/capacity/regression coverage: 132 candidate count cells; 8 unfixed reproduction cells; baseline/fixtures/replay and 11 startup modes; ordinary/mixed 8192 lifetime capacity and 8193 rejection; retained failed reservations; >=25% usable encoded-page free capacity; 32 MiB max DLL and 512 MiB valid input boundary; lazy/dense/generic/array/reflection/FieldRVA/old-Player and affected M03–M07 checks.

Run controlled Development performance pairs against the separate performance-reference checkout only on mutually supported workloads. Do not infer Release/P99/device-RAM acceptance.

### V05 — successor package and independent whole-chain M08

Build a successor archive/index using explicit new source/build/evidence paths. Include raw compiler/PCH/domain proof and all required raw runtime evidence; summary PASS files are insufficient. Authenticate archive/index bytes, membership and references, then run strict semantic verifiers and commission a genuine independent design→source→build→raw-evidence M08 review.

New auxiliary checkpoint/raw evidence for this validation must be committed under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/`, not a new `Documents/AgentHandoff/local-validation-*` directory. Update and push `LOCAL_VALIDATION.md`; use `RETURN_TO_WEB.md` for any nontrivial issue returned to Primary.

## Failure evidence

For every failure retain exact repository/branch/checkout HEAD/source anchor/pin bytes, command, cwd, exit/timeout, stdout/stderr, Unity log/XML, selected Bee DAG, macro-domain census, recursive response bytes, compiler/SDK identity, PCH original/rebuild/module-file-info/header bytes, probe source/argv/macro output for every reached context, native and managed artifact identities, build/preparation/restore state and attempt-stage/failure records.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Missing bytes are not execution failures. Preserve historical c0d3070 preflight attempts and earlier v6–v11 evidence unchanged.

## Alternatives

The acceptance route is the unchanged authoritative preflight followed by fresh strict capture and V01–V05. Explicit diagnostic replay remains investigation-only and cannot close a fresh-build requirement. The supported explicit same-source smoke reuse may avoid one redundant build only after revalidation; it is not automatic fallback.

Do **not** solve a failure by disabling PCH/PDB, ignoring compiler errors, broadening source-domain membership, relaxing witness/provenance checks, repointing reproduction to fixed native code, or replacing the performance-reference profile. Any such nontrivial alternative returns to Primary for design and review first.

## Risks

Apple Bee/Clang may expose legitimate flags, source ownership or PCH behavior not present in Primary’s bounded CI fixture. Conservative parsing/provenance may reject those cases. Treat them as actionable evidence, not justification to bypass checks.

The candidate source anchor now includes the committed c0d3070 Local Validation checkpoint because that checkpoint lives outside the old metadata-only namespace. Future auxiliary checkpoint evidence must use `Docs/AssemblyShadow/...`; otherwise it can again become a demo build-input change and invalidate the source pin.

Publishing this repaired handoff does not prove native installation, Unity compilation, Player execution, runtime matrix, performance, successor packaging or M08. Those remain Local Validation tasks.

## Local correction boundary

Local Validation may correct explicit machine paths, executable permissions, invocation syntax, output-directory choices, isolated test setup, and already-documented exact generated-file restoration after preserving before/after bytes.

Local Validation must **not** change handoff/preflight acceptance semantics, source-pin policy, macro-domain membership, compiler/PCH provenance requirements, witness allowlists, count behavior, ABI, architecture, source-identity exclusions, performance methodology, or cross-module design. Those are nontrivial Primary changes regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md`. Preserve and append empirical facts in Local-owned reports.

## Human review gate

Current project gate is H1 as defined by the committed project review documents. Current state remains `InProgress`; technical readiness is blocked pending fresh V00–V05; last independent whole-chain M08 is `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Only after implementation and actual Local Validation satisfy the current gate definition **and** a genuine independent whole-chain M08 returns PASS may Local Validation mark the package **Ready for Human Review Gate**. Then stop for explicit human approval. Neither agent may grant H1. Do not begin R02 before that approval is recorded.
