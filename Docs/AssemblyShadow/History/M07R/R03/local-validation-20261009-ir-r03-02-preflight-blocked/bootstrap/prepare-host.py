from pathlib import Path
import subprocess,json,datetime,os,plistlib,hashlib,shlex
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009A-terminal';bootstrap=Path(__file__).resolve().parent;assert not P.exists();P.mkdir();pins=json.loads((bootstrap/'SYNC_AUTHORITY.json').read_text())['repositories'];sdk=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');env=dict(os.environ,DOTNET_ROOT=str(sdk),DOTNET_ROOT_ARM64=str(sdk),DOTNET_MULTILEVEL_LOOKUP='0',PYTHONDONTWRITEBYTECODE='1',TMPDIR='/private/tmp',PATH=str(sdk)+os.pathsep+os.environ['PATH']);env['EXPECTED_DEMO_COMMIT']=pins['hybridclr_demo'];records=[]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(name,v):
 with (P/name).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def run(label,args,timeout=120):
 root=P/'commands'/label;root.mkdir(parents=True);start=utc()
 with (root/'stdout.log').open('xb') as out,(root/'stderr.log').open('xb') as err:r=subprocess.run(args,cwd=D,env=env,stdout=out,stderr=err,timeout=timeout)
 receipt={'argv':[str(x) for x in args],'cwd':str(D),'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdoutPath':str(root/'stdout.log'),'stdoutSha256':sha(root/'stdout.log'),'stderrPath':str(root/'stderr.log'),'stderrSha256':sha(root/'stderr.log')};(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');records.append(receipt);assert r.returncode==0,label;return (root/'stdout.log').read_text()
try:
 for name in ['R03IRLocal-20261009A-terminal','StorageCheck-R03IRLocal-20261009A-terminal','Storage-R03IRLocal-20261009A-terminal']:
  path=BASE/name;assert not path.exists() and not path.is_symlink();assert not path.resolve().is_relative_to(W)
 run('source-freeze',['git','-C',str(D),'merge-base','--is-ancestor','3eb309a1f82a9c7d4199a8499b95144a78cbdd24',pins['hybridclr_demo']]);run('source-docs-delta',['git','-C',str(D),'diff','--exit-code','3eb309a1f82a9c7d4199a8499b95144a78cbdd24',pins['hybridclr_demo'],'--','.',':!Docs/AssemblyShadow'])
 declared=json.loads((D/'Tools/AssemblyShadow/R03/source-pins.json').read_text());assert all(declared[n]==pins[n] for n in ['hybridclr','hybridclr_unity','il2cpp_plus'])
 unity=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');assert unity.is_file() and os.access(unity,os.X_OK);v=plistlib.loads((unity.parent.parent/'Info.plist').read_bytes());assert v['CFBundleVersion']=='2022.3.62f2'
 dotnet=run('dotnet-version',[str(sdk/'dotnet'),'--version']).strip();assert dotnet=='8.0.318'
 versions={'dotnet':dotnet,'unity':v['CFBundleVersion'],'unityExecutable':str(unity),'sdkOnlyRoot':str(sdk),'macOS':run('macos-version',['sw_vers']),'python':run('python-version',['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','--version']),'clang':run('clang-version',['/usr/bin/c++','--version']),'developerDirectory':run('developer-dir',['xcode-select','-p']),'platformSDK':run('sdk-path',['xcrun','--show-sdk-path'])}
 active=[]
 for line in subprocess.check_output(['ps','-axo','pid=,comm=,args='],text=True).splitlines():
  parts=line.strip().split(None,2)
  if len(parts)==3 and parts[1].endswith('/Unity'):
   args=shlex.split(parts[2]);project=args[args.index('-projectPath')+1] if '-projectPath' in args else None;active.append({'pid':int(parts[0]),'executable':parts[1],'projectPath':project})
 assert not active,'Active Unity exists; cannot establish isolated execution ownership'
 save('SOURCE_ENVIRONMENT.json',{'state':'Passed','recordedUtc':utc(),'pins':pins,'branch':'codex/assembly-shadow-r01b-h1','versions':versions,'activeUnity':active,'sourcePinSha256':sha(D/'Tools/AssemblyShadow/R03/source-pins.json'),'bootstrap':str(bootstrap),'sourceFreeze':'3eb309a1f82a9c7d4199a8499b95144a78cbdd24','sourceFreezeDelta':'Docs-only','credentialProtocolChanged':False,'ordinaryPrimaryUsed':False,'gateHostIdentity':'Unavailable; no Off/PASS or independent stage review claimed'})
 run('ir-host-tests',['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B','-m','unittest','discover','-s',str(D/'Tools/AssemblyShadow/R03IR'),'-p','test_*.py','-v'],180)
 executable=P/'terminal-policy';source=W/'il2cpp_plus/tools/r03/terminal_execution_tests.cpp';run('native-policy-compile',['/usr/bin/c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread','-I'+str(W/'il2cpp_plus/libil2cpp'),str(source),'-o',str(executable)]);run('native-policy-run',[str(executable)])
 save('LOCAL_HOST_PREFLIGHT.json',{'state':'Passed','recordedUtc':utc(),'commands':records,'nativePolicySource':str(source),'sourceSha256':sha(source),'headerSha256':sha(W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalExecution.h'),'executableSha256':sha(executable),'unityLaunched':False,'runtimeAcceptance':False})
 print('Local source/environment and prescribed Python/native host checks Passed',str(P),flush=True)
except BaseException as e:
 save('LOCAL_HOST_PREFLIGHT_FAILURE.json',{'state':'Blocked','recordedUtc':utc(),'type':type(e).__name__,'error':str(e),'commands':records,'unityLaunched':False});raise
