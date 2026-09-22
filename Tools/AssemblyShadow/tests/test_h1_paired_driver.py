import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shadow_tools import VerificationError


_spec = importlib.util.spec_from_file_location(
    "h1_paired_driver", Path(__file__).resolve().parents[1] / "run-h1-paired-performance.py")
driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(driver)


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class H1PairedDriverTests(unittest.TestCase):
    def test_runner_is_the_single_mode_r00_harness(self):
        self.assertEqual(driver.RUNNER_PATH.name, "run-r00-players.py")
        self.assertNotEqual(driver.RUNNER_PATH, Path(driver.__file__).resolve())


    def test_cross_remount_guard_excludes_device_but_keeps_stable_stat_identity(self):
        base = SimpleNamespace(
            st_dev=100, st_ino=200, st_mode=0o100755, st_size=4096,
            st_mtime_ns=123456789, st_ctime_ns=223456789)
        remounted = SimpleNamespace(
            st_dev=101, st_ino=200, st_mode=0o100755, st_size=4096,
            st_mtime_ns=123456789, st_ctime_ns=223456789)
        self.assertEqual(driver._stable_stat_guard(base), driver._stable_stat_guard(remounted))
        self.assertEqual(
            tuple(driver._stable_stat_guard(base).keys()), driver.PILOT_GUARD_FIELDS)
        self.assertNotIn("device", driver._stable_stat_guard(base))

        mutations = {
            "inode": {"st_ino": 201},
            "mode": {"st_mode": 0o100644},
            "size": {"st_size": 4097},
            "mtimeNs": {"st_mtime_ns": 123456790},
            "ctimeNs": {"st_ctime_ns": 223456790},
        }
        for name, changes in mutations.items():
            with self.subTest(field=name):
                values = dict(
                    st_dev=100, st_ino=200, st_mode=0o100755, st_size=4096,
                    st_mtime_ns=123456789, st_ctime_ns=223456789)
                values.update(changes)
                self.assertNotEqual(
                    driver._stable_stat_guard(base),
                    driver._stable_stat_guard(SimpleNamespace(**values)))

    def test_output_run_id_is_deterministic_and_collision_resistant_across_batch_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first = root / "batch-a" / "01-R00-OFF-NoPatch-formal-01-attempt-1"
            second = root / "batch-b" / "01-R00-OFF-NoPatch-formal-01-attempt-1"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            first_id = driver._output_run_id(first)
            second_id = driver._output_run_id(second)
            self.assertEqual(first_id, driver._output_run_id(first))
            self.assertNotEqual(first_id, second_id)
            self.assertTrue(first_id.startswith("01-R00-OFF-NoPatch-formal-01-attempt-1-"))
            self.assertEqual(len(first_id.rsplit("-", 1)[-1]), 12)


    def test_second_side_cleanup_failure_retains_both_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            inputs = [write_json(root / name, {}) for name in
                      ("protocol.json", "schedule.json", "build-map.json")]
            projects = {side: root / side for side in ("A", "B")}
            for project in projects.values():
                (project / "_temp/AssemblyShadow").mkdir(parents=True)
            row = {"pairId": "pilot", "mode": "R00-ON-NoPatch",
                   "phase": "pilot", "order": ["A", "B"]}
            def run_side(side_name, side, mode, output, project, timeout, formal_launch_authority=None):
                output.mkdir()
                return {"status": "Passed" if side_name == "A" else "Failed",
                        "stopBeforeNextSide": side_name == "B", "launchReceipt": None,
                        "marker": side_name}
            with mock.patch.object(driver, "_validate_protocol", return_value={}), \
                 mock.patch.object(driver, "_validate_schedule", return_value=[row]), \
                 mock.patch.object(driver, "_validate_build", return_value={
                     "sides": {side: {"projectRoot": path} for side, path in projects.items()}}), \
                 mock.patch.object(driver, "_load_prior", return_value=[]), \
                 mock.patch.object(driver, "_run_side", side_effect=run_side), \
                 mock.patch.object(driver, "_skipped_side") as skipped:
                code = driver.main(["--protocol", str(inputs[0]), "--schedule", str(inputs[1]),
                    "--build-map", str(inputs[2]), "--output-root", str(root / "result"),
                    "--phase", "pilot", "--pair-id", "pilot", "--attempt", "1"])
            self.assertEqual(code, 1)
            skipped.assert_not_called()
            attempt = json.loads((root / "result/sample-index.json").read_text())["attempts"][0]
            self.assertEqual(attempt["A"]["marker"], "A")
            self.assertEqual(attempt["B"]["marker"], "B")


    def test_pair_selection_is_one_pair_and_preserves_explicit_order(self):
        rows = [
            {"pairId": "pilot-a", "mode": "R00-OFF-NoPatch", "phase": "pilot", "order": ["B", "A"]},
            {"pairId": "pilot-b", "mode": "R00-ON-NoPatch", "phase": "pilot", "order": ["A", "B"]},
        ]
        self.assertEqual(driver._select_pair(rows, "pilot", "pilot-a", []), rows[0])
        self.assertEqual(driver._select_pair(rows, "pilot", None, [{"pairId": "pilot-a"}]), rows[1])
        with self.assertRaises(VerificationError):
            driver._select_pair(rows, "formal", None, [])

    def test_build_command_contains_exact_single_mode_contract(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root).resolve()
            project = root / "project"
            (project / "Assets/AssemblyShadowDemo").mkdir(parents=True)
            manifest = Path(root) / "manifest.json"
            replay = Path(root) / "replay.json"
            on = Path(root) / "on.json"
            off = Path(root) / "off.json"
            for path in (manifest, replay, on, off):
                path.write_text("{}", encoding="utf-8")
            side = {
                "fixtureManifest": manifest,
                "replayReceipt": replay,
                "builds": {"on": {"receipt": on}, "off": {"receipt": off}},
            }
            output = project / "_temp/AssemblyShadow/pair-1"
            command = driver.build_command(project, "R00-ON-P03", side, output, 321)
            self.assertEqual(command[0], driver.sys.executable)
            self.assertEqual(command[1:3], [str(driver.RUNNER_PATH), "--project-root"])
            self.assertIn("--mode", command)
            self.assertEqual(command[command.index("--mode") + 1], "R00-ON-P03")
            self.assertEqual(command[command.index("--timeout") + 1], "321")
            self.assertEqual(command[command.index("--on-build") + 1], str(on))
            self.assertEqual(command[command.index("--off-build") + 1], str(off))

    def test_formal_prior_requires_all_four_passed_pilot_receipts(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root).resolve()
            protocol = write_json(root / "protocol.json", {})
            schedule_rows = [
                {"pairId": "pilot-" + str(i), "mode": mode, "phase": "pilot", "order": ["A", "B"]}
                for i, mode in enumerate(driver.MODES)
            ] + [{"pairId": "formal-1", "mode": driver.MODES[0], "phase": "formal", "order": ["A", "B"]}]
            schedule = write_json(root / "schedule.json", {"pairs": schedule_rows})
            build_map = write_json(root / "build-map.json", {})
            launch = write_json(root / "launch.json", {"result": "Passed"})
            receipt = {"path": str(launch), "sha256": sha(launch)}
            attempts = [{"pairId": row["pairId"], "attempt": 1, "phase": row["phase"], "mode": row["mode"],
                         "A": {"status": "Passed", "runner": driver.runner_binding(), "launchReceipt": receipt},
                         "B": {"status": "Passed", "runner": driver.runner_binding(), "launchReceipt": receipt}}
                        for row in schedule_rows[:3]]
            prior = write_json(root / "prior.json", {
                "schemaVersion": 1, "kind": "H1ControlledSamples",
                "protocol": {"path": str(protocol), "sha256": sha(protocol)},
                "schedule": {"path": str(schedule), "sha256": sha(schedule)},
                "buildMap": {"path": str(build_map), "sha256": sha(build_map)},
                "attempts": attempts,
            })
            with self.assertRaises(VerificationError):
                driver._load_prior(prior, protocol, schedule, build_map, schedule_rows, "formal",
                                   {"sides": {"A": {}, "B": {}}})

    def _pilot_cache_fixture(self, root):
        protocol = write_json(root / "protocol.json", {"kind": "protocol"})
        schedule_rows = [
            {"pairId": "pilot-" + str(index), "mode": mode, "phase": "pilot", "order": ["A", "B"]}
            for index, mode in enumerate(driver.MODES)
        ] + [
            {"pairId": "formal-" + str(index), "mode": driver.MODES[index % len(driver.MODES)],
             "phase": "formal", "order": ["A", "B"]}
            for index in range(40)
        ]
        schedule = write_json(root / "schedule.json", {"pairs": schedule_rows})
        build_map = write_json(root / "build-map.json", {"kind": "map"})
        build = {"sides": {}}
        attempts = []
        launch_paths = []
        graph_paths = []
        for side in driver.SIDES:
            project = root / ("project-" + side)
            project.mkdir()
            fixture = write_json(root / ("fixture-" + side + ".json"), {})
            replay = write_json(root / ("replay-" + side + ".json"), {})
            on = write_json(root / ("on-" + side + ".json"), {})
            off = write_json(root / ("off-" + side + ".json"), {})
            graph = root / ("graph-" + side + ".bin")
            graph.write_bytes(("graph-" + side).encode())
            graph_paths.append(graph)
            build["sides"][side] = {
                "projectRoot": project,
                "fixtureManifest": fixture,
                "replayReceipt": replay,
                "builds": {"on": {"receipt": on}, "off": {"receipt": off}},
            }
        for pair in schedule_rows[:len(driver.MODES)]:
            row = {"pairId": pair["pairId"], "attempt": 1, "mode": pair["mode"],
                   "phase": "pilot", "status": "Passed"}
            for side in driver.SIDES:
                side_build = build["sides"][side]
                result = write_json(root / (pair["pairId"] + "-" + side + "-result.json"), {"passed": True})
                graph = root / ("graph-" + side + ".bin")
                launch = write_json(root / (pair["pairId"] + "-" + side + "-launch.json"), {
                    "projectRoot": str(side_build["projectRoot"]),
                    "fixtureManifestPath": str(side_build["fixtureManifest"]),
                    "nativeOnReceipt": str(side_build["builds"]["on"]["receipt"]),
                    "nativeOffReceipt": str(side_build["builds"]["off"]["receipt"]),
                    "editorReplayReceipt": str(side_build["replayReceipt"]),
                    "inputHashesBefore": {str(graph): sha(graph)},
                    "inputHashesAfter": {str(graph): sha(graph)},
                    "processLaunches": [{"resultPath": str(result), "resultSha256": sha(result),
                                         "earlyCapsulePath": "", "earlyCapsuleSha256": "",
                                         "earlyResultPath": "", "earlyResultSha256": ""}],
                })
                launch_paths.append(launch)
                row[side] = {"status": "Passed", "runner": driver.runner_binding(),
                             "launchReceipt": {"path": str(launch), "sha256": sha(launch)}}
            attempts.append(row)
        prior = write_json(root / "prior.json", {
            "schemaVersion": 1, "kind": "H1ControlledSamples",
            "protocol": {"path": str(protocol), "sha256": sha(protocol)},
            "schedule": {"path": str(schedule), "sha256": sha(schedule)},
            "buildMap": {"path": str(build_map), "sha256": sha(build_map)},
            "attempts": attempts,
        })
        verifier_paths = []
        for index in range(2):
            verifier = root / ("verifier-" + str(index) + ".py")
            verifier.write_text("VERIFIER = " + str(index) + "\n", encoding="utf-8")
            verifier_paths.append(verifier)
        return {
            "protocol": protocol, "schedule": schedule, "scheduleRows": schedule_rows,
            "buildMap": build_map, "build": build, "attempts": attempts, "prior": prior,
            "launchPaths": launch_paths, "graphPaths": graph_paths,
            "verifierPaths": tuple(verifier_paths),
        }

    def _seal_test_cache(self, fixture, root):
        cache = root / "pilot-verification.json"
        def verified(_path, expected_mode=None, pairing_authority=None):
            return {"result": "Passed", "requestedModeIds": [expected_mode],
                    "executedModeIds": [expected_mode]}
        with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
             mock.patch.object(driver._r00, "verify_suite", side_effect=verified) as deep:
            receipt = driver.seal_pilot_verification(
                fixture["attempts"], fixture["scheduleRows"], fixture["build"],
                fixture["protocol"], fixture["schedule"], fixture["buildMap"], fixture["prior"])
            write_json(cache, receipt)
            self.assertEqual(deep.call_count, 8)
            driver.verify_pilot_verification(
                cache, fixture["attempts"], fixture["scheduleRows"],
                fixture["protocol"], fixture["schedule"], fixture["buildMap"])
        return cache

    def test_seal_records_cross_remount_guard_contract_and_rejects_old_guard_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fixture = self._pilot_cache_fixture(root)
            cache = self._seal_test_cache(fixture, root)
            value = json.loads(cache.read_text())
            self.assertEqual(value["guardKind"], driver.PILOT_GUARD_KIND)
            self.assertEqual(value["guardVersion"], driver.PILOT_GUARD_VERSION)
            self.assertEqual(value["guardFields"], list(driver.PILOT_GUARD_FIELDS))
            self.assertTrue(all("device" not in row["guard"] for row in value["files"]))

            old = json.loads(json.dumps(value))
            old["guardVersion"] = 1
            old["guardFields"] = ["device"] + list(driver.PILOT_GUARD_FIELDS)
            old_path = write_json(root / "old-device-bound-seal.json", old)
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]):
                with self.assertRaisesRegex(
                        VerificationError, "stat guard contract changed"):
                    driver.verify_pilot_verification(
                        old_path, fixture["attempts"], fixture["scheduleRows"],
                        fixture["protocol"], fixture["schedule"], fixture["buildMap"])

    def test_bridge_authority_is_side_b_only_and_sealed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fixture = self._pilot_cache_fixture(root)
            bridge = write_json(root / "graph-reuse-bridge.json", {"kind": "bridge"})
            authority = {
                "kind": driver.graph_reuse.AUTHORITY_KIND,
                "projectRoot": str(fixture["build"]["sides"]["B"]["projectRoot"]),
                "graphSourcePins": {"schemaVersion": 1},
                "currentSourcePins": {"schemaVersion": 1},
                "bridgeReceipt": {"path": str(bridge), "sha256": sha(bridge)},
                "retainedPilotRunner": driver.runner_binding(),
            }
            calls = []
            def verified(path, expected_mode=None, pairing_authority=None):
                calls.append((Path(path).name, pairing_authority))
                return {"result": "Passed", "requestedModeIds": [expected_mode],
                        "executedModeIds": [expected_mode]}
            cache = root / "pilot-verification-bridge.json"
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                 mock.patch.object(driver._r00, "verify_suite", side_effect=verified):
                receipt = driver.seal_pilot_verification(
                    fixture["attempts"], fixture["scheduleRows"], fixture["build"],
                    fixture["protocol"], fixture["schedule"], fixture["buildMap"], fixture["prior"],
                    authority, bridge)
                write_json(cache, receipt)
            self.assertEqual(receipt["graphReuseBridge"], {"path": str(bridge), "sha256": sha(bridge)})
            self.assertEqual(len(calls), 8)
            self.assertEqual(sum(item[1] is authority for item in calls), 4)
            self.assertEqual(sum(item[1] is None for item in calls), 4)

    def test_formal_admission_requires_same_bridge_bound_by_seal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fixture = self._pilot_cache_fixture(root)
            project_b = fixture["build"]["sides"]["B"]["projectRoot"]
            bridge = write_json(root / "bridge.json", {"schemaVersion": 1, "projectRoot": str(project_b)})
            other = write_json(root / "bridge-other.json", {"schemaVersion": 1, "projectRoot": str(project_b), "other": True})
            authority = {
                "kind": driver.graph_reuse.AUTHORITY_KIND,
                "projectRoot": str(fixture["build"]["sides"]["B"]["projectRoot"]),
                "graphSourcePins": {"schemaVersion": 1},
                "currentSourcePins": {"schemaVersion": 1},
                "bridgeReceipt": {"path": str(bridge), "sha256": sha(bridge)},
                "retainedPilotRunner": driver.runner_binding(),
            }
            def verified(_path, expected_mode=None, pairing_authority=None):
                return {"result": "Passed", "requestedModeIds": [expected_mode],
                        "executedModeIds": [expected_mode]}
            cache = root / "pilot-verification-bridge.json"
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                 mock.patch.object(driver._r00, "verify_suite", side_effect=verified):
                receipt = driver.seal_pilot_verification(
                    fixture["attempts"], fixture["scheduleRows"], fixture["build"],
                    fixture["protocol"], fixture["schedule"], fixture["buildMap"], fixture["prior"],
                    authority, bridge)
                write_json(cache, receipt)
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                 mock.patch.object(driver.graph_reuse, "verify_bridge_compact", return_value=authority):
                loaded = driver._load_prior(
                    fixture["prior"], fixture["protocol"], fixture["schedule"], fixture["buildMap"],
                    fixture["scheduleRows"], "formal", fixture["build"], cache, bridge)
                self.assertEqual(len(loaded), len(driver.MODES))
                with self.assertRaises(VerificationError):
                    driver._load_prior(
                        fixture["prior"], fixture["protocol"], fixture["schedule"], fixture["buildMap"],
                        fixture["scheduleRows"], "formal", fixture["build"], cache, other)

    def test_forty_formal_admissions_reuse_strict_pilot_seal_without_deep_rescan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fixture = self._pilot_cache_fixture(root)
            cache = self._seal_test_cache(fixture, root)
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                 mock.patch.object(driver._r00, "verify_suite",
                                   side_effect=AssertionError("formal admission repeated deep pilot verification")) as deep:
                for _ in range(40):
                    loaded = driver._load_prior(
                        fixture["prior"], fixture["protocol"], fixture["schedule"], fixture["buildMap"],
                        fixture["scheduleRows"], "formal", fixture["build"], cache)
                    self.assertEqual(len(loaded), len(driver.MODES))
                deep.assert_not_called()

    def test_pilot_seal_fails_closed_on_every_bound_mutation_class(self):
        mutation_names = ("pilotReceipt", "boundArtifact", "protocol", "schedule", "buildMap", "verifier")
        for mutation_name in mutation_names:
            with self.subTest(mutation=mutation_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                fixture = self._pilot_cache_fixture(root)
                cache = self._seal_test_cache(fixture, root)
                if mutation_name == "pilotReceipt":
                    fixture["launchPaths"][0].write_text('{"changed":true}', encoding="utf-8")
                elif mutation_name == "boundArtifact":
                    fixture["graphPaths"][0].write_bytes(b"changed")
                elif mutation_name == "protocol":
                    fixture["protocol"].write_text('{"changed":true}', encoding="utf-8")
                elif mutation_name == "schedule":
                    fixture["schedule"].write_text('{"changed":true}', encoding="utf-8")
                elif mutation_name == "buildMap":
                    fixture["buildMap"].write_text('{"changed":true}', encoding="utf-8")
                elif mutation_name == "verifier":
                    fixture["verifierPaths"][0].write_text("VERIFIER = 'changed'\n", encoding="utf-8")
                with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                     mock.patch.object(driver._r00, "verify_suite",
                                       side_effect=AssertionError("mutation path must not deep-rescan")):
                    with self.assertRaises(VerificationError):
                        driver._load_prior(
                            fixture["prior"], fixture["protocol"], fixture["schedule"], fixture["buildMap"],
                            fixture["scheduleRows"], "formal", fixture["build"], cache)

    def test_formal_attempt_chain_rejects_pilot_seal_switch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fixture = self._pilot_cache_fixture(root)
            cache = self._seal_test_cache(fixture, root)
            prior_value = json.loads(fixture["prior"].read_text())
            prior_value["attempts"].append({
                "pairId": fixture["scheduleRows"][len(driver.MODES)]["pairId"],
                "attempt": 1,
                "mode": fixture["scheduleRows"][len(driver.MODES)]["mode"],
                "phase": "formal",
                "status": "Failed",
                "pilotVerification": {"path": str(cache), "sha256": "0" * 64},
                "A": {"status": "Failed", "runner": driver.runner_binding(), "launchReceipt": None},
                "B": {"status": "Failed", "runner": driver.runner_binding(), "launchReceipt": None},
            })
            write_json(fixture["prior"], prior_value)
            with mock.patch.object(driver, "PILOT_VERIFIER_PATHS", fixture["verifierPaths"]), \
                 mock.patch.object(driver._r00, "verify_suite",
                                   side_effect=AssertionError("formal chain must use cache only")):
                with self.assertRaises(VerificationError):
                    driver._load_prior(
                        fixture["prior"], fixture["protocol"], fixture["schedule"], fixture["buildMap"],
                        fixture["scheduleRows"], "formal", fixture["build"], cache)

    def test_failure_receipt_is_new_only(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "failure.json"
            driver._write_failure_receipt(path, "R00-OFF-NoPatch", "timeout")
            self.assertEqual(json.loads(path.read_text())["driverFailure"], True)
            with self.assertRaises(VerificationError):
                driver._write_failure_receipt(path, "R00-OFF-NoPatch", "again")

    def test_attempt_must_be_positive(self):
        with self.assertRaises(VerificationError):
            driver._positive("0")
        self.assertEqual(driver._positive("2"), 2)


if __name__ == "__main__":
    unittest.main()
