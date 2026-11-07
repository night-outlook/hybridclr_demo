#!/usr/bin/env python3
"""Host-only source-input preparation tests; no actual Editor/Player invocation."""
import json
from pathlib import Path
import tempfile
import unittest

from prepare_initializer_sources import prepare, sha, MANAGED, ADDITIONS, BRIDGE, ABI_CONTRACT


class InitializerSourcePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-init-source-")
        root = Path(self.temp.name)
        self.project = root / "isolated"
        (self.project / "Assets").mkdir(parents=True)
        (self.project / ".r03-isolated-project").write_text("fresh\n")
        existing = []
        for name in ("R03TerminalPlayer.cs", "R03EngineFrameDispatcher.cs"):
            data = ("// " + name + "\n").encode()
            (self.project / "Assets" / name).write_bytes(data)
            existing.append({"path": "Assets/" + name, "sha256": sha(data)})
        self.manifest = self.project / "source-inputs.json"
        self.manifest.write_text(json.dumps({"schemaVersion":1, "files": existing}) + "\n")
        self.overlay = root / "AssemblyShadowR03Probe.cpp"
        self.overlay.write_bytes(b"// old V1 native input\n")
        self.config = root / "config.json"
        self._write_config()
        self.out = root / "new-source"
        self.controls = root / "pinned-native-fixtures"
        self.controls.mkdir()
        self.targets = {
            "initializer-control": self.controls / "control-Methods.dll",
            "initializer-failure": self.controls / "failure-Methods.dll",
        }
        for mode, target in self.targets.items():
            target.write_bytes(("TEST HOST FIXTURE ONLY:" + mode).encode())
        self.expected = {mode:(sha(target.read_bytes()), "host-fake-mvid-" + mode)
                         for mode,target in self.targets.items()}

    def prepare(self):
        return prepare(self.project, self.config, self.out, self.targets,
                       expected_targets=self.expected)

    def tearDown(self):
        self.temp.cleanup()

    def _write_config(self):
        self.config.write_text(json.dumps({
            "schemaVersion":1, "projectPath":str(self.project),
            "sourceManifestSha256":sha(self.manifest.read_bytes()),
            "overlayPath":str(self.overlay),
            "overlaySha256":sha(self.overlay.read_bytes()),
            "outputPath":str(self.project.parent / "build" / "R03Isolated.app"),
            "receiptPath":str(self.project.parent / "build" / "build-receipt.json"),
            "featureEnabled":True, "diagnosticsLevel":2,
            "cppConfiguration":"Release"}) + "\n")

    def test_preserves_original_and_appends_exact_new_sources(self):
        previous = self.overlay.read_bytes()
        result = self.prepare()
        self.assertEqual(result["result"], "PreparedSourcesOnly_NoUnityOrPlayer")
        self.assertFalse(result["unityBuildExecuted"])
        self.assertFalse(result["runtimeAcceptance"])
        self.assertEqual(self.overlay.read_bytes(), previous)
        self.assertEqual((self.project / "Assets/R03InitializerObservationPlayer.cs").read_bytes(),
                         MANAGED.read_bytes())
        blob = (self.out / "R03InitializerCompositeOverlay.cpp").read_bytes()
        self.assertTrue(blob.startswith(previous))
        self.assertIn(ADDITIONS[0].read_bytes(), blob)
        self.assertIn(ADDITIONS[1].read_bytes(), blob)
        self.assertEqual((self.project / "Assets/Editor/R03InitializerBridge.cs").read_bytes(),
                         BRIDGE.read_bytes())
        self.assertEqual(sha(blob), result["compositeOverlaySha256"])
        self.assertEqual(json.loads(self.config.read_text())["overlaySha256"], sha(blob))
        cfg = json.loads(self.config.read_text())
        self.assertEqual(cfg["initializerBridgeContract"], ABI_CONTRACT)
        self.assertEqual(cfg["initializerBridgeControlSha256"], self.expected["initializer-control"][0])
        self.assertEqual(cfg["initializerBridgeFailureSha256"], self.expected["initializer-failure"][0])
        self.assertEqual(json.loads(self.manifest.read_text())["files"][-1]["path"],
                         "Assets/R03InitializerObservationPlayer.cs")
        self.assertEqual(json.loads((self.out / "SOURCE_PREPARATION.json").read_text()), result)

    def test_reuse_rejected(self):
        self.prepare()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_config_manifest_mismatch_rejected_without_writes(self):
        self.manifest.write_text(self.manifest.read_text() + " ")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.out.exists())

    def test_old_player_source_tamper_rejected(self):
        (self.project / "Assets/R03TerminalPlayer.cs").write_bytes(b"altered\n")
        with self.assertRaises(ValueError):
            self.prepare()

    def test_old_overlay_tamper_rejected(self):
        self.overlay.write_bytes(b"modified source")
        with self.assertRaises(ValueError):
            self.prepare()

    def test_missing_isolation_marker_rejected(self):
        (self.project / ".r03-isolated-project").unlink()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_existing_target_rejected(self):
        (self.project / "Assets/R03InitializerObservationPlayer.cs").write_bytes(b"occupied")
        with self.assertRaises(ValueError):
            self.prepare()

    def test_duplicate_manifest_path_rejected(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["files"].append(manifest["files"][0])
        self.manifest.write_text(json.dumps(manifest))
        self._write_config()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_existing_build_receipt_rejected(self):
        config = json.loads(self.config.read_text())
        receipt = Path(config["receiptPath"])
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text("already built")
        with self.assertRaises(ValueError):
            self.prepare()

    def test_disabled_feature_profile_rejected(self):
        config = json.loads(self.config.read_text())
        config["featureEnabled"] = False
        self.config.write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_in_project_output_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.project / "generated", self.targets,
                    expected_targets=self.expected)

    def test_bridge_target_hash_tamper_rejected_before_project_writes(self):
        self.targets["initializer-control"].write_bytes(b"CHANGED")
        with self.assertRaisesRegex(ValueError, "Pinned actual native fixture"):
            self.prepare()
        self.assertFalse(self.out.exists())
        self.assertFalse((self.project / "Assets/Editor/R03InitializerBridge.cs").exists())

    def test_missing_or_symlinked_bridge_target_rejected(self):
        expected = self.targets["initializer-failure"]
        saved = expected.read_bytes()
        expected.unlink()
        with self.assertRaises(ValueError):
            self.prepare()
        expected.write_bytes(saved)
        alias = self.controls / "alternate.dll"
        alias.write_bytes(saved)
        expected.unlink()
        expected.symlink_to(alias)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.out.exists())

    def test_duplicate_bridge_target_identity_fails(self):
        with self.assertRaisesRegex(ValueError, "Distinct control and failure"):
            prepare(self.project, self.config, self.out,
                    {"initializer-control": self.targets["initializer-control"],
                     "initializer-failure": self.targets["initializer-control"]},
                    expected_targets={
                        "initializer-control": self.expected["initializer-control"],
                        "initializer-failure": self.expected["initializer-control"]})
        self.assertFalse(self.out.exists())

    def test_existing_bridge_source_cannot_be_overwritten(self):
        dest = self.project / "Assets/Editor/R03InitializerBridge.cs"
        dest.parent.mkdir(parents=True)
        dest.write_text("do not overwrite")
        with self.assertRaisesRegex(ValueError, "No previous initializer source"):
            self.prepare()
        self.assertEqual(dest.read_text(), "do not overwrite")

    def test_explicit_no_unity_and_no_handoff(self):
        self.assertTrue(MANAGED.is_file())
        self.assertTrue(all(p.is_file() for p in ADDITIONS))
        receipt = self.prepare()
        self.assertIs(receipt["R03Accepted"], False)
        self.assertIs(receipt["H2Passed"], False)
        self.assertIs(receipt["playerExecuted"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
