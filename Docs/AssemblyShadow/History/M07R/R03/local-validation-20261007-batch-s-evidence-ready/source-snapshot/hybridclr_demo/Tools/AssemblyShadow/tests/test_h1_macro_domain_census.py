import copy
from pathlib import Path
import unittest
from h1_macro_domain_census import inventory


class MacroCensusTests(unittest.TestCase):
    def graph(self):
        return {'Nodes': [
            {'Annotation': 'C_Mac_arm64', 'Action': '/clang -c source.c -o out.o', 'Inputs': ['source.c'], 'Outputs': ['out.o']},
            {'Annotation': 'Link_Mac_arm64', 'Action': '/clang out.o -o GameAssembly.dylib', 'Inputs': ['out.o'], 'Outputs': ['GameAssembly.dylib']},
            {'Annotation': 'Copy', 'Inputs': ['GameAssembly.dylib'], 'Outputs': ['build/GameAssembly.dylib']}]}
    def run_census(self, graph): return inventory(graph, Path('/project'), Path('/project/build/GameAssembly.dylib'))
    def test_complete_original_node_and_declared_path(self):
        g = self.graph(); r = self.run_census(g)
        self.assertEqual(g['Nodes'][0], r['rows'][0]['rawNode'])
        self.assertEqual([0,1,2], r['rows'][0]['declaredPathToSelectedOutput'])
    def test_graph_not_mutated(self):
        g = self.graph(); before = copy.deepcopy(g); self.run_census(g); self.assertEqual(before,g)
    def test_explicit_node_edge_reported(self):
        g = self.graph(); g['Nodes'][1]['Inputs'] = []; g['Nodes'][1]['Deps'] = [0]
        self.assertEqual([0,1,2], self.run_census(g)['rows'][0]['declaredPathToSelectedOutput'])
    def test_missing_edge_not_inferred_from_command(self):
        g = self.graph(); g['Nodes'][1]['Inputs'] = []
        self.assertEqual([], self.run_census(g)['rows'][0]['declaredPathToSelectedOutput'])
    def test_ambiguous_producer_reported_not_chosen(self):
        g = self.graph(); g['Nodes'].append({'Annotation':'other','Outputs':['out.o']})
        r = self.run_census(g); self.assertEqual([],r['rows'][0]['declaredPathToSelectedOutput'])
        self.assertEqual(1,len(r['ambiguousOutputOwners']))
    def test_dependency_cycle_terminates(self):
        g = self.graph(); g['Nodes'][0]['Deps'] = [1]
        self.assertEqual([0,1,2],self.run_census(g)['rows'][0]['declaredPathToSelectedOutput'])
    def test_invalid_argument_retains_raw_action(self):
        g=self.graph(); g['Nodes'][0]['Action']='/clang "'; r=self.run_census(g)
        self.assertIn('argumentError',r['rows'][0]); self.assertEqual('/clang "',r['rows'][0]['rawNode']['Action'])
    def test_boolean_dependency_not_index(self):
        g=self.graph(); g['Nodes'][1]['Deps']=[False]; self.assertTrue(self.run_census(g)['graphErrors'])
    def test_counts_do_not_authorize_exemptions(self):
        g=self.graph(); units=[]
        for i in range(446):
            u=copy.deepcopy(g['Nodes'][0]);u['Action']='/clang -c unit%d.%s -o unit%d.o -DIL2CPP_DEBUG=%d'%(i,'c' if i<16 else 'cpp',i,0 if i<16 else 1)
            u['Inputs']=['unit%d.cpp'%i];u['Outputs']=['unit%d.o'%i];units.append(u)
        link=copy.deepcopy(g['Nodes'][1]);link['Inputs']=[u['Outputs'][0] for u in units]
        r=self.run_census({'Nodes':units+[link,g['Nodes'][2]]})
        self.assertEqual(446,r['compileActionCount']);self.assertFalse(r['domainPolicyChanged'])
        self.assertEqual({'NotClassifiedRequiresPrimaryReview'},{row['domainDecision'] for row in r['rows']})
    def test_no_native_output_owner_is_not_successful_relation(self):
        g=self.graph(); g['Nodes'][2]['Outputs']=[]
        self.assertEqual([],self.run_census(g)['rows'][0]['declaredPathToSelectedOutput'])
