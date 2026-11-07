#!/usr/bin/env python3
"""Source-only isolated project mutation regressions, never Unity/IL2CPP."""
import json
from pathlib import Path
import tempfile
import unittest

from prepare_captured_generic_sources import extend, NATIVE, MANAGED, ABICONTRACT
from prepare_initializer_sources import sha


class CapturedSourcePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r03-captured-preparer-")
        root = Path(self.temp.name).resolve(strict=True)
        self.project = root / "project"
        self.asset = self.project / "Assets"
        self.asset.mkdir(parents=True)
        (self.project / ".r03-isolated-project").write_text("fresh\n")
        files = []
        names = (
            "Assets/R03TerminalPlayer.cs", "Assets/R03EngineFrameDispatcher.cs",
            "Assets/R03InitializerObservationPlayer.cs",
            "Assets/Editor/R03InitializerBridge.cs",
        )
        for name in names:
            data = ("// HOST ONLY: " + name + "\n").encode()
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            files.append({"path":name,"sha256":sha(data)})
        self.manifest=self.project / "source-inputs.json"
        self.manifest.write_text(json.dumps({"schemaVersion":1,"files":files})+"\n")
        parent = root / "initializer-source"
        parent.mkdir()
        self.overlay = parent / "R03InitializerCompositeOverlay.cpp"
        self.overlay.write_bytes(b"// ORIGINAL COMPOSITE ONLY\n")
        (parent / "SOURCE_PREPARATION.json").write_text(json.dumps({
            "result":"PreparedSourcesOnly_NoUnityOrPlayer",
            "compositeOverlaySha256":sha(self.overlay.read_bytes()),
            "initializerBridgeSignature":"Bi4",
            "runtimeAcceptance":False,
        })+"\n")
        self.config = root / "config.json"
        self._config()
        self.out=root / "captured-source"

    def tearDown(self):
        self.temp.cleanup()

    def _config(self):
        self.config.write_text(json.dumps({
            "schemaVersion":1, "projectPath":str(self.project),
            "overlayPath":str(self.overlay),"overlaySha256":sha(self.overlay.read_bytes()),
            "sourceManifestSha256":sha(self.manifest.read_bytes()),
            "outputPath":str(self.project.parent/"build/R03Isolated.app"),
            "receiptPath":str(self.project.parent/"build/build-receipt.json"),
            "featureEnabled":True, "diagnosticsLevel":2, "cppConfiguration":"Release",
        })+"\n")

    def extend(self):
        return extend(self.project, self.config, self.out)

    def test_01_real_primary_native_and_aot_sources_are_appended(self):
        old=self.overlay.read_bytes()
        report=self.extend()
        self.assertTrue(self.overlay.read_bytes().startswith(old))
        self.assertEqual(report["initializerCompositeBeforeSha256"],sha(old))
        self.assertEqual(report["genericNativePartSha256"],sha(NATIVE.read_bytes()))
        self.assertEqual(report["combinedOverlayAfterSha256"],sha(self.overlay.read_bytes()))
        self.assertIn(NATIVE.read_bytes(),self.overlay.read_bytes())
        self.assertEqual(json.loads(self.config.read_text())["overlaySha256"],
                         report["combinedOverlayAfterSha256"])
        self.assertEqual(json.loads(self.config.read_text())["capturedGenericPhysicalContract"],
                         ABICONTRACT)
        manifests=json.loads(self.manifest.read_text())["files"]
        self.assertEqual(len(manifests),6)
        self.assertEqual(set(x["path"] for x in manifests[-2:]),set(MANAGED))
        for name,source in MANAGED.items():
            self.assertEqual((self.project/name).read_bytes(),source.read_bytes())
            self.assertEqual(report["managedSourceSha256"][name],sha(source.read_bytes()))
        self.assertFalse(report["unityBuildExecuted"])
        self.assertFalse(report["playerExecuted"])
        self.assertFalse(report["R03Accepted"])
        self.assertEqual(json.loads((self.out/"SOURCE_PREPARATION.json").read_text()),
                         report)

    def test_02_reuse_and_duplicate_src_rejected(self):
        self.extend()
        before=self.overlay.read_bytes()
        with self.assertRaises(ValueError):self.extend()
        self.assertEqual(self.overlay.read_bytes(),before)

    def test_03_wrong_current_manifest_sha_rejected(self):
        self.manifest.write_text(self.manifest.read_text()+"!")
        with self.assertRaises(ValueError):self.extend()
        self.assertFalse(self.out.exists())

    def test_04_original_player_tamper_rejected(self):
        (self.project/"Assets/R03InitializerObservationPlayer.cs").write_bytes(b"tamper")
        with self.assertRaises(ValueError):self.extend()

    def test_05_original_composite_overlay_tamper_rejected(self):
        self.overlay.write_bytes(b"changed")
        with self.assertRaises(ValueError):self.extend()

    def test_06_missing_initializer_source_proof_rejected(self):
        (self.overlay.parent/"SOURCE_PREPARATION.json").unlink()
        with self.assertRaises(ValueError):self.extend()
        self.assertFalse(self.out.exists())

    def test_07_broken_existing_Bi4_proof_rejected(self):
        p=self.overlay.parent/"SOURCE_PREPARATION.json"
        row=json.loads(p.read_text())
        row["initializerBridgeSignature"]="Fake"
        p.write_text(json.dumps(row))
        with self.assertRaises(ValueError):self.extend()

    def test_08_disallowed_profile_rejected(self):
        row=json.loads(self.config.read_text())
        row["featureEnabled"]=False
        self.config.write_text(json.dumps(row))
        with self.assertRaises(ValueError):self.extend()

    def test_09_preexisting_output_and_existing_build_rejected(self):
        self.out.mkdir()
        with self.assertRaises(ValueError):self.extend()
        self.out.rmdir()
        receipt=Path(json.loads(self.config.read_text())["receiptPath"])
        receipt.parent.mkdir(parents=True)
        receipt.write_text("consumed")
        with self.assertRaises(ValueError):self.extend()

    def test_10_duplicate_manifest_entry_rejected(self):
        row=json.loads(self.manifest.read_text())
        row["files"].append(row["files"][0])
        self.manifest.write_text(json.dumps(row))
        self._config()
        with self.assertRaises(ValueError):self.extend()

    def test_11_existing_captured_aot_source_not_overwritten(self):
        path=self.project/"Assets/R03CapturedGenericAotOwner.cs"
        path.write_text("original")
        with self.assertRaises(ValueError):self.extend()
        self.assertEqual(path.read_text(),"original")

    def test_12_missing_isolation_marker_rejected(self):
        (self.project/".r03-isolated-project").unlink()
        with self.assertRaises(ValueError):self.extend()

    def test_13_external_dest_and_symlink_rejected(self):
        with self.assertRaises(ValueError):
            extend(self.project,self.config,self.project/"in-project")
        outside=self.project.parent/"aliased-overlay"
        self.overlay.rename(outside)
        self.overlay.symlink_to(outside)
        self._config()
        with self.assertRaises(ValueError):self.extend()

    def test_14_wrong_initializer_source_hash_not_corrected(self):
        p=self.overlay.parent/"SOURCE_PREPARATION.json"
        row=json.loads(p.read_text())
        row["compositeOverlaySha256"]="a"*64
        p.write_text(json.dumps(row))
        with self.assertRaises(ValueError):self.extend()


if __name__=="__main__":
    unittest.main(verbosity=2)
