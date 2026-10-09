from pathlib import Path
import subprocess,json,hashlib,datetime
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');BOOT=BASE/'IR-R03-02-bootstrap-20261009A';P=BASE/'Preflight-R03IRLocal-20261009A-terminal';head='fca2fdb035512fc739693641a5fa2126e4254258'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],timeout=120)
def save(name,obj):
 with (P/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
files=[x for x in git(D,'ls-files','Tools/AssemblyShadow/R03IR','Tools/AssemblyShadow/R03/PlayerFixtures','Tools/AssemblyShadow/R03/PlayerApiCompile','Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs').decode().splitlines() if not x.endswith('.meta')]
rows=[]
for run in [37872834945,37894308627,37894308586,37894749414,37874183375,37893353097,37895355423]:
 r=json.loads((BOOT/'ci'/f'run-{run}.json').read_text());native=run==37872834945;repo=W/'il2cpp_plus' if native else D;current='9ce1c1bfec9a21b92ea300acda5f27a3815b2c37' if native else head
 paths=['tools/r03/terminal_execution_tests.cpp','libil2cpp/vm/AssemblyShadowTerminalExecution.h'] if native else files
 pairs=[]
 for path in paths:
  try:a=git(repo,'show',r['head_sha']+':'+path)
  except subprocess.CalledProcessError:continue
  b=git(repo,'show',current+':'+path)
  pairs.append({'path':path,'executingBlob':git(repo,'rev-parse',r['head_sha']+':'+path).decode().strip(),'currentBlob':git(repo,'rev-parse',current+':'+path).decode().strip(),'executingSha256':hashlib.sha256(a).hexdigest(),'currentSha256':hashlib.sha256(b).hexdigest(),'sameBytes':a==b})
 rows.append({'runId':run,'url':r['html_url'],'executingCommit':r['head_sha'],'createdAt':r['created_at'],'completedAt':r['updated_at'],'status':r['status'],'conclusion':r['conclusion'],'currentCommit':current,'fileComparisons':pairs})
 assert r['status']=='completed' and r['conclusion']=='success'
api=next(x for x in rows if x['runId']==37874183375);player=next(x for x in api['fileComparisons'] if x['path'].endswith('R03TerminalPlayer.cs'));assert not player['sameBytes']
diff=git(D,'diff',api['executingCommit'],head,'--',player['path']);(P/'PLAYER_API_SOURCE_DELTA.patch').write_bytes(diff)
save('CI_SOURCE_EQUIVALENCE.json',{'recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overallState':'Blocked','currentPlayerApiCoverage':'NoCoverage','runs':rows,'playerApiMismatch':player,'sourceMatchedHostFreeze':'3eb309a1f82a9c7d4199a8499b95144a78cbdd24','freezeDeltaDocsOnly':True,'limits':['Actual listed CI jobs passed at their executing commits. Full per-file comparisons do not imply each workflow compiled every listed file.','Current freeze host job and fresh Local Python tests cover current host contracts; neither compiles the current CSharp Player body.','Old Player API job compiled an earlier body; new pre/post-poison field assertions are not source-equivalent.','Official native API job covers native translation units/build helper; no R03TerminalPlayer.cs compilation claim.','Decoded GitHub log copies preserve text with normalized final newline; not byte-identity with remote ZIP.'],'logCopies':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((BOOT/'ci').glob('job-*.log'))]})
print(json.dumps({'state':'Blocked','playerApiMismatch':player}))
