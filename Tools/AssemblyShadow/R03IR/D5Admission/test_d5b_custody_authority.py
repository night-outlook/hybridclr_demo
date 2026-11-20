#!/usr/bin/env python3
"""D5-B Primary-only admission contracts; no Unity, no Local-run authorizations."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

import d5b_custody_authority as gate


class D5BSourceCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native_root=Path(os.environ["R03_D5B_NATIVE_ROOT"]).resolve(strict=True)
        cls.demo_root=Path(os.environ["R03_D5B_DEMO_ROOT"]).resolve(strict=True)
        cls.proposal=gate.require_proposal(gate.read_json(gate.PREP_FILE.read_bytes()))
        profile=cls.demo_root/"Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json"
        cls.d5a_manifest=gate.read_json(profile.read_bytes())
        cls.native_blobs = {
            name:cls.d5a_manifest["sourceGitBlobs"]["il2cpp_plus"][name]
            for name in gate.NATIVE
        }

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        t=Path(self.tmp.name).resolve(strict=True)
        self.workspace=t/"workspace";self.workspace.mkdir()
        self.roots={}
        for role in gate.ROLES:
            root=self.workspace/role;root.mkdir()
            self.roots[role]=root
        self.history={}
        self.history["originalS"]=t/"originalS"
        self.history["originalS"].mkdir()
        base=self.workspace/"old-evidence"
        base.mkdir()
        self.history["b1EvidenceBase"]=base
        for role,stem in (
            ("b1Oneuse12","oneuse-12"),
            ("b1NativeHostRaw","oneuse-12-native-host-raw"),
            ("b1B2HostRaw","oneuse-12-b2-host-raw"),
            ("b1Preflight","Preflight-NativeB1-12")):
            node=base/stem;node.mkdir()
            self.history[role]=node
        self.evidence=t/"new-evidence";self.evidence.mkdir()
        self.name="R03-B2-D5-review-only-001"

    def tearDown(self):
        self.tmp.cleanup()

    def rejected_proposal(self,mutate):
        x=copy.deepcopy(self.proposal)
        mutate(x)
        with self.assertRaises(gate.Rejected):
            gate.require_proposal(x)

    def custody(self,**override):
        opts={
            "workspace":self.workspace,"roots":self.roots,
            "historical_roots":self.history,
            "evidence_parent":self.evidence,"oneuse_name":self.name,
        }
        opts.update(override)
        return gate.check_proposed_custody(**opts)

    def test_01_exact_proposal_source_blob(self):
        self.assertEqual(gate.git_blob(gate.PREP_FILE.read_bytes()),gate.PREP_BLOB)

    def test_02_exact_proposal_contract(self):
        self.assertIs(gate.require_proposal(self.proposal),self.proposal)

    def test_03_preview_is_not_local_authority(self):
        r=gate.preview(gate.PREP_FILE)
        self.assertEqual(r["result"],"PreparedSourceOnly_NoLocalExecution")
        self.assertEqual(r["D5BLocalExecution"],"NotAuthorized")
        self.assertEqual(r["realPlayerCellsNoCoverage"],18)
        self.assertEqual(r["nativeUnityInstallation"],"NotRun")

    def test_04_fake_local_approval_rejected(self):
        self.rejected_proposal(lambda x:x["authority"].__setitem__("D5BLocalExecution","Approved"))

    def test_05_fake_approved_handoff_rejected(self):
        self.rejected_proposal(lambda x:x["reviewedHandoff"].__setitem__("status","ReadyForLocal"))

    def test_06_demo_review_baseline_does_not_become_latest(self):
        self.rejected_proposal(lambda x:x["sourceAuthority"].__setitem__("demoBaselineRole","LatestRemote"))

    def test_07_wrong_native_pin(self):
        self.rejected_proposal(lambda x:x["sourceAuthority"].__setitem__("il2cpp_plus","0"*40))

    def test_08_wrong_package_pin(self):
        self.rejected_proposal(lambda x:x["sourceAuthority"].__setitem__("hybridclr_unity","0"*40))

    def test_09_missing_history_role(self):
        self.rejected_proposal(lambda x:x["historicalRootRoles"].remove("b1Oneuse12"))

    def test_10_unreviewed_native_input(self):
        self.rejected_proposal(lambda x:x["requiredNativeInputs"].append(gate.BAD_HOST))

    def test_11_allow_creation_during_preview_rejected(self):
        self.rejected_proposal(lambda x:x["evidenceRoot"].__setitem__("createOrReserve",True))

    def test_12_player_coverage_fabrication_rejected(self):
        self.rejected_proposal(lambda x:x["testCoverage"].__setitem__("D5PlayerCasesCompleted",1))

    def test_13_duplicate_json_keys_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.read_json(b'{"a":1,"a":2}')

    def test_14_complete_history_read_only_candidate(self):
        r=self.custody()
        self.assertEqual(r["historicalRootCount"],len(gate.HISTORY))
        self.assertFalse(r["outputCreated"])
        self.assertFalse((self.evidence/self.name).exists())
        self.assertEqual(r["D5BLocalExecution"],"NotAuthorized")

    def test_15_missing_history_key_fail_closed(self):
        h=dict(self.history);h.pop("b1Oneuse12")
        with self.assertRaises(gate.Rejected):
            self.custody(historical_roots=h)

    def test_16_new_child_under_old_b1_base_rejected(self):
        parent=self.history["b1EvidenceBase"]/"unconsumed"
        parent.mkdir()
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=parent)

    def test_17_new_child_under_old_oneuse_rejected(self):
        parent=self.history["b1Oneuse12"]/"subdirectory"
        parent.mkdir()
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=parent)

    def test_18_new_child_under_original_s_rejected(self):
        parent=self.history["originalS"]/"subdirectory"
        parent.mkdir()
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=parent)

    def test_19_source_workspace_root_rejected(self):
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=self.workspace)

    def test_20_source_child_repo_rejected(self):
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=self.roots["il2cpp_plus"])

    def test_21_existing_consumed_output_rejected(self):
        (self.evidence/self.name).mkdir()
        with self.assertRaises(gate.Rejected):
            self.custody()

    def test_22_symlinked_evidence_parent_rejected(self):
        alias=self.workspace.parent/"symlink-parent"
        alias.symlink_to(self.evidence,target_is_directory=True)
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=alias)

    def test_23_symlinked_leaf_rejected(self):
        (self.evidence/self.name).symlink_to(self.history["b1Oneuse12"],target_is_directory=True)
        with self.assertRaises(gate.Rejected):
            self.custody()

    def test_24_output_traversal_rejected(self):
        with self.assertRaises(gate.Rejected):
            self.custody(oneuse_name="../R03-B2-D5-new")

    def test_25_too_short_oneuse_name_rejected(self):
        with self.assertRaises(gate.Rejected):
            self.custody(oneuse_name="R03-B2-D5-")

    def test_26_duplicate_source_root_rejected(self):
        r=dict(self.roots);r["hybridclr"]=r["il2cpp_plus"]
        with self.assertRaises(gate.Rejected):
            self.custody(roots=r)

    def test_27_wrong_historical_b1_relationship_rejected(self):
        h=dict(self.history)
        h["b1Oneuse12"]=self.evidence
        with self.assertRaises(gate.Rejected):
            self.custody(historical_roots=h)

    def test_28_canonical_physical_path_required(self):
        with self.assertRaises(gate.Rejected):
            self.custody(evidence_parent=Path(str(self.evidence)+"/../new-evidence"))

    def test_29_full_reviewed_remote_ref_accepted(self):
        sha="a"*40
        self.assertEqual(gate.parse_remote_ref(
            sha+"\trefs/heads/"+gate.BRANCH,sha),sha)

    def test_30_stale_remote_branch_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.parse_remote_ref("b"*40+"\trefs/heads/"+gate.BRANCH,"a"*40)

    def test_31_wrong_ref_name_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.parse_remote_ref("a"*40+"\trefs/heads/main","a"*40)

    def test_32_duplicate_remote_ref_lines_rejected(self):
        line="a"*40+"\trefs/heads/"+gate.BRANCH
        with self.assertRaises(gate.Rejected):
            gate.parse_remote_ref(line+"\n"+line,"a"*40)

    def test_33_non_full_sha_rejected(self):
        with self.assertRaises(gate.Rejected):
            gate.parse_remote_ref("abcdef\trefs/heads/"+gate.BRANCH,"a"*40)

    def test_34_unapproved_handoff_cannot_verify_live_source(self):
        self.assertIsNone(gate.APPROVED_LOCAL_HANDOFF_BLOB)
        with self.assertRaises(gate.Rejected):
            gate.verify_live_source_heads(self.roots,{
                "hybridclr_demo":"a"*40,**gate.PINNED})

    def test_35_exact_remote_url_policy(self):
        self.assertTrue(gate.canonical_remote(
            "https://github.com/night-outlook/hybridclr.git","hybridclr"))
        self.assertFalse(gate.canonical_remote(
            "https://github.com/unrelated/hybridclr","hybridclr"))

    def _copied_native(self):
        copied=self.workspace.parent/"native-copy"
        copied.mkdir()
        for name in gate.NATIVE:
            original=self.native_root/name
            dest=copied/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original,dest)
        return copied

    def test_36_synthetic_native_file_copy_only(self):
        copied=self._copied_native()
        r=gate.check_native_file_copy(self.native_root,copied,self.native_blobs)
        self.assertEqual(r["nativeFilesAuthenticated"],12)
        self.assertFalse(r["actualBeeCompilerInvoked"])
        self.assertFalse(r["actualPlayerLinked"])
        self.assertEqual(r["compiledTranslationUnits"],0)

    def test_37_native_copy_missing_required_header(self):
        copied=self._copied_native()
        (copied/"libil2cpp/vm/AssemblyShadowProcessSnapshotOwner.h").unlink()
        with self.assertRaises(gate.Rejected):
            gate.check_native_file_copy(self.native_root,copied,self.native_blobs)

    def test_38_native_copy_mutated_source_rejected(self):
        copied=self._copied_native()
        source=copied/"libil2cpp/vm/AssemblyShadow.cpp"
        source.write_bytes(source.read_bytes()+b"\n// modified")
        with self.assertRaises(gate.Rejected):
            gate.check_native_file_copy(self.native_root,copied,self.native_blobs)

    def test_39_native_copy_unreviewed_blob_rejected(self):
        copied=self._copied_native()
        altered=dict(self.native_blobs)
        altered["libil2cpp/vm/AssemblyShadow.cpp"]="f"*40
        with self.assertRaises(gate.Rejected):
            gate.check_native_file_copy(self.native_root,copied,altered)

    def test_40_native_copy_host_allocator_excluded(self):
        copied=self._copied_native()
        driver=copied/gate.BAD_HOST
        driver.parent.mkdir(parents=True)
        driver.write_bytes(b"global new/delete test")
        with self.assertRaises(gate.Rejected):
            gate.check_native_file_copy(self.native_root,copied,self.native_blobs)

    def test_41_native_copy_symlink_rejected(self):
        copied=self._copied_native()
        target=copied/"libil2cpp/vm/AssemblyShadow.cpp"
        target.unlink()
        target.symlink_to(self.native_root/"libil2cpp/vm/AssemblyShadow.cpp")
        with self.assertRaises(gate.Rejected):
            gate.check_native_file_copy(self.native_root,copied,self.native_blobs)

    def test_42_required_compiled_units_are_a_subset(self):
        self.assertEqual(len(gate.NATIVE),12)
        self.assertTrue(set(gate.TRANSLATION_UNITS).issubset(gate.NATIVE))
        self.assertNotIn(gate.BAD_HOST,gate.NATIVE)

    def test_43_no_local_approval_can_be_claimed_by_preview(self):
        a=gate.preview(gate.PREP_FILE)
        self.assertNotIn("LocalValidationPassed",str(a))
        self.assertEqual(a["remoteSourceVerification"],"NotRun")
        self.assertEqual(a["historicalRootAdmission"],"NotRun")


    def _synthetic_handoff_bytes(self, transform=None):
        record={
            "schemaVersion":1,
            "kind":"R03B2D5BReviewedLocalHandoffV1",
            "branch":gate.BRANCH,
            "independentReview":"Passed",
            "userD5BExecutionApproval":"ExplicitlyApproved",
            "WEB_TO_LOCAL":"OPEN_FOR_EXACT_D5B_LOCAL_ONLY",
            "sourcePins":{"hybridclr_demo":"b9776f7dc87170ba08bfed9021c0ee8546bceccf",
                          **gate.PINNED},
            "historicalRoots":{k:str(v) for k,v in self.history.items()},
        }
        if transform:
            transform(record)
        return json.dumps(record,sort_keys=True).encode("utf-8")

    def test_44_unapproved_live_handoff_fails_closed(self):
        with self.assertRaises(gate.Rejected):
            gate.read_independently_approved_handoff(self._synthetic_handoff_bytes())

    def test_45_synthetic_frozen_reviewed_blob_is_required(self):
        raw=self._synthetic_handoff_bytes()
        # TEST-ONLY fake approval anchor. Production anchor remains None.
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)):
            r=gate.read_independently_approved_handoff(raw)
        self.assertEqual(len(r["sourcePins"]),4)
        self.assertIsNone(gate.APPROVED_LOCAL_HANDOFF_BLOB)

    def test_46_changed_approved_bytes_rejected(self):
        raw=self._synthetic_handoff_bytes()
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.read_independently_approved_handoff(raw+b" ")

    def test_47_wrong_native_approved_pin_rejected(self):
        raw=self._synthetic_handoff_bytes(
            lambda obj:obj["sourcePins"].__setitem__("il2cpp_plus","a"*40))
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.read_independently_approved_handoff(raw)

    def test_48_missing_approved_history_roots_rejected(self):
        raw=self._synthetic_handoff_bytes(
            lambda obj:obj["historicalRoots"].pop("b1Oneuse12"))
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)):
            with self.assertRaises(gate.Rejected):
                gate.read_independently_approved_handoff(raw)

    def _simulated_remote(self,stale_demo=False):
        pins={"hybridclr_demo":"b9776f7dc87170ba08bfed9021c0ee8546bceccf",
              **gate.PINNED}
        calls=[]
        def read(root,*args):
            role=root.name
            calls.append((role,args))
            if args==("rev-parse","--show-toplevel"):
                return str(root)
            if args==("rev-parse","HEAD"):
                return pins[role]
            if args==("remote","get-url","origin"):
                return "https://github.com/night-outlook/"+role+".git"
            if args==("status","--porcelain=v1","--untracked-files=all"):
                return ""
            if args==("ls-remote","--exit-code","origin","refs/heads/"+gate.BRANCH):
                remote=pins[role]
                if stale_demo and role=="hybridclr_demo":
                    remote="a"*40
                return remote+"\trefs/heads/"+gate.BRANCH
            raise AssertionError("Unexpected Git call: "+str((root,args)))
        return read,calls

    def test_49_synthetic_remote_check_reads_four_exact_branch_refs(self):
        raw=self._synthetic_handoff_bytes()
        git,calls=self._simulated_remote()
        # Test mocks are not a real GitHub branch readback or Local admission.
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)), \
             mock.patch.object(gate,"run_git",side_effect=git):
            out=gate.verify_live_source_heads(self.roots,raw)
        self.assertEqual(len(out),4)
        self.assertTrue(all(v["remoteBranchMatched"] for v in out.values()))
        self.assertEqual(sum(args[0]=="ls-remote" for _,args in calls),4)
        self.assertIsNone(gate.APPROVED_LOCAL_HANDOFF_BLOB)

    def test_50_synthetic_stale_demo_remote_ref_is_rejected(self):
        raw=self._synthetic_handoff_bytes()
        git,calls=self._simulated_remote(stale_demo=True)
        with mock.patch.object(gate,"APPROVED_LOCAL_HANDOFF_BLOB",gate.git_blob(raw)), \
             mock.patch.object(gate,"run_git",side_effect=git):
            with self.assertRaises(gate.Rejected):
                gate.verify_live_source_heads(self.roots,raw)
        self.assertTrue(any(role=="hybridclr_demo" and
                            args[0]=="ls-remote" for role,args in calls))


if __name__=="__main__":
    unittest.main()
