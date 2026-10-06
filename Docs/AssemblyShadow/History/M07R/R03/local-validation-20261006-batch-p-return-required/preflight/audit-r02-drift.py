"""Authenticate known schema-extension drift in failed raw results; no verdict replacement."""
import pathlib,json,hashlib,datetime,sys
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261006P-lo-repair'
sys.path[:0]=[str(D/'Tools/AssemblyShadow/R02'),str(D/'Tools/AssemblyShadow')]
import type_resolution_schema as bridge
load=lambda p:json.loads(pathlib.Path(p).read_text())
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
result=load(R/'LOCAL_BATCH_RESULT.json');cells=[c for c in result['cells'] if c['result']=='Failed' and "unknown=['r02']" in c.get('error','')]
records=[];started=datetime.datetime.now(datetime.timezone.utc).isoformat()
for c in cells:
 p=pathlib.Path(c['error'].split('.json.typeResolutions',1)[0]+'.json');before=sha(p);raw=load(p);rows=[]
 for n,row in enumerate(raw['typeResolutions']):
  value=bridge.loads(row['rawJson']);projection=bridge.legacy_projection(value,str(p)+'.typeResolutions['+str(n)+']');ext=value['r02'];assert ext['diagnosticsLevel']==2
  rows.append({'index':n,'legacyFieldCount':len(projection),'extensionFieldCount':len(ext),'schemaVersion':ext['schemaVersion'],'diagnosticsLevel':ext['diagnosticsLevel'],'counterCoverage':ext['counterCoverage'],'classesCoverage':ext['classesCoverage'],'counterSaturated':ext['counterSaturated'],'droppedCounterThreads':ext['droppedCounterThreads'],'strictExistingExtensionContract':'Passed','legacyFieldTypeIdentityContract':'Passed'})
 assert sha(p)==before
 records.append({'cell':c['id'],'originalCellState':'Failed','originalError':c['error'],'rawPath':str(p),'rawSha256':before,'processId':raw['processId'],'typeResolutionObjects':rows,'rawBytesUnchanged':True,'completeM07ContractReclassified':False})
record={'kind':'ReadOnlyKnownR02SchemaDriftDiagnosis','startedUtc':started,'endedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':records,'failedCellsExamined':len(records),'existingStrictSchemaSource':{'path':str(D/'Tools/AssemblyShadow/R02/type_resolution_schema.py'),'sha256':sha(D/'Tools/AssemblyShadow/R02/type_resolution_schema.py')},'scope':'Existing strict 33-field extension and 18-field legacy type-info validation only, in memory; no callback replacement, full M07 recheck, raw rewrite, new Player, expectation change or original verdict promotion. Full remaining consumers still require a fresh Primary-owned fix and validation.','R03Accepted':False,'H2Passed':False,'qualificationApproved':False}
(P/'R02_SCHEMA_DRIFT_DIAGNOSIS.json').write_text(json.dumps(record,indent=2)+'\n');print('Known R02 schema diagnosis:',len(records),'original Failed cells;',sum(len(r['typeResolutionObjects']) for r in records),'strictly validated raw type-info objects; no reclassification')
