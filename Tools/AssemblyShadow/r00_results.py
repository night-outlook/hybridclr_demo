"""Strict R00 observation gate; performance observations are not release approval."""
import argparse
import importlib.util
import json
from pathlib import Path

import m07_results as m07
from r00_player_inputs import verify_inputs
from shadow_tools import VerificationError, require

MODES = ("R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03", "R00-OFF-NoPatch")
OFF_MODE = MODES[-1]
PHASES = (("first", 1, 17), ("warmup", 100, 1017), ("repeat10", 10, 2017), ("repeat10000", 10000, 3017))
OPERATIONS = ("allocation", "reflectionInvoke", "closedGeneric")
REGRESSION_EXPECTED = {
    "new": ("ctor.count=2", "ctor.first=1030", "ctor.second=1030", "helper.count=2"),
    "dispatch": ("virtual=M06-BASELINE:sealed", "abstract=M06-BASELINE:abstract", "assignable=True"),
    "generics": ("generic.value=4", "method=M06-BASELINE", "nullable=4", "boxed=4", "struct=1004", "ref=1006", "out=1007", "generic.method=6", "array=2"),
}
INTERNAL = "AssemblyA.Implementation.Internal"
WITNESS = INTERNAL + ".R00PerformanceWitness"
PAYLOAD = INTERNAL + ".R00PerformancePayload"


def read(path):
    return m07.json_text(Path(path).read_text(encoding="utf-8-sig"), str(path))


def equal(actual, expected, label):
    m07.exact(actual, expected, label)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, label + ": invalid integer")
    return value


def int32(value):
    return (value + 2**31) % 2**32 - 2**31


def marker(mode):
    return ("R00-P03", 3003) if mode == MODES[2] else ("R00-P01", 3001) if mode == MODES[1] else ("R00-BASELINE", 3000)


def expected_checksum(operation, mode, count, seed):
    name, value = marker(mode)
    total_seed = count * seed + count * (count - 1) // 2
    if operation == "allocation":
        return int32(total_seed * 17 + count * (value + len(name)))
    if operation == "reflectionInvoke":
        return int32(total_seed * 31 + count * value)
    require(operation == "closedGeneric", "Unknown R00 operation")
    return int32(total_seed)


def verify_operations(rows, mode):
    equal([(row["operation"], row["phase"]) for row in rows],
          [(operation, phase) for operation in OPERATIONS for phase, _, _ in PHASES], "R00 exact operation inventory")
    summary = []
    for row, (operation, (phase, count, seed)) in zip(rows, ((op, phase) for op in OPERATIONS for phase in PHASES)):
        label = mode + ":" + operation + ":" + phase
        for key, value in (("passed", True), ("requestedIterations", count),
                           ("methodCalls", 1 if operation == "allocation" else count),
                           ("actualNewCount", count if operation == "allocation" else 0),
                           ("actualInvocationCount", 0 if operation == "allocation" else count)):
            equal(row[key], value, label + ":" + key)
        checksum = expected_checksum(operation, mode, count, seed)
        equal(row["checksum"], checksum, label + ": checksum independently recomputed")
        equal(row["expectedChecksum"], checksum, label + ": expected checksum")
        before = integer(row["constructorCountBefore"], label + ": constructor before")
        after = integer(row["constructorCountAfter"], label + ": constructor after")
        equal(after - before, count if operation == "allocation" else 0, label + ": constructor delta")
        ticks = integer(row["elapsedTicks"], label + ": ticks")
        frequency = integer(row["stopwatchFrequency"], label + ": frequency", 1)
        summary.append({"operation": operation, "phase": phase, "iterations": count,
                        "elapsedTicks": ticks, "stopwatchFrequency": frequency,
                        "nanosecondsPerIteration": ticks * 1e9 / frequency / count})
    allocation = [row for row in rows if row["operation"] == "allocation"]
    equal(allocation[0]["constructorCountBefore"], 0, "R00 first allocation precedes warmup")
    for previous, current in zip(allocation, allocation[1:]):
        equal(current["constructorCountBefore"], previous["constructorCountAfter"], "R00 contiguous allocation counters")
    return summary


def verify_regressions(rows, enabled, patched):
    equal([(row["phase"], row["repetition"]) for row in rows],
          [(phase, repetition) for phase in REGRESSION_EXPECTED for repetition in range(2)], "R00 existing M06 phase inventory")
    for row in rows:
        equal(row["typeName"], INTERNAL + ".M06ExecutionWitness", "R00 existing witness")
        equal(row["diagnosticsCode"], "Success" if enabled else "FeatureDisabled", "R00 regression diagnostics")
        observations = row["observations"]
        require(len({value.split("=", 1)[0] for value in observations}) == len(observations), "R00 duplicate regression observation")
        require("phase=" + row["phase"] in observations and all(value in observations for value in REGRESSION_EXPECTED[row["phase"]]),
                "R00 existing M06 execution regression failed")
        if enabled:
            raw = m07.json_text(row["typeDiagnosticsJson"], "R00 existing M06 type")
            for key, value in (("isActive", True), ("logicalAssembly", INTERNAL),
                               ("executionMode", "InterpreterShadow" if patched else "AotBaseline"),
                               ("physicalImageKind", "Interpreter" if patched else "Aot")):
                equal(raw[key], value, "R00 regression physical type " + key)
        else:
            equal(row["typeDiagnosticsJson"], "", "R00 OFF type diagnostics")


def verify_result(result, mode, context):
    enabled, patched = mode != OFF_MODE, mode in MODES[1:3]
    patch = "P01" if mode == MODES[1] else "P03" if mode == MODES[2] else ""
    build = context["on" if enabled else "off"]
    player, manifest = build["player"], context["manifest"]
    for key, value in (("schemaVersion", 1), ("milestone", "M07R-R00"), ("mode", mode), ("result", "Passed"),
                       ("error", ""), ("il2cpp", True), ("featureEnabled", enabled), ("transactionCommitted", patched),
                       ("patchId", patch), ("unityVersion", "2022.3.62f2"), ("platform", "OSXPlayer"),
                       ("baselineBuildId", manifest["baselineBuildId"]), ("runtimeAbiHash", manifest["runtimeAbiHash"]),
                       ("buildGuid", player["buildGuid"])):
        equal(result[key], value, mode + ":" + key)
    for key in ("fixtureManifest", "baselineManifest", "resourceReceipt", "playerBuildReceipt"):
        receipt = result[key]
        equal(receipt["available"], True, mode + ":" + key)
        m07.bound(receipt["path"], receipt["sha256"], mode, key)
    equal(result["fixtureManifest"]["path"], manifest["_path"], "R00 fixture binding")
    equal(result["baselineManifest"]["path"], manifest["baselineManifestPath"], "R00 baseline binding")
    equal(result["playerBuildReceipt"]["path"], str(build["path"]), "R00 Player receipt binding")
    for key in ("variant", "buildGuid", "playerOutput", "inputSnapshot", "inputSnapshotHash", "nativeLibraryPath",
                "nativeLibrarySha256", "nativeMetadataPath", "nativeMetadataSha256", "nativeArguments", "nativeMetadataVersion",
                "resourceBuildReceiptPath", "resourceBuildReceiptSha256", "resourceAbiHash"):
        equal(result["playerBuildReceipt"][key], player[key], "R00 Player " + key)
    resource_receipt = Path(manifest["baselineManifestPath"]).parent / context["baseline"]["resourceBaselinePath"] / "resource-build-receipt.json"
    equal(result["resourceReceipt"]["path"], str(resource_receipt), "R00 selected baseline resources")
    equal(result["patchManifest"]["available"], patched, "R00 patch availability")
    closure = next(row["closureLoadOrder"] for row in manifest["fixtures"] if row["patchId"] == patch) if patched else []
    equal(result["stageOrder"], closure, "R00 exact staged closure")
    if patched:
        fixture = next(row for row in manifest["fixtures"] if row["patchId"] == patch)
        equal(result["patchManifest"]["path"], fixture["patchManifest"], "R00 patch path")
        equal(result["patchManifest"]["sha256"], fixture["patchManifestSha256"], "R00 patch hash")
        for key in ("configureCode", "beginCode", "validateCode", "commitCode", "stateCode"):
            equal(result[key], "Success", "R00 transaction " + key)
    equal(result["state"], "Committed" if patched else "CandidatesRegistered" if enabled else "Disabled", "R00 transaction state")
    selected = result["selectedType"]
    for key, value in (("fullName", WITNESS), ("assemblyName", INTERNAL), ("logicalAssembly", INTERNAL),
                       ("sameType", True), ("isActive", True),
                       ("executionMode", "InterpreterShadow" if patched else "AotBaseline"),
                       ("diagnosticsCode", "Success" if enabled else "FeatureDisabled")):
        equal(selected[key], value, "R00 type identity " + key)
    equal(selected["physicalImageKind"], "Interpreter" if patched else "Aot", "R00 physical type")
    if enabled:
        raw_type = m07.json_text(selected["rawJson"], "R00 selected type")
        for key in ("logicalAssembly", "isActive", "executionMode", "physicalImageKind", "pointerDetailsAvailable",
                    "definitionCacheHits", "definitionCacheMisses", "compositeRebuilds", "allocationRemaps", "guardFailures"):
            equal(selected[key], raw_type[key], "R00 raw selected type " + key)
    for name, phase in (("diagnosticsBefore", "before-benchmark"), ("diagnosticsAfter", "after-benchmark")):
        observation = result[name]
        equal(observation["phase"], phase, "R00 diagnostic phase")
        equal(observation["code"], "Success" if enabled else "FeatureDisabled", "R00 diagnostic status")
        equal(observation["diagnosticsOnly"], True, "R00 diagnostic scope")
        raw = m07.json_text(observation["rawJson"], mode + ":" + phase)
        equal(raw["enabled"], enabled, "R00 diagnostics enabled")
        equal(raw["state"], result["state"], "R00 diagnostics state")
        if patched:
            require(not any(row["name"] in closure for row in raw["baselineUses"]), "R00 selected closure used baseline")
        counters = observation["counters"]
        for counter in ("proofBuildCount", "typeRowsScanned", "nativeAllocationCount"):
            equal(counters[counter], "unavailable", "R00 unsupported counter must remain explicit")
        for counter in ("generation", "expected", "staged", "retainedBytes", "enumerationGeneration", "classEnumerationGeneration"):
            equal(counters[counter], raw[counter], "R00 raw diagnostic counter " + counter)
    witness = result["witness"]
    equal(witness["firstPayloadDistinct"], True, "R00 distinct objects")
    equal(witness["constructorDelta"], 2, "R00 witness constructors")
    equal(witness["constructorCountAfter"] - witness["constructorCountBefore"], 2, "R00 witness constructor delta")
    equal(witness["constructorCountBefore"], sum(count for _, count, _ in PHASES), "R00 fresh-return witness follows measured allocations")
    for key in ("firstPayloadType", "secondPayloadType"):
        equal(witness[key], PAYLOAD, "R00 payload identity")
    for key, seed in (("firstPayloadChecksum", 17), ("secondPayloadChecksum", 18)):
        equal(witness[key], expected_checksum("allocation", mode, 1, seed), "R00 payload checksum")
    assertions = result["assertions"]
    require(assertions and len({row["name"] for row in assertions}) == len(assertions), "R00 assertions absent or duplicated")
    require(all(row["passed"] is True for row in assertions), "R00 failed assertion")
    readiness = result["readiness"]
    equal(readiness["businessReady"], True, "R00 readiness")
    invoked = integer(readiness["probeInvocationUtcTicks"], "R00 probe invocation UTC", 1)
    ready = integer(readiness["businessReadyUtcTicks"], "R00 business readiness UTC", 1)
    require(ready >= invoked, "R00 readiness precedes probe invocation")
    if readiness["processStartAvailable"]:
        require(integer(readiness["processStartUtcTicks"], "R00 process start UTC", 1) <= invoked, "R00 invocation precedes process start")
        integer(readiness["startupToBusinessReadyMilliseconds"], "R00 readiness elapsed")
    else:
        equal(readiness["startupToBusinessReadyMilliseconds"], -1, "R00 readiness unavailable")
        require(bool(readiness["unavailableReason"]), "R00 readiness missing unavailable reason")
    verify_regressions(result["executionRegressions"], enabled, patched)
    return {"mode": mode, "buildGuid": player["buildGuid"], "readiness": readiness,
            "existingM06ExecutionRegressionPhases": list(REGRESSION_EXPECTED),
            "operations": verify_operations(result["operations"], mode)}


def verify_suite(launch_path):
    launch_path = Path(launch_path).resolve(strict=True)
    launch = read(launch_path)
    equal(launch["milestone"], "R00", "R00 launch milestone")
    equal(launch["requestedModes"], list(MODES), "R00 full matrix")
    equal(launch["inputsUnchanged"], True, "R00 immutable inputs")
    equal(launch["inputHashesAfter"], launch["inputHashesBefore"], "R00 before/after hashes")
    context = verify_inputs(Path(launch["projectRoot"]), Path(launch["fixtureManifestPath"]),
                            Path(launch["nativeOnReceipt"]), Path(launch["nativeOffReceipt"]), Path(launch["editorReplayReceipt"]))
    equal(launch["sourcePins"], context["sourcePins"], "R00 current source pairing")
    spec = importlib.util.spec_from_file_location("m07_launch_inputs", Path(__file__).with_name("run-m07-players.py"))
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    inputs = runner.collect_inputs(Path(launch["fixtureManifestPath"]), Path(launch["editorReplayReceipt"]),
                                   (Path(launch["nativeOnReceipt"]), Path(launch["nativeOffReceipt"])))
    equal(launch["inputHashesBefore"], {str(path): m07.digest(path) for path in sorted(inputs)}, "R00 complete current input inventory")
    rows = launch["processLaunches"]
    equal([row["mode"] for row in rows], list(MODES), "R00 process inventory")
    require(len({integer(row["processId"], "R00 PID", 1) for row in rows}) == len(MODES), "R00 processes must be distinct")
    summary = []
    for row in rows:
        equal(row["exitCode"], 0, "R00 clean process exit")
        equal(row["timedOut"], False, "R00 bounded process exit")
        equal(row["passed"], True, "R00 launch status")
        path = m07.bound(row["resultPath"], row["resultSha256"], launch_path, "result")
        equal(path.parent, Path(launch["resultDirectory"]), "R00 result containment")
        result = read(path)
        build = context["off" if row["mode"] == OFF_MODE else "on"]
        expected_command = [str(runner.executable_for(build["output"])), "-batchmode", "-nographics",
                            "-shadowR00Mode", row["mode"], "-shadowM07Fixtures", launch["fixtureManifestPath"],
                            "-shadowM07PlayerReceipt", str(build["path"]), "-shadowR00Result", str(path),
                            "-logFile", row["logPath"]]
        equal(row["command"], expected_command, "R00 actual launch command binding")
        data_path = m07.canonical(result["playerDataPath"], path, "playerDataPath", True)
        require(data_path.is_relative_to(build["output"]), "R00 data path escapes executed Player")
        equal(result["processId"], row["processId"], "R00 executed PID")
        observation = verify_result(result, row["mode"], context)
        ready_unix = integer(result["readiness"]["businessReadyUtcTicks"], "R00 readiness UTC", 1) / 10_000_000 - 62_135_596_800
        elapsed = ready_unix - row["startedAtUnix"]
        require(0 <= elapsed <= row["durationSeconds"] + 1, "R00 readiness is outside its process launch interval")
        observation["launchToBusinessReadyMilliseconds"] = elapsed * 1000
        observation["readinessMeasurementScope"] = "Parent Popen boundary to configured witness marker resolution; excludes scene/resource load"
        summary.append(observation)
    return {"schemaVersion": 1, "milestone": "R00", "result": "Passed", "sourcePins": context["sourcePins"],
            "launchReceipt": str(launch_path), "launchReceiptSha256": m07.digest(launch_path),
            "scope": "Four current-pairing Development IL2CPP performance observations; not legacy M05/M06 full acceptance or release approval",
            "modes": summary}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = verify_suite(args.launch_receipt)
    require(not args.output.exists() and not args.output.is_symlink(), "R00 output must be new")
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("R00 observations Passed: " + str(args.output))
    return 0
