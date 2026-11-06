from pathlib import Path
import json,hashlib,subprocess,datetime,os,sys
R=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-Initializer05-Resume-20261106-after-retirement');B=R.parent;W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';T=Path('/Users/ah/GitHub/hybridclr_cleanup_receipts/user-retire-runtime17-20261106');phase=sys.argv[1];assert phase in ['BEFORE','AFTER'];out=R/('PRESERVATION_'+phase+'.json');assert not out.exists();load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
owner=load(R/'SOURCE_PUBLICATION_RECEIPT.json');H=owner['demoCommit'];scope=load(T/'APPROVED_SCOPE.json');assert len(scope['exactRoots'])==17
for p in scope['exactRoots']:assert not Path(p).exists() and not Path(p).is_symlink()
remaining=load(T/'PROTECTED_AFTER.json');outside=[]
for row in remaining['topLevelOutsideEntries']:
 p=Path(row['path']);s=p.lstat();assert s.st_ino==row['inode'] and s.st_mode==row['mode'] and s.st_mtime_ns==row['mtimeNs'] and s.st_size==row['bytes'],p
 if row['kind']=='file':assert sha(p)==row['sha256']
 if row['kind']=='symlink':assert os.readlink(p)==row['linkTarget']
 outside.append(row['path'])
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
history=[]
for row in remaining['publishedCheckpointsVerified']:
 p=Path(row['root']);manifest=p/'MANIFEST.sha256';assert sha(manifest)==row['manifestSha256'];count=0
 for line in manifest.read_text().splitlines():
  h,rel=line.split('  ',1);assert sha(p/rel)==h;count+=1
 history.append({'root':str(p),'manifestSha256':sha(manifest),'filesVerified':count})
p=D/'Docs/AssemblyShadow/History/M07R/R03/storage-retirement-20261106-runtime17';manifest=p/'MANIFEST.sha256';count=0
for line in manifest.read_text().splitlines():
 h,rel=line.split('  ',1);assert sha(p/rel)==h;count+=1
history.append({'root':str(p),'manifestSha256':sha(manifest),'filesVerified':count})
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
sources=load(B/'initializer-04-CI_GATE.json')['sourceBindings']
for row in sources:assert sha(W/row['repository']/row['path'])==row['sha256']
recovery=B/'Initializer05-CapacityAnalysis-20261106/StrippedAOTDllsTempProj.recovery.tar.gz';assert sha(recovery)=='4b5e3b8eb84646bd5025f755f0f23436adf359cbaf9ff850983a2837fe16a727'
compression=load(B/'backup-compression-20261106-RESULT.json');assert sha(Path(compression['originalManifest']))==compression['originalManifestSha256']
for row in compression['rows']:assert sha(Path(row['compressedPath']))==row['compressedSha256']
expected={'hybridclr_demo':H,'hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'41764ae1eeefb33b05966e7f7676e52aae39c340'};repos={}
for name,h in expected.items():
 p=W/name;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  t=now();args=['git','-C',str(p),*a];r=subprocess.run(args,capture_output=True,text=True,timeout=120);rows.append({'command':args,'startUtc':t,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 assert rows[0]['stdout'].strip()==str(p) and rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[2]['stdout'].strip()==h and not rows[3]['stdout'] and rows[-1]['stdout'].split()[0]==h
 repos[name]=rows
assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip()=='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' and not subprocess.check_output(['git','-C',str(S),'status','--short'],text=True)
O=B/'R03IR-Initializer-20261106-oneuse-05';HR=O.with_name(O.name+'-native-host-raw')
if phase=='BEFORE':assert not O.exists() and not HR.exists()
x={'kind':'RemainingCustodyPreservationAfterExplicitOwnerRetirement','phase':phase,'startUtc':start,'endUtc':now(),'result':'PassedRemainingProtectedInputs_Exact17RetiredRemainUnavailable','sourcePins':expected,'sourceRepositories':repos,'remainingOutsideTopLevelEntriesVerified':len(outside),'outsideDirectoryInteriors':'Only frozen-C audit separately covers its original map; other outside raw directory metadata not represented as full new byte audit','originalSFilesVerified':len(protected['rows']),'history':history,'installedSdkFilesVerified':len(sdk['files']),'retainedSourceBindingsVerified':len(sources),'retiredExact17States':[{'path':p,'state':'Unavailable_UserAuthorizedRetirement'} for p in scope['exactRoots']],'noAdditionalDisappearanceExcused':True,'retainedRecoveryArchiveSha256':sha(recovery),'gzipTransitionStillVerified':True,'root':str(O),'hostRoot':str(HR),'runRootPresent':O.exists(),'hostRootPresent':HR.exists(),'R03Accepted':False,'runtimeAcceptance':False}
if phase=='AFTER':
 before=load(R/'PRESERVATION_BEFORE.json');assert before['history']==history and before['sourcePins']==expected and before['retiredExact17States']==x['retiredExact17States'];x['independentlyRepeatedBeforeAfterComparison']='Passed'
out.write_text(json.dumps(x,indent=2)+'\n');print('Preservation',phase,'Passed',len(history),'published checkpoints;16978 S;2405 SDK;1135 outside entries;17 intentionally unavailable',flush=True)
