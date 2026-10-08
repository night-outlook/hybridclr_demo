"""Adversarial sidecar/transport contracts using explicitly synthetic JSON.

Actual metadata resolution has separate real-DLL tests. These fake receipts
exercise rejection behavior only; they never establish an actual Unity proof.
"""
import copy
import tempfile
import unittest
from pathlib import Path
import layout_identity as identity
import layout_evidence as evidence
from batch_contract import ContractError


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.li_name = 'mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'
        self.app = 'App, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'
        self.n = identity.NETSTANDARD
        self.base = {'snapshotHash':'1'*64,'linkedPlayerReceiptHash':'2'*64,'nativeLibrarySha256':'3'*64,
                     'linkedPlayerReceipt':{'reflectionBindingEvidenceHash':'4'*64},'buildGuid':'b'*32,
                     'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64'}
        self.target = dict(self.base,snapshotHash='5'*64, references=[{'name':'netstandard','sha256':'6'*64}],
                           assemblies=[{'name':'app','sha256':'7'*64}])
        self.proof = {'facadeSha256':'8'*64,'facadePath':identity.FACADE,'buildGuid':'b'*32,'mappingPolicyVersion':1,
                      'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',
                      'forwarders':[{'typeFullName':'System.Object','destinationAssemblyIdentity':self.li_name}]}
        self.linked=[{'path':'/synthetic/app.dll','sha256':'9'*64},{'path':'/synthetic/mscorlib.dll','sha256':'a'*64}]
        self.compiler=[{'path':'/synthetic/App.dll','sha256':'7'*64},{'path':'/synthetic/netstandard.dll','sha256':'6'*64}]
        def image(name,digest):return {'assemblyIdentity':name,'sha256':digest,'mvid':'11111111-2222-3333-4444-555555555555'}
        decl=identity.key_token('System')+identity.key_token('1')+identity.key_token('Object')
        def resolved(origin,digest,path,mapped):return {'declaredAssemblyIdentity':origin,'declaration':decl,
                'definitionAssemblyIdentity':self.li_name,'declaredModuleSha256':digest,'definitionModuleSha256':'a'*64,
                'canonicalKey':identity.key_token(self.li_name)+identity.key_token(decl),'forwardingPath':path,'runtimeFacadeUsed':mapped}
        er={'profile':identity.PROFILE,'targetFrameworkProvenanceHash':'c'*64,'linkedRetargetingEvidenceHash':'4'*64,
            'runtimeFacadeSha256':'8'*64,'compilerFacadeSha256':'6'*64,
            'linkedInventory':[image(self.app,'9'*64),image(self.li_name,'a'*64)],
            'compilerInventory':[image(self.app,'7'*64),image(self.n,'6'*64)],
            'linkedResolutions':[resolved(self.li_name,'a'*64,[self.li_name+' | sha256='+'a'*64],False)],
            'compilerResolutions':[resolved(self.n,'6'*64,[self.n+' | sha256='+'6'*64,self.n+' | runtime-facade='+'8'*64,self.li_name+' | sha256='+'a'*64],True)]}
        self.value={'schemaVersion':2,'profile':'NativeLayoutAdmissionV1','inputBasis':'LinkedPlayer','nativeProofExecuted':False,
                    'runtimeMustRevalidate':True,'pureInterpreterExpansionEnabled':False,'baselineSnapshotHash':'1'*64,
                    'linkedPlayerReceiptHash':'2'*64,'baselineNativeLibrarySha256':'3'*64,'targetSnapshotHash':'5'*64,
                    'targetLoadOrder':['app'],'identityEvidence':er,'assemblies':[{'schemaVersion':2,'profile':'NativeLayoutAdmissionV1',
                    'assembly':'App','baselineDllSha256':'9'*64,'targetDllSha256':'7'*64,'editorAccepted':True,
                    'nativeProofExecuted':False,'allocationProofStillRequired':True,'pureInterpreterExpansionEnabled':False,
                    'types':[{'typeKey':'app:Type','decision':'NeedsNativeProof','reasons':['Native proof still required']}]}]}

    def check(self):
        return evidence.verify_value(self.value,self.base,self.target,self.linked,self.compiler,self.proof,'4'*64,'8'*64,['app'])

    def test_synthetic_positive_requires_native_revalidation(self):
        result=self.check();self.assertFalse(result['nativeProofExecuted']);self.assertEqual(result['mappedDeclarations'],1)
    def test_old_schema_rejected(self):
        self.value['schemaVersion']=1
        with self.assertRaises(ContractError):self.check()
    def test_runtime_authority_not_raised(self):
        for key,val in [('nativeProofExecuted',True),('runtimeMustRevalidate',False),('pureInterpreterExpansionEnabled',True)]:
            with self.subTest(key=key):
                old=self.value[key];self.value[key]=val
                with self.assertRaises(ContractError):self.check()
                self.value[key]=old
    def test_exact_source_hashes(self):
        for key in ['baselineSnapshotHash','linkedPlayerReceiptHash','baselineNativeLibrarySha256','targetSnapshotHash']:
            with self.subTest(key=key):
                old=self.value[key];self.value[key]='0'*64
                with self.assertRaises(ContractError):self.check()
                self.value[key]=old
    def test_order_not_replaced(self):
        self.value['targetLoadOrder']=['other']
        with self.assertRaises(ContractError):self.check()
    def test_exact_retargeting_proof(self):
        self.value['identityEvidence']['linkedRetargetingEvidenceHash']='0'*64
        with self.assertRaises(ContractError):self.check()
    def test_facade_bytes_not_rebound(self):
        self.value['identityEvidence']['runtimeFacadeSha256']='0'*64
        with self.assertRaises(ContractError):self.check()
    def test_facade_path_not_selectable(self):
        self.proof['facadePath']='some/other.dll'
        with self.assertRaises(ContractError):self.check()
    def test_build_guid_binding(self):
        self.proof['buildGuid']='0'*32
        with self.assertRaises(ContractError):self.check()
    def test_target_architecture_binding(self):
        self.target['architecture']='x64'
        with self.assertRaises(ContractError):self.check()
    def test_framework_provenance_required(self):
        self.value['identityEvidence']['targetFrameworkProvenanceHash']=''
        with self.assertRaises(ContractError):self.check()
    def test_compiler_facade_must_be_reference(self):
        self.target['references']=[]
        with self.assertRaises(ContractError):self.check()
    def test_compiler_facade_full_identity(self):
        self.value['identityEvidence']['compilerInventory'][1]['assemblyIdentity']='netstandard, Version=9.0.0.0'
        with self.assertRaises(ContractError):self.check()
    def test_inventory_complete(self):
        self.value['identityEvidence']['linkedInventory'].pop()
        with self.assertRaises(ContractError):self.check()
    def test_inventory_hash_not_optional(self):
        self.value['identityEvidence']['compilerInventory'][0]['sha256']='f'*64
        with self.assertRaises(ContractError):self.check()
    def test_duplicate_inventory_identity(self):
        self.value['identityEvidence']['compilerInventory'][1]['assemblyIdentity']=self.app
        with self.assertRaises(ContractError):self.check()
    def test_mvid_complete(self):
        self.value['identityEvidence']['compilerInventory'][0]['mvid']='-'*36
        with self.assertRaises(ContractError):self.check()
    def test_duplicate_resolution(self):
        a=self.value['identityEvidence']['compilerResolutions'];a.append(copy.deepcopy(a[0]))
        with self.assertRaises(ContractError):self.check()
    def test_resolution_origin_bound(self):
        self.value['identityEvidence']['compilerResolutions'][0]['declaredModuleSha256']='0'*64
        with self.assertRaises(ContractError):self.check()
    def test_qualifiers_not_removed(self):
        self.value['identityEvidence']['compilerResolutions'][0]['canonicalKey']='System.Object'
        with self.assertRaises(ContractError):self.check()
    def test_missing_facade_step(self):
        self.value['identityEvidence']['compilerResolutions'][0]['forwardingPath'].pop(1)
        with self.assertRaises(ContractError):self.check()
    def test_unattributed_path(self):
        self.value['identityEvidence']['compilerResolutions'][0]['forwardingPath'].insert(1,'Other | sha256='+'0'*64)
        with self.assertRaises(ContractError):self.check()
    def test_repeated_path_step(self):
        a=self.value['identityEvidence']['compilerResolutions'][0]['forwardingPath'];a.insert(1,a[0])
        with self.assertRaises(ContractError):self.check()
    def test_boolean_claim_not_numeric(self):
        self.value['identityEvidence']['compilerResolutions'][0]['runtimeFacadeUsed']=1
        with self.assertRaises(ContractError):self.check()
    def test_facade_claim_matches_path(self):
        self.value['identityEvidence']['compilerResolutions'][0]['runtimeFacadeUsed']=False
        with self.assertRaises(ContractError):self.check()
    def test_forwarder_target_agrees(self):
        self.proof['forwarders'][0]['destinationAssemblyIdentity']=self.app
        with self.assertRaises(ContractError):self.check()
    def test_forwarder_declaration_agrees(self):
        self.proof['forwarders'][0]['typeFullName']='System.Other'
        with self.assertRaises(ContractError):self.check()
    def test_forwarder_duplicate_rejected(self):
        self.proof['forwarders'].append(copy.deepcopy(self.proof['forwarders'][0]))
        with self.assertRaises(ContractError):self.check()
    def test_assembly_admission_flags(self):
        for key,val in [('editorAccepted',False),('nativeProofExecuted',True),('allocationProofStillRequired',False),('pureInterpreterExpansionEnabled',True)]:
            with self.subTest(key=key):
                r=self.value['assemblies'][0];old=r[key];r[key]=val
                with self.assertRaises(ContractError):self.check()
                r[key]=old
    def test_compared_dll_exact(self):
        self.value['assemblies'][0]['targetDllSha256']='0'*64
        with self.assertRaises(ContractError):self.check()
    def test_no_hidden_rejected_type(self):
        self.value['assemblies'][0]['types'][0]['decision']='Rejected'
        with self.assertRaises(ContractError):self.check()
    def test_no_omitted_type_inventory(self):
        self.value['assemblies'][0]['types']=[]
        with self.assertRaises(ContractError):self.check()
    def test_duplicate_type_rows(self):
        a=self.value['assemblies'][0]['types'];a.append(copy.deepcopy(a[0]))
        with self.assertRaises(ContractError):self.check()


class DeclarationAndPathTests(unittest.TestCase):
    def test_nested_canonical_identity(self):
        s=''.join(map(identity.key_token,['System','2','Outer`1','Inner']))
        self.assertEqual(evidence.declaration_name(s),'System.Outer`1/Inner')
    def test_non_bmp_length_uses_utf16(self):
        s=''.join(map(identity.key_token,['Test','1','Type\U0001f3b2']))
        self.assertEqual(evidence.declaration_name(s),'Test.Type\U0001f3b2')
    def test_invalid_token_length_and_shape(self):
        for value in ['','06:System;1:1;6:Object;','6:System;1:2;6:Object;','6:System;1:1;6:Object','6:System;1:0;0:;']:
            with self.subTest(value=value), self.assertRaises(ContractError):evidence.declaration_name(value)
    def test_path_escape_and_absolute(self):
        with tempfile.TemporaryDirectory() as root:
            for value in ['../x','/tmp/x','a/../x','a//x']:
                with self.subTest(value=value),self.assertRaises(ContractError):identity.child(root,value)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'file').write_text('x');(root/'link').symlink_to(root/'file')
            with self.assertRaises(ContractError):identity.child(root,'link')
    def test_case_set_unique(self):
        self.assertEqual(len(identity.CASES),33);self.assertEqual(len(set(identity.CASES)),33)


if __name__ == '__main__': unittest.main()
