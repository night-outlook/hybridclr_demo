from pathlib import Path


def replace(path, old, new, count=1):
    p=Path(path); text=p.read_text(); actual=text.count(old)
    if actual != count: raise SystemExit(f'{path}: expected {count}, got {actual}: {old[:120]!r}')
    p.write_text(text.replace(old,new,count))

path='Tools/AssemblyShadow/h1_pch_provenance.py'
replace(path,'def plan(graph, root, native, config, responses, feature):','def plan(graph, root, native, config, responses, feature, domain_policy=None):')
replace(path,'derived = a.derive_graph_evidence(stripped, root, native, config, {}, expected_feature=feature, domain_policy=a.H1_APPLE_BEE_DOMAIN_POLICY)','derived = a.derive_graph_evidence(stripped, root, native, config, {}, expected_feature=feature, domain_policy=domain_policy)')
replace(path,'blueprint = plan(graph, root, native, config, responses, binding["featureEnabled"])','blueprint = plan(graph, root, native, config, responses, binding["featureEnabled"], binding.get("macroDomainPolicy"))')
replace(path,'return {**{k: provenance[k] for k in BINDINGS}, "graphSha256": provenance["beeActionGraphSha256"],\n            "projectRoot": str(root), "featureEnabled": feature, "cppConfiguration": cpp}','return {**{k: provenance[k] for k in BINDINGS}, "graphSha256": provenance["beeActionGraphSha256"],\n            "projectRoot": str(root), "featureEnabled": feature, "cppConfiguration": cpp,\n            "macroDomainPolicy": provenance.get("macroDomainPolicy")}')
replace(path,'result["plan"] = plan(graph, root, args.native, args.config.read_text(), responses, args.feature == "on")','result["plan"] = plan(graph, root, args.native, args.config.read_text(), responses, args.feature == "on", a.H1_APPLE_BEE_DOMAIN_POLICY)')

path='Assets/AssemblyShadowDemo/Editor/H1CompilerProvenance.cs'
replace(path,'public string il2cppDebug, ndebug, il2cppDevelopment, macroEvidence, macroDomainEvidence;','public string il2cppDebug, ndebug, il2cppDevelopment, macroEvidence, macroDomainEvidence, macroDomainPolicy;')
replace(path,'public string il2cppConfigPath, cppConfiguration;\n            public GraphInventory before;','public string il2cppConfigPath, cppConfiguration, macroDomainPolicy;\n            public GraphInventory before;')
replace(path,'cppConfiguration = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone).ToString(),','cppConfiguration = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone).ToString(),\n                macroDomainPolicy = "h1-apple-bee-v1",')

path='Tools/AssemblyShadow/h1_native_capture.py'
replace(path,
    '    attempt.stage(\'planning\')\n    pch_plan = pch.plan(graph, root, native, raw_config.decode(\'utf-8\'), responses, request.get("featureEnabled")) if pch.has_pch(graph, root, responses) else None\n    derived = pch_plan[\'derived\'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode(\'utf-8\'), responses, expected_feature=request.get("featureEnabled"), domain_policy=actions.H1_APPLE_BEE_DOMAIN_POLICY)',
    '    attempt.stage(\'planning\')\n    domain_policy = request.get("macroDomainPolicy")\n    actions.need(domain_policy in (None, actions.H1_APPLE_BEE_DOMAIN_POLICY), "Unknown requested macro-domain policy")\n    pch_plan = pch.plan(graph, root, native, raw_config.decode(\'utf-8\'), responses, request.get("featureEnabled"), domain_policy) if pch.has_pch(graph, root, responses) else None\n    derived = pch_plan[\'derived\'] if pch_plan else actions.derive_graph_evidence(graph, root, native, raw_config.decode(\'utf-8\'), responses, expected_feature=request.get("featureEnabled"), domain_policy=domain_policy)')
replace(path,'"projectRoot": str(root), "featureEnabled": request[\'featureEnabled\'], "cppConfiguration": cpp}','"projectRoot": str(root), "featureEnabled": request[\'featureEnabled\'], "cppConfiguration": cpp,\n                   "macroDomainPolicy": domain_policy}')
old = "        'macroDomainEvidence': json.dumps(derived['macroDomains'], sort_keys=True, separators=(',', ':')),\n        'projectRoot': str(root),"
new = "        'macroDomainEvidence': json.dumps(derived['macroDomains'], sort_keys=True, separators=(',', ':')),\n        'macroDomainPolicy': derived['macroDomainPolicy'],\n        'projectRoot': str(root),"
replace(path, old, new)

path='Tools/AssemblyShadow/verify-h1-compiler-provenance-strict.py'
replace(path,"    provenance=read(p);need(provenance==build.get('compilerProvenance'),'Embedded and retained compiler provenance differ')","    provenance=read(p);need(provenance==build.get('compilerProvenance'),'Embedded and retained compiler provenance differ')\n    need(provenance.get('macroDomainPolicy')==strict.H1_APPLE_BEE_DOMAIN_POLICY,'Fresh H1 build lacks the reviewed Apple macro-domain policy')")

path='Tools/AssemblyShadow/h1_pch_diagnose.py'
replace(path,'blueprint = p.plan(graph, root, native, config_bytes.decode("utf-8"), responses, request["featureEnabled"])','blueprint = p.plan(graph, root, native, config_bytes.decode("utf-8"), responses, request["featureEnabled"], p.a.H1_APPLE_BEE_DOMAIN_POLICY)')
replace(path,'"diagnosticOnly": True, "replayedRequestSha256": p.sha(request_bytes)}','"diagnosticOnly": True, "replayedRequestSha256": p.sha(request_bytes),\n                   "macroDomainPolicy": p.a.H1_APPLE_BEE_DOMAIN_POLICY}')

path='Tools/AssemblyShadow/tests/test_h1_apple_macro_domains.py'
p=Path(path); text=p.read_text(); marker="if __name__=='__main__': unittest.main()\n"
if text.count(marker)!=1: raise SystemExit('domain test marker changed')
method='''    def test_committed_apple_failure_graph_is_430_2_14(self):\n        import hashlib,json,tarfile\n        repo=Path(__file__).resolve().parents[3]\n        archive=repo/'Documents/AgentHandoff/local-validation-20260914-bec2bd1/fresh-smoke-failure-inputs.tar.gz'\n        raw=archive.read_bytes(); self.assertEqual('e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8',hashlib.sha256(raw).hexdigest())\n        graph=None; config=None; graph_sha='dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181'\n        with tarfile.open(archive,'r:gz') as tf:\n            for member in tf.getmembers():\n                if not member.isfile(): continue\n                data=tf.extractfile(member).read()\n                if hashlib.sha256(data).hexdigest()==graph_sha: graph=json.loads(data.decode('utf-8-sig'))\n                if member.name.endswith('/il2cpp-config.h'): config=data.decode('utf-8')\n        self.assertIsNotNone(graph); self.assertIsNotNone(config)\n        project=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo')\n        link=next(node for node in graph['Nodes'] if str(node.get('Annotation','')).startswith('Link_Mac_arm64'))\n        native=Path(h.resolve(project,next(value for value in link['Outputs'] if Path(value).name=='GameAssembly.dylib')))\n        result=h.derive_graph_evidence(graph,project,native,config,{},expected_feature=True,domain_policy=h.H1_APPLE_BEE_DOMAIN_POLICY)\n        self.assertEqual({'runtime':430,'bdwgc':2,'zlib':14},{row['name']:row['unitCount'] for row in result['macroDomains']})\n        self.assertEqual(('1','0','0'),(result['il2cppDebug'],result['ndebug'],result['il2cppDevelopment']))\n'''
p.write_text(text.replace(marker,method+'\n'+marker,1))
