from pathlib import Path
import subprocess,json,hashlib,datetime,concurrent.futures
P=Path(__file__).resolve().parent;E=json.loads((P/'EXPECTED.json').read_text());D=Path(E['workspace'])/'hybridclr_demo';B='codex/assembly-shadow-r01b-h1';plan=json.loads((P/'PUBLICATION_PLAN.json').read_text());C=Path(plan['checkpoint']);records=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args):
 start=now();r=subprocess.run(args,capture_output=True,text=True,timeout=180);row=dict(argv=args,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr);records.append(row);(P/'PUSH_RECEIPT.json').write_text(json.dumps(dict(commands=records),indent=2)+'\n');assert r.returncode==0,row;return r.stdout.strip()
def git(*args):return cmd(['git','-C',str(D),*args])
assert json.loads((P/'PUBLICATION_VALIDATION.json').read_text())['result']=='PassedPublicationChecks'
assert json.loads((P/'LOCAL_RESULT.json').read_text())['result']=='FAIL'
assert git('rev-parse','HEAD')==E['pins']['hybridclr_demo']
assert git('ls-remote','origin','refs/heads/'+B).split()[0]==E['pins']['hybridclr_demo']
git('diff','--cached','--check');assert not git('diff','--name-only')
staged=git('diff','--cached','--name-only').splitlines();assert staged and all(p in plan['ownedReports'] or p.startswith(str(C.relative_to(D))+'/') for p in staged)
git('commit','-m','docs: publish admitted batch and failed independent audit')
head=git('rev-parse','HEAD');assert git('rev-parse','HEAD^')==E['pins']['hybridclr_demo'] and not git('status','--short')
assert all(p.startswith('Docs/') for p in git('diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines())
git('push','origin','HEAD:refs/heads/'+B)
assert git('ls-remote','origin','refs/heads/'+B).split()[0]==head and not git('status','--short')
expected={**E['pins'],'hybridclr_demo':head}
def check(n):
 path=Path(E['workspace'])/n;rows=[]
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['ls-remote','origin','refs/heads/'+B]]:
  argv=['git','-C',str(path),*args];t=now();r=subprocess.run(argv,capture_output=True,text=True,timeout=90);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,(n,args,r.stderr)
 assert rows[0]['stdout'].strip()==str(path) and rows[1]['stdout'].strip()==B and rows[2]['stdout'].strip()==expected[n] and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==expected[n]
 return n,dict(path=str(path),branch=B,head=expected[n],remote='verified',clean=True,checks=rows)
repos=dict(concurrent.futures.ThreadPoolExecutor(4).map(check,expected))
for line in (C/'MANIFEST.sha256').read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(C/rel)==h
assert sha(C/'MANIFEST.sha256')==plan['checkpointManifestSha256']
receipt=dict(result='PublishedAndRemoteVerified',time=now(),repositories=repos,executionPins=E['pins'],publishedDocumentationCommit=head,checkpoint=str(C),checkpointManifestSha256=sha(C/'MANIFEST.sha256'),checkpointReverifiedAfterPush=True,workStoppedAt='Primary Implementation',runtimeAcceptance=False)
(P/'PUBLICATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
lines='\n'.join(f'- night-outlook/{n} | path={x["path"]} | branch={B} | commit={x["head"]} | remote=verified' for n,x in repos.items())
text=f'''[HANDOFF: Local Validation -> Primary Implementation]

Result: FAIL

Read first:
- night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md
- night-outlook/hybridclr_demo/Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md
- night-outlook/hybridclr_demo/Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md

Repositories and latest pushed commits:
{lines}

Validation completed: One 15/15 Mac prerequisite, unchanged preparation and one raw PassedSourceHostAndSDKOnly batch: 25/25 components, original85 tests, eight inventories, admitted9+9, managed5+exact negative, native100 and Git20. Source/SDK/history preservation and preparer verify-after Passed. No retry or Unity/Player launch.
Failures or blockers: Required independent auditor Failed at line190: its fixed24-name roster omits admitted-execution from the actual25. Overall Local FAIL; raw PASS remains unchanged. Later auditor checks are NotRun. All historical states and false acceptance flags preserved.
Required Primary Implementation action: Fix the source-bound successor auditor roster and add exact25 identity/order regressions without changing archived bytes or weakening checks. Complete independent evidence review under new explicit authority; no further Local run is authorized.
Evidence: Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md; RETURN_TO_WEB.md; Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-admitted-execution-20261023-b7e3/README.md and FINDING.json; {E['output']}; {P}/audit.log; {P}/PUBLICATION_RECEIPT.json
Next state: Primary Implementation

Work only from the listed paths and commits. Do not infer missing state from chat history. Preserve all evidence states exactly as recorded in LOCAL_VALIDATION.md.
'''
(P/'FINAL_HANDOFF.txt').write_text(text);print(text);print('CHECKPOINT_MANIFEST_SHA256',sha(C/'MANIFEST.sha256'))
