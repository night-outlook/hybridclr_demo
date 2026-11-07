#!/usr/bin/env python3
"""Actual CLR fixture receipt + adversarial host-only captured-generic controls.

The positive is a genuine .NET8 closed MethodInfo, not an IL2CPP Player.
"""
import copy
import json
import os
from pathlib import Path
import unittest

from verify_captured_generic_host import HostRejected, loads, verify


class CapturedGenericHostContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = ("CAPTURED_OWNER_REPORT", "CAPTURED_OWNER_METHODS",
                 "CAPTURED_OWNER_SOURCE", "CAPTURED_OWNER_NATIVE")
        for name in names:
            if not os.environ.get(name):
                raise RuntimeError("Actual CLR source-bound CI input missing: " + name)
        cls.report, cls.methods, cls.owner, cls.native = [
            Path(os.environ[name]).read_bytes() for name in names]

    def check(self, report=None, methods=None, owner=None, native=None):
        return verify(self.report if report is None else report,
                      self.methods if methods is None else methods,
                      self.owner if owner is None else owner,
                      self.native if native is None else native)

    def test_01_actual_clr_closed_method_and_reference_owner(self):
        result = self.check()
        self.assertEqual(result["result"],
                         "PassedHostStructuralContextAndBodies_NotUnityOrNative")
        self.assertEqual(result["physicalOwner"], "R03CapturedGenericHost")
        self.assertEqual(result["capturedArgumentAssembly"], "Methods")
        self.assertEqual(result["prePositiveCalls"], 3)
        self.assertFalse(result["actualNativeCapturedFailure15"])
        self.assertFalse(result["R03Accepted"])

    def test_02_exact_typed_contract_and_rejection_mutations(self):
        original = loads(self.report)
        changes = (
            ("schemaVersion", True), ("schemaVersion", 2),
            ("kind", "R03NativeGeneric"), ("result", "Accepted"),
            ("ownerAssembly", "Methods"), ("ownerAssembly", ""),
            ("ownerMethod", "Methods.R03.Node.GenericKeep<T>"),
            ("capturedArgumentAssembly", "R03CapturedGenericHost"),
            ("capturedArgumentType", "R03.Unrelated"),
            ("ownerHasStaticMethodsDependency", True),
            ("ownerDifferentFromArgument", False),
            ("openGenericDefinition", False), ("closedGenericMethod", False),
            ("genericArity", True), ("genericArity", 0),
            ("referenceTypeConstraint", False),
            ("methodsSha256", "0"*64), ("methodsSha256", "a"*63),
            ("methodsMvid", "invalid"), ("methodsSize", True),
            ("methodsSize", original["methodsSize"] + 1),
            ("clrModuleMvidMatches", False),
            ("prewarmedReturn", 43), ("reflectiveReturn", 0),
            ("delegatedReturn", 13), ("callCountAfterWarm", True),
            ("callCountAfterWarm", 0), ("callCountAfterReflection", 1),
            ("callCountAfterDelegate", 2),
            ("wrongOwnerRejectedByWitnessContract", False),
            ("invalidValueTypeRejectedByCLR", False),
            ("il2cppMethodContextObserved", True),
            ("nativeGuardExecuted", True),
            ("capturedBaselineFailure15Observed", True),
            ("unityOrPlayerExecuted", True),
            ("originalSReusedAsNewInput", True),
            ("runtimeAcceptance", True), ("R03Accepted", True),
            ("H2Passed", True),
        )
        for field, value in changes:
            with self.subTest(field=field, mutation=value):
                new = copy.deepcopy(original)
                new[field] = value
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    self.check(report=(json.dumps(new)+"\n").encode())
        self.assertGreaterEqual(len(changes), 35)

    def test_03_missing_duplicate_and_extra_host_schema_are_rejected(self):
        original = loads(self.report)
        for key in ("kind", "methodsSha256", "ownerDifferentFromArgument"):
            changed = dict(original)
            changed.pop(key)
            with self.subTest(case="missing", key=key):
                with self.assertRaises(ValueError):
                    self.check(report=json.dumps(changed).encode())
        changed = dict(original, simulatedNativeErrorCode=15)
        with self.assertRaises(ValueError):
            self.check(report=json.dumps(changed).encode())
        duplicate = self.report.replace(b'"schemaVersion": 1,',
                                        b'"schemaVersion": 1, "schemaVersion": 1,', 1)
        self.assertNotEqual(duplicate, self.report)
        with self.assertRaises(ValueError):
            self.check(report=duplicate)

    def test_04_real_methods_bytes_must_be_exact(self):
        with self.assertRaisesRegex(HostRejected, "SHA/MVID/size"):
            self.check(methods=self.methods + b"mutated")
        with self.assertRaisesRegex(HostRejected, "SHA/MVID/size"):
            self.check(methods=b"")

    def test_05_actual_owner_source_required(self):
        raw = self.owner.replace(b"public static int Touch<T>() where T : class",
                                 b"public static int Touch<T>()")
        self.assertNotEqual(raw, self.owner)
        with self.assertRaisesRegex(HostRejected, "AOT owner source witness"):
            self.check(owner=raw)
        raw = self.owner.replace(b"Interlocked.Increment(ref s_calls)", b"return 42")
        self.assertNotEqual(raw, self.owner)
        with self.assertRaisesRegex(HostRejected, "AOT owner source witness"):
            self.check(owner=raw)

    def test_06_pinned_native_guard_source_required(self):
        raw = self.native.replace(b'Fail("CapturedBaselineType", candidate)',
                                  b'Fail("Other", candidate)')
        self.assertNotEqual(raw, self.native)
        with self.assertRaisesRegex(HostRejected, "Pinned native source guard"):
            self.check(native=raw)

    def test_07_reject_nonfinite_and_nonutf8_receipts(self):
        with self.assertRaises(ValueError):
            self.check(report=self.report[:-1] + b"\xff")
        with self.assertRaises(ValueError):
            self.check(report=b'{"schemaVersion": NaN}')

    def test_08_host_verifier_has_no_runtime_claim(self):
        report = self.check()
        for key in ("runtimeAcceptance", "R03Accepted", "H2Passed",
                    "actualIl2cppMethodContextObserved", "actualNativeCapturedFailure15",
                    "ReadyForHumanReviewGate"):
            self.assertIs(report[key], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
