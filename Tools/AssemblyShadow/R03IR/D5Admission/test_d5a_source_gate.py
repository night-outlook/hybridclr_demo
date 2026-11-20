#!/usr/bin/env python3
"""D5-A source-authority regressions: exact pins, old B1 immutability and no Local."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

import d5a_source_gate as gate


class D5ASourceAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=gate.read_json((gate.ROOT/"d5a_candidate_v1.json").read_bytes())
        cls.fixture=gate.read_json((gate.ROOT/"d5a_fixture_registry_v1.json").read_bytes())
        cls.roots={}
        for role,var in (
            ("hybridclr_demo","R03_D5A_DEMO_ROOT"),
            ("hybridclr","R03_D5A_HYBRID_ROOT"),
            ("hybridclr_unity","R03_D5A_PACKAGE_ROOT"),
            ("il2cpp_plus","R03_D5A_NATIVE_ROOT"),
        ):
            value=os.environ.get(var)
            if not value: raise RuntimeError("Exact D5-A four-repo input missing: "+var)
            cls.roots[role]=Path(value)
        cls.sources={}
        for role,files in cls.profile["sourceGitBlobs"].items():
            cls.sources[role]={
                p:(cls.roots[role]/p).read_bytes().decode("utf-8-sig")
                for p in files
            }

    def wrong_profile(self,mutator):
        p=copy.deepcopy(self.profile)
        mutator(p)
        with self.assertRaises(gate.Rejected):
            gate.validate_profile(p)

    def wrong_fixture(self,mutator):
        f=copy.deepcopy(self.fixture)
        mutator(f)
        with self.assertRaises(gate.Rejected):
            gate.validate_fixture(f,self.profile)

    def wrong_source(self,role,path,before,after):
        c=copy.deepcopy(self.sources)
        self.assertIn(before,c[role][path])
        c[role][path]=c[role][path].replace(before,after,1)
        with self.assertRaises(gate.Rejected):
            gate.validate_native_boundary(c)

    def test_01_exact_approved_profile(self):
        self.assertIs(gate.validate_profile(self.profile),self.profile)

    def test_02_exact_18_no_coverage_cases(self):
        self.assertIs(gate.validate_fixture(self.fixture,self.profile),self.fixture)
        self.assertEqual(len(self.fixture["cases"]),18)

    def test_03_actual_source_boundaries(self):
        gate.validate_native_boundary(self.sources)

    def test_04_profile_blob_identity(self):
        raw=(gate.ROOT/"d5a_candidate_v1.json").read_bytes()
        self.assertEqual(gate.git_blob(raw),gate.PROFILE_BLOB)

    def test_05_fixture_blob_identity(self):
        raw=(gate.ROOT/"d5a_fixture_registry_v1.json").read_bytes()
        self.assertEqual(gate.git_blob(raw),gate.FIXTURE_BLOB)

    def test_06_wrong_native_pin(self):
        self.wrong_profile(lambda p:p["pins"].__setitem__("il2cpp_plus",gate.LEGACY_NATIVE))

    def test_07_wrong_hybrid_pin(self):
        self.wrong_profile(lambda p:p["pins"].__setitem__("hybridclr",gate.LEGACY_HYBRID))

    def test_08_wrong_package_pin(self):
        self.wrong_profile(lambda p:p["pins"].__setitem__("hybridclr_unity","0"*40))

    def test_09_d5b_granted_illegally(self):
        self.wrong_profile(lambda p:p["authority"].__setitem__("D5B","Approved"))

    def test_10_local_execution_flag_illegally_enabled(self):
        self.wrong_profile(lambda p:p["authority"].__setitem__("allowUnityOrPlayerExecution",True))

    def test_11_historical_reuse_illegally_enabled(self):
        self.wrong_profile(lambda p:p["historicalReadOnly"].__setitem__("allowHistoricalEvidenceForD5",True))

    def test_12_b1_source_count_modified(self):
        self.wrong_profile(lambda p:p["historicalReadOnly"].__setitem__("oldB1SourceCount",13))

    def test_13_b1_vm_count_modified(self):
        self.wrong_profile(lambda p:p["historicalReadOnly"].__setitem__("oldB1VmDeltaCount",45))

    def test_14_inventory_missing_d4_owner(self):
        def mutate(p):p["sourceGitBlobs"]["il2cpp_plus"].pop("libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h")
        self.wrong_profile(mutate)

    def test_15_native_inventory_untracked_extra(self):
        self.wrong_profile(lambda p:p["sourceGitBlobs"]["il2cpp_plus"].__setitem__("extra.cpp","a"*40))

    def test_16_native_build_roster_includes_host_allocators(self):
        self.wrong_profile(lambda p:p["nativeInstallSources"].append("NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"))

    def test_17_native_install_proof_forged(self):
        self.wrong_profile(lambda p:p.__setitem__("sourceOnlyBuildRosterEvidence","ActualUnityNativeLinked"))

    def test_18_unity_version_changed(self):
        self.wrong_profile(lambda p:p["targetPreview"].__setitem__("unity","2022.3.0f1"))

    def test_19_fake_actual_host(self):
        self.wrong_profile(lambda p:p["targetPreview"].__setitem__("actualHostVerified",True))

    def test_20_dynamic_demo_sha_replaced_by_old_ci(self):
        self.wrong_profile(lambda p:p["pins"].__setitem__("hybridclr_demo","c3307abacaaaec9db2a0f866b726e2ae5df1108b"))

    def test_21_missing_phase_coverage(self):
        self.wrong_fixture(lambda f:f["cases"].pop(9))

    def test_22_duplicate_case(self):
        self.wrong_fixture(lambda f:f["cases"][10].__setitem__("id","D5-C10"))

    def test_23_p5_p6_real_player_claim_forged(self):
        self.wrong_fixture(lambda f:f["cases"][9].__setitem__("d5RealPlayerProof","Passed"))

    def test_24_fake_real_player_link(self):
        self.wrong_fixture(lambda f:f["cases"][8].__setitem__("d5RealPlayerProducerLinked",True))

    def test_25_critical_no_coverage_missing(self):
        self.wrong_fixture(lambda f:f["mandatoryUnproven"].remove("D5-C10"))

    def test_26_unauthenticated_historical_fixture(self):
        self.wrong_fixture(lambda f:f["cases"][0].__setitem__("historicalSource","untracked.cs"))

    def test_27_d4_owner_transfer_removed(self):
        p="libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h"
        self.wrong_source("il2cpp_plus",p,
            "retained_ = std::move(pending);","(void)pending;")

    def test_28_d4_publication_order_reversed(self):
        p="libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h"
        old=("retained_ = std::move(pending); // std::unique_ptr default deleter, noexcept\n"
             "        published.store(retained_.get(), std::memory_order_release);")
        self.wrong_source("il2cpp_plus",p,old,
            "published.store(pending.get(), std::memory_order_release);\n"
            "        retained_ = std::move(pending);")

    def test_29_d3_early_failure_seal_removed(self):
        self.wrong_source("il2cpp_plus","libil2cpp/vm/AssemblyShadow.cpp",
            "SealFailedPublicationBeforeUsageUnlock(publication);",
            "/* removed seal */")

    def test_30_p5_phase_witness_missing(self):
        self.wrong_source("il2cpp_plus","libil2cpp/vm/AssemblyShadow.cpp",
            "publication.phaseReceipt->Advance(\n                assembly_shadow_publication::Phase::ActiveSnapshotPublished)",
            "publication.phaseReceipt->Advance(\n                assembly_shadow_publication::Phase::RuntimeGroupPublished)")

    def test_31_p6_completion_absent(self):
        self.wrong_source("il2cpp_plus","libil2cpp/vm/AssemblyShadow.cpp",
            "if (!publicationPhase.Complete())","if (false)")

    def test_32_p4_real_group_store_missing(self):
        self.wrong_source("hybridclr","hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp",
            "current->groups[group].active.store(1, std::memory_order_release);",
            "current->groups[group].active.store(0, std::memory_order_release);")

    def test_33_old_b1_pins_rewritten(self):
        self.wrong_source("hybridclr_demo","Tools/AssemblyShadow/R03IR/current_native_source_gate.py",
            gate.LEGACY_NATIVE,"f"*40)

    def test_34_old_14_46_profile_bypassed(self):
        self.wrong_source("hybridclr_demo","Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py",
            "== len(source.FILES) == 14","== len(source.FILES) == 0")

    def test_35_real_unity_builder_changed(self):
        self.wrong_source("hybridclr_demo","Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs",
            "BuildPipeline.BuildPlayer(","FakeBuildPipeline.BuildPlayer(")

    def test_36_host_allocators_moved_or_lost(self):
        self.wrong_source("il2cpp_plus","NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp",
            "void* operator new(std::size_t","void* fake_operator_new(std::size_t")

    def test_37_exact_remote_forgery_rejected(self):
        self.assertFalse(gate.canonical_remote("https://github.com/example/hybridclr","hybridclr"))
        self.assertFalse(gate.canonical_remote("https://github.com/night-outlook/hybridclr_demo","hybridclr"))

    def test_38_canonical_https_and_ssh_accepted(self):
        self.assertTrue(gate.canonical_remote("https://github.com/night-outlook/hybridclr.git","hybridclr"))
        self.assertTrue(gate.canonical_remote("git@github.com:night-outlook/hybridclr","hybridclr"))

    def test_39_missing_expected_demo_sha_fails_before_git(self):
        with self.assertRaises(gate.Rejected):
            gate.inspect(self.roots,"")

    def test_40_duplicate_roots_fail_before_git(self):
        roots=dict(self.roots)
        roots["hybridclr"]=roots["hybridclr_demo"]
        with self.assertRaises(gate.Rejected):
            gate.inspect(roots,"a"*40)

    def test_41_source_blob_mismatch_detectable(self):
        path="libil2cpp/vm/AssemblyShadow.cpp"
        actual=(self.roots["il2cpp_plus"]/path).read_bytes()
        self.assertEqual(gate.git_blob(actual),
                         self.profile["sourceGitBlobs"]["il2cpp_plus"][path])
        self.assertNotEqual(gate.git_blob(actual+b"\n"),
                            self.profile["sourceGitBlobs"]["il2cpp_plus"][path])

    def test_42_duplicate_json_keys_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.read_json(b'{"a":1,"a":2}')

    def test_43_evidence_root_within_repo_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.read_only_output_guard(self.roots,
                self.roots["hybridclr_demo"]/"R03-B2-D5-test")

    def test_44_existing_historical_root_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp)
            old=parent/"R03-B2-D5-old"
            old.mkdir()
            with self.assertRaises(gate.Rejected):
                gate.read_only_output_guard(self.roots,old)

    def test_45_clean_synthetic_output_path_checks_only(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate=Path(temp)/"R03-B2-D5-clean-proposed"
            self.assertTrue(gate.read_only_output_guard(self.roots,candidate))
            self.assertFalse(candidate.exists()) # read-only; never created

    def test_46_malformed_source_path_rejected(self):
        self.wrong_profile(lambda p:p["sourceGitBlobs"]["hybridclr"].__setitem__(
            "../../spoof",p["sourceGitBlobs"]["hybridclr"].pop(
                "hybridclr/interpreter/Interpreter_Execute.cpp")))

    def test_47_current_real_source_file_count(self):
        self.assertEqual(sum(gate.COUNTS.values()),33)
        self.assertEqual(sum(len(v) for v in self.sources.values()),33)


if __name__=="__main__":
    unittest.main()
