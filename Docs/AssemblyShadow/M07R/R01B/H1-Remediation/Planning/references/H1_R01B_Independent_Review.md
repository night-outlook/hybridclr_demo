# Independent H1 review — Assembly Shadow R01B

**Recommendation: BLOCKED. R02 must remain stopped.**

Review date: 2026-09-10. This is a read-only, commit-pinned independent source review with an **incomplete evidence-authentication audit**. It is not a completed verification of the archived native/Player results, and it does not grant H1 acceptance.

The blocking condition is inability to obtain and authenticate the evidence archive bytes in this review environment. I also independently confirmed both disclosed count-narrowing defects. Those defects require correction or a specific human decision accepting a restricted input scope; inheritance from an earlier version is not, by itself, an acceptance argument.

## 1. Reviewed identity and method

| Repository | Exact reviewed commit |
|---|---|
| night-outlook/hybridclr_demo | `9534c7c775d69b79ecd612917231bef3d202a5aa` |
| night-outlook/hybridclr | `67f80ac01c15004ed9d2f0c884d0d92141d1019a` |
| night-outlook/hybridclr_unity | `c7ed6d244a2c3a8e948f062d5431c289e1369650` |
| night-outlook/il2cpp_plus | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

The reviewed scope began with [H1 gate rules, lines 12–26](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md#L12-L26), [H1 boundary, lines 67–83](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md#L67-L83), the associated design/plan and validation matrix, and the [final H1 handoff](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/H1-handoff.md#L1-L13). Critical source paths were then inspected in all four pinned repositories. This was a bounded source inspection, not an exhaustive proof of every generated-code consumer, every native build configuration, or every transitive source dependency.

GitHub comparison confirms that candidate `9d51767df790e16c7b36eed59e410c0cd0fd9921` to final demo `9534c7c...` adds only `H1-handoff.md` and `R01B-final-stage-review.json`. Comparing recorded demo executable `9b04fb9f3578a55f50915b914d0071234441289d` to the final commit shows documentation/evidence changes and `ProjectSettings/AssemblyShadowSourcePins.json`, not executable-source changes. This supports source continuity, but does not authenticate the executable that produced any receipt.

Comparison references: [candidate → final](https://github.com/night-outlook/hybridclr_demo/compare/9d51767df790e16c7b36eed59e410c0cd0fd9921...9534c7c775d69b79ecd612917231bef3d202a5aa); [recorded executable → final](https://github.com/night-outlook/hybridclr_demo/compare/9b04fb9f3578a55f50915b914d0071234441289d...9534c7c775d69b79ecd612917231bef3d202a5aa).

No branch, commit, merge, push, or R02 implementation was performed. No Unity, Player, native-suite, or project Python-suite execution was performed by this review.

## 2. Evidence authentication: what was and was not established

The published evidence directory and selected index entries were readable through the GitHub connector. The archive entry is reported as 86,092,066 bytes. The expected hashes below agree with the declared review/index metadata; **neither is a locally recomputed digest in this review**.

| Artifact | Expected SHA-256 | Independent byte authentication |
|---|---|---|
| `r01b-v6-evidence.tar.gz` | `d50193ad9e5ebe93998b6d5d412d32696a57925f4b05b55de91027011f0bd0d9` | Not completed |
| `evidence-v6-index.json` | `e82126f75efb96a83b51caa3c2d2b1cdbedb2b34ca2351c8871cfb3cf3711606` | Not completed |

Direct checkout/network retrieval failed in this environment; web retrieval was disabled. The GitHub read connector supplies text/metadata but not repository archive bytes. Its supported Actions-artifact route could not help: the branch query returned no workflow runs. These are **reviewer access limitations**, not proof that an archive hash is wrong or that the author failed to publish evidence.

Consequently I did not independently establish the advertised 329-member set, every member size/hash, duplicate/path-alias absence, transitive dependency hashes, installed-source identity, build flags, native binary hashes, or raw assertion outcomes. The previous review's “329 verified” and the finalizer's artifact counts remain **reported claims**. See [index header and selected member mappings](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/Evidence/evidence-v6-index.json#L1-L160) and [prior final-stage review record](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/R01B-final-stage-review.json#L1-L47).

Local absolute paths were treated as capture locators. For example, an ordinary-capacity launch receipt is mapped to `capacity/_temp/AssemblyShadow/R01B-v6-capacity-ordinary-1/r01b-capacity-player-launch.json`; its absence at a local `/Users/...` path is not a missing-evidence finding.

The archived `current-status.json` is the frozen pre-review snapshot. The separate final review and H1 handoff supersede it for review status. I did not treat its earlier pending state, or historical failed diagnostic records, as a current-candidate failure.

## 3. Findings, ordered by severity

### H1-B01 — BLOCKER: the central runtime evidence has not been independently authenticated

**Location:** [pinned index and archive mappings](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/Evidence/evidence-v6-index.json#L1-L160); [recorded authentication claim](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/R01B-final-stage-review.json#L1-L47); [H1 gate rules, lines 12–26](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md#L12-L26).

**Failure scenario:** An outdated or mismatched executable, a different set of DLLs, a wrong selected launch, incomplete raw results, or a stale dependency could be mistaken for proof of this candidate when only summaries and declared hashes are inspected. This review has not established that any such mismatch occurred; it cannot rule one out by authenticating the archive.

**Required correction to the review process:** Obtain the exact archive and index bytes in an isolated read-only audit environment. Recompute both SHA-256 values, enumerate the archive, reject unsafe/duplicate members, match every indexed member's size/hash, resolve receipt references through the index, and independently recompute the required raw outcomes. Verify the source → installed source → build → native library → selected launch → raw result chain, including ON/OFF and diagnostic/production distinctions.

This is an evidence-access blocker, not a code-regression verdict. A prior PASS summary cannot close it.

### H1-H02 — HIGH: method parameter count is checked after narrowing

**Location:** [InterpreterImage.cpp, lines 1781–1805](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L1781-L1805); the destination is a `uint16_t` field in [Native metadata count fields, lines 50–180](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/GlobalMetadataFileInternals.h#L50-L180).

`actualParamCount` is assigned to `md.parameterCount` before the `>= 256` rejection. An actual count of 65,536 therefore narrows to zero; 65,537 narrows to one. The subsequent guard examines the wrong value. Counts from 256 through 65,535 do hit the guard; the specific problem is wraparound before validation.

**Failure scenario:** An over-limit method signature can evade this rejection and leave method metadata inconsistent with the accumulated parameter vector, potentially producing wrong reflection/invocation behavior. This is a source-derived counterexample, not an executed loader reproduction. I do not claim that the declared bounded corpus exercised it.

**Required correction:** Validate the wide count against 255 before assignment and perform checked conversions for related extents. Exercise actual loader fixtures at 255, 256, 65,535, 65,536, and 65,537 in Debug and Release. Assert rejection before publication, correct retained reservation accounting, and preservation of previously published mappings.

**H1 disposition:** Explicit human risk acceptance is possible only for a genuinely restricted, audited input corpus or an enforceable pre-admission shape boundary. A 32 MiB size limit alone does not enforce the parameter limit. Merely documenting “0..255 supported” does not prove safe rejection above 255. Without the restriction or a correction, do not accept a broad DLL-loading guarantee.

### H1-H03 — HIGH: nested-child count wraps before validation

**Location:** [InterpreterImage.cpp, lines 2052–2085](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L2052-L2085); `nested_type_count` is also a 16-bit field in [Native metadata count fields, lines 50–180](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/GlobalMetadataFileInternals.h#L50-L180).

The code increments the narrow counter. At 65,536 children it becomes zero. A following child can enter the zero-count branch and start a new group, overwriting the enclosing type's grouping start. Later checks include an assertion and another narrowing conversion; those do not constitute release-safe pre-overflow validation.

**Failure scenario:** An over-limit declaring type can obtain a zero/truncated child count or inconsistent grouping, affecting nested-type metadata/enumeration. Debug assertion behavior is not equivalent to a controlled loader rejection. Again, no real over-limit loader reproduction was executed here.

**Required correction:** Accumulate in a wide type, reject a count above 65,535 before increment/projection, and only then populate the ABI field. Test 65,535/65,536/65,537 children and multiple/interleaved declaring types in Debug and Release, with publication and ledger assertions.

**H1 disposition:** Same bounded-input decision as H1-H02. These are inherited defects, but inheritance does not establish harmlessness.

The [workload-shape summary](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/workload-v6-shape-audit.json#L38-L71) reports zero signature parameters and zero nested children for the ordinary corpus; the listed patch maxima are three parameters and fourteen nested children. That could substantiate exclusion of these counterexamples from the selected corpus once its raw hashes/shape audit are authenticated. It does not substantiate either advertised upper boundary or over-limit rejection.

### H1-M04 — MEDIUM: the performance conclusion must remain narrower than the functional conclusion

**Location:** [normative regression/exit criteria](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01B-metadata-index-expansion.md#L38-L51); [performance and workload qualifications](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/R01B-report.md#L26-L32).

The normative plan asks for measured performance relative to the old profile. The delivery reports a historical R00 comparison with 48 timing cells, but no equivalent R01 Player timing baseline. Those are not the same claim.

**Failure scenario:** Changes in startup flow, instrumentation, harness, build conditions, or other runtime revisions are attributed to the index codec; total capacity-probe load time is interpreted as codec/load cost even though it includes I/O, hashing, invocation, validation and memory sampling.

**Required disposition:** Authenticate the comparison and identify the old profile, matched operations, builds and confounders. A historical R00 comparison may satisfy a deliberately descriptive old-profile comparison; the plan does not explicitly require an otherwise-identical R01 baseline. It does not isolate the R01B regression. A stronger performance claim needs a controlled comparison. The human decision must acknowledge any remaining causal/comparability uncertainty.

The absence of Release/P99 certification or a calibrated RAM threshold is not, by itself, an H1 blocker: no such threshold is specified by the declared H1 workload, and broader platform/production qualification is assigned later. Missing authenticated comparison evidence is still uncovered under H1-B01.

## 4. Source trace and independent arithmetic

### Encoding, sentinels and AOT compatibility

The inspected representation uses negative signed-32-bit tokens for interpreter coordinates and keeps nonnegative AOT/raw indices intact. `-1` is excluded by the interpreter-index classifier. The sparse codec excludes the whole final page, not merely the sentinel value. See [index classifier and identities](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/MetadataUtil.h#L91-L125), [AOT/sentinel adapters](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/MetadataUtil.cpp#L29-L67) and [Codec constants, lines 27–35](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexCodec.h#L27-L35).

Independent arithmetic from those constants gives 524,287 usable pages and a 393,215-page charged ceiling. The protected free margin is 131,072 pages, or **25.0000477%**. The highest usable encoded value is `0xffffefff` (`-4097`); values `-4096..-1` are outside usable page allocation. Image IDs are stable records `1..8192`, not a direct “13-bit nonzero image ID” field.

Range helpers decode raw coordinates, validate owner/range, then perform arithmetic. This avoids assuming adjacent sparse encoded pages are arithmetically contiguous. See [checked raw-coordinate helpers](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataRange.h#L37-L126) and [offset/difference and publication checks](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexCodec.h#L508-L580). I have not independently verified every generated-code consumer or the archived large-AOT/random-boundary executions.

### Lifetime accounting and failure

The codec checks batch reservation limits before committing ledger changes; sealing accounts for low-range demand and already-bound sparse pages before publication. Abort does not refund IDs or credits. Runtime records and mappings are retained for process lifetime. Ordinary load and Shadow reservation use the same runtime allocator, rather than independent budgets. See [reservation and finalization](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexCodec.h#L184-L307), [Abort](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexCodec.h#L588-L603), and [shared allocation entry points](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L73-L130).

The ordinary loader establishes a reservation guard before fallible image construction; the Shadow abort path seals all reserved IDs, including reservations without a completed image. See [ordinary private construction/publication](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/Assembly.cpp#L156-L239) and [transaction Abort semantics](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/AssemblyShadow.cpp#L1142-L1185). These are positive source observations, not a replay of the failure-injection evidence.

Using the **reported**, not independently observed, workload counters:

| Workload | Charged identities | Reserved / mapped pages | Free pages | Free percentage |
|---|---:|---:|---:|---:|
| Ordinary | 8,192 | 16,388 / 16,388 | 507,899 | 96.8742311% |
| Mixed | 8,184 + 5 + 3 = 8,192 | 16,392 / 16,389 | 507,895 | 96.8734682% |

The arithmetic is consistent. The mixed three-page reserved/mapped difference is consistent with three retained, unmapped reservation credits. Valid mixed DLLs number 8,189; their mean is approximately **65,560.009 bytes**, not 64 KiB. The 12 failed-input bytes are additional to 512 MiB of valid DLLs. None of this arithmetic authenticates the raw runtime counters. Counter source: [reported measurements](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/runtime-v6-acceptance.json#L139-L183).

### Private visibility, atomic publication and stale mappings

The codec's per-image lifecycle stores alone would not prove atomic group visibility. The runtime adds a group-active release store and, for Shadow images, an active-world visibility check. The VM then publishes one `ActiveSnapshot`; module initializers run after publication. Post-publication failure becomes `FailedAfterCommit`, not baseline rollback. See [public visibility gate](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp#L41-L65), [publication group](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp#L226-L251), [active publication callback](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/AssemblyShadow.cpp#L548-L585), and [commit/initializer sequencing](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/AssemblyShadow.cpp#L1050-L1140).

The private-visibility walker follows arrays, constructed generics, generic parameters and declaring/element types. It uses retained token provenance to identify private metadata after failure without granting permission to decode it. See [private/retained type visibility](https://github.com/night-outlook/il2cpp_plus/blob/6be7f38bec2fa4677d24efc1a4a1294240789933/libil2cpp/vm/AssemblyShadowVisibility.cpp#L17-L192). I found no additional confirmed partial-publication defect in these inspected paths; concurrency/native/Player proof remains unauthenticated.

### Metadata growth and raw bounds

Finalization accounts for table endpoints, synthesized vectors and future lazy type growth. Attribute accounting charges blob length per row occurrence, not just per distinct blob offset. See [final footprint calculation](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/InterpreterImage.cpp#L301-L354).

The inspected blob readers validate bounds in runtime code, but some raw string/image-offset/default-value accessors still rely on assertions or unchecked pointer formation. See [raw accessors and bounded blob paths](https://github.com/night-outlook/hybridclr/blob/67f80ac01c15004ed9d2f0c884d0d92141d1019a/hybridclr/metadata/RawImageBase.h#L73-L175). This supports a **selective hardening** conclusion, not a blanket malformed-DLL safety claim. It is not an executed new exploit/reproduction. The normative validation matrix assigns broad malformed-metadata fuzzing to M11; these residual limits must not be silently converted into universal H1 loader safety.

### Profile/ABI, installed sources and ON/OFF

Managed capability negotiation reads live native options, requires the exact version, and only falls back on a narrowly recognized legacy unknown-option exception. Its legacy parser requires explicit capability fields. See [capability negotiation](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Runtime/AssemblyShadow/AssemblyShadowDiagnostics.cs#L85-L148) and [guarded additive APIs](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs#L154-L219).

The profile-2 builder hashes the installed codec header and checks it against the install receipt and pinned native revision. Baseline construction verifies its snapshot/native artifact and includes the profile in the manifest. See [installed codec binding](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Editor/AssemblyShadow/Build/MetadataCapacityPlanner.cs#L92-L140) and [baseline artifact/profile binding](https://github.com/night-outlook/hybridclr_unity/blob/c7ed6d244a2c3a8e948f062d5431c289e1369650/Editor/AssemblyShadow/Build/ShadowBaselineManifestBuilder.cs#L12-L78). Header identity is not proof that every compiled native source was correct; the wider build/installed-source receipt chain still needs audit.

Native options distinguish feature-OFF from available metadata/recovery capability. The claimed OFF Player regression and immutable old-Player rejection require their actual launches/results; managed negotiation source alone cannot prove them.

## 5. Requirements → source → evidence coverage

“Source supported” below means the specified mechanism was inspected, not that the requirement has passed.

| Requirement / H1 area | Inspected source | Relevant claimed evidence | Independent disposition |
|---|---|---|---|
| Fixed four-repository identity and installed provenance | Commit comparisons; installed codec/profile and baseline builder | Source inventory; production/diagnostic build receipts; installed-source hashes | Repository continuity partially checked; complete provenance unauthenticated |
| Signed encoding, sentinel, AOT/raw separation | Codec constants; MetadataUtil; range helpers | Native codec/runtime/range, large-AOT and parser-adapter suites | Source and arithmetic supported; execution unverified |
| Shared 8,192 lifetime image budget | Codec reservation; InterpreterImage; ordinary loader | Ordinary and mixed raw capacity runs | Source/probe supported; runtime counters unverified |
| Rejected preflight vs charged later failure | Reservation checks; guards; codec Abort; VM Abort | Three retained failures; native transaction/contention/startup tests | Source distinction supported; raw failure assertions unverified |
| No private or partially published mappings | Runtime group gate; ActiveSnapshot callback; visibility walker | Native visibility/transaction tests; startup/M07 modes | Inspected mechanisms supported; concurrency/execution unverified |
| Raw metadata offsets, blobs and FieldRVA | Bounded blob access; raw-coordinate adapters; capacity probe RVA reads | Parser suites; ordinary high-RVA checks | Selective source support only; no universal malformed-input proof |
| Dense/lazy growth, generics, arrays, interfaces, reflection and attributes | Final footprint calculation; lazy/dense probe | Reported 61 raw checks and native helper regressions | Probe is substantive, but 61 is an assertion count, not 61 independent stress workloads; results unverified |
| Parameter and nested-type limits | Actual loader assignments and 16-bit ABI fields | Shape audit; over-limit loader tests explicitly NotRun | Two source-confirmed defects; upper/over-limit runtime behavior not established |
| Profile-2 negotiation and old Player refusal | Managed live/exact capability negotiation; manifest/profile binding | Old-Player rejection receipt and selected launch | Source checks supported; rejection sequence/no-mutation outcome unverified |
| Feature-ON/OFF and M07 regressions | Capability/source paths inspected selectively | 11 startup modes; 14 M07 modes including OFF | Exact modes, no-skips status and raw outcomes not recomputed |
| Managed regression | Inventory and receipt references | 1,021 Editor tests; 492 fresh Python tests | Reported only; XML/log totals and freshness unauthenticated |
| R00/performance | Normative plan and disclosed measurement scope | Four R00 modes; 48 timing cells | Neither outcome count nor comparison authenticated; no isolated R01 baseline |
| Actual workload and >=25% free charged capacity | Capacity probe and independent arithmetic | 8,191/8,192 checkpoints, distinct 8,193 rejection, ordinary/mixed totals | Probe checks real loads/invocations; reported ledger arithmetic coherent; raw execution unverified |

Evidence cross-reference: [published runtime acceptance matrix](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/runtime-acceptance-matrix.md#L7-L22); [receipt index](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/runtime-v6-acceptance.json#L38-L137).

The capacity probe verifies actual `Assembly.Load`, per-DLL hashes/names, method results, FieldRVA bytes and selected post-rejection mappings ([Capacity probe, lines 90–232](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Assets/AssemblyShadowR01BDiagnostics/Runtime/R01BCapacityProbe.cs#L90-L232)). The lazy probe covers real reflection/generic/interface/array/attribute operations and optional dense adjuncts ([Lazy/dense probe, lines 45–207](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Assets/AssemblyShadowR01BDiagnostics/Runtime/R01BLazyProbe.cs#L45-L207)). Its overall pass can omit the optional dense adjunct, so the outer evidence audit must establish that the selected run actually includes two dense fixtures and the expected checks; the word “Passed” alone is insufficient.

## 6. Disposition of each declared limitation

| Limitation | H1 classification | Necessary condition / human decision |
|---|---|---|
| Method parameter narrowing and nested count overflow | **Requires explicit human risk acceptance, or fixes; blocks an unrestricted input claim** | Accept only authenticated, audited shapes/inputs with a credible restriction, or repair and add actual boundary/counterexample runs. Do not equate inheritance with safety. |
| Native-v6 reuses v5 executions | **Consistent with H1 in principle; authentication still required** | Verify all relevant transitive source, generated files, harness, flags, compiler and raw-result identities. Metadata-only changes may be excluded only with a reasoned audit. Do not count reuse as fresh v6 execution. |
| Development-only descriptive timing; no equivalent R01 baseline | **Explicitly bounded acceptance / performance risk** | Authenticate the historical comparison and acknowledge confounders. Obtain controlled timing before claiming an R01B-specific performance regression bound. Do not fabricate a Release/P99 result. |
| No calibrated RAM threshold | **Consistent with the stated H1 boundary** | 512 MiB is DLL input, not a RAM budget. Preserve actual memory observations and avoid asserting device fitness. A separately required memory SLO would change this conclusion. |
| One Shadow transaction per process | **Consistent with this acceptance boundary** | Keep Abort/reload/retry semantics terminal as declared. The mixed five-image transaction does not validate multiple transactions or successive live versions. |
| Broader platforms and workloads excluded | **Consistent with H1, not production qualification** | Restrict acceptance to the identified macOS arm64/Unity build and workload. M10 and later gates must qualify larger real-business closure shapes, platform/build variants and production concerns. |

The native reuse record explicitly describes exclusions and non-fresh status: [native-v6 reuse audit](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Docs/AssemblyShadow/M07R/R01B/native-v6-validation.json#L1-L58). These exclusions are plausible audit hypotheses, not independently authenticated results here.

## 7. Missing or unverifiable evidence

Unavailable to this review: the archive bytes and complete member validation; original Editor XML and Python log bytes; selected startup/M07/R00/old-Player and capacity/lazy raw results; native-v5 raw executions and their transitive provenance; installed native/generated-source manifests and native-library/build-to-launch pairing.

Explicitly **NotRun**, not merely inaccessible: the disclosed actual over-limit method-parameter and nested-child loader counterexamples. Not claimed: equivalent R01 controlled Player timing, Release/P99 qualification, calibrated RAM acceptance, repeated Shadow transactions, or broader platform/workload qualification.

The archive index excludes Player/native binaries and workload DLLs themselves. That is not automatically an invalid evidence package: complete immutable receipts, hashes and raw outputs can support an archival review. It does limit independent re-hashing of those executable/input bytes without the separately retained artifacts. Authentication of a receipt is not direct byte verification of an excluded binary.

No raw test failure, archive hash mismatch, or provenance mismatch was observed in this review. That means **not established**, not “all passed.”

## 8. Precise human decision before R02

**Current decision: keep H1 unpassed and R02 stopped.**

First close H1-B01 with a genuine independent byte/member/provenance/raw-result audit at these exact pins. Preserve the frozen status snapshot and append the new review rather than rewriting historical evidence.

Then decide explicitly between correcting H1-H02/H1-H03 and re-running the affected tests, or accepting a precisely bounded residual risk: supported count limits, approved/audited input boundary, absence of over-limit certification, named follow-up owner and the next gate at which the deferral must be reconsidered. Separately accept only the justified scope of the historical performance comparison.

Only after that may the human record `Passed` or `PassedWithExplicitDeferredRisk`, bind it to the four commits and authenticated evidence, and authorize **R02 only**. The prior final-stage PASS, this source review, or a generic “risks noted” must not be substituted for that decision. The governing rule is [H1 gate rules, lines 12–26](https://github.com/night-outlook/hybridclr_demo/blob/9534c7c775d69b79ecd612917231bef3d202a5aa/Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md#L12-L26).

A conditional future pass is not the verdict of this review. **The present recommendation remains BLOCKED.**
