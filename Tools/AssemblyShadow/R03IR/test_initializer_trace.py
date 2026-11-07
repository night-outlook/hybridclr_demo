#!/usr/bin/env python3
"""Synthetic adversarial native initializer journal semantic contracts, not Unity."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from verify_initializer_trace import TraceRejected, parse, summarize, inspect


def fixture(mode="initializer-failure"):
    request = {"runId": "HostInitializerEvidenceRun000001",
               "caseId": "HOST-INIT", "stimulus": mode, "dllSha256": "a" * 64}
    phases = (100, 101, 103, 299, 300, 190, 191, 201, 230, 231, 205,
              400, 401, 600, 601, 602, 603, 620)
    rows = []
    for i, stage in enumerate(phases, 1):
        row = {
            "kind": "R03IRInitializerNativeTraceV1",
            "runId": request["runId"], "caseId": request["caseId"],
            "stimulus": mode, "fixtureSha256": request["dllSha256"],
            "pid": 521, "seq": i, "phase": stage,
            "a": 1 if stage in (100, 101, 103, 230, 231, 299, 300, 400, 620) else 0,
            "b": 0, "c": 0, "d": 0,
            "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
        }
        if stage == 191:
            row["a"] = 19 if mode == "initializer-failure" else 0
        if stage == 600:
            row["a"], row["b"] = ((19, 9) if mode == "initializer-failure" else (0, 6))
        rows.append(row)
    return rows, request


def encode(rows):
    return b"".join((json.dumps(x, sort_keys=True, separators=(",", ":")) + "\n").encode()
                    for x in rows)


class NativeInitializerTraceContracts(unittest.TestCase):
    def test_01_two_positive_phase_diaries_not_acceptance(self):
        for mode in ("initializer-control", "initializer-failure"):
            rows, request = fixture(mode)
            got = parse(encode(rows), request, 521, request["dllSha256"])
            result = summarize(got, require_complete=True)
            self.assertEqual(result["result"], "CompletePhaseTrace_NotRuntimeAuthenticated")
            self.assertFalse(result["R03Accepted"])
            self.assertFalse(result["completeStrictObservationProven"])

    def test_02_mutation_fail_closed(self):
        rows, request = fixture()
        changes = {
            "kind": "R03IRInitializerCommitObservationV1",
            "runId": "different-run",
            "caseId": "different-case",
            "stimulus": "initializer-control",
            "fixtureSha256": "b" * 64,
            "pid": 522,
            "seq": 20,
            "phase": 9999,
            "a": True,
            "runtimeAcceptance": True,
            "R03Accepted": True,
            "H2Passed": True,
        }
        for key, value in changes.items():
            with self.subTest(field=key):
                copy_rows = copy.deepcopy(rows)
                copy_rows[1][key] = value
                with self.assertRaises(TraceRejected):
                    parse(encode(copy_rows), request, 521, request["dllSha256"])

    def test_03_duplicate_and_trailing_and_partial_rejected(self):
        rows, request = fixture()
        base = encode(rows)
        rejects = [
            b'{"kind":"X","kind":"Y"}\n' + base,
            base + b"\n", base[:-1],
            base.replace(b"false", b"NaN", 1),
            base + b"x" * 65537,
            b"",
        ]
        for raw in rejects:
            with self.subTest(length=len(raw)), self.assertRaises((TraceRejected, ValueError)):
                parse(raw, request, 521, request["dllSha256"])

    def test_04_lack_of_real_native_callback_read_seal_is_not_complete(self):
        for stage in (103, 299, 300, 400, 620):
            rows, request = fixture()
            reduced = [r for r in rows if r["phase"] != stage]
            for i, r in enumerate(reduced, 1):
                r["seq"] = i
            got = parse(encode(reduced), request, 521, request["dllSha256"])
            with self.subTest(stage=stage), self.assertRaises(TraceRejected):
                summarize(got, require_complete=True)

    def test_04b_actual_linked_bridge_must_be_nonnull_and_unique(self):
        rows, request = fixture()
        index = next(i for i, r in enumerate(rows) if r["phase"] == 103)
        self.assertEqual(rows[index]["a"], 1)
        for value in (-1, -2, 0, 2):
            mutated = copy.deepcopy(rows)
            mutated[index]["a"] = value
            parsed = parse(encode(mutated), request, 521, request["dllSha256"])
            with self.subTest(value=value), self.assertRaises(TraceRejected):
                summarize(parsed, require_complete=True)

    def test_05_failure_diary_stays_non_authorizing(self):
        rows, request = fixture()
        rows = rows[:4]
        rows[-1]["phase"], rows[-1]["a"] = 300, -7
        rows.append(dict(rows[-1], seq=5, phase=900, a=190))
        rows.append(dict(rows[-1], seq=6, phase=610, a=-2, b=3))
        parsed = parse(encode(rows), request, 521, request["dllSha256"])
        report = summarize(parsed)
        self.assertEqual(report["nativeCallbackFailures"], [-7])
        self.assertEqual(report["nativeSealFailures"][0]["reason"], 3)
        self.assertEqual(report["managedCaughtPhase"], [190])
        self.assertEqual(report["result"], "BoundedTraceObserved_NotRuntimeAuthenticated")
        with self.assertRaises(TraceRejected):
            summarize(parsed, require_complete=True)

    def test_06_real_temp_raw_bytes_are_bound_to_request_pid(self):
        rows, request = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagnostic.native-trace.jsonl"
            path.write_bytes(encode(rows))
            verdict = inspect(path, request, 521, request["dllSha256"], require_complete=True)
            self.assertEqual(verdict["rawBytes"], path.stat().st_size)
            self.assertEqual(len(verdict["rawSha256"]), 64)
            self.assertIs(verdict["runtimeAcceptance"], False)
            with self.assertRaises(TraceRejected):
                inspect(path, request, 522, request["dllSha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
