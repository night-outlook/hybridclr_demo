from pathlib import Path


def replace(path, old, new, count=1):
    p=Path(path); text=p.read_text(); actual=text.count(old)
    if actual != count: raise SystemExit(f'{path}: expected {count}, got {actual}: {old[:140]!r}')
    p.write_text(text.replace(old,new,count))

path='Tools/AssemblyShadow/h1_compiler_actions.py'
old='''    candidates = [resolve(project_root, value) for value in node.get("Inputs", [])
                  if type(value) is str and Path(value).suffix.lower() in extensions]
    need(len(candidates) == 1, "Expected exactly one compile source in Bee Inputs: " + annotation)
    return candidates[0]
'''
new='''    candidates = [resolve(project_root, value) for value in node.get("Inputs", [])
                  if type(value) is str and Path(value).suffix.lower() in extensions]
    if not annotation.startswith("C_Mac_arm64Pch"):
        # Bee declares the source header used to build the consumed PCH as an
        # input of many compile nodes. It is dependency evidence, not the TU.
        candidates = [value for value in candidates
                      if (os.sep + "libil2cpp" + os.sep + "pch" + os.sep) not in value]
    need(len(candidates) == 1, "Expected exactly one compile source in Bee Inputs: " + annotation)
    return candidates[0]
'''
replace(path,old,new)
old='''        if _under(source, runtime_root) or (_under(source, generated_root) and
                (os.sep + "il2cppOutput" + os.sep + "cpp" + os.sep) in source):
            domain = "runtime"
'''
new='''        generated_runtime = (_under(source, generated_root) and
            ((os.sep + "il2cppOutput" + os.sep + "cpp" + os.sep) in source or source.endswith(".lump.cpp")))
        if _under(source, runtime_root) or generated_runtime:
            domain = "runtime"
'''
replace(path,old,new)

# Synthetic tests cover both generated forms and PCH-header source disambiguation.
path='Tools/AssemblyShadow/tests/test_h1_apple_macro_domains.py'
p=Path(path); text=p.read_text(); marker='    def test_aux_mismatch_rejected(self):\n'
if text.count(marker)!=1: raise SystemExit('domain test insertion anchor changed')
methods='''    def test_generated_lump_is_runtime_owned(self):\n        root,g=self.graph(); runtime=g['Nodes'][0]; old=runtime['Inputs'][0]; generated=str(root/'Library/Bee/artifacts/MacStandalonePlayerBuildProgram/hash/abc.lump.cpp'); runtime['Inputs']=[generated]; runtime['Action']=runtime['Action'].replace(old,generated)\n        result=self.derive(g); self.assertEqual(1,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])\n    def test_pch_header_input_is_not_translation_unit(self):\n        root,g=self.graph(); runtime=g['Nodes'][0]; runtime['Inputs'].append(str(root/'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp/pch/pch-cpp.hpp'))\n        result=self.derive(g); self.assertEqual(1,next(row for row in result['macroDomains'] if row['name']=='runtime')['unitCount'])\n'''
p.write_text(text.replace(marker,methods+marker,1))
