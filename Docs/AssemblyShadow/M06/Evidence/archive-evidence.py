#!/usr/bin/env python3
"""Retain the final M06 evidence without mutating any acceptance input."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
import stat
import shutil
import tarfile
from pathlib import Path, PurePosixPath


DEMO_EXECUTABLE_REVISION = "e1ab1ca512dfd12642c333094d884808ff757fc9"
DEMO_PIN_REVISION = "1311e7c5fb9da4769260529bb561661aa335b198"
RUNTIME_REVISION = "a19db144751f4f016769b90e61a80b8c27578678"
NATIVE_REVISION = "5b12ee96e574999d0eb82a6200d95a5b63c7fcfc"
PACKAGE_REVISION = "8d2e811fb37f4427ea15321369c883a61975a57d"
DEVELOPMENT_BASELINE = "M06-Baseline-v8"
RELEASE_BASELINE = "M06-Baseline-Release-v8"
PLAN_IDS = ("Ordinary", "P01", "P02", "P03", "InitializerFailure")
MODES = tuple(
    [
        f"T06-{number:02d}-{word}-{patch}"
        for number, word in ((1, "New"), (2, "Statics"))
        for patch in ("P01", "P02", "P03")
    ]
    + ["T06-03-P01", "T06-04-P02", "T06-05-P03"]
    + [
        f"T06-{number:02d}-{word}-{patch}"
        for number, word in ((6, "Delegates"), (7, "Generics"), (8, "Async"))
        for patch in ("P01", "P02", "P03")
    ]
    + ["T06-09-InitializerFailure", "T06-09-BaselineRecovery"]
    + [f"T06-10-Warmup-{patch}" for patch in ("P01", "P02", "P03")]
    + ["T06-11-FeatureOff"]
    + [f"T06-12-NoWarmup-{patch}" for patch in ("P01", "P02", "P03")]
    + ["T06-13-ReleaseNoPdb"]
)


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def digest_stream(stream) -> str:
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(block)
    return value.hexdigest()


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing, non-file or symlink input: " + str(path))
    with path.open("rb") as stream:
        return digest_stream(stream)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def safe_name(name: str) -> None:
    path = PurePosixPath(name)
    require(
        name != "" and not path.is_absolute() and ".." not in path.parts and str(path) == name,
        "Unsafe or noncanonical archive/copy name: " + name,
    )


def canonical_file(root: Path, path: Path) -> Path:
    require(path.is_absolute(), "Absolute input required: " + str(path))
    resolved = path.resolve(strict=True)
    require(path == resolved and resolved.is_relative_to(root), "Input escapes or aliases the project: " + str(path))
    require(resolved.is_file() and not resolved.is_symlink(), "Regular input required: " + str(path))
    return resolved


def canonical_directory(root: Path, path: Path) -> Path:
    require(path.is_absolute(), "Absolute directory required: " + str(path))
    resolved = path.resolve(strict=True)
    require(path == resolved and resolved.is_relative_to(root), "Directory escapes or aliases the project: " + str(path))
    require(resolved.is_dir() and not resolved.is_symlink(), "Regular directory required: " + str(path))
    return resolved


def write_json_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def file_entry(source: Path, name: str, category: str = "") -> dict:
    safe_name(name)
    return {
        "originalPath": str(source),
        "name": name,
        "category": category,
        "size": source.stat().st_size,
        "sha256": sha256(source),
        "executable": bool(source.stat().st_mode & stat.S_IXUSR),
    }


def collect_tree(root: Path, prefix: str, category: str) -> list[dict]:
    safe_name(prefix)
    entries = []
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "Symlink in retained tree: " + str(path))
        if path.is_dir():
            continue
        entries.append(file_entry(path, prefix + "/" + path.relative_to(root).as_posix(), category))
    require(entries, "Empty retained tree: " + str(root))
    return entries


def generation_paths(root: Path, prefix: str) -> list[dict]:
    relative = ["m06-generation.json", "m06-baseline-selection.json", "Common/AssemblyManifest.cpp", "Common/UnityVersion.h"]
    for plan in PLAN_IDS:
        relative.extend(
            [
                f"{plan}/Plan/generation-plan.json",
                f"{plan}/Plan/policy.json",
                f"{plan}/Plan/Snapshot/assembly-snapshot.json",
                f"{plan}/Plan/Snapshot/compiler-mode.json",
                f"{plan}/Plan/Snapshot/RawTypeAdmissions/configuration.json",
                f"{plan}/Plan/Snapshot/RawTypeAdmissions/compiled-evidence.json",
                f"{plan}/Plan/Snapshot/ReflectionBindings/configuration.json",
                f"{plan}/Compile/Snapshot/assembly-snapshot.json",
                f"{plan}/Compile/Snapshot/compiler-mode.json",
                f"{plan}/Compile/Snapshot/RawTypeAdmissions/configuration.json",
                f"{plan}/Compile/Snapshot/RawTypeAdmissions/compiled-evidence.json",
                f"{plan}/Compile/Snapshot/ReflectionBindings/configuration.json",
                f"{plan}/AotInputs/generation-aot-inputs.json",
                f"{plan}/Generated/AOTGenericReferences.cs",
                f"{plan}/Generated/AOTGenericReferences.cs.generation.json",
                f"{plan}/Generated/MethodBridge.cpp",
                f"{plan}/Generated/MethodBridge.cpp.generation.json",
                f"{plan}/Generated/link.xml",
                f"{plan}/Generated/link.xml.generation.json",
                f"{plan}/StartupAssets/0000-M06BootstrapRunner.cs",
                f"{plan}/StartupAssets/0001-M06BootstrapRunner.cs.meta",
                f"{plan}/StartupAssets/0002-M06Bootstrap.unity",
                f"{plan}/StartupAssets/0003-M06Bootstrap.unity.meta",
                f"{plan}/execution-policy.json",
            ]
        )
    require(len(relative) == len(set(relative)), "Duplicate generation retention path")
    entries = []
    for name in sorted(relative):
        source = root / name
        require(source.is_file() and not source.is_symlink(), "Missing generation evidence: " + str(source))
        entries.append(file_entry(source, prefix + "/" + name, "generation-proof"))
    return entries


def player_input_paths(root: Path, prefix: str) -> list[dict]:
    relative = (
        "LinkedPlayer/linked-player-receipt.json",
        "RawTypeAdmissions/compiled-evidence.json",
        "RawTypeAdmissions/configuration.json",
        "RawTypeAdmissions/linked-evidence.json",
        "ReflectionBindings/LinkedRetargeting/evidence.json",
        "ReflectionBindings/LinkedRetargeting/netstandard.dll.bytes",
        "ReflectionBindings/configuration.json",
        "assembly-snapshot.json",
        "m06-execution-policy.json",
        "m06-execution-proof.json",
        "m06-placeholder-AssemblyManifest.cpp",
        "m06-player-build.json",
        "m06-type-proof.json",
    )
    entries = []
    for name in relative:
        source = root / name
        require(source.is_file() and not source.is_symlink(), "Missing Player-input proof: " + str(source))
        entries.append(file_entry(source, prefix + "/" + name, "player-input-proof"))
    return entries


def archive_entries(destination: Path, name: str, entries: list[dict], milestone_context: dict) -> dict:
    safe_name(name)
    require(entries and len({entry["name"] for entry in entries}) == len(entries), "Empty/duplicate archive inventory")
    entries = sorted(entries, key=lambda item: item["name"])
    archive_path = destination / name
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for entry in entries:
                    source = Path(entry["originalPath"])
                    require(sha256(source) == entry["sha256"], "Archive input changed before read: " + str(source))
                    info = tarfile.TarInfo(entry["name"])
                    info.size = entry["size"]
                    info.mode = 0o755 if entry["executable"] else 0o644
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with source.open("rb") as stream:
                        archive.addfile(info, stream)

    expected = {entry["name"]: entry for entry in entries}
    seen = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            require(member.isfile() and member.name in expected and member.name not in seen, "Unexpected archive member")
            entry = expected[member.name]
            require(
                member.size == entry["size"]
                and member.mtime == 0
                and member.uid == 0
                and member.gid == 0,
                "Non-normalized archive metadata: " + member.name,
            )
            stream = archive.extractfile(member)
            require(stream is not None and digest_stream(stream) == entry["sha256"], "Archived bytes differ: " + member.name)
            seen.add(member.name)
    require(seen == set(expected), "Incomplete archive: " + name)
    for entry in entries:
        require(sha256(Path(entry["originalPath"])) == entry["sha256"], "Original changed after archive: " + entry["originalPath"])

    index_path = destination / (name.removesuffix(".tar.gz") + ".index.json")
    index = {
        "schemaVersion": 1,
        "milestone": "M06",
        "kind": "DeterministicLosslessArchive",
        **milestone_context,
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


def validate_generation(path: Path, baseline: str, development: bool) -> tuple[dict, Path]:
    value = read_json(path)
    require(
        value.get("schemaVersion") == 1
        and value.get("milestone") == "M06"
        and value.get("baselineBuildId") == baseline
        and value.get("developmentBuild") is development
        and value.get("selectedPlanId") == "P03",
        "Wrong generation context: " + str(path),
    )
    require(value.get("sourcePins", {}).get("demo", {}).get("revision") == DEMO_EXECUTABLE_REVISION, "Wrong demo build pin")
    return value, path.parent


def validate_fixture(path: Path, baseline: str, development: bool, generation: Path) -> tuple[dict, Path]:
    value = read_json(path)
    require(
        value.get("schemaVersion") == 1
        and value.get("milestone") == "M06"
        and value.get("baselineBuildId") == baseline
        and value.get("developmentBuild") is development
        and value.get("generationProofPath") == str(generation),
        "Wrong fixture context: " + str(path),
    )
    require(sha256(generation) == value.get("generationProofSha256"), "Fixture generation hash mismatch")
    require([row.get("patchId") for row in value.get("fixtures", [])] == ["P01", "P02", "P03"], "Wrong fixture inventory")
    require(value.get("initializerFailureFixture", {}).get("patchId") == "InitializerFailure", "Missing initializer fixture")
    replay = path.parent / "m06-editor-replay.json"
    require(replay.is_file() and not replay.is_symlink(), "Missing canonical independent replay: " + str(replay))
    replay_value = read_json(replay)
    require(replay_value.get("result") == "Passed" and replay_value.get("developmentBuild") is development, "Failed/wrong replay")
    return value, replay


def validate_player(path: Path, baseline: str, variant: str, development: bool, generation: Path) -> tuple[dict, Path]:
    value = read_json(path)
    require(
        value.get("schemaVersion") == 1
        and value.get("milestone") == "M06"
        and value.get("baselineBuildId") == baseline
        and value.get("variant") == variant
        and value.get("developmentBuild") is development
        and value.get("generationProofPath") == str(generation),
        "Wrong Player receipt context: " + str(path),
    )
    require(sha256(generation) == value.get("generationProofSha256"), "Player generation hash mismatch")
    for path_field, hash_field in (
        ("nativeLibraryPath", "nativeLibrarySha256"),
        ("nativeMetadataPath", "nativeMetadataSha256"),
        ("placeholderManifestPath", "placeholderManifestSha256"),
        ("typeProofPath", "typeProofSha256"),
        ("executionProofPath", "executionProofSha256"),
    ):
        source = Path(value[path_field])
        require(source.is_file() and not source.is_symlink() and sha256(source) == value[hash_field], "Player bound input mismatch")
    return value, path.parent


def validate_launches(player_root: Path) -> dict:
    receipt_path = player_root / "player-launches.json"
    receipt = read_json(receipt_path)
    launches = receipt.get("processLaunches")
    require(
        receipt.get("schemaVersion") == 1
        and receipt.get("milestone") == "M06"
        and receipt.get("diagnosticOnly") is True
        and receipt.get("fullModeInventory") == list(MODES)
        and receipt.get("requestedModes") == list(MODES)
        and receipt.get("completedModes") == 28
        and type(launches) is list
        and len(launches) == 28,
        "Incomplete Player launch inventory",
    )
    require(receipt.get("inputsUnchanged") is True and receipt.get("inputHashesBefore") == receipt.get("inputHashesAfter"), "Player inputs changed")
    require({row.get("mode") for row in launches} == set(MODES), "Wrong Player mode set")
    require(len({row.get("processId") for row in launches}) == 28, "Player cases reused a process")
    for row in launches:
        require(row.get("passed") is True and row.get("exitCode") == 0 and row.get("timedOut") is False, "Failed Player launch")
        result = Path(row["resultPath"])
        require(result.is_relative_to(player_root) and sha256(result) == row.get("resultSha256"), "Changed Player result")
        payload = read_json(result)
        require(payload.get("mode") == row.get("mode") and payload.get("processId") == row.get("processId"), "Player identity mismatch")
        for field in ("unityLogPath", "consoleLogPath"):
            log = Path(row[field])
            require(log.is_relative_to(player_root) and log.is_file() and not log.is_symlink(), "Missing Player log")
    return receipt


def copy_artifacts(destination: Path, plan: list[dict]) -> list[dict]:
    require(len({entry["name"] for entry in plan}) == len(plan), "Duplicate copy target")
    for entry in plan:
        source = Path(entry["originalPath"])
        target = destination / entry["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
        require(
            target.stat().st_size == entry["size"]
            and sha256(target) == entry["sha256"]
            and sha256(source) == entry["sha256"],
            "Copied/original bytes changed: " + entry["name"],
        )
        entry["path"] = str(target)
    return plan


def main(project: Path) -> None:
    project = project.resolve(strict=True)
    require(project == Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow"), "This receipt is bound to the isolated M06 project")
    destination = project / "Docs/AssemblyShadow/M06/Evidence"
    require(destination.is_dir() and not destination.is_symlink(), "M06 Evidence directory is missing/aliased")
    expected_outputs = (
        "player-results-v8.tar.gz",
        "fixtures-v8.tar.gz",
        "generation-proofs-v8.tar.gz",
        "player-input-proofs-v8.tar.gz",
        "closeout-validation-v8.tar.gz",
        "artifact-index-v8.json",
    )
    require(not any((destination / name).exists() for name in expected_outputs), "M06 retention output already exists")

    temporary = project / "_temp/AssemblyShadow"
    continuation_path = canonical_file(project, temporary / "m06-v8-continuation.json")
    continuation = read_json(continuation_path)
    require(continuation.get("result") == "Passed", "M06 v8 continuation did not pass")

    def continued(path_field: str, hash_field: str) -> Path:
        path = canonical_file(project, Path(continuation[path_field]))
        require(sha256(path) == continuation[hash_field], "Continuation-bound input changed: " + path_field)
        return path

    development_generation_path = continued("developmentGeneration", "developmentGenerationSha256")
    release_generation_path = continued("releaseGeneration", "releaseGenerationSha256")
    development_fixture_path = continued("developmentFixtureManifest", "developmentFixtureManifestSha256")
    development_on_path = continued("developmentOn", "developmentOnSha256")
    development_off_path = continued("developmentOff", "developmentOffSha256")
    release_player_path = continued("releasePlayer", "releasePlayerSha256")
    player_root = canonical_directory(project, Path(continuation["resultRoot"]))
    strict_path = continued("strictReceipt", "strictReceiptSha256")
    closeout_path = canonical_file(project, temporary / "m06-closeout-validation-v8.json")

    _, development_generation_root = validate_generation(development_generation_path, DEVELOPMENT_BASELINE, True)
    _, release_generation_root = validate_generation(release_generation_path, RELEASE_BASELINE, False)
    development_fixture, development_replay = validate_fixture(
        development_fixture_path, DEVELOPMENT_BASELINE, True, development_generation_path
    )
    release_fixture_path = continued("releaseFixtureManifest", "releaseFixtureManifestSha256")
    require(sha256(release_fixture_path) == continuation.get("releaseFixtureManifestSha256"), "Release fixture changed")
    release_fixture, release_replay = validate_fixture(release_fixture_path, RELEASE_BASELINE, False, release_generation_path)
    require(str(release_replay) == continuation.get("releaseReplay") and sha256(release_replay) == continuation.get("releaseReplaySha256"), "Release replay changed")
    require(str(player_root) == continuation.get("resultRoot"), "Continuation Player root mismatch")
    require(str(strict_path) == continuation.get("strictReceipt") and sha256(strict_path) == continuation.get("strictReceiptSha256"), "Strict receipt mismatch")

    development_on, development_on_root = validate_player(
        development_on_path, DEVELOPMENT_BASELINE, "NativeOn", True, development_generation_path
    )
    development_off, development_off_root = validate_player(
        development_off_path, DEVELOPMENT_BASELINE, "NativeOff", True, development_generation_path
    )
    release_player, release_player_root = validate_player(
        release_player_path, RELEASE_BASELINE, "NativeOn", False, release_generation_path
    )
    require(len({row["buildGuid"] for row in (development_on, development_off, release_player)}) == 3, "Player GUIDs are not distinct")
    require(len({row["nativeLibrarySha256"] for row in (development_on, development_off, release_player)}) == 3, "Player native binaries are not distinct")

    launches = validate_launches(player_root)
    strict = read_json(strict_path)
    require(strict.get("schemaVersion") == 1 and strict.get("milestone") == "M06" and strict.get("result") == "Passed" and strict.get("caseCount") == 28, "Strict verifier did not pass 28 cases")
    require(strict.get("fixtureManifestSha256") == sha256(development_fixture_path), "Strict Development fixture mismatch")
    require(strict.get("releaseFixtureManifestSha256") == sha256(release_fixture_path), "Strict Release fixture mismatch")
    require({row.get("processId") for row in strict.get("results", [])} == {row.get("processId") for row in launches["processLaunches"]}, "Strict/launch PID inventory differs")

    closeout = read_json(closeout_path)
    require(closeout.get("schemaVersion") == 1 and closeout.get("milestone") == "M06" and closeout.get("result") == "Passed", "Closeout validation did not pass")
    require(closeout.get("upstreamStatePath") == str(continuation_path) and closeout.get("upstreamStateSha256") == sha256(continuation_path), "Closeout upstream mismatch")
    closeout_root = canonical_directory(project, Path(closeout["python"]["logPath"]).parent)
    require(closeout_root.name == "M06CloseoutValidation-v8", "Wrong closeout root")
    closeout_roots = sorted(
        {
            canonical_directory(project, Path(row["logPath"]).parent)
            for row in closeout.get("commands", [])
        }
    )
    require(closeout_root in closeout_roots and all(
        root.parent == temporary and re.fullmatch(r"M06CloseoutValidation-v8(?:-retry[1-9][0-9]*)?", root.name)
        for root in closeout_roots
    ), "Closeout command logs escaped the bounded retry roots")
    require(int(closeout["python"].get("testCount", 0)) > 0, "No Python tests recorded")
    editor = closeout.get("editor", {})
    require(
        editor.get("result") == "Passed"
        and int(editor.get("total", 0)) == int(editor.get("passed", -1))
        and all(int(editor.get(key, 0)) == 0 for key in ("failed", "skipped", "inconclusive")),
        "Editor suite was not a complete pass",
    )

    context = {
        "demoExecutableRevision": DEMO_EXECUTABLE_REVISION,
        "demoPinRevision": DEMO_PIN_REVISION,
        "runtimeRevision": RUNTIME_REVISION,
        "nativeRevision": NATIVE_REVISION,
        "packageRevision": PACKAGE_REVISION,
        "developmentBaselineBuildId": DEVELOPMENT_BASELINE,
        "releaseBaselineBuildId": RELEASE_BASELINE,
    }
    archives = []
    archives.append(archive_entries(destination, "player-results-v8.tar.gz", collect_tree(player_root, "Players", "actual-player-evidence"), context))
    fixture_entries = collect_tree(development_fixture_path.parent, "Development", "fixture-and-replay")
    fixture_entries += collect_tree(release_fixture_path.parent, "Release", "fixture-and-replay")
    archives.append(archive_entries(destination, "fixtures-v8.tar.gz", fixture_entries, context))
    generation_entries = generation_paths(development_generation_root, "Development")
    generation_entries += generation_paths(release_generation_root, "Release")
    archives.append(archive_entries(destination, "generation-proofs-v8.tar.gz", generation_entries, context))
    player_entries = player_input_paths(development_on_root, "Development-NativeOn")
    player_entries += player_input_paths(development_off_root, "Development-NativeOff")
    player_entries += player_input_paths(release_player_root, "Release-NativeOn")
    archives.append(archive_entries(destination, "player-input-proofs-v8.tar.gz", player_entries, context))
    closeout_entries = []
    for root in closeout_roots:
        closeout_entries += collect_tree(root, "Closeout/" + root.name, "fresh-full-suite-evidence")
    archives.append(archive_entries(destination, "closeout-validation-v8.tar.gz", closeout_entries, context))

    copies: list[dict] = []

    def add(source: Path, name: str, category: str) -> None:
        source = canonical_file(project, source)
        copies.append(file_entry(source, name, category))

    add(Path(development_fixture["baselineManifestPath"]), "baselines/development-baseline-manifest-v8.json", "frozen-build")
    add(Path(release_fixture["baselineManifestPath"]), "baselines/release-baseline-manifest-v8.json", "frozen-build")
    add(development_generation_path, "generation/development-generation-v8.json", "generation-proof")
    add(release_generation_path, "generation/release-generation-v8.json", "generation-proof")
    add(development_fixture_path, "fixtures/development-fixtures-v8.json", "fixture-proof")
    add(development_replay, "fixtures/development-editor-replay-v8.json", "independent-editor-replay")
    add(release_fixture_path, "fixtures/release-fixtures-v8.json", "fixture-proof")
    add(release_replay, "fixtures/release-editor-replay-v8.json", "independent-editor-replay")
    add(development_on_path, "players/development-native-on-build-v8.json", "actual-player-build")
    add(development_off_path, "players/development-native-off-build-v8.json", "actual-player-build")
    add(release_player_path, "players/release-native-on-build-v8.json", "actual-player-build")
    add(strict_path, "verification/m06-strict-28-case-v8.json", "strict-runtime-verification")
    add(continuation_path, "verification/release-continuation-v8.json", "guarded-continuation")
    add(closeout_path, "verification/closeout-validation-v8.json", "fresh-full-suite-verification")
    add(Path(closeout["installReceipt"]["path"]), "verification/install-receipt-v8.json", "pinned-installation")
    add(Path(closeout["installRepeatability"]["path"]), "verification/install-repeatability-v8.json", "pinned-installation")
    add(Path(editor["resultsPath"]), "verification/editor-tests-v8.xml", "fresh-editor-suite")
    add(Path(editor["unityLogPath"]), "verification/editor-tests-v8.unity.log", "fresh-editor-suite")
    add(Path(closeout["python"]["logPath"]), "verification/python-tests-v8.log", "fresh-python-suite")
    for row in closeout.get("nativeReceipts", []):
        require(row.get("name") in {"m03", "visibility", "m04", "m05", "m06"}, "Unknown native suite")
        source = Path(row["path"])
        require(sha256(source) == row.get("sha256"), "Native receipt changed")
        add(source, "verification/native/" + row["name"] + "-native-tests-v8.json", "fresh-native-suite")
    add(project / "ProjectSettings/AssemblyShadowSourcePins.json", "source/current-source-pins.json", "source-identity")
    add(project / "ProjectSettings/AssemblyShadowRawTypeAdmissions.json", "source/raw-type-admission-configuration.json", "source-policy")

    # These three phases precede the guarded continuation receipt. Every later
    # wrapper and Unity log is discovered from that receipt instead of relying
    # on a timestamp or generated GUID.
    for name in ("UnityExec_20260905_055525.log", "UnityExec_20260905_083358.log", "UnityExec_20260905_122312.log"):
        add(project / "_temp" / name, "build-logs/" + name, "guarded-unity-build-log")
    for row in continuation.get("commands", []):
        require(type(row) is dict and row.get("name"), "Malformed continuation command evidence")
        for field, prefix, category in (
            ("logPath", "task-local/continuation-", "task-local-orchestration"),
            ("unityLogPath", "build-logs/", "guarded-unity-build-log"),
        ):
            value = row.get(field)
            if value:
                source = Path(value)
                target = prefix + (source.name if field == "unityLogPath" else row["name"] + ".log")
                add(source, target, category)
    for row in closeout.get("commands", []):
        require(type(row) is dict and row.get("name"), "Malformed closeout command evidence")
        for unity_log in row.get("unityLogs", []):
            source = Path(unity_log["path"])
            require(sha256(source) == unity_log["sha256"], "Closeout Unity log changed")
            add(source, "build-logs/" + source.name, "guarded-unity-build-log")
    for name in (
        "Run-M06DevelopmentFixtures-v8.ps1",
        "Run-M06DevelopmentGeneration-v8.ps1",
        "Run-M06DevelopmentNativeOff-v8.ps1",
        "Run-M06DevelopmentPlayer-v8.ps1",
        "Run-M06EditorReplay-v8.ps1",
        "Run-M06ReleaseFixtures-v8.ps1",
        "Run-M06ReleaseGeneration-v8.ps1",
        "Run-M06ReleasePlayer-v8.ps1",
        "continue-m06-v8.py",
        "closeout-m06-v8.py",
    ):
        add(project / "_temp" / name, "task-local/" + name, "task-local-orchestration")
    for name in ("m06-capture-run-players.py", "m06-v8-continuation.json", "m06-closeout-validation-v8.json"):
        add(temporary / name, "task-local/" + name, "task-local-orchestration")

    copies = copy_artifacts(destination, copies)
    script_path = Path(__file__).resolve(strict=True)
    require(script_path == destination / "archive-evidence.py", "Archive tool location changed")
    index = {
        "schemaVersion": 1,
        "milestone": "M06",
        "kind": "LosslessEvidenceRetention",
        "runtimeAcceptance": False,
        "recordedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        **context,
        "strictReceipt": {"originalPath": str(strict_path), "sha256": sha256(strict_path), "caseCount": 28},
        "closeoutReceipt": {"originalPath": str(closeout_path), "sha256": sha256(closeout_path)},
        "archiveTool": {"path": str(script_path), "sha256": sha256(script_path)},
        "archives": archives,
        "copiedArtifacts": copies,
        "allCopiedBytesMatch": True,
        "limitation": (
            "Byte-identical retention, not relocated acceptance inputs, authentication or a portable deployment. "
            "Canonical DLL/PDB/native/metadata/snapshot graphs and Player apps remain in their original immutable local roots. "
            "The generation archives retain complete plan/output receipts and generated outputs but intentionally exclude reproducible multi-gigabyte compiler/IL2CPP workspaces. Independent full gates are still required."
        ),
    }
    index_path = destination / "artifact-index-v8.json"
    write_json_new(index_path, index)
    print(
        json.dumps(
            {
                "success": True,
                "archives": len(archives),
                "archivedFiles": sum(row["fileCount"] for row in archives),
                "copiedArtifacts": len(copies),
                "artifactIndex": str(index_path),
                "artifactIndexSha256": sha256(index_path),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    arguments = parser.parse_args()
    main(arguments.project_root)
