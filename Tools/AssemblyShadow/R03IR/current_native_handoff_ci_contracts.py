#!/usr/bin/env python3
"""Nine-workflow exact-commit Local handoff trigger contract; host only.

A push modifying canonical WEB_TO_LOCAL must trigger every mandatory CI
workflow. Host contract success is NOT proof those remote runs executed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
HANDOFF = "Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md"
BRANCH = "codex/assembly-shadow-r01b-h1"
WORKFLOWS = (
    "r03-ir-current-native-local-cycle-host.yml",
    "r03-ir-current-native-source-only.yml",
    "r03-ir-current-native-vm-delta-source-only.yml",
    "r03-ir-current-native-oracle-source-only.yml",
    "r03-ir-fixture.yml",
    "r03-ir-host.yml",
    "r03-k-host-contracts.yml",
    "r03-k-sourcecheck.yml",
    "r03-l-contracts.yml",
)

def inspect_workflow(name: str, content: str) -> dict:
    if not re.fullmatch(r"r03-[a-z0-9-]+\.yml", name):
        raise ValueError("Invalid workflow name")
    if not content.startswith("name: ") or "\non:\n  push:\n" not in content:
        raise ValueError("Missing push trigger: " + name)
    event = content.split("\non:\n  push:\n", 1)[1].split("\npermissions:\n", 1)[0]
    if not re.search(r"(?m)^    branches: .*" + re.escape(BRANCH), event):
        raise ValueError("Wrong branch: " + name)
    if event.count("    paths:\n") != 1:
        raise ValueError("Missing/ambiguous path filter: " + name)
    lines = event.split("    paths:\n", 1)[1].splitlines()
    paths = []
    for line in lines:
        if not line.startswith("      - "):
            break
        m = re.fullmatch(r"      - ['\"]([^'\"]+)['\"]", line)
        if m is None:
            raise ValueError("Nonliteral path filter: " + name)
        paths.append(m.group(1))
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate path filter: " + name)
    if paths.count(HANDOFF) != 1:
        raise ValueError("Handoff does not trigger: " + name)
    if paths.count(".github/workflows/" + name) != 1:
        raise ValueError("Workflow does not self-trigger: " + name)
    return {"workflow": name, "handoffTrigger": True, "selfTrigger": True,
            "pathCount": len(paths),
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}

def inspect_checkout(root: Path = ROOT) -> list[dict]:
    rows = []
    for name in WORKFLOWS:
        path = root / ".github" / "workflows" / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing/symlink workflow: " + name)
        rows.append(inspect_workflow(name, path.read_text(encoding="utf-8")))
    return rows

NATIVE_CI_WORKFLOWS = (
    "r03-ir-current-native-local-cycle-host.yml",
    "r03-ir-current-native-source-only.yml",
    "r03-ir-current-native-vm-delta-source-only.yml",
)

def native_checkout_ref(name: str, content: str) -> str:
    if name not in NATIVE_CI_WORKFLOWS:
        raise ValueError("Unknown native workflow")
    # A false pin in a comment cannot satisfy the actual actions/checkout
    # with.ref at its checked-out native repository.
    lines = content.splitlines()
    matched = []
    for i, line in enumerate(lines):
        if line.strip() == "repository: night-outlook/il2cpp_plus":
            block = lines[i+1:i+8]
            refs = [x.strip()[5:].strip() for x in block if x.strip().startswith("ref: ")]
            if len(refs) != 1:
                raise ValueError("Ambiguous native checkout ref: " + name)
            matched.extend(refs)
    # The combined workflow now makes TWO real native checkouts: original
    # source/host oracle and a second Local-layout checkout used by genuine
    # argparse(Path) admission. Both must use the exact SAME immutable SHA.
    expected_count = 2 if name == NATIVE_CI_WORKFLOWS[0] else 1
    if (len(matched) != expected_count or
        any(re.fullmatch(r"[0-9a-f]{40}", value) is None for value in matched) or
        len(set(matched)) != 1):
        raise ValueError("Missing, stale or ambiguous native checkout ref: " + name)
    return matched[0]

class TriggerContracts(unittest.TestCase):
    def test_actual_native_checkout_refs_match_candidate_source(self):
        from current_native_source_gate import CURRENT
        expected = CURRENT["il2cpp_plus"]
        self.assertEqual(len(NATIVE_CI_WORKFLOWS), 3)
        for name in NATIVE_CI_WORKFLOWS:
            raw = (ROOT / ".github" / "workflows" / name).read_text()
            with self.subTest(name=name):
                self.assertEqual(native_checkout_ref(name, raw), expected)
                changed = raw.replace("ref: " + expected, "ref: " + "0"*40, 1)
                with self.assertRaises((AssertionError, ValueError)):
                    self.assertEqual(native_checkout_ref(name, changed), expected)
                if name == NATIVE_CI_WORKFLOWS[0]:
                    # A correct first ref must not hide a stale second checkout.
                    index = raw.rfind("ref: " + expected)
                    self.assertGreater(index, raw.find("ref: " + expected))
                    stale_second = (raw[:index] + raw[index:].replace(
                        "ref: " + expected, "ref: " + "0"*40, 1))
                    with self.assertRaises(ValueError):
                        native_checkout_ref(name, stale_second)

    def test_exact_roster_and_all_real_workflows(self):
        self.assertEqual(len(WORKFLOWS), len(set(WORKFLOWS)))
        self.assertEqual(len(inspect_checkout()), 9)

    def test_each_missing_handoff_is_rejected(self):
        for name in WORKFLOWS:
            raw = (ROOT / ".github" / "workflows" / name).read_text()
            altered = raw.replace("      - '" + HANDOFF + "'\n", "", 1)
            with self.subTest(workflow=name), self.assertRaisesRegex(ValueError, "Handoff does not trigger"):
                inspect_workflow(name, altered)

    def test_unrelated_comment_cannot_forge_trigger(self):
        name = WORKFLOWS[0]
        raw = (ROOT / ".github" / "workflows" / name).read_text()
        raw = raw.replace("      - '" + HANDOFF + "'\n", "", 1) + "\n# " + HANDOFF
        with self.assertRaisesRegex(ValueError, "Handoff does not trigger"):
            inspect_workflow(name, raw)

    def test_duplicate_path_is_rejected(self):
        name = WORKFLOWS[0]
        raw = (ROOT / ".github" / "workflows" / name).read_text()
        raw = raw.replace("      - '" + HANDOFF + "'\n",
                          "      - '" + HANDOFF + "'\n      - '" + HANDOFF + "'\n", 1)
        with self.assertRaisesRegex(ValueError, "Duplicate path filter"):
            inspect_workflow(name, raw)

    def test_wrong_branch_is_rejected(self):
        name = WORKFLOWS[0]
        raw = (ROOT / ".github" / "workflows" / name).read_text()
        with self.assertRaisesRegex(ValueError, "Wrong branch"):
            inspect_workflow(name, raw.replace(BRANCH, "main", 1))

    def test_missing_push_is_rejected(self):
        name = WORKFLOWS[0]
        raw = (ROOT / ".github" / "workflows" / name).read_text()
        with self.assertRaisesRegex(ValueError, "Missing push"):
            inspect_workflow(name, raw.replace("\non:\n  push:\n", "\non:\n  manual:\n", 1))

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TriggerContracts))
    if result.wasSuccessful():
        print("R03_EXACT_HANDOFF_TRIGGERS=" + json.dumps(inspect_checkout(), sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
