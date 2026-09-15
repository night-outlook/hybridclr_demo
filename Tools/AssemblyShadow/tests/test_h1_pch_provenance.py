"""PCH contract tests. Tiny real Clang fixtures are not Unity/Player evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import h1_compiler_actions as a
import h1_pch_provenance as p

CONFIG = '#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'
FLAGS = '-isysroot / -DIL2CPP_DEBUG=1 -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1'


def graph(root, compiler='/tool/clang'):
    return {'Nodes': [
        {'Annotation': 'C_Mac_arm64Pch fixture', 'Action': f'{compiler} {FLAGS} -x c-header -Xclang -fno-pch-timestamp p.h -o p.pch', 'Inputs': ['p.h', compiler], 'Outputs': ['p.pch']},
        {'Annotation': 'C_Mac_arm64 unit', 'Action': f'{compiler} {FLAGS} -include-pch p.pch -c u.c -o u.o', 'Inputs': ['u.c', 'p.pch'], 'Outputs': ['u.o']},
        {'Annotation': 'Link_Mac_arm64', 'Action': f'{compiler} -isysroot /', 'Inputs': ['u.o'], 'Outputs': ['GameAssembly.dylib']},
    ]}


class PchPlanTests(unittest.TestCase):
    def setUp(self):
        self.root = Path('/project'); self.g = graph(self.root)
    def plan(self): return p.plan(self.g, self.root, self.root/'GameAssembly.dylib', CONFIG, {}, True)
    def test_valid_declared_file_dependency_and_grouping(self):
        r = self.plan(); self.assertEqual(1,len(r['producers'])); self.assertEqual(1,len(r['consumers']));self.assertEqual(1,len(r['groups']))
    def test_declared_node_dependency_without_file_edge(self):
        self.g['Nodes'][1]['Inputs']=['u.c'];self.g['Nodes'][1]['Deps']=[0]
        self.assertEqual('declared-node-path',self.plan()['consumers'][0]['dependency']['kind'])
    def test_no_edge_is_not_inferred_from_command_line(self):
        self.g['Nodes'][1]['Inputs']=['u.c']
        with self.assertRaisesRegex(ValueError,'dependency'):self.plan()
    def test_unknown_pch_rejected(self):
        self.g['Nodes'][1]['Action']=self.g['Nodes'][1]['Action'].replace('p.pch','other.pch')
        with self.assertRaisesRegex(ValueError,'not produced'):self.plan()
    def test_duplicate_producer_rejected(self):
        self.g['Nodes'].append(copy.deepcopy(self.g['Nodes'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.plan()
    def test_copy_node_cannot_replace_producer_output(self):
        self.g['Nodes'].append({'Annotation':'Copy','Outputs':['p.pch']})
        with self.assertRaisesRegex(ValueError,'another graph producer'):self.plan()
    def test_output_mismatch(self):
        self.g['Nodes'][0]['Outputs']=['other.pch']
        with self.assertRaisesRegex(ValueError,'-o differs'):self.plan()
    def test_source_mismatch(self):
        self.g['Nodes'][0]['Inputs']=['wrong.h']
        with self.assertRaisesRegex(ValueError,'source absent'):self.plan()
    def test_forbidden_forced_routes(self):
        for route in ['-include x.h','-imacros x.h','-Wp,-DIL2CPP_DEBUG=0','-Xpreprocessor -DXX=1','-Xclang -ignore-pch','-Xclang -fno-validate-pch','-fmodules','-ivfsoverlay x.json','--config=x','-fplugin=x.so']:
            with self.subTest(route=route):
                self.g=graph(self.root); self.g['Nodes'][1]['Action']+=' '+route
                with self.assertRaises(ValueError):self.plan()
    def test_duplicate_pch_rejected(self):
        self.g['Nodes'][1]['Action']+=' -include-pch p.pch'
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.plan()
    def test_producer_cannot_chain_pch(self):
        self.g['Nodes'][0]['Action']+=' -include-pch p.pch'
        with self.assertRaisesRegex(ValueError,'chained'):self.plan()
    def test_ordered_undef_is_not_accepted(self):
        self.g['Nodes'][1]['Action']+=' -UHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW'
        with self.assertRaisesRegex(ValueError,'requested'):self.plan()
    def test_unique_contexts_not_merged_by_pch_alone(self):
        other=copy.deepcopy(self.g['Nodes'][1]);other['Action']=other['Action'].replace('u.c','v.c').replace('u.o','v.o')+' -DOTHER=2';other['Inputs']=['v.c','p.pch'];other['Outputs']=['v.o'];self.g['Nodes'].append(other)
        self.assertEqual(2,len(self.plan()['groups']))
    def test_legacy_parser_still_rejects_pch_without_proof(self):
        with self.assertRaisesRegex(ValueError,'Forced'):a.derive_graph_evidence(self.g,self.root,self.root/'GameAssembly.dylib',CONFIG,{},expected_feature=True)
    def test_response_input_closure_is_retained(self):
        self.g['Nodes'][1]['Action']=self.g['Nodes'][1]['Action'].replace('-include-pch p.pch','@pch.rsp')
        r=p.plan(self.g,self.root,self.root/'GameAssembly.dylib',CONFIG,{'/project/pch.rsp':b'-include-pch p.pch'},True)
        self.assertEqual(['/project/pch.rsp'],r['derived']['responseSources'])
    def test_all_unsupported_actions_are_reported_together(self):
        for n in self.g['Nodes'][:2]:n['Action']+=' -unknown-pch-setting'
        with self.assertRaises(ValueError) as e:self.plan()
        self.assertIn('"nodeIndex": 0',str(e.exception));self.assertIn('"nodeIndex": 1',str(e.exception))
    def test_macro_dump_ndebug_definedness(self):
        raw=b'#define IL2CPP_DEBUG 1\n#define NDEBUG 0\n#define IL2CPP_DEVELOPMENT 0\n#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1\n#define HYBRIDCLR_H1_COUNT_DIAGNOSTICS 1\n'
        self.assertEqual('1',p.dump_state(raw)['NDEBUG'])
    def test_missing_macro_dump_is_not_inferred_from_intent(self):
        with self.assertRaises(ValueError):p.dump_state(b'')
    def test_unrecognized_pch_inventory_fails(self):
        with self.assertRaises(ValueError):p.pch_headers(b'compiler error',self.root)
    def test_pch_inventory_unsupported_override_rejected(self):
        with self.assertRaises(ValueError):p.pch_headers(b'Information for module file\n Input file: /a.h [Overridden]\n',self.root)


CLANG=shutil.which('clang')
@unittest.skipUnless(CLANG,'Real Clang is unavailable (not a Unity substitute)')
class PchClangTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.compiler=CLANG; self.config=self.root/'il2cpp-config.h';self.config.write_text(CONFIG)
        (self.root/'p.h').write_text('#include "il2cpp-config.h"\n#define PCH_VALUE 7\n')
        (self.root/'u.c').write_text('int value = PCH_VALUE;\n')
        self.g=graph(self.root,self.compiler)
        self.compile_command(a.split(self.g['Nodes'][0]['Action']));self.compile_command(a.split(self.g['Nodes'][1]['Action']))
        self.binding={'buildId':'H1Count-On-Debug','buildGuid':'a'*32,'inputSnapshotHash':'b'*64,'nativeLibrarySha256':'c'*64,'sourcePinSha256':'d'*64,'graphSha256':p.sha(p.canonical(self.g)),'projectRoot':str(self.root),'featureEnabled':True,'cppConfiguration':'Debug'}
        self.blueprint=p.plan(self.g,self.root,self.root/'GameAssembly.dylib',CONFIG,{},True)
        self.proof=p.capture(self.blueprint,self.g,self.root,str(self.config),self.binding,self.root/'proof')
    def tearDown(self):self.temp.cleanup()
    def compile_command(self,cmd):
        subprocess.run(cmd,cwd=self.root,capture_output=True,check=True,timeout=30)
    def verify(self,proof=None,g=None):
        return p.verify(proof or self.proof,g or self.g,self.root,self.root/'GameAssembly.dylib',CONFIG,{},self.binding)
    def test_real_pch_and_probe_roundtrip(self):
        self.assertEqual(2,self.verify()['compileActionCount'])
        self.assertIn('PCH_VALUE',p.load_row(self.proof['groups'][0]['macros']['stdout']).decode())
    def test_pch_byte_tamper_rejected(self):
        Path(self.proof['producers'][0]['pch']['retainedPath']).write_bytes(b'bad-pch')
        with self.assertRaises(ValueError):self.verify()
    def test_source_header_tamper_rejected(self):
        Path(self.proof['producers'][0]['headers'][0]['retainedPath']).write_bytes(b'bad-header')
        with self.assertRaises(ValueError):self.verify()
    def test_changed_producer_args_rejected(self):
        self.g['Nodes'][0]['Action']+=' -DNEW=1'
        with self.assertRaises(ValueError):self.verify()
    def test_changed_producer_input_rejected(self):
        self.g['Nodes'][0]['Inputs'].append('unrecorded.h')
        with self.assertRaises(ValueError):self.verify()
    def test_changed_dependency_rejected(self):
        self.g['Nodes'][1]['Inputs'].remove('p.pch')
        with self.assertRaises(ValueError):self.verify()
    def test_rebound_build_guid_rejected(self):
        self.binding['buildGuid']='f'*32
        with self.assertRaises(ValueError):self.verify()
    def test_edited_probe_source_even_with_rehashed_row_rejected(self):
        row=self.proof['groups'][0]['source'];raw=b'int bypass;\n';Path(row['retainedPath']).write_bytes(raw);row['bytes']=len(raw);row['sha256']=p.sha(raw)
        with self.assertRaisesRegex(ValueError,'assertion source'):self.verify()
    def test_edited_macro_output_even_with_rehashed_row_rejected(self):
        row=self.proof['groups'][0]['macros']['stdout'];raw=p.load_row(row).replace(b'#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1',b'#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 0');Path(row['retainedPath']).write_bytes(raw);row['bytes']=len(raw);row['sha256']=p.sha(raw)
        with self.assertRaisesRegex(ValueError,'macro output'):self.verify()
    def test_missing_context_rejected(self):
        self.proof['groups']=[]
        with self.assertRaises(ValueError):self.verify()
    def test_compiler_invocation_must_include_the_pch(self):
        self.proof['groups'][0]['syntax']['argv'].remove('-include-pch')
        with self.assertRaises(ValueError):self.verify()
    def test_archive_reader_does_not_require_original_live_paths(self):
        artifacts={}
        def visit(x):
            if isinstance(x,dict):
                if 'retainedPath' in x:artifacts[x['retainedPath']]=p.load_row(x)
                for v in x.values():visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        visit(self.proof)
        shutil.rmtree(self.root/'proof')
        p.verify(self.proof,self.g,self.root,self.root/'GameAssembly.dylib',CONFIG,{},self.binding,read=lambda row:artifacts[row['retainedPath']])
    def test_actual_header_macro_drift_fails_capture(self):
        (self.root/'p.h').write_text('#include "il2cpp-config.h"\n#undef HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\n#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 0\n#define PCH_VALUE 7\n')
        self.compile_command(a.split(self.g['Nodes'][0]['Action']))
        with self.assertRaisesRegex(ValueError,'diagnostic failed'):
            p.capture(self.blueprint,self.g,self.root,str(self.config),self.binding,self.root/'drift')
        self.assertTrue(list((self.root/'drift').glob('*.stderr')))


if __name__=='__main__':unittest.main()
