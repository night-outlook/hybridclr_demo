#!/usr/bin/env python3
"""Task-local M06 process capture; strict verification remains separate."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import subprocess
import sys
import time
from pathlib import Path


PROJECT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow")
MODES = tuple(
    [f"T06-{number:02d}-{word}-{patch}" for number, word in ((1, "New"), (2, "Statics")) for patch in ("P01", "P02", "P03")]
    + ["T06-03-P01", "T06-04-P02", "T06-05-P03"]
    + [f"T06-{number:02d}-{word}-{patch}" for number, word in ((6, "Delegates"), (7, "Generics"), (8, "Async")) for patch in ("P01", "P02", "P03")]
    + ["T06-09-InitializerFailure", "T06-09-BaselineRecovery"]
    + [f"T06-10-Warmup-{patch}" for patch in ("P01", "P02", "P03")]
    + ["T06-11-FeatureOff"]
    + [f"T06-12-NoWarmup-{patch}" for patch in ("P01", "P02", "P03")]
    + ["T06-13-ReleaseNoPdb"]
)
OFF_MODES = {"T06-11-FeatureOff"}
RELEASE_MODES = {"T06-13-ReleaseNoPdb"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def existing_file(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute() or str(path) != str(path.resolve(strict=True)) or not path.is_file():
        raise ValueError("Expected an existing canonical absolute file: " + value)
    return path


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if type(value) is not dict:
        raise ValueError("Expected a JSON object: " + str(path))
    return value


def load_build(receipt_path: Path, variant: str, development: bool) -> tuple[Path, str, set[Path]]:
    receipt = load_json(receipt_path)
    if (
        receipt.get("schemaVersion") != 1
        or receipt.get("milestone") != "M06"
        or receipt.get("variant") != variant
        or receipt.get("developmentBuild") is not development
    ):
        raise ValueError("Wrong M06 Player variant/mode: " + str(receipt_path))
    app = Path(receipt["playerOutput"]).resolve(strict=True)
    app.relative_to(PROJECT / "Builds" / "AssemblyShadow" / "M06")
    with (app / "Contents" / "Info.plist").open("rb") as stream:
        executable_name = plistlib.load(stream)["CFBundleExecutable"]
    if Path(executable_name).name != executable_name:
        raise ValueError("Invalid Player executable name.")
    executable = existing_file(str(app / "Contents" / "MacOS" / executable_name))
    inputs = {receipt_path, executable}
    for path_field, hash_field in (
        ("nativeLibraryPath", "nativeLibrarySha256"),
        ("nativeMetadataPath", "nativeMetadataSha256"),
        ("placeholderManifestPath", "placeholderManifestSha256"),
        ("typeProofPath", "typeProofSha256"),
        ("executionProofPath", "executionProofSha256"),
        ("generationProofPath", "generationProofSha256"),
    ):
        item = existing_file(receipt[path_field])
        if digest(item) != receipt[hash_field]:
            raise ValueError("Player receipt hash mismatch: " + str(item))
        inputs.add(item)
    return executable, receipt["buildGuid"], inputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", required=True, type=existing_file)
    parser.add_argument("--on-build", required=True, type=existing_file)
    parser.add_argument("--off-build", required=True, type=existing_file)
    parser.add_argument("--release-fixture-manifest", required=True, type=existing_file)
    parser.add_argument("--release-build", required=True, type=existing_file)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--mode", action="append", choices=MODES)
    parser.add_argument("--failed-result", type=existing_file)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 1800:
        raise ValueError("Use a bounded 1-1800 second owned-Player timeout.")
    root = args.output_root
    if not root.is_absolute() or str(root) != str(root.resolve()) or root.exists():
        raise ValueError("Process output must be a new canonical absolute directory.")
    root.relative_to(PROJECT / "_temp" / "AssemblyShadow")
    modes = args.mode or list(MODES)
    if len(set(modes)) != len(modes):
        raise ValueError("Duplicate modes are not allowed in a capture.")

    builds = {
        "on": load_build(args.on_build, "NativeOn", True),
        "off": load_build(args.off_build, "NativeOff", True),
        "release": load_build(args.release_build, "NativeOn", False),
    }
    inputs = {args.fixture_manifest, args.release_fixture_manifest}
    for _, _, paths in builds.values():
        inputs.update(paths)
    if args.failed_result:
        inputs.add(args.failed_result)
    before = {str(path): digest(path) for path in sorted(inputs)}

    root.mkdir()
    results = root / "Results"
    results.mkdir()
    launches = []
    failed = False
    initializer_result = args.failed_result
    for mode in modes:
        build_key = "release" if mode in RELEASE_MODES else "off" if mode in OFF_MODES else "on"
        receipt_path = {
            "on": args.on_build,
            "off": args.off_build,
            "release": args.release_build,
        }[build_key]
        fixture_path = args.release_fixture_manifest if build_key == "release" else args.fixture_manifest
        executable, build_guid, _ = builds[build_key]
        result_path = results / ("m06-" + mode + ".json")
        log_path = root / (mode + ".unity.log")
        command = [
            str(executable),
            "-batchmode",
            "-nographics",
            "-shadowM06Mode",
            mode,
            "-shadowM06Fixtures",
            str(fixture_path),
            "-shadowM06PlayerReceipt",
            str(receipt_path),
            "-shadowM06Result",
            str(result_path),
            "-logFile",
            str(log_path),
        ]
        if mode == "T06-09-BaselineRecovery":
            if initializer_result is None:
                raise ValueError("Baseline recovery requires the actual initializer-failure result.")
            command += ["-shadowM06FailedResult", str(initializer_result)]
        started = time.time()
        timed_out = False
        console_path = root / (mode + ".console.log")
        with console_path.open("xb") as console:
            process = subprocess.Popen(
                command,
                cwd=str(PROJECT),
                stdin=subprocess.DEVNULL,
                stdout=console,
                stderr=subprocess.STDOUT,
            )
            print(mode + " started pid=" + str(process.pid), flush=True)
            try:
                exit_code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.terminate()
                try:
                    exit_code = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    exit_code = process.wait(timeout=10)
        outcome = None
        error = ""
        if result_path.is_file():
            try:
                outcome = load_json(result_path)
            except (OSError, ValueError) as problem:
                error = str(problem)
        passed = (
            not timed_out
            and exit_code == 0
            and outcome is not None
            and outcome.get("mode") == mode
            and outcome.get("result") == "Passed"
            and outcome.get("processId") == process.pid
            and outcome.get("buildGuid") == build_guid
        )
        launches.append(
            {
                "mode": mode,
                "buildVariant": build_key,
                "command": command,
                "processId": process.pid,
                "startedAtUnix": started,
                "durationSeconds": time.time() - started,
                "exitCode": exit_code,
                "timedOut": timed_out,
                "passed": passed,
                "resultPath": str(result_path),
                "resultSha256": digest(result_path) if result_path.is_file() else "",
                "unityLogPath": str(log_path),
                "consoleLogPath": str(console_path),
                "error": error or (outcome or {}).get("error", "No result file"),
            }
        )
        print(mode + " " + ("Passed" if passed else "FAILED") + " exit=" + str(exit_code), flush=True)
        if mode == "T06-09-InitializerFailure" and passed:
            initializer_result = result_path
        if not passed:
            failed = True
            break

    after = {str(path): digest(path) for path in sorted(inputs)}
    inputs_unchanged = before == after
    capture = {
        "schemaVersion": 1,
        "milestone": "M06",
        "diagnosticOnly": True,
        "fullModeInventory": list(MODES),
        "requestedModes": modes,
        "completedModes": len(launches),
        "processLaunches": launches,
        "inputHashesBefore": before,
        "inputHashesAfter": after,
        "inputsUnchanged": inputs_unchanged,
        "resultDirectory": str(results),
        "note": "Launch capture is not the strict M06 acceptance gate.",
    }
    with (root / "player-launches.json").open("x", encoding="utf-8") as stream:
        json.dump(capture, stream, indent=2)
        stream.write("\n")
    return int(failed or not inputs_unchanged)


if __name__ == "__main__":
    raise SystemExit(main())
