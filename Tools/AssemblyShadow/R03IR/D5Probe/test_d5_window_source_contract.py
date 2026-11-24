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

    def test_19_managed_no_native_tls_begin_missing(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "keepAttempted = R03_D5_BeginKeepAttempt() == 1;",
            "keepAttempted = FakeBeginKeepAttempt() == 1;")

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
            '"1268dd417ffe9090fcd9ea2d49542c97ed3cccb3"',
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
            "static int32_t FinishNativeReceipt(",
            "static int32_t FinishNativeReceiptRemoved(")

    def test_40_native_tls_pointer_join_cannot_be_removed(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "MatchesTargetOnCurrentThread(method)",
            "AnyThreadKeep(method)")

    def test_41_one_shot_worker_token_must_be_preserved(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "token.active = 0;",
            "token.active = 1;")

    def test_42_native_autoseal_thread_start_required(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "::pthread_create(",
            "::DoNotStartNativeCollector(")

    def test_43_native_autoseal_outside_managed_control(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "NativeCollector publishes a bounded native-only receipt",
            "ManagedFinalizerWillPublish")

    def test_44_native_completion_slot5_required(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "Record(5, decision, 1, 1, probe.TargetDenialKind())",
            "Record(5, 0, 0, 0, 0)")

    def test_45_host_autocollector_path_present(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "R03_D5_SourceHostAutoConfigure",
            "R03_D5_HostStubDeleted")

    def test_46_native_guard_TLStoken_starts_at_worker(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "ArmTargetForCurrentThread(boundKeepMethod)",
            "ArmTargetForAllThreads(boundKeepMethod)")

    def test_47_test_enabled_native_collector_cannot_call_managed_seal(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "using System;", "using System;\n// R03_D5_ReceiptSeal(postpoison)")


    def test_48_postterminal_canary_read_guarded_by_method_outcome(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "const bool canRead = hasReady && (decision == 2 || completedBody);",
            "const bool canRead = true;")

    def test_49_unarmed_staging_has_separate_bounded_deadline(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "armObserved ? 8000 : 60000",
            "armObserved ? 0 : 0")

    def test_50_denied_candidate_must_not_exit_zero(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "sawAttempt && sawGuard ? 20 : 2;",
            "sawAttempt && sawGuard ? 0 : 2;")

    def test_51_early_terminal_guard_result_mandatory(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "c10.MethodResult(d5EntryPhase,",
            "c10.EarlyTerminalResultDisabled(d5EntryPhase,")

    def test_52_early_terminal_guard_must_be_exact_target(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "c10.MatchesTargetOnCurrentThread(method), false",
            "true, false")

    def test_53_real_worker_release_requires_acquire(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "return release_.load(std::memory_order_acquire) != 0;",
            "return release_.load(std::memory_order_relaxed) != 0;")

    def test_54_timeout_must_not_read_unpublished_canary_before(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "if (hasReady) before = canaryBefore;",
            "before = canaryBefore;")

    def test_55_final_native_receipt_only_after_link(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "::link(pendingPath, finalPath)",
            "::rename(pendingPath, finalPath)")

    def test_56_private_native_evidence_name_cannot_be_removed(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            'static const char kSuffix[] = ".pending";',
            'static const char kSuffix[] = "";')

    def test_57_directory_sync_mandatory(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "const int dirSync = failDirSync ? -1 : ::fsync(dir);",
            "const int dirSync = 0;")

    def test_58_synthetic_pwrite_fault_path_mandatory(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "hostIoFault.load(std::memory_order_acquire) == 1",
            "hostIoFault.load(std::memory_order_acquire) == 777")

    def test_59_file_close_must_be_checked_before_publish(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "const int actualClose = ::close(currentFd);",
            "const int actualClose = 0;")


    def test_60_guard_entry_before_terminal(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "WindowProbe::Instance().TargetGuardEntry(",
            "WindowProbe::Instance().UnboundGuardEntry(")

    def test_61_first_error_not_fabricated(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "const int32_t first = static_cast<int32_t>(s_firstFailureV2.status());",
            "const int32_t first = 0;")

    def test_62_guard_entry_release(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "targetEntryReady_.store(1, std::memory_order_release)",
            "targetEntryReady_.store(1, std::memory_order_relaxed)")

    def test_63_guard_entry_acquire(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "if (targetEntryReady_.load(std::memory_order_acquire) != 1)",
            "if (targetEntryReady_.load(std::memory_order_relaxed) != 1)")

    def test_64_exact_tls_pointer(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "!MatchesTargetOnCurrentThread(methodIdentity)",
            "false /* no TLS identity */")

    def test_65_slot4_not_arm_only(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "sawAttempt = Record(4, 1, entryPolicy,",
            "sawAttempt = Record(4, 1, 0,")

    def test_66_no_fake_worker_finished(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "Record(6, -1, stateCode, releaseObserved,",
            "Record(6, -1, stateCode, 1,")

    def test_67_early_terminal_no_candidate(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "targetStateAtEntry == 5 /* Committing */",
            "targetStateAtEntry == 9 /* FailedAfterCommit */")

    def test_68_managed_protocol_v3(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "R03_D5_WindowProtocolVersion() != 3",
            "R03_D5_WindowProtocolVersion() != 1")

    def test_69_collector_entry_not_arming(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "probe.TryReadTargetGuardEntry(",
            "probe.TargetArmCount(")

    def test_70_native_receipt_schema_v3(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "header.schema = 3;",
            "header.schema = 1;")

    def test_71_first_error_empty_at_entry(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "firstErrorAtEntry == 0 /* Empty */",
            "firstErrorAtEntry == 2 /* Frozen */")

    def test_72_actual_release_evidence(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "const int32_t releaseObserved =",
            "const int32_t releaseObservedUnverified =")


    def test_73_durable_predicate_all_latches(self):
        self.mutated("native",N+"AssemblyShadow.cpp",
            "s_lateBaselineUse.load(std::memory_order_acquire) ||\n            s_referenceViolation.load(std::memory_order_acquire);",
            "s_lateBaselineUse.load(std::memory_order_acquire) ||\n            false;")

    def test_74_entry_mixed_latch_observation_must_fail_closed(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "before.durable != after.durable",
            "false")

    def test_75_exact_release_worker_required(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "token.owner != this || token.active != 0 || !token.method",
            "false")

    def test_76_terminal_raced_denial_not_candidate(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "terminalDenied && probe.TargetDenialKind() == 0",
            "terminalDenied")

    def test_77_worker_release_after_invoke_required(self):
        self.mutated("demo",D+"R03D5P5WindowPlayer.cs",
            "R03_D5_ReleaseP5Window();\n                    }",
            "/* no completion */\n                    }")

    def test_78_canary_uses_recorded_acquire(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "const bool completedBody = decision == 1 && releaseObserved == 1;",
            "const bool completedBody = decision == 1;")

    def test_79_entry_policy_in_receipt(self):
        self.mutated("demo",D+"R03D5WindowOverlay.cpp",
            "entryPolicy == 1 /* observed nonterminal */",
            "true")

    def test_80_release_checks_acquired_entry(self):
        self.mutated("native",N+"AssemblyShadowD5WindowProbe.h",
            "targetEntryReady_.load(std::memory_order_acquire) != 1 ||",
            "targetEntryReady_.load(std::memory_order_relaxed) != 1 ||")

if __name__=="__main__":
    unittest.main()
