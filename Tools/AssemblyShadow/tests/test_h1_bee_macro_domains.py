"""Authenticated Apple graph regressions; planning is not Player acceptance."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

import h1_bee_fixture_export as fixture
import h1_bee_macro_domains as d
import h1_compiler_actions as a
import h1_pch_provenance as p


class AppleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        explicit = os.environ.get('H1_BEE_FIXTURE_DIR')
        cls.temp = None
        if explicit:
            cls.folder = Path(explicit)
        else:
            root = Path(__file__).resolve().parents[3]
            if not (root / fixture.ARCHIVE).is_file():
                raise unittest.SkipTest('Authenticated Apple archive unavailable; set H1_BEE_FIXTURE_DIR to its exported fixture')
            cls.temp = tempfile.TemporaryDirectory()
            cls.folder = Path(cls.temp.name) / 'fixture'
            with contextlib.redirect_stdout(io.StringIO()):
                fixture.export(root, cls.folder)
        cls.index = json.loads((cls.folder / 'fixture-index.json').read_text())
        if cls.index['archiveSha256'] != fixture.EXPECTED or cls.index['graphSha256'] != fixture.GRAPH:
            raise ValueError('Fixture identity mismatch')
        for row in cls.index['files']:
            raw = (cls.folder / 'members' / row['sha256']).read_bytes()
            if p.sha(raw) != row['sha256'] or len(raw) != row['bytes']:
                raise ValueError('Authenticated member changed')
        raw = (cls.folder / 'bee-action-graph.json').read_bytes()
        if p.sha(raw) != fixture.GRAPH: raise ValueError('Raw graph changed')
        cls.raw_graph = json.loads(raw)
        manifest = next(x for x in cls.index['files'] if x['member'].endswith('/failure-input-manifest.json'))
        cls.manifest = json.loads((cls.folder / 'members' / manifest['sha256']).read_text())
        cls.root = Path(cls.manifest['projectRoot'])
        cls.native = Path(cls.manifest['nativeLibrary']['sourcePath'])
        cls.config = (cls.folder / 'members' / cls.manifest['config']['sha256']).read_text()
    @classmethod
    def tearDownClass(cls):
        if cls.temp: cls.temp.cleanup()
    def setUp(self): self.graph = copy.deepcopy(self.raw_graph)
    def plan(self): return p.plan(self.graph, self.root, self.native, self.config, {}, True)
    def reject(self, pattern=None):
        with self.assertRaisesRegex(ValueError, pattern or '.'):
            self.plan()
    def test_actual_446_actions_are_exhaustively_classified_and_linked(self):
        result = self.plan(); derived = result['derived']
        self.assertEqual(446, derived['compileActionCount'])
        self.assertEqual(444, len(derived['linkage']['objectUnitIndices']))
        self.assertEqual({'il2cpp-runtime': 430, 'external-bdwgc': 2, 'external-zlib': 14},
                         {x['id']: len(x['unitIndices']) for x in derived['macroDomains']})
        self.assertEqual(446, sum(len(g['unitIndices']) for g in result['groups']))
        self.assertEqual(6, len(result['groups']))
        self.assertEqual([669, 674], [e['nodeIndex'] for e in derived['linkage']['postLinkFileEdges']])
        p.require_profile(result, 'Debug')
    def test_brotli_and_generated_C_are_not_exempted(self):
        units = {r['nodeIndex']: r for r in self.plan()['units']}
        for i in list(range(328,357)) + [666]:
            self.assertEqual(d.RUNTIME, units[i]['macroDomain'])
    def test_external_probes_do_not_inject_IL2CPP_configuration(self):
        blueprint = self.plan()
        for group in blueprint['groups']:
            expected = p.group_expectation(blueprint, group)
            if group['macroDomain'] != d.RUNTIME:
                self.assertIsNone(expected['IL2CPP_DEBUG'])
                source = p.probe_source(None, expected)
                self.assertNotIn(b'#include', source)
                self.assertIn(b'#ifdef IL2CPP_DEBUG', source)
    def test_runtime_C_mixed_profile_is_rejected_not_moved_to_external(self):
        self.graph['Nodes'][328]['Action'] += ' -DIL2CPP_DEBUG=0'
        self.reject('within macro domain')
    def test_runtime_cpp_mixed_profile_rejected(self):
        self.graph['Nodes'][236]['Action'] += ' -DIL2CPP_DEBUG=0'
        self.reject('within macro domain')
    def test_uniform_wrong_runtime_profile_still_fails_requested_mode(self):
        for n in self.graph['Nodes']:
            if str(n.get('Annotation','')).startswith('C_Mac_arm64'):
                n['Action'] = n['Action'].replace('-DIL2CPP_DEBUG=1','-DIL2CPP_DEBUG=0')
        with self.assertRaisesRegex(ValueError, 'requested configuration'):
            p.require_profile(self.plan(), 'Debug')
    def test_bdwgc_mixed_assertion_state_rejected(self):
        self.graph['Nodes'][151]['Action'] += ' -DNDEBUG=0'
        self.reject('within macro domain')
    def test_zlib_own_uniform_assertion_state_is_recorded_not_runtime_evidence(self):
        for i in range(154,168): self.graph['Nodes'][i]['Action'] += ' -DNDEBUG=0'
        result=self.plan();p.require_profile(result,'Debug')
        rows={r['id']:r for r in result['derived']['macroDomains']}
        self.assertEqual('1',rows['external-zlib']['expectedMacros']['NDEBUG'])
        self.assertEqual('0',rows[d.RUNTIME]['expectedMacros']['NDEBUG'])
    def test_zlib_mixed_assertion_state_rejected(self):
        self.graph['Nodes'][154]['Action'] += ' -DNDEBUG=0'
        self.reject('within macro domain')
    def test_external_IL2CPP_DEBUG_definition_is_not_header_absence(self):
        self.graph['Nodes'][154]['Action'] += ' -DIL2CPP_DEBUG=0'
        self.reject('ownership')
    def test_external_development_definition_rejected(self):
        self.graph['Nodes'][151]['Action'] += ' -DIL2CPP_DEVELOPMENT=0'
        self.reject('ownership')
    def test_external_feature_flag_is_mandatory(self):
        self.graph['Nodes'][151]['Action'] += ' -UHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW'
        self.reject('requested')
    def test_external_count_flag_is_mandatory(self):
        self.graph['Nodes'][154]['Action'] += ' -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=0'
        self.reject('requested')
    def test_runtime_feature_flag_is_mandatory(self):
        self.graph['Nodes'][236]['Action'] += ' -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0'
        self.reject('requested')
    def test_arbitrary_external_C_source_is_not_allowed(self):
        n = self.graph['Nodes'][154]
        n['Action'] = n['Action'].replace('zlib/adler32.c','zlib/unknown.c')
        n['Inputs'][0] = n['Inputs'][0].replace('zlib/adler32.c','zlib/unknown.c')
        self.reject('Unreviewed external')
    def test_case_sensitive_external_membership(self):
        n = self.graph['Nodes'][154]
        n['Action'] = n['Action'].replace('zlib/adler32.c','zlib/Adler32.c')
        n['Inputs'][0] = n['Inputs'][0].replace('zlib/adler32.c','zlib/Adler32.c')
        self.reject('Unreviewed external')
    def test_project_C_is_runtime_not_exempt_by_language_or_macros(self):
        n = self.graph['Nodes'][154]; old=n['Inputs'][0]; new=str(self.root/'Assets/plugin.c')
        n['Action'] = n['Action'].replace(old,new);n['Inputs'][0]=new
        self.reject('within macro domain')
    def test_external_pch_consumption_is_not_allowed(self):
        node=self.graph['Nodes'][154];pch=self.graph['Nodes'][358]['Outputs'][0]
        node['Action'] += ' -include-pch '+pch;node['Inputs'].append(pch)
        self.reject('without a forced PCH')
    def test_changed_compiler_rejected(self):
        self.graph['Nodes'][154]['Action']=self.graph['Nodes'][154]['Action'].replace('/usr/bin/clang++','/usr/bin/other-clang')
        self.reject('identities disagree')
    def test_relative_compiler_cannot_resolve_through_ambient_PATH(self):
        self.graph['Nodes'][154]['Action']=self.graph['Nodes'][154]['Action'].replace('/Library/Developer/CommandLineTools/usr/bin/clang++','clang++')
        self.reject('explicit absolute path')
    def test_changed_sdk_rejected(self):
        self.graph['Nodes'][154]['Action']=self.graph['Nodes'][154]['Action'].replace('MacOSX26.sdk','Different.sdk')
        self.reject('identities disagree')
    def test_compiler_environment_override_rejected(self):
        self.graph['Nodes'][154]['Env']=[{'Key':'CPATH','Value':'/tmp/other'}]
        self.reject('environment')
    def test_link_environment_override_rejected(self):
        self.graph['Nodes'][667]['Env']=[{'Key':'SDKROOT','Value':'/tmp/other'}]
        self.reject('environment')
    def test_link_input_removal_rejected(self):
        self.graph['Nodes'][667]['Inputs'].remove(self.graph['Nodes'][151]['Outputs'][0])
        self.reject('coverage differs')
    def test_link_argv_removal_rejected(self):
        value=self.graph['Nodes'][151]['Outputs'][0]
        self.graph['Nodes'][667]['Action']=self.graph['Nodes'][667]['Action'].replace('"'+value+'"','')
        self.reject('coverage differs')
    def test_disconnected_compile_action_is_not_ignored(self):
        value=self.graph['Nodes'][151]['Outputs'][0]
        self.graph['Nodes'][667]['Inputs'].remove(value)
        self.graph['Nodes'][667]['Action']=self.graph['Nodes'][667]['Action'].replace('"'+value+'"','')
        self.reject('coverage differs')
    def test_extra_object_link_input_rejected(self):
        self.graph['Nodes'][667]['Inputs'].append('unproven.o')
        self.graph['Nodes'][667]['Action']+=' unproven.o'
        self.reject('coverage differs')
    def test_duplicate_object_input_rejected(self):
        self.graph['Nodes'][667]['Inputs'].append(self.graph['Nodes'][151]['Outputs'][0])
        self.reject('coverage differs')
    def test_duplicate_object_producer_rejected(self):
        self.graph['Nodes'].append(copy.deepcopy(self.graph['Nodes'][151]))
        self.reject('Duplicate object')
    def test_link_output_argument_mismatch_rejected(self):
        node=self.graph['Nodes'][667]
        node['Action']=node['Action'].replace(node['Outputs'][0],'wrong/GameAssembly.dylib')
        self.reject('Link -o')
    def test_output_copy_edge_removal_rejected(self):
        self.graph['Nodes'][674]['Inputs']=[]
        self.reject('does not reach')
    def test_annotation_display_names_do_not_select_domains(self):
        for n in self.graph['Nodes']: n['DisplayName']='UNTRUSTED display';n['DebugActionIndex']=0
        self.assertEqual([2,14,430],[len(x['unitIndices']) for x in self.plan()['derived']['macroDomains']])
    def test_release_intent_ndebug_zero_counts_as_defined(self):
        for n in self.graph['Nodes']:
            if str(n.get('Annotation','')).startswith('C_Mac_arm64'):
                n['Action']=n['Action'].replace('-DIL2CPP_DEBUG=1','-DIL2CPP_DEBUG=0')+' -DNDEBUG=0'
        blueprint=self.plan();p.require_profile(blueprint,'Release')
        self.assertTrue(all(x['expectedMacros']['NDEBUG']=='1' for x in blueprint['derived']['macroDomains']))
    def test_forced_routes_still_fail_for_external_domain(self):
        for flag in ('-include evil.h','-imacros evil.h','-Xpreprocessor -DEVIL','-Wp,-DEVIL','-Xclang -load'):
            with self.subTest(flag=flag):
                self.graph=copy.deepcopy(self.raw_graph);self.graph['Nodes'][154]['Action']+=' '+flag;self.reject('Forbidden')
    def test_old_proof_schema_cannot_assert_new_domain_coverage(self):
        with self.assertRaisesRegex(ValueError,'Unsupported PCH proof'):
            p.verify({'schemaVersion':1,'kind':'H1PchProvenance'},self.graph,self.root,self.native,self.config,{}, {})


if __name__ == '__main__': unittest.main()
