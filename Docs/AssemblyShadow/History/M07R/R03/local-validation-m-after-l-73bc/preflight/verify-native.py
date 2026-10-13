from h_common import *
import collections,re
N=B/'NativeSDK-R03M-after-L-73bc';S=B/'Scratch-R03M-after-L-73bc';start=now();r=load(N/'results.json');rows=[];warnings=[]
for f in sorted((N/'commands').glob('*/command.json')):
 c=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==c[n+'Sha256']
 assert not c['cleanupErrors'] and not c['remainingProcessGroup'] and not c['postCleanupGroupExists']
 args=c['command'];record={'receipt':str(f),'receiptSha256':sha(f),'command':args,'exitCode':c['exitCode'],'pid':c['pid'],'startUtcEpoch':c['startedUtcEpoch'],'endUtcEpoch':c['endedUtcEpoch'],'timeout':c['timeout']}
 if '-fsyntax-only' in args:
  assert '-std=c++17' in args and args[args.index('-arch')+1]=='arm64' and not c['timeout']
  source=Path(args[-1]);assert source.is_relative_to(S) or source==D/'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'
  record.update(source=str(source),sha256=sha(source),state='Passed' if c['exitCode']==0 else 'Failed')
  for path,msg in re.findall(r'^(.*):\d+:\d+: warning: (.*)$',(f.parent/'stderr.log').read_text(),re.MULTILINE):
   fp=Path(path);original=UNITY.parent.parent/'il2cpp'/fp.relative_to(S);assert fp.is_relative_to(S/'external/baselib') and sha(fp)==sha(original)
   warnings.append({'commandReceipt':str(f),'file':str(fp),'installedOriginal':str(original),'sha256':sha(fp),'diagnostic':msg})
 rows.append(record)
for x in r['sources']:assert sha(W/x['path'])==x['sha256']
for x in load(P/'J_SOURCE_BINDINGS.json')['currentSources']:
 original=Path(x['path']);copy=S/'libil2cpp'/original.relative_to(W/'il2cpp_plus/libil2cpp');assert sha(copy)==x['sha256']
configs=[x for x in rows if 'state' in x];passed=sum(x['state']=='Passed' for x in configs);failed=sum(x['state']=='Failed' for x in configs)
profiles=collections.Counter(x['profile'] for x in r['translationUnits'])
if r['result']=='Passed':
 assert len(rows)==56 and len(configs)==passed==55 and failed==0 and len(r['translationUnits'])==55 and profiles=={n:11 for n in ['candidate','debug','probe-off','diagnostics-off','feature-off']}
 assert len({(x['profile'],x['source']) for x in r['translationUnits']})==55
 assert len({x['source'] for x in r['translationUnits']})==11
 for x in r['translationUnits']:assert sha(x['source'])==x['sha256'] and x['commandReceipt'] in {y['receiptSha256'] for y in rows}
 sdk=load(N/'native-sdk-inputs.json');assert {x['path'] for x in sdk['files']}=={str(f.relative_to(S)) for f in S.rglob('*') if f.is_file()}
 for x in sdk['files']:assert sha(S/x['path'])==x['sha256']
else:sdk={'files':[]}
save(P/'NATIVE_VERIFICATION.json',{'state':r['result'],'startUtc':start,'endUtc':now(),'pins':pins,'invocations':1,'nativeConfigurations':{'Passed':passed,'Failed':failed,'NotRun':55-len(configs)},'profiles':dict(profiles),'commands':rows,'copiedSdkInventoryFiles':len(sdk['files']),'sourceInventory':r['sources'],'newNativeHeaderSha256':sha(W/'il2cpp_plus/libil2cpp/vm/AssemblyShadowFixedBoolean.h'),'compilerFlagsUnchanged':True,'syntaxOnly':True,'unityVersion':'2022.3.62f2','unityLaunches':0,'PlayerBuilds':0,'Players':0,'runtimeAcceptance':False})
save(P/'COMPILER_WARNING_AUDIT.json',{'state':'Recorded','occurrences':len(warnings),'counts':dict(collections.Counter(x['diagnostic'] for x in warnings)),'rows':warnings,'source':'Copied Baselib headers byte-identical to installed official SDK','suppressed':False,'runtimeSafetyInferred':False,'managedWarnings':'Current M fresh managed compilation recorded separately; G historical warnings retained'})
print(json.dumps({'nativeResult':r['result'],'Passed':passed,'Failed':failed,'NotRun':55-len(configs),'warnings':len(warnings),'copiedSdkFiles':len(sdk['files'])}),flush=True)
