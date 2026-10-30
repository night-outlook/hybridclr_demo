#!/usr/bin/env python3
"""Source-level R03 Unity BuildReport failure-path regressions (no Unity installed).

These are negative-order invariants on the actual C# source, not a C# execution
or an official IL2CPP build. The next Local cycle must test real failure/success.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "R03/PlayerProject/R03Build.cs"


def inspect(text: str) -> dict:
    """Fail closed on missing/duplicated mandatory outcome ordering."""
    keys = {
        "buildReport": "receipt.buildPipelineResult = report.summary.result.ToString();",
        "failedGate": "if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)",
        "emptyFailed": "receipt.playerFiles = new FileHash[0];",
        "failedReason": "throw new BuildFailedException(\"Actual IL2CPP native BuildPipeline failed:",
        "installedAfter": "receipt.installedAfter = Inventory(native);",
        "outputExists": "if (!Directory.Exists(config.outputPath))",
        "playerInventory": "receipt.playerFiles = Inventory(config.outputPath);",
        "successful": "receipt.result = \"Passed\";",
    }
    positions = {}
    for name, needle in keys.items():
        if text.count(needle) != 1:
            raise ValueError("Missing/duplicate actual BuildReport contract: " + name)
        positions[name] = text.index(needle)
    sequence = list(positions)
    if [positions[k] for k in sequence] != sorted(positions.values()):
        raise ValueError("BuildReport gate must precede optional output inventories")
    start = positions["failedGate"]
    end = positions["installedAfter"]
    failed = text[start:end]
    required = (
        'receipt.buildPipelineResult', 'receipt.errors',
        'receipt.playerInventoryStatus = Directory.Exists(config.outputPath)',
        'receipt.linkedDlls = new FileHash[0];',
        'receipt.playerFiles = new FileHash[0];',
        'receipt.result = "Passed"'  # must NOT occur inside failed branch
    )
    if not all(q in failed for q in required[:-1]) or required[-1] in failed:
        raise ValueError("Failure must remain Failed and preserve summary, not invent Player")
    if 'catch (Exception error) { receipt.exception = error.ToString(); throw; }' not in text:
        raise ValueError("The original compiler/BuildFailedException must be retained")
    if 'receipt.beeObservationPath = observation.Save(actualReport);' not in text:
        raise ValueError("Failed native build must retain optional Bee observation")
    if 'using (var stream = new FileStream(config.receiptPath, FileMode.CreateNew))' not in text:
        raise ValueError("Failed build receipt must be written once in finally")
    if 'result = "Failed"' not in text:
        raise ValueError("Initial receipt must be Failed, never optimistic")
    if 'public string buildPipelineResult;' not in text or 'public string playerInventoryStatus;' not in text:
        raise ValueError("Additive diagnostic fields must be serializable")
    return {"result": "PassedSourceOrderOnly_NotUnityRuntime",
            "errorGateBeforeInventory": True, "defaultFailed": True,
            "missingAppExplicit": True, "actualEditorBuildExecuted": False,
            "realFailedBuildRegression": "NotRun",
            "realSuccessfulPlayerRegression": "NotRun",
            "runtimeAcceptance": False}


class R03BuildFailureSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")

    def test_01_current_source_passes_order_contract(self):
        self.assertEqual(inspect(self.text)["result"], "PassedSourceOrderOnly_NotUnityRuntime")

    def test_02_missing_failure_gate_is_refused(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)", "if (false)"))

    def test_03_early_inventory_is_refused(self):
        expected = "receipt.playerFiles = Inventory(config.outputPath);"
        wrong = self.text.replace(expected, "")
        wrong = wrong.replace("receipt.installedAfter = Inventory(native);",
                              expected + "\n                receipt.installedAfter = Inventory(native);")
        with self.assertRaisesRegex(ValueError, "gate must precede"):
            inspect(wrong)

    def test_04_missing_failed_empty_inventory_is_refused(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("receipt.playerFiles = new FileHash[0];", "// missing failed inventory"))

    def test_05_optimistic_success_in_failed_branch_is_refused(self):
        altered = self.text.replace("receipt.linkedDlls = new FileHash[0];",
                                    'receipt.linkedDlls = new FileHash[0];\nreceipt.result = "Passed";')
        with self.assertRaises(ValueError):
            inspect(altered)

    def test_06_missing_Bee_capture_is_refused(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("receipt.beeObservationPath = observation.Save(actualReport);",
                                      "// lost Bee observation"))

    def test_07_missing_failure_receipt_write_is_refused(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("using (var stream = new FileStream(config.receiptPath, FileMode.CreateNew))",
                                      "using (var stream = File.OpenRead(config.receiptPath))"))

    def test_08_additive_failure_fields_required(self):
        with self.assertRaises(ValueError):
            inspect(self.text.replace("public string buildPipelineResult;", "// missing outcome field"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
