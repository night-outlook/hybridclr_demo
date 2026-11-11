"""Negative and exact-source admission contract tests, no Unity required."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import b2_definition_source_gate as audit

HERE=Path(__file__).resolve().parent
class SourceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((HERE/"b2_definition_native_candidate.json").read_text())

    def test_manifest_is_pinned_but_explicitly_not_v2(self):
        audit.validate_contract(self.original)
        self.assertFalse(self.original["runtimeAcceptance"])
        self.assertFalse(self.original["readyForNativeV2FieldCapture"])

    def test_product_promotions_all_rejected(self):
        for key in ("runtimeAcceptance","R03Accepted","H2Passed",
                    "ReadyForHumanReviewGate","nativeV2TransportImplemented",
                    "readyForNativeV2FieldCapture"):
            changed=copy.deepcopy(self.original);changed[key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_wrong_branch_and_handoff_authority_rejected(self):
        for key,value in (("branch","main"),
                          ("handoffAuthority","OpenForLocal"),
                          ("candidateNative","0"*39+"g"),
                          ("originalB1Native","bad")):
            changed=copy.deepcopy(self.original);changed[key]=value
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_missing_or_added_source_is_rejected(self):
        for key in ("nativeSources","demoPureSources"):
            for mutation in ("pop","duplicate"):
                changed=copy.deepcopy(self.original)
                if mutation=="pop":changed[key].pop()
                else:changed[key].append(copy.deepcopy(changed[key][0]))
                with self.subTest(key=key,mutation=mutation),self.assertRaises(audit.Rejected):
                    audit.validate_contract(changed)

    def test_source_roster_wrong_blob_shape(self):
        changed=copy.deepcopy(self.original)
        changed["nativeSources"][0]["gitBlob"]="hello"
        with self.assertRaises(audit.Rejected):
            audit.validate_contract(changed)
        # Format is checked on the actual file; invalid blob cannot be admitted.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            (root/"sample").write_bytes(b"a")
            with self.assertRaises(audit.Rejected):
                audit.verify_file(root,"sample","hello")

    def test_actual_git_blob_header(self):
        raw=b"physical-native-source"
        expected=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
        self.assertEqual(audit.blob(raw),expected)
        self.assertNotEqual(audit.blob(raw),audit.blob(raw+b" "))

    def test_tree_sha_and_content_must_both_match(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve();(root/"x.h").write_bytes(b"data")
            digest=audit.blob(b"data")
            with patch.object(audit,"git",return_value="100644 blob "+digest+"\tx.h"):
                self.assertEqual(audit.verify_file(root,"x.h",digest),b"data")
            with patch.object(audit,"git",return_value=""):
                with self.assertRaises(audit.Rejected):
                    audit.verify_file(root,"x.h",digest)

    def test_symlink_alias_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            (root/"real").write_bytes(b"data")
            (root/"link").symlink_to(root/"real")
            with self.assertRaises(audit.Rejected):
                audit.verify_file(root,"link",audit.blob(b"data"))

    def test_unsafe_paths_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            for unsafe in ("../escape","/absolute","some/../escape","bad"+chr(0)+"path"):
                with self.subTest(unsafe=repr(unsafe)),self.assertRaises(audit.Rejected):
                    audit.verify_file(root,unsafe,"0"*40)

    def test_structural_source_drift_is_rejected(self):
        snippets={p: b"" for p in audit.NATIVE_REQUIRED}
        with self.assertRaises(audit.Rejected):
            audit.source_boundary(snippets)

    def test_historical_four_repo_pins_are_frozen(self):
        for key in ("originalB1ExecutionDemo","originalB1Native",
                    "hybridclr","hybridclr_unity"):
            changed=copy.deepcopy(self.original)
            changed[key]="0"*40
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_terminal_and_epoch_capabilities_cannot_be_promoted(self):
        for key in ("sourceReadsAfterTerminal",
                    "arbitraryGenericInstantiationTypeKeys",
                    "crossImageGenericArgumentsSupported",
                    "realUnityRuntimeIntegrationProven",
                    "coherentVmEpochProven"):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][key]=True
            with self.subTest(key=key),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_generic_source_limits_cannot_be_relaxed(self):
        for field,bad in (("genericArgumentLimit",17),
                          ("genericOwnedOutputByteLimit",8192),
                          ("legacyTypeKeyGrammarSourceBlob","0"*40),
                          ("realGenericRuntimeMetadataAbiBlob","0"*40)):
            changed=copy.deepcopy(self.original)
            changed["nativeSourceCapabilities"][field]=bad
            with self.subTest(field=field),self.assertRaises(audit.Rejected):
                audit.validate_contract(changed)

    def test_no_execution_authority_transmitted(self):
        self.assertEqual(self.original["handoffAuthority"],"CLOSED_NO_LOCAL_EXECUTION")
        self.assertEqual(self.original["nativeSourceCapabilities"]["sourceReadsAfterTerminal"],False)

if __name__=="__main__":
    unittest.main()
