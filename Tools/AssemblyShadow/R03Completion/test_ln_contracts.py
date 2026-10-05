"""Fail-closed LN source/cwd/identity regressions; no historical runtime promotion."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent/'R03')]
import editor_contract as editor
import layout_evidence as layout
import reference_binding
import native_codec_source as codec
from batch_contract import ContractError, loads


class NameContracts(unittest.TestCase):
    def test_original_case_is_canonical_for_inventory(self):
        self.assertEqual(layout.assembly_key('AssemblyA.Implementation.Internal'), 'assemblya.implementation.internal')
        rows=[{'name':'AssemblyA.Implementation.Internal','sha256':'abc'}]
        self.assertEqual(layout.unique_files(rows,linked=False), {'assemblya.implementation.internal':'abc'})
    def test_case_collision_target_rejected(self):
        with self.assertRaises(ContractError): layout.unique_files([{'name':'App','sha256':'a'},{'name':'app','sha256':'a'}],linked=False)
    def test_case_collision_linked_rejected(self):
        with self.assertRaises(ContractError): layout.unique_files([{'path':'x/App.dll','sha256':'a'},{'path':'x/app.dll','sha256':'a'}],linked=True)
    def test_qualified_name_not_shortened(self):
        for name in ('App, Version=1.0.0.0','x/App','App.dll',' App','App ', '', 'a\\b'):
            with self.subTest(name=name), self.assertRaises(ContractError): layout.assembly_key(name)
    def test_existing_source_bound_guard_remains(self):
        source=(HERE/'layout_evidence.py').read_text()
        self.assertIn("value['targetLoadOrder'] == order",source)
        self.assertIn("assembly_key(report['assembly']) == key",source)
        self.assertIn("t_files[key]",source)
        self.assertIn("b_files[key]",source)


class CodecContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.repo=self.root/'owner/hybridclr';self.repo.mkdir(parents=True)
        self.project=self.root/'batch/projects/resource-complete';self.project.mkdir(parents=True)
        self.git('init','-q');self.git('config','user.email','test@example.invalid');self.git('config','user.name','Test')
        self.git('remote','add','origin','https://github.com/night-outlook/hybridclr.git')
        p=self.repo/codec.HEADER;p.parent.mkdir(parents=True);p.write_bytes(b'// pinned codec test bytes\n')
        self.git('add','.');self.git('commit','-qm','fixture')
        self.rev=self.git('rev-parse','HEAD').strip();self.hash=hashlib.sha256(p.read_bytes()).hexdigest()
        self.pin={'revision':self.rev,'url':'https://github.com/night-outlook/hybridclr.git','localPath':os.path.relpath(self.repo,self.project)}
        self.context=codec.CodecSourceContext(self.project,self.repo,self.rev)
    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.PIPE,text=True)
    def read(self,pin=None,context='default',rev=None,sha=None):
        return codec.read_codec(pin or self.pin,rev or self.rev,sha or self.hash,self.context if context=='default' else context)
    def test_relative_project_independent_of_cwd(self):
        old=Path.cwd()
        try:
            for cwd in (self.root,self.project,self.repo,Path('/')):
                os.chdir(cwd);data,r=self.read();self.assertEqual(r['repositoryRoot'],str(self.repo));self.assertEqual(hashlib.sha256(data).hexdigest(),self.hash)
        finally:os.chdir(old)
    def test_missing_relative_context_rejected(self):
        with self.assertRaisesRegex(ValueError,'explicit authenticated'):self.read(context=None)
    def test_absolute_without_fallback(self):
        pin=dict(self.pin,localPath=str(self.repo));self.assertEqual(self.read(pin,context=None)[1]['revision'],self.rev)
    def test_missing_path_rejected(self):
        pin=dict(self.pin);del pin['localPath']
        with self.assertRaisesRegex(ValueError,'recorded source'):self.read(pin)
    def test_foreign_owner_rejected(self):
        other=self.root/'other';other.mkdir()
        with self.assertRaisesRegex(ValueError,'foreign'):self.read(context=codec.CodecSourceContext(self.project,other,self.rev))
    def test_wrong_context_revision(self):
        with self.assertRaisesRegex(ValueError,'context'):self.read(context=codec.CodecSourceContext(self.project,self.repo,'f'*40))
    def test_wrong_pin_revision(self):
        with self.assertRaisesRegex(ValueError,'source pin'):self.read(dict(self.pin,revision='f'*40))
    def test_wrong_header_hash(self):
        with self.assertRaisesRegex(ValueError,'header hash'):self.read(sha='f'*64)
    def test_wrong_repository_origin(self):
        self.git('remote','set-url','origin','https://github.com/foreign/hybridclr.git')
        with self.assertRaisesRegex(ValueError,'owning'):self.read()
    def test_wrong_pin_url(self):
        with self.assertRaisesRegex(ValueError,'source pin'):self.read(dict(self.pin,url='https://github.com/foreign/hybridclr.git'))
    def test_nested_repository_path(self):
        pin=dict(self.pin,localPath=str(self.repo/'hybridclr'))
        with self.assertRaisesRegex(ValueError,'top level'):self.read(pin,context=None)
    def test_symlink_rejected(self):
        link=self.root/'linked';link.symlink_to(self.repo,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Symlink'):self.read(dict(self.pin,localPath=str(link)),context=None)
    def test_moved_head_rejected(self):
        (self.repo/'new').write_text('x');self.git('add','.');self.git('commit','-qm','new')
        with self.assertRaisesRegex(ValueError,'HEAD'):self.read()
    def test_mutable_working_header_not_used(self):
        (self.repo/codec.HEADER).write_text('uncommitted change')
        data,_=self.read();self.assertEqual(hashlib.sha256(data).hexdigest(),self.hash)
    def test_context_forwarded_to_repeated_validators(self):
        source=(HERE.parent/'m07_results.py').read_text();tree=ast.parse(source)
        for name in ('verify_inputs','verify_patch','verify_profile2','verify_profile2_report','verify_case','verify_transaction','verify_results','verify_suite'):
            node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertIn('source_context',[a.arg for a in node.args.args])
        self.assertIn("source_context=batch.resource_context['codecContext']",(HERE/'legacy_runtime.py').read_text())


class ScopeContracts(unittest.TestCase):
    def test_exact_thirteen_reviewed_files(self):
        self.assertEqual(len(editor.REVIEWED_PACKAGE_FILES),13)
        for name in ('Build/NativeLayoutAdmissionSnapshot.cs','Metadata/EvolutionSignature.cs','Metadata/NativeLayoutAdmissionValidator.cs','Metadata/NativeLayoutIdentityContext.cs','Metadata/NativeLayoutIdentityContext.cs.meta'):
            self.assertIn('Editor/AssemblyShadow/'+name,editor.REVIEWED_PACKAGE_FILES)
    def test_real_scope_is_not_mocked_in_host(self):
        self.assertIn('editor_contract.preflight(', (HERE/'run_host.py').read_text())
        self.assertIn('editor_contract.preflight(', (HERE/'run_completion.py').read_text())
        self.assertIn('fetch-depth: 0',(HERE.parents[2]/'.github/workflows/r03-completion.yml').read_text())
    def test_extra_package_source_remains_rejected(self):
        def git(_, *args):return 'r' if args==('rev-parse','HEAD') else '\n'.join(sorted(editor.REVIEWED_PACKAGE_FILES|{'foreign.cs'}))
        with mock.patch.object(editor,'git',side_effect=git),self.assertRaisesRegex(ContractError,'additional package'):
            editor.source_scope(None,None,'r',[],resource_complete=True)
    def test_missing_reviewed_source_remains_rejected(self):
        def git(_, *args):return 'r' if args==('rev-parse','HEAD') else '\n'.join(sorted(editor.REVIEWED_PACKAGE_FILES)[1:])
        with mock.patch.object(editor,'git',side_effect=git),self.assertRaisesRegex(ContractError,'additional package'):
            editor.source_scope(None,None,'r',[],resource_complete=False)
    def test_current_tuple_before_scope(self):
        with mock.patch.object(editor,'git',return_value='wrong'),self.assertRaisesRegex(ContractError,'revision'):
            editor.source_scope(None,None,'r',[],resource_complete=False)
    def test_production_never_discards_reference_guard(self):
        self.assertIn('verify_results(root, data)',(HERE/'reference_binding.py').read_text())
        self.assertEqual(reference_binding.KINDS,['baseline','P01','P02','P03','P04','P05'])

if __name__=='__main__':unittest.main()

class CapturedSidecarContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sidecar_replay
        cls.data=sidecar_replay.cases(HERE.parents[2])
    def test_all_five_original_case_positive(self):
        checks=[layout.verify_value(*args) for _,args in self.data]
        self.assertEqual([c['mappedDeclarations'] for c in checks],[18,18,19,18,18])
    def test_original_order_remains_exact(self):
        args=copy.deepcopy(self.data[1][1]);args[0]['targetLoadOrder'].reverse()
        with self.assertRaisesRegex(ContractError,'load order'):layout.verify_value(*args)
    def test_case_only_duplicate_order_rejected(self):
        args=copy.deepcopy(self.data[1][1]);args[-1][1]=args[-1][0].upper();args[0]['targetLoadOrder']=copy.deepcopy(args[-1])
        with self.assertRaisesRegex(ContractError,'load order'):layout.verify_value(*args)
    def test_casing_not_qualified_type_alias(self):
        args=copy.deepcopy(self.data[0][1]);args[0]['identityEvidence']['compilerResolutions'][0]['canonicalKey']='same-name'
        with self.assertRaises(ContractError):layout.verify_value(*args)
    def test_foreign_compared_hash_rejected(self):
        args=copy.deepcopy(self.data[0][1]);args[0]['assemblies'][0]['targetDllSha256']='f'*64
        with self.assertRaisesRegex(ContractError,'compared DLLs'):layout.verify_value(*args)
    def test_canonical_report_case_is_accepted_without_mutating_order(self):
        args=copy.deepcopy(self.data[0][1]);original=copy.deepcopy(args[-1]);args[0]['assemblies'][0]['assembly']=original[0].upper()
        layout.verify_value(*args);self.assertEqual(original,args[-1])
    def test_source_order_case_not_rewritten(self):
        args=copy.deepcopy(self.data[0][1]);args[0]['targetLoadOrder']=[n.lower() for n in args[-1]]
        with self.assertRaisesRegex(ContractError,'load order'):layout.verify_value(*args)
    def test_actual_target_duplicate_case_rejected(self):
        args=copy.deepcopy(self.data[0][1]);r=copy.deepcopy(args[2]['assemblies'][0]);r['name']=r['name'].upper();args[2]['assemblies'].append(r)
        with self.assertRaises(ContractError):layout.verify_value(*args)
