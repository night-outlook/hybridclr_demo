#!/usr/bin/env python3
"""Host-only source-input preparation tests; no actual Editor/Player invocation."""
import json
from pathlib import Path
import tempfile
import unittest

from prepare_initializer_sources import prepare, sha, MANAGED, ADDITIONS


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
        result = prepare(self.project, self.config, self.out)
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
        self.assertEqual(sha(blob), result["compositeOverlaySha256"])
        self.assertEqual(json.loads(self.config.read_text())["overlaySha256"], sha(blob))
        self.assertEqual(json.loads(self.manifest.read_text())["files"][-1]["path"],
                         "Assets/R03InitializerObservationPlayer.cs")
        self.assertEqual(json.loads((self.out / "SOURCE_PREPARATION.json").read_text()), result)

    def test_reuse_rejected(self):
        prepare(self.project, self.config, self.out)
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_config_manifest_mismatch_rejected_without_writes(self):
        self.manifest.write_text(self.manifest.read_text() + " ")
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)
        self.assertFalse(self.out.exists())

    def test_old_player_source_tamper_rejected(self):
        (self.project / "Assets/R03TerminalPlayer.cs").write_bytes(b"altered\n")
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_old_overlay_tamper_rejected(self):
        self.overlay.write_bytes(b"modified source")
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_missing_isolation_marker_rejected(self):
        (self.project / ".r03-isolated-project").unlink()
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_existing_target_rejected(self):
        (self.project / "Assets/R03InitializerObservationPlayer.cs").write_bytes(b"occupied")
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_duplicate_manifest_path_rejected(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["files"].append(manifest["files"][0])
        self.manifest.write_text(json.dumps(manifest))
        self._write_config()
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_existing_build_receipt_rejected(self):
        config = json.loads(self.config.read_text())
        receipt = Path(config["receiptPath"])
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text("already built")
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_disabled_feature_profile_rejected(self):
        config = json.loads(self.config.read_text())
        config["featureEnabled"] = False
        self.config.write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.out)

    def test_in_project_output_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.project, self.config, self.project / "generated")

    def test_explicit_no_unity_and_no_handoff(self):
        self.assertTrue(MANAGED.is_file())
        self.assertTrue(all(p.is_file() for p in ADDITIONS))
        receipt = prepare(self.project, self.config, self.out)
        self.assertIs(receipt["R03Accepted"], False)
        self.assertIs(receipt["H2Passed"], False)
        self.assertIs(receipt["playerExecuted"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
