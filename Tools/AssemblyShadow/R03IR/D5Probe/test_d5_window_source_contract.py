#!/usr/bin/env python3
"""Read exact Git files and mutation-test the D5 C10 test-only source boundary."""
import copy
import os
from pathlib import Path
import unittest
import d5_window_source_contract as gate

N="libil2cpp/vm/"
D="Tools/AssemblyShadow/R03IR/D5Probe/"


class D5C10SourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=Path(os.environ["R03_D5C10_NATIVE_ROOT"])
        cls.demo=Path(os.environ["R03_D5C10_DEMO_ROOT"])
        cls.ns={path:(cls.native/path).read_text(encoding="utf-8-sig")
                for path in gate.NATIVE_FILES}
        cls.ds={path:(cls.demo/path).read_text(encoding="utf-8-sig")
                for path in gate.DEMO_FILES}

    def mutated(self,role,path,a,b):
        native=copy.deepcopy(self.ns)
        demo=copy.deepcopy(self.ds)
        target=native if role=="native" else demo
        self.assertIn(a,target[path])
        target[path]=target[path].replace(a,b,1)
        with self.assertRaises(gate.SourceMismatch):
            gate.verify_sources(native,demo)

    def test_01_genuine_pinned_native_source(self):
        r=gate.verify_sources(self.ns,self.ds)
        self.assertEqual(r["result"],"PassedActualSourceContractOnly_NotUnityPlayer")
        self.assertFalse(r["realPlayerC10Completed"])

    def test_02_github_blob_rejects_one_byte_change(self):
        p=N+"AssemblyShadow.cpp"
        raw=(self.native/p).read_bytes()
        self.assertEqual(gate.git_blob(raw),gate.NATIVE_FILES[p])
        self.assertNotEqual(gate.git_blob(raw+b"\n"),gate.NATIVE_FILES[p])

    def test_03_wrong_native_commit_rejected(self):
        with self.assertRaises(gate.SourceMismatch):
            gate.inspect(self.native,self.demo,"0"*40,"a"*40)

    def test_04_test_only_core_include_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            '#include "AssemblyShadowD5WindowProbe.h"',
            '#include "MissingD5Window.h"')

    def test_05_p5_observer_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "d5Window.AtP5();","(void)d5Window;")

    def test_06_p5_hold_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "d5Window.HoldP5Bounded();","/* removed */")

    def test_07_p5_transactions_lock_reacquire_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "        d5Window.HoldP5Bounded(); // <= 2000ms; no VM, locks or callbacks.\n        lock.lock();",
            "        d5Window.HoldP5Bounded();")

    def test_08_p6_observer_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "assembly_shadow_d5::WindowProbe::Instance().AtP6();",
            "/* missing P6 */")

    def test_09_completed_observer_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "assembly_shadow_d5::WindowProbe::Instance().Complete();",
            "/* missing Complete */")

    def test_10_core_method_begin_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "WindowProbe::Instance().MethodBegin()","WindowProbe::Instance().Read()")

    def test_11_actual_shadow_method_selection_missing(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            'std::strcmp(method->name, "Keep") == 0',
            'std::strcmp(method->name, "GenericBody") == 0')

    def test_12_shadow_result_source_removed(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "WindowProbe::Instance().MethodResult(",
            "WindowProbe::Instance().IgnoredResult(")

    def test_13_timed_wait_limit_removed(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "maximumWaitMs < 20 || maximumWaitMs > 2000",
            "maximumWaitMs < 0")

    def test_14_witness_phase_token_changed(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "AtP5 = 2","AtP5 = 12")

    def test_15_witness_method_counter_missing(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "methodResultRacedP6_.fetch_add",
            "ignoredRacedP6_.fetch_add")

    def test_16_overlay_export_missing(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "IL2CPP_EXPORT int32_t R03_D5_ArmP5Window",
            "IL2CPP_EXPORT int32_t R03_D5_OtherWindow")

    def test_17_overlay_fixed_wire_size_changed(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "sizeof(int32_t) * 11","sizeof(int32_t) * 12")

    def test_18_managed_real_method_invoke_missing(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "method.Invoke(instance, null)","42")

    def test_19_managed_no_native_seal_missing(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "R03_D5_ReceiptSeal(commit, stateCode, finish, keep)",
            "FakeReceiptSeal(commit, stateCode, finish, keep)")

    def test_20_managed_r03_acceptance_forged(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "using System;",
            "using System;\n// R03Accepted = true")

    def test_21_native_d4_process_owner_source_missing(self):
        self.mutated("native",N+"AssemblyShadowProcessSnapshotOwner.h",
            "retained_ = std::move(pending);","(void)pending;")

    def test_22_managed_omits_exact_unity(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            'Application.unityVersion != "2022.3.62f2"',
            'Application.unityVersion != "2023.1"')

    def test_23_overlay_adds_global_allocator(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            '#include <cstdint>',
            '#include <cstdint>\nvoid* operator new(std::size_t);')

    def test_24_managed_reuses_output_path(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "R03_D5_ReceiptOpen(outputPath, req.runId,",
            'R03_D5_ReceiptOpen("/tmp/shared", req.runId,')

    def test_25_native_production_method_checks_unmodified(self):
        core=self.ns[N+"AssemblyShadow.cpp"]
        self.assertIn("AssemblyShadowError AssemblyShadow::CommitTransaction()",core)
        self.assertIn("bool AssemblyShadow::AssertMethodIsActive",core)
        self.assertIn("AssemblyShadowState::Committing",core)


    def test_26_builder_pinned_commit_changed(self):
        self.mutated("demo",D+"R03D5Build.cs",
            '"84f9435628b8ff4cc675409f6b4d76dd2753d8a8"',
            '"0000000000000000000000000000000000000000"')

    def test_27_builder_missing_native_install(self):
        self.mutated("demo",D+"R03D5Build.cs",
            "PinnedSourceInstaller.Install();","/* no actual install */")

    def test_28_builder_overlay_not_copied(self):
        self.mutated("demo",D+"R03D5Build.cs",
            "File.Copy(config.overlayPath, overlayDestination, false);",
            "/* unlinked D5 overlay */")

    def test_29_builder_loses_test_only_macro(self):
        self.mutated("demo",D+"R03D5Build.cs",
            '" -DHYBRIDCLR_R03_D5_WINDOW_PROBE="',
            '" -DHYBRIDCLR_R03_OLD_PROBE="')

    def test_30_builder_forges_binary_proof(self):
        self.mutated("demo",D+"R03D5Build.cs",
            "independentLinkedBinaryProof = false",
            "independentLinkedBinaryProof = true")

    def test_31_builder_reuses_output(self):
        self.mutated("demo",D+"R03D5Build.cs",
            "FileMode.CreateNew","FileMode.Create")

    def test_32_builder_without_buildpipeline(self):
        self.mutated("demo",D+"R03D5Build.cs",
            "BuildPipeline.BuildPlayer(new BuildPlayerOptions",
            "FakeBuildPipeline.BuildPlayer(new BuildPlayerOptions")


    def test_33_constructor_denial_not_keep_method(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            'std::strcmp(method->klass->name, "Node") == 0',
            'std::strcmp(method->klass->name, "AnyNode") == 0')

    def test_34_native_first_error_custody_must_stay(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "TryReadFirstFailureV2(snapshot)", "NoRealFirstError(snapshot)")

    def test_35_native_exclusive_evidence_must_stay(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "O_EXCL | O_CLOEXEC | O_NOFOLLOW",
            "O_TRUNC | O_CLOEXEC")

    def test_36_managed_target_canary_bind_must_stay(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "nativeBindSucceeded = R03_D5_BindKeepCanary(",
            "nativeBindSucceeded = PretendBindCanary(")

    def test_37_managed_post_terminal_json_is_forbidden(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "using System;", "using System;\n// JsonUtility.ToJson would be unsafe")

    def test_38_builder_real_vm_evidence_macro_must_stay(self):
        self.mutated("demo",D+"R03D5Build.cs",
            '" -DHYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE="',
            '" -DHYBRIDCLR_R03_D5_DUMMY_VM="')

    def test_39_canary_after_snapshot_is_mandatory(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "Record(9, canaryBefore, after, valid, 0)",
            "Record(9, -1, -1, 0, 0)")


if __name__=="__main__":
    unittest.main()
