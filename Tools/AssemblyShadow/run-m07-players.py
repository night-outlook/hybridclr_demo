#!/usr/bin/env python3
"""Launch each M07 acceptance mode in a fresh owned Player process."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import subprocess
import sys
import time
from pathlib import Path

MODES = (
    "T07-01-Prefab-P01", "T07-02-Nested-P02", "T07-03-FullClosure-P03",
    "T07-04-UnityApis-P01", "T07-05-Scriptable-P03",
    "T07-06-SceneSingle-P01", "T07-07-SceneAdditive-P03",
    "T07-08-SerializeReference-P03", "T07-09-Messages-P01",
    "T07-10-Cache-P03", "T07-11-DelayedCatalog-P03",
    "T07-12-P04-NonSerialized", "T07-13-P05-Rebuilt",
    "T07-14-FeatureOff",
)
OFF_MODES = frozenset(("T07-14-FeatureOff",))


def require(value: object, message: str) -> None:
    if not value:
        raise ValueError(message)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Expected regular input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_file(value: str | Path) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_file(),
            "Expected an existing canonical absolute file: " + str(value))
    return path


def canonical_new_child(value: Path, parent: Path, label: str) -> Path:
    require(value.is_absolute() and value == value.resolve() and not value.exists() and not value.is_symlink(),
            label + " must be a new canonical absolute path")
    value.relative_to(parent)
    require(not parent.is_symlink(), label + " parent must not be a symlink")
    return value


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected a JSON object: " + str(path))
    return value


def executable_for(app: Path) -> Path:
    require(app.is_dir() and app.suffix == ".app" and not app.is_symlink(), "Expected a macOS Player app: " + str(app))
    with (app / "Contents/Info.plist").open("rb") as stream:
        executable_name = plistlib.load(stream)["CFBundleExecutable"]
    require(Path(executable_name).name == executable_name, "Invalid Player executable name")
    return canonical_file(app / "Contents/MacOS" / executable_name)


def collect_tree(files: set[Path], root: Path) -> None:
    require(root.is_absolute() and root == root.resolve(strict=True) and root.is_dir() and not root.is_symlink(),
            "Expected canonical immutable artifact directory: " + str(root))
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink in immutable artifact graph: " + str(path))
        if path.is_file():
            files.add(path.resolve(strict=True))


def collect_inputs(manifest_path: Path, replay_path: Path | None, builds: tuple[Path, Path]) -> set[Path]:
    manifest = read_object(manifest_path)
    files = {manifest_path}
    if replay_path is not None:
        files.add(replay_path)
        replay = read_object(replay_path)
        collect_tree(files, Path(replay["replayScratchPath"]))
    baseline_manifest = canonical_file(manifest["baselineManifestPath"])
    files.add(baseline_manifest)
    baseline = read_object(baseline_manifest)
    baseline_root = baseline_manifest.parent
    collect_tree(files, baseline_root / baseline["resourceBaselinePath"])
    collect_tree(files, baseline_root / baseline["playerInputSnapshot"])
    collect_tree(files, Path(manifest["baselineInputSnapshot"]))
    for fixture in manifest["fixtures"]:
        collect_tree(files, Path(fixture["compileSnapshot"]))
        collect_tree(files, Path(fixture["patchDirectory"]))
        if fixture["replacementResourcePath"]:
            collect_tree(files, Path(fixture["replacementResourcePath"]))
    for rejected in manifest["rejectedFixtures"]:
        collect_tree(files, Path(rejected["compileSnapshot"]))
    for receipt_path in builds:
        files.add(receipt_path)
        receipt = read_object(receipt_path)
        app = Path(receipt["playerOutput"])
        require(app.is_absolute() and app == app.resolve(strict=True), "Player output path is aliased: " + str(app))
        executable_for(app)
        collect_tree(files, app)
        for field in ("nativeLibraryPath", "nativeMetadataPath", "placeholderManifestPath", "resourceBuildReceiptPath"):
            files.add(canonical_file(receipt[field]))
        collect_tree(files, Path(receipt["resourceBaselinePath"]))
    return files


def load_build(project: Path, path: Path, variant: str, baseline: str) -> tuple[Path, str]:
    receipt = read_object(path)
    require(receipt.get("schemaVersion") == 1 and receipt.get("milestone") == "M07" and
            receipt.get("variant") == variant and receipt.get("baselineBuildId") == baseline,
            "Wrong M07 Player receipt: " + str(path))
    app = Path(receipt["playerOutput"])
    require(app.is_absolute() and app == app.resolve(strict=True), "Player output path is aliased: " + str(app))
    app.relative_to(project / "Builds/AssemblyShadow/M07")
    executable = executable_for(app)
    for path_field, hash_field in (("nativeLibraryPath", "nativeLibrarySha256"),
                                   ("nativeMetadataPath", "nativeMetadataSha256"),
                                   ("placeholderManifestPath", "placeholderManifestSha256"),
                                   ("resourceBuildReceiptPath", "resourceBuildReceiptSha256")):
        artifact = canonical_file(receipt[path_field])
        require(digest(artifact) == receipt[hash_field], "Player receipt hash mismatch: " + str(artifact))
    return executable, receipt["buildGuid"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=canonical_file)
    parser.add_argument("--on-build", required=True, type=canonical_file)
    parser.add_argument("--off-build", required=True, type=canonical_file)
    parser.add_argument("--replay-receipt", type=canonical_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--mode", action="append", choices=MODES)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    project = args.project_root
    require(project.is_absolute() and project == project.resolve(strict=True) and project.is_dir() and not project.is_symlink(),
            "Project root must be a canonical absolute directory")
    require((project / "Assets/AssemblyShadowDemo").is_dir(), "Project is not the Assembly Shadow demo")
    output_root = canonical_new_child(args.output_root, project / "_temp/AssemblyShadow", "Output root")
    require(1 <= args.timeout <= 3600, "Use a bounded 1-3600 second timeout per owned Player")
    modes = args.mode or list(MODES)
    require(len(modes) == len(set(modes)), "Duplicate modes are not allowed")

    manifest = read_object(args.fixture_manifest)
    require(manifest.get("schemaVersion") == 1 and manifest.get("milestone") == "M07", "Wrong M07 fixture manifest")
    baseline = manifest["baselineBuildId"]
    on = load_build(project, args.on_build, "NativeOn", baseline)
    off = load_build(project, args.off_build, "NativeOff", baseline)
    immutable_inputs = collect_inputs(args.fixture_manifest, args.replay_receipt, (args.on_build, args.off_build))
    before = {str(path): digest(path) for path in sorted(immutable_inputs)}

    output_root.mkdir()
    results = output_root / "Results"
    results.mkdir()
    launches: list[dict] = []
    failed = False
    for mode in modes:
        receipt_path = args.off_build if mode in OFF_MODES else args.on_build
        executable, build_guid = off if mode in OFF_MODES else on
        result_path = results / ("m07-" + mode + ".json")
        log_path = output_root / (mode + ".unity.log")
        console_path = output_root / (mode + ".console.log")
        command = [str(executable), "-batchmode", "-nographics",
                   "-shadowM07Mode", mode, "-shadowM07Fixtures", str(args.fixture_manifest),
                   "-shadowM07PlayerReceipt", str(receipt_path),
                   "-shadowM07Result", str(result_path), "-logFile", str(log_path)]
        started = time.time()
        timed_out = False
        with console_path.open("xb") as console:
            process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                       stdout=console, stderr=subprocess.STDOUT)
            print(f"{mode} started pid={process.pid}", flush=True)
            try:
                exit_code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.terminate()
                try:
                    exit_code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    exit_code = process.wait(timeout=15)
        outcome = None
        error = ""
        if result_path.is_file():
            try:
                outcome = read_object(result_path)
            except (OSError, ValueError, json.JSONDecodeError) as problem:
                error = str(problem)
        passed = (not timed_out and exit_code == 0 and outcome is not None and
                  outcome.get("mode") == mode and outcome.get("result") == "Passed" and
                  outcome.get("processId") == process.pid and outcome.get("buildGuid") == build_guid)
        launches.append({
            "mode": mode, "command": command, "processId": process.pid,
            "startedAtUnix": started, "durationSeconds": time.time() - started,
            "exitCode": exit_code, "timedOut": timed_out, "passed": passed,
            "resultPath": str(result_path), "resultSha256": digest(result_path) if result_path.is_file() else "",
            "logPath": str(log_path), "consolePath": str(console_path),
            "error": error or (outcome or {}).get("error", "No result file"),
        })
        print(f"{mode} {'Passed' if passed else 'FAILED'} exit={exit_code}", flush=True)
        if not passed:
            failed = True
            break

    after = {str(path): digest(path) for path in sorted(immutable_inputs)}
    launch_receipt = {
        "schemaVersion": 1, "milestone": "M07", "diagnosticOnly": True,
        "fullModeInventory": list(MODES), "requestedModes": modes,
        "completedModes": len(launches), "processLaunches": launches,
        "inputHashesBefore": before, "inputHashesAfter": after,
        "inputsUnchanged": before == after, "resultDirectory": str(results),
        "note": "Launch receipt is provenance; verify-m07-results.py is the strict acceptance gate.",
    }
    with (output_root / "m07-player-launches.json").open("x", encoding="utf-8") as stream:
        json.dump(launch_receipt, stream, indent=2)
        stream.write("\n")
    return int(failed or before != after or len(launches) != len(modes))


if __name__ == "__main__":
    raise SystemExit(main())
