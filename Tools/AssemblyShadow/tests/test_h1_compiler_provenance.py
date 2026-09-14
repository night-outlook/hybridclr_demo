import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "Tools/AssemblyShadow/verify-h1-compiler-provenance.py"
SPEC = importlib.util.spec_from_file_location("h1_compiler_provenance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class H1CompilerProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "tool").write_bytes(b"compiler")
        (self.root / "sdk").mkdir()
        self.output = self.root / "build/GameAssembly.dylib"
        self.output.parent.mkdir()
        self.output.write_bytes(b"native")
        compiler = self.root / "tool"
        sdk = self.root / "sdk"
        common = f'"{compiler}" -isysroot "{sdk}" -DIL2CPP_DEBUG=1 '
        self.graph = {"Nodes": [
            {"Annotation": "C_Mac_arm64 obj/a.o", "Action": common + "-c a.cpp", "Outputs": ["obj/a.o"]},
            {"Annotation": "Link_Mac_arm64 obj/GameAssembly.dylib", "Action": common + "obj/a.o",
             "Inputs": ["obj/a.o"], "Outputs": ["obj/GameAssembly.dylib"]},
            {"Annotation": "CopyFiles build/GameAssembly.dylib", "Inputs": ["obj/GameAssembly.dylib"],
             "Outputs": ["build/GameAssembly.dylib"]},
        ]}
        self.config = "#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n"

    def tearDown(self):
        self.temp.cleanup()

    def test_default_scope_requires_complete_four_mode_inventory(self):
        self.assertEqual(MODULE.required_modes(False), frozenset(("On/Debug", "On/Release", "Off/Debug", "Off/Release")))

    def test_repro_scope_requires_exact_native_on_pair(self):
        self.assertEqual(MODULE.required_modes(True), frozenset(("On/Debug", "On/Release")))

    def test_graph_evidence_is_derived_from_actions_and_output_chain(self):
        value = MODULE.derive_graph_evidence(self.graph, self.root, self.output, self.config)
        self.assertEqual(value["compilerPath"], os.path.abspath(self.root / "tool"))
        self.assertEqual(value["sdkPath"], os.path.abspath(self.root / "sdk"))
        self.assertEqual(value["il2cppDebug"], "1")
        self.assertEqual(value["il2cppDevelopment"], "0")
        self.assertEqual(value["ndebug"], "0")
        self.assertEqual(value["compileActionCount"], 1)

    def test_graph_rejects_native_output_not_reachable_from_link(self):
        self.graph["Nodes"][2]["Inputs"] = ["obj/unrelated.dylib"]
        with self.assertRaisesRegex(MODULE.VerificationError, "does not reach"):
            MODULE.derive_graph_evidence(self.graph, self.root, self.output, self.config)

    def test_graph_rejects_inconsistent_compilers(self):
        other = self.root / "other-tool"
        other.write_bytes(b"other")
        self.graph["Nodes"][1]["Action"] = self.graph["Nodes"][1]["Action"].replace(
            str(self.root / "tool"), str(other))
        with self.assertRaisesRegex(MODULE.VerificationError, "more than one compiler"):
            MODULE.derive_graph_evidence(self.graph, self.root, self.output, self.config)

    def test_duplicate_json_keys_are_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"schemaVersion":1,"schemaVersion":2}', encoding="utf-8")
        with self.assertRaisesRegex(MODULE.VerificationError, "Duplicate JSON key"):
            MODULE.read_object(path)


if __name__ == "__main__":
    unittest.main()
