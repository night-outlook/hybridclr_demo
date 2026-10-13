from h_common import *
phase=sys.argv[1];assert phase in ['before','after'];start=now();rows=[]
for n,h in pins.items():
 repo=W/n;raw=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','-z',h]);entries=[x.split(b'\t',1) for x in raw.split(b'\0') if x]
 for meta,path in entries:
  rel=path.decode()
  if rel.startswith('Docs/'):continue
  f=repo/rel
  if f.suffix.lower() not in ['.py','.cs','.cpp','.h','.hpp','.asmdef','.asmref','.json','.csproj']:continue
  if n=='hybridclr_demo' and not rel.startswith(('Tools/AssemblyShadow/','Assets/','Packages/','ProjectSettings/')):continue
  assert f.is_file() and not f.is_symlink();data=f.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==meta.split()[2].decode()
  rows.append({'repository':str(repo),'commit':h,'path':rel,'gitBlob':blob,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
if phase=='before':save(P/'SOURCE_INPUTS_BEFORE.json',rows)
else:assert rows==load(P/'SOURCE_INPUTS_BEFORE.json')
R=B/'R03LocalBatch-20261007R-lq-storage';Q=B/'R03LocalBatch-20261006Q-lp-repair';rr=load(R/'LOCAL_BATCH_RESULT.json');qr=load(Q/'LOCAL_BATCH_RESULT.json')
restore=[c for c in rr['cells'] if 'restor' in c['id']];assert restore and any(c['result']=='Failed' for c in restore)
save(P/('SOURCE_PRESERVATION_'+phase.upper()+'.json'),{'state':'Passed','startUtc':start,'endUtc':now(),'sourceFiles':len(rows),'sourceInventorySha256':sha(P/'SOURCE_INPUTS_BEFORE.json'),'pins':pins,'retainedRResult':rr['result'],'retainedRRestorationCells':restore,'retainedQResult':qr['result'],'retainedQPath':str(Q),'retainedQSourcePins':qr.get('repositories'),'protectedHistoricalResultsUnchanged':True})
print(json.dumps({'phase':phase,'sourceFiles':len(rows),'RRestoration':[x['result'] for x in restore]}),flush=True)
