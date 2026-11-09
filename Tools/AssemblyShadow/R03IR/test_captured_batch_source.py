#!/usr/bin/env python3
"""Read-only current HEAD and strict one-build/three-Player contract checks.

Synthetic source/CLI tests only: no Unity, native Player, original S mutation
or automatic Local execution.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import run_captured_generic_local as runner
from batch_contract import ContractError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class CapturedBatchSourceContracts(unittest.TestCase):
    def test_01_fixed_distinct_onebuild_threeplayer_roster(self):
        self.assertEqual(len(runner.CELLS),19)
        self.assertEqual(len(set(runner.CELLS)),19)
        self.assertEqual(runner.CELLS.count("build-captured"),1)
        self.assertEqual(runner.CELLS[-5:],(
            "build-captured","player-initializer-control",
            "player-initializer-failure","player-captured-generic",
            "final-authority"))
        self.assertEqual(runner.MODES,(
            "initializer-control","initializer-failure","captured-generic"))

    def test_02_all_actual_new_primary_files_have_Git_HEAD_byte_authority(self):
        self.assertEqual(len(runner.EXTRA_SOURCE_PATHS),
                         len(set(runner.EXTRA_SOURCE_PATHS)))
        # All fresh managed API compilation and host-test inputs are Git HEAD
        # authenticated, not just the native/Player source files.
        for required in ("CapturedGenericPlayerHost/CapturedGenericPlayerHost.csproj",
                         "CapturedGenericPlayerHost/Program.cs",
                         "CapturedGenericPlayerHost/Stubs.cs",
                         "verify_captured_generic_host.py",
                         "test_captured_generic_host.py",
                         "test_captured_source_preparation.py",
                         "test_captured_batch_source.py"):
            self.assertIn("Tools/AssemblyShadow/R03IR/" + required,
                          runner.EXTRA_SOURCE_PATHS)
        report=runner.check_new_sources(ROOT)
        self.assertEqual(set(report),set(runner.EXTRA_SOURCE_PATHS))
        self.assertTrue(all(len(x)==64 for x in report.values()))

    def test_03_missing_foreign_repo_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="r03-capture-outside-") as tmp:
            with self.assertRaises((ContractError, OSError)):
                runner.check_new_sources(Path(tmp))

    def test_04_git_show_failure_cannot_be_labelled_PASS(self):
        with mock.patch.object(runner.subprocess,"run",
             return_value=subprocess.CompletedProcess([],returncode=1,
                 stdout=b"",stderr=b"not actual git authority")):
            with self.assertRaises((ContractError, OSError)):
                runner.check_new_sources(ROOT)

    def test_05_git_source_sha_mismatch_cannot_be_labelled_PASS(self):
        with mock.patch.object(runner.subprocess,"run",
             return_value=subprocess.CompletedProcess([],returncode=0,
                 stdout=b"not committed source bytes",stderr=b"")):
            with self.assertRaises((ContractError, OSError)):
                runner.check_new_sources(ROOT)

    def test_06_exact_coordinator_imports_and_Git_and_runtime_guards(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        ast.parse(s)
        for anchor in ("validate_destination(", "validate_original(",
                       "validate_sources(", "validate_machine(",
                       'batch.cell("entry-authority"',
                       "check_git_source(", "check_new_sources(",
                       "sha(state[\"project\"] / \"source-inputs.json\")",
                       "verify_captured(", "batch.verify_build(role)",
                       "batch.command(command, 210)", "finalize(batch.root,"):
            self.assertIn(anchor,s)

    def test_07_no_synthetic_pass_approval_or_dry_run(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        self.assertIn('"runtimeAcceptance": False',s)
        self.assertIn('"R03Accepted": False',s)
        self.assertIn('"H2Passed": False',s)
        self.assertIn('"ReadyForHumanReviewGate": False',s)
        self.assertIn('"nativeV2TransportImplemented": False',s)
        self.assertNotIn('use_stub_player',s)
        self.assertNotIn('skip_native_build',s)

    def test_08_original_initializer_bridge_and_players_kept(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        self.assertIn("super().verify_build(role_id)",s)
        self.assertIn('"initializerBridgeSignature") == "Bi4"',s)
        self.assertIn("target_fixture(batch)",s)
        self.assertIn("init_player(batch, m)",s)
        self.assertIn("original_s_fixtures(batch)",s)
        self.assertIn("archive_audit(batch)",s)
        self.assertIn("original_process_audit(batch)",s)
        self.assertIn("original_binary_audit(batch",s)

    def test_09_actual_new_native_exports_must_link(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        cpp=(HERE/"PlayerProject/R03CapturedGenericPhysicalProbe.cpp").read_text()
        for export in ("R03_IRG_Open", "R03_IRG_Probe",
                       "R03_IRG_AttemptRuntimeInvoke","R03_IRG_Seal"):
            self.assertIn('"_' + export + '"',s)
            self.assertIn(" " + export + "(",cpp)

    def test_10_actual_il2cpp_Player_calls_only_post_Commit(self):
        s=(HERE/"PlayerProject/R03CapturedGenericPlayer.cs").read_text()
        for anchor in ("R03CapturedGenericAotOwner.WarmShared()",
                       "AssemblyShadowRuntime.ConfigureCandidates(",
                       "AssemblyShadowRuntime.ValidateTransaction()",
                       "AssemblyShadowRuntime.CommitTransaction()",
                       "R03_IRG_Probe()", "R03_IRG_AttemptRuntimeInvoke()",
                       "R03_IRG_Seal()", "R03_IR_Exit(0)"):
            self.assertIn(anchor,s)
        self.assertLess(s.index("R03CapturedGenericAotOwner.WarmShared()"),
                        s.index("AssemblyShadowRuntime.ConfigureCandidates("))
        self.assertLess(s.index("AssemblyShadowRuntime.CommitTransaction()"),
                        s.index("Need(R03_IRG_Probe() == 1"))
        self.assertLess(s.index("Need(R03_IRG_Probe() == 1"),
                        s.index("Need(R03_IRG_AttemptRuntimeInvoke() == 1"))

    def test_11_native_A2_proof_requires_real_metadata_methods_not_stack_forgeries(self):
        s=(HERE/"PlayerProject/R03CapturedGenericPhysicalProbe.cpp").read_text()
        for anchor in ("GetAotAssemblyByNamePhysical(kBaseline)",
                       "GetAssemblyTypeHandle(baseline->image, index)",
                       "GetTypeNamespaceAndName(handle)",
                       "MetadataCache::GetGenericInstanceMethod(",
                       "method->genericMethod->context.method_inst",
                       "AssemblyShadow::AssertMethodIsActive(",
                       "Runtime::Invoke(witness.inflated",
                       "AssemblyShadow::GetRecoveryInfoJson(recovery)"):
            self.assertIn(anchor,s)
        self.assertNotIn("reinterpret_cast<MethodInfo*>(&",s)
        self.assertNotIn("MethodInfo fake",s)

    def test_12_fixture_is_generated_twice_and_no_historical_replacement(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        self.assertIn("--ir-terminal-producers",s)
        self.assertIn("left",s)
        self.assertIn("repeat",s)
        self.assertIn("expected.read_bytes() == reproduced.read_bytes()",s)
        self.assertIn("--ir-terminal-host",s)
        self.assertIn('"originalSRegeneratedOrReplaced": False',s)

    def test_13_help_starts_in_real_new_interpreter_from_foreign_cwd(self):
        with tempfile.TemporaryDirectory(prefix="r03-captured-help-") as tmp:
            env=dict(os.environ)
            env.pop("PYTHONPATH",None)
            env.pop("PYTHONHOME",None)
            env["PYTHONDONTWRITEBYTECODE"]="1"
            p=subprocess.run([sys.executable,"-B",str(HERE/"run_captured_generic_local.py"),
                              "--help"],cwd=tmp,env=env,
                             capture_output=True,text=True,timeout=40)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn("--demo-commit",p.stdout)
            self.assertIn("--original-s",p.stdout)
            self.assertNotIn("--dry-run",p.stdout)
            self.assertFalse(list(Path(tmp).iterdir()))

    def test_14_protected_old_initializer_source_bytes_are_not_modified_by_runner(self):
        s=(HERE/"run_captured_generic_local.py").read_text()
        self.assertIn("from run_initializer_local import (",s)
        self.assertNotIn("write_text(\"PASS\")",s)
        self.assertNotIn("def init_player(",s)
        self.assertNotIn("R03InitializerObservationPlayer.cs\"].write",s)


if __name__=="__main__":
    unittest.main(verbosity=2)
