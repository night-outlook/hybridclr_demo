from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r00_results as gate
from shadow_tools import VerificationError


class R00OperationGateTests(unittest.TestCase):
    def observations(self, mode):
        rows = []
        constructors = 0
        for operation in gate.OPERATIONS:
            for phase, count, seed in gate.PHASES:
                allocation = operation == "allocation"
                before = constructors if allocation else 0
                after = before + count if allocation else 0
                if allocation:
                    constructors = after
                checksum = gate.expected_checksum(operation, mode, count, seed)
                rows.append(dict(operation=operation, phase=phase, requestedIterations=count,
                                 methodCalls=1 if allocation else count, actualNewCount=count if allocation else 0,
                                 actualInvocationCount=0 if allocation else count, checksum=checksum,
                                 expectedChecksum=checksum, constructorCountBefore=before, constructorCountAfter=after,
                                 elapsedTicks=123, stopwatchFrequency=1_000_000_000, passed=True))
        return rows

    def test_four_worlds_and_signed_overflow_have_independent_oracles(self):
        self.assertEqual(gate.expected_checksum("allocation", gate.MODES[0], 1, 17), 3301)
        self.assertEqual(gate.int32(2**31), -(2**31))
        self.assertEqual(gate.int32(2**32 + 13), 13)
        for mode in gate.MODES:
            self.assertEqual(len(gate.verify_operations(self.observations(mode), mode)), 12)

    def test_reported_expected_value_cannot_conceal_bad_checksum(self):
        rows = self.observations(gate.MODES[1])
        rows[3]["checksum"] += 1
        rows[3]["expectedChecksum"] += 1
        with self.assertRaises(VerificationError):
            gate.verify_operations(rows, gate.MODES[1])

    def test_missing_duplicate_or_reordered_phases_reject(self):
        rows = self.observations(gate.MODES[2])
        for changed in (rows[:-1], rows + [rows[0]], [rows[1], rows[0]] + rows[2:]):
            with self.assertRaises(VerificationError):
                gate.verify_operations(changed, gate.MODES[2])

    def test_iteration_claims_require_matching_constructor_count(self):
        rows = self.observations(gate.MODES[0])
        rows[3]["constructorCountAfter"] -= 1
        with self.assertRaises(VerificationError):
            gate.verify_operations(rows, gate.MODES[0])

    def test_timing_and_boolean_integer_aliases_reject(self):
        for field, value in (("requestedIterations", True), ("elapsedTicks", -1),
                             ("stopwatchFrequency", 0), ("passed", 1)):
            with self.subTest(field=field):
                rows = self.observations(gate.MODES[0])
                rows[0][field] = value
                with self.assertRaises(VerificationError):
                    gate.verify_operations(rows, gate.MODES[0])

    def test_constructor_reset_between_batches_rejects(self):
        rows = self.observations(gate.MODES[0])
        rows[2]["constructorCountBefore"] = 0
        rows[2]["constructorCountAfter"] = 10
        with self.assertRaises(VerificationError):
            gate.verify_operations(rows, gate.MODES[0])


if __name__ == "__main__":
    unittest.main()
