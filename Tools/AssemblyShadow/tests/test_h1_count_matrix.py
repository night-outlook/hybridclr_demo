import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "h1_count_matrix.py"


def load_matrix():
    spec = importlib.util.spec_from_file_location("h1_count_matrix", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load matrix verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class H1CountMatrixTests(unittest.TestCase):
    def make_fixture_set(self, root, matrix):
        source_pin = root / "source-pins.json"
        source_pin.write_text('{"schemaVersion":1,"source":"synthetic"}\n', encoding="utf-8")
        manifests = {}
        audits = {}
        for family, cases in matrix.CASE_TABLES.items():
            manifest_cases = []
            for case_id, outcome in cases:
                artifacts = {}
                for flavor in ("ordinary", "shadow"):
                    fixture = root / f"{family}-{case_id}-{flavor}.dll"
                    fixture.write_bytes(f"{family}:{case_id}:{flavor}".encode("utf-8"))
                    artifacts[flavor] = {"path": str(fixture), "sha256": sha(fixture)}
                manifest_cases.append({"caseId": case_id, "expected": outcome,
                                       "ordinary": artifacts["ordinary"], "shadow": artifacts["shadow"]})
            manifest = root / f"{family}-manifest.json"
            write_json(manifest, {"schemaVersion": 1, "kind": "H1CountFixtureManifest",
                                  "family": family, "caseSet": "all", "cases": manifest_cases})
            audit = root / f"{family}-audit.json"
            ids = [case_id for case_id, _ in cases]
            write_json(audit, {"schemaVersion": 1, "kind": "H1CountFixtureShapeAudit",
                               "family": family, "caseSet": "all", "result": "Passed",
                               "requestedCaseIds": ids, "executedCaseIds": ids,
                               "cases": [], "sourceBinding": {
                                   "manifestPath": str(manifest), "manifestSha256": sha(manifest)}})
            manifests[family] = manifest
            audits[family] = audit
        return manifests, audits

    def make_index(self, root, matrix, manifests, audits):
        entries = []
        builds = {}
        source_pins_json = (root / "source-pins.json").read_text(encoding="utf-8")
        for cell_id, expected in matrix.required_cells().items():
            family = expected["family"]
            case_id = expected["caseId"]
            flavor = "ordinary" if expected["pathName"].startswith("Ordinary") else "shadow"
            case = next(case for case in json.loads(manifests[family].read_text())["cases"]
                        if case["caseId"] == case_id)
            fixture = Path(case[flavor]["path"])
            build_key = (expected["featureEnabled"], expected["cppConfiguration"])
            if build_key not in builds:
                build = root / ("build-" + ("on" if build_key[0] else "off") +
                                "-" + build_key[1] + ".json")
                build_guid = str(uuid.uuid4())
                executable = root / ("player-" + ("on" if build_key[0] else "off") +
                                     "-" + build_key[1] + ".bin")
                native_library = root / ("native-" + ("on" if build_key[0] else "off") +
                                         "-" + build_key[1] + ".dylib")
                native_metadata = root / ("metadata-" + ("on" if build_key[0] else "off") +
                                          "-" + build_key[1] + ".dat")
                for binary in (executable, native_library, native_metadata):
                    binary.write_bytes(binary.name.encode("utf-8"))
                source_pin = root / ("source-pins-" + ("on" if build_key[0] else "off") +
                                     "-" + build_key[1] + ".json")
                source_pin.write_text(source_pins_json, encoding="utf-8")
                snapshot_hash = hashlib.sha256(("snapshot-" + str(build_key)).encode("utf-8")).hexdigest()
                write_json(build, {"schemaVersion": 1, "kind": "H1CountDiagnosticPlayerBuild",
                                   "diagnosticOnly": True, "cppConfiguration": expected["cppConfiguration"],
                                   "featureEnabled": expected["featureEnabled"], "buildGuid": build_guid,
                                   "sourcePinsJson": source_pins_json, "runtimeAbiHash": "a" * 64,
                                   "inputSnapshotHash": snapshot_hash,
                                   "sourcePinFile": str(source_pin), "sourcePinSha256": sha(source_pin),
                                   "playerExecutable": str(executable), "playerExecutableSha256": sha(executable),
                                   "nativeLibraryPath": str(native_library), "nativeLibrarySha256": sha(native_library),
                                   "nativeMetadataPath": str(native_metadata), "nativeMetadataSha256": sha(native_metadata)})
                builds[build_key] = (build, build_guid)
            build, build_guid = builds[build_key]
            launch = root / (cell_id.replace("/", "_") + ".launch.json")
            result_path = root / (cell_id.replace("/", "_") + ".result.json")
            process_id = len(entries) + 1000
            startup_rejected = flavor == "shadow" and expected["expectedOutcome"] == "ControlledRejected"
            early_path = root / (cell_id.replace("/", "_") + ".early.json")
            if startup_rejected:
                write_json(early_path, {"schemaVersion": 1, "kind": "H1CountEarlyStartupResult",
                                        "result": "ExpectedValidationRejection", "callbackReturnCode": 1,
                                        "committed": False, "family": family, "caseId": case_id,
                                        "path": "shadow", "processId": process_id})
            else:
                write_json(result_path, {"schemaVersion": 1, "kind": "H1CountDiagnosticResult", "result": "Passed",
                                         "family": family, "caseId": case_id, "path": flavor,
                                         "processId": process_id, "buildGuid": build_guid,
                                         "expectedOutcome": expected["expectedOutcome"],
                                         "resultPath": str(result_path)})
            launch_value = {
                "schemaVersion": 1, "kind": "H1CountPlayerLaunchReceipt", "diagnosticOnly": True,
                "runId": str(uuid.uuid4()), "processId": process_id,
                "family": family, "caseId": case_id,
                "path": flavor, "mode": expected["pathName"].split("-")[0].capitalize() +
                ("On" if expected["featureEnabled"] else "Off"),
                "cppConfiguration": expected["cppConfiguration"],
                "featureEnabled": expected["featureEnabled"], "passed": True,
                "timedOut": False, "crashed": False, "signalTerminated": False,
                "processFailed": startup_rejected, "launcherInitiatedTermination": False,
                "error": "", "inputsUnchanged": True, "inputHashesBefore": {},
                "inputHashesAfter": {}, "exitCode": 1 if startup_rejected else 0, "buildGuid": build_guid,
                "buildReceiptPath": str(build), "buildReceiptSha256": sha(build),
                "fixtureManifestPath": str(manifests[family]),
                "fixtureManifestSha256": sha(manifests[family]),
                "fixtureAuditPath": str(audits[family]), "fixtureAuditSha256": sha(audits[family]),
                "fixturePath": str(fixture), "fixtureDllSha256": sha(fixture),
                "resultPath": str(result_path), "resultSha256": "" if startup_rejected else sha(result_path),
                "earlyResultPath": str(early_path),
                "earlyResultSha256": sha(early_path) if startup_rejected else "",
            }
            write_json(launch, launch_value)
            report = root / (cell_id.replace("/", "_") + ".report.json")
            write_json(report, {"schemaVersion": 1, "kind": "H1CountResultVerification",
                                "result": "Passed", "status": "Passed",
                                "requested": {"family": family, "caseId": case_id,
                                               "pathName": expected["pathName"],
                                               "cppConfiguration": expected["cppConfiguration"]},
                                "semantic": {"expectedOutcome": expected["expectedOutcome"]},
                                "executed": {"family": family, "caseId": case_id, "path": flavor,
                                              "processId": process_id, "buildGuid": build_guid,
                                              "result": ("ExpectedValidationRejection" if startup_rejected else "Passed"),
                                              "expectedOutcome": expected["expectedOutcome"],
                                              **({"earlyResultPath": str(early_path)} if startup_rejected else
                                                 {"resultPath": str(result_path)})},
                                "inputs": {"launchReceipt": {"path": str(launch), "sha256": sha(launch)}}})
            entries.append({"cellId": cell_id, "report": {"path": str(report), "sha256": sha(report)}})
        index = root / "result-index.json"
        write_json(index, {"schemaVersion": 1, "kind": "H1CountResultIndex", "cells": entries})
        return index

    def run_matrix(self, root, matrix, index, manifests, audits, name):
        output = root / (name + ".json")
        code = matrix.verify_matrix(index, output, manifests["parameters"], audits["parameters"],
                                    manifests["nested"], audits["nested"],
                                    evidence_verifier=lambda launch_path, request: {"result": "Passed"})
        return code, json.loads(output.read_text(encoding="utf-8"))

    def test_complete_132_cell_matrix_passes(self):
        matrix = load_matrix()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            manifests, audits = self.make_fixture_set(root, matrix)
            index = self.make_index(root, matrix, manifests, audits)
            code, report = self.run_matrix(root, matrix, index, manifests, audits, "positive")
            self.assertEqual(0, code, report.get("failure"))
            self.assertEqual("Passed", report["result"])
            self.assertEqual(132, report["cellCount"])

    def test_missing_duplicate_and_extra_cells_fail(self):
        matrix = load_matrix()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            manifests, audits = self.make_fixture_set(root, matrix)
            index = self.make_index(root, matrix, manifests, audits)
            value = json.loads(index.read_text())
            value["cells"].append(value["cells"][0])
            write_json(index, value)
            code, _ = self.run_matrix(root, matrix, index, manifests, audits, "duplicate")
            self.assertEqual(1, code)

            value["cells"].pop()
            value["cells"].pop()
            write_json(index, value)
            code, _ = self.run_matrix(root, matrix, index, manifests, audits, "missing")
            self.assertEqual(1, code)

            value = json.loads(index.read_text())
            value["cells"][-1]["cellId"] = "parameters/H1R-P99/Ordinary-ON/Debug"
            write_json(index, value)
            code, _ = self.run_matrix(root, matrix, index, manifests, audits, "extra")
            self.assertEqual(1, code)

    def test_wrong_build_hash_and_failed_status_fail(self):
        matrix = load_matrix()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            manifests, audits = self.make_fixture_set(root, matrix)
            index = self.make_index(root, matrix, manifests, audits)
            value = json.loads(index.read_text())
            first = value["cells"][0]
            report = Path(first["report"]["path"])
            report_value = json.loads(report.read_text())
            launch = Path(report_value["inputs"]["launchReceipt"]["path"])
            launch_value = json.loads(launch.read_text())
            build = Path(launch_value["buildReceiptPath"])
            build_value = json.loads(build.read_text())
            build_value["cppConfiguration"] = "Release" if build_value["cppConfiguration"] == "Debug" else "Debug"
            write_json(build, build_value)
            launch_value["buildReceiptSha256"] = sha(build)
            write_json(launch, launch_value)
            report_value["inputs"]["launchReceipt"]["sha256"] = sha(launch)
            write_json(report, report_value)
            first["report"]["sha256"] = sha(report)
            write_json(index, value)
            code, _ = self.run_matrix(root, matrix, index, manifests, audits, "wrong-build")
            self.assertEqual(1, code)
            report_value["result"] = "Failed"
            write_json(report, report_value)
            first["report"]["sha256"] = "0" * 64
            write_json(index, value)
            code, _ = self.run_matrix(root, matrix, index, manifests, audits, "bad-hash")
            self.assertEqual(1, code)

            failed_root = root / "failed"
            failed_root.mkdir()
            manifests, audits = self.make_fixture_set(failed_root, matrix)
            index = self.make_index(failed_root, matrix, manifests, audits)
            value = json.loads(index.read_text())
            report = Path(value["cells"][0]["report"]["path"])
            report_value = json.loads(report.read_text())
            report_value["result"] = "Failed"
            write_json(report, report_value)
            value["cells"][0]["report"]["sha256"] = sha(report)
            write_json(index, value)
            code, _ = self.run_matrix(failed_root, matrix, index, manifests, audits, "failed-status")
            self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
