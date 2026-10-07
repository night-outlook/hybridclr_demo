"""Prescribed read-only publication budget; no evidence packing or deletion."""
from pathlib import Path
import os,sys,json,datetime,subprocess
P=Path(__file__).resolve().parent;D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');B=P.parent/'R03LocalBatch-20261007R-lq-storage';sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03Storage'));import storage_guard as s
assert (P/'runner-exit.json').is_file() and (B/'seal-receipt.json').is_file()
start=s.utc();size=s.footprint(B);required=max(s.FLOOR,size['planningBytes']+s.MARGIN);common=Path(subprocess.check_output(['git','-C',str(D),'rev-parse','--path-format=absolute','--git-common-dir']).decode().strip());observation=s.sample({'publicationCheckout':D,'retainedBatch':B,'gitCommon':common});record={'kind':'R03StoragePublicationCheck','startUtc':start,'requiredBytes':required,'size':size,'observation':observation,'state':'Blocked','coreAndStorageSessionUnmodified':True}
try:s.capacity_ok(observation,required);record['state']='Passed'
finally:
 record['endUtc']=s.utc();s.write_new(P/'storage-publication-check.json',record)
print(json.dumps({'publicationCapacity':record['state'],'requiredGiB':required/1024**3,'availableGiB':min(v['availableBytes'] for v in observation['volumes'])/1024**3,'planningBytes':size['planningBytes']}))
