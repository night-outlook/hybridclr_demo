# M07 Unity resources and APIs report

Status: **Gate 3B accepted** for `M07-Baseline-v6` on Unity 2022.3.62f2,
StandaloneOSX arm64. All evidence is local and unsigned; no push or PR was
created.

## Accepted source boundary

| Repository | Accepted executable revision |
| --- | --- |
| `hybridclr` runtime | `a19db144751f4f016769b90e61a80b8c27578678` |
| `il2cpp_plus` native | `666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8` |
| `hybridclr_unity` package | `2180b99daf39095cd76301da2bdf34ac945ee8b4` |
| isolated demo | `3aab779a3304dd9785ab14fb5fcdc73a107066f7` |

Demo commit `671737c082effa5094bed16b087f6da5c3c666c9` changes only the source-pin
metadata to identify that executable pairing. Evidence and report commits after
it do not change Player build inputs. The exact M06-to-M07 delta is recorded in
`M07-source-inventory.json`: runtime 0 files, native 3 files, package 15 files
and demo 91 files.

## Implemented scope

M07 adds seven canonical resource bundles, guarded baseline/P05 source-asset
generation, five positive patch policies, three structural rejection policies,
a business-free bootstrap and a 14-case runtime probe. Unity type acquisition,
allocation, deserialization, messages, scenes and cache reuse occur only after
a hash-bound transaction Commit.

The package resource receipt records effective compiler and Editor define sets.
Startup validation scans `Resources`, preloaded assets, ProjectSettings GUID
references and installed Addressables configuration for candidate scripts. The
native layout gate admits only safe appended private primitive storage at the
physical metadata boundary; serialized compatibility stays under the resource
ABI/build policy.

## Guarded build and fixtures

The guarded v6 workflow passed and restored the exact scripting settings after
the structural P05 domain:

- workflow SHA-256:
  `98f753f58a88fad23d0334eccb78448536d7f6d40826cea842a0eec40b84a239`;
- fixture SHA-256:
  `e4b15a7aa2af67758dc9b5af56aac9d01aa8955a52790a8894edb8f1626e5272`;
- independent Editor replay SHA-256:
  `e0ca8189e1631abb7d2211cbb732affca09e20040445c2827f34f72a24a19085`;
- accepted fixtures: P01, P02, P03, P04 and P05;
- rejected before publication with `ResourceRebuildRequired`:
  P05-DllOnly, P14-ClassRename and P15-SerializeReferenceRename.

The two Players are genuine distinct builds:

| Variant | Build GUID | Receipt SHA-256 | Native library SHA-256 |
| --- | --- | --- | --- |
| Native ON | `1beb5252b1344306bd26887043c75cb0` | `40d7a5b51c73f26defb6112ca51c542dd00d82444812ea9990177c5f221f044f` | `6a4f07c729c1357c1c2bd1383fde0efaa76dd605b44ece5df20566f280160a41` |
| Native OFF | `e27a8f100f3f4855b1c4f05a2adc5868` | `e3c52aa62eabc62688587c65a58a98d1b1a50e057c89e38a06971c7775cf3bbb` | `85e3c7b7293b4fcaf333eeee3d9c78e44c9c1a7e9e5ac5866d74140bd19c1bec` |

## Runtime and verifier result

All 14 required modes ran in distinct operating-system processes, exited zero,
wrote `result=Passed`, and left the complete ON/OFF Player app-tree hashes
unchanged. The launch receipt SHA-256 is
`231e8faa1942eac0688c073d30a357ff0c7f8c2af7e4600f85b4ac8df24c9467`.

The strict verifier was rerun from the final source and emitted Gate 3B with
`diagnosticOnly=false`, no missing modes and SHA-256
`c70ff3930d87e61b5e69fd03f0ba98b7d8cb18306f614a1bd584bbaa20c8da10`.
Its bound identities are:

- runtime ABI:
  `a41a8261e5fdbade351943b118d153c6f75e39595709b281c11c230427305015`;
- baseline resource ABI:
  `sha256:bd3ae1cc1adc603cd1553dc22f0d9b06fc4c8889b7f333d4234828ae04a33751`;
- P05 rebuilt resource ABI:
  `sha256:f99cbb1f42858874f1a1ff96cc10c7b4d273861ca7608cb83a5d667f23a96360`.

Legitimate baseline-use diagnostics for AOT dependencies outside the selected
closure remain visible. Acceptance rejects any selected-closure baseline use;
it does not erase or misclassify nonclosure observations.

## Final suites and installation

- Unity Editor: 912/912 passed, zero failed/skipped/inconclusive;
- Python: 356/356 passed with the preserved real M05 compiler boundary and
  zero skips;
- native: 824 focused checks, 20 ON/OFF syntax checks and 1,080 dependency
  inputs, all passed and unchanged;
- pinned installation: two identical installs, 942 installed files;
- installed-source verifier: complete demo source checked (no
  `--skip-demo-source`), native Shadow configured ON.

The native harness needs Unity-expanded `UnityVersion.h`, while the pinned
installer deliberately restores the template form of generated allowlisted
files. Closeout therefore ran the dedicated IL2CPP definition generator before
the native matrix, then reran installation repeatability and the complete
installed-source verifier for the final installed state. The initial lifecycle
diagnostic and the successful retry are both retained.

## Retention and independent commit gates

Evidence commit `8aaf30783eb9e5c0aebf96db6afe08aa81209ff8` contains six deterministic
archives, 8,816 archived files and 19 directly readable key artifacts. Archive
metadata is normalized and every archived/copied SHA-256 is checked against the
original immutable input. The artifact index SHA-256 is
`aba0d5df77706c1a25c0c300974c8ce21f791aff59735703f1229479b90341cc`.

Two clean-commit reviews passed:

- Gate A, current checkout:
  `990e1f63341d0fef84b78425c9720eea05628c18e8b56079dbd21af9b1fda3cf`;
- Gate B, separate detached worktree:
  `d87b6496c641740a65838a5c69f6d942cce98301671f725a6f23ddb2a71a4e98`.

Both gates verify committed Git blobs, the exact four-repository delta, all
archive members and originals, rerun all 356 Python tests, replay strict Gate
3B, and run complete installed-source verification. Gate B is an independent
deterministic detached-worktree process review, not an independent human or LLM
review. Editor/native execution remains byte-bound recorded evidence in those
commit gates; the raw outputs and logs are retained losslessly.

## Limits

This is local unsigned evidence for Unity 2022.3.62f2 StandaloneOSX arm64. It
does not claim authentication, Windows/Android behavior, arbitrary Addressables
installations, cross-version Unity serialization, M08 production build
integration, or M09-M12 download/security/rollback/release behavior. A partial
mode set or `--allow-incomplete` remains diagnostic only.
