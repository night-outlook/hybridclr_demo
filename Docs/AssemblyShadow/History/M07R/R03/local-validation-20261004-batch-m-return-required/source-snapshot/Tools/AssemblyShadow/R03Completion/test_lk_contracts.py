"""Fixed-image INPUT and verifier adversarial contracts; not runtime evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import fixed_image_inputs as fixed
import fixture_project as fixture
import resource_pipeline as pipeline
from batch_contract import ContractError
from batch_evidence import write
from evidence import EvidenceError
import test_completion_contracts as fixture_test_support


def digest(data): return hashlib.sha256(data).hexdigest()


class FixedProvisionTests(unittest.TestCase):
    setUp = fixture_test_support.SourceFixtureTests.setUp

    def test_pinned_sources_now_mandatory_tracked_inputs(self):
        rows=fixture.source_catalog(self.demo,self.commit)
        for name,blob in fixed.FILES.items():
            self.assertIn({'path':name,'blob':blob,'size':(self.demo/name).stat().st_size,'sha256':digest((self.demo/name).read_bytes())},rows)

    def test_k_git_only_ignored_directory_does_not_supply_authority(self):
        self.rows=[row for row in self.rows if row.split('\t')[1] not in fixed.FILES]
        with self.assertRaisesRegex(ContractError,'fixed-image source missing'):
            fixture.provision(self.batch)
        self.assertFalse((self.batch.root/'projects/resource-complete').exists())

    def test_no_ignored_image_is_selected(self):
        self.assertFalse(fixture.select(fixed.ordinary.IMAGE_PATH))
        destination=self.demo/fixed.ordinary.IMAGE_PATH
        destination.parent.mkdir(parents=True);destination.write_bytes(b'untrusted ignored cache')
        project,config=fixture.provision(self.batch)
        self.assertEqual(digest((project/fixed.ordinary.IMAGE_PATH).read_bytes()),fixed.ordinary.IMAGE_SHA256)
        self.assertEqual(destination.read_bytes(),b'untrusted ignored cache')
        self.assertEqual(config['fixedImageProfile'],fixed.PROFILE)

    def test_materialization_is_not_fresh_compilation(self):
        project,config=fixture.provision(self.batch)
        record=json.loads((project/fixed.MATERIALIZATION/'preparation.json').read_text())
        self.assertEqual(record['classification'],'FrozenHistoricalInputMaterialization')
        for name in ('freshCscExecutionClaimed','historicalPlayerExecutionReused','runtimeAcceptance'):
            self.assertIs(record[name],False)
        self.assertIsNone(record['destinationBefore'])
        self.assertEqual(fixture.verify_sources(project,config)['fixedImage']['siteIds'],fixed.SITES)

    def test_missing_staged_image_fails_before_compiler(self):
        project,config=fixture.provision(self.batch);(project/fixed.ordinary.IMAGE_PATH).unlink()
        with self.assertRaises((ContractError,EvidenceError)):
            fixture.verify_sources(project,config,configured=True)

    def test_changed_staged_image_is_not_restored(self):
        project,config=fixture.provision(self.batch);path=project/fixed.ordinary.IMAGE_PATH
        path.write_bytes(b'changed')
        with self.assertRaises((ContractError,EvidenceError)):
            fixture.verify_sources(project,config,configured=True)
        self.assertEqual(path.read_bytes(),b'changed')

    def test_altered_origin_even_with_same_image_fails(self):
        project,config=fixture.provision(self.batch);path=project/fixed.ordinary.ORIGIN
        row=json.loads(path.read_text());row['extractionCommit']='0'*40;path.write_text(json.dumps(row))
        with self.assertRaises((ContractError,EvidenceError)):fixed.verify_materialization(project)

    def test_output_reuse_refused(self):
        project,_=fixture.provision(self.batch)
        with self.assertRaises(EvidenceError):fixed.provision(project)

    def test_wrong_existing_image_is_preserved(self):
        project,_=fixture.provision(self.batch)
        shutil.rmtree(project/fixed.MATERIALIZATION)
        (project/fixed.ordinary.IMAGE_PATH).write_bytes(b'wrong')
        with self.assertRaises(EvidenceError):fixed.provision(project)
        self.assertEqual((project/fixed.ordinary.IMAGE_PATH).read_bytes(),b'wrong')

    def test_missing_explicit_profile_fails(self):
        project,config=fixture.provision(self.batch);del config['fixedImageProfile']
        with self.assertRaises(ContractError):fixture.verify_sources(project,config)

    def test_changed_config_never_rebaselines_pinned_sites(self):
        path=self.demo/fixed.CONFIG;value=json.loads(path.read_text())
        value['sites'][-1]['imageSha256']='1'*64;path.write_text(json.dumps(value))
        with self.assertRaises(ContractError):fixed.source_contract(self.demo)

    def test_symlink_authority_rejected(self):
        path=self.demo/fixed.ordinary.FIXTURE;data=path.read_bytes();path.unlink()
        outside=self.root/'outside';outside.write_bytes(data);path.symlink_to(outside)
        with self.assertRaises(ContractError):fixed.source_contract(self.demo)


class FixedObservationTests(unittest.TestCase):
    """Synthetic records test verification, never claim an actual Unity run."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.controls=self.root/'controls';self.controls.mkdir()
        demo=Path(__file__).resolve().parents[3]
        original=json.loads((demo/fixed.CONFIG).read_text());image=fixed.ordinary.fixture(demo)[0]
        self.value={'profile':fixed.PROFILE,'imageSha256':fixed.ordinary.IMAGE_SHA256,'providerIdentity':fixed.ordinary.PROVIDER,
            'sizeBytes':4608,'mvid':'e7f5b1ac-eca4-4034-8da4-69e25ca9fe3b','siteIds':fixed.SITES,
            'imageSemanticHash':fixed.MODES['Development'],'classification':fixed.ordinary.CLASSIFICATION,
            'freshCscExecutionClaimed':False,'historicalPlayerExecutionReused':False,'runtimeAcceptance':False,'cases':[]}
        for i,(label,code) in enumerate(fixed.CODES.items()):
            config=copy.deepcopy(original)
            if label=='F04-provider-identity':
                for site in config['sites']:
                    if site['kind']=='FixedAssemblyBytes':site['providerAssemblyIdentity']='Other, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'
            if label=='F09-omitted-variant':
                site=next(s for s in config['sites'] if s['id']==fixed.SITES[0]);site['providerSemanticVariants']=site['providerSemanticVariants'][:1]
            if label=='F10-image-path':next(s for s in config['sites'] if s['id']==fixed.SITES[0])['imagePath']='../outside.dll'
            path=self.controls/(label+'.json');write(path,config)
            inp=None
            if i in (0,2,3):
                inp=self.controls/(label+'.dll.bytes');inp.write_bytes(image if i!=2 else image[:-1]+bytes([image[-1]^1]))
            mode={'F05-development':'Development','F06-release':'Release','F08-unknown-mode':'Unknown'}.get(label)
            self.value['cases'].append({'id':label,'expectedCode':code,'observedCode':code,'result':'Passed',
                'operation':'ValidateImageEvidence' if i<4 else 'ProviderSemanticHash' if i<8 else 'Parse',
                'mode':mode,'selectedSemanticHash':fixed.MODES.get(mode) if i in (4,5) else None,
                'configurationPath':str(path),'configurationSha256':digest(path.read_bytes()),
                'imagePath':None if inp is None else str(inp),'imageSha256':None if inp is None else digest(inp.read_bytes())})

    def verify(self):return fixed.verify_observation(self.value,self.controls,pinned_semantics=True)
    def test_exact_synthetic_record(self):self.assertEqual(self.verify()['cases'],10)
    def test_unknown_semantic_not_added_as_variant(self):
        self.value['imageSemanticHash']='a'*64
        with self.assertRaises(ContractError):self.verify()
    def test_omitted_site(self):
        self.value['siteIds']=fixed.SITES[:1]
        with self.assertRaises(ContractError):self.verify()
    def test_claimed_new_compilation(self):
        self.value['freshCscExecutionClaimed']=True
        with self.assertRaises(ContractError):self.verify()
    def test_missing_control(self):
        self.value['cases'].pop()
        with self.assertRaises(ContractError):self.verify()
    def test_duplicate_control(self):
        self.value['cases'].append(self.value['cases'][0])
        with self.assertRaises(ContractError):self.verify()
    def test_code_substitution(self):
        self.value['cases'][1]['observedCode']='Success'
        with self.assertRaises(ContractError):self.verify()
    def test_mode_substitution(self):
        self.value['cases'][4]['mode']='Release'
        with self.assertRaises(ContractError):self.verify()
    def test_omitted_image_control(self):
        self.value['cases'][0]['imagePath']=None
        with self.assertRaises(ContractError):self.verify()
    def test_refreshed_hash_cannot_hide_control_config_mutation(self):
        row=self.value['cases'][0];p=Path(row['configurationPath']);c=json.loads(p.read_text());c['sites'][0]['allowedTypes']=[];p.write_text(json.dumps(c))
        row['configurationSha256']=digest(p.read_bytes())
        with self.assertRaises(ContractError):self.verify()
    def test_wrong_mutation_cannot_pass_by_refreshing_hash(self):
        row=self.value['cases'][2];p=Path(row['imagePath']);p.write_bytes(b'0'*4608);row['imageSha256']=digest(p.read_bytes())
        with self.assertRaises(ContractError):self.verify()
    def test_added_unbound_control_file(self):
        (self.controls/'extra').write_text('x')
        with self.assertRaises(ContractError):self.verify()
    def test_outside_control(self):
        row=self.value['cases'][0];other=self.root/'other.json';shutil.copyfile(row['configurationPath'],other);row['configurationPath']=str(other)
        with self.assertRaises(ContractError):self.verify()
    def test_symlink_control(self):
        row=self.value['cases'][0];p=Path(row['configurationPath']);other=self.root/'other.json';p.rename(other);p.symlink_to(other)
        with self.assertRaises(ContractError):self.verify()
    def test_expected_negative_image_has_no_fake_hash(self):
        self.value['cases'][1]['imageSha256']='f'*64
        with self.assertRaises(ContractError):self.verify()
    def test_dotnet_observation_does_not_approve_pinned_mono(self):
        self.value['imageSemanticHash']='a'*64
        self.assertFalse(fixed.verify_observation(self.value,self.controls,pinned_semantics=False)['pinnedSemanticsVerified'])
        with self.assertRaises(ContractError):self.verify()


class FixedPipelineTests(unittest.TestCase):
    def test_origin_precedes_any_resource_copy(self):
        with patch.object(fixed,'authenticate_origin',side_effect=ContractError('origin failed')),patch.object(pipeline,'provision') as copy:
            with self.assertRaises(ContractError):pipeline.prepare(SimpleNamespace())
            copy.assert_not_called()
    def test_fixed_guard_failure_prevents_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            project=Path(temp)/'project';project.mkdir()
            config={'projectPath':str(project),'baselineId':'test','receiptRoot':str(project/'receipts'),'runPath':str(project/'run')}
            batch=SimpleNamespace(resource_config=config,root=Path(temp),unity='unused')
            calls=[]
            with patch.object(pipeline,'authenticate_copy',return_value=(project,{})),patch.object(pipeline,'verify_sources',return_value={}),\
                 patch.object(pipeline,'unity_command',side_effect=lambda b,args,t:calls.append(args) or {}),\
                 patch.object(pipeline,'verify_capability_report',return_value={}),\
                 patch.object(fixed,'verify_report',side_effect=ContractError('fixed input failed')):
                with self.assertRaises(ContractError):pipeline.phase(batch,'compiler')
            methods=[c[c.index('-executeMethod')+1] for c in calls]
            self.assertEqual(methods,['AssemblyShadowDemo.Editor.R03CompletionInventoryContract.Verify','AssemblyShadowDemo.Editor.R03CompletionFixedImageContract.Verify'])
    def test_materialization_and_actual_compiler_are_distinct(self):
        self.assertEqual(pipeline.METHODS['compiler'],'CompilerPreflight')
        self.assertEqual(pipeline.METHODS['fixed-image-preflight'],'Verify')
