from pathlib import Path
p=Path('Tools/AssemblyShadow/tests/test_h1_apple_macro_domains.py')
text=p.read_text()
old='import h1_compiler_actions as h\n'
new='import h1_compiler_actions as h\nimport h1_pch_provenance as pch\n'
if text.count(old)!=1: raise SystemExit('domain import anchor changed')
text=text.replace(old,new,1)
old="        result=h.derive_graph_evidence(graph,project,native,config,{},expected_feature=True,domain_policy=h.H1_APPLE_BEE_DOMAIN_POLICY)\n"
new="        result=pch.plan(graph,project,native,config,{},True,h.H1_APPLE_BEE_DOMAIN_POLICY)['derived']\n"
if text.count(old)!=1: raise SystemExit('authenticated fixture call anchor changed')
p.write_text(text.replace(old,new,1))
