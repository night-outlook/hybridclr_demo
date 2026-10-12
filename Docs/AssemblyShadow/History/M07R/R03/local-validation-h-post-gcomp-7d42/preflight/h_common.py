from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess
P=Path(__file__).resolve().parent;B=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';pins=json.loads((P/'SOURCE_AUTHORITY.json').read_text())['pins'];PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';UNITY=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');H=B/'R03IRLocal-H-post-GCOMP-7d42';hist=D/'Docs/AssemblyShadow/History/M07R/R03'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
def load(p):return json.loads(Path(p).read_text())
def environment(extra=None):
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_ROOT=str(SDK),DOTNET_ROOT_ARM64=str(SDK),DOTNET_MULTILEVEL_LOOKUP='0',PATH=str(SDK)+os.pathsep+os.environ['PATH'],EXPECTED_DEMO_COMMIT=pins['hybridclr_demo']);env.update(extra or {});return env

def command(label,args,timeout=600,extra=None):
 root=P/'commands'/label;root.mkdir(parents=True);args=list(map(str,args));start=now();env=environment(extra)
 save(root/'invocation.json',{'argv':args,'cwd':str(D),'startUtc':start,'pins':pins,'environmentOverrides':{k:env[k] for k in ['PYTHONDONTWRITEBYTECODE','DOTNET_ROOT','DOTNET_ROOT_ARM64','DOTNET_MULTILEVEL_LOOKUP','PATH','EXPECTED_DEMO_COMMIT']},'extraEnvironment':extra or {},'timeoutSeconds':timeout})
 with (root/'stdout.log').open('xb') as out,(root/'stderr.log').open('xb') as err:r=subprocess.run(args,cwd=D,env=env,stdout=out,stderr=err,timeout=timeout)
 row={'argv':args,'cwd':str(D),'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'pins':pins,'stdoutPath':str(root/'stdout.log'),'stderrPath':str(root/'stderr.log'),'stdoutSha256':sha(root/'stdout.log'),'stderrSha256':sha(root/'stderr.log'),'invocationReceipt':str(root/'invocation.json')};save(root/'receipt.json',row);print(json.dumps({'command':label,'exitCode':r.returncode,'receipt':str(root/'receipt.json')}),flush=True);return row

def clean_sources():
 for n,h in pins.items():
  p=W/n;assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()==h;assert not subprocess.check_output(['git','-C',str(p),'status','--short'],text=True).strip()
def no_unity():
 rows=[s for s in subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True).splitlines() if s.strip().endswith('/Unity') or s.strip().endswith('/R03Isolated')];assert not rows,rows
