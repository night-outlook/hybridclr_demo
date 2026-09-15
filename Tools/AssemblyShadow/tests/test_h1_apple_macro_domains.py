import unittest
from pathlib import Path
import h1_compiler_actions as h
import h1_pch_provenance as pch
CONFIG='#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'
class Tests(unittest.TestCase):
    def graph(self,release=False):
        root=Path('/project'); base=root/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp'; sources=[base/'libil2cpp/vm/A.cpp',base/'external/bdwgc/extra/gc.c',base/'external/zlib/adler32.c',base/'external/zlib/crc32.c']; runtime='-DNDEBUG=1' if release else '-DIL2CPP_DEBUG=1'; nodes=[]
        for i,src in enumerate(sources):
            out=f'o{i}.o'; flag=runtime if i==0 else ''; lang='c++' if i==0 else 'c'; nodes.append({'Annotation':'C_Mac_arm64 '+out,'Action':f'/tool/clang++ -isysroot /sdk -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1 {flag} -c -x {lang} "{src}" -o {out}','Inputs':[str(src)],'Outputs':[out]})
        nodes += [{'Annotation':'Link_Mac_arm64','Action':'/tool/clang++ -isysroot /sdk','Inputs':[f'o{i}.o' for i in range(4)],'Outputs':['Library/GameAssembly.dylib']},{'Annotation':'Copy','Inputs':['Library/GameAssembly.dylib'],'Outputs':['Build/GameAssembly.dylib']}]; return root,{'Nodes':nodes}
    def derive(self,g,release=False): root,_=self.graph(release); return h.derive_graph_evidence(g,root,root/'Build/GameAssembly.dylib',CONFIG,{},expected_feature=True,domain_policy=h.H1_APPLE_BEE_DOMAIN_POLICY)
    def test_split(self): _,g=self.graph(); r=self.derive(g); self.assertEqual({'runtime':1,'bdwgc':1,'zlib':2},{x['name']:x['unitCount'] for x in r['macroDomains']}); self.assertEqual(('1','0'),(r['il2cppDebug'],r['ndebug']))
    def test_release(self): _,g=self.graph(True); r=self.derive(g,True); self.assertEqual(('0','1'),(r['il2cppDebug'],r['ndebug']))
    def test_generated_lump_is_runtime_owned(self):
        root,g=self.graph(); generated=str(root/'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/hash/abc.lump.cpp')
        node={'Annotation':'C_Mac_arm64 lump.o','Action':f'/tool/clang++ -isysroot /sdk -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1 -DIL2CPP_DEBUG=1 -c -x c++ "{generated}" -o lump.o','Inputs':[generated],'Outputs':['lump.o']}
        g['Nodes'].insert(4,node); g['Nodes'][5]['Inputs'].append('lump.o')
        result=self.derive(g); self.assertEqual(2,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])
    def test_pch_header_input_is_not_translation_unit(self):
        root,g=self.graph(); runtime=g['Nodes'][0]; runtime['Inputs'].append(str(root/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp/pch/pch-cpp.hpp'))
        result=self.derive(g); self.assertEqual(1,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])
    def test_aux_mismatch_rejected(self):
        _,g=self.graph(); g['Nodes'][3]['Action']=g['Nodes'][3]['Action'].replace(' -c ',' -DIL2CPP_DEBUG=1 -c ')
        with self.assertRaisesRegex(ValueError,'domain disagrees internally'): self.derive(g)
    def test_unknown_rejected(self):
        _,g=self.graph(); old='/project/HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/external/zlib/adler32.c'; g['Nodes'][2]['Inputs']=['/other/adler32.c']; g['Nodes'][2]['Action']=g['Nodes'][2]['Action'].replace(old,'/other/adler32.c')
        with self.assertRaisesRegex(ValueError,'Unreviewed Apple'): self.derive(g)
    def test_link_relation_required(self):
        _,g=self.graph(); g['Nodes'][4]['Inputs'].remove('o2.o')
        with self.assertRaisesRegex(ValueError,'direct input'): self.derive(g)
    def test_committed_apple_failure_graph_is_430_2_14(self):
        import hashlib,json,tarfile
        repo=Path(__file__).resolve().parents[3]
        archive=repo/'Documents/AgentHandoff/local-validation-20260914-bec2bd1/fresh-smoke-failure-inputs.tar.gz'
        raw=archive.read_bytes(); self.assertEqual('e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8',hashlib.sha256(raw).hexdigest())
        graph=None; config=None; graph_sha='dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181'
        with tarfile.open(archive,'r:gz') as tf:
            for member in tf.getmembers():
                if not member.isfile(): continue
                data=tf.extractfile(member).read()
                if hashlib.sha256(data).hexdigest()==graph_sha: graph=json.loads(data.decode('utf-8-sig'))
                if member.name.endswith('/il2cpp-config.h'): config=data.decode('utf-8')
        self.assertIsNotNone(graph); self.assertIsNotNone(config)
        project=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo')
        link=next(node for node in graph['Nodes'] if str(node.get('Annotation','')).startswith('Link_Mac_arm64'))
        native=Path(h.resolve(project,next(value for value in link['Outputs'] if Path(value).name=='GameAssembly.dylib')))
        result=pch.plan(graph,project,native,config,{},True,h.H1_APPLE_BEE_DOMAIN_POLICY)['derived']
        self.assertEqual({'runtime':430,'bdwgc':2,'zlib':14},{row['name']:row['unitCount'] for row in result['macroDomains']})
        self.assertEqual(('1','0','0'),(result['il2cppDebug'],result['ndebug'],result['il2cppDevelopment']))

if __name__=='__main__': unittest.main()
