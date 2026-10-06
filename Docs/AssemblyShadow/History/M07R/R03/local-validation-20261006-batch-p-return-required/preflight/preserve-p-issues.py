"""Preserve only observed non-trivial Primary-owned problems from the sealed batch."""
import pathlib,json,hashlib,datetime,subprocess
P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261006P-lo-repair';W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def evidence(p):
 p=pathlib.Path(p);assert p.is_file();return {'path':str(p),'sha256':sha(p),'size':p.stat().st_size}
r=load(R/'LOCAL_BATCH_RESULT.json');failed={c['id']:c for c in r['cells'] if c['result']=='Failed'}
items=load(P/'ISSUE_DESCRIPTIONS.json') if (P/'ISSUE_DESCRIPTIONS.json').exists() else []
sources=[];covered=[]
for item in items:
 assert item['affectedCells'] and all(n in failed for n in item['affectedCells']);covered+=item['affectedCells'];ev=[evidence(R/'cells'/(n+'.json')) for n in item['affectedCells']]
 for p in item.pop('evidencePaths',[]):ev.append(evidence(p))
 for repo,name in item.pop('sourceFiles',[]):
  repo=W/repo;f=repo/name;h=r['repositories'][repo.name];assert f.read_bytes()==subprocess.check_output(['git','-C',str(repo),'show',h+':'+name]);ev.append(evidence(f));copy=P/'additional-issue-source'/repo.name/name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(f.read_bytes());ev.append(evidence(copy));sources.append({'repository':str(repo),'commit':h,'path':name,'sha256':sha(f)})
 item['evidence']=list({e['path']:e for e in ev}.values())
assert len(covered)==len(set(covered)) and set(covered)==set(failed),(covered,list(failed))
(P/'PRIMARY_ISSUES.json').write_text(json.dumps({'kind':'R03PPrimaryImplementationIssues','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'issues':items,'allFailedCellsCovered':sorted(covered),'scope':'Observed non-trivial current-source failures requiring Primary only; no Local source fixes','R03Accepted':False,'H2Passed':False,'qualificationApproved':False},indent=2)+'\n')
(P/'ROOT_CAUSE_SOURCE_BINDINGS.json').write_text(json.dumps({'kind':'ExactGitBlobSourceBindings','sources':sources,'noSourceChanges':True},indent=2)+'\n')
print('Observed Primary issues:',len(items),'Failed cells covered:',len(covered))
