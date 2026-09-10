"""Focused manifest and shape binding regressions for H1 parameter fixtures."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import h1_count_manifest as manifest
from shadow_tools import VerificationError


FIXTURE_MANIFEST = Path(
    "/Users/ah/GitHub/hybridclr/h1r-coordination-20260910/"
    "parameter-fixtures-next/h1-count-fixture-manifest.json")


def read_fixture_manifest():
    return json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))


def shape_for(case, flavor="ordinary"):
    count, variant = case["count"], case["variant"]
    if variant == "mixed-kinds":
        pattern = ("System.Int32", "System.String", "System.Object", "System.Int32&", "System.String[]")
        parameter_types = [pattern[index % 5] for index in range(count)]
    else:
        parameter_types = ["System.Int32"] * count
    if variant == "return255":
        sequences, names = [0], ["result"]
    elif variant == "partial-names":
        sequences = [sequence for sequence in range(1, count + 1)
                     if (sequence - 1) % 17 == 0]
        names = [f"p{sequence:04d}" for sequence in sequences]
    else:
        sequences, names = [], []
    target = case[flavor]["targetType"]
    rows = [{"rid": index + 1, "flags": 0, "sequence": sequence, "name": name}
            for index, (sequence, name) in enumerate(zip(sequences, names))]
    return {
        "sha256": case[flavor]["sha256"], "sizeBytes": case[flavor]["sizeBytes"],
        "identity": {field: case[flavor][field]
                      for field in ("name", "fullName", "version", "mvid")},
        "types": [{"rid": 2, "fullName": target}],
        "methods": [{"rid": 1, "declaringType": target, "name": "Probe",
                     "signature": {"count": count, "returnType": "System.Int32",
                                   "instance": variant == "instance",
                                   "parameterTypes": parameter_types},
                     "paramRows": rows}],
    }


class H1CountManifestTests(unittest.TestCase):
    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(VerificationError):
            manifest.parse_manifest_bytes(b'{"schemaVersion":1,"schemaVersion":1}')

    def test_canonical_matrix_rejects_negative_count_missing_duplicate_and_zero(self):
        original = read_fixture_manifest()
        bad = copy.deepcopy(original)
        bad["cases"][0]["count"] = -1
        with self.assertRaises(VerificationError):
            manifest.validate_manifest_structure(bad)

        for cases in (original["cases"][:-1],
                      original["cases"][:-1] + [copy.deepcopy(original["cases"][0])],
                      []):
            bad = copy.deepcopy(original)
            bad["cases"] = cases
            with self.assertRaises(VerificationError):
                manifest.validate_manifest_structure(bad)

    def test_positive_zero_and_four_p04_shapes_bind_to_independent_controls(self):
        original = read_fixture_manifest()
        for case_id in ("H1R-P01-a", "H1R-P04-return255", "H1R-P04-partial-names",
                        "H1R-P04-instance", "H1R-P04-mixed-kinds"):
            case = next(item for item in original["cases"] if item["caseId"] == case_id)
            for flavor in ("ordinary", "shadow"):
                observed = manifest.validate_observation(case, flavor, shape_for(case, flavor))
                self.assertEqual(observed["signatureCount"], case["count"])
                if case_id == "H1R-P04-return255":
                    self.assertTrue(observed["returnParamRow0Retained"])

    def test_high_signature_count_with_no_param_rows_is_accepted_as_shape(self):
        original = read_fixture_manifest()
        case = next(item for item in original["cases"] if item["caseId"] == "H1R-P03-a")
        actual = {
            "sha256": case["ordinary"]["sha256"],
            "sizeBytes": case["ordinary"]["sizeBytes"],
            "identity": {field: case["ordinary"][field]
                          for field in ("name", "fullName", "version", "mvid")},
            "types": [{"rid": 2, "fullName": case["ordinary"]["targetType"]}],
            "methods": [{"rid": 1, "declaringType": case["ordinary"]["targetType"],
                         "name": "Probe", "signature": {
                             "count": 65536, "returnType": "System.Int32", "instance": False,
                             "parameterTypes": ["System.Int32"] * 65536},
                         "paramRows": []}],
        }
        observed = manifest.validate_observation(case, "ordinary", actual)
        self.assertEqual(observed["signatureCount"], 65536)
        self.assertEqual(observed["paramRowCount"], 0)

    def test_hash_identity_count_missing_and_duplicate_target_observations_fail(self):
        original = read_fixture_manifest()
        case = original["cases"][1]
        valid = shape_for(case)

        for mutation in (
                lambda value: value.update(sha256="0" * 64),
                lambda value: value["identity"].update(mvid="changed"),
                lambda value: value["methods"][0]["signature"].update(count=2),
                lambda value: value.update(types=[]),
                lambda value: value.update(types=[{"rid": 2, "fullName": case["ordinary"]["targetType"]},
                                                  {"rid": 3, "fullName": case["ordinary"]["targetType"]}]),
        ):
            bad = copy.deepcopy(valid)
            mutation(bad)
            with self.assertRaises(VerificationError):
                manifest.validate_observation(case, "ordinary", bad)

    def test_cli_failure_retains_new_receipt_and_refuses_overwrite(self):
        original = read_fixture_manifest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            invalid_manifest = root / "invalid.json"
            invalid_manifest.write_bytes(b'{"schemaVersion":1,"schemaVersion":2}')
            output = root / "failure.json"
            self.assertEqual(manifest.main(["--manifest", str(invalid_manifest.resolve()),
                                            "--output", str(output.resolve())]), 1)
            failure = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(failure["result"], "Failed")
            self.assertNotIn("FullMatrixPassed", output.read_text(encoding="utf-8"))

            output.write_text("keep", encoding="utf-8")
            self.assertEqual(manifest.main(["--manifest", str(invalid_manifest.resolve()),
                                            "--output", str(output.resolve())]), 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
