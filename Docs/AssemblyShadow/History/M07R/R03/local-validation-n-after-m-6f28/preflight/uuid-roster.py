from h_common import *
import re
R=B/'R03IRLocal-N-after-M-6f28';a=load(P/'FINAL_EVIDENCE_AUDIT.json');rows=[]
for role in ['candidate-release','candidate-debug','candidate-off']:
 app=R/'builds'/role/'R03Isolated.app';images=[]
 for name in ['R03Isolated','GameAssembly.dylib','UnityPlayer.dylib']:
  f=app/('Contents/MacOS/'+name if name=='R03Isolated' else 'Contents/Frameworks/'+name);c=command('uuid-'+role+'-'+name.replace('.','-'),['/usr/bin/dwarfdump','--uuid',f]);assert c['exitCode']==0
  text=Path(c['stdoutPath']).read_text();u=re.findall(r'UUID: ([0-9A-F-]{36}) \(arm64\)',text);assert len(u)==1;images.append({'path':str(f),'sha256':sha(f),'arm64Uuid':u[0],'receipt':str(P/'commands'/('uuid-'+role+'-'+name.replace('.','-'))/'receipt.json')})
 players=[x for x in a['players'] if ('candidate-debug' if 'debug' in x['caseId'] else 'candidate-off' if x['caseId'].endswith('-off') else 'candidate-release')==role]
 for p in players:
  cmd=load(p['commandReceipt'])['command'];assert cmd[0]==str(app/'Contents/MacOS/R03Isolated')
 rows.append({'role':role,'app':str(app),'images':images,'players':[{'caseId':x['caseId'],'runId':x['runId'],'pid':x['pid'],'requestSha256':x['requestSha256'],'commandReceipt':x['commandReceipt']} for x in players]})
save(P/'MACHO_BUILD_PLAYER_JOINS.json',{'state':'PassedIdentityBinding','recordedUtc':now(),'roles':rows,'builds':3,'players':5,'newPlayerLaunches':0,'source':pins,'classification':'Read-only fresh M app bytes and actual launch/request/PID joins; UUIDs do not establish acceptance'})
