import datetime,json,os,pathlib,subprocess,time
P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261002H-rejection');W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';R=P.parent/'R03LocalBatch-20261002H-rejection';assert not R.exists() and not(P/'runner-invocation.json').exists()
sdk='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';env=os.environ.copy();env.update({'PATH':sdk+':'+env['PATH'],'DOTNET_ROOT':sdk,'DOTNET_ROOT_ARM64':sdk,'DOTNET_MULTILEVEL_LOOKUP':'0','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp'})
command=['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',str(D/'Tools/AssemblyShadow/R03/run_local.py'),'--workspace',str(W),'--output',str(R),'--unity','/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity','--demo-commit','2007c5dbd3dcf535706688e6595700e3ba26a11e']
receipt={'command':command,'cwd':str(D),'startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'startedEpoch':time.time(),'environment':{k:env[k] for k in ['PATH','DOTNET_ROOT','DOTNET_ROOT_ARM64','DOTNET_MULTILEVEL_LOOKUP','PYTHONDONTWRITEBYTECODE','TMPDIR']},'batchInvocations':1}
with (P/'runner-stdout.log').open('xb') as out,(P/'runner-stderr.log').open('xb') as err:
 process=subprocess.Popen(command,cwd=D,env=env,stdout=out,stderr=err);receipt['pid']=process.pid
 with (P/'runner-invocation.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print('Runner started',process.pid,receipt['startedUtc'],flush=True);code=process.wait()
receipt.update({'exitCode':code,'endedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endedEpoch':time.time()})
with (P/'runner-exit.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Runner exited',code,receipt['endedUtc'],flush=True)
