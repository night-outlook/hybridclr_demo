import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from m01_results import BUSINESS_NAMES, NAME, TYPE, component, verify_negative_result, verify_player_evidence, verify_result
from shadow_tools import VerificationError


def object_info(shadow):
    return {"object": "0xf0", "class": "0xc0", "physicalAssembly": {"name": NAME, "assembly": "0xb0" if shadow else "0xa0",
            "isInterpreter": shadow, "matchesShadow": shadow}}


def component_info(shadow):
    marker = "PATCH-P01-INTERNAL" if shadow else "BASELINE-INTERNAL"
    return {"passed": True, "missingScript": False, "getComponentByName": True, "getComponentByNameFound": True,
            "byNameNativeObject": object_info(shadow), "getComponentByType": True,
            "dataReference": True, "serializedValue": 1234, "baseSerializedValue": 7,
            "result": "BASELINE-EXT|" + marker + "|1234", "nativeObject": object_info(shadow)}


class M01EvidenceTests(unittest.TestCase):
    def test_physical_baseline_and_shadow_probes(self):
        component(component_info(False), False)
        component(component_info(True), True, "0xb0")

    def test_matching_managed_name_does_not_override_baseline_header(self):
        probe = component_info(True)
        probe["nativeObject"] = object_info(False)
        with self.assertRaises(VerificationError): component(probe, True, "0xb0")

    def test_interpreter_flag_does_not_replace_physical_pointer_identity(self):
        probe = component_info(True)
        probe["nativeObject"]["physicalAssembly"]["assembly"] = "0xb1"
        with self.assertRaises(VerificationError): component(probe, True, "0xb0")

    def test_string_lookup_must_return_same_physical_component(self):
        probe = component_info(True)
        probe["byNameNativeObject"]["object"] = "0xf1"
        with self.assertRaises(VerificationError): component(probe, True, "0xb0")

    def test_changed_serialization_missing_scripts_and_wrong_body_fail(self):
        for field, value in (("serializedValue", 0), ("baseSerializedValue", 0), ("missingScript", True),
                             ("result", "BASELINE-EXT|BASELINE-INTERNAL|1234"), ("dataReference", False)):
            with self.subTest(field=field):
                probe = component_info(True)
                probe[field] = value
                with self.assertRaises(VerificationError): component(probe, True, "0xb0")

    def fixture(self, root):
        native = {"enabled": True, "active": True,
                  "baseline": {"name": NAME, "assembly": "0xa0", "isInterpreter": False},
                  "shadow": {"name": NAME, "assembly": "0xb0", "isInterpreter": True},
                  "events": [{"phase": phase, "type": TYPE, "site": "Object::New.input", "isInterpreter": True,
                              "assembly": "0xb0", "stack": [{"module": "GameAssembly.dylib", "moduleOffset": "0x123"}]}
                             for phase in ("prefab", "scene-first", "scene-reload")]}
        native_path = root / "native.json"
        native_path.write_text(json.dumps(native))
        result = {"milestone": "M01", "il2cpp": True, "mode": "P01", "result": "Passed", "gate": "CONDITIONAL-GO", "nativeFeatureEnabled": True,
                  "originalBundlesUnchanged": True, "nativeDiagnosticsPath": str(native_path),
                  "nativeDiagnosticsSha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
                  "baselineUsesBeforeActivate": [],
                  "reflection": {"passed": True, "typeAssemblyIdentity": True, "result": "PATCH-P01-INTERNAL",
                                 "moduleMvid": "", "moduleMvidSupported": False, "moduleMvidNote": "Unsupported IL2CPP API",
                                 "instance": object_info(True), "assembly": {"assembly": "0xb0"}},
                  "prefab": component_info(True),
                  "scene": {"passed": True, "derivedConsumerAot": True, "derivedConsumerResult": "BASELINE-EXT",
                            "firstLoad": component_info(True), "reload": component_info(True)},
                  "scriptableObject": {"passed": True, "serializedValue": 5678, "result": "BASELINE-DATA",
                                       "nativeObject": object_info(True)}}
        result_path = root / "result.json"
        result_path.write_text(json.dumps(result))
        return result_path, result, native_path, native

    def test_complete_native_evidence_passes(self):
        with tempfile.TemporaryDirectory(prefix="m01-evidence-") as folder:
            path, _, _, _ = self.fixture(Path(folder))
            verify_result(path, True)

    def test_runtime_mvid_must_not_be_fabricated(self):
        with tempfile.TemporaryDirectory(prefix="m01-evidence-") as folder:
            path, result, _, _ = self.fixture(Path(folder))
            result["reflection"]["moduleMvid"] = "00000000-0000-0000-0000-000000000000"
            path.write_text(json.dumps(result))
            with self.assertRaises(VerificationError): verify_result(path, True)

    def test_negative_resource_witness_preserves_actual_baseline_object(self):
        with tempfile.TemporaryDirectory(prefix="m01-negative-") as folder:
            path, result, native_path, native = self.fixture(Path(folder))
            native["moduleInitializerRun"] = False
            native_path.write_text(json.dumps(native))
            before = object_info(False)
            before["object"] = "0x77"
            result.update(mode="PreUsePrefab", result="Failed", baselineManifestSha256="baseline",
                          patchDllSha256="patch", nativeDiagnosticsSha256=hashlib.sha256(native_path.read_bytes()).hexdigest(),
                          baselineUsesBeforeActivate=[{"kind": "PreUsePrefab", "assemblyBefore": {"name": ""},
                              "objectBefore": before, "objectAfterActivate": copy.deepcopy(before),
                              "resultAfterActivate": "BASELINE-EXT|BASELINE-INTERNAL|1234"}])
            path.write_text(json.dumps(result))
            verify_negative_result(path, "baseline", "patch")
            result["baselineUsesBeforeActivate"][0]["objectAfterActivate"]["object"] = "0x88"
            path.write_text(json.dumps(result))
            with self.assertRaises(VerificationError): verify_negative_result(path, "baseline", "patch")

    def test_negative_harness_failure_is_not_successful_timing_evidence(self):
        with tempfile.TemporaryDirectory(prefix="m01-negative-") as folder:
            path, result, _, _ = self.fixture(Path(folder))
            result.update(mode="PreUseType", originalBundlesUnchanged=False,
                          baselineUsesBeforeActivate=[{"assemblyBefore": object_info(False)["physicalAssembly"]}])
            path.write_text(json.dumps(result))
            with self.assertRaises(VerificationError): verify_negative_result(path, "baseline", "patch")

    def test_build_input_receipt_checks_native_and_managed_bytes(self):
        with tempfile.TemporaryDirectory(prefix="m01-inputs-") as folder:
            root = Path(folder)
            manifest = {"unityVersion": "2022.3.62f2", "target": "StandaloneOSX", "architecture": "arm64", "assemblies": []}
            inputs = []
            for name in sorted(BUSINESS_NAMES):
                dll = root / (name + ".dll")
                dll.write_bytes(name.encode())
                sha = hashlib.sha256(dll.read_bytes()).hexdigest()
                mvid = "ae7099dc-4653-46c8-a6a7-d02f8d8a2224"
                manifest["assemblies"].append({"name": name, "path": dll.name, "sha256": sha, "mvid": mvid})
                inputs.append({"name": name, "path": str(dll), "sha256": sha, "mvid": mvid,
                               "baselineSha256": sha, "baselineMvid": mvid, "matchesBaselineMvid": True,
                               "matchesBaselineSemantics": True,
                               "comparisonPolicy": "same-types-fields-method-signatures-and-il"})
            manifest_path = root / "baseline-manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            native = root / "GameAssembly.dylib"
            native.write_bytes(b"native-build")
            evidence = {"schemaVersion": 1, "milestone": "M01", "unityVersion": manifest["unityVersion"],
                        "target": manifest["target"], "architecture": manifest["architecture"],
                        "baselineManifestSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                        "gameAssemblyPath": str(native), "gameAssemblySha256": hashlib.sha256(native.read_bytes()).hexdigest(),
                        "assemblies": inputs}
            receipt = root / "inputs.json"
            receipt.write_text(json.dumps(evidence))
            verify_player_evidence(receipt, root, manifest)
            evidence["assemblies"][0]["mvid"] = "678eaf66-1bbf-41a0-ac2b-5546446a9c15"
            receipt.write_text(json.dumps(evidence))
            with self.assertRaises(VerificationError): verify_player_evidence(receipt, root, manifest)
            evidence["assemblies"][0]["matchesBaselineMvid"] = False
            receipt.write_text(json.dumps(evidence))
            verify_player_evidence(receipt, root, manifest)
            evidence["assemblies"][0]["matchesBaselineSemantics"] = False
            receipt.write_text(json.dumps(evidence))
            with self.assertRaises(VerificationError): verify_player_evidence(receipt, root, manifest)
            evidence["assemblies"][0]["matchesBaselineSemantics"] = True
            evidence["assemblies"][0]["matchesBaselineMvid"] = True
            evidence["assemblies"][0]["mvid"] = manifest["assemblies"][0]["mvid"]
            receipt.write_text(json.dumps(evidence))
            native.write_bytes(b"different-native-build")
            with self.assertRaises(VerificationError): verify_player_evidence(receipt, root, manifest)

    def test_scene_reload_failure_cannot_be_hidden_by_summary(self):
        with tempfile.TemporaryDirectory(prefix="m01-evidence-") as folder:
            path, result, _, _ = self.fixture(Path(folder))
            result["scene"]["reload"]["nativeObject"] = object_info(False)
            path.write_text(json.dumps(result))
            with self.assertRaises(VerificationError): verify_result(path, True)

    def test_native_trace_hash_tampering_fails(self):
        with tempfile.TemporaryDirectory(prefix="m01-evidence-") as folder:
            path, _, native_path, native = self.fixture(Path(folder))
            native["active"] = False
            native_path.write_text(json.dumps(native))
            with self.assertRaises(VerificationError): verify_result(path, True)

    def test_missing_native_resource_creation_stack_fails(self):
        with tempfile.TemporaryDirectory(prefix="m01-evidence-") as folder:
            path, result, native_path, native = self.fixture(Path(folder))
            native["events"][2]["stack"] = []
            native_path.write_text(json.dumps(native))
            result["nativeDiagnosticsSha256"] = hashlib.sha256(native_path.read_bytes()).hexdigest()
            path.write_text(json.dumps(result))
            with self.assertRaises(VerificationError): verify_result(path, True)


if __name__ == "__main__":
    unittest.main()
