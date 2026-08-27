import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shadow_tools as tools


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="assembly-shadow-tests-")
        self.root = Path(self.temporary.name).resolve() / "workspace with spaces"
        self.root.mkdir()
        self.repos = {name: self.root / name for name in tools.REPOSITORIES}
        for root in self.repos.values():
            root.mkdir()
            self.git(root, "init", "-q")
            self.git(root, "config", "user.name", "Assembly Shadow Tests")
            self.git(root, "config", "user.email", "tests@example.invalid")
            self.git(root, "config", "core.autocrlf", "false")
        self.project = self.repos["demo"]
        self.native = {
            "libil2cpp/AssemblyShadowConfig.h": "#ifndef HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\n#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 0\n#endif\n",
            "libil2cpp/il2cpp-config.h": '#include "AssemblyShadowConfig.h"\n',
            "libil2cpp/vm/Sample.cpp": "// pinned native source\n",
        }
        self.runtime = {"hybridclr/RuntimeApi.cpp": "// pinned interpreter\n"}
        for name in ("AssemblyManifest.cpp", "MethodBridge.cpp", "UnityVersion.h"):
            self.runtime["hybridclr/generated/" + name] = "// generated source baseline\n"
        for name, files in (("il2cppPlus", self.native), ("hybridclr", self.runtime)):
            for path, content in files.items():
                self.write(self.repos[name] / path, content)
        self.write_json(self.repos["hybridclrUnity"] / "package.json", {"name": tools.PACKAGE, "version": "8.14.1"})
        self.write(self.project / ".gitignore", "_temp/\nLibrary/\nignored.cs\n")
        self.write(self.project / "Assets/Source.cs", "// source input\n")
        self.write(self.project / "ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 2022.3.62f2\n")
        self.write(self.project / "ProjectSettings/ProjectSettings.asset", "  additionalIl2CppArgs: --compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0\"\n")
        self.write_json(self.project / "Packages/manifest.json", {"dependencies": {tools.PACKAGE: "file:../../hybridclrUnity"}})
        for root in self.repos.values():
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "fixture source")
        self.pins = {"schemaVersion": 1, "unityVersion": "2022.3.62f2", "target": "StandaloneOSX"}
        for name, root in self.repos.items():
            self.pins[name] = {"url": "https://example.invalid/" + name,
                               "revision": self.git(root, "rev-parse", "HEAD").strip(),
                               "localPath": "." if name == "demo" else "../" + name}
        self.write_json(self.project / tools.PINS, self.pins)
        self.installed = self.root / "installed runtime" / "libil2cpp"
        hashes = []
        for name, files in (("il2cppPlus", self.native), ("hybridclr", self.runtime)):
            for path, content in files.items():
                installed_path = path.removeprefix("libil2cpp/") if name == "il2cppPlus" else path
                self.write(self.installed / installed_path, content)
                hashes.append({"source": name, "path": installed_path,
                               "sha256": hashlib.sha256(content.encode()).hexdigest()})
        self.write(self.installed / "hybridclr/generated/libil2cpp-version.txt", "8.14.1")
        self.receipt = {"schemaVersion": 1, "installMode": "PinnedLocal", "unityVersion": "2022.3.62f2",
                        "target": "StandaloneOSX", "packageVersion": "8.14.1",
                        "packageRevision": self.pins["hybridclrUnity"]["revision"],
                        "repositories": {name: self.pins[name] for name in tools.REPOSITORIES},
                        "sourceFileHashes": hashes, "generatedFileExclusions": sorted(tools.GENERATED),
                        "defaultShadowMacro": 0, "defaultShadowMacroSource": "AssemblyShadowConfig.h"}
        self.save_receipt()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def git(root, *args):
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode()

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, path, data):
        self.write(path, json.dumps(data))

    def save_receipt(self):
        self.write_json(self.installed / tools.RECEIPT, self.receipt)

    def verify(self):
        return tools.verify(self.project, self.installed)

    def test_clean_pairing_and_complete_inventory_pass(self):
        result = self.verify()
        self.assertTrue(result["demoSourceVerified"])
        self.assertEqual(result["sourceFiles"], len(self.native) + len(self.runtime))

    def test_installed_byte_tamper_fails(self):
        self.write(self.installed / "vm/Sample.cpp", "tampered")
        with self.assertRaisesRegex(tools.VerificationError, "Installed byte mismatch"):
            self.verify()

    def test_forged_receipt_does_not_authorize_tamper(self):
        self.write(self.installed / "vm/Sample.cpp", "tampered")
        for entry in self.receipt["sourceFileHashes"]:
            if entry["path"] == "vm/Sample.cpp":
                entry["sha256"] = hashlib.sha256(b"tampered").hexdigest()
        self.save_receipt()
        with self.assertRaisesRegex(tools.VerificationError, "exact pinned Git"):
            self.verify()

    def test_incomplete_receipt_fails(self):
        self.receipt["sourceFileHashes"].pop()
        self.save_receipt()
        with self.assertRaises(tools.VerificationError):
            self.verify()

    def test_extra_installed_source_fails(self):
        self.write(self.installed / "vm/Unexpected.cpp", "injected")
        with self.assertRaisesRegex(tools.VerificationError, "Installed inventory differs"):
            self.verify()

    def test_missing_generated_file_fails(self):
        (self.installed / "hybridclr/generated/UnityVersion.h").unlink()
        with self.assertRaises(tools.VerificationError):
            self.verify()

    def test_only_named_generated_files_may_change(self):
        self.write(self.installed / "hybridclr/generated/MethodBridge.cpp", "// regenerated\n")
        self.assertTrue(self.verify()["demoSourceVerified"])
        self.receipt["generatedFileExclusions"].append("vm/Sample.cpp")
        self.save_receipt()
        with self.assertRaisesRegex(tools.VerificationError, "four-file allowlist"):
            self.verify()

    def test_mismatched_target_and_unity_fail(self):
        for key in ("target", "unityVersion"):
            original = self.receipt[key]
            self.receipt[key] = "wrong"
            self.save_receipt()
            with self.assertRaises(tools.VerificationError):
                self.verify()
            self.receipt[key] = original

    def test_source_pin_mismatch_fails(self):
        self.receipt["packageRevision"] = "0" * 40
        self.save_receipt()
        with self.assertRaisesRegex(tools.VerificationError, "Package revision"):
            self.verify()

    def test_native_override_is_not_confused_with_header_default(self):
        self.write(self.project / "ProjectSettings/ProjectSettings.asset", "  additionalIl2CppArgs: --compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\"\n")
        with self.assertRaisesRegex(tools.VerificationError, "configuration is on"):
            tools.verify(self.project, self.installed, demo_source=False)
        self.assertEqual(tools.verify(self.project, self.installed, demo_source=False,
                                      expected_shadow="on")["configuredShadowMode"], "on")

    def test_duplicate_receipt_path_fails(self):
        self.receipt["sourceFileHashes"].append(self.receipt["sourceFileHashes"][0])
        self.save_receipt()
        with self.assertRaisesRegex(tools.VerificationError, "Duplicate receipt path"):
            self.verify()

    def test_traversal_receipt_path_fails(self):
        self.receipt["sourceFileHashes"][0]["path"] = "../escape.cpp"
        self.save_receipt()
        with self.assertRaisesRegex(tools.VerificationError, "Unsafe source path"):
            self.verify()

    def test_duplicate_json_keys_fail(self):
        self.write(self.installed / tools.RECEIPT, '{"schemaVersion": 1, "schemaVersion": 1}')
        with self.assertRaisesRegex(tools.VerificationError, "Duplicate JSON key"):
            self.verify()

    def test_assume_unchanged_source_drift_is_detected(self):
        root = self.repos["il2cppPlus"]
        self.git(root, "update-index", "--assume-unchanged", "libil2cpp/vm/Sample.cpp")
        self.write(root / "libil2cpp/vm/Sample.cpp", "hidden drift")
        self.assertEqual(self.git(root, "status", "--short"), "")
        with self.assertRaisesRegex(tools.VerificationError, "pinned Git blob"):
            self.verify()

    def test_demo_metadata_only_advance_is_allowed(self):
        self.write(self.project / "Docs/AssemblyShadow/report.md", "Evidence, not code")
        self.git(self.project, "add", "Docs", tools.PINS)
        self.git(self.project, "commit", "-qm", "record pairing")
        self.assertTrue(self.verify()["demoSourceVerified"])

    def test_ignored_unpinned_unity_script_is_detected(self):
        self.write(self.project / "Assets/ignored.cs", "// still compiled by Unity")
        with self.assertRaisesRegex(tools.VerificationError, "Unpinned Unity code"):
            self.verify()

    @unittest.skipIf(sys.platform == "win32", "Symlink creation may require elevated Windows privileges")
    def test_installed_symlink_is_rejected(self):
        path = self.installed / "vm/Sample.cpp"
        path.unlink()
        path.symlink_to(self.repos["il2cppPlus"] / "libil2cpp/vm/Sample.cpp")
        with self.assertRaisesRegex(tools.VerificationError, "Symlink"):
            self.verify()

    def test_cache_dry_run_is_non_mutating(self):
        self.write(self.project / "Library/Bee/test.bin", "cache")
        result = tools.clean_cache(self.project)
        self.assertFalse(result["applied"])
        self.assertTrue((self.project / "Library/Bee/test.bin").exists())
        self.assertFalse((self.project / "_temp").exists())

    def test_cache_apply_is_recoverable(self):
        self.write(self.project / "Library/Bee/test.bin", "cache")
        with mock.patch.object(tools, "check_editor_stopped"):
            result = tools.clean_cache(self.project, apply=True)
        self.assertEqual((Path(result["backup"]) / "Bee/test.bin").read_text(), "cache")
        self.assertFalse((self.project / "Library/Bee").exists())
        self.assertTrue((Path(result["backup"]) / "manifest.json").is_file())

    def test_cache_apply_refuses_active_editor(self):
        self.write(self.project / "Library/Bee/test.bin", "cache")
        with mock.patch.object(tools, "check_editor_stopped", side_effect=tools.VerificationError("active Editor")):
            with self.assertRaises(tools.VerificationError):
                tools.clean_cache(self.project, apply=True)
        self.assertTrue((self.project / "Library/Bee/test.bin").exists())

    @unittest.skipIf(sys.platform == "win32", "Symlink creation may require elevated Windows privileges")
    def test_cache_symlink_is_rejected(self):
        (self.project / "Library").symlink_to(self.repos["hybridclr"])
        with self.assertRaisesRegex(tools.VerificationError, "Symlink"):
            tools.clean_cache(self.project)


if __name__ == "__main__":
    unittest.main()
