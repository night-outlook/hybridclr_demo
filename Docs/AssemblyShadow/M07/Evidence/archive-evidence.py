#!/usr/bin/env python3
"""Validate and retain the final M07 v6 evidence without rewriting inputs."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


PROJECT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow_m07")
TEMP = PROJECT / "_temp/AssemblyShadow"
WORKFLOW_ROOT = TEMP / "M02Validation-00d060a2714443d2ba21203d5f1e9c8e"
RESOURCE_ROOT = TEMP / "M07ResourceBaseline-M07-Baseline-v6-69dc0abc1b82475da36eb518980dee6f"
ON_ROOT = TEMP / "M07PlayerInputs-30c933f9043545cc887466494ecef5d4"
OFF_ROOT = TEMP / "M07PlayerInputs-b90e7402282a44108f738b5a3f718e74"
RESULT_ROOT = TEMP / "M07Results-v6-20260906T2207"
CLOSEOUT_ROOT = TEMP / "M07Closeout-20260906T2248"
EDITOR_ROOT = TEMP / "EditorTests-63381b6d5cb34f2a8de80ce878b3c3c0"
DEMO_EXECUTABLE = "3aab779a3304dd9785ab14fb5fcdc73a107066f7"
DEMO_PIN = "671737c082effa5094bed16b087f6da5c3c666c9"
RUNTIME = "a19db144751f4f016769b90e61a80b8c27578678"
NATIVE = "666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8"
PACKAGE = "2180b99daf39095cd76301da2bdf34ac945ee8b4"
BASELINE = "M07-Baseline-v6"
PATCHES = ("P01", "P02", "P03", "P04", "P05")
REJECTED = ("P05-DllOnly", "P14-ClassRename", "P15-SerializeReferenceRename")
MODES = (
    "T07-01-Prefab-P01",
    "T07-02-Nested-P02",
    "T07-03-FullClosure-P03",
    "T07-04-UnityApis-P01",
    "T07-05-Scriptable-P03",
    "T07-06-SceneSingle-P01",
    "T07-07-SceneAdditive-P03",
    "T07-08-SerializeReference-P03",
    "T07-09-Messages-P01",
    "T07-10-Cache-P03",
    "T07-11-DelayedCatalog-P03",
    "T07-12-P04-NonSerialized",
    "T07-13-P05-Rebuilt",
    "T07-14-FeatureOff",
)
BUILD_LOGS = tuple(
    PROJECT / "_temp" / ("UnityExec_20260906_" + stamp + ".log")
    for stamp in (
        "212951",
        "213106",
        "213156",
        "213645",
        "213920",
        "213938",
        "214252",
        "214303",
    )
)


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest_stream(stream) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def write_json_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=root, text=True, env={**os.environ, "LC_ALL": "C"}
    ).strip()


def canonical_file(path: Path) -> Path:
    require(path.is_absolute(), "Absolute input required: " + str(path))
    resolved = path.resolve(strict=True)
    require(path == resolved and resolved.is_relative_to(PROJECT), "Input escapes/aliases project: " + str(path))
    require(resolved.is_file() and not resolved.is_symlink(), "Regular file required: " + str(path))
    return resolved


def canonical_directory(path: Path) -> Path:
    require(path.is_absolute(), "Absolute directory required: " + str(path))
    resolved = path.resolve(strict=True)
    require(path == resolved and resolved.is_relative_to(PROJECT), "Directory escapes/aliases project: " + str(path))
    require(resolved.is_dir() and not resolved.is_symlink(), "Regular directory required: " + str(path))
    return resolved


def safe_name(name: str) -> None:
    value = PurePosixPath(name)
    require(name and not value.is_absolute() and ".." not in value.parts and str(value) == name, "Unsafe archive name: " + name)


def file_entry(source: Path, name: str, category: str) -> dict:
    safe_name(name)
    source = canonical_file(source)
    return {
        "originalPath": str(source),
        "name": name,
        "category": category,
        "size": source.stat().st_size,
        "sha256": sha256(source),
        "executable": bool(source.stat().st_mode & stat.S_IXUSR),
    }


def collect_tree(root: Path, prefix: str, category: str, predicate=None) -> list[dict]:
    root = canonical_directory(root)
    safe_name(prefix)
    entries = []
    for source in sorted(root.rglob("*")):
        require(not source.is_symlink(), "Symlink in evidence tree: " + str(source))
        if source.is_dir():
            continue
        relative = source.relative_to(root)
        if predicate is not None and not predicate(relative):
            continue
        entries.append(file_entry(source, prefix + "/" + relative.as_posix(), category))
    require(entries, "Empty evidence tree: " + str(root))
    return entries


def archive_entries(destination: Path, name: str, entries: list[dict], context: dict) -> dict:
    safe_name(name)
    require(entries and len({row["name"] for row in entries}) == len(entries), "Empty/duplicate archive inventory")
    entries = sorted(entries, key=lambda row: row["name"])
    archive_path = destination / name
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for row in entries:
                    source = Path(row["originalPath"])
                    require(sha256(source) == row["sha256"], "Archive input changed: " + str(source))
                    info = tarfile.TarInfo(row["name"])
                    info.size = row["size"]
                    info.mode = 0o755 if row["executable"] else 0o644
                    info.mtime = info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with source.open("rb") as stream:
                        archive.addfile(info, stream)
    expected = {row["name"]: row for row in entries}
    seen = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            require(member.isfile() and member.name in expected and member.name not in seen, "Unexpected archive member")
            row = expected[member.name]
            require(member.size == row["size"] and member.mtime == member.uid == member.gid == 0, "Archive metadata drift")
            stream = archive.extractfile(member)
            require(stream is not None and digest_stream(stream) == row["sha256"], "Archive payload differs: " + member.name)
            seen.add(member.name)
    require(seen == set(expected), "Incomplete archive: " + name)
    index_path = destination / (name.removesuffix(".tar.gz") + ".index.json")
    index = {
        "schemaVersion": 1,
        "milestone": "M07",
        "kind": "DeterministicLosslessArchive",
        **context,
        "archivePath": str(archive_path),
        "archiveSha256": sha256(archive_path),
        "archiveSize": archive_path.stat().st_size,
        "fileCount": len(entries),
        "files": entries,
        "allArchivedBytesMatch": True,
        "normalizedTarMetadata": True,
    }
    write_json_new(index_path, index)
    return {
        "name": name,
        "path": str(archive_path),
        "sha256": index["archiveSha256"],
        "size": index["archiveSize"],
        "fileCount": len(entries),
        "indexPath": str(index_path),
        "indexSha256": sha256(index_path),
    }


def copy_artifacts(destination: Path, entries: list[dict]) -> list[dict]:
    require(len({row["name"] for row in entries}) == len(entries), "Duplicate copy target")
    for row in entries:
        source = Path(row["originalPath"])
        target = destination / row["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(target.stat().st_size == row["size"] and sha256(target) == row["sha256"] == sha256(source), "Copied evidence differs")
        row["path"] = str(target)
    return entries


def validate_player(path: Path, variant: str) -> dict:
    value = read_json(path)
    require(value.get("schemaVersion") == 1 and value.get("milestone") == "M07", "Wrong Player schema")
    require(value.get("baselineBuildId") == BASELINE and value.get("variant") == variant, "Wrong Player identity")
    require(value.get("resourceBaselinePath") == str(RESOURCE_ROOT), "Player resource root differs")
    for path_field, hash_field in (
        ("nativeLibraryPath", "nativeLibrarySha256"),
        ("nativeMetadataPath", "nativeMetadataSha256"),
        ("placeholderManifestPath", "placeholderManifestSha256"),
        ("resourceBuildReceiptPath", "resourceBuildReceiptSha256"),
    ):
        source = canonical_file(Path(value[path_field]))
        require(sha256(source) == value[hash_field], "Player-bound input differs: " + path_field)
    canonical_directory(Path(value["playerOutput"]))
    return value


def validate_launches(path: Path) -> dict:
    value = read_json(path)
    launches = value.get("processLaunches")
    require(value.get("schemaVersion") == 1 and value.get("milestone") == "M07", "Wrong launch schema")
    require(value.get("diagnosticOnly") is True and value.get("fullModeInventory") == list(MODES), "Wrong full mode inventory")
    require(value.get("requestedModes") == list(MODES) and value.get("completedModes") == 14, "Incomplete launch inventory")
    require(value.get("inputsUnchanged") is True and value.get("inputHashesBefore") == value.get("inputHashesAfter"), "Player app/input tree changed")
    require(type(launches) is list and len(launches) == 14 and len({row.get("processId") for row in launches}) == 14, "Player processes are not distinct")
    require({row.get("mode") for row in launches} == set(MODES), "Player launch modes differ")
    for row in launches:
        require(row.get("passed") is True and row.get("exitCode") == 0 and row.get("timedOut") is False, "Failed Player launch")
        result = canonical_file(Path(row["resultPath"]))
        require(result.is_relative_to(RESULT_ROOT) and sha256(result) == row["resultSha256"], "Player result changed")
        payload = read_json(result)
        require(payload.get("result") == "Passed" and payload.get("mode") == row["mode"] and payload.get("processId") == row["processId"], "Player payload identity differs")
    return value


def main(project: Path) -> None:
    project = project.resolve(strict=True)
    require(project == PROJECT, "Archiver is bound to the isolated M07 checkout")
    destination = PROJECT / "Docs/AssemblyShadow/M07/Evidence"
    require(destination.is_dir() and not destination.is_symlink(), "Evidence directory is missing/aliased")
    outputs = (
        "player-results-v6.tar.gz",
        "workflow-proofs-v6.tar.gz",
        "resource-baseline-v6.tar.gz",
        "player-input-proofs-v6.tar.gz",
        "closeout-v6.tar.gz",
        "build-logs-v6.tar.gz",
        "artifact-index-v6.json",
    )
    require(not any((destination / name).exists() for name in outputs), "Retention output already exists")

    workflow_path = canonical_file(WORKFLOW_ROOT / "m07-build-workflow.json")
    fixture_path = canonical_file(WORKFLOW_ROOT / "m07-fixtures.json")
    replay_path = canonical_file(WORKFLOW_ROOT / "m07-editor-replay.json")
    on_path = canonical_file(ON_ROOT / "m07-player-build.json")
    off_path = canonical_file(OFF_ROOT / "m07-player-build.json")
    launches_path = canonical_file(RESULT_ROOT / "m07-player-launches.json")
    strict_path = canonical_file(CLOSEOUT_ROOT / "m07-strict-current.json")
    native_path = canonical_file(CLOSEOUT_ROOT / "m07-native-current-pass.json")
    installed_path = canonical_file(CLOSEOUT_ROOT / "installed-source-final.json")
    python_path = canonical_file(CLOSEOUT_ROOT / "python-tests.log")
    install_receipt = canonical_file(TEMP / "m00-install-receipt.json")
    install_repeatability = canonical_file(TEMP / "m00-install-repeatability.json")

    workflow = read_json(workflow_path)
    require(workflow.get("schemaVersion") == 1 and workflow.get("milestone") == "M07" and workflow.get("result") == "Passed", "Workflow did not pass")
    require(workflow.get("baselineBuildId") == BASELINE and workflow.get("resourceBaselinePath") == str(RESOURCE_ROOT), "Workflow identity differs")
    require(workflow.get("nativeOnReceipt") == str(on_path) and workflow.get("nativeOffReceipt") == str(off_path), "Workflow Player receipts differ")
    require(workflow.get("fixtureManifest") == str(fixture_path) and workflow.get("editorReplayReceipt") == str(replay_path), "Workflow fixture/replay differs")

    fixture = read_json(fixture_path)
    require(fixture.get("schemaVersion") == 1 and fixture.get("milestone") == "M07" and fixture.get("baselineBuildId") == BASELINE, "Fixture identity differs")
    require([row.get("patchId") for row in fixture.get("fixtures", [])] == list(PATCHES), "Positive fixture inventory differs")
    require([row.get("patchId") for row in fixture.get("rejectedFixtures", [])] == list(REJECTED), "Rejected fixture inventory differs")
    require(all(row.get("errorCode") == "ResourceRebuildRequired" for row in fixture["rejectedFixtures"]), "Structural rejection code differs")
    replay = read_json(replay_path)
    require(replay.get("schemaVersion") == 1 and replay.get("milestone") == "M07" and replay.get("result") == "Passed", "Editor replay did not pass")
    require(replay.get("fixtureManifestPath") == str(fixture_path) and replay.get("fixtureManifestSha256") == sha256(fixture_path), "Replay fixture binding differs")

    on = validate_player(on_path, "NativeOn")
    off = validate_player(off_path, "NativeOff")
    require(on["buildGuid"] != off["buildGuid"] and on["nativeLibrarySha256"] != off["nativeLibrarySha256"], "ON/OFF Players are not distinct")
    launches = validate_launches(launches_path)
    strict = read_json(strict_path)
    require(strict.get("milestone") == "M07" and strict.get("resultPassed") is True and strict.get("diagnosticOnly") is False, "Strict Gate 3B did not pass")
    require(strict.get("gate") == "Gate 3B" and strict.get("missingModes") == [] and len(strict.get("modes", [])) == 14, "Strict mode inventory differs")
    require({row.get("processId") for row in strict["modes"]} == {row.get("processId") for row in launches["processLaunches"]}, "Strict/launch PID inventory differs")

    editor_xml = canonical_file(EDITOR_ROOT / "results.xml")
    editor_log = canonical_file(EDITOR_ROOT / "unity.log")
    test_run = ET.parse(editor_xml).getroot()
    editor = {key: test_run.attrib.get(key, "") for key in ("result", "total", "passed", "failed", "skipped", "inconclusive")}
    require(editor["result"] == "Passed" and editor["total"] == editor["passed"] == "912", "Editor suite did not pass 912 tests")
    require(all(int(editor[key] or 0) == 0 for key in ("failed", "skipped", "inconclusive")), "Editor suite was incomplete")
    python_text = python_path.read_text(encoding="utf-8", errors="replace")
    require(re.search(r"Ran 356 tests? in", python_text) is not None and re.search(r"(?m)^OK$", python_text) is not None, "Python suite did not pass 356 tests")
    require("skipped=" not in python_text and " ... skipped " not in python_text, "Python suite contains a skip")
    native = read_json(native_path)
    require(native.get("success") is True and native.get("checks") == 824 and native.get("syntaxChecks") == 20 and native.get("dependencyCount") == 1080, "Native suite differs")
    installed = read_json(installed_path)
    require(installed.get("demoSourceVerified") is True and installed.get("configuredShadowMode") == "on" and installed.get("installedFiles") == 942, "Installed-source verification differs")
    repeatability = read_json(install_repeatability)
    require(repeatability.get("identical") is True and repeatability.get("installedFiles") == 942 and repeatability.get("receiptSha256") == sha256(install_receipt), "Install repeatability differs")
    for path in BUILD_LOGS:
        canonical_file(path)

    pins_path = canonical_file(PROJECT / "ProjectSettings/AssemblyShadowSourcePins.json")
    pins = read_json(pins_path)
    require(pins["demo"]["revision"] == DEMO_EXECUTABLE and pins["hybridclr"]["revision"] == RUNTIME, "Demo/runtime source pin differs")
    require(pins["il2cppPlus"]["revision"] == NATIVE and pins["hybridclrUnity"]["revision"] == PACKAGE, "Native/package source pin differs")
    require(git(PROJECT, "rev-parse", "HEAD") == DEMO_PIN, "Demo HEAD differs before retention")
    for root, revision in ((Path("/Users/ah/GitHub/hybridclr/hybridclr"), RUNTIME), (Path("/Users/ah/GitHub/hybridclr/il2cpp_plus"), NATIVE), (Path("/Users/ah/GitHub/hybridclr/hybridclr_unity"), PACKAGE)):
        require(git(root, "rev-parse", "HEAD") == revision and not git(root, "status", "--short"), "Paired repository drift: " + str(root))

    closeout_path = CLOSEOUT_ROOT / "m07-closeout-v6.json"
    require(not closeout_path.exists() and not closeout_path.is_symlink(), "Closeout receipt already exists")
    closeout = {
        "schemaVersion": 1,
        "milestone": "M07",
        "kind": "PostPlayerCloseoutValidation",
        "result": "Passed",
        "recordedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "baselineBuildId": BASELINE,
        "sourceRevisions": {"demoExecutable": DEMO_EXECUTABLE, "demoPin": DEMO_PIN, "runtime": RUNTIME, "native": NATIVE, "package": PACKAGE},
        "workflow": {"path": str(workflow_path), "sha256": sha256(workflow_path)},
        "fixtureManifest": {"path": str(fixture_path), "sha256": sha256(fixture_path), "positiveFixtures": 5, "rejectedFixtures": 3},
        "editorReplay": {"path": str(replay_path), "sha256": sha256(replay_path), "result": "Passed"},
        "players": [
            {"variant": on["variant"], "receiptPath": str(on_path), "receiptSha256": sha256(on_path), "buildGuid": on["buildGuid"], "nativeLibrarySha256": on["nativeLibrarySha256"]},
            {"variant": off["variant"], "receiptPath": str(off_path), "receiptSha256": sha256(off_path), "buildGuid": off["buildGuid"], "nativeLibrarySha256": off["nativeLibrarySha256"]},
        ],
        "playerLaunches": {"path": str(launches_path), "sha256": sha256(launches_path), "caseCount": 14, "distinctProcesses": 14, "inputsUnchanged": True},
        "strictGate": {"path": str(strict_path), "sha256": sha256(strict_path), "gate": "Gate 3B", "caseCount": 14, "diagnosticOnly": False},
        "editorTests": {"resultsPath": str(editor_xml), "resultsSha256": sha256(editor_xml), "unityLogPath": str(editor_log), "unityLogSha256": sha256(editor_log), **editor},
        "pythonTests": {"path": str(python_path), "sha256": sha256(python_path), "tests": 356, "skipped": 0},
        "nativeTests": {"path": str(native_path), "sha256": sha256(native_path), "checks": 824, "syntaxChecks": 20, "dependencyCount": 1080},
        "installedSource": {"path": str(installed_path), "sha256": sha256(installed_path), "demoSourceVerified": True, "installedFiles": 942, "configuredShadowMode": "on"},
        "installReceipt": {"path": str(install_receipt), "sha256": sha256(install_receipt)},
        "installRepeatability": {"path": str(install_repeatability), "sha256": sha256(install_repeatability), "identical": True},
        "buildLogs": [{"path": str(path), "sha256": sha256(path)} for path in BUILD_LOGS],
        "limitations": "StandaloneOSX arm64 Unity 2022.3.62f2 only; unsigned local evidence is not authentication and does not claim M08-M12 behavior.",
    }
    write_json_new(closeout_path, closeout)

    context = {
        "baselineBuildId": BASELINE,
        "demoExecutableRevision": DEMO_EXECUTABLE,
        "demoPinRevision": DEMO_PIN,
        "runtimeRevision": RUNTIME,
        "nativeRevision": NATIVE,
        "packageRevision": PACKAGE,
    }
    archives = [
        archive_entries(destination, "player-results-v6.tar.gz", collect_tree(RESULT_ROOT, "Players", "actual-player-evidence"), context),
        archive_entries(destination, "workflow-proofs-v6.tar.gz", collect_tree(WORKFLOW_ROOT, "Workflow", "fixture-resource-proof", lambda relative: not relative.parts[0].endswith("-compile")), context),
        archive_entries(destination, "resource-baseline-v6.tar.gz", collect_tree(RESOURCE_ROOT, "ResourceBaseline", "resource-build-proof"), context),
    ]
    player_entries = []
    proof_paths = (
        "LinkedPlayer/linked-player-receipt.json",
        "RawTypeAdmissions/compiled-evidence.json",
        "RawTypeAdmissions/configuration.json",
        "RawTypeAdmissions/linked-evidence.json",
        "ReflectionBindings/LinkedRetargeting/evidence.json",
        "ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes",
        "ReflectionBindings/configuration.json",
        "assembly-snapshot.json",
        "m07-placeholder-AssemblyManifest.cpp",
        "m07-player-build.json",
    )
    for root, prefix in ((ON_ROOT, "NativeOn"), (OFF_ROOT, "NativeOff")):
        for relative in proof_paths:
            player_entries.append(file_entry(root / relative, prefix + "/" + relative, "player-input-proof"))
    archives.append(archive_entries(destination, "player-input-proofs-v6.tar.gz", player_entries, context))
    closeout_entries = collect_tree(EDITOR_ROOT, "EditorTests", "fresh-editor-suite")
    for source, name in (
        (python_path, "python-tests.log"),
        (strict_path, "m07-strict-current.json"),
        (native_path, "m07-native-current-pass.json"),
        (CLOSEOUT_ROOT / "m07-native-current.json", "m07-native-template-lifecycle-diagnostic.json"),
        (installed_path, "installed-source-final.json"),
        (closeout_path, "m07-closeout-v6.json"),
        (install_receipt, "m00-install-receipt.json"),
        (install_repeatability, "m00-install-repeatability.json"),
        (PROJECT / "_temp/UnityExec_20260906_225630.log", "UnityExec_20260906_225630.log"),
        (PROJECT / "_temp/UnityExec_20260906_225804.log", "UnityExec_20260906_225804.log"),
    ):
        closeout_entries.append(file_entry(source, "Closeout/" + name, "fresh-closeout-evidence"))
    archives.append(archive_entries(destination, "closeout-v6.tar.gz", closeout_entries, context))
    archives.append(archive_entries(destination, "build-logs-v6.tar.gz", [file_entry(path, "BuildLogs/" + path.name, "guarded-unity-build-log") for path in BUILD_LOGS], context))

    copies = []
    def add(source: Path, name: str, category: str) -> None:
        copies.append(file_entry(source, name, category))

    baseline_manifest = canonical_file(Path(fixture["baselineManifestPath"]))
    add(workflow_path, "workflow/m07-build-workflow-v6.json", "guarded-build-workflow")
    add(fixture_path, "fixtures/m07-fixtures-v6.json", "fixture-proof")
    add(replay_path, "fixtures/m07-editor-replay-v6.json", "independent-editor-replay")
    add(on_path, "players/m07-native-on-build-v6.json", "actual-player-build")
    add(off_path, "players/m07-native-off-build-v6.json", "actual-player-build")
    add(baseline_manifest, "resources/m07-baseline-manifest-v6.json", "frozen-resource-build")
    add(RESOURCE_ROOT / "resource-build-receipt.json", "resources/m07-resource-build-v6.json", "resource-build-proof")
    add(RESOURCE_ROOT / "resource-abi.json", "resources/m07-resource-abi-v6.json", "resource-abi-proof")
    add(launches_path, "verification/m07-player-launches-v6.json", "actual-player-launches")
    add(strict_path, "verification/m07-strict-gate-3b-v6.json", "strict-runtime-verification")
    add(closeout_path, "verification/m07-closeout-v6.json", "fresh-closeout-verification")
    add(editor_xml, "verification/editor-tests-v6.xml", "fresh-editor-suite")
    add(editor_log, "verification/editor-tests-v6.unity.log", "fresh-editor-suite")
    add(python_path, "verification/python-tests-v6.log", "fresh-python-suite")
    add(native_path, "verification/native-tests-v6.json", "fresh-native-suite")
    add(installed_path, "verification/installed-source-v6.json", "pinned-installation")
    add(install_receipt, "verification/install-receipt-v6.json", "pinned-installation")
    add(install_repeatability, "verification/install-repeatability-v6.json", "pinned-installation")
    add(pins_path, "source/current-source-pins.json", "source-identity")
    copies = copy_artifacts(destination, copies)

    script_path = Path(__file__).resolve(strict=True)
    index = {
        "schemaVersion": 1,
        "milestone": "M07",
        "kind": "LosslessEvidenceRetention",
        "runtimeAcceptance": False,
        "recordedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        **context,
        "strictReceipt": {"originalPath": str(strict_path), "sha256": sha256(strict_path), "caseCount": 14, "gate": "Gate 3B"},
        "closeoutReceipt": {"originalPath": str(closeout_path), "sha256": sha256(closeout_path)},
        "archiveTool": {"path": str(script_path), "sha256": sha256(script_path)},
        "archives": archives,
        "copiedArtifacts": copies,
        "allCopiedBytesMatch": True,
        "limitation": "Byte-identical retention, not authentication or portable deployment. Player apps and compiler workspaces remain in their original immutable local roots; the archive retains their hash-bound receipts, full app-tree before/after hashes, raw process results and the complete M07 resource evidence roots.",
    }
    index_path = destination / "artifact-index-v6.json"
    write_json_new(index_path, index)
    print(json.dumps({"success": True, "archives": len(archives), "archivedFiles": sum(row["fileCount"] for row in archives), "copiedArtifacts": len(copies), "artifactIndex": str(index_path), "artifactIndexSha256": sha256(index_path)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    arguments = parser.parse_args()
    main(arguments.project_root)
