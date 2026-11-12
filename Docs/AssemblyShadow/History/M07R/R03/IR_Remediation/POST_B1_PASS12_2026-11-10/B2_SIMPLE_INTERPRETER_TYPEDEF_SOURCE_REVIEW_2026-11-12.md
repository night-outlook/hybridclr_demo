# R03 B2 — Simple interpreter TypeDef source implementation and review

Date: 2026-11-12 UTC. Scope: Primary Implementation only, inactive B2 original-V1 execution field15 source. Native commit: night-outlook/il2cpp_plus@90206c7b4abdbf756c8fb1f2c353fcdf78a792e6; demo source/test anchor: night-outlook/hybridclr_demo@46ea3a35c3a89f9c0ab25ef8b7a0d51e575f2833. Unchanged forks: hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, all on codex/assembly-shadow-r01b-h1. The original V1 getter, B1 and active Player behavior are unchanged.

## Design and original semantics

The actual original V1 GetExecutionDiagnosticsJson obtains token-valid **physical** assemblies from CaptureShadowEnumeration, inserts metadata handles into an image map via unordered_map::emplace (**first handle owner wins**), and calls FormatMetadataOnly on each registered class's byval_arg. Original FormatType accepts IL2CPP_TYPE_CLASS / IL2CPP_TYPE_VALUETYPE metadata definitions regardless of physical image kind, but explicitly rejects VAR/MVAR open execution keys when a metadata image map is present. The current GlobalMetadata::GetAssemblyTypeHandle delegates interpreter-image handles to MetadataModule::GetAssemblyTypeHandleFromRawIndex. These are concrete native source facts, not proof of live Unity interpreter class lifetime.

The earlier bounded producer rejected every physically matched interpreter class even when the original V1 getter could serialize a simple TypeDef. This change implements exactly one additional shape: a physically registered plain interpreter CLASS or VALUETYPE TypeDef with no constructed generic, generic-container, declaring class, rank or qualifiers. Interpreter generic/nested/composite/VAR/MVAR sources remain unsupported.

## Production source changes

1. Discovery continues to require independent registered AOT image admission for AOT classes. For matched interpreter classes it instead requires inclusion in the independently visited ORIGINAL token-valid physical V1 image inventory. The same initial metadata Reader, g_MetadataLock, registered execution identity and witness checks remain in force.
2. For the simple interpreter root only, resolveOwner scans the constrained original physical image for the exact metadata handle within the existing 65,536 lookup budget. The separate original V1 first-emplace owner check then rejects an earlier competing image. Unconstrained generic arguments still use registered AOT image owners exclusively.
3. Before metadata generic-container or declaring-type lookup, interpreter roots reject non-invalid genericContainerIndex or declaringTypeIndex. The existing canonical Unicode folding, declaration formatting, class-fact three-pass reads and original V1 JSON serializer are reused.
4. Only a successful owned row may set usedSimpleInterpreterDefinition in the bounded receipt; all rejection paths clear it and revoke rows and record. This field does not establish complete field15, metadata provenance, GC lifetime, whole-VM epoch, or terminal-safe V2.

Native files: libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl; libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h; NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp; .github/workflows/r03-native-b2-definition-live-source-host.yml. The native code remains inactive with no Player caller.

## Source tests and chronology

Seven new host-mode scenarios: two positives (simple interpreter class and value-type definitions); five negatives (unowned/unknown metadata handle, generic definition, nested definition, original first-owner alias, interpreter image absent from original V1 registry). The existing CrossImageInterpreter scenario still fails closed. Success checks the original serializer's actual physicalImageKind string value, not a fabricated physicalInterpreter JSON property; all failures revoke receipts and completed owned data.

The initial CI run 43205974322 failed because one newly written test incorrectly searched for a nonexistent physicalInterpreter JSON field. Actual original V1 uses physicalImageKind. No runtime serializer edit was needed; the fixture was corrected in commit 90206c7b4abdbf756c8fb1f2c353fcdf78a792e6. The corrected run is https://github.com/night-outlook/il2cpp_plus/actions/runs/43206145229. Its Ubuntu-24.04 C++11 and C++17 Release/Debug, strict/sanitized jobs are **Passed**, with 88 actual source-mock scenarios and 2,389 assertions per process. macOS jobs were still queued when this review was authored; treat the entire workflow as pending until completed.

Exact four-fork 63-native/eight-demo source admission is https://github.com/night-outlook/hybridclr_demo/actions/runs/43206474551 at demo code anchor 46ea3a35c3a89f9c0ab25ef8b7a0d51e575f2833: Ubuntu Passed, macOS queued at the report checkpoint. Source manifest and tests now pin all four updated native Git blob IDs, numeric coverage, true scope, and false overclaim booleans. A final documentation commit requires separate CI remote-HEAD verification.

## Independent Primary source review

INTP-01 — Scoped source PASS: exact original physical token-valid image and first-owner semantics are used for independently registered simple interpreter TypeDefs. AOT registered-image and generic argument paths remain separate; unsupported interpreter shapes fail without inventing empty rows.

INTP-02 — Real runtime NOT PROVEN: synthetic VM metadata readers do not prove actual HybridCLR staged metadata, class pointer allocation provenance, or Unity C++ full-TU/IL2CPP/Player behavior. No new real Player ran. A real original V1 nonempty byte comparison is still needed.

INTP-03 — Coverage INCOMPLETE: nested, constructed, generic/interpreter argument, and VAR/MVAR shapes remain unsupported. The restricted source also still needs at least one admitted registered AOT TypeDef image. It cannot represent complete V1 classes for arbitrary registries.

INTP-04 — Consistency/lifetime NOT PROVEN: initial Reader and g_MetadataLock plus three class-fact observations do not provide atomic GC/cctor/metadata lifetime or a whole-VM epoch; ABA and changes after the last sample remain possible. The original allocating getter itself is not a safe terminal capture.

INTP-05 — Resource and acceptance OPEN: interpreter root scans up to 8192 TypeDefs per image under a global 65536 lookup cap, but Unity latency/stack/GC/RSS and real metadata behavior are NotRun. Complete terminal-safe field14/finalDiagnostics, field15/finalExecutionDiagnostics, one-owner native V2 descriptor artifact/envelope, external identity-bound receipt and independent first recovery are missing. Historical B1 oneuse-12 focused 19/19 real Player PASS is consumed, and original independent R03 full-stage FAIL/High findings remain.

Next Primary: complete original execution registry/class-shape admission with a defensible VM/GC/metadata lifetime source boundary; only then freeze complete field14+15 and implement authenticated native V2 transport. Preserve Human Review Gate. No H2/M08A/X02/SNAP-01.

Flags: readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. Handoff: CLOSED / NO EXECUTION.
