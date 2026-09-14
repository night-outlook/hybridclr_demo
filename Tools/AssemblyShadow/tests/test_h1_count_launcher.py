import importlib.util
import json
import os
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "run-h1-count-players.py"


def load_launcher():
    spec = importlib.util.spec_from_file_location("h1_count_player_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load H1 count launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class H1CountPlayerLauncherTests(unittest.TestCase):
    def test_result_identity_requires_current_schema_two(self):
        launcher = load_launcher()
        result_path = Path("/tmp/h1-result.json")
        fixture = Path("/tmp/h1-fixture.dll")
        fixture_hash = "a" * 64
        build = {"buildGuid": "build", "featureEnabled": True, "cppConfiguration": "Debug"}
        case = {"caseId": "H1R-P01-a", "count": 0, "expected": "Accepted"}
        result = {"schemaVersion": 2, "kind": "H1CountDiagnosticResult", "result": "Passed",
                  "resultPath": str(result_path), "processId": 123, "buildGuid": "build",
                  "family": "parameters", "path": "ordinary", "caseId": "H1R-P01-a",
                  "expectedCount": 0, "fixturePath": str(fixture),
                  "inputHashBefore": fixture_hash, "inputHashAfter": fixture_hash,
                  "fixtureSha256Expected": fixture_hash, "expectedOutcome": "Accepted",
                  "expectedFeatureEnabled": True, "expectedCppConfiguration": "Debug",
                  "operationSucceeded": True}
        self.assertTrue(launcher.validate_result(result, result_path, 123, build, "parameters",
                                                "ordinary", case, fixture, fixture_hash)["passed"])
        result["schemaVersion"] = 1
        self.assertFalse(launcher.validate_result(result, result_path, 123, build, "parameters",
                                                 "ordinary", case, fixture, fixture_hash)["passed"])

    def test_immutable_native_snapshot_survives_live_drift_but_rejects_snapshot_drift(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder).resolve()
            root = project / "_temp/AssemblyShadow/snapshot"
            installed, external = root / "installedlibil2cpp", root / "external"
            def put(path, value):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
                return str(path)
            pin = put(root / "source-pins.json", "{}")
            verifier = put(root / "tools/verify-installed-runtime.py", "verify")
            support = put(root / "tools/shadow_tools.py", "support")
            python = put(project / "python", "python executable bytes")
            for name in ("AssemblyManifest.cpp", "MethodBridge.cpp", "UnityVersion.h", "libil2cpp-version.txt"):
                put(installed / "hybridclr/generated" / name, name)
            generated_paths = ["hybridclr/generated/" + name for name in
                               ("AssemblyManifest.cpp", "MethodBridge.cpp", "UnityVersion.h", "libil2cpp-version.txt")]
            receipt = {"sourceFileHashes": [{"path": path, "source": "hybridclr", "sha256": "a" * 64}
                                             for path in generated_paths[:3]],
                       "generatedFileExclusions": generated_paths}
            receipt_path = put(installed / "assembly-shadow-install.json", json.dumps(receipt))
            put(external / "header.h", "external")
            native_entries, _ = launcher._native_inventory(installed, "native", receipt)
            external_entries, _ = launcher._native_inventory(external, "external")
            snapshot_entries = sorted([{"path": f.relative_to(root).as_posix(), "source": "snapshot",
                                       "sha256": launcher.digest(f)} for f in launcher.collect_tree(root, "snapshot")],
                                      key=lambda item: item["path"])
            provenance = {"schemaVersion": 2, "snapshotRoot": str(root),
                          "snapshotFiles": snapshot_entries,
                          "snapshotInventorySha256": launcher._inventory_hash(snapshot_entries),
                          "installedRoot": str(installed), "externalRoot": str(external),
                          "installedFiles": native_entries, "externalFiles": external_entries,
                          "installedInventorySha256": launcher._inventory_hash(native_entries),
                          "externalInventorySha256": launcher._inventory_hash(external_entries),
                          "verificationExitCode": 0, "liveSourcePinFile": str(project / "live-pin.json")}
            for field, path in (("sourcePinFile", pin), ("verificationToolPath", verifier),
                                ("verificationSupportToolPath", support), ("installReceiptPath", receipt_path),
                                ("pythonExecutable", python)):
                provenance[field] = path
                hash_field = {"sourcePinFile": "sourcePinSha256", "verificationToolPath": "verificationToolSha256",
                              "verificationSupportToolPath": "verificationSupportToolSha256",
                              "installReceiptPath": "installReceiptSha256", "pythonExecutable": "pythonExecutableSha256"}[field]
                provenance[hash_field] = launcher.digest(Path(path))
            build = {"sourcePinFile": pin, "sourcePinSha256": provenance["sourcePinSha256"]}
            put(project / "live-pin.json", "later build")
            launcher.validate_native_provenance(provenance, build, project)
            put(external / "header.h", "changed snapshot")
            with self.assertRaisesRegex(ValueError, "snapshot inventory differs"):
                launcher.validate_native_provenance(provenance, build, project)

    def test_json_read_is_bounded_before_rejecting_oversize(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "large.json"
            path.write_bytes(b"x" * 65)
            with mock.patch.object(launcher, "MAX_PLAYER_BYTES", 64):
                with self.assertRaisesRegex(ValueError, "oversized"):
                    launcher.read_json_captured(path, "bounded JSON")

    def test_overlapping_binary_observation_cannot_replace_build_hash(self):
        launcher = load_launcher()
        expected = {"/fixture/Player.app/Contents/MacOS/Player": "a" * 64}
        with self.assertRaisesRegex(ValueError, "validated input hash conflict"):
            launcher.bind_expected_hash(expected,
                "/fixture/Player.app/Contents/MacOS/Player", "b" * 64)
        self.assertEqual(expected["/fixture/Player.app/Contents/MacOS/Player"], "a" * 64)
        launcher.bind_expected_hash(expected,
            "/fixture/Player.app/Contents/MacOS/Player", "a" * 64)


    def test_mode_policy_requires_shadow_feature_on(self):
        launcher = load_launcher()
        self.assertEqual("OrdinaryOff", launcher.mode_for("parameters", "ordinary", False))
        self.assertEqual("OrdinaryOn", launcher.mode_for("nested", "ordinary", True))
        self.assertEqual("ShadowOn", launcher.mode_for("nested", "shadow", True))
        with self.assertRaises(ValueError):
            launcher.mode_for("nested", "shadow", False)

    def test_command_binds_registered_probe_flags_and_exact_fixture(self):
        launcher = load_launcher()
        for family, path in (("parameters", "ordinary"), ("nested", "shadow")):
            command = launcher.build_player_command(
                Path("/tmp/H1Count.app/Contents/MacOS/H1Count"), family, path,
                "H1R-N03-interleaved", Path("/tmp/H1R-N03-interleaved.dll"),
                "a" * 64, Path("/tmp/result.json"), Path("/tmp/player.log"),
                witness_path=Path("/tmp/ordinary-witness.dll.bytes"))
            self.assertEqual(family, command[command.index("-shadowH1Family") + 1])
            self.assertEqual(path, command[command.index("-shadowH1Path") + 1])
            self.assertEqual("/tmp/H1R-N03-interleaved.dll",
                             command[command.index("-shadowH1Fixture") + 1])
            self.assertEqual("a" * 64,
                             command[command.index("-shadowH1FixtureSha256") + 1])
            self.assertEqual("/tmp/result.json",
                             command[command.index("-shadowH1Result") + 1])
            self.assertEqual("/tmp/ordinary-witness.dll.bytes",
                             command[command.index("-shadowH1Witness") + 1])
            self.assertEqual("-logFile", command[-2])
            self.assertEqual("/tmp/player.log", command[-1])

    def test_audit_kinds_are_family_specific(self):
        launcher = load_launcher()
        self.assertEqual("H1CountFixtureShapeAudit", launcher.AUDIT_KINDS["parameters"])
        self.assertEqual("H1NestedFixtureShapeAudit", launcher.AUDIT_KINDS["nested"])

    def test_symlink_observation_is_rejected_without_raising(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "input.txt"
            target.write_text("fixture", encoding="utf-8")
            link = root / "link.txt"
            os.symlink(target, link)
            value, error = launcher.safe_digest(link)
            self.assertEqual("", value)
            self.assertIn("existing canonical file", error)

    def test_added_tree_file_is_detected(self):
        launcher = load_launcher()
        root = Path("/tmp/assembly-shadow-root")
        before = {root / "existing"}
        after = {root / "existing", root / "added"}
        unchanged, errors = launcher.compare_observations(
            {str(root / "existing"): "a"},
            {str(root / "existing"): "a", str(root / "added"): "b"},
            {"playerOutput": before}, {"playerOutput": after})
        self.assertFalse(unchanged)
        self.assertTrue(any("added" in error for error in errors))

    def test_normal_failure_is_distinct_from_signal_termination(self):
        launcher = load_launcher()
        normal = launcher.classify_exit(1)
        signal = launcher.classify_exit(-9)
        self.assertTrue(normal["processFailed"])
        self.assertFalse(normal["signalTerminated"])
        self.assertFalse(normal["crashed"])
        self.assertTrue(signal["processFailed"])
        self.assertTrue(signal["signalTerminated"])
        self.assertTrue(signal["crashed"])
        owned = launcher.classify_exit(-15, launcher_initiated_termination=True)
        self.assertTrue(owned["signalTerminated"])
        self.assertTrue(owned["launcherInitiatedTermination"])
        self.assertFalse(owned["crashed"])

    def test_replacement_during_build_validation_is_refused_before_popen(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / "Assets/AssemblyShadowDemo").mkdir(parents=True)
            output_parent = root / "_temp/AssemblyShadow"
            output_parent.mkdir(parents=True)
            output = output_parent / "run"
            fixture = root / "fixture.dll"
            fixture.write_bytes(b"original")
            manifest_path = root / "manifest.json"
            audit_path = root / "audit.json"
            build_path = root / "build.json"
            for path in (manifest_path, audit_path, build_path):
                path.write_text("{}", encoding="utf-8")

            def fake_manifest(*args):
                expected = launcher.digest(fixture)
                args[-1][str(fixture)] = expected
                return {}, {"caseId": "case", "count": 0, "expected": "Accepted"}, {"sourceBinding": {}}, fixture

            def fake_build(*args):
                fixture.write_bytes(b"replacement")
                return {"featureEnabled": False, "cppConfiguration": "Debug"}, set(), {}

            argv = [
                "--project-root", str(root), "--build-receipt", str(build_path),
                "--fixture-manifest", str(manifest_path), "--fixture-audit", str(audit_path),
                "--family", "parameters", "--path", "ordinary", "--case", "case",
                "--output-root", str(output),
            ]
            with mock.patch.object(launcher, "validate_manifest_and_audit", side_effect=fake_manifest), \
                    mock.patch.object(launcher, "validate_build_receipt", side_effect=fake_build), \
                    mock.patch.object(launcher.subprocess, "Popen", side_effect=AssertionError("must not launch")) as popen:
                self.assertEqual(1, launcher.main(argv))
            popen.assert_not_called()
            receipt = launcher.read_json(output / "h1-count-player-launch.json", "launch receipt")
            self.assertIn("validated input changed before launch", receipt["error"])

    def test_wrong_native_app_path_is_rejected(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            app = root / "H1.app"
            executable = app / "Contents/MacOS/H1"
            library = app / "Contents/Frameworks/libil2cpp.dylib"
            metadata = app / "Contents/Resources/Data/global-metadata.dat"
            for path in (executable, library, metadata):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x")
            (app / "Contents/Info.plist").write_bytes(plistlib.dumps({"CFBundleExecutable": "H1"}))
            launcher.validate_player_layout(app, executable, library, metadata)
            with self.assertRaises(ValueError):
                launcher.validate_player_layout(app, executable, root / "outside.dylib", metadata)

    def test_wrong_native_provenance_is_rejected_before_launch(self):
        launcher = load_launcher()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source_pin = root / "pins.json"
            source_pin.write_text("{}", encoding="utf-8")
            provenance = {"sourcePinFile": str(source_pin)}
            build = {"sourcePinFile": str(root / "other-pins.json"),
                     "sourcePinSha256": "0" * 64}
            with self.assertRaises(ValueError):
                launcher.validate_native_provenance(provenance, build, root)


if __name__ == "__main__":
    unittest.main()
