from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261010E-native-receipt');B=P.parent/'R03IRLocal-20261010E-native-receipt';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
start=now();out=P/'diagnostics';out.mkdir();rows=[];ops=[]
def cmd(argv):
 t=now();r=subprocess.run(argv,capture_output=True,text=True,timeout=60);ops.append({'argv':argv,'startUtc':t,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout
for root in [Path('/Users/ah/Library/Logs/DiagnosticReports'),Path('/Library/Logs/DiagnosticReports')]:
 for p in sorted(root.glob('R03Isolated*.ips')):
  j=json.loads('\n'.join(p.read_text().splitlines()[1:]));pid=j.get('pid')
  if pid not in [10439,10441,10443]:continue
  case={10439:'release-baseline',10441:'debug-baseline',10443:'release-type'}[pid];role='candidate-debug' if pid==10441 else 'candidate-release';app=B/'builds'/role/'R03Isolated.app'
  command=json.loads((B/'commands'/{10439:'0006',10441:'0007',10443:'0008'}[pid]/'command.json').read_text());assert command['pid']==pid
  bindings=[]
  for name in ['R03Isolated','GameAssembly.dylib','UnityPlayer.dylib']:
   image=next(x for x in j['usedImages'] if x.get('name')==name);binary=app/('Contents/MacOS/'+name if name=='R03Isolated' else 'Contents/Frameworks/'+name);uuid=cmd(['/usr/bin/dwarfdump','--uuid',str(binary)]);assert image['uuid'].lower() in uuid.lower();bindings.append({'path':str(binary),'sha256':sha(binary),'imageUuid':image['uuid'],'loadAddress':image['base'],'uuidMatched':True})
  dst=out/p.name;shutil.copyfile(p,dst);assert sha(p)==sha(dst)
  t=j['threads'][j['faultingThread']];frames=t['frames'];symbols=[x.get('symbol','') for x in frames]
  assert any('RaiseTerminalExecutionRejected' in x for x in symbols);assert any('CallOverridenDebugHandler' in x for x in symbols)
  # macOS already supplies symbolicated frames and native source line numbers.
  rows.append({'caseId':'IR-R03-02-'+case,'pid':pid,'originalPath':str(p),'copyPath':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,'captureTime':j['captureTime'],'procPathRedactedByMacOS':j.get('procPath'),'exception':j['exception'],'faultingThread':j['faultingThread'],'frames':frames,'originalLength':t.get('originalLength'),'recursionInfoArray':t.get('recursionInfoArray'),'imageBindings':bindings,'binding':'Command PID/time + all three fresh binary Mach-O UUIDs; report paths are OS-redacted','symbolication':'Already symbolicated by macOS; no Player rerun'})
sources=[]
for repo,rel in [('il2cpp_plus','libil2cpp/vm/AssemblyShadow.cpp'),('il2cpp_plus','libil2cpp/vm/Runtime.cpp'),('il2cpp_plus','libil2cpp/vm/AssemblyShadowTerminalExecution.h'),('hybridclr_demo','Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs')]:
 f=W/repo/rel;h=cmd(['git','-C',str(W/repo),'rev-parse','HEAD']).strip();raw=subprocess.check_output(['git','-C',str(W/repo),'show',h+':'+rel]);assert raw==f.read_bytes();dst=out/'source'/repo/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);sources.append({'repository':str(W/repo),'commit':h,'path':rel,'sha256':sha(f),'snapshot':str(dst)})
record={'state':'EvidenceCaptured','startUtc':start,'endUtc':now(),'reports':rows,'reportUnavailableForPids':[x for x in [10439,10441,10443] if x not in [r['pid'] for r in rows]],'operations':ops,'sources':sources,'sourceChanges':False,'newPlayerLaunches':0,'inference':'Terminal rejection reaches Unity Runtime::Invoke and repeated Unity debug-handler invocation, causing stack-guard SIGSEGV. Exact original first failure and semantic progress remain Unavailable because ON raw records were never written. Reporting/exception infrastructure cannot complete under the current global terminal guard; Primary must investigate without permitting business execution.'}
with (P/'CRASH_DIAGNOSIS.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({'reports':len(rows),'pids':[r['pid'] for r in rows],'unavailable':record['reportUnavailableForPids'],'state':record['state']}))
