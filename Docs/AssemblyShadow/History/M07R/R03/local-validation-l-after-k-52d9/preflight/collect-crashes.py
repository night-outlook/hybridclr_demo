from h_common import *
import shutil
start=now();R=B/'R03IRLocal-L-after-K-52d9';out=P/'diagnostics';out.mkdir();rows=[];ops=[];audit=load(P/'FINAL_EVIDENCE_AUDIT.json');targets={r['pid']:r for r in audit['players'] if r.get('exitCode') in [-6,-11]}
for base in [Path('/Users/ah/Library/Logs/DiagnosticReports'),Path('/Library/Logs/DiagnosticReports')]:
 for f in sorted(base.glob('R03Isolated*.ips')):
  try:j=json.loads('\n'.join(f.read_text().splitlines()[1:]))
  except ValueError:continue
  if j.get('pid') not in targets:continue
  r=targets[j['pid']];captured=datetime.datetime.strptime(j['captureTime'],'%Y-%m-%d %H:%M:%S.%f %z').timestamp()
  if not r['startEpoch']-2<=captured<=r['endEpoch']+15:continue
  role='candidate-debug' if 'debug' in r['caseId'] else 'candidate-off' if r['caseId'].endswith('-off') else 'candidate-release';app=R/'builds'/role/'R03Isolated.app';bindings=[]
  for name in ['R03Isolated','GameAssembly.dylib','UnityPlayer.dylib']:
   im=next(x for x in j['usedImages'] if x.get('name')==name);binary=app/('Contents/MacOS/'+name if name=='R03Isolated' else 'Contents/Frameworks/'+name);t=now();x=subprocess.run(['/usr/bin/dwarfdump','--uuid',str(binary)],capture_output=True,text=True,check=True);assert im['uuid'].lower() in x.stdout.lower();ops.append({'argv':['/usr/bin/dwarfdump','--uuid',str(binary)],'startUtc':t,'endUtc':now(),'exitCode':x.returncode,'stdout':x.stdout,'stderr':x.stderr});bindings.append({'path':str(binary),'sha256':sha(binary),'imageUuid':im['uuid'],'uuidMatched':True})
  dst=out/f.name;shutil.copyfile(f,dst);frames=j['threads'][j['faultingThread']]['frames'];rows.append({'caseId':r['caseId'],'pid':j['pid'],'runId':r['runId'],'commandReceipt':r['commandReceipt'],'captureTime':j['captureTime'],'originalPath':str(f),'copyPath':str(dst),'sha256':sha(dst),'exception':j['exception'],'imageBindings':bindings,'frames':frames,'identityBinding':'Fresh PID/time/request plus all three binary Mach-O UUIDs'})
save(P/'CRASH_DIAGNOSIS.json',{'state':'EvidenceCaptured' if rows else 'Unavailable','startUtc':start,'endUtc':now(),'reports':rows,'unavailableForPids':[pid for pid in targets if pid not in [r['pid'] for r in rows]],'operations':ops,'newPlayerLaunches':0,'historicalIOrEReclassified':False});print(json.dumps({'boundReports':len(rows),'pids':[r['pid'] for r in rows],'unavailable':[pid for pid in targets if pid not in [r['pid'] for r in rows]]}),flush=True)
