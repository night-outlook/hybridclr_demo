from pathlib import Path
import sys,json,hashlib,datetime
D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009C-capacity-retry');sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03'));sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03IR'));from ir_original_fixtures import stage_immutable_original_s
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
entries,receipt=stage_immutable_original_s(D,P/'original-s-fixtures',sha);record={'state':'Passed','startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originalFixtures':len(entries),'authorityReceipt':str(receipt),'authoritySha256':sha(receipt),'regenerationAttempted':False,'runtimeAcceptance':False,'fixtureStagingIsIndependentOfBlockedStorageExecution':True};(P/'ORIGINAL_INPUT_PREFLIGHT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
