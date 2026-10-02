# R03 F — installed-root provenance and isolated Editor scope

Primary Implementation self-review and host evidence, 2026-10-01 UTC. **Not independent stage review, Local acceptance, or a Human Review Gate.**

## Received authority and immutable result

Local return `33d7b1fce2f3b8463dc4ac78061250ecc7df925d` records one batch D from executed demo `faa351d6854e71982ca047b994fb8579475f542a`: **ReturnRequired, 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed. Read `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md` and `History/M07R/R03/local-validation-20261001-batch-d-return-required/` under `Docs/AssemblyShadow`.

D produced four successful native artifact receipts and ARM64 apps, but the four build cells failed the strict installation-receipt lookup. Actual Editor execution recorded 754 Passed and one Ignored; its aggregate failed the runner. The ignored M01 frozen-resource test remains NoCoverage. All nineteen Players were Blocked/NotRun. Artifact existence is not retrospective cell or runtime acceptance.

Local authenticated 1,736 indexed files and 1,737 archive members. Primary has read the published records, not accessed the retained macOS live root. All Local-owned reports, D's original archive/byte parts, and A–D/R02/H1 evidence are unchanged.

D result/index/archive SHA-256 remain:
- `1d24e6ccfce7cd9f8e77cd51ca0afc1d5eb3ce5a8f8af5fba60cfccf9e6d1844`
- `b7bbe6d66c3c398db0fb504679cf560226aad4e044fe8a3ef04ccff3fc01e08b`
- `989d7211e1772efc2b20f13b5354e533bc4760adf93fa4a45b1d5176ed17ff53`

## R03-LD-001: select identity at production, not by global hash search

The old verifier searched recursively for an installation-receipt hash and required exactly one match. Generation legitimately copied the same receipt from the installed SDK to the stripped-AOT output project. Equal content identifies receipt bytes, not the native root that the build producer inventoried. D's canonical SDK matched installedAfter; the generation copy differed in MethodBridge.cpp. Neither is an unexpected file that should be deleted.

Selection: extend the diagnostic **build receipt to schema 2**, adding `installedNativeRoot`. The producer records `Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp"))` immediately after installation, before it inventories/copies/generates anything. The runtime manifest, BuildConfig, errors/warnings and Player protocols are unchanged.

The verifier requires that recorded root to be the supported installed SDK for the exact batch/role, under `HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp`. This profile is derived from the pinned package's SettingsUtil.cs, Git blob `014b8f3f62be45f58f15f150032a9e2d0a65cc30`, not a directory-search preference. Relative, traversing, noncanonical, linked, different-batch and different-role roots are rejected. Even an identical copied inventory outside that canonical root is rejected.

The selected installation receipt must match its hash, PinnedLocal mode, Unity version, target, prepared source-pin document and complete four-repository tuple. The package revision is verified separately. Exact installedAfter membership/size/hash, the unchanged install receipt in both inventories, additive diagnostic probe and non-generated preservation remain enforced. Only the existing four generated exceptions are permitted. File and directory symlinks, duplicate inventory entries and unexplained additions fail closed. Existing Player inventory, source/config/overlay and ARM64 checks remain; verification repeats before each Player launch.

The successful build cell emits `nativeBinding` with the checked path, receipt hash, source pins, tuple and file count. The production verifier does not recursively discover copies, choose a first matching hash, reinterpret a schema-1 receipt, modify generated copies or reuse D's apps.

Alternatives rejected: accepting the first hash match would confuse the two native snapshots; accepting any root with a matching inventory would lose role/root authority; deleting legitimate copied receipts would hide evidence rather than fix identity.

## R03-LD-002: explicit scope, not skipped-result tolerance

Selection: retain all **754 executable cases** observed in the pinned package and exclude exactly `HybridCLR.Editor.AssemblyShadow.Tests.ResourceAbiTests.FrozenDemoResourcesUseActualScriptGuidsAndOnlyAffectedBundles`. The isolated project lacks the frozen VersionedPrefab, Business scene and VersionedData assets. This is a scope decision for the focused batch, not an implementation of that missing fixture.

An anchored, escaped negative full-name `-testFilter` excludes only that identity. All other resource tests remain selected. Unity Test Framework 1.1.33, already pinned in the project, documents full-name regular expressions and `!` negation: https://docs.unity.cn/Packages/com.unity.test-framework@1.1/manual/reference-command-line.html . This external reference supports invocation syntax only; it is not execution evidence.

The immutable D XML (Git blob `74da7de9e99e79aae01365f2c3dea5e49f812ef5`, SHA-256 `4d43e1f3722965af9d0284bac6b774bd773181a7a5b35670750c690d8a5f9163`) is used solely as a name catalog. Its bytes and the package revision are pinned. The next run must produce exactly the 754 selected full names with no duplicates, substitutions, skipped cases, ignored labels, failures or inconclusive cases. Aggregate Passed and consistent counts are required. All 35 exact R03 parameterized cases and the true target-cycle test are mandatory; substring matching is no longer sufficient.

`editor-scope.json` is written before launch. `editor-verification.json` records success/failure and explicitly retains the single excluded case as **NoCoverage**. Any newly present frozen asset requires scope review. The original unfiltered D XML still fails the new verifier; a synthetic filtered projection is only a host contract test and is labeled accordingly. No new Editor execution is claimed from a transformed XML tree.

Alternatives rejected: accepting Skipped:Ignored would silently tolerate future missing required tests; narrowing to only 36 mandatory cases would unnecessarily discard 718 executable regressions; inventing replacement M01 assets/GUIDs would not establish frozen-resource compatibility. The real M01 resource contract and broader old-resource coverage remain required before full R03/H2 review.

## Tests, source and diagnostic changes

Implementation commit: `1b89581a802a660057fd507f4deb65f060b29669`.
Final tested source anchor: `979abd80b673e690c5f82819ed194200f8d2e536`.

- `PlayerProject/R03Build.cs`: schema 2 and explicit actual installed root; no runtime semantic change.
- `build_provenance.py`: canonical identity, exact inventories, source tuple and preservation checks.
- `editor_scope.py`: hash-pinned exact scope, strict current-XML verification and explicit NoCoverage.
- `run_local.py`: integrations, success/failure diagnostic records; original 36 cells/dependencies and nineteen Player cases unchanged.
- `test_build_provenance.py`, `test_editor_scope.py`: **49 new tests**. These exercise duplicates/copy rejection, mismatched roots/roles/pins, traversal/symlinks, missing/tampered/extra native files, actual Batch verifier integration with a synthetic app, and strict positive/negative Editor identity/skip/aggregate cases. Synthetic inputs are not runtime evidence.
- `run_host_provenance.py`: read-only audit of the published D receipt-copy/role facts and the exact name catalog; rejects the original ignored result without reclassifying it.
- `run_host_lifetime.py`, `.github/workflows/r03-primary.yml`: execute all **116 tests**, prior managed regressions and the new read-only audit on Linux and macOS.

The new test audit initially imposed candidate inventory counts on the reference core. First host run `36925913478` caught that assumption. The correction in `979abd80...` authenticates each role's own receipt/inventory and exact added probe. Recorded candidate counts are 965→966; reference counts are 964→965. The production verifier never imposed those fixed counts. Neither the historical records nor the required runtime/Editor expectations were changed to conceal that host-test failure.

## Completed Primary validation

Final host workflow **36926248759** passed on Linux x86_64 and macOS 15.7.9 arm64 using SDK 8.0.318. Each passed 116 Python contracts, both 9-case graph suites, all 35 admission/method contracts, 15 generated Player DLLs, 33 fixture audits/consumers, actual Runtime API compilation and shared compiler success/failure lifetime checks. Each retained **49 positive and two expected-negative owned command completions**, all without survivors. The provenance/scope audit passed against the four published D artifact receipts and the real 754-name catalog.

Final pinned-Unity API workflow **36926248750**, job **110584176565**, compiled the three actual package dependencies and complete updated helper using the official Unity 2022.3.62f2 compiler/API bytes. The helper emitted no compiler errors or warnings. The unchanged C helper still produced exactly two CS0266 errors and no output DLL. Four positive plus one expected-negative compiler command completed cleanly. This remains compiler-only evidence: no Editor/IL2CPP/Player execution was performed by Primary.

Updated helper source SHA-256: `46f448196ceb69570be3d1fca87c0c811d40122498da7f007eb0bce46f9d604b`; emitted DLL `5da3810b498ebb659f1c421615dc6465625cd87fb7c15389c2babf97571151c5`, 13,824 bytes. The actual CoreModule remains `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. Package sources remain unchanged; their existing CS0649 warnings are retained, not silently suppressed.

| Evidence | Workflow / artifact | ZIP SHA-256 | Exact membership |
| --- | --- | --- | --- |
| Linux host | 36926248759 / 11194471090 | `0ba217af0638e58aced3334add098a3fd8969bfa43b69ae36246434f79d6cafe` | 629 indexed / 630 ZIP files |
| macOS host | 36926248759 / 11193902947 | `c54777f8fd96a7a23b237849281f708a91dbd12ee761524a254865a62ec001f6` | 629 indexed / 630 ZIP files |
| Pinned Unity API | 36926248750 / 11194331920 | `f0a009e6b471110b3b38250c32a04faafae123eb7630f698137db621eac4e227` | 28 indexed / 29 ZIP files |

Primary downloaded and authenticated all three final ZIPs: exact safe/nonduplicate membership, every indexed size/hash, command stream hashes, result/source identities and relevant outputs. F_HOST_EVIDENCE.json contains the structured audit, role counts, NoCoverage scope and command/result/ZIP bindings. Artifacts expire on 2026-10-15 in GitHub; retained downloaded copies are separate from D's Local seal. The current Linux container also passed all 116 Python tests; actual SDK/Unity compiler execution occurred in CI, not in that container.

## Review disposition, handoff and limits

R03-LD-001: **source repaired and host-validated; new integrated native-root validation required**. R03-LD-002: **explicit focused-scope correction implemented and host-validated; actual filtered Editor run required**. The frozen M01 fixture itself remains unavailable/NoCoverage. This self-review is not an independent stage review or gate approval.

Four feature refs were read through the Connector at entry. Only demo changes in this repair; external pins remain `041c0cbb42d3e64e54fe605673d99799b5d63893` / `120bb01be680cec0375002a0823552d66d34b84c` / `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`. A new demo Connector smoke passed on `codex/connector-smoke-r03-provenance-20261001`, commit `94ce2f9c26a57996bb144c9a8b1d6df19855402d`, with exact remote read-back. Earlier external write-smoke records remain historical; fresh reads confirm their unchanged pins. No delete-ref operation is exposed; the disposable smoke branch remains non-authoritative.

Next root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001E-provenance`. Local follows the final pushed WEB_TO_LOCAL.md tuple, executes the prepared batch once, publishes evidence and stops. No non-trivial implementation is delegated. Fresh schema-2 builds, all 754 scoped Editor cases and nineteen Players are still required; D's apps must not substitute for them.

Rollback is a new coherent Primary-controlled source/handoff revision, never modification of previous results or reuse of mixed-source binaries. Full R03 legacy/resource, broader generic/interface/delegate/stack-trace, performance/memory/capacity, PureInterpreter qualification and independent review remain open. R03Accepted=false; H2Passed=false; expansion disabled. R02 deferred CPU and original H1 RSS risks remain visible through H2.
