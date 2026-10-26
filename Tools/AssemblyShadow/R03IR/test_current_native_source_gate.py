#!/usr/bin/env python3
"""Host-only R03 IR current-source candidate tests; no Player/SDK invocation."""
from __future__ import annotations

import argparse
import ast
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from current_native_source_gate import (
    CandidateSourceError, BRANCH, CONFIG, CURRENT, FILES, OLD_NATIVE,
    candidate_pins, git_blob, read_config, verify_source_roots,
)


class CurrentNativeSourceGateContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "args"):
            raise RuntimeError("Explicit --demo/--native/--hybridclr/--package required")
        cls.roots = {
            "hybridclr_demo": Path(cls.args.demo).resolve(),
            "il2cpp_plus": Path(cls.args.native).resolve(),
            "hybridclr": Path(cls.args.hybridclr).resolve(),
            "hybridclr_unity": Path(cls.args.package).resolve(),
        }
        cls.config = read_config()
        cls.original_pins = json.loads(
            (cls.roots["hybridclr_demo"] /
             "Tools/AssemblyShadow/R03/source-pins.json").read_text())

    def synthetic_sources(self, parent: Path):
        roots = {}
        for name in ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus"):
            path = parent / name
            path.mkdir()
            roots[name] = path
        for (name, relative) in FILES:
            source = self.roots[name] / relative
            target = roots[name] / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        return roots

    def test_01_manifest_has_exact_ten_files_and_fixed_source_pins(self):
        self.assertEqual(len(self.config["files"]), len(FILES))
        self.assertEqual(len(FILES), 10)
        self.assertEqual(self.config["candidateNativePin"], CURRENT["il2cpp_plus"])
        self.assertEqual(self.config["legacyR03NativePin"], OLD_NATIVE)
        self.assertNotEqual(CURRENT["il2cpp_plus"], OLD_NATIVE)
        self.assertEqual(self.config["branch"], BRANCH)

    def test_02_original_legacy_r03_pin_remains_byte_bound_to_old_native(self):
        original = (self.roots["hybridclr_demo"] /
                    "Tools/AssemblyShadow/R03/source-pins.json").read_bytes()
        self.assertEqual(git_blob(original), FILES[(
            "hybridclr_demo", "Tools/AssemblyShadow/R03/source-pins.json")])
        self.assertEqual(self.original_pins["il2cpp_plus"], OLD_NATIVE)
        self.assertFalse(self.original_pins["runtimeAcceptance"])

    def test_03_current_candidate_is_a_pure_in_memory_pin_overlay(self):
        original = copy.deepcopy(self.original_pins)
        new = candidate_pins(original, self.config)
        self.assertEqual(new["il2cpp_plus"], CURRENT["il2cpp_plus"])
        self.assertEqual(new["hybridclr"], CURRENT["hybridclr"])
        self.assertEqual(new["hybridclr_unity"], CURRENT["hybridclr_unity"])
        self.assertEqual(original["il2cpp_plus"], OLD_NATIVE)
        self.assertEqual(new["branch"], BRANCH)
        self.assertIsNot(new, original)

    def test_04_real_checkout_sources_have_exact_ten_known_git_blobs(self):
        d = verify_source_roots(self.roots, require_checkout_heads=True)
        self.assertEqual(d["result"], "PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation")
        self.assertEqual(d["verifiedSourceFiles"], 10)
        self.assertEqual(d["currentCandidatePins"], CURRENT)
        self.assertEqual(d["checkoutHeads"], CURRENT)
        self.assertEqual(d["currentSourceMatchedPlayerExecution"], "NotRun")
        self.assertFalse(d["runtimeAcceptance"])
        self.assertFalse(d["newBuildOrUnityPlayerRun"])

    def test_05_candidate_file_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            roots = self.synthetic_sources(Path(d).resolve())
            source = roots["il2cpp_plus"] / "libil2cpp/vm/AssemblyShadow.cpp"
            source.write_bytes(source.read_bytes() + b"\n// unexpected native drift\n")
            with self.assertRaisesRegex(CandidateSourceError, "Git blob mismatch"):
                verify_source_roots(roots)

    def test_06_interpreter_source_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            roots = self.synthetic_sources(Path(d).resolve())
            source = roots["hybridclr"] / "hybridclr/interpreter/Interpreter_Execute.cpp"
            source.write_bytes(source.read_bytes() + b"\n// drift\n")
            with self.assertRaises(CandidateSourceError):
                verify_source_roots(roots)

    def test_07_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            roots = self.synthetic_sources(Path(d).resolve())
            (roots["hybridclr_demo"] / "Tools/AssemblyShadow/R03IR/run_terminal_local.py").unlink()
            with self.assertRaises(CandidateSourceError):
                verify_source_roots(roots)

    def test_08_symlinked_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            roots = self.synthetic_sources(Path(d).resolve())
            original = roots["il2cpp_plus"] / "libil2cpp/vm/Runtime.cpp"
            alias = original.parent / "RuntimeTarget.cpp"
            original.rename(alias)
            original.symlink_to(alias)
            with self.assertRaises(CandidateSourceError):
                verify_source_roots(roots)

    def test_09_symlinked_parent_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            roots = self.synthetic_sources(Path(d).resolve())
            parent = roots["il2cpp_plus"] / "libil2cpp/vm"
            physical = roots["il2cpp_plus"] / "physical-vm"
            parent.rename(physical)
            parent.symlink_to(physical, target_is_directory=True)
            with self.assertRaises(CandidateSourceError):
                verify_source_roots(roots)

    def test_10_duplicate_or_missing_manifest_source_is_rejected(self):
        data = copy.deepcopy(self.config)
        data["files"].append(data["files"][0])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve() / "candidate.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(CandidateSourceError):
                read_config(p)
            data["files"] = data["files"][1:-1]
            p.write_text(json.dumps(data))
            with self.assertRaises(CandidateSourceError):
                read_config(p)

    def test_11_unknown_optional_source_cannot_silently_expand_manifest(self):
        data = copy.deepcopy(self.config)
        data["files"][0]["gitBlob"] = "0" * 40
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve() / "candidate.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(CandidateSourceError):
                read_config(p)

    def test_12_old_and_current_native_revisions_cannot_be_swapped(self):
        data = copy.deepcopy(self.config)
        data["candidateNativePin"] = OLD_NATIVE
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve() / "candidate.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(CandidateSourceError):
                read_config(p)

    def test_13_gate_cannot_promote_runtime_acceptance(self):
        for flag in ("candidateRuntimeAcceptance", "sourceOnlyValidationIsProductValidation",
                     "originalSResultReclassified", "originalB7e3AndC42aFailReclassified"):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as d:
                data = copy.deepcopy(self.config)
                data[flag] = True
                p = Path(d).resolve() / "candidate.json"
                p.write_text(json.dumps(data))
                with self.assertRaises(CandidateSourceError):
                    read_config(p)

    def test_14_duplicate_json_key_is_rejected(self):
        raw = CONFIG.read_text()
        self.assertIn('"schemaVersion": 1', raw)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve() / "candidate.json"
            p.write_text(raw.replace('"schemaVersion": 1',
                                     '"schemaVersion": 1, "schemaVersion": 1', 1))
            with self.assertRaises(CandidateSourceError):
                read_config(p)

    def test_15_original_runner_must_inject_explicit_batch_type(self):
        original = (self.roots["hybridclr_demo"] /
                    "Tools/AssemblyShadow/R03IR/run_terminal_local.py").read_text()
        self.assertIn("def execute(workspace, output, unity, demo_commit, *, batch_type=Batch)", original)
        self.assertIn("batch = batch_type(workspace, output, unity, demo_commit)", original)
        for case in ("IR-R03-02-release-baseline", "IR-R03-02-debug-baseline",
                     "IR-R03-02-release-type", "IR-R03-02-off",
                     "IR-R03-02-release-engine"):
            self.assertIn(case, original)

    def test_16_new_wrapper_validates_before_collector_output_creation(self):
        wrapper = (HERE / "run_terminal_current.py").read_text()
        ast.parse(wrapper)
        start = wrapper.index("class CurrentNativeBatch(")
        before = wrapper.index("verify_source_roots(", start)
        base = wrapper.index("super().__init__(", start)
        overlay = wrapper.index("self.pins = candidate_pins(", start)
        self.assertLess(before, base)
        self.assertLess(base, overlay)
        self.assertIn("require_checkout_heads=True", wrapper)
        self.assertIn("run_existing_focused_batch(", wrapper)
        self.assertIn("batch_type=CurrentNativeBatch", wrapper)
        self.assertNotIn("subprocess.run(", wrapper)

    def test_17_native_terminal_policy_and_dispatch_entry_are_both_bound(self):
        for key in (("il2cpp_plus", "libil2cpp/vm/AssemblyShadow.cpp"),
                    ("il2cpp_plus", "libil2cpp/vm/AssemblyShadowTerminalExecution.h"),
                    ("il2cpp_plus", "libil2cpp/vm/Runtime.cpp"),
                    ("hybridclr", "hybridclr/interpreter/Interpreter_Execute.cpp")):
            self.assertIn(key, FILES)
            self.assertEqual(git_blob((self.roots[key[0]] / key[1]).read_bytes()), FILES[key])

    def test_18_test_manifest_must_not_claim_complete_generic_initializer_coverage(self):
        d = verify_source_roots(self.roots)
        self.assertEqual(d["focusedPlayerCaseCount"], 5)
        self.assertEqual(d["candidateNativeBuildRoles"], 3)
        self.assertEqual(d["originalSFixtureCount"], 15)
        self.assertFalse(d["H2Passed"])
        self.assertFalse(d["ReadyForHumanReviewGate"])
        self.assertFalse(d["R03Accepted"])
        self.assertEqual(d["nextLocalAuthority"], "NotAuthorized")

    def test_19_source_malformed_json_or_wrong_repository_roots_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d).resolve() / "candidate.json"
            p.write_text("{ invalid JSON")
            with self.assertRaises(ValueError):
                read_config(p)
            duplicate_roots = dict(self.roots)
            duplicate_roots["hybridclr"] = duplicate_roots["il2cpp_plus"]
            with self.assertRaises(CandidateSourceError):
                verify_source_roots(duplicate_roots)

    def test_20_legacy_pin_mutation_not_allowed_as_candidate_shortcut(self):
        original = copy.deepcopy(self.original_pins)
        original["il2cpp_plus"] = CURRENT["il2cpp_plus"]
        with self.assertRaises(CandidateSourceError):
            candidate_pins(original, self.config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for key in ("demo", "native", "hybridclr", "package"):
        parser.add_argument("--" + key, required=True)
    args = parser.parse_args()
    CurrentNativeSourceGateContracts.args = args
    unittest.main(argv=[sys.argv[0]])
