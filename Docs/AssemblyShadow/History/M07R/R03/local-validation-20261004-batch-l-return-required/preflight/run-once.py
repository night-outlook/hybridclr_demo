import datetime,json,os,pathlib,subprocess,time
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261004L-fixed-image');W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';R=P.parent/'R03LocalBatch-20261004L-fixed-image';assert not R.exists() and not(P/'runner-invocation.json').exists()
os.environ['GIT_SSH_COMMAND']=json.loads((P/'SSH_TRANSPORT.json').read_text())['command']
expected=json.loads((P/'environment.json').read_text())['expected']
for name,sha in expected.items():
 repo=W/name
 assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==sha
 assert subprocess.check_output(['git','-C',str(repo),'status','--porcelain=v1','--untracked-files=all'],text=True)==''
 assert subprocess.check_output(['git','-C',str(repo),'ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1'],text=True).split()[0]==sha

sdk='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';env=os.environ.copy();env.update({'PATH':sdk+':'+env['PATH'],'DOTNET_ROOT':sdk,'DOTNET_ROOT_ARM64':sdk,'DOTNET_MULTILEVEL_LOOKUP':'0','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp'})
command=['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',str(D/'Tools/AssemblyShadow/R03Completion/run_completion.py'),'--workspace',str(W),'--output',str(R),'--unity','/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity','--demo-commit','96eaa341d8eea476aec72506bac1a2d0456e24d7']
receipt={'command':command,'cwd':str(D),'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'startedEpoch':time.time(),'environment':{k:env[k] for k in ['PATH','DOTNET_ROOT','DOTNET_ROOT_ARM64','DOTNET_MULTILEVEL_LOOKUP','PYTHONDONTWRITEBYTECODE','TMPDIR']},'batchInvocations':1}
with (P/'runner-stdout.log').open('xb') as out,(P/'runner-stderr.log').open('xb') as err:
 process=subprocess.Popen(command,cwd=D,env=env,stdout=out,stderr=err);receipt['pid']=process.pid
 with (P/'runner-invocation.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print('Runner started',process.pid,receipt['startedUtc'],flush=True);code=process.wait()
receipt.update({'exitCode':code,'endedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endedEpoch':time.time()})
with (P/'runner-exit.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Runner exited',code,receipt['endedUtc'],flush=True)
