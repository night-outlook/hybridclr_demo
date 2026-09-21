import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "h1_retained_early_preflight_test",
    TOOLS / "verify-h1-retained-early-reuse.py")
preflight = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(preflight)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class H1RetainedEarlyReusePreflightTests(unittest.TestCase):
    def fixture(self, root: Path):
        protocol = write_json(root / "protocol.json", {})
        schedule_path = write_json(root / "schedule.json", {})
        build_map = write_json(root / "build-map.json", {})
        pilot_index = write_json(root / "pilot-index.json", {})
        bridge = write_json(root / "bridge.json", {})
        candidate = root / "candidate"
        candidate.mkdir()

        schedule = []
        attempts = []
        launches = {}
        for index, mode in enumerate(preflight.driver.MODES):
            pair_id = f"pilot-{index + 1}"
            schedule.append({
                "pairId": pair_id,
                "mode": mode,
                "phase": "pilot",
                "order": ["A", "B"],
            })
            row = {
                "pairId": pair_id,
                "attempt": 1,
                "mode": mode,
                "phase": "pilot",
                "status": "Passed",
            }
            for side in ("A", "B"):
                launch = write_json(root / f"{pair_id}-{side}.json", {"mode": mode, "side": side})
                launches[(mode, side)] = launch
                row[side] = {
                    "status": "Passed",
                    "runner": preflight.driver.runner_binding(),
                    "launchReceipt": {"path": str(launch), "sha256": sha(launch)},
                }
            attempts.append(row)

        build = {
            "sides": {
                "A": {"projectRoot": root / "reference"},
                "B": {"projectRoot": candidate},
            }
        }
        (root / "reference").mkdir()
        authority = {
            "kind": preflight.graph_reuse.AUTHORITY_KIND,
            "projectRoot": str(candidate),
        }
        return {
            "protocol": protocol,
            "schedulePath": schedule_path,
            "buildMap": build_map,
            "pilotIndex": pilot_index,
            "bridge": bridge,
            "schedule": schedule,
            "attempts": attempts,
            "build": build,
            "authority": authority,
            "launches": launches,
        }

    def test_preflight_strictly_verifies_all_three_candidate_on_modes_with_same_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            calls = []

            def verify(launch_path, expected_mode=None, pairing_authority=None):
                calls.append((Path(launch_path), expected_mode, pairing_authority))
                return {
                    "result": "Passed",
                    "requestedModeIds": [expected_mode],
                    "executedModeIds": [expected_mode],
                    "sourcePins": {"demo": {"revision": "69130bbb"}},
                }

            with mock.patch.object(preflight.driver, "_validate_protocol", return_value={}), \
                 mock.patch.object(preflight.driver, "_validate_schedule", return_value=fx["schedule"]), \
                 mock.patch.object(preflight.driver, "_validate_build", return_value=fx["build"]), \
                 mock.patch.object(preflight.driver, "_load_prior", return_value=fx["attempts"]), \
                 mock.patch.object(
                     preflight.graph_reuse, "verify_bridge_full", return_value=fx["authority"]) as bridge_verify, \
                 mock.patch.object(preflight.driver._r00, "verify_suite", side_effect=verify):
                output = root / "preflight.json"
                code = preflight.main([
                    "--protocol", str(fx["protocol"]),
                    "--schedule", str(fx["schedulePath"]),
                    "--build-map", str(fx["buildMap"]),
                    "--pilot-index", str(fx["pilotIndex"]),
                    "--graph-reuse-bridge", str(fx["bridge"]),
                    "--output", str(output),
                ])

            self.assertEqual(code, 0)
            bridge_verify.assert_called_once_with(
                fx["bridge"], fx["build"]["sides"]["B"]["projectRoot"], fx["buildMap"])
            self.assertEqual([row[1] for row in calls], list(preflight.ON_MODES))
            self.assertTrue(all(row[2] is fx["authority"] for row in calls))
            self.assertEqual(
                [row[0] for row in calls],
                [fx["launches"][(mode, "B")] for mode in preflight.ON_MODES])
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt["kind"], "H1RetainedEarlyReusePreflight")
            self.assertEqual(receipt["result"], "Passed")
            self.assertEqual(receipt["modeCount"], 3)
            self.assertEqual([row["mode"] for row in receipt["modes"]], list(preflight.ON_MODES))

    def test_preflight_rejects_missing_candidate_on_mode_before_strict_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            fx["attempts"] = [
                row for row in fx["attempts"] if row["mode"] != "R00-ON-P03"
            ]
            fx["schedule"] = [
                row for row in fx["schedule"] if row["mode"] != "R00-ON-P03"
            ]
            with mock.patch.object(preflight.driver, "_validate_protocol", return_value={}), \
                 mock.patch.object(preflight.driver, "_validate_schedule", return_value=fx["schedule"]), \
                 mock.patch.object(preflight.driver, "_validate_build", return_value=fx["build"]), \
                 mock.patch.object(preflight.driver, "_load_prior", return_value=fx["attempts"]), \
                 mock.patch.object(
                     preflight.graph_reuse, "verify_bridge_full", return_value=fx["authority"]), \
                 mock.patch.object(preflight.driver._r00, "verify_suite") as verify:
                with self.assertRaises(preflight.VerificationError):
                    preflight.main([
                        "--protocol", str(fx["protocol"]),
                        "--schedule", str(fx["schedulePath"]),
                        "--build-map", str(fx["buildMap"]),
                        "--pilot-index", str(fx["pilotIndex"]),
                        "--graph-reuse-bridge", str(fx["bridge"]),
                        "--output", str(root / "preflight.json"),
                    ])
                verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
