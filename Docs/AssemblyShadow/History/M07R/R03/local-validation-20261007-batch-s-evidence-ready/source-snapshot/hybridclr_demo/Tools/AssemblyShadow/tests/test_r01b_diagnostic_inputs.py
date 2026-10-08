"""Synthetic byte/provenance checks; these do not claim diagnostic Player execution."""
import copy
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import r01b_diagnostic_inputs as gate
from shadow_tools import VerificationError
from test_m04_results import make_pe


def with_debug(data, guid_byte=0x12, stamp=2):
    image=bytearray(data); directory=640; payload=700
    codeview=b'RSDS'+bytes([guid_byte])*16+struct.pack('<I',1)+b'/src/Fixture.pdb\0'
    struct.pack_into('<II',image,0x98+96+6*8,0x2000+directory-512,28)
    struct.pack_into('<IIHHIIII',image,directory,0,stamp,0,0,2,len(codeview),0x2000+payload-512,payload)
    image[payload:payload+len(codeview)]=codeview
    return bytes(image)


class DiagnosticByteProofTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.regular=self.root/'regular.dll';self.diag=self.root/'diag.dll'
    def tearDown(self):self.temp.cleanup()
    def verify(self,left,right):
        self.regular.write_bytes(left);self.diag.write_bytes(right)
        return gate.verify_compatible_dll(self.regular,self.diag,'fixture')
    def test_identical_bytes(self):
        data=make_pe();self.assertEqual(self.verify(data,data)['policy'],'ExactDllBytes')
    def test_only_mvid_and_pe_provenance_can_differ(self):
        for wide in (False,True):
            a=make_pe(wide=wide);b=bytearray(make_pe(mvid=uuid.UUID('12345678-1234-4234-9234-123456789abc'),wide=wide))
            struct.pack_into('<I',b,0x80+8,777);struct.pack_into('<I',b,0x98+64,888)
            self.assertEqual(self.verify(a,bytes(b))['policy'],'ExactRuntimeBytesExceptPeProvenanceV1')
    def test_actual_debug_directory_ranges_are_bound(self):
        a=with_debug(make_pe());b=with_debug(make_pe(mvid=uuid.UUID('12345678-1234-4234-9234-123456789abc')),0x34,45)
        self.verify(a,b)
        bad=bytearray(b);struct.pack_into('<I',bad,640+24,704)
        with self.assertRaises(VerificationError):self.verify(a,bytes(bad))
        bad=bytearray(b);struct.pack_into('<I',bad,640+12,17)
        with self.assertRaises(VerificationError):self.verify(a,bytes(bad))
    def test_other_runtime_and_metadata_bytes_fail(self):
        a=make_pe()
        for change in ('padding','identity','references','extraBytes'):
            if change=='padding':b=bytearray(a);b[600]=99;b=bytes(b)
            elif change=='identity':b=make_pe(version=(1,2,3,5))
            elif change=='references':b=make_pe(refs=[dict(name='Other')])
            else:b=a+b'\0'
            with self.subTest(change=change),self.assertRaises(VerificationError):self.verify(a,b)
    def test_corrupt_pe_and_symlink_fail(self):
        with self.assertRaises(VerificationError):self.verify(make_pe(),b'not-pe')
        self.regular.write_bytes(make_pe());self.diag.unlink();self.diag.symlink_to(self.regular)
        with self.assertRaises(VerificationError):gate.verify_compatible_dll(self.regular,self.diag,'symlink')


class DiagnosticReceiptTests(unittest.TestCase):
    def setUp(self):
        import json
        from shadow_tools import PINS
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.source=self.root/PINS;self.source.parent.mkdir(parents=True)
        pins=dict(schemaVersion=1,demo=dict(revision='1'*40))
        self.source.write_text(json.dumps(pins))
        self.fixture=self.root/'fixture.json';self.fixture.write_text('{}')
        self.on=self.root/'on.json';self.on.write_text('{}')
        baseline=dict(baselineBuildId='baseline',runtimeAbiHash='a'*64,unityVersion='2022.3.62f2',target='StandaloneOSX',architecture='arm64')
        self.context=dict(baseline=baseline,sourcePins=pins,manifest={'_path':str(self.fixture)},
            on=dict(path=self.on,player=dict(buildGuid='00112233-4455-4677-8899-aabbccddeeff'),snapshot=dict(extraScriptingDefines=['BOUND'])),
            off=dict(player=dict(buildGuid='00112233-4455-4677-8899-aabbccddeeaa'),snapshot=dict(extraScriptingDefines=['BOUND'])))
        value={key:'' for key in gate.RECEIPT_FIELDS.split()}
        value.update(baseline,schemaVersion=1,nativeMetadataVersion=31,diagnosticOnly=True,productionPolicyAdmission=False,
            kind='R01BDiagnosticPlayerBuild',milestone='R01B',uniqueGuid='1'*32,
            buildGuid='12345678-1234-4234-9234-123456789abc',diagnosticAssemblyName=gate.DIAGNOSTIC_ASSEMBLY,
            nativeArguments=gate.NATIVE_ARGUMENTS,scenes=[gate.DIAGNOSTIC_SCENE,'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity'],
            extraScriptingDefines=['BOUND',gate.DIAGNOSTIC_DEFINE],linkedInputNames=[],linkedInputSha256=[],assemblyIdentities=[],
            nativeAssemblyIdentities=[],nativeGeneratedAssemblyNames=[],regularFixtureManifestPath=str(self.fixture),
            regularFixtureManifestSha256=gate.digest(self.fixture),regularPlayerReceiptPath=str(self.on),regularPlayerReceiptSha256=gate.digest(self.on),
            sourcePinFile=str(self.source),sourcePinSha256=gate.digest(self.source),sourcePinsJson=json.dumps(pins),note='Diagnostic only.')
        self.value=value
    def tearDown(self):self.temp.cleanup()
    def check(self,value):gate._verify_receipt_header(value,self.context,self.root,self.root/'receipt.json')
    def test_exact_receipt_and_separate_production_context(self):
        before=copy.deepcopy(self.context);self.check(self.value);self.assertEqual(self.context,before)
    def test_unknown_missing_and_production_claims_rejected(self):
        for key,val in [('unexpected',True),('productionPolicyAdmission',True),('diagnosticOnly',False),('kind','M07'),
                        ('buildGuid',self.context['on']['player']['buildGuid']),('sourcePinsJson','{}'),
                        ('extraScriptingDefines',['BOUND']),('nativeArguments','off'),('diagnosticAssemblyName','AssemblyShadowDemo.Bootstrap')]:
            with self.subTest(key=key),self.assertRaises(VerificationError):self.check(dict(self.value,**{key:val}))
        value=dict(self.value);del value['productionPolicyAdmission']
        with self.assertRaises(VerificationError):self.check(value)
    def test_regular_binding_and_current_pins_hashes_are_not_advisory(self):
        for key in ('sourcePinSha256','regularFixtureManifestSha256','regularPlayerReceiptSha256'):
            with self.subTest(key=key),self.assertRaises(VerificationError):self.check(dict(self.value,**{key:'0'*64}))
        self.context['off']['snapshot']['extraScriptingDefines'].append(gate.DIAGNOSTIC_DEFINE)
        with self.assertRaises(VerificationError):self.check(self.value)
    def test_builder_dto_field_inventory_matches_verifier(self):
        import re
        source=(Path(__file__).resolve().parents[3]/'Assets/AssemblyShadowDemo/Editor/R01BDiagnosticBuild.cs').read_text()
        dto=source.split('public sealed class DiagnosticBuildReceipt')[1]
        fields=[]
        for declaration in re.findall(r'public [\w\[\]]+ ([\w, ]+);',dto):
            fields.extend(item.strip() for item in declaration.split(','))
        self.assertEqual(set(fields),set(gate.RECEIPT_FIELDS.split()))
    def test_inventory_binds_capture_linked_and_application(self):
        root=self.root/'capture';root.mkdir();linked=root/'LinkedPlayer';linked.mkdir()
        app=self.root/'diagnostic.app';app.mkdir();receipt=self.root/'receipt.json';receipt.write_text('{}')
        files=[root/'assembly-snapshot.json',linked/'test.dll',app/'executable']
        for f in files:f.write_bytes(b'input')
        context={'diagnostic':dict(path=receipt,root=root,output=app)}
        self.assertEqual(gate.collect_diagnostic_inputs(context),set(files+[receipt]))
        (app/'alias').symlink_to(files[0])
        with self.assertRaises(VerificationError):gate.collect_diagnostic_inputs(context)


if __name__=='__main__':unittest.main()
