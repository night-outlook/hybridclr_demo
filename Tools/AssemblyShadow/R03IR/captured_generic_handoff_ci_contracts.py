#!/usr/bin/env python3
"""A2 seven-workflow exact handoff-trigger audit, source-only.

Checks that the current WEB_TO_LOCAL.md push actually schedules each required
CI gate. DOES NOT claim that any workflow completed or Local is authorized.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import unittest

from current_native_handoff_ci_contracts import inspect_workflow, HANDOFF

ROOT = Path(__file__).resolve().parents[3]
NATIVE = "41764ae1eeefb33b05966e7f7676e52aae39c340"
REQUIRED = (
    "r03-ir-captured-generic-owner-host.yml",
    "r03-ir-captured-generic-native-host.yml",
    "r03-ir-captured-generic-batch-host.yml",
    "r03-ir-captured-generic-real-headers.yml",
    "r03-ir-initializer-bridge-host.yml",
    "r03-ir-initializer-local-contracts.yml",
    "r03-ir-current-native-local-cycle-host.yml",
)


def exact_native_checkout(workflow: str) -> bool:
    # Do not accept a matching SHA in comments or unrelated instructions.
    lines = workflow.splitlines()
    occurrences = []
    for i, line in enumerate(lines):
        if line.strip() != "repository: night-outlook/il2cpp_plus":
            continue
        block = lines[i+1:i+7]
        match = [x.strip()[5:].strip() for x in block if x.strip().startswith("ref: ")]
        if len(match) != 1:
            return False
        occurrences.append(match[0])
    return len(occurrences) == 1 and occurrences[0] == NATIVE


def verify_sources(inputs):
    if type(inputs) is not dict or set(inputs) != set(REQUIRED):
        raise ValueError("Exact seven mandatory A2 workflow inputs required")
    rows = []
    for name in REQUIRED:
        raw = inputs[name]
        if type(raw) is not str:
            raise ValueError("Actual YAML source text required")
        result = inspect_workflow(name, raw)
        if name == "r03-ir-captured-generic-real-headers.yml":
            if not exact_native_checkout(raw):
                raise ValueError("A2 public-native fork checkout not pinned to reviewed 40-char commit")
            if "NO official Unity SDK" not in raw and "no vendor Unity SDK" not in raw:
                raise ValueError("Public-fork source audit cannot pose as official SDK C++ compile")
        rows.append(result)
    return {
        "kind": "R03A2SevenWorkflowHandoffTriggerV1",
        "result": "PassedSevenSourceTriggers_NotWorkflowCompletion",
        "workflows": rows,
        "allHandoffTriggersSourceVerified": True,
        "actualWorkflowJobsInspected": False,
        "realUnitySdkCompiled": False,
        "actualNativeCapturedError15": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }


def actual_inputs():
    result = {}
    for name in REQUIRED:
        p = ROOT / ".github/workflows" / name
        if not p.is_file() or p.is_symlink():
            raise ValueError("Missing/aliased workflow source: " + name)
        result[name] = p.read_text(encoding="utf-8")
    return result


class HandoffSevenTriggerContracts(unittest.TestCase):
    def test_01_real_seven_trigger_sources(self):
        result = verify_sources(actual_inputs())
        self.assertEqual(len(result["workflows"]), 7)
        self.assertEqual(result["result"], "PassedSevenSourceTriggers_NotWorkflowCompletion")
        for k in ("actualWorkflowJobsInspected", "realUnitySdkCompiled",
                  "actualNativeCapturedError15", "runtimeAcceptance", "R03Accepted"):
            self.assertIs(result[k], False)

    def test_02_any_missing_workflow_is_refused(self):
        inputs = actual_inputs()
        for name in REQUIRED:
            with self.subTest(missing=name), self.assertRaises(ValueError):
                verify_sources({k:v for k,v in inputs.items() if k != name})

    def test_03_any_missing_handoff_trigger_is_refused(self):
        inputs = actual_inputs()
        for name in REQUIRED:
            altered = dict(inputs)
            row = "      - '" + HANDOFF + "'\n"
            self.assertIn(row, altered[name])
            altered[name] = altered[name].replace(row, "", 1)
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify_sources(altered)

    def test_04_wrong_native_checkout_ref_is_refused(self):
        inputs = actual_inputs()
        name = "r03-ir-captured-generic-real-headers.yml"
        self.assertTrue(exact_native_checkout(inputs[name]))
        changed = dict(inputs)
        changed[name] = changed[name].replace("ref: " + NATIVE, "ref: " + "0"*40, 1)
        with self.assertRaises(ValueError):
            verify_sources(changed)

    def test_05_no_skipping_or_reclassification(self):
        inputs = actual_inputs()
        self.assertEqual(len(REQUIRED), len(set(REQUIRED)))
        self.assertFalse(verify_sources(inputs)["actualWorkflowJobsInspected"])
        for bad in ("r03-ir-captured-generic-source-skipped.yml",
                    "r03-ir-captured-generic-not-implemented.yml"):
            self.assertNotIn(bad, REQUIRED)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HandoffSevenTriggerContracts)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print(json.dumps(verify_sources(actual_inputs()), sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
