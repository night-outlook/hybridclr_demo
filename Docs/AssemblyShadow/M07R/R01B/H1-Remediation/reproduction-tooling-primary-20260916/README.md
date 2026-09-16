# R01B H1 — Protected Reproduction Validation Tooling Repair

## Status

Primary Implementation completed. Candidate source/implementation anchor: `1b1cc9fe192b88be2a20fad31ea030b1e30be669`.

The protected reproduction branch remains `codex/assembly-shadow-h1-count-repro` at `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`; its unfixed behavior source pin remains `4e3d2035991ab5629265ac663e61bcb2ca62828b`. No protected runtime/native/package/IL2CPP pin moved.

A separate tooling-only branch is published at:

- branch: `codex/assembly-shadow-h1-count-repro-tooling`
- revision: `482a615bb662666f16f861c560f15c6607b82224`

This branch exists only so the protected reproduction Player can execute the current reviewed provenance capture policy during a fresh build. It is not the reproduction behavior authority.

## Root cause

Local Validation at `9dbe8ee7549b105a29a94bd7ec7383b2909ba066` established that candidate V02 and all four candidate V03 modes had valid current provenance, while the protected reproduction Player itself built successfully but its older project-local `h1_native_capture.py` rejected the same 446-action Apple graph under obsolete global macro-equivalence policy. Candidate-owned replay accepted that graph, but replay is diagnostic-only and cannot become build provenance.

The coupling came from the reproduction Editor wrapper invoking validation scripts from its own protected project tree. Keeping that old tooling preserved behavior history but prevented fresh reproduction build receipts under the current reviewed policy.

## Selected design

Use a separately authenticated tooling-only reproduction successor.

Candidate authority (`h1_reproduction_tooling.py`) requires all of the following before any reproduction build can be treated as eligible for provenance verification:

1. the protected reproduction behavior source and published head remain exact;
2. protected runtime/native/package/IL2CPP pins remain exact;
3. the tooling checkout is the exact declared branch/revision;
4. its non-metadata delta from the protected head is exactly the declared six-file validation override set;
5. the complete seven-file validation dependency set, including one already-identical dependency, has exact Git blob IDs equal to the candidate source anchor;
6. all current non-metadata working bytes match Git and no untracked Unity build inputs exist.

The candidate-owned batch wrapper (`h1_count_build_batch_tooling.py`) then:

- uses the normal candidate flow unchanged;
- runs reproduction from the authenticated tooling checkout;
- verifies the installed runtime against the protected reproduction pins;
- runs candidate-owned strict native and managed verifiers on the resulting fresh receipt;
- re-authenticates the split source identity after restoration;
- emits `validation-tooling-binding.json`, binding the verified build-receipt SHA to role, protected behavior source, tooling revision, source-pin SHA, source-target SHA and exact tool file set.

The sidecar status is `ToolingBoundToVerifiedBuildReceiptNotRuntimeAccepted`; it is not runtime/M08/human acceptance.

## Tool identity

Required candidate-authenticated tool set:

| Path | Git blob |
| --- | --- |
| `Assets/AssemblyShadowDemo/Editor/H1CompilerProvenance.cs` | `b92a8cdb045c563d8339aad5c358e170e5a081ca` |
| `Tools/AssemblyShadow/h1_bee_macro_domains.py` | `6c87c3134a2ae63fbf933687afdd28ed51b6bfc2` |
| `Tools/AssemblyShadow/h1_capture_attempt.py` | `1cd7b993234ef3d39e5a69f98d55a207adeb1dd2` |
| `Tools/AssemblyShadow/h1_compiler_actions.py` | `e89c97c553793a8866c25b3090972a550f91b751` |
| `Tools/AssemblyShadow/h1_macro_domain_census.py` | `b89059a7d50fdb4026bad3d6f0bef09c2d0f62f7` |
| `Tools/AssemblyShadow/h1_native_capture.py` | `d1e1153de9c0784e4d202a573cb31c81ac888ef7` |
| `Tools/AssemblyShadow/h1_pch_provenance.py` | `42019759411a076a982149dd654f6347c0e6c65b` |

`h1_compiler_actions.py` was already byte-identical on the protected reproduction head, so the tooling branch changes only the other six paths.

## Primary validation

Workflow `35081136990` at candidate anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` passed **294/294**, zero nonpasses.

- artifact ID: `10439663711`
- artifact SHA-256: `a7ad62cbd34200056448374b69f942c0cd7e9d3515bb7e499fe2d64c44d3dd7d`

The suite covers exact tooling delta, runtime-delta rejection, wrong-tool-blob rejection, real disposable two-checkout ancestry/tree authentication, dirty tool rejection, candidate-source blob equality, wrapper source/install path, and receipt-bound tooling sidecar.

This is bounded Primary/tool evidence only. It does not replace fresh macOS Unity reproduction builds or independent whole-chain M08.

## Evidence preservation

`local-validation-20260916-9568ea3` remains historical Local evidence. Its candidate V02/V03 results are preserved as valid evidence for their original source/handoff; they are not deleted or relabeled. Because the candidate source anchor now includes new validation tooling, the next handoff nevertheless requires fresh V00–V05.

H1 remains InProgress, last independent M08 remains FAIL, `humanGatePassed=false`, `mayEnterR02=false`.
