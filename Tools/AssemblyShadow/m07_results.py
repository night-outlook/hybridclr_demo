"""Strict read-only M07 Unity-resource and Player acceptance gate.

The gate reopens every compiler, linked-Player, native-metadata, patch and
resource byte referenced by M07.  Receipts are unsigned evidence rather than
authentication; the separately bound Editor replay owns the complete dnlib and
Unity serialization-policy decision.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

import m02_results as resource_v2
import m04_results as prior
import m05_raw_type_admissions as raw_admissions
import m05_results as types
from shadow_tools import VerificationError, require, unique_object


CANDIDATES = prior.CANDIDATES
ORDER = prior.PROVIDER_ORDER
INTERNAL = prior.INTERNAL
CONTRACTS, EXTENSIBILITY, _, CONTRACTS_CONSUMER, EXTENSIBILITY_CONSUMER = CANDIDATES
BOOTSTRAP = "AssemblyShadowDemo.Bootstrap"
BUNDLES = (
    "additive-scene.bundle", "business-scene.bundle", "mixed-assets.bundle",
    "nested-prefab.bundle", "scriptable-object.bundle",
    "serialize-reference.bundle", "versioned-prefab.bundle",
)
ASSETS = {
    "additive-scene.bundle": ("AdditiveScene.unity",),
    "business-scene.bundle": ("BusinessScene.unity",),
    "mixed-assets.bundle": ("MixedAssets.prefab", "MonoScriptCarrier.asset"),
    "nested-prefab.bundle": ("NestedPrefab.prefab",),
    "scriptable-object.bundle": ("VersionedData.asset",),
    "serialize-reference.bundle": ("ManagedGraph.asset",),
    "versioned-prefab.bundle": ("VersionedPrefab.prefab",),
}
MODES = frozenset((
    "T07-01-Prefab-P01", "T07-02-Nested-P02", "T07-03-FullClosure-P03",
    "T07-04-UnityApis-P01", "T07-05-Scriptable-P03",
    "T07-06-SceneSingle-P01", "T07-07-SceneAdditive-P03",
    "T07-08-SerializeReference-P03", "T07-09-Messages-P01",
    "T07-10-Cache-P03", "T07-11-DelayedCatalog-P03",
    "T07-12-P04-NonSerialized", "T07-13-P05-Rebuilt",
    "T07-14-FeatureOff",
))
MODE_PATCH = {
    "T07-01-Prefab-P01": "P01", "T07-02-Nested-P02": "P02",
    "T07-03-FullClosure-P03": "P03", "T07-04-UnityApis-P01": "P01",
    "T07-05-Scriptable-P03": "P03", "T07-06-SceneSingle-P01": "P01",
    "T07-07-SceneAdditive-P03": "P03", "T07-08-SerializeReference-P03": "P03",
    "T07-09-Messages-P01": "P01", "T07-10-Cache-P03": "P03",
    "T07-11-DelayedCatalog-P03": "P03", "T07-12-P04-NonSerialized": "P04",
    "T07-13-P05-Rebuilt": "P05", "T07-14-FeatureOff": None,
}

MANIFEST_FIELDS = "schemaVersion milestone unityVersion target architecture baselineBuildId runtimeAbiHash baselineManifestPath baselineManifestSha256 baselineInputSnapshot baselineInputSnapshotHash playerBuildReceiptPath playerBuildReceiptSha256 candidateNames bundleNames stableAotNames stableAotProvenance stableAotProvenanceHash fixtures rejectedFixtures"
FIXTURE_FIELDS = "patchId defines changedRoots compileSnapshot compileSnapshotHash patchDirectory patchManifest patchManifestSha256 closureLoadOrder baselineResourceAbiHash resourceAbiHash resourceChangeLevel dllOnly resourceBundlesRequired assemblyIdentities replacementResourcePath replacementResourceReceiptPath replacementResourceReceiptSha256 replacementBundleNames"
REJECTED_FIELDS = "patchId defines changedRoots compileSnapshot compileSnapshotHash errorCode errorMessage"
PLAYER_FIELDS = "schemaVersion milestone variant baselineBuildId runtimeAbiHash unityVersion target architecture buildGuid playerOutput inputSnapshot inputSnapshotHash nativeLibraryPath nativeLibrarySha256 nativeArguments assemblyIdentities placeholderManifestPath placeholderManifestSha256 placeholderAssemblyNames nativeMetadataPath nativeMetadataSha256 nativeMetadataVersion nativeAssemblyIdentities nativeGeneratedAssemblyNames resourceBaselinePath resourceBuildReceiptPath resourceBuildReceiptSha256 resourceAbiHash bundleNames"
REPLAY_FIELDS = "schemaVersion milestone result comparisonPolicy fixtureManifestPath fixtureManifestSha256 baselineManifestPath baselineManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineInputSnapshotHash baselineBuildId playerBuildGuid nativeLibrarySha256 linkedPlayerReceiptHash runtimeAbiHash unityVersion target architecture stableAotProvenanceHash resourceBuildReceiptPath resourceBuildReceiptSha256 resourceAbiHash replayScratchPath validatorSourcePins fixtures rejectedFixtures"
REPLAY_FIXTURE_FIELDS = "patchId patchManifestSha256 compileSnapshotHash resourceAbiHash dllOnly changedRoots closureLoadOrder resourceBundlesRequired"
REPLAY_REJECTED_FIELDS = "patchId compileSnapshotHash errorCode errorMessage"
RESULT_FIELDS = "schemaVersion processId milestone mode result error unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineManifestPath baselineManifestSha256 patchId patchManifestPath patchManifestSha256 resourceReceiptPath resourceReceiptSha256 baselineResourceAbiHash selectedResourceAbiHash resourcePrecheckPhase il2cpp resourcePrecheckPassed commitCompletedBeforeResourceLoad businessResourceLoadStarted configureCode beginCode stageProbeCode validateCode commitCode abortCode stateCode state executionModeCode diagnosticsCode typeResolutionCode executionDiagnosticsCode nativeDiagnosticsJson rawDiagnosticsPath rawDiagnosticsSha256 unityPathJson monoScriptClass monoScriptAssembly graphType graphDescription serializedState lifecycleBefore lifecycleAfter sceneLifecycleAfter graphSum p04RuntimeValue p05SerializedValue baselineUseCount nativeEventCount transactionGeneration stageOrder checks stageResults snapshots bundles assets scenes typeResolutions cacheEvents assemblyModes"
RESOURCE_FIELDS = "schemaVersion provenance unityVersion target architecture compilerSnapshotPath compilerSnapshotHash compilerSnapshotIsPlayer compilerDefines editorScriptingDefines metadataAssemblyDirectory metadataAssemblies resourceAbiPath resourceAbiHash resourceAbiFileSha256 resourceIndexPath resourceIndexHash bundleDirectory candidateAssemblies buildMap bundles sources sourceSetHash scripts dependencies originalManifestPath originalManifestSha256 originalSourceAuditPath originalSourceAuditSha256 reconstructionProof"
PATCH_FIELDS = "schemaVersion semanticHashSchema patchId baselineBuildId baselineManifestSha256 unityVersion target architecture sourcePins runtimeAbiHash compileSnapshotHash reflectionBindingConfigurationSha256 reflectionBindingConfigurationHash reflectionBindings bootstrapAbiHash baselineResourceAbiHash resourceAbiHash resourceChangeLevel dllOnly resourceBundlesRequired resourceChangeReasons changedRoots loadOrder closure dependencyGraph deferredFacadeReferences unsigned signatureAlgorithm"
PATCH_ASSEMBLY_FIELDS = "name dll sha256 semanticHash mvid baselineMvid pdb pdbSha256 references"
CHECK_FIELDS = "name actual expected passed"
STAGE_FIELDS = "name code dllSha256 pdbSha256"
SNAPSHOT_FIELDS = "phase diagnostics"
BUNDLE_FIELDS = "name path sha256 assetCount sceneCount loaded unloaded"
ASSET_FIELDS = "phase bundle assetName typeName assemblyName marker serializedState active instantiated"
SCENE_FIELDS = "phase bundle scenePath componentType marker serializedState lifecycle loaded additive activationDelayed unloaded"
TYPE_FIELDS = "phase typeName assemblyName code executionMode rawJson sameType active"
CACHE_FIELDS = "operation typeName marker active distinctInstance"
ASSEMBLY_MODE_FIELDS = "name code mode expectedShadow"
RESOURCE_SOURCE_FIELDS = "path snapshotPath sha256 metaSnapshotPath metaSha256 guid builtin dependencies"
RESOURCE_SCRIPT_FIELDS = "path guid localId assembly namespace type"
RESOURCE_PROOF_FIELDS = "path sha256"
RESOURCE_BUNDLE_FIELDS = "name sha256 assets"
RESOURCE_MAP_FIELDS = "schemaVersion bundleDirectory bundles"
RESOURCE_MAP_BUNDLE_FIELDS = "name assets"
DEPENDENCY_FIELDS = "schemaVersion runtimeDependencies resourceDependencies bootstrapEntrypoints"
RUNTIME_DEP_FIELDS = "consumer provider kind evidence callSite"
RESOURCE_DEP_FIELDS = "bundle assembly"
BOOTSTRAP_DEP_FIELDS = "consumer provider typeName method reason callSite target"
PATH_RESULT_FIELDS = "marker componentType componentAssembly baseType baseAssembly interfaceType interfaceAssembly getComponentGeneric getComponentType tryGetComponent getComponents getComponentInChildren getComponentInParent interfaceComponent baseComponent addComponentGeneric addComponentType createInstanceGeneric createInstanceType createInstanceString instantiateExisting serializedState messageMarker p04RuntimeValue p05SerializedValue"
EDITOR_REPLAY_POLICY = "compiler-linked-policy-resource-abi-unity-assets:1"
STABLE_DOMAIN = "m05-stable-aot:1\n"

fields, array, boolean, strings = prior._fields, prior._array, prior._bool, prior._strings
digest, canonical, bound = prior.digest, types._canonical, types._bound_file


def exact(actual, expected, path):
    require(type(actual) is type(expected), f"{path}: typed value differs")
    if type(expected) is dict:
        require(set(actual) == set(expected), f"{path}: object inventory differs")
        for key in expected: exact(actual[key], expected[key], f"{path}.{key}")
    elif type(expected) is list:
        require(len(actual) == len(expected), f"{path}: array length differs")
        for index, wanted in enumerate(expected): exact(actual[index], wanted, f"{path}[{index}]")
    else:
        require(actual == expected, f"{path}: expected {expected!r}, got {actual!r}")


def integer(value, path, minimum=0, maximum=(1 << 63) - 1):
    require(type(value) is int and minimum <= value <= maximum, f"{path}: invalid exact integer")
    return value


def names(value, path):
    rows = array(value, path)
    require(all(type(item) is str and item and item == item.strip() for item in rows) and len(rows) == len(set(rows)),
            f"{path}: invalid or duplicate names")
    return rows


def hash64(value, path):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None, f"{path}: invalid SHA-256")
    return value


def resource_hash(value, path):
    require(type(value) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None,
            f"{path}: invalid resource ABI hash")
    return value


def json_text(text, path):
    require(type(text) is str, f"{path}: expected JSON text")
    try:
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(VerificationError(f"{path}: invalid numeric constant")))
    except (ValueError, TypeError) as error:
        raise VerificationError(f"{path}: invalid JSON: {error}") from error


def user_defines(values, path):
    controls = ("ASSEMBLY_SHADOW_REFLECTION_BINDINGS_", raw_admissions.PREFIX)
    return sorted(value for value in names(values, path) if not value.startswith(controls))


def artifact_tree(root):
    root = canonical(str(root), root, "artifact tree", True)
    result = {}
    for path in root.rglob("*"):
        require(not path.is_symlink(), f"{path}: symlinked evidence")
        if path.is_file(): result[path.relative_to(root).as_posix()] = digest(path)
    return result


def fixture_order(patch_id):
    if patch_id in ("P01", "P04", "P05"): return [INTERNAL]
    if patch_id == "P02": return [EXTENSIBILITY, INTERNAL, EXTENSIBILITY_CONSUMER]
    if patch_id == "P03": return list(ORDER)
    raise VerificationError(f"unknown M07 patch: {patch_id}")


def fixture_policy(patch_id):
    if patch_id == "P01": return ["ASSEMBLY_SHADOW_P01"], [INTERNAL], True
    if patch_id == "P02": return ["ASSEMBLY_SHADOW_P02"], [EXTENSIBILITY], True
    if patch_id == "P03": return ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_P03"], list(CANDIDATES), True
    if patch_id == "P04": return ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M07_P04"], [INTERNAL], True
    if patch_id == "P05": return ["ASSEMBLY_SHADOW_P05"], [INTERNAL], False
    raise VerificationError(f"unknown M07 fixture policy: {patch_id}")


def rejected_policy(patch_id):
    if patch_id == "P05-DllOnly": return ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_P05"]
    if patch_id == "P14-ClassRename": return ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M07_P14"]
    if patch_id == "P15-SerializeReferenceRename": return ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M07_P15"]
    raise VerificationError(f"unknown M07 rejected fixture: {patch_id}")


def expected_asset_map(variant):
    prefix = f"Assets/AssemblyShadowDemo/M07Resources/{variant}/"
    return {name: [prefix + leaf for leaf in ASSETS[name]] for name in BUNDLES}


def managed_player_inputs(snapshot, path):
    root_keys = ("schemaVersion", "kind", "unityVersion", "target", "architecture", "buildId",
                 "playerBuildSucceeded", "playerBuildFilterCaptured", "playerBuildOptions",
                 "normalHotUpdateAssemblies", "extraScriptingDefines", "sourcePins", "assemblies",
                 "references", "filteredAssemblies", "filteredAssemblyCapabilities",
                 "linkerExcludedAssemblies", "linkerExcludedAssemblyCapabilities")
    linked_keys = ("schemaVersion", "target", "architecture", "sourceDirectory", "protectedAssemblies", "assemblies")
    require(type(snapshot) is dict and all(key in snapshot for key in root_keys) and
            type(snapshot.get("linkedPlayerReceipt")) is dict and
            all(key in snapshot["linkedPlayerReceipt"] for key in linked_keys),
            f"{path}: incomplete managed Player projection")
    result = {key: copy.deepcopy(snapshot[key]) for key in root_keys}
    result["linkedPlayerReceipt"] = {key: copy.deepcopy(snapshot["linkedPlayerReceipt"][key]) for key in linked_keys}
    return result


def verify_compile_snapshot(root, expected_hash, baseline, path, expected_defines):
    root = canonical(str(root), path, "compileSnapshot", True)
    receipt_path = root / "assembly-snapshot.json"
    receipt = prior._obj(receipt_path)
    require(receipt.get("schemaVersion") == 1 and receipt.get("kind") == "CompilePlayerScripts" and
            prior._linked_claim_absent(receipt) and not (root / "LinkedPlayer").exists(),
            f"{receipt_path}: compile snapshot claims a linked Player")
    prior._pins(receipt.get("sourcePins"), receipt_path, baseline["sourcePins"])
    for key in ("unityVersion", "target", "architecture"):
        exact(receipt.get(key), baseline[key], f"{receipt_path}.{key}")
    prior._snapshot_files(receipt, root, receipt_path)
    exact(receipt.get("snapshotHash"), expected_hash, f"{receipt_path}.snapshotHash")
    exact(receipt.get("snapshotHash"), prior._snapshot_hash(receipt, root, receipt_path), f"{receipt_path}.snapshotHash")
    prior._reflection_snapshot(root, receipt, receipt_path)
    raw_admissions.verify_snapshot(root, receipt)
    exact(user_defines(receipt.get("extraScriptingDefines"), receipt_path), sorted(expected_defines),
          f"{receipt_path}.extraScriptingDefines")
    return root, receipt


def verify_resource_baseline(root, expected_abi, manifest, expected_defines):
    root = canonical(str(root), root, "resource baseline", True)
    receipt_path = root / "resource-build-receipt.json"
    receipt = prior._obj(receipt_path, RESOURCE_FIELDS)
    sidecar = root / "manifest.sha256"
    require(sidecar.is_file() and not sidecar.is_symlink() and sidecar.read_text(encoding="utf-8").strip() == digest(receipt_path),
            f"{sidecar}: missing or stale resource manifest sidecar")
    exact(receipt["schemaVersion"], 1, f"{receipt_path}.schemaVersion")
    exact(receipt["provenance"], "CompilePlayerScriptsAndBuildAssetBundles", f"{receipt_path}.provenance")
    for key in ("unityVersion", "target", "architecture"):
        exact(receipt[key], manifest[key], f"{receipt_path}.{key}")
    exact(receipt["compilerSnapshotPath"], "CompilerInputs", f"{receipt_path}.compilerSnapshotPath")
    exact(receipt["compilerSnapshotIsPlayer"], False, f"{receipt_path}.compilerSnapshotIsPlayer")
    exact(receipt["metadataAssemblyDirectory"], "ResourceAssemblies", f"{receipt_path}.metadataAssemblyDirectory")
    exact(receipt["resourceAbiPath"], "resource-abi.json", f"{receipt_path}.resourceAbiPath")
    exact(receipt["resourceIndexPath"], "resource-script-index.json", f"{receipt_path}.resourceIndexPath")
    exact(receipt["bundleDirectory"], "Bundles", f"{receipt_path}.bundleDirectory")
    exact(receipt["candidateAssemblies"], list(CANDIDATES), f"{receipt_path}.candidateAssemblies")
    resource_hash(receipt["resourceAbiHash"], f"{receipt_path}.resourceAbiHash")
    exact(receipt["resourceAbiHash"], expected_abi, f"{receipt_path}.resourceAbiHash")
    for key in ("compilerSnapshotHash", "resourceAbiFileSha256", "resourceIndexHash", "sourceSetHash"):
        hash64(receipt[key], f"{receipt_path}.{key}")
    exact(receipt["compilerDefines"], sorted(expected_defines), f"{receipt_path}.compilerDefines")
    editor_defines = names(receipt["editorScriptingDefines"], f"{receipt_path}.editorScriptingDefines")
    exact(editor_defines, sorted(editor_defines), f"{receipt_path}.editorScriptingDefines")
    require(set(expected_defines) <= set(editor_defines), f"{receipt_path}: compiler defines were absent from the fresh Editor domain")
    for key in ("originalManifestPath", "originalManifestSha256", "originalSourceAuditPath", "originalSourceAuditSha256"):
        require(receipt[key] in (None, ""), f"{receipt_path}.{key}: fresh build claims historical import evidence")
    exact(receipt["reconstructionProof"], [], f"{receipt_path}.reconstructionProof")

    build_map = fields(receipt["buildMap"], RESOURCE_MAP_FIELDS, f"{receipt_path}.buildMap")
    exact(build_map["schemaVersion"], 1, f"{receipt_path}.buildMap.schemaVersion")
    exact(build_map["bundleDirectory"], "Bundles", f"{receipt_path}.buildMap.bundleDirectory")
    variant = "P05" if expected_defines == ["ASSEMBLY_SHADOW_P05"] else "Baseline"
    expected_assets = expected_asset_map(variant)
    mapped = {}
    for index, row in enumerate(array(build_map["bundles"], f"{receipt_path}.buildMap.bundles")):
        rp = f"{receipt_path}.buildMap.bundles[{index}]"
        fields(row, RESOURCE_MAP_BUNDLE_FIELDS, rp)
        require(row["name"] not in mapped, f"{rp}: duplicate bundle")
        mapped[row["name"]] = names(row["assets"], rp + ".assets")
    exact(list(mapped), list(BUNDLES), f"{receipt_path}.buildMap.bundle order")
    exact(mapped, expected_assets, f"{receipt_path}.buildMap")

    bundles = []
    for index, row in enumerate(array(receipt["bundles"], f"{receipt_path}.bundles")):
        rp = f"{receipt_path}.bundles[{index}]"
        fields(row, RESOURCE_BUNDLE_FIELDS, rp)
        hash64(row["sha256"], rp + ".sha256")
        exact(row["assets"], expected_assets.get(row["name"]), rp + ".assets")
        physical = prior._rel(root, "Bundles/" + row["name"], rp, "bundle")
        exact(digest(physical), row["sha256"], rp + ".sha256")
        bundles.append(row)
    exact([row["name"] for row in bundles], list(BUNDLES), f"{receipt_path}.bundles")

    sources = array(receipt["sources"], f"{receipt_path}.sources")
    require(sources, f"{receipt_path}: resource source inventory is empty")
    exact(receipt["sourceSetHash"], resource_v2._resource_source_set_hash(sources), f"{receipt_path}.sourceSetHash")
    source_by_path = {}
    for index, source in enumerate(sources):
        sp = f"{receipt_path}.sources[{index}]"
        fields(source, RESOURCE_SOURCE_FIELDS, sp)
        strings(source, sp, "path snapshotPath sha256 metaSnapshotPath metaSha256 guid")
        boolean(source["builtin"], sp + ".builtin")
        require(source["path"] not in source_by_path, f"{sp}: duplicate source path")
        source_by_path[source["path"]] = source
        snapshot = prior._rel(root, source["snapshotPath"], sp, "snapshotPath")
        exact(digest(snapshot), source["sha256"], sp + ".sha256")
        dependencies = names(source["dependencies"], sp + ".dependencies") if source["dependencies"] else []
        exact(dependencies, sorted(dependencies), sp + ".dependencies")
        if source["metaSnapshotPath"]:
            meta = prior._rel(root, source["metaSnapshotPath"], sp, "metaSnapshotPath")
            exact(digest(meta), source["metaSha256"], sp + ".metaSha256")
        else:
            exact(source["metaSha256"], "", sp + ".metaSha256")
        if source["builtin"]:
            resource_v2._verify_builtin_source(root, source, sp, manifest["unityVersion"])
    for asset in sum((list(value) for value in expected_assets.values()), []):
        require(asset in source_by_path, f"{receipt_path}: mapped asset absent from frozen source inventory: {asset}")

    compiler_root, compiler = verify_compile_snapshot(root / receipt["compilerSnapshotPath"],
                                                       receipt["compilerSnapshotHash"], manifest,
                                                       receipt_path, expected_defines)
    compiled = {row["name"]: row for row in compiler.get("assemblies", []) if type(row) is dict}
    metadata = array(receipt["metadataAssemblies"], f"{receipt_path}.metadataAssemblies")
    require(len(metadata) == len(CANDIDATES), f"{receipt_path}: metadata root count differs")
    for index, row in enumerate(metadata):
        rp = f"{receipt_path}.metadataAssemblies[{index}]"
        fields(row, RESOURCE_PROOF_FIELDS, rp)
        name = Path(row["path"]).stem
        exact(name, CANDIDATES[index], rp + ".path")
        exact(row["path"], "ResourceAssemblies/" + name + ".dll", rp + ".path")
        physical = prior._rel(root, row["path"], rp, "metadata assembly")
        exact(digest(physical), row["sha256"], rp + ".sha256")
        require(name in compiled and compiled[name]["sha256"] == row["sha256"], f"{rp}: metadata bytes differ from compiler output")
    metadata_root = root / "ResourceAssemblies"
    exact({path.resolve() for path in metadata_root.rglob("*.dll")},
          {prior._rel(root, row["path"], receipt_path, "metadata assembly").resolve() for row in metadata},
          f"{metadata_root}: DLL inventory")

    abi_path = prior._rel(root, receipt["resourceAbiPath"], receipt_path, "resource ABI")
    exact(digest(abi_path), receipt["resourceAbiFileSha256"], f"{receipt_path}.resourceAbiFileSha256")
    abi = prior._obj(abi_path)
    exact(abi.get("schemaVersion"), 2, f"{abi_path}.schemaVersion")
    exact(abi.get("unknowns"), [], f"{abi_path}.unknowns")
    exact(resource_v2._resource_abi_hash(abi), receipt["resourceAbiHash"], f"{abi_path}: computed hash")
    index_path = prior._rel(root, receipt["resourceIndexPath"], receipt_path, "resource index")
    exact(digest(index_path), receipt["resourceIndexHash"], f"{receipt_path}.resourceIndexHash")
    index_value = prior._obj(index_path, "schemaVersion entries bundles hasUnknown unknowns")
    exact(index_value["schemaVersion"], 2, f"{index_path}.schemaVersion")
    exact(index_value["bundles"], list(BUNDLES), f"{index_path}.bundles")
    exact(index_value["hasUnknown"], False, f"{index_path}.hasUnknown")
    exact(index_value["unknowns"], [], f"{index_path}.unknowns")
    for number, entry in enumerate(array(index_value["entries"], f"{index_path}.entries")):
        ep = f"{index_path}.entries[{number}]"
        fields(entry, "typeKey assetGuids assetPaths bundleNames", ep)
        require(type(entry["typeKey"]) is str and entry["typeKey"], f"{ep}: empty type key")
        for key in ("assetGuids", "assetPaths", "bundleNames"):
            values = names(entry[key], ep + "." + key) if entry[key] else []
            exact(values, sorted(values), ep + "." + key)
        require(set(entry["assetPaths"]) <= set(source_by_path) and set(entry["bundleNames"]) <= set(BUNDLES),
                f"{ep}: index escapes frozen resources")

    scripts = array(receipt["scripts"], f"{receipt_path}.scripts")
    seen_scripts = set()
    for number, script in enumerate(scripts):
        sp = f"{receipt_path}.scripts[{number}]"
        fields(script, RESOURCE_SCRIPT_FIELDS, sp)
        strings(script, sp, "path guid assembly namespace type")
        integer(script["localId"], sp + ".localId", 1)
        require(script["path"] in source_by_path and script["guid"] == source_by_path[script["path"]]["guid"] and
                script["assembly"] in compiled and (script["guid"], script["localId"]) not in seen_scripts,
                f"{sp}: script identity is not compiler/source bound")
        seen_scripts.add((script["guid"], script["localId"]))
    require(any(script["assembly"] in CANDIDATES for script in scripts), f"{receipt_path}: no candidate script reference was proven")

    dependencies = fields(receipt["dependencies"], DEPENDENCY_FIELDS, f"{receipt_path}.dependencies")
    exact(dependencies["schemaVersion"], 1, f"{receipt_path}.dependencies.schemaVersion")
    for key, shape in (("runtimeDependencies", RUNTIME_DEP_FIELDS), ("resourceDependencies", RESOURCE_DEP_FIELDS),
                       ("bootstrapEntrypoints", BOOTSTRAP_DEP_FIELDS)):
        for number, row in enumerate(array(dependencies[key], f"{receipt_path}.dependencies.{key}")):
            rp = f"{receipt_path}.dependencies.{key}[{number}]"
            fields(row, shape, rp)
            strings(row, rp, shape)
    return dict(root=root, path=receipt_path, receipt=receipt, compiler=compiler, bundles=bundles,
                abi=abi, index=index_value)


def verify_baseline(manifest, manifest_path):
    baseline_path = bound(manifest["baselineManifestPath"], manifest["baselineManifestSha256"],
                          manifest_path, "baselineManifestPath")
    baseline = prior._obj(baseline_path)
    require(baseline.get("schemaVersion") == baseline.get("semanticHashSchema") == 1,
            f"{baseline_path}: invalid baseline schema")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        exact(baseline.get(key), manifest[key], f"{baseline_path}.{key}")
    prior._pins(baseline.get("sourcePins"), baseline_path)
    exact(prior._runtime_abi_hash(baseline["sourcePins"], baseline_path), manifest["runtimeAbiHash"],
          f"{baseline_path}.runtimeAbiHash")
    exact(baseline.get("shadowCandidates"), list(CANDIDATES), f"{baseline_path}.shadowCandidates")
    hash64(baseline.get("bootstrapAbiHash"), f"{baseline_path}.bootstrapAbiHash")
    resource_hash(baseline.get("resourceAbiHash"), f"{baseline_path}.resourceAbiHash")
    descriptors = array(baseline.get("assemblies"), f"{baseline_path}.assemblies")
    names([row.get("name") for row in descriptors], f"{baseline_path}.assemblies")
    for row in descriptors:
        dll = prior._rel(baseline_path.parent, row.get("filePath"), baseline_path, "baseline DLL")
        actual = prior.read_identity(dll)
        for key in ("name", "mvid", "sha256"):
            exact(row.get(key), actual[key], f"{baseline_path}.{row.get('name')}.{key}")
    frozen, _, _, reflection = prior._verify_player_snapshot(
        baseline_path.parent, baseline, {row["name"]: row for row in descriptors}, baseline_path)
    prior._reflection_manifest(baseline, reflection, baseline_path)
    frozen_root = canonical(str(baseline_path.parent / baseline["playerInputSnapshot"]), baseline_path,
                            "frozen Player snapshot", True)
    raw_admissions.verify_snapshot(frozen_root, frozen, require_linked=True)

    snapshot_root = canonical(manifest["baselineInputSnapshot"], manifest_path, "baselineInputSnapshot", True)
    snapshot = prior._verify_snapshot(snapshot_root, manifest["baselineBuildId"], manifest["runtimeAbiHash"],
                                      baseline, manifest_path)
    prior._snapshot_files(snapshot, snapshot_root, manifest_path)
    prior._reflection_snapshot(snapshot_root, snapshot, manifest_path, require_linked=True)
    raw_admissions.verify_snapshot(snapshot_root, snapshot, require_linked=True)
    exact(manifest["baselineInputSnapshotHash"], snapshot["snapshotHash"], f"{manifest_path}.baselineInputSnapshotHash")
    exact(snapshot["snapshotHash"], frozen["snapshotHash"], f"{manifest_path}: frozen/current snapshot")
    exact(snapshot["linkedPlayerReceiptHash"], frozen["linkedPlayerReceiptHash"],
          f"{manifest_path}: frozen/current linked receipt")
    exact(snapshot["buildGuid"], baseline["playerBuildGuid"], f"{manifest_path}: build GUID")

    resource_root = canonical(str(baseline_path.parent / baseline["resourceBaselinePath"]), baseline_path,
                              "baseline resource copy", True)
    resources = verify_resource_baseline(resource_root, baseline["resourceAbiHash"], baseline, [])
    exact(digest(resources["path"]), baseline["resourceBuildReceiptHash"], f"{baseline_path}.resourceBuildReceiptHash")
    exact(resources["receipt"]["resourceIndexHash"], baseline["resourceIndexHash"], f"{baseline_path}.resourceIndexHash")
    exact([dict(name=row["name"], sha256=row["sha256"], assets=row["assets"]) for row in resources["bundles"]],
          baseline["bundles"], f"{baseline_path}.bundles")

    provenance = manifest["stableAotProvenance"]
    exact(manifest["stableAotProvenanceHash"], hashlib.sha256((STABLE_DOMAIN + provenance).encode()).hexdigest(),
          f"{manifest_path}.stableAotProvenanceHash")
    stable = names(manifest["stableAotNames"], f"{manifest_path}.stableAotNames")
    exact(stable, sorted(stable), f"{manifest_path}.stableAotNames")
    require(not {value.casefold() for value in stable} & {value.casefold() for value in CANDIDATES},
            f"{manifest_path}: stable AOT overlaps candidates")
    lines = provenance.split("\n")
    exact([line.partition("=")[0] for line in lines],
          ["framework", "compiler-libraries", "linked-player", "bootstrap-policy", "physical"],
          f"{manifest_path}.stableAotProvenance")
    for line in lines[:2]: hash64(line.partition("=")[2], f"{manifest_path}.stableAotProvenance")
    exact(lines[2], "linked-player=" + snapshot["linkedPlayerReceiptHash"], f"{manifest_path}.stableAotProvenance")
    exact(lines[3], "bootstrap-policy=" + ",".join(sorted(name.casefold() for name in baseline["bootstrapAssemblies"])),
          f"{manifest_path}.stableAotProvenance")
    exact(lines[4], "physical=" + ",".join(stable), f"{manifest_path}.stableAotProvenance")
    require(set(stable) <= {row["name"] for row in snapshot["linkedPlayerReceipt"]["assemblies"]},
            f"{manifest_path}: stable AOT includes an unlinked assembly")
    return baseline, baseline_path, snapshot, snapshot_root, resources


def verify_patch(fixture, manifest, baseline, manifest_path):
    patch_id = fixture["patchId"]
    defines, roots, dll_only = fixture_policy(patch_id)
    exact(sorted(fixture["defines"]), sorted(defines), f"{manifest_path}.{patch_id}.defines")
    exact(set(fixture["changedRoots"]), set(roots), f"{manifest_path}.{patch_id}.changedRoots")
    exact(fixture["dllOnly"], dll_only, f"{manifest_path}.{patch_id}.dllOnly")
    expected_order = fixture_order(patch_id)
    exact(fixture["closureLoadOrder"], expected_order, f"{manifest_path}.{patch_id}.closureLoadOrder")
    compile_root, compiled = verify_compile_snapshot(fixture["compileSnapshot"], fixture["compileSnapshotHash"],
                                                     baseline, manifest_path, defines)
    patch_root = canonical(fixture["patchDirectory"], manifest_path, "patchDirectory", True)
    patch_path = bound(fixture["patchManifest"], fixture["patchManifestSha256"], manifest_path, "patchManifest")
    exact(patch_path, patch_root / "patch-manifest.json", f"{manifest_path}.{patch_id}.patchManifest")
    patch = prior._obj(patch_path, PATCH_FIELDS)
    sidecar = patch_root / "manifest.sha256"
    require(sidecar.is_file() and not sidecar.is_symlink() and sidecar.read_text(encoding="utf-8").strip() == digest(patch_path),
            f"{sidecar}: missing or stale patch manifest sidecar")
    exact(patch["schemaVersion"], 1, f"{patch_path}.schemaVersion")
    exact(patch["semanticHashSchema"], 1, f"{patch_path}.semanticHashSchema")
    exact(patch["patchId"], patch_id, f"{patch_path}.patchId")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        exact(patch[key], manifest[key], f"{patch_path}.{key}")
    exact(patch["baselineManifestSha256"], manifest["baselineManifestSha256"], f"{patch_path}.baselineManifestSha256")
    exact(patch["compileSnapshotHash"], compiled["snapshotHash"], f"{patch_path}.compileSnapshotHash")
    prior._pins(patch["sourcePins"], patch_path, baseline["sourcePins"])
    exact(prior._runtime_abi_hash(patch["sourcePins"], patch_path), manifest["runtimeAbiHash"], f"{patch_path}.runtimeAbiHash")
    exact(patch["unsigned"], True, f"{patch_path}.unsigned")
    exact(patch["signatureAlgorithm"], "None", f"{patch_path}.signatureAlgorithm")
    exact(patch["dllOnly"], dll_only, f"{patch_path}.dllOnly")
    exact(set(patch["changedRoots"]), set(roots), f"{patch_path}.changedRoots")
    exact(patch["loadOrder"], expected_order, f"{patch_path}.loadOrder")
    exact(fixture["baselineResourceAbiHash"], baseline["resourceAbiHash"], f"{manifest_path}.{patch_id}.baselineResourceAbiHash")
    exact(patch["baselineResourceAbiHash"], baseline["resourceAbiHash"], f"{patch_path}.baselineResourceAbiHash")
    exact(fixture["resourceAbiHash"], patch["resourceAbiHash"], f"{manifest_path}.{patch_id}.resourceAbiHash")
    exact(fixture["resourceChangeLevel"], patch["resourceChangeLevel"], f"{manifest_path}.{patch_id}.resourceChangeLevel")
    exact(fixture["resourceBundlesRequired"], patch["resourceBundlesRequired"], f"{manifest_path}.{patch_id}.resourceBundlesRequired")
    if patch_id == "P05":
        exact(patch["resourceChangeLevel"], "ResourceRebuildRequired", f"{patch_path}.resourceChangeLevel")
        require(patch["resourceAbiHash"] != baseline["resourceAbiHash"] and not patch["dllOnly"],
                f"{patch_path}: P05 did not change structural resource ABI")
        required = names(patch["resourceBundlesRequired"], f"{patch_path}.resourceBundlesRequired")
        require(set(required) <= set(BUNDLES) and required, f"{patch_path}: invalid P05 required bundles")
    else:
        exact(patch["resourceChangeLevel"], "CodeOnly", f"{patch_path}.resourceChangeLevel")
        exact(patch["resourceAbiHash"], baseline["resourceAbiHash"], f"{patch_path}.resourceAbiHash")
        exact(patch["resourceBundlesRequired"], [], f"{patch_path}.resourceBundlesRequired")
        exact(patch["resourceChangeReasons"], [], f"{patch_path}.resourceChangeReasons")

    closure = array(patch["closure"], f"{patch_path}.closure")
    exact([row.get("name") for row in closure], expected_order, f"{patch_path}.closure")
    compiled_by_name = {row["name"]: row for row in compiled.get("assemblies", []) if type(row) is dict}
    baseline_by_name = {row["name"]: row for row in baseline["assemblies"]}
    dlls, pdbs = [], []
    for index, row in enumerate(closure):
        rp = f"{patch_path}.closure[{index}]"
        fields(row, PATCH_ASSEMBLY_FIELDS, rp)
        name = row["name"]
        require(name in compiled_by_name and name in baseline_by_name, f"{rp}: unknown closure assembly")
        dll = prior._rel(patch_root, row["dll"], rp, "dll")
        exact(digest(dll), row["sha256"], rp + ".sha256")
        exact(row["sha256"], compiled_by_name[name]["sha256"], rp + ".compilerSha256")
        exact(row["baselineMvid"], baseline_by_name[name]["mvid"], rp + ".baselineMvid")
        pdb = prior._rel(patch_root, row["pdb"], rp, "pdb")
        source_pdb = prior._rel(compile_root, compiled_by_name[name]["pdbPath"], rp, "compiler PDB")
        exact(digest(pdb), row["pdbSha256"], rp + ".pdbSha256")
        exact(row["pdbSha256"], digest(source_pdb), rp + ".compilerPdbSha256")
        dlls.append(dll)
        pdbs.append(pdb)
    identities = prior.verify_identities(fixture["assemblyIdentities"], dlls, f"{manifest_path}.{patch_id}.assemblyIdentities")
    for row in closure:
        actual = identities[row["name"]]
        exact(row["mvid"], actual["mvid"], f"{patch_path}.{row['name']}.mvid")
        exact(set(row["references"]), {item["name"] for item in actual["referenceIdentities"]},
              f"{patch_path}.{row['name']}.references")
    exact({path.resolve() for path in patch_root.rglob("*.dll")}, {path.resolve() for path in dlls},
          f"{patch_path}: DLL inventory")
    exact({path.resolve() for path in patch_root.rglob("*.pdb")}, {path.resolve() for path in pdbs},
          f"{patch_path}: PDB inventory")
    edges = prior._edges(patch["dependencyGraph"], patch_path)
    closure_set = prior._closure(edges, patch["changedRoots"], {row["name"] for row in baseline["assemblies"]}, patch_path)
    exact(closure_set, set(expected_order), f"{patch_path}: reverse closure")
    prior._verify_topological(expected_order, closure_set, edges, patch_path)
    reflected = prior._reflection_snapshot(compile_root, compiled, patch_path)
    prior._reflection_manifest(patch, reflected, patch_path)
    return dict(fixture=fixture, patch=patch, root=patch_root, path=patch_path,
                compile_root=compile_root, compiled=compiled, identities=identities)


def verify_rejected(row, manifest, baseline, manifest_path):
    fields(row, REJECTED_FIELDS, manifest_path)
    defines = rejected_policy(row["patchId"])
    exact(sorted(row["defines"]), sorted(defines), f"{manifest_path}.{row['patchId']}.defines")
    exact(row["changedRoots"], [INTERNAL], f"{manifest_path}.{row['patchId']}.changedRoots")
    exact(row["errorCode"], "ResourceRebuildRequired", f"{manifest_path}.{row['patchId']}.errorCode")
    require(type(row["errorMessage"]) is str and row["errorMessage"].startswith("ResourceRebuildRequired: "),
            f"{manifest_path}.{row['patchId']}: missing actual structural rejection message")
    compile_root, compiled = verify_compile_snapshot(row["compileSnapshot"], row["compileSnapshotHash"],
                                                     baseline, manifest_path, defines)
    output = manifest_path.parent / (row["patchId"] + "-must-not-exist")
    require(not output.exists() and not output.is_symlink() and not list(output.parent.glob(output.name + ".building-*")),
            f"{output}: rejected build published output")
    return dict(row=row, compile_root=compile_root, compiled=compiled)


def verify_inputs(path):
    path = canonical(str(path), path, "fixtureManifest")
    manifest = prior._obj(path, MANIFEST_FIELDS)
    exact(manifest["schemaVersion"], 1, f"{path}.schemaVersion")
    exact(manifest["milestone"], "M07", f"{path}.milestone")
    require(re.fullmatch(r"M07-Baseline-[A-Za-z0-9_.-]+", manifest["baselineBuildId"]) is not None,
            f"{path}: fresh M07 baseline identity required")
    exact((manifest["unityVersion"], manifest["target"], manifest["architecture"]),
          ("2022.3.62f2", "StandaloneOSX", "arm64"), f"{path}: pinned target")
    hash64(manifest["runtimeAbiHash"], f"{path}.runtimeAbiHash")
    exact(manifest["candidateNames"], list(CANDIDATES), f"{path}.candidateNames")
    exact(manifest["bundleNames"], list(BUNDLES), f"{path}.bundleNames")
    baseline, baseline_path, snapshot, snapshot_root, resources = verify_baseline(manifest, path)
    rows = array(manifest["fixtures"], f"{path}.fixtures")
    exact([row.get("patchId") for row in rows], ["P01", "P02", "P03", "P04", "P05"], f"{path}.fixtures")
    fixtures = {}
    for row in rows:
        fields(row, FIXTURE_FIELDS, path)
        fixtures[row["patchId"]] = verify_patch(row, manifest, baseline, path)
    rejected_rows = array(manifest["rejectedFixtures"], f"{path}.rejectedFixtures")
    exact([row.get("patchId") for row in rejected_rows],
          ["P05-DllOnly", "P14-ClassRename", "P15-SerializeReferenceRename"], f"{path}.rejectedFixtures")
    rejected = {row["patchId"]: verify_rejected(row, manifest, baseline, path) for row in rejected_rows}
    manifest["_path"] = str(path)
    manifest["_baselinePath"] = str(baseline_path)
    manifest["_snapshot"] = snapshot
    manifest["_snapshotRoot"] = str(snapshot_root)
    return manifest, baseline, fixtures, rejected, resources


def verify_player(path, manifest, baseline, baseline_resources, variant):
    path = canonical(str(path), path, "playerBuildReceipt")
    player = prior._obj(path, PLAYER_FIELDS)
    exact(player["schemaVersion"], 1, f"{path}.schemaVersion")
    exact(player["milestone"], "M07", f"{path}.milestone")
    exact(player["variant"], variant, f"{path}.variant")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        exact(player[key], manifest[key], f"{path}.{key}")
    flag = "1" if variant == "NativeOn" else "0"
    exact(player["nativeArguments"], '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + flag + '"',
          f"{path}.nativeArguments")
    root = canonical(player["inputSnapshot"], path, "inputSnapshot", True)
    exact(path, root / "m07-player-build.json", f"{path}: canonical receipt location")
    snapshot = prior._verify_snapshot(root, manifest["baselineBuildId"], manifest["runtimeAbiHash"], baseline,
                                      path, variant == "NativeOn")
    for key, source in (("inputSnapshotHash", "snapshotHash"), ("buildGuid", "buildGuid"),
                        ("playerOutput", "playerOutput"), ("nativeLibraryPath", "nativeLibraryPath"),
                        ("nativeLibrarySha256", "nativeLibrarySha256")):
        exact(player[key], snapshot[source], f"{path}.{key}")
    output = canonical(player["playerOutput"], path, "playerOutput", True)
    native = bound(player["nativeLibraryPath"], player["nativeLibrarySha256"], path, "nativeLibraryPath")
    require(native.is_relative_to(output), f"{path}: native library is outside Player output")
    require(type(snapshot.get("playerBuildOptions")) is int and snapshot["playerBuildOptions"] & 1,
            f"{path}: M07 requires Development Player evidence")
    prior._pins(snapshot["sourcePins"], path, baseline["sourcePins"])
    prior._snapshot_files(snapshot, root, path)
    prior._verify_linked_player(root, snapshot, {row["name"]: row for row in baseline["assemblies"]}, path)
    prior._reflection_snapshot(root, snapshot, path, require_linked=True)
    raw_admissions.verify_snapshot(root, snapshot, require_linked=True)
    linked = snapshot["linkedPlayerReceipt"]["assemblies"]
    prior.verify_identities(player["assemblyIdentities"],
                            [prior._rel(root / "LinkedPlayer", row["path"], path, "linked DLL") for row in linked],
                            f"{path}.assemblyIdentities")
    prior._verify_native_metadata(player, path)
    placeholder = bound(player["placeholderManifestPath"], player["placeholderManifestSha256"], path,
                        "placeholderManifestPath")
    exact(placeholder, root / "m07-placeholder-AssemblyManifest.cpp", f"{path}.placeholderManifestPath")
    exact(player["placeholderAssemblyNames"], prior.parse_placeholders(placeholder.read_bytes(), placeholder),
          f"{path}.placeholderAssemblyNames")
    exact(player["bundleNames"], list(BUNDLES), f"{path}.bundleNames")
    exact(player["resourceAbiHash"], baseline["resourceAbiHash"], f"{path}.resourceAbiHash")
    resource_root = canonical(player["resourceBaselinePath"], path, "resourceBaselinePath", True)
    resource_path = bound(player["resourceBuildReceiptPath"], player["resourceBuildReceiptSha256"], path,
                          "resourceBuildReceiptPath")
    exact(resource_path, resource_root / "resource-build-receipt.json", f"{path}.resourceBuildReceiptPath")
    exact(player["resourceBuildReceiptSha256"], baseline["resourceBuildReceiptHash"],
          f"{path}.resourceBuildReceiptSha256")
    resources = verify_resource_baseline(resource_root, player["resourceAbiHash"], baseline, [])
    exact(artifact_tree(resource_root), artifact_tree(baseline_resources["root"]),
          f"{path}: original and immutable baseline resource trees")
    return dict(player=player, path=path, root=root, snapshot=snapshot, output=output, resources=resources)


def verify_replay(path, manifest, baseline, fixtures, rejected, on_build, baseline_resources):
    path = canonical(str(path), path, "editor replay")
    replay = prior._obj(path, REPLAY_FIELDS)
    require(replay["schemaVersion"] == 1 and replay["milestone"] == "M07" and replay["result"] == "Passed" and
            replay["comparisonPolicy"] == EDITOR_REPLAY_POLICY, f"{path}: invalid M07 Editor replay receipt")
    player = on_build["player"]
    expected = {
        "fixtureManifestPath": manifest["_path"],
        "fixtureManifestSha256": digest(Path(manifest["_path"])),
        "baselineManifestPath": manifest["baselineManifestPath"],
        "baselineManifestSha256": manifest["baselineManifestSha256"],
        "playerBuildReceiptPath": str(on_build["path"]),
        "playerBuildReceiptSha256": digest(on_build["path"]),
        "baselineInputSnapshotHash": manifest["baselineInputSnapshotHash"],
        "baselineBuildId": manifest["baselineBuildId"],
        "playerBuildGuid": player["buildGuid"],
        "nativeLibrarySha256": player["nativeLibrarySha256"],
        "linkedPlayerReceiptHash": manifest["_snapshot"]["linkedPlayerReceiptHash"],
        "runtimeAbiHash": manifest["runtimeAbiHash"],
        "unityVersion": manifest["unityVersion"], "target": manifest["target"],
        "architecture": manifest["architecture"],
        "stableAotProvenanceHash": manifest["stableAotProvenanceHash"],
        "resourceBuildReceiptPath": str(baseline_resources["path"]),
        "resourceBuildReceiptSha256": digest(baseline_resources["path"]),
        "resourceAbiHash": baseline["resourceAbiHash"],
    }
    for key, value in expected.items(): exact(replay[key], value, f"{path}.{key}")
    prior._pins(replay["validatorSourcePins"], path, baseline["sourcePins"])
    scratch = canonical(replay["replayScratchPath"], path, "replayScratchPath", True)
    require(re.fullmatch(r"M07Replay-[0-9a-f]{32}", scratch.name) and scratch.parent == Path(manifest["_path"]).parent.parent,
            f"{path}: noncanonical replay scratch")
    rows = array(replay["fixtures"], f"{path}.fixtures")
    exact([row.get("patchId") for row in rows], list(fixtures), f"{path}.fixtures")
    for row in rows:
        fields(row, REPLAY_FIXTURE_FIELDS, path)
        item = fixtures[row["patchId"]]["fixture"]
        expected_row = {key: item[key] for key in REPLAY_FIXTURE_FIELDS.split()}
        exact(row, expected_row, f"{path}.{row['patchId']}")
        rebuilt = scratch / (row["patchId"] + "-patch")
        exact(artifact_tree(rebuilt), artifact_tree(fixtures[row["patchId"]]["root"]),
              f"{path}.{row['patchId']}: replay artifact tree")
    rows = array(replay["rejectedFixtures"], f"{path}.rejectedFixtures")
    exact([row.get("patchId") for row in rows], list(rejected), f"{path}.rejectedFixtures")
    for row in rows:
        fields(row, REPLAY_REJECTED_FIELDS, path)
        source = rejected[row["patchId"]]["row"]
        exact(row, {key: source[key] for key in REPLAY_REJECTED_FIELDS.split()}, f"{path}.{row['patchId']}")
        output = scratch / (row["patchId"] + "-must-not-exist")
        require(not output.exists() and not output.is_symlink() and not list(scratch.glob(output.name + ".building-*")),
                f"{path}: replayed rejected fixture published output")
    return replay


def marker_for(patch_id):
    return {
        None: "M07-BASELINE", "P01": "M07-P01", "P02": "M07-BASELINE",
        "P03": "M07-P03", "P04": "M07-P04", "P05": "M07-P05",
    }[patch_id]


def parse_counters(value, count, path):
    require(type(value) is str, f"{path}: missing counter string")
    parts = value.split("|")
    require(len(parts) == count, f"{path}: expected {count} counters")
    result = []
    for index, part in enumerate(parts):
        require(re.fullmatch(r"0|[1-9][0-9]*", part) is not None, f"{path}[{index}]: noncanonical counter")
        result.append(integer(int(part), f"{path}[{index}]"))
    return result


def parse_scene_counters(value, path):
    require(type(value) is str, f"{path}: missing scene counters")
    parts = value.split("|")
    require(len(parts) == 13, f"{path}: expected twelve counters and marker")
    counters = []
    for index, part in enumerate(parts[:12]):
        require(re.fullmatch(r"0|[1-9][0-9]*", part) is not None, f"{path}[{index}]: noncanonical counter")
        counters.append(integer(int(part), f"{path}[{index}]"))
    require(parts[12], f"{path}: missing active scene marker")
    return counters, parts[12]


def raw_diagnostic(result, result_path):
    raw_path = bound(result["rawDiagnosticsPath"], result["rawDiagnosticsSha256"], result_path,
                     "rawDiagnosticsPath")
    exact(raw_path, result_path.with_name(result_path.stem + "-diagnostics.json"),
          f"{result_path}.rawDiagnosticsPath")
    inline = json_text(result["nativeDiagnosticsJson"], f"{result_path}.nativeDiagnosticsJson")
    disk = prior._obj(raw_path)
    exact(inline, disk, f"{result_path}: inline/raw diagnostics")
    prior._diagnostic(disk, raw_path)
    return disk


def verify_result_header(path, manifest, baseline, build):
    path = canonical(str(path), path, "result")
    result = prior._obj(path, RESULT_FIELDS)
    require(result["schemaVersion"] == 1 and result["milestone"] == "M07" and result["mode"] in MODES and
            path.name == "m07-" + result["mode"] + ".json" and result["result"] == "Passed" and
            result["error"] == "" and result["il2cpp"] is True,
            f"{path}: not a successful real M07 IL2CPP process result")
    integer(result["processId"], f"{path}.processId", 1, (1 << 31) - 1)
    for key in ("graphSum", "p04RuntimeValue", "p05SerializedValue", "baselineUseCount", "nativeEventCount"):
        integer(result[key], f"{path}.{key}", -1)
    integer(result["transactionGeneration"], f"{path}.transactionGeneration", 0, (1 << 64) - 1)
    for key in ("resourcePrecheckPassed", "commitCompletedBeforeResourceLoad", "businessResourceLoadStarted"):
        boolean(result[key], f"{path}.{key}")
    for key in ("stageOrder", "checks", "stageResults", "snapshots", "bundles", "assets", "scenes",
                "typeResolutions", "cacheEvents", "assemblyModes"):
        array(result[key], f"{path}.{key}")
    nonstrings = {"schemaVersion", "processId", "il2cpp", "resourcePrecheckPassed",
                  "commitCompletedBeforeResourceLoad", "businessResourceLoadStarted", "graphSum",
                  "p04RuntimeValue", "p05SerializedValue", "baselineUseCount", "nativeEventCount",
                  "transactionGeneration", "stageOrder", "checks", "stageResults", "snapshots", "bundles",
                  "assets", "scenes", "typeResolutions", "cacheEvents", "assemblyModes"}
    for key in set(RESULT_FIELDS.split()) - nonstrings:
        require(type(result[key]) is str, f"{path}.{key}: expected string evidence")
    player = build["player"]
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "buildGuid"):
        exact(result[key], player[key], f"{path}.{key}")
    exact(result["platform"], "OSXPlayer", f"{path}.platform")
    data_path = canonical(result["playerDataPath"], path, "playerDataPath", True)
    require(data_path.is_relative_to(build["output"]), f"{path}: Player data path escapes executed output")
    expected = {
        "fixtureManifestPath": manifest["_path"],
        "fixtureManifestSha256": digest(Path(manifest["_path"])),
        "playerBuildReceiptPath": str(build["path"]),
        "playerBuildReceiptSha256": digest(build["path"]),
        "baselineManifestPath": manifest["baselineManifestPath"],
        "baselineManifestSha256": manifest["baselineManifestSha256"],
        "baselineResourceAbiHash": baseline["resourceAbiHash"],
    }
    for key, value in expected.items(): exact(result[key], value, f"{path}.{key}")
    return path, result


def verify_transaction(result, path, manifest, patch_item):
    feature_off = patch_item is None
    checks = []
    seen = set()
    for index, row in enumerate(result["checks"]):
        rp = f"{path}.checks[{index}]"
        fields(row, CHECK_FIELDS, rp)
        strings(row, rp, "name actual expected")
        boolean(row["passed"], rp + ".passed")
        require(row["passed"] and row["name"] not in seen, f"{rp}: failed or duplicate check")
        seen.add(row["name"])
        checks.append(row["name"])
    resource_checks = ["resource-load-not-started-at-entry", "prefab-serialized-state",
                       "serialize-reference-graph", "nested-cross-reference", "monoscript-evidence-policy",
                       "monoscript-logical-identity",
                       "monoscript-active-after-unload-true", "scriptable-object-state",
                       "dont-destroy-survives-scene-switch", "p04-runtime-storage", "p05-serialized-storage"]
    if feature_off:
        operations = ["configure", "begin", "stage", "validate", "commit", "abort", "state",
                      "execution-mode", "diagnostics", "type-resolution", "execution-diagnostics"]
        expected_checks = operations + ["assembly-mode-" + name for name in CANDIDATES] + resource_checks
        exact(checks, expected_checks, f"{path}.checks")
        for key in ("configureCode", "beginCode", "stageProbeCode", "validateCode", "commitCode", "abortCode",
                    "stateCode", "executionModeCode", "diagnosticsCode", "typeResolutionCode", "executionDiagnosticsCode"):
            exact(result[key], "FeatureDisabled", f"{path}.{key}")
        exact(result["state"], "Disabled", f"{path}.state")
        exact(result["stageOrder"], [], f"{path}.stageOrder")
        exact(result["stageResults"], [], f"{path}.stageResults")
        exact([row["phase"] for row in result["snapshots"]], ["disabled"], f"{path}.snapshots")
        fields(result["snapshots"][0], SNAPSHOT_FIELDS, f"{path}.snapshots[0]")
        diagnostic = raw_diagnostic(result, path)
        exact(result["snapshots"][0]["diagnostics"], diagnostic, f"{path}.snapshots[0].diagnostics")
        require(diagnostic["enabled"] is False and diagnostic["state"] == "Disabled" and diagnostic["lastError"] == 1,
                f"{path}: feature-OFF diagnostic differs")
        for key in ("generation", "expected", "staged", "retainedBytes", "enumerationGeneration", "classEnumerationGeneration"):
            exact(diagnostic[key], 0, f"{path}.diagnostics.{key}")
        for key in ("ordinaryAssemblies", "ordinaryClasses", "closureLoadOrder", "stableAotNames", "commitOrder",
                    "assemblies", "events", "baselineUses"):
            exact(diagnostic[key], [], f"{path}.diagnostics.{key}")
        exact((result["baselineUseCount"], result["nativeEventCount"], result["transactionGeneration"]), (0, 0, 0),
              f"{path}: feature-OFF counters")
        return diagnostic

    fixture, patch = patch_item["fixture"], patch_item["patch"]
    order = fixture["closureLoadOrder"]
    expected_checks = ["configure", "begin"] + ["stage-" + name for name in order] + ["validate", "commit"] + \
                      ["assembly-mode-" + name for name in CANDIDATES] + resource_checks
    if result["mode"] == "T07-11-DelayedCatalog-P03": expected_checks.insert(len(expected_checks) - len(resource_checks) + 1, "delayed-catalog-after-commit")
    exact(checks, expected_checks, f"{path}.checks")
    for key in ("configureCode", "beginCode", "validateCode", "commitCode", "stateCode"):
        exact(result[key], "Success", f"{path}.{key}")
    for key in ("stageProbeCode", "abortCode", "executionModeCode", "diagnosticsCode", "typeResolutionCode", "executionDiagnosticsCode"):
        exact(result[key], "", f"{path}.{key}")
    exact(result["state"], "Committed", f"{path}.state")
    exact(result["stageOrder"], order, f"{path}.stageOrder")
    by_name = {row["name"]: row for row in patch["closure"]}
    expected_stages = [dict(name=name, code="Success", dllSha256=by_name[name]["sha256"],
                            pdbSha256=by_name[name]["pdbSha256"]) for name in order]
    for index, row in enumerate(result["stageResults"]):
        fields(row, STAGE_FIELDS, f"{path}.stageResults[{index}]")
    exact(result["stageResults"], expected_stages, f"{path}.stageResults")
    phases = ["staged", "validated-resource-precheck-complete", "committed-before-resources", "final-resource"]
    exact([row["phase"] for row in result["snapshots"]], phases, f"{path}.snapshots")
    previous_events = []
    final = None
    for index, row in enumerate(result["snapshots"]):
        rp = f"{path}.snapshots[{index}]"
        fields(row, SNAPSHOT_FIELDS, rp)
        diagnostic = prior._diagnostic(row["diagnostics"], rp)
        prior._verify_diag_invariants(diagnostic, order, manifest["stableAotNames"], rp, patch=patch)
        exact(diagnostic["baselineBuildId"], manifest["baselineBuildId"], rp + ".baselineBuildId")
        exact(diagnostic["patchId"], patch["patchId"], rp + ".patchId")
        exact(diagnostic["baselineUses"], [], rp + ".baselineUses")
        exact(diagnostic["events"][:len(previous_events)], previous_events, rp + ".eventPrefix")
        previous_events = diagnostic["events"]
        expected_state = "Staged" if index == 0 else "Validated" if index == 1 else "Committed"
        exact(diagnostic["state"], expected_state, rp + ".state")
        final = diagnostic
    raw = raw_diagnostic(result, path)
    exact(raw, final, f"{path}: final/raw diagnostic")
    exact(result["baselineUseCount"], 0, f"{path}.baselineUseCount")
    exact(result["nativeEventCount"], len(final["events"]), f"{path}.nativeEventCount")
    exact(result["transactionGeneration"], final["generation"], f"{path}.transactionGeneration")
    require(result["nativeEventCount"] > 0 and result["transactionGeneration"] > 0,
            f"{path}: native resolver event/generation evidence is empty")
    return final


def verify_assembly_modes(result, path, closure, feature_off):
    rows = result["assemblyModes"]
    exact([row.get("name") for row in rows], list(CANDIDATES), f"{path}.assemblyModes")
    for index, row in enumerate(rows):
        rp = f"{path}.assemblyModes[{index}]"
        fields(row, ASSEMBLY_MODE_FIELDS, rp)
        name = row["name"]
        shadow = not feature_off and name in closure
        exact(row["expectedShadow"], shadow, rp + ".expectedShadow")
        exact(row["mode"], "InterpreterShadow" if shadow else "AotBaseline", rp + ".mode")
        if feature_off: exact(row["code"], "FeatureDisabled", rp + ".code")
        elif shadow: exact(row["code"], "Success", rp + ".code")
        else: require(row["code"] in ("Success", "CandidateNotRegistered"), f"{rp}: invalid baseline-mode query code")


def verify_type_resolutions(result, path, closure, feature_off):
    component = "AssemblyA.Implementation.Internal.VersionedPrefabComponent"
    phases = [
        ("data-asset", INTERNAL), ("prefab-asset", INTERNAL), ("prefab-first", INTERNAL),
        ("unity-path-probe", INTERNAL), ("prefab-cached-after-unload-false", INTERNAL),
        ("prefab-reloaded-after-gc", INTERNAL), ("serialize-reference-owner", INTERNAL),
        ("serialize-reference-concrete", INTERNAL), ("nested-internal", INTERNAL),
        ("nested-external", EXTENSIBILITY_CONSUMER), ("mixed-rename-guard", INTERNAL),
        ("monoscript-get-class", INTERNAL), ("mixed-reload-after-unload-true", INTERNAL),
        ("scene-single", INTERNAL), ("dont-destroy-component", INTERNAL),
        ("scene-additive-delayed", INTERNAL), ("scene-scene-reload", INTERNAL),
    ]
    rows = result["typeResolutions"]
    exact([(row.get("phase"), row.get("assemblyName")) for row in rows], phases, f"{path}.typeResolutions")
    for index, row in enumerate(rows):
        rp = f"{path}.typeResolutions[{index}]"
        fields(row, TYPE_FIELDS, rp)
        for key in ("phase", "typeName", "assemblyName", "code", "executionMode", "rawJson"):
            require(type(row[key]) is str, f"{rp}.{key}: expected string")
        exact(row["sameType"], True, rp + ".sameType")
        exact(row["active"], True, rp + ".active")
        expected_mode = "InterpreterShadow" if not feature_off and row["assemblyName"] in closure else "AotBaseline"
        exact(row["executionMode"], expected_mode, rp + ".executionMode")
        if feature_off:
            exact(row["code"], "FeatureDisabled", rp + ".code")
            exact(row["rawJson"], "", rp + ".rawJson")
        else:
            exact(row["code"], "Success", rp + ".code")
            info = json_text(row["rawJson"], rp + ".rawJson")
            types.verify_type_info(info, rp + ".rawJson")
            exact(info["logicalAssembly"], row["assemblyName"], rp + ".logicalAssembly")
            exact(info["executionMode"], expected_mode, rp + ".executionMode")
            exact(info["isActive"], True, rp + ".isActive")
            require(info["typeKey"], f"{rp}: native type key is empty")
    require(any(row["typeName"] == component for row in rows), f"{path}: active prefab type was not observed")


def verify_unity_path(result, path, marker, patch_id):
    value = json_text(result["unityPathJson"], f"{path}.unityPathJson")
    fields(value, PATH_RESULT_FIELDS, f"{path}.unityPathJson")
    for key in set(PATH_RESULT_FIELDS.split()) - {"p04RuntimeValue", "p05SerializedValue"}:
        require(type(value[key]) is str, f"{path}.unityPathJson.{key}: expected string")
    component = "AssemblyA.Implementation.Internal.VersionedPrefabComponent"
    data = "AssemblyA.Implementation.Internal.VersionedScriptableObject"
    base = "AssemblyA.Implementation.Extensibility.VersionedComponentBase"
    interface = "AssemblyA.Contracts.IVersionTextProvider"
    identity = INTERNAL + ":" + component
    data_identity = INTERNAL + ":" + data
    expected = {
        "marker": marker, "componentType": component, "componentAssembly": INTERNAL,
        "baseType": base, "baseAssembly": EXTENSIBILITY,
        "interfaceType": interface, "interfaceAssembly": CONTRACTS,
        "getComponentGeneric": identity, "getComponentType": identity,
        "tryGetComponent": "True:" + identity, "getComponents": "1:" + identity,
        "getComponentInChildren": identity, "getComponentInParent": identity,
        "interfaceComponent": identity, "baseComponent": identity,
        "addComponentGeneric": identity, "addComponentType": identity,
        "createInstanceGeneric": data_identity, "createInstanceType": data_identity,
        "createInstanceString": data_identity, "instantiateExisting": data_identity,
        "serializedState": result["serializedState"], "messageMarker": marker,
        "p04RuntimeValue": 704 if patch_id == "P04" else -1,
        "p05SerializedValue": 705 if patch_id == "P05" else -1,
    }
    exact(value, expected, f"{path}.unityPathJson")
    exact(result["p04RuntimeValue"], expected["p04RuntimeValue"], f"{path}.p04RuntimeValue")
    exact(result["p05SerializedValue"], expected["p05SerializedValue"], f"{path}.p05SerializedValue")


def verify_resource_observations(result, path, selected, patch_id, closure, feature_off):
    marker = marker_for(patch_id)
    node_marker = "M07-BASELINE-NODE" if marker == "M07-BASELINE" else marker + "-NODE"
    data_marker = "M07-BASELINE-DATA" if marker == "M07-BASELINE" else marker + "-DATA"
    scene_marker = "M07-BASELINE-SCENE" if marker == "M07-BASELINE" else marker + "-SCENE"
    exact(result["resourceReceiptPath"], str(selected["path"]), f"{path}.resourceReceiptPath")
    exact(result["resourceReceiptSha256"], digest(selected["path"]), f"{path}.resourceReceiptSha256")
    exact(result["selectedResourceAbiHash"], selected["receipt"]["resourceAbiHash"], f"{path}.selectedResourceAbiHash")
    exact(result["resourcePrecheckPassed"], True, f"{path}.resourcePrecheckPassed")
    exact(result["resourcePrecheckPhase"], "before-commit-before-business-resource-load", f"{path}.resourcePrecheckPhase")
    exact(result["commitCompletedBeforeResourceLoad"], True, f"{path}.commitCompletedBeforeResourceLoad")
    exact(result["businessResourceLoadStarted"], True, f"{path}.businessResourceLoadStarted")
    exact(result["serializedState"],
          "701|M07-BASELINE-TEXT|71:M07-INLINE|72:M07-LIST-72,73:M07-LIST-73|M07 Versioned Data|74:M07-NESTED",
          f"{path}.serializedState")
    exact(result["graphSum"], 77, f"{path}.graphSum")
    exact(result["graphDescription"], "NODE-A|" + node_marker + "|NODE-B|" + marker, f"{path}.graphDescription")
    require(result["graphType"].startswith("AssemblyA.Implementation.Internal.M07NodeA, " + INTERNAL),
            f"{path}: SerializeReference concrete identity differs")
    mono_check = [row for row in result["checks"] if row["name"] == "monoscript-evidence-policy"]
    require(len(mono_check) == 1, f"{path}: MonoScript evidence policy check is missing or duplicated")
    exact(mono_check[0]["expected"], "direct-or-plan-permitted-runtime-component-helper",
          f"{path}.monoscript-evidence-policy.expected")
    require(mono_check[0]["actual"] in (
        "direct-monoscript-get-class",
        "runtime-component-fallback-script-unavailable",
        "runtime-component-fallback-getclass-unavailable",
        "runtime-component-fallback-getclass-not-supported",
    ), f"{path}: unsupported MonoScript evidence path")
    exact(result["monoScriptClass"], "AssemblyA.Implementation.Internal.VersionedPrefabComponent", f"{path}.monoScriptClass")
    exact(result["monoScriptAssembly"], INTERNAL, f"{path}.monoScriptAssembly")
    verify_unity_path(result, path, marker, patch_id)

    before = parse_counters(result["lifecycleBefore"], 8, f"{path}.lifecycleBefore")
    after = parse_counters(result["lifecycleAfter"], 8, f"{path}.lifecycleAfter")
    require(all(right > left for left, right in zip(before, after)), f"{path}: every prefab lifecycle/message counter must advance")
    scene_counts, observed_scene_marker = parse_scene_counters(result["sceneLifecycleAfter"], f"{path}.sceneLifecycleAfter")
    require(all(scene_counts[index] > 0 for index in (0, 1, 2, 3, 4, 5, 8, 9, 10)) and
            scene_counts[11] >= 11 and observed_scene_marker == scene_marker,
            f"{path}: scene serialization/lifecycle/message counters differ")

    expected_bundle_order = ["scriptable-object.bundle", "versioned-prefab.bundle", "versioned-prefab.bundle",
                             "serialize-reference.bundle", "nested-prefab.bundle", "mixed-assets.bundle",
                             "mixed-assets.bundle", "business-scene.bundle", "additive-scene.bundle"]
    exact([row.get("name") for row in result["bundles"]], expected_bundle_order, f"{path}.bundles")
    claims = {row["name"]: row for row in selected["bundles"]}
    for index, row in enumerate(result["bundles"]):
        rp = f"{path}.bundles[{index}]"
        fields(row, BUNDLE_FIELDS, rp)
        claim = claims[row["name"]]
        exact(row["path"], str(selected["root"] / "Bundles" / row["name"]), rp + ".path")
        exact(row["sha256"], claim["sha256"], rp + ".sha256")
        exact((row["loaded"], row["unloaded"]), (True, True), rp + ".lifecycle")
        if row["name"] in ("business-scene.bundle", "additive-scene.bundle"):
            require(row["assetCount"] in (0, 1) and row["sceneCount"] == 1, f"{rp}: scene bundle inventory differs")
        else:
            exact(row["sceneCount"], 0, rp + ".sceneCount")
            exact(row["assetCount"], len(ASSETS[row["name"]]), rp + ".assetCount")

    expected_asset_phases = ["prefab-first", "unity-api", "prefab-cached-after-unload-false", "prefab-reloaded-after-gc"]
    exact([row.get("phase") for row in result["assets"]], expected_asset_phases, f"{path}.assets")
    for index, row in enumerate(result["assets"]):
        rp = f"{path}.assets[{index}]"
        fields(row, ASSET_FIELDS, rp)
        exact(row["bundle"], "versioned-prefab.bundle", rp + ".bundle")
        exact(row["typeName"], "AssemblyA.Implementation.Internal.VersionedPrefabComponent", rp + ".typeName")
        exact(row["assemblyName"], INTERNAL, rp + ".assemblyName")
        exact(row["marker"], marker, rp + ".marker")
        exact(row["serializedState"], result["serializedState"], rp + ".serializedState")
        exact((row["active"], row["instantiated"]), (True, True), rp + ".state")
        require(type(row["assetName"]) is str and row["assetName"], f"{rp}: missing instantiated object name")

    expected_scenes = [
        ("single", "business-scene.bundle", False, False, "707"),
        ("additive-delayed", "additive-scene.bundle", True, True, "708"),
        ("scene-reload", "business-scene.bundle", True, False, "707"),
    ]
    exact([(row.get("phase"), row.get("bundle"), row.get("additive"), row.get("activationDelayed")) for row in result["scenes"]],
          [item[:4] for item in expected_scenes], f"{path}.scenes")
    for index, (row, expected) in enumerate(zip(result["scenes"], expected_scenes)):
        rp = f"{path}.scenes[{index}]"
        fields(row, SCENE_FIELDS, rp)
        exact((row["loaded"], row["unloaded"]), (True, True), rp + ".state")
        exact(row["componentType"], "AssemblyA.Implementation.Internal.M07SceneOnlyComponent", rp + ".componentType")
        exact(row["marker"], scene_marker, rp + ".marker")
        exact(row["serializedState"], expected[4] + "|M07 Versioned Data|M07 Managed Graph|AssemblyA.Implementation.Internal.VersionedPrefabComponent",
              rp + ".serializedState")
        expected_scene_path = expected_asset_map("P05" if patch_id == "P05" else "Baseline")[row["bundle"]][0]
        exact(row["scenePath"].casefold(), expected_scene_path.casefold(), rp + ".scenePath")
        _, lifecycle_marker = parse_scene_counters(row["lifecycle"], rp + ".lifecycle")
        exact(lifecycle_marker, scene_marker, rp + ".lifecycle.marker")

    cache = result["cacheEvents"]
    expected_cache = [
        ("unload-false-retained-asset", "AssemblyA.Implementation.Internal.VersionedPrefabComponent", marker),
        ("bundle-reloaded", "versioned-prefab.bundle", claims["versioned-prefab.bundle"]["sha256"]),
        ("reload-after-unload-unused-and-gc", "AssemblyA.Implementation.Internal.VersionedPrefabComponent", marker),
        ("bundle-reloaded", "mixed-assets.bundle", claims["mixed-assets.bundle"]["sha256"]),
    ]
    exact([(row.get("operation"), row.get("typeName"), row.get("marker")) for row in cache], expected_cache,
          f"{path}.cacheEvents")
    for index, row in enumerate(cache):
        fields(row, CACHE_FIELDS, f"{path}.cacheEvents[{index}]")
        exact((row["active"], row["distinctInstance"]), (True, True), f"{path}.cacheEvents[{index}].state")

    verify_assembly_modes(result, path, closure, feature_off)
    verify_type_resolutions(result, path, closure, feature_off)
    expected_data = "81:M07-INLINE-DATA|82:M07-DATA-LIST-82,83:M07-DATA-LIST-83|" + data_marker
    require(any(row["name"] == "scriptable-object-state" and row["actual"] == expected_data for row in result["checks"]),
            f"{path}: active ScriptableObject data marker evidence differs")


def verify_case(path, manifest, baseline, fixtures, baseline_resources, on_build, off_build):
    mode = Path(path).stem[4:]
    build = off_build if mode == "T07-14-FeatureOff" else on_build
    path, result = verify_result_header(path, manifest, baseline, build)
    patch_id = MODE_PATCH[result["mode"]]
    feature_off = patch_id is None
    patch_item = None if feature_off else fixtures[patch_id]
    if feature_off:
        for key in ("patchId", "patchManifestPath", "patchManifestSha256"):
            exact(result[key], "", f"{path}.{key}")
        selected = baseline_resources
        closure = []
    else:
        patch_item = fixtures[patch_id]
        exact(result["patchId"], patch_id, f"{path}.patchId")
        exact(result["patchManifestPath"], str(patch_item["path"]), f"{path}.patchManifestPath")
        exact(result["patchManifestSha256"], digest(patch_item["path"]), f"{path}.patchManifestSha256")
        closure = patch_item["fixture"]["closureLoadOrder"]
        selected = patch_item.get("resources", baseline_resources)
    verify_transaction(result, path, manifest, patch_item)
    verify_resource_observations(result, path, selected, patch_id, closure, feature_off)
    return dict(mode=result["mode"], processId=result["processId"], passed=True, resultSha256=digest(path),
                patchId=patch_id or "", resourceAbiHash=result["selectedResourceAbiHash"])


def prepare_fixture_resources(manifest, baseline, fixtures, baseline_resources):
    for patch_id, item in fixtures.items():
        fixture = item["fixture"]
        if patch_id == "P05":
            root = canonical(fixture["replacementResourcePath"], manifest["_path"], "P05 replacementResourcePath", True)
            exact(root, Path(manifest["_path"]).parent / "P05-Resources", f"{manifest['_path']}.P05.replacementResourcePath")
            receipt = bound(fixture["replacementResourceReceiptPath"], fixture["replacementResourceReceiptSha256"],
                            manifest["_path"], "P05 replacementResourceReceiptPath")
            exact(receipt, root / "resource-build-receipt.json", f"{manifest['_path']}.P05.replacementResourceReceiptPath")
            exact(fixture["replacementBundleNames"], list(BUNDLES), f"{manifest['_path']}.P05.replacementBundleNames")
            resources = verify_resource_baseline(root, fixture["resourceAbiHash"], baseline, ["ASSEMBLY_SHADOW_P05"])
            exact(resources["receipt"]["resourceAbiHash"], item["patch"]["resourceAbiHash"],
                  f"{manifest['_path']}.P05.resourceAbiHash")
            item["resources"] = resources
        else:
            require(fixture["replacementResourcePath"] in (None, "") and
                    fixture["replacementResourceReceiptPath"] in (None, "") and
                    fixture["replacementResourceReceiptSha256"] in (None, "") and
                    fixture["replacementBundleNames"] in (None, []),
                    f"{manifest['_path']}.{patch_id}: code-only fixture claims replacement resources")
            item["resources"] = baseline_resources


def verify_results(result_dir, manifest, baseline, fixtures, baseline_resources, on_build, off_build,
                   allow_incomplete=False):
    root = canonical(str(result_dir), result_dir, "resultDir", True)
    paths = [path for path in root.glob("m07-*.json") if not path.name.endswith("-diagnostics.json")]
    expected_files = {"m07-" + mode + ".json" for mode in MODES}
    actual_files = {path.name for path in paths}
    require(actual_files <= expected_files, f"{root}: unknown M07 result files")
    missing = sorted(expected_files - actual_files)
    require(not missing or allow_incomplete, f"{root}: incomplete M07 process coverage: {missing}")
    require(paths, f"{root}: no M07 process results")
    results = [verify_case(path, manifest, baseline, fixtures, baseline_resources, on_build, off_build)
               for path in sorted(paths)]
    require(len({row["processId"] for row in results}) == len(results),
            f"{root}: every M07 mode requires a fresh process")
    raw_files = {path.name for path in root.glob("m07-*-diagnostics.json")}
    expected_raw = {"m07-" + row["mode"] + "-diagnostics.json" for row in results}
    exact(raw_files, expected_raw, f"{root}: raw diagnostic inventory")
    return {
        "milestone": "M07", "resultPassed": not missing, "diagnosticOnly": bool(missing),
        "missingModes": [name[4:-5] for name in missing], "baselineBuildId": manifest["baselineBuildId"],
        "runtimeAbiHash": manifest["runtimeAbiHash"], "resourceAbiHash": baseline["resourceAbiHash"],
        "gate": "Gate 3B", "modes": results,
        "evidence": "Byte-bound compiler, linked Player, native metadata, patch and seven-bundle resources; P05 atomic rebuilt catalog; three structural rejections; exact Editor replay and fresh IL2CPP process observations. Unsigned evidence is not authentication.",
    }


def verify_suite(fixture_manifest, result_dir, on_build_path, off_build_path, allow_incomplete=False,
                 replay_receipt=None):
    manifest, baseline, fixtures, rejected, baseline_resources = verify_inputs(fixture_manifest)
    prepare_fixture_resources(manifest, baseline, fixtures, baseline_resources)
    on_build = verify_player(on_build_path, manifest, baseline, baseline_resources, "NativeOn")
    off_build = verify_player(off_build_path, manifest, baseline, baseline_resources, "NativeOff")
    exact(on_build["path"], Path(manifest["playerBuildReceiptPath"]), f"{manifest['_path']}.playerBuildReceiptPath")
    exact(digest(on_build["path"]), manifest["playerBuildReceiptSha256"], f"{manifest['_path']}.playerBuildReceiptSha256")
    exact(on_build["root"], Path(manifest["baselineInputSnapshot"]), f"{manifest['_path']}.baselineInputSnapshot")
    for key in ("root", "output"):
        require(on_build[key] != off_build[key], f"M07 native ON/OFF {key} must be distinct")
    for key in ("inputSnapshotHash", "nativeLibrarySha256", "buildGuid"):
        require(on_build["player"][key] != off_build["player"][key], f"M07 native ON/OFF {key} must be distinct")
    exact(managed_player_inputs(on_build["snapshot"], on_build["path"]),
          managed_player_inputs(off_build["snapshot"], off_build["path"]),
          "M07 native ON/OFF managed Player inputs")
    exact(on_build["player"]["resourceBuildReceiptSha256"], off_build["player"]["resourceBuildReceiptSha256"],
          "M07 native ON/OFF resource receipt")
    replay_path = Path(replay_receipt) if replay_receipt else Path(manifest["_path"]).with_name("m07-editor-replay.json")
    verify_replay(replay_path, manifest, baseline, fixtures, rejected, on_build, baseline_resources)
    return verify_results(result_dir, manifest, baseline, fixtures, baseline_resources, on_build, off_build,
                          allow_incomplete)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture-manifest", "result-dir", "on-build", "off-build", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--replay-receipt", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="diagnostic only; missing modes can never produce full PASS")
    args = parser.parse_args(argv)
    try:
        result = verify_suite(args.fixture_manifest.absolute(), args.result_dir.absolute(),
                              args.on_build.absolute(), args.off_build.absolute(), args.allow_incomplete,
                              args.replay_receipt.absolute() if args.replay_receipt else None)
        output = args.output.absolute()
        require(not output.exists() and not output.is_symlink() and str(output) == str(output.resolve()),
                f"Refusing existing/symlinked/aliased output: {output}")
        canonical(str(output.parent), output, "output parent", True)
        text = json.dumps(result, indent=2) + "\n"
        with output.open("x", encoding="utf-8") as stream: stream.write(text)
        print(text, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError, StopIteration, IndexError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
