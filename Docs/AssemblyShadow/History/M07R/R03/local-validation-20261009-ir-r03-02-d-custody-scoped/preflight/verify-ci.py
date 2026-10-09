from pathlib import Path
import json,hashlib,subprocess,datetime,re
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');BOOT=BASE/'Preflight-R03IRLocal-20261009D-custody-scoped';P=BASE/'Preflight-R03IRLocal-20261009D-custody-scoped';A=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-preflight-blocked';E=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09';start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with f.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
run=json.loads((BOOT/'CI_RUN.json').read_text());jobs=json.loads((BOOT/'CI_JOBS.json').read_text());assert run['head_sha']=='ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b' and run['id']==37903041633 and run['conclusion']=='success' and run['status']=='completed';assert jobs['jobs'][0]['id']==113729828150 and jobs['jobs'][0]['conclusion']=='success'
inputs=json.loads((E/'compile-inputs.json').read_text());result=json.loads((E/'compile-result.json').read_text());joblog=(BOOT/'CI_JOB.log').read_text();decoded=(P/'compiler-build.log').read_text();bound={}
for label in ['INPUTS','RESULT']:
 rows=re.findall('R03_IR_COMPILE_'+label+'_JSON=(\\{[^\\n]*\\})',joblog);assert len(rows)==1,(label,len(rows));bound[label]=json.loads(rows[0])
assert bound['INPUTS']==inputs and bound['RESULT']==result
assert 'Build succeeded.' in decoded and '13 Warning(s)' in decoded and '0 Error(s)' in decoded and '../../R03IR/PlayerProject/R03TerminalPlayer.cs' in decoded and '/langversion:9.0' in decoded
matched=[]
for row in inputs['inputs']:
 root=W/row['repository'].split('/')[1];f=root/row['path'];h=sha(f);assert h==row['sha256'];matched.append(row)
assert len(matched)==22 and sum(x['compileItem'] for x in matched)==19
previous=json.loads((A/'SOURCE_BINDINGS.json').read_text());unchanged=[]
for row in previous:
 if row['path'].startswith('Tools/') or row['repository'].endswith('/il2cpp_plus'):
  f=Path(row['repository'])/row['path'];assert sha(f)==row['sha256'];unchanged.append(row)
ci=json.loads((A/'preflight/CI_SOURCE_EQUIVALENCE.json').read_text());priorLogs=[]
for row in ci['logCopies']:
 f=Path(row['path']);assert sha(f)==row['sha256'];priorLogs.append({'path':str(f),'sha256':row['sha256'],'state':'ReusedAudited actual prior downloaded job log'})
report={'state':'Passed','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceMatchedManagedApi':'Passed','demoCommit':'7313c768a2658ae77357e3fb1a83e9542585c99c','ciSource':run['head_sha'],'runId':37903041633,'jobId':113729828150,'inputEntries':22,'explicitCSharpInputs':19,'inputs':matched,'inputReceiptSha256':sha(E/'compile-inputs.json'),'resultReceiptSha256':sha(E/'compile-result.json'),'compilerLogSha256':sha(P/'compiler-build.log'),'apiErrors':0,'apiWarnings':13,'sdk':'10.0.401','targetFramework':'net8.0','languageVersion':'9.0','unityApi':'checked-in stubs, not official managed assemblies','jobOutputReceiptsMatchPublished':True,'actualJobLogSha256':sha(BOOT/'CI_JOB.log'),'actualJobLogCopyEncoding':'Decoded connector text with normalized final newline; not remote ZIP byte identity','unchangedRuntimeAndNativeSourcesFromA':unchanged,'priorNativeApiFixtureSourceEvidence':'ReusedAudited with unchanged source bindings, not freshly run CI or Player','priorLogs':priorLogs,'oldApiRun37874183375':'Historical NoCoverage retained','freshLocalManagedCompile':False,'primaryArtifactZip':'Not downloaded by Local; Primary verification remains attributed','primarySyntheticReceiptTests':'11 Passed in published Primary evidence; not freshly run by Local','prescribedSourceCheckOriginalStartEnd':'Unavailable; exact prescribed script command and output retained in CI_CURRENT_SOURCE.json','unityRun':False,'playerRun':False,'runtimeAcceptance':False}
with (P/'CI_EQUIVALENCE_VERIFICATION.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'state':'Passed','currentCompilerInputs':22,'currentSourceApi':'Passed','runtimeAcceptance':False}))
