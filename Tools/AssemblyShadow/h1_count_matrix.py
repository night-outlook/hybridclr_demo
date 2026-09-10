"""Independently aggregate authenticated H1 count cell reports."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid


SHA256 = re.compile(r"^[0-9a-f]{64}$")
PATHS = (("Ordinary-ON", True), ("Ordinary-OFF", False), ("Shadow-ON", True))
CONFIGS = ("Debug", "Release")
PARAMETER_CASES = (
    ("H1R-P01-a", "Accepted"), ("H1R-P01-b", "Accepted"),
    ("H1R-P01-c", "Accepted"), ("H1R-P01-d", "Accepted"),
    ("H1R-P02-a", "ControlledRejected"), ("H1R-P02-b", "ControlledRejected"),
    ("H1R-P03-a", "ControlledRejected"), ("H1R-P03-b", "ControlledRejected"),
)
PARAMETER_VARIANTS = (
    ("H1R-P04-return255", "Accepted"), ("H1R-P04-partial-names", "Accepted"),
    ("H1R-P04-instance", "Accepted"), ("H1R-P04-mixed-kinds", "Accepted"),
)
NESTED_CASES = (
    ("H1R-N01-a", "Accepted"), ("H1R-N01-b", "Accepted"),
    ("H1R-N01-c", "Accepted"), ("H1R-N01-d", "Accepted"),
    ("H1R-N02-a", "ControlledRejected"), ("H1R-N02-b", "ControlledRejected"),
)
NESTED_VARIANTS = (
    ("H1R-N03-interleaved", "Accepted"),
    ("H1R-N04-adjacent-valid", "Accepted"),
    ("H1R-N04-adjacent-overflow", "ControlledRejected"),
    ("H1R-N05-final-repeat", "Accepted"),
)
CASE_TABLES = {
    "parameters": PARAMETER_CASES + PARAMETER_VARIANTS,
    "nested": NESTED_CASES + NESTED_VARIANTS,
}


class MatrixError(ValueError):
    """An unauthenticated, incomplete, or unstable matrix input."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def _sha(value: object, label: str) -> str:
    _require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
             label + " must be a lowercase SHA-256")
    return value


def _file(path_value: object, label: str) -> Path:
    _require(isinstance(path_value, (str, Path)) and str(path_value), label + " path is missing")
    path = Path(path_value)
    _require(path.is_absolute() and path == path.resolve() and path.is_file() and
             not path.is_symlink(), label + " must be an existing canonical file")
    for parent in path.parents:
        _require(not parent.is_symlink() and parent == parent.resolve(),
                 label + " has a symlinked or noncanonical parent")
    return path


def _digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        _require(key not in value, "duplicate JSON key: " + str(key))
        value[key] = item
    return value


def _read(path: Path, label: str) -> tuple[dict, bytes]:
    data = path.read_bytes()
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError) as error:
        raise MatrixError(label + " is not valid JSON: " + str(error)) from error
    _require(type(value) is dict, label + " must be a JSON object")
    return value, data


def canonical_cell_id(family: str, case_id: str, path_name: str, cpp: str) -> str:
    return f"{family}/{case_id}/{path_name}/{cpp}"


def required_cells() -> dict[str, dict]:
    cells = {}
    for family, cases in CASE_TABLES.items():
        for case_id, outcome in cases:
            for path_name, feature in PATHS:
                for cpp in CONFIGS:
                    cell_id = canonical_cell_id(family, case_id, path_name, cpp)
                    cells[cell_id] = {"family": family, "caseId": case_id,
                                      "pathName": path_name, "featureEnabled": feature,
                                      "cppConfiguration": cpp, "expectedOutcome": outcome}
    _require(len(cells) == 132, "canonical H1 matrix must contain 132 cells")
    return cells


def _validate_fixture_inputs(path: Path, audit_path: Path, family: str) -> tuple[dict, dict, str, str]:
    manifest, manifest_bytes = _read(path, family + " fixture manifest")
    audit, audit_bytes = _read(audit_path, family + " fixture audit")
    expected_cases = [case_id for case_id, _ in CASE_TABLES[family]]
    _require(manifest.get("schemaVersion") == 1 and
             manifest.get("kind") == "H1CountFixtureManifest" and
             manifest.get("family") == family and manifest.get("caseSet") == "all",
             family + " fixture manifest identity differs")
    _require([case.get("caseId") for case in manifest.get("cases", [])] == expected_cases,
             family + " fixture manifest case set differs")
    _require(audit.get("schemaVersion") == 1 and audit.get("result") == "Passed" and
             audit.get("family") == family and audit.get("caseSet") == "all",
             family + " fixture audit identity differs")
    _require(audit.get("requestedCaseIds") == expected_cases and
             audit.get("executedCaseIds") == expected_cases,
             family + " fixture audit coverage differs")
    binding = audit.get("sourceBinding")
    _require(isinstance(binding, dict) and binding.get("manifestPath") == str(path) and
             binding.get("manifestSha256") == hashlib.sha256(manifest_bytes).hexdigest(),
             family + " fixture audit is bound to a different manifest")
    return manifest, audit, hashlib.sha256(manifest_bytes).hexdigest(), hashlib.sha256(audit_bytes).hexdigest()


def _manifest_case(manifest: dict, case_id: str) -> dict:
    matches = [case for case in manifest["cases"] if case.get("caseId") == case_id]
    _require(len(matches) == 1, "fixture manifest case is absent or duplicated: " + case_id)
    return matches[0]


def _load_evidence_verifier():
    try:
        from h1_count_results import verify_evidence
    except (ImportError, AttributeError) as error:
        raise MatrixError("h1_count_results.verify_evidence is required by the matrix verifier") from error
    return verify_evidence


def _verify_cell(entry: dict, expected: dict, manifests: dict[str, tuple[dict, str, Path, Path, str]],
                 seen_reports: set[Path], seen_launches: set[Path], seen_runs: set[str],
                 seen_builds: dict[tuple[bool, str], tuple[Path, str]],
                 seen_source_pins: dict[tuple[bool, str], Path],
                 shared_build_identity: dict[str, str], evidence_verifier) -> dict:
    startup_rejected = (expected["pathName"] == "Shadow-ON" and
                        expected["expectedOutcome"] == "ControlledRejected")
    _require(set(entry) == {"cellId", "report"}, "cell index entry has unexpected fields")
    _require(entry.get("cellId") == next(cell_id for cell_id, value in required_cells().items()
                                          if value == expected), "cell ID does not match its canonical tuple")
    report_ref = entry["report"]
    _require(isinstance(report_ref, dict) and set(report_ref) == {"path", "sha256"},
             "cell report reference is malformed")
    report_path = _file(report_ref.get("path"), "cell report")
    report_hash = _sha(report_ref.get("sha256"), "cell report hash")
    _require(_digest(report_path) == report_hash, "cell report hash differs: " + str(report_path))
    _require(report_path not in seen_reports, "cell report path is reused")
    seen_reports.add(report_path)
    report, _ = _read(report_path, "cell report")
    _require(report.get("kind") == "H1CountResultVerification" and report.get("result") == "Passed",
             "cell report is not a passed H1 verification")
    if "status" in report:
        _require(report["status"] == "Passed", "cell report status is not Passed")
    requested = report.get("requested")
    _require(isinstance(requested, dict) and
             requested.get("family") == expected["family"] and
             requested.get("caseId") == expected["caseId"] and
             requested.get("pathName") == expected["pathName"] and
             requested.get("cppConfiguration") == expected["cppConfiguration"],
             "cell report requested tuple differs")
    executed = report.get("executed")
    _require(isinstance(executed, dict) and
             executed.get("family") == expected["family"] and
             executed.get("caseId") == expected["caseId"] and
             executed.get("path") == expected["pathName"].split("-")[0].lower(),
             "cell report executed tuple differs")
    semantic = report.get("semantic")
    _require(isinstance(semantic, dict) and semantic.get("expectedOutcome") == expected["expectedOutcome"],
             "cell report expected outcome differs")
    launch_ref = (report.get("inputs") or {}).get("launchReceipt")
    _require(isinstance(launch_ref, dict) and set(launch_ref) == {"path", "sha256"},
             "cell report launch reference is missing")
    launch_path = _file(launch_ref.get("path"), "launch receipt")
    launch_hash = _sha(launch_ref.get("sha256"), "launch receipt hash")
    _require(_digest(launch_path) == launch_hash, "launch receipt hash differs: " + str(launch_path))
    _require(launch_path not in seen_launches, "launch receipt path is reused")
    seen_launches.add(launch_path)
    launch, _ = _read(launch_path, "launch receipt")
    _require(launch.get("kind") == "H1CountPlayerLaunchReceipt" and
             launch.get("diagnosticOnly") is True and launch.get("passed") is True and
             launch.get("timedOut") is False and launch.get("crashed") is False and
             launch.get("signalTerminated") is False and
             launch.get("launcherInitiatedTermination") is False and launch.get("error") == "" and
             launch.get("inputsUnchanged") is True and
             isinstance(launch.get("processId"), int) and launch["processId"] > 0,
             "launch receipt is failed, unstable, or incomplete")
    _require((launch.get("exitCode") == 1 and launch.get("processFailed") is True) if startup_rejected else
             (launch.get("exitCode") == 0 and launch.get("processFailed") is False),
             "launch exit/process status differs from the requested startup outcome")
    _require(executed.get("processId") == launch.get("processId") and
             executed.get("buildGuid") == launch.get("buildGuid"),
             "cell report executed PID/build GUID differs from launch receipt")
    try:
        run_id = str(uuid.UUID(launch.get("runId", "")))
    except (ValueError, AttributeError) as error:
        raise MatrixError("launch receipt runId is invalid") from error
    _require(run_id not in seen_runs, "launch runId is reused")
    seen_runs.add(run_id)
    _require(launch.get("family") == expected["family"] and launch.get("caseId") == expected["caseId"] and
             launch.get("path") == expected["pathName"].split("-")[0].lower() and
             launch.get("cppConfiguration") == expected["cppConfiguration"] and
             launch.get("featureEnabled") is expected["featureEnabled"] and
             launch.get("mode") == expected["pathName"].split("-")[0].capitalize() +
             ("On" if expected["featureEnabled"] else "Off"),
             "launch receipt tuple or feature/configuration differs")
    manifest, manifest_hash, manifest_path, audit_path, audit_hash = manifests[expected["family"]]
    _require(launch.get("fixtureManifestPath") == str(manifest_path) and
             launch.get("fixtureManifestSha256") == manifest_hash and
             launch.get("fixtureAuditPath") == str(audit_path) and
             launch.get("fixtureAuditSha256") == audit_hash,
             "launch receipt fixture source binding differs")
    build_path = _file(launch.get("buildReceiptPath"), "build receipt")
    build_hash = _sha(launch.get("buildReceiptSha256"), "build receipt hash")
    _require(_digest(build_path) == build_hash, "build receipt hash differs: " + str(build_path))
    build, _ = _read(build_path, "build receipt")
    _require(build.get("kind") == "H1CountDiagnosticPlayerBuild" and
             build.get("diagnosticOnly") is True and
             build.get("cppConfiguration") == expected["cppConfiguration"] and
             build.get("featureEnabled") is expected["featureEnabled"] and
             build.get("buildGuid") == launch.get("buildGuid"),
             "build receipt tuple differs from the requested cell")
    build_key = (expected["featureEnabled"], expected["cppConfiguration"])
    for prior_key, (prior_path, prior_hash) in seen_builds.items():
        if prior_key != build_key:
            _require(build_path != prior_path and build_hash != prior_hash,
                     "one build receipt is claimed by multiple feature/configuration tuples")
    if build_key in seen_builds:
        _require(seen_builds[build_key] == (build_path, build_hash),
                 "a feature/configuration cell uses more than one build receipt")
    seen_builds[build_key] = (build_path, build_hash)
    for field in ("sourcePinsJson", "runtimeAbiHash", "sourcePinSha256"):
        _require(isinstance(build.get(field), str) and build[field],
                 "build receipt shared identity field is missing: " + field)
        if field in ("runtimeAbiHash", "sourcePinSha256"):
            _sha(build[field], "build receipt " + field)
        if field in shared_build_identity:
            _require(shared_build_identity[field] == build[field],
                     "build receipt shared source/runtime identity differs: " + field)
        else:
            shared_build_identity[field] = build[field]
    source_pin = _file(build.get("sourcePinFile"), "build source pin")
    if build_key in seen_source_pins:
        _require(seen_source_pins[build_key] == source_pin,
                 "a feature/configuration build changed its source pin path")
    else:
        seen_source_pins[build_key] = source_pin
    _require(_digest(source_pin) == build["sourcePinSha256"] and
             source_pin.read_text(encoding="utf-8") == build["sourcePinsJson"],
             "build source pin bytes differ from shared build identity")
    _sha(build.get("inputSnapshotHash"), "build input snapshot hash")
    for path_field, hash_field in (("playerExecutable", "playerExecutableSha256"),
                                   ("nativeLibraryPath", "nativeLibrarySha256"),
                                   ("nativeMetadataPath", "nativeMetadataSha256")):
        binary = _file(build.get(path_field), "build " + path_field)
        binary_hash = _sha(build.get(hash_field), "build " + hash_field)
        _require(_digest(binary) == binary_hash,
                 "fresh " + path_field + " bytes differ from build receipt")
    case = _manifest_case(manifest, expected["caseId"])
    flavor = "ordinary" if expected["pathName"].startswith("Ordinary") else "shadow"
    artifact = case[flavor]
    fixture = _file(launch.get("fixturePath"), "fixture DLL")
    _require(fixture == Path(artifact["path"]) and _digest(fixture) == artifact["sha256"] and
             launch.get("fixtureDllSha256") == artifact["sha256"],
             "launch fixture is not bound to the explicit manifest artifact")
    if startup_rejected:
        early_path = _file(launch.get("earlyResultPath"), "early startup result")
        early_hash = _sha(launch.get("earlyResultSha256"), "early startup result hash")
        _require(_digest(early_path) == early_hash and executed.get("earlyResultPath") == str(early_path),
                 "early startup result differs from launch/report binding")
        _require(launch.get("resultSha256") in (None, "") and
                 isinstance(launch.get("resultPath"), str) and launch.get("resultPath") and
                 not Path(launch["resultPath"]).exists(),
                 "startup-rejected cell unexpectedly produced a scene result")
        early_result, _ = _read(early_path, "early startup result")
        _require(early_result.get("schemaVersion") == 1 and
                 early_result.get("kind") == "H1CountEarlyStartupResult" and
                 early_result.get("result") == "ExpectedValidationRejection" and
                 early_result.get("callbackReturnCode") == 1 and early_result.get("committed") is False and
                 early_result.get("family") == expected["family"] and
                 early_result.get("caseId") == expected["caseId"] and
                 early_result.get("path") == "shadow" and
                 early_result.get("processId") == launch.get("processId"),
                 "early startup raw result is not bound to the authenticated launch")
        _require(executed.get("result") == early_result.get("result") and
                 executed.get("expectedOutcome") == expected["expectedOutcome"],
                 "cell report executed startup outcome differs")
    else:
        result_path = _file(launch.get("resultPath"), "diagnostic result")
        result_hash = _sha(launch.get("resultSha256"), "diagnostic result hash")
        _require(_digest(result_path) == result_hash,
                 "diagnostic result hash differs from launch receipt")
        _require(executed.get("resultPath") == str(result_path),
                 "cell report executed result path differs from launch receipt")
        raw_result, _ = _read(result_path, "diagnostic result")
        _require(raw_result.get("schemaVersion") == 1 and
                 raw_result.get("kind") == "H1CountDiagnosticResult" and
                 raw_result.get("result") == "Passed" and
                 raw_result.get("family") == expected["family"] and
                 raw_result.get("caseId") == expected["caseId"] and
                 raw_result.get("path") == expected["pathName"].split("-")[0].lower() and
                 raw_result.get("processId") == launch.get("processId") and
                 raw_result.get("buildGuid") == launch.get("buildGuid") and
                 raw_result.get("expectedOutcome") == expected["expectedOutcome"],
                 "diagnostic raw result is not bound to the authenticated launch")
        _require(executed.get("result") == raw_result.get("result"),
                 "cell report executed result differs from diagnostic raw result")
        if "expectedOutcome" in executed:
            _require(executed["expectedOutcome"] == raw_result.get("expectedOutcome"),
                     "cell report executed outcome differs from diagnostic raw result")
        if "resultPath" in raw_result:
            _require(raw_result["resultPath"] == str(result_path),
                     "diagnostic raw result path differs from launch receipt")
    request = {"family": expected["family"], "caseId": expected["caseId"],
               "pathName": expected["pathName"], "cppConfiguration": expected["cppConfiguration"]}
    evidence = evidence_verifier(launch_path, request)
    _require(isinstance(evidence, dict) and evidence.get("result") == "Passed",
             "per-cell evidence verifier did not pass")
    return {"cellId": entry["cellId"], "reportSha256": report_hash,
            "launchReceiptSha256": launch_hash, "buildReceiptSha256": build_hash,
            "runId": run_id}


def verify_matrix(result_index: Path, output: Path, parameter_manifest: Path,
                  parameter_audit: Path, nested_manifest: Path, nested_audit: Path,
                  evidence_verifier=None) -> int:
    report = {"schemaVersion": 1, "kind": "H1CountMatrixVerification", "result": "Failed"}
    try:
        index, index_bytes = _read(_file(result_index, "result index"), "result index")
        _require(index.get("schemaVersion") == 1 and index.get("kind") == "H1CountResultIndex" and
                 isinstance(index.get("cells"), list), "result index header differs")
        parameter, audit_p, parameter_hash, audit_hash_p = _validate_fixture_inputs(
            _file(parameter_manifest, "parameter manifest"), _file(parameter_audit, "parameter audit"), "parameters")
        nested, audit_n, nested_hash, audit_hash_n = _validate_fixture_inputs(
            _file(nested_manifest, "nested manifest"), _file(nested_audit, "nested audit"), "nested")
        manifests = {
            "parameters": (parameter, parameter_hash, _file(parameter_manifest, "parameter manifest"),
                            _file(parameter_audit, "parameter audit"), audit_hash_p),
            "nested": (nested, nested_hash, _file(nested_manifest, "nested manifest"),
                        _file(nested_audit, "nested audit"), audit_hash_n),
        }
        expected = required_cells()
        entries = index["cells"]
        ids = [entry.get("cellId") for entry in entries if isinstance(entry, dict)]
        _require(len(entries) == len(ids) and len(ids) == len(set(ids)),
                 "result index contains missing or duplicate cell IDs")
        _require(set(ids) == set(expected), "result index has missing or extra canonical cells")
        seen_reports: set[Path] = set()
        seen_launches: set[Path] = set()
        seen_runs: set[str] = set()
        seen_builds: dict[tuple[bool, str], tuple[Path, str]] = {}
        seen_source_pins: dict[tuple[bool, str], Path] = {}
        shared_build_identity: dict[str, str] = {}
        evidence_verifier = evidence_verifier or _load_evidence_verifier()
        verified = []
        for entry in entries:
            cell_id = entry["cellId"]
            verified.append(_verify_cell(entry, expected[cell_id], manifests, seen_reports,
                                         seen_launches, seen_runs, seen_builds,
                                         seen_source_pins,
                                         shared_build_identity, evidence_verifier))
        _require(set(seen_builds) == {(True, "Debug"), (True, "Release"),
                                      (False, "Debug"), (False, "Release")},
                 "matrix does not contain exactly four shared feature/configuration builds")
        report.update({"result": "Passed", "status": "Passed", "cellCount": len(verified),
                       "expectedCellCount": len(expected), "cells": sorted(verified, key=lambda x: x["cellId"]),
                       "inputs": {"resultIndex": {"path": str(result_index),
                                                    "sha256": hashlib.sha256(index_bytes).hexdigest()},
                                  "parameterManifest": {"path": str(parameter_manifest), "sha256": parameter_hash},
                                  "parameterAudit": {"path": str(parameter_audit), "sha256": audit_hash_p},
                                  "nestedManifest": {"path": str(nested_manifest), "sha256": nested_hash},
                                  "nestedAudit": {"path": str(nested_audit), "sha256": audit_hash_n}}})
    except Exception as error:
        report["failure"] = {"class": type(error).__name__, "message": str(error)}
    _require(output.is_absolute() and output == output.resolve() and not output.exists() and
             output.parent.is_dir() and output.parent == output.parent.resolve(),
             "aggregate output must be a new canonical file")
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return 0 if report["result"] == "Passed" else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--parameter-manifest", required=True, type=Path)
    parser.add_argument("--parameter-audit", required=True, type=Path)
    parser.add_argument("--nested-manifest", required=True, type=Path)
    parser.add_argument("--nested-audit", required=True, type=Path)
    args = parser.parse_args(argv)
    return verify_matrix(args.result_index, args.output, args.parameter_manifest, args.parameter_audit,
                         args.nested_manifest, args.nested_audit)


if __name__ == "__main__":
    raise SystemExit(main())
