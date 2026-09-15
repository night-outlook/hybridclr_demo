import json, sys, tempfile, types, unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import h1_compiler_actions as a

CONFIG='''#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'''

def action(src,out,debug=None,ndebug=False,feature='1'):
    args=['/usr/bin/clang++','-isysroot','/sdk','-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+feature,'-DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1']
    if debug is not None: args.append('-DIL2CPP_DEBUG='+debug)
    if ndebug: args.append('-DNDEBUG')
    args += ['-c',src,'-o',out]
    return ' '.join(args)

def graph(root, runtime_state=('1',False), bdwgc_state=(None,False), zlib_state=(None,False)):
    objs=[]; nodes=[]
    specs=[('runtime/a.cpp','a.o',*runtime_state),('runtime/b.cpp','b.o',*runtime_state),
           ('libil2cpp/external/bdwgc/gc.c','gc.o',*bdwgc_state),('libil2cpp/external/zlib/adler32.c','z.o',*zlib_state)]
    for src,out,debug,ndebug in specs:
        s=str(root/src); o=str(root/out); objs.append(o)
        nodes.append({'Annotation':'C_Mac_arm64 '+o,'Action':action(s,o,debug,ndebug),'Inputs':[s], 'Outputs':[o]})
    game=str(root/'GameAssembly.dylib')
    nodes.append({'Annotation':'Link_Mac_arm64 '+game,'Action':'/usr/bin/clang++ -isysroot /sdk '+' '.join(objs)+' -o '+game,
                  'Inputs':objs,'Outputs':[game]})
    return {'Nodes':nodes}, Path(game)

class MacroDomainTests(unittest.TestCase):
    def test_source_owned_domains_accept_apple_split(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            result=a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
            self.assertEqual(('1','0','0'),(result['il2cppDebug'],result['ndebug'],result['il2cppDevelopment']))
            self.assertEqual({'runtime','bdwgc','zlib'},{r['domain'] for r in result['macroDomains']})
            self.assertEqual(4,sum(r['count'] for r in result['macroDomains']))
    def test_release_runtime_profile_is_independent_of_external_domains(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root,runtime_state=('0',True))
            result=a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
            self.assertEqual(('0','1','0'),(result['il2cppDebug'],result['ndebug'],result['il2cppDevelopment']))
    def test_runtime_domain_still_fails_on_mixed_debug_state(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            g['Nodes'][1]['Action']=action(str(root/'runtime/b.cpp'),str(root/'b.o'),'0',False)
            with self.assertRaisesRegex(a.CompilerActionError,'inside macro domain: runtime'):
                a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
    def test_bdwgc_domain_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            src=str(root/'libil2cpp/external/bdwgc/extra.c'); out=str(root/'gc2.o')
            g['Nodes'].insert(-1,{'Annotation':'C_Mac_arm64 '+out,'Action':action(src,out,'1',False),'Inputs':[src],'Outputs':[out]})
            g['Nodes'][-1]['Inputs'].append(out); g['Nodes'][-1]['Action']=g['Nodes'][-1]['Action'].replace(' -o '+str(native),' '+out+' -o '+str(native))
            with self.assertRaisesRegex(a.CompilerActionError,'inside macro domain: bdwgc'):
                a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
    def test_zlib_domain_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            src=str(root/'libil2cpp/external/zlib/extra.c'); out=str(root/'z2.o')
            g['Nodes'].insert(-1,{'Annotation':'C_Mac_arm64 '+out,'Action':action(src,out,'1',False),'Inputs':[src],'Outputs':[out]})
            g['Nodes'][-1]['Inputs'].append(out); g['Nodes'][-1]['Action']=g['Nodes'][-1]['Action'].replace(' -o '+str(native),' '+out+' -o '+str(native))
            with self.assertRaisesRegex(a.CompilerActionError,'inside macro domain: zlib'):
                a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
    def test_external_actions_must_feed_selected_link(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            dead=str(root/'z.o'); g['Nodes'][-1]['Inputs'].remove(dead); g['Nodes'][-1]['Action']=g['Nodes'][-1]['Action'].replace(' '+dead,'')
            with self.assertRaisesRegex(a.CompilerActionError,'does not feed the selected GameAssembly link'):
                a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)
    def test_feature_define_required_in_every_domain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); g,native=graph(root)
            g['Nodes'][2]['Action']=g['Nodes'][2]['Action'].replace('-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1','')
            with self.assertRaisesRegex(a.CompilerActionError,'lacks the requested Shadow/count-diagnostic defines'):
                a.derive_graph_evidence(g,root,native,CONFIG,expected_feature=True)

if __name__=='__main__': unittest.main()
