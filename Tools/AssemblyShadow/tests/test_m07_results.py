"""Focused schema and tamper tests for the strict M07 evidence gate."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m07_results as gate
from shadow_tools import VerificationError


class M07ResultTests(unittest.TestCase):
    def test_exact_fourteen_mode_inventory(self):
        self.assertEqual(len(gate.MODES), 14)
        self.assertEqual(set(gate.MODE_PATCH.values()), {None, "P01", "P02", "P03", "P04", "P05"})
        self.assertEqual(gate.MODE_PATCH["T07-14-FeatureOff"], None)
        self.assertEqual(gate.MODE_PATCH["T07-13-P05-Rebuilt"], "P05")

    def test_exact_seven_bundle_inventory_and_assets(self):
        self.assertEqual(len(gate.BUNDLES), 7)
        self.assertEqual(tuple(sorted(gate.BUNDLES)), gate.BUNDLES)
        self.assertEqual(set(gate.ASSETS), set(gate.BUNDLES))
        self.assertEqual(len(gate.ASSETS["mixed-assets.bundle"]), 2)
        for variant in ("Baseline", "P05"):
            mapped = gate.expected_asset_map(variant)
            self.assertEqual(list(mapped), list(gate.BUNDLES))
            self.assertTrue(all(path.startswith("Assets/AssemblyShadowDemo/M07Resources/" + variant + "/")
                                for values in mapped.values() for path in values))

    def test_fixture_policy_is_finite_and_exact(self):
        self.assertEqual(gate.fixture_policy("P01"), (["ASSEMBLY_SHADOW_P01"], [gate.INTERNAL], True))
        self.assertEqual(gate.fixture_order("P02"), [gate.EXTENSIBILITY, gate.INTERNAL, gate.EXTENSIBILITY_CONSUMER])
        self.assertEqual(gate.fixture_order("P03"), list(gate.ORDER))
        self.assertEqual(gate.fixture_policy("P05"), (["ASSEMBLY_SHADOW_P05"], [gate.INTERNAL], False))
        for unknown in ("", "P06", "p01", None):
            with self.assertRaises(VerificationError): gate.fixture_policy(unknown)

    def test_rejected_structural_policies_are_exact(self):
        self.assertEqual(gate.rejected_policy("P05-DllOnly"), ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_P05"])
        self.assertEqual(gate.rejected_policy("P14-ClassRename"), ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M07_P14"])
        self.assertEqual(gate.rejected_policy("P15-SerializeReferenceRename"), ["ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M07_P15"])
        with self.assertRaises(VerificationError): gate.rejected_policy("LayoutMismatch")

    def test_result_and_receipt_schema_require_new_resource_fields(self):
        self.assertIn("resourceReceiptPath", gate.RESULT_FIELDS.split())
        self.assertIn("selectedResourceAbiHash", gate.RESULT_FIELDS.split())
        self.assertIn("businessResourceLoadStarted", gate.RESULT_FIELDS.split())
        self.assertIn("compilerDefines", gate.RESOURCE_FIELDS.split())
        self.assertIn("editorScriptingDefines", gate.RESOURCE_FIELDS.split())
        self.assertIn("serializeReferenceDependencies", gate.DEPENDENCY_FIELDS.split())
        self.assertEqual(gate.SERIALIZE_REFERENCE_DEP_FIELDS.split(),
                         ["consumer", "callSite", "concreteTypes", "evidence"])
        self.assertEqual(len(gate.REPLAY_FIXTURE_FIELDS.split()), 8)

    def test_monoscript_player_evidence_policy_is_finite(self):
        source = (Path(__file__).resolve().parents[3] / "Assets/AssemblyShadowDemo/Bootstrap/M07ResourceProbe.cs").read_text()
        verifier = (Path(__file__).resolve().parents[1] / "m07_results.py").read_text()
        self.assertIn('"monoscript-evidence-policy"', source)
        self.assertIn('"direct-or-plan-permitted-runtime-component-helper"', source)
        self.assertIn('"runtime-component-fallback-script-unavailable"', verifier)
        self.assertNotIn("carrier != null && carrier.Script != null", source)

    def test_exact_object_rejects_bool_integer_alias(self):
        with self.assertRaises(VerificationError): gate.exact({"value": False}, {"value": 0}, "typed")
        with self.assertRaises(VerificationError): gate.integer(False, "integer")
        self.assertEqual(gate.integer((1 << 64) - 1, "uint64", 0, (1 << 64) - 1), (1 << 64) - 1)

    def test_reference_names_are_case_normalized_without_aliases(self):
        self.assertEqual(gate.canonical_names(["AssemblyA.Contracts", "netstandard"], "references"),
                         ["assemblya.contracts", "netstandard"])
        with self.assertRaises(VerificationError):
            gate.canonical_names(["AssemblyA.Contracts", "assemblya.contracts"], "references")

    def test_json_duplicate_and_nonfinite_numbers_reject(self):
        for text in ('{"value":0,"value":1}', '{"value":NaN}', '{"value":Infinity}'):
            with self.subTest(text=text):
                with self.assertRaises(VerificationError): gate.json_text(text, "json")

    def test_user_defines_strip_only_proof_controls(self):
        values = [gate.raw_admissions.PREFIX + "a" * 64, "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + "b" * 64,
                  "ASSEMBLY_SHADOW_P05"]
        self.assertEqual(gate.user_defines(values, "defines"), ["ASSEMBLY_SHADOW_P05"])
        with self.assertRaises(VerificationError): gate.user_defines(values + ["ASSEMBLY_SHADOW_P05"], "duplicates")

    def test_marker_matrix_keeps_p02_on_baseline_logic(self):
        self.assertEqual(gate.marker_for(None), "M07-BASELINE")
        self.assertEqual(gate.marker_for("P02"), "M07-BASELINE")
        self.assertEqual(gate.marker_for("P03"), "M07-P03")
        self.assertEqual(gate.marker_for("P05"), "M07-P05")

    def test_counter_parsers_reject_shape_sign_and_aliases(self):
        self.assertEqual(gate.parse_counters("0|1|2", 3, "counts"), [0, 1, 2])
        for value in ("0|1", "00|1|2", "-1|1|2", "False|1|2"):
            with self.subTest(value=value):
                with self.assertRaises(VerificationError): gate.parse_counters(value, 3, "counts")
        counters, marker = gate.parse_scene_counters("|".join(["1"] * 12 + ["M07-P01-SCENE"]), "scene")
        self.assertEqual(len(counters), 12)
        self.assertEqual(marker, "M07-P01-SCENE")

    def test_assembly_mode_projection_rejects_wrong_active_domain(self):
        rows = []
        for name in gate.CANDIDATES:
            shadow = name == gate.INTERNAL
            rows.append(dict(name=name, code="Success", mode="InterpreterShadow" if shadow else "AotBaseline",
                             expectedShadow=shadow))
        gate.verify_assembly_modes(dict(assemblyModes=rows), "modes", [gate.INTERNAL], False)
        bad = copy.deepcopy(rows)
        bad[0]["mode"] = "InterpreterShadow"
        with self.assertRaises(VerificationError):
            gate.verify_assembly_modes(dict(assemblyModes=bad), "modes", [gate.INTERNAL], False)

    def test_transaction_gate_allows_only_monotonic_nonclosure_baseline_uses(self):
        use = {"name": gate.CONTRACTS}
        self.assertEqual(gate.verify_allowed_baseline_uses([use], [], [gate.INTERNAL], "uses"), [use])
        with self.assertRaises(VerificationError):
            gate.verify_allowed_baseline_uses([{"name": gate.INTERNAL}], [], [gate.INTERNAL], "uses")
        with self.assertRaises(VerificationError):
            gate.verify_allowed_baseline_uses([], [use], [gate.INTERNAL], "uses")

    def test_feature_off_type_rows_must_be_real_same_active_aot_types(self):
        phases = [
            ("data-asset", gate.INTERNAL), ("prefab-asset", gate.INTERNAL), ("prefab-first", gate.INTERNAL),
            ("unity-path-probe", gate.INTERNAL), ("prefab-cached-after-unload-false", gate.INTERNAL),
            ("prefab-reloaded-after-gc", gate.INTERNAL), ("serialize-reference-owner", gate.INTERNAL),
            ("serialize-reference-concrete", gate.INTERNAL), ("nested-internal", gate.INTERNAL),
            ("nested-external", gate.EXTENSIBILITY_CONSUMER), ("mixed-rename-guard", gate.INTERNAL),
            ("monoscript-get-class", gate.INTERNAL), ("mixed-reload-after-unload-true", gate.INTERNAL),
            ("scene-single", gate.INTERNAL), ("dont-destroy-component", gate.INTERNAL),
            ("scene-additive-delayed", gate.INTERNAL), ("scene-scene-reload", gate.INTERNAL),
        ]
        rows = [dict(phase=phase, typeName="AssemblyA.Implementation.Internal.VersionedPrefabComponent",
                     assemblyName=assembly, code="FeatureDisabled", executionMode="AotBaseline", rawJson="",
                     sameType=True, active=True) for phase, assembly in phases]
        gate.verify_type_resolutions(dict(typeResolutions=rows), "types", [], True)
        rows[0]["sameType"] = False
        with self.assertRaises(VerificationError):
            gate.verify_type_resolutions(dict(typeResolutions=rows), "types", [], True)

    def test_managed_native_on_off_projection_excludes_only_native_identity(self):
        linked = dict(schemaVersion=2, target="StandaloneOSX", architecture="arm64", sourceDirectory="/linked",
                      protectedAssemblies=[gate.BOOTSTRAP], assemblies=[])
        snapshot = dict(schemaVersion=1, kind="PlayerBuildInputs", unityVersion="2022.3.62f2", target="StandaloneOSX",
                        architecture="arm64", buildId="M07-Baseline-v1", playerBuildSucceeded=True,
                        playerBuildFilterCaptured=True, playerBuildOptions=129, normalHotUpdateAssemblies=[],
                        extraScriptingDefines=["PIN"], sourcePins={}, assemblies=[], references=[], filteredAssemblies=[],
                        filteredAssemblyCapabilities=[], linkerExcludedAssemblies=[], linkerExcludedAssemblyCapabilities=[],
                        linkedPlayerReceipt=linked, snapshotHash="a" * 64, buildGuid="on", playerOutput="/on",
                        nativeLibraryPath="/on/native", nativeLibrarySha256="b" * 64, linkedPlayerReceiptHash="c" * 64)
        off = copy.deepcopy(snapshot)
        off.update(snapshotHash="d" * 64, buildGuid="off", playerOutput="/off", nativeLibraryPath="/off/native",
                   nativeLibrarySha256="e" * 64, linkedPlayerReceiptHash="f" * 64)
        self.assertEqual(gate.managed_player_inputs(snapshot, "on"), gate.managed_player_inputs(off, "off"))
        off["extraScriptingDefines"] = ["CHANGED"]
        self.assertNotEqual(gate.managed_player_inputs(snapshot, "on"), gate.managed_player_inputs(off, "off"))

    def test_artifact_tree_rejects_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="m07-tree-") as directory:
            root = Path(directory).resolve()
            (root / "file").write_text("proof")
            self.assertEqual(set(gate.artifact_tree(root)), {"file"})
            (root / "link").symlink_to(root / "file")
            with self.assertRaises(VerificationError): gate.artifact_tree(root)

    def test_runtime_source_uses_bundle_identity_for_reloaded_scene_value(self):
        source = (Path(__file__).resolve().parents[3] / "Assets/AssemblyShadowDemo/Bootstrap/M07ResourceProbe.cs").read_text()
        self.assertIn('bundle == "additive-scene.bundle" ? "708" : "707"', source)
        self.assertNotIn('(additive ? "708" : "707")', source)

    def test_original_and_copied_resource_paths_are_byte_compared_not_equated(self):
        root = Path(__file__).resolve().parents[3]
        runtime = (root / "Assets/AssemblyShadowDemo/Bootstrap/M07Probe.cs").read_text()
        editor = (root / "Assets/AssemblyShadowDemo/Editor/M07EditorValidation.cs").read_text()
        launcher = (root / "Tools/AssemblyShadow/run-m07-players.py").read_text()
        self.assertIn("frozen and baseline-copied resource bundle bytes differ", runtime)
        self.assertIn("original and baseline-copied resource bytes differ", editor)
        self.assertIn('collect_tree(files, Path(replay["replayScratchPath"]))', launcher)
        self.assertIn("collect_tree(files, app)", launcher)
        self.assertNotIn("Path.GetFullPath(player.resourceBaselinePath) == baselineResourceRoot", runtime)


if __name__ == "__main__":
    unittest.main()
