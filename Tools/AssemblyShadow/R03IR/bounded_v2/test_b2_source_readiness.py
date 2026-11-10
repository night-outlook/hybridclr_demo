"""Focused negative and expected-BLOCK tests for B2 full field source admission."""
from __future__ import annotations
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_source_readiness as gate

P = "libil2cpp/vm/"

def known_sources():
    return {
        P+"AssemblyShadow.h":
            "TryCaptureBoundedGeneralLive TryCaptureBoundedEmptyExecutionLive "
            "TryReadFirstFailureV2",
        P+"AssemblyShadow.cpp":
            "AssemblyShadow::GetDiagnosticsJson ShadowDiagnosticSnapshot snapshot "
            "AssemblyShadow::GetExecutionDiagnosticsJson std::ostringstream output "
            "FormatMetadataOnly",
        P+"AssemblyShadowBoundedGeneralLiveSource.inl":
            "AssemblyShadow::TryCaptureBoundedGeneralLive "
            "assembly_shadow_metadata_lifetime::Gate::Reader reader "
            "receipt.componentSourcesComplete=true "
            "receipt.observableSourceFenceStable=true "
            "NOT an atomic all-VM epoch",
        P+"AssemblyShadowBoundedExecutionEmptyLiveSource.inl":
            "AssemblyShadow::TryCaptureBoundedEmptyExecutionLive "
            "if(before.count!=0) live::Error::ClassRowsNotSupported "
            "assembly_shadow_metadata_lifetime::Gate::Reader admission",
        P+"AssemblyShadowTypeKey.cpp":
            "std::string FormatType( MetadataDefinitionKey( std::string value "
            "AssemblyShadowTypeKey::FormatMetadataOnly",
        P+"AssemblyShadowMetadataLifetime.h":
            "sourceEpoch initial admitted session class Gate final",
        P+"AssemblyShadowFrozenExecutionRecord.h":
            "class Record final size_t Bytes() const noexcept "
            "bool Complete() const noexcept RejectInvalidSource()",
        P+"AssemblyShadowOwnedPhysicalNamesSource.inl":
            "namesCopiedFromMatchedEnumeratorCallbacks=true "
            "not an execution TypeKey",
    }

REFERENCE = "FIELDS = ('finalDiagnostics', 'finalExecutionDiagnostics')\n"

class SourceReadinessTests(unittest.TestCase):
    def test_01_known_incomplete_source_is_not_published(self):
        result=gate.assess(known_sources(),REFERENCE)
        self.assertEqual(result["sourceAudit"],"PassedPinnedStructuralInspection")
        self.assertEqual((result["field14"],result["field15"]),
                         ("finalDiagnostics","finalExecutionDiagnostics"))
        self.assertFalse(result["readyForNativeV2FieldCapture"])
        self.assertFalse(result["nativeV2TransportImplemented"])
        self.assertEqual(len(result["blockers"]),3)

    def test_02_valid_host_fields_never_upgrade_vm_proof(self):
        f=known_sources()
        f[P+"AssemblyShadow.cpp"]+=" B1 code19/origin2 and first-reason equality "
        self.assertFalse(gate.assess(f,REFERENCE)["readyForNativeV2FieldCapture"])

    def test_03_reordered_or_reduced_schema_rejected(self):
        for sample in (
            "FIELDS = ('finalExecutionDiagnostics','finalDiagnostics')\n",
            "FIELDS = ('finalDiagnostics',)\n",
            "FIELDS = ('firstFailure','finalExecutionDiagnostics')\n",
            "FIELDS = ['finalDiagnostics','finalExecutionDiagnostics']\n",
            "# original schema missing\n",
        ):
            with self.subTest(sample=sample),self.assertRaises(gate.SourceAdmissionError):
                gate.assess(known_sources(),sample)

    def test_04_missing_native_producer_rejected(self):
        for file in gate.NATIVE:
            f=known_sources()
            del f[file]
            with self.subTest(file=file),self.assertRaises(gate.SourceAdmissionError):
                gate.assess(f,REFERENCE)

    def test_05_reject_legacy_execution_allocator_drift(self):
        f=known_sources()
        f[P+"AssemblyShadow.cpp"]=f[P+"AssemblyShadow.cpp"].replace(
            "std::ostringstream output","alternate sink")
        with self.assertRaises(gate.SourceAdmissionError):
            gate.assess(f,REFERENCE)

    def test_06_nonempty_class_rejection_must_remain_visible(self):
        f=known_sources()
        p=P+"AssemblyShadowBoundedExecutionEmptyLiveSource.inl"
        f[p]=f[p].replace("if(before.count!=0)","if(false)")
        with self.assertRaises(gate.SourceAdmissionError):
            gate.assess(f,REFERENCE)

    def test_07_metadata_lifetime_gate_must_remain_visible(self):
        f=known_sources()
        p=P+"AssemblyShadowBoundedGeneralLiveSource.inl"
        f[p]=f[p].replace(
            "assembly_shadow_metadata_lifetime::Gate::Reader reader",
            "arbitrary pointer read")
        with self.assertRaises(gate.SourceAdmissionError):
            gate.assess(f,REFERENCE)

    def test_08_class_display_name_cannot_be_mistaken_for_typekey(self):
        f=known_sources()
        p=P+"AssemblyShadowOwnedPhysicalNamesSource.inl"
        f[p]=f[p].replace("not an execution TypeKey","full canonical TypeKey")
        with self.assertRaises(gate.SourceAdmissionError):
            gate.assess(f,REFERENCE)

    def test_09_drift_of_fence_guard_rejected(self):
        f=known_sources()
        p=P+"AssemblyShadowBoundedGeneralLiveSource.inl"
        f[p]=f[p].replace("receipt.observableSourceFenceStable=true","")
        with self.assertRaises(gate.SourceAdmissionError):
            gate.assess(f,REFERENCE)

    def test_10_git_blob_uses_real_git_header(self):
        raw=b"canonical B2 source\n"
        self.assertEqual(gate.git_blob(raw),
            __import__("hashlib").sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest())
        self.assertNotEqual(gate.git_blob(raw),gate.git_blob(raw+b" "))

    def test_11_pinned_read_rejects_symlink_or_wrong_blob(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"source.cpp").write_text("x")
            with patch.object(gate,"run_git",return_value="100644 blob "+gate.git_blob(b"x")+"\tsource.cpp"):
                with self.assertRaises(gate.SourceAdmissionError):
                    gate.read_pinned(root,"source.cpp","0"*40)
            (root/"link.cpp").symlink_to(root/"source.cpp")
            with self.assertRaises(gate.SourceAdmissionError):
                gate.read_pinned(root,"link.cpp",gate.git_blob(b"x"))

    def test_12_git_tree_missing_or_mixed_commit_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"source.cpp").write_bytes(b"x")
            with patch.object(gate,"run_git",return_value=""):
                with self.assertRaises(gate.SourceAdmissionError):
                    gate.read_pinned(root,"source.cpp",gate.git_blob(b"x"))

if __name__=="__main__":
    unittest.main()
