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

import h1_formal_launch_authority as authority
from shadow_tools import VerificationError

_driver_spec = importlib.util.spec_from_file_location(
    "h1_formal_boundary_driver", TOOLS / "run-h1-paired-performance.py")
driver = importlib.util.module_from_spec(_driver_spec)
_driver_spec.loader.exec_module(driver)

_runner_spec = importlib.util.spec_from_file_location(
    "h1_formal_boundary_runner", TOOLS / "run-r00-players.py")
runner = importlib.util.module_from_spec(_runner_spec)
_runner_spec.loader.exec_module(runner)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def bind(path: Path) -> dict:
    return {"path": str(path), "sha256": digest(path)}


class H1FormalLaunchAuthorityTests(unittest.TestCase):
    def fixture(self, root: Path):
        protocol = write_json(root / "protocol.json", {"protocol": 1})
        pair_id = "R00-OFF-NoPatch-formal-01"
        mode = "R00-OFF-NoPatch"
        order = ["A", "B"]
        schedule = write_json(root / "schedule.json", {
            "schemaVersion": 1,
            "kind": "H1ControlledPairSchedule",
            "pairs": [{
                "pairId": pair_id,
                "mode": mode,
                "phase": "formal",
                "order": order,
                "includedInFormalStatistics": True,
            }],
        })
        fixture = write_json(root / "fixture.json", {"fixture": 1})
        replay = write_json(root / "replay.json", {"replay": 1})
        on = write_json(root / "on.json", {"variant": "NativeOn"})
        off = write_json(root / "off.json", {"variant": "NativeOff"})
        bridge = write_json(root / "bridge.json", {"bridge": 1})
        build_map = write_json(root / "build-map.json", {
            "schemaVersion": 1,
            "kind": "H1ControlledBuildMap",
            "status": "Frozen",
            "sides": {
                "B": {
                    "projectRoot": str(ROOT.resolve()),
                    "fixtureManifest": bind(fixture),
                    "replayReceipt": bind(replay),
                    "builds": {
                        "on": {"receipt": bind(on)},
                        "off": {"receipt": bind(off)},
                    },
                }
            },
        })
        seal = write_json(root / "seal.json", {
            "schemaVersion": 1,
            "kind": "H1PilotVerificationReceipt",
            "status": "PassedStrictReconstructionAndStatGuardSealed",
            "protocol": bind(protocol),
            "schedule": bind(schedule),
            "buildMap": bind(build_map),
            "graphReuseBridge": bind(bridge),
        })
        pairing = {
            "kind": "H1AuthenticatedGraphReuseAuthority",
            "projectRoot": str(ROOT.resolve()),
            "bridgeReceipt": bind(bridge),
            "policyId": "H1V04RetainedGraphToolOnlySuccessor-v1",
            "graphSourcePins": {"demo": {"revision": "69130bbb"}},
            "currentSourcePins": {"demo": {"revision": "current"}},
        }
        return {
            "protocol": protocol, "schedule": schedule, "buildMap": build_map,
            "fixture": fixture, "replay": replay, "on": on, "off": off,
            "bridge": bridge, "seal": seal, "pairing": pairing,
            "pairId": pair_id, "mode": mode, "order": order,
        }

    def test_receipt_binds_formal_pair_map_bridge_seal_inputs_and_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            with mock.patch.object(
                    authority.graph_reuse, "verify_bridge_compact",
                    return_value=fx["pairing"]):
                value = authority.create_receipt(
                    ROOT.resolve(), fx["pairId"], 2, fx["mode"], fx["order"],
                    fx["protocol"], fx["schedule"], fx["buildMap"], fx["bridge"], fx["seal"],
                    fx["fixture"], fx["on"], fx["off"], fx["replay"])
                receipt = write_json(root / "authority.json", value)
                verified = authority.verify_receipt(
                    receipt, ROOT.resolve(), fx["mode"], fx["fixture"], fx["on"], fx["off"], fx["replay"],
                    expected_pair_id=fx["pairId"], expected_attempt=2)

            self.assertEqual(value["kind"], authority.KIND)
            self.assertEqual(value["status"], authority.STATUS)
            self.assertEqual(value["side"], "B")
            self.assertEqual(verified["pairingAuthority"], fx["pairing"])
            self.assertEqual(verified["graphReuseBridge"], bind(fx["bridge"]))
            self.assertEqual(verified["pilotVerification"], bind(fx["seal"]))
            self.assertTrue(any(
                row["path"] == "Tools/AssemblyShadow/run-r00-players.py"
                for row in value["toolBindings"]))

    def test_receipt_rejects_schedule_input_and_tool_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fx = self.fixture(root)
            with mock.patch.object(
                    authority.graph_reuse, "verify_bridge_compact",
                    return_value=fx["pairing"]):
                value = authority.create_receipt(
                    ROOT.resolve(), fx["pairId"], 1, fx["mode"], fx["order"],
                    fx["protocol"], fx["schedule"], fx["buildMap"], fx["bridge"], fx["seal"],
                    fx["fixture"], fx["on"], fx["off"], fx["replay"])

            mutations = [
                lambda v: v.update(mode="R00-ON-NoPatch"),
                lambda v: v["nativeOffReceipt"].update(sha256="0" * 64),
                lambda v: v["toolBindings"][0].update(sha256="0" * 64),
            ]
            for index, mutate in enumerate(mutations):
                with self.subTest(index=index):
                    changed = json.loads(json.dumps(value))
                    mutate(changed)
                    receipt = write_json(root / f"authority-{index}.json", changed)
                    with mock.patch.object(
                            authority.graph_reuse, "verify_bridge_compact",
                            return_value=fx["pairing"]):
                        with self.assertRaises(VerificationError):
                            authority.verify_receipt(
                                receipt, ROOT.resolve(), fx["mode"], fx["fixture"],
                                fx["on"], fx["off"], fx["replay"],
                                expected_pair_id=fx["pairId"], expected_attempt=1)

    def test_real_formal_command_boundary_uses_retained_verifier_only_for_authorized_side_b(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "candidate"
            temp = project / "_temp/AssemblyShadow"
            temp.mkdir(parents=True)
            fixture = write_json(root / "fixture.json", {})
            replay = write_json(root / "replay.json", {})
            on = write_json(root / "on.json", {})
            off = write_json(root / "off.json", {})
            authority_receipt = write_json(root / "authority.json", {"kind": authority.KIND})
            side = {
                "fixtureManifest": fixture,
                "replayReceipt": replay,
                "builds": {
                    "on": {"receipt": on},
                    "off": {"receipt": off},
                },
            }
            output = temp / "formal-side-b"
            mode = "R00-OFF-NoPatch"
            command = driver.build_command(
                project, mode, side, output, 30, authority_receipt)
            self.assertEqual(Path(command[1]).name, "run-r00-players.py")
            self.assertIn("--h1-formal-launch-authority", command)
            self.assertEqual(
                command[command.index("--h1-formal-launch-authority") + 1],
                str(authority_receipt))

            pairing = {
                "kind": "H1AuthenticatedGraphReuseAuthority",
                "projectRoot": str(project),
                "graphSourcePins": {"demo": {"revision": "69130bbb"}},
                "currentSourcePins": {"demo": {"revision": "current"}},
                "bridgeReceipt": {"path": str(root / "bridge.json"), "sha256": "1" * 64},
            }
            formal_verified = {
                "receipt": bind(authority_receipt),
                "pairId": "R00-OFF-NoPatch-formal-01",
                "attempt": 1,
                "mode": mode,
                "pairOrder": ["A", "B"],
                "buildMap": {"path": str(root / "map.json"), "sha256": "2" * 64},
                "graphReuseBridge": {"path": str(root / "bridge.json"), "sha256": "1" * 64},
                "pilotVerification": {"path": str(root / "seal.json"), "sha256": "3" * 64},
                "pairingAuthority": pairing,
            }
            context = {
                "sourcePins": pairing["graphSourcePins"],
                "off": {"player": {"playerOutput": str(root / "off.app"), "buildGuid": "off-guid"}},
                "on": {"player": {"playerOutput": str(root / "on.app"), "buildGuid": "on-guid"}},
            }

            class FakeProcess:
                pid = 43210
                def __init__(self, argv):
                    result = Path(argv[argv.index("-shadowR00Result") + 1])
                    result.parent.mkdir(parents=True, exist_ok=True)
                    result.write_text(json.dumps({
                        "mode": mode,
                        "result": "Passed",
                        "processId": self.pid,
                        "buildGuid": "off-guid",
                    }), encoding="utf-8")
                def wait(self, timeout=None):
                    return 0
                def terminate(self):
                    pass
                def kill(self):
                    pass

            args = command[2:]
            with mock.patch.object(
                    runner.formal_authority, "verify_receipt",
                    return_value=formal_verified) as verify_authority, \
                 mock.patch.object(
                    runner, "verify_inputs",
                    side_effect=AssertionError("authorized formal side B fell back to current pairing")), \
                 mock.patch.object(
                    runner, "verify_inputs_with_reuse",
                    return_value=context) as reuse_verify, \
                 mock.patch.object(runner.m07, "collect_inputs", return_value=set()), \
                 mock.patch.object(runner.m07, "executable_for", return_value=Path("/bin/true")), \
                 mock.patch.object(
                    runner.subprocess, "Popen",
                    side_effect=lambda argv, **_kwargs: FakeProcess(argv)):
                code = runner.main(args)

            self.assertEqual(code, 0)
            verify_authority.assert_called_once()
            reuse_verify.assert_called_once_with(
                project, fixture, on, off, replay, pairing)
            launch = json.loads((output / "r00-player-launches.json").read_text())
            self.assertEqual(launch["formalLaunchAuthority"], bind(authority_receipt))
            self.assertEqual(launch["graphReuseBridge"], formal_verified["graphReuseBridge"])
            self.assertEqual(launch["pilotVerification"], formal_verified["pilotVerification"])
            self.assertEqual(launch["sourcePins"], pairing["graphSourcePins"])

    def test_direct_runner_without_formal_authority_remains_current_pairing(self):
        source = (TOOLS / "run-r00-players.py").read_text()
        self.assertIn("if args.h1_formal_launch_authority is not None:", source)
        self.assertIn("if pairing_authority is None else", source)
        self.assertIn("verify_inputs(project, args.fixture_manifest", source)
        self.assertIn("verify_inputs_with_reuse(", source)
        self.assertIn("--h1-formal-launch-authority", source)
        self.assertNotIn("--source-pin", source)
        self.assertNotIn("--historical-revision", source)


if __name__ == "__main__":
    unittest.main()
