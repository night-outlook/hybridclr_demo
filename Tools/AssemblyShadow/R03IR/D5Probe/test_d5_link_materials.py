#!/usr/bin/env python3
"""D5-B synthetic material integrity regression tests, NOT Unity/IL2CPP builds."""
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import d5_link_materials as gate

class LinkMaterialSourceOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo=Path(os.environ["R03_D5C10_DEMO_ROOT"]).resolve(strict=True)
        cls.native=Path(os.environ["R03_D5C10_NATIVE_ROOT"]).resolve(strict=True)
        cls.pinset=gate.source_pinset(gate.PINSET.read_bytes())

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name).resolve(strict=True)
        self.installed=self.root/"installed";self.installed.mkdir()
        self.evidence=self.root/"evidence";self.evidence.mkdir()
        self.overlay=self.demo/"Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp"
        self.native_hashes={}
        for name in self.pinset["nativeInstalledSources"]:
            source=self.native/"libil2cpp"/name
            dest=self.installed/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,dest)
            self.native_hashes[name]=gate.sha(dest.read_bytes())
        dest=self.installed/self.pinset["overlayInstallDestination"]
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(self.overlay,dest)
        self.objects={}
        for src in gate.EXPECTED_TUS:
            obj="objects/"+src.rsplit("/",1)[-1]+".o"
            cmd="raw-commands/"+src.rsplit("/",1)[-1]+".txt"
            self._write(obj, b"synthetic-object-binary-"+src.encode())
            self._write(cmd,("clang++ -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 "
                "-DHYBRIDCLR_R03_D5_WINDOW_PROBE=1 -c "+src+" -o "+obj).encode())
            self.objects[src]={"source":src,"object":obj,
                "objectSha256":gate.sha(self._path(obj).read_bytes()),
                "command":cmd}
        self._write("commands/link.txt",
            ("clang++ -shared "+" ".join(x["object"] for x in self.objects.values())+
             " -o linked/GameAssembly.dylib").encode())
        self.binary="linked/GameAssembly.dylib"
        self._write(self.binary, b"\xcf\xfa\xed\xfe"+b"\x00"*128)
        self._write("commands/symbols.txt",
            ("\n".join("00000000 T _"+k for k in gate.EXPORTS)+"\n").encode())
        self.build={
            "schemaVersion":1,"kind":"R03D5C10IsolatedUnityBuildV1",
            "result":"BuildPipelineSucceeded_NotYetBinaryVerified",
            "unityVersion":"2022.3.62f2","featureEnabled":True,
            "cppConfiguration":"Release",
            "actualUnityBuildPipelineInvoked":True,
            "actualUnityBuildReportSucceeded":True,
            "independentLinkedBinaryProof":False,
            "actualD5PlayerRun":False,"R03Accepted":False,
            "nativeCommit":gate.NATIVE,
            "compilerFlags":"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_R03_D5_WINDOW_PROBE=1",
            "requiredNativeFileHashes":[{"path":p,"sha256":v}
                                        for p,v in self.native_hashes.items()],
            "overlayInstalledSha256":gate.sha(self.overlay.read_bytes()),
        }
        self._save_receipt()
        self.envelope={
            "schemaVersion":1,"kind":"R03D5C10LinkMaterialBundleV1",
            "evidenceClass":"SyntheticSourceHost",
            "sourcePins":self.pinset["sourcePins"],
            "buildRole":"ON-Release",
            "target":"macOS-arm64-Unity2022.3.62f2-IL2CPP",
            "buildReceipt":"BUILD_RECEIPT.json",
            "compiledInputs":list(self.objects.values()),
            "linkCommand":"commands/link.txt",
            "linkedBinary":self.binary,
            "linkedBinarySha256":gate.sha(self._path(self.binary).read_bytes()),
            "nmSymbols":"commands/symbols.txt",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _path(self,name):
        return self.evidence/name

    def _write(self,name,content):
        file=self._path(name)
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(content)

    def _save_receipt(self):
        self._write("BUILD_RECEIPT.json",json.dumps(self.build).encode())

    def verify(self):
        return gate.check_submitted_link_material(
            self.evidence,self.native,self.installed,self.overlay,
            self.pinset,self.envelope)

    def rejected(self):
        with self.assertRaises(gate.Rejected):
            self.verify()

    def test_01_valid_proposal_pinset_blob(self):
        self.assertEqual(gate.git_blob(gate.PINSET.read_bytes()),gate.PINSET_BLOB)

    def test_02_preview_explicit_notrun(self):
        r=gate.preview()
        self.assertEqual(r["result"],"SourceOnlyProvenanceContract_NotRun")
        self.assertFalse(r["actualUnityOrIL2CPPExecutionVerified"])
        self.assertFalse(r["realPlayerC10Passed"])

    def test_03_synthetic_bundle_material_only(self):
        r=self.verify()
        self.assertEqual(r["nativeSourcesMatched"],13)
        self.assertEqual(r["compiledInputRecordsMatched"],5)
        self.assertEqual(r["exportSymbolsMatched"],4)
        self.assertFalse(r["realPlayerC10Passed"])
        self.assertFalse(r["actualBeeCompilerCommandExecutionVerified"])

    def test_04_wrong_native_install_hash_rejected(self):
        with (self.installed/"vm/AssemblyShadow.cpp").open("ab") as f:f.write(b"\n")
        self.rejected()

    def test_05_missing_native_d5_header_rejected(self):
        (self.installed/"vm/AssemblyShadowD5WindowProbe.h").unlink()
        self.rejected()

    def test_06_overlay_not_installed_rejected(self):
        (self.installed/"vm/AssemblyShadowD5WindowOverlay.cpp").unlink()
        self.rejected()

    def test_07_overlay_bytes_drift_rejected(self):
        with (self.installed/"vm/AssemblyShadowD5WindowOverlay.cpp").open("ab") as f:
            f.write(b"\n")
        self.rejected()

    def test_08_standalone_allocator_host_excluded(self):
        bad=self.installed/"NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp"
        bad.parent.mkdir(parents=True)
        bad.write_bytes(b"operator new / delete")
        self.rejected()

    def test_09_wrong_build_native_commit_rejected(self):
        self.build["nativeCommit"]="0"*40
        self._save_receipt()
        self.rejected()

    def test_10_builder_must_not_claim_link_proof(self):
        self.build["independentLinkedBinaryProof"]=True
        self._save_receipt()
        self.rejected()

    def test_11_build_receipt_feature_off_not_on(self):
        self.build["featureEnabled"]=False
        self._save_receipt()
        self.rejected()

    def test_12_missing_compiler_object_rejected(self):
        self._path(next(iter(self.objects.values()))["object"]).unlink()
        self.rejected()

    def test_13_mutated_compiler_object_sha_rejected(self):
        with self._path(next(iter(self.objects.values()))["object"]).open("ab") as f:
            f.write(b"malformed")
        self.rejected()

    def test_14_missing_compiler_flags_rejected(self):
        source=self._path(next(iter(self.objects.values()))["command"])
        source.write_text("clang++ -c ignored.cpp",encoding="utf-8")
        self.rejected()

    def test_15_missing_compile_source_record_rejected(self):
        self.envelope["compiledInputs"].pop()
        self.rejected()

    def test_16_missing_link_object_rejected(self):
        self._write("commands/link.txt",b"clang++ -shared -o GameAssembly.dylib")
        self.rejected()

    def test_17_wrong_macho_magic_rejected(self):
        b=self._path(self.binary)
        b.write_bytes(b"not-a-mach-o"+b"x"*128)
        self.envelope["linkedBinarySha256"]=gate.sha(b.read_bytes())
        self.rejected()

    def test_18_wrong_binary_digest_rejected(self):
        self.envelope["linkedBinarySha256"]="f"*64
        self.rejected()

    def test_19_missing_native_exports_rejected(self):
        self._write("commands/symbols.txt",b"000000 T _WrongTestSymbol\n")
        self.rejected()

    def test_20_untrusted_realplayer_class_rejected(self):
        self.envelope["evidenceClass"]="RealUnityPlayer"
        self.rejected()

    def test_21_wrong_source_tuple_rejected(self):
        self.envelope["sourcePins"]=dict(self.envelope["sourcePins"])
        self.envelope["sourcePins"]["il2cpp_plus"]="f"*40
        self.rejected()

    def test_22_symlinked_object_rejected(self):
        obj=next(iter(self.objects.values()))["object"]
        target=self._path(obj)
        target.unlink()
        target.symlink_to(self.native/"libil2cpp/vm/AssemblyShadow.cpp")
        self.rejected()

    def test_23_outside_evidence_path_rejected(self):
        self.envelope["linkedBinary"]="../outside.dylib"
        self.rejected()

    def test_24_reused_build_output_role_rejected(self):
        self.envelope["buildRole"]="OFF-Release"
        self.rejected()

    def test_25_host_allocator_in_link_command_rejected(self):
        p=self._path("commands/link.txt")
        p.write_text(p.read_text()+" NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp")
        self.rejected()


if __name__=="__main__":
    unittest.main()
