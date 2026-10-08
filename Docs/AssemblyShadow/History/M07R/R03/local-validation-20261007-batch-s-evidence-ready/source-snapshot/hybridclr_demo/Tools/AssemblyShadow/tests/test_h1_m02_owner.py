"""Run in the complete demo checkout. No wrapper installation is performed."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import m02_results as owner
import h1_witness_contract as witness

TOOLS = Path(__file__).resolve().parents[1]
PROJECT = TOOLS.parents[1]
CONFIG = PROJECT / 'ProjectSettings/AssemblyShadowReflectionBindings.json'


class H1M02OwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuration = json.loads(CONFIG.read_text(encoding='utf-8'))
        witness.expected_site_ids(cls.configuration, require_current=True)

    def parse(self, value):
        return owner._reflection_parse(CONFIG, json.dumps(value).encode('utf-8'))

    def test_normal_owner_accepts_current_six_sites_without_install(self):
        self.assertEqual(6, len(self.parse(self.configuration)['declarations']))
        self.assertEqual('m02_results', owner._reflection_parse.__module__)

    def test_historical_five_sites_remain_readable(self):
        value=copy.deepcopy(self.configuration);value['sites']=[s for s in value['sites'] if s['id']!=witness.SITE_ID]
        self.assertEqual(5,len(self.parse(value)['declarations']))

    def test_compatibility_install_does_not_replace_the_owner(self):
        before=owner._reflection_parse
        compatibility=importlib.import_module('h1_m02_results');compatibility.install()
        self.assertIs(before,owner._reflection_parse)

    def test_current_hash_is_of_original_six_site_bytes(self):
        raw=json.dumps(self.configuration,indent=2).encode()
        result=owner._reflection_parse(CONFIG,raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),result['rawSha256'])
        self.assertEqual(owner._reflection_canonical_hash(self.configuration,CONFIG),result['canonicalHash'])

    def test_declared_h1_fields_are_not_loosened(self):
        for field,value in {'assembly':'Another.Assembly','typeName':'Another.Type','methodSignature':'Other()',
                            'originalMethodHash':'0'*64,'operationIndex':26,'imageSha256':'0'*64,
                            'providerAssemblyIdentity':'Other, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null',
                            'imagePath':'Other.dll','kind':'TypeGetType','allowedTypes':['System.String, mscorlib']}.items():
            with self.subTest(field=field):
                configuration=copy.deepcopy(self.configuration)
                next(s for s in configuration['sites'] if s['id']==witness.SITE_ID)[field]=value
                with self.assertRaises(owner.VerificationError):self.parse(configuration)

    def test_variant_type_hash_and_membership_are_exact(self):
        for variants in ([],[{'originalMethodHash':'0'*64,'operationIndex':25}],
                         [{'originalMethodHash':witness.METHOD_VARIANTS[1][0],'operationIndex':25.0}]):
            value=copy.deepcopy(self.configuration);next(s for s in value['sites'] if s['id']==witness.SITE_ID)['additionalMethodVariants']=variants
            with self.subTest(variants=variants),self.assertRaises(owner.VerificationError):self.parse(value)

    def test_unknown_and_duplicate_sites_rejected(self):
        for name in ('extra.site',witness.SITE_ID):
            value=copy.deepcopy(self.configuration);extra=copy.deepcopy(next(s for s in value['sites'] if s['id']==witness.SITE_ID));extra['id']=name;value['sites'].append(extra)
            with self.subTest(name=name),self.assertRaises(owner.VerificationError):self.parse(value)

    def test_duplicate_json_keys_rejected_by_normal_owner(self):
        raw=json.dumps(self.configuration).replace('"schemaVersion": 4','"schemaVersion": 4, "schemaVersion": 4',1)
        with self.assertRaises(owner.VerificationError):owner._reflection_parse(CONFIG,raw.encode())

    def test_schema_integer_type_is_strict(self):
        value=copy.deepcopy(self.configuration);value['schemaVersion']=4.0
        with self.assertRaises(owner.VerificationError):self.parse(value)

    def test_normal_cli_current_preflight(self):
        result=subprocess.run([sys.executable,str(TOOLS/'verify-m02-results.py'),'--check-reflection-config',str(CONFIG),'--require-h1-witness'],capture_output=True,text=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stderr)
        value=json.loads(result.stdout);self.assertEqual(6,value['siteCount']);self.assertFalse(value['runtimeVerified']);self.assertFalse(value['humanGatePassed'])

    def test_normal_cli_rejects_tampered_current_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json';value=copy.deepcopy(self.configuration)
            next(s for s in value['sites'] if s['id']==witness.SITE_ID)['operationIndex']=0;path.write_text(json.dumps(value))
            result=subprocess.run([sys.executable,str(TOOLS/'verify-m02-results.py'),'--check-reflection-config',str(path)],capture_output=True,text=True,timeout=30)
            self.assertEqual(1,result.returncode);self.assertIn('[FAIL]',result.stderr)

    def test_fresh_import_process_needs_no_wrapper(self):
        code="import json,pathlib,m02_results; p=pathlib.Path(__import__('sys').argv[1]); assert len(m02_results._reflection_parse(p,p.read_bytes())['declarations'])==6"
        result=subprocess.run([sys.executable,'-c',code,str(CONFIG)],cwd=TOOLS,capture_output=True,text=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stderr)

    def test_full_runtime_probe_checks_executed_h1_guard_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path,receipt,reflection,probe=self.runtime_fixture(Path(directory))
            path.write_text(json.dumps(probe));self.assertEqual('Passed',owner._verify_reflection_probe(path,receipt,reflection)['result'])
            for field in ('h1WitnessTamperRejected','h1WitnessNullRejected','h1WitnessCallerBytesUnchanged'):
                value=copy.deepcopy(probe);value[field]=False;path.write_text(json.dumps(value))
                with self.subTest(field=field),self.assertRaises(owner.VerificationError):owner._verify_reflection_probe(path,receipt,reflection)

    def test_contract_only_h1_summary_is_not_runtime_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            path,receipt,reflection,probe=self.runtime_fixture(Path(directory))
            for field in list(probe):
                if field in ('h1WitnessGuard','h1WitnessTamperRejected','h1WitnessNullRejected','h1WitnessCallerBytesUnchanged','h1WitnessAssemblyResolveEvents'):del probe[field]
            path.write_text(json.dumps(probe))
            with self.assertRaises(owner.VerificationError):owner._verify_reflection_probe(path,receipt,reflection)

    def test_wrong_h1_guard_or_resolver_events_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path,receipt,reflection,probe=self.runtime_fixture(Path(directory))
            for field,value in (('h1WitnessGuard','wrong'),('h1WitnessAssemblyResolveEvents',1)):
                wrong=copy.deepcopy(probe);wrong[field]=value;path.write_text(json.dumps(wrong))
                with self.subTest(field=field),self.assertRaises(owner.VerificationError):owner._verify_reflection_probe(path,receipt,reflection)

    def runtime_fixture(self, root):
        # Synthetic verifier fixtures, never reported as actual Player evidence.
        raw=json.dumps(self.configuration).encode();reflection=owner._reflection_parse(CONFIG,raw)
        output=root/'Synthetic.app';staged=output/'Contents/Resources/Data/StreamingAssets/AssemblyShadow/M02/reflection-bindings.json'
        staged.parent.mkdir(parents=True);staged.write_bytes(raw)
        receipt={'unityVersion':'2022.3.62f2','buildGuid':'1'*32,'playerOutput':str(output)}
        sites={s['id']:s for s in self.configuration['sites']};canvas=sites['urp-debug-ui-prefab-types']
        guard=lambda name:'__AssemblyShadowReflectionBinding_'+reflection['canonicalHash']+'_'+hashlib.sha256(name.encode()).hexdigest()
        probe={'schemaVersion':2,'milestone':'M02','mode':'M02ReflectionBindings','result':'Passed','il2cpp':True,'error':'',
               'unityVersion':receipt['unityVersion'],'platform':'OSXPlayer','buildGuid':receipt['buildGuid'],'playerDataPath':str(output/'Contents'),
               'configurationSha256':reflection['rawSha256'],'configurationHash':reflection['canonicalHash'],
               'canvasGuard':guard('urp-debug-ui-prefab-types'),'enumGuard':guard('urp-serializable-enum-player'),
               'finiteAssemblyGuard':guard('urp-volume-assembly-domain'),'finiteTypesGuard':guard('urp-volume-type-domain'),
               'fixedImageGuard':guard('m00-normal-hot-update-image'),
               'discoveryAllowedTypes':sorted(sites['urp-volume-type-domain']['allowedTypes']),
               'discoveryAssemblyNames':['Unity.RenderPipelines.Universal.Runtime'],'discoveryDeniedBeforeEnumeration':True,
               'fixedImageSha256':witness.IMAGE_SHA256,'fixedImageLoadedAssembly':witness.PROVIDER,'fixedImageLoadedMarker':'M00-HOTUPDATE-OK',
               'fixedImageTamperRejected':True,'fixedImageNullRejected':True,'fixedImageCallerBytesUnchanged':True,'volumeManagerMatchesContract':True,
               'h1WitnessContractValidated':True,'h1WitnessMethod':witness.METHOD,'h1WitnessPrimaryHash':witness.METHOD_VARIANTS[0][0],
               'h1WitnessOperationIndex':25,'h1WitnessImageSha256':witness.IMAGE_SHA256,'h1WitnessProviderAssembly':witness.PROVIDER,
               'h1WitnessGuard':guard(witness.SITE_ID),'h1WitnessTamperRejected':True,'h1WitnessNullRejected':True,
               'h1WitnessCallerBytesUnchanged':True,'h1WitnessAssemblyResolveEvents':0}
        probe['allowed']=[{'input':s,'type':s.split(',')[0],'assembly':s.split(',')[1].strip()} for s in sorted(canvas['allowedTypes'])]
        candidate='AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal'
        vectors=[('candidate',candidate),('generic-provider-escape','System.Collections.Generic.List`1[['+candidate+']], mscorlib'),
                 ('null',None),('unqualified','UnityEngine.Rendering.DebugUI+Value'),('unknown','AssemblyShadowUnknown.Type, AssemblyShadowUnknown'),
                 ('mutated-string',canvas['allowedTypes'][0]+' '),('runtime-prefab-mutation',candidate),('serializable-enum-deny-all','System.DayOfWeek, mscorlib')]
        probe['denied']=[{'name':name,'input':value,'inputWasNull':value is None,'denied':True,'exceptionType':'System.InvalidOperationException',
                         'assemblyResolveEvents':0,'message':'AssemblyShadow reflection denied; configuration='+reflection['canonicalHash']+'; site='+
                         ('urp-serializable-enum-player' if name=='serializable-enum-deny-all' else 'urp-debug-ui-prefab-types')} for name,value in vectors]
        return root/'probe.json',receipt,reflection,probe


if __name__=='__main__':unittest.main()
