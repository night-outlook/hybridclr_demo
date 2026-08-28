"""Strict, read-only M05 offline input and real-process evidence gate.

M04 domains remain untouched. This module composes byte-bound primitives and
independently decodes M05 types and linked wrapper IL. Unsigned evidence is not
authentication; the bound Editor replay owns complete semantic/resource policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import m04_results as prior
import m05_raw_type_admissions as raw_admissions
from m05_types import (TYPE_FIELDS, INVENTORY_FIELDS, read_type_inventory, read_method_witnesses,
                       MethodProof, METHOD_SELECTION, TypeKeyReader)
from shadow_tools import VerificationError, require, unique_object

CANDIDATES, INTERNAL, PROVIDER_ORDER = prior.CANDIDATES, prior.INTERNAL, prior.PROVIDER_ORDER
MANIFEST_FIELDS = prior.MANIFEST_FIELDS + " rejectedFixtures"
FIXTURE_FIELDS = prior.FIXTURE_FIELDS + " typeInventories"
PLAYER_FIELDS = prior.PLAYER_FIELDS + " typeProofPath typeProofSha256"
REJECTED_FIELDS = "fixtureId defines changedRoots compileSnapshot compileSnapshotHash errorCode errorMessage dllPath dllSha256 assemblyIdentity typeInventory"
PROOF_FIELDS = "schemaVersion milestone policy compileSnapshotHash linkedPlayerReceiptHash nativeLibrarySha256 buildGuid developmentBuild assemblies moduleMethods"
METHOD_FIELDS = "declaringType name signature hasBody implementationFlags instructions"
REPLAY_FIELDS = prior.REPLAY_FIELDS + " typeProofPath typeProofSha256 replayScratchPath rejectedFixtures"
STABLE_DOMAIN = "m05-stable-aot:1\n"
REPLAY_POLICY = "compiler-linked-policy-resource-type-world:1"
MVID_POLICY = prior.MVID_POLICY
TYPE_INFO_FIELDS = "schemaVersion logicalAssembly executionModeCode executionMode isActive physicalImageKind typeKey inputTypePointer activeTypePointer baselineTypePointer pointerDetailsAvailable baselinePointerAvailable containsShadowTypes definitionCacheHits definitionCacheMisses compositeRebuilds allocationRemaps guardFailures"
TYPE_INFO_INTS = ("schemaVersion", "executionModeCode")
TYPE_INFO_BOOLS = ("isActive", "pointerDetailsAvailable", "baselinePointerAvailable", "containsShadowTypes")
TYPE_INFO_COUNTERS = ("definitionCacheHits", "definitionCacheMisses", "compositeRebuilds", "allocationRemaps", "guardFailures")
REQUIRED_MODES = frozenset([f"T05-{n:02d}-{p}" for n in (1, 2, 3, 5, 8, 10) for p in ("P01", "P03")] +
                           ["T05-04-EarlyType", "T05-06-P01", "T05-07-P03", "T05-09-LayoutMismatch",
                            "T05-11-FeatureOff", "T05-12-BenchmarkOn", "T05-13-BenchmarkOff"])
OFF_MODES = {"T05-11-FeatureOff", "T05-13-BenchmarkOff"}


def _precise_allocation_guard(detail):
    namespace, leaf = RESOURCE_COMPONENT.rsplit(".", 1)
    part = lambda text: str(len(text.encode("utf-8"))) + ":" + text
    key = "type(" + part(INTERNAL.casefold()) + "/" + part(namespace) + "/" + part(leaf) + "@0)"
    site = " Site=Object::NewAllocSpecific"
    if detail == "ShadowFieldLayoutMismatch " + key + site:
        return True
    match = re.fullmatch(re.escape("ShadowLayoutMismatch " + key + site) +
                         r" BaselineSize=([0-9]+) ActiveSize=([0-9]+)", detail or "")
    if match is None:
        return False
    if any(len(value) > 10 or (len(value) > 1 and value[0] == "0") for value in match.groups()):
        return False
    baseline_size, active_size = int(match[1]), int(match[2])
    return (0 < baseline_size < 1 << 32 and 0 < active_size < 1 << 32 and
            baseline_size != active_size)
NEGATIVE_MODES = {"T05-04-EarlyType", "T05-09-LayoutMismatch"}
RESULT_FIELDS = "schemaVersion processId milestone mode result error unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash il2cpp fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 typeProofPath typeProofSha256 patchId patchManifestPath patchManifestSha256 compileSnapshotHash rawDiagnosticsPath rawDiagnosticsSha256 moduleMvidObservationPolicy businessMarker configure begin stage validate commit abort stateCode state diagnosticsCode executionModeCode executionMode allocationException nativeDiagnosticsJson stageOrder checks snapshots actualLogicalAssemblies assemblyObservations typeObservations typeResolutionObservations typeEnumerations memberObservations identityObservations assignabilityObservations loadObservations sceneObservations stageResults benchmark ordinary"
RESULT_ARRAYS = "stageOrder checks snapshots actualLogicalAssemblies assemblyObservations typeObservations typeResolutionObservations typeEnumerations memberObservations identityObservations assignabilityObservations loadObservations sceneObservations stageResults"
TYPE_OBSERVATION_FIELDS = "requested fullName assemblyName kind genericDefinition elementShape genericArguments isActive sameType isAssignable castSucceeded"
MEMBER_FIELDS = "declaringType reflectedType memberName memberKind returnType fieldType parameterTypes sameMember activeOwner"
SCENE_FIELDS = "phase bundleName bundlePath bundleSha256 scenePath componentAssemblyName componentType businessMarker error serializedValue baseSerializedValue dataSerializedValue loaded activeType referenceIdentity"
BENCHMARK_FIELDS = "enabled finalSameType warmupCount lookupCount elapsedTicks stopwatchFrequency checksum requestedName finalTypeName finalAssemblyName"
_fields, _obj, _array, _strings, _bool = prior._fields, prior._obj, prior._array, prior._strings, prior._bool
_same, _exact, _names, _name_set, digest = prior._same, prior._exact, prior._names, prior._name_set, prior.digest


def _canonical(value, path, field, directory=False):
    result = prior._absolute(value, path, field, directory)
    require(type(value) is str and value == str(result.resolve()), f"{path}: aliased {field} path")
    return result


def _bound_file(value, sha256, path, field):
    file = _canonical(value, path, field)
    prior._hash(sha256, path, field + "Sha256")
    require(digest(file) == sha256, f"{path}: {field} hash differs from actual bytes")
    return file


def expected_defines(patch_id):
    require(patch_id in ("P01", "P03", "LayoutMismatch"), "Unsupported M05 fixture")
    result = ["ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M04", "ASSEMBLY_SHADOW_M05"]
    if patch_id == "P03": result += ["ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M04_P03", "ASSEMBLY_SHADOW_M05_P03"]
    if patch_id == "LayoutMismatch": result += ["ASSEMBLY_SHADOW_M05_LAYOUT_MISMATCH"]
    return result


def verify_type_inventories(claimed, identities, path):
    rows = _array(claimed, path)
    actual = [read_type_inventory(identity["path"], identity["sha256"], identity["name"])
              for identity in sorted(identities, key=lambda row: row["name"])]
    for assembly in rows:
        _fields(assembly, INVENTORY_FIELDS, path)
        prior._s(assembly["assemblyName"], path, "assemblyName")
        for definition in _array(assembly["types"], path):
            _fields(definition, TYPE_FIELDS, path)
            _strings(definition, path, "fullName namespaceName name kind")
            require(type(definition["genericArity"]) is int and 0 <= definition["genericArity"] <= 65536,
                    f"{path}: invalid metadata generic arity")
            _bool(definition["isExported"], path)
            require(all(type(n) is str and n for n in _array(definition["nestingPath"], path)), f"{path}: invalid nesting path")
            require(definition["kind"] in ("class", "interface", "valuetype", "enum"), f"{path}: invalid type kind")
    require(_same(rows, actual), f"{path}: type inventory differs from actual DLL TypeDef rows")
    return {assembly["assemblyName"]: assembly["types"] for assembly in actual}


def verify_type_proof(player, snapshot, path):
    proof_path = _bound_file(player["typeProofPath"], player["typeProofSha256"], path, "typeProofPath")
    require(proof_path == Path(player["inputSnapshot"]) / "m05-type-proof.json", f"{path}: type proof is not the snapshot companion")
    proof = _obj(proof_path, PROOF_FIELDS)
    require(type(proof["schemaVersion"]) is int and proof["schemaVersion"] == 1 and proof["milestone"] == "M05" and
            proof["policy"] == "active-type-world:1", f"{proof_path}: invalid type proof schema/domain")
    expected = dict(compileSnapshotHash=snapshot["snapshotHash"], linkedPlayerReceiptHash=snapshot["linkedPlayerReceiptHash"],
                    nativeLibrarySha256=player["nativeLibrarySha256"], buildGuid=player["buildGuid"])
    for key, value in expected.items(): require(proof[key] == value, f"{proof_path}: type proof cross-build {key}")
    require(type(snapshot["playerBuildOptions"]) is int and snapshot["playerBuildOptions"] & 1 and
            _bool(proof["developmentBuild"], proof_path), f"{proof_path}: actual development Player proof required")
    verify_type_inventories(proof["assemblies"], player["assemblyIdentities"], proof_path)
    mscorlib = next(a for a in player["assemblyIdentities"] if a["name"] == "mscorlib")
    actual = read_method_witnesses(mscorlib["path"])
    for row in _array(proof["moduleMethods"], proof_path):
        _fields(row, METHOD_FIELDS, proof_path)
        _strings(row, proof_path, "declaringType name signature")
        _bool(row["hasBody"], proof_path)
        require(type(row["implementationFlags"]) is int and 0 <= row["implementationFlags"] <= 65535,
                f"{proof_path}: invalid method implementation flags")
        require(all(type(value) is str for value in _array(row["instructions"], proof_path)), f"{proof_path}: invalid IL witness")
    require(_same(proof["moduleMethods"], actual), f"{proof_path}: method witnesses differ from actual linked DLL IL")
    runtime = next(a for a in player["assemblyIdentities"] if a["name"] == "HybridCLR.Runtime")
    linked_fields = MethodProof(Path(runtime["path"]).read_bytes(), runtime["path"]).fields("HybridCLR.AssemblyShadowTypeResolutionInfo")
    public_fields = [field for field in linked_fields if field["flags"] & 7 == 6 and not field["flags"] & 0x10]
    expected_fields = {name: "System.Int32" if name in TYPE_INFO_INTS else "System.Boolean" if name in TYPE_INFO_BOOLS else
                       "System.UInt64" if name in TYPE_INFO_COUNTERS else "System.String" for name in TYPE_INFO_FIELDS.split()}
    require(len(public_fields) == len(expected_fields) and {field["name"]: field["type"] for field in public_fields} == expected_fields,
            f"{proof_path}: actual linked type-resolution DTO field types/inventory differ")
    return proof


def verify_player(path, manifest, baseline, variant):
    path = _canonical(str(path), path, "playerBuildReceipt")
    player = _obj(path, PLAYER_FIELDS)
    require(type(player["schemaVersion"]) is int and player["schemaVersion"] == 1 and player["milestone"] == "M05" and
            player["variant"] == variant, f"{path}: M05 Player schema/variant mismatch")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(player[key] == manifest[key], f"{path}: Player {key} differs")
    flag = "1" if variant == "NativeOn" else "0"
    require(player["nativeArguments"] == '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + flag + '"', f"{path}: wrong native feature switch")
    root = _canonical(player["inputSnapshot"], path, "inputSnapshot", True)
    require(path == root / "m05-player-build.json", f"{path}: noncanonical M05 Player receipt")
    snapshot = prior._verify_snapshot(root, manifest["baselineBuildId"], manifest["runtimeAbiHash"], baseline, path, variant == "NativeOn")
    for key, source in (("inputSnapshotHash", "snapshotHash"), ("buildGuid", "buildGuid"), ("playerOutput", "playerOutput"),
                        ("nativeLibraryPath", "nativeLibraryPath"), ("nativeLibrarySha256", "nativeLibrarySha256")):
        require(player[key] == snapshot[source], f"{path}: Player snapshot {key} differs")
    output = _canonical(player["playerOutput"], path, "playerOutput", True)
    native = _bound_file(player["nativeLibraryPath"], player["nativeLibrarySha256"], path, "nativeLibraryPath")
    require(native.is_relative_to(output), f"{path}: native library outside Player")
    prior._pins(snapshot["sourcePins"], path, baseline["sourcePins"])
    prior._snapshot_files(snapshot, root, path)
    prior._verify_linked_player(root, snapshot, {a["name"]: a for a in baseline["assemblies"]}, path)
    prior._reflection_snapshot(root, snapshot, path, require_linked=True)
    raw = raw_admissions.verify_snapshot(root, snapshot, require_linked=True)
    require(raw["configurationSha256"] == raw_admissions.control_hash(manifest["_snapshot"]["extraScriptingDefines"], path),
            f"{path}: executed Player raw admission configuration differs from baseline")
    linked = snapshot["linkedPlayerReceipt"]["assemblies"]
    identities = prior.verify_identities(player["assemblyIdentities"], [prior._rel(root / "LinkedPlayer", a["path"], path, "linked DLL") for a in linked], path)
    for row in linked:
        actual = next(a for name, a in identities.items() if name.casefold() == row["name"].casefold())
        require(actual["mvid"] == row["mvid"], f"{path}: linked MVID differs from actual DLL")
    prior._verify_native_metadata(player, path)
    placeholder = _bound_file(player["placeholderManifestPath"], player["placeholderManifestSha256"], path, "placeholderManifestPath")
    require(placeholder == root / "m05-placeholder-AssemblyManifest.cpp", f"{path}: incorrect placeholder snapshot")
    _exact(player["placeholderAssemblyNames"], prior.parse_placeholders(placeholder.read_bytes(), placeholder), path, "placeholder names")
    proof = verify_type_proof(player, snapshot, path)
    return player, snapshot, proof


def verify_baseline(manifest, path, m01_root):
    baseline_path = _bound_file(manifest["baselineManifestPath"], manifest["baselineManifestSha256"], path, "baselineManifestPath")
    baseline = _obj(baseline_path)
    require(type(baseline["schemaVersion"]) is int and baseline["schemaVersion"] == baseline["semanticHashSchema"] == 1,
            f"{baseline_path}: invalid baseline schema")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(baseline[key] == manifest[key], f"{baseline_path}: baseline {key} differs")
    prior._pins(baseline["sourcePins"], baseline_path)
    require(prior._runtime_abi_hash(baseline["sourcePins"], baseline_path) == manifest["runtimeAbiHash"], f"{baseline_path}: runtime ABI differs")
    _name_set(baseline["shadowCandidates"], CANDIDATES, baseline_path, "shadowCandidates")
    prior._hash(baseline["bootstrapAbiHash"], baseline_path, "bootstrapAbiHash")
    prior._resource_abi_hash(baseline["resourceAbiHash"], baseline_path, "resourceAbiHash")
    descriptors = baseline["assemblies"]
    _names([a["name"] for a in descriptors], baseline_path, "prelink baseline names")
    for row in descriptors:
        actual = prior.read_identity(prior._rel(baseline_path.parent, row["filePath"], baseline_path, "baseline DLL"))
        require(all(actual[key] == row[key] for key in ("name", "mvid", "sha256")), f"{baseline_path}: actual PRELINK baseline identity differs")
    frozen, _, _, reflection = prior._verify_player_snapshot(baseline_path.parent, baseline, {a["name"]: a for a in descriptors}, baseline_path)
    prior._reflection_manifest(baseline, reflection, baseline_path)
    require(baseline["playerInputSnapshot"] == "PlayerInputs", f"{baseline_path}: noncanonical frozen Player input root")
    frozen_root = _canonical(str(baseline_path.parent / "PlayerInputs"), baseline_path, "frozen Player inputs", True)
    frozen_raw = raw_admissions.verify_snapshot(frozen_root, frozen, require_linked=True)
    root = _canonical(manifest["baselineInputSnapshot"], path, "baselineInputSnapshot", True)
    snapshot = prior._verify_snapshot(root, manifest["baselineBuildId"], manifest["runtimeAbiHash"], baseline, path)
    raw = raw_admissions.verify_snapshot(root, snapshot, require_linked=True)
    require(raw["configurationSha256"] == frozen_raw["configurationSha256"], f"{path}: frozen raw admission configuration differs")
    require(manifest["baselineInputSnapshotHash"] == frozen["snapshotHash"] == snapshot["snapshotHash"] and
            frozen["linkedPlayerReceiptHash"] == snapshot["linkedPlayerReceiptHash"] and snapshot["buildGuid"] == baseline["playerBuildGuid"],
            f"{path}: frozen and captured baseline Player proofs differ")
    m01 = _canonical(str(m01_root), path, "m01BaselineRoot", True)
    prior._verify_bundles(m01, baseline, baseline_path)
    resource = prior._verify_resource_baseline(baseline_path.parent, baseline, baseline_path, m01)
    require(resource["provenance"] == "M01AuditedFrozenSourceReconstruction" and resource["compilerSnapshotHash"] == snapshot["snapshotHash"],
            f"{path}: frozen M01 resource proof does not bind M05")
    lines = manifest["stableAotProvenance"].split("\n")
    require([line.partition("=")[0] for line in lines] == ["framework", "compiler-libraries", "linked-player", "bootstrap-policy", "physical"],
            f"{path}: stable authorization provenance fields/order differ")
    for line in lines[:2]: prior._hash(line.partition("=")[2], path, "compiler proof hash")
    stable = manifest["stableAotNames"]
    require(lines[2] == "linked-player=" + snapshot["linkedPlayerReceiptHash"] and
            lines[3] == "bootstrap-policy=" + ",".join(sorted(n.casefold() for n in baseline["bootstrapAssemblies"])) and
            lines[4] == "physical=" + ",".join(stable), f"{path}: stable authorization provenance differs")
    require(set(stable) <= {a["name"] for a in snapshot["linkedPlayerReceipt"]["assemblies"]}, f"{path}: stable authorization includes unlinked assembly")
    return baseline, snapshot


def verify_compile(fixture, baseline, path):
    root = _canonical(fixture["compileSnapshot"], path, "compileSnapshot", True)
    receipt_path = root / "assembly-snapshot.json"
    snapshot = _obj(receipt_path)
    require(type(snapshot["schemaVersion"]) is int and snapshot["schemaVersion"] == 1 and snapshot["kind"] == "CompilePlayerScripts" and
            prior._linked_claim_absent(snapshot) and not (root / "LinkedPlayer").exists(), f"{receipt_path}: compiler snapshot claims Player proof")
    prior._pins(snapshot["sourcePins"], receipt_path, baseline["sourcePins"])
    for key in ("unityVersion", "target", "architecture"):
        require(snapshot[key] == baseline[key], f"{receipt_path}: compiler {key} differs")
    prior._snapshot_files(snapshot, root, receipt_path)
    require(snapshot["snapshotHash"] == fixture["compileSnapshotHash"] == prior._snapshot_hash(snapshot, root, receipt_path), f"{receipt_path}: compiler snapshot hash differs")
    prior._reflection_snapshot(root, snapshot, receipt_path)
    raw_admissions.verify_snapshot(root, snapshot)
    user_defines = [d for d in _names(snapshot["extraScriptingDefines"], receipt_path, "extraScriptingDefines")
                   if not d.startswith(("ASSEMBLY_SHADOW_REFLECTION_BINDINGS_", raw_admissions.PREFIX))]
    _name_set(user_defines, fixture["defines"], receipt_path, "actual compiler defines")
    return root, snapshot


def _no_rejected_output(parent, path):
    output = parent / "LayoutMismatch-must-not-be-admitted"
    require(not output.exists() and not output.is_symlink() and not list(parent.glob(output.name + ".building-*")),
            f"{path}: rejected fixture produced admitted/partial output")


def verify_inputs(path, m01_root):
    path = _canonical(str(path), path, "fixtureManifest")
    manifest = _obj(path, MANIFEST_FIELDS)
    require(type(manifest["schemaVersion"]) is int and manifest["schemaVersion"] == 1 and manifest["milestone"] == "M05" and
            re.fullmatch(r"M05-Baseline-[A-Za-z0-9_.-]+", manifest["baselineBuildId"]) is not None,
            f"{path}: fresh M05 baseline/domain required")
    require((manifest["unityVersion"], manifest["target"], manifest["architecture"]) == ("2022.3.62f2", "StandaloneOSX", "arm64"), f"{path}: unsupported Player target")
    _exact(manifest["candidateNames"], CANDIDATES, path, "candidateNames")
    _exact(manifest["closureLoadOrder"], PROVIDER_ORDER, path, "closureLoadOrder")
    stable = _names(manifest["stableAotNames"], path, "stableAotNames")
    require(stable and stable == sorted(stable) and not {n.casefold() for n in stable} & {n.casefold() for n in CANDIDATES}, f"{path}: invalid stable AOT domain")
    prior._hash(manifest["runtimeAbiHash"], path, "runtimeAbiHash")
    require(manifest["stableAotProvenanceHash"] == hashlib.sha256((STABLE_DOMAIN + manifest["stableAotProvenance"]).encode()).hexdigest(), f"{path}: invalid M05 stable domain hash")
    baseline, snapshot = verify_baseline(manifest, path, m01_root)
    normal, fixtures = _array(manifest["fixtures"], path), {}
    _exact([f["patchId"] for f in normal], ["P01", "P03"], path, "normal fixture set/order")
    for fixture in normal:
        _fields(fixture, FIXTURE_FIELDS, path)
        pid = fixture["patchId"]
        order = [INTERNAL] if pid == "P01" else PROVIDER_ORDER
        _name_set(fixture["defines"], expected_defines(pid), path, "exact fixture defines")
        _name_set(fixture["changedRoots"], order, path, "changedRoots")
        _exact(fixture["closureLoadOrder"], order, path, "closureLoadOrder")
        _exact(fixture["stableAotNames"], stable, path, "fixture stableAotNames")
        compile_root, compiled = verify_compile(fixture, baseline, path)
        require(raw_admissions.control_hash(compiled["extraScriptingDefines"], path) == raw_admissions.control_hash(snapshot["extraScriptingDefines"], path),
                f"{path}: fixture raw admission configuration differs from baseline")
        patch_root = _canonical(fixture["patchDirectory"], path, "patchDirectory", True)
        patch_path = _bound_file(fixture["patchManifest"], fixture["patchManifestSha256"], path, "patchManifest")
        require(patch_root == path.parent / pid and patch_path == patch_root / "patch-manifest.json", f"{path}: fixture patch is outside immutable root")
        item = fixture, patch_root, patch_path, compile_root, compiled
        prior._verify_patch(pid, item, manifest, baseline)
        require(_artifact_tree(compile_root / "RawTypeAdmissions") == _artifact_tree(patch_root / "RawTypeAdmissions"),
                f"{patch_path}: copied raw admission evidence differs from actual compiler proof")
        verify_type_inventories(fixture["typeInventories"], fixture["assemblyIdentities"], patch_path)
        fixtures[pid] = item
    rejected = _array(manifest["rejectedFixtures"], path)
    require(len(rejected) == 1, f"{path}: exactly one separate rejected fixture required")
    bad = _fields(rejected[0], REJECTED_FIELDS, path)
    require(bad["fixtureId"] == "LayoutMismatch" and bad["errorCode"] == "ResourceRebuildRequired" and type(bad["errorMessage"]) is str and bad["errorMessage"],
            f"{path}: required actual resource rejection absent")
    _name_set(bad["defines"], expected_defines("LayoutMismatch"), path, "rejected defines")
    _exact(bad["changedRoots"], [INTERNAL], path, "rejected changedRoots")
    compile_root, compiled = verify_compile(bad, baseline, path)
    require(raw_admissions.control_hash(compiled["extraScriptingDefines"], path) == raw_admissions.control_hash(snapshot["extraScriptingDefines"], path),
            f"{path}: rejected fixture raw admission configuration differs from baseline")
    source = next(a for a in compiled["assemblies"] if a["name"] == INTERNAL)
    dll = _bound_file(bad["dllPath"], bad["dllSha256"], path, "rejected DLL")
    require(dll == prior._rel(compile_root, source["path"], path, "rejected compiler DLL") and bad["dllSha256"] == source["sha256"], f"{path}: rejected DLL is not actual compiler output")
    prior.verify_identities([bad["assemblyIdentity"]], [dll], path)
    verify_type_inventories([bad["typeInventory"]], [bad["assemblyIdentity"]], path)
    baseline_file = next(row for row in baseline["assemblies"] if row["name"] == INTERNAL)
    baseline_dll = prior._rel(Path(manifest["baselineManifestPath"]).parent, baseline_file["filePath"], path, "layout baseline DLL")
    target_type = "AssemblyA.Implementation.Internal.VersionedPrefabComponent"
    before = [f for f in MethodProof(baseline_dll.read_bytes(), baseline_dll).fields(target_type) if not f["flags"] & 0x10]
    after = [f for f in MethodProof(dll.read_bytes(), dll).fields(target_type) if not f["flags"] & 0x10]
    before_by_name, after_by_name = {f["name"]: f for f in before}, {f["name"]: f for f in after}
    require(len(before_by_name) == len(before) and len(after_by_name) == len(after) and
            all(after_by_name.get(name) == field for name, field in before_by_name.items()) and
            len(after) > len(before) and all(field["type"] == "System.Int32" for name, field in after_by_name.items() if name not in before_by_name),
            f"{path}: rejected bytes do not contain the intended added Int32 instance layout field")
    _no_rejected_output(path.parent, path)
    manifest["_path"], manifest["_snapshot"], manifest["_m01Root"] = str(path), snapshot, str(Path(m01_root))
    return manifest, baseline, fixtures


def _artifact_tree(root):
    root = _canonical(str(root), root, "artifact tree", True)
    files = {}
    for path in root.rglob("*"):
        require(not path.is_symlink(), f"{path}: symlinked replay artifact")
        if path.is_file(): files[path.relative_to(root).as_posix()] = digest(path)
    return files


def verify_replay(path, manifest, baseline, fixtures, player, player_path):
    replay = _obj(path, REPLAY_FIELDS)
    require(type(replay["schemaVersion"]) is int and replay["schemaVersion"] == 1 and replay["milestone"] == "M05" and replay["result"] == "Passed" and
            replay["comparisonPolicy"] == REPLAY_POLICY, f"{path}: invalid M05 replay schema/domain/result")
    bindings = {key: manifest[key] for key in "baselineManifestPath baselineManifestSha256 baselineInputSnapshotHash baselineBuildId runtimeAbiHash unityVersion target architecture stableAotProvenanceHash".split()}
    bindings.update(fixtureManifestPath=manifest["_path"], fixtureManifestSha256=digest(Path(manifest["_path"])),
                    playerBuildReceiptPath=str(player_path), playerBuildReceiptSha256=digest(player_path),
                    playerBuildGuid=player["buildGuid"], nativeLibrarySha256=player["nativeLibrarySha256"],
                    linkedPlayerReceiptHash=manifest["_snapshot"]["linkedPlayerReceiptHash"],
                    typeProofPath=player["typeProofPath"], typeProofSha256=player["typeProofSha256"])
    for key, value in bindings.items(): require(replay[key] == value, f"{path}: replay binding differs: {key}")
    prior._pins(replay["validatorSourcePins"], path, baseline["sourcePins"])
    scratch = _canonical(replay["replayScratchPath"], path, "replayScratchPath", True)
    require(scratch.name.startswith("M05Replay-") and scratch.parent == Path(manifest["_path"]).parent.parent,
            f"{path}: noncanonical fresh replay scratch identity")
    rows = _array(replay["fixtures"], path)
    require(len(rows) == len(fixtures), f"{path}: replay normal fixture count differs")
    for row, (pid, item) in zip(rows, fixtures.items()):
        _fields(row, "patchId patchManifestSha256 compileSnapshotHash changedRoots closureLoadOrder", path)
        require(_same(row, {key: item[0][key] for key in row}), f"{path}: replay normal fixture differs")
        replayed = _canonical(str(scratch / pid), path, "replayed patch", True)
        require(_artifact_tree(item[1]) == _artifact_tree(replayed), f"{path}: replayed artifact tree differs byte-for-byte")
    rows = _array(replay["rejectedFixtures"], path)
    require(len(rows) == 1, f"{path}: missing rejected replay")
    _fields(rows[0], "fixtureId compileSnapshotHash dllSha256 errorCode errorMessage", path)
    require(_same(rows[0], {key: manifest["rejectedFixtures"][0][key] for key in rows[0]}), f"{path}: actual rejection replay differs")
    _no_rejected_output(scratch, path)
    return replay


def verify_type_info(value, path):
    info = _fields(value, TYPE_INFO_FIELDS, path)
    require(type(info["schemaVersion"]) is int and info["schemaVersion"] == 1 and
            type(info["executionModeCode"]) is int and info["executionModeCode"] in (0, 1), f"{path}: type-info schema/mode code differs")
    for key in TYPE_INFO_BOOLS: _bool(info[key], path)
    for key in TYPE_INFO_COUNTERS: prior._uint64(info[key], path)
    for key in set(TYPE_INFO_FIELDS.split()) - set(TYPE_INFO_INTS) - set(TYPE_INFO_BOOLS) - set(TYPE_INFO_COUNTERS):
        require(type(info[key]) is str, f"{path}: missing type-info string: {key}")
    require(info["logicalAssembly"] and info["typeKey"] and info["executionMode"] == ("AotBaseline", "InterpreterShadow")[info["executionModeCode"]] and
            info["physicalImageKind"] in ("Aot", "Interpreter"), f"{path}: invalid type-info identity/mode")
    for key in ("inputTypePointer", "activeTypePointer", "baselineTypePointer"):
        available = info["baselinePointerAvailable"] if key == "baselineTypePointer" else info["pointerDetailsAvailable"]
        require((bool(re.fullmatch(r"0x[0-9a-f]{1,16}", info[key])) and int(info[key][2:], 16) > 0) if available else info[key] == "",
                f"{path}: pointer value/availability mismatch: {key}")
    require(not info["baselinePointerAvailable"] or info["pointerDetailsAvailable"], f"{path}: baseline pointer available without pointer details")
    return info


def verify_type_resolution(row, inventories, identities, closure, path, field_annotations=()):
    _fields(row, "operation requested rawJson info sameType", path)
    _strings(row, path, "operation requested rawJson")
    require(row["operation"] and row["requested"] and row["rawJson"] and _bool(row["sameType"], path), f"{path}: missing actual type-resolution observation")
    info = verify_type_info(row["info"], path)
    try: raw = json.loads(row["rawJson"], object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error: raise VerificationError(f"{path}: invalid/duplicate raw type-info JSON") from error
    verify_type_info(raw, path)
    require(_same(raw, info), f"{path}: raw and typed type-resolution diagnostics differ")
    actual = TypeKeyReader(info["typeKey"], inventories, identities, closure, path, field_annotations=field_annotations).read()
    owner = actual["assemblyName"]
    require(info["logicalAssembly"] == owner and row["requested"] == actual["fullName"] and info["isActive"] and
            info["containsShadowTypes"] == actual["containsShadowTypes"] and
            info["executionModeCode"] == int(owner in closure) and
            info["physicalImageKind"] == ("Interpreter" if owner in closure else "Aot"), f"{path}: type resolution is inconsistent with active byte-bound type components")
    return actual


def verify_result_header(path, manifest, player, player_path):
    result = _obj(path, RESULT_FIELDS)
    require(type(result["schemaVersion"]) is int and result["schemaVersion"] == 1 and result["milestone"] == "M05" and
            result["result"] == "Passed" and result["error"] == "" and result["il2cpp"] is True,
            f"{path}: result is not a successful real IL2CPP M05 observation")
    mode = result["mode"]
    require(mode in REQUIRED_MODES and path.name == "m05-" + mode + ".json", f"{path}: invalid mode/filename")
    require(type(result["processId"]) is int and 0 < result["processId"] < 1 << 31, f"{path}: invalid actual process ID")
    require(result["platform"] == "OSXPlayer" and result["moduleMvidObservationPolicy"] == MVID_POLICY, f"{path}: platform/MVID policy differs")
    for key in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "buildGuid", "typeProofPath", "typeProofSha256"):
        require(result[key] == player[key], f"{path}: result cross-build {key}")
    require(result["playerDataPath"] == str(Path(player["playerOutput"]) / "Contents"), f"{path}: not executed Player data path")
    require(player["variant"] == ("NativeOff" if mode in OFF_MODES else "NativeOn"), f"{path}: wrong native variant for mode")
    expected = dict(fixtureManifestPath=manifest["_path"], fixtureManifestSha256=digest(Path(manifest["_path"])),
                    playerBuildReceiptPath=str(player_path), playerBuildReceiptSha256=digest(player_path))
    for key, value in expected.items(): require(result[key] == value, f"{path}: result immutable binding differs: {key}")
    for key in RESULT_ARRAYS.split(): _array(result[key], path)
    for key in set(RESULT_FIELDS.split()) - set(RESULT_ARRAYS.split()) - {"schemaVersion", "processId", "il2cpp", "benchmark", "ordinary"}:
        require(type(result[key]) is str, f"{path}: missing result string: {key}")
    return result


def verify_benchmark(value, enabled, path):
    benchmark = _fields(value, BENCHMARK_FIELDS, path)
    require(_bool(benchmark["enabled"], path) == enabled and _bool(benchmark["finalSameType"], path), f"{path}: benchmark identity/variant differs")
    for key in ("warmupCount", "lookupCount", "elapsedTicks", "stopwatchFrequency", "checksum"):
        require(type(benchmark[key]) is int and 0 <= benchmark[key] < 1 << 63, f"{path}: benchmark {key} is not Int64")
    require(benchmark["warmupCount"] == 1000 and benchmark["lookupCount"] == benchmark["checksum"] == 100000 and
            benchmark["elapsedTicks"] > 0 and benchmark["stopwatchFrequency"] > 0, f"{path}: missing actual 100k timing/count evidence")
    require(benchmark["requestedName"] == "AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal" and
            benchmark["finalTypeName"] == "AssemblyA.Implementation.Internal.InternalEntry" and benchmark["finalAssemblyName"] == INTERNAL,
            f"{path}: benchmark did not measure the same literal Internal type")


def verify_type_observation(row, actual, path):
    _fields(row, TYPE_OBSERVATION_FIELDS, path)
    _strings(row, path, "requested fullName assemblyName kind genericDefinition elementShape")
    require(all(type(argument) is str for argument in _array(row["genericArguments"], path)), f"{path}: incomplete generic argument names")
    for field in ("isActive", "sameType", "isAssignable", "castSucceeded"): _bool(row[field], path)
    for key in ("fullName", "assemblyName", "kind", "genericDefinition", "elementShape", "genericArguments"):
        require(_same(row[key], actual[key]), f"{path}: actual type observation differs from byte-bound TypeKey: {key}")
    require(row["requested"] == row["fullName"] and row["isActive"] and row["sameType"], f"{path}: type observation is not actual active identity")


RESOURCE_COMPONENT = "AssemblyA.Implementation.Internal.VersionedPrefabComponent"
RESOURCE_DATA = "AssemblyA.Implementation.Internal.VersionedScriptableObject"
RESOURCE_VALUE = "AssemblyA.Contracts.DemoValue"
RESOURCE_MARKER = "BASELINE-EXT|PATCH-P01-INTERNAL|1234"


def resource_field_annotations(identities, path):
    """Bind cached reflection annotations to the actual observed resource fields.

    The pinned reflection cache ignores Il2CppType.attrs when matching a Type
    object. Reading these fields can therefore retain their field flags on the
    later data/value GetType diagnostics. Those flags are not a managed type
    suffix, nor authority to accept arbitrary qualified keys in other modes.
    """
    identity = identities[INTERNAL]
    dll = _bound_file(identity["path"], identity["sha256"], path, "resource component DLL")
    fields = MethodProof(dll.read_bytes(), dll).reflection_fields(RESOURCE_COMPONENT)
    annotations = {}
    for label, field_name, owner, type_name in (("data", "dataReference", INTERNAL, RESOURCE_DATA),
                                               ("value", "value", CANDIDATES[0], RESOURCE_VALUE)):
        matches = [field for field in fields if field["name"] == field_name]
        require(len(matches) == 1, f"{path}: missing/ambiguous actual resource field: {field_name}")
        field = matches[0]
        require(field["type"] == type_name and field["assembly"] == identities[owner]["fullName"] and
                not field["flags"] & 0x10, f"{path}: resource field type/scope/instance binding differs: {field_name}")
        for phase in ("prefab", "scene-first", "scene-reload"):
            annotations["resource:" + phase + ":" + label] = ((owner, type_name, field["flags"]),)
    return annotations


def verify_resources(result, manifest, player, path):
    """Check actual old-resource bytes plus each observed load/reload phase."""
    frozen_root = _canonical(manifest["_m01Root"], path, "frozen M01 root", True)
    frozen_path = _canonical(str(frozen_root / "baseline-manifest.json"), path, "frozen M01 manifest")
    frozen = _obj(frozen_path)
    require(frozen["baselineBuildId"] == "M01-Baseline-v1", f"{path}: incorrect frozen resource baseline")
    bundles = {bundle["name"]: bundle for bundle in frozen["bundles"]}
    require(len(bundles) == len(frozen["bundles"]) == 3 and set(bundles) == {"versioned-data.bundle", "versioned-prefab.bundle", "business-scene.bundle"},
            f"{path}: frozen bundle inventory differs")
    for name, bundle in bundles.items():
        require(bundle["path"] == "Bundles/" + name, f"{path}: unsafe frozen bundle path")
        require(digest(prior._rel(frozen_root, bundle["path"], path, "frozen bundle")) == bundle["sha256"], f"{path}: frozen bundle bytes changed")
    scene_path = next(asset["path"] for asset in frozen["assets"] if asset["kind"] == "scene")
    rows = _array(result["sceneObservations"], path)
    _exact([row["phase"] for row in rows], ["prefab", "scene-first", "scene-reload"], path, "actual resource phases")
    player_output = Path(player["playerOutput"])
    staged_root = None
    for row in rows:
        _fields(row, SCENE_FIELDS, path)
        _strings(row, path, "phase bundleName bundlePath bundleSha256 scenePath componentAssemblyName componentType businessMarker error")
        for name in ("loaded", "activeType", "referenceIdentity"):
            require(_bool(row[name], path), f"{path}: resource {name} observation failed")
        for name in ("serializedValue", "baseSerializedValue", "dataSerializedValue"):
            require(type(row[name]) is int, f"{path}: missing actual serialized integer: {name}")
        bundle_name = "versioned-prefab.bundle" if row["phase"] == "prefab" else "business-scene.bundle"
        bundle = bundles[bundle_name]
        require(row["bundleName"] == bundle_name and row["bundleSha256"] == bundle["sha256"], f"{path}: observed resource bundle differs")
        loaded_path = _bound_file(row["bundlePath"], row["bundleSha256"], path, "loaded resource bundle")
        resource_root = loaded_path.parent.parent
        require(loaded_path.is_relative_to(player_output) and loaded_path.parent.name == "Bundles" and resource_root.name == "M01" and
                resource_root.parent.name == "AssemblyShadow" and (staged_root is None or staged_root == resource_root), f"{path}: resource input outside executed Player's frozen resource root")
        staged_root = resource_root
        require(row["scenePath"] == "" if row["phase"] == "prefab" else row["scenePath"].casefold() == scene_path.casefold(), f"{path}: resource scene path differs")
        require(row["componentAssemblyName"] == INTERNAL and row["componentType"] == RESOURCE_COMPONENT and row["businessMarker"] == RESOURCE_MARKER and
                row["error"] == "" and (row["serializedValue"], row["baseSerializedValue"], row["dataSerializedValue"]) == (1234, 7, 5678),
                f"{path}: old resource identity/values/marker differ")
    _bound_file(str(staged_root / "baseline-manifest.json"), digest(frozen_path), path, "Player frozen manifest")
    expected_checks = [("resource-baseline", "M01-Baseline-v1", 0)]
    for name in ("versioned-data.bundle", "versioned-prefab.bundle", "business-scene.bundle"):
        require(digest(prior._rel(staged_root, bundles[name]["path"], path, "Player resource bundle")) == bundles[name]["sha256"], f"{path}: Player resource bytes differ from frozen originals")
        expected_checks.append(("resource-bundle:" + name, bundles[name]["sha256"], 0))
    expected_resolutions = [("resource:prefab-asset:component", RESOURCE_COMPONENT)]
    for phase in ("prefab", "scene-first", "scene-reload"):
        expected_resolutions += [("resource:" + phase + ":" + label, full_name) for label, full_name in (("component", RESOURCE_COMPONENT), ("data", RESOURCE_DATA), ("value", RESOURCE_VALUE))]
    _exact([(row["operation"], row["requested"]) for row in result["typeResolutionObservations"]], expected_resolutions, path, "actual resource type observations")
    identities = _array(result["identityObservations"], path)
    require(len(identities) == 1, f"{path}: scene reload must observe two actual distinct components")
    identity = _fields(identities[0], "operation left right sameObject", path)
    require(identity["operation"] == "resource:scene-reload:new-component" and not _bool(identity["sameObject"], path), f"{path}: scene reload reused component")
    ids = []
    for field in ("left", "right"):
        require(type(identity[field]) is str, f"{path}: missing observed scene component ID")
        match = re.fullmatch(re.escape(RESOURCE_COMPONENT) + r"#(-?[1-9][0-9]*)", identity[field])
        require(match is not None and -(1 << 31) <= int(match[1]) < 1 << 31, f"{path}: invalid scene component instance ID")
        ids.append(int(match[1]))
    require(ids[0] != ids[1] and result["businessMarker"] == RESOURCE_MARKER, f"{path}: scene reload/marker evidence differs")
    return expected_checks


def verify_enumerations(rows, fixture, baseline_types, path):
    inventories = {assembly["assemblyName"]: assembly["types"] for assembly in fixture["typeInventories"]}
    expected = []
    for name in fixture["closureLoadOrder"]:
        types = inventories[name]
        require(set(row["fullName"] for row in types) - set(row["fullName"] for row in baseline_types[name]),
                f"{path}: enumeration fixture has no actual patch-added type: {name}")
        for operation in ("Assembly.GetTypes", "Assembly.DefinedTypes", "Assembly.ExportedTypes", "Module.GetTypes"):
            expected.append(dict(operation=operation, assemblyName=name,
                                 typeNames=[row["fullName"] for row in types if operation != "Assembly.ExportedTypes" or row["isExported"]]))
    for row in _array(rows, path):
        _fields(row, "operation assemblyName typeNames", path)
        _strings(row, path, "operation assemblyName")
        require(all(type(name) is str and name for name in _array(row["typeNames"], path)), f"{path}: invalid raw type enumeration")
    require(_same(rows, expected), f"{path}: raw type enumeration inventory/API/order differs from actual TypeDef rows")


def verify_members(rows, identities, inventories, closure, path):
    """Validate exact byte-backed canonical signatures; never map by tokens."""
    cache = {}
    for row in _array(rows, path):
        _fields(row, MEMBER_FIELDS, path)
        _strings(row, path, "declaringType reflectedType memberName memberKind returnType fieldType")
        require(all(type(name) is str and name for name in _array(row["parameterTypes"], path)), f"{path}: invalid member parameter types")
        require(_bool(row["sameMember"], path) and _bool(row["activeOwner"], path), f"{path}: member identity/active owner mismatch")
        owners = [name for name in closure if any(t["fullName"] == row["declaringType"] for t in inventories[name])]
        require(len(owners) == 1 and row["reflectedType"] == row["declaringType"], f"{path}: member declaring/reflected owner is not an active patch type")
        owner = owners[0]
        if owner not in cache:
            dll = _bound_file(identities[owner]["path"], identities[owner]["sha256"], path, "member-owner DLL")
            cache[owner] = MethodProof(dll.read_bytes(), dll)
            def scope(type_name,assembly):
                if not assembly.startswith("netstandard, "):return assembly
                targets=[name for name,types in inventories.items() if any(row["fullName"]==type_name for row in types)]
                require(len(targets)==1,f"{path}: facade signature type lacks a unique byte-bound active definition: {type_name}")
                return identities[targets[0]]["fullName"]
            cache[owner].reflection_scope=scope
        actual = cache[owner].reflection_members(row["declaringType"])
        signature = {key: row[key] for key in ("declaringType", "memberName", "memberKind", "returnType", "fieldType", "parameterTypes")}
        require(sum(_same(signature, candidate) for candidate in actual) == 1, f"{path}: member signature absent/ambiguous in actual DLL")


def verify_checks(rows, expected, path):
    """An expected row is (operation, actual value, numeric ABI code)."""
    require(len(_array(rows, path)) == len(expected), f"{path}: missing/extra ordered operation witnesses")
    for row, (name, value, code) in zip(rows, expected):
        _fields(row, "name actual expected actualCode expectedCode", path)
        _strings(row, path, "name actual expected")
        require(row["name"] == name and row["actual"] == row["expected"] == value and
                type(row["actualCode"]) is int and type(row["expectedCode"]) is int and
                row["actualCode"] == row["expectedCode"] == code, f"{path}: ordered check/ABI code differs: {name}")


def verify_phases(result, manifest, player, closure, staged_identities, path):
    """Native state transitions, not copied final snapshots or success flags."""
    mode = result["mode"]
    early, layout = mode == "T05-04-EarlyType", mode == "T05-09-LayoutMismatch"
    phases = ["initial", "staged", "validated"] + (["aborted"] if early else
              ["committed", "allocation-failure"] if layout else
              ["committed", "final-resource"] if mode.startswith("T05-08-") else ["committed", "final"])
    snapshots = _array(result["snapshots"], path)
    _exact([row["phase"] for row in snapshots], phases, path, "fresh transaction phases")
    native_order = [row["name"] for row in sorted(player["nativeAssemblyIdentities"], key=lambda row: row["assemblyIndex"])]
    previous_events, previous_uses = [], []
    for row in snapshots:
        _fields(row, "phase diagnostics", path)
        phase = row["phase"]
        d = prior._diagnostic(row["diagnostics"], f"{path}.{phase}")
        initial, staged = phase == "initial", phase == "staged"
        published = phase in ("committed", "final", "final-resource", "allocation-failure")
        prior._verify_diag_invariants(d, [] if initial else closure, [] if initial else manifest["stableAotNames"], path)
        state = {"initial": "Disabled", "staged": "Staged", "validated": "Validated", "aborted": "Aborted",
                 "committed": "Committed", "final": "Committed", "final-resource": "Committed", "allocation-failure": "FailedAfterCommit"}[phase]
        require(d["state"] == state and d["generation"] == int(published) and
                d["staged"] == (0 if initial else len(closure)), f"{path}.{phase}: native state/staged/publication differs")
        require(d["lastError"] == (16 if phase == "allocation-failure" else 0), f"{path}.{phase}: native error boundary differs")
        require(d["baselineBuildId"] == ("" if initial else manifest["baselineBuildId"]) and
                d["patchId"] == ("" if initial else result["patchId"]), f"{path}.{phase}: native transaction identity differs")
        physical = [(name, False) for name in native_order] + ([(name, True) for name in closure] if published else [])
        require([(a["name"], a["isInterpreter"]) for a in d["ordinaryAssemblies"]] == physical,
                f"{path}.{phase}: physical native/shadow assembly order differs")
        for assembly in d["assemblies"]:
            name = assembly["name"]
            require(name in staged_identities and assembly["mvid"] == staged_identities[name]["mvid"] and assembly["skeletonBuilt"] and
                    assembly["runtimeMetadataInitialized"] == (not staged) and assembly["published"] == published and
                    assembly["moduleInitializerAttempted"] == published and assembly["moduleInitializerRan"] == published,
                    f"{path}.{phase}: staged DLL identity/metadata/initializer state differs: {name}")
        require(_same(d["events"][:len(previous_events)], previous_events), f"{path}.{phase}: actual native event history rewritten")
        previous_events = d["events"]
        for use in previous_uses:
            require(use in d["baselineUses"], f"{path}.{phase}: first-use observation removed or changed")
        previous_uses = d["baselineUses"]
        closure_uses = [use for use in d["baselineUses"] if use["name"] in closure]
        require(not closure_uses if phase != "aborted" else bool(closure_uses), f"{path}.{phase}: unexpected/missing baseline first-use")
        if phase == "aborted":
            uses = [use for use in closure_uses if use["name"] == INTERNAL]
            require(len(uses) == 1, f"{path}: early rejection lacks the Internal first-use observation")
            use = uses[0]
            # The native recorder retains only the first use of each assembly.
            # FromTypeNameParseInfo traces its image before resolving the class;
            # the actual typed lookup is bound separately below, not invented
            # as a replacement for this assembly-level first-use record.
            sequence = re.fullmatch(r"Image::FromTypeNameParseInfo FirstUseSequence=([1-9][0-9]{0,19})", use["detail"])
            require(use["kind"] == "AssemblyReflection" and use["type"] == "" and sequence is not None and
                    int(sequence[1]) < 1 << 64 and use["thread"] > 0 and use["timestamp"] > 0,
                    f"{path}: early rejection lacks the pinned assembly-lookup first-use observation")
        for kind in ("metadata-begin", "metadata-ready"):
            _exact([event["name"] for event in d["events"] if event["kind"] == kind],
                   [] if initial or staged else closure, path, "actual " + kind)
        for kind in ("initializer-begin", "initializer-complete"):
            _exact([event["name"] for event in d["events"] if event["kind"] == kind], closure if published else [], path, "actual " + kind)
        require(sum(event["kind"] == "active-published" for event in d["events"]) == int(published), f"{path}.{phase}: premature/duplicate publication")
        if phase == "allocation-failure":
            require(_precise_allocation_guard(d["detail"]),
                    f"{path}: layout failure is not the precise byte-bound component/allocation site/guard")
        elif phase == "aborted":
            require(d["detail"] == "Private metadata retained; a second transaction is forbidden.",
                    f"{path}: abort does not retain/seal the private metadata")
        else: require(d["detail"] == "", f"{path}.{phase}: unexpected native failure detail")
    require(result["stateCode"] == "Success" and result["state"] == snapshots[-1]["diagnostics"]["state"] and
            result["diagnosticsCode"] == "Success", f"{path}: final queried state/diagnostics code differs")
    prior._raw_diagnostic(result, path)


def verify_assembly_observations(result, identities, closure, player, path):
    prior._observations(result["assemblyObservations"], identities, closure, True, path)
    _exact([row["name"] for row in result["assemblyObservations"]], list(CANDIDATES), path, "direct assembly observations")
    prior._observations(result["actualLogicalAssemblies"], identities, closure, True, path)
    native_order = [row["name"] for row in sorted(player["nativeAssemblyIdentities"], key=lambda row: row["assemblyIndex"])]
    _exact([row["name"] for row in result["actualLogicalAssemblies"]], native_order, path,
           "raw logical assembly inventory/order; no duplicates or physical shadow append")


def _empty(result, fields, path):
    for key in fields.split():
        expected = [] if key in RESULT_ARRAYS.split() else ""
        require(result[key] == expected, f"{path}: unexpected observation/activity: {key}")


def verify_early_type_observations(result, path):
    """Typed proof is independent of the per-assembly first-use classification.

    verify_case also verifies each row's raw native JSON, active baseline type
    key, repeated handle, and byte-bound linked type inventory before this gate.
    """
    _empty(result,"assemblyObservations actualLogicalAssemblies typeObservations typeEnumerations memberObservations identityObservations assignabilityObservations sceneObservations allocationException",path)
    _exact([(row["operation"],row["requested"]) for row in result["typeResolutionObservations"]],
           [("early-baseline-type",RESOURCE_COMPONENT)],path,"early baseline type exposure")
    expected_load=[dict(requested=RESOURCE_COMPONENT + ", " + INTERNAL,overload="early-baseline",typeName=RESOURCE_COMPONENT,
                        assemblyName=INTERNAL,sameAssembly=False,sameType=True)]
    require(_same(result["loadObservations"],expected_load),f"{path}: early actual Type.GetType witness differs")


def inactive_benchmark(value, path):
    if value is None: return
    _fields(value, BENCHMARK_FIELDS, path)
    for key in ("enabled", "finalSameType"):
        require(not _bool(value[key], path), f"{path}: inactive benchmark claims identity")
    for key in ("warmupCount", "lookupCount", "elapsedTicks", "stopwatchFrequency", "checksum"):
        require(type(value[key]) is int and value[key] == 0, f"{path}: inactive benchmark claims work")
    for key in ("requestedName", "finalTypeName", "finalAssemblyName"):
        require(value[key] in (None, ""), f"{path}: inactive benchmark claims a type")


def _proof_types(player, path):
    proof_path = _bound_file(player["typeProofPath"], player["typeProofSha256"], path, "typeProofPath")
    proof = _obj(proof_path, PROOF_FIELDS)
    return {row["assemblyName"]: row["types"] for row in proof["assemblies"]}


PAYLOAD_PREFIXES = dict(zip(CANDIDATES, (
    "AssemblyA.Contracts.M05Contract", "AssemblyA.Implementation.Extensibility.M05Extensibility",
    "AssemblyA.Implementation.Internal.M05Internal", "AssemblyShadowDemo.Consumers.M05ContractsConsumer",
    "AssemblyShadowDemo.Consumers.M05ExtensibilityConsumer")))


def _generic_name(definition, arguments, identities):
    return definition + "[[" + "],[".join(name + ", " + identities[assembly]["fullName"] for name, assembly in arguments) + "]]"


def verify_mode_observations(result, manifest, player, fixture, linked_types, active_types, identities, actual_types, path):
    mode, closure = result["mode"], fixture["closureLoadOrder"]
    number = mode[4:6]
    if number == "08":
        _empty(result,"typeObservations typeEnumerations memberObservations assignabilityObservations loadObservations",path)
        return verify_resources(result,manifest,player,path)
    _empty(result,"sceneObservations",path)
    if number == "02":
        _empty(result,"typeObservations typeResolutionObservations memberObservations identityObservations assignabilityObservations loadObservations",path)
        verify_enumerations(result["typeEnumerations"],fixture,linked_types,path)
        return []
    _empty(result,"typeEnumerations",path)
    if number == "12":
        _empty(result,"typeObservations memberObservations identityObservations assignabilityObservations loadObservations",path)
        _exact([(row["operation"],row["requested"]) for row in result["typeResolutionObservations"]],
               [("benchmark-prewarm",prior.TYPE_NAMES[INTERNAL])],path,"actual benchmark prewarm type")
        verify_benchmark(result["benchmark"],True,path)
        return []
    if number in ("01", "05"):
        _empty(result,"memberObservations assignabilityObservations loadObservations",path)
        expected=[]
        for name in closure:
            prefix=PAYLOAD_PREFIXES[name]
            expected += [("name-form",prefix+"Payload"),("name-form",prefix+"Outer+Inner"),
                         ("name-form",_generic_name(prefix+"Generic`1",[("System.Int32","mscorlib")],identities))]
        checks=[]; array_identities=[]
        if number == "05":
            prefix=PAYLOAD_PREFIXES[INTERNAL]; payload=prefix+"Payload"
            composites = (
                _generic_name("System.Collections.Generic.List`1",[(payload,INTERNAL)],identities),
                _generic_name("System.Collections.Generic.Dictionary`2",[("System.String","mscorlib"),(payload,INTERNAL)],identities),
                _generic_name(prefix+"Generic`1",[("System.Int32","mscorlib")],identities),
                _generic_name(prefix+"Generic`1",[(payload,INTERNAL)],identities),
                _generic_name(prefix+"GenericOuter`1+Inner`1",[("System.Int32","mscorlib"),(payload,INTERNAL)],identities),
                payload+"[]",payload+"[,]",payload+"&",payload+"*")
            arguments=[(payload,),("System.String",payload),("System.Int32",),(payload,),("System.Int32",payload)]
            for index,name in enumerate(composites):
                expected += [("composite",name),("composite-handle",name)]
                expected += [("composite-argument",argument) for argument in arguments[index]] if index<5 else [("composite-element",payload)]
                checks.append(("composite-handle-"+str(index),"True",1))
            for rank,name in enumerate(composites[5:7],1):
                expected.append(("composite-array-runtime-type",name))
                array_identities.append(dict(operation="composite-array-runtime-type",left=name,right=name,sameObject=True))
                checks.append(("composite-array-rank-"+str(rank),"True",1))
        _exact([(row["operation"],row["requested"]) for row in result["typeResolutionObservations"]],expected,path,"literal/composite type coverage and order")
        require(len(result["typeObservations"]) == len(actual_types),f"{path}: missing observed type shapes")
        for row,actual in zip(result["typeObservations"],actual_types):
            verify_type_observation(row,actual,path)
            require(row["isAssignable"] is False and row["castSucceeded"] is False,f"{path}: non-cast type row fabricated cast evidence")
        require(_same(result["identityObservations"],array_identities),f"{path}: actual allocated array identity differs")
        return checks
    if number in ("03","10"):
        _empty(result,"typeObservations assignabilityObservations loadObservations",path)
        expected_types,expected_members,expected_identities,checks=[],[],[],[]
        for name in closure:
            payload=PAYLOAD_PREFIXES[name]+"Payload"; full=identities[name]["fullName"]
            event_type=_generic_name("System.Action`1",[(payload,name)],identities)
            expected_identities += [dict(operation=operation,left=value,right=value,sameObject=True) for operation,value in (
                ("Assembly.Load",full),("ManifestModule",full),("Type/Module.GetType",prior.TYPE_NAMES[name]),("PatchType/Assembly",full),
                ("PatchType witness repeat",payload),("ManifestModule.Assembly",full))]
            checks.append(("module-identity-"+name,"True",1))
            expected_types.append(("GetTypeResolutionInfo",prior.TYPE_NAMES[name]))
            for kind,member in (("method","Echo"),("field","Field"),("property","Property"),("event","Changed")):
                expected_types += [("member-"+kind+"-declaring",payload),("member-"+kind+"-reflected",payload)]
                checks.append(("member-"+kind+"-identity-"+name,"True",1))
                return_type=payload if kind in ("method","property") else ""
                field_type=payload if kind=="field" else event_type if kind=="event" else ""
                expected_types.append(("member-"+kind+("-return" if return_type else "-type"),return_type or field_type))
                if kind=="method":
                    expected_types.append(("member-method-parameter-0",payload))
                    checks.append(("member-method-parameter-identity-"+name+"-0","True",1))
                expected_members.append(dict(declaringType=payload,reflectedType=payload,memberName=member,memberKind=kind,
                    returnType=return_type,fieldType=field_type,parameterTypes=[payload] if kind=="method" else [],sameMember=True,activeOwner=True))
        _exact([(row["operation"],row["requested"]) for row in result["typeResolutionObservations"]],expected_types,path,"actual member owner/signature type coverage")
        require(_same(result["identityObservations"],expected_identities),f"{path}: Assembly/Module/Type cache identity coverage differs")
        require(_same(result["memberObservations"],expected_members),f"{path}: complete ordered method/field/property/event coverage differs")
        verify_members(result["memberObservations"],identities,active_types,closure,path)
        return checks
    if number in ("06","07"):
        _empty(result,"typeObservations memberObservations identityObservations loadObservations",path)
        source=PAYLOAD_PREFIXES[INTERNAL]+"InterfacePayload"; contract="AssemblyA.Contracts.IVersionTextProvider"
        expected_types=[("interface-source",source),("Contracts interface",contract)]
        expected=[dict(operation="Contracts interface",sourceType=source,targetType=contract,castMarker="M05-INTERNAL",isAssignable=True,isInstance=True,castSucceeded=True)]
        checks=[]
        relations=[(INTERNAL,source,"interfaces",CANDIDATES[0],contract)]
        if number=="07":
            derived=PAYLOAD_PREFIXES[CANDIDATES[4]]+"Payload"; base=PAYLOAD_PREFIXES[CANDIDATES[1]]+"Payload"
            expected_types += [("contracts-consumer-owner",prior.TYPE_NAMES[CANDIDATES[3]]),("extensibility-consumer-source",derived),
                               ("extensibility-consumer-base",base),("extensibility-consumer-contract",contract),("extensibility-consumer-owner",prior.TYPE_NAMES[CANDIDATES[4]])]
            expected.append(dict(operation="Extensibility consumer inheritance",sourceType=derived,targetType=base,
                castMarker="M05-EXT-CONSUMER|M05-SHADOW-CONTRACTS",isAssignable=True,isInstance=True,castSucceeded=True))
            checks.append(("contracts-consumer-interface-dispatch","True",1))
            relations += [(CANDIDATES[4],derived,"base",CANDIDATES[1],base),(CANDIDATES[4],derived,"interfaces",CANDIDATES[0],contract)]
        _exact([(row["operation"],row["requested"]) for row in result["typeResolutionObservations"]],expected_types,path,"interface/consumer active type coverage")
        require(_same(result["assignabilityObservations"],expected),f"{path}: actual cast/assignability/consumer dispatch differs")
        for owner,source,kind,target_assembly,target in relations:
            dll=_bound_file(identities[owner]["path"],identities[owner]["sha256"],path,"assignability owner")
            actual=MethodProof(dll.read_bytes(),dll).type_relations(source)[kind]
            expected_relation=(target,identities[target_assembly]["fullName"])
            require(expected_relation==actual if kind=="base" else expected_relation in actual,f"{path}: claimed assignability relation absent from actual DLL metadata")
        return checks
    raise VerificationError(f"{path}: unknown M05 successful observation mode")


def verify_case(path, manifest, baseline, fixtures, player, player_path):
    """One result over previously fully verified inputs (see verify_suite)."""
    path = _canonical(str(path), path, "result")
    result = verify_result_header(path, manifest, player, player_path)
    mode = result["mode"]
    identities = {row["name"]: row for row in player["nativeAssemblyIdentities"]}
    identities.update({row["name"]: row for row in player["assemblyIdentities"]})
    linked_types = _proof_types(player, path)
    if mode not in {"T05-12-BenchmarkOn", "T05-13-BenchmarkOff"}: inactive_benchmark(result["benchmark"], path)
    if mode != "T05-11-FeatureOff": prior._inactive(result["ordinary"], prior.ORDINARY_FIELDS, path)
    if mode in OFF_MODES:
        _empty(result, "patchId patchManifestPath patchManifestSha256 compileSnapshotHash allocationException stageOrder stageResults assemblyObservations actualLogicalAssemblies typeObservations typeResolutionObservations typeEnumerations memberObservations identityObservations assignabilityObservations loadObservations sceneObservations", path)
        require(result["businessMarker"] == "M05-TYPE-PROBE", f"{path}: OFF marker differs")
        if mode == "T05-13-BenchmarkOff":
            _empty(result, "checks snapshots configure begin stage validate commit abort stateCode state diagnosticsCode executionModeCode executionMode nativeDiagnosticsJson rawDiagnosticsPath rawDiagnosticsSha256", path)
            verify_benchmark(result["benchmark"], False, path)
        else:
            # Existing nine APIs plus the new type-resolution API are all mandatory.
            operations = "configure begin stage validate commit abort state diagnostics execution-mode type-resolution".split()
            checks=[(name,"FeatureDisabled",1) for name in operations]
            checks += [("type-resolution-valid-null-json","True",1),("type-resolution-null-input","FeatureDisabled",1),
                       ("type-resolution-invalid-null-json","True",1)]
            verify_checks(result["checks"], checks, path)
            require(all(result[key] == "FeatureDisabled" for key in "configure begin stage validate commit abort stateCode diagnosticsCode executionModeCode".split()) and
                    result["state"] == "Disabled" and result["executionMode"] == "AotBaseline", f"{path}: native-OFF outputs/ABI codes differ")
            require(len(result["snapshots"]) == 1, f"{path}: OFF diagnostics phase count differs")
            _fields(result["snapshots"][0], "phase diagnostics", path)
            require(result["snapshots"][0]["phase"] == "disabled", f"{path}: OFF diagnostics phase differs")
            diagnostic = prior._raw_diagnostic(result, path)
            require(diagnostic["enabled"] is False and diagnostic["state"] == "Disabled" and diagnostic["lastError"] == 1,
                    f"{path}: OFF native diagnostics differ")
            for key in "generation expected staged retainedBytes enumerationGeneration classEnumerationGeneration".split():
                require(diagnostic[key] == 0, f"{path}: OFF state changed")
            for key in "ordinaryAssemblies ordinaryClasses closureLoadOrder stableAotNames commitOrder assemblies events baselineUses".split():
                require(diagnostic[key] == [], f"{path}: OFF diagnostics claim registry state")
            require(diagnostic["detail"] == diagnostic["baselineBuildId"] == diagnostic["patchId"] == "", f"{path}: OFF transaction identity differs")
            prior._verify_ordinary(result["ordinary"], player, path)
    else:
        early, layout = mode == "T05-04-EarlyType", mode == "T05-09-LayoutMismatch"
        if layout:
            bad = manifest["rejectedFixtures"][0]
            closure, staged = [INTERNAL], {INTERNAL: bad["assemblyIdentity"]}
            bindings = dict(patchId="LayoutMismatch", patchManifestPath="", patchManifestSha256="", compileSnapshotHash=bad["compileSnapshotHash"])
            expected_stages = []
            stage_checks = [("stage-layout-mismatch", "Success", 0)]
        else:
            pid = "P01" if mode.endswith("P01") else "P03"
            fixture, _, patch_path, _, _ = fixtures[pid]
            patch = _obj(patch_path)
            closure, staged = fixture["closureLoadOrder"], {row["name"]: row for row in fixture["assemblyIdentities"]}
            bindings = dict(patchId=pid, patchManifestPath=str(patch_path), patchManifestSha256=digest(patch_path), compileSnapshotHash=fixture["compileSnapshotHash"])
            by_name = {row["name"]: row for row in patch["closure"]}
            expected_stages = [dict(name=name,code="Success",dllSha256=by_name[name]["sha256"],pdbSha256=by_name[name]["pdbSha256"]) for name in closure]
            stage_checks = [("stage-" + name,"Success",0) for name in closure]
        for key, value in bindings.items(): require(result[key] == value, f"{path}: actual staged fixture binding differs: {key}")
        _exact(result["stageOrder"], closure, path, "stage order")
        for row in result["stageResults"]:
            _fields(row,"name code dllSha256 pdbSha256",path); _strings(row,path,"name code dllSha256 pdbSha256")
        require(_same(result["stageResults"], expected_stages), f"{path}: staged bytes/order/return code differ")
        checks = [("type-resolution-state-before","Success",0),("type-resolution-null-input","InvalidArgument",3),
                  ("type-resolution-invalid-null-json","True",1),("type-resolution-state-after","Success",0),
                  ("type-resolution-state-unchanged","True",1),
                  ("configure","Success",0),("begin","Success",0)] + stage_checks + [("validate","Success",0)]
        if early:
            checks += [("first-use-kind","baseline-Type.GetType",0),("commit","BaselineAlreadyUsed",15),("abort","Success",0)]
        else: checks += [("commit","Success",0)]
        require(result["configure"] == result["begin"] == result["validate"] == "Success" and
                result["stage"] == ("Success" if layout else "") and result["commit"] == ("BaselineAlreadyUsed" if early else "Success") and
                result["abort"] == ("Success" if early else "") and result["executionModeCode"] == result["executionMode"] == "",
                f"{path}: transaction API outcome differs")
        verify_phases(result,manifest,player,closure,staged,path)
        active_closure = [] if early else closure
        active_types = dict(linked_types)
        if not early:
            identities.update(staged)
            active_types.update({row["assemblyName"]:row["types"] for row in ([bad["typeInventory"]] if layout else fixture["typeInventories"])})
        field_annotations = resource_field_annotations(identities,path) if mode.startswith("T05-08-") else {}
        actual_types, previous_counters = [], None
        for row in result["typeResolutionObservations"]:
            actual_types.append(verify_type_resolution(row,active_types,identities,active_closure,path,
                                                       field_annotations.get(row["operation"],())))
            counters = [row["info"][key] for key in TYPE_INFO_COUNTERS]
            require(previous_counters is None or all(a <= b for a,b in zip(previous_counters,counters)), f"{path}: native type counters regressed")
            previous_counters = counters
        if early:
            verify_early_type_observations(result,path)
        elif layout:
            _empty(result,"assemblyObservations actualLogicalAssemblies typeObservations typeResolutionObservations typeEnumerations memberObservations identityObservations assignabilityObservations loadObservations sceneObservations",path)
            require(result["allocationException"],f"{path}: missing actual thrown allocation exception")
            checks += [("allocation-no-object","True",1),("allocation-guard","16",16)]
        else:
            _empty(result,"allocationException",path)
            verify_assembly_observations(result,identities,closure,player,path)
            checks += [("appdomain-identity-"+row["name"],"True",1) for row in sorted(player["nativeAssemblyIdentities"],key=lambda row:row["assemblyIndex"]) if row["name"] in CANDIDATES]
            checks += verify_mode_observations(result,manifest,player,fixture,linked_types,active_types,identities,actual_types,path)
        if not mode.startswith("T05-08-"):
            require(result["businessMarker"] == "M05-TYPE-PROBE",f"{path}: unexpected business marker")
        verify_checks(result["checks"],checks,path)
    return dict(mode=mode,processId=result["processId"],passed=True,resultSha256=digest(path))


def verify_results(result_dir, manifest, baseline, fixtures, on, off, on_path, off_path, allow_incomplete=False):
    """Result gate over already verified inputs; never a standalone input gate."""
    root = _canonical(str(result_dir), result_dir, "resultDir", True)
    paths = [path for path in root.glob("m05-*.json") if not path.name.endswith("-native-diagnostics.json")]
    expected_files = {"m05-" + mode + ".json" for mode in REQUIRED_MODES}
    actual_files = {path.name for path in paths}
    require(actual_files <= expected_files, f"{root}: unknown process result files")
    missing = sorted(expected_files - actual_files)
    require(not missing or allow_incomplete, f"{root}: incomplete M05 process coverage: {missing}")
    require(paths, f"{root}: no actual M05 process results")
    results = []
    for path in sorted(paths):
        mode = path.stem[4:]
        results.append(verify_case(path, manifest, baseline, fixtures,
                                   off if mode in OFF_MODES else on, off_path if mode in OFF_MODES else on_path))
    require(len({row["processId"] for row in results}) == len(results), f"{root}: each mode requires a fresh unique process ID")
    raw_files = {path.name for path in root.glob("m05-*-native-diagnostics.json")}
    expected_raw = {"m05-" + row["mode"] + "-native-diagnostics.json" for row in results if row["mode"] != "T05-13-BenchmarkOff"}
    require(raw_files == expected_raw, f"{root}: missing/extra raw native diagnostic files")
    return dict(milestone="M05", resultPassed=not missing, diagnosticOnly=bool(missing), missingModes=[name[4:-5] for name in missing],
                baselineBuildId=manifest["baselineBuildId"], runtimeAbiHash=manifest["runtimeAbiHash"], modes=results,
                moduleMvidObservationPolicy=MVID_POLICY,
                evidence="Byte-bound PE type/assembly identities, selected managed wrapper IL and exact compiled/linked raw-type query fingerprints and literal chains; actual captured facade forwarding and native format-31 assembly identities; compiler/linker/resource and Editor replay; exact real-process observations. Unsigned evidence is not authentication. Editor owns complete semantic/resource policy and installed compiler-catalog membership; no native type-table or runtime MVID claim.")


def verify_suite(fixture_manifest_path, result_dir, on_build_path, off_build_path, m01_baseline_root, allow_incomplete=False):
    manifest_path = _canonical(str(fixture_manifest_path), fixture_manifest_path, "fixtureManifest")
    manifest, baseline, fixtures = verify_inputs(manifest_path, m01_baseline_root)
    on_path = _canonical(str(on_build_path), on_build_path, "NativeOn receipt")
    off_path = _canonical(str(off_build_path), off_build_path, "NativeOff receipt")
    on, _, _ = verify_player(on_path, manifest, baseline, "NativeOn")
    off, _, _ = verify_player(off_path, manifest, baseline, "NativeOff")
    require(on["inputSnapshot"] == manifest["baselineInputSnapshot"], "M05 NativeOn receipt does not bind actual baseline Player")
    for key in ("inputSnapshot", "inputSnapshotHash", "nativeLibrarySha256", "buildGuid", "playerOutput", "typeProofPath", "typeProofSha256"):
        require(on[key] != off[key], f"M05 native ON/OFF {key} must be distinct")
    verify_replay(manifest_path.with_name("m05-editor-replay.json"), manifest, baseline, fixtures, on, on_path)
    return verify_results(result_dir, manifest, baseline, fixtures, on, off, on_path, off_path, allow_incomplete)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture-manifest", "result-dir", "on-build", "off-build", "m01-baseline-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true", help="Partial diagnostics only; missing modes can never yield full PASS")
    args = parser.parse_args(argv)
    try:
        result = verify_suite(args.fixture_manifest.absolute(), args.result_dir.absolute(), args.on_build.absolute(),
                              args.off_build.absolute(), args.m01_baseline_root.absolute(), args.allow_incomplete)
        output = args.output.absolute()
        require(not output.exists() and not output.is_symlink() and str(output) == str(output.resolve()),
                f"Refusing existing/symlinked/aliased output: {output}")
        _canonical(str(output.parent), output, "output parent", True)
        text = json.dumps(result, indent=2) + "\n"
        # Explicit output only: no build, scratch, directory creation or rewrite.
        with output.open("x", encoding="utf-8") as stream: stream.write(text)
        print(text, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError, StopIteration, IndexError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
