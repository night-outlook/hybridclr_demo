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
import h1_historical_reanalysis as historical
import h1_paired_performance as paired
import r00_player_inputs
import r00_results
import r01_early_results as early_results
import shadow_tools

_analyzer_spec = __import__("importlib.util").util.spec_from_file_location(
    "h1_reuse_analyzer_test", TOOLS / "analyze-h1-paired-performance.py")
analyzer = __import__("importlib.util").util.module_from_spec(_analyzer_spec)
_analyzer_spec.loader.exec_module(analyzer)
from shadow_tools import PINS, VerificationError


class H1GraphReuseTests(unittest.TestCase):
    def successor_pins_at_head(self):
        pins = shadow_tools.read_json(ROOT / PINS)
        pins = copy.deepcopy(pins)
        entries = pins.get("repositories", pins)
        entries["demo"]["revision"] = shadow_tools.git(ROOT, "rev-parse", "HEAD").decode().strip()
        return pins

    def real_old_pins(self):
        return reuse.retained_graph_pins(self.successor_pins_at_head())

    def test_returned_analysis_failure_is_exact_real_producer_shape(self):
        diagnosis_path = (
            ROOT / "Docs/AssemblyShadow/History/M07R/H1/"
            "local-validation-20260923-authority27df-formal-analysis-blocked/"
            "V04/performance/final-analysis-contract-failure.json"
        )
        diagnosis = json.loads(diagnosis_path.read_text())
        contract = diagnosis["contractDiagnosis"]
        self.assertTrue(contract["rawTopLevelBaselineBuildIdPresent"])
        self.assertTrue(contract["rawTopLevelRuntimeAbiHashPresent"])
        self.assertFalse(contract["rawPlayerBuildReceiptBaselineBuildIdPresent"])
        self.assertFalse(contract["rawPlayerBuildReceiptRuntimeAbiHashPresent"])
        self.assertEqual(
            contract["analyzerRequiresNestedFields"],
            ["buildGuid", "baselineBuildId", "runtimeAbiHash"])

    def test_analyzer_build_binding_matches_real_r00_producer_contract(self):
        expected = {
            "path": "/tmp/m07-player-build.json",
            "sha256": "a" * 64,
            "receipt": {
                "buildGuid": "build-guid",
                "baselineBuildId": "baseline-id",
                "runtimeAbiHash": "b" * 64,
            },
        }
        raw = {
            "buildGuid": "build-guid",
            "baselineBuildId": "baseline-id",
            "runtimeAbiHash": "b" * 64,
            "playerBuildReceipt": {
                "path": expected["path"],
                "sha256": expected["sha256"],
                "buildGuid": "build-guid",
            },
        }
        paired._check_build_binding(raw, expected)

        for field, bad_value in (
            ("buildGuid", "other-guid"),
            ("baselineBuildId", "other-baseline"),
            ("runtimeAbiHash", "c" * 64),
        ):
            with self.subTest(topLevelField=field):
                changed = copy.deepcopy(raw)
                changed[field] = bad_value
                with self.assertRaisesRegex(
                        VerificationError, "top-level build field differs: " + field):
                    paired._check_build_binding(changed, expected)

        for field in ("baselineBuildId", "runtimeAbiHash"):
            with self.subTest(missingTopLevelField=field):
                changed = copy.deepcopy(raw)
                del changed[field]
                with self.assertRaisesRegex(
                        VerificationError, "top-level build field differs: " + field):
                    paired._check_build_binding(changed, expected)

        for field, bad_value in (
            ("baselineBuildId", "nested-wrong"),
            ("runtimeAbiHash", "d" * 64),
        ):
            with self.subTest(conflictingOptionalNestedField=field):
                changed = copy.deepcopy(raw)
                changed["playerBuildReceipt"][field] = bad_value
                with self.assertRaisesRegex(
                        VerificationError, "nested build field differs: " + field):
                    paired._check_build_binding(changed, expected)

    def test_historical_reanalysis_delta_is_exact_analysis_only_successor(self):
        current = shadow_tools.git(ROOT, "rev-parse", "HEAD").decode().strip()
        result = historical.authenticate_analysis_delta(ROOT, current)
        self.assertEqual(result["policyId"], historical.POLICY_ID)
        self.assertEqual(
            {row["path"] for row in result["nonMetadataDelta"]},
            set(historical.ALLOWED_ANALYSIS_DELTA))
        forbidden = (
            "run-r00-players.py", "r00_results.py", "r00_player_inputs.py",
            "run-h1-paired-performance.py", "seal-h1-pilot-verification.py",
        )
        self.assertTrue(all(
            not any(row["path"].endswith(name) for name in forbidden)
            for row in result["nonMetadataDelta"]))

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

    def test_real_transition_on_pilot_nested_early_prepare_preserves_authenticated_authority(self):
        current = self.successor_pins_at_head()
        graph = reuse.retained_graph_pins(current)
        transition = reuse.authenticate_transition(ROOT, graph, current)
        self.assertEqual(transition["graphDemoRevision"], reuse.GRAPH_SOURCE_REVISION)
        authority = {
            "kind": reuse.AUTHORITY_KIND,
            "projectRoot": str(ROOT.resolve()),
            "graphSourcePins": graph,
            "currentSourcePins": current,
            "bridgeReceipt": {"path": "/tmp/h1-graph-reuse-bridge.json", "sha256": "1" * 64},
            "policyId": reuse.POLICY_ID,
        }
        context = {
            "baseline": {"nativeBudgetCapabilityVersion": 2},
            "sourcePins": graph,
        }

        class Runner:
            @staticmethod
            def collect_inputs(_fixture, _replay, _builds):
                return {Path("/tmp/on-pilot-input")}

        with mock.patch.object(
                early_results, "verify_inputs",
                side_effect=AssertionError("nested early prepare fell back to current-pairing verification")), \
             mock.patch.object(
                early_results, "verify_inputs_with_reuse",
                return_value=context) as reuse_verify, \
             mock.patch.object(early_results.failures, "metadata_profile", return_value=2), \
             mock.patch.object(early_results, "_load_runner", return_value=Runner()), \
             mock.patch.object(
                early_results.m07, "verify_inputs",
                return_value=({}, {}, [], [], {"resource": "bound"})):
            prepared = early_results._prepare(
                ROOT.resolve(), Path("/tmp/fixture"), Path("/tmp/on"), Path("/tmp/off"),
                Path("/tmp/replay"), None, None, ["Baseline"],
                pairing_authority=authority)

        reuse_verify.assert_called_once_with(
            ROOT.resolve(), Path("/tmp/fixture"), Path("/tmp/on"), Path("/tmp/off"),
            Path("/tmp/replay"), authority)
        self.assertIs(prepared["context"], context)
        self.assertEqual(prepared["profile"], 2)
        self.assertEqual(prepared["baselineResources"], {"resource": "bound"})

    def test_nested_early_reuse_authority_rejects_nonperformance_modes(self):
        authority = {
            "kind": reuse.AUTHORITY_KIND,
            "projectRoot": str(ROOT.resolve()),
            "graphSourcePins": self.real_old_pins(),
            "currentSourcePins": self.successor_pins_at_head(),
            "bridgeReceipt": {"path": "/tmp/h1-graph-reuse-bridge.json", "sha256": "1" * 64},
        }
        for mode in ("OrdinaryFirst", "MetadataFailure", "Type"):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(
                        VerificationError, "limited to R00 performance Baseline/Control"):
                    early_results._prepare(
                        ROOT.resolve(), Path("/tmp/fixture"), Path("/tmp/on"), Path("/tmp/off"),
                        Path("/tmp/replay"), None, None, [mode],
                        pairing_authority=authority)

    def test_r00_threads_authority_while_direct_early_verifier_stays_current_pairing_only(self):
        r00_source = (TOOLS / "r00_results.py").read_text()
        self.assertGreaterEqual(
            r00_source.count("pairing_authority=pairing_authority"), 2)

        early_source = (TOOLS / "r01_early_results.py").read_text()
        self.assertIn("def verify_suite(launch_path: Path) -> dict[str, Any]:", early_source)
        self.assertNotIn(
            "def verify_suite(launch_path: Path, pairing_authority", early_source)
        self.assertIn(
            "verify_inputs_with_reuse(project, fixture, on, off, replay, pairing_authority)",
            early_source)

        start = early_source.index("def _prepare")
        end = early_source.index("\n\ndef _capsule_for", start)
        prepare_body = early_source[start:end]
        self.assertIn("*, pairing_authority:", prepare_body)
        self.assertIn("if pairing_authority is None", prepare_body)
        self.assertIn("verify_inputs(project, fixture, on, off, replay)", prepare_body)
        self.assertIn(
            "verify_inputs_with_reuse(project, fixture, on, off, replay, pairing_authority)",
            prepare_body)

        verify_start = early_source.index("def verify_suite(launch_path: Path)")
        verify_end = early_source.find("\n\ndef ", verify_start + 1)
        verify_body = early_source[verify_start:verify_end if verify_end >= 0 else len(early_source)]
        self.assertNotIn("pairing_authority=", verify_body)

    def test_analyzer_prepare_reuse_binds_same_seal_bridge_and_formal_side_authority(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "project"
            project.mkdir()
            build_map = root / "build-map.json"
            build_map.write_text("{}", encoding="utf-8")
            bridge = root / "bridge.json"
            bridge.write_text(json.dumps({"projectRoot": str(project)}), encoding="utf-8")
            pilot = root / "pilot.json"
            pilot.write_text(json.dumps({
                "kind": "H1PilotVerificationReceipt",
                "status": "PassedStrictReconstructionAndStatGuardSealed",
                "graphReuseBridge": analyzer._binding(bridge),
            }), encoding="utf-8")
            fixture = root / "fixture.json"; fixture.write_text("{}", encoding="utf-8")
            on = root / "on.json"; on.write_text("{}", encoding="utf-8")
            off = root / "off.json"; off.write_text("{}", encoding="utf-8")
            replay = root / "replay.json"; replay.write_text("{}", encoding="utf-8")
            formal_authority = root / "formal-authority.json"
            formal_output = project / "_temp/AssemblyShadow/formal-01-B"
            formal_output.parent.mkdir(parents=True)
            formal_authority.write_text(json.dumps({
                "projectRoot": str(project),
                "runnerOutputRoot": str(formal_output),
                "fixtureManifest": analyzer._binding(fixture),
                "nativeOnReceipt": analyzer._binding(on),
                "nativeOffReceipt": analyzer._binding(off),
                "editorReplayReceipt": analyzer._binding(replay),
            }), encoding="utf-8")
            authority_binding = analyzer._binding(formal_authority)
            launch_a = root / "launch-a.json"
            launch_a.write_text(json.dumps({"formalLaunchAuthority": None}), encoding="utf-8")
            launch_b = root / "launch-b.json"
            launch_b.write_text(json.dumps({
                "projectRoot": str(project),
                "fixtureManifestPath": str(fixture),
                "nativeOnReceipt": str(on),
                "nativeOffReceipt": str(off),
                "editorReplayReceipt": str(replay),
                "formalLaunchAuthority": authority_binding,
            }), encoding="utf-8")
            sample = root / "sample.json"
            attempt = {
                "pairId": "formal-01",
                "attempt": 1,
                "mode": "R00-OFF-NoPatch",
                "phase": "formal",
                "pilotVerification": analyzer._binding(pilot),
                "graphReuseBridge": analyzer._binding(bridge),
                "A": {
                    "formalLaunchAuthority": None,
                    "launchReceipt": analyzer._binding(launch_a),
                },
                "B": {
                    "formalLaunchAuthority": authority_binding,
                    "launchReceipt": analyzer._binding(launch_b),
                },
            }
            sample.write_text(json.dumps({
                "buildMap": analyzer._binding(build_map),
                "attempts": [attempt],
            }), encoding="utf-8")
            authority = {
                "kind": reuse.AUTHORITY_KIND,
                "projectRoot": str(project),
                "graphSourcePins": {"schemaVersion": 1},
                "currentSourcePins": {"schemaVersion": 1},
                "bridgeReceipt": analyzer._binding(bridge),
            }
            verified_formal = {
                "graphReuseBridge": analyzer._binding(bridge),
                "pilotVerification": analyzer._binding(pilot),
                "pairingAuthority": authority,
            }
            with mock.patch.object(
                    analyzer.graph_reuse, "verify_bridge_full", return_value=authority), \
                 mock.patch.object(
                    analyzer.formal_authority, "verify_receipt",
                    return_value=verified_formal) as formal_verify:
                prepared = analyzer._prepare_reuse(sample, pilot, bridge)
            self.assertEqual(prepared["authority"], authority)
            self.assertEqual(prepared["pilotVerification"], analyzer._binding(pilot))
            self.assertEqual(prepared["graphReuseBridge"], analyzer._binding(bridge))
            formal_verify.assert_called_once_with(
                formal_authority, project, "R00-OFF-NoPatch",
                fixture, on, off, replay, formal_output,
                expected_pair_id="formal-01", expected_attempt=1)

            value = json.loads(sample.read_text())
            value["attempts"][0]["A"]["formalLaunchAuthority"] = authority_binding
            sample.write_text(json.dumps(value), encoding="utf-8")
            with mock.patch.object(analyzer.graph_reuse, "verify_bridge_full", return_value=authority):
                with self.assertRaisesRegex(VerificationError, "protected formal side A"):
                    analyzer._prepare_reuse(sample, pilot, bridge)

    def test_analyzer_retains_failed_formal_side_b_authority_without_launch_receipt(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "project"; project.mkdir()
            build_map = root / "build-map.json"; build_map.write_text("{}", encoding="utf-8")
            bridge = root / "bridge.json"; bridge.write_text(json.dumps({"projectRoot": str(project)}), encoding="utf-8")
            pilot = root / "pilot.json"
            pilot.write_text(json.dumps({
                "kind": "H1PilotVerificationReceipt",
                "status": "PassedStrictReconstructionAndStatGuardSealed",
                "graphReuseBridge": analyzer._binding(bridge),
            }), encoding="utf-8")
            fixture = root / "fixture.json"; fixture.write_text("{}", encoding="utf-8")
            on = root / "on.json"; on.write_text("{}", encoding="utf-8")
            off = root / "off.json"; off.write_text("{}", encoding="utf-8")
            replay = root / "replay.json"; replay.write_text("{}", encoding="utf-8")
            auth = root / "authority.json"
            failed_output = project / "_temp/AssemblyShadow/formal-failed-B"
            failed_output.parent.mkdir(parents=True)
            auth.write_text(json.dumps({
                "projectRoot": str(project),
                "runnerOutputRoot": str(failed_output),
                "fixtureManifest": analyzer._binding(fixture),
                "nativeOnReceipt": analyzer._binding(on),
                "nativeOffReceipt": analyzer._binding(off),
                "editorReplayReceipt": analyzer._binding(replay),
            }), encoding="utf-8")
            auth_binding = analyzer._binding(auth)
            sample = root / "sample.json"
            sample.write_text(json.dumps({
                "buildMap": analyzer._binding(build_map),
                "attempts": [{
                    "pairId": "formal-failed",
                    "attempt": 1,
                    "mode": "R00-OFF-NoPatch",
                    "phase": "formal",
                    "pilotVerification": analyzer._binding(pilot),
                    "graphReuseBridge": analyzer._binding(bridge),
                    "A": {"formalLaunchAuthority": None, "launchReceipt": None, "status": "Passed"},
                    "B": {"formalLaunchAuthority": auth_binding, "launchReceipt": None, "status": "Failed"},
                }],
            }), encoding="utf-8")
            pairing = {
                "kind": reuse.AUTHORITY_KIND,
                "projectRoot": str(project),
                "graphSourcePins": {},
                "currentSourcePins": {},
                "bridgeReceipt": analyzer._binding(bridge),
            }
            verified = {
                "graphReuseBridge": analyzer._binding(bridge),
                "pilotVerification": analyzer._binding(pilot),
                "pairingAuthority": pairing,
            }
            with mock.patch.object(analyzer.graph_reuse, "verify_bridge_full", return_value=pairing), \
                 mock.patch.object(analyzer.formal_authority, "verify_receipt", return_value=verified) as verify:
                prepared = analyzer._prepare_reuse(sample, pilot, bridge)
            self.assertEqual(prepared["authority"], pairing)
            verify.assert_called_once()

    def test_analyzer_requires_explicit_bridge_and_seal(self):
        source = (TOOLS / "analyze-h1-paired-performance.py").read_text()
        self.assertIn("--pilot-verification-receipt", source)
        self.assertIn("--graph-reuse-bridge", source)
        self.assertIn("graph_reuse.verify_bridge_full", source)
        self.assertIn("pairing_authority=authority", source)


if __name__ == "__main__":
    unittest.main()
