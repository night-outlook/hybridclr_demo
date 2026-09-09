#!/usr/bin/env python3
"""Run and strictly verify the bounded R01B lazy-path IL2CPP Player case."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import time

import m07_results
from m04_metadata import read_identity
from m05_types import CliTables
from r01b_diagnostic_inputs import verify_diagnostic_inputs
from r01b_capacity_inputs import canonical_directory, canonical_file, digest, executable_for
from shadow_tools import read_json, require


HERE = Path(__file__).resolve().parent
LAZY_SOURCE = HERE / "r01b-lazy-fixture.cs"
LAZY_LAUNCHER = HERE / "create-r01b-lazy-fixture.py"
IDENTITY_READER = HERE / "m04_metadata.py"
MONO = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge/bin/mono")
COMPILER = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge/bin/mcs")
CECIL = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge/lib/mono/net_4_x-macos/Mono.Cecil.dll")
LAZY_NAME = "AssemblyShadow.R01BLazyFixture"
LAZY_VERSION = "1.0.0.1"
IMAGE_COUNT = 8192
USABLE_PAGES = 524287
MVID_FIELDS = ("name", "fullName", "version", "mvid")

LAZY_RECEIPT_FIELDS = frozenset(("schemaVersion", "kind", "milestone", "result", "createdAtUtc", "assembly", "generator", "verification"))
LAZY_ASSEMBLY_FIELDS = frozenset(("name", "version", "path", "sha256", "mvid", "fullName", "sizeBytes"))
LAZY_GENERATOR_FIELDS = frozenset(("sourcePath", "sourceSha256", "launcherPath", "launcherSha256", "monoPath", "monoSha256",
                                   "monoVersion", "compilerPath", "compilerSha256", "compilerVersion", "cecilPath", "cecilSha256",
                                   "compileCommand", "generateCommands", "inputHashesBefore", "inputHashesAfter", "inputsUnchanged",
                                   "reproducibleTwoRunSha256"))
LAZY_VERIFICATION_FIELDS = frozenset(("identityReader", "identityReaderSha256", "independentPeIdentity", "note"))
DENSE_FIELDS = frozenset(("fixtures", "kind", "parser", "schemaVersion", "sourceCorpus", "status"))
DENSE_SOURCE_FIELDS = frozenset(("manifestSha256", "note", "path", "reparseSha256"))
DENSE_PARSER_FIELDS = frozenset(("identity", "tables"))
DENSE_ROW_FIELDS = frozenset(("id", "methodDefRows", "mvid", "name", "path", "sha256", "sizeBytes", "stringsHeapBytes", "typeDefRows", "typeInventoryCount"))
RESULT_FIELDS = frozenset(("schemaVersion", "processId", "passedChecks", "failedAttributeAttempts", "malformedAttributeAttempts", "malformedConstructorCalls", "denseFixtures", "denseBoundaryChecks",
                           "fixtureBytes", "kind", "milestone", "result", "error", "baselineBuildId", "runtimeAbiHash", "unityVersion",
                           "platform", "buildGuid", "resultPath", "fixturePath", "fixtureSha256", "assemblyName", "assemblyFullName", "il2cpp",
                           "checks", "capacitySnapshots", "retryExceptions"))
CHECK_FIELDS = frozenset(("name", "detail", "passed"))
SNAPSHOT_FIELDS = frozenset(("phase", "reservedPages", "mappedPages", "lifetimeReservedImageCount", "remainingImageCount",
                             "ordinaryAllocatedCount", "shadowAllocatedCount", "reservedShadowImageCount", "aggregateInputDllBytes"))
LAUNCH_FIELDS = frozenset(("schemaVersion", "kind", "milestone", "diagnosticOnly", "projectRoot", "fixtureManifestPath", "fixtureManifestSha256",
                           "onBuildPath", "onBuildSha256", "offBuildPath", "offBuildSha256", "diagnosticBuildPath", "diagnosticBuildSha256", "replayReceiptPath", "replayReceiptSha256",
                           "lazyFixtureReceiptPath", "lazyFixtureReceiptSha256", "lazyFixturePath", "lazyFixtureSha256", "denseManifestPath",
                           "denseManifestSha256", "denseFixturePaths", "denseFixtureSha256", "playerOutput", "playerExecutable", "command", "processId",
                           "startedAtUnix", "durationSeconds", "exitCode", "timedOut", "passed", "resultPath", "resultSha256", "unityLogPath",
                           "unityLogSha256", "consoleLogPath", "consoleLogSha256", "inputHashesBefore", "inputHashesAfter", "inputsUnchanged", "error", "note"))


def exact(value: object, fields: frozenset[str], label: str) -> dict:
    require(type(value) is dict and set(value) == fields, label + ": object inventory differs")
    return value


def strict_hash(value: object, label: str) -> None:
    require(type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value),
            label + ": invalid SHA256")


def verify_lazy_receipt(receipt_path: Path) -> tuple[dict, Path, set[Path]]:
    receipt = exact(read_json(receipt_path), LAZY_RECEIPT_FIELDS, "lazy receipt")
    require(receipt["schemaVersion"] == 1 and receipt["kind"] == "R01BLazyFixtureReceipt" and
            receipt["milestone"] == "R01B" and receipt["result"] == "Passed" and
            type(receipt["createdAtUtc"]) is str and receipt["createdAtUtc"].endswith("Z"),
            "lazy receipt header differs")

    assembly = exact(receipt["assembly"], LAZY_ASSEMBLY_FIELDS, "lazy receipt assembly")
    lazy_dll = canonical_file(assembly["path"], "lazy fixture DLL")
    require(assembly["name"] == LAZY_NAME and assembly["version"] == LAZY_VERSION and lazy_dll.parent == receipt_path.parent and
            type(assembly["sizeBytes"]) is int and assembly["sizeBytes"] > 0 and lazy_dll.stat().st_size == assembly["sizeBytes"],
            "lazy fixture assembly identity or location differs")
    strict_hash(assembly["sha256"], "lazy receipt assembly.sha256")
    require(digest(lazy_dll) == assembly["sha256"], "lazy fixture DLL hash differs from its receipt")
    identity = read_identity(lazy_dll)
    for field in MVID_FIELDS:
        require(identity[field] == assembly[field], "lazy fixture PE " + field + " differs from its receipt")

    generator = exact(receipt["generator"], LAZY_GENERATOR_FIELDS, "lazy receipt generator")
    source = canonical_file(generator["sourcePath"], "lazy generator source")
    launcher = canonical_file(generator["launcherPath"], "lazy generator launcher")
    identity_reader = canonical_file(receipt["verification"]["identityReader"], "lazy identity reader")
    mono = canonical_file(generator["monoPath"], "lazy Mono")
    compiler = canonical_file(generator["compilerPath"], "lazy compiler")
    cecil = canonical_file(generator["cecilPath"], "lazy Cecil")
    require(source == LAZY_SOURCE and launcher == LAZY_LAUNCHER and identity_reader == IDENTITY_READER and
            mono == MONO and compiler == COMPILER and cecil == CECIL,
            "lazy receipt tool paths are not the pinned repository/toolchain paths")
    for field, path in (("sourceSha256", source), ("launcherSha256", launcher), ("monoSha256", mono),
                        ("compilerSha256", compiler), ("cecilSha256", cecil)):
        strict_hash(generator[field], "lazy receipt generator." + field)
        require(generator[field] == digest(path), "lazy receipt generator." + field + " is stale")
    strict_hash(receipt["verification"]["identityReaderSha256"], "lazy receipt identityReaderSha256")
    require(receipt["verification"]["identityReaderSha256"] == digest(identity_reader) and
            receipt["verification"]["independentPeIdentity"] is True,
            "lazy receipt independent identity provenance is invalid")
    require(type(generator["monoVersion"]) is str and generator["monoVersion"] and
            type(generator["compilerVersion"]) is str and generator["compilerVersion"],
            "lazy receipt tool versions are missing")
    current_tool_inputs = {str(path): digest(path) for path in (source, launcher, identity_reader, mono, compiler, cecil)}
    require(type(generator["inputHashesBefore"]) is dict and type(generator["inputHashesAfter"]) is dict and
            generator["inputHashesBefore"] == current_tool_inputs and generator["inputHashesAfter"] == current_tool_inputs and
            generator["inputsUnchanged"] is True and generator["reproducibleTwoRunSha256"] is True,
            "lazy receipt generator input hashes are stale or incomplete")

    compile_command = generator["compileCommand"]
    require(type(compile_command) is list and all(type(item) is str for item in compile_command) and len(compile_command) >= 5 and
            compile_command[0] == str(compiler) and compile_command[1:3] == ["-nologo", "-target:exe"] and
            sum(item.startswith("-out:") for item in compile_command) == 1 and
            sum(item.startswith("-r:") for item in compile_command) == 1 and
            Path(compile_command[-1]).is_absolute() and Path(compile_command[-1]).name == source.name and
            Path(next(item[3:] for item in compile_command if item.startswith("-r:"))).name == cecil.name,
            "lazy receipt compile command is not bound to the pinned generator")
    generate_commands = generator["generateCommands"]
    require(type(generate_commands) is list and len(generate_commands) == 2 and
            all(type(command) is list and len(command) == 3 and all(type(item) is str for item in command) and
                command[0] == str(mono) and Path(command[1]).is_absolute() and Path(command[1]).name.endswith(".exe") and
                Path(command[2]).is_absolute() and Path(command[2]).name in ("lazy-1.dll", "lazy-2.dll")
                for command in generate_commands),
            "lazy receipt generation commands are not reproducibly bound")

    verification = exact(receipt["verification"], LAZY_VERIFICATION_FIELDS, "lazy receipt verification")
    require(type(verification["note"]) is str and verification["note"], "lazy receipt verification note is missing")
    return receipt, lazy_dll, {source, launcher, identity_reader, mono, compiler, cecil}


def verify_dense_manifest(manifest_path: Path) -> tuple[dict, set[Path]]:
    manifest = exact(read_json(manifest_path), DENSE_FIELDS, "dense adjunct manifest")
    require(manifest["schemaVersion"] == 1 and manifest["kind"] == "R01BWorkloadV3DenseMetadataAdjunct" and
            manifest["status"] == "VerifiedSealedV1FixturesOutsideV2Envelope", "dense adjunct header differs")
    source = exact(manifest["sourceCorpus"], DENSE_SOURCE_FIELDS, "dense source corpus")
    corpus = canonical_directory(source["path"], "dense source corpus directory")
    for filename, field in (("workload-manifest.json", "manifestSha256"), ("workload-reparse.json", "reparseSha256")):
        path = canonical_file(corpus / filename, "dense source corpus " + filename)
        strict_hash(source[field], "dense source corpus." + field)
        require(digest(path) == source[field], "dense source corpus hash differs for " + filename)
    parser = exact(manifest["parser"], DENSE_PARSER_FIELDS, "dense parser provenance")
    require(parser["identity"] == "Tools/AssemblyShadow/m04_metadata.py::read_identity_bytes" and
            parser["tables"] == "Tools/AssemblyShadow/m05_types.py::CliTables", "dense parser provenance differs")
    fixtures = manifest["fixtures"]
    require(type(fixtures) is list and len(fixtures) == 2, "dense adjunct must contain exactly two fixtures")
    inputs = {manifest_path, corpus / "workload-manifest.json", corpus / "workload-reparse.json"}
    seen = set()
    for fixture in fixtures:
        row = exact(fixture, DENSE_ROW_FIELDS, "dense fixture row")
        require(type(row["id"]) is int and row["id"] in (1, 2) and row["id"] not in seen and
                row["name"] == "AssemblyShadow.Workload.I%04d" % row["id"] and
                type(row["sizeBytes"]) is int and row["sizeBytes"] > 0 and
                type(row["typeDefRows"]) is int and row["typeDefRows"] >= 4098 and
                type(row["methodDefRows"]) is int and row["methodDefRows"] >= 4097 and
                type(row["typeInventoryCount"]) is int and row["typeInventoryCount"] >= 4097,
                "dense fixture envelope differs")
        strict_hash(row["sha256"], "dense fixture sha256")
        path = canonical_file(row["path"], "dense fixture DLL")
        require(path.parent == corpus and path.name == row["name"] + ".dll" and path.stat().st_size == row["sizeBytes"] and
                digest(path) == row["sha256"], "dense fixture path/hash differs")
        identity = read_identity(path)
        tables = CliTables(path.read_bytes(), path)
        require(identity["name"] == row["name"] and identity["mvid"] == row["mvid"] and
                tables.counts[2] == row["typeDefRows"] and tables.counts[6] == row["methodDefRows"] and
                len(tables.streams["#Strings"]) == row["stringsHeapBytes"] and
                len(tables.type_inventory()["types"]) == row["typeInventoryCount"],
                "dense fixture PE/CLI identity differs")
        seen.add(row["id"])
        inputs.add(path)
    require(seen == {1, 2}, "dense adjunct fixture IDs differ")
    return manifest, inputs


def collect_inputs(fixture_manifest: Path, on_build: Path, off_build: Path, replay: Path,
                   lazy_receipt: Path, lazy_dll: Path, lazy_inputs: set[Path], dense_inputs: set[Path], app: Path) -> set[Path]:
    inputs = {fixture_manifest, on_build, off_build, replay, lazy_receipt, lazy_dll}
    inputs.update(lazy_inputs)
    inputs.update(dense_inputs)
    for path in app.rglob("*"):
        require(not path.is_symlink(), "Symlink in Player input tree: " + str(path))
        if path.is_file():
            inputs.add(path.resolve(strict=True))
    return inputs


def read_optional_json(path: Path) -> dict | None:
    if not path.is_file() or path.is_symlink():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if type(value) is dict else None
    except (OSError, ValueError, UnicodeError):
        return None


def verify_result(result: dict, result_path: Path, launch_pid: int, expected: dict, lazy_receipt: dict,
                  lazy_dll: Path, dense_manifest: Path, dense: dict, dense_enabled: bool) -> None:
    value = exact(result, RESULT_FIELDS, "lazy Player result")
    require(type(value["schemaVersion"]) is int and type(value["processId"]) is int and type(value["passedChecks"]) is int and
            type(value["failedAttributeAttempts"]) is int and type(value["malformedAttributeAttempts"]) is int and
            type(value["malformedConstructorCalls"]) is int and type(value["denseFixtures"]) is int and type(value["denseBoundaryChecks"]) is int and
            type(value["fixtureBytes"]) is int and type(value["il2cpp"]) is bool and type(value["checks"]) is list and
            type(value["capacitySnapshots"]) is list and type(value["retryExceptions"]) is list and
            all(type(value[field]) is str for field in ("kind", "milestone", "result", "error", "baselineBuildId", "runtimeAbiHash",
                                                        "unityVersion", "platform", "buildGuid", "resultPath", "fixturePath", "fixtureSha256",
                                                        "assemblyName", "assemblyFullName")), "lazy Player result types differ")
    require(value["schemaVersion"] == 1 and value["kind"] == "R01BLazyPlayerResult" and value["milestone"] == "R01B" and
            value["result"] == "Passed" and value["error"] == "" and value["il2cpp"] is True and value["platform"] == "OSXPlayer" and
            value["processId"] == launch_pid and value["buildGuid"] == expected["buildGuid"] and
            value["baselineBuildId"] == expected["baselineBuildId"] and value["runtimeAbiHash"] == expected["runtimeAbiHash"] and
            value["resultPath"] == str(result_path) and value["fixturePath"] == str(lazy_dll) and
            value["fixtureSha256"] == lazy_receipt["assembly"]["sha256"] and value["fixtureBytes"] == lazy_dll.stat().st_size and
            value["assemblyName"] == lazy_receipt["assembly"]["name"] and value["assemblyFullName"] == lazy_receipt["assembly"]["fullName"],
            "lazy Player result identity or provenance differs")

    checks = value["checks"]
    required_checks = {"il2cpp-player", "fixture-exists", "assembly-identity", "ordinary-image-accounted", "generic-int-method",
                       "generic-string-method", "generic-type-reflection", "generic-array-method", "reflection-array",
                       "inherited-interface-enumeration", "inherited-interface-assignability", "inherited-interface-map",
                       "inherited-aot-interface", "inherited-aot-interface-invoke", "attribute-data", "attribute-conversion",
                       "failed-attribute-data", "failed-attribute-constructor-retry-1", "failed-attribute-constructor-retry-2",
                       "malformed-attribute-conversion-retry-1", "malformed-attribute-conversion-retry-2",
                       "lazy-image-stable", "capacity-pages-monotonic"}
    names = set()
    for check in checks:
        item = exact(check, CHECK_FIELDS, "lazy Player check")
        require(type(item["name"]) is str and item["name"] and item["name"] not in names and type(item["detail"]) is str and
                type(item["passed"]) is bool and item["passed"] is True, "lazy Player check failed or duplicated")
        names.add(item["name"])
    require(required_checks.issubset(names) and value["passedChecks"] == len(checks) and len(checks) >= len(required_checks) and
            value["failedAttributeAttempts"] == 2 and value["malformedAttributeAttempts"] == 2 and
            value["malformedConstructorCalls"] == 0 and len(value["retryExceptions"]) == 4 and
            all(type(item) is str and item for item in value["retryExceptions"]), "lazy Player checks do not cover the required paths")

    snapshots = value["capacitySnapshots"]
    expected_phases = ["before-load", "after-load", "after-generics", "after-arrays", "after-interfaces",
                       "after-valid-attribute", "after-failed-attribute-1", "after-failed-attribute-2",
                       "after-malformed-attribute-1", "after-malformed-attribute-2"]
    if dense_enabled:
        expected_phases.append("after-dense-adjunct")
    require(len(snapshots) == len(expected_phases), "lazy Player capacity snapshot count differs")
    previous = None
    for index, snapshot in enumerate(snapshots):
        item = exact(snapshot, SNAPSHOT_FIELDS, "lazy Player capacity snapshot")
        require(item["phase"] == expected_phases[index] and all(type(item[field]) is int and item[field] >= 0 for field in SNAPSHOT_FIELDS - {"phase"}) and
                item["mappedPages"] <= item["reservedPages"] and item["reservedPages"] <= USABLE_PAGES and
                item["remainingImageCount"] == IMAGE_COUNT - item["lifetimeReservedImageCount"] and
                item["ordinaryAllocatedCount"] + item["shadowAllocatedCount"] == item["lifetimeReservedImageCount"] and
                item["reservedShadowImageCount"] == item["shadowAllocatedCount"], "lazy Player capacity ledger is inconsistent")
        if previous is not None:
            require(item["reservedPages"] >= previous["reservedPages"], "lazy Player capacity pages moved backwards")
        previous = item
    require(snapshots[1]["lifetimeReservedImageCount"] == snapshots[0]["lifetimeReservedImageCount"] + 1,
            "lazy fixture load did not reserve exactly one ordinary image")
    pre_dense = snapshots[1:-1] if dense_enabled else snapshots[1:]
    require(all(item["lifetimeReservedImageCount"] == snapshots[1]["lifetimeReservedImageCount"] for item in pre_dense),
            "lazy metadata operations changed the process image count")
    if dense_enabled:
        require(value["denseFixtures"] == len(dense["fixtures"]) == 2 and value["denseBoundaryChecks"] == 4 and
                snapshots[-1]["lifetimeReservedImageCount"] == snapshots[1]["lifetimeReservedImageCount"] + 2,
                "dense adjunct result or ledger accounting differs")
    else:
        require(value["denseFixtures"] == 0 and value["denseBoundaryChecks"] == 0, "lazy Player omitted dense adjunct evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--on-build", required=True, type=Path)
    parser.add_argument("--off-build", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--diagnostic-build", required=True, type=Path)
    parser.add_argument("--lazy-fixture-receipt", required=True, type=Path)
    parser.add_argument("--dense-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    project = canonical_directory(args.project_root, "project root")
    fixture_manifest = canonical_file(args.fixture_manifest, "M07 fixture manifest")
    on_build = canonical_file(args.on_build, "NativeOn build receipt")
    off_build = canonical_file(args.off_build, "NativeOff build receipt")
    replay = canonical_file(args.replay_receipt, "M07 replay receipt")
    diagnostic_build = canonical_file(args.diagnostic_build, "diagnostic build receipt")
    lazy_receipt_path = canonical_file(args.lazy_fixture_receipt, "lazy fixture receipt")
    dense_manifest_path = canonical_file(args.dense_manifest, "dense adjunct manifest")
    require(1 <= args.timeout <= 3600, "timeout must be in 1..3600 seconds")
    output_root = args.output_root
    require(output_root.is_absolute() and output_root == output_root.resolve() and not output_root.exists() and
            output_root.parent == project / "_temp/AssemblyShadow", "output root must be a new direct _temp/AssemblyShadow child")

    context = verify_diagnostic_inputs(project, fixture_manifest, on_build, off_build, replay, diagnostic_build)
    lazy_receipt, lazy_dll, lazy_inputs = verify_lazy_receipt(lazy_receipt_path)
    dense_manifest, dense_inputs = verify_dense_manifest(dense_manifest_path)
    app = context["diagnostic"]["output"]
    executable = executable_for(app)
    direct_inputs = collect_inputs(fixture_manifest, on_build, off_build, replay, lazy_receipt_path, lazy_dll, lazy_inputs,
                                   dense_inputs, app)
    direct_inputs.add(diagnostic_build)
    direct_inputs.update(context["diagnostic"]["inventory"])
    hashes_before = {str(path): digest(path) for path in sorted(direct_inputs)}

    output_root.mkdir()
    result_path = output_root / "r01b-lazy-result.json"
    unity_log = output_root / "r01b-lazy.unity.log"
    console_log = output_root / "r01b-lazy.console.log"
    launch_path = output_root / "r01b-lazy-player-launch.json"
    command = [str(executable), "-batchmode", "-nographics", "-shadowR01BLazyDll", str(lazy_dll),
               "-shadowR01BLazyResult", str(result_path), "-shadowR01BDenseManifest", str(dense_manifest_path),
               "-logFile", str(unity_log)]
    started = time.time()
    timed_out = False
    with console_log.open("xb") as console:
        process = subprocess.Popen(command, cwd=project, stdin=subprocess.DEVNULL,
                                   stdout=console, stderr=subprocess.STDOUT)
        print(f"R01B lazy Player started pid={process.pid}", flush=True)
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
    duration = time.time() - started

    result = read_optional_json(result_path)
    error = ""
    if result is None:
        error = "Missing or malformed lazy Player result"
    passed = False
    if result is not None and not timed_out and exit_code == 0:
        try:
            verify_result(result, result_path, process.pid, context["diagnostic"]["player"], lazy_receipt, lazy_dll,
                          dense_manifest_path, dense_manifest, True)
            passed = True
        except Exception as problem:
            error = str(problem)
    if result is not None and result.get("error"):
        error = error or result["error"]

    verify_diagnostic_inputs(project, fixture_manifest, on_build, off_build, replay, diagnostic_build)
    hashes_after = {str(path): digest(path) for path in sorted(direct_inputs)}
    unity_log_hash = digest(unity_log) if unity_log.is_file() and not unity_log.is_symlink() else ""
    console_log_hash = digest(console_log) if console_log.is_file() and not console_log.is_symlink() else ""
    logs_present = bool(unity_log_hash and console_log_hash)
    passed = passed and logs_present and hashes_before == hashes_after
    receipt = {
        "schemaVersion": 1, "kind": "R01BLazyPlayerLaunchReceipt", "milestone": "R01B", "diagnosticOnly": True,
        "projectRoot": str(project), "fixtureManifestPath": str(fixture_manifest), "fixtureManifestSha256": digest(fixture_manifest),
        "onBuildPath": str(on_build), "onBuildSha256": digest(on_build), "offBuildPath": str(off_build), "offBuildSha256": digest(off_build),
        "diagnosticBuildPath": str(diagnostic_build), "diagnosticBuildSha256": digest(diagnostic_build),
        "replayReceiptPath": str(replay), "replayReceiptSha256": digest(replay), "lazyFixtureReceiptPath": str(lazy_receipt_path),
        "lazyFixtureReceiptSha256": digest(lazy_receipt_path), "lazyFixturePath": str(lazy_dll), "lazyFixtureSha256": digest(lazy_dll),
        "denseManifestPath": str(dense_manifest_path), "denseManifestSha256": digest(dense_manifest_path),
        "denseFixturePaths": [str(row["path"]) for row in dense_manifest["fixtures"]],
        "denseFixtureSha256": [digest(canonical_file(row["path"], "dense fixture DLL")) for row in dense_manifest["fixtures"]],
        "playerOutput": str(app), "playerExecutable": str(executable), "command": command, "processId": process.pid,
        "startedAtUnix": started, "durationSeconds": duration, "exitCode": exit_code, "timedOut": timed_out, "passed": passed,
        "resultPath": str(result_path), "resultSha256": digest(result_path) if result_path.is_file() else "",
        "unityLogPath": str(unity_log), "unityLogSha256": unity_log_hash, "consoleLogPath": str(console_log),
        "consoleLogSha256": console_log_hash, "inputHashesBefore": hashes_before, "inputHashesAfter": hashes_after,
        "inputsUnchanged": hashes_before == hashes_after,
        "error": error or (result or {}).get("error", "No result file"),
        "note": "This receipt binds the actual diagnostic Player process and direct inputs; its result is accepted only when all lazy checks and ledger snapshots pass.",
    }
    with launch_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"result": "Passed" if passed else "Failed", "processId": process.pid,
                      "exitCode": exit_code, "durationSeconds": duration, "logsPresent": logs_present,
                      "inputsUnchanged": hashes_before == hashes_after}))
    return int(not passed)


if __name__ == "__main__":
    raise SystemExit(main())
