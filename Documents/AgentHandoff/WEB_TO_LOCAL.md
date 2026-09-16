# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the protected-reproduction validation-tool coupling repair.

Authoritative candidate demo source / implementation anchor:

`1b1cc9fe192b88be2a20fad31ea030b1e30be669`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

Local Validation commit `9dbe8ee7549b105a29a94bd7ec7383b2909ba066` established that candidate V02 and all four candidate V03 modes had current provenance, while the protected reproduction Player built but its older project-local native provenance tool rejected the real 446-action Apple Bee graph. Review also found the protected managed-source bridge predates the current schema-3 cache proof. Candidate-owned replay is diagnostic evidence only and cannot be promoted to fresh build provenance.

Primary resolves the coupling with a separately authenticated **tooling-only reproduction successor** covering the required native and managed validation chain. The protected reproduction branch, unfixed behavior source and all protected runtime pins remain unchanged. Fresh V00–V05 are required. Preserve `local-validation-20260916-9568ea3` and all older evidence unchanged; its candidate V02/V03 results remain valid historical evidence for their original source chain, not fresh acceptance for this candidate anchor.

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Documents/AgentHandoff/source-targets.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-9568ea3/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/reproduction-tooling-primary-20260916/`

Git is the handoff authority. Do not apply chat ZIPs or unpublished patches.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate demo source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `1b1cc9fe192b88be2a20fad31ea030b1e30be669` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| **Protected reproduction branch — preserve** | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction unfixed behavior source | same repository/history | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| **Reproduction validation tooling only** | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `0c9c2508d94a097dff50028212a01695c8e29c60` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. Candidate `AssemblyShadowSourcePins.json` pins `1b1cc9fe...`; the reproduction-tooling checkout retains the protected reproduction pin file, including demo behavior revision `4e3d203...` and reproduction native `99cdb1b...`.

The final candidate branch HEAD is expected to be a later metadata-only handoff successor. Record both final checkout HEAD and candidate source anchor. The tooling revision is not a new behavior/source pin and must never replace the protected reproduction identity in runtime/count conclusions.

## Implementation

### Split reproduction behavior/tooling identity

The protected reproduction branch remains historical and unfixed, but its Editor validation wrappers execute project-local tools. Preserving the old project tree therefore preserved obsolete validation policy as well as unfixed runtime behavior.

Primary published a separate tooling-only successor. Candidate authority now proves:

1. behavior source `4e3d203...` → protected head `352d747...` → tooling revision `0c9c250...` ancestry;
2. the protected published head contains no non-metadata behavior changes after its behavior source pin;
3. tooling revision non-metadata delta from protected head is **exactly nine validation-only overrides**;
4. the **complete eleven-file native+managed validation dependency set**, including already-identical `H1EvidenceProcess.cs` and `h1_compiler_actions.py`, has exact Git blob IDs matching candidate source anchor `1b1cc9fe...`;
5. reproduction pin bytes still identify the original unfixed behavior/native/package/IL2CPP chain;
6. working bytes match Git and no untracked Unity build inputs are present.

The authority tool is `Tools/AssemblyShadow/h1_reproduction_tooling.py`; expected V00 status is `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`.

The tooling successor includes current native provenance capture plus the current managed build wrapper, managed-source bridge and schema-3 `h1_managed_provenance.py`. It does **not** replace `H1CountDiagnosticBuild`, runtime diagnostic code, unfixed native code or protected pins.

### Fresh build integration

For fresh V03 use candidate-owned `Tools/AssemblyShadow/h1_count_build_batch_tooling.py`.

Candidate builds use the normal source/provenance flow. Reproduction builds run Unity from the exact tooling-only checkout while installed runtime remains verified against protected reproduction pins. Candidate-owned strict native and managed verifiers verify the resulting fresh receipt, and split identity is re-authenticated after restoration.

After strict build verification the wrapper writes `validation-tooling-binding.json` binding exact build-receipt SHA-256, role, protected behavior source, validation checkout/tooling revision, source-pin SHA-256, current `source-targets.json` SHA-256 and complete tool-file map. Its status is `ToolingBoundToVerifiedBuildReceiptNotRuntimeAccepted`; it is not runtime/M08/human acceptance.

Diagnostic replay remains non-acceptance.

### Primary review

Candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` passed workflow **35081136990** with **294/294** bounded tests, zero nonpasses.

- authenticated Apple fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10439663711`
- artifact ZIP SHA-256: `a7ad62cbd34200056448374b69f942c0cd7e9d3515bb7e499fe2d64c44d3dd7d`

The tooling branch tree was additionally reviewed against the protected reproduction head: its direct non-metadata delta is the declared nine validation paths. All eleven required dependency blobs are candidate-authenticated by V00. Primary CI is bounded tool evidence only, not macOS Unity reproduction acceptance or M08.

## Local validation

Run fresh **V00–V05**. Follow `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/reproduction-tooling-primary-20260916/LOCAL_VALIDATION_TASKS.md`.

### V00 — dual authority preflight

1. Pull candidate `codex/assembly-shadow-r01b-h1`; record final HEAD/source anchor/dirty state.
2. Run normal candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted` and source anchor `1b1cc9fe...`.
3. Use a separate reproduction checkout on `codex/assembly-shadow-h1-count-repro-tooling` at exact `0c9c2508d94a097dff50028212a01695c8e29c60`.
4. From candidate run:

```sh
python3 Tools/AssemblyShadow/h1_reproduction_tooling.py \
  --project /ABS/REPRO_TOOLING \
  --authority-project /ABS/CANDIDATE \
  --output /ABS/NEW/v00/reproduction-tooling.json
```

Require behavior `4e3d203...`, protected head `352d747...`, tooling `0c9c250...`, exact 11-file tool map / 9-file override map, protected pins unchanged and gate flags false. If either preflight fails, stop before V01–V05.

### V01 — source/tool/Unity regressions

Run full H1 Python inventory and exact Primary suite, including split-tooling and receipt-binding regressions. Compile candidate and exact reproduction-tooling checkout in Unity 2022.3.62f2; explicitly verify current native provenance wrapper and managed schema-3 bridge compile. Run affected H1/Assembly Shadow Editor tests. Preserve exact logs/XML/nonpasses and both preflight records.

### V02 — fresh candidate normal-cache proof

Re-run fresh candidate ON/Debug schema-3 normal-cache validation for source anchor `1b1cc9fe...`. Preserve normal Bee cache; require action-local recursive response ownership and all prior graph/action/dependency/output/reachability/fresh-Player-binding controls. Do not use `--reuse-proof` as substitute acceptance.

Previous candidate V02/V03 evidence from `local-validation-20260916-9568ea3` stays preserved and referenceable, but is not relabeled as fresh evidence for this source anchor.

### V03 — fresh six-build set

Use only:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch_tooling.py \
  --candidate /ABS/CANDIDATE \
  --reproduction /ABS/REPRO_TOOLING \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /ABS/pwsh \
  --scope all \
  --output /ABS/NEW/v03/builds \
  --execute
```

Do not reuse old-source smoke receipts. Produce fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release receipts.

Every reproduction build must pass current strict native **and managed** provenance and exact restoration, and produce `validation-tooling-binding.json` with behavior source `4e3d203...`, tooling revision `0c9c250...`, exact receipt SHA, protected pin SHA, current source-target SHA and complete 11-file tool identity map.

### V04 — runtime/count/startup/capacity/performance

After a valid six-build set, execute the established chain: 132 candidate count cells, 8 unfixed reproduction cells, fresh baseline/fixtures/replay, startup11, 8192/8193 capacity boundary, required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage. Run controlled Development performance only against protected reference `88508b59...` on common supported workloads.

### V05 — successor package and independent M08

Archive/index all required fresh raw evidence, including the reproduction-tooling V00 preflight, source-target/pin bytes, exact tooling tree/delta, each reproduction `validation-tooling-binding.json`, bound receipt and raw native+managed/PCH/store evidence. Preserve old candidate V02/V03 evidence with original source identity/disposition.

Authenticate archive/index bytes and semantic membership, then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review. **Only genuine independent whole-chain M08 PASS** may make the package Ready for Human Review Gate; then stop for explicit human H1 approval.

## Failure evidence

For split-tooling failures retain candidate/reproduction checkout HEADs/branches/remotes, candidate `source-targets.json`, reproduction pins, behavior/protected/tooling SHAs, exact tree delta, complete tool blob map, working-tree/untracked state, preflight stdout/stderr/exit/output, Unity logs/XML, build receipt and raw native/managed provenance evidence.

For V03 retain every `validation-tooling-binding.json` even if a later stage fails and identify whether failure occurred at tooling authority, Unity compilation/build, native capture, managed capture, strict verification, receipt binding, restoration/source recheck, runtime validation or later chain stage.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Preserve `local-validation-20260916-9568ea3` and all earlier evidence unchanged.

## Alternatives

Do not move/rewrite the protected reproduction branch, repin it to fixed/current candidate source, copy current runtime/native fixes into reproduction, manually copy validation files outside the declared tooling revision, or promote diagnostic replay to acceptance.

A future external candidate-owned tool bundle would require a separate reviewed design that binds exact tool bytes into fresh Unity capture. It is not authorized by this handoff.

## Risks

The tooling-only successor changes Editor/validation infrastructure in the reproduction checkout. Local must empirically prove Unity compilation and fresh reproduction native+managed provenance while confirming protected runtime/Player behavior and pins remain unchanged. Any additional required tooling path means the current allowlist is incomplete and must return to Primary.

The candidate source anchor changed to add validation infrastructure; prior candidate V02/V03 results are preserved evidence but not fresh current-anchor acceptance. Primary's 294/294 CI does not replace macOS Unity/Player validation.

## Local correction boundary

Local may correct machine paths, executable permissions, invocation syntax, output-directory choices and isolated test setup, and may perform already-documented exact generated-file restoration after preserving before/after bytes.

Local must not change tooling branch/revision, tool-file/override maps, protected reproduction branch/source pins, native/package/IL2CPP pins, runtime behavior, provenance acceptance semantics, cache/macro/PCH rules, count behavior, ABI/architecture or performance methodology. Such issues return to Primary regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress / BlockedPendingFreshV00ToV05**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

Fresh V00–V05 and a genuine independent whole-chain M08 PASS are required before **Ready for Human Review Gate**. Then stop for explicit human H1 approval.

**Do not begin R02.**
