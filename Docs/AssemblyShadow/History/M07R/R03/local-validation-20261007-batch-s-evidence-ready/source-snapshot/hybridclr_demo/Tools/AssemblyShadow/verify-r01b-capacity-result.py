#!/usr/bin/env python3
"""Strictly verify the real R01B capacity Player result and immutable inputs."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import r01_early_results as early
from r01b_diagnostic_inputs import verify_diagnostic_inputs
from r01b_capacity_inputs import (CHARGED_PAGE_CEILING, IMAGE_COUNT, MINIMUM_FREE_PAGES, TOTAL_DLL_BYTES,
                                  USABLE_PAGES, canonical_directory, canonical_file, collect_direct_inputs,
                                  digest, executable_for, validate_mixed_workload, validate_overflow, validate_workload)
from shadow_tools import VerificationError, read_json, require, unique_object


RESULT_FIELDS = frozenset(("schemaVersion", "processId", "loadedImages", "invokedImages", "payloadRvaChecks",
                           "denseNameChecks", "postRejectionMappingChecks", "retainedFailureCount", "validImagesToLoad",
                           "highRvaFieldChecks",
                           "kind", "milestone", "result", "error", "memoryMeasurement",
                           "baselineBuildId", "runtimeAbiHash", "unityVersion", "platform", "buildGuid", "resultPath",
                           "manifestPath", "manifestSha256", "corpusRoot", "mixedManifestPath", "mixedManifestSha256",
                           "mixedCorpusRoot", "limitException", "overflowPath",
                           "overflowName", "overflowSha256", "scenario", "retainedFailureExceptions", "il2cpp",
                           "loadedDllBytes", "shadowDllBytes", "validDllBytes", "retainedFailureInputBytes", "overflowDllBytes",
                           "loadMilliseconds", "workingSetBytesBefore", "maximumWorkingSetBytes", "managedBytesAfter",
                           "initial", "afterRetainedFailures", "before", "at8191", "after", "afterRejected"))
CAPTURE_FIELDS = frozenset(("rawJson", "failureReason", "fitsPreliminary", "firstFailingIndex", "requiredImages",
                            "acceptedImages", "reservedPages", "mappedPages", "lifetimeReservedImageCount",
                            "remainingImageCount", "ordinaryAllocatedCount", "shadowAllocatedCount",
                            "reservedShadowImageCount", "freeUsablePages"))
NATIVE_FIELDS = frozenset(("schemaVersion", "enabled", "profileVersion", "maximumImageCount", "maximumDllBytes",
                           "usablePageCapacity", "chargedPageCeiling", "minimumFreePageMargin", "reservedPages",
                           "mappedPages", "lifetimeReservedImageCount", "remainingImageCount", "requiredImages",
                           "acceptedImages", "firstFailingIndex", "firstFailingSize", "failureReason",
                           "fitsPreliminary", "runtimeFinalizationRequired", "aggregateInputDllBytes",
                           "aggregateInputDllBytesInformational", "ordinaryAllocatedCount", "shadowAllocatedCount",
                           "reservedShadowImageCount"))
LAUNCH_FIELDS = frozenset(("schemaVersion", "kind", "milestone", "diagnosticOnly", "projectRoot",
                           "scenario",
                           "fixtureManifestPath", "fixtureManifestSha256", "onBuildPath", "onBuildSha256",
                           "offBuildPath", "offBuildSha256", "replayReceiptPath", "replayReceiptSha256",
                           "workloadManifestPath", "workloadManifestSha256", "corpusRoot", "mixedManifestPath",
                           "mixedManifestSha256", "mixedCorpusRoot", "overflowReceiptPath",
                           "overflowReceiptSha256", "playerOutput", "playerExecutable", "command", "processId",
                           "startedAtUnix", "durationSeconds", "exitCode", "timedOut", "passed", "resultPath",
                           "resultSha256", "diagnosticBuildPath", "diagnosticBuildSha256",
                           "capsulePath", "capsuleSha256", "earlyResultPath", "earlyResultSha256", "unityLogPath", "consoleLogPath", "inputHashesBefore", "inputHashesAfter",
                           "inputsUnchanged", "error", "note"))


def exact_fields(value: object, fields: frozenset[str], label: str) -> dict:
    require(type(value) is dict and set(value) == fields, label + ": object inventory differs")
    return value


def strict_types(value: dict, integer_fields: set[str], string_fields: set[str], boolean_fields: set[str],
                 list_fields: set[str], object_fields: set[str], label: str) -> None:
    require(all(type(value[field]) is int for field in integer_fields) and
            all(type(value[field]) is str for field in string_fields) and
            all(type(value[field]) is bool for field in boolean_fields) and
            all(type(value[field]) is list for field in list_fields) and
            all(type(value[field]) is dict for field in object_fields),
            label + ": field types differ")


def capacity(value: object, label: str) -> tuple[dict, dict]:
    captured = exact_fields(value, CAPTURE_FIELDS, label)
    require(type(captured["rawJson"]) is str and type(captured["failureReason"]) is str and
            type(captured["fitsPreliminary"]) is bool and type(captured["firstFailingIndex"]) is int and
            all(type(captured[field]) is int and captured[field] >= 0 for field in CAPTURE_FIELDS - {
                "rawJson", "failureReason", "fitsPreliminary", "firstFailingIndex"}),
            label + ": captured value types differ")
    try:
        raw = json.loads(captured["rawJson"], object_pairs_hook=unique_object,
                         parse_constant=lambda token: (_ for _ in ()).throw(
                             VerificationError(label + ".rawJson: invalid constant " + token)))
    except (ValueError, TypeError, UnicodeError) as error:
        raise VerificationError(label + ".rawJson: invalid JSON: " + str(error)) from error
    exact_fields(raw, NATIVE_FIELDS, label + ".rawJson")
    boolean_fields = {"enabled", "fitsPreliminary", "runtimeFinalizationRequired",
                      "aggregateInputDllBytesInformational"}
    string_fields = {"failureReason"}
    signed_fields = {"firstFailingIndex"}
    require(all(type(raw[field]) is bool for field in boolean_fields) and
            all(type(raw[field]) is str for field in string_fields) and
            all(type(raw[field]) is int for field in signed_fields) and
            all(type(raw[field]) is int and raw[field] >= 0
                for field in NATIVE_FIELDS - boolean_fields - string_fields - signed_fields),
            label + ".rawJson: native value types differ")
    require(raw["schemaVersion"] == 2 and raw["enabled"] is True and raw["profileVersion"] == 2 and
            raw["maximumImageCount"] == IMAGE_COUNT and raw["maximumDllBytes"] == 32 * 1024 * 1024 and
            raw["usablePageCapacity"] == USABLE_PAGES and raw["chargedPageCeiling"] == CHARGED_PAGE_CEILING and
            raw["minimumFreePageMargin"] == MINIMUM_FREE_PAGES and raw["runtimeFinalizationRequired"] is True and
            raw["aggregateInputDllBytesInformational"] is True, label + ": wrong native profile 2 constants")
    for field in CAPTURE_FIELDS - {"rawJson", "freeUsablePages"}:
        require(captured[field] == raw[field], label + ": captured/native " + field + " differs")
    require(captured["freeUsablePages"] == USABLE_PAGES - raw["reservedPages"] and
            0 <= raw["mappedPages"] <= raw["reservedPages"] <= CHARGED_PAGE_CEILING and
            raw["lifetimeReservedImageCount"] <= IMAGE_COUNT and
            raw["remainingImageCount"] == IMAGE_COUNT - raw["lifetimeReservedImageCount"] and
            raw["ordinaryAllocatedCount"] + raw["shadowAllocatedCount"] == raw["lifetimeReservedImageCount"] and
            raw["reservedShadowImageCount"] == raw["shadowAllocatedCount"] and
            raw["acceptedImages"] <= raw["requiredImages"],
            label + ": invalid page/image accounting")
    if raw["fitsPreliminary"]:
        require(raw["requiredImages"] <= raw["remainingImageCount"] and
                raw["acceptedImages"] == raw["requiredImages"] and raw["firstFailingIndex"] == -1 and
                raw["firstFailingSize"] == 0 and raw["failureReason"] == "None",
                label + ": successful native report has failure markers")
    else:
        require(raw["requiredImages"] > 0 and raw["acceptedImages"] == 0 and
                0 <= raw["firstFailingIndex"] < raw["requiredImages"] and raw["firstFailingSize"] > 0 and
                raw["failureReason"] in {"EmptyDll", "DllTooLarge", "ImageLimit", "InvalidInput", "InvalidState"},
                label + ": failed native report has invalid markers")
    return captured, raw


def startup_mode(mixed: bool) -> str:
    """Select the startup transaction represented by this capacity scenario."""
    return "Control" if mixed else "Baseline"


def startup_binding(launch: dict, launch_path: Path, mixed: bool) -> tuple[str, Path, Path]:
    """Validate launch startup paths and bind the capsule mode before provenance setup."""
    mode = startup_mode(mixed)
    capsule_path = canonical_file(launch["capsulePath"], "R01B startup capsule")
    early_path = canonical_file(launch["earlyResultPath"], "R01B startup result")
    require(capsule_path.parent == launch_path.parent and launch["capsuleSha256"] == digest(capsule_path) and
            early_path.parent == launch_path.parent and launch["earlyResultSha256"] == digest(early_path),
            "R01B startup result/capsule path binding differs")
    capsule_data = early.capsule.decode(capsule_path.read_bytes())
    early.exact(capsule_data["mode"], mode, "R01B startup capsule mode")
    return mode, capsule_path, early_path


def validate_startup_receipt_contract(early_path: Path, capsule_path: Path, mode: str,
                                     process_id: int) -> dict:
    """Check the process binding and operation shape before profile-2 replay."""
    receipt = early.read(early_path)
    early.fields(receipt, early.RECEIPT_FIELDS, "R01B startup receipt")
    capsule_data = early.capsule.decode(capsule_path.read_bytes())
    early.exact(receipt["mode"], mode, "R01B startup receipt mode")
    early.exact(receipt["processId"], process_id, "R01B startup receipt process")
    early.exact(receipt["capsulePath"], str(capsule_path), "R01B startup receipt capsule")
    early.exact(receipt["capsuleSha256"], early.digest(capsule_path), "R01B startup receipt capsule hash")
    early.exact(receipt["resultPath"], str(early_path), "R01B startup receipt result")
    early.exact(receipt["result"], "Passed", "R01B startup receipt result status")
    early.exact(receipt["error"], "", "R01B startup receipt error")
    expected_callback = 0 if mode in early.POSITIVE_MODES or mode == "Baseline" else 1
    early.exact(receipt["callbackReturnCode"], expected_callback, "R01B startup receipt callback")
    expected_operations = early._expected_operations(mode, [row["name"] for row in capsule_data["inputs"]])
    operations = receipt["operations"]
    early.exact(len(operations), len(expected_operations), "R01B startup receipt operation count")
    for index, (operation, expected) in enumerate(zip(operations, expected_operations)):
        early.fields(operation, early.OPERATION_FIELDS, f"R01B startup receipt operation[{index}]")
        early.exact((operation["phase"], operation["code"], operation["intCode"]), expected,
                    f"R01B startup receipt operation[{index}]")
    return receipt


def verify_startup_receipt(early_path: Path, capsule_path: Path, mode: str, process_id: int) -> dict:
    """Run the shared strict profile-2 startup receipt verifier."""
    validate_startup_receipt_contract(early_path, capsule_path, mode, process_id)
    return early.verify_early_receipt(early_path, capsule_path, mode, process_id, profile=2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--on-build", required=True, type=Path)
    parser.add_argument("--off-build", required=True, type=Path)
    parser.add_argument("--diagnostic-build", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--workload-manifest", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--mixed-manifest", type=Path)
    parser.add_argument("--mixed-corpus", type=Path)
    parser.add_argument("--overflow-receipt", required=True, type=Path)
    parser.add_argument("--launch-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mixed", action="store_true")
    args = parser.parse_args()

    project = canonical_directory(args.project_root, "project root")
    fixture = canonical_file(args.fixture_manifest, "M07 fixture manifest")
    on_path = canonical_file(args.on_build, "NativeOn build receipt")
    off_path = canonical_file(args.off_build, "NativeOff build receipt")
    diagnostic_path = canonical_file(args.diagnostic_build, "diagnostic build receipt")
    diagnostic_receipt = diagnostic_path
    replay = canonical_file(args.replay_receipt, "M07 replay receipt")
    workload_path = canonical_file(args.workload_manifest, "R01B workload manifest")
    corpus = canonical_directory(args.corpus_root, "R01B corpus root")
    mixed_manifest = mixed_corpus = None
    if args.mixed:
        require(args.mixed_manifest is not None and args.mixed_corpus is not None,
                "mixed mode requires a separate mixed manifest and corpus")
        mixed_manifest = canonical_file(args.mixed_manifest, "R01B mixed workload manifest")
        mixed_corpus = canonical_directory(args.mixed_corpus, "R01B mixed corpus root")
    else:
        require(args.mixed_manifest is None and args.mixed_corpus is None,
                "ordinary mode must not claim a mixed workload")
    overflow_path = canonical_file(args.overflow_receipt, "R01B overflow receipt")
    launch_path = canonical_file(args.launch_receipt, "R01B launch receipt")
    output = args.output
    require(output.is_absolute() and output == output.resolve() and not output.exists() and not output.is_symlink(),
            "strict verifier output must be a new canonical absolute path")

    context = verify_diagnostic_inputs(project, fixture, on_path, off_path, replay, diagnostic_receipt)
    diagnostic = context["diagnostic"]
    workload, workload_files = validate_workload(workload_path, corpus, deep=True)
    mixed_workload = None
    mixed_workload_files = []
    if mixed_manifest is not None and mixed_corpus is not None:
        mixed_workload, mixed_workload_files = validate_mixed_workload(mixed_manifest, mixed_corpus, deep=True)
        require(mixed_workload["source"]["ordinaryManifestPath"] == str(workload_path) and
                mixed_workload["source"]["ordinaryCorpusRoot"] == str(corpus),
                "Mixed workload is not derived from the selected ordinary corpus")
    overflow, overflow_dll = validate_overflow(overflow_path, deep=True)
    names = {row["name"].casefold() for row in workload["assemblies"]}
    hashes = {row["sha256"] for row in workload["assemblies"]}
    require(overflow["assembly"]["name"].casefold() not in names and overflow["assembly"]["sha256"] not in hashes,
            "Overflow assembly is not distinct from every supported assembly")

    launch = exact_fields(read_json(launch_path), LAUNCH_FIELDS, "launch")
    strict_types(
        launch,
        {"schemaVersion", "processId", "exitCode"},
        {field for field in LAUNCH_FIELDS if field not in {
            "schemaVersion", "processId", "exitCode", "diagnosticOnly", "command", "startedAtUnix",
            "durationSeconds", "timedOut", "passed", "inputsUnchanged", "inputHashesBefore", "inputHashesAfter"}},
        {"diagnosticOnly", "timedOut", "passed", "inputsUnchanged"}, {"command"},
        {"inputHashesBefore", "inputHashesAfter"}, "launch")
    require(type(launch["startedAtUnix"]) in (int, float) and type(launch["startedAtUnix"]) is not bool and
            type(launch["durationSeconds"]) in (int, float) and type(launch["durationSeconds"]) is not bool and
            math.isfinite(launch["startedAtUnix"]) and math.isfinite(launch["durationSeconds"]) and
            launch["startedAtUnix"] > 0 and launch["durationSeconds"] > 0 and launch["processId"] > 0 and
            all(type(item) is str for item in launch["command"]), "launch: invalid timing/process/command fields")
    expected_paths = {
        "projectRoot": project, "fixtureManifestPath": fixture, "onBuildPath": on_path, "offBuildPath": off_path,
        "replayReceiptPath": replay, "workloadManifestPath": workload_path, "corpusRoot": corpus,
        "overflowReceiptPath": overflow_path, "playerOutput": diagnostic["output"],
    }
    for field, expected in expected_paths.items():
        require(launch[field] == str(expected), "launch." + field + " differs")
    for field, path in (("fixtureManifestSha256", fixture), ("onBuildSha256", on_path),
                        ("offBuildSha256", off_path), ("replayReceiptSha256", replay),
                        ("workloadManifestSha256", workload_path), ("overflowReceiptSha256", overflow_path)):
        require(launch[field] == digest(path), "launch." + field + " hash differs")
    require(launch["diagnosticBuildPath"] == str(diagnostic_path) and
            launch["diagnosticBuildSha256"] == digest(diagnostic_path),
            "launch diagnostic build binding differs")
    require(launch["mixedManifestPath"] == (str(mixed_manifest) if mixed_manifest is not None else "") and
            launch["mixedManifestSha256"] == (digest(mixed_manifest) if mixed_manifest is not None else "") and
            launch["mixedCorpusRoot"] == (str(mixed_corpus) if mixed_corpus is not None else ""),
            "launch mixed workload binding differs")
    executable = executable_for(diagnostic["output"])
    require(launch["playerExecutable"] == str(executable) and launch["schemaVersion"] == 1 and
            launch["kind"] == "R01BCapacityPlayerLaunchReceipt" and launch["milestone"] == "R01B" and
            launch["diagnosticOnly"] is True and launch["exitCode"] == 0 and launch["timedOut"] is False and
            launch["passed"] is True and launch["inputsUnchanged"] is True and launch["durationSeconds"] > 0,
            "Invalid R01B Player launch outcome")
    require(launch["error"] == "", "R01B Player launch reported an error")
    for field in ("unityLogPath", "consoleLogPath"):
        log_path = canonical_file(launch[field], "R01B " + field)
        require(log_path.parent == launch_path.parent, "R01B " + field + " is outside the launch evidence directory")
    result_path = canonical_file(launch["resultPath"], "R01B Player result")
    prefix = "r01b-mixed" if args.mixed else "r01b-capacity"
    require(result_path.parent == launch_path.parent and launch_path.name == prefix + "-player-launch.json" and
            launch["resultSha256"] == digest(result_path), "R01B result path/hash binding differs")
    expected_command = [str(executable), "-batchmode", "-nographics",
                        "-shadowR01BManifest", str(workload_path), "-shadowR01BCorpus", str(corpus),
                        "-shadowR01BOverflowDll", str(overflow_dll),
                        "-shadowR01BOverflowName", overflow["assembly"]["name"],
                        "-shadowR01BOverflowSha256", overflow["assembly"]["sha256"],
                        "-shadowR01BResult", str(result_path), "-logFile", launch["unityLogPath"]]
    early_mode = startup_mode(args.mixed)
    startup_args = ["-shadowEarlyCapsule", launch["capsulePath"],
                    "-shadowEarlyCapsuleSha256", launch["capsuleSha256"], "-shadowEarlyResult",
                    launch["earlyResultPath"]]
    if args.mixed:
        startup_args = ["-shadowR01BMixed"] + startup_args + ["-shadowR01BMixedManifest",
                       str(mixed_manifest), "-shadowR01BMixedCorpus", str(mixed_corpus)]
    expected_command[3:3] = startup_args
    require(launch["command"] == expected_command, "R01B Player command differs")
    require(launch["scenario"] == ("MixedShadowRetainedFailures" if args.mixed else "OrdinaryEnvelope"),
            "R01B launch scenario differs")
    early_mode, capsule_path, early_path = startup_binding(launch, launch_path, args.mixed)
    prepared = early._prepare(project, fixture, on_path, off_path, replay, None, None, [early_mode])
    require(prepared["profile"] == 2, "R01B startup setup requires metadata profile 2")
    early.exact(early.capsule.decode(capsule_path.read_bytes()),
                early.expected_capsule(prepared, early_mode, fixture, "P03"),
                "R01B admitted startup capsule")
    verify_startup_receipt(early_path, capsule_path, early_mode, launch["processId"])

    direct_inputs = collect_direct_inputs(workload_path, workload_files, overflow_path, overflow_dll,
                                          fixture, on_path, off_path, replay, diagnostic["output"])
    direct_inputs.update({diagnostic_path, *diagnostic["inventory"]})
    if mixed_manifest is not None and mixed_corpus is not None:
        direct_inputs.update({mixed_manifest, *mixed_workload_files})
        direct_inputs.update(Path(row["path"]).resolve(strict=True) for row in mixed_workload["shadow"]["assemblies"])
        direct_inputs.update(prepared["inventory"])
        direct_inputs.add(capsule_path)
    else:
        direct_inputs.update(prepared["inventory"])
        direct_inputs.add(capsule_path)
    expected_hashes = {str(path): digest(path) for path in sorted(direct_inputs)}
    require(launch["inputHashesBefore"] == expected_hashes and launch["inputHashesAfter"] == expected_hashes,
            "R01B direct input inventory/hash binding differs")

    result = exact_fields(read_json(result_path), RESULT_FIELDS, "result")
    strict_types(
        result,
        {field for field in RESULT_FIELDS if field not in {
            "kind", "milestone", "result", "error", "memoryMeasurement", "baselineBuildId", "runtimeAbiHash", "unityVersion",
            "platform", "buildGuid", "resultPath", "manifestPath", "manifestSha256", "corpusRoot",
            "mixedManifestPath", "mixedManifestSha256", "mixedCorpusRoot",
            "limitException", "overflowPath", "overflowName", "overflowSha256", "scenario",
            "retainedFailureExceptions", "il2cpp", "initial", "afterRetainedFailures", "before", "at8191",
            "after", "afterRejected"}},
        {"kind", "milestone", "result", "error", "memoryMeasurement", "baselineBuildId", "runtimeAbiHash", "unityVersion",
         "platform", "buildGuid", "resultPath", "manifestPath", "manifestSha256", "corpusRoot", "mixedManifestPath", "mixedManifestSha256", "mixedCorpusRoot", "limitException",
         "overflowPath", "overflowName", "overflowSha256", "scenario"}, {"il2cpp"},
        {"retainedFailureExceptions"}, {"initial", "afterRetainedFailures", "before", "at8191", "after", "afterRejected"},
        "result")
    player = diagnostic["player"]
    require(result["schemaVersion"] == 1 and result["kind"] == "R01BCapacityPlayerResult" and
            result["milestone"] == "R01B" and result["result"] == "Passed" and not result["error"] and
            result["il2cpp"] is True and result["processId"] == launch["processId"] and
            result["buildGuid"] == player["buildGuid"] and result["baselineBuildId"] == player["baselineBuildId"] and
            result["runtimeAbiHash"] == player["runtimeAbiHash"] and result["unityVersion"] == player["unityVersion"] and
            result["platform"] == "OSXPlayer" and result["resultPath"] == str(result_path),
            "R01B Player identity/outcome differs")
    require(result["memoryMeasurement"] == "DarwinMachTaskBasicInfoResidentAndLifetimePeakBytes",
            "R01B memory evidence must use Darwin current RSS and kernel lifetime peak bytes")
    selected_manifest_path = mixed_manifest if mixed_manifest is not None else workload_path
    selected_corpus = mixed_corpus if mixed_corpus is not None else corpus
    require(result["manifestPath"] == str(selected_manifest_path) and result["manifestSha256"] == digest(selected_manifest_path) and
            result["corpusRoot"] == str(selected_corpus) and
            result["mixedManifestPath"] == (str(mixed_manifest) if mixed_manifest is not None else "") and
            result["mixedManifestSha256"] == (digest(mixed_manifest) if mixed_manifest is not None else "") and
            result["mixedCorpusRoot"] == (str(mixed_corpus) if mixed_corpus is not None else "") and
            result["overflowPath"] == str(overflow_dll) and
            result["overflowName"] == overflow["assembly"]["name"] and
            result["overflowSha256"] == overflow["assembly"]["sha256"] and
            result["overflowDllBytes"] == overflow["assembly"]["sizeBytes"], "R01B workload/overflow binding differs")
    expected_shadow = mixed_workload["shadow"]["imageCount"] if args.mixed else 0
    expected_failures = mixed_workload["retainedFailureCount"] if args.mixed else 0
    expected_valid = mixed_workload["ordinary"]["selectedCount"] if args.mixed else IMAGE_COUNT
    selected_rows = mixed_workload["assemblies"] if args.mixed else workload["assemblies"]
    expected_bytes = sum(row["sizeBytes"] for row in selected_rows[:expected_valid])
    require(result["loadedImages"] == expected_valid and result["invokedImages"] == expected_valid and
            result["payloadRvaChecks"] == expected_valid + 4 and result["highRvaFieldChecks"] == 4 and
            result["denseNameChecks"] == 4 and
            result["postRejectionMappingChecks"] == 4 and result["loadedDllBytes"] == expected_bytes and
            result["shadowDllBytes"] == (mixed_workload["shadow"]["validDllBytes"] if args.mixed else 0) and
            result["validDllBytes"] == (mixed_workload["totals"]["validDllBytes"] if args.mixed else TOTAL_DLL_BYTES) and
            result["retainedFailureInputBytes"] == (mixed_workload["failedInputBytes"] if args.mixed else 0) and
            result["scenario"] == ("MixedShadowRetainedFailures" if args.mixed else "OrdinaryEnvelope") and
            result["retainedFailureCount"] == expected_failures and
            type(result["retainedFailureExceptions"]) is list and
            len(result["retainedFailureExceptions"]) == expected_failures and
            all(type(item) is str and item for item in result["retainedFailureExceptions"]) and
            result["validImagesToLoad"] == expected_valid and
            result["loadMilliseconds"] > 0 and result["workingSetBytesBefore"] > 0 and
            result["maximumWorkingSetBytes"] >= result["workingSetBytesBefore"] and result["managedBytesAfter"] >= 0 and
            result["limitException"].startswith("System.ExecutionEngineException: ") and
            "InterpreterImage::AllocImageIndex failed" in result["limitException"],
            "R01B execution observations differ")

    initial, initial_raw = capacity(result["initial"], "initial")
    retained, retained_raw = capacity(result["afterRetainedFailures"], "afterRetainedFailures")
    before, before_raw = capacity(result["before"], "before")
    at8191, at8191_raw = capacity(result["at8191"], "at8191")
    after, after_raw = capacity(result["after"], "after")
    rejected, rejected_raw = capacity(result["afterRejected"], "afterRejected")
    require(initial_raw["lifetimeReservedImageCount"] == expected_shadow and
            initial_raw["remainingImageCount"] == IMAGE_COUNT - expected_shadow and initial_raw["requiredImages"] == 0 and
            initial_raw["acceptedImages"] == 0 and initial_raw["ordinaryAllocatedCount"] == 0 and
            initial_raw["shadowAllocatedCount"] == expected_shadow and initial_raw["reservedShadowImageCount"] == expected_shadow and
            (not args.mixed or initial_raw["reservedPages"] > 0 and initial_raw["mappedPages"] > 0),
            "R01B scenario initial interpreter ledger differs")
    if not args.mixed:
        require(initial_raw["reservedPages"] == 0 and initial_raw["mappedPages"] == 0,
                "Ordinary R01B scenario did not start with an empty page ledger")
    require(retained_raw["lifetimeReservedImageCount"] == expected_shadow + expected_failures and
            retained_raw["remainingImageCount"] == expected_valid and retained_raw["ordinaryAllocatedCount"] == expected_failures and
            retained_raw["shadowAllocatedCount"] == expected_shadow and retained_raw["reservedShadowImageCount"] == expected_shadow and
            retained_raw["reservedPages"] >= initial_raw["reservedPages"] + expected_failures and
            retained_raw["mappedPages"] == initial_raw["mappedPages"],
            "Retained failure accounting differs")
    require(before_raw["lifetimeReservedImageCount"] == expected_shadow + expected_failures and
            before_raw["remainingImageCount"] == expected_valid and before_raw["requiredImages"] == expected_valid and
            before_raw["acceptedImages"] == expected_valid and before_raw["fitsPreliminary"] is True and
            before_raw["aggregateInputDllBytes"] == expected_bytes and
            before_raw["ordinaryAllocatedCount"] == expected_failures and before_raw["shadowAllocatedCount"] == expected_shadow and
            before_raw["reservedShadowImageCount"] == expected_shadow and before_raw["reservedPages"] == retained_raw["reservedPages"] and
            before_raw["mappedPages"] == retained_raw["mappedPages"],
            "Player did not admit the exact remaining ordinary workload")
    require(at8191_raw["lifetimeReservedImageCount"] == IMAGE_COUNT - 1 and at8191_raw["remainingImageCount"] == 1 and
            at8191_raw["requiredImages"] == at8191_raw["acceptedImages"] == 1 and
            at8191_raw["ordinaryAllocatedCount"] == IMAGE_COUNT - 1 - expected_shadow and
            at8191_raw["shadowAllocatedCount"] == expected_shadow and
            at8191_raw["reservedShadowImageCount"] == expected_shadow and at8191_raw["fitsPreliminary"] is True and
            at8191_raw["aggregateInputDllBytes"] == selected_rows[expected_valid - 1]["sizeBytes"],
            "8,191 checkpoint did not admit exactly one final identity")
    require(after_raw["lifetimeReservedImageCount"] == IMAGE_COUNT and
            after_raw["ordinaryAllocatedCount"] == IMAGE_COUNT - expected_shadow and
            after_raw["remainingImageCount"] == after_raw["requiredImages"] == after_raw["acceptedImages"] == 0 and
            after_raw["shadowAllocatedCount"] == expected_shadow and after_raw["reservedShadowImageCount"] == expected_shadow and
            after_raw["fitsPreliminary"] is True and after_raw["failureReason"] == "None" and
            after_raw["firstFailingIndex"] == -1 and after_raw["aggregateInputDllBytes"] == 0 and
            after["freeUsablePages"] >= MINIMUM_FREE_PAGES,
            "8,192 checkpoint does not preserve the selected image/page capacity")
    require(rejected_raw["lifetimeReservedImageCount"] == IMAGE_COUNT and rejected_raw["remainingImageCount"] == 0 and
            rejected_raw["requiredImages"] == 1 and rejected_raw["acceptedImages"] == 0 and
            rejected_raw["firstFailingIndex"] == 0 and rejected_raw["firstFailingSize"] == overflow["assembly"]["sizeBytes"] and
            rejected_raw["failureReason"] == "ImageLimit" and rejected_raw["fitsPreliminary"] is False and
            rejected_raw["aggregateInputDllBytes"] == overflow["assembly"]["sizeBytes"] and
            all(rejected_raw[field] == after_raw[field] for field in ("reservedPages", "mappedPages",
                "lifetimeReservedImageCount", "remainingImageCount", "ordinaryAllocatedCount", "shadowAllocatedCount",
                "reservedShadowImageCount")), "8,193 rejection changed the process-lifetime ledger")
    require(before_raw["reservedPages"] <= at8191_raw["reservedPages"] <= after_raw["reservedPages"] and
            before_raw["mappedPages"] <= at8191_raw["mappedPages"] <= after_raw["mappedPages"],
            "R01B page accounting is not monotonic")

    verify_diagnostic_inputs(project, fixture, on_path, off_path, replay, diagnostic_path)
    summary = {
        "schemaVersion": 1,
        "kind": "R01BCapacityStrictVerification",
        "milestone": "R01B",
        "result": "Passed",
        "launchReceiptPath": str(launch_path),
        "launchReceiptSha256": digest(launch_path),
        "playerResultPath": str(result_path),
        "playerResultSha256": digest(result_path),
        "assemblyCount": IMAGE_COUNT,
        "ordinaryDllBytesLoaded": expected_bytes,
        "supportedEnvelopeDllBytes": TOTAL_DLL_BYTES,
        "shadowDllBytes": mixed_workload["shadow"]["validDllBytes"] if args.mixed else 0,
        "validDllBytes": mixed_workload["totals"]["validDllBytes"] if args.mixed else TOTAL_DLL_BYTES,
        "retainedFailureInputBytes": mixed_workload["failedInputBytes"] if args.mixed else 0,
        "mixedManifestPath": str(mixed_manifest) if mixed_manifest is not None else "",
        "shadowImages": expected_shadow,
        "retainedFailedOrdinaryReservations": expected_failures,
        "reservedPagesAt8192": after_raw["reservedPages"],
        "mappedPagesAt8192": after_raw["mappedPages"],
        "freeUsablePagesAt8192": after["freeUsablePages"],
        "minimumFreePages": MINIMUM_FREE_PAGES,
        "memoryMeasurement": result["memoryMeasurement"],
        "workingSetBytesBefore": result["workingSetBytesBefore"],
        "maximumWorkingSetBytes": result["maximumWorkingSetBytes"],
        "workingSetGrowthBytes": result["maximumWorkingSetBytes"] - result["workingSetBytesBefore"],
        "loadMilliseconds": result["loadMilliseconds"],
        "scope": ("Same-process committed M07 P03 Shadow closure, three retained failed ordinary reservations, remaining valid ordinary loads, exact 512 MiB valid ordinary-plus-Shadow DLL bytes, and exact 8,191/8,192/8,193 boundaries. "
                  if args.mixed else "Real ordinary Assembly.Load path: 8,191/8,192/8,193 boundaries. ") +
                 "All loaded fixture methods and initialized RVA fields, four high-offset RVA fields, four dense cross-page names, and post-rejection mappings were checked.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
