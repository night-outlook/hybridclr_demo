import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "Tools/AssemblyShadow"
sys.path.insert(0, str(TOOLS))

import h1_graph_reuse as reuse
import r00_player_inputs
import shadow_tools
from shadow_tools import PINS, VerificationError


class H1GraphReuseTests(unittest.TestCase):
    def real_old_pins(self):
        return reuse._git_json(ROOT, reuse.GRAPH_SOURCE_REVISION, PINS)

    def successor_pins_at_head(self):
        pins = copy.deepcopy(self.real_old_pins())
        entries = pins.get("repositories", pins)
        entries["demo"]["revision"] = shadow_tools.git(ROOT, "rev-parse", "HEAD").decode().strip()
        return pins

    def test_real_69130_graph_to_current_tool_only_successor_matches_exact_policy(self):
        old_pins = self.real_old_pins()
        current_pins = self.successor_pins_at_head()
        result = reuse.authenticate_transition(ROOT, old_pins, current_pins)
        self.assertEqual(result["policyId"], reuse.POLICY_ID)
        self.assertEqual(result["graphDemoRevision"], reuse.GRAPH_SOURCE_REVISION)
        self.assertEqual(
            {row["path"] for row in result["nonMetadataDelta"]},
            set(reuse.ALLOWED_NON_METADATA_PATHS))
        self.assertTrue(all(
            row["path"].startswith(".github/") or row["path"].startswith("Tools/AssemblyShadow/")
            for row in result["nonMetadataDelta"]))

    def test_real_transition_rejects_runtime_pin_change(self):
        old_pins = self.real_old_pins()
        current_pins = self.successor_pins_at_head()
        entries = current_pins.get("repositories", current_pins)
        entries["hybridclr"]["revision"] = "0" * 40
        with self.assertRaises(VerificationError):
            reuse.authenticate_transition(ROOT, old_pins, current_pins)

    def test_real_transition_rejects_graph_revision_other_than_retained_anchor(self):
        old_pins = self.real_old_pins()
        old_entries = old_pins.get("repositories", old_pins)
        old_entries["demo"]["revision"] = "0" * 40
        with self.assertRaises(VerificationError):
            reuse.authenticate_transition(ROOT, old_pins, self.successor_pins_at_head())

    def test_default_r00_pairing_stays_current_only(self):
        project = ROOT.resolve()
        current = {"schemaVersion": 1, "demo": {"revision": "current"}}
        marker = {"sourcePins": current}
        with mock.patch.object(r00_player_inputs, "read_json", return_value=current), \
             mock.patch.object(r00_player_inputs, "_verify_inputs", return_value=marker) as internal:
            result = r00_player_inputs.verify_inputs(
                project, Path("fixture"), Path("on"), Path("off"), Path("replay"))
        self.assertIs(result, marker)
        self.assertEqual(internal.call_args.args[-1], current)

    def test_reuse_r00_pairing_requires_authenticated_authority_and_preserves_current_pin(self):
        project = ROOT.resolve()
        current = {"schemaVersion": 1, "demo": {"revision": "current"}}
        graph = {"schemaVersion": 1, "demo": {"revision": reuse.GRAPH_SOURCE_REVISION}}
        authority = {
            "kind": reuse.AUTHORITY_KIND,
            "projectRoot": str(project),
            "graphSourcePins": graph,
            "currentSourcePins": current,
            "bridgeReceipt": {"path": "/tmp/bridge.json", "sha256": "1" * 64},
        }
        marker = {"sourcePins": graph, "currentSourcePins": current}
        with mock.patch.object(r00_player_inputs, "read_json", return_value=current), \
             mock.patch.object(r00_player_inputs, "_verify_inputs", return_value=marker) as internal:
            result = r00_player_inputs.verify_inputs_with_reuse(
                project, Path("fixture"), Path("on"), Path("off"), Path("replay"), authority)
        self.assertIs(result, marker)
        self.assertEqual(internal.call_args.args[-1], graph)

        bad = dict(authority)
        bad["kind"] = "Untrusted"
        with self.assertRaises(VerificationError):
            r00_player_inputs.verify_inputs_with_reuse(
                project, Path("fixture"), Path("on"), Path("off"), Path("replay"), bad)

    def test_source_contract_does_not_modify_require_current_pairing(self):
        source = (TOOLS / "r00_player_inputs.py").read_text()
        start = source.index("def require_current_pairing")
        end = source.index("\n\ndef ", start)
        body = source[start:end]
        self.assertIn("m07.prior._pins(captured, label, expected)", body)
        self.assertIn("m07.exact(captured, expected, label + \".sourcePins\")", body)
        self.assertNotIn("reuse", body.lower())
        self.assertNotIn("override", body.lower())

    def test_analyzer_requires_explicit_bridge_and_seal(self):
        source = (TOOLS / "analyze-h1-paired-performance.py").read_text()
        self.assertIn("--pilot-verification-receipt", source)
        self.assertIn("--graph-reuse-bridge", source)
        self.assertIn("graph_reuse.verify_bridge_full", source)
        self.assertIn("pairing_authority=authority", source)


if __name__ == "__main__":
    unittest.main()
