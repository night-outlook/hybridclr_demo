import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "h1_formal_batch_test", TOOLS / "run-h1-formal-batch.py")
batch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(batch)


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def arg_value(argv, name):
    return argv[argv.index(name) + 1]


class H1FormalBatchTests(unittest.TestCase):
    def fixture(self, root: Path, count=40):
        protocol = write_json(root / "protocol.json", {})
        schedule = write_json(root / "schedule.json", {})
        build_map = write_json(root / "build-map.json", {})
        bridge = write_json(root / "bridge.json", {})
        seal = write_json(root / "seal.json", {})
        prior = write_json(root / "prior.json", {
            "schemaVersion": 1,
            "kind": "H1ControlledSamples",
            "attempts": [],
        })
        rows = [
            {
                "pairId": f"formal-{index + 1:02d}",
                "mode": batch.driver.MODES[index % len(batch.driver.MODES)],
                "phase": "formal",
                "order": ["A", "B"] if index % 2 == 0 else ["B", "A"],
            }
            for index in range(count)
        ]
        return protocol, schedule, build_map, bridge, seal, prior, rows

    def patched_validation(self, rows):
        return (
            mock.patch.object(batch.driver, "_validate_protocol", return_value={}),
            mock.patch.object(batch.driver, "_validate_schedule", return_value=rows),
            mock.patch.object(batch.driver, "_validate_build", return_value={"sides": {}}),
            mock.patch.object(
                batch.driver, "_load_prior",
                side_effect=lambda path, *_args, **_kwargs: json.loads(Path(path).read_text())["attempts"]),
        )

    def test_complete_forty_formal_pairs_chain_sample_indexes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            protocol, schedule, build_map, bridge, seal, prior, rows = self.fixture(root, 40)
            calls = []

            def fake_driver(argv):
                pair_id = arg_value(argv, "--pair-id")
                output = Path(arg_value(argv, "--output-root"))
                prior_path = Path(arg_value(argv, "--prior-index"))
                value = json.loads(prior_path.read_text())
                pair = next(row for row in rows if row["pairId"] == pair_id)
                value["attempts"].append({
                    "pairId": pair_id,
                    "attempt": 1,
                    "mode": pair["mode"],
                    "phase": "formal",
                    "order": pair["order"],
                    "status": "Passed",
                    "A": {},
                    "B": {},
                })
                output.mkdir()
                write_json(output / "sample-index.json", value)
                calls.append((pair_id, str(prior_path), str(output / "sample-index.json")))
                return 0

            patches = self.patched_validation(rows)
            with patches[0], patches[1], patches[2], patches[3],                  mock.patch.object(batch.driver, "main", side_effect=fake_driver):
                code = batch.main([
                    "--protocol", str(protocol),
                    "--schedule", str(schedule),
                    "--build-map", str(build_map),
                    "--graph-reuse-bridge", str(bridge),
                    "--pilot-verification-receipt", str(seal),
                    "--prior-index", str(prior),
                    "--output-root", str(root / "batch"),
                ])

            self.assertEqual(code, 0)
            self.assertEqual(len(calls), 40)
            self.assertEqual([row[0] for row in calls], [row["pairId"] for row in rows])
            for previous, current in zip(calls, calls[1:]):
                self.assertEqual(current[1], previous[2])
            receipt = json.loads((root / "batch/formal-batch.json").read_text())
            self.assertEqual(receipt["status"], "PassedAllFormalPairs")
            self.assertEqual(receipt["formalPairCount"], 40)
            self.assertEqual(receipt["formalPairsPassed"], 40)
            self.assertEqual(receipt["formalPairsStartedByThisBatch"], 40)

    def test_batch_stops_on_first_failed_whole_pair_without_retry_or_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            protocol, schedule, build_map, bridge, seal, prior, rows = self.fixture(root, 4)
            calls = []

            def fake_driver(argv):
                pair_id = arg_value(argv, "--pair-id")
                output = Path(arg_value(argv, "--output-root"))
                prior_path = Path(arg_value(argv, "--prior-index"))
                value = json.loads(prior_path.read_text())
                pair = next(row for row in rows if row["pairId"] == pair_id)
                status = "Failed" if len(calls) == 1 else "Passed"
                value["attempts"].append({
                    "pairId": pair_id,
                    "attempt": 1,
                    "mode": pair["mode"],
                    "phase": "formal",
                    "order": pair["order"],
                    "status": status,
                    "A": {},
                    "B": {},
                })
                output.mkdir()
                write_json(output / "sample-index.json", value)
                calls.append(pair_id)
                return 1 if status == "Failed" else 0

            patches = self.patched_validation(rows)
            with patches[0], patches[1], patches[2], patches[3],                  mock.patch.object(batch.driver, "main", side_effect=fake_driver):
                code = batch.main([
                    "--protocol", str(protocol),
                    "--schedule", str(schedule),
                    "--build-map", str(build_map),
                    "--graph-reuse-bridge", str(bridge),
                    "--pilot-verification-receipt", str(seal),
                    "--prior-index", str(prior),
                    "--output-root", str(root / "batch"),
                ])

            self.assertEqual(code, 1)
            self.assertEqual(calls, [rows[0]["pairId"], rows[1]["pairId"]])
            receipt = json.loads((root / "batch/formal-batch.json").read_text())
            self.assertEqual(receipt["status"], "StoppedOnFailedWholePair")
            self.assertEqual(receipt["formalPairsStartedByThisBatch"], 2)
            final = json.loads(Path(receipt["finalSampleIndex"]["path"]).read_text())
            with self.assertRaises(batch.VerificationError):
                batch.require_resumable(final["attempts"], rows)


if __name__ == "__main__":
    unittest.main()
