"""Synthetic verifier fault injection, not fabricated Unity execution evidence."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import resource_capabilities as c
from batch_contract import ContractError, sha
from batch_evidence import write

class CapabilityContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name).resolve()/'project';self.project.mkdir()
        self.receipts=self.project/'_temp/receipts';self.receipts.mkdir(parents=True)
        self.batch=SimpleNamespace(resource_config={'receiptRoot':str(self.receipts),'baselineId':'baseline'},unity=self.project/'SDK/Unity.app/Contents/MacOS/Unity')
        self.manifest=c.dependency_profile({'com.unity.modules.jsonserialize':'1.0.0','com.unity.render-pipelines.universal':'14.0.12','com.unity.test-framework':'1.1.33','com.unity.ugui':'1.0.0'},self.project/'package')
        self.lock={'dependencies':{k:{'version':v} for k,v in self.manifest['dependencies'].items()}}
        for relative in c.INPUTS:
            p=self.project/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
        (self.project/c.INPUTS[0]).write_text(json.dumps(self.manifest));(self.project/c.INPUTS[1]).write_text(json.dumps(self.lock))
        for name in c.SOURCES:
            p=self.project/'Assets/AssemblyShadowDemo/Editor'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(name)
        files=[]
        for n in c.INCLUDED:
            p=self.project/'Library/PackageCache'/ (n+'.dll');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(n.encode())
            files.append({'path':str(p),'sha256':sha(p),'size':p.stat().st_size})
        groups=[{'mode':m,'name':'Consumer','flags':'None','compiledReferences':[f['path'] for f in files]} for m in ('Player','PlayerWithoutTestAssemblies')]
        inventory=[{'name':n,'classification':k,'isPrecompiled':v} for n,k,v in c.reconstruct_inventory(groups,self.batch.unity).values()]
        self.report={'kind':'R03ActualTargetCapabilityContract','schemaVersion':1,'result':'Passed','profile':c.PROFILE,
          'projectPath':str(self.project),'baselineId':'baseline','unityVersion':'2022.3.62f2','target':'StandaloneOSX','architecture':'arm64',
          'consumer':'AssemblyShadowSettingsUtil.CreatePolicyConfiguration/BuildCompilerInventory/BuildCapabilities',
          'unityEditorRun':True,'snapshotCompilationRun':False,'R03Accepted':False,'H2Passed':False,'expansionAuthorized':False,
          'before':[{'path':n,'sha256':sha(self.project/n)} for n in c.INPUTS],
          'sourceFiles':[{'path':n,'sha256':sha(self.project/'Assets/AssemblyShadowDemo/Editor'/n)} for n in c.SOURCES],
          'inventory':inventory,'declarations':[{'name':n,'included':n in c.INCLUDED,'present':n in c.INCLUDED,'isShadowCapable':False} for n in (*c.INCLUDED,*c.EXCLUDED)],
          'compilerAssemblies':groups,'referenceFiles':files,'cases':[],
          'policyJson':json.dumps({'rejectUnknownReflectionDependencies':True,'enforceResourceAbi':True,
             'assemblies':[{'name':n,'classification':0,'isPrecompiled':True,'capabilityDeclared':True,'isShadowCapable':False,'isBootstrap':False} for n in c.INCLUDED]})}
        self.report['after']=copy.deepcopy(self.report['before'])
        for name,code in c.CODES.items():
            p=self.receipts/'capability-inputs'/(name+'.json');p.parent.mkdir(exist_ok=True);p.write_text('{}')
            self.report['cases'].append({'id':name,'path':str(p),'sha256':sha(p),'expectedCode':code,'observedCode':code,'result':'Passed'})
        self.path=self.receipts/'capability-contract.json'
    def verify(self):
        self.path.write_text(json.dumps(self.report));return c.verify_report(self.path,self.batch,self.project)
    def reject(self):
        with self.assertRaises(ContractError):self.verify()
    def test_exact_synthetic_contract(self):self.assertEqual(self.verify()['declarationsAudited'],5)
    def test_missing_declaration(self):self.report['declarations'].pop();self.reject()
    def test_duplicate_declaration(self):self.report['declarations'][-1]=self.report['declarations'][0];self.reject()
    def test_excluded_present(self):self.report['inventory'].append({'name':c.EXCLUDED[0],'classification':'Runtime','isPrecompiled':True});self.reject()
    def test_missing_required_plugin(self):self.report['inventory'].pop();self.reject()
    def test_testonly_required_plugin(self):self.report['inventory'][-1]['classification']='TestOnly';self.reject()
    def test_full_inventory_no_omission(self):self.report['inventory']=self.report['inventory'][1:];self.reject()
    def test_raw_inventory_missing_mode(self):self.report['compilerAssemblies'].pop();self.reject()
    def test_raw_reference_added(self):self.report['compilerAssemblies'][0]['compiledReferences'].append('/new.dll');self.reject()
    def test_duplicate_reference_inventory(self):self.report['referenceFiles'].append(self.report['referenceFiles'][0]);self.reject()
    def test_changed_reference(self):Path(self.report['referenceFiles'][0]['path']).write_text('other');self.reject()
    def test_each_negative_code_preserved(self):
        for index in range(len(c.CODES)):
            old=self.report['cases'][index]['observedCode'];self.report['cases'][index]['observedCode']='wrong';self.reject();self.report['cases'][index]['observedCode']=old
    def test_missing_control(self):self.report['cases'].pop();self.reject()
    def test_duplicate_control(self):self.report['cases'][-1]=self.report['cases'][0];self.reject()
    def test_changed_control_bytes(self):Path(self.report['cases'][0]['path']).write_text('different');self.reject()
    def test_outside_control(self):self.report['cases'][0]['path']=str(self.project/c.INPUTS[0]);self.report['cases'][0]['sha256']=sha(self.project/c.INPUTS[0]);self.reject()
    def test_changed_settings(self):(self.project/c.INPUTS[2]).write_text('different');self.reject()
    def test_changed_consumer_source(self):(self.project/'Assets/AssemblyShadowDemo/Editor'/c.SOURCES[0]).write_text('different');self.reject()
    def test_invented_consumer(self):self.report['consumer']='name-only';self.reject()
    def test_authorization_forbidden(self):self.report['expansionAuthorized']=True;self.reject()
    def test_policy_guard_preserved(self):
        policy=json.loads(self.report['policyJson']);policy['rejectUnknownReflectionDependencies']=False;self.report['policyJson']=json.dumps(policy);self.reject()
    def test_policy_role_preserved(self):
        policy=json.loads(self.report['policyJson']);policy['assemblies'][0]['classification']=4;self.report['policyJson']=json.dumps(policy);self.reject()
    def test_all_dependency_versions_pinned(self):
        self.assertTrue(c.validate_packages(self.manifest,self.lock))
        for n in c.PACKAGES:
            bad=copy.deepcopy(self.lock);bad['dependencies'][n]['version']='other'
            with self.assertRaises(ContractError):c.validate_packages(self.manifest,bad)
    def test_unknown_dependency_not_optional(self):
        self.lock['dependencies']['com.unity.visualscripting']={'version':'1.9.4'}
        with self.assertRaises(ContractError):c.validate_packages(self.manifest,self.lock)
    def test_all_five_inherited_declarations_are_still_in_default(self):
        import re
        source=(HERE.parents[2]/'Assets/AssemblyShadowDemo/Editor/M02Build.cs').read_text()
        method=source.split('internal static AssemblyCapability[] InheritedPrecompiledCapabilities()')[1].split('public static void ValidateConfiguration')[0]
        self.assertEqual(set(re.findall(r'name = "([^"]+)"',method)),{*c.INCLUDED,*c.EXCLUDED})
        self.assertIn('R03ResourceCapabilityProfile.Apply(InheritedPrecompiledCapabilities())',source)
    def test_no_inventory_filter_in_profile(self):
        source=(HERE.parents[2]/'Assets/AssemblyShadowDemo/Editor/R03ResourceCapabilityProfile.cs').read_text()
        self.assertNotIn('CompilationPipeline.GetAssemblies',source)
        self.assertIn('if (current == 0) return inherited',source)
        self.assertIn('Thread.CurrentThread.ManagedThreadId',source)
    def test_preflight_runs_before_compiler(self):
        source=(HERE/'resource_pipeline.py').read_text()
        self.assertLess(source.index("command(batch, 'capability-preflight')"),source.index('command(batch, name)'))
    def test_resource_scope_keeps_full_ninety_cells(self):
        import run_completion
        from batch_contract import loads
        matrix=loads((HERE.parent/'R03/player-cases.json').read_text())
        self.assertEqual(len(run_completion.cell_plan(matrix)),90)
