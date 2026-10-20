#!/usr/bin/env python3
"""Read-only source/CLI controls for the R03 P1 one-shot Local SDK preflight.

This is a HOST-only gate, not an installed Unity test or R03 runtime result.
"""
from __future__ import annotations
import ast
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
SRC=HERE/"run_p1_metadata_local_preflight.py"
BUILD=HERE.parent/"R03/native_validation.py"
class PreflightContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pre=SRC.read_text()
        cls.sdk=BUILD.read_text()
        ast.parse(cls.pre,filename=str(SRC))
        ast.parse(cls.sdk,filename=str(BUILD))
        spec=importlib.util.spec_from_file_location("p1_single_batch",SRC)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.mod=module

    def test_bounds_and_case_matrix(self):
        required=(
            "run_p1_command_failure_tests.py",
            "run_primary_host_preflight.py",
            "run_metadata_lifetime_gate.py",
            "run_bounded_ordinary_classes.py",
            "run_bounded_physical_assemblies.py",
            "run_bounded_first_use.py",
            "run_bounded_general_composer.py",
            "run_bounded_general_live.py",
            "run_frozen_execution.py",
            "run_bounded_execution_empty_live.py",
            "run_opaque_execution_inventory.py",
            "AssemblyShadowExecutionRegistryRevision.h",
            "AssemblyShadowExecutionRegistrationWitness.h",
            "AssemblyShadowExecutionRegistryPublisher.h",
            "AssemblyShadowOpaqueInventorySyntax.cpp",
            "AssemblyShadowExecutionEmptyLiveSyntax.cpp",
            "AssemblyShadowExecutionComposeSyntax.cpp",
            "run_bounded_transaction_status.py",
            "run_bounded_transaction_inventory.py",
            "run_frozen_v2.py",
            "build_api.py",
            "native_validation.py",
        )
        for name in required:
            with self.subTest(name=name):
                self.assertIn(name,self.pre)
        self.assertIn('len(cases)==16',self.pre)
        self.assertIn('sourcePreserved',self.pre)
        self.assertIn('expectedNativeSyntaxUnits":90',self.pre)
        self.assertIn('historicalEvidenceReclassified":False',self.pre)
        self.assertIn('"UnityPlayerExecuted":False',self.pre)

    def test_candidate_sdk_is_opt_in_and_histories_unchanged(self):
        self.assertIn("--candidate-native-sha",self.pre)
        self.assertIn("--candidate-native-sha",self.sdk)
        self.assertIn("expected_units=18 if candidate else 12",self.sdk)
        self.assertIn("candidateNativeSha",self.sdk)
        self.assertIn("historicalPinsOverriddenOnDisk",self.sdk)
        self.assertIn("source-pins.json",self.pre)
        self.assertNotIn("source-pins.json\").write_text(",self.pre)

    def test_help_has_explicit_pins(self):
        proc=subprocess.run([sys.executable,"-B",str(SRC),"--help"],
                            capture_output=True,text=True,timeout=20)
        self.assertEqual(proc.returncode,0,proc.stderr)
        for flag in ("--workspace","--unity","--output","--sdk-scratch",
                     "--expected-demo","--expected-native"):
            self.assertIn(flag,proc.stdout)

    def test_invalid_pin_and_roots_refuse_before_io(self):
        with tempfile.TemporaryDirectory() as d:
            t=Path(d)
            workspace=t/"workspace"
            workspace.mkdir()
            output=t/"evidence"
            scratch=t/"scratch"
            bad=[sys.executable,"-B",str(SRC),
                 "--workspace",str(workspace),
                 "--unity",str(t/"missing/2022.3.62f2/Unity.app/Contents/MacOS/Unity"),
                 "--output",str(output),"--sdk-scratch",str(scratch),
                 "--expected-demo","bad",
                 "--expected-native","0"*40]
            r=subprocess.run(bad,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse(output.exists())
            self.assertFalse(scratch.exists())
            bad[bad.index("bad")]="1"*40
            bad[bad.index(str(scratch))]=str(output)
            r=subprocess.run(bad,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse(output.exists())

    def test_known_remote_identity_pin_coverage(self):
        self.assertEqual(len(self.mod.FIXED),2)
        self.assertEqual(len(self.mod.REPOS),4)
        self.assertEqual(self.mod.BRANCH,"codex/assembly-shadow-r01b-h1")
        for sha in self.mod.FIXED.values():
            self.assertEqual(len(sha),40)

if __name__=="__main__":
    unittest.main(verbosity=2)
