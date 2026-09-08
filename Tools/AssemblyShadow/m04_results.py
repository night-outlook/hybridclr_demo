"""Strict offline M04 evidence verification. Unsigned evidence is not authentication.

Reopens byte-backed compiler/linker/resource/patch inputs and PE identities.
Unity semantic ABI, compiler-catalog membership and IL guard/schema replay are
the separately hash-bound Editor replay's responsibility, not inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from shadow_tools import VerificationError, require, read_json, unique_object
from m04_metadata import (read_identity, read_native_metadata, find_native_metadata,
                          NATIVE_METADATA_VERSION, NATIVE_ASSEMBLY_FIELDS)
from m03_results import (CANDIDATES, INTERNAL, PROVIDER_ORDER, ERROR_CODES, STATE_CODES,
                         digest, _absolute, _rel, _s, _hash, _guid, _integer, _same,
                         _names, _exact, _name_set, _name_order, _resource_abi_hash,
                         _verify_snapshot, _verify_patch as _generic_patch,
                         _verify_diag_invariants)
from m02_results import (_runtime_abi_hash, _verify_source_pins, _snapshot_hash,
                         _snapshot_files, _linked_claim_absent, _reflection_snapshot,
                         _reflection_manifest, _verify_player_snapshot, _verify_linked_player,
                         _verify_resource_baseline, _verify_bundles, _edges, _closure,
                         _verify_topological, _reflection_parse)

STABLE_AOT_HASH_DOMAIN = "m04-stable-aot:1\n"
EDITOR_REPLAY_POLICY = "compiler-linked-policy-graph-resource-abi-assembly-identity:1"
MVID_POLICY = "unavailable-pinned-il2cpp-use-byte-bound-build-and-native-diagnostics"
REQUIRED_MODES = frozenset([f"T04-{i:02d}" for i in range(1, 9)] +
                           ["T04-09-BenchmarkOn", "T04-10-BenchmarkOff"])
OFF_MODES = {"T04-08", "T04-10-BenchmarkOff"}
SUCCESS_MODES = {"T04-01", "T04-02", "T04-06", "T04-07", "T04-09-BenchmarkOn"}
FIXTURE_FIELDS = "patchId defines changedRoots compileSnapshot compileSnapshotHash patchDirectory patchManifest patchManifestSha256 closureLoadOrder stableAotNames assemblyIdentities"
MANIFEST_FIELDS = "schemaVersion milestone unityVersion target architecture baselineManifestPath baselineManifestSha256 baselineBuildId runtimeAbiHash baselineInputSnapshot baselineInputSnapshotHash candidateNames closureLoadOrder stableAotNames stableAotProvenanceHash stableAotProvenance fixtures"
PLAYER_FIELDS = "schemaVersion milestone variant baselineBuildId runtimeAbiHash unityVersion target architecture buildGuid playerOutput inputSnapshot inputSnapshotHash nativeLibraryPath nativeLibrarySha256 nativeArguments assemblyIdentities placeholderManifestPath placeholderManifestSha256 placeholderAssemblyNames nativeMetadataPath nativeMetadataSha256 nativeMetadataVersion nativeAssemblyIdentities nativeGeneratedAssemblyNames"
IDENTITY_FIELDS = "name fullName version culture publicKeyToken mvid path sha256 referenceIdentities"
REF_FIELDS = "referenceIndex name fullName version culture publicKeyToken"
REPLAY_FIELDS = "schemaVersion milestone result comparisonPolicy fixtureManifestPath fixtureManifestSha256 baselineManifestPath baselineManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 baselineInputSnapshotHash baselineBuildId playerBuildGuid nativeLibrarySha256 linkedPlayerReceiptHash runtimeAbiHash unityVersion target architecture stableAotProvenanceHash validatorSourcePins fixtures"


def _fields(value, fields, path):
    require(type(value) is dict, f"{path}: expected object")
    expected = set(fields.split()) if isinstance(fields, str) else set(fields)
    require(set(value) == expected,
            f"{path}: missing/unknown members: missing={sorted(expected - set(value))}, unknown={sorted(set(value) - expected)}")
    return value


def _obj(path, fields=None):
    value = read_json(path)
    require(type(value) is dict, f"{path}: expected JSON object")
    if fields is not None: _fields(value, fields, path)
    return value


def _array(value, path):
    require(type(value) is list, f"{path}: expected array")
    return value


def _strings(value, path, fields):
    for field in fields.split():
        require(type(value[field]) is str, f"{path}.{field}: expected string (including empty evidence)")


def _bool(value, path):
    require(type(value) is bool, f"{path}: expected Boolean")
    return value


def _pins(value, path, expected=None):
    _fields(value, "schemaVersion unityVersion target architecture hybridclr hybridclrUnity il2cppPlus demo", path)
    for repo in ("hybridclr", "hybridclrUnity", "il2cppPlus", "demo"):
        _fields(value[repo], "url revision localPath", f"{path}.{repo}")
        _s(value[repo]["localPath"], path, repo + ".localPath")
    require(type(value["schemaVersion"]) is int, f"{path}: invalid source pin schema type")
    _verify_source_pins(value, path, expected)


def verify_identities(claims, files, path):
    """The inventory is exact; AssemblyRef rows remain ordered, never a set."""
    claims = _array(claims, path)
    actual = sorted((read_identity(file) for file in files), key=lambda row: row["name"])
    require(len(claims) == len(actual), f"{path}: assembly identity inventory differs")
    _names([row["name"] for row in actual], path, "actual identities")
    for index, (claimed, parsed) in enumerate(zip(claims, actual)):
        p = f"{path}[{index}]"
        _fields(claimed, IDENTITY_FIELDS, p)
        _strings(claimed, p, "name fullName version culture publicKeyToken mvid path sha256")
        refs = _array(claimed["referenceIdentities"], p + ".referenceIdentities")
        for ri, row in enumerate(refs):
            _fields(row, REF_FIELDS, p + f".referenceIdentities[{ri}]")
            require(type(row["referenceIndex"]) is int and row["referenceIndex"] == ri,
                    f"{p}: AssemblyRef index/order differs")
            _strings(row, p, "name fullName version culture publicKeyToken")
        require(_same(claimed, parsed), f"{p}: assembly/AssemblyRef identity differs from actual DLL bytes")
    return {row["name"]: row for row in actual}


def parse_placeholders(data, path="placeholder manifest"):
    try: text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error: raise VerificationError(f"{path}: invalid UTF-8") from error
    begin, end = "//!!!{{PLACE_HOLDER", "//!!!}}PLACE_HOLDER"
    require(text.count(begin) == text.count(end) == 1 and text.index(begin) < text.index(end),
            f"{path}: expected exactly one ordered placeholder region")
    names = []
    for line in text.split(begin)[1].split(end)[0].splitlines():
        if not line.strip(): continue
        match = re.fullmatch(r'\s*"([^"\\\r\n]+)"\s*,\s*', line)
        require(match is not None, f"{path}: invalid placeholder declaration")
        name = match[1]
        require(name == name.strip() and name and "/" not in name and "\\" not in name,
                f"{path}: invalid placeholder simple name")
        names.append(name)
    require(names, f"{path}: empty placeholder inventory")
    return _names(names, path, "placeholder names")


def _verify_native_metadata(player, path):
    """Native-generated identities are derived from actual Player metadata.

    This is a separate physical identity domain, not a waiver for unknown names
    and not a synthetic DLL/MVID. Linked names must retain exact PE identity.
    """
    output = _absolute(player["playerOutput"], path, "playerOutput", directory=True)
    metadata = _absolute(player["nativeMetadataPath"], path, "nativeMetadataPath")
    require(player["playerOutput"] == str(output.resolve()) and player["nativeMetadataPath"] == str(metadata.resolve()),
            f"{path}: aliased Player/native metadata path")
    require(metadata == find_native_metadata(output),
            f"{path}: native metadata is not the executed Player's unique metadata file")
    expected_hash = _hash(player["nativeMetadataSha256"], path, "nativeMetadataSha256")
    require(type(player["nativeMetadataVersion"]) is int and player["nativeMetadataVersion"] == NATIVE_METADATA_VERSION,
            f"{path}: unsupported native metadata format/version")
    actual = read_native_metadata(metadata)
    require(actual["nativeMetadataSha256"] == expected_hash, f"{path}: native metadata SHA differs from actual Player bytes")
    rows = _array(player["nativeAssemblyIdentities"], path)
    for index, row in enumerate(rows):
        rp = f"{path}.nativeAssemblyIdentities[{index}]"
        _fields(row, NATIVE_ASSEMBLY_FIELDS, rp)
        for field in ("assemblyIndex", "imageIndex"):
            require(type(row[field]) is int and 0 <= row[field] < 1 << 31, f"{rp}: invalid {field}")
        require(type(row["token"]) is int and 0 <= row["token"] < 1 << 32, f"{rp}: token must be UInt32")
        _strings(row, rp, "imageName name fullName version culture publicKeyToken")
    require(_same(rows, actual["nativeAssemblyIdentities"]), f"{path}: native Assembly/Image identities differ from actual Player metadata")
    native = {row["name"]: row for row in rows}
    linked_rows = _array(player["assemblyIdentities"], path)
    linked_names = _names([row["name"] for row in linked_rows], path, "linked identity names")
    for row in linked_rows:
        require(row["name"] in native and all(row[key] == native[row["name"]][key]
                for key in ("name", "fullName", "version", "culture", "publicKeyToken")),
                f"{path}: linked DLL identity disagrees with native metadata: {row['name']}")
    generated = sorted(set(native) - set(linked_names))
    _exact(player["nativeGeneratedAssemblyNames"], generated, path, "native-generated assembly inventory")
    return native


def _verify_player_build_receipt(path, manifest, baseline, variant):
    path = _absolute(str(path), path, "playerBuildReceipt")
    r = _obj(path, PLAYER_FIELDS)
    require(type(r["schemaVersion"]) is int and r["schemaVersion"] == 1 and r["milestone"] == "M04" and r["variant"] == variant,
            f"{path}: Player schema/milestone/variant mismatch")
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(r[field] == manifest[field], f"{path}: Player {field} differs")
    flag = "1" if variant == "NativeOn" else "0"
    require(r["nativeArguments"] == '--compiler-flags="-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=' + flag + '"',
            f"{path}: exact native compiler switch differs")
    root = _absolute(r["inputSnapshot"], path, "inputSnapshot", directory=True)
    require(root == path.parent and path.name == "m04-player-build.json", f"{path}: noncanonical Player receipt location")
    snapshot = _verify_snapshot(root, manifest["baselineBuildId"], manifest["runtimeAbiHash"], baseline, path, variant == "NativeOn")
    for field, source in (("buildGuid", "buildGuid"), ("playerOutput", "playerOutput"),
                          ("inputSnapshotHash", "snapshotHash"), ("nativeLibraryPath", "nativeLibraryPath"),
                          ("nativeLibrarySha256", "nativeLibrarySha256")):
        require(r[field] == snapshot[source], f"{path}: {field} differs from actual Player snapshot")
    output = _absolute(r["playerOutput"], path, "playerOutput", directory=True)
    native = _absolute(r["nativeLibraryPath"], path, "nativeLibraryPath")
    require(native.is_relative_to(output), f"{path}: native library outside Player output")
    _guid(r["buildGuid"], path, "buildGuid")
    require(type(snapshot["playerBuildOptions"]) is int and snapshot["playerBuildOptions"] & 1,
            f"{path}: requires Development Player build")
    _pins(snapshot["sourcePins"], path, baseline["sourcePins"])
    _snapshot_files(snapshot, root, path)
    _verify_linked_player(root, snapshot, {a["name"]: a for a in baseline["assemblies"]}, path)
    _reflection_snapshot(root, snapshot, path, require_linked=True)
    files = [_rel(root / "LinkedPlayer", a["path"], path, "linked DLL") for a in snapshot["linkedPlayerReceipt"]["assemblies"]]
    identities = verify_identities(r["assemblyIdentities"], files, f"{path}.assemblyIdentities")
    for linked in snapshot["linkedPlayerReceipt"]["assemblies"]:
        parsed = next(value for name, value in identities.items() if name.casefold() == linked["name"].casefold())
        require(parsed["mvid"] == linked["mvid"], f"{path}: linked receipt MVID differs from DLL")
    _verify_native_metadata(r, path)
    placeholders = root / "m04-placeholder-AssemblyManifest.cpp"
    require(r["placeholderManifestPath"] == str(placeholders) and digest(placeholders) == r["placeholderManifestSha256"],
            f"{path}: placeholder snapshot binding differs")
    _exact(r["placeholderAssemblyNames"], parse_placeholders(placeholders.read_bytes(), placeholders), path, "placeholderAssemblyNames")
    return r


def _verify_patch(patch_id, item, manifest, baseline):
    # This helper's actual contract is generic byte/manifest binding (no M03
    # domain or M03 fixture admission); M04 adds its exact schema/PE proof below.
    patch = _generic_patch(patch_id, item, manifest, baseline)
    fixture, patch_root, patch_path, compile_root, compiled = item
    identities = verify_identities(fixture["assemblyIdentities"],
                                  [_rel(patch_root, a["dll"], patch_path, "dll") for a in patch["closure"]], patch_path)
    for entry in patch["closure"]:
        actual = identities[entry["name"]]
        require(entry["mvid"] == actual["mvid"], f"{patch_path}: patch MVID differs from DLL")
        _name_set(entry["references"], [r["name"] for r in actual["referenceIdentities"]], patch_path, "declared reference names")
    edges = _edges(patch["dependencyGraph"], patch_path)
    known = {a["name"] for a in baseline["assemblies"]}
    closure = _closure(edges, patch["changedRoots"], known, patch_path)
    require(closure == set(patch["loadOrder"]), f"{patch_path}: reverse closure differs")
    _verify_topological(patch["loadOrder"], closure, edges, patch_path)
    reflected = _reflection_snapshot(compile_root, compiled, patch_path)
    _reflection_manifest(patch, reflected, patch_path)
    return patch


def _verify_inputs(manifest_path, baseline_manifest_path=None, baseline_snapshot_path=None, m01_baseline_root=None):
    m = _obj(manifest_path, MANIFEST_FIELDS)
    require(type(m["schemaVersion"]) is int and m["schemaVersion"] == 1 and m["milestone"] == "M04", f"{manifest_path}: M04 manifest schema mismatch")
    require(re.fullmatch(r"M04-Baseline-[A-Za-z0-9_.-]+", m["baselineBuildId"]) is not None,
            f"{manifest_path}: expected fresh M04 baseline identity")
    require((m["unityVersion"], m["target"], m["architecture"]) == ("2022.3.62f2", "StandaloneOSX", "arm64"),
            f"{manifest_path}: unaccepted Unity/target/architecture")
    _exact(m["candidateNames"], CANDIDATES, manifest_path, "candidateNames")
    _exact(m["closureLoadOrder"], PROVIDER_ORDER, manifest_path, "closureLoadOrder")
    stable = _names(m["stableAotNames"], manifest_path, "stableAotNames")
    require(stable and stable == sorted(stable) and not {n.casefold() for n in stable} & {n.casefold() for n in CANDIDATES},
            f"{manifest_path}: invalid stable AOT domain")
    _hash(m["runtimeAbiHash"], manifest_path, "runtimeAbiHash")
    _hash(m["stableAotProvenanceHash"], manifest_path, "stableAotProvenanceHash")
    require(m["stableAotProvenanceHash"] == hashlib.sha256((STABLE_AOT_HASH_DOMAIN + m["stableAotProvenance"]).encode()).hexdigest(),
            f"{manifest_path}: stable AOT hash/domain mismatch")
    bp = _absolute(m["baselineManifestPath"], manifest_path, "baselineManifestPath")
    require(baseline_manifest_path is None or Path(baseline_manifest_path) == bp, f"{manifest_path}: baseline override cannot replace bound path")
    require(digest(bp) == m["baselineManifestSha256"], f"{bp}: baseline manifest hash differs")
    baseline = _obj(bp)
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture"):
        require(baseline[field] == m[field], f"{bp}: {field} differs")
    require(type(baseline["schemaVersion"]) is int and baseline["schemaVersion"] == baseline["semanticHashSchema"] == 1, f"{bp}: baseline schema mismatch")
    _pins(baseline["sourcePins"], bp)
    require(_runtime_abi_hash(baseline["sourcePins"], bp) == m["runtimeAbiHash"], f"{bp}: runtime ABI mismatch")
    _name_set(baseline["shadowCandidates"], CANDIDATES, bp, "shadowCandidates")
    _hash(baseline["bootstrapAbiHash"], bp, "bootstrapAbiHash")
    _resource_abi_hash(baseline["resourceAbiHash"], bp, "resourceAbiHash")
    descriptors = baseline["assemblies"]
    _names([a["name"] for a in descriptors], bp, "baseline assembly names")
    # The immutable baseline descriptor is PRELINK, never the Player's linked
    # MVID. Prove its own DLL domain rather than equating these two inventories.
    for descriptor in descriptors:
        parsed = read_identity(_rel(bp.parent, descriptor["filePath"], bp, "baseline DLL"))
        require(parsed["name"] == descriptor["name"] and parsed["mvid"] == descriptor["mvid"] and parsed["sha256"] == descriptor["sha256"],
                f"{bp}: prelink baseline identity differs from actual DLL")
    frozen, _, _, reflection = _verify_player_snapshot(bp.parent, baseline, {a["name"]: a for a in descriptors}, bp)
    _reflection_manifest(baseline, reflection, bp)
    root = _absolute(m["baselineInputSnapshot"], manifest_path, "baselineInputSnapshot", directory=True)
    require(baseline_snapshot_path is None or Path(baseline_snapshot_path) == root, f"{manifest_path}: snapshot override cannot replace bound path")
    snapshot = _verify_snapshot(root, m["baselineBuildId"], m["runtimeAbiHash"], baseline, bp)
    require(m["baselineInputSnapshotHash"] == frozen["snapshotHash"] == snapshot["snapshotHash"] and
            frozen["linkedPlayerReceiptHash"] == snapshot["linkedPlayerReceiptHash"] and snapshot["buildGuid"] == baseline["playerBuildGuid"],
            f"{manifest_path}: original/frozen Player binding differs")
    require(m01_baseline_root is not None, "M04 requires --m01-baseline-root for independent frozen resource proof")
    m01 = _absolute(str(m01_baseline_root), manifest_path, "m01BaselineRoot", directory=True)
    _verify_bundles(m01, baseline, bp)
    resource = _verify_resource_baseline(bp.parent, baseline, bp, m01)
    require(resource["provenance"] == "M01AuditedFrozenSourceReconstruction" and resource["compilerSnapshotHash"] == snapshot["snapshotHash"],
            f"{bp}: resource proof is not the frozen M01 import bound to this Player")
    lines = m["stableAotProvenance"].split("\n")
    require([line.partition("=")[0] for line in lines] == ["framework", "compiler-libraries", "linked-player", "bootstrap-policy", "physical"],
            f"{manifest_path}: stable provenance fields/order differ")
    for line in lines[:2]: _hash(line.partition("=")[2], manifest_path, "compiler proof hash")
    require(lines[2] == "linked-player=" + snapshot["linkedPlayerReceiptHash"] and
            lines[3] == "bootstrap-policy=" + ",".join(sorted(n.casefold() for n in baseline["bootstrapAssemblies"])) and
            lines[4] == "physical=" + ",".join(stable), f"{manifest_path}: stable authorization provenance differs")
    require(set(stable) <= {a["name"] for a in snapshot["linkedPlayerReceipt"]["assemblies"]}, f"{manifest_path}: stable allowlist includes unlinked assembly")
    fixtures = {}
    for f in _array(m["fixtures"], manifest_path):
        _fields(f, FIXTURE_FIELDS, manifest_path)
        pid = f["patchId"]
        require(pid in ("P01", "P03") and pid not in fixtures, f"{manifest_path}: duplicate/unknown fixture")
        expected = [INTERNAL] if pid == "P01" else PROVIDER_ORDER
        defines = ["ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M04"]
        if pid == "P03": defines += ["ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M04_P03"]
        _name_set(f["defines"], defines, manifest_path, "exact M04 defines")
        _name_set(f["changedRoots"], expected, manifest_path, "changedRoots")
        _exact(f["closureLoadOrder"], expected, manifest_path, "fixture load order")
        _exact(f["stableAotNames"], stable, manifest_path, "fixture stable AOT")
        pr = _absolute(f["patchDirectory"], manifest_path, "patchDirectory", directory=True)
        pp = _absolute(f["patchManifest"], manifest_path, "patchManifest")
        require(pp == pr / "patch-manifest.json" and digest(pp) == f["patchManifestSha256"], f"{pp}: patch path/hash differs")
        cr = _absolute(f["compileSnapshot"], manifest_path, "compileSnapshot", directory=True)
        cp = cr / "assembly-snapshot.json"
        compiled = _obj(cp)
        require(compiled["kind"] == "CompilePlayerScripts" and compiled["schemaVersion"] == 1 and _linked_claim_absent(compiled) and not (cr / "LinkedPlayer").exists(), f"{cp}: compiler snapshot claims Player evidence")
        _pins(compiled["sourcePins"], cp, baseline["sourcePins"])
        for field in ("unityVersion", "target", "architecture"):
            require(compiled[field] == m[field], f"{cp}: compiler target identity differs")
        _snapshot_files(compiled, cr, cp)
        require(compiled["snapshotHash"] == f["compileSnapshotHash"] == _snapshot_hash(compiled, cr, cp), f"{cp}: stale compiler snapshot hash")
        user_defines = [d for d in _names(compiled["extraScriptingDefines"], cp, "extraScriptingDefines") if not d.startswith("ASSEMBLY_SHADOW_REFLECTION_BINDINGS_")]
        _name_set(user_defines, defines, cp, "compiler defines")
        fixtures[pid] = (f, pr, pp, cr, compiled)
    require(list(fixtures) == ["P01", "P03"], f"{manifest_path}: exact ordered P01/P03 fixture set required")
    m["_path"], m["_snapshot"] = str(manifest_path), snapshot
    return m, baseline, root, fixtures


def _verify_replay(path, manifest, baseline, fixtures, on_build):
    replay = _obj(path, REPLAY_FIELDS)
    require(type(replay["schemaVersion"]) is int and replay["schemaVersion"] == 1 and replay["milestone"] == "M04" and
            replay["result"] == "Passed" and replay["comparisonPolicy"] == EDITOR_REPLAY_POLICY, f"{path}: Editor replay policy/schema/result differs")
    bindings = {key: manifest[key] for key in "baselineManifestPath baselineManifestSha256 baselineInputSnapshotHash baselineBuildId runtimeAbiHash unityVersion target architecture stableAotProvenanceHash".split()}
    bindings.update(fixtureManifestPath=manifest["_path"], fixtureManifestSha256=digest(Path(manifest["_path"])),
                    playerBuildGuid=baseline["playerBuildGuid"], nativeLibrarySha256=baseline["nativeLibrarySha256"],
                    linkedPlayerReceiptHash=manifest["_snapshot"]["linkedPlayerReceiptHash"],
                    playerBuildReceiptPath=str(on_build), playerBuildReceiptSha256=digest(on_build))
    for key, value in bindings.items(): require(replay[key] == value, f"{path}: Editor replay {key} differs")
    _pins(replay["validatorSourcePins"], path, baseline["sourcePins"])
    rows = _array(replay["fixtures"], path)
    require(len(rows) == len(fixtures), f"{path}: replay fixture set differs")
    for row, (pid, item) in zip(rows, fixtures.items()):
        _fields(row, "patchId patchManifestSha256 compileSnapshotHash changedRoots closureLoadOrder", path)
        expected = {key: item[0][key] for key in row}
        require(_same(row, expected), f"{path}: replay fixture identity/order differs")
    return replay


DIAGNOSTIC_FIELDS = "schemaVersion enabled runtimeAbiVersion state stateCode lastError detail baselineBuildId patchId generation expected staged retainedBytes enumerationGeneration ordinaryAssemblies classEnumerationGeneration ordinaryClasses closureLoadOrder stableAotNames commitOrder assemblies events baselineUses"
R01_DIAGNOSTIC_FIELDS = DIAGNOSTIC_FIELDS + " startupCandidateSchemaVersion startupCandidateNames startupObservationMode metadataBudgetCapabilityVersion recoveryCapabilityVersion"
LEGACY_DIAGNOSTIC_ERROR_CODES = dict(ERROR_CODES, BaselineMethodExecution=21)
R01_DIAGNOSTIC_ERROR_CODES = dict(LEGACY_DIAGNOSTIC_ERROR_CODES, CapabilityUnavailable=22,
                                MetadataCapacityExceeded=23, MetadataBudgetMismatch=24)
ASSEMBLY_DIAG_FIELDS = "name mvid skeletonBuilt runtimeMetadataInitialized published moduleInitializerAttempted moduleInitializerRan"
BENCHMARK_FIELDS = "enabled finalSameAssembly requestedName warmupCount lookupCount elapsedTicks stopwatchFrequency checksum finalAssemblyName finalFullName finalMvid finalMvidAvailable finalReferenceIdentities"
ORDINARY_FIELDS = "schemaVersion moduleMvidObservationPolicy aotMvidAvailable fixedImageMvidAvailable aotFullName aotMvid aotLoadMatchesType placeholderName placeholderFoundBefore placeholderHiddenBefore placeholderSameAfterLoad assemblyCountBefore assemblyCountAfter ordinaryCountBefore ordinaryCountAfter ordinaryCountAfterDuplicate configurationPath configurationSha256 configurationHash fixedImageGuard fixedImagePath fixedImageSha256 fixedImageFullName fixedImageMvid fixedImageMarker fixedImageTamperRejected fixedImageNullRejected fixedImageCallerBytesUnchanged loadedNameSame enumeratedSame duplicateRejected duplicateExceptionType duplicateMessage knownNameResolveInput knownNameResolveFullName knownNameResolveEvents knownNameResolveSame supplementaryInputPath supplementaryInputSha256 supplementaryInputFullName supplementaryInputMvid supplementaryFirstCode supplementaryRepeatCode supplementaryInvalidModeCode supplementaryCallerBytesUnchanged"


def _uint64(value, path):
    require(type(value) is int and 0 <= value < 1 << 64, f"{path}: expected UInt64 JSON integer")
    return value


def _diagnostic(value, path):
    actual = _fields(value, R01_DIAGNOSTIC_FIELDS, path) if type(value) is dict and set(value) == set(R01_DIAGNOSTIC_FIELDS.split()) else _fields(value, DIAGNOSTIC_FIELDS, path)
    d = actual
    require(type(d["schemaVersion"]) is int and d["schemaVersion"] == 1 and
            type(d["runtimeAbiVersion"]) is int and d["runtimeAbiVersion"] == 1, f"{path}: diagnostic schema mismatch")
    _bool(d["enabled"], path)
    if set(d) == set(R01_DIAGNOSTIC_FIELDS.split()):
        require(type(d["startupCandidateSchemaVersion"]) is int and d["startupCandidateSchemaVersion"] >= 0,
                f"{path}: invalid startup candidate schema version")
        _names(d["startupCandidateNames"], path, "startupCandidateNames")
        require(type(d["startupObservationMode"]) is str and d["startupObservationMode"] in
                {"Unavailable", "ConfigureOnly", "EarlyTracking"}, f"{path}: invalid startup observation mode")
        for field in ("metadataBudgetCapabilityVersion", "recoveryCapabilityVersion"):
            require(type(d[field]) is int and d[field] >= 0, f"{path}: invalid {field}")
        if d["enabled"]:
            require(d["metadataBudgetCapabilityVersion"] == 1 and d["recoveryCapabilityVersion"] == 1,
                    f"{path}: enabled diagnostic capability version mismatch")
    _strings(d, path, "state detail baselineBuildId patchId")
    require(d["state"] in STATE_CODES and type(d["stateCode"]) is int and d["stateCode"] == STATE_CODES[d["state"]], f"{path}: state enum/code mismatch")
    errors = R01_DIAGNOSTIC_ERROR_CODES if set(d) == set(R01_DIAGNOSTIC_FIELDS.split()) else LEGACY_DIAGNOSTIC_ERROR_CODES
    require(type(d["lastError"]) is int and d["lastError"] in errors.values(), f"{path}: invalid native error code")
    for field in "generation expected staged retainedBytes enumerationGeneration classEnumerationGeneration".split(): _uint64(d[field], f"{path}.{field}")
    for field in "closureLoadOrder stableAotNames commitOrder".split(): _names(d[field], path, field)
    for a in _array(d["assemblies"], path):
        _fields(a, ASSEMBLY_DIAG_FIELDS, path)
        _strings(a, path, "name mvid")
        for field in "skeletonBuilt runtimeMetadataInitialized published moduleInitializerAttempted moduleInitializerRan".split(): _bool(a[field], f"{path}.{field}")
    for a in _array(d["ordinaryAssemblies"], path):
        _fields(a, "name isInterpreter", path)
        _s(a["name"], path, "physical assembly name")
        _bool(a["isInterpreter"], path)
    for c in _array(d["ordinaryClasses"], path):
        _fields(c, "assemblyName typeName isInterpreter isConstructedGeneric usesStagedMetadata", path)
        _strings(c, path, "assemblyName typeName")
        for field in "isInterpreter isConstructedGeneric usesStagedMetadata".split(): _bool(c[field], path)
    for e in _array(d["events"], path):
        _fields(e, "sequence kind name generation stagedCount", path)
        _strings(e, path, "kind name")
        for field in "sequence generation stagedCount".split(): _uint64(e[field], path)
    for u in _array(d["baselineUses"], path):
        _fields(u, "name kind detail type thread timestamp", path)
        _strings(u, path, "name kind detail type")
        _s(u["name"], path, "baseline use name")
        _s(u["kind"], path, "baseline use kind")
        _uint64(u["thread"], path); _uint64(u["timestamp"], path)
    _names([u["name"] for u in d["baselineUses"]], path, "baseline use names")
    return d


def _raw_diagnostic(result, path):
    raw = _absolute(result["rawDiagnosticsPath"], path, "rawDiagnosticsPath")
    require(raw == path.with_name(path.stem + "-native-diagnostics.json"), f"{path}: noncanonical raw diagnostics path")
    require(digest(raw) == _hash(result["rawDiagnosticsSha256"], path, "rawDiagnosticsSha256"), f"{path}: raw diagnostics hash differs")
    _s(result["nativeDiagnosticsJson"], path, "nativeDiagnosticsJson")
    try:
        inline = json.loads(result["nativeDiagnosticsJson"], object_pairs_hook=unique_object,
                            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except ValueError as error: raise VerificationError(f"{path}: invalid inline native JSON") from error
    disk = _obj(raw)
    require(_same(inline, disk), f"{path}: raw/inline diagnostics differ")
    _diagnostic(disk, raw)
    require(result["snapshots"] and _same(disk, result["snapshots"][-1]["diagnostics"]),
            f"{path}: raw diagnostics do not equal final freshly captured typed snapshot")
    return disk


def _verify_benchmark(value, identity, enabled, path):
    b = _fields(value, BENCHMARK_FIELDS, path)
    require(_bool(b["enabled"], path) is enabled, f"{path}: benchmark mode differs")
    require(_bool(b["finalSameAssembly"], path) and not _bool(b["finalMvidAvailable"], path) and b["finalMvid"] == "",
            f"{path}: benchmark equality/MVID unavailable policy differs")
    for field in "warmupCount lookupCount elapsedTicks stopwatchFrequency checksum".split():
        require(type(b[field]) is int and 0 <= b[field] < 1 << 63, f"{path}: benchmark {field} is not Int64")
    require(b["warmupCount"] == 1000 and b["lookupCount"] == b["checksum"] == 1_000_000 and b["elapsedTicks"] > 0 and b["stopwatchFrequency"] > 0,
            f"{path}: missing raw million-lookup benchmark measurement")
    for field, expected in (("requestedName", INTERNAL), ("finalAssemblyName", INTERNAL),
                            ("finalFullName", identity["fullName"])):
        require(b[field] == expected, f"{path}: benchmark {field} differs from actual active DLL")
    _exact(b["finalReferenceIdentities"], [r["fullName"] for r in identity["referenceIdentities"]], path, "benchmark declared references")


def _verify_ordinary(value, player, path):
    o = _fields(value, ORDINARY_FIELDS, path)
    require(type(o["schemaVersion"]) is int and o["schemaVersion"] == 1, f"{path}: ordinary schema differs")
    true_fields = "aotLoadMatchesType placeholderFoundBefore placeholderHiddenBefore placeholderSameAfterLoad fixedImageTamperRejected fixedImageNullRejected fixedImageCallerBytesUnchanged loadedNameSame enumeratedSame duplicateRejected knownNameResolveSame supplementaryCallerBytesUnchanged"
    for field in true_fields.split(): require(_bool(o[field], path) is True, f"{path}: ordinary regression failed: {field}")
    int_fields = "schemaVersion assemblyCountBefore assemblyCountAfter ordinaryCountBefore ordinaryCountAfter ordinaryCountAfterDuplicate knownNameResolveEvents supplementaryFirstCode supplementaryRepeatCode supplementaryInvalidModeCode"
    for field in int_fields.split(): _integer(o[field], path, field)
    unavailable = {"aotMvidAvailable", "fixedImageMvidAvailable"}
    for field in unavailable: require(not _bool(o[field], path), f"{path}: fabricated observed runtime MVID")
    require(o["moduleMvidObservationPolicy"] == MVID_POLICY and o["aotMvid"] == o["fixedImageMvid"] == "",
            f"{path}: unavailable runtime MVID policy differs")
    for field in set(ORDINARY_FIELDS.split()) - set(true_fields.split()) - set(int_fields.split()) - unavailable:
        require(type(o[field]) is str, f"{path}: ordinary {field} must be string")
    require(o["assemblyCountBefore"] > 0 and o["assemblyCountAfter"] == o["assemblyCountBefore"] + 1 and
            o["ordinaryCountBefore"] == 0 and o["ordinaryCountAfter"] == o["ordinaryCountAfterDuplicate"] == 1,
            f"{path}: ordinary placeholder enumeration/invalidation differs")
    ordinary_name = "AssemblyShadowBaseline.HotUpdate"
    require(o["placeholderName"] == o["knownNameResolveInput"] == ordinary_name and ordinary_name in player["placeholderAssemblyNames"],
            f"{path}: placeholder not bound to generated native manifest")
    require(o["knownNameResolveEvents"] == 0, f"{path}: known-name callback unexpectedly invoked")
    require((o["supplementaryFirstCode"], o["supplementaryRepeatCode"], o["supplementaryInvalidModeCode"]) == (0, 5, 6),
            f"{path}: supplementary metadata ABI return codes differ")
    mscorlib = next(a for a in player["assemblyIdentities"] if a["name"] == "mscorlib")
    for field, key in (("aotFullName", "fullName"), ("supplementaryInputPath", "path"),
                       ("supplementaryInputSha256", "sha256"), ("supplementaryInputFullName", "fullName"), ("supplementaryInputMvid", "mvid")):
        require(o[field] == mscorlib[key], f"{path}: ordinary {field} not from executed Player linked mscorlib")
    require(digest(Path(mscorlib["path"])) == mscorlib["sha256"], f"{path}: linked supplementary bytes changed")
    config = _absolute(o["configurationPath"], path, "ordinary configuration")
    captured = Path(player["inputSnapshot"]) / "ReflectionBindings/configuration.json"
    require(digest(config) == digest(captured) == o["configurationSha256"], f"{path}: ordinary configuration differs from captured compiler proof")
    require(config.is_relative_to(Path(player["playerOutput"])), f"{path}: configuration outside executed Player")
    reflection = _reflection_parse(config, config.read_bytes())
    require(o["configurationHash"] == reflection["canonicalHash"], f"{path}: generated fixed-image guard configuration hash differs")
    sites = [s for s in reflection["configuration"]["sites"] if s["id"] == "m00-normal-hot-update-image"]
    require(len(sites) == 1 and sites[0]["kind"] == "FixedAssemblyBytes" and sites[0]["allowedTypes"] == [], f"{path}: fixed M00 image guard missing")
    site = sites[0]
    guard = "__AssemblyShadowReflectionBinding_" + o["configurationHash"] + "_" + hashlib.sha256(site["id"].encode()).hexdigest()
    require(o["fixedImageGuard"] == guard, f"{path}: fixed-image guard identity differs")
    image = _absolute(o["fixedImagePath"], path, "fixedImagePath")
    require(image.is_relative_to(Path(player["playerOutput"])) and image.name == ordinary_name + ".dll.bytes", f"{path}: ordinary image is not the Player M00 input")
    identity = read_identity(image)
    require(identity["name"] == ordinary_name and identity["sha256"] == site["imageSha256"] == o["fixedImageSha256"] and
            identity["fullName"] == site["providerAssemblyIdentity"] == o["fixedImageFullName"] == o["knownNameResolveFullName"],
            f"{path}: ordinary image identity/hash differs from actual fixed bytes")
    require(o["fixedImageMarker"] == "M00-HOTUPDATE-OK", f"{path}: ordinary interpreter marker absent")
    require(o["duplicateExceptionType"] == "System.ExecutionEngineException" and
            "reloading placeholder assembly is not supported!" in o["duplicateMessage"], f"{path}: duplicate-filled-placeholder failure contract differs")


RESULT_FIELDS = "schemaVersion processId milestone mode result error il2cpp moduleMvidObservationPolicy unityVersion platform buildGuid playerDataPath baselineBuildId runtimeAbiHash fixtureManifestPath fixtureManifestSha256 playerBuildReceiptPath playerBuildReceiptSha256 patchId patchManifestPath patchManifestSha256 compileSnapshotHash rawDiagnosticsPath rawDiagnosticsSha256 businessMarker configure begin stage validate commit abort stateCode state executionModeCode executionMode diagnosticsCode nativeDiagnosticsJson stageOrder checks snapshots actualLogicalAssemblies assemblyObservations loadObservations refRows executingWitnesses stageResults benchmark ordinary"
OBSERVATION_FIELDS = "name fullName mvid mvidAvailable executionCode executionMode isInterpreter logical"
TYPE_NAMES = dict(zip(CANDIDATES, (
    "AssemblyA.Contracts.AssemblyAContractVersion", "AssemblyA.Implementation.Extensibility.VersionedComponentBase",
    "AssemblyA.Implementation.Internal.InternalEntry", "AssemblyShadowDemo.Consumers.ContractsConsumer",
    "AssemblyShadowDemo.Consumers.DerivedExternalComponent")))


def _check_operations(checks, expected, path):
    rows = _array(checks, path)
    require(len(rows) == len(expected), f"{path}: missing/extra API checks")
    for row, (name, code) in zip(rows, expected):
        _fields(row, "name actual expected actualCode expectedCode", path)
        require(row["name"] == name and row["actual"] == row["expected"] == code and
                type(row["actualCode"]) is int and type(row["expectedCode"]) is int and
                row["actualCode"] == row["expectedCode"] == ERROR_CODES[code],
                f"{path}: exact ordered operation/ABI code differs: {name}")


def _observations(rows, identities, closure, logical, path):
    rows = _array(rows, path)
    _names([row["name"] for row in rows], path, "logical assembly names")
    for row in rows:
        _fields(row, OBSERVATION_FIELDS, path)
        name = row["name"]
        require(name in identities, f"{path}: observed unbound assembly: {name}")
        shadow = name in closure
        require(row["fullName"] == identities[name]["fullName"] and row["mvid"] == "" and not _bool(row["mvidAvailable"], path),
                f"{path}: assembly identity/unsupported MVID observation differs")
        require(_bool(row["isInterpreter"], path) == shadow and _bool(row["logical"], path) == logical and
                row["executionMode"] == ("InterpreterShadow" if shadow else "AotBaseline") and
                row["executionCode"] == ("Success" if name in CANDIDATES else "CandidateNotRegistered"),
                f"{path}: observed execution mode differs: {name}")


def _verify_phases(result, manifest, patch, expected, stages, path):
    mode = result["mode"]
    phases = ["initial", "staged", "validated"] + (["committed", "final"] if mode in SUCCESS_MODES else
              ["sealed"] if mode == "T04-03" else ["aborted"])
    snapshots = _array(result["snapshots"], path)
    _exact([s["phase"] for s in snapshots], phases, path, "actual snapshot phase order")
    previous_events = []
    for snapshot in snapshots:
        _fields(snapshot, "phase diagnostics", path)
        phase = snapshot["phase"]
        d = _diagnostic(snapshot["diagnostics"], f"{path}.{phase}")
        initial = phase == "initial"
        members, stable = ([], []) if initial else (expected, manifest["stableAotNames"])
        _verify_diag_invariants(d, members, stable, path, patch=patch)
        native_rows = sorted(manifest["_onBuild"]["nativeAssemblyIdentities"], key=lambda a: a["assemblyIndex"])
        physical = [(a["name"].casefold(), False) for a in native_rows]
        if mode == "T04-02" and phase == "final":
            ordinary = _fields(result["ordinary"], ORDINARY_FIELDS, f"{path}.ordinary")
            # Startup registered the token-zero placeholder after the native
            # inventory, before any shadows. Filling that SAME object makes
            # its existing slot visible; RegisterInterpreterAssembly only
            # invalidates enumeration and never appends it a second time.
            physical.append((ordinary["placeholderName"].casefold(), True))
        if d["generation"] == 1:
            physical += [(name.casefold(), True) for name in expected]
        require([(a["name"].casefold(), a["isInterpreter"]) for a in d["ordinaryAssemblies"]] == physical,
                f"{path}.{phase}: physical Assembly order/inventory differs from native metadata and actual publication")
        require(d["baselineBuildId"] == ("" if initial else manifest["baselineBuildId"]) and d["patchId"] == ("" if initial else patch["patchId"]),
                f"{path}.{phase}: native transaction identity differs")
        require(_same(d["events"][:len(previous_events)], previous_events), f"{path}.{phase}: native event history rewritten")
        previous_events = d["events"]
        expected_state = "Disabled" if initial else "Staging" if mode == "T04-04" and phase in ("staged", "validated") else \
            "Staged" if phase == "staged" or (mode == "T04-05" and phase == "validated") else \
            "Validated" if phase == "validated" else "Aborted" if phase in ("aborted", "sealed") else "Committed"
        require(d["state"] == expected_state, f"{path}.{phase}: wrong native transaction state")
        require(d["staged"] == (0 if initial else len(stages)), f"{path}.{phase}: staged member count differs")
        actual_staged = [a["name"].casefold() for a in d["assemblies"] if a["skeletonBuilt"]]
        require(set(actual_staged) == {name.casefold() for name in ([] if initial else stages)}, f"{path}.{phase}: wrong staged members")
        no_metadata = initial or phase == "staged" or mode in {"T04-04", "T04-05"}
        require(all(a["runtimeMetadataInitialized"] is (not no_metadata) for a in d["assemblies"] if a["skeletonBuilt"]),
                f"{path}.{phase}: private metadata initialization phase differs")
        error = "ClosureMemberMissing" if mode == "T04-04" and phase == "validated" else \
            "ReferenceEscapesClosure" if mode == "T04-05" and phase == "validated" else "Success"
        require(d["lastError"] == ERROR_CODES[error], f"{path}.{phase}: native validation error differs")
        if mode in SUCCESS_MODES:
            require(not {u["name"].casefold() for u in d["baselineUses"]} & {n.casefold() for n in expected},
                    f"{path}.{phase}: successful closure already used baseline")
        if phase in ("validated", "committed", "final", "sealed") and mode not in {"T04-04", "T04-05"}:
            for kind in ("metadata-begin", "metadata-ready"):
                _name_order([e["name"] for e in d["events"] if e["kind"] == kind], expected, path, kind)
        if phase in ("committed", "final"):
            require(sum(e["kind"] == "active-published" for e in d["events"]) == 1, f"{path}: publication must occur exactly once")
            for kind in ("initializer-begin", "initializer-complete"):
                _name_order([e["name"] for e in d["events"] if e["kind"] == kind], expected, path, kind)
        elif d["generation"] == 0:
            require(not any(e["kind"] in {"active-published", "initializer-begin", "initializer-complete"} for e in d["events"]), f"{path}: premature publication/initializer")
        if mode == "T04-05" and phase == "validated":
            match = re.fullmatch(r"ShadowClosureViolation Requester=(\S+) Provider=(\S+) ReferenceIndex=(\d+) Path=(\S+) -> (\S+) Site=(\S+)", d["detail"])
            require(match is not None, f"{path}: missing closure-violation requester/provider/index/path/site")
            requester, provider, index, left, right, site = match.groups()
            require(requester == left and provider == right and provider.casefold() == CANDIDATES[0].casefold() and
                    requester.casefold() not in {n.casefold() for n in expected} and site == "Validate.PhysicalAotAssemblyRef",
                    f"{path}: closure violation path/site differs")
            identities = manifest["_onBuild"]["assemblyIdentities"]
            rows = [a for a in identities if a["name"].casefold() == requester.casefold()]
            require(len(rows) == 1 and int(index) < len(rows[0]["referenceIdentities"]) and
                    rows[0]["referenceIdentities"][int(index)]["name"].casefold() == provider.casefold(),
                    f"{path}: violation reference index is not an actual linked requester AssemblyRef")
    if mode == "T04-03":
        require(any(u["name"].casefold() == CANDIDATES[0].casefold() for u in snapshots[-1]["diagnostics"]["baselineUses"]),
                f"{path}: baseline-use rejection lacks actual Contracts observation")
    require(result["stateCode"] == "Success" and result["state"] == snapshots[-1]["diagnostics"]["state"],
            f"{path}: final native GetState evidence differs")


def _verify_witnesses(result, identities, path):
    expected_loads = []
    for name in PROVIDER_ORDER:
        prefix = "AssemblyA" if name.startswith("AssemblyA.") else "Consumers"
        for overload, requested in (("simple", name), ("dll-suffix", name + ".dll"), ("AssemblyName", name),
                                    ("Type.GetType", TYPE_NAMES[name] + ", " + name), ("path", prefix + "/" + name + ".dll"),
                                    ("case", name.lower()), ("backslash-path", prefix + "\\" + name + ".dll")):
            expected_loads.append(dict(requested=requested, overload=overload, assemblyName=name, sameAssembly=True))
    require(_same(result["loadObservations"], expected_loads), f"{path}: literal load variants or reference equality witnesses differ")
    expected_refs = [dict(assemblyName=name, **row) for name in PROVIDER_ORDER for row in identities[name]["referenceIdentities"]]
    for row in result["refRows"]:
        _fields(row, "assemblyName " + REF_FIELDS, path)
        require(type(row["referenceIndex"]) is int, f"{path}: AssemblyRef index not integer")
    require(_same(result["refRows"], expected_refs), f"{path}: active declared AssemblyRef rows differ from actual patch DLLs")
    expected_exec = [dict(assemblyName=name, executingAssemblyName=name, sameAssembly=True) for name in PROVIDER_ORDER]
    require(_same(result["executingWitnesses"], expected_exec), f"{path}: executing Assembly equality witnesses differ")


def _inactive(value, fields, path):
    # Unity may represent an unassigned inline serializable class as null or
    # as its zero/default DTO. Neither representation can claim an observation.
    if value is None: return
    _fields(value, fields, path)
    booleans = set("enabled finalSameAssembly finalMvidAvailable aotMvidAvailable fixedImageMvidAvailable aotLoadMatchesType placeholderFoundBefore placeholderHiddenBefore placeholderSameAfterLoad fixedImageTamperRejected fixedImageNullRejected fixedImageCallerBytesUnchanged loadedNameSame enumeratedSame duplicateRejected knownNameResolveSame supplementaryCallerBytesUnchanged".split())
    integers = set("schemaVersion warmupCount lookupCount elapsedTicks stopwatchFrequency checksum assemblyCountBefore assemblyCountAfter ordinaryCountBefore ordinaryCountAfter ordinaryCountAfterDuplicate knownNameResolveEvents supplementaryFirstCode supplementaryRepeatCode supplementaryInvalidModeCode".split())
    for key, item in value.items():
        if key in booleans: valid = type(item) is bool and not item
        elif key in integers: valid = type(item) is int and (item == 0 or key == "schemaVersion" and item == 1)
        elif key == "finalReferenceIdentities": valid = item is None or item == []
        else: valid = item is None or type(item) is str and item == ""
        require(valid, f"{path}: inactive probe contains mistyped or claimed evidence: {key}")


def verify_case(path, manifest, baseline, fixtures, player, player_path):
    result = _obj(path, RESULT_FIELDS)
    mode = result["mode"]
    require(mode in REQUIRED_MODES and path.name == "m04-" + mode + ".json", f"{path}: unknown mode/filename")
    require(type(result["schemaVersion"]) is int and result["schemaVersion"] == 1 and result["milestone"] == "M04" and
            result["result"] == "Passed" and result["error"] == "" and result["il2cpp"] is True,
            f"{path}: not a successful real IL2CPP M04 result")
    require(result["moduleMvidObservationPolicy"] == MVID_POLICY, f"{path}: unsupported runtime MVID policy absent")
    _integer(result["processId"], path, "processId", 1)
    require(result["platform"] == "OSXPlayer", f"{path}: not pinned macOS Player")
    for field in ("baselineBuildId", "runtimeAbiHash", "unityVersion", "buildGuid"):
        require(result[field] == player[field], f"{path}: result {field} differs from executed build")
    require(result["playerDataPath"] == str(Path(player["playerOutput"]) / "Contents"), f"{path}: Player data path differs")
    for field, expected in (("fixtureManifestPath", manifest["_path"]), ("fixtureManifestSha256", digest(Path(manifest["_path"]))),
                            ("playerBuildReceiptPath", str(player_path)), ("playerBuildReceiptSha256", digest(player_path))):
        require(result[field] == expected, f"{path}: immutable {field} binding differs")
    array_fields = "stageOrder checks snapshots actualLogicalAssemblies assemblyObservations loadObservations refRows executingWitnesses stageResults"
    for field in array_fields.split(): _array(result[field], f"{path}.{field}")
    nonstrings = set(array_fields.split()) | {"schemaVersion", "processId", "il2cpp", "benchmark", "ordinary"}
    for field in set(RESULT_FIELDS.split()) - nonstrings:
        require(type(result[field]) is str, f"{path}.{field}: missing string evidence")
    identities = _verify_native_metadata(player, player_path)
    identities.update({a["name"]: a for a in player["assemblyIdentities"]})
    if mode in OFF_MODES:
        for field in "patchId patchManifestPath patchManifestSha256 compileSnapshotHash".split():
            require(result[field] == "", f"{path}: OFF process claims patch activity")
        for field in "stageOrder stageResults assemblyObservations actualLogicalAssemblies loadObservations refRows executingWitnesses".split():
            require(result[field] == [], f"{path}: OFF process fabricated shadow observations")
        require(result["businessMarker"] == "M04-REFERENCE-PROBE", f"{path}: OFF business marker differs")
        if mode == "T04-10-BenchmarkOff":
            require(result["checks"] == result["snapshots"] == [], f"{path}: OFF benchmark called diagnostic/API path")
            for field in "configure begin stage validate commit abort stateCode state executionModeCode executionMode diagnosticsCode nativeDiagnosticsJson rawDiagnosticsPath rawDiagnosticsSha256".split():
                require(result[field] == "", f"{path}: OFF benchmark must not configure/query Shadow API")
        else:
            names = "configure begin stage validate commit abort state execution-mode diagnostics".split()
            _check_operations(result["checks"], [(n, "FeatureDisabled") for n in names], path)
            for field in "configure begin stage validate commit abort stateCode executionModeCode diagnosticsCode".split():
                require(result[field] == "FeatureDisabled", f"{path}: OFF API code differs")
            require(result["state"] == "Disabled" and result["executionMode"] == "AotBaseline", f"{path}: OFF output values differ")
            _exact([s["phase"] for s in result["snapshots"]], ["disabled"], path, "OFF snapshots")
            _fields(result["snapshots"][0], "phase diagnostics", path)
            d = _raw_diagnostic(result, path)
            require(d["enabled"] is False and d["state"] == "Disabled" and d["lastError"] == 1, f"{path}: OFF diagnostics differ")
            for field in "generation expected staged retainedBytes enumerationGeneration classEnumerationGeneration".split():
                require(d[field] == 0, f"{path}: OFF state changed")
            for field in "ordinaryAssemblies ordinaryClasses closureLoadOrder stableAotNames commitOrder assemblies events baselineUses".split():
                require(d[field] == [], f"{path}: OFF diagnostics claim registry state")
            require(d["detail"] == d["baselineBuildId"] == d["patchId"] == "", f"{path}: OFF diagnostics claim transaction identity")
            _verify_ordinary(result["ordinary"], player, path)
        _verify_benchmark(result["benchmark"], identities[INTERNAL], False, path)
    else:
        pid = "P01" if mode == "T04-01" else "P03"
        fixture, _, patch_path, _, _ = fixtures[pid]
        patch = _obj(patch_path)
        for field, expected in (("patchId", pid), ("patchManifestPath", str(patch_path)),
                                ("patchManifestSha256", digest(patch_path)), ("compileSnapshotHash", fixture["compileSnapshotHash"])):
            require(result[field] == expected, f"{path}: result patch binding differs: {field}")
        expected = [CANDIDATES[0]] if mode == "T04-05" else fixture["closureLoadOrder"]
        stages = [INTERNAL] if mode == "T04-04" else expected
        _exact(result["stageOrder"], stages, path, "stageOrder")
        expected_stage = [dict(name=n, code="Success", dllSha256=next(a["sha256"] for a in patch["closure"] if a["name"] == n),
                               pdbSha256=next(a["pdbSha256"] for a in patch["closure"] if a["name"] == n)) for n in stages]
        require(_same(result["stageResults"], expected_stage), f"{path}: stage byte hash/code observations differ")
        validation = "ClosureMemberMissing" if mode == "T04-04" else "ReferenceEscapesClosure" if mode == "T04-05" else "Success"
        operations = [("configure", "Success"), ("begin", "Success")] + [("stage-" + n, "Success") for n in stages] + [("validate", validation)]
        if mode in SUCCESS_MODES: operations += [("commit", "Success")]
        elif mode == "T04-03": operations += [("commit-after-baseline-use", "BaselineAlreadyUsed"), ("abort-after-baseline-use", "Success")]
        else: operations += [("abort", "Success")]
        _check_operations(result["checks"], operations, path)
        require(result["configure"] == result["begin"] == "Success" and result["validate"] == validation and result["stage"] == "" and
                result["executionModeCode"] == result["executionMode"] == "" and result["diagnosticsCode"] == "Success", f"{path}: result API fields differ")
        require(result["commit"] == ("Success" if mode in SUCCESS_MODES else "BaselineAlreadyUsed" if mode == "T04-03" else "") and
                result["abort"] == ("" if mode in SUCCESS_MODES else "Success"), f"{path}: commit/abort outcomes differ")
        _verify_phases(result, manifest, patch, expected, stages, path)
        _raw_diagnostic(result, path)
        closure = set(fixture["closureLoadOrder"]) if mode in SUCCESS_MODES else set()
        if closure: identities.update({a["name"]: a for a in fixture["assemblyIdentities"]})
        if mode in SUCCESS_MODES:
            _observations(result["assemblyObservations"], identities, closure, True, path)
            _exact([a["name"] for a in result["assemblyObservations"]], list(CANDIDATES) + ["mscorlib", "UnityEngine.CoreModule"], path, "direct assembly observations")
            require(result["businessMarker"] == "PATCH-P01-INTERNAL", f"{path}: missing real shadow Internal execution marker")
        else:
            require(result["assemblyObservations"] == [] and result["businessMarker"] == "M04-REFERENCE-PROBE", f"{path}: private transaction ran business code")
        if mode in {"T04-01", "T04-02", "T04-03", "T04-06", "T04-07"}:
            _observations(result["actualLogicalAssemblies"], identities, closure, mode != "T04-03", path)
            before = [a["name"].casefold() for a in result["snapshots"][0]["diagnostics"]["ordinaryAssemblies"]]
            after = [a["name"].casefold() for a in result["actualLogicalAssemblies"]]
            require(after == before, f"{path}: logical enumeration lost baseline position/order or deduplicated fabricated observations")
            require(set(CANDIDATES) <= {a["name"] for a in result["actualLogicalAssemblies"]}, f"{path}: logical candidates missing")
        else: require(result["actualLogicalAssemblies"] == [], f"{path}: unexpected logical observation phase")
        if mode in {"T04-02", "T04-06", "T04-07"}: _verify_witnesses(result, identities, path)
        elif mode == "T04-03":
            require(_same(result["loadObservations"], [dict(requested=CANDIDATES[0], overload="staged-normal", assemblyName=CANDIDATES[0], sameAssembly=True)]) and
                    result["refRows"] == result["executingWitnesses"] == [], f"{path}: staged normal-lookup witness differs")
        else:
            require(result["loadObservations"] == result["refRows"] == result["executingWitnesses"] == [], f"{path}: unexpected identity witness mode")
        if mode == "T04-02": _verify_ordinary(result["ordinary"], player, path)
        if mode == "T04-09-BenchmarkOn": _verify_benchmark(result["benchmark"], identities[INTERNAL], True, path)
    if mode not in {"T04-02", "T04-08"}: _inactive(result["ordinary"], ORDINARY_FIELDS, f"{path}.ordinary")
    if mode not in {"T04-08", "T04-09-BenchmarkOn", "T04-10-BenchmarkOff"}: _inactive(result["benchmark"], BENCHMARK_FIELDS, f"{path}.benchmark")
    return {"mode": mode, "processId": result["processId"], "passed": True, "resultSha256": digest(path)}


def verify_suite(fixture_manifest_path, result_dir, baseline_manifest_path=None, baseline_snapshot_path=None,
                 on_build_path=None, off_build_path=None, editor_replay_path=None, m01_baseline_root=None):
    manifest_path = _absolute(str(fixture_manifest_path), fixture_manifest_path, "fixtureManifest")
    if m01_baseline_root is None:
        m01_baseline_root = Path(__file__).resolve().parents[2] / "BaselineArtifacts/StandaloneOSX/M01-Baseline-v1"
    manifest, baseline, snapshot, fixtures = _verify_inputs(manifest_path, baseline_manifest_path, baseline_snapshot_path, m01_baseline_root)
    require(on_build_path is not None and off_build_path is not None, "M04 requires explicit native ON/OFF build receipts")
    on_path, off_path = Path(on_build_path), Path(off_build_path)
    on = _verify_player_build_receipt(on_path, manifest, baseline, "NativeOn")
    off = _verify_player_build_receipt(off_path, manifest, baseline, "NativeOff")
    require(Path(on["inputSnapshot"]) == snapshot, "NativeOn does not bind the M04 baseline snapshot")
    for field in ("inputSnapshot", "inputSnapshotHash", "nativeLibrarySha256", "buildGuid", "playerOutput"):
        require(on[field] != off[field], f"M04 native ON/OFF {field} must be distinct")
    manifest["_onBuild"], manifest["_offBuild"] = on, off
    for pid, item in fixtures.items(): _verify_patch(pid, item, manifest, baseline)
    _verify_replay(Path(editor_replay_path) if editor_replay_path else manifest_path.with_name("m04-editor-replay.json"), manifest, baseline, fixtures, on_path)
    return verify_results(result_dir, manifest, baseline, fixtures, on, off, on_path, off_path)


def verify_results(result_dir, manifest, baseline, fixtures, on, off, on_path, off_path):
    """Result gate over already-verified inputs; not a standalone artifact gate."""
    root = _absolute(str(result_dir), result_dir, "resultDir", directory=True)
    paths = [p for p in root.glob("m04-*.json") if not p.name.endswith("-native-diagnostics.json")]
    require({p.name for p in paths} == {"m04-" + mode + ".json" for mode in REQUIRED_MODES}, f"{root}: exact required M04 process modes differ")
    results = []
    for path in sorted(paths):
        mode = path.stem[4:]
        results.append(verify_case(path, manifest, baseline, fixtures, off if mode in OFF_MODES else on, off_path if mode in OFF_MODES else on_path))
    require(len({r["processId"] for r in results}) == len(results), f"{root}: modes must identify separate actual Player processes")
    expected_raw = {"m04-" + mode + "-native-diagnostics.json" for mode in REQUIRED_MODES if mode != "T04-10-BenchmarkOff"}
    require({p.name for p in root.glob("m04-*-native-diagnostics.json")} == expected_raw, f"{root}: missing/extra raw native diagnostics files")
    return dict(milestone="M04", resultPassed=True, baselineBuildId=manifest["baselineBuildId"], runtimeAbiHash=manifest["runtimeAbiHash"], modes=results,
                moduleMvidObservationPolicy=MVID_POLICY,
                evidence="Byte-bound PE and native format-31 Assembly/Image identities, compiler/linker/resources, Editor replay and exact real-process observations. Unsigned evidence is not authentication; Editor owns semantic/IL and installed-catalog proof; no unsupported runtime module MVID claim.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture-manifest", "result-dir", "on-build", "off-build"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("baseline-manifest", "baseline-snapshot", "editor-replay", "m01-baseline-root", "output"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify_suite(args.fixture_manifest.absolute(), args.result_dir.absolute(),
                              args.baseline_manifest.absolute() if args.baseline_manifest else None,
                              args.baseline_snapshot.absolute() if args.baseline_snapshot else None,
                              args.on_build.absolute(), args.off_build.absolute(),
                              args.editor_replay.absolute() if args.editor_replay else None,
                              args.m01_baseline_root.absolute() if args.m01_baseline_root else None)
        text = json.dumps(result, indent=2) + "\n"
        if args.output:
            require(not args.output.is_symlink(), f"Refusing symlinked output: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            # Atomic exclusive creation, not a racy exists()+write_text pair.
            with args.output.open("x", encoding="utf-8") as stream: stream.write(text)
        print(text, end="")
        return 0
    except (VerificationError, OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
