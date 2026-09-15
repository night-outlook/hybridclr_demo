from pathlib import Path
p=Path('Tools/AssemblyShadow/tests/test_h1_apple_macro_domains.py')
text=p.read_text()
old='''    def test_generated_lump_is_runtime_owned(self):
        root,g=self.graph(); runtime=g['Nodes'][0]; old=runtime['Inputs'][0]; generated=str(root/'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/hash/abc.lump.cpp'); runtime['Inputs']=[generated]; runtime['Action']=runtime['Action'].replace(old,generated)
        result=self.derive(g); self.assertEqual(1,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])
'''
new='''    def test_generated_lump_is_runtime_owned(self):
        root,g=self.graph(); generated=str(root/'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/hash/abc.lump.cpp')
        node={'Annotation':'C_Mac_arm64 lump.o','Action':f'/tool/clang++ -isysroot /sdk -DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1 -DHYBRIDCLR_H1_COUNT_DIAGNOSTICS=1 -DIL2CPP_DEBUG=1 -c -x c++ "{generated}" -o lump.o','Inputs':[generated],'Outputs':['lump.o']}
        g['Nodes'].insert(4,node); g['Nodes'][5]['Inputs'].append('lump.o')
        result=self.derive(g); self.assertEqual(2,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])
'''
if text.count(old)!=1: raise SystemExit('generated lump test anchor changed')
p.write_text(text.replace(old,new,1))
