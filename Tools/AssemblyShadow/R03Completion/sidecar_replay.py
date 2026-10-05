"""Read-only five-N-sidecar regression. Not a reclassification of N or native proof."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'R03'))
from batch_contract import loads,require,sha
from batch_evidence import write
import layout_evidence as layout
from compiler_policy_inputs import regular
from reference_binding import CHECKPOINT

AUDIT_SHA='a63a48adf592d1876918a31ee7ec9dfbf9f90f7c99b618f226b48d0ef7aea012'


def cases(demo):
    root=Path(demo)/CHECKPOINT
    audit_path=regular(root/'preflight/CURRENT_SIDECAR_AUDIT.json')
    require(sha(audit_path)==AUDIT_SHA,'Exact N independent sidecar audit')
    audit=loads(audit_path.read_text());require(audit['status']=='Failed','Preserve original Failed audit')
    index=loads(regular(root/'batch/evidence-index.json').read_text())
    # The committed audit/manifest hashes are authority for JSON replay. Original
    # sealed DLL/file custody remains Local's result, not a new native build.
    def mapped(live):
        suffix=live.split('/R03LocalBatch-20261005N-identity/',1)[1]
        require(not Path(suffix).is_absolute() and '..' not in Path(suffix).parts,'Captured path')
        p=regular(root/'batch'/suffix)
        entries=index['files']
        rows=[f for f in entries if f['path']==suffix]
        require(len(rows)==1 and sha(p)==rows[0]['sha256'],'Exact N indexed JSON input')
        return p
    manifest_path=mapped(audit['manifest']);require(sha(manifest_path)==audit['manifestSha256'],'N manifest binding')
    manifest=loads(manifest_path.read_text());base=manifest['baselineInputSnapshot']
    baseline=loads(mapped(base+'/assembly-snapshot.json').read_text())
    proof_path=mapped(base+'/ReflectionBindings/LinkedRetargeting/evidence.json');proof=loads(proof_path.read_text())
    linked=[{'path':f['path'],'sha256':f['sha256']} for f in baseline['linkedPlayerReceipt']['assemblies']]
    output=[]
    for f,a in zip(manifest['fixtures'],audit['fixtures']):
        require(f['patchId']==a['patchId'],'Exact fixture sequence')
        target=loads(mapped(f['compileSnapshot']+'/assembly-snapshot.json').read_text())
        compiler=[{'path':f['path'],'sha256':f['sha256']} for f in target['assemblies']+target['references']]
        side=mapped(a['sidecar']);require(sha(side)==a['sha256'],'Exact N sidecar hash')
        args=[loads(side.read_text()),baseline,target,linked,compiler,proof,sha(proof_path),proof['facadeSha256'],f['closureLoadOrder']]
        output.append((f['patchId'],args))
    require([p for p,_ in output]==['P01','P02','P03','P04','P05'],'All five captured sidecars')
    return output


def verify(demo,output):
    values=[{'patchId':p,'checks':layout.verify_value(*a)} for p,a in cases(demo)]
    r={'kind':'R03NReadOnlySidecarReplay','result':'Passed','basis':'ReusedAuditedLocalNJsonInputs',
       'historicalNVerification':'Failed','fixtures':values,'runtimeAcceptance':False,'nativeProofExecuted':False}
    write(output,r);return r
