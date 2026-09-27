# R02 batch-E repair: fixed input bytes are not a compiler reproducibility promise

## Authority and observed failure

Input: Local return `1d7dc134003206ada8a92b50763ca2da7dc9530d`. Batch E remains ReturnRequired (9 Passed, 2 Failed, 22 Blocked). Roslyn v2 cleanup passed on both installers and both failed compiler commands. No controlled Player graph or D1/D2 series was accepted.

The two same-source 4,608-byte ordinary provider compilations had SHA-256 `9d05065f57806073919b551cb9b23e8f2ef86fab96bb3cb6d8da80f74b82ba99` and `b6e8b232d1749ed67db7f7bda028522993c7e912a68192c05cad0fe8ef31f5e5`; neither matched the fixed witness `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`. The original failed receipts and compiled roots are not modified.

## Contract correction, not relaxed acceptance

The unchanged `h1_witness_contract.py` and reflection-binding configuration declare `FixedAssemblyBytes`: one exact image path, hash and provider identity. They separately declare Development/Release provider semantic variants. A new compiler output is not necessarily that historical fixed image. The previous R02 helper incorrectly conflated those two contracts.

Primary recovered the exact image from the already-versioned September 19 H1 archive. Archive SHA-256 is `2ecb3d04cdd093c469717d4c2959ec416ec8d0745c51c2a4ba37c82f9bc253e8`. The exact member, extraction commit/run/artifact and image identity are recorded in `Tools/AssemblyShadow/R02/fixtures/m00-origin.json`. The same archive separately contains a compiled provider with SHA-256 `717471bd6405eb3e6800bc190660c3a3c929b214521bf0ace4609458d31ec8f9`, already distinct from its fixed ReflectionBindings image. No candidate or control workspace supplied the recovered fixture.

`ordinary_input.py` now materializes the committed canonical zlib/base64 fixture (decompression bounded to 4,608 bytes) independently in each owning checkout. It authenticates image size, exact original SHA-256, CLI full identity, origin, source-pin digest and all input/output bindings. An existing correct destination is not rewritten. Wrong existing bytes, linked paths, racing writers, changed pins, old compiler receipts and altered fixture/origin fail. New receipts explicitly state `FrozenHistoricalInputMaterialization`, `freshCscExecutionClaimed=false` and `historicalPlayerExecutionReused=false`.

The obsolete Unity compiler-and-stage helper and its host stub are removed. M07 still performs its original fresh compilation, provider semantic checks, compiler provenance and fixed-image validation. No production guard, accepted hash, semantic variant or source-policy allowlist is changed. Historical input reuse is not historical execution reuse.

The fixture-provenance CI independently reopens the hash-bound historical archive, locates the exact recorded member and compares it byte-for-byte with the compact committed fixture. Local does not need to expand that large archive to stage the small fixed input.

## What the binary evidence supports

The recovered image's CodeView record embeds `/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/Library/Bee/artifacts/200b00PDevDbg.dag/AssemblyShadowBaseline.HotUpdate.pdb`. Its MVID is `e7f5b1ac-eca4-4034-8da4-69e25ca9fe3b`. These are directly inspected fields, not inferred compiler settings.

Equal C#/asmdef hashes are not the full deterministic compiler input set: source paths, compiler/options, references and other inputs matter. Roslyn documents that distinction, and Microsoft documents embedded PDB paths/PathMap. See official references below. This explains why source hashes alone cannot guarantee byte equality; it does not prove which inputs caused each E difference.

`m00_forensics.py` reads the exact E receipt blobs from Git and the retained raw DLLs on the Local machine. It reports CLI identity, MVID, CodeView/PDB paths, timestamps/checksum, every differing byte span and conservative comparisons under the already-existing PE provenance mask. It never normalizes staged bytes, grants admission or edits an input. Differences beyond the mask remain explicitly unaccounted for. The E raw binaries are unavailable in Primary; their exact pairwise causes remain unproven until this supplied diagnostic executes.

## Batch and tests

One independent read-only `m00-batch-e-forensics` cell increases the batch from 33 to 34 cells. Its failure retains the diagnostic report and available inputs and does not block otherwise valid fresh builds. Complete evidence readiness still requires all required cells. Per-role builds materialize the same fixed input before M07, then reauthenticate it afterwards. The existing 8 functional sidecars, 4 pilot + 40 formal pairs, generated-native prerequisites, regressions and seals remain required.

Host regression tests cover independent materialization, no-overwrite/exclusive writes, hash/origin/path/pin tampering, old receipt rejection, exact archive origin and unsafe members, real PE fields, provenance-only versus other differences, pinned E receipt mutation, missing retained input and failure retention. Synthetic forensic cases are explicitly labelled; they are not results for E. Linux and macOS CI exercise the materializer/PE tests; Unity/IL2CPP remains Local execution.

This is a focused Primary self-review, not the independent R02 stage review. Preserve A/B/C/D/E, old installed roots and H1 records. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false. D1/D2 need measured disposition before H2.

## Official compiler references

- Roslyn deterministic inputs: https://github.com/dotnet/roslyn/blob/main/docs/compilers/Deterministic%20Inputs.md
- Microsoft C# PathMap and embedded PDB paths: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/advanced

## Transport

Demo-only Connector write/read-back smoke test: `codex/connector-smoke-r02-e-20260927-c18a@733055280571c5adadb3e268dd449f93fc8f74ba`. It is not acceptance evidence, must not be merged, and remains because no branch-deletion action is exposed. Runtime repositories are unchanged.
