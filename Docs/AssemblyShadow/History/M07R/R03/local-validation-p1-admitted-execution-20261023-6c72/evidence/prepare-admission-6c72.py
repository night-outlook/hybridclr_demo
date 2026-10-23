from pathlib import Path
import ast
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');s=(B/'preflight-p1-admitted-execution-e1e5-bootstrap.py').read_text()
s=s.replace('R03-P1-ADMITTED-EXECUTION-20261022-e1e5','R03-P1-ADMITTED-EXECUTION-20261023-6c72').replace('local-validation-p1-admitted-execution-20261022-e1e5','local-validation-p1-admitted-execution-20261023-6c72').replace('19de9dd4d1040aeb2b72b4e3fe0f89b18df94696','7a098e45b41b98ee024ed0205b353aa2f132aae9')
tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='rel');old=ast.get_source_segment(s,node.iter);paths=ast.literal_eval(old)
reads=['Docs/AssemblyShadow/README.md','Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md']
reads+=['Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261022-e1e5/'+n for n in ['README.md','FINDING.json','preflight/run-once.py','preflight/AssemblyShadow.cpp.FROZEN_COMPARISON.json','preflight/AssemblyShadow.h.FROZEN_COMPARISON.json','preflight/audit.py','MANIFEST.sha256']]
reads+=['Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/P1_LOCAL_PREFLIGHT_RECONSTRUCTION_2026-10-23/'+n for n in ['DESIGN.md','PLAN.md','PRIMARY_SOURCE_AUDIT.md','EVIDENCE.json']]
reads+=['Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py','Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py']
reads+=[p for p in paths if p not in reads];s=s.replace(old,repr(reads),1)
s=s.replace('P.mkdir()\ndef save(n,x):(P/n).write_text(json.dumps(x,indent=2)+\'\\n\')',"""bundle={}
def save(n,x):bundle[n]=x""")
s=s.replace("print('ADMITTED',P)","""# Authenticate the blocked checkpoint/external collector separately from the original 24 checkpoints.
bc=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261022-e1e5';bp=B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261022-e1e5';br=[]
for line in (bc/'MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);q=bc/rel;assert sha(q)==h;br.append(dict(path=rel,sha256=h,bytes=q.stat().st_size))
assert len(br)==42 and {str(q.relative_to(bc)) for q in bc.rglob('*') if q.is_file()}=={r['path'] for r in br}|{'MANIFEST.sha256'}
assert sha(bc/'preflight/run-once.py')=='73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd'
assert not (B/'R03-P1-ADMITTED-EXECUTION-20261022-e1e5').exists() and not (B/'Scratch-R03-P1-ADMITTED-EXECUTION-20261022-e1e5').exists()
oldp=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q)) for q in sorted(bp.rglob('*')) if q.is_file() and not q.is_symlink()]
save('BLOCKED_ADMISSION_BEFORE.json',dict(result='PreservedBeforeNewRootCreation',checkpoint=str(bc),manifestSha256=sha(bc/'MANIFEST.sha256'),files=br,externalPreflight=str(bp),externalFiles=oldp,oldCoreAndScratchAbsent=True,oldOutcome='PrerequisiteBlocked_0of25_NotRun'))
for rel,blob in [('Docs/AssemblyShadow/Handoff/Tools/prepare_p1_admitted_local.py','cf2fdf39fe17df076d50dcc33ed72c757eaa3b26'),('Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py','58e6e0b9ff870d1ada20021ab36a82882d60b837')]:
 assert (D/rel).read_bytes()==subprocess.check_output(['git','-C',str(D),'cat-file','blob',blob])
for root in [P,O,S,C]:assert not root.exists() and not root.is_symlink()
out=B/'Admission-R03-P1-ADMITTED-EXECUTION-20261023-6c72.json';assert not out.exists();out.write_text(json.dumps(bundle,indent=2)+'\\n');print('ADMITTED without creating four roots',out)
""")
assert 'P.mkdir()' not in s
p=B/'admission-6c72.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s)
