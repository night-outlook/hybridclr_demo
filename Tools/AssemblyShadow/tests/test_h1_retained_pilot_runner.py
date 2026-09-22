import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "Tools/AssemblyShadow"
sys.path.insert(0, str(TOOLS))

import h1_graph_reuse as reuse
from shadow_tools import VerificationError

_driver_spec = importlib.util.spec_from_file_location(
    "h1_retained_pilot_driver", TOOLS / "run-h1-paired-performance.py")
driver = importlib.util.module_from_spec(_driver_spec)
_driver_spec.loader.exec_module(driver)

_seal_spec = importlib.util.spec_from_file_location(
    "h1_retained_pilot_seal", TOOLS / "seal-h1-pilot-verification.py")
seal = importlib.util.module_from_spec(_seal_spec)
_seal_spec.loader.exec_module(seal)

_admission_spec = importlib.util.spec_from_file_location(
    "h1_retained_pilot_admission", TOOLS / "verify-h1-retained-pilot-admission.py")
admission = importlib.util.module_from_spec(_admission_spec)
_admission_spec.loader.exec_module(admission)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def bind(path: Path) -> dict:
    return {"path": str(path), "sha256": sha(path)}


class H1RetainedPilotRunnerTests(unittest.TestCase):
    EXPECTED_RETAINED_RUNNER_SHA = "afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c"

    def fixture(self, root: Path):
        protocol = write_json(root / "protocol.json", {"kind": "protocol"})
        schedule_rows = [
            {
                "pairId": f"pilot-{index}",
                "mode": mode,
                "phase": "pilot",
                "order": ["A", "B"],
            }
            for index, mode in enumerate(driver.MODES)
        ]
        schedule = write_json(root / "schedule.json", {"pairs": schedule_rows})
        build_map = write_json(root / "build-map.json", {"kind": "map"})
        bridge = write_json(root / "bridge.json", {"projectRoot": str(ROOT.resolve())})

        retained_runner = reuse.retained_pilot_runner_binding(ROOT.resolve())
        self.assertEqual(retained_runner["sha256"], self.EXPECTED_RETAINED_RUNNER_SHA)
        self.assertNotEqual(retained_runner, driver.runner_binding())

        side_projects = {"A": root / "reference", "B": ROOT.resolve()}
        side_projects["A"].mkdir()
        build = {"sides": {}}
        attempts = []
        for side in driver.SIDES:
            fixture = write_json(root / f"fixture-{side}.json", {})
            replay = write_json(root / f"replay-{side}.json", {})
            on = write_json(root / f"on-{side}.json", {})
            off = write_json(root / f"off-{side}.json", {})
            build["sides"][side] = {
                "projectRoot": side_projects[side],
                "fixtureManifest": fixture,
                "replayReceipt": replay,
                "builds": {
                    "on": {"receipt": on},
                    "off": {"receipt": off},
                },
            }

        for pair in schedule_rows:
            attempt = {
                "pairId": pair["pairId"],
                "attempt": 1,
                "mode": pair["mode"],
                "phase": "pilot",
                "status": "Passed",
            }
            for side in driver.SIDES:
                graph = root / f"{pair['pairId']}-{side}-graph.bin"
                graph.write_bytes((pair["pairId"] + side).encode())
                result = write_json(root / f"{pair['pairId']}-{side}-result.json", {"passed": True})
                side_build = build["sides"][side]
                launch = write_json(root / f"{pair['pairId']}-{side}-launch.json", {
                    "schemaVersion": 2,
                    "milestone": "R00",
                    "projectRoot": str(side_build["projectRoot"]),
                    "fixtureManifestPath": str(side_build["fixtureManifest"]),
                    "nativeOnReceipt": str(side_build["builds"]["on"]["receipt"]),
                    "nativeOffReceipt": str(side_build["builds"]["off"]["receipt"]),
                    "editorReplayReceipt": str(side_build["replayReceipt"]),
                    "inputHashesBefore": {str(graph): sha(graph)},
                    "inputHashesAfter": {str(graph): sha(graph)},
                    "processLaunches": [{
                        "mode": pair["mode"],
                        "resultPath": str(result),
                        "resultSha256": sha(result),
                        "earlyCapsulePath": "",
                        "earlyCapsuleSha256": "",
                        "earlyResultPath": "",
                        "earlyResultSha256": "",
                    }],
                })
                attempt[side] = {
                    "status": "Passed",
                    "runner": dict(retained_runner),
                    "launchReceipt": bind(launch),
                }
            attempts.append(attempt)

        prior = write_json(root / "pilot-index.json", {
            "schemaVersion": 1,
            "kind": "H1ControlledSamples",
            "protocol": bind(protocol),
            "schedule": bind(schedule),
            "buildMap": bind(build_map),
            "attempts": attempts,
        })
        authority = {
            "kind": reuse.AUTHORITY_KIND,
            "projectRoot": str(ROOT.resolve()),
            "graphSourcePins": {"schemaVersion": 1},
            "currentSourcePins": {"schemaVersion": 1},
            "bridgeReceipt": bind(bridge),
            "policyId": reuse.POLICY_ID,
            "retainedPilotRunner": retained_runner,
        }
        return {
            "protocol": protocol,
            "schedule": schedule,
            "scheduleRows": schedule_rows,
            "buildMap": build_map,
            "bridge": bridge,
            "build": build,
            "prior": prior,
            "attempts": attempts,
            "authority": authority,
            "retainedRunner": retained_runner,
        }

    def test_actual_admission_preflight_accepts_exact_retained_runner_without_deep_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            output = root / "pilot-admission.json"
            with mock.patch.object(admission.driver, "_validate_protocol", return_value={}), \
                 mock.patch.object(admission.driver, "_validate_schedule", return_value=fx["scheduleRows"]), \
                 mock.patch.object(admission.driver, "_validate_build", return_value=fx["build"]), \
                 mock.patch.object(
                     admission.graph_reuse, "verify_bridge_full",
                     return_value=fx["authority"]) as full_bridge, \
                 mock.patch.object(
                     admission.driver._r00, "verify_suite",
                     side_effect=AssertionError("admission preflight must not deep-verify R00")):
                code = admission.main([
                    "--protocol", str(fx["protocol"]),
                    "--schedule", str(fx["schedule"]),
                    "--build-map", str(fx["buildMap"]),
                    "--pilot-index", str(fx["prior"]),
                    "--graph-reuse-bridge", str(fx["bridge"]),
                    "--output", str(output),
                ])

            self.assertEqual(code, 0)
            full_bridge.assert_called_once_with(
                fx["bridge"], ROOT.resolve(), fx["buildMap"])
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt["kind"], "H1RetainedPilotAdmissionPreflight")
            self.assertEqual(receipt["result"], "Passed")
            self.assertEqual(receipt["selectedPilotCount"], 4)
            self.assertEqual(receipt["retainedPilotRunner"], fx["retainedRunner"])

    def test_actual_seal_entry_accepts_exact_retained_runner_and_reaches_eight_deep_sides(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            output = root / "pilot-seal.json"

            def verified(_path, expected_mode=None, pairing_authority=None):
                return {
                    "result": "Passed",
                    "requestedModeIds": [expected_mode],
                    "executedModeIds": [expected_mode],
                }

            with mock.patch.object(seal.driver, "_validate_protocol", return_value={}),                  mock.patch.object(seal.driver, "_validate_schedule", return_value=fx["scheduleRows"]),                  mock.patch.object(seal.driver, "_validate_build", return_value=fx["build"]),                  mock.patch.object(
                     seal.graph_reuse, "verify_bridge_full",
                     return_value=fx["authority"]) as full_bridge,                  mock.patch.object(
                     seal.driver.graph_reuse, "verify_bridge_compact",
                     return_value=fx["authority"]),                  mock.patch.object(
                     seal.driver._r00, "verify_suite",
                     side_effect=verified) as deep:
                code = seal.main([
                    "--protocol", str(fx["protocol"]),
                    "--schedule", str(fx["schedule"]),
                    "--build-map", str(fx["buildMap"]),
                    "--pilot-index", str(fx["prior"]),
                    "--graph-reuse-bridge", str(fx["bridge"]),
                    "--output", str(output),
                ])

            self.assertEqual(code, 0)
            full_bridge.assert_called_once_with(
                fx["bridge"], ROOT.resolve(), fx["buildMap"])
            self.assertEqual(deep.call_count, 8)
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt["deepLaunchVerificationCount"], 8)
            self.assertEqual(receipt["status"], "PassedStrictReconstructionAndStatGuardSealed")
            self.assertEqual(receipt["graphReuseBridge"], bind(fx["bridge"]))

    def test_retained_runner_rejected_without_authenticated_bridge_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            with self.assertRaisesRegex(VerificationError, "runner binding mismatch"):
                driver._load_prior(
                    fx["prior"], fx["protocol"], fx["schedule"], fx["buildMap"],
                    fx["scheduleRows"], "pilot", fx["build"])

    def test_retained_runner_rejects_wrong_hash_or_path(self):
        mutations = ("sha", "path")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                fx = self.fixture(root)
                value = json.loads(fx["prior"].read_text())
                if mutation == "sha":
                    value["attempts"][0]["A"]["runner"]["sha256"] = "0" * 64
                else:
                    value["attempts"][0]["A"]["runner"]["path"] = str(root / "other-runner.py")
                fx["prior"].write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaisesRegex(VerificationError, "runner binding mismatch"):
                    driver._load_prior(
                        fx["prior"], fx["protocol"], fx["schedule"], fx["buildMap"],
                        fx["scheduleRows"], "pilot", fx["build"],
                        graph_reuse_bridge_path=fx["bridge"],
                        retained_pilot_authority=fx["authority"])

    def test_retained_runner_rejects_bridge_switch_before_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            other = write_json(root / "other-bridge.json", {"other": True})
            with self.assertRaisesRegex(VerificationError, "bridge binding mismatch"):
                driver._load_prior(
                    fx["prior"], fx["protocol"], fx["schedule"], fx["buildMap"],
                    fx["scheduleRows"], "pilot", fx["build"],
                    graph_reuse_bridge_path=other,
                    retained_pilot_authority=fx["authority"])


if __name__ == "__main__":
    unittest.main()
