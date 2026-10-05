"""Synthetic input/receipt adversaries. No generated object is Unity evidence."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
import compiler_policy_inputs as policy
import fixture_project as fixture
from batch_contract import ContractError
import test_completion_contracts as prior


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value));return path

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Inputs(unittest.TestCase):
    setUp=prior.SourceFixtureTests.setUp
    def rebind(self,path):
        name=str(path.relative_to(self.demo));self.rows=[r for r in self.rows if r.split('\t')[1]!=name]
        self.rows.append('100644 blob '+fixture.blob(path.read_bytes())+'\t'+name)
    def test_raw_is_required_and_immutable(self):
        self.assertIn(policy.RAW,fixture.SETTINGS);self.assertNotIn(policy.RAW,fixture.MUTABLE)
        p,c=fixture.provision(self.batch);self.assertEqual(c['compilerPolicyInputs'],policy.validate_inputs(p))
    def test_missing_tracked_raw_configuration_fails_before_copy(self):
        self.rows=[r for r in self.rows if r.split('\t')[1]!=policy.RAW]
        with self.assertRaises(ContractError):fixture.provision(self.batch)
        self.assertFalse((self.batch.root/'projects/resource-complete').exists())
    def test_changed_raw_even_when_git_record_is_changed_fails(self):
        p=self.demo/policy.RAW;p.write_text(p.read_text()+'\n');self.rebind(p)
        with self.assertRaisesRegex(ContractError,'raw-type'):fixture.provision(self.batch)
    def test_new_unreviewed_policy_file_is_not_silently_omitted(self):
        self.rows.append('100644 blob '+'0'*40+'\tProjectSettings/AssemblyShadowOtherGuard.json')
        with self.assertRaisesRegex(ContractError,'input closure'):fixture.provision(self.batch)
    def test_missing_other_policy_inputs_fails(self):
        for name in policy.CONFIGS:
            with self.subTest(name=name):
                original=self.rows;self.rows=[r for r in original if r.split('\t')[1]!=name]
                with self.assertRaises(ContractError):fixture.source_catalog(self.demo,self.commit)
                self.rows=original
    def test_raw_mutation_after_copy_is_never_allowed_configuration(self):
        p,c=fixture.provision(self.batch);(p/policy.RAW).write_text('{}')
        with self.assertRaises(ContractError):fixture.verify_sources(p,c,configured=True)
    def test_missing_finite_entry_fails(self):
        p=self.demo/policy.DEPENDENCY;d=json.loads(p.read_text());d['bootstrapEntrypoints']=[e for e in d['bootstrapEntrypoints'] if e.get('method')!=policy.CALLSITE];put(p,d);self.rebind(p)
        with self.assertRaisesRegex(ContractError,'entry required'):fixture.provision(self.batch)
    def test_every_finite_entry_field_is_bound(self):
        p=self.demo/policy.DEPENDENCY;old=p.read_bytes()
        for key in ('consumer','provider','typeName','target','method','reason'):
            with self.subTest(key=key):
                d=json.loads(old);e=next(e for e in d['bootstrapEntrypoints'] if e.get('method')==policy.CALLSITE);e[key]='' if key=='reason' else 'Wrong';put(p,d)
                with self.assertRaises(ContractError):policy.validate_inputs(self.demo)
        p.write_bytes(old)
    def test_existing_dependencies_are_not_replaced_by_a_blanket_allowance(self):
        p=self.demo/policy.DEPENDENCY;d=json.loads(p.read_text());d['bootstrapEntrypoints'][0]['reason']='altered';put(p,d)
        with self.assertRaisesRegex(ContractError,'Existing dependency'):policy.validate_inputs(self.demo)
    def test_duplicate_entry_fails(self):
        p=self.demo/policy.DEPENDENCY;d=json.loads(p.read_text());d['bootstrapEntrypoints'].append(next(e for e in d['bootstrapEntrypoints'] if e.get('method')==policy.CALLSITE));put(p,d)
        with self.assertRaises(ContractError):policy.validate_inputs(self.demo)
    def test_marker_cannot_omit_the_closure(self):
        p,c=fixture.provision(self.batch);del c['compilerPolicyInputs']
        with self.assertRaises(ContractError):fixture.verify_sources(p,c)
    def test_symlink_raw_source_fails(self):
        p=self.demo/policy.RAW;other=self.root/'outside';other.write_bytes(p.read_bytes());p.unlink();p.symlink_to(other)
        with self.assertRaises(ContractError):policy.validate_inputs(self.demo)

class Receipts(unittest.TestCase):
    setUp=prior.SourceFixtureTests.setUp
    def sample(self):
        p,c=fixture.provision(self.batch);self.project=p;self.batch.resource_config=c
        root=Path(c['receiptRoot']);s=p/'_temp/AssemblyShadow/M07CompilerPreflight-synthetic/Snapshot';ctrl=root/'compiler-policy-controls'
        raw=json.loads((p/policy.RAW).read_text());deps=json.loads((p/policy.DEPENDENCY).read_text())
        names=sorted({x['providerAssemblyIdentity'].split(',')[0] for x in raw['sites']}|{'AssemblyShadowDemo.Bootstrap'})
        # Explicitly non-executable synthetic DLL bytes test receipt verification only.
        files=[]
        for name in names:
            q=s/('Assemblies/'+name+'.dll');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(('synthetic:'+name).encode());files.append({'name':name,'path':str(q.relative_to(s)),'sha256':digest(q)})
        snap={'kind':'CompilePlayerScripts','playerBuildSucceeded':False,'sourcePins':json.loads((p/policy.PINS).read_text()),'extraScriptingDefines':['ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_'+policy.RAW_SHA],'assemblies':files,'references':[]}
        put(s/'assembly-snapshot.json',snap);hashes={f['name']:f['sha256'] for f in files}
        observation={'kind':'R03CompilerPolicyChecks','mode':'Development','rawSha256':policy.RAW_SHA,'dependencySha256':digest(p/policy.DEPENDENCY),
            'snapshotSha256':digest(s/'assembly-snapshot.json'),'onQuitMethodHash':'a'*64,'moduleFiles':[{'path':str(s/f['path']),'sha256':f['sha256']} for f in files],
            'linkedProofExecuted':False,'runtimeAcceptance':False,'expansionAuthorized':False,'sites':[],'controls':[]}
        for site in sorted(raw['sites'],key=lambda x:x['id']):
            variant=next(v for v in site['compilerVariants'] if v['compilerMode']=='Development')
            observation['sites'].append({'id':site['id'],'consumerAssemblyIdentity':site['consumerAssembly']+', Version=0.0.0.0, Culture=neutral, PublicKeyToken=null',
                'consumerSha256':hashes[site['consumerAssembly']],'providerAssemblyIdentity':site['providerAssemblyIdentity'],'providerSha256':hashes[site['providerAssemblyIdentity'].split(',')[0]],
                'providerInventoryHash':'b'*64,'methodSignature':site['methodSignature'],'methodHash':variant['methodHash'],'operationIndex':variant['operationIndex'],'operationSignature':site['operationSignature']})
        for label,code in policy.CODES.items():
            value=copy.deepcopy(raw if label[0]=='R' else deps);mode=None;omitted=None
            if label[0]=='R':
                mode=None if label=='R06' else 'Development';omitted='AssemblyShadowDemo.Bootstrap' if label=='R07' else None
                if label=='R02':value=None
                if label=='R03':
                    method=value['sites'][0]['methodSignature']
                    for site in value['sites']:
                        if site['methodSignature']==method:next(v for v in site['compilerVariants'] if v['compilerMode']=='Development')['methodHash']='0'*64
                if label=='R04':value['sites'][0]['compilerVariants'][0]['operationIndex']=100000
                if label=='R05':value['sites'][0]['providerAssemblyIdentity']='AssemblyA.Contracts, Version=9.0.0.0, Culture=neutral, PublicKeyToken=null'
                if label=='R08':value['sites'][0]['compilerVariants'].pop(1)
            else:
                e=next(e for e in value['bootstrapEntrypoints'] if e.get('method')==policy.CALLSITE)
                if label=='B02':value['bootstrapEntrypoints'].remove(e)
                mutations={'B03':('method',policy.CALLSITE+'Wrong'),'B04':('provider','AssemblyA.Contracts'),'B05':('typeName',policy.TYPE+'Wrong'),'B06':('target',policy.TARGET+'Wrong'),'B07':('consumer','Other.Bootstrap'),'B08':('reason','')}
                if label in mutations:k,v=mutations[label];e[k]=v
            path=put(ctrl/(label+'.json'),value)
            observation['controls'].append({'id':label,'expected':code,'actual':code,'result':'Passed','mode':mode,'omittedModule':omitted,
                'operation':'RawTypeAdmissionVerifier.Verify' if label[0]=='R' else 'BootstrapIsolationRule.IsApprovedReflection','configurationPath':str(path),'configurationSha256':digest(path)})
        put(ctrl/'observation.json',observation)
        config=s/'RawTypeAdmissions/configuration.json';config.parent.mkdir(parents=True);config.write_bytes((p/policy.RAW).read_bytes())
        proof={'phase':'Compiled','configurationSha256':policy.RAW_SHA,'buildGuid':'','sites':[dict(x,compiledMethodHash=x['methodHash']) for x in observation['sites']]}
        put(s/'RawTypeAdmissions/compiled-evidence.json',proof)
        inputs=[{'path':name,'sha256':digest(p/name)} for name in policy.INPUTS]
        report={'schemaVersion':1,'kind':'R03ActualCompilerPolicyContract','result':'Passed','projectPath':str(p),'baselineId':c['baselineId'],
            'unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64','unityEditorRun':True,'originalCompilerPolicyPassed':True,'capturedRawProofVerified':True,
            'linkedProofExecuted':False,'runtimeAcceptance':False,'expansionAuthorized':False,'R03Accepted':False,'H2Passed':False,
            'snapshot':str(s),'snapshotSha256':digest(s/'assembly-snapshot.json'),'compiledProofSha256':digest(s/'RawTypeAdmissions/compiled-evidence.json'),
            'before':inputs,'after':copy.deepcopy(inputs),'observation':observation}
        path=put(root/'compiler-policy-contract.json',report);self.path=path;return report
    def verify(self,r):
        put(self.path,r);return policy.verify_report(self.path,self.batch,self.project)
    def test_synthetic_receipt_shape_only(self):self.assertEqual(self.verify(self.sample())['rawSites'],25)
    def test_false_or_unavailable_original_gate_rejected(self):
        r=self.sample();r['originalCompilerPolicyPassed']=False
        with self.assertRaises(ContractError):self.verify(r)
    def test_unclaimed_capture_rejected(self):
        r=self.sample();r['capturedRawProofVerified']=False
        with self.assertRaises(ContractError):self.verify(r)
    def test_skipped_raw_row_rejected(self):
        r=self.sample();r['observation']['sites'].pop()
        with self.assertRaises(ContractError):self.verify(r)
    def test_changed_config_hash_rejected(self):
        r=self.sample();r['before'][0]['sha256']='f'*64
        with self.assertRaises(ContractError):self.verify(r)
    def test_extra_compiler_dll_rejected(self):
        r=self.sample();(Path(r['snapshot'])/'extra.dll').write_bytes(b'synthetic')
        with self.assertRaises(ContractError):self.verify(r)
    def test_control_bypass_not_a_pass(self):
        r=self.sample();r['observation']['controls'][1]['actual']='Success'
        with self.assertRaises(ContractError):self.verify(r)
    def test_altered_control_even_with_hash_rebound_rejected(self):
        r=self.sample();c=r['observation']['controls'][3];p=Path(c['configurationPath']);d=json.loads(p.read_text());d['sites'][0]['compilerVariants'][0]['operationIndex']=200000;put(p,d);c['configurationSha256']=digest(p)
        with self.assertRaises(ContractError):self.verify(r)
    def test_unbound_module_inventory_rejected(self):
        r=self.sample();r['observation']['moduleFiles'].pop()
        with self.assertRaises(ContractError):self.verify(r)
    def test_linked_or_runtime_authorization_claim_rejected(self):
        r=self.sample()
        for flag in ('linkedProofExecuted','runtimeAcceptance','expansionAuthorized','R03Accepted','H2Passed'):
            d=copy.deepcopy(r);d[flag]=True
            with self.assertRaises(ContractError):self.verify(d)
    def test_outside_snapshot_rejected(self):
        r=self.sample();r['snapshot']=str(self.root/'outside/Snapshot')
        with self.assertRaises(ContractError):self.verify(r)
    def test_original_inputs_and_mutation_failures_not_restored(self):
        r=self.sample();p=self.project/policy.RAW;p.write_text('{}')
        with self.assertRaises(ContractError):self.verify(r)
        self.assertEqual(p.read_text(),'{}')

if __name__=='__main__':unittest.main()
