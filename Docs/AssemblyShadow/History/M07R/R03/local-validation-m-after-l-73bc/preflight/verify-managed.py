from h_common import *
import collections,re
M=B/'ManagedAPI-R03M-after-L-73bc';start=now();j=load(M/'build-api/results.json');receipts=[];warnings=[]
for row in j['commands']:
 f=Path(row['receipt']['path']);assert sha(f)==row['receipt']['sha256'];rsp=Path(row['response']['path']);assert sha(rsp)==row['response']['sha256'];c=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==c[n+'Sha256']
 assert c['exitCode']==row['expectedExit'] and not c['cleanupErrors'] and not c['remainingProcessGroup'] and not c['postCleanupGroupExists'] and not c['timeout']
 text=(f.parent/'stdout.log').read_text()+(f.parent/'stderr.log').read_text();errors=re.findall(r'\berror (CS\d+):',text)
 if row['expectedExit']==0:assert not errors
 else:assert errors==['CS0266','CS0266'] and row['id']=='OriginalUnsignedCounts' and not (M/'build-api/OriginalUnsignedCounts/OriginalUnsignedCounts.dll').exists()
 warnings+=re.findall(r'\bwarning (CS\d+):',text)
 receipts.append({'target':row['id'],'expectedExit':row['expectedExit'],'actualExit':c['exitCode'],'receipt':str(f),'receiptSha256':sha(f),'responseSha256':sha(rsp),'errors':errors})
for r in j.get('inputs',[]):assert sha(r['path'])==r['sha256']
outputs=[]
for r in j.get('packageAssemblies',[]):outputs.append(r['output'])
if 'completeHelper' in j:outputs.append(j['completeHelper'])
if 'terminalPlayerApi' in j:outputs.append(j['terminalPlayerApi']['output'])
for x in outputs:assert sha(x['path'])==x['sha256']
if j['result']=='Passed':assert len(receipts)==6 and len(outputs)==5 and len(j['inputs'])==428
save(P/'MANAGED_VERIFICATION.json',{'state':j['result'],'startUtc':start,'endUtc':now(),'pins':pins,'invocations':1,'commands':receipts,'outputs':outputs,'currentCompilerInputFiles':len(j.get('inputs',[])),'warningCount':len(warnings),'warningCodes':dict(collections.Counter(warnings)),'currentHelperSha256':sha(D/'Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs'),'currentPlayerSha256':sha(D/'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'),'freshOfficialManagedCompilation':True,'expectedNegativeClassification':'PassedExpectedNegative; never a product build','UnityLaunches':0,'Players':0,'runtimeAcceptance':False})
print(json.dumps({'result':j['result'],'products':len(outputs),'controls':sum(x['expectedExit']==1 for x in receipts),'warnings':len(warnings)}),flush=True)
