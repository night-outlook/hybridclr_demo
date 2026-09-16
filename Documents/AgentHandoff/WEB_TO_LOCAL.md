# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the reproduction-tooling Editor-source compatibility repair returned by Local Validation commit `cef1ec761e268ebbb699cc16b6ab037d7bc5a482`.

Authoritative candidate source / implementation anchor:

`3242b071540278510ea4ae287c70e37fc4c60340`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

The previous tooling successor correctly authenticated current native+managed provenance tooling but retained the protected historical `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs`. That stale test referenced removed `H1ManagedSourceProvenance.Capture` API and failed Unity compilation with CS0426 before any reproduction Player build.

Primary publishes a reviewed tooling-only successor that removes that obsolete test and its `.meta`, exactly matching their absence from the candidate source anchor. Protected reproduction behavior/runtime pins and all historical evidence remain unchanged.

Run fresh **V00–V05**. Last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Documents/AgentHandoff/source-targets.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-534b03e/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/reproduction-tooling-compat-primary-20260916/`

Git is the authority. Preserve all prior checkpoints/evidence; do not apply unpublished patches or mutate protected branches.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `3242b071540278510ea4ae287c70e37fc4c60340` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction branch — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Unfixed reproduction behavior source | same repository/history | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction tooling successor | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**.

Candidate `ProjectSettings/AssemblyShadowSourcePins.json` pins source anchor `3242b071...`. The tooling checkout retains the protected reproduction pin bytes: behavior `4e3d203...`, native `99cdb1b...`, package `0ea633a...`, IL2CPP `6be7f38...`.

The final candidate branch HEAD will be a later metadata-only handoff successor. Record both final checkout HEAD and source anchor. Never use the tooling revision as the reproduction runtime/behavior identity.

## Implementation

### Exact tooling successor delta

Relative to protected reproduction head `352d747...`, tooling successor `ba8fee33...` contains only validation-infrastructure changes:

- the existing **nine** reviewed validation blob replacements from the prior tooling successor;
- deletion of `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs`;
- deletion of `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs.meta`.

The complete protected-head → tooling-successor delta is therefore **11 validation-only paths**. No gameplay/runtime/native product source or protected pin is changed.

### Authenticated deletions

`h1_reproduction_tooling.py` now treats deletions as first-class authority entries rather than implicit exceptions.

V00 requires every declared deletion to:

1. exist in the protected head;
2. be absent from the tooling successor;
3. participate in the exact full changed-build-input set;
4. be absent from the exact candidate source anchor as well.

A path cannot be both an override and deletion. Undeclared deletion, extra deletion, wrong blob, runtime-source change or pin drift remains a hard failure.

### Assembled Editor-source compatibility

After tree/blob/untracked verification, V00 audits the exact assembled tracked C# set under:

- `Assets/AssemblyShadowDemo/Editor/`
- `Assets/AssemblyShadowDemo/Tests/Editor/`

It rejects retained consumers of the removed historical `H1ManagedSourceProvenance` API, including the `Capture`/`CaptureBeforeBuild`/`RequireUnchanged` surface that caused the CS0426 failure.

The V00 result now includes:

- `toolDeletions` — exact two deleted paths;
- `editorSourceCompatibility.status=Compatible`;
- Editor-source inventory count/hash.

This is a bounded source-compatibility check, not a substitute for V01 Unity compilation.

### Regression and Primary validation

The real disposable-Git regression now constructs the exact failure topology: protected reproduction has the stale Editor test, tooling successor deletes it, candidate source omits it, and the assembled tooling source audit must pass. Negative tests reject undeclared deletion, a legacy API consumer, and a deletion not absent from the candidate anchor.

Candidate source anchor `3242b071540278510ea4ae287c70e37fc4c60340` passed workflow **35093281267** with **298/298**, zero nonpasses.

- authenticated Apple Bee fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10444094920`
- artifact ZIP SHA-256: `336777f8cec845bc2a9557f3a6312d472229cb62e3eed31ec17dde97dd5f4045`

This is bounded Primary/tool evidence only. Fresh Unity compilation and V00–V05 remain mandatory.

## Local validation

Follow `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/reproduction-tooling-compat-primary-20260916/LOCAL_VALIDATION_TASKS.md`.

### V00 — dual authority and assembled-source preflight

1. Pull candidate `codex/assembly-shadow-r01b-h1`; record final HEAD, source anchor `3242b071...`, dirty/untracked state and protected sibling heads.
2. Run normal candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Use a separate checkout on `codex/assembly-shadow-h1-count-repro-tooling` at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. From candidate run:

```sh
python3 Tools/AssemblyShadow/h1_reproduction_tooling.py \
  --project /ABS/REPRO_TOOLING \
  --authority-project /ABS/CANDIDATE \
  --output /ABS/NEW/v00/reproduction-tooling.json
```

Require exact behavior/protected/tooling identities, exact eleven-file required tool map, exact nine replacement map, exact two deletion paths, `editorSourceCompatibility.status=Compatible`, protected pins unchanged and gate flags false.

If either V00 check fails, stop before V01–V05.

### V01 — real compile and focused regressions

Run full H1 Python inventory and bounded Primary suite. Compile candidate and exact tooling successor under Unity 2022.3.62f2. The historical CS0426 must be absent. Run affected H1/Assembly Shadow Editor NUnit suites in both checkouts and preserve exact test IDs/logs/XML/skips/nonpasses.

Any further assembled tooling Editor-source incompatibility returns to Primary; do not expand the tooling allowlist locally.

### V02 — fresh candidate schema-3 proof

Run fresh candidate ON/Debug normal-cache proof for source anchor `3242b071...`. Preserve the normal Bee cache and require current schema-3 action-local response ownership, graph/action/dependency/output/reachability controls, exact fresh Player input binding and no `--reuse-proof` substitution.

Historical V02/V03 results under older anchors remain historical and must not be relabeled.

### V03 — fresh six-build provenance set

Use candidate-owned `Tools/AssemblyShadow/h1_count_build_batch_tooling.py` with candidate and exact `ba8fee33...` tooling checkouts. Do not reuse old-source smoke receipts.

Produce fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release. Every reproduction build must pass current strict native+managed provenance and exact restoration. Archive the V00 tooling preflight alongside receipt-bound tooling evidence so the authenticated replacements/deletions and assembled-source compatibility remain in the evidence chain.

### V04 — runtime/count/startup/capacity/performance

After a valid fresh six-build set, execute the established R01B runtime chain: 132 candidate cells, 8 unfixed reproduction cells, fresh baseline/fixtures/replay, startup11, 8192/8193 capacity boundary, required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage, plus controlled Development performance against preserved reference `88508b59...` on common supported workloads.

### V05 — successor and independent whole-chain M08

Build the successor package only from explicit fresh evidence. Include both V00 authority outputs, exact source-target/pin bytes, tooling tree/delta, `toolDeletions`, `editorSourceCompatibility`, fresh receipts/bindings, raw native+managed/PCH/store evidence, runtime/count/startup/capacity/performance evidence, and historical evidence with original identity/disposition.

Authenticate archive/index bytes and semantic membership. Then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only a genuine independent whole-chain **M08 PASS** may make the package Ready for Human Review Gate. Then stop for explicit human H1 approval.

## Failure evidence

On V00/V01 failure retain candidate/tooling branches and exact HEADs, source anchor, source-target bytes/hash, protected pin bytes, complete tooling compare/delta, tool replacement/deletion maps, `editorSourceCompatibility`, working-tree/untracked state, Unity compile logs and NUnit XML.

On V02–V05 failure retain the established raw build/provenance/runtime evidence and identify the exact stage. Do not overwrite or relabel `local-validation-20260916-534b03e`, `local-validation-20260916-9568ea3`, or older checkpoints.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct.

## Alternatives

Do not reintroduce or locally port the historical managed-source test, move/rewrite the protected reproduction branch, repin reproduction to candidate/fixed behavior, copy runtime/native fixes into reproduction, or manually alter the tooling checkout.

If Unity finds another legitimate Editor dependency not covered by the reviewed successor, preserve evidence and return to Primary for a new reviewed tooling successor.

## Risks

The compatibility audit targets the concrete removed managed-source API that blocked Local Validation; it is not a general C# compiler. Fresh V01 Unity compilation of the exact assembled tooling checkout therefore remains mandatory.

Candidate source anchor changed again because authority/deletion logic and regressions changed. Historical candidate V02/V03 evidence remains preserved but is not fresh acceptance for `3242b071...`.

Primary 298/298 does not establish Player, runtime, performance, M08 or Human Review Gate acceptance.

## Local correction boundary

Local may correct machine-specific paths, executable permissions, invocation syntax, new output-directory choices and isolated test harness setup, and may perform already-documented exact generated-file restoration after preserving before/after bytes.

Local must not change the tooling revision, replacement/deletion authority, protected behavior/runtime pins, provenance semantics, cache/macro/PCH rules, count behavior, ABI/architecture or performance methodology. Such issues return to Primary regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress / BlockedPendingFreshV00ToV05**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

Fresh V00–V05 and genuine independent whole-chain M08 PASS are required before Ready for Human Review Gate. Then stop for explicit human H1 approval.

**Do not begin R02.**
