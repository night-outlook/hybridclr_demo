#!/usr/bin/env python3
"""Synthetic-only tests for the R03 B2 offline TypeDef census analyzer."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analyze_typedef_census import CensusError, analyze, load_bytes

SHA_NATIVE = "cecf4b859d50b128e5c0fc6c90cd89e3a452b96a"
SHA_DEMO = "66ef5d0c1cb1682629bd80b5f40a75bb23d2bef8"


def event(handle=1, role="root", ns=4, name=4, owner=0):
    return {"handleId": handle, "ownerImageOrdinal": owner,
            "firstOwnerImageOrdinal": owner, "role": role,
            "namespaceBytes": ns, "simpleNameBytes": name,
            "declaringIndex": -1, "genericIndex": -1, "arity": 0}


def document(events, *, complete=True, dropped=0, classes=1, kind="Synthetic"):
    return {
        "schema": "R03B2TypeDefCensusV1", "captureKind": kind,
        "source": {
            "branch": "codex/assembly-shadow-r01b-h1",
            "nativeCommit": SHA_NATIVE, "demoCommit": SHA_DEMO,
            "metadataReaderEpoch": 1, "metadataLockHeld": True,
            "originalV1ImageCount": 2, "classPasses": 3,
            "originalV1ImagePasses": 2, "observedClasses": classes,
            "declaredEvents": len(events), "droppedEvents": dropped,
            "complete": complete,
        },
        "events": events,
    }


class CensusTests(unittest.TestCase):
    def test_overlap_deduplicated_and_storage_estimates(self):
        v = analyze(document([event(1), event(1, "nonroot"),
                              event(2, "nonroot", 9, 33)]))
        self.assertEqual(v["analysisStatus"], "StructurallyCompleteUnverified")
        self.assertEqual(v["distinctTypeDefs"],
                         {"union": 2, "roots": 1, "nonroots": 2, "sharedBothRoles": 1})
        self.assertEqual(v["events"]["recorded"], 3)
        self.assertEqual(v["nameLengths"]["totalDistinctNameBytes"], 50)
        self.assertEqual(v["capacityObservations"]["fixedSlabMinimumBufferBytes64BitHostModel"], 384)
        self.assertEqual(v["capacityObservations"]["compactArenaMinimumBufferBytes64BitHostModel"], 194)
        self.assertEqual(v["nameLengths"]["namespaceHistogram"]["9-16"], 1)

    def test_129_distinct_roots_over_128_combined_cap(self):
        events = [event(i + 1) for i in range(129)]
        events.append(event(1, "nonroot"))
        v = analyze(document(events, classes=129))
        self.assertEqual(v["distinctTypeDefs"]["union"], 129)
        self.assertEqual(v["distinctTypeDefs"]["sharedBothRoles"], 1)
        self.assertTrue(v["capacityObservations"]["currentCombined128Exceeded"])
        self.assertFalse(v["capacityObservations"]["prototype1024Exceeded"])

    def test_129_classes_with_shared_root_does_not_exceed(self):
        v = analyze(document([event(1) for _ in range(129)], classes=129))
        self.assertEqual(v["distinctTypeDefs"]["union"], 1)
        self.assertFalse(v["capacityObservations"]["currentCombined128Exceeded"])

    def test_1025_distinct_handles_over_prototype_cap(self):
        v = analyze(document([event(i + 1, "nonroot") for i in range(1025)]))
        self.assertTrue(v["capacityObservations"]["prototype1024Exceeded"])

    def test_name_over_64_retained_as_budget_finding(self):
        v = analyze(document([event(1, ns=65, name=2048)]))
        self.assertTrue(v["capacityObservations"]["current64ByteFieldLimitExceeded"])
        self.assertEqual(v["nameLengths"]["totalDistinctNameBytes"], 2113)
        self.assertEqual(v["nameLengths"]["simpleNameHistogram"]["65+"], 1)

    def test_conflicting_first_owner_rejected(self):
        d = document([event()])
        d["events"][0]["firstOwnerImageOrdinal"] = 1
        with self.assertRaisesRegex(CensusError, "first-owner mismatch"):
            analyze(d)

    def test_drift_in_declaration_rejected(self):
        d = document([event(), event(1, "nonroot")])
        d["events"][1]["genericIndex"] = 2
        with self.assertRaisesRegex(CensusError, "conflicting owner/declaration"):
            analyze(d)

    def test_conflicting_image_owner_rejected(self):
        d = document([event(), event(1, "nonroot", owner=1)])
        with self.assertRaisesRegex(CensusError, "conflicting owner/declaration"):
            analyze(d)

    def test_incomplete_input_is_lower_bound(self):
        v = analyze(document([event()], complete=False, dropped=4))
        self.assertEqual(v["analysisStatus"], "IncompleteLowerBound")
        self.assertEqual(v["events"]["dropped"], 4)
        self.assertFalse(v["capacityObservations"]["capacityDecisionAuthorized"])

    def test_false_completion_with_dropped_events_rejected(self):
        with self.assertRaisesRegex(CensusError, "completed source"):
            analyze(document([event()], dropped=1))

    def test_epoch_and_lock_admission_guarded(self):
        d = document([event()])
        d["source"]["metadataReaderEpoch"] = 2
        with self.assertRaisesRegex(CensusError, "initial metadata reader epoch"):
            analyze(d)
        d["source"]["metadataReaderEpoch"] = 1
        d["source"]["metadataLockHeld"] = False
        with self.assertRaisesRegex(CensusError, "metadata lock admission"):
            analyze(d)

    def test_malformed_fields_rejected(self):
        d = document([event()])
        d["source"]["declaredEvents"] = True
        with self.assertRaisesRegex(CensusError, "invalid unsigned integer"):
            analyze(d)
        d = document([event()])
        d["events"][0]["pointer"] = "not permitted"
        with self.assertRaisesRegex(CensusError, "unexpected"):
            analyze(d)
        d = document([event()])
        d["events"][0]["handleId"] = -1
        with self.assertRaisesRegex(CensusError, "invalid unsigned"):
            analyze(d)

    def test_duplicate_json_fields_and_non_finite_rejected(self):
        with self.assertRaisesRegex(CensusError, "duplicate JSON property"):
            load_bytes(b'{"schema":"a","schema":"b"}')
        with self.assertRaisesRegex(CensusError, "non-finite"):
            load_bytes(b'{"value":NaN}')

    def test_unverified_source_never_becomes_runtime_evidence(self):
        v = analyze(document([event()], kind="UnverifiedSource"))
        self.assertEqual(v["captureKind"], "UnverifiedSource")
        self.assertFalse(any(v["provenance"].values()))
        self.assertFalse(v["capacityObservations"]["capacityDecisionAuthorized"])

    def test_zero_events_remain_lower_bound(self):
        v = analyze(document([], classes=0))
        self.assertEqual(v["analysisStatus"], "IncompleteLowerBound")
        self.assertEqual(v["distinctTypeDefs"]["union"], 0)

    def test_cli_deterministic_output_and_fail_closed_exit(self):
        script = Path(__file__).with_name("analyze_typedef_census.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = (json.dumps(document([event(), event(1, "nonroot")]),
                              sort_keys=True) + "\n").encode("utf-8")
            inp = root / "trace.json"
            inp.write_bytes(raw)
            result = subprocess.run([sys.executable, str(script), "--input", str(inp)],
                                    text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["inputSha256"], hashlib.sha256(raw).hexdigest())
            self.assertFalse(parsed["provenance"]["inputOriginAuthenticated"])
            again = subprocess.run([sys.executable, str(script), "--input", str(inp)],
                                   text=True, capture_output=True, check=False)
            self.assertEqual(again.stdout, result.stdout)
            inp.write_text('{"schema":"bad"}', encoding="utf-8")
            failed = subprocess.run([sys.executable, str(script), "--input", str(inp)],
                                    text=True, capture_output=True, check=False)
            self.assertEqual(failed.returncode, 2)
            self.assertIn("CensusRejected", failed.stderr)


if __name__ == "__main__":
    unittest.main()
