from pathlib import Path
import json,subprocess,hashlib,datetime,os,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261030-oneuse-E';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-e';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
load=lambda p:json.loads(p.read_text())
for p in [O,C]:assert not p.exists() and not p.is_symlink() and p.resolve()==p
assert load(B/'oneuse-E-CI_GATE-20261102.json')['actualGeneratorGatePassed']
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert len(protected['rows'])==16978
old=load(B/'oneuse-D-PRESERVATION_BEFORE-20261029.json');roots=[Path(x['root']) for x in old['history']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261029-oneuse-d'];history=[]
for root in roots:
 rows=[]
 for line in (root/'MANIFEST.sha256').read_text().splitlines():
  h,rel=line.split('  ',1);p=root/rel;assert sha(p)==h;rows.append(dict(path=rel,sha256=h,bytes=p.stat().st_size))
 history.append(dict(root=str(root),manifestSha256=sha(root/'MANIFEST.sha256'),files=rows))
# Retained D raw root is also authenticated against its full pre-publication inventory.
draw=load(B/'oneuse-D-RAW_MANIFEST.json');dr=Path(draw['root'])
for row in draw['files']:
 p=dr/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in draw['symlinks']:
 p=dr/row['path'];assert p.is_symlink() and os.readlink(p)==row['target']
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
source=[]
for row in load(D/'Tools/AssemblyShadow/R03IR/current_native_candidate.json')['files']+[dict(repository='il2cpp_plus',**r) for r in load(D/'Tools/AssemblyShadow/R03IR/current_native_vm_delta.json')['files']]:
 p=W/row['repository']/row['path'];blob=subprocess.check_output(['git','-C',str(W/row['repository']),'hash-object',str(p)],text=True).strip();assert blob==row['gitBlob'];source.append(dict(repository=row['repository'],path=row['path'],gitBlob=blob,sha256=sha(p)))
pins=load(B/'oneuse-E-initial-git-20261102.json')['expected'];repos={}
for n in [*pins,'OriginalS']:
 p=S if n=='OriginalS' else W/n;rows=[]
 for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--porcelain=v1','--untracked-files=all'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive']]+([] if n=='OriginalS' else [['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]):
  argv=['git','-C',str(p),*a];t=now();r=subprocess.run(argv,capture_output=True,text=True,timeout=120);rows.append(dict(argv=argv,start=t,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 expected='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' if n=='OriginalS' else pins[n];assert rows[0]['stdout'].strip()==str(p) and rows[2]['stdout'].strip()==expected and not rows[3]['stdout']
 if n!='OriginalS':assert rows[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1' and rows[-1]['stdout'].split()[0]==expected
 else:assert not rows[1]['stdout']
 repos[n]=rows
assert subprocess.check_output(['git','-C',str(S),'config','core.sparseCheckout'],text=True).strip()=='true'
subtree='Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready';assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD:'+subtree],text=True).strip()=='2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79'
procs=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True);conflicts=[]
for line in procs.splitlines():
 f=line.strip().split(None,3)
 if len(f)==4 and any(x in f[3].split(' ',1)[0] for x in ['Unity.app','il2cpp','dotnet','clang++']) and any(str(p) in f[3] for p in [W,S,O]):conflicts.append(line)
assert not conflicts
p=B/'oneuse-E-PRESERVATION_BEFORE-20261102.json';assert not p.exists();p.write_text(json.dumps(dict(kind='IndependentOneuseEPreExecutionAdmission',start=start,end=now(),sourcePins=pins,sourceRepositories=repos,protectedOriginalSFiles=16978,protectedLogicalBytes=3882340952,protectedBeforeReceiptSha256=sha(B/'oneuse-C-PROTECTED_BEFORE.json'),originalSparseProjectionUnchanged=True,history=history,retainedDRawFilesVerified=len(draw['files']),retainedDRawManifestSha256=sha(B/'oneuse-D-RAW_MANIFEST.json'),retainedDRawSymlinksVerified=len(draw['symlinks']),installedSdkFilesVerified=len(sdk['files']),sourceBindings=source,runRoot=str(O),checkpoint=str(C),availableBytes=shutil.disk_usage(B).free,conflictingProcesses=conflicts,previousSourceProjectionRetried=False),indent=2)+'\n');print('Pre-execution custody Passed:',len(history),'historical checkpoints;16978 S files;',len(draw['files']),'D raw files;',len(sdk['files']),'SDK inputs;',len(source),'source bindings',flush=True)
