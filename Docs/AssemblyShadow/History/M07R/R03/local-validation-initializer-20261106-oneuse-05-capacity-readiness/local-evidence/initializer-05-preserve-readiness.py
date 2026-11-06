from pathlib import Path
import json,hashlib,subprocess,datetime,sys,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse'
phase=sys.argv[1];assert phase in ('BEFORE','AFTER');out=B/f'initializer-05-PRESERVATION_{phase}.json';assert not out.exists()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now();load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def git(p,*a):return subprocess.check_output(['git','-C',str(p),*a],text=True).strip()
assert git(D,'rev-parse','HEAD')=='85fb825ccd70291afa3eaa279cc6280703ed58f7'
assert not git(D,'status','--porcelain=v1','--untracked-files=all')
roots=[Path(x['root']) for x in load(B/'initializer-04-PRESERVATION_BEFORE.json')['history']]+[D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-04']
history=[]
for root in roots:
 manifest=root/'MANIFEST.sha256';rel=str(manifest.relative_to(D));blob=git(D,'rev-parse','HEAD:'+rel);assert git(D,'hash-object',str(manifest))==blob
 rows=[]
 for line in manifest.read_text().splitlines():
  h,rel=line.split('  ',1);p=root/rel;assert p.is_file() and not p.is_symlink() and sha(p)==h;rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':h})
 assert set(r['path'] for r in rows)=={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}-{'MANIFEST.sha256'}
 history.append({'root':str(root),'manifestSha256':sha(manifest),'manifestGitBlob':blob,'filesVerified':len(rows),'regularBytesVerified':sum(x['bytes'] for x in rows)})
protected=load(B/'oneuse-C-PROTECTED_BEFORE.json')
for row in protected['rows']:
 p=S/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert git(S,'rev-parse','HEAD')=='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b' and not git(S,'status','--porcelain=v1','--untracked-files=all')
assert git(S,'config','core.sparseCheckout')=='true'
assert git(S,'rev-parse','HEAD:Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready')=='2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79'
sdk=load(B/'Preflight-R03-P1-ADMITTED-EXECUTION-20261023-b7e3/SDK_BEFORE.json')
for row in sdk['files']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
old=load(B/'initializer-04-RETAINED_PRIOR_BEFORE.json');external=[]
for row in old['externalFiles']:
 p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];external.append(row)
for p in sorted(B.glob('initializer-04-*')):
 assert p.is_file() and not p.is_symlink();external.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
sources=load(B/'initializer-04-CI_GATE.json')['sourceBindings']
for row in sources:
 p=W/row['repository']/row['path'];assert sha(p)==row['sha256'] and git(W/row['repository'],'hash-object',str(p))==git(W/row['repository'],'rev-parse','HEAD:'+row['path'])
bindings=[]
for rel in ['Tools/AssemblyShadow/R03IR/capacity_readiness.py','Tools/AssemblyShadow/R03IR/test_capacity_readiness.py','.github/workflows/r03-ir-capacity-readiness.yml','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md']:
 p=D/rel;assert git(D,'hash-object',str(p))==git(D,'rev-parse','HEAD:'+rel);bindings.append({'repository':'hybridclr_demo','path':rel,'sha256':sha(p),'gitBlob':git(D,'hash-object',str(p))})
env=load(B/'oneuse-E-ENVIRONMENT_BEFORE.json');binaries={}
for name,key in [('dotnet','dotnetSha256'),('Unity2022','unitySha256')]:
 p=Path(env[name]);assert sha(p)==env[key];binaries[name]={'path':str(p),'sha256':sha(p)}
absent=[]
for n in ['R03IR-Initializer-20261106-oneuse-04','R03IR-Initializer-20261106-oneuse-04-native-host-raw','R03IR-Initializer-20261106-oneuse-05','R03IR-Initializer-20261106-oneuse-05-native-host-raw']:
 p=B/n;assert not p.exists() and not p.is_symlink() and p.resolve()==p;absent.append(str(p))
reports=[]
for name in ['LOCAL_VALIDATION.md','RETURN_TO_WEB.md']:
 p=D/'Docs/AssemblyShadow/Handoff'/name;assert git(D,'hash-object',str(p))==git(D,'rev-parse','HEAD:'+str(p.relative_to(D)));reports.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
x={'kind':'ReadOnlyCapacityReadinessPreservation','phase':phase,'startUtc':start,'endUtc':now(),'result':'PassedWithinReadinessScope','history':history,'originalSFilesVerified':len(protected['rows']),'originalSLogicalBytesVerified':sum(r['bytes'] for r in protected['rows']),'installedSdkFilesVerified':len(sdk['files']),'binaries':binaries,'priorExternalFiles':external,'retainedRuntimeSourceBindingsVerified':len(sources),'newReadinessSourceBindings':bindings,'reportBindingsBeforePublication':reports,'absentRoots':absent,'rawRuntimeTrees':'ReusedAuditedPreservationFrom04_NoFreshFullRawTreeAudit','fullRuntimeAdmission':'NotRun_CapacityPrerequisiteFailed','UnityLaunches':0,'runnerInvocations':0,'Players':0,'dataDeletionOrRelocationOperations':0,'runtimeAcceptance':False}
if phase=='AFTER':
 before=load(B/'initializer-05-PRESERVATION_BEFORE.json')
 for key in ['history','priorExternalFiles','newReadinessSourceBindings','binaries','reportBindingsBeforePublication','absentRoots']:assert x[key]==before[key],key
 x['independentlyRepeatedComparison']='Passed'
out.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:x[k] for k in ['phase','result','startUtc','endUtc','originalSFilesVerified','installedSdkFilesVerified','retainedRuntimeSourceBindingsVerified']}));print('checkpointCount',len(history),'priorExternalFiles',len(external))
